# REFEREE_TRIAGE — bounded triage of the hostile referee report, 2026-09-06

Report: `hostile_referee_report.pdf` (5 pages, "Hostile Referee Report — ACM
Digital Threats: Research and Practice", written against the manuscript built
at commit `ad01b8b`). Its arithmetic audit found no recomputed discrepancy;
its findings are about design, terminology, protocol completeness and
anonymity. Every finding below was verified against the built PDF, the code
the manifests pin, and the archived manifests before anything was changed.
Verdicts: **confirmed** (the finding is correct as stated), **refuted** (the
finding is not correct; recorded, not fixed). Actions are bounded by the
round's brief: archived data only, no detector reruns, no new claims beyond
what the brief authorises.

Table and section numbers in the finding rows are those of the build the
referee read (ad01b8b). In the current build the protocol table is split into
Tables 2 and 3 (Table 2 grew past one page with the added rows), so every
later table number is one higher: the referee's Table 5 is now Table 6, and so
on.

The analyses run for this round are in `findings_referee_analyses.md`,
manifest `referee_bounded_analyses_20260906T182158_de69afab` (1,427 s wall,
seed 11, inputs: both archived score dumps and the four archived stream CSVs).
Analyses asked for and not run are in `RESPONSE_SHELF.md`.

## BLOCKING

