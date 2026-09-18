# RESPONSE_SHELF — prepared answers for anticipated objections

Each entry: the objection as a referee would put it, the prepared response,
and the evidence line. Responses are written to be pasted into an author
reply with minimal editing. New shelf items from the fresh round get appended
under "From the fresh round".

## S1. "Three of the tuned finals are missing; the tuning study is incomplete."

**Response.** Correct, and stated in the artifact rather than smoothed over:
the prior tuning campaign completed 11 of 14 finals before its compute cap
(CI-4 scopes those results to the synthetic protocol). The three missing
cells are LITNET kitnet-tuned, LITNET lof-tuned re-run, and CICIDS
iforest\_asd-tuned. Bounded revision-window cost to complete them locally,
measured from the archived per-row rates: approximately 6–9 hours of
single-machine compute. We will run them within a revision window if the
referees judge them load-bearing; we note they belong to the *synthetic
protocol* line (binding rule 3), so they cannot alter the paper's central
claim, which is construction-versus-construction, not method-versus-method.
**Evidence:** `findings_tuning.md`, `SCOPE_DECISIONS.md` CI-4,
`results/tuning_parts/`.

## S2. "Single-seed results are not results."

**Response.** We agree, and the paper enforces exactly that: binding rule 7
forbids flat comparative claims for any stochastic method from a single
seed. Where we bought additional seeds, the HST/ECOD ordering flipped in 2
of 2 cells — which is why every flat claim in the paper is between
deterministic methods, where seeds cannot move anything: the evaluated
detector against ECOD in the assembly contrast, and against LOF at the
unresampled level of the prevalence sweep (Section 8). Every HST number
appears either as a single draw marked as such, with no placement asserted,
or as a mean over three draws with the per-draw values archived (Section 11). Extending every cell to ≥3 seeds costs
roughly 1.5 h per HST cell locally; the four uncovered cells total ~6 h and
we will run them within a revision window on request. No conclusion of the
paper rests on a stochastic placement. **Evidence:** `SCOPE_DECISIONS.md`
rule 7 and CI-10/CI-16; `findings_contrast.md` seed-sensitivity section.

## S3. "Why retain the composite construction at all if it is invalid?"

**Response.** Because it is the construction the literature (and our own
prior version) actually evaluates, and deleting it would remove the paper's
control arm. It is retained as an explicitly labeled synthetic protocol,
never as a deployment claim (binding rules 2 and 3): the synthetic arms
reproduce the archived prior evaluations exactly (LITNET pooled 225,000
flows / 14,621 attacks; CICIDS interleaved 60,575 attacks), which is what
makes the contrast a measurement of the construction rather than a strawman.
The alternative — comparing natural order against nothing — would assert the
construction effect without measuring it. **Evidence:**
`findings_contrast.md`; `AUDIT_FINDINGS.md` A13.

## S4. "The detector is known art; where is the contribution?"

**Response.** The paper claims no new detector. Section 3 characterizes the
evaluated detector as the code implements it: the score is the maximum of a
chi-square tail term under a global, slowly adapting diagonal Gaussian and
0.25·P(r≤5); below the run-length cap the reset posterior equals the hazard
exactly, a property of the published recursion rather than a coding error,
and at and beyond the cap it wanders. The contribution is (a) the assembly
contrast on identical records, with its membership and dilution mechanism
measured; (b) the pooling identity, offered as an audit check; (c) the
method-identity audit, scoped to this implementation: the described score is
not the evaluated score; (d) the composition defect of Section 7, where the
deployed score ranks worse than its own tail term; and (e) the ECOD batch
dependence of Section 6.3. Appendix A reports one untuned alternative reset
formulation, degenerate in a different quantity, and draws no conclusion
about tuned variants. DTRAP's scope includes evaluation practice for
operational detection; that is the lane this paper occupies. **Evidence:**
`findings_score_threshold.md`, `findings_review_analyses.md`,
`findings_ecod_composition.md`, `findings_bocpd_ablation.md`; Sections 3,
6.3 and 7 and Appendix A of the manuscript.

## S5. "The natural-order test slice is one 204-minute window; that is not an
evaluation."

