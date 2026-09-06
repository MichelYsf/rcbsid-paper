# findings_bootstrap_robustness — block-length robustness of every reported interval

Generating run: `bootstrap_block_robustness_20260906T200612_b7c847e1`. Archived intervals: `referee_bounded_analyses_20260906T182158_de69afab` (block 100, p90 attack run 70, max attack run 2522). Every number is a provenance macro.

| quantity | archived, block 100 | rerun, block 100 | block 250 | block 2600 |
|---|---|---|---|---|
| FullNaturalMargin | [0.021099, 0.032692] | [0.021099, 0.032692] | [0.018042, 0.035454] | [0.001937, 0.050610] |
| FullSyntheticMargin | [0.122046, 0.130294] | [0.122046, 0.130294] | [0.121204, 0.131410] | [0.117304, 0.134710] |
| Shared240NaturalMargin | [0.053856, 0.067720] | [0.053856, 0.067720] | [0.051113, 0.070588] | [0.031124, 0.084248] |
| Shared78NaturalMargin | [0.051770, 0.064229] | [0.051770, 0.064229] | [0.048228, 0.067490] | [0.030989, 0.077495] |
| Shared240SyntheticMargin | [0.044634, 0.056329] | [0.044634, 0.056329] | [0.042866, 0.058594] | [0.026784, 0.069844] |
| Shared78SyntheticMargin | [0.048620, 0.061923] | [0.048620, 0.061923] | [0.046375, 0.064365] | [0.027819, 0.075492] |
| BranchCombinedAucpr | [0.714449, 0.744732] | [0.714449, 0.744732] | [0.704283, 0.752667] | [0.653543, 0.807028] |
| BranchCombinedAucroc | [0.510641, 0.542664] | [0.510641, 0.542664] | [0.502010, 0.552808] | [0.450625, 0.604844] |
| BranchTailOnlyAucpr | [0.822025, 0.842969] | [0.822025, 0.842969] | [0.815425, 0.848083] | [0.781947, 0.880632] |
| BranchTailOnlyAucroc | [0.824120, 0.834607] | [0.824120, 0.834607] | [0.822881, 0.836370] | [0.811981, 0.845811] |
| BranchAuxOnlyAucpr | [0.583380, 0.619628] | [0.583380, 0.619628] | [0.571799, 0.630170] | [0.519763, 0.700544] |
| BranchAuxOnlyAucroc | [0.272288, 0.291531] | [0.272288, 0.291531] | [0.268107, 0.296220] | [0.247030, 0.317353] |
| AuxAucrocMinusHalf | [-0.227712, -0.208469] | [-0.227712, -0.208469] | [-0.231893, -0.203780] | [-0.252970, -0.182647] |

Block-100 reproduction: exact to six decimals (largest absolute deviation of a bound 0.000000).

| check | block 100 | block 250 | block 2600 |
|---|---|---|---|
| FullNaturalFullMarginAboveZero | yes | yes | yes |
| FullSyntheticFullMarginAboveZero | yes | yes | yes |
| Shared240NaturalMarginAboveZero | yes | yes | yes |
| Shared78NaturalMarginAboveZero | yes | yes | yes |
| Shared240SyntheticMarginAboveZero | yes | yes | yes |
| Shared78SyntheticMarginAboveZero | yes | yes | yes |
| AuxBelowChanceEntireInterval | yes | yes | yes |
| TailAboveDeployedAucpr | yes | yes | NO |
| TailAboveDeployedAucroc | yes | yes | yes |

Conclusion changes across block lengths 250, 2600: **1** of 18 checks.

Wall time: 2081 s.
