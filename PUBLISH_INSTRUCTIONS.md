# PUBLISH_INSTRUCTIONS — what each package is, and the invariants before it leaves

Zenodo versions 2.0.0 and 2.1.0 are published; nothing has gone to arXiv, to
DTRAP, or to any other submission system. The click-by-click execution lives
in `HUMAN_ACTIONS.md`, **which is the operative document and takes precedence
over this one wherever they differ**. This file records what each package is
and the invariants that must hold before any of them leaves this machine.

## Invariants (check all five before publishing anything)

```bash
python scripts/check_provenance.py        # gate + claim ledger: must end GREEN twice
python scripts/check_manuscript_macros.py # must PASS
python scripts/check_tarball_anonymity.py # shipped tarballs: must PASS
python -m pytest -q                       # full suite: must pass
```

The tarball check is not one of the nine gate checks and does not change that
count. It exists because the gate checks package *staleness* and the artifact
builder checks the *zip*, and neither looked inside a tarball: all three
shipped tarballs stored the author's machine username in their member headers,
where `tar tvf` prints it without extracting anything.

4. `paper/main.pdf` rebuilt from the current tree (three-pass pdflatex+bibtex,
   zero undefined references), and
5. `git status` clean, branch `rebuild/honest-v1` pushed. **Do not check this
   by eye — run it:**

   ```
   python scripts/check_provenance.py --publish-ready
   ```

   It also fails when a live run manifest ran on an uncommitted tree, which the
   eye cannot catch at all. Stated precisely (CI-35): the base commit in such a
   stamp *does* resolve, and every one recorded here is an ancestor of the
   pushed branch, so a reader reaches the code to commit granularity; what is
   lost is the uncommitted delta at run time. `zenodo_metadata.md` names the
   GitHub repo as an *is derived from* identifier on a deposit that cannot be
   withdrawn, so this is the invariant with no undo.
   **As of 2026-09-09, 27 of the 33 live run manifests carry the
   uncommitted-tree marker, two of them irreducibly.** The accepted decision
   and the disclosure wording are in `ZENODO_DEPOSIT_SHEET.md` Step 0 and
   Step 5. `--publish-ready` exits 1 on that count by design, so a non-zero
   exit here is expected and is not on its own a reason to stop.

## The packages (`packages/`)

- **arxiv_v3/** — the v3 replacement for arXiv:2605.24696: source tarball
  (`arxiv_v3_source.tar.gz`, compiles standalone: main.tex + numbers.tex +
  references.bib + the two generated tables copied in), the Comments-field
  text in both sibling-decision variants, and the title-change note.
- **zenodo/** — the deposit bundle, always staged as a **new version** in the
  lineage that begins at Zenodo record 10.5281/zenodo.20074590 (v1.0.0 of
  2026-05-07, the pre-audit artifact; the "first deposit" description that
  stood here was false, CI-36): code + scripts + manifests + logs + stream
  hashes. Version 2.0.0 was published 2026-08-31
  (doi:10.5281/zenodo.22213264) and version 2.1.0 after it
  (doi:10.5281/zenodo.22638195); both are frozen. **What is staged here now is
  version 2.2.0, DOI reserved and not yet published:
  doi:10.5281/zenodo.22673735, which `CITATION.cff` carries.** The five files,
  their sizes and checksums are in `ZENODO_DEPOSIT_SHEET.md` Step 2, which is
  the only place they are maintained.
- **dtrap/** — the double-anonymous submission: anonymized PDF and source
  zip, cover letter, artifact-access strategy, and the ORCID clarification
  reply. Portal verified fresh 2026-08-24: https://mc.manuscriptcentral.com/dtrap.
- **sibling/** — the arXiv v3 correction-note wording. Use the **no venue
  claim** variant. The withdrawal letter and both earlier note variants in this
  directory are **retired and void**: verification in the IEEE Author Portal on
  2026-08-27 established that no TIFS submission exists (see
  `SIBLING_DECISION.md`, CI-25). They are kept as a record, not as options.

## Ordering constraint

There is no withdrawal step and no venue to notify first; that ordering
constraint was void and is removed. **The Zenodo publish now comes first and
is required**, which is a change from the earlier "preferred but not
required" advice this section used to give. The reason is that the texts the
operator pastes into DTRAP now assert the deposit already exists and give its
DOI: the cover letter, the editor note, the prior-appearance note and the
portal questionnaire all name version 2.2.0 and doi:10.5281/zenodo.22673735.
That DOI is reserved, so it does not resolve until the record is published.
Submitting first would hand the editors a false statement and a dead link.
The order in `HUMAN_ACTIONS.md` governs.
