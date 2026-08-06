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


def draw_resample_indices(y: np.ndarray, target_rate: float, rng: np.random.Generator) -> np.ndarray:
    """One random draw of retained flow indices, in original chronological order.

    Below natural rate: keep all benign flows, subsample attacks.
    Above natural rate: keep all attack flows, subsample benigns.
    """
    y = np.asarray(y, dtype=int)
    attack_idx = np.flatnonzero(y == 1)
    benign_idx = np.flatnonzero(y == 0)
    n_attack, n_benign = len(attack_idx), len(benign_idx)
    if n_attack == 0 or n_benign == 0:
        raise ValueError("stream must contain both classes")
    natural = n_attack / (n_attack + n_benign)
    if not (0.0 < target_rate < 1.0):
        raise ValueError("target_rate must be in (0, 1)")

    if target_rate <= natural:
        # keep benigns, thin attacks: a / (a + n_benign) = target
        keep_attacks = int(round(target_rate * n_benign / (1.0 - target_rate)))
        keep_attacks = max(1, min(keep_attacks, n_attack))
        chosen = rng.choice(attack_idx, size=keep_attacks, replace=False)
        retained = np.concatenate([benign_idx, chosen])
    else:
        # keep attacks, thin benigns: n_attack / (n_attack + b) = target
        keep_benign = int(round(n_attack * (1.0 - target_rate) / target_rate))
        keep_benign = max(1, min(keep_benign, n_benign))
        chosen = rng.choice(benign_idx, size=keep_benign, replace=False)
        retained = np.concatenate([attack_idx, chosen])
    return np.sort(retained)  # chronological order, no duplicates by construction


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
