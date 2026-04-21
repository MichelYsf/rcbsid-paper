import numpy as np
from sklearn.metrics import roc_auc_score
from src.baselines.registry import make_streaming_baseline, score_streaming_model


def test_streaming_baselines_are_instantiable_and_score():
    rng = np.random.default_rng(123)
    X = np.vstack([rng.normal(0, 1, size=(600, 3)), rng.normal(2, 1, size=(150, 3))])
    y = np.r_[np.zeros(600), np.ones(150)]
    for name in ['hst', 'kitnet', 'loda', 'xstream', 'rrcf', 'iforest_asd']:
        model = make_streaming_baseline(name, n_features=3, seed=42)
        scores = np.asarray(score_streaming_model(model, X), dtype=float)
        assert len(scores) == len(y)
        assert np.all(np.isfinite(scores))
        # Not every fallback is expected to be strong on tiny streams, but it
        # must produce a non-crashing, non-constant score vector after warm-up.
        assert np.nanstd(scores[250:]) > 0
