#!/usr/bin/env python
"""Provenance spine — THE governing rule of the honest rebuild.

No number, table, or figure may enter the manuscript unless it was produced by
a script in this repo that wrote, in the same execution, a run manifest
containing: git commit hash, config hash, input dataset SHA-256, seed,
environment lockfile hash, timestamp, and output path.

This module is the only sanctioned way to produce a number-bearing artifact.
Every experiment script calls `manifest(...)` (or the `provenance_run`
context manager) and writes its outputs through the returned handle, so the
manifest and the outputs cannot drift apart.

Usage
-----
    from provenance import provenance_run

    with provenance_run("prevalence_sweep", config=cfg, seed=11,
                        inputs=["data/raw/cicids2017/cicids2017_labeled.csv"],
                        outputs=["results/prevalence_sweep_cicids.csv"]) as run:
        ...
        run.emit_macro("PrevSweepNaturalAUCPR", 0.544998)   # number -> manifest

Design notes
------------
* Dataset SHA-256 is expensive on multi-GB CSVs, so it is cached in a
  sidecar `<file>.sha256` keyed by (size, mtime_ns). The cache is a speed
  optimisation only: a changed file always re-hashes.
* Macro values are recorded WITH the manifest, so `check_provenance.py` can
  scan the manuscript for `\\newcommand{\\Macro}{value}` and confirm each is
  backed by a real execution.
* Nothing here raises on a logging failure; a manifest write failure IS fatal,
  because a run whose provenance cannot be recorded must not produce numbers.
"""
from __future__ import annotations

import contextlib
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "results" / "manifests"
MACRO_INDEX = ROOT / "results" / "manifests" / "macro_index.json"


# --------------------------------------------------------------------------
# primitive hashes
# --------------------------------------------------------------------------
def sha256_file(path: str | Path, chunk: int = 1 << 20) -> str:
    """SHA-256 of a file, with a (size, mtime_ns)-keyed sidecar cache."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"cannot hash missing input: {p}")
    st = p.stat()
    side = p.with_suffix(p.suffix + ".sha256")
    key = f"{st.st_size}:{st.st_mtime_ns}"
    if side.exists():
        try:
            cached = json.loads(side.read_text())
            if cached.get("key") == key:
                return cached["sha256"]
        except Exception:
            pass
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    digest = h.hexdigest()
    try:
        side.write_text(json.dumps({"key": key, "sha256": digest}))
    except Exception:
        pass  # cache is optional
    return digest


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_obj(obj: Any) -> str:
    """Stable hash of a config-like object (dicts sorted, floats repr'd)."""
    return sha256_bytes(json.dumps(obj, sort_keys=True, default=str).encode())


# --------------------------------------------------------------------------
# environment identity
# --------------------------------------------------------------------------
def git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT),
                             capture_output=True, text=True, timeout=60)
        commit = out.stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=str(ROOT),
                               capture_output=True, text=True, timeout=60).stdout.strip()
        return commit + ("-dirty" if dirty else "")
    except Exception:
        return "unknown"


def env_lock_hash() -> dict:
    """Hash the environment: requirements.txt plus the resolved interpreter."""
    req = ROOT / "requirements.txt"
    req_hash = sha256_file(req) if req.exists() else "absent"
    try:
        freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"],
                                capture_output=True, text=True, timeout=300).stdout
    except Exception:
        freeze = ""
    return {
        "requirements_sha256": req_hash,
        "pip_freeze_sha256": sha256_bytes(freeze.encode()) if freeze else "unavailable",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "executable": sys.executable,
    }


