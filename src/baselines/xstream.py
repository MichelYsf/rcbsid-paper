from __future__ import annotations
import numpy as np
from .common import as_array, WindowDistanceScorer, BaselineDependencyError
from .score_utils import scalar_score


class XStreamWrapper:
    """xStream baseline wrapper.

    Uses PySAD xStream when available; otherwise falls back to a streaming random
    projection distance scorer. The fallback is clearly marked and intended for
    CI/smoke tests, not for final paper numbers.
    """
    def __init__(self, n_features: int, seed: int = 42, window_size: int = 256, allow_fallback: bool = True):
        self.uses_fallback = False
        try:
            from pysad.models import xStream  # type: ignore
            self.model = xStream()
            self.native = True
        except Exception as exc:
            if not allow_fallback:
                raise BaselineDependencyError("xStream requires pysad and mmh3. Install requirements in Python 3.11 or enable fallback only for smoke tests.") from exc
            self.native = False
            self.uses_fallback = True
            self.model = WindowDistanceScorer(n_features=n_features, window_size=window_size)

    def score_one(self, x) -> float:
        x = as_array(x)
        if self.native:
            try:
                return scalar_score(self.model.score_partial(x))
            except AttributeError:
                # Some PySAD versions require a first fit_partial before score_partial.
                return 0.0
        return float(self.model.score_one(x))

    def learn_one(self, x) -> None:
        x = as_array(x)
        if self.native:
            self.model.fit_partial(x)
        else:
            self.model.learn_one(x)
