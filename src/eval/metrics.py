from __future__ import annotations
import numpy as np
from scipy.stats import wilcoxon
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, precision_recall_fscore_support

def expected_calibration_error(y_true, y_prob, n_bins=10):
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (y_prob >= bins[i]) & (y_prob < bins[i+1] if i < n_bins - 1 else y_prob <= bins[i+1])
        if mask.any():
            ece += mask.mean() * abs(y_true[mask].mean() - y_prob[mask].mean())
    return float(ece)

def classification_metrics(y_true, scores, threshold):
    y_true = np.asarray(y_true).astype(int)
    scores = np.asarray(scores, dtype=float)
    y_pred = (scores >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary', zero_division=0)
    return {
        'auc_roc': float(roc_auc_score(y_true, scores)) if len(set(y_true)) > 1 else float('nan'),
        'auc_pr': float(average_precision_score(y_true, scores)) if len(set(y_true)) > 1 else float('nan'),
        'precision': float(precision),
        'recall': float(recall),
        'f1': float(f1),
        'brier': float(brier_score_loss(y_true, np.clip(scores, 0, 1))),
        'ece_10': expected_calibration_error(y_true, np.clip(scores, 0, 1), 10),
    }

def bootstrap_ci(values, confidence=0.95, n_bootstrap=5000, seed=42):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = [np.mean(rng.choice(values, size=len(values), replace=True)) for _ in range(n_bootstrap)]
    alpha = 1 - confidence
    return float(np.mean(values)), float(np.quantile(means, alpha/2)), float(np.quantile(means, 1-alpha/2))

def wilcoxon_against_reference(reference_values, baseline_values):
    stat, p = wilcoxon(reference_values, baseline_values, zero_method='wilcox', alternative='two-sided')
    return float(stat), float(p)

def holm_bonferroni(p_values):
    ordered = sorted(p_values.items(), key=lambda kv: kv[1])
    m = len(ordered)
    return {name: min((m-i)*p, 1.0) for i, (name, p) in enumerate(ordered)}
