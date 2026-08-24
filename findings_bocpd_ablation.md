# findings_bocpd_ablation — the corrected change-point statistic (Stage 6)

Generating run: `s6_bocpd_corrected_ablation_20260824T092655_a47acf51`. Every number is a provenance macro.

## Scope reduction, stated up front

The operator capped Stage 6 at **30 minutes of local compute** (down from 90) with no cloud. Scope was reduced to fit, and the reductions are limitations of this result, not footnotes:

- **One stream**, `litnet2020_udp_flood_natural` (d=36, ~1.75 ms/row). CICIDS2017 is excluded: at d=84 a two-arm full-stream run is ~3.3 h.
- **A 200,000-record prefix**, not the 500,000-record stream. Both arms see the identical prefix, so this is a paired comparison on one slice. No prevalence figure here is comparable with Stage 1 or Stage 4.
- **blaster_worm and spam excluded** for an independent reason: their attacks sit at the end of the stream, so any prefix holds no test attacks.
- **One seed**, permitted by binding rule 7 because both variants are deterministic (Stage 2 measured this detector at sd 0.0000 across three draws).

Total local compute: **155.3 s** against a cap of 1800 s.

## Does the corrected statistic respond to a change point?

A 6-sigma mean shift in a 3-D Gaussian stream, hazard 0.001:

| variant | peak `P(r=0)` after the shift | as a multiple of the hazard |
|---|---|---|
| evaluated detector | 0.001000 | 1.0x |
| corrected statistic | 1.000000 | 1000.0x |

**Yes.** The correction does what audit finding A2 said was missing: the reset branch is scored under a freshly started run rather than under the existing ones, the predictive term stops cancelling, and `P(r=0)` becomes a function of the data.

The first attempt at this correction failed and the failure is worth recording. Using the *global* slowly-adapting Gaussian as the prior predictive changed nothing (`P(r=0)` peak 0.001001 against a hazard of 0.001000), because immediately after a change the global model is just as stale as the run-conditional ones and both branches take the same penalty. A reset branch is informative only if a surprising point is *better* explained by starting over — which requires a vague predictive. The implemented version is the Normal-Inverse-Gamma prior predictive, a Student-t with nu=2 and squared scale twice the global variance, at the standard weakly-informative hyperparameters. No value was chosen by looking at a result.

## Does it change detection?

On a 200000-record prefix, 30000 held-out records carrying 4840 attacks (chance floor 0.1613):

| variant | AUC-PR | lift above chance | AUC-ROC | wall |
|---|---|---|---|---|
| original | 0.3975 | +0.2362 | 0.8482 | 743 s |
| corrected | 0.1699 | +0.0086 | 0.5096 | 586 s |

**Measured (mechanical, threshold = 0.01 AUC-PR):** the corrected variant **DEGRADES** AUC-PR on this slice (delta -0.2276), and its AUC-ROC of 0.5096 is at chance.

### Why — and why the obvious reading is wrong

| quantity | evaluated detector | corrected statistic |
|---|---|---|
| mean posterior mass `P(r<=5)` | 0.0065 | 1.0000 |
| scores exactly at the 0.25 cap | 0.5% | 92.7% |
| distinct score values | 3899 | 747 |
| score standard deviation | 0.2190 | 0.1593 |

The corrected variant's run-length posterior is collapsed onto short runs at **every step** (mean `P(r<=5)` = 1.0000), so `0.25 * P(r<=5)` saturates and 92.7% of its scores are exactly 0.25. It emits 747 distinct values where the original emits 3899. A score that is constant on most records cannot rank, which is what an AUC-ROC of 0.5096 means.

**So the honest conclusion is not "repairing the change-point statistic degrades detection".** It is that both variants are degenerate, in opposite directions. The evaluated detector never resets — `P(r=0)` is algebraically pinned to the hazard. This correction always resets — a nu=2 Student-t prior predictive assigns a fresh run higher likelihood than any fitted run for nearly every point. Neither is change-point detection.

A statistic that resets when the data warrants it needs a prior-predictive scale between the two, and locating it is a hyperparameter search. That is excluded here by the 30-minute cap, and it is constrained by the rule against selecting on test labels. **Stage 6 therefore establishes the failure mode and not a working correction**, and the manuscript may claim no more.

This is one stream and one slice. It does not establish what the correction does on CICIDS2017, on the full stream, or at other prevalences, and none of those may be asserted from it.

