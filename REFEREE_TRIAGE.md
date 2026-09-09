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

**Block-length robustness (final read, 2026-09-06).** Every interval above
was recomputed from the same archived scores at block lengths 250 and 2600
records (the second longer than the longest attack run, 2,522), with block 100
rerun first as a reproduction check: exact to six decimals on all 13 intervals
(manifest `bootstrap_block_robustness_20260906T200612_b7c847e1`,
`findings_bootstrap_robustness.md`). Every margin interval stays above zero
and the auxiliary-only AUC-ROC interval stays below 0.5 at both lengths. One
of the eighteen checks changes: at block 2600 the tail-only AUC-PR interval
[0.781947, 0.880632] overlaps the deployed composition's [0.653543, 0.807028];
the AUC-ROC intervals stay disjoint. Section 12 states this in one sentence.

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

---

# Second report (2026-09-07): `report-source.md`

The second report re-examines the eleven earlier objections and adds a cold
review (3 BLOCKING, 6 MAJOR, 6 MINOR) with a reject recommendation. Every
finding was verified against the built PDF (tip d2742e1), the code and the
manifests before anything changed. Table numbers below are the report's, which
are the d2742e1 build's; the per-cut table added this round shifts later
numbers by one in the current build. Analysis run this round: E
(`findings_ecod_composition.md`, manifest
`ecod_batch_composition_20260907T061817_7d2ec490`, 131 s). Analyses not run,
with reasons: `RESPONSE_SHELF.md` entries 4 to 6.

## Cold review, BLOCKING

| # | finding (gist) | verdict | evidence | action |
|---|---|---|---|---|
| B1 | Table 6's "only the history each detector saw before scoring them differs" is false for ECOD, which is fitted on each arm's benign-only training rows; the shared-record comparison does not hold the fitted model fixed. | confirmed | `scripts/run_construction_contrast.py` line 183 fits ECOD on the benign rows of each arm's own training split; the splits differ (77,670 relocated attacks and the benign rows around them). The shared-batch analysis scored the identical batch under two fitted models (`run_referee_analyses.py`, stage A). | B: caption and Section 6.1 now say membership and prevalence are held fixed while everything upstream of scoring still varies (the detector's prefix, ECOD's training rows and, in the slice columns, its batch) and cite the two measured movements, 0.005242 AP (detector, between prefixes) and 0.002788 AP (ECOD, between fitted models on the identical shared batch); Section 12 says the same. The crossed design stays shelved (`RESPONSE_SHELF.md` 1). |
| B2 | The constant reset marginal P(r_t=0)=h follows from the Adams and MacKay recursion (same predictive on both branches, Algorithm 1), so it is not evidence of an implementation defect; and the consumed score uses P(r<=5), so the identity does not make the score data-independent. | confirmed | Read-only check of arXiv:0710.3742: Eq. 3 and Algorithm 1 steps 3 to 5 weight the changepoint branch by the previous run's predictive; the identity and the one-step lag follow from steps 4 to 8 (the paper does not state them). `src/bocpd/truncated_bocpd.py` lines 161 to 168 reproduce that recursion below the cap. The paper already said the consumed score is a function of P(r<=5). | A: Section 3.2 states the identity as a property of the published recursion (cited with its equation and algorithm), not a coding error, and states the audit finding as the description-versus-implementation mismatch; abstract and contribution 3 say "the reset posterior P(r_t=0)"; Section 9 is retitled "An Alternative Reset Formulation", every "repair" is gone, the prior-predictive reset is described as modelling the change point before x_t, all measured results kept; Table 9 heading and the Section 12 Construct clause follow. |
| B3 | The manifest id, the run name in Section 3, the public-version statement and the companion disclosure are searchable fingerprints. | confirmed for the identifiers; the two statements are kept by instruction | Grep of the d2742e1 body: `bootstrap_block_robustness_20260906T200612_b7c847e1` (Section 12) and `s3_score_threshold_verification` (Section 3 opening). | C: both replaced by "archived in the artifact". After the edit the body has zero hits for `_2026`, `T2026` and 8-hex-digit suffixes other than the two ACM CCS concept ids in the CCSXML block, which every acmart submission carries. The earlier-versions and companion statements stay as they were, by the brief. |

