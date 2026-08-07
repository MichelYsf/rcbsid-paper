import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from prevalence_lib import (  # noqa: E402
    draw_resample_indices,
    natural_rate,
    resample_to_prevalence,
    split_prevalences,
)


def make_stream(n=20000, rate=0.22, seed=7):
    rng = np.random.default_rng(seed)
    return (rng.random(n) < rate).astype(int)


def test_below_natural_hits_target_on_all_splits():
    y = make_stream()
    idx, info = resample_to_prevalence(y, 0.05, seed=11)
    assert abs(info["achieved_overall"] - 0.05) < 0.01
    for split in ("achieved_train", "achieved_val", "achieved_test"):
        assert abs(info[split] - 0.05) <= 0.01 + 1e-12


def test_above_natural_hits_target_on_all_splits():
    y = make_stream()
    idx, info = resample_to_prevalence(y, 0.64, seed=11)
    assert abs(info["achieved_overall"] - 0.64) < 0.01
    for split in ("achieved_train", "achieved_val", "achieved_test"):
        assert abs(info[split] - 0.64) <= 0.01 + 1e-12


def test_below_natural_keeps_every_benign_and_no_duplicates():
    y = make_stream()
    idx, _ = resample_to_prevalence(y, 0.10, seed=23)
    assert len(np.unique(idx)) == len(idx)
    benign_original = np.flatnonzero(y == 0)
    assert set(benign_original).issubset(set(idx.tolist()))


def test_above_natural_drops_only_structurally_excess_attacks():
    # On a uniformly mixed stream the attack mass is split-proportional, so
    # the joint-quota construction keeps essentially every attack (rounding
    # and the binding-segment cap may shave a small fraction).
    y = make_stream()
    idx, _ = resample_to_prevalence(y, 0.40, seed=23)
    attack_original = set(np.flatnonzero(y == 1).tolist())
    attacks_kept = attack_original & set(idx.tolist())
    assert len(attacks_kept) >= 0.97 * len(attack_original)
    assert len(np.unique(idx)) == len(idx)


def test_chronological_order_preserved():
    y = make_stream()
    rng = np.random.default_rng(0)
    idx = draw_resample_indices(y, 0.05, rng)
    assert np.all(np.diff(idx) > 0)


def test_deterministic_per_seed_and_distinct_across_seeds():
    y = make_stream()
    idx_a, _ = resample_to_prevalence(y, 0.05, seed=11)
    idx_b, _ = resample_to_prevalence(y, 0.05, seed=11)
    idx_c, _ = resample_to_prevalence(y, 0.05, seed=47)
    assert np.array_equal(idx_a, idx_b)
    assert not np.array_equal(idx_a, idx_c)


def test_redraw_counter_and_failure_path():
    # Adversarial stream: all attacks at the very end, so a 40% target can
    # never balance the front train split -> must exhaust redraws.
    y = np.concatenate([np.zeros(5000, dtype=int), np.ones(5000, dtype=int)])
    with pytest.raises(RuntimeError):
        resample_to_prevalence(y, 0.40, seed=11, max_redraws=3)


def test_split_prevalences_match_runner_cuts():
    y = np.array([0, 0, 0, 0, 0, 0, 0, 1, 1, 1])
    p = split_prevalences(y)  # int(10*0.7)=7 train, int(10*0.15)=1 val, 2 test
    assert p["train"] == 0.0
    assert p["val"] == 1.0
    assert p["test"] == 1.0


def test_natural_rate():
    assert natural_rate(np.array([0, 1, 1, 0])) == 0.5


def test_structural_gradient_still_hits_per_split_targets():
    # Mimic CICIDS: the tail of the stream is attack-richer than the front.
    # An unstratified uniform draw preserves this gradient and can never meet
    # the per-split tolerance at 40%; the stratified draw must.
    rng = np.random.default_rng(9)
    front = (rng.random(17000) < 0.20).astype(int)
    tail = (rng.random(3000) < 0.28).astype(int)
    y = np.concatenate([front, tail])
    for target in (0.05, 0.40, 0.64):
        _, info = resample_to_prevalence(y, target, seed=11)
        for split in ("achieved_train", "achieved_val", "achieved_test"):
            assert abs(info[split] - target) <= 0.01 + 1e-12, (target, split, info)
