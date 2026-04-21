from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

def list_data_files(path):
    p = Path(path)
    return sorted(list(p.glob('*.csv')) + list(p.glob('*.CSV')) + list(p.glob('*.parquet')))

def list_csv_files(path):
    return [f for f in list_data_files(path) if f.suffix.lower() == '.csv']

def load_dataset_folder(path, label_column):
    files = list_data_files(path)
    if not files:
        raise FileNotFoundError(f'No CSV or Parquet files found in {path}')
    frames = []
    for f in files:
        if f.suffix.lower() == '.parquet':
            frames.append(pd.read_parquet(f))
        else:
            frames.append(pd.read_csv(f, low_memory=False))
    df = pd.concat(frames, ignore_index=True)
    if label_column not in df.columns:
        raise KeyError(f'Label column {label_column!r} not found')
    return df

def prepare_xy(df, label_column):
    y_raw = df[label_column].astype(str).str.lower()
    y = (~y_raw.isin(['benign', 'normal', '0', 'false'])).astype(int).to_numpy()
    X = df.drop(columns=[label_column])
    X = X.select_dtypes(include=[np.number]).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return X.to_numpy(dtype=float), y, list(X.columns)
