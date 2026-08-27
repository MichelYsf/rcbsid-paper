# HUMAN_ACTIONS — clicks and logins only, in execution order

Nothing here needs judgment. The sibling decision has been made (withdraw); the
one thing only you can supply is the TIFS manuscript ID, which is not on this
machine. Every file referenced is in this repository.

**Order matters.** The TIFS withdrawal goes first, so the journal hears from you
before the public correction note appears. Zenodo before arXiv/DTRAP so the DOI
can be carried into both.

---

## 0. ORCID confirmation (60 seconds)

Your ORCID is **0009-0000-0664-8228** — the public registry record at that iD is
yours and lists your papers; the `-8224` variant returns 404 and appears nowhere
in the current packages.

1. Sign in at https://orcid.org/signin.
2. Confirm the iD under your name reads 0009-0000-0664-8228.

## 1. Retrieve the TIFS manuscript ID from email (5 minutes)

Searched and **not found** anywhere on this machine: profile, repository, and
every prior session transcript. Search your mail for "Information Forensics",
"atyponrex", or the title "Risk-Calibrated Bayesian Streaming Intrusion
Detection with SRE-Aligned Decisions". From the submission confirmation email,
copy two things:

- the **manuscript ID**, and
- the **editorial-office email address** it was sent from or names.

Note which system the confirmation points to: TIFS has migrated to the IEEE
Author Portal (`https://ieee.atyponrex.com/journal/tifs-ieee`), so a submission
made before the migration may still live in the older system.

## 2. Send the TIFS withdrawal (login + email)

Open `packages/sibling/WITHDRAWAL_LETTER_TIFS.md`.

1. Replace both `[[MANUSCRIPT ID]]` placeholders (subject line and first
   sentence) with the ID from step 1.
2. **To:** Prof. Luisa Verdoliva, Editor-in-Chief — `verdoliv@unina.it`.
   **Cc:** the editorial-office address from step 1.
3. **Subject:** the subject line in the file.
4. **Body:** the letter, verbatim. No attachments.
5. If the Author Portal shows an explicit *Withdraw* action on the submission,
   use it **as well as** the email — IEEE's guidance is that withdrawal is not
   self-service, so the email is the operative request and the portal action, if
   present, is confirmation. Do not rely on the portal action alone.
6. **Save the confirmation**: the sent message and any acknowledgement, into
   your records. Nothing downstream depends on it, but a withdrawal you cannot
   evidence is a withdrawal you may have to argue about later.

## 3. Zenodo deposit (login wall)

1. Sign in at https://zenodo.org (GitHub or ORCID login).
2. "New upload".
3. Zip `packages/zenodo/manifests_bundle/` to `manifests_bundle.zip`, then
   upload the files listed at the bottom of
   `packages/zenodo/zenodo_metadata.md`.
4. Fill the form by copy-paste from `zenodo_metadata.md`.
5. Publish. Copy the **version DOI**.

## 4. Propagate the DOI (2 minutes, local)

1. In `CITATION.cff`, replace the explanatory sentence in `message:` with a
   `doi:` field carrying the version DOI.
2. Commit and push.

## 5. arXiv v3 replacement (login wall)

1. Sign in at https://arxiv.org → paper 2605.24696 → **Replace**.
2. Upload `packages/arxiv_v3/arxiv_v3_source.tar.gz`.
3. **Title:** the new title in `packages/arxiv_v3/METADATA.md`.
4. **Comments:** the **WITHDRAWAL VARIANT** at the top of
   `packages/sibling/ARXIV_V3_COMMENT_COEXIST.txt`. Do not use the coexistence
   variant — it is retained only as a record of the branch not taken. Confirm
   the page count in the text matches the compiled PDF.
5. Preview arXiv's build; confirm the page count and your name on page 1.
6. Submit the replacement.

## 6. DTRAP submission (login wall)

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

## 7. Optional — retire the AWS IAM access key

eu-central-1 holds nothing; the cloud phase is over.

1. AWS console → IAM → Users → `michel-cli` → Security credentials.
2. Deactivate, then delete, the key in `C:\Users\CYBERWIZARD\.aws\credentials`.
3. Delete the local credentials entry.

---

Everything else — compiles, gates, ledger, tests, packages, anonymity scans — is
done and verified. See `TRIAGE_REPORT.md` for this round and
`FINALIZE_REPORT.md` for the previous one.
