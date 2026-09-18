# Artifact-access strategy — DTRAP double-anonymous compliance

Re-read 2026-09-18 at dl.acm.org/journal/dtrap/author-guidelines (first
verified 2026-08-24 from a search snapshot, when the page blocked robots):
submissions are double-anonymous, prepared on the ACM large-format template,
and submitted as PDF via ScholarOne at `https://mc.manuscriptcentral.com/dtrap`.
Manuscripts must anonymize the title page and remove funding sources and
personal acknowledgments. The venue is DTRAP again after the TMLR
submission of 16 September 2026 was desk-rejected on 18 September 2026
without review.

## During review

- **What reviewers get:** `artifact_anonymous.zip`, uploaded as
  supplementary material in ScholarOne alongside `manuscript_anonymous.pdf`.
- **What it contains:** analysis code (`src/`, `scripts/`, `tests/`), paper
  source with the generated macro layer, every run manifest including retired
  ones, the claim ledger, the findings documents, the corrected-incident
  history, headline CSVs, and the stream-reconstruction expectation hashes.
  Raw benchmark data is not included (public downloads; scripts fetch and
  hash-verify).
- **How anonymity is assured, mechanically:** the zip is produced by
  `scripts/build_anonymous_artifact.py`, which assembles from an allowlist,
  excludes the identity-bearing files (CITATION.cff, cloud-ops scripts that
  reference the named GitHub remote and machine paths), scrubs the machine
  username from archived manifest paths, and **fails the build if any token
  from the identity list survives anywhere in the zip**. The shipped zip
  passed that check (233 files at the 2026-09-18 build). No external links in the manuscript point
  to author-named resources: the Data Availability section says the artifact
  is provided through the submission system during review.

## After acceptance

Camera-ready replaces the anonymous availability sentence with the public
GitHub repository (branch `rebuild/honest-v1`) and the DOI of the
camera-ready Zenodo deposit, which will carry the final manuscript source.
The version published now is 2.2.0 (10.5281/zenodo.22673735). It carries
the manuscript source in the TMLR template of the earlier submission, and
its analysis code (src/, tests/ and the analysis scripts), its 95 run
manifests, its macro layer and its claim ledger are identical to those behind
the DTRAP submission; the manuscript source, the figure renderer's width
constants, three packaging scripts and the response shelf's section pointers
differ. CITATION.cff travels with the public artifact only.
