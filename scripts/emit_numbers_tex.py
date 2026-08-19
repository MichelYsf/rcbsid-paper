#!/usr/bin/env python
"""Render paper/numbers.tex from the macro index.

This is the transcription layer between manifested runs and the manuscript.
It creates no numbers: every value it writes was emitted by a run that wrote a
manifest, and the run id for each is recorded inline as a comment.

What this does and does not prove
---------------------------------
Because numbers.tex is GENERATED from the index, running the provenance gate
against a freshly generated file cannot fail on orphans - there are none by
construction. That first pass is therefore not evidence that the numbers are
right; it only confirms the transcription is faithful. The gate earns its keep
afterwards, when a human edits the manuscript: a hand-typed value, a stale
number left behind after a rerun, or a macro two runs disagree about will all
fail. Presenting the generated-then-checked pass as strong verification would
overstate it, so this docstring says so and so does the file header.

A macro that two manifests claim with different values is refused outright
rather than resolved by recency (CI-5): the operator must delete the superseded
manifest deliberately.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_provenance import distinct_values  # noqa: E402
from provenance import load_macro_index  # noqa: E402

OUT = ROOT / "paper" / "numbers.tex"


def render(value) -> str | None:
    """LaTeX body for a macro, or None if it is not a number."""
    if isinstance(value, bool):
        return str(int(value))
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))
        return repr(value)
    try:
        f = float(str(value))
    except (TypeError, ValueError):
        return None
    return repr(f)


def main() -> int:
    index = load_macro_index()
    if not index:
        print("no macro index; nothing to render")
        return 1

    ambiguous, emitted, skipped = [], [], []
    for name in sorted(index):
        variants = distinct_values(index[name])
        if len(variants) > 1:
            ambiguous.append((name, variants))
            continue
        rec = index[name][-1]
        body = render(rec.get("value"))
        if body is None:
            skipped.append(name)
            continue
        emitted.append((name, body, rec))

    if ambiguous:
        print("REFUSING to render: " + str(len(ambiguous)) +
              " macro(s) are claimed by more than one run with different values.")
        for name, variants in ambiguous:
            print("  " + name)
            for val, rec in variants:
                print("      " + str(val) + "  from " + str(rec.get("run_id")))
        print("")
        print("Delete the superseded manifest deliberately; recency must never "
              "decide which number the manuscript carries.")
        return 1

    lines = [
        "% paper/numbers.tex - GENERATED, do not hand-edit.",
        "% Rendered by scripts/emit_numbers_tex.py from results/manifests/.",
        "% Every value below was emitted by a run that wrote a manifest; the run",
        "% id is given on each line.",
        "%",
        "% Note on what the provenance gate proves here: this file is generated",
        "% FROM the manifests, so a gate run immediately after generation cannot",
        "% find an orphan. That pass confirms faithful transcription, nothing",
        "% more. The gate becomes evidence once the manuscript is edited by hand,",
        "% when it catches typed values, stale numbers after a rerun, and macros",
        "% two runs disagree about.",
        "",
    ]
    for name, body, rec in emitted:
        desc = str(rec.get("desc") or "").replace("\n", " ").strip()
        unit = str(rec.get("unit") or "").strip()
        comment = "  % " + (desc if desc else name)
        if unit:
            comment += " [" + unit + "]"
        comment += " -- " + str(rec.get("run_id"))
        lines.append("\\newcommand{\\" + name + "}{" + body + "}" + comment)
    lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("wrote " + str(OUT) + ": " + str(len(emitted)) + " macro(s)")
    if skipped:
        print("skipped " + str(len(skipped)) + " non-numeric macro(s): " +
              ", ".join(skipped[:8]) + ("..." if len(skipped) > 8 else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
