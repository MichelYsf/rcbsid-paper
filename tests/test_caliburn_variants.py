import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from caliburn_variants import (  # noqa: E402
    caliburn_variant_evaluations,
    crc_threshold,
    elkan_threshold,
    fit_isotonic,
    threshold_operating_point,
)


def test_elkan_threshold_matches_paper():
    assert abs(elkan_threshold(10.0) - 1.0 / 11.0) < 1e-12  # 0.0909... = paper's 0.091
    assert abs(elkan_threshold(1.0) - 0.5) < 1e-12
    assert abs(elkan_threshold(50.0) - 0.0196078) < 1e-6


def test_crc_bound_holds_on_calibration_set():
    rng = np.random.default_rng(0)
    benign = rng.random(10000)
    alpha = 0.05
    tau = crc_threshold(benign, alpha)
    n0 = len(benign)
    fpr = np.mean(benign >= tau)
    assert (n0 * fpr + 1) / (n0 + 1) <= alpha
    # And tau is the *smallest* candidate: one score-step lower must violate.
    lower = benign[benign < tau]
    if len(lower):
        tau_prev = np.max(lower)
        fpr_prev = np.mean(benign >= tau_prev)
        assert (n0 * fpr_prev + 1) / (n0 + 1) > alpha


def test_crc_infeasible_on_saturated_scores():
    # 5% of benign scores sit exactly at 1.0 -> no tau in [0,1] can push the
    # upper-bounded FPR below alpha=0.01 under the >= alert rule (paper Table 12 N/A).
    benign = np.concatenate([np.full(500, 1.0), np.linspace(0, 0.5, 9500)])
    assert np.isnan(crc_threshold(benign, 0.01))


def test_crc_monotone_in_alpha():
    rng = np.random.default_rng(1)
    benign = rng.random(5000)
    taus = [crc_threshold(benign, a) for a in (0.01, 0.05, 0.10)]
    assert taus[0] >= taus[1] >= taus[2]


def test_isotonic_is_monotone_and_bounded():
    rng = np.random.default_rng(2)
    s = rng.random(2000)
    y = (rng.random(2000) < np.clip(s, 0, 1)).astype(int)
    iso = fit_isotonic(s, y)
    grid = np.linspace(0, 1, 101)
    p = iso.predict(grid)
    assert np.all(np.diff(p) >= -1e-12)
    assert p.min() >= 0.0 and p.max() <= 1.0


def test_operating_point_counts():
    scores = np.array([0.0, 0.2, 0.5, 0.9, 1.0])
    y = np.array([0, 0, 1, 0, 1])
    op = threshold_operating_point(scores, y, 0.5)
    assert op["alert_rate"] == pytest.approx(3 / 5)
    assert op["test_fpr"] == pytest.approx(1 / 3)  # only the 0.9 benign alerts
    assert op["recall"] == pytest.approx(1.0)
    assert op["precision"] == pytest.approx(2 / 3)


def test_operating_point_infeasible_threshold_is_all_zero():
    op = threshold_operating_point(np.array([0.1, 0.9]), np.array([0, 1]), float("nan"))
    assert op == {"alert_rate": 0.0, "test_fpr": 0.0, "recall": 0.0, "precision": 0.0, "f1": 0.0}


def test_variant_evaluations_end_to_end():
    rng = np.random.default_rng(3)
    n = 4000
    y_val = (rng.random(n) < 0.2).astype(int)
    s_val = np.clip(0.4 * y_val + 0.3 * rng.random(n), 0, 1)
    y_test = (rng.random(n) < 0.2).astype(int)
    s_test = np.clip(0.4 * y_test + 0.3 * rng.random(n), 0, 1)
    ev = caliburn_variant_evaluations(s_val, y_val, s_test, y_test, alpha=0.05)
    assert set(ev["rows"]) == {"bocpd_v1_iso_crc", "bocpd_v3_iso_elkan", "bocpd_v4_raw_elkan"}
    assert ev["shared"]["brier_iso"] <= ev["shared"]["brier_raw"] + 0.05
    assert ev["rows"]["bocpd_v3_iso_elkan"]["threshold"] == pytest.approx(1 / 11)
    v1 = ev["rows"]["bocpd_v1_iso_crc"]
    if np.isfinite(v1["threshold"]):
        n0 = int(np.sum(y_val == 0))
        assert (n0 * v1["test_fpr"] + 1) / (n0 + 1) <= 0.05 + 0.03  # loose test-side check
