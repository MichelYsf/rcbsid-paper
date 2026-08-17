#!/usr/bin/env python
"""Provenance gate — FAILS the build on any orphan number in the manuscript.

Scans a manuscript for number-bearing macros and confirms each is backed by a
run manifest produced by scripts/provenance.py. A number without a manifest is
an orphan; the rule is that it is deleted, never drafted, so this gate exits
non-zero and names it.

What counts as a number-bearing macro
-------------------------------------
The manuscript declares its numbers as LaTeX macros:

    \\newcommand{\\PrevSweepNaturalAUCPR}{0.545}

Only macros whose expansion parses as a number are checked (so \\newcommand
for text is ignored). Every such macro must exist in the macro index with a
value that agrees to the manuscript's stated precision.

Usage
-----
    python scripts/check_provenance.py                     # default manuscript
    python scripts/check_provenance.py paper/numbers.tex   # explicit target
    python scripts/check_provenance.py --selftest          # gate's own tests

Exit codes: 0 green, 1 orphan/mismatch found, 2 usage error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from provenance import load_macro_index  # noqa: E402

DEFAULT_TARGETS = [ROOT / "paper" / "numbers.tex"]
NEWCOMMAND = re.compile(r"\\newcommand\{\\([A-Za-z][A-Za-z0-9]*)\}\{([^}]*)\}")
NUMERIC = re.compile(r"^\s*[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?\s*(\\%|%)?\s*$")


def parse_macros(text: str) -> dict[str, str]:
    return {m.group(1): m.group(2).strip() for m in NEWCOMMAND.finditer(text)}


def is_numeric(raw: str) -> bool:
    return bool(NUMERIC.match(raw))


def as_float(raw: str) -> float:
    return float(raw.strip().replace("\\%", "").replace("%", ""))


def agrees(manuscript_raw: str, manifest_value) -> bool:
    """Agreement at the manuscript's own stated precision."""
    try:
        mv = float(manifest_value)
    except (TypeError, ValueError):
        return str(manifest_value).strip() == manuscript_raw.strip()
    got = as_float(manuscript_raw)
    frac = manuscript_raw.split(".")
    dp = len(frac[1].replace("\\%", "").replace("%", "").strip()) if len(frac) > 1 else 0
    return round(mv, dp) == round(got, dp)


def check(targets: list[Path]) -> int:
    index = load_macro_index()
    orphans, mismatches, ok = [], [], []
    scanned = 0
    for t in targets:
        if not t.exists():
            print(f"[skip] {t} (absent)")
            continue
        scanned += 1
        macros = parse_macros(t.read_text(encoding="utf-8", errors="replace"))
        for name, raw in macros.items():
            if not is_numeric(raw):
                continue                      # prose macro, not a number
            if name not in index:
                orphans.append((t.name, name, raw))
            elif not agrees(raw, index[name][-1]["value"]):
                mismatches.append((t.name, name, raw, index[name][-1]["value"],
                                   index[name][-1]["run_id"]))
            else:
                ok.append((name, raw, index[name][-1]["run_id"]))

    print(f"provenance gate: scanned {scanned} file(s); "
          f"{len(ok)} manifested, {len(orphans)} orphan(s), {len(mismatches)} mismatch(es)")
    for f, n, v in orphans:
        print(f"  ORPHAN    {f}: \\{n} = {v}  -- no manifest produced this number")
    for f, n, v, mv, rid in mismatches:
        print(f"  MISMATCH  {f}: \\{n} = {v}  but manifest {rid} recorded {mv}")
    if orphans or mismatches:
        print("\nGATE FAILED — a number without a manifest is deleted, never drafted.")
        return 1
    print("GATE PASSED — every number in the manuscript traces to a run manifest.")
    return 0


def selftest() -> int:
    """The gate must fail on a deliberately orphaned number and pass on a
    manifested one (Stage 0 acceptance criterion)."""
    import tempfile
    from provenance import provenance_run

    failures = []
    with provenance_run("selftest_provenance_gate", config={"selftest": True}, seed=0,
                        notes="Stage 0 gate acceptance test") as run:
        run.emit_macro("SelfTestManifested", 0.4242, desc="gate acceptance")

    with tempfile.TemporaryDirectory() as td:
        good = Path(td) / "good.tex"
        good.write_text("\\newcommand{\\SelfTestManifested}{0.4242}\n"
                        "\\newcommand{\\SomeProse}{CALIBURN}\n", encoding="utf-8")
        rc_good = check([good])
        if rc_good != 0:
            failures.append("gate FAILED on a manifested number (should pass)")

        bad = Path(td) / "bad.tex"
        bad.write_text("\\newcommand{\\SelfTestManifested}{0.4242}\n"
                       "\\newcommand{\\TotallyMadeUpNumber}{0.999}\n", encoding="utf-8")
        rc_bad = check([bad])
        if rc_bad == 0:
            failures.append("gate PASSED with an orphan number (should fail)")

        drift = Path(td) / "drift.tex"
        drift.write_text("\\newcommand{\\SelfTestManifested}{0.5555}\n", encoding="utf-8")
        rc_drift = check([drift])
        if rc_drift == 0:
            failures.append("gate PASSED on a value that contradicts its manifest")

    print("\n--- selftest ---")
    if failures:
        for f in failures:
            print(f"  FAIL: {f}")
        return 1
    print("  PASS: fails on orphan, fails on drift, passes on manifested")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="*", type=Path, default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    targets = a.targets or DEFAULT_TARGETS
    return check(list(targets))


if __name__ == "__main__":
    raise SystemExit(main())
