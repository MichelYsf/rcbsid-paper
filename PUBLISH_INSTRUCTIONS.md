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
5. `git status` clean, branch `rebuild/honest-v1` pushed.

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
- **sibling/** — the TIFS withdrawal letter and the coexistence wording;
  which one is used is the operator's decision (`SIBLING_DECISION.md`).

## Ordering constraint

If the sibling decision is Branch W (recommended), the TIFS withdrawal is
sent BEFORE the arXiv v3 replacement is announced, so the journal hears from
the author first. Zenodo before DTRAP submission is preferred (the cover
letter can then cite the minted DOI), but not required — DTRAP's anonymous
artifact channel works without it.
