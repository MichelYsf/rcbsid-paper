# DTRAP_SUBMISSION_SHEET — nothing submitted

Assembled 2026-08-27 against commit **`45229a57fbf3cef9ce7f2dbe66b9e34263c96ff1`**.
Portal: **https://mc.manuscriptcentral.com/dtrap** (ScholarOne, verified
2026-08-24). Do this **last**, after Zenodo and arXiv.

> **Double-anonymous.** The main document must stay anonymous. The identifying
> material — prior appearance, the overlap matrix, the correction history — goes
> in *Confidential Comments to the Editor*, never in the manuscript. Verified:
> the anonymized PDF contains **zero** identity tokens.

---

## Step 1 — Article type

**Full research paper.** Not a Field Note. 17 pages, inside DTRAP's 10–25.

## Step 2 — Title

```
Stream Assembly Is an Uncontrolled Treatment in Streaming Intrusion-Detection Benchmarks
```

## Step 3 — Abstract

Use the same expanded text as `ARXIV_V3_SHEET.md` Step 3 (identical wording; the
two builds differ only in author identification). If the portal strips LaTeX,
that text is already plain.

## Step 4 — CCS concepts (ACM CCS 2012)

| significance | concept |
|---|---|
| 500 | Security and privacy → Intrusion detection systems |
| 300 | Computing methodologies → Machine learning |
| 300 | General and reference → Evaluation |

## Step 5 — Keywords

```
streaming network intrusion detection; benchmark stream construction;
evaluation methodology; experimental design; anomaly detection benchmarks;
reproducibility; provenance
```

## Step 6 — Files to upload

| # | file | size | role |
|---|---|---|---|
| 1 | `packages/dtrap/manuscript_anonymous.pdf` | 570,998 B | **main document** |
| 2 | `packages/dtrap/artifact_anonymous.zip` | 475,753 B | supplementary, **not for publication** |
| 3 | `packages/dtrap/source_anonymous.tar.gz` | 43,665 B | supplementary, **not for publication** |

The artifact contains 205 files and passes its own documented reproduction
instructions inside a fresh extraction (verified; see `PUBLISH_PREP_REPORT.md`).

## Step 7 — Cover letter

Paste `packages/dtrap/COVER_LETTER.md`. **Corrected 2026-08-27**: it previously
named the withdrawn title and claimed "reordering alone … inverts which of the
two deterministic methods under test wins" — the claim analysis A1 refuted. Both
now match the manuscript.

## Step 8 — Confidential Comments to the Editor

Paste **`packages/dtrap/PRIOR_APPEARANCE_EDITOR_NOTE.md` in full** (140 lines).
It contains, and the manuscript deliberately does not:

- the prior appearance: arXiv:2605.24696 v1 (23 May 2026) and v2 (25 June 2026),
  neither submitted to a journal
- the per-result-group overlap matrix — reused / re-derived / new / withdrawn
- the dated correction history with the claims each version invalidates
- the companion preprint arXiv:2510.09619: a public preprint, **not under review
  at any venue**, verified in the IEEE Author Portal on 2026-08-27 (one record,
  `TDSC-2025-10-1842`, rejected 22 October 2025). An earlier draft of this note
  told the editors a journal "has been or is being informed"; that was false and
  the note now says so itself
- the two failures of the provenance mechanism (CI-22, CI-26), disclosed rather
  than presented at the strength their names implied

Printing any of this in the body would deanonymize the submission; the note says
so and offers to move it if the editors prefer.

## Step 9 — Portal questions that need an answer

| question | answer |
|---|---|
| Is the work previously published? | **No** — but it has prior *public appearance* as a preprint; see the confidential note |
| Is it under consideration elsewhere? | **No.** This manuscript is under consideration at DTRAP and nowhere else, and so is nothing else of the author's |
| Conflicts of interest | None to declare |
| Funding | None to declare |
| **Code availability** | Yes — Apache-2.0. Anonymous copy uploaded as supplementary material; on acceptance, the public repository and the Zenodo DOI |
| **Data availability** | The benchmarks are public third-party datasets (CICIDS2017, Engelen-corrected release; LITNET-2020). They are **not** redistributed. The artifact ships `EXPECTED_SHA256.txt`, line-ending-normalized hashes that let a reader verify their own reconstruction of each stream |
| Generative AI disclosure | **Required and already in the manuscript**, in *Acknowledgements: Generative AI Usage*: use is disclosed, no AI tool is an author, no reported number was produced by one, and the authors take full responsibility |
| ORCID | 0009-0000-0664-8228 — link if prompted |
| Open-access fee / waiver | A waiver was confirmed 2026-08-07. **`ACM_waiver_confirmation_2026-08-07.pdf` is not on this machine** — retrieve it from email ("ACM waiver", around 2026-08-07), or cite the waiver ticket number in the fee section |
| Suggested reviewers | **[decide]** — none prepared |

## Step 10 — Before submitting

1. Confirm the uploaded PDF is `manuscript_anonymous.pdf`, **not** `paper/main.pdf`
   (the latter is the same build but the arXiv variant is the named one; the
   anonymous build is what carries "Anonymous Author(s)").
2. If the editorial thread with Delman about the ORCID is still open, reply with
   `packages/dtrap/DELMAN_CLARIFICATION_REPLY.md`.
3. Submit.