## Cold review, MAJOR

| # | finding (gist) | verdict | evidence | action |
|---|---|---|---|---|
| M1 | The conclusion attributes the reversal unconditionally while the body conditions it on an untested assumption. | confirmed | Conclusion sentence "attributing it to the sample the assembly selects rather than to the order it imposes" carried no clause. | D: the sentence now carries the Section 6 assumption in a clause. |
| M2 | "In size or composition" exceeds the design: the ladder varied size and content together; Figure 2 does not say which Table 6 batch it plots. | confirmed as to the ladder; the composition-only experiment was feasible and run | Ladder pads add validation records (`run_review_analyses.py`); Figure 2 caption named no batch. | E: the 78,000 shared records scored under the timestamp arm's fitted model inside two batches of identical size (240,000) and different content (the timestamp slice and the round-robin slice, differing in 162,000 records): AUC-PR 0.844487 against 0.852039, a difference of 0.007552 (AUC-ROC 0.799910 against 0.809006, 0.009096); the timestamp-slice value reproduces the Table 6 slice value exactly. Composition alone moves it, so "in size or composition" is kept and Section 6.3 states that both size and content enter through the recomputed ECDFs. Figure 2's caption says the right panel plots the slice-batch values. A size-only manipulation at fixed content is impossible by construction (`RESPONSE_SHELF.md` 6). |
| M3 | "Table 9 shows why" explains the held-out ranking with diagnostics from a disjoint 15,000-record prefix. | confirmed | Table 9 caption states the two populations; the ablation manifests declare only the findings file as output and `results/s6_ablation_arms.json` holds per-arm metrics, so no held-out per-record scores exist. | F: the sentence now says the prefix diagnostics are consistent with, not proof of, the held-out ranking, names the two populations and says the held-out scores were not archived. Recomputation shelved (`RESPONSE_SHELF.md` 4). |
| M4 | Biswas is mischaracterised: the coverage-versus-drift separation is within CSE-CIC-IDS2018 by a stratified-temporal control; cross-dataset transfer is a separate experiment; no intersected held-out set. | confirmed | Read-only read of the preprint (abstract, Sections 1, 1.2, 5.3, 6.1 to 6.3, 7; the Crossref record for 10.20944/preprints202606.0903.v1 matches the bib entry). | G: the sentence now describes a within-corpus comparison of random, stratified-temporal and class-blind chronological splits that separates unseen-attack coverage from drift, with transfer to CIC-DDoS2019 reported separately and each protocol scored on its own partition; nothing quoted. |
| M5 | Interval coverage is selective and the paper's evidentiary language does not say so. | confirmed | Intervals existed for the CICIDS contrast, shared records and branches only. | H: one Section 12 sentence names which results carry intervals and which do not (LITNET per-stream values, per-cut values, prevalence-level means, the one-stream Section 9 result) and why; LITNET intervals are not possible from archived data (`RESPONSE_SHELF.md` 5). |
| M6 | The conformal paragraph misreads the cited algorithm (an empty feasible set selects lambda_max; it does not make CRC infeasible) and gives no reproducible feasibility analysis. | confirmed | Paragraph in Section 11; no calibration details were reported. | I: paragraph deleted; `angelopoulos2024crc` and `bates2021rcps` became uncited and were removed, recorded in `BIB_AUDIT.md`. |

## Cold review, MINOR

