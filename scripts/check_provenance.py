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
from provenance import MANIFEST_DIR, build_index, load_macro_index, tex_macro_name  # noqa: E402
import check_control_chars  # noqa: E402
import check_overfull  # noqa: E402
import check_package_freshness  # noqa: E402
import check_publish_ready  # noqa: E402
import check_decimals  # noqa: E402
import check_figures  # noqa: E402
import check_literals  # noqa: E402

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


def index_drift(stored: dict, computed: dict) -> list[str]:
    """Ways the stored macro index disagrees with the manifests on disk.

    macro_index.json is DERIVED. On 2026-08-19 it was found in the working tree
    missing 43 macros - every S4 number the manuscript cites - while all the
    manifests that produced them sat untouched beside it. A gate that reads the
    index without checking it will report that a vanished number still traces
    to a manifest. So the index is now evidence to be verified, not consulted.
    """
    problems = []
    for name in sorted(set(computed) - set(stored)):
        problems.append("missing from index: " + name +
                        " (a manifest emits it, the index does not carry it)")
    for name in sorted(set(stored) - set(computed)):
        problems.append("stale in index: " + name +
                        " (no manifest on disk emits it)")
    for name in sorted(set(stored) & set(computed)):
        sv = [r.get("value") for r in stored[name]]
        cv = [r.get("value") for r in computed[name]]
        if [str(x) for x in sv] != [str(x) for x in cv]:
            problems.append("value drift in index: " + name +
                            " stored=" + str(sv) + " manifests=" + str(cv))
    return problems


def check(targets: list[Path], verify_index: bool = True) -> int:
    index = load_macro_index()
    if verify_index:
        try:
            drift = index_drift(index, build_index())
        except Exception as exc:                       # never mask a real check
            drift = ["could not rebuild the index from manifests: " + repr(exc)]
        if drift:
            print("provenance gate: macro index does NOT match the manifests on disk")
            for d in drift[:25]:
                print("  INDEX  " + d)
            if len(drift) > 25:
                print("  INDEX  ... and " + str(len(drift) - 25) + " more")
            print("")
            print("GATE FAILED - the macro index is a derived artifact and it has "
                  "drifted from its manifests; regenerate it with "
                  "`python scripts/provenance.py` and re-run.")
            return 1
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
        alias = {tex_macro_name(k): k for k in index}
        for name, raw in macros.items():
            name = alias.get(name, name)
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
    print("GATE PASSED — every macro resolved in the scanned target(s) traces to "
          "a run manifest. (This check reads generated files only; typed literals "
          "are the literal scan's job — see check_literals.py.)")
    return 0


LEDGER = ROOT / "CLAIM_LEDGER.md"


