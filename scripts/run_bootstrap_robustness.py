#!/usr/bin/env python
"""Block-length robustness of the event-block bootstrap (final read, item 4).

The referee-round intervals (run referee_bounded_analyses_20260906T182158_de69afab)
use moving blocks of 100 records, chosen to exceed the p90 attack run of 70.
This run recomputes every interval the paper reports at block lengths 250 and
2600 records, the second exceeding the longest attack run, from the same
archived per-record score dumps, with ECOD refit exactly as the referee run
refit it (benign-only training rows of the arm, PyOD defaults). Block 100 is
rerun first, with the same seed and the same call order, as a reproduction
check against the archived intervals. The detector is never re-run.

For each block length the conclusions the paper draws from its intervals are
re-evaluated: every margin interval lies above zero; the auxiliary-only
AUC-ROC interval lies entirely below 0.5; the tail-only interval lies entirely
above the deployed composition's on both metrics. A "conclusion change" is any
of those nine checks whose truth value differs from the archived block-100
run's, where all nine hold.

--dry-run exercises the whole code path with random ECOD scores and a handful
of resamples, writes no manifest and touches no index.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from provenance import MANIFEST_DIR, load_macro_index, provenance_run  # noqa: E402
from run_referee_analyses import (DUMPS, SRC, ap, roc, split_idx, bootstrap,  # noqa: E402
                                  fit_score_ecod)
from run_construction_contrast import TRAIN, VAL, interleave_by_day  # noqa: E402
from src.data.loaders import prepare_xy  # noqa: E402

ARCHIVED_RUN = "referee_bounded_analyses_20260906T182158_de69afab"
ARCHIVED_BLOCK = 100
OUT = ROOT / "findings_bootstrap_robustness.md"

# (result key as the referee run's bootstrap names it, macro stem, archived macro stem)
QUANTITIES = [
    ("FullNaturalFullMargin", "FullNaturalMargin", "RefBootFullNaturalMargin"),
    ("FullSyntheticFullMargin", "FullSyntheticMargin", "RefBootFullSyntheticMargin"),
    ("Shared240NaturalMargin", "Shared240NaturalMargin", "RefBootShared240NaturalMargin"),
    ("Shared78NaturalMargin", "Shared78NaturalMargin", "RefBootShared78NaturalMargin"),
    ("Shared240SyntheticMargin", "Shared240SyntheticMargin", "RefBootShared240SyntheticMargin"),
    ("Shared78SyntheticMargin", "Shared78SyntheticMargin", "RefBootShared78SyntheticMargin"),
    ("BranchCombinedAucpr", "BranchCombinedAucpr", "RefBootBranchCombinedAucpr"),
    ("BranchCombinedAucroc", "BranchCombinedAucroc", "RefBootBranchCombinedAucroc"),
    ("BranchTailOnlyAucpr", "BranchTailOnlyAucpr", "RefBootBranchTailOnlyAucpr"),
    ("BranchTailOnlyAucroc", "BranchTailOnlyAucroc", "RefBootBranchTailOnlyAucroc"),
    ("BranchAuxOnlyAucpr", "BranchAuxOnlyAucpr", "RefBootBranchAuxOnlyAucpr"),
    ("BranchAuxOnlyAucroc", "BranchAuxOnlyAucroc", "RefBootBranchAuxOnlyAucroc"),
    ("AuxAucrocMinusHalf", "AuxAucrocMinusHalf", "RefBootAuxAucrocMinusHalf"),
]
MARGINS = [q[0] for q in QUANTITIES[:6]]


class _DryRun:
    run_id = "DRY-RUN-NOT-MANIFESTED"

    def __init__(self):
        self.declared_inputs: list[str] = []
        self.macros: dict[str, object] = {}

    def emit_macro(self, macro, value, unit="", desc=""):
        self.macros[macro] = value
        return value


@contextlib.contextmanager
def _dry_run(*_a, **_kw):
    yield _DryRun()


def one_pass(L, B, y_te, det_te, ecod, y_sh, det_sh, nat, te):
    """The referee run's B stage, verbatim in call order, at block length L."""
    rng = np.random.default_rng(11)
    res = {}

    def run_boot(tag, m, stats):
        out = bootstrap(rng, m, L, B, stats)
        res.update({tag + k: v for k, v in out.items()})
        return out

    for name, dsign in (("Natural", -1), ("Synthetic", +1)):
        y_ = y_te[name]; d_ = det_te[name]; e_ = ecod[name]["full480"]
        run_boot("Full" + name, len(y_), {
            "FullMargin": (lambda idx, y_=y_, d_=d_, e_=e_, s=dsign:
                           s * (ap(y_[idx], d_[idx]) - ap(y_[idx], e_[idx])))})
    for name in ("Natural", "Synthetic"):
        for tag, e_ in (("240", ecod[name]["sh240"]), ("78", ecod[name]["sh78"])):
            d_ = det_sh[name]
            run_boot("Shared%s%s" % (tag, name), len(y_sh), {
                "Margin": (lambda idx, d_=d_, e_=e_:
                           ap(y_sh[idx], d_[idx]) - ap(y_sh[idx], e_[idx]))})
    y_ = y_te["Natural"]
    comps = {"Combined": nat["score"][te], "TailOnly": nat["tail"][te], "AuxOnly": nat["aux"][te]}
    stats = {}
    for nm, v in comps.items():
        stats[nm + "Aucpr"] = (lambda idx, v=v: ap(y_[idx], v[idx]))
        stats[nm + "Aucroc"] = (lambda idx, v=v: roc(y_[idx], v[idx]))
    run_boot("Branch", len(y_), stats)
    lo, hi, nb = res["BranchAuxOnlyAucroc"]
    res["AuxAucrocMinusHalf"] = (lo - 0.5, hi - 0.5, nb)
    return {k: (float(v[0]), float(v[1])) for k, v in res.items()}


