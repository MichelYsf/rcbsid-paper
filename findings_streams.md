# findings_streams — natural-order evaluation streams (Stage 1)

Generating run: `stage1_natural_streams_20260818T114117_285582fc` at commit `419125e91dd3`.
Every number below is a provenance macro from that manifest.

## What changed and why

The prior artifact evaluated **label-aware round-robin composites**: LITNET-2020's
three captures were interleaved into one stream, and UNSW-NB15 was a seeded
permutation. Neither is a chronology. Stage 1 abandons both as primary evaluation.

**LITNET-2020 admits no coherent global chronology.** Its three captures are
temporally *disjoint*: udp_flood 2019-03-06 (~4 min), spam 2019-12-09..2020-01-06
(~27 days), blaster_worm 2020-01-25 (~1.6 min). A global timestamp sort merely
re-blocks them. Per the rebuild rule, LITNET is therefore evaluated as **three
separate per-attack-type streams**, never a manufactured composite.
CICIDS2017 is a single capture week, so a global chronological sort is coherent.

## Constructed streams (monotonic-timestamp gate passed for all)

| stream | rows | overall prev | TEST prev | test attacks | run len med/p90/max | span |
|---|---|---|---|---|---|---|
| `litnet2020 / blaster_worm` | 500,000 | 0.6562% | **3.544%** | 2,658 | 1 / 2 / 5 | 1.6 min |
| `litnet2020 / spam` | 500,000 | 0.0276% | **0.176%** | 132 | 1 / 1 / 2 | 39,122.2 min |
| `litnet2020 / udp_flood` | 500,000 | 14.9384% | **15.7747%** | 11,831 | 1 / 2 / 20 | 4.0 min |
| `cicids2017 (whole week)` | 1,600,000 | 22.0601% | **68.235%** | 163,764 | 2 / 70 / 2522 | 6,246.7 min |

SHA-256 of each constructed stream is recorded in the manifest and in a
`.sha256` sidecar next to each file.

## Natural order versus the old interleaved construction

| quantity | old interleaved | natural order | consequence |
|---|---|---|---|
| CICIDS2017 test prevalence | 25.240% | **68.235%** | the paper's "moderate 22.06% regime" does not survive; in true chronological order the held-out slice is a HIGH-prevalence regime |
| CICIDS2017 test attacks | 60,575 | 163,764 | |
| LITNET test prevalence | 6.498% (composite) | 15.7747% udp_flood / 3.544% blaster_worm / 0.176% spam | the single "5.2% rare-attack regime" is an artifact of pooling three unrelated captures |

## Benchmark microstructure — the finding that constrains every claim

CICIDS2017 contains genuinely sustained attacks: run lengths median 2, p90 70, max 2522. All three LITNET streams do not: median 1, max 20 (udp_flood), max 5 (blaster_worm), max 2 (spam).

LITNET attacks are near-isolated single flows. Any claim about *sustained* attack
detection, burn-rate escalation over time, or dwell-time behaviour is untestable on
LITNET and must be confined to CICIDS2017.

Two LITNET captures span minutes (udp_flood ~4.0, blaster_worm ~1.6). Multi-window
burn-rate alerting with 60/360/4320-minute windows is **undefined** on them; only
spam (~27 days) admits such windows at all.

## Retained, explicitly relabelled

The interleaved streams are kept ONLY as a labelled synthetic stress protocol
(`data/raw/{litnet2020,cicids2017}/*_labeled.csv`), never as primary evaluation.
