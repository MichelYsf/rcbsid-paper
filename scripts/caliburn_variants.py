#!/usr/bin/env python
"""CALIBURN calibration / CRC variant layer (paper Sections 3.3-3.4, Table 12).

Implements, on top of the repo's raw BOCPD scores:
- isotonic calibration g fit on the validation split (Zadrozny & Elkan 2002),
- the cost-sensitive (Elkan) threshold tau* = 1 / (1 + C)  (Eq. 13; C=10 -> 0.091),
- Conformal Risk Control for a false-positive alert budget alpha (Eq. 16):
      tau_hat = inf { tau in [0,1] : (n0 * FPR_val(tau) + 1) / (n0 + 1) <= alpha }
  where FPR_val is the empirical FPR of the (calibrated) scores on validation
  negatives and alerts fire when score >= tau (the repo-wide decision rule).
  If no tau in [0,1] satisfies the bound (e.g. raw scores saturating at 1.0),
  the threshold is infeasible and NaN is returned — matching the paper's
  Table 12 "N/A" rows.

Variants (Table 12; all share the same BOCPD scoring stage):
- V1 (Full):       isotonic + CRC threshold at alpha
- V3 (No CRC):     isotonic + Elkan tau* = 0.091
- V4 (raw+Elkan):  raw scores + Elkan tau* = 0.091
(V2 = raw + CRC exists in the paper but is not part of the Stage 2 sweep.)
"""
from __future__ import annotations

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss


def fit_isotonic(scores_val: np.ndarray, y_val: np.ndarray) -> IsotonicRegression:
    iso = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds="clip")
    iso.fit(np.asarray(scores_val, dtype=float), np.asarray(y_val, dtype=int))
    return iso


def elkan_threshold(cost_ratio: float = 10.0) -> float:
    """tau* = C_FP / (C_FP + C_FN) = 1 / (1 + C) with C = C_FN / C_FP (Eq. 13)."""
    if cost_ratio <= 0:
        raise ValueError("cost_ratio must be positive")
    return 1.0 / (1.0 + cost_ratio)


def crc_threshold(benign_val_scores: np.ndarray, alpha: float) -> float:
    """CRC threshold per Eq. 16 with the >= alert rule. NaN if infeasible."""
    s = np.sort(np.asarray(benign_val_scores, dtype=float))
    n0 = len(s)
    if n0 == 0:
        raise ValueError("no validation negatives to calibrate on")
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must be in (0, 1)")

    def bound(tau: float) -> float:
        n_alert = n0 - np.searchsorted(s, tau, side="left")  # count of s >= tau
        return (float(n_alert) + 1.0) / (n0 + 1.0)

    # The bound is a step function with jumps at the score values; the infimum
    # of the feasible set is attained either at a score value or just above the
    # maximum benign score (where FPR drops to zero).
    for tau in np.unique(s):
        if bound(float(tau)) <= alpha:
            return float(tau)
    tau_above = float(np.nextafter(s[-1], np.inf))
    if tau_above <= 1.0 and bound(tau_above) <= alpha:
        return tau_above
    return float("nan")


def threshold_operating_point(scores: np.ndarray, y: np.ndarray, tau: float) -> dict:
    """Alert-rate / FPR / recall / precision / F1 at threshold tau (>= rule)."""
    scores = np.asarray(scores, dtype=float)
    y = np.asarray(y, dtype=int)
    if not np.isfinite(tau):
        return {"alert_rate": 0.0, "test_fpr": 0.0, "recall": 0.0, "precision": 0.0, "f1": 0.0}
    pred = (scores >= tau).astype(int)
    n_benign = int(np.sum(y == 0))
    n_attack = int(np.sum(y == 1))
    tp = int(np.sum((pred == 1) & (y == 1)))
    fp = int(np.sum((pred == 1) & (y == 0)))
    alert_rate = float(np.mean(pred))
    fpr = fp / n_benign if n_benign else float("nan")
    recall = tp / n_attack if n_attack else float("nan")
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"alert_rate": alert_rate, "test_fpr": float(fpr), "recall": float(recall),
            "precision": float(precision), "f1": float(f1)}


def brier(y: np.ndarray, scores: np.ndarray) -> float:
    return float(brier_score_loss(np.asarray(y, dtype=int), np.clip(np.asarray(scores, dtype=float), 0, 1)))


def caliburn_variant_evaluations(
    scores_val_raw: np.ndarray,
    y_val: np.ndarray,
    scores_test_raw: np.ndarray,
    y_test: np.ndarray,
    alpha: float = 0.01,
    cost_ratio: float = 10.0,
) -> dict:
    """Evaluate V1 / V3 / V4 on one scored stream. Returns a dict of row dicts
    plus the shared calibration diagnostics."""
    y_val = np.asarray(y_val, dtype=int)
    y_test = np.asarray(y_test, dtype=int)
    iso = fit_isotonic(scores_val_raw, y_val)
    p_val = iso.predict(np.asarray(scores_val_raw, dtype=float))
    p_test = iso.predict(np.asarray(scores_test_raw, dtype=float))

    tau_star = elkan_threshold(cost_ratio)
    tau_crc = crc_threshold(p_val[y_val == 0], alpha)

    shared = {
        "brier_raw": brier(y_test, scores_test_raw),
        "brier_iso": brier(y_test, p_test),
        "crc_alpha": float(alpha),
        "crc_tau": float(tau_crc),
        "elkan_tau": float(tau_star),
    }
    variants = {
        "bocpd_v1_iso_crc": {"scores": p_test, "tau": tau_crc},
        "bocpd_v3_iso_elkan": {"scores": p_test, "tau": tau_star},
        "bocpd_v4_raw_elkan": {"scores": np.asarray(scores_test_raw, dtype=float), "tau": tau_star},
    }
    out = {"shared": shared, "rows": {}, "p_test_iso": p_test, "p_val_iso": p_val}
    for name, v in variants.items():
        op = threshold_operating_point(v["scores"], y_test, v["tau"])
        out["rows"][name] = {"threshold": float(v["tau"]), **op}
    return out
