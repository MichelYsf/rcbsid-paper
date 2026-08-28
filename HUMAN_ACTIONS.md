# HUMAN_ACTIONS — clicks and logins only, in execution order

Nothing here needs judgment, and nothing here is blocked on a missing
identifier. Every file referenced is in this repository.

**Order matters.** Zenodo first, so its DOI can be carried into the arXiv
replacement and the DTRAP submission.

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

The Zenodo record names the GitHub repository and branch `rebuild/honest-v1` as
the source it derives from, and a Zenodo DOI cannot be withdrawn. Right now that
branch does not contain this work: the whole correction round is uncommitted and
the branch has no upstream, so 61 of 65 live run manifests record a `-dirty`
commit that no reader can resolve.

```
python scripts/check_provenance.py --publish-ready
```

Run it until it passes. If you deposit before it does, the deposit will point at
a public commit that does not contain the results it archives.

## 1. Zenodo deposit (login wall)

1. Sign in at https://zenodo.org (GitHub or ORCID login).
2. "New upload".
3. Zip `packages/zenodo/manifests_bundle/` to `manifests_bundle.zip`, then
   upload the files listed at the bottom of
   `packages/zenodo/zenodo_metadata.md`.
4. Fill the form by copy-paste from `zenodo_metadata.md`.
5. Publish. Copy the **version DOI**.

## 2. Propagate the DOI (2 minutes, local)

1. In `CITATION.cff`, replace the explanatory sentence in `message:` with a
   `doi:` field carrying the version DOI.
2. Commit and push.

## 3. arXiv v3 replacement (login wall)

1. Sign in at https://arxiv.org → paper 2605.24696 → **Replace**.
2. Upload `packages/arxiv_v3/arxiv_v3_source.tar.gz`.
3. **Title:** the new title in `packages/arxiv_v3/METADATA.md`.
4. **Comments:** the **NO VENUE CLAIM VARIANT** at the top of
   `packages/sibling/ARXIV_V3_COMMENT_COEXIST.txt`. The withdrawal and
   coexistence variants below it are **retired and false** — both asserted a
   journal status for the companion preprint that does not exist — and are kept
   only as a record. Replace `[[PAGES]]` with the page count of the compiled
   PDF before pasting; this field is public and permanent.
5. Preview arXiv's build; confirm the page count and your name on page 1.
6. Submit the replacement.

## 4. DTRAP submission (login wall)

1. Sign in at **https://mc.manuscriptcentral.com/dtrap** (verified 2026-08-24);
   link ORCID 0009-0000-0664-8228 if prompted.
2. Submission type: **full research paper** (not Field Note).
3. Upload `packages/dtrap/manuscript_anonymous.pdf` as the main document.
4. Upload `packages/dtrap/artifact_anonymous.zip` and
   `packages/dtrap/source_anonymous.tar.gz` as supplementary material **not for
   publication**.
5. Cover letter: paste `packages/dtrap/COVER_LETTER.md`.
6. **Confidential Comments to the Editor**: paste
   `packages/dtrap/PRIOR_APPEARANCE_EDITOR_NOTE.md`. This is where the prior
   appearance, the overlap matrix and the correction history live — they are
   deliberately **not** in the manuscript, because printing them would
   deanonymize the submission.
7. **Attach the ACM waiver confirmation**: `ACM_waiver_confirmation_2026-08-07.pdf`
   is **not on this machine** — retrieve it from email (search "ACM waiver"
   around 2026-08-07), or reference the waiver ticket number in the fee section.
8. If the editorial thread with Delman about your ORCID is still open, reply
   with `packages/dtrap/DELMAN_CLARIFICATION_REPLY.md`.
9. Submit.

## 5. Optional — retire the AWS IAM access key

eu-central-1 holds nothing; the cloud phase is over.

1. AWS console → IAM → Users → `michel-cli` → Security credentials.
2. Deactivate, then delete, the key in `C:\Users\CYBERWIZARD\.aws\credentials`.
3. Delete the local credentials entry.

---

Everything else — compiles, gates, ledger, tests, packages, anonymity scans — is
done and verified. See `TRIAGE_REPORT.md` for this round and
`FINALIZE_REPORT.md` for the previous one.
