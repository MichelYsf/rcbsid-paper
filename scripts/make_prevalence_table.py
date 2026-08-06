#!/usr/bin/env python
"""Generate the Stage 2 LaTeX table from results/prevalence_sweep_cicids.csv.

AUC-PR mean +/- std over the three resample seeds, one column per prevalence
level. The caption notes that the variance source is the resampling draw,
since CALIBURN itself is deterministic.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results/prevalence_sweep_cicids.csv"
OUT = ROOT / "results/prevalence_sweep_table.tex"

LABELS = {
    "bocpd_slo": r"CALIBURN (raw scores, Stage-1 threshold)",
    "bocpd_v1_iso_crc": r"CALIBURN V1 (isotonic + CRC $\alpha{=}0.01$)",
    "bocpd_v3_iso_elkan": r"CALIBURN V3 (isotonic + Elkan $\tau^*{=}0.091$)",
    "bocpd_v4_raw_elkan": r"CALIBURN V4 (raw + Elkan $\tau^*{=}0.091$)",
    "loda": "LODA",
    "hst": "HST",
    "lof_batch_ref": "LOF (batch ref.)",
    "ecod_batch_ref": "ECOD (batch ref.)",
}
ORDER = list(LABELS)

df = pd.read_csv(CSV)
df = df[df["auc_pr"].notna()]
levels = sorted(df["level_target_pct"].unique())

agg = df.groupby(["level_target_pct", "method"]).agg(
    m=("auc_pr", "mean"), s=("auc_pr", "std"), n=("auc_pr", "size")).reset_index()
agg["s"] = agg["s"].fillna(0.0)

lines = []
lines.append(r"\begin{table}[t]")
lines.append(r"\centering")
lines.append(r"\small")
col_spec = "l" + "c" * len(levels)
lines.append(rf"\begin{{tabular}}{{{col_spec}}}")
lines.append(r"\toprule")
header = "Method & " + " & ".join(
    (rf"{lvl:g}\% (nat.)" if abs(lvl - 22.06) < 0.01 else rf"{lvl:g}\%") for lvl in levels
) + r" \\"
lines.append(header)
lines.append(r"\midrule")
for method in ORDER:
    cells = []
    for lvl in levels:
        sub = agg[(agg["level_target_pct"] == lvl) & (agg["method"] == method)]
        if sub.empty:
            cells.append("--")
        else:
            m, s = float(sub["m"].iloc[0]), float(sub["s"].iloc[0])
            cells.append(rf"{m:.3f} $\pm$ {s:.3f}" if s > 5e-4 else rf"{m:.3f}")
    lines.append(f"{LABELS[method]} & " + " & ".join(cells) + r" \\")
lines.append(r"\bottomrule")
lines.append(r"\end{tabular}")
lines.append(
    r"\caption{AUC-PR across attack-prevalence levels with the dataset held fixed "
    r"(CICIDS2017, interleaved corrected stream, resampled per level; chronological "
    r"70/15/15 split applied after resampling). Values are mean $\pm$ std over three "
    r"resample seeds (11, 23, 47); the variance source is the resampling draw, since "
    r"CALIBURN itself is deterministic. The 22.06\% column is the natural stream with "
    r"no resampling and reproduces the published Table~5 configuration exactly. "
    r"Stochastic baselines (LODA, HST) additionally re-seed the method with the "
    r"resample seed.}")
lines.append(r"\label{tab:prevalence-sweep}")
lines.append(r"\end{table}")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines) + "\n")
print(f"wrote {OUT}")
print("\n".join(lines))
