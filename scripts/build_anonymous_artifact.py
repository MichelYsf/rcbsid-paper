#!/usr/bin/env python
"""Build the DTRAP anonymized artifact zip, and PROVE it is anonymous.

Double-anonymous review requires the supplementary artifact to carry no
author-identifying strings. Assembling it by hand and eyeballing is how a
name ships; this script assembles the zip from an allowlist, scrubs the two
files that legitimately carry identity (CITATION.cff is excluded outright;
README.md has its repository URL redacted), replaces the machine username in
archived manifest paths, and then FAILS if any identifying token survives
anywhere in the zip.
"""
from __future__ import annotations

import io
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "packages/dtrap/artifact_anonymous.zip"

IDENTIFYING = [b"Youssef", b"youssef", b"MichelYsf", b"Michel", b"michel",
               b"hotmail", b"0664-8228", b"0664-8224", b"CYBERWIZARD",
               b"camich289"]

INCLUDE_DIRS = ["src", "scripts", "tests"]
INCLUDE_FILES = [
    "requirements.txt", "README.md", "SCOPE_DECISIONS.md",
    "AUDIT_FINDINGS.md", "CLAIM_LEDGER.md", "SUPERSEDED.md",
    "REBUILD_DONE.md", "findings_contrast.md", "findings_prevalence.md",
    "findings_score_threshold.md", "findings_bocpd_ablation.md",
    "findings_contributions.md", "findings_streams.md",
    "findings_review_analyses.md",
    "paper/main.tex", "paper/numbers.tex", "paper/references.bib",
    "results/construction_contrast.csv", "results/prevalence_sweep_cicids.csv",
    "results/table_construction_contrast.tex",
    "results/table_prevalence_sweep.tex",
    "data/raw/natural/EXPECTED_SHA256.txt",
]
EXCLUDE_NAMES = {"CITATION.cff", "build_anonymous_artifact.py",
                 # cloud/ops infrastructure, not analysis: these carry machine
                 # paths and the named GitHub remote, and a reviewer needs none
                 # of them to reproduce the results locally
                 "autopilot_launch.cmd", "autopilot_runner.py",
                 "ec2_bootstrap.sh", "ec2_rebuild_bootstrap.sh",
                 "phase5_bring_home.sh", "local_puller.sh",
                 "pull_rebuild_results.py", "teardown_rebuild_instance.py",
                 "apply_power_settings.cmd", "rebuild_runner.py",
                 "build_arxiv_variant.py"}
EXCLUDE_SUFFIX = {".pyc", ".pdf", ".zip", ".tar.gz"}


def scrub(rel: str, data: bytes) -> bytes:
    text_like = rel.endswith((".py", ".md", ".txt", ".tex", ".bib", ".json",
                              ".csv", ".cfg", ".yaml", ".yml", ".sh"))
    if not text_like:
        return data
    # machine username inside archived absolute paths
    data = data.replace(b"CYBERWIZARD", b"ANON")
    data = data.replace(b"camich289", b"ANON")
    if rel == "README.md":
        data = re.sub(rb"https://github\.com/\S+", b"[public-repo-redacted-for-review]", data)
        data = data.replace(b"MichelYsf", b"[redacted]")
    if rel == "paper/main.tex":
        pass  # already the anonymous variant
    return data


def main() -> int:
    files: list[Path] = []
    for d in INCLUDE_DIRS:
        files += [p for p in (ROOT / d).rglob("*") if p.is_file()]
    files += [ROOT / f for f in INCLUDE_FILES if (ROOT / f).exists()]
    files += [p for p in (ROOT / "results/manifests").rglob("*.json")]
    # The retirement reasons live in a README beside the retired manifests, not
    # in a manifest, so a *.json glob silently drops them (B8/CI-31).
    _sup = ROOT / "results/manifests/superseded/README.md"
    if _sup.exists():
        files.append(_sup)

    # Every file the claim ledger cites must be IN the artifact: a referee who
    # extracts the zip and runs the ledger check is the first reader, and until
    # this was added that check failed on the artifact's own missing evidence.
    _ledger = ROOT / "CLAIM_LEDGER.md"
    if _ledger.exists():
        import re as _re
        _cited = set(_re.findall(r"file:([A-Za-z0-9_./-]+)",
                                 _ledger.read_text(encoding="utf-8")))
        _missing = []
        for _c in sorted(_cited):
            _p = ROOT / _c
            if not _p.exists():
                continue
            if _p not in files:
                files.append(_p)
                _missing.append(_c)
        if _missing:
            print("added %d ledger-cited file(s) the include list omitted: %s"
                  % (len(_missing), ", ".join(_missing)))

    leaks: list[str] = []
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(set(files)):
            rel = p.relative_to(ROOT).as_posix()
            if p.name in EXCLUDE_NAMES or p.suffix in EXCLUDE_SUFFIX:
                continue
            if "__pycache__" in rel or "/_dryrun/" in rel:
                continue
            data = scrub(rel, p.read_bytes())
            for tok in IDENTIFYING:
                if tok in data:
                    leaks.append(rel + " contains " + tok.decode(errors="replace"))
            z.writestr("artifact/" + rel, data)

    n = len(zipfile.ZipFile(OUT).namelist())
    print("wrote %s (%d files, %d bytes)" % (OUT.name, n, OUT.stat().st_size))
    if leaks:
        for l in sorted(set(leaks))[:20]:
            print("  IDENTITY LEAK  " + l)
        print("FAILED - the artifact is not anonymous. Not shippable.")
        OUT.unlink()
        return 1
    print("PASSED - no identifying token survives in the artifact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