| # | finding (gist) | verdict | evidence | action |
|---|---|---|---|---|
| m1 | The chance level is not exactly the finite-sample expectation of step-wise AP under a random permutation; Manzhos, Ianevych and Melnyk give the exact formula; Table 9 still says "floor". | confirmed | The closed form E[AP] = (m-1)/(n-1) + (H_n/n)(n-m)/(n-1) reproduces the report's four values to nine decimals (0.682365837, 0.252433107, 0.776633616, 0.161609716); the cited paper verifies (Modern Stochastics: Theory and Applications 13(3):357-374, 2026, DOI 10.15559/26-VMSTA298); its Theorem 1 gives AP at cutoff k and the full-list case is its k = n specialisation. | J: Table 2's chance-level row states that the exact expectation differs from p in the fifth decimal, prints one worked value (0.682366 against 0.682350 on the timestamp-order slice, a supplementary macro checked by a decimals relation with its own operator), cites the record, and says it changes no conclusion; Table 9's "floor" is "chance level". |
| m2 | "No coherent global timestamp order exists" overstates disjoint capture intervals. | confirmed | Section 4.2 wording. | J: "no continuous global chronology, three disjoint intervals separated by gaps of weeks", with the reason that a global order would concatenate the gaps. |
| m3 | Gurjar and Camp implement gradient-boosted classification of a 95th-percentile exceedance, not extreme-value methods. | confirmed | Read-only read of arXiv:2601.14299 (Sections 4.1 to 4.4, 6.2, 7): XGBoost per severity stratum on intensity, momentum and volatility; 30-minute horizon; EVT is related work only. | J: sentence rewritten to the implemented predictor; nothing quoted. |
| m4 | The two-arm split sweep is not auditable from the paper. | confirmed | Only three cut points were named; Figure 3 shows one arm. | J: a table of chance level and AUC-PR of both scorers in both arms at all seven cuts, with an agreement column, from the archived paired-sweep macros. |
| m5 | "Sampling uncertainty is small" is not robust to the block-2600 result. | confirmed | Section 12 reports the AP overlap at 2,600. | J: the sentence is restricted to the block lengths at which the branches' AP intervals separate (100 and 250). |
| m6 | C_FP, C_FN and the validation threshold rule are not in the protocol tables. | confirmed | `posterior_threshold(1.0, 10.0, 0.05)` in `run_construction_contrast.py`; `_threshold_from_validation` in `src/experiments/run_streaming_eval.py` maximises F1 on the validation precision-recall curve with the Bayes threshold as fallback. | J: a "decision threshold" row in Table 3 states the formula with C_FP = 1, C_FN = 10, rho = 0.05 and the printed value 0.655172, the baselines' F1 rule and its fallback, and that no threshold-dependent column is reported; "PyOD 2.0.5" added to the ECOD row. |

## Dispositions of the eleven earlier objections

1 partial (conclusion): fixed by D. 2 partial (ECOD training rows differ): B and E. 3 partial (size versus composition): E. 4 resolved with a version gap: PyOD 2.0.5 added to Table 3. 5 partial (Table 9 "floor", finite-sample chance level): J. 6, 9 and 11 resolved: no action. 7 partial (interval coverage): H. 8 mostly resolved (second arm not auditable): the per-cut table. 10 not cleanly resolved (identifiers): C.

## Analysis E in full

| batch (timestamp-arm model, 240,000 records each, sharing the 78,000 evaluated records) | AUC-PR | AUC-ROC |
|---|---|---|
| timestamp-order held-out slice (reproduces the Table 6 slice value) | 0.844487 | 0.799910 |
| day-round-robin held-out slice | 0.852039 | 0.809006 |
| difference, from reported values | 0.007552 | 0.009096 |

F and H were not run: no per-record scores are archived for the ablation's held-out slice or for any LITNET method (see the shelf).

---

# Third round (2026-09-09): eleven final-read findings

Verified against the code, the manifests and the built PDF (tip cd6cea9) before
anything changed. No analysis was run: every number printed this round already
existed in an archived manifest. Section and table numbers below are the
current build's, which is 23 pages.

## Findings and verdicts

