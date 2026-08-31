# ZENODO_DEPOSIT_SHEET — EXECUTED 2026-08-31

> **The deposit is LIVE.** Published 2026-08-31 as **version 2.0.0** of the
> record lineage: version DOI **10.5281/zenodo.22213264**, concept DOI
> 10.5281/zenodo.20074589, superseding v1.0.0 (10.5281/zenodo.20074590).
> Verified against the Zenodo API on 2026-08-31: title, creator with ORCID
> 0009-0000-0664-8228, and all five files at their staged byte sizes
> (rcbsid_rebuild_code.zip 363,694 B; manifests_bundle.zip 143,621 B;
> EXPECTED_SHA256.txt 932 B; construction_contrast.csv 4,755 B;
> prevalence_sweep_cicids.csv 48,587 B). The published version string is
> **"2.0.0"** — the operator entered the plain string, not this sheet's
> "2.0.0-honest-rebuild"; every project reference is reconciled to "2.0.0".
> This sheet is retained below as the record of what was entered.

Assembled 2026-08-27 against commit **`083df8acb6e48c2f403218ae765260584c3a2fdb`**.
Nothing here has been uploaded. Work top to bottom; every value is final unless
marked **[decide]**.

> **Immutability, before you start.** On Zenodo, **the files are frozen at
> publication** — you cannot add, replace or remove one afterwards, only publish
> a *new version* with its own DOI. **Metadata (title, description, authors,
> keywords, related identifiers) remains editable after publication.** The DOI
> itself is permanent and cannot be withdrawn; a record can be hidden by
> Zenodo support only in exceptional cases. Confirm both behaviours in the UI
> before you press Publish — the field behaviours were written offline, while
> the record facts below (v1.0.0, both DOIs, file, dates) are account-verified
> as of 2026-08-31.

> **Which commit to name.** Use **`083df8acb6e48c2f403218ae765260584c3a2fdb`**.
> That commit contains the five deposit files byte-for-byte as they are on
> disk now — the sheets were updated afterwards, and updating a sheet cannot
> change what it names without moving the target again, so the tip may be one
> commit ahead. That is harmless: the artifacts are identical in both, and the
> named commit is the one whose tree the deposit was built from. If you have
> rebuilt anything since, run `git rev-parse HEAD` on a clean tree instead.

---

## Step 0 — the decision you must make first

`python scripts/check_provenance.py --publish-ready` **exits 1**, on one point:

- tree clean ✓, HEAD pushed ✓, every manifest's base commit resolves in the
  pushed history ✓
- **19 of 25 live run manifests ran while the working tree carried
  uncommitted edits.** Their base commit resolves and is an ancestor of the
  published branch; the exact source state at run time does not.
- **Two of those cannot be regenerated at all**: the CICIDS construction-contrast
  arms (`s4_construction_contrast_20260819T064027_20f44694`,
  `s4_construction_contrast_20260819T090813_46e9bd32`) ran 8,702 s and 8,644 s
  on an **EC2 Linux** instance that has been decommissioned. Re-running on this
  Windows machine would change published numbers — the cross-platform effect
  recorded as CI-16.

**DECIDED 2026-08-27: accept the nineteen. The seventeen are not re-run.** The
disclosure paragraph in Step 5 states this, and the identical wording is in the
DTRAP confidential editor note and the arXiv v3 correction note. Nothing else
blocks the sequence.

---

## Step 1 — New version, not New upload

**This is a new version of an existing record, not a first deposit.** Record
**doi:10.5281/zenodo.20074590** — version 1.0.0, "SLO-Aware Streaming Intrusion
Detection: Reproducibility Package", deposited 2026-05-07 — is published and
public. It holds the pre-audit codebase (one file,
`MichelYsf/rcbsid-paper-v1.0.0.zip`, 2,028,268 B, md5
f67dfa9c0203490a4de1648f6d6ce8c6) and is what arXiv:2605.24696 v1/v2 cite. The
concept DOI **10.5281/zenodo.20074589** groups every version of the record. (An
earlier revision of this sheet called the rebuild "the first deposit"; that was
false — CI-36.)

1. Open doi:10.5281/zenodo.20074590 signed in as the record's owner.
2. Click **New version**.
3. **Do NOT import the old file.** If the form carries
   `MichelYsf/rcbsid-paper-v1.0.0.zip` over from v1.0.0, remove it — the new
   version contains exactly the five files of Step 2 and nothing else.

A new version pre-fills its metadata from v1.0.0. **Inherited fields that MUST
be changed:**

| inherited from v1.0.0 | change to |
|---|---|
| title "SLO-Aware Streaming Intrusion Detection: Reproducibility Package" | the Step 3 title |
| description ("Initial release for CALIBURN paper submission to KeAi Cyber Security and Applications") | the Step 5 text |
| version `1.0.0` | `2.0.0` (published string; the sheet had said `2.0.0-honest-rebuild`) |
| keywords | the six in Step 8 |
| related identifier *is-supplement-to* `…/rcbsid-paper/tree/v1.0.0` | **replace** with the two rows in Step 7 |

