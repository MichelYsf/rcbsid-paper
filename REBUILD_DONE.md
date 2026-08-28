# REBUILD_DONE — the honest rebuild is complete

Recorded 2026-08-24 on `rebuild/honest-v1`. All stages of the rebuild runbook
have terminal states:

| stage | state | deliverable |
|---|---|---|
| S0 provenance spine + gates | done | `scripts/provenance.py`, `scripts/check_provenance.py`, `tests/` |
| S1 natural-order streams | done | `data/raw/natural/`, `findings_streams.md`, cross-platform SHA verification |
| S2 prevalence sweep relabelled | done | `findings_prevalence.md` (CI-15, CI-16) |
| S3 score/threshold identity | done | `findings_score_threshold.md` (CI-17) |
| S4 construction contrast | done | `findings_contrast.md`, four arms + seed sensitivity, adversarially verified (0/6 claims survived unchanged; all acted on) |
| S5 verified contributions | done | `findings_contributions.md` (1 supported / 3 partial / 4 unsupported / 3 withdrawn) |
| S6 corrected-statistic ablation | done under a 30-minute cap (CI-18) | `findings_bocpd_ablation.md` — a failure mode, not a working correction |
| S7 ACM manuscript rebuild | done | `paper/main.tex` compiles clean (pdflatex+bibtex ×3, 0 undefined refs; 17 pp as of the round-3 revisions); every number a manifest-backed macro |
| S8 artifact preparation | done | `PUBLISH_INSTRUCTIONS.md`, `packages/`, nothing published |
| WRAP | done | `SCOPE_DECISIONS.md` (corrected-incident log), `SUPERSEDED.md`, `CLAIM_LEDGER.md` (gate-checked), `README.md`, `CITATION.cff` |

Governing rule enforced end to end: 564 manifested macros, 0 orphans,
0 ambiguous, macro index verified against manifests, claim ledger green,
manuscript macro check green, 72 tests passing.

Cloud: torn down and verified 2026-08-20; eu-central-1 holds 0 instances,
0 volumes, 0 snapshots. Total rebuild cloud spend: $4.86.

Remaining work is FINALIZE-scope (post-rebuild): see `FINALIZE_DONE.md` for
the residual human actions.
