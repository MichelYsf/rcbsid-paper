#!/usr/bin/env python
"""Fail when a shipped source tarball carries identity in its member headers.

Why this exists. The double-anonymous source tarball was assembled with a plain
`tar -czf`, which preserves POSIX owner metadata. Every one of its eleven
members stored `uname='CYBERWIZARD'`, the author's machine username, and
`tar tvf` prints that on every line -- a referee sees it before extracting
anything. The username is one of the exact tokens
`build_anonymous_artifact.py` treats as identifying and scrubs out of the
artifact zip, so the project already classified the string as a de-anonymiser;
it was simply never checked in the tarballs, which have no builder script and
had no anonymity scan of any kind.

The two public tarballs carry the same metadata. There it is not an anonymity
breach, because arXiv postings are named, but it is still a disclosure of the
author's machine account on a permanent public upload, so they are checked too.

This is NOT one of the nine build-gate checks and deliberately does not change
that count, which is quoted verbatim in the deposit description and in three
venue texts. Run it before an upload; `check_package_freshness.py` covers
staleness, this covers content.

Rebuild a clean tarball with:

    tar --owner=0 --group=0 --numeric-owner -czf <out> <members...>
"""
from __future__ import annotations

import re
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_anonymous_artifact import IDENTIFYING  # noqa: E402

# (tarball, is it double-anonymous?)
TARBALLS = [
    (ROOT / "packages/dtrap/source_anonymous.tar.gz", True),
    (ROOT / "packages/arxiv_v3/arxiv_v3_source.tar.gz", False),
    (ROOT / "packages/sibling/arxiv_2510_09619_v2_source.tar.gz", False),
]

# Owner metadata identifies the build machine's account whether or not the
# posting is anonymous, so it is checked in every tarball.
MACHINE = [b"CYBERWIZARD", b"camich289"]

DOI_RE = re.compile(rb"10\.5281/zenodo\.\d+")
URL_RE = re.compile(rb"https?://(?:www\.)?zenodo\.org/\S*")


def check(path: Path, anonymous: bool) -> list[str]:
    if not path.exists():
        return ["missing: %s" % path.relative_to(ROOT).as_posix()]
    bad: list[str] = []
    rel = path.relative_to(ROOT).as_posix()
    with tarfile.open(path) as tf:
        members = tf.getmembers()
        for m in members:
            # 1. owner metadata, which `tar tvf` prints without extracting
            for field, value in (("uname", m.uname), ("gname", m.gname)):
                if value:
                    bad.append("%s: member %s carries %s=%r"
                               % (rel, m.name, field, value))
            for field, value in (("uid", m.uid), ("gid", m.gid)):
                if value:
                    bad.append("%s: member %s carries %s=%s"
                               % (rel, m.name, field, value))
            # 2. the member path itself
            name = m.name.encode("utf-8", "replace")
            for tok in MACHINE:
                if tok in name:
                    bad.append("%s: member name %s carries %s"
                               % (rel, m.name, tok.decode()))
            # 3. contents
            if not m.isfile():
                continue
            f = tf.extractfile(m)
            data = f.read() if f else b""
            tokens = list(IDENTIFYING) if anonymous else list(MACHINE)
            for tok in tokens:
                if tok in data:
                    bad.append("%s: %s contains the identifying token %s"
                               % (rel, m.name, tok.decode()))
            if anonymous:
                for hit in DOI_RE.findall(data):
                    bad.append("%s: %s contains a Zenodo DOI %s"
                               % (rel, m.name, hit.decode()))
                for hit in URL_RE.findall(data):
                    bad.append("%s: %s contains a Zenodo URL %s"
                               % (rel, m.name, hit.decode()[:60]))
        print("  %-52s %2d member(s), %s"
              % (rel, len(members),
                 "double-anonymous" if anonymous else "public, machine-account only"))
    return bad


def main() -> int:
    print("tarball anonymity: %d tarball(s) checked" % len(TARBALLS))
    bad: list[str] = []
    for path, anonymous in TARBALLS:
        bad += check(path, anonymous)
    print()
    if bad:
        for b in bad:
            print("  LEAK  " + b)
        print()
        print("FAILED - a shipped tarball carries identity. Rebuild it with "
              "`tar --owner=0 --group=0 --numeric-owner`; an arXiv version and "
              "a submitted artifact are both permanent.")
        return 1
    print("PASSED - no owner metadata and no identifying token in any shipped "
          "tarball.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
