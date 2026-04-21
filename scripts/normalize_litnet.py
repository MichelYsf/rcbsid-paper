#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import re
import pandas as pd


def normalize_col(c: str) -> str:
    c = c.strip().lower()
    c = re.sub(r'[^a-z0-9]+', '_', c)
    c = re.sub(r'_+', '_', c).strip('_')
    aliases = {
        'label': 'label', 'class': 'label', 'attack': 'label', 'attack_type': 'label',
        'timestamp': 'timestamp', 'time': 'timestamp', 'date_time': 'timestamp',
    }
    return aliases.get(c, c)


def main():
    p = argparse.ArgumentParser(description='Normalize LITNET-2020 CSV column names and merge into a single CSV/parquet file.')
    p.add_argument('--input', default='data/raw/litnet2020', help='Folder containing LITNET CSV files')
    p.add_argument('--output', default='data/processed/litnet2020/litnet2020_normalized.parquet')
    args = p.parse_args()
    in_dir = Path(args.input)
    files = sorted(list(in_dir.glob('*.csv')) + list(in_dir.glob('*.CSV')))
    if not files:
        raise FileNotFoundError(f'No CSV files found in {in_dir}')
    frames = []
    all_cols = set()
    for f in files:
        df = pd.read_csv(f, low_memory=False)
        df.columns = [normalize_col(c) for c in df.columns]
        if 'label' not in df.columns:
            # fallback: infer attack type from filename when per-attack zips are used
            name = f.stem.lower()
            df['label'] = 'benign' if 'normal' in name or 'benign' in name else name
        df['source_file'] = f.name
        frames.append(df)
        all_cols.update(df.columns)
    cols = sorted(all_cols)
    merged = pd.concat([df.reindex(columns=cols) for df in frames], ignore_index=True)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix.lower() == '.csv':
        merged.to_csv(out, index=False)
    else:
        merged.to_parquet(out, index=False)
    print(f'Wrote {len(merged):,} rows to {out}')


if __name__ == '__main__':
    main()
