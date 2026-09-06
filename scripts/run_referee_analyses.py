#!/usr/bin/env python
"""Bounded analyses answering the hostile referee report, from archived data
only. The detector is never re-run: every detector number comes from the
per-record score dumps written by run_arm_score_dump.py. ECOD is deterministic
and is refit where an analysis requires it, exactly as the contrast fits it
(benign-only training rows of the arm).

  A  ECOD BATCH-CONTROLLED RESCORING (referee BLOCKING 2). The archived
     shared-record ECOD values were produced by scoring each arm's full
     240000-record held-out slice and then restricting to the 78000 shared
     records, so the two arms' ECOD numbers carry batches of equal size but
     different composition. Here the 78000 shared records are scored as their
     own batch under each arm's fitted model, so both arms' ECOD numbers carry
     the identical batch. Both sets are reported.
  B  EVENT-BLOCK BOOTSTRAP (MAJOR 2). Moving blocks of L records, L chosen to
     exceed the p90 attack run of the labelled stream, 1000 resamples, seed
     11. Percentile intervals for the Section 5.3 margins, the Table 5
     margins, the Table 6 branch values, and the auxiliary AUC-ROC against
     0.5.
  C  RELOCATION DESTINATIONS (MAJOR 7). From the archived split positions:
     of the attacks that leave the held-out slice under day round robin, how
     many land in training and how many in validation.
  D  IMPUTATION COUNTS (MAJOR 10). Rows and features touched by the
     +-inf -> NaN and NaN -> 0 mapping, per stream, from the stream files.
  E  PAIRED CUT-BY-ASSEMBLY SWEEP (MAJOR 3). The seven chronological cuts of
     A2 repeated on BOTH arms, ECOD refit per arm and cut.

Every metric uses the paper's implementation: sklearn average_precision_score
and roc_auc_score, positive class 1. Derived margins are computed from
REPORTED operand values (rule 9).
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from provenance import provenance_run, reported  # noqa: E402
from run_construction_contrast import TRAIN, VAL, interleave_by_day  # noqa: E402
from src.baselines.batch import run_batch_reference  # noqa: E402
from src.data.loaders import prepare_xy  # noqa: E402

DUMPS = ROOT / "results/score_dumps"
RAW = ROOT / "data/raw/natural"
SRC = RAW / "cicids2017_natural.csv"
STREAMS = {
    "Cicids": SRC,
    "LitnetUdpFlood": RAW / "litnet2020_udp_flood_natural.csv",
    "LitnetBlasterWorm": RAW / "litnet2020_blaster_worm_natural.csv",
    "LitnetSpam": RAW / "litnet2020_spam_natural.csv",
}
OUT = ROOT / "findings_referee_analyses.md"

ARCHIVED = {  # reproduction targets, from the archived manifests
    "nat_ecod_full": 0.755142, "syn_ecod_full": 0.418966,
    "nat_det_full": 0.728337, "syn_det_full": 0.544998,
    "moved_attacks": 103189, "p90_run": 70,
}


def ap(y, s):
    return float(average_precision_score(y, s)) if len(set(y.tolist())) > 1 else float("nan")


def roc(y, s):
    return float(roc_auc_score(y, s)) if len(set(y.tolist())) > 1 else float("nan")


def split_idx(n):
    i_tr = int(TRAIN * n)
    return i_tr, i_tr + int(VAL * n)


def block_indices(rng, m, L, nb):
    starts = rng.integers(0, m - L + 1, size=nb)
    return (starts[:, None] + np.arange(L)[None, :]).ravel()[:m]


def bootstrap(rng, m, L, B, stats):
    """stats: dict name -> callable(idx) -> float. Returns name -> (lo, hi)."""
    nb = math.ceil(m / L)
    draws = {k: [] for k in stats}
    for _ in range(B):
        idx = block_indices(rng, m, L, nb)
        for k, f in stats.items():
            v = f(idx)
            if not math.isnan(v):
                draws[k].append(v)
    return {k: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)), len(v))
            for k, v in draws.items()}


def fit_score_ecod(X_arm, y_arm, i_tr, X_batch):
    Xtr, ytr = X_arm[:i_tr], y_arm[:i_tr]
    Xfit = Xtr[ytr == 0] if np.any(ytr == 0) else Xtr
    return np.asarray(run_batch_reference("ecod", Xfit, X_batch, seed=11,
                                          allow_fallback=False))


def impute_counts(path: Path, label: str) -> dict:
    """Chunked pass: rows/features touched by +-inf and by NaN, as prepare_xy
    sees them (numeric columns only, label dropped)."""
    inf_rows = nan_rows = any_rows = rows = 0
    inf_cols: set = set()
    nan_cols: set = set()
    inf_cells = nan_cells = 0
    n_feat = None
    for chunk in pd.read_csv(path, low_memory=False, chunksize=200_000):
        X = chunk.drop(columns=[label]).select_dtypes(include=[np.number])
        if n_feat is None:
            n_feat = X.shape[1]
        A = X.to_numpy(dtype=float)
        isinf = np.isinf(A)
        isnan = np.isnan(A)
        inf_cells += int(isinf.sum()); nan_cells += int(isnan.sum())
        r_inf = isinf.any(axis=1); r_nan = isnan.any(axis=1)
        inf_rows += int(r_inf.sum()); nan_rows += int(r_nan.sum())
        any_rows += int((r_inf | r_nan).sum())
        inf_cols.update(np.flatnonzero(isinf.any(axis=0)).tolist())
        nan_cols.update(np.flatnonzero(isnan.any(axis=0)).tolist())
        rows += len(A)
    return {"rows": rows, "features": n_feat, "inf_rows": inf_rows, "nan_rows": nan_rows,
            "affected_rows": any_rows, "inf_features": len(inf_cols),
            "nan_features": len(nan_cols), "inf_cells": inf_cells, "nan_cells": nan_cells,
            "affected_features": len(inf_cols | nan_cols)}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--resamples", type=int, default=1000)
    p.add_argument("--block", type=int, default=100)
    p.add_argument("--cuts", type=int, default=7)
    p.add_argument("--skip-e", action="store_true")
    a = p.parse_args()
    t_start = time.time()

    nat = np.load(DUMPS / "cicids_natural_scores.npz")
    syn = np.load(DUMPS / "cicids_synthetic_scores.npz")
    n = len(nat["score"])
    i_tr, i_va = split_idx(n)
    te = slice(i_va, n)

    print("loading design matrix", flush=True)
    df = pd.read_csv(SRC, low_memory=False)
    df["_pos"] = np.arange(len(df))
    X_nat, y_nat, _ = prepare_xy(df.drop(columns=["_pos"]), "label")
    di = interleave_by_day(df)
    pos_syn = di["_pos"].to_numpy().astype(np.int64)
    del df, di
    assert np.array_equal(pos_syn, syn["pos"]), "synthetic permutation mismatch"
    X_syn, y_syn = X_nat[pos_syn], y_nat[pos_syn]
    assert np.array_equal(y_syn, syn["y"]) and np.array_equal(y_nat, nat["y"])

    with provenance_run(
        "referee_bounded_analyses",
        config={"A": "ECOD rescoring of the shared records as their own batch, per arm",
                "B": "moving-block bootstrap, block %d records, %d resamples, seed 11"
                     % (a.block, a.resamples),
                "C": "relocation destinations of attacks leaving the held-out slice",
                "D": "imputation counts per stream, numeric columns, label dropped",
                "E": "paired cut-by-assembly sweep, %d cuts, both arms" % a.cuts,
                "metric": "sklearn average_precision_score / roc_auc_score, positive class 1",
                "train": TRAIN, "val": VAL},
        seed=11,
        notes="hostile-referee triage: BLOCKING 2, MAJOR 2, 3, 7, 10, from archived "
              "dumps and stream files; no detector rerun",
    ) as run:
        for f in (DUMPS / "cicids_natural_scores.npz", DUMPS / "cicids_synthetic_scores.npz",
                  *STREAMS.values()):
            run.declared_inputs.append(str(f))
        L = []
        A = L.append
        A("# findings_referee_analyses — A to E (hostile-referee triage)")
        A("")
        A("Generating run: `" + run.run_id + "`. Every number is a provenance macro.")
        A("")

        # ---- shared records and archived alignment ---------------------------
        nat_pos_te, syn_pos_te = nat["pos"][te], syn["pos"][te]
        shared = np.intersect1d(nat_pos_te, syn_pos_te)          # sorted by natural pos

        def restrict(dump, shared_set):
            pp = dump["pos"][te]
            m = np.isin(pp, shared_set)
            order = np.argsort(pp[m])
            return dump["y"][te][m][order], dump["score"][te][m][order], pp[m][order], m, order

        y_sh, s_sh_nat, p_a, m_nat, o_nat = restrict(nat, shared)
        _, s_sh_syn, p_b, m_syn, o_syn = restrict(syn, shared)
        assert np.array_equal(p_a, p_b)
        run.emit_macro("RefSharedRecords", int(len(shared)), desc="records held out by both arms")

        # ---- ECOD per arm: 480000-batch (contrast), 240000-batch (Table 5) and
        #      78000-batch (this analysis) ----------------------------------------
        print("A: ECOD refits", flush=True)
        ecod = {}
        for name, Xa, ya, dump, m_sh, o_sh in (("Natural", X_nat, y_nat, nat, m_nat, o_nat),
                                               ("Synthetic", X_syn, y_syn, syn, m_syn, o_syn)):
            # (i) the contrast's own call: validation-plus-test batch, test part kept
            full480 = fit_score_ecod(Xa, ya, i_tr, Xa[i_tr:])[i_va - i_tr:]
            # (ii) Table 5's call: the 240000-record test slice as the batch
            full240 = fit_score_ecod(Xa, ya, i_tr, Xa[i_va:])
            # (iii) batch-controlled: the 78000 shared records as their own batch
            X_shared = Xa[i_va:][m_sh][o_sh]        # the shared records, natural-pos order
            sh78 = fit_score_ecod(Xa, ya, i_tr, X_shared)
            ecod[name] = {"full480": full480, "full240": full240,
                          "sh240": full240[m_sh][o_sh], "sh78": sh78}
        y_te = {"Natural": nat["y"][te], "Synthetic": syn["y"][te]}
        det_te = {"Natural": nat["score"][te], "Synthetic": syn["score"][te]}
        det_sh = {"Natural": s_sh_nat, "Synthetic": s_sh_syn}

        # reproduction of the archived contrast and Table 5 values
        repro = {}
        for name in ("Natural", "Synthetic"):
            repro[name] = {"ecod_full": ap(y_te[name], ecod[name]["full480"]),
                           "det_full": ap(y_te[name], det_te[name]),
                           "ecod_sh240": ap(y_sh, ecod[name]["sh240"]),
                           "det_sh": ap(y_sh, det_sh[name])}
        run.emit_macro("RefReproNaturalEcodFullAucpr", round(repro["Natural"]["ecod_full"], 6),
                       desc="ECOD AUC-PR, natural held-out slice, refit here in the contrast's 480000-record batch")
        run.emit_macro("RefReproSyntheticEcodFullAucpr", round(repro["Synthetic"]["ecod_full"], 6),
                       desc="ECOD AUC-PR, synthetic held-out slice, refit here in the contrast's 480000-record batch")

        A("## A — ECOD on the shared records, batch-controlled")
        A("")
        A("| arm | ECOD AUC-PR, 240000-record batch (Table 5) | ECOD AUC-PR, 78000-record batch (own batch) | detector AUC-PR | margin det minus ECOD (240000) | margin det minus ECOD (78000) |")
        A("|---|---|---|---|---|---|")
        for name in ("Natural", "Synthetic"):
            e240 = ap(y_sh, ecod[name]["sh240"]); e78 = ap(y_sh, ecod[name]["sh78"])
            r240 = roc(y_sh, ecod[name]["sh240"]); r78 = roc(y_sh, ecod[name]["sh78"])
            d = ap(y_sh, det_sh[name])
            run.emit_macro("RefEcodShared240" + name + "Aucpr", round(e240, 6),
                           desc="ECOD AUC-PR on the shared records, %s arm, scored in the 240000-record held-out batch (reproduces Table 5)" % name.lower())
            run.emit_macro("RefEcodShared78" + name + "Aucpr", round(e78, 6),
                           desc="ECOD AUC-PR on the shared records, %s arm, scored as their own 78000-record batch" % name.lower())
            run.emit_macro("RefEcodShared78" + name + "Aucroc", round(r78, 6),
                           desc="ECOD AUC-ROC on the shared records, %s arm, own 78000-record batch" % name.lower())
            run.emit_macro("RefEcodShared240" + name + "Aucroc", round(r240, 6),
                           desc="ECOD AUC-ROC on the shared records, %s arm, 240000-record batch" % name.lower())
            run.emit_macro("RefMarginShared78" + name, round(reported(d) - reported(e78), 6),
                           desc="detector minus ECOD AUC-PR on the shared records, %s arm, ECOD in its own 78000-record batch" % name.lower())
            run.emit_macro("RefMarginShared240" + name, round(reported(d) - reported(e240), 6),
                           desc="detector minus ECOD AUC-PR on the shared records, %s arm, ECOD in the 240000-record batch" % name.lower())
            A("| %s | %.6f | %.6f | %.6f | %.6f | %.6f |" % (name.lower(), e240, e78, d,
                                                        reported(d) - reported(e240), reported(d) - reported(e78)))
        e78n, e78s = ap(y_sh, ecod["Natural"]["sh78"]), ap(y_sh, ecod["Synthetic"]["sh78"])
        run.emit_macro("RefEcodShared78CrossArmSpread", round(abs(reported(e78n) - reported(e78s)), 6),
                       desc="ECOD AUC-PR difference between arms on the identical 78000-record batch (history-only difference for ECOD)")
        both_lead = (ap(y_sh, det_sh["Natural"]) > e78n) and (ap(y_sh, det_sh["Synthetic"]) > e78s)
        run.emit_macro("RefDetectorLeadsBothArmsBatchControlled", 1 if both_lead else 0,
                       desc="1 if the detector leads ECOD in both arms on the shared records with ECOD batch-controlled")
        A("")

        # ---- B: event-block bootstrap ---------------------------------------------
        print("B: bootstrap", flush=True)
        run.emit_macro("RefBootBlockLength", int(a.block),
                       desc="moving-block length in records; exceeds the p90 attack run of %d" % ARCHIVED["p90_run"])
        run.emit_macro("RefBootResamples", int(a.resamples), desc="bootstrap resamples")
        rng = np.random.default_rng(11)
        results = {}

        def run_boot(tag, m, stats):
            out = bootstrap(rng, m, a.block, a.resamples, stats)
            results.update({tag + k: v for k, v in out.items()})
            return out

        # full held-out slices, arm order (history order)
        for name, dsign in (("Natural", -1), ("Synthetic", +1)):
            y_ = y_te[name]; d_ = det_te[name]; e_ = ecod[name]["full480"]
            stats = {
                "FullMargin": (lambda idx, y_=y_, d_=d_, e_=e_, s=dsign: s * (ap(y_[idx], d_[idx]) - ap(y_[idx], e_[idx]))),
            }
            out = run_boot("Full" + name, len(y_), stats)
            point = dsign * (reported(ap(y_, d_)) - reported(ap(y_, e_)))
            lo, hi, nb = out["FullMargin"]
            label = "ECOD minus detector" if dsign < 0 else "detector minus ECOD"
            run.emit_macro("RefBootFull%sMarginPoint" % name, round(point, 6),
                           desc="%s AUC-PR margin on the %s held-out slice, from reported values" % (label, name.lower()))
            run.emit_macro("RefBootFull%sMarginLo" % name, round(lo, 6), desc="2.5th percentile of that margin, block bootstrap")
            run.emit_macro("RefBootFull%sMarginHi" % name, round(hi, 6), desc="97.5th percentile of that margin, block bootstrap")
            run.emit_macro("RefBootFull%sMarginCrossesZero" % name, 1 if lo <= 0.0 <= hi else 0,
                           desc="1 if the bootstrap interval of that margin includes zero")

        # shared records, natural-position order, both ECOD batches
        for name in ("Natural", "Synthetic"):
            for tag, e_ in (("240", ecod[name]["sh240"]), ("78", ecod[name]["sh78"])):
                d_ = det_sh[name]
                out = run_boot("Shared%s%s" % (tag, name), len(y_sh), {
                    "Margin": (lambda idx, d_=d_, e_=e_: ap(y_sh[idx], d_[idx]) - ap(y_sh[idx], e_[idx]))})
                lo, hi, nb = out["Margin"]
                run.emit_macro("RefBootShared%s%sMarginLo" % (tag, name), round(lo, 6),
                               desc="2.5th percentile, detector minus ECOD on the shared records, %s arm, ECOD %s-batch" % (name.lower(), "240000" if tag == "240" else "78000"))
                run.emit_macro("RefBootShared%s%sMarginHi" % (tag, name), round(hi, 6),
                               desc="97.5th percentile of the same margin")
                run.emit_macro("RefBootShared%s%sMarginCrossesZero" % (tag, name), 1 if lo <= 0.0 <= hi else 0,
                               desc="1 if that interval includes zero")

        # branch values on the natural held-out slice
        y_ = y_te["Natural"]
        comps = {"Combined": nat["score"][te], "TailOnly": nat["tail"][te], "AuxOnly": nat["aux"][te]}
        stats = {}
        for nm, v in comps.items():
            stats[nm + "Aucpr"] = (lambda idx, v=v: ap(y_[idx], v[idx]))
            stats[nm + "Aucroc"] = (lambda idx, v=v: roc(y_[idx], v[idx]))
        out = run_boot("Branch", len(y_), stats)
        for nm in comps:
            for met in ("Aucpr", "Aucroc"):
                lo, hi, nb = out[nm + met]
                run.emit_macro("RefBootBranch%s%sLo" % (nm, met), round(lo, 6),
                               desc="2.5th percentile of %s %s on the natural held-out slice" % (nm, met))
                run.emit_macro("RefBootBranch%s%sHi" % (nm, met), round(hi, 6),
                               desc="97.5th percentile of %s %s on the natural held-out slice" % (nm, met))
        lo, hi, _ = out["AuxOnlyAucroc"]
        run.emit_macro("RefBootAuxAucrocMinusHalfLo", round(lo - 0.5, 6),
                       desc="2.5th percentile of auxiliary-only AUC-ROC minus 0.5")
        run.emit_macro("RefBootAuxAucrocMinusHalfHi", round(hi - 0.5, 6),
                       desc="97.5th percentile of auxiliary-only AUC-ROC minus 0.5")
        run.emit_macro("RefBootAuxBelowChanceEntireInterval", 1 if hi < 0.5 else 0,
                       desc="1 if the whole auxiliary-only AUC-ROC interval lies below 0.5")

        A("## B — event-block bootstrap (block %d, %d resamples)" % (a.block, a.resamples))
        A("")
        A("| quantity | 2.5% | 97.5% |")
        A("|---|---|---|")
        for k, (lo, hi, nb) in results.items():
            A("| %s | %.6f | %.6f |" % (k, lo, hi))
        A("")

        # ---- C: relocation destinations ---------------------------------------------
        print("C: relocation", flush=True)
        inv = np.empty(n, dtype=np.int64); inv[syn["pos"]] = np.arange(n)
        att_nat_te = nat_pos_te[nat["y"][te] == 1]
        moved = np.setdiff1d(att_nat_te, syn_pos_te)
        dest = inv[moved]
        to_tr = int((dest < i_tr).sum()); to_va = int(((dest >= i_tr) & (dest < i_va)).sum())
        assert to_tr + to_va == len(moved) and len(moved) == ARCHIVED["moved_attacks"], (to_tr, to_va, len(moved))
        run.emit_macro("RefRelocatedAttacks", int(len(moved)), desc="attacks in the natural held-out slice that the round-robin arm does not hold out")
        run.emit_macro("RefRelocatedToTraining", to_tr, desc="of those, landing in the round-robin training split")
        run.emit_macro("RefRelocatedToValidation", to_va, desc="of those, landing in the round-robin validation split")
        A("## C — where the relocated attacks land")
        A("")
        A("Of the %d attacks that leave the held-out slice under day round robin, **%d** land in training and **%d** in validation." % (len(moved), to_tr, to_va))
        A("")

        # ---- D: imputation counts ------------------------------------------------------
        print("D: imputation counts", flush=True)
        del X_syn
        A("## D — rows and features touched by the infinity and NaN mapping")
        A("")
        A("| stream | rows | numeric features | rows with +-inf | features with +-inf | rows with NaN | features with NaN | rows affected | features affected |")
        A("|---|---|---|---|---|---|---|---|---|")
        for key, path in STREAMS.items():
            c = impute_counts(path, "label")
            for k, v in c.items():
                run.emit_macro("RefImpute%s%s" % (key, "".join(w.capitalize() for w in k.split("_"))), int(v),
                               desc="%s: %s (numeric columns after dropping the label)" % (key, k.replace("_", " ")))
            A("| %s | %d | %d | %d | %d | %d | %d | %d | %d |" % (key, c["rows"], c["features"], c["inf_rows"], c["inf_features"], c["nan_rows"], c["nan_features"], c["affected_rows"], c["affected_features"]))
        A("")

        # ---- E: paired cut-by-assembly sweep -------------------------------------------
        if not a.skip_e:
            print("E: paired sweep", flush=True)
            X_syn = X_nat[pos_syn]
            cuts = np.linspace(0.60, 0.90, a.cuts)
            A("## E — paired cut-by-assembly sweep")
            A("")
            A("| cut | natural: detector | natural: ECOD | natural: ECOD leads | synthetic: detector | synthetic: ECOD | synthetic: ECOD leads | orderings agree |")
            A("|---|---|---|---|---|---|---|---|")
            agree = 0
            for c in cuts:
                cut = int(c * n); tag = "RefPairedCut%d" % int(round(100 * c))
                tr_end = int(TRAIN / (TRAIN + VAL) * cut)
                row = {}
                for name, Xa, ya, dump in (("Natural", X_nat, y_nat, nat), ("Synthetic", X_syn, y_syn, syn)):
                    y_t = dump["y"][cut:]
                    d_ap = ap(y_t, dump["score"][cut:])
                    ytr = ya[:tr_end]
                    Xfit = Xa[:tr_end][ytr == 0] if np.any(ytr == 0) else Xa[:tr_end]
                    e_ap = ap(y_t, np.asarray(run_batch_reference("ecod", Xfit, Xa[cut:], seed=11, allow_fallback=False)))
                    run.emit_macro(tag + name + "DetectorAucpr", round(d_ap, 6), desc="detector AUC-PR at the %d%% cut, %s arm" % (int(round(100 * c)), name.lower()))
                    run.emit_macro(tag + name + "EcodAucpr", round(e_ap, 6), desc="ECOD AUC-PR at the %d%% cut, %s arm, refit on that arm's prefix" % (int(round(100 * c)), name.lower()))
                    run.emit_macro(tag + name + "Prevalence", round(float(np.mean(y_t)), 6), desc="held-out prevalence at the %d%% cut, %s arm" % (int(round(100 * c)), name.lower()))
                    row[name] = (d_ap, e_ap, e_ap > d_ap)
                same = row["Natural"][2] == row["Synthetic"][2]
                agree += int(same)
                run.emit_macro(tag + "OrderingsAgree", 1 if same else 0, desc="1 if ECOD-versus-detector ordering is the same in both arms at the %d%% cut" % int(round(100 * c)))
                A("| %.0f%% | %.6f | %.6f | %s | %.6f | %.6f | %s | %s |" % (100 * c, row["Natural"][0], row["Natural"][1], "yes" if row["Natural"][2] else "no", row["Synthetic"][0], row["Synthetic"][1], "yes" if row["Synthetic"][2] else "no", "yes" if same else "no"))
            run.emit_macro("RefPairedCuts", int(len(cuts)), desc="chronological cut points evaluated in both arms")
            run.emit_macro("RefPairedCutsOrderingsAgree", int(agree), desc="cut points at which both arms show the same ECOD-versus-detector ordering")
            run.emit_macro("RefPairedCutsOrderingsDiffer", int(len(cuts) - agree), desc="cut points at which the two arms show opposite orderings")
            A("")

        run.emit_macro("RefWallSeconds", int(time.time() - t_start), unit="s", desc="wall time of this run")
        OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
        run.declared_outputs.append(str(OUT)) if hasattr(run, "declared_outputs") else None
    print("done in %.0fs -> %s" % (time.time() - t_start, OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
