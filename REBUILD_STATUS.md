# CALIBURN honest rebuild — status

- **State**: STAGE 1 COMPLETE (streams built and gated); Stages 2-8 NOT STARTED
- **Branch**: `rebuild/honest-v1`; recoverable tag `verified-artifacts-2026-08`
- **Cloud spend so far**: $0.00 of the $12.00 cap (all Stage 0-1 work ran on the laptop)
- **Last update**: 2026-08-18

## Gate results

| gate | result |
|---|---|
| Stage 0 reproduction (bit-for-bit deterministic refs) | PASSED, manifest `stage0_reproduction_checks_20260817T221558_53c31fe7` |
| provenance self-test (orphan fails / manifested passes) | PASSED |
| provenance gate: absent target, vacuous scan | **FIXED THEN PASSED** (see corrected incident) |
| Stage 1 monotonic-timestamp gate (all 4 streams) | PASSED |
| full test suite | 50 passed |

## Corrected incident — the provenance gate could be bypassed

`check_provenance.py` printed `GATE PASSED` and exited 0 when a manuscript
target was absent, and when zero targets were supplied. A wrong or renamed
path would therefore have greened the governing rule instead of failing it.
Fixed in `419125e`; three regression tests added. **The Stage 0 "gate green"
recorded on 2026-08-17 must be read as "self-test only", not "gate proven
sound".** History retained; nothing rewritten.

## Stage 1 outcome (see `findings_streams.md`)

LITNET-2020 admits **no coherent global chronology** — its three captures are
temporally disjoint — so it is now evaluated as three per-attack-type streams,
never a composite. CICIDS2017 sorts coherently across its capture week.

Two results that invalidate prior framing:
- CICIDS2017 test prevalence in true chronological order is **68.235%**, not
  the 22.06%/25.24% of the interleaved construction. The "moderate prevalence
  regime" characterisation does not survive.
- LITNET attack runs are near-isolated single flows (median 1, max 2-20);
  CICIDS2017 has sustained attacks (median 2, p90 70, max 2522). Claims about
  sustained detection or burn-rate escalation are untestable on LITNET.

## Not started (honest)

Stages 2-8: bug fixes with before/after runs; score/threshold prose honesty;
the full rerun matrix under provenance; the verified contributions; the
corrected-BOCPD ablation; the ACM manuscript rebuild; artifact preparation.
No manuscript numbers exist yet, and none may be drafted until produced by a
manifested run.
