"""Tests for the provenance spine — the governing rule's enforcement.

The rule: no number enters the manuscript without a run manifest carrying git
commit, config hash, input SHA-256, seed, environment hash, timestamp, and
output path. These tests hold that rule mechanically.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import provenance as prov  # noqa: E402
import check_provenance as gate  # noqa: E402


def test_manifest_carries_every_required_field(tmp_path, monkeypatch):
    monkeypatch.setattr(prov, "MANIFEST_DIR", tmp_path)
    monkeypatch.setattr(prov, "MACRO_INDEX", tmp_path / "macro_index.json")
    src = tmp_path / "input.csv"
    src.write_text("a,b\n1,2\n")
    out = tmp_path / "out.csv"
    out.write_text("x\n")
    with prov.provenance_run("t", config={"k": 1}, seed=11,
                             inputs=[src], outputs=[out]) as r:
        r.emit_macro("TestValue", 1.25, unit="AUC-PR", desc="unit test")
    written = list(tmp_path.glob("t_*.json"))
    assert len(written) == 1
    d = json.loads(written[0].read_text())
    for field in ("git_commit", "config_sha256", "seed", "inputs", "outputs",
                  "environment", "started_utc", "finished_utc", "macros"):
        assert field in d, f"manifest missing required field {field}"
    assert d["inputs"][0]["sha256"] and len(d["inputs"][0]["sha256"]) == 64
    assert d["outputs"][0]["path"].endswith("out.csv")
    assert d["environment"]["requirements_sha256"]
    assert d["macros"]["TestValue"]["value"] == 1.25


def test_missing_input_is_fatal(tmp_path, monkeypatch):
    monkeypatch.setattr(prov, "MANIFEST_DIR", tmp_path)
    monkeypatch.setattr(prov, "MACRO_INDEX", tmp_path / "macro_index.json")
    with pytest.raises(FileNotFoundError):
        with prov.provenance_run("t", inputs=[tmp_path / "nope.csv"]) as r:
            r.emit_macro("X", 1)


def test_sha256_changes_when_file_changes(tmp_path):
    f = tmp_path / "d.csv"
    f.write_text("one")
    h1 = prov.sha256_file(f)
    f.write_text("two")
    h2 = prov.sha256_file(f)
    assert h1 != h2, "sidecar cache must not mask a changed file"


def test_gate_detects_orphan_number():
    assert gate.is_numeric("0.545")
    assert gate.is_numeric("61.03")
    assert not gate.is_numeric("CALIBURN")
    macros = gate.parse_macros("\\newcommand{\\A}{0.5}\n\\newcommand{\\B}{text}")
    assert macros == {"A": "0.5", "B": "text"}


def test_gate_agreement_respects_stated_precision():
    assert gate.agrees("0.545", 0.544998)      # 3dp in manuscript
    assert gate.agrees("0.5450", 0.544998)     # 4dp rounds equal
    assert not gate.agrees("0.546", 0.544998)
    assert not gate.agrees("0.545", 0.6)


def test_gate_selftest_passes():
    """The gate's own acceptance test: fails on orphan, fails on drift,
    passes on a manifested number."""
    assert gate.selftest() == 0


def test_macro_index_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(prov, "MANIFEST_DIR", tmp_path)
    monkeypatch.setattr(prov, "MACRO_INDEX", tmp_path / "macro_index.json")
    with prov.provenance_run("r1", seed=1) as r:
        r.emit_macro("Alpha", 0.1)
    with prov.provenance_run("r2", seed=2) as r:
        r.emit_macro("Beta", 0.2)
    idx = json.loads((tmp_path / "macro_index.json").read_text())
    assert set(idx) == {"Alpha", "Beta"}
    assert idx["Alpha"][0]["value"] == 0.1


# --- Regression: the gate must never pass vacuously -------------------------
# Found in the Stage 0 self-audit (2026-08-17): check_provenance.py printed
# "GATE PASSED" for an absent manuscript, so a wrong or renamed path silently
# greened the build and the governing rule could be bypassed entirely.

def test_gate_fails_on_absent_target(tmp_path):
    import check_provenance as cp
    assert cp.check([tmp_path / "does_not_exist.tex"]) == 1


def test_gate_fails_on_zero_targets():
    import check_provenance as cp
    assert cp.check([]) == 1


def test_gate_still_fails_on_orphan(tmp_path):
    import check_provenance as cp
    f = tmp_path / "orphan.tex"
    f.write_text(chr(92) + "newcommand{" + chr(92) + "DefinitelyNotManifested}{0.4242}" + chr(10), encoding="utf-8")
    assert cp.check([f]) == 1


# --- Regression: a macro claimed by two runs with different values ----------
# The gate resolved a macro to index[name][-1], i.e. whichever manifest was
# written last. Parallel experiment arms legitimately re-emit shared macros, so
# a disagreement between two arms would have been resolved silently in favour
# of the arm that happened to finish second, while the manuscript number still
# "traced to a manifest". Ambiguous sourcing is now a failure in its own right.

def _tex(tmp_path, name, macro, value):
    f = tmp_path / name
    f.write_text(chr(92) + "newcommand{" + chr(92) + macro + "}{" + value + "}" + chr(10),
                 encoding="utf-8")
    return f


def test_gate_fails_when_two_runs_claim_one_macro_differently(tmp_path, monkeypatch):
    import check_provenance as cp
    index = {"Shared": [{"value": 84, "run_id": "arm_natural", "manifest": "a.json"},
                        {"value": 83, "run_id": "arm_synthetic", "manifest": "b.json"}]}
    monkeypatch.setattr(cp, "load_macro_index", lambda: index)
    # The manuscript agrees with one of them; that must not be enough.
    assert cp.check([_tex(tmp_path, "amb.tex", "Shared", "84")]) == 1


def test_gate_allows_two_runs_that_agree(tmp_path, monkeypatch):
    import check_provenance as cp
    index = {"Shared": [{"value": 84, "run_id": "arm_natural", "manifest": "a.json"},
                        {"value": 84, "run_id": "arm_synthetic", "manifest": "b.json"}]}
    monkeypatch.setattr(cp, "load_macro_index", lambda: index)
    assert cp.check([_tex(tmp_path, "ok.tex", "Shared", "84")]) == 0


def test_distinct_values_treats_equal_floats_as_one():
    import check_provenance as cp
    recs = [{"value": 0.5, "run_id": "a"}, {"value": 0.5000000000001, "run_id": "b"}]
    assert len(cp.distinct_values(recs)) == 1
