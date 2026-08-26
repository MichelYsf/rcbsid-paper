# CLAIM_LEDGER — every abstract and introduction sentence, mapped to its source

Machine-checked by `scripts/check_provenance.py --ledger`. Each row's
**source** column carries one or more references of the form
`manifest:<run_id>` (a file in `results/manifests/`), `file:<repo-path>`
(a findings or scope document), or `logic` (a definition, transition, or
statement of intent carrying no measured number). The gate fails if any
referenced manifest or file does not exist. Sentence text is abbreviated;
the sentence numbering follows `paper/main.tex` reading order.

## Abstract

| # | sentence (gist) | source |
|---|---|---|
| A1 | Streaming IDS results are reported on assembled streams (pooled / interleaved). | logic — framing; construction practice documented in file:AUDIT_FINDINGS.md (A5, A13) and file:findings_streams.md |
| A2 | Stream assembly is an uncontrolled treatment: it jointly changes held-out membership, prevalence and order, and thereby the measured outcome. | manifest:s4_contrast_deliverables_20260826T203706_083c4e0e; file:findings_contrast.md |
| A3 | Identical full multiset; under a fixed positional split the two arms hold out different samples at 68.235% and 25.240% prevalence (42.995 pp apart). | manifest:s4_contrast_deliverables_20260826T203706_083c4e0e; manifest:cicids_heldout_composition_20260819T120420_ebb7c281 |
| A4 | Held-out slices share only 32.5% of records. | manifest:cicids_heldout_composition_20260819T120420_ebb7c281 |
| A5 | The measured ordering of the two deterministic scorers reverses between arms; ECOD is a label-privileged diagnostic reference, so this is a pipeline-level outcome, not method superiority. | manifest:s4_construction_contrast_20260819T090813_46e9bd32; manifest:s4_construction_contrast_20260819T064027_20f44694; file:findings_contrast.md |
| A6 | LITNET pooled 6.498% held-out prevalence is the equal-weight mean over captures spanning 0.176%–15.775% held-out prevalence. | manifest:s4_construction_contrast_20260818T124510_2b2d27b1; manifest:s4_construction_contrast_20260819T064027_a3c43fc6; file:findings_contrast.md |
| A7 | Branch cancellation pins P(r=0) to the hazard BELOW the run-length cap; at and beyond the cap, where the evaluations live, it wanders; the scored quantity is a function of P(r<=5). | manifest:s3_score_threshold_verification_20260820T084659_1e2b01b8; file:findings_score_threshold.md |
| A8 | One untuned prior-predictive repair saturates the score and ranks near chance on the stream and prefix tested. | manifest:s6_bocpd_corrected_ablation_20260824T092655_a47acf51; file:findings_bocpd_ablation.md |
| A5b | Restricting both arms to the 78,000 shared held-out records removes the reversal: the detector leads in both. | manifest:review_bounded_analyses_20260826T224417_b8314db2; file:findings_review_analyses.md |
| A7b | The auxiliary branch ranks below chance and the deployed composition ranks worse than its own tail term. | manifest:review_bounded_analyses_20260826T224417_b8314db2; file:findings_review_analyses.md |
| A9 | Every number traces to an archived hash-verified manifest; the ledger ships with the artifact. | logic — enforced by file:scripts/check_provenance.py; this document |

## Introduction

| # | sentence (gist) | source |
|---|---|---|
| I1 | Benchmark criticism context (Catillo, Arp, Ring). | logic — citation framing |
| I2 | This paper adds the assembly step to that list. | logic — thesis statement, evidenced by I5–I8 |
| I3 | Captures are rarely usable as-is (CICIDS five days; LITNET disjoint). | manifest:stage1_natural_streams_20260818T114117_285582fc; file:findings_streams.md |
| I4 | Assembly is treated as neutral plumbing; it is not - it moves prevalence, replaces two-thirds of the evaluated sample, and changes the measured ordering. | manifest:s4_contrast_deliverables_20260826T203706_083c4e0e; manifest:cicids_heldout_composition_20260819T120420_ebb7c281 |
| I5 | (Origin) Earlier versions reported composite-construction results and described a scoring rule the code did not implement. | file:AUDIT_FINDINGS.md (A1–A4); file:SCOPE_DECISIONS.md (CI-1, CI-2) |
| I6 | (Origin) Independent adversarial review and line-by-line audit established both. | file:AUDIT_FINDINGS.md; file:SUPERSEDED.md (review documents) |
| I7 | (Origin) Present version: labeled synthetic protocol, detector described as implemented, every number manifested, gate fails on orphans. | logic — process; enforced by file:scripts/check_provenance.py; file:SCOPE_DECISIONS.md |
| I8 | (Origin) Eighteen corrected incidents ship with the artifact. | file:SCOPE_DECISIONS.md |
| I9 | (C1) Identical multiset verified mechanically; 1,600,000 records / 352,962 attacks both arms. | manifest:cicids_heldout_composition_20260819T120420_ebb7c281 |
| I10 | (C1) Prevalence 68.235→25.240; slices share 78,000 of 240,000 (32.5%); 103,189 attacks relocated; the deterministic ordering reverses under a fixed split rule. | manifest:s4_contrast_deliverables_20260826T203706_083c4e0e; manifest:cicids_heldout_composition_20260819T120420_ebb7c281 |
| I11 | (C2) Pooled 6.498% held-out prevalence equals the equal-weight mean of 0.176%/3.544%/15.775% held-out prevalences. | manifest:s4_contrast_deliverables_20260826T203706_083c4e0e; file:findings_contrast.md |
| I12 | (C3) Posterior pinned to hazard; auxiliary contributes mean 0.0025 where it binds. | manifest:s3_score_threshold_verification_20260820T084659_1e2b01b8 |
| I13 | (C3) One untuned repair saturates: 92.7% of scores at the cap, 747 distinct values, near-chance ranking; both variants degenerate in opposite directions. | manifest:s6_bocpd_corrected_ablation_20260824T092655_a47acf51 |
| I14 | (C4) Provenance discipline: macro layer, gate fails on orphans/ambiguity/index drift. | logic — process; file:scripts/check_provenance.py; file:tests/test_provenance.py |
| I15 | LOF 0.8632 vs detector 0.5450 on the identical held-out slice of the interleaved (unresampled) stream. | manifest:s2_prevalence_relabelled_20260826T203109_0d596e73; file:findings_prevalence.md |
| I16 | Detector lift peaks at +0.348 (10%) and falls from there to −0.020 (64%), below chance. | manifest:s2_prevalence_relabelled_20260826T203109_0d596e73; file:findings_prevalence.md |

## Standing constraints the ledger enforces on prose

- Binding rule 7 (`file:SCOPE_DECISIONS.md`): no flat ranking claim involving a
  stochastic method; HST appears only with seed distributions
  (manifest:s4_contrast_deliverables_20260826T203706_083c4e0e carries the
  seed-sensitivity macros; the sweep spreads are in
  manifest:s2_prevalence_relabelled_20260826T203109_0d596e73).
- Binding rule 8 (`file:SCOPE_DECISIONS.md`): the central claim is stated as
  measured — rotation not reversal, no causal-deployment language, floor-
  relative reading included (A5, I10 above).
