import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_baseline_tuning import (  # noqa: E402
    GRIDS,
    grid_points,
    select_best,
    to_wrapper_params,
)


def test_grid_sizes_match_runbook():
    assert len(grid_points("hst")) == 27
    assert len(grid_points("loda")) == 9
    assert len(grid_points("rrcf")) == 4
    assert len(grid_points("iforest_asd")) == 9
    assert len(grid_points("kitnet")) == 3
    assert len(grid_points("lof")) == 4


def test_grid_values_are_exactly_the_runbook_grids():
    assert GRIDS["hst"] == {"num_trees": [25, 50, 100], "max_depth": [10, 15, 20],
                            "window_size": [100, 250, 500]}
    assert GRIDS["loda"] == {"n_bins": [10, 20, 50], "n_random_cuts": [100, 200, 500]}
    assert GRIDS["rrcf"] == {"num_trees": [40, 100], "tree_size": [256, 512]}
    assert GRIDS["iforest_asd"] == {"n_estimators": [50, 100, 200],
                                    "window_size": [1024, 2048, 4096]}
    assert GRIDS["kitnet"] == {"max_size_ae": [5, 10, 20]}
    assert GRIDS["lof"] == {"n_neighbors": [10, 20, 35, 50]}


def test_param_mapping_to_wrapper_kwargs():
    assert to_wrapper_params("hst", {"num_trees": 50, "max_depth": 10, "window_size": 100}) == \
        {"n_trees": 50, "height": 10, "window_size": 100}
    assert to_wrapper_params("loda", {"n_bins": 20, "n_random_cuts": 500}) == \
        {"n_bins": 20, "n_projections": 500}
    assert to_wrapper_params("rrcf", {"num_trees": 100, "tree_size": 512}) == \
        {"n_trees": 100, "tree_size": 512}
    assert to_wrapper_params("lof", {"n_neighbors": 10}) == {"n_neighbors": 10}


def test_kitnet_grace_scales_with_stream_length():
    small = to_wrapper_params("kitnet", {"max_size_ae": 10}, stream_len=150_000)
    large = to_wrapper_params("kitnet", {"max_size_ae": 10}, stream_len=1_500_000)
    assert small["max_ae"] == large["max_ae"] == 10
    assert small["fm_grace"] < large["fm_grace"]
    assert small["ad_grace"] < large["ad_grace"]


def test_select_best_picks_validation_argmax_and_drops_crashed(tmp_path):
    rows = [
        {"dataset": "d", "method": "hst", "phase": "grid",
         "params": json.dumps({"num_trees": 25}), "val_auc_pr": 0.30, "error": ""},
        {"dataset": "d", "method": "hst", "phase": "grid",
         "params": json.dumps({"num_trees": 50}), "val_auc_pr": 0.55, "error": ""},
        {"dataset": "d", "method": "hst", "phase": "grid",
         "params": json.dumps({"num_trees": 100}), "val_auc_pr": float("nan"),
         "error": "RuntimeError: boom"},
    ]
    for i, r in enumerate(rows):
        pd.DataFrame([r]).to_csv(tmp_path / f"grid_d_hst_{i:03d}.csv", index=False)
    best, df = select_best(tmp_path, "d", "hst")
    assert best == {"num_trees": 50}
    assert len(df) == 3


def test_select_best_all_failed_exits(tmp_path):
    r = {"dataset": "d", "method": "loda", "phase": "grid",
         "params": json.dumps({"n_bins": 10}), "val_auc_pr": float("nan"),
         "error": "RuntimeError: boom"}
    pd.DataFrame([r]).to_csv(tmp_path / "grid_d_loda_000.csv", index=False)
    with pytest.raises(SystemExit):
        select_best(tmp_path, "d", "loda")
