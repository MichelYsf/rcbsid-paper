from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd


def list_data_files(path):
    p = Path(path)
    return sorted(list(p.glob('*.csv')) + list(p.glob('*.CSV')) + list(p.glob('*.parquet')))


def list_csv_files(path):
    return [f for f in list_data_files(path) if f.suffix.lower() == '.csv']


def load_dataset_folder(path, label_column, shuffle_within_files=None, shuffle_seed=20260422):
    """Load all CSV/Parquet files from a folder and concatenate.

    If shuffle_within_files is True (or auto-detected for UNSW-NB15), each file
    is shuffled independently before concatenation. This is required for datasets
    like UNSW-NB15 whose canonical CSVs are sorted by label, which would otherwise
    produce single-class tail splits when doing a chronological train/val/test cut.
    """
    files = list_data_files(path)
    if not files:
        raise FileNotFoundError(f'No CSV or Parquet files found in {path}')

    path_str = str(path).lower()
    if shuffle_within_files is None:
        shuffle_within_files = 'unsw' in path_str

    frames = []
    rng = np.random.default_rng(shuffle_seed)
    for f in files:
        if f.suffix.lower() == '.parquet':
            frame = pd.read_parquet(f)
        else:
            frame = pd.read_csv(f, low_memory=False)
        if shuffle_within_files:
            idx = rng.permutation(len(frame))
            frame = frame.iloc[idx].reset_index(drop=True)
        frames.append(frame)
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
