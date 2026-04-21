from __future__ import annotations
from collections import deque
import numpy as np
from sklearn.ensemble import IsolationForest
from .common import as_array, WindowDistanceScorer


class IForestASDWrapper:
    """Sliding-window streaming Isolation Forest baseline.

    This wrapper uses scikit-learn, which is a required dependency. The
    ``allow_fallback`` argument is accepted for registry API consistency; the
    early warm-up fallback is part of the model and is not used for final scoring
    once the window has enough samples.
    """
    def __init__(self, n_features: int, seed: int = 42, window_size: int = 1000, n_estimators: int = 100, refit_every: int = 100, allow_fallback: bool = True):
        self.window = deque(maxlen=window_size)
        self.seed = seed
        self.n_estimators = n_estimators
        self.refit_every = refit_every
        self.model: IsolationForest | None = None
        self.i = 0
        self.warmup = WindowDistanceScorer(n_features=n_features, window_size=min(256, window_size))
        self.uses_fallback = False

    def _maybe_fit(self) -> None:
        if len(self.window) < max(50, self.n_estimators // 2):
            return
        if self.model is None or self.i % self.refit_every == 0:
            X = np.asarray(self.window, dtype=float)
            self.model = IsolationForest(n_estimators=self.n_estimators, contamination="auto", random_state=self.seed, n_jobs=-1)
            self.model.fit(X)

    def score_one(self, x) -> float:
        x = as_array(x)
        if self.model is None:
            return self.warmup.score_one(x)
        raw = -float(self.model.score_samples(x.reshape(1, -1))[0])
        return raw / (1.0 + abs(raw)) if raw > 0 else 0.0

    def learn_one(self, x) -> None:
        x = as_array(x)
        self.window.append(x)
        self.warmup.learn_one(x)
        self.i += 1
        self._maybe_fit()
