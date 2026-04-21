import numpy as np
from sklearn.metrics import roc_auc_score
from src.bocpd.truncated_bocpd import TruncatedBOCPDConfig, TruncatedGaussianBOCPD


def _score_stream(X):
    model = TruncatedGaussianBOCPD(TruncatedBOCPDConfig(hazard=0.001, max_run_length=200, variance_floor=1e-4, warmup=30))
    return np.asarray([model.update_score(row) for row in X], dtype=float)


def test_bocpd_detects_large_mean_shift():
    rng = np.random.default_rng(42)
    X = np.vstack([rng.normal(0, 1, size=(800, 3)), rng.normal(3, 1, size=(200, 3))])
    y = np.r_[np.zeros(800), np.ones(200)]
    scores = _score_stream(X)
    assert roc_auc_score(y, scores) > 0.90


def test_bocpd_detects_variance_shift():
    rng = np.random.default_rng(43)
    X = np.vstack([rng.normal(0, 1, size=(800, 3)), rng.normal(0, 3, size=(200, 3))])
    y = np.r_[np.zeros(800), np.ones(200)]
    scores = _score_stream(X)
    assert roc_auc_score(y, scores) > 0.80


def test_bocpd_no_change_is_near_random_for_artificial_labels():
    rng = np.random.default_rng(44)
    X = rng.normal(0, 1, size=(1000, 3))
    y = np.r_[np.zeros(800), np.ones(200)]
    scores = _score_stream(X)
    assert roc_auc_score(y, scores) < 0.65
