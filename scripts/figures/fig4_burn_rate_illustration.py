#!/usr/bin/env python3
"""
fig4_burn_rate_illustration.py

Generates Figure 4: Multi-window burn-rate alerting illustration.

Synthetic time-series demonstrating how page-fast (5min/60min) and page-slow
(30min/360min) windows respond to:
  (a) a brief noise burst (should NOT trigger any alert)
  (b) a sustained attack (should trigger page-fast then page-slow)

This figure makes Section 3.4 concrete for readers unfamiliar with SRE practice.
The data is fully synthetic; it does NOT come from the real experiments.

Outputs:
    figures/fig4_burn_rate_illustration.pdf
    figures/fig4_burn_rate_illustration.png
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle

# ----------------------------------------------------------------------------
# Style: single-column width
# ----------------------------------------------------------------------------
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 9,
    "axes.titlesize": 9,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 7,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.linewidth": 0.6,
    "lines.linewidth": 1.0,
})

# ----------------------------------------------------------------------------
# Synthetic event stream
# ----------------------------------------------------------------------------
# Time axis: 12 hours = 720 minutes, 1-minute resolution
np.random.seed(42)
duration_min = 720
t = np.arange(duration_min)

# Baseline: ~1 budget-consuming event per minute (within budget)
baseline_rate = 1.0

# Event 1: brief noise burst at t=120-130 minutes (10 min)
# Burst rate is high enough to trigger short-window page-fast briefly,
# but the 60-min long window stays below threshold => no firing.
# This illustrates dual-window protection from transient noise.
burst_start, burst_end = 120, 130
burst_rate = 60.0

# Event 2: sustained attack at t=300-480 minutes (180 min)
# Sustained at 50 events/min — high enough that BOTH 5min and 60min windows
# exceed page-fast threshold of 14.4 simultaneously.
attack_start, attack_end = 300, 480
attack_rate = 50.0

events = np.full(duration_min, baseline_rate)
events[burst_start:burst_end] = burst_rate
events[attack_start:attack_end] = attack_rate
# Add poisson noise
events = np.random.poisson(events).astype(float)

# ----------------------------------------------------------------------------
# Compute burn rates over windows
# Burn rate = (events_in_window / window_length) / (budget / SLO_period)
# Use SLO period T = 24 hours = 1440 min, budget B = baseline_rate * T = 2 * 1440 = 2880
# Allowed rate = B / T = 2 events/min
# ----------------------------------------------------------------------------
SLO_T = 1440.0
B = baseline_rate * SLO_T  # 2880 allowed events per 24h
allowed_rate = B / SLO_T   # 2 events/min

def burn_rate_series(events, window_min):
    """Compute trailing-window burn rate at each minute."""
    n = len(events)
    rate = np.zeros(n)
    csum = np.concatenate([[0], np.cumsum(events)])
    for i in range(n):
        start = max(0, i - window_min + 1)
        window_events = csum[i + 1] - csum[start]
        actual_window = i - start + 1
        rate[i] = (window_events / actual_window) / allowed_rate
    return rate

# Page-fast: 5min short, 60min long, threshold 14.4
br_short_pf = burn_rate_series(events, 5)
br_long_pf  = burn_rate_series(events, 60)
PF_THRESHOLD = 14.4

# Page-slow: 30min short, 360min long, threshold 6.0
br_short_ps = burn_rate_series(events, 30)
br_long_ps  = burn_rate_series(events, 360)
PS_THRESHOLD = 6.0

# Alert firing logic: both windows above threshold simultaneously
pf_fires = (br_short_pf > PF_THRESHOLD) & (br_long_pf > PF_THRESHOLD)
ps_fires = (br_short_ps > PS_THRESHOLD) & (br_long_ps > PS_THRESHOLD)

# ----------------------------------------------------------------------------
# Plot: 3 stacked subplots — events, burn rates, alert firings
# ----------------------------------------------------------------------------
fig, axes = plt.subplots(3, 1, figsize=(3.5, 4.5), sharex=True,
                         gridspec_kw={"height_ratios": [1.0, 1.5, 0.5]})

# (a) Event stream
ax0 = axes[0]
ax0.fill_between(t, 0, events, color="#1F77B4", alpha=0.6, linewidth=0)
ax0.set_ylabel("events / min")
ax0.set_ylim(0, 75)
ax0.set_title("(a) Budget-consuming event stream", loc="left", fontsize=9)
# Highlight the burst and attack windows
ax0.axvspan(burst_start, burst_end, color="orange", alpha=0.15)
ax0.axvspan(attack_start, attack_end, color="red", alpha=0.15)
ax0.text(125, 65, "transient\nnoise burst", ha="center", fontsize=7,
         color="darkorange", style="italic")
ax0.text(390, 65, "sustained attack", ha="center", fontsize=7,
         color="darkred", style="italic")
ax0.grid(True, axis="y", linestyle="-", linewidth=0.3, alpha=0.4)
ax0.set_axisbelow(True)

# (b) Burn rates with thresholds
ax1 = axes[1]
ax1.plot(t, br_short_pf, color="#D62728", linewidth=0.9,
         label="page-fast: 5min", alpha=0.9)
ax1.plot(t, br_long_pf,  color="#D62728", linewidth=0.9, linestyle="--",
         label="page-fast: 60min", alpha=0.9)
ax1.plot(t, br_short_ps, color="#FF7F0E", linewidth=0.9,
         label="page-slow: 30min", alpha=0.9)
ax1.plot(t, br_long_ps,  color="#FF7F0E", linewidth=0.9, linestyle="--",
         label="page-slow: 360min", alpha=0.9)
ax1.axhline(y=PF_THRESHOLD, color="#D62728", linewidth=0.6,
            linestyle=":", alpha=0.5)
ax1.axhline(y=PS_THRESHOLD, color="#FF7F0E", linewidth=0.6,
            linestyle=":", alpha=0.5)
ax1.text(720, PF_THRESHOLD, f"  β={PF_THRESHOLD}",
         fontsize=7, color="#D62728", va="center")
ax1.text(720, PS_THRESHOLD, f"  β={PS_THRESHOLD}",
         fontsize=7, color="#FF7F0E", va="center")
ax1.set_ylabel("burn rate b")
ax1.set_ylim(0, 70)
ax1.set_title("(b) Burn rates across short/long windows", loc="left", fontsize=9)
ax1.legend(loc="upper right", ncol=2, frameon=True, framealpha=0.92,
           handlelength=2.0, columnspacing=0.8)
ax1.grid(True, axis="y", linestyle="-", linewidth=0.3, alpha=0.4)
ax1.set_axisbelow(True)

# (c) Alert firings (both windows above threshold)
ax2 = axes[2]
# Show firings as horizontal bars
ax2.fill_between(t, 0.55, 0.95, where=pf_fires,
                 color="#D62728", alpha=0.9, linewidth=0)
ax2.fill_between(t, 0.05, 0.45, where=ps_fires,
                 color="#FF7F0E", alpha=0.9, linewidth=0)
ax2.set_yticks([0.25, 0.75])
ax2.set_yticklabels(["page-slow", "page-fast"], fontsize=8)
ax2.set_ylim(0, 1)
ax2.set_xlabel("time (minutes)")
ax2.set_title("(c) Alert firings", loc="left", fontsize=9)
ax2.set_xlim(0, duration_min)
ax2.grid(True, axis="x", linestyle="-", linewidth=0.3, alpha=0.4)
ax2.set_axisbelow(True)

# Make all subplots share x range
for ax in axes:
    ax.set_xlim(0, duration_min)

# ----------------------------------------------------------------------------
# Save
# ----------------------------------------------------------------------------
OUTPUT_DIR = Path("figures")
OUTPUT_DIR.mkdir(exist_ok=True)
pdf_path = OUTPUT_DIR / "fig4_burn_rate_illustration.pdf"
png_path = OUTPUT_DIR / "fig4_burn_rate_illustration.png"
plt.tight_layout(h_pad=0.5)
fig.savefig(pdf_path)
fig.savefig(png_path)
print(f"Saved: {pdf_path}")
print(f"Saved: {png_path}")
