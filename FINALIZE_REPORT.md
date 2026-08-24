# FINALIZE_REPORT — 2026-08-24

Mission: carry the rebuilt project to submission-ready with zero human input
except logins, one decision, and pasting reviewer output. **Status: COMPLETE.**
Nothing was published, submitted, emailed, or sent anywhere.

## Verification state (all green, all re-runnable)

| check | result |
|---|---|
| `pytest -q` | 72 passed |
| provenance gate | 367 manifested macros, 0 orphans, 0 mismatches, 0 ambiguous, index verified |
| claim ledger (`--ledger`) | 25 sentence rows, every reference resolves |
| manuscript macro check | every macro used is defined |
| anonymous manuscript compile | pdflatex+bibtex ×3, exit 0, **0 undefined refs**, 10 pp |
| arXiv named variant compile | exit 0, 0 undefined refs, 10 pp, `.bbl` shipped |
| anonymity scan of DTRAP artifact | 163 files, no identifying token survives |
| PDF content scan | key numbers render; no macro leaks; no author identity; all table refs resolve |
| resume entries | none registered (Startup, scheduled tasks, processes all clean) |
| cloud | nothing exists, nothing billing (verified 2026-08-20) |

## F-item outcomes

- **F1**: `REBUILD_DONE.md` — S0–S8+WRAP terminal.
- **F2**: `README_repo_final.md` never committed (tree + full history verified);
  `README.md` regenerated truthfully; `CITATION.cff` corrected (real ORCID, no
  invented DOI — none ever existed); `SUPERSEDED.md` covers repo, branches,
  and the Downloads-folder artifacts.
- **F3**: ORCID resolved: **0009-0000-0664-8228** (registry record is the
  author's, lists the papers; **…8224 is a 404**). Used everywhere; 60-second
  confirmation is HUMAN_ACTIONS step 0.
- **F4**: manuscript rewritten under R1–R12; `CLAIM_LEDGER.md` gate-checked;
  `TITLE_ABSTRACT_OPTIONS.md` (3 titles, 2 abstracts, ledger-mapped); gate
  green is standing.
- **F5**: `REVIEWER_KIT/` — prompt, compiled PDF, one-round triage template,
  response shelf seeded with the six anticipated objections (missing finals
  with bounded cost, single-seed policy, why the composite is retained,
  known-art detector, the 204-minute window, the correction history).
- **F6**: `SIBLING_DECISION.md` + both artifacts final-quality; standing
  recommendation recorded (withdraw before v3); nothing executed.
- **F7**: all four packages built; DTRAP portal fetched fresh
  (ScholarOne at mc.manuscriptcentral.com/dtrap; ACM large-format; 10–25 pp;
  double-anonymous — cited from the author-guidelines page via search
  snapshot, the page itself blocks robots); `HUMAN_ACTIONS.md` is
  click-by-click with exactly one decision point.
- **F8**: this report; contradiction sweep run and acted on (below).

## The contradiction sweep earned its cost (CI-19)

Three independent auditors over the compiled manuscript returned
**7 BLOCKING / 10 WORDING / 6 NIT** findings; every one was fixed and
re-verified in the recompiled PDF. The three worth remembering:

1. The introduction attributed the LOF-vs-detector result to the
   "natural-order held-out slice" — the CI-1 class error, reintroduced during
   the rebuild itself, **and the claim ledger's row I15 carried the same
   words**, so the instrument built to catch it validated it instead.
   Independence of the checker from the author is what worked; the ledger
   alone is not sufficient.
2. "Falls monotonically" was falsified by the sentence's own two first
   values. Mechanical claim, mechanical refutation.
3. The shipped PDF rendered "(Table eftab:litnet)": a `\ref` whose backslash
   had been destroyed by the shell-heredoc `\r` escape, invisible to the
   undefined-reference check because a `\ref` without its backslash is not a
   reference. The `\b`/`\t`/`\r` heredoc-damage class is now fully recorded;
   backslash-bearing edits go through script files only.

Also from the sweep: five typed literals are now manifested
(`supplementary_macros` run: 162,000 attack-free rows, 77.660% Friday
density, the 15,000-record diagnostic window, and two unsigned magnitudes);
single-seed HST placements were removed from all flat rankings; the arXiv
IDs were stripped from the anonymous build (they de-anonymized it) and are
reinstated only in the named variant by `scripts/build_arxiv_variant.py`.

## Deviations from the mission text, stated

- DTRAP's fetched instructions ("ACM large format") supersede the rebuild
  spec's `sigconf`; the submission uses acmart `manuscript,anonymous,review`.
- `ACM_waiver_confirmation_2026-08-07.pdf` and the Delman thread are not on
  this machine; the cover letter references the waiver and flags the
  attachment step, and the Delman reply is drafted from the resolved-ORCID
  context (HUMAN_ACTIONS steps 5.5–5.6).
- Zenodo's search API was down (504) during F2 verification; the no-deposit
  conclusion rests on the repository's placeholder-only history and the
  prior abstract's "[TO BE INSERTED]" comment.
- The compiled manuscript is 10 pages against DTRAP's "most submissions
  10–25": at the low edge, deliberately — the response shelf carries the
  compact-by-design answer.

## Residual risk register

- The sweep's auditor 3 flagged an unresolved tension about the sibling
  paper's threshold derivation (`findings_paper_overlap.md` vs
  `SIBLING_DECISION.md`) that only a human read of the sibling manuscript can
  settle; it does not affect this paper's packages.
- CLAIM_LEDGER gists are prose and can drift from manifests in ways the gate
  cannot see (CI-19); any future manuscript edit should re-run an independent
  sweep, not just the gate.
