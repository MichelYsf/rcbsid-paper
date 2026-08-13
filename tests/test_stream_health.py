"""Regression tests for the stream-health gate.

Guards the 2026-08-13 incident: an un-interleaved LITNET stream (three
contiguous attack-type blocks) sent pure `spam` into validation and test, and
an entire cloud run produced garbage before anyone noticed.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import check_stream_health as csh  # noqa: E402


def _blocked(tmp_path):
    """Three contiguous attack-type blocks — the broken layout."""
    rows = []
    for name, n, rate in (("blaster_worm", 5000, 0.008), ("udp_flood", 5000, 0.148),
                          ("spam", 5000, 0.0006)):
        rng = np.random.default_rng(len(name))
        rows.append(pd.DataFrame({"label": (rng.random(n) < rate).astype(int),
                                  "attack_type": name}))
    p = tmp_path / "blocked.csv"
    pd.concat(rows, ignore_index=True).to_csv(p, index=False)
    return p


def _interleaved(tmp_path):
    """Round-robin across the same three types — the documented layout."""
    frames = []
    for name, n, rate in (("blaster_worm", 5000, 0.008), ("udp_flood", 5000, 0.148),
                          ("spam", 5000, 0.0006)):
        rng = np.random.default_rng(len(name))
        frames.append(pd.DataFrame({"label": (rng.random(n) < rate).astype(int),
                                    "attack_type": name}))
    inter = pd.concat(frames, ignore_index=True).iloc[
        np.array([[i, i + 5000, i + 10000] for i in range(5000)]).ravel()
    ].reset_index(drop=True)
    p = tmp_path / "interleaved.csv"
    inter.to_csv(p, index=False)
    return p


def test_blocked_stream_is_rejected(tmp_path, capsys):
    problems = csh.check("litnet2020", _blocked(tmp_path))
    assert problems, "a blocked stream must be rejected"
    joined = " ".join(problems)
    assert "NOT interleaved" in joined
    assert "validation prevalence" in joined  # pure-spam validation also caught


def test_interleaved_stream_passes(tmp_path):
    assert csh.check("litnet2020", _interleaved(tmp_path)) == []


def test_missing_stream_is_skipped_not_failed(tmp_path):
    assert csh.check("litnet2020", tmp_path / "absent.csv") == []


def test_low_validation_prevalence_is_rejected(tmp_path):
    # Interleaved (so the type-change check passes) but almost no positives:
    # selection on this validation split would be noise.
    n = 9000
    d = pd.DataFrame({"label": 0, "attack_type": ["a", "b", "c"] * (n // 3)})
    d.loc[:5, "label"] = 1
    p = tmp_path / "sparse.csv"
    d.to_csv(p, index=False)
    problems = csh.check("litnet2020", p)
    assert any("validation prevalence" in x for x in problems)


def test_thresholds_match_the_documented_gate():
    assert csh.MIN_TYPE_CHANGES == 1000
    assert csh.MIN_VAL_PREVALENCE == 0.01
