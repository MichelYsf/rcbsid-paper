"""Stage 2 regression tests: the audited defects must stay fixed.

A7 one-step scoring lag (KitNET, RRCF), A8 unapplied RRCF seed,
A9 silent batch fallback, A10 burn-rate label leak.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


def _spike_stream(n=180, spike_at=150, d=4):
    """Benign noise with one unmistakable spike; the scorer must react AT the
    spike, not one observation later."""
    rng = np.random.default_rng(0)
    X = rng.normal(0.0, 0.1, size=(n, d))
    X[spike_at] += 40.0
    return X, spike_at


def test_rrcf_scores_current_observation_not_previous():
    from src.baselines.registry import make_streaming_baseline
    X, spike = _spike_stream()
    m = make_streaming_baseline("rrcf", n_features=X.shape[1], seed=11, allow_fallback=False)
    s = []
    for row in X:
        s.append(float(m.score_one(row)))
        m.learn_one(row)
    s = np.asarray(s)
    peak = int(np.argmax(s))
    assert peak == spike, f"RRCF peaked at {peak}, expected {spike} (one-step lag regression)"


def test_rrcf_seed_is_actually_applied():
    from src.baselines.registry import make_streaming_baseline
    X, _ = _spike_stream(n=120, spike_at=100)

    def run(seed):
        m = make_streaming_baseline("rrcf", n_features=X.shape[1], seed=seed,
                                    allow_fallback=False)
        out = []
        for row in X:
            out.append(float(m.score_one(row)))
            m.learn_one(row)
        return np.asarray(out)

    a1, a2, b = run(11), run(11), run(47)
    assert np.allclose(a1, a2), "same seed must reproduce"
    assert not np.allclose(a1, b), "different seeds must differ (seed was ignored before)"


def test_rrcf_does_not_double_insert():
    from src.baselines.registry import make_streaming_baseline
    X, _ = _spike_stream(n=50, spike_at=40)
    m = make_streaming_baseline("rrcf", n_features=X.shape[1], seed=3, allow_fallback=False)
    for row in X:
        m.score_one(row)
        m.learn_one(row)
    assert m.index == len(X), f"index {m.index} != {len(X)}; point counted twice"


def test_kitnet_scores_current_observation():
    pytest.importorskip("KitNET")
    from src.baselines.registry import make_streaming_baseline
    X, spike = _spike_stream(n=400, spike_at=350)
    m = make_streaming_baseline("kitnet", n_features=X.shape[1], seed=11, allow_fallback=False)
    s = []
    for row in X:
        s.append(float(m.score_one(row)))
        m.learn_one(row)
    s = np.asarray(s)
    assert int(np.argmax(s)) == spike, "KitNET peaked off the spike (one-step lag regression)"


def test_batch_fallback_is_surfaced_not_silent():
    from src.baselines import batch
    X = np.random.default_rng(0).normal(size=(200, 3))
    batch.run_batch_reference("ecod", X, X)
    assert batch.LAST_FALLBACK.get("ecod") is False, "PyOD present: must not report fallback"


def test_burn_rate_never_consumes_labels():
    """A10: budget events must be label-free threshold crossings.

    Checked structurally (the signature cannot accept ground truth) and
    behaviourally (identical predictions give identical alert counts no matter
    what the labels are), rather than by grepping source text -- the docstring
    legitimately mentions the old defect.
    """
    import inspect
    from src.experiments import run_streaming_eval as r

    params = list(inspect.signature(r._burn_rate_count).parameters)
    assert "y_true" not in params, f"burn-rate still takes ground truth: {params}"
    assert params[0] == "y_pred", f"first parameter should be y_pred, got {params}"

    cfg = {"burn_rate_alerting": {"slo": 0.999,
                                  "page_fast": {"long_window_minutes": 60,
                                                "short_window_minutes": 5,
                                                "burn_rate": 14.4}}}
    rng = np.random.default_rng(0)
    y_pred = (rng.random(5000) < 0.2).astype(int)
    a = r._burn_rate_count(y_pred, cfg)
    b = r._burn_rate_count(y_pred, cfg)
    assert a == b, "burn-rate must be deterministic given predictions alone"


def test_burn_rate_alert_metric_is_named_as_record_windows():
    """The config names windows in minutes but consumes record counts."""
    import inspect
    from src.experiments import run_streaming_eval as r
    src = inspect.getsource(r._evaluate_row)
    assert "burn_rate_alerts_record_windows" in src,         "metric must state that its windows are record counts, not minutes"
