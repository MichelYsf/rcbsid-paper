from __future__ import annotations
import numpy as np
from scipy.stats import rankdata
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler


class _EmpiricalTailDetector:
    def __init__(self, mode: str = 'ecod'):
        self.mode = mode
        self.scaler = StandardScaler()
        self.train_: np.ndarray | None = None

    def fit(self, X):
        X = np.asarray(X, dtype=float)
        self.train_ = self.scaler.fit_transform(X)
        return self

    def decision_function(self, X):
        Xs = self.scaler.transform(np.asarray(X, dtype=float))
        train = self.train_
        assert train is not None
        scores = []
        for j in range(Xs.shape[1]):
            col = train[:, j]
            # two-sided empirical tail probability with Laplace smoothing.
            ranks = np.searchsorted(np.sort(col), Xs[:, j], side='right')
            cdf = (ranks + 1.0) / (len(col) + 2.0)
            tail = np.minimum(cdf, 1.0 - cdf)
            scores.append(-np.log(np.maximum(tail, 1e-12)))
        S = np.vstack(scores).T
        if self.mode == 'copod':
            raw = np.max(S, axis=1)
        else:
            raw = np.mean(S, axis=1)
        return raw


def _minmax(scores):
    scores = np.asarray(scores, dtype=float)
    lo, hi = float(np.nanmin(scores)), float(np.nanmax(scores))
    if hi <= lo:
        return np.zeros_like(scores)
    return (scores - lo) / (hi - lo)


def run_batch_reference(name: str, X_train, X_eval, seed: int = 42):
    name = name.lower()
    X_train = np.asarray(X_train, dtype=float)
    X_eval = np.asarray(X_eval, dtype=float)
    if name in {'ecod', 'copod'}:
        try:
            if name == 'ecod':
                from pyod.models.ecod import ECOD  # type: ignore
                model = ECOD()
            else:
                from pyod.models.copod import COPOD  # type: ignore
                model = COPOD()
            model.fit(X_train)
            return _minmax(model.decision_function(X_eval))
        except Exception:
            model = _EmpiricalTailDetector(mode=name).fit(X_train)
            return _minmax(model.decision_function(X_eval))
    if name == 'lof':
        try:
            model = LocalOutlierFactor(n_neighbors=35, novelty=True, contamination='auto')
            model.fit(X_train)
            return _minmax(-model.score_samples(X_eval))
        except Exception:
            model = _EmpiricalTailDetector(mode='ecod').fit(X_train)
            return _minmax(model.decision_function(X_eval))
    raise KeyError(f'Unknown batch reference baseline: {name}')
