# Cover letter — DTRAP submission

To the Co-Editors-in-Chief, ACM Digital Threats: Research and Practice,

Please consider the attached manuscript, "Benchmark Stream Construction, Not
Attack Prevalence, Produces the Regime Structure of Streaming Intrusion
Detection," for publication in DTRAP.

**What the paper contributes.** The paper shows, with mechanically verified
experiments, that the step assembling public capture files into evaluation
streams — day interleaving, capture pooling — produces the operating
conditions that streaming intrusion-detection results are reported under: on
identical records, reordering alone moves held-out prevalence by 43
percentage points and inverts which of the two deterministic methods under
test wins, and pooling disjoint captures reports a prevalence no capture
exhibits. It further characterizes the evaluated detector as implemented
(its change-point posterior is provably data-independent) and shows the
textbook repair is degenerate in the opposite direction. We believe this
sits squarely in DTRAP's remit: it is about what operational detection
evaluations measure.

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
