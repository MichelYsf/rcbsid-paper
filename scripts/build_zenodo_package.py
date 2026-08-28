#!/usr/bin/env python
"""Rebuild the Zenodo deposit from the current tree.

Why this script exists. The deposit used to be staged by hand, and by the time
the round-3 sweep looked at it the code zip was frozen at a point three days
and one whole correction round behind the sources: 510 macros against 564, a
corrected-incident log stopping at CI-21, and -- worst -- the four
full-precision derived values that binding rule 9 exists to remove, plus a
sentence CI-21 had withdrawn. The manifest bundle was 20 manifests short and
carried two retired manifests at top level as though they were live. Every
other package artifact had been rebuilt that round; the Zenodo one was the one
nobody could rebuild, because rebuilding it was a manual procedure.

It is also the deposit that goes out under an immutable DOI, and the first
thing HUMAN_ACTIONS publishes.

So: one command, deterministic, and a staleness check the gate can run.
"""
from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

OUT = ROOT / "packages" / "zenodo"
BUNDLE = OUT / "manifests_bundle"
CODE_ZIP = OUT / "rcbsid_rebuild_code.zip"
BUNDLE_ZIP = OUT / "manifests_bundle.zip"

CODE_DIRS = ["src", "scripts", "tests", "paper"]
CODE_FILES = [
    "requirements.txt", "README.md", "CITATION.cff", "SCOPE_DECISIONS.md",
    "AUDIT_FINDINGS.md", "CLAIM_LEDGER.md", "SUPERSEDED.md",
    "REBUILD_DONE.md", "TRIAGE_REPORT.md",
    "findings_contrast.md", "findings_prevalence.md",
    "findings_score_threshold.md", "findings_bocpd_ablation.md",
    "findings_contributions.md", "findings_streams.md",
    "findings_review_analyses.md",
]
SKIP_SUFFIX = {".pdf", ".aux", ".log", ".out", ".bbl", ".blg", ".synctex.gz",
               ".pyc", ".sha256"}
SKIP_NAMES = {"__pycache__"}

COPY_FILES = [
    ("results/construction_contrast.csv", "construction_contrast.csv"),
    ("results/prevalence_sweep_cicids.csv", "prevalence_sweep_cicids.csv"),
    ("data/raw/natural/EXPECTED_SHA256.txt", "EXPECTED_SHA256.txt"),
]


def wanted(p: Path) -> bool:
    if any(part in SKIP_NAMES for part in p.parts):
        return False
    return p.suffix not in SKIP_SUFFIX


def build_code_zip() -> int:
    files: list[Path] = []
    for d in CODE_DIRS:
        files += [p for p in (ROOT / d).rglob("*") if p.is_file() and wanted(p)]
    files += [ROOT / f for f in CODE_FILES if (ROOT / f).exists()]
    files = sorted(set(files))
    with zipfile.ZipFile(CODE_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, p.relative_to(ROOT).as_posix())
    return len(files)


def build_bundle() -> tuple[int, int]:
    if BUNDLE.exists():
        shutil.rmtree(BUNDLE)
    (BUNDLE / "superseded").mkdir(parents=True)
    live = sorted((ROOT / "results/manifests").glob("*.json"))
    for p in live:
        shutil.copy2(p, BUNDLE / p.name)
    sup_dir = ROOT / "results/manifests/superseded"
    sup = sorted(sup_dir.glob("*.json"))
    for p in sup:
        shutil.copy2(p, BUNDLE / "superseded" / p.name)
    readme = sup_dir / "README.md"
    if readme.exists():
        # the ONLY record of why each manifest was retired; the deposit
        # description promises it explicitly
        shutil.copy2(readme, BUNDLE / "superseded" / "README.md")
    return len(live), len(sup)


def zip_bundle() -> tuple[int, int]:
    """Write the upload zip the deposit sheet names.

    Entries are relative to the bundle root with NO wrapping directory,
    because README.md tells a downloader to extract this zip *into*
    results/manifests/. Zipping the folder itself -- which is what a
    right-click "compress" does on Windows -- produces
    results/manifests/manifests_bundle/... and silently breaks the documented
    reproduction step. Doing it here removes that choice from the operator.
    """
    files = sorted(p for p in BUNDLE.rglob("*") if p.is_file())
    with zipfile.ZipFile(BUNDLE_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f.relative_to(BUNDLE).as_posix())
    return len(files), BUNDLE_ZIP.stat().st_size


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    n_code = build_code_zip()
    n_live, n_sup = build_bundle()
    n_zip, z_size = zip_bundle()
    for src, dst in COPY_FILES:
        s = ROOT / src
        if s.exists():
            shutil.copy2(s, OUT / dst)
    print("zenodo package rebuilt from the current tree")
    print("  rcbsid_rebuild_code.zip : %d files" % n_code)
    print("  manifests_bundle/       : %d live + %d superseded (+ README)"
          % (n_live, n_sup))
    print("  manifests_bundle.zip    : %d entries, %d B" % (n_zip, z_size))
    print("  copied                  : %d result/expectation file(s)"
          % len(COPY_FILES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
