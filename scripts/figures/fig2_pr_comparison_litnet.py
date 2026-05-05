#!/usr/bin/env python3
"""
fig2_pr_comparison_litnet.py

Generates Figure 2: Precision-Recall operating points across methods on LITNET-2020.

Since per-flow scores were not saved during the experimental runs, this figure shows
the actual operating point (precision, recall) achieved by each method's chosen threshold,
rather than smoothed PR curves. This is arguably more honest because it reflects how each
method would actually behave at deployment time.

Inputs:
    results_litnet_trial/tables/main_metrics_raw.csv

Outputs:
    figures/fig2_pr_comparison_litnet.pdf
    figures/fig2_pr_comparison_litnet.png
"""

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# ----------------------------------------------------------------------------
# Style setup: publication-quality, single-column width (~3.5 in), sans-serif
# ----------------------------------------------------------------------------
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 9,
    "axes.titlesize": 9,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "lines.linewidth": 1.0,
    "lines.markersize": 5,
})

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
INPUT_CSV = Path("results_litnet_trial/tables/main_metrics_raw.csv")
OUTPUT_DIR = Path("figures")
OUTPUT_DIR.mkdir(exist_ok=True)

# Method display names and presentation order (CALIBURN first, baselines after)
METHOD_DISPLAY = {
    "bocpd_slo": "CALIBURN",
    "loda": "LODA",
    "hst": "HST",
    "ecod_batch_ref": "ECOD",
    "copod_batch_ref": "COPOD",
    "iforest_asd": "iForest_ASD",
    "lof_batch_ref": "LOF",
    "kitnet": "KitNET",
    "rrcf": "RRCF",
}

# Distinct markers and colors per method.
# CALIBURN is the only filled star to make the headline result visually obvious.
METHOD_STYLE = {
    "bocpd_slo":       {"marker": "*",  "color": "#D62728", "size": 200, "zorder": 10},  # red star
    "loda":            {"marker": "o",  "color": "#1F77B4", "size": 50},
    "hst":             {"marker": "s",  "color": "#2CA02C", "size": 50},
    "ecod_batch_ref":  {"marker": "^",  "color": "#9467BD", "size": 50},
    "copod_batch_ref": {"marker": "v",  "color": "#8C564B", "size": 50},
    "iforest_asd":     {"marker": "D",  "color": "#FF7F0E", "size": 50},
    "lof_batch_ref":   {"marker": "P",  "color": "#7F7F7F", "size": 50},
    "kitnet":          {"marker": "X",  "color": "#BCBD22", "size": 50},
    "rrcf":            {"marker": "p",  "color": "#17BECF", "size": 50},
}

# ----------------------------------------------------------------------------
# Load and aggregate data
# ----------------------------------------------------------------------------
if not INPUT_CSV.exists():
    sys.exit(f"ERROR: {INPUT_CSV} not found. Run from the rcbsid_v7 root directory.")

df = pd.read_csv(INPUT_CSV)
print(f"Loaded {len(df)} rows from {INPUT_CSV}")
print(f"Methods: {sorted(df['method'].unique())}")
print(f"Seeds: {sorted(df['seed'].unique())}")

# Aggregate across seeds: mean precision, mean recall, mean AUC-PR
agg = df.groupby("method").agg(
    precision_mean=("precision", "mean"),
    precision_std=("precision", "std"),
    recall_mean=("recall", "mean"),
    recall_std=("recall", "std"),
    auc_pr_mean=("auc_pr", "mean"),
    auc_pr_std=("auc_pr", "std"),
    n_seeds=("seed", "nunique"),
).reset_index()

# Replace NaN std (single seed -> 0)
agg["precision_std"] = agg["precision_std"].fillna(0)
agg["recall_std"] = agg["recall_std"].fillna(0)
agg["auc_pr_std"] = agg["auc_pr_std"].fillna(0)

print("\nAggregated:")
print(agg.to_string(index=False))

# ----------------------------------------------------------------------------
# Plot
# ----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.5, 3.2))

for method, display_name in METHOD_DISPLAY.items():
    row = agg[agg["method"] == method]
    if row.empty:
        print(f"WARNING: method {method} not in CSV, skipping")
        continue
    style = METHOD_STYLE[method]
    p_mean = row["precision_mean"].iloc[0]
    p_std = row["precision_std"].iloc[0]
    r_mean = row["recall_mean"].iloc[0]
    r_std = row["recall_std"].iloc[0]
    auc = row["auc_pr_mean"].iloc[0]

    # Plot error bars (only if non-zero, i.e., stochastic methods)
    if p_std > 1e-6 or r_std > 1e-6:
        ax.errorbar(
            r_mean, p_mean,
            xerr=r_std, yerr=p_std,
            fmt="none",
            ecolor=style["color"],
            elinewidth=0.8,
            capsize=2,
            alpha=0.5,
            zorder=style.get("zorder", 5) - 1,
        )

    # Plot the point
    ax.scatter(
        r_mean, p_mean,
        marker=style["marker"],
        c=style["color"],
        s=style["size"],
        edgecolors="black",
        linewidths=0.5,
        label=f"{display_name} (AUC-PR={auc:.3f})",
        zorder=style.get("zorder", 5),
    )

# Reference lines
# Random classifier baseline (precision = attack rate ~5.2% on LITNET)
attack_rate = 0.052
ax.axhline(y=attack_rate, color="gray", linestyle=":", linewidth=0.7, alpha=0.6)
ax.text(0.02, attack_rate + 0.015, f"random ({attack_rate:.1%})",
        fontsize=7, color="gray", style="italic")

# Axes
ax.set_xlim(-0.02, 1.02)
ax.set_ylim(-0.02, 1.02)
ax.set_xlabel("Recall")
ax.set_ylabel("Precision")
ax.set_title("LITNET-2020: precision-recall operating points")

# Grid
ax.grid(True, linestyle="-", linewidth=0.3, alpha=0.4)
ax.set_axisbelow(True)

# Legend: outside right would crowd a single-column figure. Use upper-right inside.
# Sort legend by AUC-PR descending so CALIBURN is first.
handles, labels = ax.get_legend_handles_labels()
# Re-sort by AUC-PR (extract the number from the label)
import re
def auc_from_label(lbl):
    m = re.search(r"AUC-PR=([\d.]+)", lbl)
    return float(m.group(1)) if m else 0
order = sorted(range(len(labels)), key=lambda i: -auc_from_label(labels[i]))
handles = [handles[i] for i in order]
labels = [labels[i] for i in order]
ax.legend(handles, labels, loc="center right", frameon=True,
          framealpha=0.92, edgecolor="gray", borderpad=0.4,
          handletextpad=0.4, labelspacing=0.3, fontsize=7)

# ----------------------------------------------------------------------------
# Save
# ----------------------------------------------------------------------------
pdf_path = OUTPUT_DIR / "fig2_pr_comparison_litnet.pdf"
png_path = OUTPUT_DIR / "fig2_pr_comparison_litnet.png"
fig.savefig(pdf_path)
fig.savefig(png_path)
print(f"\nSaved: {pdf_path}")
print(f"Saved: {png_path}")
