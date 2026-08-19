"""The 12 h ceiling and durable, TRUTHFUL failure evidence.

Two regressions, both found on real runs:

1. 2026-08-19 (design): the per-job ceiling was 6 h while the CICIDS contrast
   arms project to 6-8 CPU-hours, so those arms would have been killed having
   written NOTHING - indistinguishable from never having run.

2. 2026-08-19 (live): the CICIDS natural arm was OOM-killed at 8,680 s and the
   runner recorded it as "TIMEOUT: job exceeded the 8680s per-job ceiling".
   The ceiling is 43,200 s and the cause was memory, not time. The exclusion
   record was a confident wrong answer, which is worse than a missing file.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import rebuild_runner as rr  # noqa: E402


def test_ceiling_exceeds_projected_cicids_cost():
    assert rr.JOB_TIMEOUT_S >= 12 * 3600, "ceiling must clear the 6-8 h CICIDS arms"


def test_failure_writes_durable_partial_with_reason(tmp_path):
    out = tmp_path / "contrast_cicids_natural.csv"
    assert rr.write_failure_partial(out, "cicids_natural", 43200,
                                    "exceeded the per-job wall ceiling",
                                    "arm: natural")
    assert out.exists() and out.stat().st_size > 0

    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert len(rows) == 1
    r = rows[0]
    assert r["stream"] == "cicids_natural"
    assert "ceiling" in r["excluded_reason"]
    assert r["elapsed_seconds"] == "43200"
    assert r["recorded_utc"]


def test_failure_partial_is_not_mistaken_for_results(tmp_path):
    """A failure partial must carry no metric columns to be misread as data."""
    out = tmp_path / "t.csv"
    rr.write_failure_partial(out, "x", 60, "exited non-zero with status 1")
    cols = set(next(csv.reader(out.open(encoding="utf-8"))))
    assert "auc_pr" not in cols and "test_prevalence" not in cols
    assert "excluded_reason" in cols


# --- Regression 2: the record must name the real cause ----------------------

def test_sigkill_is_reported_as_memory_not_timeout():
    d = rr.describe_exit(-9)
    assert "signal 9" in d and "OOM" in d
    assert "ceiling" not in d.lower() and "timeout" not in d.lower()


def test_ordinary_nonzero_exit_is_not_called_a_timeout():
    d = rr.describe_exit(1)
    assert "non-zero" in d and "status 1" in d
    assert "timeout" not in d.lower()


def test_oom_partial_does_not_claim_the_ceiling_was_hit(tmp_path):
    """The live defect, end to end: an OOM kill at 8,680 s must not be recorded
    as having exceeded a ceiling - and must not imply the ceiling is 8,680 s."""
    out = tmp_path / "oom.csv"
    rr.write_failure_partial(out, "cicids_natural", 8680, rr.describe_exit(-9))
    r = list(csv.DictReader(out.open(encoding="utf-8")))[0]
    reason = r["excluded_reason"]
    assert "OOM" in reason
    assert "ceiling" not in reason.lower()
    # the true ceiling is recorded separately and is NOT the elapsed time
    assert r["elapsed_seconds"] == "8680"
    assert r["job_ceiling_seconds"] == str(rr.JOB_TIMEOUT_S) != "8680"
