#!/usr/bin/env python
"""Vectorized round-robin interleave of LITNET CSV by attack_type.

Avoids pd.DataFrame(list_of_Series) — builds an integer permutation and uses
df.iloc[perm] for a single vectorized reorder. Runs in ~30 seconds at 1.5M rows.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path

CSV = Path("data/raw/litnet2020/litnet2020_labeled.csv")

print("loading CSV", flush=True)
df = pd.read_csv(CSV)
print(f"loaded: {len(df):,} rows, {df.shape[1]} cols", flush=True)

# Step 1: sort within each attack_type by timestamp, stable
print("sorting within each attack_type", flush=True)
df = df.sort_values(["attack_type", "timestamp"], kind="mergesort").reset_index(drop=True)

# Step 2: build per-type integer index arrays
groups = {}
for at, sub in df.groupby("attack_type", sort=True):
    groups[at] = sub.index.to_numpy()
    print(f"  {at}: {len(groups[at]):,} rows", flush=True)

# Step 3: round-robin interleave indices
print("building interleaved index permutation", flush=True)
names = sorted(groups.keys())
lens = [len(groups[n]) for n in names]
max_len = max(lens)

# Pre-allocate output
perm = np.empty(sum(lens), dtype=np.int64)
write_pos = 0
for i in range(max_len):
    for n in names:
        if i < len(groups[n]):
            perm[write_pos] = groups[n][i]
            write_pos += 1
perm = perm[:write_pos]
assert write_pos == len(df)
print(f"permutation built: {len(perm):,} indices", flush=True)

# Step 4: reorder in one vectorized shot
print("applying permutation (vectorized reorder)", flush=True)
out = df.iloc[perm].reset_index(drop=True)
print(f"reordered: {len(out):,} rows", flush=True)

# Verify split balance
n = len(out)
i_train = int(n * 0.70)
i_val = i_train + int(n * 0.15)
for name, slc in [("train", out.iloc[:i_train]), ("val", out.iloc[i_train:i_val]), ("test", out.iloc[i_val:])]:
    attacks = int(slc["label"].sum())
    print(f"  {name}: n={len(slc):,} attacks={attacks:,} rate={slc['label'].mean():.4f}", flush=True)

# Save (overwrite)
print("saving", flush=True)
out.to_csv(CSV, index=False)
size_mb = CSV.stat().st_size / 1e6
print(f"wrote {CSV} ({size_mb:.1f} MB)", flush=True)
