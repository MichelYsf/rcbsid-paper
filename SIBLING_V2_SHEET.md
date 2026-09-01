# SIBLING_V2_SHEET: v2 replacement of arXiv:2510.09619

**What this is.** The companion preprint ("Risk-Calibrated Bayesian Streaming
Intrusion Detection with SRE-Aligned Decisions") gets a corrected
**replacement**, not a withdrawal. The decision is FINAL and recorded in
`SIBLING_DECISION.md`. The v2 is the v1 paper plus the prepared correction
note. Nothing else in the paper changes.

**When.** After the DTRAP submission and after the main paper's arXiv v3
replacement (`HUMAN_ACTIONS.md` steps 3 and 4). Nothing in the main paper's
path waits on this.

**State as of 2026-09-01: the upload package is built and verified.** The v1
source was fetched from arXiv's public e-print endpoint in one request and
unpacked to `packages/sibling/v1_source/`. Compiled unchanged, it reproduces
the public v1 PDF: 8 pages, same title, same abstract text, verified against
the arXiv-stamped copy. The two blocks from
`packages/sibling/V2_CORRECTION_NOTE.tex` were inserted at the positions this
sheet specified (the framed note right after `\maketitle`, the bracketed
sentence first inside the abstract). A diff of `v1_source/main.tex` against
`v2_source/main.tex` shows exactly those two insertions and nothing else. The
v2 build has zero errors, zero undefined references, and zero overfull boxes.
It is 8 pages, the same count as v1. The staged tarball itself was extracted
fresh and compiled clean.

## Steps

1. **Upload the staged tarball.** Sign in at https://arxiv.org, open paper
   2510.09619, choose **Replace**, and upload
   `packages/sibling/arxiv_2510_09619_v2_source.tar.gz` (117,077 bytes). It
   contains `main.tex`, `refs.bib`, `main.bbl` (arXiv does not run BibTeX),
   `00README.json`, and the seven figure PDFs, in the same layout as v1.
2. **Abstract metadata field.** Add the correction sentence to the abstract
   metadata so it shows on the arXiv abstract page, not only in the PDF.
   Paste it as plain text, without the `\emph`:

   > [Corrected v2: an audit found that the score, threshold, and latency
   > descriptions below are not what the shared codebase implements, and that
   > the evaluation streams are assembled constructions. See the correction
   > note on the title page and the corrected companion work,
   > arXiv:2605.24696 (v3 forthcoming), artifact doi:10.5281/zenodo.22213264.]

3. **Comments field.** Set to exactly:

   > v2: correction note added (title page and abstract). An audit of the
   > shared codebase found the score, threshold, and latency descriptions
   > unsupported by the implementation, and the evaluation streams to be
   > assembled constructions. No quantitative result tables are affected.
   > See arXiv:2605.24696 (corrected v3) and doi:10.5281/zenodo.22213264.

4. **License.** Keep the license chosen for v1. arXiv applies the license per
   version. Changing it on a correction invites questions the note already
   answers. Do not select a broader license than v1's.
5. **Preview.** Confirm arXiv's own build shows 8 pages, the framed
   correction note on page 1 above the abstract, and the bracketed sentence
   opening the abstract. Then submit the replacement and note the
   announcement date.
6. **Order.** Post this only after the main paper's v3 is on arXiv. The
   staged note says "v3 forthcoming", which is accurate while v3 is submitted
   and awaiting announcement. If you would rather the note cite v3 plainly,
   that needs a small edit round first: change the two "(v3 forthcoming)"
   spots in `packages/sibling/v2_source/main.tex`, recompile, and re-tar.

**Do not post any of this yet.** This sheet is preparation. Execution is
`HUMAN_ACTIONS.md` step 5.