**Response.** It is what true chronology on this benchmark yields under a
fixed chronological split, and the paper states it prominently rather than
engineering around it — because engineering around it (reordering,
resampling, interleaving) is precisely the construction step under study.
The narrowness of the natural test window is what a positional chronological
split yields on this budgeted subsample, stated rather than engineered around
(Section 11); the paper presents no ordering as a stable property of
CICIDS2017 (Section 6.2), and constructions that appear to fix the window
change the operating point instead. We agreed a split-rule sensitivity
analysis was the right next step, and it has since been run: A2 sweeps seven
chronological cuts from 60% to 90% and finds ECOD ahead of the detector at
three of them, including the cut this paper uses. The narrowness of the
window stands; the claim that no such check exists does not, and has been
withdrawn wherever it appeared. **Evidence:**
`findings_contrast.md`; `findings_review_analyses.md` A2; manifest
`cicids_heldout_composition_*`; Section 6.2, Table 7 and Figure 3 (the
sweep); Section 11 (Limitations: the window).

## S6. "Why should we trust numbers from a project with this correction
history?"

**Response.** Because the correction history is the evidence of the control,
not of its absence. Every number in the manuscript resolves through a macro
generated from an archived manifest; the build fails on any number without
one, on any macro two runs disagree about, and on drift between the index
and its manifests; the abstract and introduction are sentence-mapped to
generating runs in a gate-checked ledger. Every corrected incident in the log
is recorded because the discipline caught it. A paper with no visible
corrections is not a paper with no errors. We would add one qualification
rather than let this answer stand unqualified: the gate as originally written
scanned only the *generated* numbers file, so it could not see a value typed
directly into the manuscript, and three defects of that class did reach a green
gate (CI-11, CI-19, and four AUC-ROC values in the shared-record table). That
hole is now closed structurally — the scan covers the manuscript, everything it
includes, and every file the claim ledger cites — and the incident that records
it (CI-22) also records what the widened scan then caught. **Evidence:**
`scripts/check_provenance.py`, `scripts/check_literals.py`, `CLAIM_LEDGER.md`,
`SCOPE_DECISIONS.md` CI-22.

## From the fresh round

(appended by the triage pass; one entry per shelved item)

## From the fresh round (26 Aug 2026)

Items the one-round triage classified SHELF: judgment, or new work whose cost
exceeded the round's 3-hour analysis cap. Each carries the measured or
estimated cost of doing it, so a revision window can be planned rather than
guessed.

### S7. "Determinism does not establish a stable winner" (review T8)

**Verified TRUE on 26 August 2026; closed since.** At the time no confidence
interval, repeated split or event-block bootstrap was reported. **Response.**
We agreed and removed every "winner" formulation: the manuscript reports a
*measured ordering under the stated protocol* and says so. The instrument has
since been applied. Attack runs on CICIDS2017 have median/p90/max length
2/70/2522, so rows are not exchangeable, and Section 11 reports moving-block
bootstrap intervals over the archived per-record scores of the evaluated
slice, in stream order, with a block length longer than the p90 run: for the
two margins of Section 5.3, the margins of Table 6 and the branch values of
Table 8, with a rerun at two further block lengths. Section 6.2 sweeps seven
chronological cuts and, in Table 7, repeats the assembly contrast at each of
them. The LITNET, sweep and Appendix A results carry no interval, because
their per-record scores were not archived, and Section 11 says so. A
rolling-origin procedure is not applied, and Section 11 states that as a
limit.

### S8. Factorial decomposition of the assembly treatment (review T6)

**Verified TRUE that the design does not identify order alone.** **Response.**
The manuscript now states the estimand as the complete assembly pipeline under
a fixed split rule and makes no order-only claim. A factorial or
prevalence-matched design — separate interventions on training order, test
order, split membership, and prevalence — is the natural next experiment. Cost:
each additional CICIDS arm is one full prequential pass, measured at
3.524 ms/record on the reference machine, so about 1.6 hours per arm plus batch
refits; a 2x2x2 factorial is roughly 13 hours of single-machine compute.

### S9. Protocol-aligned ECOD comparison (review T7)

