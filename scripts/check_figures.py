#!/usr/bin/env python
"""Fail when a manuscript figure is stale, unmanifested, off-macro, or carries
identifying PDF metadata (SCOPE_DECISIONS rule 12).

What it checks, and why each check exists:
  * the figure manifest exists and every input it names is unchanged (SHA-256)
    and no newer than any figure: a manifest edited after the render means the
    figures show values the archive no longer carries;
  * the generator itself is unchanged (SHA-256) and no newer than the figures;
  * every figure the manifest names exists and hashes as recorded;
  * every \\includegraphics in the manuscript resolves to a manifested figure:
    a figure without a manifest is a number without a run;
  * every value the manifest says it plotted equals the macro index's value
    for that macro name, so the figures render the macro layer and nothing
    typed;
  * every figure PDF carries no Author, Creator, Producer, Subject, Keywords,
    CreationDate or ModDate, its Title is empty or the paper title, and no
    identifying token appears in its bytes.

It never passes vacuously: the manifest must name a generator with its hash,
at least one input, at least MIN_FIGURES figures, and at least one plotted
value, and every figure the manuscript references must be among them.

What it does NOT check, so that nobody reads it as more than it is: it does
not re-render, so determinism, fixed style, fixed random state and the
absence of timestamps in the generator rest on scripts/make_figures.py and
on the audit sweep, not on this script; it does not parse caption text or
tick locators; and its identity scan reads the PDF's uncompressed bytes,
which cover the Info dictionary but not Flate-compressed content streams.

Runs in the repository, or in an extracted artifact after
scripts/make_figures.py has been re-run there (the artifact's manifests are
anonymized copies whose bytes differ from the repository originals).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "paper" / "figures" / "figure_manifest.json"
MANUSCRIPT = ROOT / "paper" / "main.tex"
MACRO_INDEX = ROOT / "results" / "manifests" / "macro_index.json"
PAPER_TITLE = ("Stream Assembly Is an Uncontrolled Treatment in Streaming "
               "Intrusion-Detection Benchmarks")

INCLUDE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
PDF_META = re.compile(rb"/(Title|Author|Creator|Producer|Subject|Keywords|"
                      rb"CreationDate|ModDate)\s*(\(((?:[^()\\]|\\.)*)\)|<[0-9A-Fa-f]*>)")
# Tokens that must not appear in a figure file. This script ships inside the
# double-anonymous artifact, so it carries only path-shaped tokens that name
# nobody. Personal tokens (usernames, handles, names, mailboxes) are read from
# an untracked, gitignored local file, one token per line, that no package
# builder lists, so they are scanned for in the repository and never shipped.
IDENTITY = [b"/home/", b"C:\\Users", b"C:/Users", b"/Users/"]
_LOCAL_TOKENS = ROOT / ".identity_tokens.local"
if _LOCAL_TOKENS.exists():
    IDENTITY += [line.strip().encode("utf-8")
                 for line in _LOCAL_TOKENS.read_text(encoding="utf-8").splitlines()
                 if line.strip() and not line.startswith("#")]
SLACK_S = 2.0
# The manuscript carries four figures. A manifest naming fewer is not the
# manifest of this manuscript, however internally consistent it is.
MIN_FIGURES = 4
# The one definitional constant a figure may carry (rule 12): the AUC-ROC of
# an uninformative ranking. Everything else must come from a manifest.
ALLOWED_CONSTANTS = {"auc_roc_chance": 0.5}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_index_values(path: Path) -> dict:
    idx = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for name, records in idx.items():
        if isinstance(records, list) and records:
            out[name] = records[0].get("value")
        elif isinstance(records, dict):
            out[name] = records.get("value")
    return out


def pdf_metadata_problems(data: bytes, title: str) -> list[str]:
    problems = []
    for m in PDF_META.finditer(data):
        key = m.group(1).decode()
        raw = m.group(3) if m.group(3) is not None else b""
        val = raw.decode("latin-1")
        if key == "Title":
            if val not in ("", title):
                problems.append("Title is %r, expected empty or the paper title" % val[:60])
        elif val != "":
            problems.append("%s is set (%r)" % (key, val[:60]))
    for tok in IDENTITY:
        if tok in data:
            problems.append("identifying token %r in figure bytes" % tok.decode(errors="replace"))
    return problems


def check(root: Path = ROOT, manifest: Path = MANIFEST, manuscript: Path = MANUSCRIPT,
          macro_index: Path = MACRO_INDEX, title: str = PAPER_TITLE,
          min_figures: int = MIN_FIGURES) -> int:
    fails: list[str] = []
    notes: list[str] = []
    if not manifest.exists():
        print("figure check: %s is absent" % manifest.relative_to(root).as_posix())
        print("FAILED - figures without a figure manifest are numbers without a run.")
        return 1
    fm = json.loads(manifest.read_text(encoding="utf-8"))
    figures = fm.get("figures", {})
    inputs = fm.get("inputs", {})
    # A manifest that lists nothing would pass every loop below. It must not.
    for key in ("generator", "generator_sha256", "inputs", "figures", "values"):
        if not fm.get(key):
            fails.append("figure manifest lacks %s; the check must never pass vacuously" % key)
    if len(figures) < min_figures:
        fails.append("figure manifest names %d figure(s); the manuscript carries at least %d"
                     % (len(figures), min_figures))

    fig_paths = {rel: root / rel for rel in figures}
    newest_fig = 0.0
    for rel, p in fig_paths.items():
        if not p.exists():
            fails.append("figure missing: " + rel)
            continue
        if sha256(p) != figures[rel]:
            fails.append("figure differs from its manifest hash: " + rel)
        newest_fig = max(newest_fig, p.stat().st_mtime)
    oldest_fig = min((p.stat().st_mtime for p in fig_paths.values() if p.exists()),
                     default=0.0)

    for rel, h in inputs.items():
        p = root / rel
        if not p.exists():
            fails.append("input missing: " + rel)
            continue
        changed = sha256(p) != h
        if changed:
            fails.append("input changed since the render: " + rel)
        if p.stat().st_mtime - oldest_fig > SLACK_S:
            fails.append("input is newer than a figure: " + rel
                         + ("" if changed else
                            " (content hash unchanged, so a checkout or extraction reset the"
                            " timestamps; re-run scripts/make_figures.py, which renders"
                            " byte-identically)"))

    gen_rel = fm.get("generator")
    gen = root / gen_rel if gen_rel else None
    if gen and gen.exists():
        if sha256(gen) != fm.get("generator_sha256"):
            fails.append("generator changed since the render: " + gen_rel)
        if gen.stat().st_mtime - oldest_fig > SLACK_S:
            fails.append("generator is newer than a figure: " + gen_rel)
    elif gen_rel:
        fails.append("generator missing: " + gen_rel)

    referenced = set()
    if manuscript.exists():
        text = manuscript.read_text(encoding="utf-8", errors="replace")
        text = re.sub(r"(?<!\\)%.*", "", text)
        for m in INCLUDE.finditer(text):
            name = m.group(1).strip()
            cand = [name, name + ".pdf"]
            base = manuscript.parent
            hit = None
            for c in cand:
                rel = (base / c).resolve()
                try:
                    rel_s = rel.relative_to(root.resolve()).as_posix()
                except ValueError:
                    rel_s = None
                if rel_s in figures:
                    hit = rel_s
                    break
            if hit is None:
                fails.append("manuscript includes a figure with no manifest entry: " + name)
            else:
                referenced.add(hit)
    else:
        fails.append("manuscript missing: " + manuscript.as_posix())
    for rel in figures:
        if rel not in referenced:
            notes.append("manifested but not referenced by the manuscript: " + rel)

    if macro_index.exists():
        idx = load_index_values(macro_index)
        for name, v in fm.get("values", {}).items():
            if name not in idx:
                fails.append("plotted value has no macro in the index: " + name)
                continue
            try:
                if abs(float(idx[name]) - float(v)) > 5e-7:
                    fails.append("plotted value disagrees with the macro index: %s (%r vs %r)"
                                 % (name, v, idx[name]))
            except (TypeError, ValueError):
                if idx[name] != v:
                    fails.append("plotted value disagrees with the macro index: " + name)
    else:
        fails.append("macro index missing: " + macro_index.as_posix())

    # Typed constants: the only one the generator may carry is the chance
    # level of AUC-ROC, a definition rather than a measurement (rule 12). Any
    # other constant, or a different value for this one, fails the check.
    for name, v in (fm.get("constants") or {}).items():
        if name == "note":
            continue
        if name not in ALLOWED_CONSTANTS or float(v) != ALLOWED_CONSTANTS[name]:
            fails.append("typed constant not on the allow list: %s=%r" % (name, v))

    for rel, p in fig_paths.items():
        if p.exists():
            for prob in pdf_metadata_problems(p.read_bytes(), title):
                fails.append(rel + ": " + prob)

    print("figure check: %d figure(s), %d input(s), %d plotted value(s) checked"
          % (len(figures), len(inputs), len(fm.get("values", {}))))
    for n in notes:
        print("  NOTE      " + n)
    for f in fails:
        print("  FAILED    " + f)
    if fails:
        print("FAILED - a figure is stale, unmanifested, off-macro, or carries "
              "identifying metadata. Re-run scripts/make_figures.py.")
        return 1
    print("PASSED - every figure is fresh, manifested, drawn from the macro "
          "layer, and metadata-clean.")
    return 0


def main() -> int:
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
