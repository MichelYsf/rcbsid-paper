# TMLR_SUBMISSION_SHEET — submission of the manuscript to Transactions on Machine Learning Research, nothing submitted

Assembled 2026-09-14 against commit **`adf9e62bcb69b0694ba1c33224c18f86e65e404b`**, whose tree
holds the two files of Step 5 at the sizes given there. Venue guidance below
was read on 2026-09-14 from jmlr.org/tmlr/author-guide.html, the OpenReview
submission invitation `TMLR/-/Submission` (fields and their order are quoted
from it), and github.com/JmlrOrg/tmlr-style-file.

**Order per `HUMAN_ACTIONS.md`:** Zenodo 2.2.0 publish first, then this
submission, then the arXiv v3 replacement, then the companion's v2
replacement. The private note in Step 8 says the corrected preprint follows the
submission; the anonymous PDF itself names no version, DOI or repository.

> **Immutable on submission.** The anonymous PDF and the supplementary zip are
> visible to reviewers and, TMLR says, to the public throughout and after the
> review period. Revision happens inside the review cycle; the decision is
> accept or reject, with required camera-ready changes on acceptance.

> **Anonymity, verified 2026-09-14.** The PDF, the artifact zip and the source
> tarball carry no author name, ORCID, email, machine username, repository or
> branch name, Zenodo DOI or URL, or GitHub handle; `tar tvf` shows zeroed
> owner metadata on every member. `scripts/build_anonymous_artifact.py` fails
> its own build if any identity token survives, `scripts/check_tarball_anonymity.py`
> checks the tarballs, and an independent scan of all three packages found
> nothing. Re-run both scripts if anything is rebuilt.

---

## Step 0 — What changed for this venue

The manuscript was reset on 2026-09-14 in the official TMLR template,
`tmlr.sty` and `tmlr.bst` unmodified (sha256 `816214ff…` and `306fd454…`,
fetched from github.com/JmlrOrg/tmlr-style-file), anonymous mode. Every ACM
element is gone: CCS concepts, keywords block, ACM reference format, the
copyright footer and `\Description`. The bibliography is natbib author-year
through `tmlr.bst`; all 51 entries resolve and render, including the two
GitHub-issue entries and the arXiv-only entries. Section 9 (the alternative
reset formulation) and the mechanics of Section 10 (the gate's covered set and
the claim-ledger internals) are appendices, each with a short statement in the
main text. Section 12 is retitled "Limitations and What Would Change Our
Conclusions" and consolidates the existing limitation content in one place.
One framing paragraph was added at the end of the introduction and one clause
to the abstract. No macro, table value or claim changed.

| build fact | value |
|---|---|
| total pages | 24 |
| main body (before References) | 20, references begin mid-page 20 |
| Appendix A / Appendix B | pages 23 / 24 |
| compile | 3-pass pdflatex+bibtex, exit 0, 0 undefined references, 51 bibliography entries |
| overfull | one box of 0.75pt in the prevalence-sweep table, inside the gate's 2pt tolerance |
| gate | `python scripts/check_provenance.py` 9 of 9 |

## Step 1 — OpenReview account

All authors must have a complete and active OpenReview profile: affiliation
history, conflicts of interest and publication history. TMLR uses the profile,
not the submission, for conflict handling. Sign in at
**https://openreview.net**, open the TMLR group, and choose the submission
form. The profile ID is what the `authorids` field takes.

## Step 2 — Fields, in the form's order

The order and field names are those of the `TMLR/-/Submission` invitation.

### 1. title

```
Stream Assembly Is an Uncontrolled Treatment in Streaming Intrusion-Detection Benchmarks
```

### 2. abstract

Paste verbatim. It is the compiled abstract with every macro resolved (429
words, 2,782 characters). Verify against page 1 of the PDF before pasting.

