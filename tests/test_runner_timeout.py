"""The 12 h ceiling and durable timeout evidence.

Regression for the defect found 2026-08-19: the per-job ceiling was 6 h while
the CICIDS contrast arms project to 6-8 CPU-hours, so those arms would have
been killed and written NOTHING - indistinguishable from never having run.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import rebuild_runner as rr  # noqa: E402


def test_ceiling_exceeds_projected_cicids_cost():
    assert rr.JOB_TIMEOUT_S >= 12 * 3600, "ceiling must clear the 6-8 h CICIDS arms"


def test_timeout_writes_durable_partial_with_reason(tmp_path):
    out = tmp_path / "contrast_cicids_natural.csv"
    assert rr.write_timeout_partial(out, "cicids_natural", 43200, "arm: natural")
    assert out.exists() and out.stat().st_size > 0

    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert len(rows) == 1
    r = rows[0]
    assert r["stream"] == "cicids_natural"
    assert "TIMEOUT" in r["excluded_reason"]
    assert "43200" in r["excluded_reason"] or r["timeout_seconds"] == "43200"
    assert r["recorded_utc"]


def test_timeout_partial_is_not_mistaken_for_results(tmp_path):
    """A timeout partial must carry no metric columns to be misread as data."""
    out = tmp_path / "t.csv"
    rr.write_timeout_partial(out, "x", 60)
    cols = set(next(csv.reader(out.open(encoding="utf-8"))))
    assert "auc_pr" not in cols and "test_prevalence" not in cols
    assert "excluded_reason" in cols
