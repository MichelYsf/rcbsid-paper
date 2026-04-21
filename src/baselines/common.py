from __future__ import annotations
from collections import deque
import numpy as np


class BaselineDependencyError(RuntimeError):
    """Raised when a publication baseline cannot run natively.

    Fallbacks are acceptable for smoke tests only. Full experiments should fail
    loudly if a named baseline is missing, so reviewer-facing tables cannot be
    accidentally populated with fallback numbers.
    """


def as_array(x) -> np.ndarray:
    if isinstance(x, dict):
        return np.asarray([x[k] for k in sorted(x.keys())], dtype=float)
    return np.asarray(x, dtype=float)


class RunningStandardizer:
    def __init__(self, n_features: int, eps: float = 1e-8):
        self.n = 0
        self.mean = np.zeros(n_features, dtype=float)
        self.m2 = np.zeros(n_features, dtype=float)
        self.eps = eps

    def transform(self, x) -> np.ndarray:
        x = as_array(x)
        if self.n < 2:
            return np.zeros_like(x, dtype=float)
        var = np.maximum(self.m2 / max(self.n - 1, 1), self.eps)
        return (x - self.mean) / np.sqrt(var)

    def learn_one(self, x) -> None:
        x = as_array(x)
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        self.m2 += delta * (x - self.mean)


class WindowDistanceScorer:
    """Small dependency-free streaming fallback used for smoke tests.

    It is not a replacement for the named baselines in the paper, but it keeps
    the package runnable when optional libraries are absent. The wrappers report
    whether the native implementation or fallback implementation is in use.
    """

    def __init__(self, n_features: int, window_size: int = 256):
        self.scaler = RunningStandardizer(n_features)
        self.window = deque(maxlen=window_size)

    def score_one(self, x) -> float:
        z = self.scaler.transform(x)
        if len(self.window) < 10:
            return 0.0
        W = np.asarray(self.window, dtype=float)
        d = np.sqrt(((W - z) ** 2).sum(axis=1))
        # normalized nearest-neighbor distance in [0,1)
        val = float(np.min(d))
        return float(val / (1.0 + val))

    def learn_one(self, x) -> None:
        z = self.scaler.transform(x)
        self.scaler.learn_one(x)
        self.window.append(z)
