#!/usr/bin/env python
"""
Figure 6: AUC-PR vs attack prevalence with the dataset held fixed (CICIDS2017).

Companion to the regime-sensitivity figure (paper Fig. 5): same three-series
comparison and colors, but prevalence varies *within* one dataset via
resampling, removing the dataset-identity confound. The natural-prevalence
anchor (22.06%, no resampling) is marked; it reproduces the published Table 5
numbers exactly for the deterministic methods.

Reads results/prevalence_sweep_cicids.csv (one row per run).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "results/prevalence_sweep_cicids.csv"
OUTPUT_DIR = ROOT / "figures"
OUTPUT_DIR.mkdir(exist_ok=True)

CALIBURN_KEY = "bocpd_slo"
STREAMING = ["loda", "hst"]
BATCH = ["lof_batch_ref", "ecod_batch_ref"]
NATURAL_PCT = 22.06

df = pd.read_csv(CSV)
df = df[df["auc_pr"].notna()]

agg = df.groupby(["level_target_pct", "method"]).agg(
    auc_pr_mean=("auc_pr", "mean"),
    auc_pr_std=("auc_pr", "std"),
    n=("auc_pr", "size"),
).reset_index()
agg["auc_pr_std"] = agg["auc_pr_std"].fillna(0.0)
levels = sorted(agg["level_target_pct"].unique())


def series(methods: list[str]):
    """Per level: the best method (by mean AUC-PR) among `methods`."""
    means, stds, labels = [], [], []
    for lvl in levels:
        sub = agg[(agg["level_target_pct"] == lvl) & (agg["method"].isin(methods))]
        if sub.empty:
            means.append(np.nan); stds.append(0.0); labels.append("?")
            continue
        best = sub.loc[sub["auc_pr_mean"].idxmax()]
        means.append(best["auc_pr_mean"]); stds.append(best["auc_pr_std"])
        labels.append(best["method"].replace("_batch_ref", "").upper())
    return np.array(means), np.array(stds), labels


cal_mean, cal_std, _ = series([CALIBURN_KEY])
str_mean, str_std, str_labels = series(STREAMING)
bat_mean, bat_std, bat_labels = series(BATCH)

fig, ax = plt.subplots(figsize=(7.0, 3.5))

ax.errorbar(levels, cal_mean, yerr=cal_std, label="CALIBURN",
            color="#D62728", marker="o", markersize=5, linewidth=1.6,
            capsize=3, elinewidth=0.8, zorder=5)
ax.errorbar(levels, bat_mean, yerr=bat_std, label="best batch reference",
            color="#7F7F7F", marker="s", markersize=4.5, linewidth=1.4,
            capsize=3, elinewidth=0.8, zorder=4)
ax.errorbar(levels, str_mean, yerr=str_std, label="best streaming baseline",
            color="#1F77B4", marker="^", markersize=4.5, linewidth=1.4,
            capsize=3, elinewidth=0.8, zorder=4)

# Annotate which method is "best" at each level (fig3-style italic tags).
for x, ym, lab in zip(levels, str_mean, str_labels):
    if np.isfinite(ym):
        ax.annotate(lab, (x, ym), textcoords="offset points", xytext=(0, -12),
                    ha="center", fontsize=6.5, color="#1F77B4", style="italic")
for x, ym, lab in zip(levels, bat_mean, bat_labels):
    if np.isfinite(ym):
        ax.annotate(lab, (x, ym), textcoords="offset points", xytext=(0, 6),
                    ha="center", fontsize=6.5, color="#404040", style="italic")

# Natural-prevalence anchor: no resampling, exact Stage 1 reproduction.
ax.axvline(NATURAL_PCT, color="black", linestyle=":", linewidth=0.9, zorder=1)
ax.annotate("natural\n(22.06%, no resampling)", (NATURAL_PCT, ax.get_ylim()[1]),
            xytext=(4, -2), textcoords="offset points", ha="left", va="top",
            fontsize=7, color="black")

# Chance level: AUC-PR of a random ranker equals prevalence.
grid = np.linspace(min(levels), max(levels), 100)
ax.plot(grid, grid / 100.0, color="black", linewidth=0.7, linestyle="--",
        alpha=0.5, zorder=1)
ax.annotate("chance (AUC-PR = prevalence)", (grid[70], grid[70] / 100.0),
            xytext=(0, -11), textcoords="offset points", fontsize=6.5,
            color="black", alpha=0.7)

ax.set_xlabel("attack prevalence after resampling (%)")
ax.set_ylabel("AUC-PR (mean ± std, 3 resample seeds)")
ax.set_title("Prevalence sweep within CICIDS2017 (dataset held fixed)")
ax.set_xticks(levels)
ax.set_xticklabels([f"{lvl:g}" for lvl in levels])
ax.set_ylim(0, 1.05)
ax.legend(loc="upper left", fontsize=8, frameon=False)
ax.spines[["top", "right"]].set_visible(False)

fig.tight_layout()
for ext in ("pdf", "png"):
    out = OUTPUT_DIR / f"fig6_prevalence_sweep.{ext}"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"wrote {out}")
