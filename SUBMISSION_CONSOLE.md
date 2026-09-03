# SUBMISSION_CONSOLE: DTRAP submission morning, top to bottom

Work through this file in order on submission morning. Every field is in
ScholarOne paste order. Nothing here needs judgment except where a step says
so. Assembled 2026-08-31. This is the operative document. The older
DTRAP_SUBMISSION_SHEET.md now defers to it.

## 1. Portal and login

Address: https://mc.manuscriptcentral.com/dtrap (verified 2026-08-24).
Sign in with your own account, the one registered to
michelyoussef@hotmail.com. ScholarOne will ask to link your ORCID. Link
0009-0000-0664-8228.

## 2. Article type

Select: **full research paper**. The paper is 20 pages, inside DTRAP's 10 to
25 page range. If the type list does not offer a clearly matching option,
stop and report the list. Choose nothing.

## 3. Title

Paste exactly:

```
Stream Assembly Is an Uncontrolled Treatment in Streaming Intrusion-Detection Benchmarks
```

## 4. Abstract

Paste the full abstract below. It is plain text, already expanded from the
manuscript macros, and it was verified on 2026-08-31 to match the manuscript
abstract exactly after LaTeX normalization. It is 399 words and 2,607
characters.

```
Public network captures are rarely usable as evaluation streams as they stand,
so streaming intrusion-detection studies assemble them: interleaving capture
days, pooling temporally disjoint captures, or replaying records round robin. We
show on two benchmarks that this assembly step is not neutral plumbing but an
uncontrolled experimental treatment. On CICIDS2017, holding the full record
multiset identical and changing only the ordering, a fixed positional 70/15/15
chronological split then produces held-out samples that share only 32.5% of
their records, at held-out prevalences of 68.235% and 25.2396% -- a
42.9954-point difference -- and the measured ordering of the two deterministic
scorers reverses. Restricting both arms to the 78000 records they both held out
removes that reversal: the same scorer leads in both arms there. The reversal is
therefore a consequence of which records the assembly hands to the test set, not
of the order in which the detector saw its history, and we locate it
accordingly. On LITNET-2020, pooling three temporally disjoint captures reports
a single 6.4982% operating point that is the equal-weight mean of per-capture
held-out prevalences spanning 0.176% to 15.7747%; we present that identity as an
audit check rather than a discovery. We also audit the evaluated detector
against its description: its reset and growth branches share a predictive term
that cancels, so the run-length posterior equals the hazard rate exactly below
the run-length cap, while the evaluations spend nearly all their length at or
beyond that cap, where the posterior instead wanders; and the score the
evaluation consumes is a function of P(r<=5), not of P(r=0). Scoring that
detector one branch at a time yields a separate result: its deployed max
composition ranks worse than its own tail term alone (0.103477 AP, 0.302658
AUC-ROC), because the auxiliary branch is inverted rather than uninformative
(AUC-ROC 0.281890) and a maximum lets it govern the rank wherever the tail is
small -- a defect no metric computed on the assembled score can attribute.
Finally, we quantify a batch dependence in the ECOD reference implementation,
whose empirical CDFs are recomputed over the training matrix concatenated with
the scored batch: holding the evaluated records and the fitted model fixed and
changing only the accompanying batch moves its AUC-PR by 0.003063, so published
ECOD numbers are not comparable across studies that score different batch sizes.
Every measured value traces to an archived, hash-verified run manifest, and the
sentence-level claim ledger ships with the artifact.
```

The abstract text keeps the manuscript's own punctuation, including its
double-hyphen dashes and semicolons. It is manuscript text and is not
rewritten by the plain-register rule.

Condensed variant, use ONLY if the portal enforces a length cap the full
abstract exceeds. It is derived from the full abstract with no new claims.