**Verified TRUE.** ECOD is fitted on benign-only training rows. **Response.**
ECOD is now presented throughout as a *label-privileged diagnostic reference*
and all method-superiority language is removed. Aligning information access
properly means either giving the streaming methods the same benign-only warm
start or refitting ECOD without label access; both change what ECOD is, so the
comparison would need re-designing rather than re-running. Cost: one full pass
per configuration (~1.6 h each) plus design work.

### S10. Truncated-regime characterization of the posterior (review T11, T12)

**Verified TRUE that the exact result covers only the pre-cap regime.**
**Response.** The manuscript now states the three facts separately — exact
cancellation below the cap, measured wandering at and beyond it, and that the
scored quantity is P(r<=5) rather than P(r=0) — and claims nothing about
data-independence over the truncated regime. Characterizing the truncated
recurrence analytically is a mathematical contribution in its own right and is
out of scope for a revision window; an empirical characterization over the
archived component dumps is affordable (hours).

### S11. Broader validation of the alternative reset formulation (review T15)

**Verified TRUE.** One prior, one stream, one prefix, no tuning. **Response.**
The manuscript now says "one untuned instance" everywhere and draws no
conclusion about tuned variants. A meaningful result for a tuned variant needs
a training/validation tuning protocol for the prior scale and more than one
stream, as Appendix A states; cost is dominated by the tuning grid, roughly 8-20 hours depending on
grid size, and it must not select on test labels.

### S12. Systematic literature survey of assembly practice (review T2)

**Verified TRUE that no survey exists.** **Response.** The frequency claims are
withdrawn: the manuscript now says only that the contrasted assembly is the one
used by the audited earlier evaluation, with interleaving and pooling also
discussed in the cited benchmark-criticism literature. A coded survey of
streaming-IDS evaluations would be a contribution of its own; cost is
weeks, not revision-window hours.

### S13. Artifact audit (review T20)

**UNVERIFIABLE from the review packet** — the reviewer had no repository
access, correctly noting that manifests prove lineage, not correctness.
**Response.** The anonymized artifact accompanies the submission, and the
manuscript now states explicitly that provenance establishes traceability and
integrity and *not* that code, labels, preprocessing or interpretation are
correct.

---

## Round-2 additions (submission-side and withdrawal round, 2026-08-27)

### S14. "Your single pre-submission review is not convergence evidence."

**Verified TRUE.** Only one review targets the submitted version; the two
other reviews on file (2026-08-17) address the superseded pre-rebuild
manuscript and were processed separately as V1–V12 in `AUDIT_FINDINGS.md`.
**Response.** We agree and say so in `TRIAGE_REPORT.md`. Our mitigation was not
to seek agreement but to seek verification: the three findings we acted on
(identification, method-identity scope, mean-magnitude) were each settled by
running an analysis against archived per-record scores, not by accepting the
argument. A1 in particular *refuted our own headline*, which is the strongest
available evidence that the round was not self-serving. Single-reviewer
judgment items were shelved rather than acted on.

### S15. "Why is the correction history not in the paper?"

**Judgment, and the answer is anonymity.** **Response.** It was in the paper,
and moving it out was a deliberate fix. Under ACM double-anonymous review the
identifiers of prior appearance go to the editors, not the referees; a
per-result-group overlap matrix against named public preprints, plus a dated
version history, identifies the author. Both tables are in the confidential editor note in
full, expanded with the claims each version invalidates. The anonymized body
(Section 10) states that prior versions exist and were publicly posted, and
that some measurements also appear in them under an interpretation this
paper withdraws; which measurements, which results are new and which are
withdrawn are supplied to the editors. The dated correction history is the
corrected-incident log that ships with the artifact. The note offers to follow the editors'
instruction on how this history is handled, including moving it into the body.

### S16. "A1 only removes the membership difference after the fact."

**Verified TRUE, and stated in the paper.** **Response.** A1 is a post-hoc
restriction to the shared records, not a prospective control: it holds the
evaluated sample fixed but leaves each detector's prequential history, and
ECOD's training rows, different between the arms, and the shared records are
the intersection two particular assemblies produce, not a random subsample.
That is why the paper reports A1 as attributing the reversal to sample
membership under a stated assumption the archived design does not test, not
as decomposing the treatment, and why the
factorial or prevalence-matched design (S8, ≈13 h) remains the named next
experiment rather than a claim we make.
