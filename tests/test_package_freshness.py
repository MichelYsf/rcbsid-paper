"""The package-freshness check: staged packages by age, published ones by content.

A published deposit is frozen, so its files grow older than every later source
edit. The check must pass such a file while it still has its published bytes,
fail it the moment it does not, keep failing ordinary staged packages that
predate their sources, and never pass vacuously. Every case runs on a temporary
tree; nothing in the repository is read or written.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import check_package_freshness as cpf  # noqa: E402

PUBLISHED = b"the bytes the record published"


def _write(path: Path, data: bytes, mtime: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    os.utime(path, (mtime, mtime))


def _tree(tmp_path: Path, local: bytes = PUBLISHED, pinned: bool = True):
    """A source file edited after the deposit, a deposit file older than it, and
    one ordinary staged package rebuilt after the edit."""
    now = time.time()
    _write(tmp_path / "src" / "analysis.py", b"x = 1\n", now)
    deposit = tmp_path / "packages" / "frozen" / "code.zip"
    _write(deposit, local, now - 86400)
    staged = tmp_path / "packages" / "staged" / "artifact.zip"
    _write(staged, b"rebuilt after the edit", now + 60)
    pins = tmp_path / "pins.json"
    files = {"packages/frozen/code.zip": {"size": len(PUBLISHED),
                                          "md5": hashlib.md5(PUBLISHED).hexdigest()}}
    pins.write_text(json.dumps({"files": files if pinned else {}}), encoding="utf-8")
    return [(deposit, ["src"]), (staged, ["src"])], pins


def test_published_file_with_its_published_bytes_passes_although_older(tmp_path, capsys):
    packages, pins = _tree(tmp_path)
    assert cpf.main(root=tmp_path, packages=packages, pins_path=pins) == 0
    assert "FROZEN" in capsys.readouterr().out


def test_published_file_whose_bytes_changed_fails(tmp_path, capsys):
    packages, pins = _tree(tmp_path, local=b"a rebuilt zip, same age")
    assert cpf.main(root=tmp_path, packages=packages, pins_path=pins) == 1
    assert "CHANGED" in capsys.readouterr().out


def test_published_file_of_the_same_size_but_other_content_fails(tmp_path):
    packages, pins = _tree(tmp_path, local=bytes(reversed(PUBLISHED)))
    assert cpf.main(root=tmp_path, packages=packages, pins_path=pins) == 1


def test_missing_published_file_fails(tmp_path):
    packages, pins = _tree(tmp_path)
    packages[0][0].unlink()
    assert cpf.main(root=tmp_path, packages=packages, pins_path=pins) == 1


def test_unpinned_package_older_than_its_sources_is_still_stale(tmp_path, capsys):
    packages, pins = _tree(tmp_path, pinned=False)
    assert cpf.main(root=tmp_path, packages=packages, pins_path=pins) == 1
    assert "STALE" in capsys.readouterr().out


def test_unpinned_package_newer_than_its_sources_passes(tmp_path):
    packages, pins = _tree(tmp_path, pinned=False)
    os.utime(packages[0][0], (time.time() + 60, time.time() + 60))
    assert cpf.main(root=tmp_path, packages=packages, pins_path=pins) == 0


def test_matching_pins_do_not_excuse_every_staged_package_being_absent(tmp_path, capsys):
    packages, pins = _tree(tmp_path)
    packages[1][0].unlink()
    assert cpf.main(root=tmp_path, packages=packages, pins_path=pins) == 1
    assert "never pass vacuously" in capsys.readouterr().out


def test_no_package_and_no_pin_never_passes_vacuously(tmp_path):
    pins = tmp_path / "pins.json"
    pins.write_text(json.dumps({"files": {}}), encoding="utf-8")
    assert cpf.main(root=tmp_path, packages=[], pins_path=pins) == 1
