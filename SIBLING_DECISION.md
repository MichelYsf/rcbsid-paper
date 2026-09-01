# Companion manuscript (arXiv:2510.09619) — verified status and FINAL disposition

**Decision (FINAL, 2026-08-31): the companion preprint gets a corrected
replacement (v2), not a withdrawal.** arXiv updates are replacements by design,
and a withdrawal notice reads as a retraction of the whole line of work, which
overstates the case: the manuscript's method descriptions are unsupported by
the shared codebase, but the manuscript reports no quantitative result tables,
so there are no numbers to retract. The v2 replacement is the existing paper
plus a prominent correction note (title page and abstract) stating concretely
what is unsupported — no science rebuild. The note is prepared at
`packages/sibling/V2_CORRECTION_NOTE.tex`; the click-by-click replacement
procedure is `SIBLING_V2_SHEET.md`. **The sibling's LaTeX source is not on this
machine** (verified 2026-08-31: local search found only two PDFs of the
companion, and both candidate zips in Downloads contain the main CALIBURN
paper per their `\title`) — the sheet's first step retrieves the source from
the author's own arXiv account. *Update 2026-09-01:* retrieval is done. arXiv
serves any LaTeX submission's source publicly at its e-print endpoint, so the
v1 source was fetched in one request, verified against the public v1 PDF,
and the correction note is inserted. The staged upload is
`packages/sibling/arxiv_2510_09619_v2_source.tar.gz`.

**The venue question underneath was already closed:**

## What was verified, when, and how

**Verified 2026-08-27 by the author, in the IEEE Author Portal.** With the
filters set to *All Publications* and *All Submission Statuses*, the account
returns **exactly one record**:

| record | status | date |
|---|---|---|
| `TDSC-2025-10-1842` | rejected | 22 October 2025 |

That is a *Transactions on Dependable and Secure Computing* record, and it is
closed. **There is no IEEE TIFS submission, and no open submission of any
kind.** This document does not assert that the TDSC record corresponds to the
companion manuscript; that was not checked and nothing here depends on it.

**Verified state of the companion manuscript:** `arXiv:2510.09619`
("Risk-Calibrated Bayesian Streaming Intrusion Detection with SRE-Aligned
Decisions") is a **public arXiv preprint and nothing else**. It is not under
review at any journal. No editor anywhere is waiting on it, and no editor has
been informed of anything about it.

## What this replaces

The previous version of this file offered two branches — *Branch W* (withdraw
from TIFS before v3 goes public) and *Branch C* (keep the TIFS submission alive
and coordinate a correction) — and recommended Branch W. **Both branches rested
on a submission that does not exist.** They are void, not merely unchosen, and
the recommendation is void with them. The artifacts they produced are retired
in place rather than deleted, so the record shows what was prepared and why it
was wrong:

| artifact | disposition |
|---|---|
| `packages/sibling/WITHDRAWAL_LETTER_TIFS.md` | **RETIRED — do not send.** Header records why. |
| `packages/sibling/ARXIV_V3_COMMENT.txt` | Both prior variants retired; a third variant that makes no venue claim is now the one to use. |

## How the error happened, and the rule it produces

The venue was researched carefully and the submission was never verified. The
prior round fetched the TIFS editor-in-chief, the portal migration, and IEEE's
withdrawal procedure, all correctly — and none of that research could establish
the one fact everything rested on, namely that a submission existed. The
manuscript ID was recorded as "not on this machine", which was treated as *the
operator must look it up* when it was equally consistent with *there is nothing
to look up*. An absent identifier is evidence about the record, not only about
where the record is stored.

**Rule.** Before preparing any artifact that asserts a venue relationship —
a withdrawal, a disclosure, a correction note, a cover-letter sentence — the
existence of that relationship must be verified against the venue's own system,
and the verification recorded with its date and source. Venue *procedure*
research is not verification of venue *status*. Recorded as **CI-25**.

## What remains true and still needs doing

The companion's *technical* problem is unchanged and is not a venue question:
it shares part of the audited codebase, and the method-identity findings of the
audit apply to that shared lineage. The FINAL disposition at the top of this
file resolves it: a v2 replacement carrying the prepared correction note.
Nothing in this repository's submission path depends on it — the DTRAP
submission and the arXiv v3 replacement of the main paper proceed first
(`HUMAN_ACTIONS.md` steps 3–4), and the companion replacement is step 5. No
artifact here may assert that the replacement has been posted until it has.