# --------------------------------------------------------------------------
# the manifest
# --------------------------------------------------------------------------
class ProvenanceRun:
    def __init__(self, name: str, config: Any = None, seed: Any = None,
                 inputs: Iterable[str | Path] = (), outputs: Iterable[str | Path] = (),
                 notes: str = ""):
        self.name = name
        self.started = datetime.datetime.now(datetime.timezone.utc)
        self.config = config
        self.seed = seed
        self.declared_inputs = [str(x) for x in inputs]
        self.declared_outputs = [str(x) for x in outputs]
        self.notes = notes
        self.macros: dict[str, Any] = {}
        self.extra: dict[str, Any] = {}
        # The commit whose code is ACTUALLY RUNNING. Captured at construction,
        # not at write: a long run outlives edits to its own repository. Three
        # S4 contrast arms were attributed to a commit made two hours after
        # they started, because git_commit() was only called when the manifest
        # was written. The code that ran is the code that must be recorded.
        self.git_commit_start = git_commit()
        self.run_id = (f"{name}_{self.started:%Y%m%dT%H%M%S}_"
                       f"{sha256_obj([name, config, seed, self.started.isoformat()])[:8]}")

    # numbers ---------------------------------------------------------------
    def emit_macro(self, macro: str, value: Any, unit: str = "", desc: str = "") -> Any:
        """Register a number that may appear in the manuscript as \\macro."""
        if not macro or not macro[0].isalpha():
            raise ValueError(f"macro name must start with a letter: {macro!r}")
        self.macros[macro] = {"value": value, "unit": unit, "desc": desc}
        return value

    def note(self, key: str, value: Any) -> None:
        self.extra[key] = value

    # writing ---------------------------------------------------------------
    def to_dict(self) -> dict:
        finished = datetime.datetime.now(datetime.timezone.utc)
        commit_at_write = git_commit()
        return {
            "run_id": self.run_id,
            "name": self.name,
            # git_commit is the commit the run STARTED on - the code that
            # produced these numbers. The write-time commit is kept alongside
            # so a repository edited mid-run is visible rather than silent.
            "git_commit": self.git_commit_start,
            "git_commit_at_write": commit_at_write,
            "repo_changed_during_run": bool(commit_at_write != self.git_commit_start),
            "config_sha256": sha256_obj(self.config) if self.config is not None else None,
            "config": self.config if isinstance(self.config, (dict, list, str, int, float)) else str(self.config),
            "seed": self.seed,
            "inputs": [{"path": p, "sha256": sha256_file(p)} for p in self.declared_inputs],
            "outputs": [{"path": p, "exists": Path(p).exists(),
                         "sha256": sha256_file(p) if Path(p).exists() else None}
                        for p in self.declared_outputs],
            "environment": env_lock_hash(),
            "started_utc": self.started.isoformat(),
            "finished_utc": finished.isoformat(),
            "wall_seconds": (finished - self.started).total_seconds(),
            "macros": self.macros,
            "notes": self.notes,
            "extra": self.extra,
        }

    def write(self) -> Path:
        MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
        d = self.to_dict()
        path = MANIFEST_DIR / f"{self.run_id}.json"
        path.write_text(json.dumps(d, indent=2, default=str), encoding="utf-8")
        _reindex_macros()
        return path


@contextlib.contextmanager
def provenance_run(name: str, **kw):
    run = ProvenanceRun(name, **kw)
    try:
        yield run
    finally:
        run.write()


def build_index() -> dict:
    """Compute the macro index from the manifests on disk, WITHOUT writing it.

    Split out from _reindex_macros so the gate can check the stored index
    against the manifests rather than trusting it. macro_index.json is a
    DERIVED artifact: on 2026-08-19 it was found in the working tree missing 43
    macros - every S4 number the manuscript cites - while all the manifests
    that produced them sat untouched beside it. Anything that runs the
    reindexer against a different manifest directory can silently rewrite it,
    and a gate that reads it without verifying it will happily report that a
    vanished number "traces to a manifest".
    """
    index: dict[str, list] = {}
    if MANIFEST_DIR.exists():
        for f in sorted(MANIFEST_DIR.glob("*.json")):
            if f.name == "macro_index.json":
                continue
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            for macro, rec in (d.get("macros") or {}).items():
                index.setdefault(macro, []).append({
                    "value": rec.get("value"), "unit": rec.get("unit"),
                    "desc": rec.get("desc"), "run_id": d.get("run_id"),
                    "manifest": f.name, "git_commit": d.get("git_commit"),
                    "finished_utc": d.get("finished_utc"),
                })
    return index


def _reindex_macros() -> None:
    """Rebuild results/manifests/macro_index.json from all manifests."""
    index = build_index()
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    MACRO_INDEX.write_text(json.dumps(index, indent=2, default=str), encoding="utf-8")


def load_macro_index() -> dict:
    if not MACRO_INDEX.exists():
        return {}
    try:
        return json.loads(MACRO_INDEX.read_text(encoding="utf-8"))
    except Exception:
        return {}


if __name__ == "__main__":
    _reindex_macros()
    idx = load_macro_index()
    print(f"macro index: {len(idx)} macro(s) across "
          f"{len(list(MANIFEST_DIR.glob('*.json'))) - 1} manifest(s)")
    for m, recs in sorted(idx.items()):
        print(f"  \\{m} = {recs[-1]['value']}  ({recs[-1]['run_id']})")
