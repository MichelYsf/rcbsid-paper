#!/usr/bin/env python
"""Verify the invariants that must hold before anything LEAVES this machine.

Deliberately NOT part of the default gate. The build gate answers "is this tree
internally consistent"; this answers "is this tree publishable", and those are
different questions with different answers. Running it in the default gate
would make every working state red and train the operator to ignore it.

It exists because `PUBLISH_INSTRUCTIONS.md` invariant 5 -- "git status clean,
branch pushed" -- was written as a thing a human would check, and was false
while every other invariant was green and the round was declared closed
(CI-32). An assertion nobody executes is the failure mode this whole project
documents.

What it enforces, and why each matters for an IMMUTABLE deposit:

  * clean working tree -- a deposit must correspond to a state that exists
  * HEAD published on the remote -- `zenodo_metadata.md` names the GitHub repo
    and branch as an "is derived from" identifier, so a downloader must be able
    to resolve it
  * no manifest recording a "-dirty" commit -- a "-dirty" sha is not
    recoverable from the public repository, so a number that cites one cannot
    be traced by anyone but the author
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "results" / "manifests"


def git(*args: str) -> tuple[int, str]:
    p = subprocess.run(["git", "-C", str(ROOT), *args],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return p.returncode, (p.stdout or "").strip()


def main() -> int:
    rc = 0
    print("publish-ready check (NOT part of the build gate)")

    code, porcelain = git("status", "--porcelain")
    if code != 0:
        print("FAILED - not a git repository, or git unavailable.")
        return 1
    paths = [l for l in porcelain.splitlines() if l.strip()]
    if paths:
        kinds: dict[str, int] = {}
        for l in paths:
            kinds[l[:2].strip() or "??"] = kinds.get(l[:2].strip() or "??", 0) + 1
        print("  DIRTY TREE      %d uncommitted path(s): %s"
              % (len(paths), ", ".join("%s=%d" % kv for kv in sorted(kinds.items()))))
        rc = 1
    else:
        print("  clean tree")

    _, head = git("rev-parse", "HEAD")
    _, branch = git("rev-parse", "--abbrev-ref", "HEAD")
    code_up, upstream = git("rev-parse", "@{upstream}")
    if code_up != 0:
        print("  NO UPSTREAM     branch %s has no tracking remote" % branch)
        rc = 1
    elif upstream != head:
        _, ahead = git("rev-list", "--count", "@{upstream}..HEAD")
        print("  UNPUSHED        %s is %s commit(s) ahead of its remote" % (branch, ahead))
        rc = 1
    else:
        print("  HEAD published  %s == remote" % head[:12])

    dirty = []
    if MANIFESTS.exists():
        for m in sorted(MANIFESTS.glob("*.json")):
            try:
                t = m.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if '"git_commit"' in t and "-dirty" in t:
                dirty.append(m.name)
    total = len(list(MANIFESTS.glob("*.json"))) if MANIFESTS.exists() else 0
    if dirty:
        print("  DIRTY PROVENANCE %d of %d live manifest(s) record a '-dirty' commit"
              % (len(dirty), total))
        print("                   e.g. %s" % ", ".join(dirty[:3]))
        rc = 1
    elif total:
        print("  provenance      all %d live manifests cite a clean commit" % total)

    print("")
    if rc:
        print("NOT PUBLISH-READY. Commit and push this branch, then re-run the "
              "generating scripts whose manifests record a dirty commit, or "
              "state plainly in the deposit metadata that the archived state is "
              "not resolvable from the public repository. An uploaded Zenodo "
              "deposit cannot be withdrawn.")
    else:
        print("PUBLISH-READY - tree clean, HEAD published, provenance traceable.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
