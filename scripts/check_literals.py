#!/usr/bin/env python
"""Catch measurement-shaped numbers that never went through the macro layer.

Why this exists
---------------
`check_provenance.py` scans exactly one file: `paper/numbers.tex`. That file is
GENERATED from the manifests, so it cannot contain an orphan, and the gate has
therefore been printing "every number in the manuscript traces to a run
manifest" while checking nothing the author actually typed. Three defects of
this class shipped past a green gate this month:

  CI-11  the pooled attack count 14,621 sat in a manuscript-bound LaTeX table
         and in no manifest anywhere;
  CI-19  the same class again, caught only by an independent auditor;
  round-2 four shared-record AUC-ROC values typed straight into Table 4.

The pattern is stable: the gate certifies the generated file, the defect lives
in the hand-written one. So this module scans the hand-written artifacts — the
manuscript, every .tex it pulls in, and every file the claim ledger cites — for
numbers that LOOK like measurements and do not correspond to any value in the
macro index.

What counts as measurement-shaped
---------------------------------
Deliberately narrow, because a noisy gate gets switched off:

  * a decimal with >= 3 fractional digits (0.728355, 42.9954), or
  * an integer >= 1000, optionally comma-grouped (78,000; 1600000).

Excluded, with reasons, because these are identifiers and not measurements:
years 1900-2100; anything inside a fenced code block; anything inside a URL,
DOI or arXiv identifier; LaTeX lengths and column specs; and the digits inside
a macro name (\\StreamCicidsTwoZeroOneSeven... carries none, but \\SFourL... may).

A literal passes if the macro index holds a value that renders to it at the
literal's own printed precision — the same agreement rule the orphan gate uses.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from provenance import load_macro_index  # noqa: E402

LEDGER = ROOT / "CLAIM_LEDGER.md"
MANUSCRIPT = ROOT / "paper" / "main.tex"

DECIMAL = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?(?![\w])")
CODE_FENCE = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`\n]*`")
URLISH = re.compile(r"(https?://\S+|10\.\d{4,}/\S+|arXiv:\S+|doi:\S+)", re.I)
TEX_COMMENT = re.compile(r"(?<!\\)%.*")
TEX_MACRO = re.compile(r"\\[A-Za-z]+")
TEX_LENGTH = re.compile(r"\d*\.?\d+\s*(pt|pc|in|cm|mm|em|ex|bp|dd|sp|\\linewidth|\\textwidth)")


def _strip(text: str, is_tex: bool) -> str:
    text = CODE_FENCE.sub(" ", text)
    text = INLINE_CODE.sub(" ", text)
    text = URLISH.sub(" ", text)
    if is_tex:
        text = TEX_COMMENT.sub(" ", text)
        text = TEX_LENGTH.sub(" ", text)
        text = TEX_MACRO.sub(" ", text)   # macro names carry transliterated digits
    return text


def measurement_shaped(whole: str, frac: str | None) -> bool:
    if frac is not None and len(frac) >= 3:
        return True
    digits = whole.replace(",", "")
    if frac is None and digits.isdigit() and int(digits) >= 1000:
        if 1900 <= int(digits) <= 2100:      # a year, not a measurement
            return False
        return True
    return False


def index_values(idx: dict) -> set[str]:
    """Every manifested value, as strings at several plausible precisions."""
    out: set[str] = set()
    for recs in idx.values():
        for rec in recs:
            v = rec.get("value")
            try:
                f = float(v)
            except (TypeError, ValueError):
                continue
            out.add(str(v))
            # The scanner reads digits, not signs: a manuscript writes
            # "0.333 below chance" for a macro whose value is -0.3333, and the
            # directional word carries the sign. Register both polarities so a
            # signed macro does not read as an orphan.
            for g in (f, abs(f)):
                if g == int(g):
                    out.add(str(int(g)))
                    out.add("{:,}".format(int(g)))
                for dp in range(0, 9):
                    out.add(("%." + str(dp) + "f") % g)
                out.add("{:,}".format(round(g, 3)))
    return out


def ledger_cited_files() -> list[Path]:
    if not LEDGER.exists():
        return []
    refs = re.findall(r"file:([A-Za-z0-9_./-]+)", LEDGER.read_text(encoding="utf-8"))
    seen, out = set(), []
    for r in sorted(set(refs)):
        p = ROOT / r
        if p.exists() and p.is_file() and r not in seen:
            seen.add(r)
            out.append(p)
    return out


def tex_inputs(main: Path) -> list[Path]:
    if not main.exists():
        return []
    out = []
    for rel in re.findall(r"\\input\{([^}]+)\}", main.read_text(encoding="utf-8")):
        for cand in (main.parent / (rel + ".tex"), main.parent / rel,
                     ROOT / (rel + ".tex"), ROOT / rel):
            if cand.exists() and cand.name != "numbers.tex":
                out.append(cand.resolve())
                break
    return out


# Files whose PURPOSE is to record numbers, including numbers that were wrong.
# SCOPE_DECISIONS and AUDIT_FINDINGS quote superseded values, dmesg readings,
# process IDs and margins that were withdrawn; forcing those through the macro
# layer would mean manifesting an error as though it were a measurement. The
# self-test fixtures are fake numbers by design (\TotallyMadeUpNumber). These
# are scanned and REPORTED, never failed on.
RECORD_ONLY = {
    "SCOPE_DECISIONS.md",       # corrected-incident log: quotes withdrawn values
    "AUDIT_FINDINGS.md",        # audit log: quotes pre-rebuild values
    "SUPERSEDED.md",            # by definition a record of superseded numbers
    "scripts/check_provenance.py",   # gate self-test fixtures
    "tests/test_provenance.py",      # gate unit-test fixtures
}

# Genuine non-measurements inside enforced files. Each needs a reason, so that
# an exclusion is a recorded decision and not a silent hole in the gate.
ALLOW = {
    "10002978.10003022": "ACM CCS concept identifier, not a measurement",
    "10010147.10010257": "ACM CCS concept identifier, not a measurement",
    "4320": "SRE burn-rate window length in minutes (60/360/4320), a cited "
            "practice parameter, not a value we measured",
}


def enforced(rel: str) -> bool:
    return rel not in RECORD_ONLY


def targets() -> list[Path]:
    out = [MANUSCRIPT] + tex_inputs(MANUSCRIPT) + ledger_cited_files()
    seen, uniq = set(), []
    for p in out:
        if p.exists() and str(p) not in seen:
            seen.add(str(p))
            uniq.append(p)
    return uniq


def scan(paths: list[Path], known: set[str]) -> list[tuple[str, int, str]]:
    findings = []
    for p in paths:
        is_tex = p.suffix == ".tex"
        try:
            raw = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for lineno, line in enumerate(raw.splitlines(), 1):
            for m in DECIMAL.finditer(_strip(line, is_tex)):
                whole, frac = m.group(1), m.group(2)
                if not measurement_shaped(whole, frac):
                    continue
                lit = whole + ("." + frac if frac else "")
                if lit in known or lit.replace(",", "") in known:
                    continue
                if lit in ALLOW:
                    continue
                findings.append((str(p.relative_to(ROOT)).replace("\\", "/"),
                                 lineno, lit))
    return findings


def main() -> int:
    idx = load_macro_index()
    known = index_values(idx)
    paths = targets()
    findings = scan(paths, known)

    hard = [f for f in findings if enforced(f[0])]
    soft = [f for f in findings if not enforced(f[0])]

    print("literal scan: %d file(s) — manuscript, its \\input'ed tex, and every "
          "file the claim ledger cites" % len(paths))
    for p in paths:
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        print("    %-34s %s" % (rel, "[record-only]" if not enforced(rel) else ""))
    if soft:
        print("")
        print("%d literal(s) in record-only files (reported, not failed — these "
              "files exist to record numbers, including withdrawn ones):" % len(soft))
        by_file: dict[str, int] = {}
        for f, _ln, _lit in soft:
            by_file[f] = by_file.get(f, 0) + 1
        for f in sorted(by_file):
            print("    %-34s %d" % (f, by_file[f]))
    if not hard:
        print("")
        print("PASSED — no measurement-shaped literal outside the macro layer "
              "in any enforced file.")
        return 0
    print("")
    print("%d measurement-shaped literal(s) with no manifested value:" % len(hard))
    for f, ln, lit in hard[:60]:
        print("  UNMANIFESTED  %s:%d  %s" % (f, ln, lit))
    if len(hard) > 60:
        print("  ... and %d more" % (len(hard) - 60))
    print("")
    print("FAILED — a number a reader can see must trace to a manifest.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
