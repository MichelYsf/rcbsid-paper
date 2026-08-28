# Stream Assembly Is an Uncontrolled Treatment in Streaming Intrusion-Detection Benchmarks — reproducibility package

This repository is the artifact for the rebuilt manuscript in `paper/main.tex`
(branch `rebuild/honest-v1`). It exists in its present form because earlier
versions of this work (arXiv:2605.24696 v1/v2) reported results produced under
a composite stream construction and described a scoring rule the code did not
implement. An adversarial review and a line-by-line audit established both;
this package is the rebuild from that audit. The correction history is not
hidden: `SCOPE_DECISIONS.md` records the binding scope rules and every
**numbered corrected incident** (the count is a record of the process, not a
quality claim, so none is quoted), `AUDIT_FINDINGS.md` records the audit (A1–A13), and
`SUPERSEDED.md` lists every stale artifact class so nothing old can be
mistaken for current.

## What the paper shows

1. **The construction contrast** (`findings_contrast.md`). On CICIDS2017, the
   identical 1,600,000-record multiset evaluated in true timestamp order versus
   day-of-week round robin: held-out prevalence moves 68.235% → 25.240%, the
   held-out slices share only 32.5% of their records, and the ordering of the
   two deterministic methods (ECOD vs the evaluated detector) inverts. The
   ranking change is a rotation (Kendall τ = −0.333), not a reversal.
2. **The pooling identity on LITNET-2020**. The composite's single 6.498%
   prevalence is the equal-budget mixture of three disjoint captures spanning
   0.176%–15.775%; it is a property of assembly, not of any capture.
3. **Method identity** (`findings_score_threshold.md`). The evaluated
   detector's run-length posterior equals the hazard rate for any data; the
   system is prequential global-Gaussian tail scoring. The textbook repair
   saturates the score and detects nothing (`findings_bocpd_ablation.md`) —
   both variants are degenerate, in opposite directions.
4. **Findings that cut against the detector, stated as findings**: batch LOF
   beats it 0.8632 vs 0.5450 on the identical natural-order slice, and its
   lift over the chance floor goes negative at 64% prevalence
   (`findings_prevalence.md`).

## The governing rule

**No number, table, or figure enters the manuscript unless it was produced by
a script in this repo that wrote, in the same execution, an archived run
manifest** (git commit, config hash, input SHA-256, seed, environment hash,
timestamps, output paths). Enforcement:

- `scripts/provenance.py` — the manifest spine; manifests live in
  `results/manifests/`, retired ones in `results/manifests/superseded/` with
  reasons.
- `scripts/emit_numbers_tex.py` — generates `paper/numbers.tex`; the
  manuscript contains no numeric literals, only macro references.
- `scripts/check_provenance.py` — fails the build on orphans, on macros two
  runs claim with different values, and on drift between the derived macro
  index and the manifests behind it.
- `scripts/check_manuscript_macros.py` — every macro the manuscript uses must
  be defined.
- `CLAIM_LEDGER.md` — every abstract/introduction sentence mapped to its
  generating run; ledger entries are gate-checked.

## Reproducing

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
python -m pytest -q                          # full test suite
python scripts/check_provenance.py           # the gate (repository only)

# From an extracted ARTIFACT rather than the repository, run the checks that
# do not need the build tree. Two of the eight are repository-only by
# construction: the overfull-hbox check reads paper/main.log, and the
# package-freshness check reads packages/ -- neither ships in an artifact, and
# both fail loudly rather than pass vacuously if you run them anyway.
python scripts/check_provenance.py --ledger  # claim ledger
python scripts/check_provenance.py --literals   # typed-literal scan
python scripts/check_provenance.py --decimals   # derived-value arithmetic
python scripts/check_provenance.py --controlchars

# ZENODO CODE ZIP ONLY: the run manifests are deposited separately, in
# manifests_bundle.zip. Extract it to results/manifests/ before running any
# check that resolves a macro, or every number reports as an orphan -- the
# manifests are absent, not missing.
```

Stream reconstruction from the original public captures:
`scripts/build_cicids_labeled.py`, `scripts/build_litnet_labeled.py`,
`scripts/build_natural_streams.py`; verify against the committed expectation
with `scripts/normalized_sha256.py` (hashes are line-ending-normalised —
raw-byte SHA-256 of CSVs is not portable across platforms).

Key experiment entry points, each writing manifests:
`scripts/run_construction_contrast.py` (Stage 4, the central experiment),
`scripts/make_findings_prevalence.py` (Stage 2, relabelled),
`scripts/verify_score_threshold.py` (Stage 3),
`scripts/run_bocpd_ablation.py` (Stage 6),
`scripts/verify_contributions.py` (Stage 5).

## Honest limitations, up front

Two benchmarks, one split rule for the headline contrast (70/15/15
chronological); a seven-point split-rule sensitivity sweep is reported
separately and finds the measured ordering changes with the cut. ECOD is
fitted benign-only and is
label-privileged. Stochastic baselines carry seed distributions or are
withheld — the HST/ECOD ordering flips with the seed in 2 of 2 cells where
extra seeds were bought. The CICIDS dataset is a 76.63% budgeted subsample
with a measured −2.15 pp prevalence bias. KitNET, xStream, RRCF, and
streaming iForest have wrappers in `src/baselines/` but **no manifested runs
in this rebuild** and therefore carry no numbers anywhere.

## Citation

See `CITATION.cff`. No Zenodo deposit exists yet; the first publication of
this artifact will mint the DOI.
