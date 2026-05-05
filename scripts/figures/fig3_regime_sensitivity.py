#!/usr/bin/env python3
"""
fig3_regime_sensitivity.py

Generates Figure 3: AUC-PR vs attack prevalence regime, comparing CALIBURN
against LOF (best batch reference) and the best streaming baseline at each regime.

This figure visualizes the central narrative of the paper: CALIBURN's advantage
is regime-dependent. It dominates at rare-attack prevalence (LITNET 5.2%),
remains strongest streaming method at moderate prevalence (CICIDS 22.06%),
and collapses with all streaming methods at high prevalence (UNSW 64%).

Inputs:
    results_litnet_trial/tables/main_metrics_raw.csv
    results_cicids_trial/tables/main_metrics_raw.csv
    results_unsw_trial/tables/main_metrics_raw.csv

Outputs:
    figures/fig3_regime_sensitivity.pdf
    figures/fig3_regime_sensitivity.png
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# ----------------------------------------------------------------------------
# Style: double-column width (~7 in), publication-quality
# ----------------------------------------------------------------------------
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.linewidth": 0.7,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "lines.linewidth": 1.5,
    "lines.markersize": 7,
})

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
DATASETS = [
    {
        "csv": "results_litnet_trial/tables/main_metrics_raw.csv",
        "name": "LITNET-2020",
        "attack_rate": 5.2,  # percent
    },
    {
        "csv": "results_cicids_trial/tables/main_metrics_raw.csv",
        "name": "CICIDS2017",
        "attack_rate": 22.06,
    },
    {
        "csv": "results_unsw_trial/tables/main_metrics_raw.csv",
        "name": "UNSW-NB15",
        "attack_rate": 64.0,
    },
]

OUTPUT_DIR = Path("figures")
OUTPUT_DIR.mkdir(exist_ok=True)

# Methods to compare
CALIBURN_KEY = "bocpd_slo"
BATCH_REF_KEY = "lof_batch_ref"
STREAMING_BASELINES = ["loda", "hst", "iforest_asd", "rrcf", "kitnet"]

# ----------------------------------------------------------------------------
# Load all three datasets and compute aggregates
# ----------------------------------------------------------------------------
records = []  # one record per (dataset, method)
for ds in DATASETS:
    csv_path = Path(ds["csv"])
    if not csv_path.exists():
        print(f"WARNING: {csv_path} not found, skipping")
        continue
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from {csv_path}")

    # Aggregate per method
    agg = df.groupby("method").agg(
        auc_pr_mean=("auc_pr", "mean"),
        auc_pr_std=("auc_pr", "std"),
        n_seeds=("seed", "nunique"),
    ).reset_index()
    agg["auc_pr_std"] = agg["auc_pr_std"].fillna(0)

    for _, row in agg.iterrows():
        records.append({
            "dataset": ds["name"],
            "attack_rate": ds["attack_rate"],
            "method": row["method"],
            "auc_pr_mean": row["auc_pr_mean"],
            "auc_pr_std": row["auc_pr_std"],
            "n_seeds": int(row["n_seeds"]),
        })

results_df = pd.DataFrame(records)
print("\nAggregated results:")
print(results_df.to_string(index=False))

# ----------------------------------------------------------------------------
# Identify "best streaming baseline" per dataset
# (best AUC-PR among streaming methods, excluding CALIBURN itself)
# ----------------------------------------------------------------------------
best_streaming_per_ds = {}
for ds in DATASETS:
    sub = results_df[
        (results_df["dataset"] == ds["name"]) &
        (results_df["method"].isin(STREAMING_BASELINES))
    ]
    if sub.empty:
        continue
    best_row = sub.loc[sub["auc_pr_mean"].idxmax()]
    best_streaming_per_ds[ds["name"]] = {
        "method": best_row["method"],
        "auc_pr_mean": best_row["auc_pr_mean"],
        "auc_pr_std": best_row["auc_pr_std"],
    }
    print(f"\nBest streaming baseline on {ds['name']}: "
          f"{best_row['method']} = {best_row['auc_pr_mean']:.3f}")

# ----------------------------------------------------------------------------
# Build plot data
# ----------------------------------------------------------------------------
ds_names = [ds["name"] for ds in DATASETS]
attack_rates = [ds["attack_rate"] for ds in DATASETS]
x_positions = np.arange(len(ds_names))  # 0, 1, 2

caliburn_means = []
caliburn_stds = []
for ds in DATASETS:
    sub = results_df[
        (results_df["dataset"] == ds["name"]) &
        (results_df["method"] == CALIBURN_KEY)
    ]
    if sub.empty:
        caliburn_means.append(np.nan)
        caliburn_stds.append(0)
    else:
        caliburn_means.append(sub["auc_pr_mean"].iloc[0])
        caliburn_stds.append(sub["auc_pr_std"].iloc[0])

batch_means = []
batch_stds = []
for ds in DATASETS:
    sub = results_df[
        (results_df["dataset"] == ds["name"]) &
        (results_df["method"] == BATCH_REF_KEY)
    ]
    if sub.empty:
        batch_means.append(np.nan)
        batch_stds.append(0)
    else:
        batch_means.append(sub["auc_pr_mean"].iloc[0])
        batch_stds.append(sub["auc_pr_std"].iloc[0])

stream_means = []
stream_stds = []
stream_labels = []
for ds in DATASETS:
    info = best_streaming_per_ds.get(ds["name"])
    if info is None:
        stream_means.append(np.nan)
        stream_stds.append(0)
        stream_labels.append("?")
    else:
        stream_means.append(info["auc_pr_mean"])
        stream_stds.append(info["auc_pr_std"])
        stream_labels.append(info["method"].upper())

# ----------------------------------------------------------------------------
# Plot: grouped bar chart with CALIBURN, LOF, best other streaming
# ----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.0, 3.5))

bar_width = 0.26
x = x_positions

bars1 = ax.bar(x - bar_width, caliburn_means, bar_width,
               yerr=caliburn_stds, label="CALIBURN",
               color="#D62728", edgecolor="black", linewidth=0.5,
               capsize=3, error_kw={"linewidth": 0.8})

bars2 = ax.bar(x, batch_means, bar_width,
               yerr=batch_stds, label="LOF (batch reference)",
               color="#7F7F7F", edgecolor="black", linewidth=0.5,
               capsize=3, error_kw={"linewidth": 0.8})

bars3 = ax.bar(x + bar_width, stream_means, bar_width,
               yerr=stream_stds, label="best other streaming method",
               color="#1F77B4", edgecolor="black", linewidth=0.5,
               capsize=3, error_kw={"linewidth": 0.8})

# Annotate the "best other streaming" bars with the actual method name
for i, (bar, label) in enumerate(zip(bars3, stream_labels)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height + 0.02,
            label, ha="center", va="bottom", fontsize=7,
            color="#1F77B4", style="italic")

# Annotate CALIBURN values on top
for i, bar in enumerate(bars1):
    height = bar.get_height()
    if not np.isnan(height):
        ax.text(bar.get_x() + bar.get_width() / 2, height + 0.02,
                f"{height:.3f}", ha="center", va="bottom",
                fontsize=8, color="#D62728", fontweight="bold")

# Annotate LOF values
for i, bar in enumerate(bars2):
    height = bar.get_height()
    if not np.isnan(height):
        ax.text(bar.get_x() + bar.get_width() / 2, height + 0.02,
                f"{height:.3f}", ha="center", va="bottom",
                fontsize=7, color="#404040")

# X-axis: dataset names + attack rates
xtick_labels = [f"{n}\n({r:.1f}% attacks)" for n, r in zip(ds_names, attack_rates)]
ax.set_xticks(x)
ax.set_xticklabels(xtick_labels)

ax.set_ylabel("AUC-PR (mean ± std across seeds)")
ax.set_title("Regime sensitivity: AUC-PR vs attack prevalence")
ax.set_ylim(0, 1.10)

# Minor x-axis label indicating the regime continuum
ax.set_xlabel("Increasing attack prevalence →", fontsize=9, style="italic", color="#555")

# Grid
ax.grid(True, axis="y", linestyle="-", linewidth=0.3, alpha=0.4)
ax.set_axisbelow(True)

# Legend
ax.legend(loc="upper right", frameon=True, framealpha=0.95,
          edgecolor="gray", borderpad=0.5)

# ----------------------------------------------------------------------------
# Save
# ----------------------------------------------------------------------------
pdf_path = OUTPUT_DIR / "fig3_regime_sensitivity.pdf"
png_path = OUTPUT_DIR / "fig3_regime_sensitivity.png"
fig.savefig(pdf_path)
fig.savefig(png_path)
print(f"\nSaved: {pdf_path}")
print(f"Saved: {png_path}")
