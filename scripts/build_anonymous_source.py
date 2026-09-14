#!/usr/bin/env python
"""Stage the anonymous manuscript source and write its tarball.

Why this is a script and not two shell lines. The tarball was assembled by hand
twice and shipped two defects a referee would have met before reading a word:
`tar -czf` wrote the author's machine username into every member header, and
the copied main.tex kept `\\input{../results/...}` paths that resolve in the
repository but not in a flat tarball, so the shipped source did not compile.
Both are fixed here, once, and `check_tarball_anonymity.py` checks the first.

Layout matches the arXiv variant: the two generated tables sit beside main.tex,
so the `\\input` paths are rewritten to the flat layout in the staged copy
only; `paper/main.tex` is not touched. The unmodified TMLR template files ship
inside the tarball so it compiles standalone.
"""
from __future__ import annotations

import io
import shutil
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "packages/dtrap/src"
OUT = ROOT / "packages/dtrap/source_anonymous.tar.gz"

FILES = [
    ("paper/main.tex", "main.tex"),
    ("paper/numbers.tex", "numbers.tex"),
    ("paper/references.bib", "references.bib"),
    ("paper/main.bbl", "main.bbl"),
    ("paper/tmlr.sty", "tmlr.sty"),
    ("paper/tmlr.bst", "tmlr.bst"),
    ("paper/fancyhdr.sty", "fancyhdr.sty"),
    ("results/table_construction_contrast.tex", "table_construction_contrast.tex"),
    ("results/table_prevalence_sweep.tex", "table_prevalence_sweep.tex"),
]
INPUT_REWRITES = [
    ("\\input{../results/table_construction_contrast}", "\\input{table_construction_contrast}"),
    ("\\input{../results/table_prevalence_sweep}", "\\input{table_prevalence_sweep}"),
]


def anonymous(info: tarfile.TarInfo) -> tarfile.TarInfo:
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    return info


def main() -> int:
    SRC.mkdir(parents=True, exist_ok=True)
    (SRC / "figures").mkdir(exist_ok=True)
    for src, dst in FILES:
        shutil.copy(ROOT / src, SRC / dst)
    for f in sorted((ROOT / "paper/figures").glob("*.pdf")):
        shutil.copy(f, SRC / "figures" / f.name)

    p = SRC / "main.tex"
    t = p.read_text(encoding="utf-8")
    for old, new in INPUT_REWRITES:
        if t.count(old) != 1:
            print("ANCHOR: expected exactly one %r in main.tex, found %d" % (old, t.count(old)))
            return 1
        t = t.replace(old, new)
    p.write_text(t, encoding="utf-8", newline="\n")

    members = [dst for _, dst in FILES] + ["figures"]
    with tarfile.open(OUT, "w:gz") as tf:
        for m in members:
            tf.add(SRC / m, arcname=m, filter=anonymous)
    with tarfile.open(OUT) as tf:
        n = len(tf.getmembers())
        leak = [m.name for m in tf.getmembers() if m.uname or m.gname or m.uid or m.gid]
    print("wrote %s: %d member(s), %d B%s"
          % (OUT.relative_to(ROOT).as_posix(), n, OUT.stat().st_size,
             "" if not leak else "; OWNER METADATA LEAKED on %s" % leak))
    return 1 if leak else 0


if __name__ == "__main__":
    raise SystemExit(main())
