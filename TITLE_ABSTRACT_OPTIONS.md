# TITLE_ABSTRACT_OPTIONS — ledger-checked alternatives

Every claim in every option below maps to CLAIM_LEDGER.md rows A1–A9; no
option introduces a claim the ledger does not carry. The manuscript currently
uses Title 1 + Abstract A. Swapping is a find-replace in `paper/main.tex`,
nothing else moves.

## Titles

**T1 (current).** *Benchmark Stream Construction, Not Attack Prevalence,
Produces the Regime Structure of Streaming Intrusion Detection*
— Declarative, states the finding. Risk: reads strong; the paper's fencing
(rotation not reversal, no deployment causality) is in the body, and a
skimming referee may test the title against the strongest reading.

**T2.** *The Assembly Is the Regime: How Stream Construction Manufactures
Evaluation Conditions in Streaming Intrusion Detection*
— Slightly hedged, mechanism-first. Risk: "manufactures" carries rhetorical
charge; DTRAP referees may prefer flatter wording.

**T3.** *Same Records, Different Regime: Ordering and Pooling Effects in
Streaming Intrusion-Detection Benchmarks*
— The most conservative; promises exactly the two experiments delivered
(ordering contrast, pooling identity). Risk: undersells the method-identity
findings (Sections 3 and 7), which reviewers of the prior version will look
for.

## Abstracts

**Abstract A (current, in `paper/main.tex`).** Ledger rows A1–A9. Leads with
the construction finding, states the CICIDS contrast with its three numbers
(prevalence shift, slice overlap, deterministic inversion), the LITNET
pooling identity, then the method-identity findings, then the provenance
discipline.

**Abstract B (alternative, correction-forward).** Ledger rows A1–A9 plus
I5–I8. For use if the venue or editor prefers the correction history in the
abstract rather than only in the introduction:

> Earlier versions of this work reported streaming intrusion-detection
> results produced under a composite benchmark construction and described a
> scoring rule the released code did not implement. This version rebuilds
> the study from an adversarial audit and reports what survives. Holding the
> CICIDS2017 record multiset identical and changing only the ordering moves
> held-out prevalence by 43 percentage points, leaves the natural and
> synthetic held-out slices sharing 32.5% of their records, and inverts the
> ordering of the two deterministic methods under test; the full ranking
> change is a rotation (Kendall τ = −0.333). On LITNET-2020, the composite's
> single 6.5% prevalence is an identity of pooling three temporally disjoint
> captures spanning 0.18%–15.8%. The evaluated detector's run-length
> posterior is algebraically pinned to its hazard rate, making the system
> prequential global-Gaussian tail scoring rather than change-point
> detection; the textbook repair saturates the score and detects nothing.
> Every number traces to an archived, hash-verified run manifest, and the
> sentence-level claim ledger ships with the artifact.

Ledger check for Abstract B: sentence 1–2 → I5–I8; sentence 3 → A3–A5;
sentence 4 → A6; sentence 5 → A7–A8; sentence 6 → A9. Verified 2026-08-24
against CLAIM_LEDGER.md; the gate's `--ledger` mode covers the referenced
rows' sources.

## Recommendation

T1 + Abstract A for DTRAP (the venue rewards direct findings; the origin
paragraph in the introduction carries the correction openly). If the editor
requests the correction be surfaced earlier, switch to Abstract B without
changing anything else.
