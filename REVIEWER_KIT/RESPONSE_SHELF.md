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