| # | finding (gist) | verdict | evidence | action |
|---|---|---|---|---|
| B1 | "is produced by which records the assembly places in the test set" (§6.1) contradicts "it does not decompose the remaining factors, and a factorial design still would" (§Threats); the post-hoc intersection leaves history different and selects a non-random 0.776603-prevalence subset, so it cannot identify membership as the cause without a crossed design. | confirmed | Both quoted sentences are in the ad01b8b PDF (pp. 10 and 16). The shared records are the intersection of the two held-out slices, prevalence `RevSharedPrevalence` = 0.776603; the detector remains prequential, so the two rows of Table 5 differ in history (the paper's own second caution). Nothing in the archived design crosses history with sample. | Text 1: §6.1 and the abstract say *attributable to*, and state the assumption the attribution rests on (history contributes no more on the unshared records than on the shared ones). Threats and the Conclusion aligned to *attributes*. The crossed design is shelved: it scores records the other arm trained on (`RESPONSE_SHELF.md` §1, with the 77,670/25,519 destination counts of analysis C). |
| B2 | Table 5's ECOD values are scored in each arm's 240,000-record held-out batch; the two batches have different membership, so equal size does not control composition and the Table 5 ECOD comparison does not isolate history. | confirmed | `scripts/run_review_analyses.py` scores `Xa[i_va:]` per arm (240,000 records, 78,000 shared) and restricts afterwards; the 162,000 non-shared records differ between arms by construction (`CicidsHeldoutOverlap` = 78,000 of 240,000). | Analysis A: the 78,000 shared records rescored as their own batch under each arm's fitted ECOD. Table 5 now carries both batches per arm; §6.1 and §6.3 state which batch each ECOD number carries; the "fixed batch size" sentence in §6.3 is corrected (composition differs; cross-arm ECOD comparisons are batch-controlled only where the rescoring makes them so). Result: the detector leads under both batches (§A below). |
| B3 | §11 names which measurements are shared with the earlier public versions (pooled LITNET composite, assembled CICIDS arm), a deanonymisation recipe. | confirmed | ad01b8b PDF p. 16, lines 783–794, as quoted. | Text 8: §11 keeps that earlier versions exist and that a full account goes to the editors, and no longer names which measurements are shared, which are new, or which are withdrawn. The editor note (`packages/dtrap/EDITOR_NOTE.txt`, `PRIOR_APPEARANCE_EDITOR_NOTE.md`) is unchanged and carries the full table. The named arXiv variant states the detail in full (`scripts/build_arxiv_variant.py`). |
| B4 | The companion-manuscript disclosure (shared codebase, precise relationship, verification date 27 August 2026, "submission system of record") is a second identity fingerprint. | confirmed | ad01b8b PDF p. 17, lines 875–883, as quoted. | Text 8: the disclosure drops the exact date and the system-of-record phrase; it keeps that the companion is a public preprint not under review anywhere. The editor note is unchanged and carries the verification account. |

## MAJOR

| # | finding (gist) | verdict | evidence | action |
|---|---|---|---|---|
| M1 | The batch ladder changes which records accompany the evaluated set, not only how many; size and composition are confounded, so "not comparable across studies that score different batch sizes" overstates a size-only effect. | confirmed | The ladder pads the 240,000 test records with 0, `RevEcodBatchLadder1`−240,000, `RevEcodBatchLadder2`−240,000 and all validation records (`scripts/run_review_analyses.py`, `pads = [...]`); each pad adds records, so composition changes with size. | Text 2: "batch size" becomes "batch, in size or composition" wherever the cross-study consequence is stated (abstract, contribution 5, §6.3), and the §6.3 measurement sentence says the accompanying records vary "in number and therefore in composition". |
| M2 | No confidence interval; an event-block or rolling-origin procedure is named as the right instrument and not applied. | confirmed | Threats, ad01b8b PDF p. 16, lines 819–823, as quoted. | Analysis B: moving-block bootstrap, block length 100 records (> p90 attack run 70), 1,000 resamples, 2.5th/97.5th percentiles, over the archived per-record scores in stream order. Every interval is reported (§B below) and printed in §5.3(iii), §6.1, §7 and Threats. No interval crosses zero, so no wording changes from *reversal* to *reversal in point estimate*. Rolling-origin is stated as not applied. |
| M3 | The split sweep varies the cut in the timestamp-ordered arm only; the assembly contrast is supported at one positional boundary. | confirmed | `RevSplitCut*` macros exist for the natural arm only (`scripts/run_review_analyses.py`). | Analysis E ran (within the three-hour bound; the whole A–E run took 1,427 s): both arms at the same 7 cuts, ECOD refit at each. Orderings differ at 3 cuts (75 %, 80 %, 85 %) and agree at 4 (60 %, 65 %, 70 %, 90 %), where the detector leads in both arms; the detector leads in the day-round-robin arm at every cut. Stated in §6.2. |
| M4 | Flow-wise AP lets a 2,522-record incident outweigh a one-record incident 2,522:1; no event/range-based sensitivity; Tatbul et al. (NeurIPS 2018) absent. | confirmed | Table 2 metric row names `average_precision_score` only; `references.bib` had no Tatbul entry. | Text 5: `tatbul2018precision` added (DBLP conf/nips/TatbulLZAG18, pp. 1924–1934; proceedings.neurips.cc) and cited at the metric row with one sentence: flow-wise AP is the convention of the compared work and event-based evaluation is future work. Shelved with reason in `RESPONSE_SHELF.md` §2. |
| M5 | Table 2 omits the HST, LODA, LOF and ECOD hyperparameters, the feature count, the Gaussian adaptation rule, and the resampling and seed procedure, so "self-contained" is false. | confirmed | ad01b8b Table 2 rows as listed in this file's history; none of the named items was present. | Text 3: rows added, every value read from code: `src/baselines/hst.py` (river HalfSpaceTrees behind MinMaxScaler, 25 trees, height 15, window 250), `src/baselines/loda.py` (100 unit-norm projections, 32 bins, window 512, running standardisation), `src/baselines/batch.py` (LOF 35 neighbours, novelty, contamination auto, −score_samples min–max scaled; ECOD PyOD defaults, min–max scaled; both fitted on benign-only rows per `scripts/run_construction_contrast.py`), `src/bocpd/truncated_bocpd.py` (diagonal Gaussian, Welford mean/M2 after every record, variance floor 1e-4, χ²_d CDF tail score on pre-update global statistics, zero during warm-up, per-run-length statistics by the same recurrence), `scripts/prevalence_lib.py` (stratified per split segment, thinning rules, order preserved, 1 pp tolerance, ≤ 20 redraws at seed + 100000·attempt), seeds 11/23/47 (`run_prevalence_sweep.py`, `run_construction_contrast.py`: method seed = resample seed; contrast seed 11 with HST at 23 and 47). Feature counts as macros (84; 36, 36, 36). |
| M6 | "The mechanism is identified and is not statistical" is not established by one deterministic value on one correlated slice, given the paper's own concession of sampling uncertainty. | confirmed | §7 sentence as quoted; no interval existed. | Text 6: the sentence now says the mechanism is identified on this slice with its sampling uncertainty stated: auxiliary AUC-ROC 0.281890, interval [0.272288, 0.291531], entirely below 0.5. The max-governs-rank sentence now says the maximum sets the record's score and the rank follows from all scores together (abstract and contribution 4 echoes aligned). |
| M7 | "103,189 attacks relocated into training" is unsupported: the held-out counts show they leave the test slice, not that all enter training. | confirmed | `CicidsAttacksMovedOutOfHeldout` is derived from held-out counts only. | Analysis C from the archived splits: 77,670 land in training, 25,519 in validation (total asserted equal to 103,189). Stated in §5.2. |
| M8 | Prevalence is a no-skill reference level, not a floor: the 64 % sweep row reports detector AP 0.619546 below the 0.639991 "floor". | confirmed | Table 7, 64 % row, in the ad01b8b PDF; `STwoLSixtyFour...` macros. | Text 4: "chance floor" is "chance level" throughout prose, captions, table headers (both generated tables relabelled from their pinned runs) and figure legends (figures regenerated). Table 2 keeps one sentence that prevalence is the expected AP of an uninformative ranking, not a lower bound, and a ranking can fall below it. Macro *names* containing `ChanceFloor` are identifiers and are unchanged. |
| M9 | Gama, Sebastião and Rodrigues (Machine Learning 90, 2013), the foundational treatment of prequential evaluation, is not cited. | confirmed | `references.bib` had no Gama 2013 entry. | Text 5: `gama2013prequential` added (Crossref, DOI 10.1007/s10994-012-5320-9, 90(3):317–346) and cited at the prequential protocol (Table 2, update-timing row). |
| M10 | Neither the affected row/feature counts nor an ablation of the infinity/NaN mapping is reported. | confirmed | Table 2 stated the rule only. | Analysis D from the archived streams: CICIDS2017 4 of 1,600,000 rows, 8 infinite cells in 2 of 84 features, no NaN; each LITNET stream 0 of 500,000 rows. Counts in Table 2. The ablation is shelved with reason (`RESPONSE_SHELF.md` §3). |

## MINOR

| # | finding (gist) | verdict | evidence | action |
|---|---|---|---|---|
| m1 | "proposes no detector" alternates with "proposed detector". | confirmed | Table 3 caption and both generated table headers used "proposed". | Text 5: "evaluated detector" everywhere: the caption, and both generated tables rewritten from their pinned runs with the generator's new labels (`--relabel-table`, no manifest written, no number re-derived). Macro names containing `Proposed` are identifiers and unchanged. |
| m2 | 0.01099 is printed to five decimals against the six-decimal policy. | refuted | `SThreePrZeroTruncatedMean` is the mean of the posterior P(r=0), a probability, not a metric: binding rule 9 and Table 2 define the six-decimal family as AUC-PR, AUC-ROC, chance level, prevalence, lifts and their margins, ranges and differences; the rendering layer (`provenance.is_metric`) classifies it outside that family, and it is printed as emitted. | Recorded, not fixed: the value is unchanged. Table 2's exemption list now names posterior probabilities and diagnostic fractions explicitly, so the family is stated rather than implied. |
| m3 | "measured composite spread across three seeds is a, b, c" — three draws are not a spread. | confirmed | Table 4 caption as quoted. | Text 7: "its three composite draws across seeds are". Table 2's "spreads" becomes "ranges"; Threats' "draw spread" becomes "the three draws". |
| m4 | "the round's most consequential result" — "round" undefined. | confirmed | §6.1 as quoted. | Text 7: "the paper's most consequential result". |
| m5 | "0.755142 is exactly 0.755142" is a tautology. | confirmed | Two macros with the same value printed either side of "is exactly". | Text 7: reworded to say the independent pass reproduces the arm's reported value, printing it once. |
| m6 | "the auxiliary value governs the record's rank" — the maximum governs the score; the rank depends on every other record. | confirmed | §7 sentence. | Text 6: the maximum sets the record's score and the rank follows from all scores together. |
| m7 | "the spread of every method is the resampling draw" — a draw is not a spread. | confirmed | Table 7 caption. | Text 7: "the three draws of every method differ by the resampling draw". |
| m8 | 0.9274 (and 0.004733) violate the six-decimal policy. | refuted | `SSixDiagCorrectedFracAtCap` and `SSixDiagOriginalFracAtCap` are the fraction of emitted scores lying exactly at the 0.25 cap, a diagnostic count ratio of Table 8, not an evaluation metric; both are printed at the precision they were emitted with (four significant figures), as rule 9's exemption for non-metric values provides. | Recorded, not fixed: values unchanged; the exemption is now explicit in Table 2. |

## Rubric and recommendation

The rubric's internal-validity and external-validity readings rest on B1, B2,
M2 and M3, all confirmed and all answered above by analysis rather than by
wording. "Major revision" is not disputed; this round is the bounded part of
it that runs from archived data.

## Analysis A — ECOD on the shared records, batch-controlled (referee B2)

The 78,000 shared records scored as their own batch under each arm's fitted
ECOD model (benign-only training rows of that arm, PyOD defaults), beside the
existing values from each arm's 240,000-record held-out batch.

| arm | ECOD AUC-PR, slice batch (240,000) | ECOD AUC-PR, shared batch (78,000) | ECOD AUC-ROC, slice | ECOD AUC-ROC, shared | detector AUC-PR | margin det − ECOD, slice | margin det − ECOD, shared |
|---|---|---|---|---|---|---|---|
| timestamp order | 0.844487 | 0.847585 | 0.799910 | 0.802003 | 0.905613 | 0.061126 | 0.058028 |
| day round robin | 0.849842 | 0.844797 | 0.805657 | 0.797670 | 0.900371 | 0.050529 | 0.055574 |

The detector leads in both arms under both batches. ECOD's batch-controlled
AUC-PR differs between the two fitted models by 0.002788. Reproduction checks
inside the same run: ECOD on each arm's full validation-plus-test batch gives
0.755142 (timestamp order) and 0.418966 (day round robin), the archived
contrast values exactly.

## Analysis B — event-block bootstrap (referee M2)

Moving-block bootstrap over the archived per-record scores of the evaluated
slice in stream order; block length 100 records (p90 attack run 70, max
2,522), 1,000 resamples, seed 11, 2.5th and 97.5th percentiles. Full-slice
margins are on each arm's 240,000-record held-out slice; shared-record margins
on the 78,000 shared records in stream-position order; branch values on the
timestamp-ordered held-out slice.

| quantity | point (reported values) | 2.5 % | 97.5 % | crosses zero / chance |
|---|---|---|---|---|
| §5.3 timestamp order, ECOD − detector AUC-PR | 0.026805 | 0.021099 | 0.032692 | no |
| §5.3 day round robin, detector − ECOD AUC-PR | 0.126032 | 0.122046 | 0.130294 | no |
| Table 5 timestamp order, detector − ECOD, slice batch | 0.061126 | 0.053856 | 0.067720 | no |
| Table 5 day round robin, detector − ECOD, slice batch | 0.050529 | 0.044634 | 0.056329 | no |
| Table 5 timestamp order, detector − ECOD, shared batch | 0.058028 | 0.051770 | 0.064229 | no |
| Table 5 day round robin, detector − ECOD, shared batch | 0.055574 | 0.048620 | 0.061923 | no |
| Table 6 deployed composition AUC-PR | 0.728355 | 0.714449 | 0.744732 | — |
| Table 6 deployed composition AUC-ROC | 0.526623 | 0.510641 | 0.542664 | — |
| Table 6 tail term only AUC-PR | 0.831832 | 0.822025 | 0.842969 | — |
| Table 6 tail term only AUC-ROC | 0.829281 | 0.824120 | 0.834607 | — |
| Table 6 auxiliary term only AUC-PR | 0.600270 | 0.583380 | 0.619628 | — |
| Table 6 auxiliary term only AUC-ROC | 0.281890 | 0.272288 | 0.291531 | entirely below 0.5 |
| auxiliary AUC-ROC − 0.5 | −0.218110 | −0.227712 | −0.208469 | no |

The §5.3 point values are the arithmetic on the reported contrast cells
(`SFourCicidsNaturalEcodMinusDetectorAucpr`,
`SFourCicidsSyntheticDetectorMinusEcodAucpr`, emitted by
`emit_supplementary_macros.py` from the pinned deliverables manifest); the
bootstrap's own point on the timestamp-ordered slice is 0.026787, because the
archived dump reproduces that arm's detector AUC-PR to 1.8e-05 (a known
cross-platform delta, `RevReproNaturalDelta`). The tail-only and deployed
intervals do not overlap on either metric.

