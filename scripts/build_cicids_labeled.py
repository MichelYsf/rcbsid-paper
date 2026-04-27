#!/usr/bin/env python
"""Build a labeled CICIDS2017 dataset from Engelen-improved (CNS2022) per-day CSVs.

Per day:
1. Read CSV (already has labels in column 'Label' and timestamps in 'Timestamp')
2. Drop noise columns: id, Flow ID, Src IP, Dst IP, Attempted Category
3. Drop rows with " - Attempted" labels (failed attacks, ~0.6% of data)
4. Convert Label column to binary: 1 if attack-of-any-kind, 0 if BENIGN
5. PROPORTIONAL subsample: scale benigns AND attacks by the same factor so
   the natural per-day attack rate is preserved. This avoids inflating attack
   rates the way pure attack-keeping does.

Concatenate Mon -> Fri, write a single labeled CSV.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

SRC = Path("data/raw/cicids2017_original")
OUT_DIR = Path("data/raw/cicids2017")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = OUT_DIR / "cicids2017_labeled.csv"

# Per-day budget. Sized to preserve natural per-day prevalence while keeping
# the combined dataset around ~1.5M rows.
DAYS = [
    ("monday",    "monday.csv",    300_000),
    ("tuesday",   "tuesday.csv",   300_000),
    ("wednesday", "wednesday.csv", 350_000),
    ("thursday",  "thursday.csv",  300_000),
    ("friday",    "friday.csv",    350_000),
]

DROP_COLS = ["id", "Flow ID", "Src IP", "Dst IP", "Attempted Category"]


def process_day(day_name: str, fname: str, budget: int, write_header: bool, out_path: Path) -> tuple[int, int]:
    print(f"\n=== {day_name} ===", flush=True)
    df = pd.read_csv(SRC / fname, low_memory=False)
    print(f"  loaded {len(df):,} rows, {df.shape[1]} cols", flush=True)

    # Drop noise columns
    df = df.drop(columns=[c for c in DROP_COLS if c in df.columns])

    # Drop "Attempted" rows
    pre = len(df)
    df = df[~df["Label"].astype(str).str.contains(" - Attempted", na=False)].copy()
    print(f"  dropped {pre - len(df):,} 'Attempted' rows -> {len(df):,} rows", flush=True)

    # Binary label + keep attack_type
    df["label"] = (df["Label"] != "BENIGN").astype(int)
    df["attack_type"] = df["Label"].where(df["Label"] != "BENIGN", "benign")
    df = df.drop(columns=["Label"])

    natural_rate = df["label"].mean()
    n_attack_natural = int(df["label"].sum())
    print(f"  natural rate: {n_attack_natural:,} attacks of {len(df):,} ({natural_rate*100:.2f}%)", flush=True)

    # Proportional subsample: same factor on both classes, preserving rate
    if len(df) > budget:
        keep_factor = budget / len(df)
        attack_df = df[df["label"] == 1]
        benign_df = df[df["label"] == 0]

        n_attack_keep = round(len(attack_df) * keep_factor)
        n_benign_keep = round(len(benign_df) * keep_factor)

        # Stride-sample to preserve temporal distribution within each class
        if n_attack_keep > 0 and len(attack_df) > 0:
            stride_a = max(1, len(attack_df) // n_attack_keep)
            attack_keep = attack_df.iloc[::stride_a].head(n_attack_keep)
        else:
            attack_keep = attack_df.iloc[:0]

        if n_benign_keep > 0 and len(benign_df) > 0:
            stride_b = max(1, len(benign_df) // n_benign_keep)
            benign_keep = benign_df.iloc[::stride_b].head(n_benign_keep)
        else:
            benign_keep = benign_df.iloc[:0]

        kept = pd.concat([attack_keep, benign_keep], ignore_index=False)
        kept = kept.sort_values("Timestamp", kind="mergesort").reset_index(drop=True)
        df = kept
        n_attack = int(df["label"].sum())
        print(f"  subsampled to {len(df):,} rows ({n_attack:,} attacks, {df['label'].mean()*100:.2f}%) -- preserved natural rate", flush=True)
    else:
        df = df.sort_values("Timestamp", kind="mergesort").reset_index(drop=True)
        n_attack = int(df["label"].sum())

    df.to_csv(out_path, mode="a" if not write_header else "w", header=write_header, index=False)
    print(f"  wrote {len(df):,} rows", flush=True)
    return len(df), n_attack


def main():
    if OUT_CSV.exists():
        OUT_CSV.unlink()

    total_rows = 0
    total_attacks = 0
    for i, (day_name, fname, budget) in enumerate(DAYS):
        n, a = process_day(day_name, fname, budget, write_header=(i == 0), out_path=OUT_CSV)
        total_rows += n
        total_attacks += a

    print(f"\n=== COMBINED ===", flush=True)
    print(f"total rows:    {total_rows:,}", flush=True)
    print(f"total attacks: {total_attacks:,}", flush=True)
    print(f"attack rate:   {total_attacks / max(1, total_rows) * 100:.3f}%", flush=True)
    size_mb = OUT_CSV.stat().st_size / 1e6
    print(f"wrote {OUT_CSV} ({size_mb:.1f} MB)", flush=True)


if __name__ == "__main__":
    main()
