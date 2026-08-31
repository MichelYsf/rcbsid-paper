# Zenodo new-version metadata — ready to paste

**Corrected 2026-08-31 (CI-36): this is a NEW VERSION of the existing record
doi:10.5281/zenodo.20074590** (v1.0.0, deposited 2026-05-07, the pre-audit
codebase; concept DOI 10.5281/zenodo.20074589). The note that stood here
declared it "the FIRST deposit" — overriding the F-scope's own "new
version" wording — after finding only a placeholder DOI in the repository's
history; a repo search is not a registrar query. **The operative checklist is
`../../ZENODO_DEPOSIT_SHEET.md`; use it.** This file is retained as a
historical staging note only.

- **Upload type:** Software
- **Title:** Stream Assembly Is an Uncontrolled Treatment in Streaming Intrusion-Detection Benchmarks: Reproducibility Package
  (honest rebuild v2.0.0)
- **Authors:** Youssef, Michel (ORCID 0009-0000-0664-8228)
- **License:** Apache-2.0
- **Version:** 2.0.0-honest-rebuild
- **Related identifiers:**
  - `arXiv:2605.24696` — "is supplement to"
  - `https://github.com/MichelYsf/rcbsid-paper` — "is derived from",
    branch `rebuild/honest-v1`
- **Keywords:** intrusion detection; streaming evaluation; benchmark
  construction; attack prevalence; reproducibility; provenance

**Description (paste as-is):**

> Reproducibility package for the rebuilt manuscript "Stream Assembly Is an Uncontrolled Treatment in Streaming Intrusion-Detection Benchmarks"
> (a corrected replacement of
> arXiv:2605.24696 v1/v2). Contains the analysis code, stream-construction
> scripts with line-ending-normalised SHA-256 verification, every archived
> run manifest (including retired manifests with their retirement reasons),
> the generated macro layer, the sentence-level claim ledger, the
> provenance gate that fails the build on any number without a manifest,
> and the full corrected-incident history. Earlier
> versions of the associated manuscript reported results produced under a
> composite benchmark construction and described a scoring rule the code
> did not implement; this package is the rebuild from the audit that
> established both. Raw benchmark data is not redistributed; the scripts
> download the public captures (Engelen-corrected CICIDS2017, LITNET-2020)
> and verify reconstruction hashes.

**Files to upload (all in this directory):**
1. `rcbsid_rebuild_code.zip` — code, tests, paper source, findings, at the
   archived commit
2. `manifests_bundle/` (zip it as `manifests_bundle.zip` before upload) —
   every run manifest incl. `superseded/` and its retirement reasons.
   **A downloader must extract this into `results/manifests/` inside the code
   zip before running the provenance gate**; the code zip deliberately carries
   no manifests, so without this step every number reports as an orphan.
3. `EXPECTED_SHA256.txt` — the committed stream expectation
4. `construction_contrast.csv`, `prevalence_sweep_cicids.csv` — headline
   result tables