def check_ledger() -> int:
    """Every manifest:<run_id> and file:<path> in CLAIM_LEDGER.md must exist.

    The ledger maps each abstract/introduction sentence to its generating run.
    An entry pointing at a manifest that does not exist is an orphaned CLAIM -
    the sentence-level analogue of an orphaned number - and fails the build.
    An absent or empty ledger also fails: the manuscript's headline claims
    must be mapped, not merely mappable.
    """
    import re as _re
    if not LEDGER.exists():
        print("LEDGER FAILED - CLAIM_LEDGER.md is absent.")
        return 1
    text = LEDGER.read_text(encoding="utf-8", errors="replace")
    refs_m = _re.findall(r"manifest:([A-Za-z0-9_]+)", text)
    refs_f = _re.findall(r"file:([A-Za-z0-9_./-]+)", text)
    # [a-z]? because rows inserted between existing ones are lettered
    # (A5b, A7b); without it the count silently omitted them.
    rows = _re.findall(r"^\| [AI]\d+[a-z]? \|", text, flags=_re.M)
    problems = []
    for rid in sorted(set(refs_m)):
        if not (MANIFEST_DIR / (rid + ".json")).exists():
            problems.append("manifest missing: " + rid)
    for f in sorted(set(refs_f)):
        if not (ROOT / f).exists():
            problems.append("file missing: " + f)
    print("claim ledger: %d sentence rows, %d manifest refs (%d unique), "
          "%d file refs (%d unique)"
          % (len(rows), len(refs_m), len(set(refs_m)),
             len(refs_f), len(set(refs_f))))
    if not rows:
        print("LEDGER FAILED - no sentence rows found; the ledger must map "
              "the abstract and introduction, not merely exist.")
        return 1
    if problems:
        for pr in problems:
            print("  ORPHANED CLAIM  " + pr)
        print("LEDGER FAILED - a claim references a source that does not exist.")
        return 1
    print("LEDGER PASSED - every claim reference resolves.")
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
    # The fixture has to enter the store for the gate to resolve it below, but
    # it must not STAY there. Forty of these accumulated -- 61% of the live
    # provenance store, all recording a dirty commit, and one of them leaking
    # a fake number into the generated macro file the manuscript reads from.
    # A self-test that pollutes the thing it tests is not a self-test (CI-34).
    _fixture = MANIFEST_DIR / (run.run_id + ".json")

    # Ambiguous sourcing (CI-5) is covered hermetically in
    # tests/test_provenance.py with an injected index. It is deliberately NOT
    # exercised here: doing so would write two mutually contradictory manifests
    # into the real provenance store on every selftest run, which is precisely
    # the contamination the check exists to detect.

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
    # remove the fixture and reindex, so the store is exactly as it was
    try:
        _fixture.unlink(missing_ok=True)
        (MANIFEST_DIR / (run.run_id + ".json.sha256")).unlink(missing_ok=True)
        from provenance import _reindex_macros
        _reindex_macros()
    except Exception as exc:
        print("  WARNING: could not remove the selftest fixture: " + repr(exc))

    print("  PASS: fails on orphan and drift, passes on a manifested number "
          "(ambiguous sourcing covered in tests/test_provenance.py)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="*", type=Path, default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--ledger", action="store_true",
                    help="check CLAIM_LEDGER.md only")
    ap.add_argument("--no-ledger", action="store_true",
                    help="skip the ledger check (pre-ledger workflows)")
    ap.add_argument("--no-literals", action="store_true",
                    help="skip the typed-literal scan (diagnostic use only)")
    ap.add_argument("--literals", action="store_true",
                    help="run the typed-literal scan only")
    ap.add_argument("--no-decimals", action="store_true",
                    help="skip the decimal-consistency check")
    ap.add_argument("--decimals", action="store_true",
                    help="run the decimal-consistency check only")
    ap.add_argument("--no-controlchars", action="store_true",
                    help="skip the heredoc-damage scan")
    ap.add_argument("--controlchars", action="store_true",
                    help="run the heredoc-damage scan only")
    ap.add_argument("--no-overfull", action="store_true",
                    help="skip the overfull-hbox check")
    ap.add_argument("--overfull", action="store_true",
                    help="run the overfull-hbox check only")
    ap.add_argument("--no-packages", action="store_true",
                    help="skip the staged-package freshness check")
    ap.add_argument("--packages", action="store_true",
                    help="run the staged-package freshness check only")
    ap.add_argument("--no-figures", action="store_true",
                    help="skip the figure check")
    ap.add_argument("--figures", action="store_true",
                    help="run the figure check only")
    ap.add_argument("--publish-ready", action="store_true",
                    dest="publish_ready",
                    help="pre-upload invariants: clean tree, pushed HEAD, "
                         "no manifest citing a dirty commit. NOT part of "
                         "the default gate.")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.ledger:
        return check_ledger()
    if a.literals:
        return check_literals.main()
    if a.decimals:
        return check_decimals.main()
    if a.controlchars:
        return check_control_chars.main()
    if a.overfull:
        return check_overfull.main()
    if a.packages:
        return check_package_freshness.main()
    if a.figures:
        return check_figures.main()
    if a.publish_ready:
        return check_publish_ready.main()
    targets = a.targets or DEFAULT_TARGETS
    rc = check(list(targets))
    if not a.no_ledger and LEDGER.exists():
        rc = max(rc, check_ledger())
    # The orphan check above reads paper/numbers.tex, which is GENERATED and so
    # cannot contain an orphan. Every defect of the "number typed straight into
    # the manuscript" class (CI-11, CI-19, and the round-2 AUC-ROC table) lived
    # in a hand-written file this gate never opened. The literal scan closes
    # that hole over the manuscript and every file the claim ledger cites.
    if not a.no_literals:
        print("")
        rc = max(rc, check_literals.main())
    # The orphan and literal checks both ask "does this number come from
    # somewhere". Neither asks whether the numbers agree with each other
    # once printed, which is how a margin came to disagree with the two
    # values printed beside it in the same sentence.
    if not a.no_decimals:
        print("")
        rc = max(rc, check_decimals.main())
    # Every check above reads NUMBERS. None of them reads markup, which is
    # how a \\ref whose backslash had been eaten by a shell heredoc reached
    # a shipped PDF once already (CI-19) and reached a staged package again
    # (CI-29). The compiler cannot see it either: a \\ref without its
    # backslash is not a reference, so it is not an undefined one.
    if not a.no_controlchars:
        print("")
        rc = max(rc, check_control_chars.main())
    # Everything above reads SOURCES. None of it reads the typeset result,
    # which is how half of five protocol-table rows shipped off the page in
    # three PDFs behind a compile that exited 0 with no undefined
    # references (CI-30).
    if not a.no_overfull:
        print("")
        rc = max(rc, check_overfull.main())
    # Everything above checks the SOURCES and the typeset result. None of
    # it looks at what is actually staged for upload, which is how a Zenodo
    # deposit sat a whole correction round behind the tree it claims to
    # archive, under a DOI that cannot be taken back (CI-31).
    if not a.no_packages:
        print("")
        rc = max(rc, check_package_freshness.main())
    # Every check above reads numbers, markup, the typeset text and the
    # staged packages. None of it reads a FIGURE, and a figure is a
    # rendering of numbers that can go stale, be typed, or carry the
    # author's name in PDF metadata without any of the checks above
    # noticing (SCOPE_DECISIONS rule 12).
    if not a.no_figures:
        print("")
        rc = max(rc, check_figures.main())
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
