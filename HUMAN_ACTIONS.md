# HUMAN_ACTIONS — everything that still needs a human, in execution order

Only logins, clicks, one decision, and pasting reviewer output. No judgment
calls except step 3. Every file referenced is in this repository.

---

## 0. ORCID confirmation (60 seconds)

The resolved ORCID is **0009-0000-0664-8228**. Evidence: the public registry
record at that iD is yours (name, country, your three arXiv works listed);
the -8224 variant returns 404 — it does not exist.

1. Go to https://orcid.org/signin and sign in.
2. Confirm the iD shown under your name reads 0009-0000-0664-8228.
3. Done. (-8224 was a transcription error; it appears nowhere current — it
   was purged from CITATION.cff and all prepared packages.)

## 1. Fresh adversarial review round (no accounts needed)

1. Open `REVIEWER_KIT/REVIEWER_PROMPT.txt`; copy its full text.
2. Paste it, with `REVIEWER_KIT/manuscript_review.pdf` attached, into each
   fresh reviewer session you want (two independent sessions recommended).
3. Save each review's output as `REVIEWER_KIT/review_fresh_<n>.md`.
4. Tell the finalize agent "reviews are in" — it executes
   `REVIEWER_KIT/REVIEW_TRIAGE_TEMPLATE.md` exactly once and regenerates the
   packages. (One round only. That rule is in the template.)

## 2. Zenodo deposit (login wall)

1. Sign in at https://zenodo.org (GitHub or ORCID login).
2. Click "New upload".
3. Zip `packages/zenodo/manifests_bundle/` into `manifests_bundle.zip`
   (right-click → Compress), then upload the five files listed at the bottom
   of `packages/zenodo/zenodo_metadata.md`.
4. Fill the form by copy-pasting each field from `zenodo_metadata.md`
   (upload type, title, author+ORCID, license, version, related identifiers,
   keywords, description).
5. Click Publish. Copy the **version DOI** Zenodo shows.
6. Paste that DOI into `CITATION.cff` (replace the sentence in `message:`
   with the DOI in a new `doi:` field), commit, push.

## 3. THE DECISION — sibling paper (read `SIBLING_DECISION.md`, choose one)

- **Branch W (recommended):** email `packages/sibling/WITHDRAWAL_LETTER_TIFS.md`
  to the TIFS editorial office through the ScholarOne thread for the
  submission of arXiv:2510.09619. Send BEFORE step 4.
- **Branch C:** do not withdraw; instead email the TIFS editor a disclosure
  (the letter's middle two paragraphs serve verbatim) the same day step 4
  executes, and use the COEXIST comment variant in step 4.

## 3b. Companion-disclosure paragraph matches the branch (2 minutes, local)

The manuscript's Companion Paper Disclosure currently reads (anonymous and
named variants alike) "a correction process for the companion manuscript is
in progress and has been disclosed to the relevant editors" - written to be
true under EITHER branch once step 3 is executed. After deciding step 3:
- Branch W: optionally strengthen the named (arXiv) variant to "has been
  withdrawn from journal consideration by the author pending its own
  correction" - edit packages/arxiv_v3/src/main.tex, recompile (three-pass),
  re-tar. The neutral wording is also acceptable as-is.
- Branch C: send the TIFS editor disclosure the same day, so the sentence is
  true when v3 goes public. No edit needed.

## 4. arXiv v3 replacement (login wall)

1. Sign in at https://arxiv.org; go to your paper 2605.24696 → "Replace".
2. Upload `packages/arxiv_v3/arxiv_v3_source.tar.gz`.
3. Title field: the new title from `packages/arxiv_v3/METADATA.md`.
4. Comments field: the variant matching your step-3 decision, from
   `packages/sibling/ARXIV_V3_COMMENT_COEXIST.txt`, with the page count set
   to 10.
5. Preview arXiv's compiled PDF; confirm 10 pages and your name on page 1.
6. Submit the replacement.

## 5. DTRAP submission (login wall)

1. Sign in at **https://mc.manuscriptcentral.com/dtrap** (portal verified
   current 2026-08-24; create/link your account with ORCID 0009-0000-0664-8228
   if prompted).
2. New submission → upload `packages/dtrap/manuscript_anonymous.pdf` as the
   main document.
3. Upload `packages/dtrap/artifact_anonymous.zip` and
   `packages/dtrap/source_anonymous.tar.gz` as supplementary material NOT for
   publication.
4. Paste the cover letter from `packages/dtrap/COVER_LETTER.md` into the
   cover-letter field.
5. **Attach the ACM waiver confirmation**: the file
   `ACM_waiver_confirmation_2026-08-07.pdf` is NOT on this machine — retrieve
   it from your email (search "ACM waiver" around 2026-08-07) and attach it,
   or reference the waiver ticket number in the fee section.
6. If the editorial thread with Delman about your ORCID is still open, reply
   with the body in `packages/dtrap/DELMAN_CLARIFICATION_REPLY.md`.
7. Submit.

## 6. Optional — retire the AWS IAM access key

The rebuild's cloud phase is over; eu-central-1 holds nothing. The
`michel-cli` access key on this machine no longer needs to exist.

1. Sign in to the AWS console → IAM → Users → `michel-cli` → Security
   credentials.
2. Deactivate, then delete, the access key currently in
   `C:\Users\CYBERWIZARD\.aws\credentials`.
3. Delete that credentials entry locally.

---

That is the complete list. Everything else — compiles, gates, tests, ledger,
packages, anonymity checks — is done and verified; see `FINALIZE_REPORT.md`.
