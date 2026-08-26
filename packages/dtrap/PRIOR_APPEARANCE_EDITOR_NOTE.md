# Confidential note to the DTRAP editors — prior appearance and correction status

Paste into the ScholarOne "Confidential Comments to the Editor" field, or send
to dtrap-editors@acm.org referencing the submission ID. It is deliberately
outside the manuscript so the manuscript stays anonymous; DTRAP's guidance asks
authors to disclose prior appearance to the editors.

---

Dear Editors,

This submission has prior public appearance, and it is a correction of that
prior work. I would rather you have the full picture from me at submission than
discover it later.

**Prior versions.** The manuscript supersedes a preprint posted as
**arXiv:2605.24696**, "CALIBURN: Operationally Calibrated Streaming Intrusion
Detection with Regime-Dependent Conformal Risk Control":

| version | date | status |
|---|---|---|
| v1 | 23 May 2026 | public preprint, never submitted to a journal |
| v2 | 25 June 2026 | public preprint, never submitted to a journal |

Neither version was accepted anywhere. A corrected v3, matching this
submission, will be posted; I will hold it until the editors advise if you
prefer.

**What was wrong, and what the correction covers.** An adversarial review and a
line-by-line audit of the archived artifacts established two defects that
affect interpretation rather than arithmetic:

1. The released code does not implement the anomaly score the papers describe.
   The evaluated score is a maximum of a chi-square tail term and a weighted
   short-run posterior mass, not the run-length-reset posterior of the text;
   the decision threshold is the prior-inclusive Bayes rule rather than the
   cost-only rule described; and the quantity reported as "latency in
   milliseconds" is a count of records.
2. The headline results were produced on *assembled* evaluation streams
   (pooled captures, day-interleaved records). The prior versions interpreted
   the resulting operating points as dataset properties ("rare-attack regime",
   "moderate-prevalence regime"). The present submission shows that those
   operating points are properties of the assembly.

**Overlap with the prior versions.** The submission's Section 9
(Table "Overlap with the public earlier versions") states this per result group
in the manuscript itself. In summary: the LITNET pooled composite results and
the CICIDS assembled-arm results are the **same measurements** as the prior
versions' corresponding tables, carried forward with corrected interpretation;
the prevalence sweep is re-derived from the archived pre-audit runs and
re-scoped; the timestamp-ordered CICIDS arm, the per-capture LITNET streams,
the held-out overlap and dilution analysis, and the method-identity audit are
new; and the prior versions' UNSW-NB15 results are withdrawn and are not
relied upon.

**Companion manuscript.** A companion preprint, **arXiv:2510.09619**
("Risk-Calibrated Bayesian Streaming Intrusion Detection with SRE-Aligned
Decisions"), shares part of the same codebase and predates the audit. The
method-identity findings apply to its shared lineage. It reports no
quantitative result tables, so it has no numeric overlap with this submission;
its correction is being handled separately and the relevant journal has been
or is being informed.

**Anonymity.** The manuscript suppresses these identifiers for double-anonymous
review and points to this note. If you judge that the correction history makes
effective anonymity impossible and would prefer a different handling, I will
follow your instruction.

The full artifact — code, every run manifest, the claim ledger, and the
numbered corrected-incident log — accompanies the submission as anonymized
supplementary material.

Sincerely,
[Author, identified to the editorial system]
