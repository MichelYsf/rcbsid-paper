#!/usr/bin/env python
"""Generate findings_prevalence.md from results/prevalence_sweep_cicids.csv.

Every number is computed from the CSV; the verdicts are mechanical
comparisons stated with their thresholds, no massaging in either direction.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results/prevalence_sweep_cicids.csv"
OUT = ROOT / "findings_prevalence.md"

df = pd.read_csv(CSV)
df = df[df["auc_pr"].notna()]
STREAMING = ["loda", "hst"]
BATCH = ["lof_batch_ref", "ecod_batch_ref"]

agg = df.groupby(["level_target_pct", "method"]).agg(
    auc_pr=("auc_pr", "mean"), auc_pr_std=("auc_pr", "std"),
    f1=("f1", "mean"), alert_rate=("alert_rate", "mean"),
    test_fpr=("test_fpr", "mean"), crc_tau=("crc_tau", "mean"),
    brier_raw=("brier_raw", "mean"), brier_iso=("brier_iso", "mean"),
).reset_index()
levels = sorted(agg["level_target_pct"].unique())


def get(lvl, method, col):
    s = agg[(agg["level_target_pct"] == lvl) & (agg["method"] == method)][col]
    return float(s.iloc[0]) if len(s) else float("nan")


lines = ["# Findings: prevalence sweep within CICIDS2017 (Stage 2)", ""]
lines.append("The paper's regime-dependence claim confounds attack prevalence with "
             "dataset identity. This experiment holds the dataset fixed (the same "
             "interleaved corrected CICIDS2017 stream) and varies prevalence by "
             "stratified resampling: 5, 10, 22.06 (natural), 40, 64 percent, three "
             "resample seeds (11/23/47). CALIBURN is deterministic; the variance "
             "source is the resampling draw.")
lines.append("")
lines.append("## Headline table (AUC-PR, mean over resample seeds)")
lines.append("")
lines.append("| prevalence | CALIBURN (raw) | best streaming | best batch | chance floor |")
lines.append("|---|---|---|---|---|")
rows = {}
for lvl in levels:
    cal = get(lvl, "bocpd_slo", "auc_pr")
    stream_best = max(STREAMING, key=lambda m: get(lvl, m, "auc_pr") or -1)
    batch_best = max(BATCH, key=lambda m: get(lvl, m, "auc_pr") or -1)
    sb, bb = get(lvl, stream_best, "auc_pr"), get(lvl, batch_best, "auc_pr")
    rows[lvl] = (cal, stream_best, sb, batch_best, bb)
    lines.append(f"| {lvl:g}% | {cal:.3f} | {sb:.3f} ({stream_best}) | "
                 f"{bb:.3f} ({batch_best.replace('_batch_ref','')}) | {lvl / 100:.3f} |")
lines.append("")

lo, hi = levels[0], levels[-1]
nat = min(levels, key=lambda l: abs(l - 22.06))

# Question 1: does the low-prevalence advantage reproduce inside one dataset?
cal_lo, _, sb_lo, _, bb_lo = rows[lo]
cal_nat, _, sb_nat, _, bb_nat = rows[nat]
lead_stream_lo = cal_lo - sb_lo
lead_batch_lo = cal_lo - bb_lo
lines.append("## Question 1: low-prevalence advantage")
lines.append("")
lines.append(f"At {lo:g}% prevalence CALIBURN's AUC-PR is {cal_lo:.3f} vs "
             f"{sb_lo:.3f} for the best streaming baseline "
             f"(lead {lead_stream_lo:+.3f}) and {bb_lo:.3f} for the best batch "
             f"reference (lead {lead_batch_lo:+.3f}). At natural prevalence the "
             f"same leads are {cal_nat - sb_nat:+.3f} (streaming) and "
             f"{cal_nat - bb_nat:+.3f} (batch).")
verdict1 = ("REPRODUCES against the streaming group" if lead_stream_lo > 0 else
            "DOES NOT reproduce against the streaming group")
verdict1b = ("and against the batch reference" if lead_batch_lo > 0 else
             "but NOT against the batch reference")
lines.append("")
lines.append(f"**Verdict (mechanical, threshold = lead > 0):** the low-prevalence "
             f"advantage {verdict1} {verdict1b} when prevalence is lowered inside "
             f"CICIDS2017 alone.")
lines.append("")

# Question 2: does the high-prevalence collapse reproduce?
lines.append("## Question 2: high-prevalence collapse (CRC mechanism)")
lines.append("")
lines.append("| prevalence | V1 F1 | V1 alert rate | V1 CRC tau | V3 FPR | V4 F1 | CALIBURN AUC-PR minus floor |")
lines.append("|---|---|---|---|---|---|---|")
for lvl in levels:
    v1f1 = get(lvl, "bocpd_v1_iso_crc", "f1")
    v1ar = get(lvl, "bocpd_v1_iso_crc", "alert_rate")
    tau = get(lvl, "bocpd_v1_iso_crc", "crc_tau")
    v3fpr = get(lvl, "bocpd_v3_iso_elkan", "test_fpr")
    v4f1 = get(lvl, "bocpd_v4_raw_elkan", "f1")
    cal = rows[lvl][0]
    lines.append(f"| {lvl:g}% | {v1f1:.3f} | {v1ar:.4f} | {tau:.3f} | "
                 f"{v3fpr:.3f} | {v4f1:.3f} | {cal - lvl / 100:+.3f} |")
high = [l for l in levels if l >= 40]
low = [l for l in levels if l <= 10]
collapse_high = all(get(l, "bocpd_v1_iso_crc", "f1") < 0.05 for l in high)
alive_low = any(get(l, "bocpd_v1_iso_crc", "f1") > 0.10 for l in low)
floor_hug = all((rows[l][0] - l / 100) < 0.05 for l in high)
lines.append("")
lines.append(f"**Verdict (mechanical):** V1 F1 < 0.05 at every level >= 40%: "
             f"{collapse_high}. V1 F1 > 0.10 at some level <= 10%: {alive_low}. "
             f"CALIBURN AUC-PR within 0.05 of the prevalence floor at every level "
             f">= 40%: {floor_hug}. The high-prevalence collapse "
             f"{'REPRODUCES' if (collapse_high and alive_low) else 'DOES NOT fully reproduce'} "
             f"inside one dataset, and the ranking degeneracy near the floor "
             f"{'accompanies it' if floor_hug else 'does not accompany it'}.")
lines.append("")
lines.append("## Interpretation constraint")
lines.append("")
lines.append("Because the dataset, features, preprocessing, and stream construction "
             "are identical across levels, any pattern above is attributable to "
             "prevalence (and the resampling it requires), not to dataset identity. "
             "Where the within-dataset pattern matches the cross-dataset Figure 5 "
             "pattern, the regime-dependence reading survives this control; where it "
             "does not, the cross-dataset pattern was carrying dataset-identity "
             "effects.")
lines.append("")
lines.append("Construction notes: stratified per-split resampling (see RUN_REPORT "
             "and commit d8d0796) was required because the interleaved stream has a "
             "structural attack-share gradient across splits; above-natural levels "
             "retain 97.3% of attacks. The natural column reuses the bit-exact "
             "Stage 1 rows for baselines (provenance column in the CSV) and "
             "recomputes CALIBURN through the sweep harness as the internal control.")

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
