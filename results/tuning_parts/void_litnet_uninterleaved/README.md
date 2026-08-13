# VOID — un-interleaved LITNET-2020 grid partials

These 14 grid points were computed on a LITNET stream this harness built
WITHOUT running `scripts/interleave_litnet.py`. The stream was three
contiguous attack-type blocks, so the validation and test splits were pure
`spam` (6 and 132 attacks respectively) instead of the ~5-6.5% prevalence the
documented pipeline produces.

They are **not data**. They say nothing about LITNET-2020, about the
baselines, or about CALIBURN, and they must never be merged into results or
quoted. Every row carries VOID=True and a void_reason. They are kept only as
the record of a corrected incident.

The paper's own LITNET evaluation is unaffected and sound: a correctly
interleaved stream yields a test slice of 14,621 attacks in 225,000 rows
(6.498%).