| # | finding (gist) | verdict | evidence | action |
|---|---|---|---|---|
| 1 | Section 9's "both variants are degenerate in opposite directions: the evaluated one never resets below the cap, this variant almost always resets" contradicts Section 3.2 in both halves. | confirmed, both halves | Section 3.2 states that below the cap the reset posterior equals the hazard rate exactly, so the evaluated variant resets with probability exactly the hazard, not never. For the alternative, the ablation manifest `s6_bocpd_corrected_ablation_20260824T092655_a47acf51` records P(r=0) only as `SSixProbeCorrectedPeak` = 1.0, the peak after a 6-sigma shift on the synthetic probe; it holds no real-data P(r=0) macro, so "almost always resets" on the stream rested on nothing archived. | Replaced with the measured quantities: below the cap the evaluated variant's reset posterior is pinned at the hazard rate and carries no information from the current record; under the alternative the short-run mass saturates at `SSixDiagCorrectedMeanShortRunMass` = 1 and the score sits at the 0.25 cap on `SSixDiagCorrectedFracAtCap` = 0.9274 of records. The replacement states that P(r=0) for the alternative was recorded only on the synthetic probe and asserts nothing about how often it resets on the stream. The sweep of Sections 3, 9 and 12 found no other sentence of that kind. |
| 2 | Sections 6.1 and the conclusion state the attribution without stating what the restriction does not bound. | confirmed | The paragraph carried the assumption sentence but nothing about the scope of the demonstration itself. | Added one sentence in each place: the restriction shows that the ordering does not reverse on a sample both arms held out and that the detector's score on it moves by 0.005242 AP between histories, and it does not bound history's effect on comparisons between shared and unshared records, which the full-slice AP also contains. **"Attributable to" was kept.** Reason: the phrase is followed immediately by the assumption sentence and now by the limitation sentence, so the claim is conditioned in the same breath and the reader is told exactly which comparison is unbounded. Weakening it further would understate a result that does hold on the shared sample, which is the opposite error. |
| 3 | The four-point batch ladder is asserted but not printed, so the 0.006966 span and the non-monotonicity cannot be audited from the page. | confirmed | Only the first and last rungs appeared in the prose. | All four rungs printed with their definitions, from the archived macros: 240000 records (the evaluated slice alone) 0.758205, 300000 0.760029, 360000 0.762108, and 480000 (validation plus test) 0.755142. The construction matches `scripts/run_review_analyses.py`, whose pads are 0, 60000, 120000 and the full validation length. The span is now the reader's own subtraction, and the shape (up, up, down) is visible. |
| 4 | "Standard vague hyperparameters" does not specify the alternative's prior. | confirmed | The prose gave nu and the scale but not the location, the floor or the hyperparameters. | The specification now prints, from `_prior_predictive_nll`: a Student-t centred at the running global mean, nu = 2 degrees of freedom, squared scale twice the running global variance floored at 1e-4, with kappa0 = 1, alpha0 = 1 and beta0 the global variance, giving nu = 2*alpha0 and squared scale (beta0/alpha0)(1 + 1/kappa0). "Standard vague hyperparameters" is gone. |
| 5 | Section 5.2's "not because attacks are redistributed" contradicts the relocation counts three lines above. | confirmed | The same paragraph reports 77,670 attacks relocated into training and 25,519 into validation, which is a redistribution of attacks. | Reworded so both describe one event: prevalence falls because attack-free rows from the four other days enter the held-out slice and displace Friday attack rows, which is the same movement the relocation counts report. |
| 6 | "Each computed from the reported cells above" does not name its table. | confirmed | The nearest preceding table cells are Table 6's, but the reference was positional. | Names Table 6 by label. |
| 7 | Section 8 claims the additive and normalized forms peak at different levels while printing only the normalized ones. | confirmed, and the claim is true | Additive lift runs 0.317640, 0.348209, 0.292602, 0.094222, -0.020445 and peaks at the 10 percent level; normalized runs 0.334190, 0.386471, 0.391386, 0.157035, -0.056790 and peaks at the unresampled level. | Both families printed through the macro layer, so the claim is now checkable on the page. |
| 8 | "The specification is silent" is too categorical: the ECOD paper's Section IV-D speaks to new data points. | confirmed | Read against arXiv:2201.00382. Section IV-D is the preprint's Section 4.4, whose closing paragraph states that ECOD requires no re-training to fit new data points, with two stated conditions: a relatively large sample and no assumed data shift. The paper nonetheless defines its scores for the rows of the input matrix (Algorithm 1 takes X and returns one score per row) and states no rule for scoring a new record with the fitted per-dimension ECDFs held fixed. | Reconciled and narrowed: the paper is not silent on new records, its Section IV-D is cited with both conditions, and what is identified as absent is the rule for scoring an out-of-sample record without recomputing the ECDFs over the concatenation. The sentence now says the specification is silent at exactly the point where the batch enters, rather than silent outright. |
| 9 | Calling the implemented cutoff a Bayes rule for this score is unwarranted. | confirmed | `update_score` returns max(chi-square tail CDF, 0.25 * P(r<=5)) clipped to [0,1], which is not a class posterior, so Elkan's formula has no optimality warrant on it. | Section 3.3 now says the earlier implementation applied Elkan's prior-inclusive formula to a score that is not a class posterior, so the cutoff carries no Bayes-optimality warrant for it, records this as an audit observation and not a defect claim, and states that the ranking metrics are unaffected. The two other places that called it a Bayes rule, the Related Work sentence and the Table 3 decision-threshold row, were made consistent. |
| 10 | The chronology claim is attributed to LITNET-2020 as a whole. | confirmed as to scope; the claim itself is true and archived | Verified against the dataset paper (DOI 10.3390/electronics9050800): collection ran 6 March 2019 to 31 January 2020, about ten months, and twelve attack types are annotated, so attributing a finding drawn from three attack-type captures to the dataset as a whole overreaches. The disjointness itself holds and is archived: `findings_streams.md`, the Stage 1 output, records the capture dates (udp_flood 2019-03-06, spam 2019-12-09 to 2020-01-06, blaster_worm 2020-01-25), and each released stream carries a per-record timestamp column whose SHA-256 the Stage 1 manifest pins; the three windows do not overlap and the gaps are weeks and months. What the dataset paper does not support is the attribution: it describes two capture periods and never describes per-attack-type captures. | Section 4.2 is scoped to the three captures this paper evaluates and states the claim as this paper's own: they do not overlap in time, they are separated by gaps of weeks and months, and their spans are the 3.97, 1.62 and 39122.23 minutes Table 1 records, so a global timestamp order over them would concatenate three intervals rather than describe one observed stream. It then says no chronology claim is made about LITNET-2020 as a whole, which was collected over about ten months and annotates twelve attack types. The introduction cited the dataset paper for the disjointness; it now cites it only for the span and the attack-type count and attributes the disjointness to this paper. The abstract is unchanged. |
| 11 | "Repetition" varies across draws, which contradicts Table 3's "no duplicates". | confirmed | `scripts/prevalence_lib.py` draws without replacement and returns sorted unique indices, so no record repeats within a draw. | Reworded to what does vary: which records are retained, how many there are, and how far apart in the stream the retained ones sit. |

