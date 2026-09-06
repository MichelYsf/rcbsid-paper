# findings_referee_analyses — A to E (hostile-referee triage)

Generating run: `referee_bounded_analyses_20260906T182158_de69afab`. Every number is a provenance macro.

## A — ECOD on the shared records, batch-controlled

| arm | ECOD AUC-PR, 240000-record batch (Table 5) | ECOD AUC-PR, 78000-record batch (own batch) | detector AUC-PR | margin det minus ECOD (240000) | margin det minus ECOD (78000) |
|---|---|---|---|---|---|
| natural | 0.844487 | 0.847585 | 0.905613 | 0.061126 | 0.058028 |
| synthetic | 0.849842 | 0.844797 | 0.900371 | 0.050529 | 0.055574 |

## B — event-block bootstrap (block 100, 1000 resamples)

| quantity | 2.5% | 97.5% |
|---|---|---|
| FullNaturalFullMargin | 0.021099 | 0.032692 |
| FullSyntheticFullMargin | 0.122046 | 0.130294 |
| Shared240NaturalMargin | 0.053856 | 0.067720 |
| Shared78NaturalMargin | 0.051770 | 0.064229 |
| Shared240SyntheticMargin | 0.044634 | 0.056329 |
| Shared78SyntheticMargin | 0.048620 | 0.061923 |
| BranchCombinedAucpr | 0.714449 | 0.744732 |
| BranchCombinedAucroc | 0.510641 | 0.542664 |
| BranchTailOnlyAucpr | 0.822025 | 0.842969 |
| BranchTailOnlyAucroc | 0.824120 | 0.834607 |
| BranchAuxOnlyAucpr | 0.583380 | 0.619628 |
| BranchAuxOnlyAucroc | 0.272288 | 0.291531 |

## C — where the relocated attacks land

Of the 103189 attacks that leave the held-out slice under day round robin, **77670** land in training and **25519** in validation.

## D — rows and features touched by the infinity and NaN mapping

| stream | rows | numeric features | rows with +-inf | features with +-inf | rows with NaN | features with NaN | rows affected | features affected |
|---|---|---|---|---|---|---|---|---|
| Cicids | 1600000 | 84 | 4 | 2 | 0 | 0 | 4 | 2 |
| LitnetUdpFlood | 500000 | 36 | 0 | 0 | 0 | 0 | 0 | 0 |
| LitnetBlasterWorm | 500000 | 36 | 0 | 0 | 0 | 0 | 0 | 0 |
| LitnetSpam | 500000 | 36 | 0 | 0 | 0 | 0 | 0 | 0 |

## E — paired cut-by-assembly sweep

| cut | natural: detector | natural: ECOD | natural: ECOD leads | synthetic: detector | synthetic: ECOD | synthetic: ECOD leads | orderings agree |
|---|---|---|---|---|---|---|---|
| 60% | 0.483383 | 0.451502 | no | 0.395789 | 0.386564 | no | yes |
| 65% | 0.528435 | 0.498989 | no | 0.402082 | 0.385961 | no | yes |
| 70% | 0.578913 | 0.561230 | no | 0.436118 | 0.389094 | no | yes |
| 75% | 0.508857 | 0.556352 | yes | 0.477333 | 0.389087 | no | no |
| 80% | 0.585598 | 0.639969 | yes | 0.536930 | 0.400022 | no | no |
| 85% | 0.728355 | 0.758205 | yes | 0.544998 | 0.417522 | no | no |
| 90% | 0.799279 | 0.791671 | no | 0.574244 | 0.474453 | no | yes |

