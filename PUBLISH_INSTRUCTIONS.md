# PUBLISH_INSTRUCTIONS — how to publish the rebuilt artifact (nothing has been published)

Per the rebuild's absolute prohibitions, nothing was posted to arXiv, Zenodo,
or any submission system. Everything is PREPARED; the click-by-click execution
lives in `HUMAN_ACTIONS.md`. This file records what each package is and the
invariants that must hold before any of them leaves this machine.

## Invariants (check all five before publishing anything)

```bash
python scripts/check_provenance.py        # gate + claim ledger: must end GREEN twice
python scripts/check_manuscript_macros.py # must PASS
python -m pytest -q                       # full suite: must pass
```

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
   **As of 2026-08-27 the tree is clean and pushed; 17 manifests still carry
   the uncommitted-tree marker, two of them irreducibly** (see
   `PUBLISH_PREP_REPORT.md`).

## The packages (`packages/`)

- **arxiv_v3/** — the v3 replacement for arXiv:2605.24696: source tarball
  (`arxiv_v3_source.tar.gz`, compiles standalone: main.tex + numbers.tex +
  references.bib + the two generated tables copied in), the Comments-field
  text in both sibling-decision variants, and the title-change note.
- **zenodo/** — the first (v2.0.0) deposit bundle: code + scripts + manifests
  + logs + stream hashes, with `zenodo_metadata.md` ready to paste. Minting
  this DOI, then writing it into CITATION.cff, is a HUMAN_ACTIONS step.
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
constraint was void and is removed. Zenodo before DTRAP submission is preferred
(the cover letter can then cite the minted DOI), but not required — DTRAP's anonymous
artifact channel works without it.
