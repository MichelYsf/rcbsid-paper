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

# Measured validation-split health (2026-08-13, from the built streams).
# A selection made against a handful of positives is noise, and any table of
# "selected configs" must say so on its face or it will be misread as usable.
VALIDATION_HEALTH = {
    "litnet2020": {"prevalence_pct": 0.003, "attacks": 6, "n": 225_000, "usable": False},
    "cicids2017": {"prevalence_pct": 21.70, "attacks": 52_085, "n": 240_000, "usable": True},
}

t = pd.read_csv(CSV)
for col in ("phase", "method", "dataset", "params", "error"):
    if col not in t.columns:
        t[col] = ""
for col in ("auc_pr", "val_auc_pr"):
    if col not in t.columns:
        t[col] = float("nan")

lines = ["# Findings: baseline tuning (Stage 3)", ""]

# --- corrected incident: emitted by the generator so the retraction cannot be
# --- lost the next time this file is regenerated.
lines += [
    "## CORRECTED INCIDENT — retraction of an earlier claim about LITNET-2020",
    "",
    "An earlier version of this document, of DONE_ALL.md, of RUN_REPORT.md and of",
    "results/tuning_parts/reductions.json asserted that the **paper's** LITNET-2020",
    "evaluation was built on a degenerate split (validation holding 6 attacks, a",
    "0.059% test slice) and that this undermined Table 9's calibration and the CRC",
    "exchangeability assumption. **That claim was wrong and is fully retracted. The",
    "paper's LITNET evaluation is sound.** The defect was in this harness.",
    "",
    "What actually happened:",
    "",
    "- Both the EC2 bootstrap (`scripts/ec2_bootstrap.sh`) and the local Stage 0",
    "  build ran `scripts/build_litnet_labeled.py` and then went straight to the",
    "  runner, **omitting `scripts/interleave_litnet.py`**. The CICIDS2017 path did",
    "  run its equivalent (`interleave_cicids.py`), which is why only LITNET was",
    "  affected.",
    "- The resulting stream was **three contiguous attack-type blocks** (measured: 2",
    "  adjacent `attack_type` changes across 1,500,000 rows, where round-robin gives",
    "  ~1,499,999). Validation and test were therefore **100% `spam`**, whose native",
    "  attack rate is 0.06% — hence 6 attacks in validation and 132 in test.",
    "- **Every LITNET grid result from this run is an artifact of that broken stream",
    "  and is void.** The partials are quarantined under",
    "  `results/tuning_parts/void_litnet_uninterleaved/` and excluded from",
    "  `baseline_tuning.csv`.",
    "- The **published** LITNET evaluation uses a correctly interleaved stream: an",
    "  in-memory reconstruction of the documented interleave gives train 4.928% /",
    "  validation 5.218% / **test 6.498% (14,621 attacks in 225,000 rows)**. Two",
    "  independent checks agree: the paper's Table 12 ablation row (alert rate 0.057,",
    "  precision 0.976, recall 0.850) implies 6.54% prevalence and predicts FPR",
    "  0.0015 against the 0.001 reported; and LOF's precision 0.0667 at recall 0.9605",
    "  bounds test prevalence at <= 6.95%. A 0.059% slice would require an alert rate",
    "  of 0.051% against the 5.7% reported — wrong by two orders of magnitude.",
    "- **The reallocation of Stage 3 from LITNET-2020 to CICIDS2017 was therefore",
    "  made on a false premise.** The CICIDS2017 tuning below is itself valid and",
    "  its validation split is healthy, but LITNET tuning should not have been",
    "  dropped and remains legitimate unfinished work.",
    "",
]

# Coverage first: a truncated run must say plainly what it did and did not
# produce, before any verdict is read.
grid = t[t["phase"] == "grid"]
finals = t[t["phase"].astype(str).str.startswith("final")]
dropped = grid[grid["val_auc_pr"].isna()]
if len(dropped) or finals.empty:
    lines.append("## Coverage and completeness")
    lines.append("")
    lines.append(f"- Grid points evaluated: {len(grid) - len(dropped)} usable, "
                 f"{len(dropped)} crashed and dropped (runbook rule: drop and log).")
    for _, r in dropped.iterrows():
        lines.append(f"  - DROPPED `{r['method']}` `{r['params']}` — {str(r['error'])[:90]}")
    if finals.empty:
        lines.append("- **No final (full-stream) runs completed.** Selection results "
                     "below are validation-only; no tuned test numbers exist yet, so "
                     "no default-versus-tuned verdict can be drawn.")
    else:
        have = sorted(finals["method"].unique())
        lines.append(f"- Final runs completed for: {', '.join(have)}.")
    lines.append("")
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
    if tuned.empty:
        sel = t[(t["dataset"] == ds) & (t["phase"] == "grid") & t["val_auc_pr"].notna()]
        if sel.empty:
            lines.append(f"## {ds}: not tuned (reduction rung; documented defaults carried)")
            lines.append("")
            continue
        # Validation-only outcome: report the selections that WOULD be used,
        # clearly marked as not yet confirmed on the test stream.
        health = VALIDATION_HEALTH.get(ds, {})
        void = health and not health.get("usable", True)
        suffix = " — **SELECTIONS VOID**" if void else ""
        lines.append(f"## {ds}: validation-stage selections only (no finals completed){suffix}")
        lines.append("")
        if void:
            lines.append(f"> **VOID — do not use these configurations, and do not read them "
                         f"as evidence about {ds} or about CALIBURN.** They were computed on "
                         f"a **broken stream that this harness built**, not on the dataset "
                         f"the paper evaluates. See the corrected-incident section above: "
                         f"`scripts/interleave_litnet.py` was never run, so the stream was "
                         f"three contiguous attack-type blocks and the validation split held "
                         f"**{health['attacks']} attacks in {health['n']:,} rows** "
                         f"({health['prevalence_pct']}%). The published evaluation uses a "
                         f"correctly interleaved stream with a ~6.5% test slice. These rows "
                         f"are retained only to document what the broken run produced.")
            lines.append("")
        elif health:
            lines.append(f"Validation split: {health['attacks']:,} attacks in "
                         f"{health['n']:,} rows ({health['prevalence_pct']}% prevalence) — "
                         f"selection is statistically meaningful here.")
            lines.append("")
        lines.append("| baseline | selected config (max validation AUC-PR) | val AUC-PR | grid points used |")
        lines.append("|---|---|---|---|")
        for method in sorted(sel["method"].unique()):
            g = sel[sel["method"] == method].sort_values("val_auc_pr", ascending=False)
            best = g.iloc[0]
            lines.append(f"| {method} | `{best['params']}` | {best['val_auc_pr']:.4f} | {len(g)} |")
        lines.append("")
        lines.append("**No verdict is drawn on whether CALIBURN still leads after "
                     "tuning**: that comparison requires test-set numbers from the "
                     "full-stream final runs, which did not complete in the available "
                     "window. Selection above touched validation labels only.")
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
