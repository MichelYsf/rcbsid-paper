#!/usr/bin/env python
"""Generate findings_tuning.md from results/baseline_tuning.csv (mechanical)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results/baseline_tuning.csv"
OUT = ROOT / "findings_tuning.md"
DEFAULTS = {
    "litnet2020": ROOT / "results_litnet_trial/tables/main_metrics_raw.csv",
    "cicids2017": ROOT / "results_cicids_trial/tables/main_metrics_raw.csv",
}
STREAM_GROUP = ["hst", "loda", "rrcf", "iforest_asd", "kitnet", "xstream"]

t = pd.read_csv(CSV)
lines = ["# Findings: baseline tuning (Stage 3)", ""]
lines.append("Selection criterion: validation AUC-PR only — the same chronological "
             "validation split CALIBURN's calibration layer uses. Test labels were "
             "never read during selection. Reductions applied are logged in "
             "results/tuning_parts/reductions.json and RUN_REPORT.md.")
lines.append("")

for ds, dpath in DEFAULTS.items():
    if not dpath.exists():
        continue
    base = pd.read_csv(dpath)
    base = base[base["auc_pr"].notna()]
    tuned = t[(t["dataset"] == ds) & (t["phase"] == "final_tuned") & t["auc_pr"].notna()]
    if tuned.empty and ds != "litnet2020":
        lines.append(f"## {ds}: not tuned (reduction rung; documented defaults carried)")
        lines.append("")
        continue
    cal = base[base["method"] == "bocpd_slo"]["auc_pr"].mean()
    lines.append(f"## {ds}")
    lines.append("")
    lines.append("| baseline | default AUC-PR | tuned AUC-PR | delta | selected config |")
    lines.append("|---|---|---|---|---|")
    best_stream_tuned = -1.0
    best_stream_name = ""
    for method in sorted(tuned["method"].unique()):
        g = tuned[tuned["method"] == method]
        tv = float(g["auc_pr"].mean())
        key = method if method in base["method"].unique() else f"{method}_batch_ref"
        dv = float(base[base["method"] == key]["auc_pr"].mean()) if key in base["method"].unique() else float("nan")
        params = g["params"].iloc[0]
        lines.append(f"| {method} | {dv:.3f} | {tv:.3f} | {tv - dv:+.3f} | `{params}` |")
        if method in STREAM_GROUP and tv > best_stream_tuned:
            best_stream_tuned, best_stream_name = tv, method
    # untouched streaming methods keep defaults in the comparison group
    for method in STREAM_GROUP:
        if method in tuned["method"].unique():
            continue
        if method in base["method"].unique():
            dv = float(base[base["method"] == method]["auc_pr"].mean())
            if dv > best_stream_tuned:
                best_stream_tuned, best_stream_name = dv, f"{method} (default)"
    lines.append("")
    lead = cal - best_stream_tuned
    lines.append(f"CALIBURN (untuned, deterministic) AUC-PR: **{cal:.3f}**. Best "
                 f"streaming baseline after tuning: **{best_stream_name} "
                 f"{best_stream_tuned:.3f}**. Lead: **{lead:+.3f}** "
                 f"({cal / best_stream_tuned:.2f}x)." if best_stream_tuned > 0 else "")
    lines.append("")
    verdict = ("CALIBURN still leads the streaming group after symmetric tuning"
               if lead > 0 else
               "CALIBURN NO LONGER leads the streaming group after symmetric tuning")
    lines.append(f"**Verdict (mechanical, threshold = lead > 0) on {ds}: {verdict}.**")
    lines.append("")

n_crash = int(t[(t["phase"] == "grid")]["error"].fillna("").astype(bool).sum())
lines.append(f"Grid points that crashed and were dropped (logged): {n_crash}.")
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
