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


def distinct_values(records: list[dict]) -> list:
    """Distinct values a macro was emitted with, across all manifests.

    More than one means the manuscript number is ambiguously sourced: two runs
    claim the same symbol with different values. Taking the most recent silently
    would let a number 'trace to a manifest' while a second manifest contradicts
    it, which is exactly what the governing rule forbids.
    """
    seen: list = []
    for rec in records:
        v = rec.get("value")
        try:
            key: object = round(float(v), 12)
        except (TypeError, ValueError):
            key = str(v)
        if key not in [k for k, _ in seen]:
            seen.append((key, rec))
    return seen


def check(targets: list[Path]) -> int:
    index = load_macro_index()
    orphans, mismatches, ok, missing, ambiguous = [], [], [], [], []
    scanned = 0
    for t in targets:
        if not t.exists():
            # A target that cannot be read is NOT a pass. Silently skipping an
            # absent manuscript let a wrong path green the gate (found in the
            # Stage 0 self-audit), which would defeat the governing rule.
            missing.append(str(t))
            continue
        scanned += 1
        macros = parse_macros(t.read_text(encoding="utf-8", errors="replace"))
        for name, raw in macros.items():
            if not is_numeric(raw):
                continue                      # prose macro, not a number
            if name not in index:
                orphans.append((t.name, name, raw))
                continue
            variants = distinct_values(index[name])
            if len(variants) > 1:
                ambiguous.append((t.name, name, raw, variants))
            elif not agrees(raw, index[name][-1]["value"]):
                mismatches.append((t.name, name, raw, index[name][-1]["value"],
                                   index[name][-1]["run_id"]))
            else:
                ok.append((name, raw, index[name][-1]["run_id"]))

    print(f"provenance gate: scanned {scanned} file(s); "
          f"{len(ok)} manifested, {len(orphans)} orphan(s), "
          f"{len(mismatches)} mismatch(es), {len(ambiguous)} ambiguous")
    for f, n, v in orphans:
        print(f"  ORPHAN    {f}: \\{n} = {v}  -- no manifest produced this number")
    for f, n, v, mv, rid in mismatches:
        print(f"  MISMATCH  {f}: \\{n} = {v}  but manifest {rid} recorded {mv}")
    for f, n, v, variants in ambiguous:
        print(f"  AMBIGUOUS {f}: \\{n} = {v}  -- {len(variants)} manifests emitted "
              f"this macro with DIFFERENT values:")
        for val, rec in variants:
            print(f"              {val}  from {rec.get('run_id')} "
                  f"({rec.get('manifest')})")
    for m in missing:
        print(f"  MISSING   {m}  -- target absent, nothing could be verified")
    if ambiguous:
        print("")
        print("GATE FAILED - a macro is claimed by two runs with different "
              "values; the manuscript number is not uniquely sourced.")
        return 1
    if missing:
        print("")
        print("GATE FAILED - a target could not be read; an unverifiable "
              "manuscript is never a pass.")
        return 1
    if scanned == 0:
        print("")
        print("GATE FAILED - zero files scanned; the gate must never pass vacuously.")
        return 1
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

    # Two runs claiming one symbol with different values. Parallel experiment
    # arms legitimately re-emit shared macros (feature dimensionality, say), so
    # the gate must distinguish "both agree" from "they disagree and the last
    # one silently won". The macro name is unique to this test; no manuscript
    # references it, so the manifests it leaves behind cannot affect real numbers.
    for v in (1.0, 2.0):
        with provenance_run("selftest_provenance_ambiguity",
                            config={"selftest": True, "v": v}, seed=0,
                            notes="gate must reject a doubly-claimed macro") as run:
            run.emit_macro("SelfTestAmbiguous", v, desc="two runs, two values")

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

        amb = Path(td) / "ambiguous.tex"
        amb.write_text("\\newcommand{\\SelfTestAmbiguous}{1.0}\n", encoding="utf-8")
        rc_amb = check([amb])
        if rc_amb == 0:
            failures.append("gate PASSED on a macro two runs claim with "
                            "different values (not uniquely sourced)")

    print("\n--- selftest ---")
    if failures:
        for f in failures:
            print(f"  FAIL: {f}")
        return 1
    print("  PASS: fails on orphan, drift, and ambiguous sourcing; "
          "passes on a uniquely manifested number")
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
