from __future__ import annotations
import numpy as np


def scalar_score(value) -> float:
    """Convert a detector score to a finite Python float.

    Some streaming anomaly libraries, including PySAD, return one-element numpy
    arrays from ``score_partial``. Calling ``float(array([x]))`` raises on modern
    NumPy versions. This helper accepts Python scalars, 0-D arrays, and one-item
    arrays, but intentionally raises for empty or multi-valued outputs so wrapper
    bugs are not silently hidden.
    """
    arr = np.asarray(value)
    if arr.size != 1:
        raise ValueError(f"Expected scalar or one-element score, got shape {arr.shape}")
    out = float(arr.reshape(-1)[0])
    if not np.isfinite(out):
        return 0.0
    return out
