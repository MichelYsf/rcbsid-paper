#!/usr/bin/env python
"""S4 - the construction contrast, the rebuilt paper's central experiment.

Claim under test: **benchmark stream CONSTRUCTION, not attack prevalence,
produces the regime structure the literature reports.**

Two contrasts, because the constructions differ in kind
-------------------------------------------------------
CICIDS2017 is one capture week containing many attack types, so the synthetic
construction reorders records WITHIN the stream:
    arm "natural"      : true timestamp order
    arm "interleaved"  : day-of-week round robin (scripts/interleave_cicids.py)
Both arms hold the same records; only order differs.

LITNET-2020 cannot be contrasted that way. Its three captures are temporally
disjoint, so each per-attack-type stream contains exactly ONE attack_type and
round-robin within it is the IDENTITY. (Verified: attack_type is ['spam'] in
the spam stream.) The real LITNET contrast is at the level of COMPOSITION:
    arm "natural"      : the three per-type streams, each evaluated separately
    arm "composite"    : the pooled 3-type interleaved composite
This is why LITNET's "5.2% rare-attack regime" exists at all - it is produced
by pooling, not by any deployment property.

Bounded evaluation budget (documented reduction)
------------------------------------------------
Measured per-row costs on this hardware: detector 2.50 ms, HST 6.58 ms,
LODA 12.09 ms. A full-stream two-arm contrast is ~13.8 h for one 500k stream
and far more for CICIDS, which breaks the 6 h wall cap. We therefore evaluate
a fixed budget of --budget records per arm, applied IDENTICALLY to both arms
of a contrast, and drop LODA (the costliest baseline) from the contrast.
Holding the record budget equal is what keeps the comparison fair: the arms
differ only in the ORDER of the records they see.
"""
from __future__ import annotations

import argparse
import gc
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from provenance import provenance_run, sha256_file                  # noqa: E402
from src.baselines.batch import LAST_FALLBACK, run_batch_reference   # noqa: E402
from src.baselines.registry import make_streaming_baseline           # noqa: E402
from src.bocpd.slo import posterior_threshold                        # noqa: E402
from src.data.loaders import prepare_xy                              # noqa: E402
from src.eval.metrics import classification_metrics                  # noqa: E402
from src.experiments.run_streaming_eval import (                     # noqa: E402
    _make_bocpd, _score_stream_with_warmup, _split_chronological,
    _threshold_from_validation,
)

TRAIN, VAL = 0.70, 0.15
STREAMING = ["hst"]      # LODA dropped from the contrast: 12.09 ms/row
BATCH = ["ecod"]         # deterministic reference
PROPOSED = {
    "hazard_grid": [0.01, 0.002, 0.001, 0.0002, 0.0001],
    "run_length_truncation": 500,
    "default_incident_prior": 0.05,
}


def camel(*parts: str) -> str:
    out = []
    for p in parts:
        for w in str(p).replace("-", "_").split("_"):
            out.append(w.capitalize())
    return "".join(out)


def interleave_by_day(df: pd.DataFrame) -> pd.DataFrame:
    """CICIDS synthetic construction: round robin across capture days."""
    ts = pd.to_datetime(df["Timestamp"], errors="coerce")
    day = ts.dt.date.astype(str)
    groups = {k: g.to_numpy() for k, g in day.groupby(day).groups.items()} \
        if False else {k: np.asarray(v) for k, v in day.groupby(day).groups.items()}
    names = sorted(groups)
    longest = max(len(groups[n]) for n in names)
    order = []
    for k in range(longest):
        for n in names:
            g = groups[n]
            if k < len(g):
                order.append(g[k])
    return df.loc[order].reset_index(drop=True)


def interleave_by_type(df: pd.DataFrame) -> pd.DataFrame:
    """LITNET synthetic construction: round robin across attack types."""
    groups = {k: np.asarray(v) for k, v in df.groupby("attack_type").groups.items()}
    names = sorted(groups)
    longest = max(len(groups[n]) for n in names)
    order = []
    for k in range(longest):
        for n in names:
            g = groups[n]
            if k < len(g):
                order.append(g[k])
    return df.loc[order].reset_index(drop=True)


