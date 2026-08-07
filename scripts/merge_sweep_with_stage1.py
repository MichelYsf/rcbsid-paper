#!/usr/bin/env python
"""Assemble results/prevalence_sweep_cicids.csv from sweep cell partials plus
the natural-level rows reused from Stage 1.

Reuse rationale (logged reduction): Stage 1 already ran the identical
protocol on the identical natural stream, and its LODA/HST/LOF/ECOD and
CALIBURN rows reproduced the published values bit-for-bit per seed — the
runner code paths invoked by the sweep harness are the same imported
functions, so recomputation would deterministically regenerate the same
numbers at ~27 core-hours cost. The natural-level BOCPD control cell IS
recomputed through the sweep harness (plus the V1/V3/V4 variant rows), which
is the internal control with actual verification power: its bocpd_slo row
must equal Stage 1 exactly. Reused rows carry provenance='stage1_reuse';
harness rows carry provenance='sweep_cell'.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

NATURAL_META = {
    # measured on the natural interleaved stream (build log + Stage 1)
    "level_target_pct": 22.06,
    "is_natural": True,
    "n_redraws": 0,
    "n_flows": 1_600_000,
    "achieved_train_prev": 240302 / 1_120_000,
    "achieved_val_prev": 52085 / 240_000,
    "achieved_test_prev": 60575 / 240_000,
}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--parts", default=str(ROOT / "results/sweep_parts"))
    p.add_argument("--stage1", nargs="*", default=[str(ROOT / f"results_stage1/seed{s}")
                                                  for s in (11, 23, 47)])
    p.add_argument("--out", default=str(ROOT / "results/prevalence_sweep_cicids.csv"))
    a = p.parse_args()

    parts = sorted(Path(a.parts).glob("*.csv"))
    if not parts:
        raise SystemExit(f"no sweep partials in {a.parts}")
    frames = [pd.read_csv(f) for f in parts]
    sweep = pd.concat(frames, ignore_index=True)
    sweep["provenance"] = "sweep_cell"

    reuse_rows = []
    for d in a.stage1:
        raw = pd.read_csv(Path(d) / "tables/main_metrics_raw.csv")
        raw = raw[raw["method"].isin(["loda", "hst", "lof_batch_ref", "ecod_batch_ref",
                                      "bocpd_slo"])]
        for _, r in raw.iterrows():
            row = r.to_dict()
            row.update(NATURAL_META)
            row["resample_seed"] = int(r["seed"])
            row["provenance"] = "stage1_reuse"
            reuse_rows.append(row)
    reuse = pd.DataFrame(reuse_rows)

    merged = pd.concat([sweep, reuse], ignore_index=True)
    merged = merged.sort_values(["level_target_pct", "method", "resample_seed"]).reset_index(drop=True)

    # Internal control: the harness-recomputed natural bocpd_slo row must
    # equal the Stage 1 (= published-pipeline) row exactly.
    ctrl = merged[(merged["method"] == "bocpd_slo") & (merged["is_natural"] == True)]  # noqa: E712
    cell = ctrl[ctrl["provenance"] == "sweep_cell"]
    ref = ctrl[ctrl["provenance"] == "stage1_reuse"]
    if not cell.empty and not ref.empty:
        for metric in ("auc_pr", "auc_roc", "f1", "precision", "recall", "brier"):
            diff = float(np.abs(cell[metric].iloc[0] - ref[metric].iloc[0]).max())
            status = "OK" if diff <= 1e-12 else "MISMATCH"
            print(f"control {metric}: harness={cell[metric].iloc[0]:.9f} "
                  f"stage1={ref[metric].iloc[0]:.9f} diff={diff:.2e} [{status}]")
            if diff > 1e-12:
                raise SystemExit("INTERNAL CONTROL FAILED — do not use the sweep CSV")
    else:
        print("WARNING: natural bocpd control rows incomplete; control not yet checkable")

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(a.out, index=False)
    print(f"wrote {a.out}: {len(merged)} rows "
          f"({(merged['provenance'] == 'stage1_reuse').sum()} reused from Stage 1)")


if __name__ == "__main__":
    main()
