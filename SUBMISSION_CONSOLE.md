# SUBMISSION_CONSOLE: DTRAP submission on ScholarOne, top to bottom

Work through this file in order. Every field is in ScholarOne paste order.
Nothing here needs judgment except where a step says so. Re-assembled
2026-09-18 for the DTRAP submission. This is the operative document. The older
DTRAP_SUBMISSION_SHEET.md is superseded by it. Venue facts below were re-read
on 2026-09-18 from dl.acm.org/journal/dtrap/author-guidelines and from the
portal's login page.

## 1. Portal and login

Address: https://mc.manuscriptcentral.com/dtrap. The DTRAP author guidelines
name it, and on 2026-09-18 the page opened as "Digital Threats: Research and
Practice ScholarOne Manuscripts". Sign in with your own account, the one
registered to michelyoussef@hotmail.com. ScholarOne will ask to link your
ORCID. Link 0009-0000-0664-8228.

## 2. Article type

DTRAP's guidelines call this kind of paper a "Peer-Reviewed Research Paper".
Select the portal's type that matches it. The paper is 24 pages, inside
the 10 to 25 journal pages DTRAP expects and under its 30-page soft limit. If
the type list does not offer a clearly matching option, stop and report the
list. Choose nothing.

## 3. Title

Paste exactly:

```
Stream Assembly Is an Uncontrolled Treatment in Streaming Intrusion-Detection Benchmarks
```

## 4. Abstract

Paste the full abstract below. It is plain text, expanded from the manuscript
macros, and it was verified on 2026-09-18 to match the manuscript abstract
exactly after LaTeX normalization. It is 428 words and 2,786
characters, ASCII only.

```
Public network captures are rarely usable as evaluation streams as they stand,
so streaming intrusion-detection studies assemble them: interleaving capture
days, pooling temporally disjoint captures, or replaying records round robin. We
show on two benchmarks that this assembly step is not neutral plumbing but an
uncontrolled experimental treatment, a benchmark-construction choice that
changes what the evaluation measures. On CICIDS2017, holding the full record
multiset identical and changing only the ordering, a fixed positional 70/15/15
split then produces held-out samples that share only 32.5% of their records, at
held-out prevalences of 68.235% and 25.2396% -- a 42.9954-point difference --
and the measured ordering of the two deterministic scorers reverses. Restricting
both arms to the 78000 records they both held out removes that reversal: the
same scorer leads in both arms there. The reversal is therefore attributable to
which records the assembly hands to the test set, not to the order in which the
detector saw its history. That attribution assumes that history contributes no
more on the records the arms do not share than on those they do. On LITNET-2020,
pooling three temporally disjoint captures reports a single 6.4982% operating
point that is the equal-weight mean of per-capture held-out prevalences spanning
0.176% to 15.7747%; we present that identity as an audit check rather than a
discovery. We also audit the evaluated detector against its description: its
reset and growth branches share a predictive term that cancels, so the reset
posterior P(r_t=0) equals the hazard rate exactly below the run-length cap,
while the evaluations spend nearly all their length at or beyond that cap, where
the posterior instead wanders; and the score the evaluation consumes is a
function of P(r<=5), not of P(r=0). Scoring that detector one branch at a time
yields a separate result: its deployed max composition ranks worse than its own
tail term alone (0.103477 AP, 0.302658 AUC-ROC), because the auxiliary branch is
inverted rather than uninformative (AUC-ROC 0.281890) and a maximum lets it set
the record's score wherever the tail is small -- a defect no metric computed on
the assembled score can attribute. Finally, we quantify a batch dependence in
the ECOD reference implementation, whose empirical CDFs are recomputed over the
training matrix concatenated with the scored batch: holding the evaluated
records and the fitted model fixed and changing only the accompanying batch
moves its AUC-PR by 0.003063, so published ECOD numbers are not comparable
across studies that score a different batch, in size or composition. Every
measured value traces to an archived, hash-verified run manifest, and the
sentence-level claim ledger ships with the artifact.
```

The abstract text keeps the manuscript's own punctuation, including its
double-hyphen dashes and semicolons. It is manuscript text and is not
rewritten by the plain-register rule.