def run_arm(run, tag: str, arm: str, X, y, seeds: list[int]) -> list[dict]:
    (Xtr, ytr), (Xva, yva), (Xte, yte) = _split_chronological(X, y, TRAIN, VAL)
    default_thr = posterior_threshold(1.0, 10.0, PROPOSED["default_incident_prior"])
    n_feat = X.shape[1]
    rows: list[dict] = []

    MIN_TEST_ATTACKS = 20

    def record(method, seed, scores_te, thr, elapsed, fallback=False):
        n_atk = int(np.sum(yte))
        if n_atk < MIN_TEST_ATTACKS:
            # Integrity: AUC-PR is undefined/meaningless on a test slice with
            # (almost) no positives. Record the fact instead of a silent nan.
            run.note(f"{tag}_{arm}_{method}_excluded",
                     f"test slice holds {n_atk} attacks (< {MIN_TEST_ATTACKS}); "
                     f"AUC-PR not defined, cell excluded")
            rows.append({"stream": tag, "arm": arm, "method": method, "seed": seed,
                         "n_test": int(len(yte)), "test_attacks": n_atk,
                         "excluded_reason": f"test attacks {n_atk} < {MIN_TEST_ATTACKS}"})
            return None
        m = classification_metrics(yte, np.asarray(scores_te, float), thr)
        m.update({"stream": tag, "arm": arm, "method": method, "seed": seed,
                  "threshold": float(thr), "n_test": int(len(yte)),
                  "test_prevalence": float(np.mean(yte)),
                  "elapsed_s": round(elapsed, 2), "uses_fallback": bool(fallback),
                  "test_attacks": n_atk})
        rows.append(m)
        run.emit_macro("Contrast" + camel(tag, arm, method) + "Aucpr",
                       round(float(m["auc_pr"]), 6),
                       desc=f"{tag}/{arm}/{method} AUC-PR")
        return m

    t0 = time.time()
    model = _make_bocpd(PROPOSED, 11)
    _score_stream_with_warmup(model, Xtr, Xva)
    st = _score_stream_with_warmup(model, np.empty((0, n_feat)), Xte)
    record("proposed_detector", 11, st, default_thr, time.time() - t0)

    for method in STREAMING:
        for seed in seeds:
            t0 = time.time()
            mdl = make_streaming_baseline(method, n_features=n_feat, seed=seed,
                                          allow_fallback=False)
            for r in Xtr:
                mdl.learn_one(r)
            sval = []
            for r in Xva:
                sval.append(float(mdl.score_one(r)))
                mdl.learn_one(r)
            thr = _threshold_from_validation(yva, sval, default_thr)
            ste = []
            for r in Xte:
                ste.append(float(mdl.score_one(r)))
                mdl.learn_one(r)
            record(method, seed, ste, thr, time.time() - t0,
                   bool(getattr(mdl, "uses_fallback", False)))

    for method in BATCH:
        t0 = time.time()
        Xfit = Xtr[ytr == 0] if np.any(ytr == 0) else Xtr
        ev = run_batch_reference(method, Xfit, np.vstack([Xva, Xte]), seed=11,
                                 allow_fallback=False)
        thr = _threshold_from_validation(yva, ev[:len(Xva)], default_thr)
        record(method, 11, ev[len(Xva):], thr, time.time() - t0,
               bool(LAST_FALLBACK.get(method, False)))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contrast", required=True,
                    choices=["cicids_order", "litnet_composition"])
    ap.add_argument("--budget", type=int, default=0,
                    help="records per arm; 0 = FULL stream (default). A prefix changes the "
                         "measured prevalence because the chronological tail is exactly where "
                         "CICIDS reaches 68 percent, so full streams are the default.")
    ap.add_argument("--arm", default="both",
                    choices=["both", "natural", "synthetic"],
                    help="run one arm per invocation to stay under the wall cap")
    ap.add_argument("--seeds", type=int, nargs="*", default=[11])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    nat = ROOT / "data/raw/natural"
    with provenance_run("s4_construction_contrast",
                        config={"contrast": a.contrast, "budget": a.budget,
                                "seeds": a.seeds, "train": TRAIN, "val": VAL,
                                "streaming": STREAMING, "batch": BATCH,
                                "reduction": "LODA dropped (12.09 ms/row); "
                                             "fixed record budget per arm",
                                "claim": "construction, not prevalence, drives regime"},
                        seed=11,
                        notes="natural vs synthetic construction; all else held constant") as run:
        rows: list[dict] = []
        B = a.budget if a.budget > 0 else None
        want_nat = a.arm in ("both", "natural")
        want_syn = a.arm in ("both", "synthetic")

        if a.contrast == "cicids_order":
            src = nat / "cicids2017_natural.csv"
            run.declared_inputs.append(str(src))
            df = pd.read_csv(src, nrows=B, low_memory=False)
            Xn, yn, _ = prepare_xy(df.copy(), "label")
            run.emit_macro("ContrastCicidsDim", int(Xn.shape[1]),
                           desc="CICIDS2017 feature dimensionality d")
            if want_nat:
                if not want_syn:
                    del df
                    gc.collect()
                rows += run_arm(run, "cicids2017", "natural", Xn, yn, a.seeds)
            if want_syn:
                # Memory, not statistics: Xn exists only to report d. Holding it
                # while the interleaved copy is materialised peaks near 2x on the
                # 1.6M-row stream, which is what would OOM a 16 GB box. Freeing it
                # changes no computed value - the arms still see the same records
                # in a different order.
                del Xn, yn
                gc.collect()
                di = interleave_by_day(df)
                del df
                gc.collect()
                Xi, yi, _ = prepare_xy(di, "label")
                del di
                gc.collect()
                rows += run_arm(run, "cicids2017", "interleaved_synthetic",
                                Xi, yi, a.seeds)

        else:  # litnet_composition
            per = {"udp_flood": nat / "litnet2020_udp_flood_natural.csv",
                   "blaster_worm": nat / "litnet2020_blaster_worm_natural.csv",
                   "spam": nat / "litnet2020_spam_natural.csv"}
            share = (B // 3) if B else None
            frames = []
            for t, p in per.items():
                run.declared_inputs.append(str(p))
                d = pd.read_csv(p, nrows=share, low_memory=False)
                if want_syn:
                    frames.append(d)
                X, y, _ = prepare_xy(d.copy(), "label")
                run.emit_macro("Contrast" + camel("litnet", t) + "Dim", int(X.shape[1]),
                               desc=f"litnet {t} feature dimensionality d")
                if want_nat:
                    rows += run_arm(run, "litnet_" + t, "natural", X, y, a.seeds)
                del X, y, d
                gc.collect()
            if want_syn:
                pooled = interleave_by_type(pd.concat(frames, ignore_index=True))
                frames.clear()
                gc.collect()
                Xp, yp, _ = prepare_xy(pooled, "label")
                del pooled
                gc.collect()
                rows += run_arm(run, "litnet_pooled", "composite_synthetic",
                                Xp, yp, a.seeds)

        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        d = pd.DataFrame(rows)
        d.to_csv(out, index=False)
        run.declared_outputs.append(str(out))
        run.note("output_sha256", sha256_file(out))

        if "auc_pr" in d.columns:
            ok = d[d["auc_pr"].notna()]
            for (stream, method), g in ok.groupby(["stream", "method"]):
                for arm, gg in g.groupby("arm"):
                    print(f"  {stream:<20} {arm:<22} {method:<18} "
                          f"AUC-PR={gg['auc_pr'].mean():.4f} "
                          f"prev={gg['test_prevalence'].mean()*100:6.3f}% "
                          f"atk={int(gg['test_attacks'].mean())}")
        exc = d[d.get("excluded_reason").notna()] if "excluded_reason" in d.columns else d.iloc[0:0]
        for _, r in exc.iterrows():
            print(f"  EXCLUDED {r['stream']}/{r['arm']}/{r['method']}: {r['excluded_reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
