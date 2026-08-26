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
of 2 cells — which is why every flat claim in the paper is between the two
deterministic methods (the evaluated detector and ECOD), where seeds cannot
move anything, and every HST number appears with its seed distribution
(composite spread 0.1776–0.3678). Extending every cell to ≥3 seeds costs
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

**Response.** We agree the detector is known art, and the paper says so in
its own Section 3: what was evaluated is prequential global-Gaussian tail
scoring, and we withdrew the change-point framing after measuring the
posterior pinned to its hazard. The contribution is the characterization:
(a) the construction contrast on identical records with its mechanism
(dilution, not redistribution) measured; (b) the pooling identity; (c) the
method-identity result itself, which generalizes — any BOCPD implementation
whose reset branch shares the growth branch's predictive is silently not
doing change-point detection, and the failure is invisible to every
downstream metric; (d) the both-directions degeneracy of the obvious repair.
DTRAP's scope includes evaluation practice for operational detection; that
is the lane this paper occupies. **Evidence:** `findings_score_threshold.md`,
`findings_bocpd_ablation.md`, Section 3 and 7 of the manuscript.

## S5. "The natural-order test slice is one 204-minute window; that is not an
evaluation."

**Response.** It is what true chronology on this benchmark yields under a
fixed chronological split, and the paper states it prominently rather than
engineering around it — because engineering around it (reordering,
resampling, interleaving) is precisely the construction step under study.
The narrowness of the natural test window is itself a finding about the
benchmark: CICIDS2017 cannot support a chronological evaluation with a
representative test period, and constructions that appear to fix this
manufacture the operating point instead. We agree a split-rule sensitivity
analysis is the right next step and state it as future work; it does not
exist yet and nothing in the paper pretends it does. **Evidence:**
`findings_contrast.md`; manifest `cicids_heldout_composition_*`;
Section 8 (Threats).

## S6. "Why should we trust numbers from a project with this correction
history?"

**Response.** Because the correction history is the evidence of the control,
not of its absence. Every number in the manuscript resolves through a macro
generated from an archived manifest; the build fails on any number without
one, on any macro two runs disagree about, and on drift between the index
and its manifests; the abstract and introduction are sentence-mapped to
generating runs in a gate-checked ledger. The eighteen corrected incidents
are recorded because the discipline caught them. A paper with no visible
corrections is not a paper with no errors. **Evidence:**
`scripts/check_provenance.py`, `CLAIM_LEDGER.md`, `SCOPE_DECISIONS.md`.

## From the fresh round

(appended by the triage pass; one entry per shelved item)

## From the fresh round (26 Aug 2026)

Items the one-round triage classified SHELF: judgment, or new work whose cost
exceeded the round's 3-hour analysis cap. Each carries the measured or
estimated cost of doing it, so a revision window can be planned rather than
guessed.

### S7. "Determinism does not establish a stable winner" (review T8)

**Verified TRUE.** No confidence interval, repeated split, or event-block
bootstrap is reported anywhere. **Response.** We agree and have removed every
"winner" formulation: the manuscript now reports a *measured ordering under the
stated protocol* and says so. The right instrument is an event-block or
rolling-origin procedure, not an IID row bootstrap — attack runs on CICIDS2017
have median/p90/max length 2/70/2522, so rows are not exchangeable. Estimated
cost: a moving-block bootstrap over the archived per-record score vectors is
cheap (minutes) once block length is justified; justifying block length against
the run-length distribution is the actual work, roughly a revision-window day.
The score vectors now exist in the artifact, so this needs no re-scoring.

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

### S11. Broader validation of the change-point repair (review T15)

**Verified TRUE.** One prior, one stream, one prefix, no tuning. **Response.**
The manuscript now says "one untuned instance" everywhere and draws no
conclusion about tuned variants. A meaningful corrected-BOCPD result needs a
training/validation tuning protocol for the prior scale and at least two
streams; cost is dominated by the tuning grid, roughly 8-20 hours depending on
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
