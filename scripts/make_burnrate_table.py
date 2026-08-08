#!/usr/bin/env python
"""Small LaTeX table for the Stage 4 real-data burn-rate validation."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results/burnrate_litnet.csv"
OUT = ROOT / "results/burnrate_litnet_table.tex"

df = pd.read_csv(CSV)
span_h = float(df["span_min"].iloc[0]) / 60.0
lines = [r"\begin{table}[t]", r"\centering", r"\small",
         r"\begin{tabular}{lccccc}", r"\toprule",
         r"Alert level & Windows (min) & $\beta$ & Evaluable & Alert episodes & "
         r"Coinciding w/ attack \\", r"\midrule"]
for _, r in df.iterrows():
    ev = "yes" if bool(r["evaluable"]) else "no (span)"
    eps = int(r.get("n_episodes", 0) or 0) if bool(r["evaluable"]) else "--"
    co = int(r.get("n_coinciding_minutes", 0) or 0) if bool(r["evaluable"]) else "--"
    lines.append(rf"{r['level'].replace('_','-')} & {int(r['long_min'])}/{int(r['short_min'])} & "
                 rf"{r['beta']:g} & {ev} & {eps} & {co} \\")
lines += [r"\bottomrule", r"\end{tabular}",
          rf"\caption{{Multi-window burn-rate alerting on the real LITNET-2020 test "
          rf"stream (span {span_h:.1f} h). Threshold-crossing events are CALIBURN V1 "
          rf"(isotonic + CRC $\alpha{{=}}0.01$) crossings bucketed into real minutes; "
          rf"only levels whose long window fits inside the span are evaluated. "
          rf"``Coinciding'' counts alert minutes whose lookback window contains at "
          rf"least one labeled attack flow.}}",
          r"\label{tab:burnrate-real}", r"\end{table}"]
OUT.write_text("\n".join(lines) + "\n")
print(f"wrote {OUT}")
