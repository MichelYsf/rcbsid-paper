# ZENODO_DEPOSIT_SHEET — version 2.2.0 STAGED 2026-09-09, DOI reserved, nothing uploaded

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

> **This sheet stages version 2.2.0 as a New version on record 22638195. Its
> version DOI is reserved, not published: 10.5281/zenodo.22673735.** The
> propagation round ran on 2026-09-09, before the publish: `CITATION.cff`, the
> README, the artifact access strategy, the DTRAP editor note and
> prior-appearance note, the cover letter, every sheet, the named arXiv
> variant's availability sentence, the companion's v2 correction note and the
> canonical lineage sentence in all five canon venues now cite 2.2.0. **None
> of those citations resolves until you publish**, so publishing is the next
> outward action (Step 9). The provenance-limitation canon is deliberately
> untouched; see the note under Step 0.

Assembled 2026-09-09 against commit **`10aa1bd19f4672d3e821f3b1624929002be76a12`**, the
packaging commit whose tree holds the five files of Step 2 byte-for-byte as
staged (their SHA-256 values are recorded there). The packaging commit moved twice on
2026-09-09 and 224d130 is no longer it: the DOI propagation changed
`README.md`, `CITATION.cff` and two scripts, and the audit fixes that followed
changed three more scripts and added `scripts/check_tarball_anonymity.py`. All
of those ship inside the code zip, which is why it is now 145 entries rather
than 144. This sheet is committed one commit ahead of the packaging commit,
and changes no file it names. If you rebuild anything
after that, run `git rev-parse HEAD` on a clean tree and update Step 2 and
Step 7 before uploading.

> **Why the checksums move even when nothing does.** Zip and gzip store a
> timestamp per entry, and pdflatex stamps a creation date, so rebuilding
> produces different bytes from identical inputs. After the rebuild of
> 2026-09-09 that closed the provenance-canon counts, all five deposit files
> were compared against the previous build entry by entry: every entry of the
> code zip and of the manifests bundle was byte-identical, and the three data
> files did not move at all. Only the archives' embedded timestamps changed,
> which is why row 1 and row 2 of Step 2 carry new SHA-256 values for
> unchanged content. Read Step 2 off the tree at the commit named above; do
> not carry a checksum over from an earlier revision of this sheet.

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
across the DTRAP editor note, the arXiv v3 comment and this sheet. **It now
describes this deposit and no longer version 2.0.0's**: twenty-seven of the
thirty-three live run manifests, two of them irreducible, the other
twenty-five left as they are. Those three counts were read from
`packages/zenodo/manifests_bundle.zip` itself, by parsing each live
manifest's `git_commit` field, not from any document that quotes them.

> **That staleness is now closed.** From version 2.0.0 until 2026-09-09 the
> canon opened "Nineteen of the twenty-five live run manifests in this record"
> and closed on "the other seventeen", figures that were true of 2.0.0 and
> were carried forward unchanged through 2.1.0 and into this staging. They were
> corrected on 2026-09-09 to twenty-seven of thirty-three, two irreducible and
> the other twenty-five, verified by parsing every live manifest in
> `packages/zenodo/manifests_bundle.zip`. The two named CICIDS run ids, the
> decommissioned EC2 Linux instance, CI-16, the ancestry argument and the
> reason the rest were not re-run are carried verbatim; only the three counts
> moved. The canon is 1,009 characters and byte-identical across the five
> venues. **A published record still carries the old figures**: version 2.0.0's
> description was true when written, and version 2.1.0's was not, since that
> deposit held thirty-one live manifests of which twenty-five ran dirty.
> Metadata on a published Zenodo version stays editable, so 2.1.0's
> description can be corrected in place; its files cannot.

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

## Step 2 — Files (all five in `packages/zenodo/`, rebuilt 2026-09-09; the
DOI propagation of that date changed only the code zip, and the other four
are byte-identical to what the pre-deposit round staged)

`manifests_bundle.zip` is built by `python scripts/build_zenodo_package.py`
with entries relative to the bundle root and no wrapping directory, because
`README.md` tells a downloader to extract it *into* `results/manifests/`. Do
not re-zip it by hand. The bundle holds every live manifest (33, plus the
macro index) and every retired one (60, with the retirement README),
including the two that this round's document regenerations created.

