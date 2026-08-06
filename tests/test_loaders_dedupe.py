import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.loaders import list_data_files, load_dataset_folder  # noqa: E402


def test_case_insensitive_filesystem_does_not_double_files(tmp_path):
    pd.DataFrame({"a": [1, 2], "label": [0, 1]}).to_csv(tmp_path / "data.csv", index=False)
    files = list_data_files(tmp_path)
    assert len(files) == 1


def test_load_dataset_folder_row_count_is_not_doubled(tmp_path):
    pd.DataFrame({"a": [1, 2, 3], "label": [0, 1, 0]}).to_csv(tmp_path / "d.csv", index=False)
    df = load_dataset_folder(tmp_path, "label")
    assert len(df) == 3


def test_distinct_files_are_still_all_loaded(tmp_path):
    pd.DataFrame({"a": [1], "label": [0]}).to_csv(tmp_path / "one.csv", index=False)
    pd.DataFrame({"a": [2], "label": [1]}).to_csv(tmp_path / "two.csv", index=False)
    df = load_dataset_folder(tmp_path, "label")
    assert len(df) == 2
