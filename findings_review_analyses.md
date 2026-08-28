# findings_review_analyses — A1, A2, A3 (fresh-review round)

Generating run: `review_bounded_analyses_20260827T131839_87899899`. Every number is a provenance macro.

## Reproduction check

Recomputing the archived arms from these dumps gives detector AUC-PR **0.728355** (natural) and **0.544998** (synthetic) against the archived 0.728337 and 0.544998. The synthetic arm reproduces exactly; the natural arm differs by 1.79e-05. That arm's archived value was produced on Linux and this pass ran on Windows, and a cross-platform difference of this order in the detector was already measured and recorded for this pipeline (corrected incident CI-16, 2.8e-07 per value); AUC-PR aggregates a ranking, so near-ties can reorder. The dumps reproduce the runs they are meant to explain, to that stated tolerance.

## A1 — the same records, both arms

The two held-out slices share **78000** records (prevalence 0.7766, 60575 attacks). Restricting both arms to exactly those records and recomputing:

| arm | detector AUC-PR | ECOD AUC-PR | detector AUC-ROC | ECOD AUC-ROC |
|---|---|---|---|---|
| natural | 0.905613 | 0.844487 | 0.869219 | 0.799910 |
| synthetic | 0.900371 | 0.849842 | 0.864159 | 0.805657 |

**Verdict (mechanical): the ordering inversion DOES NOT SURVIVE on the identical record sample.**

The scores still differ between arms because the detector is prequential: the same record is scored after a different history in each arm. What this isolates is the effect of that history on the same evaluated records, with membership and prevalence held fixed.

## A2 — split sensitivity (natural arm)

| test starts at | test records | prevalence | detector AUC-PR | ECOD AUC-PR | ECOD > detector |
|---|---|---|---|---|---|
| 60% | 640000 | 0.3501 | 0.483383 | 0.451502 | no |
| 65% | 560000 | 0.4000 | 0.528435 | 0.498989 | no |
| 70% | 480000 | 0.4616 | 0.578913 | 0.561230 | no |
| 75% | 400000 | 0.4290 | 0.508857 | 0.556352 | yes |
| 80% | 320000 | 0.5131 | 0.585598 | 0.639969 | yes |
| 85% | 240000 | 0.6824 | 0.728355 | 0.758205 | yes |
| 90% | 160000 | 0.7163 | 0.799279 | 0.791671 | no |

ECOD exceeds the detector at **3 of 7** cut points.

## A3 — which branch discriminates (natural held-out slice)

| scoring branch | AUC-PR | AUC-ROC |
|---|---|---|
| Combined | 0.728355 | 0.526623 |
| TailOnly | 0.831832 | 0.829281 |
| AuxOnly | 0.600270 | 0.281890 |

**Verdict (mechanical, threshold 0.01 AUC-PR):** tail-only does NOT reproduce the combined score, so the claim that the tail term performs the discriminative work of the deployed score is NOT SUPPORTED.

The direction matters and is not the one the objection anticipated. Tail-only does not merely differ from the combined score, it **outranks** it: +0.103477 AUC-PR and +0.302658 AUC-ROC better. The auxiliary branch ranks *below* chance on this slice (AUC-ROC 0.281890), and because the deployed score is a maximum, that branch overrides the tail wherever the tail is small. The composition, not either component, is what produces the near-chance ranking of the deployed detector on this slice.

## A4 — ECOD scores depend on the batch they are scored in

Model fitted once on the same benign training rows; the evaluated index set is the same **240000** records in every row below. Only the number of records accompanying them in the `decision_function` call changes.

| scored batch | evaluated records | ECOD AUC-PR |
|---|---|---|
| 240000 | 240000 | 0.758205 |
| 300000 | 240000 | 0.760029 |
| 360000 | 240000 | 0.762108 |
| 480000 | 240000 | 0.755142 |

Scoring the identical records alone rather than alongside the validation block moves ECOD's AUC-PR by **0.003063**; the full ladder spans 0.006966. This is not run-to-run noise — ECOD is deterministic and the fitted model is byte-identical across these rows.

