# SIBLING_V2_SHEET — v2 replacement of arXiv:2510.09619

**What this is.** The companion preprint ("Risk-Calibrated Bayesian Streaming
Intrusion Detection with SRE-Aligned Decisions") gets a corrected
**replacement**, not a withdrawal — decision FINAL, `SIBLING_DECISION.md`.
The v2 is the existing paper plus the prepared correction note; no science
rebuild, no other text changes.

**When.** After the DTRAP submission and the arXiv v3 replacement of the main
paper (`HUMAN_ACTIONS.md` steps 3–4). Nothing in the main paper's path waits
on this.

**Compile status of the note.** The sibling's LaTeX source is **not on this
machine** (verified 2026-08-31: only two PDFs of the companion exist locally;
both candidate zips in Downloads contain the *main* CALIBURN paper per their
`\title`). The correction note itself was compile-verified 2026-08-31 in a
minimal two-column `article` wrapper — both blocks, zero errors, zero
overfull — but it has, necessarily, **not** been compiled inside the real
sibling source. Step 3 below is therefore mandatory, not a formality.

## Steps

1. **Retrieve your own source.** Sign in at https://arxiv.org → your papers →
   2510.09619. Under "Download source" (or via the Replace flow, which offers
   the current source), download the v1 source archive to this machine. Do not
   reconstruct the paper from the PDF.
2. **Paste the correction note.** Open the main `.tex` file and paste the two
   blocks from `packages/sibling/V2_CORRECTION_NOTE.tex`:
   - **Block 1** (the framed note) immediately after `\maketitle`. If the
     class builds the title with `\twocolumn[...]` and you want the note
     spanning both columns, place Block 1 inside that bracket group instead;
     in-column is also acceptable — it compiles either way.
   - **Block 2** (the bracketed `\emph` sentence, uncomment it) as the first
     sentence inside the abstract environment, before the original first
     sentence. Do not remove or reword any original abstract text.
3. **Recompile locally** (same engine as v1, typically pdflatex ×2). Confirm:
   zero errors; the framed note visible on page 1; the abstract opens with the
   bracketed correction sentence; page count may grow by up to one — that is
   fine.
4. **Replace on arXiv.** Paper 2510.09619 → **Replace** → upload the modified
   source archive. Title, authors, abstract *metadata field*: update the
   abstract metadata to include Block 2's sentence (plain text, drop the
   `\emph`), so the correction is visible on the abstract page, not only in
   the PDF.
5. **Comments field** — set to exactly:

   > v2: correction note added (title page and abstract). An audit of the
   > shared codebase found the score, threshold, and latency descriptions
   > unsupported by the implementation, and the evaluation streams to be
   > assembled constructions. No quantitative result tables are affected.
   > See arXiv:2605.24696 (corrected v3) and doi:10.5281/zenodo.22213264.

6. **License:** keep the license chosen for v1 — arXiv applies the license per
   version, and changing it on a correction invites questions the note already
   answers. Do not select a broader license than v1's.
7. Confirm arXiv's preview, submit the replacement, and note the announcement
   date. **Do not post before the main paper's v3 is on arXiv** — the note
   says "v3 forthcoming" only until then; if v3 is already announced, you may
   change "(corrected version v3 forthcoming)" in Block 1 and "(v3
   forthcoming)" in Block 2 to cite v3 plainly before uploading.

**Do not post any of this yet.** This sheet is preparation; execution is
`HUMAN_ACTIONS.md` step 5.