## Two further defects found while verifying finding 10, and fixed

- The introduction asserted that LITNET-2020's captures are temporally disjoint and cited the dataset paper for it. The paper does not support that, so the sentence now states what the paper does support, twelve attack types over about ten months, and attributes the span observation to this paper's own measurement.
- The abstract twice called the captures "temporally disjoint". Since no start times are archived and the source does not say it, both were changed to "separate", which changes no claim the paper makes. The two operator abstract copies were updated in step and re-verified against the built abstract.

## A correction made inside this round

The first revision of finding 10 went too far. It removed the disjointness
claim as well as the misattribution, on the premise that no start or end
timestamp is archived in this project, and replaced it with a sentence saying
that a timestamp order over the three captures would interleave them. Both
halves were wrong. `findings_streams.md` archives the capture dates, and the
released streams carry a timestamp column the Stage 1 manifest pins by hash,
so the disjointness was always checkable here; and because the three windows
do not overlap, a timestamp sort concatenates them and interleaves nothing.
The pre-commit verification pass caught it by scanning the timestamp column of
the three pinned stream files directly. Section 4.2 now states the claim the
archive supports, scoped to the three captures, and this record keeps the
error rather than hiding it.

## Residues reported and deliberately not fixed

Three shipping documents still carry the "both variants are degenerate in
opposite directions, the evaluated one never resets, this one always resets"
framing that finding 1 removed from the manuscript.