| # | file | size | sha256 |
|---|---|---|---|
| 1 | `rcbsid_rebuild_code.zip` (145 entries, 1,264,599 B unzipped) | 448,411 B | `c7e6c4aae6106e06368e92f56742c9ec44475e500093db8da5c9f8da1cf6b55e` |
| 2 | `manifests_bundle.zip` (95 entries, 966,981 B unzipped) | 171,747 B | `2b1ff2fa78c9086105efc02ed84824231a0a2a322f2c7466df648734ee095cfa` |
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
2.2.0 adds over 2.1.0, and with the canonical DOI-lineage sentence extended to
name 2.2.0. That lineage canon is now two sentences, 689 characters, and is
byte-identical across the five canon venues after whitespace normalisation.
The provenance-limitation paragraph is the other canon and is **unchanged**;
the note under Step 0 records what it does and does not describe. **Paste the
text below verbatim.**

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

Provenance limitation, stated precisely. Twenty-seven of the thirty-three live
run manifests in this record executed on a working tree that carried
uncommitted edits, so the exact source state for those runs is not
recoverable. Every base commit they name resolves and is an ancestor of the
published branch, so the generating code is reachable at commit granularity;
what is missing is the uncommitted delta at run time. Two of the twenty-seven
are irreducible: the CICIDS construction-contrast arms, run ids
s4_construction_contrast_20260819T064027_20f44694 and
s4_construction_contrast_20260819T090813_46e9bd32, ran on an EC2 Linux
instance that has since been decommissioned, and re-running them on the
author's Windows machine would change published numbers -- the cross-platform
difference this project records as corrected incident CI-16. They were
therefore not re-run, and the other twenty-five were deliberately left as they
are rather than regenerate a subset that would not change this disclosure.

Earlier versions of the associated manuscript (arXiv:2605.24696 v1 and v2)
reported results produced under a composite benchmark construction and described
a scoring rule the released code did not implement. This package is the rebuild
from that audit. Earlier manuscript versions cite doi:10.5281/zenodo.20074590, which resolves to version 1.0.0 of the artifact record, deposited 2026-05-07 and containing the pre-audit codebase; this corrected rebuild is published in the same record lineage, first as version 2.0.0 (doi:10.5281/zenodo.22213264) and then, with the manifests of the pre-submission review rounds added, as version 2.1.0 (doi:10.5281/zenodo.22638195), each superseding the one before it. The version accompanying this manuscript is 2.2.0 (doi:10.5281/zenodo.22673735), which adds the revisions of the final pre-submission review round and supersedes 2.1.0, and Zenodo displays a newer-version notice on each superseded record.
```

## Step 6 — License (inherited, unchanged)

| field | value |
|---|---|
| License | **Apache-2.0** (`LICENSE` in the repository, and inside the code zip) |
| Access right | Open Access |

## Step 7 — Related identifiers

| relation | identifier | note |
|---|---|---|
| **is derived from** | `https://github.com/MichelYsf/rcbsid-paper/tree/10aa1bd19f4672d3e821f3b1624929002be76a12` | **the commit, not the branch**: the one commit whose tree holds the five Step 2 files byte-for-byte as staged; replaces the inherited 389540f… link, which belongs to 2.1.0 |
| is supplement to | `arXiv:2605.24696` | inherited, unchanged |

Zenodo records the version relation to 2.1.0 itself; do not add it by hand.

## Step 8 — Version and keywords

| field | value |
|---|---|
| Version | `2.2.0` |
| Keywords | inherited, unchanged: intrusion detection; streaming evaluation; benchmark stream construction; evaluation methodology; reproducibility; provenance |

## Step 9 — Publish, then

0. **Done 2026-09-09, before the publish.** The DOI was reserved and
   propagated: `CITATION.cff` carries doi 10.5281/zenodo.22673735, version
   2.2.0, date-released 2026-09-09; the canonical lineage sentence in all five
   canon venues names 2.2.0; the README, the artifact access strategy, the
   DTRAP editor note and prior-appearance note, the cover letter in both
   renders, every sheet, the named arXiv variant's availability sentence and
   the companion's v2 correction note cite 2.2.0. Nothing in the repository
   now cites 2.1.0 as the accompanying artifact, and every one of those
   citations is unresolvable until you publish.
1. Confirm against the Zenodo API that the published version DOI is exactly
   10.5281/zenodo.22673735 and that the five files are at the Step 2
   sizes. **If Zenodo mints a different DOI, stop**: the whole repository
   already cites the reserved one, and it would all have to be re-propagated
   before anything goes to DTRAP or arXiv.
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
