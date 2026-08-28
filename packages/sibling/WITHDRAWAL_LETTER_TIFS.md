> # ⛔ RETIRED 2026-08-27 — VOID, DO NOT SEND
>
> **There is no IEEE TIFS submission to withdraw.** Verified by the author in
> the IEEE Author Portal on 2026-08-27: with filters set to *All Publications*
> and *All Submission Statuses*, the account returns exactly one record —
> `TDSC-2025-10-1842`, **rejected 22 October 2025** — and no TIFS record of any
> kind. The companion manuscript `arXiv:2510.09619` is a public preprint and is
> not under review anywhere.
>
> This letter would therefore have asked an editor to withdraw a manuscript
> that was never submitted to that journal. **Do not send it. Do not adapt it
> for another venue.**
>
> It is kept rather than deleted for one reason: the record should show what
> was prepared on a false premise and how far it got. Everything below the rule
> is the retired draft, preserved verbatim. Its venue research (portal
> migration, editor-in-chief, IEEE's non-self-service withdrawal procedure) was
> accurate about TIFS as a journal and irrelevant, because none of it could
> establish that a submission existed. See `SIBLING_DECISION.md` and corrected
> incident **CI-25**.
>
> The withdrawal-first ordering it imposed on `HUMAN_ACTIONS.md` has been
> removed; the sequence is now Zenodo → DOI → arXiv v3 → DTRAP.

---

# Withdrawal request — IEEE Transactions on Information Forensics and Security

**Status: RETIRED AND VOID (see the notice above). Previously: drafted, not
sent.** One field required the operator (marked `[[MANUSCRIPT ID]]`) — an
absence that should have been read as evidence that no submission existed.

## Where this goes, verified fresh 2026-08-27

- **The portal has migrated.** IEEE TIFS now takes submissions through the IEEE
  Author Portal at `https://ieee.atyponrex.com/journal/tifs-ieee`, not
  ScholarOne (verified 2026-08-27 at
  `https://signalprocessingsociety.org/publications-resources/ieee-transactions-information-forensics-and-security/ieee-transactions`).
  Any previously recorded ScholarOne address for this journal is stale — check
  which system holds *your* submission before acting; a manuscript submitted
  before the migration may still live in the old system.
- **Withdrawal is not a self-service action.** IEEE's guidance is that authors
  cannot withdraw a manuscript from within their submission account and must
  contact the editorial office to request it (IEEE Author Center journal
  guidance; corroborated by IEEE journal author FAQs, retrieved 2026-08-27).
  So the letter below is the mechanism, not a button.
- **Addressee.** Editor-in-Chief, IEEE TIFS: **Prof. Luisa Verdoliva**
  (University of Naples Federico II), listed contact `verdoliv@unina.it`
  (IEEE Signal Processing Society TIFS pages, retrieved 2026-08-27). Send to
  the EiC and copy the editorial office address shown in your submission
  confirmation email — that address is authoritative for your submission and is
  not published on the public pages.
- **Resubmission after withdrawal.** IEEE does not prohibit later submission of
  a corrected manuscript; a voluntarily withdrawn manuscript is not a retracted
  one, and IEEE's post-publication policies (retraction, correction) govern
  *published* articles, which this is not. A corrected version would be a new
  submission, and disclosing this withdrawal in its cover letter is the
  defensible course. **Verify this against the acceptance/withdrawal terms in
  your own submission confirmation before relying on it.**

---

## The letter

**To:** Prof. Luisa Verdoliva, Editor-in-Chief, IEEE Transactions on
Information Forensics and Security (`verdoliv@unina.it`), cc the editorial
office address from the submission confirmation email

**Subject:** Author-initiated withdrawal — Manuscript `[[MANUSCRIPT ID]]`,
"Risk-Calibrated Bayesian Streaming Intrusion Detection with SRE-Aligned
Decisions"

Dear Professor Verdoliva,

I am writing to withdraw manuscript `[[MANUSCRIPT ID]]`, "Risk-Calibrated
Bayesian Streaming Intrusion Detection with SRE-Aligned Decisions," from
consideration at IEEE Transactions on Information Forensics and Security. The
withdrawal is author-initiated and precautionary, and I am sorry to take the
editorial team's and any reviewers' time before doing so.

An audit of the research codebase shared between this manuscript and a
companion work established two defects in the shared lineage. First, the
implemented anomaly-scoring rule differs from the scoring rule described in the
text: the evaluated score is a maximum of a chi-square tail term and a weighted
short-run posterior mass, not the run-length-reset posterior the text defines,
and the decision threshold is the prior-inclusive Bayes rule rather than the
cost-only rule described. Second, a quantity reported as a detection latency in
milliseconds is in fact a count of records between attack onset and first
alert. The affected code lineage produced the results in the submitted
manuscript.

Until each affected claim is regenerated under a corrected and
provenance-tracked pipeline, I cannot stand behind the submitted description of
the method, and I do not wish reviewers to spend further time on it.

A corrected version of the companion work, with an archived generating run
recorded for every reported number, is being prepared for public posting with a
correction note. I am sending this withdrawal first so that the journal hears
of the issue from me rather than from that note.

If, after correction, the work remains sound and novel, I would hope to submit
a corrected version as a new submission, disclosing this withdrawal in the
cover letter. I am grateful for the journal's time and consideration.

Sincerely,
Michel Youssef
ORCID: 0009-0000-0664-8228
michelyoussef@hotmail.com

---

## The one field the operator must supply

`[[MANUSCRIPT ID]]` — **not present anywhere on this machine.** Searched: the
whole user profile (Downloads, Documents, Desktop, OneDrive), the repository,
and every prior session transcript, for `TIFS-#####`-style identifiers and for
"manuscript ID" near TIFS. Zero hits. Retrieve it from the submission
confirmation email (search your mail for "Information Forensics" or
"atyponrex" or the manuscript title) and paste it into the subject line and the
first sentence. If the confirmation email also names an editorial-office
address, use that as the cc.