- `findings_bocpd_ablation.md` and `findings_contributions.md` are archived run
  outputs whose SHA-256 values are recorded as manifest outputs (the 27 August
  ablation run and the Stage 5 contributions run respectively). Editing either
  would break a recorded output hash and require re-running, which this round's
  bound excludes.
- `SCOPE_DECISIONS.md` carries it in the Stage 6 narrative. It is the project's
  historical record of binding rules and corrected incidents, and this project's
  standing rule is that history is recorded rather than rewritten, so it is left
  for the operator to decide whether to add a correction entry.

`README.md` carried the same framing plus an unqualified "equals the hazard
rate for any data"; it is hand-maintained, is the first thing a reader of the
artifact sees, and was corrected in this round to state the cap qualifier and
the current framing.

# Fourth round (2026-09-09): the two generator residues, regenerated

The previous round left `findings_bocpd_ablation.md` and
`findings_contributions.md` carrying the retired framing, on the reasoning that
editing either would break a recorded manifest output hash and that re-running
was outside that round's bound. That reasoning was half right. Editing the
*documents* would indeed break their recorded hashes; editing their
*generators* and re-running them does not, because a run writes a fresh
manifest that records the new hash. CI-27 states the rule directly: editing a
generator is not a fix, running it is.

Both generators could regenerate from archived data with no new detector run:

- `scripts/verify_contributions.py` reads run manifests and the macro index
  only, so it recomputes nothing.
- `scripts/run_bocpd_ablation.py` reuses the arm metrics from
  `results/s6_ablation_arms.json` whenever the cached prefix length matches,
  emits the arm macros from that cache with `SSixArmsRecomputed` = 0, and by
  design claims no stage wall time on that path (CI-24), so the run measures no
  arm. Its saturation diagnostic over the first 15,000 records is deterministic
  and was recomputed, as it is on every run.

The retired framing was replaced in both generators with the wording the
manuscript now uses: the two variants are degenerate in different quantities,
each stated in the quantity that was measured; below the run-length cap the
evaluated detector's reset posterior is pinned at the hazard rate, a property
of the published recursion rather than a coding error; under the alternative it
is the short-run mass that saturates; and `P(r=0)` for the alternative was
measured only on the synthetic probe, so nothing is asserted about how often it
resets on the stream. The Stage 6 sentence that called the alternative's score
"constant on most records" was corrected in the same edit, because the
manuscript states the opposite and the archived standard deviation supports the
manuscript.

Both generators were then run. New manifests
`s6_bocpd_corrected_ablation_20260909T060039_7766d5ff` and
`s5_verified_contributions_20260909T060341_6108db2a` record the new document
hashes. Neither run changed a macro value: the three Stage 6 manifests agree on
all 27 shared macros, the two Stage 5 manifests agree on all 16, and
`paper/numbers.tex` regenerated to the same 799 macros with no value changed,
only the provenance attribution comments moving to the new run ids.

`SCOPE_DECISIONS.md` still carries the retired framing in its Stage 6 narrative
and is deliberately untouched; it is the historical log, and this project
records history rather than rewriting it. One further residue was found and
fixed in this round: `CLAIM_LEDGER.md` entry I13 abbreviated the introduction
sentence with the retired framing, which the manuscript no longer says. The
gist now matches the manuscript.
