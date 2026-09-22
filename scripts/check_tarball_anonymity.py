#!/usr/bin/env python
"""Fail when a shipped source tarball carries identity in its member headers,
or when the named title page has leaked into an anonymized package.

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

The title page. DTRAP asked for a separate title page (the manuscript was
unsubmitted on 2026-09-22 for lack of one). `packages/dtrap/title_page.pdf`,
built from the `.tex` beside it, names the author on purpose: it is uploaded as
its own file for the editors only. It is therefore excluded from every
anonymity scan by design, and this script checks the converse instead: none of
the three anonymized packages contains it, by member name, by byte identity, or
by the two strings only it carries (the manuscript number and the author's
full name as printed there).

This is NOT one of the nine build-gate checks and deliberately does not change
that count, which is quoted verbatim in the deposit description and in three
venue texts. Run it before an upload; `check_package_freshness.py` covers
staleness, this covers content.

Rebuild a clean tarball with:

    tar --owner=0 --group=0 --numeric-owner -czf <out> <members...>
"""
from __future__ import annotations

import hashlib
import re
import sys
import tarfile
import zipfile
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

# The named title page and the three anonymized packages it must not enter.
TITLE_PAGE = [ROOT / "packages/dtrap/title_page.pdf",
              ROOT / "packages/dtrap/title_page.tex"]
ANONYMIZED = [ROOT / "packages/dtrap/manuscript_anonymous.pdf",
              ROOT / "packages/dtrap/artifact_anonymous.zip",
              ROOT / "packages/dtrap/source_anonymous.tar.gz"]
# Strings that appear on the title page and nowhere in an anonymous package.
TITLE_PAGE_ONLY = [b"DTRAP-2026-0211", b"Michel A. Youssef"]


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


def _pdf_text(data: bytes) -> bytes | None:
    """Rendered text of a PDF, or None when no PDF reader is available (the
    byte scan then still runs, but compressed text streams are opaque to it)."""
    try:
        import pymupdf  # type: ignore
    except ImportError:
        return None
    doc = pymupdf.open(stream=data, filetype="pdf")
    return "\n".join(page.get_text() for page in doc).encode("utf-8")


def _members(path: Path):
    """(member name, bytes) for every file inside a package, or the package
    itself as its single member when it is not an archive."""
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as zf:
            for info in zf.infolist():
                if not info.is_dir():
                    yield info.filename, zf.read(info)
    elif path.name.endswith(".tar.gz"):
        with tarfile.open(path) as tf:
            for m in tf.getmembers():
                if m.isfile():
                    f = tf.extractfile(m)
                    yield m.name, (f.read() if f else b"")
    else:
        yield path.name, path.read_bytes()


def check_title_page() -> list[str]:
    """The named title page must not be inside any anonymized package."""
    bad: list[str] = []
    present = [p for p in TITLE_PAGE if p.exists()]
    if not present:
        print("  title page: not built; nothing to isolate")
        return bad
    digests = {hashlib.sha256(p.read_bytes()).hexdigest(): p.name for p in present}
    names = {p.stem for p in present}
    text_checked = True
    for pkg in ANONYMIZED:
        rel = pkg.relative_to(ROOT).as_posix()
        if not pkg.exists():
            bad.append("missing: %s" % rel)
            continue
        n = 0
        for name, data in _members(pkg):
            n += 1
            stem = Path(name).stem
            if stem in names or "title_page" in name:
                bad.append("%s: carries a member named %s" % (rel, name))
            d = hashlib.sha256(data).hexdigest()
            if d in digests:
                bad.append("%s: member %s is byte-identical to %s" % (rel, name, digests[d]))
            haystacks = [data]
            if name.lower().endswith(".pdf"):
                text = _pdf_text(data)
                if text is None:
                    text_checked = False
                else:
                    haystacks.append(text)
            for tok in TITLE_PAGE_ONLY:
                if any(tok in h for h in haystacks):
                    bad.append("%s: %s contains the title-page string %s"
                               % (rel, name, tok.decode()))
        print("  %-52s %2d member(s) checked against the title page" % (rel, n))
    if not text_checked:
        bad.append("PDF text could not be inspected (pymupdf is not installed); "
                   "install it so the title-page strings are checked in rendered text")
    return bad


def main() -> int:
    print("tarball anonymity: %d tarball(s) checked" % len(TARBALLS))
    bad: list[str] = []
    for path, anonymous in TARBALLS:
        bad += check(path, anonymous)
    print("title page isolation: %d anonymized package(s) checked" % len(ANONYMIZED))
    bad += check_title_page()
    print()
    if bad:
        for b in bad:
            print("  LEAK  " + b)
        print()
        print("FAILED - a shipped package carries identity. Rebuild a tarball with "
              "`tar --owner=0 --group=0 --numeric-owner`; keep the title page out of "
              "every anonymized package; an arXiv version and a submitted artifact "
              "are both permanent.")
        return 1
    print("PASSED - no owner metadata and no identifying token in any shipped "
          "tarball, and the title page is in no anonymized package.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
