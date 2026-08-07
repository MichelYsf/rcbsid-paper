#!/usr/bin/env python
"""
Figure 7: Multi-window burn-rate alerting on the REAL LITNET-2020 test stream
(companion to the synthetic illustration figure; same three-panel layout).

(a) per-minute CALIBURN V1 threshold-crossing events, labeled attack minutes shaded
(b) long/short-window burn rates for each evaluable alert level
(c) fired alerts per level

Reads results/burnrate_litnet_trace.csv and results/burnrate_litnet.csv.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib as mpl  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
TRACE = ROOT / "results/burnrate_litnet_trace.csv"
SUMMARY = ROOT / "results/burnrate_litnet.csv"
OUTPUT_DIR = ROOT / "figures"
OUTPUT_DIR.mkdir(exist_ok=True)

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 7,
    "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
    "axes.linewidth": 0.6, "lines.linewidth": 1.0,
})

SLO = 0.999
LEVEL_STYLE = {
    "page_fast": {"color": "#D62728", "label": "page-fast (60/5 min, $\\beta$=14.4)"},
    "page_slow": {"color": "#FF7F0E", "label": "page-slow (360/30 min, $\\beta$=6.0)"},
    "ticket": {"color": "#1F77B4", "label": "ticket (4320/360 min, $\\beta$=1.0)"},
}

trace = pd.read_csv(TRACE, parse_dates=["minute"])
summary = pd.read_csv(SUMMARY)
budget = trace["crossing"].to_numpy(dtype=float)
attack = trace["attack"].to_numpy(dtype=int)
t_h = np.arange(len(budget)) / 60.0  # hours since span start


def rolling_rate(x: np.ndarray, w: int) -> np.ndarray:
    c = np.cumsum(np.concatenate([[0.0], x]))
    out = np.full(len(x), np.nan)
    if len(x) >= w:
        out[w - 1:] = (c[w:] - c[:-w]) / w
    return out


fig, axes = plt.subplots(3, 1, figsize=(7.0, 6.2), sharex=True,
                         gridspec_kw={"height_ratios": [1.0, 1.4, 0.8]})

ax = axes[0]
# shade labeled attack minutes
in_attack = np.flatnonzero(attack == 1)
if len(in_attack):
    splits = np.split(in_attack, np.flatnonzero(np.diff(in_attack) > 1) + 1)
    for i, seg in enumerate(splits):
        ax.axvspan(t_h[seg[0]], t_h[seg[-1]] + 1 / 60, color="#D62728", alpha=0.15,
                   lw=0, label="labeled attack window" if i == 0 else None)
ax.step(t_h, budget, where="post", color="#404040", linewidth=0.7,
        label="minute with $\\geq$1 V1 threshold crossing")
ax.set_ylabel("crossing")
ax.set_yticks([0, 1])
ax.set_title("(a) CALIBURN V1 threshold-crossing events on the real test stream")
ax.legend(loc="upper right", frameon=False)

ax = axes[1]
for level, style in LEVEL_STYLE.items():
    row = summary[summary["level"] == level]
    if row.empty or not bool(row["evaluable"].iloc[0]):
        continue
    long_w = int(row["long_min"].iloc[0]); short_w = int(row["short_min"].iloc[0])
    beta = float(row["beta"].iloc[0])
    br_long = rolling_rate(budget, long_w) / (1 - SLO)
    ax.plot(t_h, br_long, color=style["color"], linewidth=0.9, label=style["label"])
    ax.axhline(beta, color=style["color"], linewidth=0.6, linestyle=":")
ax.set_yscale("log")
ax.set_ylabel("long-window burn rate")
ax.set_title("(b) long-window burn rates vs their thresholds (dotted)")
ax.legend(loc="upper right", frameon=False)

ax = axes[2]
ypos = {}
for i, (level, style) in enumerate(LEVEL_STYLE.items()):
    row = summary[summary["level"] == level]
    ypos[level] = len(LEVEL_STYLE) - i
    if row.empty:
        continue
    if not bool(row["evaluable"].iloc[0]):
        ax.text(0.01, ypos[level], f"{level}: not evaluable (span too short)",
                fontsize=7, va="center", color="#777777",
                transform=ax.get_yaxis_transform())
        continue
    eps = str(row.get("alert_episodes", pd.Series([""])).iloc[0] or "")
    for j, ep in enumerate([e for e in eps.split(";") if e.strip()]):
        s, e = ep.strip().split("..")
        s_i = (pd.Timestamp(s) - trace["minute"].iloc[0]).total_seconds() / 3600
        e_i = (pd.Timestamp(e) - trace["minute"].iloc[0]).total_seconds() / 3600
        ax.plot([s_i, max(e_i, s_i + 0.02)], [ypos[level]] * 2, color=style["color"],
                linewidth=5, solid_capstyle="butt")
ax.set_yticks(list(ypos.values()))
ax.set_yticklabels(list(ypos.keys()))
ax.set_ylim(0.4, len(LEVEL_STYLE) + 0.6)
ax.set_xlabel("hours since test-span start")
ax.set_title("(c) alerts fired per level")

fig.tight_layout()
for ext in ("pdf", "png"):
    out = OUTPUT_DIR / f"fig7_burnrate_litnet.{ext}"
    fig.savefig(out)
    print(f"wrote {out}")