Condensed variant, use ONLY if the portal enforces a length cap the full
abstract exceeds. It is derived from the full abstract with no new claims, and
every number in it is in the full abstract.

```
Streaming intrusion-detection studies assemble evaluation streams from public
capture files by interleaving capture days, pooling disjoint captures, or
replaying records round robin. We show on two benchmarks that this assembly
step is an uncontrolled experimental treatment, not neutral plumbing. On
CICIDS2017, holding the record multiset identical and changing only the
ordering, a fixed positional split produces held-out samples that share only
32.5% of their records, sit 42.9954 percentage points apart in prevalence, and
reverse the measured ordering of the two deterministic scorers. Restricting
both arms to the records they both held out removes the reversal, attributing
it to test-set membership rather than to processing order. On LITNET-2020, the
pooled operating point is the equal-weight mean of per-capture prevalences
spanning 0.176% to 15.7747%. We also audit the evaluated detector against its
description and quantify a batch dependence in the ECOD reference
implementation. Every measured value traces to an archived, hash-verified run
manifest.
```

## 5. Keywords

One line, comma separated, as in the manuscript:

```
streaming network intrusion detection, benchmark stream construction, evaluation methodology, experimental design, anomaly detection benchmarks, reproducibility, provenance
```

## 6. CCS concepts

Three concepts, with significance, as in the manuscript:

| significance | concept |
|---|---|
| 500 | Security and privacy, Intrusion detection systems |
| 300 | Computing methodologies, Machine learning |
| 300 | General and reference, Evaluation |

## 7. Author block

One author. Name: Michel Youssef. Email: michelyoussef@hotmail.com.
Affiliation: Independent Researcher. City: Beirut. Country: Lebanon. ORCID:
0009-0000-0664-8228. ScholarOne will ask you to link the ORCID through its
own dialog. Complete that link.

## 8. Suggested reviewers, re-verified 2026-09-18

Three verified candidates, in `SUGGESTED_REVIEWERS.md` with a source URL and
fetch time for each. Enter the ones you choose:

1. Pierazzi, Fabio, f.pierazzi@ucl.ac.uk, University College London.
   Coauthor of TESSERACT, the closest prior work on evaluation-stream bias,
   which the paper cites and distinguishes.
2. Botacin, Marcus, botacin@tamu.edu, Texas A&M University. Coauthor of
   DTRAP's own stream-of-problems paper on ML security evaluation, with work
   on artifact-level reproducibility.
3. Quiring, Erwin, erwin.quiring@fbeta.de, _fbeta GmbH, Berlin. Coauthor of
   the Dos and Don'ts pitfalls paper that anchors the sampling-bias
   discussion. Now in industry, which DTRAP's practice remit fits.

Vera Rimmer was dropped this round: the affiliation is confirmed, but no
official page shows the email without a CAPTCHA. `SUGGESTED_REVIEWERS.md`
says how to restore the entry yourself.

Excluded and confirmed clean: Seth Barrett and every FIRCE and FADES author
(all Augusta University plus DFAIR Lab). No candidate overlaps.

## 9. Cover letter

Paste the whole of `packages/dtrap/COVER_LETTER.txt` (946 words). It is
plain ASCII text with no markdown residue and no operator note.

Contingency: if the portal offers no separate confidential-comments box, do
not paste the editor note into the cover-letter field; the submission history
belongs in a confidential-to-editor field only. Stop and report before
submitting.

## 10. Confidential comments to the editor

Paste the whole of `packages/dtrap/EDITOR_NOTE.txt` (2,180 words). It carries
the prior-appearance disclosure, the two prior submissions and the review they
did not receive, what Zenodo 2.2.0 carries, the overlap account, the correction history, the
companion-manuscript status with its IEEE portal record, and the provenance
limitation. The cover letter carries none of the submission history; it
belongs in this field only.

## 11. Portal questionnaire

Answers, one per row:

| question | answer |
|---|---|
| Previously published? | No. It has prior public appearance as a preprint. The confidential note covers it. |
| Under consideration elsewhere? | No |
| Previously submitted elsewhere? (only if the form asks this) | Yes, twice, and neither was peer reviewed: an earlier, pre-audit version to KeAi Cyber Security and Applications in May 2026, rejected within 48 hours without peer review; and this version to Transactions on Machine Learning Research on 16 September 2026, desk-rejected on 18 September 2026 without review. The confidential comments give the details. |
| Conflicts of interest | None to declare. |
| Funding | None to declare. |
| Code availability | Yes, Apache-2.0. An anonymous copy is uploaded as supplementary material. The author-named release is archived as Zenodo version 2.2.0 (doi:10.5281/zenodo.22673735). The public repository and the DOI of the camera-ready deposit are supplied in the manuscript at camera-ready. |
| Data availability | The benchmarks are public third-party datasets (CICIDS2017 in the Engelen-corrected release, and LITNET-2020). They are not redistributed. The artifact ships EXPECTED_SHA256.txt, line-ending-normalized hashes that let a reader verify their own reconstruction of each stream. |
| Generative AI disclosure | Required and already in the manuscript, under "Acknowledgements: Generative AI Usage". Use is disclosed. No AI tool is an author. No reported number was produced by one. The author takes full responsibility. |
| ORCID | 0009-0000-0664-8228. Link when prompted. |
| Suggested reviewers | Enter your picks from step 8. |

Open-access fee waiver. Attach the waiver confirmation ONLY if the portal
shows a fee or waiver field, and only in that field. The file is
`C:\Users\CYBERWIZARD\Downloads\ACM_Waiver.pdf` (643,261 bytes, present
2026-09-18). If the portal shows no fee or waiver field, attach it nowhere.
Never attach it in the file-upload step of section 12.

Submitting address and the waiver. The submitting address is
michelyoussef@hotmail.com, the account of section 1. Lebanon's 100%
geographic waiver was confirmed in writing by ACM's Director of Publications,
Scott Delman, on 6 August 2026: the email says the waiver will be applied
automatically to this paper during the eRights process, and it sets no
institutional condition on the waiver. The same email asks for an
institutional email address for submission and eRights; the request it
answered stated that you have no institutional affiliation, so there is none
to use. If eRights asks about the waiver or the address, forward that
confirmation (the same ACM_Waiver.pdf).

## 12. File uploads

Three files, with designations. Sizes are those of the files built
2026-09-18 and committed with this console:

| # | full path | bytes | SHA-256 (first 16) | designation |
|---|---|---|---|---|
| 1 | `C:\Users\CYBERWIZARD\projects\rcbsid-paper\packages\dtrap\manuscript_anonymous.pdf` | 682,410 | `c21d9de1f4b32d8d` | main document |
| 2 | `C:\Users\CYBERWIZARD\projects\rcbsid-paper\packages\dtrap\artifact_anonymous.zip` | 618,195 | `44171c251dba1e67` | supplementary for review, not for publication |
| 3 | `C:\Users\CYBERWIZARD\projects\rcbsid-paper\packages\dtrap\source_anonymous.tar.gz` | 103,254 | `25daf24b83cb7805` | supplementary for review, not for publication |

Upload exactly these three files and nothing else. The waiver PDF is not one of
them. The anonymous build is the one that says "ANONYMOUS AUTHOR(S)" on page 1.

Before uploading, run `python scripts/check_tarball_anonymity.py`. It must
print PASSED. It reads the tarballs' POSIX owner metadata, which `tar tvf`
shows a referee without extracting anything.

## 13. Proof check and submit

ScholarOne renders a proof PDF of your entries before submission. Open it.
Confirm the title, the abstract, one anonymous main document of 24 pages,
and both supplementary files. Confirm the manuscript PDF shows no author name.
Confirm ACM_Waiver.pdf is not among the uploaded files. Then press submit.

## 14. After submit

Save the confirmation email as a PDF into `C:\Users\CYBERWIZARD\Downloads`.
Record the manuscript ID here in this file, next to this line. Nothing else is
due on submission: the corrected arXiv v3 and the companion's v2 were both
posted on 14 September 2026 and announced on 16 September 2026.
