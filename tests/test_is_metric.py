"""CI-38: an interval bound or point estimate OF a metric is that metric.

The referee-round bootstrap emits RefBoot...MarginLo / MarginHi / MarginPoint
whose descriptions say only "percentile of that margin"; before the fix they
rendered at the five decimals they were emitted with and the width check,
which groups by name suffix, filed them in the catch-all family and passed.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from provenance import is_metric  # noqa: E402


def test_interval_bounds_and_points_of_a_metric_are_that_metric():
    assert is_metric("RefBootSharedTwoFourZeroNaturalMarginHi",
                     "97.5th percentile of that margin, block bootstrap")
    assert is_metric("RefBootSharedSevenEightSyntheticMarginLo",
                     "2.5th percentile of that margin, block bootstrap")
    assert is_metric("RefBootFullNaturalMarginPoint",
                     "ECOD minus detector margin, from reported values")
    assert is_metric("RefBootBranchAuxOnlyAucrocLo", "2.5th percentile")


def test_flags_and_counts_beside_them_stay_integers():
    assert not is_metric("RefBootFullNaturalMarginCrossesZero",
                         "1 if the bootstrap interval of that margin includes zero")
    assert not is_metric("RefBootResamples", "bootstrap resamples")
    assert not is_metric("RefBootBlockLength", "moving-block length in records")
    assert not is_metric("RefBootAuxBelowChanceEntireInterval",
                         "1 if the whole interval lies below 0.5")