```
Public network captures are rarely usable as evaluation streams as they stand, so streaming intrusion-detection studies assemble them: interleaving capture days, pooling temporally disjoint captures, or replaying records round robin. We show on two benchmarks that this assembly step is not neutral plumbing but an uncontrolled experimental treatment, a benchmark-construction choice that changes what the evaluation measures. On CICIDS2017, holding the full record multiset identical and changing only the ordering, a fixed positional 70/15/15 split then produces held-out samples that share only 32.5% of their records, at held-out prevalences of 68.235% and 25.2396% — a 42.9954-point difference — and the measured ordering of the two deterministic scorers reverses. Restricting both arms to the 78000 records they both held out removes that reversal: the same scorer leads in both arms there. The reversal is therefore attributable to which records the assembly hands to the test set, not to the order in which the detector saw its history. That attribution assumes that history contributes no more on the records the arms do not share than on those they do. On LITNET-2020, pooling three temporally disjoint captures reports a single 6.4982% operating point that is the equal-weight mean of per-capture held-out prevalences spanning 0.176% to 15.7747%; we present that identity as an audit check rather than a discovery. We also audit the evaluated detector against its description: its reset and growth branches share a predictive term that cancels, so the reset posterior P(r_t=0) equals the hazard rate exactly below the run-length cap, while the evaluations spend nearly all their length at or beyond that cap, where the posterior instead wanders; and the score the evaluation consumes is a function of P(r ≤ 5), not of P(r=0). Scoring that detector one branch at a time yields a separate result: its deployed max composition ranks worse than its own tail term alone (0.103477 AP, 0.302658 AUC-ROC), because the auxiliary branch is inverted rather than uninformative (AUC-ROC 0.281890) and a maximum lets it set the record's score wherever the tail is small — a defect no metric computed on the assembled score can attribute. Finally, we quantify a batch dependence in the ECOD reference implementation, whose empirical CDFs are recomputed over the training matrix concatenated with the scored batch: holding the evaluated records and the fitted model fixed and changing only the accompanying batch moves its AUC-PR by 0.003063, so published ECOD numbers are not comparable across studies that score a different batch, in size or composition. Every measured value traces to an archived, hash-verified run manifest, and the sentence-level claim ledger ships with the artifact.
```

The form accepts TeX for formulas (`$...$`); the two posterior expressions
above are given in plain text and may be entered as `$P(r_t{=}0)$` and
`$P(r \le 5)$` instead.

### 3. authors

```
Michel Youssef
```

### 4. authorids

The OpenReview profile ID of the author. Not the email.

### 5. pdf

Upload `packages/dtrap/manuscript_anonymous.pdf` (the directory name is
historical; the file is the TMLR anonymous build). Never `paper/main.pdf`
from a tree where the arXiv variant was built into it, and never anything from
`packages/arxiv_v3/`, which is named.

### 6. submission_length

Select **Long submission (more than 12 pages of main content)**. The main
body is 20 pages. TMLR states that long submissions may take significantly
longer to review; the length is the price of the provenance and limitation
material, and the appendices are where the mechanics went.

### 7. supplementary_material

Upload **one** zip: `packages/dtrap/artifact_anonymous.zip`. It holds the
code, tests, run manifests, claim ledger, findings documents, the manuscript
source with the TMLR template files, and the figures, and it passes the
artifact-safe gate checks from a fresh extraction. TMLR's limit is 100 MB in
PDF or ZIP; this is under 1 MB. Supplementary material is visible to reviewers
and the public, so it is anonymized exactly as the PDF is.

The anonymous source tarball `packages/dtrap/source_anonymous.tar.gz` is not
uploaded separately: OpenReview takes a single supplementary file, and the zip
already contains the source. It stays staged as the record of what the source
was, and compiles standalone.

### 8. previous_TMLR_submission_url

Leave empty. This work has not been submitted to TMLR before.

### 9. changes_since_last_submission

Leave empty; it applies only to resubmissions.

### 10. competing_interests

```
None. The sole author is an independent researcher with no institutional affiliation, no funding, and no financial or other relationship in the last 36 months with any entity that could be perceived to influence this work. The work uses public datasets and open-source libraries only.
```

### 11. human_subjects_reporting

```
N/A
```

## Step 3 — Files to upload

| # | file | size | role |
|---|---|---|---|
| 1 | `packages/dtrap/manuscript_anonymous.pdf` | 499,838 B | the submission PDF, 24 pages |
| 2 | `packages/dtrap/artifact_anonymous.zip` | 627,366 B | the single supplementary file, 236 entries |

Read both sizes off the tree at the commit named at the top of this sheet
before uploading. Run `python scripts/check_tarball_anonymity.py` and rebuild
the artifact with `python scripts/build_anonymous_artifact.py` if any source
changed; the artifact builder fails on any identity token.

## Step 4 — Keywords

OpenReview's form has no keywords field in this invitation. If one appears,
use the manuscript's former keyword list:

```
streaming network intrusion detection; benchmark stream construction; evaluation methodology; experimental design; anomaly detection benchmarks; reproducibility; provenance
```

## Step 5 — Action editor recommendation, after submission

TMLR's author guide says authors "must provide information on appropriate
action editors for the submission." OpenReview opens this as a task on the
submission after it is created, not as a field on the form. Recommend from the
public board at jmlr.org/tmlr/editorial-board.html. The board lists each
action editor's stated interests; the names below were matched on 2026-09-14
against the paper's subject and are candidates for your judgement, not a
recommendation this sheet makes for you. Check each one's current OpenReview
profile for conflicts before recommending.

