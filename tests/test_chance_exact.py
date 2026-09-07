"""The exact finite-sample chance level of step-wise average precision.

Under a uniformly random permutation of n items with m positives,
E[AP] = (m-1)/(n-1) + (H_n/n)(n-m)/(n-1) (the full-list case of Manzhos,
Ianevych and Melnyk 2026, Theorem 1). The decimals check derives the
manuscript's printed value with this operator; the four values below are the
ones the second referee report computed independently for the paper's own
counts, so a regression here would mean the operator no longer matches an
outside derivation.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_decimals import compute  # noqa: E402


def test_matches_the_referee_values_to_nine_decimals():
    cases = [((240000, 163764), 0.682365837), ((240000, 60575), 0.252433107),
             ((78000, 60575), 0.776633616), ((30000, 4840), 0.161609716)]
    for (n, m), expected in cases:
        assert abs(compute("chance_exact", [n, m]) - expected) < 5e-10


def test_differs_from_prevalence_only_in_the_fifth_decimal_on_the_slice():
    v = compute("chance_exact", [240000, 163764])
    assert round(v, 6) == 0.682366 and abs(v - 163764 / 240000) < 2e-5
