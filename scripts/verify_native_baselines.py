#!/usr/bin/env python3
"""Verify that publication baselines instantiate and score natively.

This script is intentionally stricter than a smoke test. It fails if a baseline
falls back to a dependency-light implementation, and it also fails if a native
baseline silently returns a constant score vector. Run it before launching the
full publication experiments.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.baselines.registry import make_streaming_baseline

BASELINES = ["hst", "kitnet", "loda", "xstream", "rrcf", "iforest_asd"]


def exercise_baseline(model, n_features: int = 5, n: int = 350, seed: int = 42) -> np.ndarray:
    """Run score-then-learn on a small synthetic stream and return scores."""
    rng = np.random.default_rng(seed)
    x0 = rng.normal(0.0, 1.0, size=(n // 2, n_features))
    x1 = rng.normal(2.5, 1.0, size=(n - n // 2, n_features))
    X = np.vstack([x0, x1])
    scores = []
    for row in X:
        scores.append(float(model.score_one(row)))
        model.learn_one(row)
    return np.asarray(scores, dtype=float)


def main() -> int:
    failed = []
    for name in BASELINES:
        try:
            model = make_streaming_baseline(name, n_features=5, seed=42, allow_fallback=False)
            if getattr(model, "uses_fallback", False):
                failed.append((name, "constructed fallback"))
                continue
            scores = exercise_baseline(model)
            tail = scores[100:]
            if not np.all(np.isfinite(tail)):
                failed.append((name, "native scorer produced non-finite values"))
                continue
            if float(np.std(tail)) <= 1e-9:
                failed.append((name, "native scorer produced a constant score vector"))
                continue
            print(f"OK: {name} native; score_std={float(np.std(tail)):.6g}")
        except Exception as exc:
            failed.append((name, str(exc)))
    if failed:
        print("\nFAILED native-baseline verification:")
        for name, err in failed:
            print(f"- {name}: {err}")
        print("\nDo not run publication experiments until these are fixed. Smoke tests may use fallbacks, but paper tables must not.")
        return 1
    print("\nAll publication streaming baselines are native and produce non-constant scores.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
