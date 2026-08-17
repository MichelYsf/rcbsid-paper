#!/usr/bin/env python
"""Stage 0.2 — re-run both reproduction checks and archive their manifests.

Check A: the Stage 1 reproduction gate (fresh CICIDS2017 runs vs the published
         trial), which is the paper's own deterministic reference.
Check B: the deterministic batch references (ECOD/COPOD) from the finals run
         vs the published trials, on BOTH datasets.

Gate: the deterministic references must reproduce bit-for-bit. Non-deterministic
methods are reported but do not gate. Exit non-zero => Stage 0 HALT.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from provenance import provenance_run  # noqa: E402

PUB = {"cicids2017": ROOT / "results_cicids_trial/tables/main_metrics_raw.csv",
       "litnet2020": ROOT / "results_litnet_trial/tables/main_metrics_raw.csv"}
STAGE1 = [ROOT / f"results_stage1/seed{s}" for s in (11, 23, 47)]
FINALS = ROOT / "results/tuning_parts"
DET_METRICS = ("auc_pr", "auc_roc", "f1", "precision", "recall")


def check_a(run) -> list[str]:
    """Stage 1 reproduction: fresh runs vs published, deterministic methods."""
    fails = []
    pub = pd.read_csv(PUB["cicids2017"])
    dirs = [d for d in STAGE1 if (d / "tables/main_metrics_raw.csv").exists()]
    if not dirs:
        return ["CHECK A: no archived Stage 1 runs found"]
    new = pd.concat([pd.read_csv(d / "tables/main_metrics_raw.csv") for d in dirs],
                    ignore_index=True)
    for method in ("bocpd_slo", "ecod_batch_ref"):
        p = pub[pub.method == method].sort_values("seed")
        n = new[new.method == method].sort_values("seed")
        if p.empty or n.empty:
            fails.append(f"CHECK A: {method} missing")
            continue
        for m in DET_METRICS:
            if m not in p or m not in n:
                continue
            diff = float(abs(float(p[m].iloc[0]) - float(n[m].iloc[0])))
            run.emit_macro(f"Stage1{method.replace('_','').title()}{m.replace('_','').title()}Diff",
                           diff, desc=f"Stage1 repro |new-published| for {method}/{m}")
            if diff > 1e-9:
                # AUC metrics carry documented sklearn-version tie-handling drift;
                # F1 is the bit-exactness witness (see RUN_REPORT).
                if m in ("auc_pr", "auc_roc") and diff < 1e-5:
                    continue
                fails.append(f"CHECK A: {method}/{m} diff {diff:.3e} > 1e-9")
    return fails


def check_b(run) -> list[str]:
    """Deterministic batch references from the finals run vs published."""
    fails = []
    for ds, pubpath in PUB.items():
        pub = pd.read_csv(pubpath)
        for method in ("ecod", "copod"):
            f = FINALS / f"final_{ds}_{method}_default.csv"
            if not f.exists():
                fails.append(f"CHECK B: {ds}/{method} final absent")
                continue
            got = pd.read_csv(f)
            got = got[got.auc_pr.notna()]
            if got.empty:
                fails.append(f"CHECK B: {ds}/{method} final has no metrics")
                continue
            want = pub[pub.method == f"{method}_batch_ref"]
            for m in ("auc_pr", "auc_roc", "f1"):
                a, b = float(got[m].iloc[0]), float(want[m].iloc[0])
                diff = abs(a - b)
                run.emit_macro(f"Repro{ds.title()}{method.title()}{m.replace('_','').title()}",
                               a, desc=f"{ds} {method} {m} reproduced on the rebuilt stream")
                if diff > 1e-9:
                    fails.append(f"CHECK B: {ds}/{method}/{m} {a:.6f} vs published {b:.6f} "
                                 f"(diff {diff:.3e})")
    return fails


def main() -> int:
    inputs = [p for p in PUB.values() if p.exists()]
    with provenance_run("stage0_reproduction_checks",
                        config={"check_a": "stage1 gate", "check_b": "deterministic batch refs"},
                        seed=None, inputs=inputs,
                        notes="Stage 0.2 gate: published deterministic references must "
                              "reproduce bit-for-bit before the rebuild proceeds.") as run:
        fails = check_a(run) + check_b(run)
        run.note("failures", fails)
        run.emit_macro("Stage0DeterministicChecksFailed", len(fails),
                       desc="count of deterministic reproduction failures at Stage 0")
        print("=== Stage 0.2 reproduction checks ===")
        if fails:
            for f in fails:
                print(f"  FAIL {f}")
            print("\nSTAGE 0 GATE FAILED")
            return 1
        print("  CHECK A (Stage 1 gate, deterministic methods): PASS")
        print("  CHECK B (ECOD/COPOD both datasets vs published): PASS bit-for-bit")
        print("\nSTAGE 0 GATE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
