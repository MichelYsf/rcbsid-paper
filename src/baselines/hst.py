from __future__ import annotations
from .common import as_array, WindowDistanceScorer, BaselineDependencyError


class HalfSpaceTreesWrapper:
    def __init__(self, n_features: int | None = None, seed: int = 42, n_trees: int = 25, height: int = 15, window_size: int = 250, allow_fallback: bool = True):
        self.uses_fallback = False
        try:
            from river import anomaly, compose, preprocessing
            self.model = compose.Pipeline(
                preprocessing.MinMaxScaler(),
                anomaly.HalfSpaceTrees(n_trees=n_trees, height=height, window_size=window_size, seed=seed),
            )
            self.native = True
        except Exception as exc:
            if not allow_fallback:
                raise BaselineDependencyError("HalfSpaceTrees requires river. Install requirements in Python 3.11 or enable fallback only for smoke tests.") from exc
            if n_features is None:
                raise
            self.model = WindowDistanceScorer(n_features=n_features, window_size=window_size)
            self.native = False
            self.uses_fallback = True

    def _to_dict(self, x):
        arr = as_array(x)
        return {f"f{i}": float(v) for i, v in enumerate(arr)}

    def score_one(self, x) -> float:
        if self.native:
            return float(self.model.score_one(self._to_dict(x)))
        return self.model.score_one(x)

    def learn_one(self, x) -> None:
        if self.native:
            self.model.learn_one(self._to_dict(x))
        else:
            self.model.learn_one(x)


def make_hst(seed: int = 42, n_features: int | None = None):
    return HalfSpaceTreesWrapper(n_features=n_features, seed=seed)


def score_stream(model, X):
    scores = []
    for x in X:
        scores.append(model.score_one(x))
        model.learn_one(x)
    return scores