```
Streaming intrusion-detection studies assemble evaluation streams from public
capture files by interleaving capture days, pooling disjoint captures, or
replaying records round robin. We show on two benchmarks that this assembly
step is an uncontrolled experimental treatment, not neutral plumbing. On
CICIDS2017, holding the record multiset identical and changing only the
ordering, a fixed positional split produces held-out samples that share only
32.5% of their records, sit 42.9954 percentage points apart in prevalence, and
reverse the measured ordering of the two deterministic scorers. Restricting
both arms to the records they both held out removes the reversal, locating it
in test-set membership rather than processing order. On LITNET-2020, the
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

Three concepts, with significance:

| significance | concept |
|---|---|
| 500 | Security and privacy, Intrusion detection systems |
| 300 | Computing methodologies, Machine learning |
| 300 | General and reference, Evaluation |

## 7. Author block

One author. Name: Michel Youssef. Email: michelyoussef@hotmail.com.
Affiliation: Independent Researcher. Country: Lebanon. ORCID:
0009-0000-0664-8228. ScholarOne will ask you to link the ORCID through its
own dialog. Complete that link.

## 8. Suggested reviewers, verified 2026-08-31

Four verified candidates, in `SUGGESTED_REVIEWERS.md` with sources and the
two drops explained. Enter the ones you choose:

1. Pierazzi, Fabio, f.pierazzi@ucl.ac.uk, University College London. He wrote
   TESSERACT, the closest prior work on evaluation-stream bias, which the
   paper cites and distinguishes.
2. Botacin, Marcus, botacin@tamu.edu, Texas A&M University. He coauthored
   DTRAP's own stream-of-problems paper on ML security evaluation and works
   on artifact-level reproducibility.
3. Rimmer, Vera, vera.rimmer@kuleuven.be, KU Leuven. She coauthored the
   CICIDS2017 re-evaluation work this paper's CICIDS findings rest on.
4. Quiring, Erwin, erwin.quiring@fbeta.de, _fbeta GmbH, Berlin. He coauthored
   the Dos and Don'ts pitfalls paper that anchors the sampling-bias
   discussion. He is now in industry, which DTRAP's practice remit fits.

Excluded and confirmed clean: Seth Barrett and every FIRCE and FADES author
(all Augusta University plus DFAIR Lab). No candidate overlaps.

## 9. Cover letter

Paste the whole of `packages/dtrap/COVER_LETTER.txt` (836 words). It is plain
text with no markdown residue.

Contingency: if the portal offers no separate confidential-comments box, use
the single cover-letter field for both texts. Paste the cover letter, then
this heading on its own line, then the editor note:

```
CONFIDENTIAL TO THE EDITORS: PRIOR APPEARANCE AND CORRECTION HISTORY
```

## 10. Confidential comments to the editor

Paste the whole of `packages/dtrap/EDITOR_NOTE.txt` (1,647 words). It carries
the prior-appearance disclosure, the overlap account, the correction history,
the companion-manuscript status, and the provenance limitation.

## 11. Portal questionnaire

Answers, one per row:

| question | answer |
|---|---|
| Previously published? | No. It has prior public appearance as a preprint. The confidential note covers it. |
| Under consideration elsewhere? | No. This manuscript is under consideration at DTRAP and nowhere else, and so is nothing else of the author's. |
| Conflicts of interest | None to declare. |
| Funding | None to declare. |
| Code availability | Yes, Apache-2.0. An anonymous copy is uploaded as supplementary material. The public repository and the Zenodo DOI follow at acceptance. |
| Data availability | The benchmarks are public third-party datasets (CICIDS2017 in the Engelen-corrected release, and LITNET-2020). They are not redistributed. The artifact ships EXPECTED_SHA256.txt, line-ending-normalized hashes that let a reader verify their own reconstruction of each stream. |
| Generative AI disclosure | Required and already in the manuscript, in Acknowledgements: Generative AI Usage. Use is disclosed. No AI tool is an author. No reported number was produced by one. The author takes full responsibility. |
| ORCID | 0009-0000-0664-8228. Link when prompted. |
| Open-access fee waiver | A waiver was confirmed 2026-08-07. The confirmation PDF is at `C:\Users\CYBERWIZARD\Downloads\ACM_Waiver.pdf` (643,261 bytes, verified present 2026-08-31). Attach it in the fee section. |
| Suggested reviewers | Enter your picks from step 8. |

## 12. File uploads

Three files, with designations:

| # | full path | bytes | designation |
|---|---|---|---|
| 1 | `C:\Users\CYBERWIZARD\projects\rcbsid-paper\packages\dtrap\manuscript_anonymous.pdf` | 641,538 | main document |
| 2 | `C:\Users\CYBERWIZARD\projects\rcbsid-paper\packages\dtrap\artifact_anonymous.zip` | 542,095 | supplementary for review, not for publication |
| 3 | `C:\Users\CYBERWIZARD\projects\rcbsid-paper\packages\dtrap\source_anonymous.tar.gz` | 92,399 | supplementary for review, not for publication |

Upload the anonymized PDF, never `paper\main.pdf`. The anonymous build is the
one that says "Anonymous Author(s)" on page 1.

## 13. Proof check and submit

ScholarOne renders a proof PDF of your entries before submission. Open it.
Confirm the title, the abstract, one anonymous main document of 20 pages, and
both supplementary files. Confirm the manuscript PDF shows no author name.
Then press submit.

## 14. After submit

Save the confirmation email as a PDF into `C:\Users\CYBERWIZARD\Downloads`.
Record the manuscript ID here in this file, next to this line. The 48-hour
clock for the arXiv v3 replacement starts at submission. Step 4 of
`HUMAN_ACTIONS.md` and `ARXIV_V3_SHEET.md` carry that replacement. If the
Delman ORCID thread is still open, reply with
`packages/dtrap/DELMAN_CLARIFICATION_REPLY.md`.
