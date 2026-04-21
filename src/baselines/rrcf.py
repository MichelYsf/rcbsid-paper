from __future__ import annotations
import numpy as np
from .common import as_array, WindowDistanceScorer, BaselineDependencyError


class RRCFWrapper:
    def __init__(self, n_features: int, seed: int = 42, n_trees: int = 40, tree_size: int = 256, allow_fallback: bool = True):
        self.uses_fallback = False
        try:
            import rrcf  # type: ignore
            self.rrcf = rrcf
            self.forest = [rrcf.RCTree() for _ in range(n_trees)]
            self.tree_size = tree_size
            self.index = 0
            self.native = True
        except Exception as exc:
            if not allow_fallback:
                raise BaselineDependencyError(
                    "RRCF requires the rrcf package. Install requirements in Python 3.11 or enable fallback only for smoke tests."
                ) from exc
            self.native = False
            self.uses_fallback = True
            self.model = WindowDistanceScorer(n_features=n_features, window_size=tree_size)

    def score_one(self, x) -> float:
        x = as_array(x)
        if not self.native:
            return self.model.score_one(x)
        if self.index == 0:
            return 0.0
        scores = []
        for tree in self.forest:
            try:
                scores.append(float(tree.codisp(self.index - 1)))
            except Exception:
                pass
        if not scores:
            return 0.0
        raw = float(np.mean(scores))
        return raw / (1.0 + raw)

    def learn_one(self, x) -> None:
        x = as_array(x)
        if not self.native:
            self.model.learn_one(x)
            return
        i = self.index
        for tree in self.forest:
            if len(tree.leaves) >= self.tree_size:
                try:
                    tree.forget_point(i - self.tree_size)
                except Exception:
                    pass
            tree.insert_point(x, index=i)
        self.index += 1
