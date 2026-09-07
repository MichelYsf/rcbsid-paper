# ZENODO_DEPOSIT_SHEET — version 2.1.0 STAGED 2026-09-07, nothing uploaded

> **Version 2.0.0 is LIVE and frozen.** Published 2026-08-31: version DOI
> **10.5281/zenodo.22213264**, concept DOI 10.5281/zenodo.20074589,
> superseding v1.0.0 (10.5281/zenodo.20074590). Verified against the Zenodo
> API on 2026-08-31: title, creator with ORCID 0009-0000-0664-8228, and its
> five files at their staged sizes (rcbsid_rebuild_code.zip 363,694 B;
> manifests_bundle.zip 143,621 B; EXPECTED_SHA256.txt 932 B;
> construction_contrast.csv 4,755 B; prevalence_sweep_cicids.csv 48,587 B).
> Nothing about that version changes.

> **This sheet stages version 2.1.0 as a New version on record 22213264.**
> It has not been uploaded. Its version DOI is minted when you publish and is
> not known yet; every place that must carry it is listed in Step 9.

Assembled 2026-09-07 against commit **`b9f32addaf60a927e4c9d57b1c7280da2867501d`**, the
packaging commit whose tree holds the five files below byte-for-byte; this
sheet is committed one commit ahead of it, which is harmless (the files are
identical in both). If you rebuild anything after that, run `git rev-parse
HEAD` on a clean tree instead.

> **Immutability, before you start.** On Zenodo, **the files are frozen at
> publication**; you cannot add, replace or remove one afterwards, only publish
> a further version with its own DOI. **Metadata (title, description, authors,
> keywords, related identifiers, version string) remains editable after
> publication.** The DOI is permanent. Confirm both behaviours in the UI
> before you press Publish.

---

## Step 0 — the decision, restated for 2.1.0

`python scripts/check_provenance.py --publish-ready` **exits 1**, on the same
point as before and by the same accepted decision:

- tree clean, HEAD pushed, every manifest's base commit resolves in the pushed
  history;
- **25 of the 31 live run manifests ran while the working tree carried
  uncommitted edits**: the 19 of 25 that version 2.0.0 disclosed, plus all six
  that 2.1.0 adds (`referee_bounded_analyses_20260906T182158_de69afab`,
  `bootstrap_block_robustness_20260906T200612_b7c847e1`,
  `ecod_batch_composition_20260907T061817_7d2ec490`, and the three
  `supplementary_macros_2026090…` derivation runs). Each records its base
  commit (ad01b8b, e76ee0b or d2742e1) with a dirty marker; each base commit
  is an ancestor of the pushed branch; none changed during its run.
- The two irreducible arms are unchanged (CI-16).

**DECIDED 2026-08-27, reaffirmed 2026-09-07: accept the dirty-tree manifests;
nothing is re-run.** The provenance-limitation paragraph in Step 5 is a canon
held byte-identical across the DTRAP editor note, the arXiv v3 comment and this
sheet; it describes the twenty-five live manifests of version 2.0.0 and stays
as it is. The paragraph 2.1.0 adds states the six new manifests plainly.

---

## Step 1 — New version of record 22213264

1. Open **doi:10.5281/zenodo.22213264** (version 2.0.0) signed in as the
   record's owner.
2. Click **New version**.
3. Zenodo carries the five 2.0.0 files into the draft. **Remove
   `rcbsid_rebuild_code.zip` and `manifests_bundle.zip` and upload the 2.1.0
   ones from `packages/zenodo/`.** `EXPECTED_SHA256.txt`,
   `construction_contrast.csv` and `prevalence_sweep_cicids.csv` are
   byte-identical to 2.0.0's (same SHA-256, Step 2); keeping the carried-over
   copies or re-uploading them gives the same record.

A new version pre-fills its metadata from 2.0.0. **Inherited fields that MUST
be changed:**

