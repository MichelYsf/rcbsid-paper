# HUMAN_ACTIONS — clicks and logins only, in execution order

Nothing here needs judgment, and nothing here is blocked on a missing
identifier. Every file referenced is in this repository.

**Where things stand, 2026-09-18.** The venue is **ACM Digital Threats:
Research and Practice (DTRAP)**, through ScholarOne. The one outward action
left is that submission, from `SUBMISSION_CONSOLE.md` (step 3 below).
Everything before it in the sequence is done and is kept below as the record,
marked historical:

- Zenodo 2.2.0 is published (doi:10.5281/zenodo.22673735).
- arXiv v3 of 2605.24696 and the companion's v2 of 2510.09619 were both
  posted on 14 September 2026 and announced on 16 September 2026.
- The TMLR submission of 16 September 2026 was desk-rejected on 18 September
  2026 without review, in a decision signed by the venue, with no action
  editor assigned and no comment given. That is why the venue is DTRAP again.

> **Removed 2026-08-27: the TIFS withdrawal steps.** This file previously
> opened with two steps — retrieve the TIFS manuscript ID from email, then send
> a withdrawal letter to the editor-in-chief — and made them the *first* thing
> you did. Both were void: you verified in the IEEE Author Portal that the
> account holds one record, `TDSC-2025-10-1842`, rejected 22 October 2025, and
> no TIFS submission at all. That record is the companion's: arXiv:2510.09619 was submitted to IEEE Transactions on
> Dependable and Secure Computing and desk-rejected on 22 October 2025 on scope
> grounds, without peer review. The companion preprint is not under review
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

## 0b. Commit and push before the deposit — HISTORICAL, done before the 2.2.0 publish

The Zenodo record names the GitHub repository as the source it derives from, and
a Zenodo DOI cannot be withdrawn. This step preceded the publish of 2.2.0 and
is kept for the next deposit, the camera-ready one.

```
python scripts/check_provenance.py --publish-ready
```

**Status 2026-09-14 (historical): the reformat round for TMLR, the venue at
the time, was committed and pushed at its end, the tree was clean, and every
base commit any manifest records resolves in the pushed history. Run `--publish-ready` before the deposit; it prints
whether HEAD is on the remote, and the Step 7 commit link resolves only if
it is.** The
check still exits 1, on one point only: 27 of 33 live run manifests ran while
the tree carried uncommitted edits, so their exact source state is not
recoverable (the base commit is). Two of those cannot be regenerated at all ---
the CICIDS contrast arms ran 4.8 hours on an AWS Linux instance that no longer
exists, and re-running them on this Windows machine would change the published
numbers, the cross-platform effect this project already recorded as CI-16.
`scripts/check_publish_ready.py` prints the same two numbers; if it ever
disagrees with the deposit description, the manifests bundle settles it.

**This is a judgement for you, not a bug to fix.** Either accept it and say so
in the deposit description (`ZENODO_DEPOSIT_SHEET.md` carries the wording), or
do not deposit. Nothing else blocks the sequence.

## 1. Zenodo 2.2.0 publish — DONE, 14 September 2026 (historical)

Version 2.2.0 was published on 14 September 2026 at 21:48 UTC (publication
date 2026-09-15 on the record) as **doi:10.5281/zenodo.22673735**. Verified
2026-09-18 against the Zenodo API: the record is published, it is the latest
of the four versions in the lineage (2.2.0, 2.1.0 doi:10.5281/zenodo.22638195,
2.0.0 doi:10.5281/zenodo.22213264, 1.0.0 doi:10.5281/zenodo.20074590), and its
five files match `packages/zenodo/` by MD5. Its manuscript source is the build
reset on 2026-09-14 in the TMLR template (24 pages, 20 of them main body);
that is a historical fact about the deposit. As for the rest, its analysis code (src/ and the analysis scripts), its manifests bundle (93
run manifests, the macro index and the retirement README) and its macro layer
are identical to those behind the DTRAP submission; its claim ledger differs
only by corrected internal cross references and two rows for the reshaped opening; the manuscript source, the
figure renderer's size constants and the figure manifest, the packaging and
gate scripts with their tests, and the response shelf differ.
The camera-ready deposit will carry the final source. `packages/zenodo/` is frozen: do not rebuild it.

