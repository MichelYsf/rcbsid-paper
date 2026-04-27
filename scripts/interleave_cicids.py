#!/usr/bin/env python
"""Vectorized round-robin interleave of CICIDS2017 CSV by day-of-week.

Each weekday's data is from a different time window with different attack
prevalence, so concatenated chronological order produces wildly imbalanced
train/val/test splits. Round-robin by day fixes this — each chronological
slice contains rows from all 5 days, so all splits see all attack types
at roughly the dataset-wide attack rate.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path

CSV = Path("data/raw/cicids2017/cicids2017_labeled.csv")

print("loading CSV", flush=True)
df = pd.read_csv(CSV, low_memory=False)
print(f"loaded: {len(df):,} rows, {df.shape[1]} cols", flush=True)

# Derive day-of-week from Timestamp string (YYYY-MM-DD HH:MM:SS.ffffff)
# CICIDS2017 was captured Mon Jul 3 -> Fri Jul 7, 2017
date_to_day = {
    "2017-07-03": "monday",
    "2017-07-04": "tuesday",
    "2017-07-05": "wednesday",
    "2017-07-06": "thursday",
    "2017-07-07": "friday",
}
df["day"] = df["Timestamp"].str[:10].map(date_to_day)
unmapped = df["day"].isna().sum()
if unmapped > 0:
    print(f"  WARNING: {unmapped:,} rows have unmapped timestamps", flush=True)
    df = df.dropna(subset=["day"]).reset_index(drop=True)

print("\nper-day breakdown:", flush=True)
for day, sub in df.groupby("day", sort=False):
    print(f"  {day}: {len(sub):,} rows, {int(sub['label'].sum()):,} attacks ({sub['label'].mean()*100:.2f}%)", flush=True)

# Sort within each day by Timestamp (preserves intra-day chronology)
print("\nsorting within each day", flush=True)
df = df.sort_values(["day", "Timestamp"], kind="mergesort").reset_index(drop=True)

# Build per-day index arrays
groups = {}
for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
    mask = df["day"] == day
    groups[day] = np.where(mask)[0]

# Round-robin interleave indices: row i of mon, row i of tue, row i of wed, ...
print("building interleaved index permutation", flush=True)
day_order = ["monday", "tuesday", "wednesday", "thursday", "friday"]
max_len = max(len(groups[d]) for d in day_order)

perm = np.empty(sum(len(groups[d]) for d in day_order), dtype=np.int64)
write_pos = 0
for i in range(max_len):
    for d in day_order:
        if i < len(groups[d]):
            perm[write_pos] = groups[d][i]
            write_pos += 1
perm = perm[:write_pos]
print(f"permutation built: {len(perm):,} indices", flush=True)

# Reorder vectorized
print("applying permutation", flush=True)
out = df.iloc[perm].reset_index(drop=True)

# Drop the helper 'day' column before writing
out = out.drop(columns=["day"])

# Verify split balance
n = len(out)
i_train = int(n * 0.70)
i_val = i_train + int(n * 0.15)
print("\nsplit verification:", flush=True)
for name, slc in [("train", out.iloc[:i_train]), ("val", out.iloc[i_train:i_val]), ("test", out.iloc[i_val:])]:
    attacks = int(slc["label"].sum())
    print(f"  {name}: n={len(slc):,} attacks={attacks:,} rate={slc['label'].mean():.4f}", flush=True)

# Save (overwrite)
print("\nsaving", flush=True)
out.to_csv(CSV, index=False)
size_mb = CSV.stat().st_size / 1e6
print(f"wrote {CSV} ({size_mb:.1f} MB)", flush=True)
