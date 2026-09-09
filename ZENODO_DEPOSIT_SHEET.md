# ZENODO_DEPOSIT_SHEET — version 2.2.0 STAGED 2026-09-09, nothing uploaded

> **Versions 2.0.0 and 2.1.0 are LIVE and frozen.** 2.0.0 was published
> 2026-08-31 (version DOI **10.5281/zenodo.22213264**); 2.1.0 was published
> from this sheet's previous staging under the DOI it had reserved,
> **10.5281/zenodo.22638195**. Both sit under concept DOI
> 10.5281/zenodo.20074589, above v1.0.0 (10.5281/zenodo.20074590). Files on a
> published version are frozen. Nothing about either version changes here, and
> neither is touched by anything below.

> **2.1.0's five files, as this sheet staged them**, for the check in Step 1:
> rcbsid_rebuild_code.zip 439,133 B; manifests_bundle.zip 168,084 B;
> EXPECTED_SHA256.txt 932 B; construction_contrast.csv 4,755 B;
> prevalence_sweep_cicids.csv 48,587 B. They were **not** re-verified against
> the Zenodo API in this round, which contacted nothing; Step 1 has you read
> them off the record you are versioning.

> **This sheet stages version 2.2.0 as a New version on record 22638195, and
> no version DOI has been reserved for it yet.** Every document in this
> repository that carries a Zenodo DOI still cites 2.1.0
> (10.5281/zenodo.22638195), which is correct and resolvable today. The
> canonical lineage sentence and the provenance-limitation paragraph are
> canons and are deliberately unchanged in this round. Both are updated in a
> propagation round once 2.2.0's DOI is reserved, and **that round must run
> before you publish 2.2.0** (Step 9), or the deposit ships documents naming
> a superseded version as current.

Assembled 2026-09-09 against commit **`224d13023259fe98a33c49a73a2918ca99ac82ba`**, the
packaging commit whose tree holds the five files of Step 2 byte-for-byte as
staged (their SHA-256 values are recorded there). This sheet is committed one
commit ahead of it, which changes no file it names. If you rebuild anything
after that, run `git rev-parse HEAD` on a clean tree and update Step 2 and
Step 7 before uploading.

> **Immutability, before you start.** On Zenodo, **the files are frozen at
> publication**; you cannot add, replace or remove one afterwards, only publish
> a further version with its own DOI. **Metadata (title, description, authors,
> keywords, related identifiers, version string) remains editable after
> publication.** The DOI is permanent. Confirm both behaviours in the UI
> before you press Publish.

---

## Step 0 — the decision, restated for 2.2.0

`python scripts/check_provenance.py --publish-ready` **exits 1**, on the same
point as before and by the same accepted decision:

- tree clean, HEAD pushed, every manifest's base commit resolves in the pushed
  history;
- **27 of the 33 live run manifests ran while the working tree carried
  uncommitted edits**: the 25 of 31 that version 2.1.0 disclosed, plus the two
  that 2.2.0 adds (`s6_bocpd_corrected_ablation_20260909T060039_7766d5ff` and
  `s5_verified_contributions_20260909T060341_6108db2a`). Both record base
  commit 328ecf2 with a dirty marker, 328ecf2 is an ancestor of the pushed
  branch, and neither tree changed during its run. Both are document
  regenerations that recompute no detector arm and changed no macro value:
  the three Stage 6 manifests agree on all 27 shared macros and the two Stage
  5 manifests on all 16.
- The two irreducible arms are unchanged (CI-16).

**DECIDED 2026-08-27, reaffirmed 2026-09-09: accept the dirty-tree manifests;
no earlier run is repeated in order to clean its tree.** The
provenance-limitation paragraph in Step 5 is a canon held byte-identical
across the DTRAP editor note, the arXiv v3 comment and this sheet; it
describes the twenty-five live manifests of version 2.0.0 and stays as it is
in this round. The paragraph 2.2.0 adds states the two new manifests plainly
and says what they did not change.

---

## Step 1 — New version of record 22638195

1. Open **doi:10.5281/zenodo.22638195** (version 2.1.0) signed in as the
   record's owner.