| stated interests on the board | action editors whose entry states them |
|---|---|
| anomaly detection | Jicong Fan; Satoshi Hara; Markus Lange-Hegermann (with time series); Antonio Vergari; Chuan Sheng Foo |
| machine learning and security | Sanghyun Hong; Chaowei Xiao; Pin-Yu Chen |
| benchmarking, validity, distribution shift | Olawale Elijah Salaudeen; Chinmay Hegde |
| reproducibility, hypothesis testing | Junpei Komiyama |

The paper is an evaluation-methodology study with an anomaly-detection
instance and a security corpus; an action editor from the first or third row
is the closest fit to TMLR's two acceptance questions. Avoid recommending
anyone you have co-authored with or corresponded with about this work.

## Step 6 — Do not do

- Do not enter a cover letter anywhere; TMLR has none.
- Do not suggest reviewers; TMLR takes none. The DTRAP reviewer block in
  `SUBMISSION_CONSOLE.md` is retired.
- Do not upload the named arXiv variant, `paper/main.pdf` after an arXiv
  build, or anything from `packages/arxiv_v3/`.
- Do not paste the DTRAP cover letter or editor note into any field. Both are
  retired as historical and carry a notice saying so.

## Step 7 — Preprint policy, checked

TMLR permits authors to upload their submissions to arXiv at any time,
anonymously or named, provided the double-blind status of the TMLR submission
itself is maintained by the authors. The anonymous PDF names no version, DOI
or repository, so the arXiv v3 replacement may follow the submission as
`HUMAN_ACTIONS.md` step 4 says. Reviewers who search for the title will find
the named preprint; that is permitted by the policy and is not a breach on the
author's side.

## Step 8 — Private note to the action editor

OpenReview has no confidential-comments field on the submission form. After
the action editor is assigned, send this as an official comment with readers
set to the action editor only (and the editors-in-chief if the form offers
it), not to reviewers. Everything in it is already disclosed in the paper in
anonymized form; the identifiers are what the anonymous PDF withholds.

```
Dear Action Editor,

Three disclosures about this submission, made privately because they identify
the authors.

1. Prior public versions contained errors this version corrects. The manuscript
supersedes arXiv:2605.24696 v1 (23 May 2026) and v2 (25 June 2026), which
reported results produced under a composite benchmark construction and
described a scoring rule the released code did not implement. An adversarial
review and a line-by-line audit of the archived artifacts established both.
This version is the rebuild from that audit; Section 11 and the Origin
paragraph of the introduction state this in anonymized form. The per-result
account of what is reused, re-derived, corrected, withdrawn or new: the pooled
LITNET composite and the assembled CICIDS arm are the same measurements as in
v1 and v2, reported there under a regime interpretation that this paper
replaces with an assembly interpretation; the timestamp-ordered CICIDS arm,
the per-capture LITNET streams, the shared-record analysis and the
method-identity audit have no counterpart in any earlier version; and results
on a third dataset that appeared in the earlier versions are withdrawn and are
not relied upon anywhere in this paper. A corrected v3 of the preprint,
matching this submission, will be posted after submission; TMLR's preprint
policy permits this and the anonymous PDF names no version.

2. The Zenodo record lineage. The artifact is archived on Zenodo under concept
DOI 10.5281/zenodo.20074589. Version 1.0.0 (doi:10.5281/zenodo.20074590,
deposited 2026-05-07) holds the pre-audit codebase cited by v1 and v2. The
corrected rebuild is published in the same lineage as version 2.0.0
(doi:10.5281/zenodo.22213264) and version 2.1.0 (doi:10.5281/zenodo.22638195),
and the version accompanying this manuscript is 2.2.0
(doi:10.5281/zenodo.22673735). The paper's Data and Artifact Availability
section refers to the archived artifact without naming it, so that reviewers
are not led to an author-named record; the anonymized supplementary zip is
the same artifact. The camera-ready will carry the lineage.

3. The work is not under review anywhere. A submission to ACM Digital Threats:
Research and Practice was prepared and not made; the venue was changed to
TMLR before any submission. A companion preprint sharing parts of the codebase
(arXiv:2510.09619) is a public preprint, is not under review at any venue,
and is being corrected separately; the manuscript's Companion Manuscript
Disclosure states this in anonymized form.

Michel Youssef, independent researcher, Beirut, Lebanon.
ORCID 0009-0000-0664-8228.
```

## Step 9 — After submit

1. Record the OpenReview forum URL in `HUMAN_ACTIONS.md`.
2. Complete the action-editor recommendation task (Step 5).
3. Send the private note (Step 8) once the action editor is assigned.
4. Proceed to the arXiv v3 replacement, `ARXIV_V3_SHEET.md`.
