#!/usr/bin/env python
"""Fail when a staged package is older than what it is supposed to contain.

Packages are built from the tree and then sit in `packages/` until someone
uploads them. Nothing connected the two, so a package could silently fall
behind: the Zenodo code zip was found three days and one correction round
stale, still carrying values a binding rule had removed and a sentence a
corrected incident had withdrawn, and the DTRAP artifact was rebuilt 37
seconds before the last source edit and so shipped a weaker gate than the
repository's (CI-31).

The rule is simple enough to enforce mechanically: a package artifact must be
at least as new as every source file it is built from. This does not verify
CONTENT -- a package can be newer and still wrong -- but the failure it catches
is the one that actually happened, twice, and it costs nothing to run.

A PUBLISHED deposit is the exception. Its files are frozen on the record and
must not be rebuilt, so every later source edit makes it look "stale" by the
rule above, and the check would demand a rebuild that would itself be the
error. A published file is therefore checked by content instead: it passes
while its local copy still has the size and checksum the published record
reports, and fails the moment it does not. The published checksums are pinned
in `packages/zenodo_published.json`, written only after each local copy was
verified against the record. A file that is not pinned (a new version being
staged) falls back to the mtime rule.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# The Zenodo code zip's sources used to be listed here by hand, and the list
# had drifted: fourteen of the twenty-two root files the builder ships were
# invisible to this check, README.md and CITATION.cff among them. Those two are
# exactly what a DOI propagation edits, so a propagation that touched nothing
# else would have left the zip stale and this check would still have printed
# PASSED -- the CI-31 failure again, on the one artifact that cannot be
# withdrawn after upload. Import the list from the builder instead, so the two
# cannot disagree.
from build_zenodo_package import CODE_DIRS, CODE_FILES  # noqa: E402

_ZENODO_CODE_SOURCES = list(CODE_DIRS) + list(CODE_FILES)

# Checksums of published, frozen deposit files, keyed by repository path.
PUBLISHED_PINS = ROOT / "packages/zenodo_published.json"

# (package artifact, [source roots it is built from])
PACKAGES = [
    (ROOT / "packages/zenodo/rcbsid_rebuild_code.zip", _ZENODO_CODE_SOURCES),
    (ROOT / "packages/dtrap/artifact_anonymous.zip",
     ["src", "scripts", "tests", "paper/main.tex", "paper/numbers.tex",
      "SCOPE_DECISIONS.md", "CLAIM_LEDGER.md", "results/manifests",
      "findings_contrast.md", "findings_review_analyses.md", "findings_referee_analyses.md",
      "findings_bootstrap_robustness.md", "findings_ecod_composition.md"]),
    (ROOT / "packages/dtrap/source_anonymous.tar.gz",
     ["paper/main.tex", "paper/numbers.tex", "paper/references.bib",
      "paper/figures"]),
    (ROOT / "packages/dtrap/manuscript_anonymous.pdf",
     ["paper/main.tex", "paper/numbers.tex", "paper/references.bib",
      "paper/figures"]),
    (ROOT / "packages/arxiv_v3/arxiv_v3_source.tar.gz",
     ["paper/main.tex", "paper/numbers.tex", "paper/references.bib",
      "paper/figures"]),
    # Built PDFs. paper/main.pdf is the source of every shipped copy, so a
    # stale one silently makes all of them stale; packages/arxiv_v3/src/main.pdf
    # is what the arXiv page count is read from; and the reviewer-kit copy was
    # found four pages and a whole correction round behind (CI-31), pointed at
    # by a step no longer in the operator's sequence.
    (ROOT / "paper/main.pdf",
     ["paper/main.tex", "paper/numbers.tex", "paper/references.bib",
      "paper/figures"]),
    (ROOT / "packages/arxiv_v3/src/main.pdf",
     ["paper/main.tex", "paper/numbers.tex", "paper/references.bib",
      "paper/figures"]),
    (ROOT / "REVIEWER_KIT/manuscript_review.pdf",
     ["paper/main.tex", "paper/numbers.tex", "paper/references.bib",
      "paper/figures"]),
]

SKIP_SUFFIX = {".pyc", ".aux", ".log", ".out", ".bbl", ".blg", ".pdf",
               ".sha256"}
SLACK_S = 2.0     # filesystem timestamp granularity, not a grace period


def newest(paths: list[str], root: Path = ROOT) -> tuple[float, Path | None]:
    best, who = 0.0, None
    for rel in paths:
        p = root / rel
        if not p.exists():
            continue
        it = [p] if p.is_file() else [q for q in p.rglob("*") if q.is_file()]
        for q in it:
            if q.suffix in SKIP_SUFFIX or "__pycache__" in q.parts:
                continue
            m = q.stat().st_mtime
            if m > best:
                best, who = m, q
    return best, who


def load_pins(pins_path: Path, root: Path = ROOT) -> dict[Path, dict]:
    """Published files and the size and MD5 the published record reports."""
    if not pins_path.exists():
        return {}
    data = json.loads(pins_path.read_text(encoding="utf-8"))
    return {(root / rel).resolve(): spec for rel, spec in data.get("files", {}).items()}


def published_mismatch(path: Path, spec: dict) -> str | None:
    """None while the local copy still has the published bytes; else why not."""
    if not path.exists():
        return "absent"
    data = path.read_bytes()
    if len(data) != int(spec["size"]):
        return "size %d, published %d" % (len(data), int(spec["size"]))
    if hashlib.md5(data).hexdigest() != spec["md5"]:
        return "checksum differs from the published record"
    return None


def main(root: Path = ROOT, packages: list | None = None,
         pins_path: Path | None = None) -> int:
    packages = PACKAGES if packages is None else packages
    pins = load_pins(PUBLISHED_PINS if pins_path is None else pins_path, root)
    rel = lambda p: p.resolve().relative_to(root.resolve()).as_posix()

    stale, checked, absent = [], 0, []
    for pkg, sources in packages:
        if pkg.resolve() in pins:
            continue                      # published and frozen: checked by content below
        if not pkg.exists():
            absent.append(pkg)
            continue
        checked += 1
        src_m, who = newest(sources, root)
        if src_m - pkg.stat().st_mtime > SLACK_S:
            stale.append((pkg, who, src_m - pkg.stat().st_mtime))

    frozen_ok, frozen_bad = [], []
    for path, spec in sorted(pins.items()):
        why = published_mismatch(path, spec)
        (frozen_bad if why else frozen_ok).append((path, why))

    print("package freshness: %d staged artifact(s) checked by age, "
          "%d published file(s) checked by content" % (checked, len(pins)))
    for p in absent:
        print("  ABSENT    %s" % rel(p))
    for pkg, who, delta in stale:
        print("  STALE     %s" % rel(pkg))
        print("            %.0fs older than %s" % (delta, rel(who) if who else "?"))
    for path, _ in frozen_ok:
        print("  FROZEN    %s  matches its published bytes" % rel(path))
    for path, why in frozen_bad:
        print("  CHANGED   %s  %s" % (rel(path), why))
    if not checked:
        print("FAILED - no staged package found; the check must never pass "
              "vacuously.")
        return 1
    if frozen_bad:
        print("")
        print("FAILED - a published deposit file no longer matches the record. "
              "Its files are frozen: restore the published bytes rather than "
              "rebuild it. To stage a new version on purpose, first remove the "
              "file's entry from the pin file, so it is checked by age again.")
    if stale:
        print("")
        print("FAILED - a staged package predates its sources. Rebuild it "
              "before any upload; an uploaded Zenodo deposit is immutable.")
    if stale or frozen_bad:
        return 1
    print("PASSED - every staged package is at least as new as its sources, "
          "and every published file still matches its published bytes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
