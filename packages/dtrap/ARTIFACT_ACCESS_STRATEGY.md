# Artifact-access strategy — DTRAP double-anonymous compliance

Verified fresh 2026-08-24 against dl.acm.org/journal/dtrap/author-guidelines
(via web search snapshot; the page itself blocks robots): submissions are
double-anonymous, prepared on the ACM template, submitted as PDF via
ScholarOne at `https://mc.manuscriptcentral.com/dtrap`. Manuscripts must
anonymize the title page and remove identifying acknowledgments.

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
  passed that check (160 files). No external links in the manuscript point
  to author-named resources: the Data Availability section says the artifact
  is provided through the submission system during review.

## After acceptance

Camera-ready replaces the anonymous availability sentence with the public
GitHub repository (branch `rebuild/honest-v1`) and the Zenodo DOI minted in
HUMAN_ACTIONS step 2; CITATION.cff travels with the public artifact only.
