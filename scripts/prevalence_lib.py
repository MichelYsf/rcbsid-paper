#!/usr/bin/env python
"""Prevalence resampling for the fixed-dataset prevalence sweep (Stage 2).

Protocol (from the experiment runbook):
- Below natural prevalence: randomly subsample attack flows to the target rate.
- Above natural prevalence: randomly subsample benign flows.
- Selection is random by flow, but retained flows keep their original
  chronological order. Flows are never duplicated.
- The standard chronological 70/15/15 split is applied *after* resampling.
- Achieved prevalence in every split must land within `tolerance_pp`
  percentage points of the target, otherwise the draw is redone with a
  derived seed (seed + 100000 * attempt). Redraws are logged in the info dict.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def split_prevalences(y: np.ndarray, train_ratio: float = 0.70, val_ratio: float = 0.15) -> dict:
    """Prevalence per chronological split, using the runner's exact int() cuts."""
    n = len(y)
    i_train = int(n * train_ratio)
    i_val = i_train + int(n * val_ratio)
    return {
        "train": float(np.mean(y[:i_train])) if i_train > 0 else float("nan"),
        "val": float(np.mean(y[i_train:i_val])) if i_val > i_train else float("nan"),
        "test": float(np.mean(y[i_val:])) if n > i_val else float("nan"),
    }


def draw_resample_indices(y: np.ndarray, target_rate: float, rng: np.random.Generator,
                          train_ratio: float = 0.70, val_ratio: float = 0.15) -> np.ndarray:
    """One random draw of retained flow indices, in original chronological order.

    Below natural rate: keep all benign flows, subsample attacks.
    Above natural rate: keep all attack flows, subsample benigns.

    The draw is STRATIFIED over the three chronological split segments: the
    thinned class gets a per-segment quota that hits the target rate inside
    each segment. This is required, not cosmetic: the interleaved stream's
    attack share varies structurally across splits (CICIDS2017: train 21.46%,
    val 21.70%, test 25.24%), so an unstratified uniform draw preserves that
    gradient and the runbook's per-split 1 pp tolerance can never be met at
    targets far from natural (e.g. 40% target -> ~44.3% test split, a
    structural bias no redraw can fix). Stratification keeps selection random
    by flow within each segment, preserves chronological order, and never
    duplicates a flow.
    """
    y = np.asarray(y, dtype=int)
    n = len(y)
    if not (0.0 < target_rate < 1.0):
        raise ValueError("target_rate must be in (0, 1)")
    n_attack_total = int(np.sum(y == 1))
    n_benign_total = n - n_attack_total
    if n_attack_total == 0 or n_benign_total == 0:
        raise ValueError("stream must contain both classes")
    natural = n_attack_total / n

    i_train = int(n * train_ratio)
    i_val = i_train + int(n * val_ratio)
    segments = [(0, i_train), (i_train, i_val), (i_val, n)]

    kept: list[np.ndarray] = []
    if target_rate <= natural:
        for lo, hi in segments:
            seg_y = y[lo:hi]
            attack_idx = np.flatnonzero(seg_y == 1) + lo
            benign_idx = np.flatnonzero(seg_y == 0) + lo
            # keep all benigns in the segment, thin its attacks to the target
            quota = int(round(target_rate * len(benign_idx) / (1.0 - target_rate)))
            quota = max(1, min(quota, len(attack_idx))) if len(attack_idx) else 0
            chosen = rng.choice(attack_idx, size=quota, replace=False) if quota else attack_idx[:0]
            kept.append(benign_idx)
            kept.append(chosen)
    else:
        # Above natural, keeping ALL attacks is mathematically incompatible
        # with per-split targets whenever the attack mass is not distributed
        # in the split proportions (CICIDS: 68.1/14.8/17.2 vs 70/15/15 — the
        # test split is attack-over-endowed). Choose the largest resampled
        # stream n' whose 70/15/15 re-split hits the target rate in EVERY
        # split, then draw per-segment quotas for BOTH classes; only the
        # structurally excess attacks of over-endowed segments are thinned.
        kept = []
        seg_frac = [(hi - lo) / n for lo, hi in segments]
        n_prime = None
        for (lo, hi), r in zip(segments, seg_frac):
            seg_y = y[lo:hi]
            a, b = int(np.sum(seg_y == 1)), int(np.sum(seg_y == 0))
            cap = min(a / (target_rate * r), b / ((1.0 - target_rate) * r)) if a and b else 0.0
            n_prime = cap if n_prime is None else min(n_prime, cap)
        n_prime = int(n_prime or 0)
        if n_prime < 100:
            raise ValueError("target rate structurally unachievable on this stream")
        for (lo, hi), r in zip(segments, seg_frac):
            seg_y = y[lo:hi]
            attack_idx = np.flatnonzero(seg_y == 1) + lo
            benign_idx = np.flatnonzero(seg_y == 0) + lo
            length = r * n_prime
            qa = min(int(round(target_rate * length)), len(attack_idx))
            qb = min(int(round((1.0 - target_rate) * length)), len(benign_idx))
            kept.append(rng.choice(attack_idx, size=qa, replace=False))
            kept.append(rng.choice(benign_idx, size=qb, replace=False))
    return np.sort(np.concatenate(kept))  # chronological order, no duplicates


def resample_to_prevalence(
    y: np.ndarray,
    target_rate: float,
    seed: int,
    tolerance_pp: float = 1.0,
    max_redraws: int = 20,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
) -> tuple[np.ndarray, dict]:
    """Resample the stream to a target prevalence with a per-split tolerance gate.

    Returns (retained_indices, info). Raises RuntimeError if no draw within
    `max_redraws` lands every split inside the tolerance.
    """
    tol = tolerance_pp / 100.0
    for attempt in range(max_redraws + 1):
        rng = np.random.default_rng(seed + 100000 * attempt)
        idx = draw_resample_indices(y, target_rate, rng)
        prevs = split_prevalences(np.asarray(y)[idx], train_ratio, val_ratio)
        if all(abs(p - target_rate) <= tol for p in prevs.values()):
            info = {
                "target_rate": float(target_rate),
                "seed": int(seed),
                "n_redraws": int(attempt),
                "effective_seed": int(seed + 100000 * attempt),
                "n_flows": int(len(idx)),
                "achieved_overall": float(np.mean(np.asarray(y)[idx])),
                "achieved_train": prevs["train"],
                "achieved_val": prevs["val"],
                "achieved_test": prevs["test"],
            }
            return idx, info
    raise RuntimeError(
        f"no draw achieved target {target_rate:.4f} within {tolerance_pp}pp on all "
        f"splits after {max_redraws} redraws (seed {seed})"
    )


def natural_rate(y: np.ndarray) -> float:
    y = np.asarray(y, dtype=int)
    return float(np.mean(y))
