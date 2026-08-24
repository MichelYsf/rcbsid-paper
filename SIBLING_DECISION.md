# SIBLING_DECISION — arXiv:2510.09619 ("Risk-Calibrated Bayesian Streaming
# Intrusion Detection with SRE-Aligned Decisions"), currently under TIFS review

**This is the one strategic decision the operator must make. Nothing below has
been executed.** Both artifacts are drafted to final quality in
`packages/sibling/` and referenced from `HUMAN_ACTIONS.md`.

## The situation

The sibling paper shares the audited codebase lineage. The audit findings
that force the present rebuild apply to it directly where they touch shared
code: the implemented score is not the described score (A1), the run-length
posterior is data-independent (A2, re-measured in Stage 3), the threshold is
the prior-inclusive rule rather than the described cost-only rule (A3), and
"latency in milliseconds" is a record count (A4). The sibling's v1 abstract
also states its threshold derivation as the cost-only form. Its results were
produced before the audit; some of its claims are therefore known-wrong in
the same way v1/v2 of this paper were.

Meanwhile, this paper's arXiv v3 (the corrected version) will be public and
will say, in its introduction, that earlier versions described a scoring rule
the code did not implement. Anyone who reads v3 and then reads the sibling
will see the contradiction within minutes.

## Branch W — withdraw from TIFS before v3 goes public

**Artifact:** `packages/sibling/WITHDRAWAL_LETTER_TIFS.md` (final quality).

Consequences:
- Clean: no reviewer at TIFS spends further time on results the authors know
  are affected; no editor learns of the defect from a third party.
- The withdrawal is author-initiated and cites the shared-codebase
  correction; this is the strongest possible position for a future
  resubmission of a corrected sibling.
- Cost: loses the submission's place in the TIFS queue; a corrected sibling
  starts over, and its correction work (its own rebuild) is unfunded time.
- Timing constraint: to keep the narrative accurate, the withdrawal should be
  SENT before or simultaneously with the v3 arXiv replacement going public.

## Branch C — keep the TIFS submission alive; coordinate a correction

**Artifact:** `packages/sibling/ARXIV_V3_COMMENT_COEXIST.txt` — the v3
correction-note wording drafted so it does not contradict an active TIFS
submission (it speaks only about THIS paper's versions and the shared
lineage, and says a correction process for the companion "is underway and
disclosed to editors of both venues").

Consequences:
- Requires actually disclosing to the TIFS editor immediately (the v3 note
  asserts it), then either a major-revision request or an editor-directed
  withdrawal anyway — the decision is deferred to the editor, not avoided.
- Risk: if a TIFS referee finds the v3 confession before the disclosure
  lands, the authors' position degrades from "self-corrected" to "caught".
- Only defensible if the sibling's headline results can be shown unaffected
  by A1–A4 quickly, which has NOT been established (no manifested runs cover
  the sibling's tables).

## Standing recommendation (recorded, not executed)

**Withdraw before v3 goes public (Branch W).** The sibling's results rest on
the same unaudited lineage; nothing manifested supports its tables; and the
cost asymmetry is decisive — Branch W costs a queue position, Branch C risks
the credibility of both papers and of the correction itself. The
click-by-click sequencing (withdrawal first, v3 replacement second) is in
`HUMAN_ACTIONS.md`. If the operator chooses Branch C instead, use the
coexistence wording for the v3 Comments field and send the TIFS editor
disclosure the same day — both texts are ready.