| inherited from 2.0.0 | change to |
|---|---|
| description | the Step 5 text (2.0.0's text plus one paragraph) |
| version `2.0.0` | `2.1.0` |
| related identifier *is derived from* `…/rcbsid-paper/tree/083df8acb6e48c2f403218ae765260584c3a2fdb` | the Step 7 commit link |

**Inherited and kept:** title (Step 3), resource type Software, creator
Youssef, Michel with ORCID 0009-0000-0664-8228, licence Apache-2.0, access
Open, keywords (Step 8), related identifier *is supplement to*
`arXiv:2605.24696`.

## Step 2 — Files (all five in `packages/zenodo/`, rebuilt 2026-09-07)

`manifests_bundle.zip` is built by `python scripts/build_zenodo_package.py`
with entries relative to the bundle root and no wrapping directory, because
`README.md` tells a downloader to extract it *into* `results/manifests/`. Do
not re-zip it by hand. The bundle holds every live manifest (31, plus the
macro index) and every retired one (60, with the retirement README),
including all six manifests the referee rounds created and the one they
retired.

| # | file | size | sha256 |
|---|---|---|---|
| 1 | `rcbsid_rebuild_code.zip` (144 files) | 438,888 B | `34185b586ec157a87a7d3205db99e96da130c447ce035922d5d52da2cf11b1a6` |
| 2 | `manifests_bundle.zip` (93 entries, 939,967 B unzipped) | 168,084 B | `3ddab2d15db932f230e1d01f9d181c0b89c99d665d898d56a4013151893787c5` |
| 3 | `EXPECTED_SHA256.txt` (unchanged from 2.0.0) | 932 B | `6ebe8ad220ebf5b02e581e9dd0f5ad91a2c36c9a98cb5d129978f6a9bde7edc5` |
| 4 | `construction_contrast.csv` (unchanged from 2.0.0) | 4,755 B | `f3c94a988500b31ffd4b03c722fe6a8bfe8607d0a18360986df7f205cc06486e` |
| 5 | `prevalence_sweep_cicids.csv` (unchanged from 2.0.0) | 48,587 B | `ba096d1dbb34a81c93df97ba0d646f2654dcc3dc26769b1bb2995b485ad22759` |

Verified before staging: the code zip extracted with the bundle placed in
`results/manifests/` passes every gate check that applies outside a compiled
tree once the figures are re-rendered (`python scripts/make_figures.py`, as
the README says; the code zip carries no rendered figure PDF). **Files are
immutable after publication.**

## Step 3 — Title (inherited, unchanged)

```
Stream Assembly Is an Uncontrolled Treatment in Streaming Intrusion-Detection Benchmarks: Reproducibility Package
```

## Step 4 — Authors (inherited, unchanged)

| field | value |
|---|---|
| Family name | Youssef |
| Given name | Michel |
| ORCID | **0009-0000-0664-8228** |
| Affiliation | Independent Researcher |

## Step 5 — Description (paste verbatim)

The 2.0.0 description with one added paragraph (the second). The
provenance-limitation paragraph and the DOI-lineage sentence are canons and
are unchanged.

```
Reproducibility package for "Stream Assembly Is an Uncontrolled Treatment in
Streaming Intrusion-Detection Benchmarks".

Version 2.1.0 adds, over version 2.0.0, the material of the two referee-triage
rounds of 6 and 7 September 2026: the bounded referee analyses
(batch-controlled ECOD rescoring of the 78,000 shared held-out records,
moving-block bootstrap intervals for every reported margin and branch value,
the training and validation destinations of the 103,189 relocated attacks,
the imputation counts, and the paired cut-by-assembly sweep), the block-length
robustness rerun at 250 and 2,600 records, the ECOD batch-composition
experiment at fixed batch size and fixed model, the scripts and findings
documents of those runs, six live manifests and one retired manifest with its
reason, the supplementary macros derived from them, the deterministic figure
renderer with its figure manifest and a ninth gate check for figures, the
revised manuscript source (22 pages), the claim ledger, the bibliography audit,
and the referee triage and response-shelf records. No manifest of version
2.0.0 is changed. The six live manifests added here executed, like nineteen of
the twenty-five they join, on a working tree with uncommitted edits; each
records its base commit with a dirty marker.

Contents: the analysis code and tests, the LaTeX source of the manuscript, the
generated macro layer that every reported number resolves through, the full set
of run manifests (including retired manifests with their retirement reasons),
the sentence-level claim ledger, the provenance gate that fails the build on any
number without a manifest, and the two headline result tables.

Every measured value in the manuscript is generated by a script that writes an
archived run manifest in the same execution. An eight-check build gate fails on:
a number with no manifest; a macro two runs claim with different values; drift
between the derived macro index and the manifests; a typed literal anywhere in
the manuscript, its inputs, or any file the claim ledger cites; a derived value
that disagrees with the values printed beside it; inconsistent display width;
shell-escape damage in the LaTeX sources; and text typeset past the page measure.

Provenance limitation, stated precisely. Nineteen of the twenty-five live run
manifests in this record executed on a working tree that carried uncommitted
edits, so the exact source state for those runs is not recoverable. Every base
commit they name resolves and is an ancestor of the published branch, so the
generating code is reachable at commit granularity; what is missing is the
uncommitted delta at run time. Two of the nineteen are irreducible: the CICIDS
construction-contrast arms, run ids
s4_construction_contrast_20260819T064027_20f44694 and
s4_construction_contrast_20260819T090813_46e9bd32, ran on an EC2 Linux instance
that has since been decommissioned, and re-running them on the author's Windows
machine would change published numbers -- the cross-platform difference this
project records as corrected incident CI-16. They were therefore not re-run, and
the other seventeen were deliberately left as they are rather than regenerate a
subset that would not change this disclosure.

Earlier versions of the associated manuscript (arXiv:2605.24696 v1 and v2)
reported results produced under a composite benchmark construction and described
a scoring rule the released code did not implement. This package is the rebuild
from that audit. Earlier manuscript versions cite doi:10.5281/zenodo.20074590, which resolves to version 1.0.0 of the artifact record, deposited 2026-05-07 and containing the pre-audit codebase; this corrected rebuild is published as version 2.0.0 in the same record lineage (doi:10.5281/zenodo.22213264) and supersedes it, and Zenodo displays a newer-version notice on the superseded record.
```

## Step 6 — License (inherited, unchanged)

| field | value |
|---|---|
| License | **Apache-2.0** (`LICENSE` in the repository, and inside the code zip) |
| Access right | Open Access |

## Step 7 — Related identifiers

| relation | identifier | note |
|---|---|---|
| **is derived from** | `https://github.com/MichelYsf/rcbsid-paper/tree/b9f32addaf60a927e4c9d57b1c7280da2867501d` | **the commit, not the branch**; replaces the inherited 083df8a… link, which belongs to 2.0.0 |
| is supplement to | `arXiv:2605.24696` | inherited, unchanged |

Zenodo records the version relation to 2.0.0 itself; do not add it by hand.

## Step 8 — Version and keywords

| field | value |
|---|---|
| Version | `2.1.0` |
| Keywords | inherited, unchanged: intrusion detection; streaming evaluation; benchmark stream construction; evaluation methodology; reproducibility; provenance |

## Step 9 — Publish, then

1. Record the new version DOI in the header of this sheet.
2. `CITATION.cff`: the `doi:` field carries 10.5281/zenodo.22213264 (version
   2.0.0); change it to the 2.1.0 version DOI. Commit and push.
3. The named arXiv variant's artifact-availability sentence
   (`scripts/build_arxiv_variant.py`) names version 2.0.0 and its DOI. Update
   it to 2.1.0 before the arXiv v3 replacement is posted, rebuild the variant,
   and re-stage `packages/arxiv_v3/arxiv_v3_source.tar.gz`.
4. **Decision for you, not made here:** the canon DOI-lineage sentence shared
   by the DTRAP editor note, the arXiv v3 comment and this sheet names
   version 2.0.0 as "this corrected rebuild". Once 2.1.0 exists it is still
   true of 2.0.0 and silent about 2.1.0; changing it changes all five canon
   venues together, under binding rule 11's canon exemption.
5. Optional: annotate the 2.0.0 record's description with one sentence
   naming 2.1.0 as the version that carries the referee-round material.
   Metadata on 2.0.0 stays editable; its files stay frozen.

---

## Field mutability summary

| field | after publication |
|---|---|
| Files | **frozen**; new version only |
| DOI | **permanent** |
| Title, description, authors, keywords, related identifiers, license | editable |
| Version string | editable |
| Access right (open to closed) | restricted; treat as frozen |

The two irreversible commitments are **the files** and **the DOI**. Everything
in Step 5 can be corrected later; the manifests cannot.
