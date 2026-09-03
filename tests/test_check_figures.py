"""Tests for the figure gate (SCOPE_DECISIONS rule 12): a figure whose inputs
are newer than it fails, a figure referenced without a manifest fails, a
plotted value off the macro layer fails, and identifying PDF metadata fails."""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_figures as cf  # noqa: E402

TITLE = cf.PAPER_TITLE


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _pdf(title=TITLE, extra=b"") -> bytes:
    t = title.encode("latin-1")
    return (b"%PDF-1.4\n1 0 obj\n<< /Title (" + t + b") " + extra +
            b">>\nendobj\ntrailer\n<< /Info 1 0 R >>\n%%EOF\n")


def _fixture(tmp_path: Path, *, pdf_bytes=None, value=0.5, include="figures/fig_a"):
    (tmp_path / "paper" / "figures").mkdir(parents=True)
    (tmp_path / "results" / "manifests").mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    inp = tmp_path / "results" / "manifests" / "run.json"
    inp.write_text('{"macros": {"M": {"value": 0.5}}}', encoding="utf-8")
    gen = tmp_path / "scripts" / "make_figures.py"
    gen.write_text("# generator\n", encoding="utf-8")
    fig = tmp_path / "paper" / "figures" / "fig_a.pdf"
    fig.write_bytes(pdf_bytes if pdf_bytes is not None else _pdf())
    # figures must be at least as new as their inputs
    old = time.time() - 100
    os.utime(inp, (old, old))
    os.utime(gen, (old, old))
    man = tmp_path / "paper" / "figures" / "figure_manifest.json"
    man.write_text(json.dumps({
        "generator": "scripts/make_figures.py",
        "generator_sha256": _sha(gen),
        "inputs": {"results/manifests/run.json": _sha(inp)},
        "figures": {"paper/figures/fig_a.pdf": _sha(fig)},
        "values": {"M": value},
    }), encoding="utf-8")
    ms = tmp_path / "paper" / "main.tex"
    ms.write_text("\\begin{document}\\includegraphics[width=3in]{%s}\\end{document}\n"
                  % include, encoding="utf-8")
    idx = tmp_path / "results" / "manifests" / "macro_index.json"
    idx.write_text(json.dumps({"M": [{"value": 0.5}]}), encoding="utf-8")
    # the fixture carries one figure; the four-figure floor is tested separately
    return dict(root=tmp_path, manifest=man, manuscript=ms, macro_index=idx,
                min_figures=1)


def test_consistent_fixture_passes(tmp_path):
    assert cf.check(**_fixture(tmp_path)) == 0


def test_default_floor_is_four_figures(tmp_path):
    kw = _fixture(tmp_path)
    kw.pop("min_figures")          # default MIN_FIGURES applies
    assert cf.MIN_FIGURES == 4
    assert cf.check(**kw) == 1     # one figure is not the manuscript's manifest


def test_empty_manifest_sections_fail(tmp_path):
    for key in ("inputs", "values", "generator_sha256", "generator"):
        kw = _fixture(tmp_path / key)
        man = kw["manifest"]
        d = json.loads(man.read_text(encoding="utf-8"))
        d[key] = {} if isinstance(d[key], dict) else ""
        man.write_text(json.dumps(d), encoding="utf-8")
        assert cf.check(**kw) == 1, key


def test_input_newer_than_figure_fails(tmp_path):
    kw = _fixture(tmp_path)
    inp = tmp_path / "results" / "manifests" / "run.json"
    now = time.time() + 50
    os.utime(inp, (now, now))
    assert cf.check(**kw) == 1


def test_changed_input_fails(tmp_path):
    kw = _fixture(tmp_path)
    inp = tmp_path / "results" / "manifests" / "run.json"
    inp.write_text('{"macros": {"M": {"value": 0.6}}}', encoding="utf-8")
    old = time.time() - 100
    os.utime(inp, (old, old))
    assert cf.check(**kw) == 1


def test_unmanifested_figure_reference_fails(tmp_path):
    kw = _fixture(tmp_path, include="figures/fig_b")
    assert cf.check(**kw) == 1


def test_value_off_macro_layer_fails(tmp_path):
    kw = _fixture(tmp_path, value=0.51)
    assert cf.check(**kw) == 1


def test_author_metadata_fails(tmp_path):
    kw = _fixture(tmp_path, pdf_bytes=_pdf(extra=b"/Author (Someone) "))
    assert cf.check(**kw) == 1


def test_creation_date_fails(tmp_path):
    kw = _fixture(tmp_path, pdf_bytes=_pdf(extra=b"/CreationDate (D:20260901) "))
    assert cf.check(**kw) == 1


def test_identity_token_in_bytes_fails(tmp_path):
    kw = _fixture(tmp_path, pdf_bytes=_pdf() + b"C:\\Users\\CYBERWIZARD\\x")
    assert cf.check(**kw) == 1


def test_unlisted_typed_constant_fails(tmp_path):
    kw = _fixture(tmp_path)
    man = kw["manifest"]
    d = json.loads(man.read_text(encoding="utf-8"))
    d["constants"] = {"auc_roc_chance": 0.5, "some_threshold": 0.9}
    man.write_text(json.dumps(d), encoding="utf-8")
    assert cf.check(**kw) == 1
    d["constants"] = {"auc_roc_chance": 0.5, "note": "by definition"}
    man.write_text(json.dumps(d), encoding="utf-8")
    assert cf.check(**kw) == 0


def test_missing_manifest_fails(tmp_path):
    kw = _fixture(tmp_path)
    kw["manifest"].unlink()
    assert cf.check(**kw) == 1