**Inherited and kept:** resource type Software; creator Youssef, Michel —
confirm ORCID 0009-0000-0664-8228 is attached; licence Apache-2.0; access
Open.

## Step 2 — Files (upload in this order)

**`manifests_bundle.zip` is already built**, at
`packages/zenodo/manifests_bundle.zip`. Do **not** re-zip it by hand: its
entries are relative to the bundle root with no wrapping directory, because
`README.md` tells a downloader to extract it *into* `results/manifests/`. A
right-click "compress" on Windows wraps the folder and silently breaks that
step. If you need to rebuild it, run `python scripts/build_zenodo_package.py`,
which writes it. All five files upload as they are.

| # | file | size | sha256 |
|---|---|---|---|
| 1 | `rcbsid_rebuild_code.zip` | 363,694 B | `41dd667d57acd5dac9295a1510f6e66bf36c54b0eac5082c42d928f7c7c641fe` |
| 2 | `manifests_bundle.zip` (86 entries, 718,048 B unzipped) | 143,621 B | `cb021540cc85f061f64091a04a0c775360049402773409042ff973f023c9ce0a` |
| 3 | `EXPECTED_SHA256.txt` | 932 B | `6ebe8ad220ebf5b02e581e9dd0f5ad91a2c36c9a98cb5d129978f6a9bde7edc5` |
| 4 | `construction_contrast.csv` | 4,755 B | `f3c94a988500b31ffd4b03c722fe6a8bfe8607d0a18360986df7f205cc06486e` |
| 5 | `prevalence_sweep_cicids.csv` | 48,587 B | `ba096d1dbb34a81c93df97ba0d646f2654dcc3dc26769b1bb2995b485ad22759` |

All five are in `packages/zenodo/`. **Files are immutable after publication.**

## Step 3 — Title

```
Stream Assembly Is an Uncontrolled Treatment in Streaming Intrusion-Detection Benchmarks: Reproducibility Package
```

## Step 4 — Authors

| field | value |
|---|---|
| Family name | Youssef |
| Given name | Michel |
| ORCID | **0009-0000-0664-8228** |
| Affiliation | Independent Researcher |

Confirm the ORCID resolves before entering it (HUMAN_ACTIONS step 0). The
`-8224` variant is a 404 and appears nowhere in these packages.

## Step 5 — Description (paste verbatim)

```
Reproducibility package for "Stream Assembly Is an Uncontrolled Treatment in
Streaming Intrusion-Detection Benchmarks".

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

## Step 6 — License

| field | value |
|---|---|
| License | **Apache-2.0** (`LICENSE` in the repository, and inside the code zip) |
| Access right | Open Access |

## Step 7 — Related identifiers

| relation | identifier | note |
|---|---|---|
| **is derived from** | `https://github.com/MichelYsf/rcbsid-paper/tree/083df8acb6e48c2f403218ae765260584c3a2fdb` | **the commit, not the branch** — a branch name moves, and the deposit must name a state that cannot change |
| is supplement to | `arXiv:2605.24696` | the manuscript this package supports; v3 replacement is a later step |

These two rows **replace** the inherited *is-supplement-to*
`…/rcbsid-paper/tree/v1.0.0` row, which belongs to v1.0.0 (that git tag exists
on the remote, so the old record's link keeps resolving).

## Step 8 — Version and keywords

| field | value |
|---|---|
| Version | `2.0.0` (as published) |
| Keywords | intrusion detection; streaming evaluation; benchmark stream construction; evaluation methodology; reproducibility; provenance |

## Step 9 — Publish, then

1. **DONE** — the new version's DOI is **10.5281/zenodo.22213264**
   (not 10.5281/zenodo.20074590, which is v1.0.0, and not the concept DOI
   10.5281/zenodo.20074589, which groups all versions).
2. `CITATION.cff`: replace the explanatory `message:` block with a `doi:` field
   carrying that new version DOI.
3. Commit and push. Then, and only then, HUMAN_ACTIONS step 3 (arXiv).
4. **Optional, after publish — annotate the superseded record.** Metadata on
   v1.0.0 stays editable: open doi:10.5281/zenodo.20074590, choose Edit, and
   append one factual sentence to its description: "Version 1.0.0 is the
   pre-audit artifact evaluated in arXiv:2605.24696 v1/v2; it is superseded by
   version 2.0.0, the corrected rebuild." Its files stay frozen and public,
   and Zenodo shows the newer-version notice regardless.

---

## Field mutability summary

| field | after publication |
|---|---|
| Files | **frozen** — new version only |
| DOI | **permanent** |
| Title, description, authors, keywords, related identifiers, license | editable |
| Version string | editable |
| Access right (open → closed) | restricted; treat as frozen |

The two irreversible commitments are **the files** and **the DOI**. Everything
in Step 5 can be corrected later; the manifests cannot.
