# HUMAN_ACTIONS — clicks and logins only, in execution order

Nothing here needs judgment, and nothing here is blocked on a missing
identifier. Every file referenced is in this repository.

**Order matters.** Zenodo is done. The submission order is now: **DTRAP
first**, then the arXiv v3 replacement **within 48 hours** (the editor note
promises that window), then the companion's v2 replacement, then the optional
AWS cleanup.

> **Removed 2026-08-27: the TIFS withdrawal steps.** This file previously
> opened with two steps — retrieve the TIFS manuscript ID from email, then send
> a withdrawal letter to the editor-in-chief — and made them the *first* thing
> you did. Both were void: you verified in the IEEE Author Portal that the
> account holds one record, `TDSC-2025-10-1842`, rejected 22 October 2025, and
> no TIFS submission at all. The companion preprint is not under review
> anywhere, so there is nothing to withdraw and no editor to write to. The
> letter is retired in place at `packages/sibling/WITHDRAWAL_LETTER_TIFS.md`
> with a notice explaining why; do not send or adapt it. See
> `SIBLING_DECISION.md` and CI-25.

---

## 0. ORCID confirmation (60 seconds)

Your ORCID is **0009-0000-0664-8228** — the public registry record at that iD is
yours and lists your papers; the `-8224` variant returns 404 and appears nowhere
in the current packages.

1. Sign in at https://orcid.org/signin.
2. Confirm the iD under your name reads 0009-0000-0664-8228.

## 0b. Commit and push this round — BEFORE the deposit

The Zenodo record names the GitHub repository as the source it derives from, and
a Zenodo DOI cannot be withdrawn.

```
python scripts/check_provenance.py --publish-ready
```

**Status 2026-08-27: the round is committed and pushed, the tree is clean, and
every base commit any manifest records resolves in the pushed history.** The
check still exits 1, on one point only: 19 of 25 live run manifests ran while the tree
carried uncommitted edits, so their exact source state is not recoverable (the
base commit is). Two of those cannot be regenerated at all --- the CICIDS
contrast arms ran 4.8 hours on an AWS Linux instance that no longer exists, and
re-running them on this Windows machine would change the published numbers, the
cross-platform effect this project already recorded as CI-16.

**This is a judgement for you, not a bug to fix.** Either accept it and say so
in the deposit description (`ZENODO_DEPOSIT_SHEET.md` carries the wording), or
do not deposit. Nothing else blocks the sequence.

## 1. Zenodo deposit — EXECUTED 2026-08-31

Published as **version 2.0.0** of the existing lineage: version DOI
**10.5281/zenodo.22213264**, concept DOI 10.5281/zenodo.20074589, superseding
v1.0.0 (10.5281/zenodo.20074590). Verified against the Zenodo API 2026-08-31;
all five files at their staged sizes. Record of what was entered:
`ZENODO_DEPOSIT_SHEET.md`.

## 2. DOI propagation — EXECUTED 2026-08-31

`CITATION.cff` carries `doi: 10.5281/zenodo.22213264`, version `2.0.0`,
date-released 2026-08-31; the canonical lineage sentence in all four venue
texts carries the DOI; committed and pushed.

## 3. DTRAP submission (login wall) — FIRST outward action

1. Sign in at **https://mc.manuscriptcentral.com/dtrap** (verified 2026-08-24);
   link ORCID 0009-0000-0664-8228 if prompted.
2. Work through `SUBMISSION_CONSOLE.md` top to bottom. It carries every
   field in paste order: article type, title, verified abstract, keywords,
   CCS concepts, author block, the verified reviewer block, the plain-text
   cover letter and editor note, the questionnaire, and the upload table.
3. Suggested reviewers: your call — candidates with reasons are in
   `SUGGESTED_REVIEWERS.md` (not auto-submitted).
4. **Attach the ACM waiver confirmation.** The PDF is at
   `C:\Users\CYBERWIZARD\Downloads\ACM_Waiver.pdf` (verified present
   2026-08-31). Attach it in the fee section.
5. If the editorial thread with Delman about your ORCID is still open, reply
   with `packages/dtrap/DELMAN_CLARIFICATION_REPLY.md`.
6. Submit. Note the submission date: step 4 is promised within 48 hours of it.

## 4. arXiv v3 replacement — within 48 hours of step 3

Follow `ARXIV_V3_SHEET.md`: paper 2605.24696 → Replace → upload
`packages/arxiv_v3/arxiv_v3_source.tar.gz`; new title; Comments = the NO VENUE
CLAIM variant (it already carries doi:10.5281/zenodo.22213264 and the
provenance disclosure); confirm 17 pages in arXiv's preview and your name on
page 1.

## 5. Companion v2 replacement (arXiv:2510.09619)

Decision is FINAL: corrected **replacement**, not withdrawal (arXiv updates are
replacements; withdrawal reads as retraction). Follow `SIBLING_V2_SHEET.md`.
The sibling's LaTeX source is **not on this machine** (verified: only the PDF
exists locally) — the sheet's first step retrieves your own source from your
arXiv account, then pastes the prepared correction note
(`packages/sibling/V2_CORRECTION_NOTE.tex`).

## 6. AWS closeout — verified 2026-08-31, one console click remains

Checked from the local CLI on 2026-08-31, account confirmed by
`aws sts get-caller-identity`: account 753493992639, user `michel-cli`.
Region eu-central-1 is empty. Zero EC2 instances in any state. Zero EBS
snapshots owned by the account. Zero AMIs owned by the account. Zero EBS
volumes. Estimated ongoing monthly EC2 and EBS cost: $0.00. There are no
snapshots, so no snapshot-deletion decision remains.

The key deactivation could NOT be done from the CLI. The call
`aws iam list-access-keys --user-name michel-cli` returns AccessDenied
because the michel-cli identity has no IAM permissions on itself. That is
good hygiene and it means this step stays yours, in the console:

1. AWS console, IAM, Users, `michel-cli`, Security credentials.
2. Deactivate the access key. Delete it once you are sure nothing needs it.
3. Delete the local entry in `C:\Users\CYBERWIZARD\.aws\credentials`.

---

**Fallback ladder if DTRAP declines:** **TMLR first, DMLR second.** TNSM is
removed from the ladder — it is not free to publish at this paper's 17 pages.

Everything else — compiles, gates, ledger, tests, packages, anonymity scans —
is done and verified. See `PUBLISH_PREP_REPORT.md` and `TRIAGE_REPORT.md`.
