from __future__ import annotations
from collections import deque
import numpy as np
from .common import as_array, RunningStandardizer


class LODAWrapper:
    """Dependency-free online LODA baseline.

    This implements the core LODA idea from Pevny (2016): random one-dimensional
    projections plus histogram-density scoring. We intentionally do **not** use
    ``pysad.models.LODA`` because audit testing showed that the PySAD 0.3.4 LODA
    implementation can collapse to a constant score vector on simple streams.

    The implementation is considered native for this project: it has no fallback
    mode, no optional dependency, and is safe for publication runs. It follows
    the score-before-learn streaming convention used by the experiment runner.
    """

    def __init__(
        self,
        n_features: int,
        seed: int = 42,
        n_projections: int = 100,
        window_size: int = 512,
        n_bins: int = 32,
        allow_fallback: bool = True,  # kept for registry API compatibility
    ):
        self.uses_fallback = False
        self.native = True
        self.n_features = int(n_features)
        self.n_bins = int(n_bins)
        self.window = deque(maxlen=int(window_size))
        self.scaler = RunningStandardizer(n_features=n_features)

        rng = np.random.default_rng(seed)
        W = rng.normal(size=(int(n_projections), int(n_features)))
        norms = np.maximum(np.linalg.norm(W, axis=1, keepdims=True), 1e-12)
        self.W = W / norms

    def _project(self, x) -> np.ndarray:
        z = self.scaler.transform(as_array(x))
        return self.W @ z

    def score_one(self, x) -> float:
        projected_x = self._project(x)
        if len(self.window) < max(20, self.n_bins):
            return 0.0

        history = np.asarray(self.window, dtype=float)
        scores = []
        n = history.shape[0]

        for j, value in enumerate(projected_x):
            col = history[:, j]
            lo = float(np.min(col))
            hi = float(np.max(col))
            if not np.isfinite(value) or not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
                scores.append(0.0)
                continue

            # Values outside the observed projection range are assigned the
            # lowest smoothed density rather than being clipped into an edge bin.
            if value < lo or value > hi:
                density = 1.0 / (n + self.n_bins)
            else:
                hist, edges = np.histogram(col, bins=self.n_bins, range=(lo, hi))
                idx = int(np.searchsorted(edges, value, side="right") - 1)
                idx = int(np.clip(idx, 0, self.n_bins - 1))
                density = (hist[idx] + 1.0) / (n + self.n_bins)
            scores.append(-np.log(max(float(density), 1e-12)))

        raw = float(np.mean(scores)) if scores else 0.0
        # Map positive density-surprise to [0,1), preserving ranking.
        return float(raw / (1.0 + raw))

    def learn_one(self, x) -> None:
        # Project using statistics available before seeing x, then update the
        # running standardizer. This preserves the score-before-learn protocol.
        projected_x = self._project(x)
        self.window.append(projected_x)
        self.scaler.learn_one(x)
