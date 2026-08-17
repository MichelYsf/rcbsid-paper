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
