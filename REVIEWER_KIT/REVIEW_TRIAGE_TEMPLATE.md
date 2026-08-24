# REVIEW_TRIAGE_TEMPLATE — the one-round rule

When fresh reviews arrive, this template is executed **exactly once**. There
is no second adversarial round before submission: fix what is verified
broken, shelve what is judgment, submit. Looping on reviewer output is how a
paper dies of polish.

## Step 1 — Verify before believing (every factual claim, no exceptions)

For each factual claim in a review (a number is wrong, a test is missing, a
cited work says otherwise, the code does X):

1. Locate the primary source: the macro in `paper/numbers.tex`, its manifest
   in `results/manifests/`, the findings file, or the code line.
2. Record in the triage table: `VERIFIED-TRUE`, `VERIFIED-FALSE` (with the
   evidence), or `UNVERIFIABLE` (reviewer claim references nothing checkable).
3. A reviewer's confident assertion is not evidence. This project has a
   recorded history of confident wrong readings — including our own (CI-12,
   CI-17, the Stage-6 first reading). Reviews of the *previous* version also
   contained findings that were correct about v2 but are already fixed; check
   against the CURRENT tree, not memory.

Triage table (fill in place):

| # | reviewer claim (gist) | class | verification | disposition |
|---|---|---|---|---|
| 1 | … | factual / judgment | VERIFIED-TRUE: <evidence> | FIX / SHELF |

## Step 2 — Fix only what is VERIFIED-TRUE, under the F4 binding claim rules

- Every fix respects R1–R12 (SCOPE_DECISIONS.md rules 7–8 and the F4 rules):
  no flat stochastic rankings, the central claim stated exactly as measured,
  no causal-deployment language, negative results stay findings.
- A fix that requires NEW compute is only made if it fits locally in under
  30 minutes; otherwise it goes to the shelf with its measured cost
  (see RESPONSE_SHELF.md, "bounded revision-window costs").
- After fixes: `python scripts/emit_numbers_tex.py`, full gate
  (`python scripts/check_provenance.py` — includes the claim ledger), macro
  check, recompile, contradiction sweep. All green before Step 3.

## Step 3 — Shelve judgment items

Anything that is opinion, scope preference, framing taste, or a request for
work beyond the revision window goes to `RESPONSE_SHELF.md` with a prepared
response for the eventual author reply. Do NOT edit the paper for judgment
items in this round.

## Step 4 — Regenerate packages, stop

Rebuild the arXiv/Zenodo/DTRAP packages (`FINALIZE_DONE.md` lists the
commands), update `HUMAN_ACTIONS.md` if any click changed, and stop. The
round is closed. Never loop.