## Analysis C — relocation destinations (referee M7)

Of the 103,189 attacks that leave the held-out slice under day round robin,
77,670 land in training and 25,519 in validation (sum asserted equal to
`CicidsAttacksMovedOutOfHeldout`).

## Analysis D — imputation counts (referee M10)

| stream | rows | numeric features | rows with ±∞ | features with ±∞ | infinite cells | rows with NaN | rows affected |
|---|---|---|---|---|---|---|---|
| CICIDS2017 | 1,600,000 | 84 | 4 | 2 | 8 | 0 | 4 |
| LITNET udp_flood | 500,000 | 36 | 0 | 0 | 0 | 0 | 0 |
| LITNET blaster_worm | 500,000 | 36 | 0 | 0 | 0 | 0 | 0 |
| LITNET spam | 500,000 | 36 | 0 | 0 | 0 | 0 | 0 |

## Analysis E — paired cut-by-assembly sweep (referee M3)

Both arms at the same 7 cuts, detector scores from the archived dumps, ECOD
refit at each cut on that arm's benign-only prefix and scored on the tail.

| cut | timestamp order: detector / ECOD | ECOD leads | day round robin: detector / ECOD | ECOD leads | orderings agree |
|---|---|---|---|---|---|
| 60 % | 0.483383 / 0.451502 | no | 0.395789 / 0.386564 | no | yes |
| 65 % | 0.528435 / 0.498989 | no | 0.402082 / 0.385961 | no | yes |
| 70 % | 0.578913 / 0.561230 | no | 0.436118 / 0.389094 | no | yes |
| 75 % | 0.508857 / 0.556352 | yes | 0.477333 / 0.389087 | no | no |
| 80 % | 0.585598 / 0.639969 | yes | 0.536930 / 0.400022 | no | no |
| 85 % | 0.728355 / 0.758205 | yes | 0.544998 / 0.417522 | no | no |
| 90 % | 0.799279 / 0.791671 | no | 0.574244 / 0.474453 | no | yes |

## Bibliography

Both additions verified against a registrar before entry (`BIB_AUDIT.md`,
"Additions (2026-09-06)"): Gama, Sebastião and Rodrigues 2013 via Crossref
(DOI 10.1007/s10994-012-5320-9); Tatbul et al. 2018 via DBLP
(conf/nips/TatbulLZAG18, pp. 1924–1934) and the NeurIPS proceedings page.
NeurIPS 2018 papers carry no Crossref DOI, so none is entered.
