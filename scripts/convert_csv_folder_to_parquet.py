#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd


def main():
    p = argparse.ArgumentParser(description='Convert every CSV in a folder to Parquet.')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    in_dir = Path(args.input)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(list(in_dir.glob('*.csv')) + list(in_dir.glob('*.CSV')))
    if not files:
        raise FileNotFoundError(f'No CSV files found in {in_dir}')
    for f in files:
        df = pd.read_csv(f, low_memory=False)
        out = out_dir / (f.stem + '.parquet')
        df.to_parquet(out, index=False)
        print(f'{f} -> {out}')


if __name__ == '__main__':
    main()
