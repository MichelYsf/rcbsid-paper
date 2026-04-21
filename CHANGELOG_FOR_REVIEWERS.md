# Reviewer-Facing Change Log

## Critical fixes

1. Replaced unfair main baselines with real online streaming baselines.
2. Added Kitsune/KitNET and HS-Trees as non-negotiable baselines.
3. Moved LOF, ECOD, and COPOD to batch-reference status only.
4. Added LITNET-2020 as the third dataset.
5. Replaced original CICIDS2017 with the Engelen-corrected version.
6. Added chronological 70/15/15 splits with five fixed seeds.
7. Added Wilcoxon signed-rank testing with Holm-Bonferroni correction.
8. Added latency, calibration, throughput, and burn-rate analysis.
9. Removed unsupported O(1) claim.
10. Added O(kd) complexity statement with explicit run-length truncation.
11. Reframed contribution as SLO-aware operational thresholding.

## Required before submission

Do not submit until tables contain real numbers generated from the three datasets. No fabricated metrics should be inserted.