2. **Before changing anything**, read the five carried-over file sizes off the
   record and check them against 2.1.0's staged sizes in the note at the top
   of this sheet. If any differs, stop: the record does not hold what this
   sheet believes it holds, and Step 2's "unchanged from 2.1.0" rows are then
   unsafe.
3. Click **New version**.
4. Zenodo carries the five 2.1.0 files into the draft. **Remove
   `rcbsid_rebuild_code.zip` and `manifests_bundle.zip` and upload the 2.2.0
   ones from `packages/zenodo/`.** `EXPECTED_SHA256.txt`,
   `construction_contrast.csv` and `prevalence_sweep_cicids.csv` are
   byte-identical to 2.1.0's, and to 2.0.0's (same SHA-256, Step 2); keeping
   the carried-over copies or re-uploading them gives the same record.

A new version pre-fills its metadata from 2.1.0. **Inherited fields that MUST
be changed:**

| inherited from 2.1.0 | change to |
|---|---|
| description | the Step 5 text (2.1.0's text with its second paragraph replaced) |
| version `2.1.0` | `2.2.0` |
| related identifier *is derived from* `…/rcbsid-paper/tree/389540f84bec5bea05ed57ebce3355825126481b` | the Step 7 commit link |

**Inherited and kept:** title (Step 3), resource type Software, creator
Youssef, Michel with ORCID 0009-0000-0664-8228, licence Apache-2.0, access
Open, keywords (Step 8), related identifier *is supplement to*
`arXiv:2605.24696`.

## Step 2 — Files (all five in `packages/zenodo/`, rebuilt 2026-09-09)

`manifests_bundle.zip` is built by `python scripts/build_zenodo_package.py`
with entries relative to the bundle root and no wrapping directory, because
`README.md` tells a downloader to extract it *into* `results/manifests/`. Do
not re-zip it by hand. The bundle holds every live manifest (33, plus the
macro index) and every retired one (60, with the retirement README),
including the two that this round's document regenerations created.

| # | file | size | sha256 |
|---|---|---|---|
| 1 | `rcbsid_rebuild_code.zip` (144 entries, 1,257,370 B unzipped) | 445,388 B | `f6eb13d9643320b1bc278994fac93a072874241fa6b2faed615c473c65317da9` |
| 2 | `manifests_bundle.zip` (95 entries, 966,981 B unzipped) | 171,747 B | `a3f601de3b847b6a5173b145c31111f8908f50080f3fd1432586a84524957786` |
| 3 | `EXPECTED_SHA256.txt` (unchanged from 2.1.0 and 2.0.0) | 932 B | `6ebe8ad220ebf5b02e581e9dd0f5ad91a2c36c9a98cb5d129978f6a9bde7edc5` |
| 4 | `construction_contrast.csv` (unchanged from 2.1.0 and 2.0.0) | 4,755 B | `f3c94a988500b31ffd4b03c722fe6a8bfe8607d0a18360986df7f205cc06486e` |
| 5 | `prevalence_sweep_cicids.csv` (unchanged from 2.1.0 and 2.0.0) | 48,587 B | `ba096d1dbb34a81c93df97ba0d646f2654dcc3dc26769b1bb2995b485ad22759` |

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

The 2.1.0 description with its second paragraph replaced by one stating what
2.2.0 adds over 2.1.0. The provenance-limitation paragraph and the canonical
DOI-lineage sentence are canons and are **unchanged in this round**: the
lineage sentence still ends at 2.1.0 and stays byte-identical across the five
canon venues. It gains 2.2.0 in the propagation round that follows the DOI
reservation, so **re-read this description after that round and before you
paste it** — pasting it as it stands would describe 2.2.0 with a lineage that
stops one version short.

```
Reproducibility package for "Stream Assembly Is an Uncontrolled Treatment in
Streaming Intrusion-Detection Benchmarks".

Version 2.2.0 adds, over version 2.1.0, the revisions of the final referee
round of 9 September 2026 and the manuscript source they produced, which is 23
pages. Eleven findings were verified against the code, the archived manifests
and the built PDF before anything was changed. The substantive results are
these: the discussion of the alternative reset formulation is restated in the
quantities that were actually measured, rather than as two failures in
opposite directions; the LITNET-2020 chronology claim is scoped to the three
captures this paper evaluates and attributed to this paper; the ECOD
reconciliation names the section of the source it reconciles against; the
run-length cap qualifier is carried into every statement of the method
identity; and the reported limitations are extended where the referee was
right. It also adds the two document regenerations of 9 September, which
brought the Stage 5 and Stage 6 findings documents onto that wording by
editing their generators and re-running them, and archived the result as two
further live manifests; neither run recomputed a detector arm and neither
changed a macro value. No manifest of version 2.0.0 or 2.1.0 is changed. The
two live manifests added here executed, like twenty-five of the thirty-one
they join, on a working tree with uncommitted edits; each records its base
commit with a dirty marker.

Contents: the analysis code and tests, the LaTeX source of the manuscript, the
generated macro layer that every reported number resolves through, the full set
of run manifests (including retired manifests with their retirement reasons),
the sentence-level claim ledger, the provenance gate that fails the build on any
number without a manifest, and the two headline result tables.

Every measured value in the manuscript is generated by a script that writes an
archived run manifest in the same execution. A nine-check build gate fails on:
a number with no manifest; a macro two runs claim with different values; drift
between the derived macro index and the manifests; a typed literal anywhere in
the manuscript, its inputs, or any file the claim ledger cites; a derived value
that disagrees with the values printed beside it; inconsistent display width;
shell-escape damage in the LaTeX sources; text typeset past the page measure;
and a figure whose inputs or generator changed or whose plotted values disagree
with the macro index.

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
from that audit. Earlier manuscript versions cite doi:10.5281/zenodo.20074590, which resolves to version 1.0.0 of the artifact record, deposited 2026-05-07 and containing the pre-audit codebase; this corrected rebuild is published in the same record lineage, first as version 2.0.0 (doi:10.5281/zenodo.22213264) and, with the manifests of the pre-submission review rounds added, as version 2.1.0 (doi:10.5281/zenodo.22638195), which supersedes it, and Zenodo displays a newer-version notice on each superseded record.
```

## Step 6 — License (inherited, unchanged)

| field | value |
|---|---|
| License | **Apache-2.0** (`LICENSE` in the repository, and inside the code zip) |
| Access right | Open Access |

## Step 7 — Related identifiers

| relation | identifier | note |
|---|---|---|
| **is derived from** | `https://github.com/MichelYsf/rcbsid-paper/tree/224d13023259fe98a33c49a73a2918ca99ac82ba` | **the commit, not the branch**: the one commit whose tree holds the five Step 2 files byte-for-byte as staged; replaces the inherited 389540f… link, which belongs to 2.1.0 |
| is supplement to | `arXiv:2605.24696` | inherited, unchanged |

Zenodo records the version relation to 2.1.0 itself; do not add it by hand.

## Step 8 — Version and keywords

| field | value |
|---|---|
| Version | `2.2.0` |
| Keywords | inherited, unchanged: intrusion detection; streaming evaluation; benchmark stream construction; evaluation methodology; reproducibility; provenance |

## Step 9 — Publish, then

0. **Before you publish.** Reserve the 2.2.0 version DOI in the draft, then
   run the propagation round with it. Every document in this repository that
   carries a Zenodo DOI still cites 2.1.0: `CITATION.cff`, `README.md`, the
   canonical lineage sentence in all five canon venues, the DTRAP editor
   note, the cover letter, every sheet, the named arXiv variant's
   artifact-availability sentence, and the companion's v2 correction note.
   None of that is wrong today, because 2.1.0 is published and resolvable;
   all of it becomes wrong the moment 2.2.0 exists and supersedes it.
   Publishing first is the one ordering this sheet cannot repair afterwards
   for the manuscript source already shipped inside DTRAP and arXiv copies.
1. Confirm against the Zenodo API that the published version DOI is exactly
   the one you reserved and that the five files are at the Step 2 sizes. If
   Zenodo minted a different DOI, stop and re-propagate before going further.
2. Optional: annotate the 2.1.0 record's description with one sentence
   naming 2.2.0 as the version that carries the final referee round's
   manuscript. Metadata on 2.1.0 stays editable; its files stay frozen.

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
