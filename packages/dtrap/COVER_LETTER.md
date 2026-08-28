# Cover letter — DTRAP submission

To the Co-Editors-in-Chief, ACM Digital Threats: Research and Practice,

Please consider the attached manuscript, "Stream Assembly Is an Uncontrolled
Treatment in Streaming Intrusion-Detection Benchmarks," for publication in
DTRAP.

**What the paper contributes.** The paper shows, with mechanically verified
experiments, that the step assembling public capture files into evaluation
streams — day interleaving, capture pooling — is not neutral plumbing but an
uncontrolled experimental treatment. On CICIDS2017, holding the record multiset
identical and changing only the ordering, a fixed positional split produces
held-out samples sharing 32.5% of their records, at held-out prevalences 43
percentage points apart, and the measured ordering of the two deterministic
scorers reverses. Restricting both arms to the records they both held out
removes that reversal, which locates the effect in *which records the assembly
places in the test set* rather than in the order the detector processed them —
a result that refuted our own earlier headline and reshaped the paper around the
smaller supported claim. Pooling disjoint LITNET captures reports a prevalence
no capture exhibits, offered as an audit check rather than a discovery. The
paper also characterizes the evaluated detector as implemented: its reset and
growth branches share a predictive term that cancels, so the run-length
posterior equals the hazard rate exactly *below* the run-length cap, while the
evaluations spend nearly all their length at or beyond it, where the posterior
wanders — three facts we state separately because only the first is exact. And
scored one branch at a time, the detector's deployed maximum composition ranks
worse than its own tail term alone. We believe this sits squarely in DTRAP's
remit: it is about what operational detection evaluations measure.

**Correction transparency.** This manuscript is a corrected rebuild of work
previously posted as arXiv:2605.24696 (v1/v2). Earlier versions reported
results produced under the composite construction that this paper now
studies as its labeled synthetic arm, and described a scoring rule the
released code did not implement. Both issues were established by an
adversarial audit of the archived artifacts; the introduction discloses this
in full, the artifact ships the audit and the full corrected-incident
history, and every number in the manuscript traces to an archived
run manifest through a build gate and a sentence-level claim ledger. We
prefer the editors to have this history from us directly.

**Open-access fee.** An ACM publication-fee waiver was confirmed for this
work on 2026-08-07 (reference: ACM waiver confirmation of 2026-08-07,
attached to the submission). [NOTE TO OPERATOR: the confirmation PDF
(ACM_waiver_confirmation_2026-08-07.pdf) is not on this machine — attach it
from the email record; HUMAN_ACTIONS step 4.6.]

**Artifact access under double-anonymous review.** The full artifact (code,
manifests, claim ledger, stream-reconstruction scripts with hash
verification) is provided as an anonymized zip through the submission
system's supplementary-material channel. It contains no author-identifying
strings (verified mechanically). A public, author-named release of the same
artifact will be linked in the camera-ready version.

**Companion manuscript.** A related manuscript sharing parts of the audited
codebase (arXiv:2510.09619) is a public preprint, is not under review at any
venue, and is being corrected separately; the manuscript's Companion Manuscript
Disclosure section states this, and the confidential editor note records how it
was verified. This submission is under consideration at DTRAP and nowhere else.

Thank you for your consideration.

[Submitting author: identified to the editorial system only, per
double-anonymous policy. ORCID: 0009-0000-0664-8228.]
