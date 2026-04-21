import numpy as np
import pytest
from src.baselines.score_utils import scalar_score


def test_scalar_score_accepts_scalar_zero_dim_and_single_item_array():
    assert scalar_score(0.25) == 0.25
    assert scalar_score(np.array(0.5)) == 0.5
    assert scalar_score(np.array([0.75])) == 0.75


def test_scalar_score_rejects_multi_value_array():
    with pytest.raises(ValueError):
        scalar_score(np.array([0.1, 0.2]))