def conclusions(r):
    """The nine checks the paper's conclusions rest on, as booleans."""
    c = {}
    for k in MARGINS:
        c[k + "AboveZero"] = r[k][0] > 0.0
    c["AuxBelowChanceEntireInterval"] = r["BranchAuxOnlyAucroc"][1] < 0.5
    c["TailAboveDeployedAucpr"] = r["BranchTailOnlyAucpr"][0] > r["BranchCombinedAucpr"][1]
    c["TailAboveDeployedAucroc"] = r["BranchTailOnlyAucroc"][0] > r["BranchCombinedAucroc"][1]
    return c


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--resamples", type=int, default=1000)
    p.add_argument("--blocks", type=int, nargs="+", default=[250, 2600])
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    t_start = time.time()

    archived_path = MANIFEST_DIR / (ARCHIVED_RUN + ".json")
    archived = json.loads(archived_path.read_text(encoding="utf-8"))["macros"]
    idx = load_macro_index()
    max_run = int(idx["StreamCicids2017RunMax"][-1]["value"])
    p90_run = int(idx["StreamCicids2017RunPninety"][-1]["value"])
    assert int(archived["RefBootBlockLength"]["value"]) == ARCHIVED_BLOCK
    assert int(archived["RefBootResamples"]["value"]) == 1000

    nat = np.load(DUMPS / "cicids_natural_scores.npz")
    syn = np.load(DUMPS / "cicids_synthetic_scores.npz")
    n = len(nat["score"])
    i_tr, i_va = split_idx(n)
    te = slice(i_va, n)

    nat_pos_te, syn_pos_te = nat["pos"][te], syn["pos"][te]
    shared = np.intersect1d(nat_pos_te, syn_pos_te)

    def restrict(dump, shared_set):
        pp = dump["pos"][te]
        m = np.isin(pp, shared_set)
        order = np.argsort(pp[m])
        return dump["y"][te][m][order], dump["score"][te][m][order], pp[m][order], m, order

    y_sh, s_sh_nat, p_a, m_nat, o_nat = restrict(nat, shared)
    _, s_sh_syn, p_b, m_syn, o_syn = restrict(syn, shared)
    assert np.array_equal(p_a, p_b)
    y_te = {"Natural": nat["y"][te], "Synthetic": syn["y"][te]}
    det_te = {"Natural": nat["score"][te], "Synthetic": syn["score"][te]}
    det_sh = {"Natural": s_sh_nat, "Synthetic": s_sh_syn}

    ecod = {}
    if a.dry_run:
        rng0 = np.random.default_rng(0)
        for name, m_sh, o_sh in (("Natural", m_nat, o_nat), ("Synthetic", m_syn, o_syn)):
            f240 = rng0.random(n - i_va)
            ecod[name] = {"full480": rng0.random(n - i_va), "sh240": f240[m_sh][o_sh],
                          "sh78": rng0.random(len(y_sh))}
    else:
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
        print("ECOD refits", flush=True)
        for name, Xa, ya, m_sh, o_sh in (("Natural", X_nat, y_nat, m_nat, o_nat),
                                         ("Synthetic", X_syn, y_syn, m_syn, o_syn)):
            full480 = fit_score_ecod(Xa, ya, i_tr, Xa[i_tr:])[i_va - i_tr:]
            full240 = fit_score_ecod(Xa, ya, i_tr, Xa[i_va:])
            X_shared = Xa[i_va:][m_sh][o_sh]
            sh78 = fit_score_ecod(Xa, ya, i_tr, X_shared)
            ecod[name] = {"full480": full480, "sh240": full240[m_sh][o_sh], "sh78": sh78}
        del X_nat, X_syn

    runner = _dry_run if a.dry_run else provenance_run
    blocks = [ARCHIVED_BLOCK] + [int(b) for b in a.blocks]
    with runner(
        "bootstrap_block_robustness",
        config={"blocks": blocks, "resamples": a.resamples, "seed": 11,
                "archived_run": ARCHIVED_RUN, "archived_block": ARCHIVED_BLOCK,
                "metric": "sklearn average_precision_score / roc_auc_score, positive class 1",
                "train": TRAIN, "val": VAL},
        seed=11,
        notes="final-read item 4: every reported interval recomputed at block lengths "
              + ", ".join(str(b) for b in a.blocks) + "; block 100 rerun as reproduction "
              "check; ECOD refit as in the referee run; no detector rerun",
    ) as run:
        for f in (DUMPS / "cicids_natural_scores.npz", DUMPS / "cicids_synthetic_scores.npz",
                  SRC, archived_path):
            run.declared_inputs.append(str(f))

        results = {}
        for L in blocks:
            print("bootstrap, block %d" % L, flush=True)
            results[L] = one_pass(L, a.resamples, y_te, det_te, ecod, y_sh, det_sh, nat, te)

        # reproduction of the archived block-100 intervals
        deltas = []
        for key, stem, arch in QUANTITIES:
            lo, hi = results[ARCHIVED_BLOCK][key]
            alo = float(archived[arch + "Lo"]["value"]); ahi = float(archived[arch + "Hi"]["value"])
            deltas.append(max(abs(round(lo, 6) - alo), abs(round(hi, 6) - ahi)))
        max_delta = max(deltas)
        reproduced = 1 if (max_delta == 0.0 and not a.dry_run) else 0
        run.emit_macro("RefBootRobustBlockHundredReproduced", reproduced,
                       desc="1 if rerunning block 100 with the archived seed reproduces every archived interval bound to six decimals")
        run.emit_macro("RefBootRobustBlockHundredMaxAbsDelta", round(max_delta, 6),
                       desc="largest absolute difference between a rerun block-100 interval bound and the archived one")

        base = conclusions(results[ARCHIVED_BLOCK])
        assert all(base.values()) or a.dry_run, base
        total_changes = 0
        for L in a.blocks:
            r = results[L]
            for key, stem, arch in QUANTITIES:
                lo, hi = r[key]
                unit_desc = "AUC-ROC" if "Aucroc" in key or "MinusHalf" in key else "AUC-PR"
                run.emit_macro("RefBootB%d%sLo" % (L, stem), round(lo, 6),
                               desc="2.5th percentile of %s (%s), block length %d" % (stem, unit_desc, L))
                run.emit_macro("RefBootB%d%sHi" % (L, stem), round(hi, 6),
                               desc="97.5th percentile of %s (%s), block length %d" % (stem, unit_desc, L))
            c = conclusions(r)
            changes = sum(1 for k in base if c[k] != base[k])
            total_changes += changes
            run.emit_macro("RefBootB%dConclusionChanges" % L, changes,
                           desc="of the nine interval-based checks, how many differ from the archived block-100 run at block length %d" % L)
            run.emit_macro("RefBootB%dAllMarginsAboveZero" % L, 1 if all(c[k + "AboveZero"] for k in MARGINS) else 0,
                           desc="1 if all six margin intervals lie above zero at block length %d" % L)
            run.emit_macro("RefBootB%dAuxBelowChanceEntireInterval" % L, 1 if c["AuxBelowChanceEntireInterval"] else 0,
                           desc="1 if the auxiliary-only AUC-ROC interval lies entirely below 0.5 at block length %d" % L)
            run.emit_macro("RefBootB%dTailAboveDeployedAucpr" % L, 1 if c["TailAboveDeployedAucpr"] else 0,
                           desc="1 if the tail-only AUC-PR interval lies entirely above the deployed composition's at block length %d" % L)
            run.emit_macro("RefBootB%dTailAboveDeployedAucroc" % L, 1 if c["TailAboveDeployedAucroc"] else 0,
                           desc="1 if the tail-only AUC-ROC interval lies entirely above the deployed composition's at block length %d" % L)

        run.emit_macro("RefBootRobustBlockLengthA", int(a.blocks[0]), desc="first robustness block length, records")
        run.emit_macro("RefBootRobustBlockLengthB", int(a.blocks[-1]), desc="second robustness block length, records")
        run.emit_macro("RefBootRobustIntervals", len(QUANTITIES), desc="intervals recomputed per block length")
        run.emit_macro("RefBootRobustConclusionChanges", total_changes,
                       desc="conclusion changes summed over the robustness block lengths")
        run.emit_macro("RefBootRobustLongestBlockExceedsMaxRun", 1 if int(a.blocks[-1]) > max_run else 0,
                       desc="1 if the longest robustness block exceeds the longest attack run (%d records)" % max_run)
        wall = int(time.time() - t_start)
        run.emit_macro("RefBootRobustWallSeconds", wall, unit="s", desc="wall time of this run")

        L_ = []
        A = L_.append
        A("# findings_bootstrap_robustness — block-length robustness of every reported interval")
        A("")
        A("Generating run: `" + run.run_id + "`. Archived intervals: `" + ARCHIVED_RUN + "` "
          "(block %d, p90 attack run %d, max attack run %d). Every number is a provenance macro."
          % (ARCHIVED_BLOCK, p90_run, max_run))
        A("")
        hdr = "| quantity | archived, block %d | rerun, block %d |" % (ARCHIVED_BLOCK, ARCHIVED_BLOCK)
        hdr += "".join(" block %d |" % L for L in a.blocks)
        A(hdr)
        A("|---|---|---|" + "---|" * len(a.blocks))
        for key, stem, arch in QUANTITIES:
            row = "| %s | [%.6f, %.6f] | [%.6f, %.6f] |" % (
                stem, float(archived[arch + "Lo"]["value"]), float(archived[arch + "Hi"]["value"]),
                results[ARCHIVED_BLOCK][key][0], results[ARCHIVED_BLOCK][key][1])
            row += "".join(" [%.6f, %.6f] |" % results[L][key] for L in a.blocks)
            A(row)
        A("")
        A("Block-%d reproduction: %s (largest absolute deviation of a bound %.6f)."
          % (ARCHIVED_BLOCK, "exact to six decimals" if reproduced else "NOT exact", max_delta))
        A("")
        A("| check |" + "".join(" block %d |" % L for L in blocks))
        A("|---|" + "---|" * len(blocks))
        for k in base:
            A("| %s |" % k + "".join(" %s |" % ("yes" if conclusions(results[L])[k] else "NO") for L in blocks))
        A("")
        A("Conclusion changes across block lengths %s: **%d** of %d checks."
          % (", ".join(str(b) for b in a.blocks), total_changes, len(base) * len(a.blocks)))
        A("")
        A("Wall time: %d s." % wall)
        out = OUT if not a.dry_run else ROOT / "results" / "_dryrun" / OUT.name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(L_) + "\n", encoding="utf-8")
        print("wrote", out, flush=True)
    print("done in %ds" % int(time.time() - t_start), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