## 2. DOI propagation for 2.2.0 — EXECUTED 2026-09-09 (historical)

`CITATION.cff` carries doi 10.5281/zenodo.22673735, version 2.2.0,
date-released 2026-09-14; the canonical lineage sentence in all five venue
texts names 2.2.0 as the version accompanying this manuscript and keeps the
1.0.0, 2.0.0 and 2.1.0 lineage intact; the editor note, the prior-appearance
note, the cover letter in both renders, the README, the artifact access
strategy, every sheet, the named arXiv variant's availability sentence and the
companion's v2 correction note all cite 2.2.0. Since the publish of 14
September 2026 every one of those citations resolves.

## 3. DTRAP submission — NEXT, the only outward action left

Work through `SUBMISSION_CONSOLE.md` top to bottom at
https://mc.manuscriptcentral.com/dtrap. It carries every ScholarOne field in
paste order, the three files to upload with their sizes, the cover letter
(`packages/dtrap/COVER_LETTER.txt`), the confidential note
(`packages/dtrap/EDITOR_NOTE.txt`, which discloses both prior submissions),
the verified reviewers, the questionnaire answers and the waiver rule. After
submitting, record the manuscript ID in the console.

## 3a. TMLR submission — HISTORICAL: submitted 2026-09-16, desk-rejected 2026-09-18

Submitted 16 September 2026 through `TMLR_SUBMISSION_SHEET.md`, forum
https://openreview.net/forum?id=qbYQReMqwP. Desk-rejected without review on
18 September 2026, in a decision signed by the venue; no action editor was
assigned and no comment was given. The follow-ups of that sheet's Step 9, the
action-editor recommendation and the private note to the action editor, had
no action editor to go to and are void. `TMLR_SUBMISSION_SHEET.md` is marked
historical.

## 4. arXiv v3 replacement — DONE: posted 2026-09-14, announced 2026-09-16 (historical)

Verified 2026-09-18 on arxiv.org/abs/2605.24696v3: posted 14 September 2026 at
22:18 UTC under the new title, with the 1,898-character abstract of
`ARXIV_V3_SHEET.md` Step 3, CC BY 4.0, cs.CR with cross-list cs.LG, 24 pages
by its Comments field. The source posted is the named variant in the TMLR
template staged at commit 2bfb896, verified 2026-09-18: arXiv's submission receipt lists the archive contents as tmlr.sty, tmlr.bst,
fancyhdr.sty, main.tex, numbers.tex, references.bib, the two table files and
the four figures. The tarball staged at commit 2bfb896 (113,688 B) holds those
files and main.bbl, which the receipt's list as relayed does not name; the
listing's 108 KB is arXiv's recompressed size.
That is a historical fact. The tarball now in
`packages/arxiv_v3/` is the acmart rebuild of 2026-09-18 (25 pages) and was not
posted. The Comments field actually posted is a 411-character text as arXiv
renders it, not the sheet's NO VENUE CLAIM variant; `ARXIV_V3_SHEET.md`
records it. Nothing to do.

## 5. Companion v2 replacement (arXiv:2510.09619) — DONE: posted 2026-09-14, announced 2026-09-16 (historical)

Verified 2026-09-18 on arxiv.org/abs/2510.09619v2: posted 14 September 2026 at
22:30 UTC as a corrected replacement, not a withdrawal, with the correction
note on the title page, the bracketed correction sentence opening the
abstract, and the Comments field of `SIBLING_V2_SHEET.md` step 3 (the DOI
rendered as a link, no final period). Nothing to do.

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

**Fallback ladder, as last recorded: DMLR.** TMLR is off it after the desk
rejection of 18 September 2026. TNSM stays removed: it is not free to publish
at this paper's 24 pages.

Everything else — compiles, gates, ledger, tests, packages, anonymity scans —
is done and verified, with one expected exception: the gate's package-freshness
check fails on the frozen Zenodo 2.2.0 code zip, which must not be rebuilt. See `PUBLISH_PREP_REPORT.md` and `TRIAGE_REPORT.md`.
