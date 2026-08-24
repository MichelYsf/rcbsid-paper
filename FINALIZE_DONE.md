# FINALIZE_DONE — status COMPLETE (2026-08-24)

Everything that can be done without a login is done and verified
(`FINALIZE_REPORT.md`). No resume entries are registered. Nothing has been
published, submitted, or sent.

## Residual human actions (the complete list)

Execute `HUMAN_ACTIONS.md` top to bottom. In brief:

0. **ORCID** — 60-second confirmation at orcid.org that your iD is
   0009-0000-0664-8228.
1. **Reviewer round** — paste `REVIEWER_KIT/REVIEWER_PROMPT.txt` +
   `REVIEWER_KIT/manuscript_review.pdf` into fresh reviewer sessions; save
   outputs as `REVIEWER_KIT/review_fresh_<n>.md`.
2. **Zenodo** — publish the prepared bundle; paste the minted DOI into
   CITATION.cff.
3. **THE DECISION** — sibling paper: withdraw from TIFS before v3
   (recommended; letter ready) or coexist (wording ready). Then step 3b's
   two-minute paragraph alignment.
4. **arXiv v3** — upload `packages/arxiv_v3/arxiv_v3_source.tar.gz`, new
   title, chosen Comments variant.
5. **DTRAP** — submit at mc.manuscriptcentral.com/dtrap with the anonymous
   PDF, artifact zip, cover letter; attach the waiver PDF from email; send
   the Delman reply if the thread is open.
6. **Optional** — retire the AWS IAM key.

## Reviewer-kit usage, exactly

When the fresh reviews are back and you say "reviews are in":

1. `REVIEWER_KIT/REVIEW_TRIAGE_TEMPLATE.md` is executed **once**:
   - every factual claim verified against `paper/numbers.tex`,
     `results/manifests/`, and the code before it is believed;
   - verified-true items fixed under the binding claim rules
     (SCOPE_DECISIONS.md rules 7–8, F4 R1–R12), gates re-run
     (`python scripts/check_provenance.py`,
     `python scripts/check_manuscript_macros.py`, `python -m pytest -q`),
     manuscript recompiled three-pass, and an independent contradiction
     sweep re-run (CI-19: the ledger alone is not sufficient);
   - judgment items appended to `REVIEWER_KIT/RESPONSE_SHELF.md` with
     prepared responses;
   - packages regenerated: `python scripts/build_arxiv_variant.py` +
     three-pass compile + re-tar; `python scripts/build_anonymous_artifact.py`;
     recopy `paper/main.pdf` into `packages/dtrap/` and `REVIEWER_KIT/`.
2. The round closes. **Never loop.**

## Invariants that must stay true at every future edit

`python scripts/check_provenance.py` green (gate + ledger),
`python scripts/check_manuscript_macros.py` green, `python -m pytest -q`
green, three-pass compile with zero undefined references, anonymity scan
green — and no backslash-bearing text ever edited through a shell heredoc.
