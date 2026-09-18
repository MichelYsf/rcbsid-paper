# PUBLISH_INSTRUCTIONS — what each package is, and the invariants before it leaves

Zenodo versions 2.0.0, 2.1.0 and 2.2.0 are published. arXiv v3 of 2605.24696
and the companion's v2 were posted on 14 September 2026 and announced on 16
September 2026. The TMLR submission of 16 September 2026 was desk-rejected
on 18 September 2026 without review (historical). The venue is now ACM
DTRAP, not yet submitted. The click-by-click execution lives
in `HUMAN_ACTIONS.md`, **which is the operative document and takes precedence
over this one wherever they differ**. This file records what each package is
and the invariants that must hold before any of them leaves this machine.

## Invariants (check all five before publishing anything)

```bash
python scripts/check_provenance.py        # gate + claim ledger: GREEN except package freshness on the frozen Zenodo 2.2.0 zip (expected; never rebuild it)
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
   lost is the uncommitted delta at run time. `ZENODO_DEPOSIT_SHEET.md` Step 7
   names one GitHub commit as the *is derived from* identifier on a deposit
   that cannot be withdrawn, so this is the invariant with no undo; that
   commit must be pushed before the deposit.
   **As of 2026-09-09, 27 of the 33 live run manifests carry the
   uncommitted-tree marker, two of them irreducibly.** The accepted decision
   and the disclosure wording are in `ZENODO_DEPOSIT_SHEET.md` Step 0 and
   Step 5. `--publish-ready` exits 1 on that count by design, so a non-zero
   exit here is expected and is not on its own a reason to stop.

## The packages (`packages/`)

- **arxiv_v3/** — the v3 replacement for arXiv:2605.24696, posted on 14
  September 2026 (historical). The source staged for it was the named build in
  the TMLR template at commit 2bfb896; the listing's 108 KB source size does not
  match that 113,688 B tarball, so which exact file was uploaded is unverified.
  The tarball here now (`arxiv_v3_source.tar.gz`)
  is the acmart rebuild of 2026-09-18, which compiles standalone (main.tex +
  numbers.tex + references.bib + main.bbl + the two generated tables + the
  figures) and was not posted. `METADATA.md` carries the title-change note.
  The Comments field actually posted is a 411-character text recorded in
  `ARXIV_V3_SHEET.md`, not the NO VENUE CLAIM variant of
  `packages/sibling/ARXIV_V3_COMMENT.txt`; the two variants below that one are
  retired and false.
- **zenodo/** — the deposit bundle, always staged as a **new version** in the
  lineage that begins at Zenodo record 10.5281/zenodo.20074590 (v1.0.0 of
  2026-05-07, the pre-audit artifact; the "first deposit" description that
  stood here was false, CI-36): code + scripts + manifests + logs + stream
  hashes. Version 2.0.0 was published 2026-08-31
  (doi:10.5281/zenodo.22213264) and version 2.1.0 after it
  (doi:10.5281/zenodo.22638195); both are frozen. **Version 2.2.0 was
  published on 14 September 2026 as doi:10.5281/zenodo.22673735, which
  `CITATION.cff` carries; its files are frozen and this directory is not to
  be rebuilt.** The five files,
  their sizes and checksums are in `ZENODO_DEPOSIT_SHEET.md` Step 2, which is
  the only place they are maintained.
- **dtrap/** — the anonymous deliverables for the **ACM DTRAP** submission on
  ScholarOne (`SUBMISSION_CONSOLE.md`): the anonymous manuscript PDF, the
  anonymous source tarball and the anonymous artifact zip. The same directory
  served the TMLR submission of 16 September 2026, desk-rejected on 18
  September 2026 (historical). The cover letter, editor note and access
  strategy in this directory are current again as of 2026-09-18; the reviewer
  block is `SUGGESTED_REVIEWERS.md` at the repository root (console section 8).
- **sibling/** — the arXiv v3 Comments-field wording and the companion's v2
  source, posted on 14 September 2026 (both historical; the Comments actually
  posted with v3 are the shorter text `ARXIV_V3_SHEET.md` records). The withdrawal letter and both earlier note variants in this
  directory are **retired and void**: verification in the IEEE Author Portal on
  2026-08-27 established that no TIFS submission exists (see
  `SIBLING_DECISION.md`, CI-25). They are kept as a record, not as options.

## Ordering constraint — met, historical

There is no withdrawal step and no venue to notify first; that ordering
constraint was void and is removed. The requirement that the Zenodo publish
come first was met: version 2.2.0 was published on 14 September 2026 at
21:48 UTC, before the arXiv v3 posting that evening and before the TMLR
submission of 16 September, so every citation of doi:10.5281/zenodo.22673735
in the DTRAP documents and in the named arXiv variant resolves. The one
outward action left is the DTRAP submission. The order in `HUMAN_ACTIONS.md`
governs.
