# PUBLISH_PREP_REPORT — 2026-08-27

Publish preparation for `rcbsid-paper`. No new analyses, no new claims. Nothing
was deposited, submitted, emailed, or sent. Two things left this machine, both
authorized: **a commit and a push to the project's own GitHub remote.**

---

## P1 — Commit and push

### What the 120 uncommitted paths were

| category | n | what |
|---|---|---|
| Modified | 68 | manuscript source and generated macro file, the eight gate scripts and the emitters, `SCOPE_DECISIONS.md` (CI-23…CI-33), `CLAIM_LEDGER.md`, `TRIAGE_REPORT.md`, the findings documents, and every staged package artifact |
| Untracked | 46 | 8 new scripts (`check_literals`, `check_decimals`, `check_control_chars`, `check_overfull`, `check_package_freshness`, `check_publish_ready`, `build_zenodo_package`, `emit_branch_binding_macro`), 33 manifest-bundle files, 5 LaTeX build products |
| Deleted | 6 | 5 manifests **moved** to `superseded/` (git recorded them as renames, R100) and one stale scratch file |

Plus **24 manifests present on disk but invisible to `git status`**, because
`.gitignore` carries `/results/`, and the manifests are force-added by
convention. Staging with `git add -A` alone would have silently published a
round with no provenance for its own runs. They were added with `git add -f`.

### Safety review before staging

Scanned every candidate file (581) for credentials, keys, tokens, password
assignments, private-key blocks, personal paths, emails and dataset content.

| pattern | hits | disposition |
|---|---|---|
| AWS access key id | 0 | — |
| AWS secret | 0 | — |
| Private key block | 0 | — |
| Generic token (ghp_, sk-, xox…) | 0 | — |
| Password/secret assignment | 0 | — |
| `.pem` | 5 | **filename references only** in cloud scripts; the key itself is gitignored and absent |
| Personal path `C:\Users\CYBERWIZARD` | 577 | a machine username, in manifest `declared_inputs` and logs. Already throughout the pushed history; the author is named in `CITATION.cff` and on the arXiv variant, so nothing is concealed by removing it. **Reported, not blocked.** |
| Emails | 12 | `michelyoussef@hotmail.com` (the author's, intended and public); `verdoliv@unina.it` and `dtrap-editors@acm.org` (public editorial addresses); `noreply@anthropic.com`; **`camich289@gmail.com`** in two EC2 bootstrap scripts and in `build_anonymous_artifact.py` — the last is deliberate, it is an identity token the scrubber searches for. All three files were **already in the pushed history**, so the commit changed nothing about exposure. |
| `data/raw`, `data/downloads`, `.venv`, `external/` | 0 staged | only `data/raw/natural/EXPECTED_SHA256.txt`, a 932 B hash list, which is intended |

**Nothing was withheld and nothing required a halt.** `.gitignore` gained the
LaTeX build products of the two package trees, and later `scratch_*`.

### Commands and results

```
git add -A && git add -f results/manifests/        # 139 files: 64 A, 69 M, 1 D, 5 R100
git commit -F <message>                            # exit 0
git push -u origin rebuild/honest-v1               # exit 0, 64ad3e8..e7aea84
```

Two further commits followed (the self-test fix and its correction; removal of a
scratch file committed by mistake).

| item | value |
|---|---|
| **Final commit** | **`083df8acb6e48c2f403218ae765260584c3a2fdb`** |
| **Remote** | **`https://github.com/MichelYsf/rcbsid-paper.git`** |
| Branch | `rebuild/honest-v1`, upstream set |
| Push | **succeeded**; `origin/rebuild/honest-v1` == local HEAD |
| Working tree | clean at the time of each `--publish-ready` run |

---

## P2 — Publish-ready gate: **NOT CLEARED. Halted as instructed.**

```
python scripts/check_provenance.py --publish-ready     # exit 1
```

| invariant | result |
|---|---|
| Clean working tree | **PASS** |
| HEAD published on the remote | **PASS** — `afbb2c9` == remote |
| No manifest recording an uncommitted tree | **FAIL** — 19 of 25 live run manifests |

### First: I had overstated the problem, and corrected it

The previous round's check said a `-dirty` stamp is *"not resolvable from the
public repository"*, and that wording had propagated into `HUMAN_ACTIONS.md`,
`PUBLISH_INSTRUCTIONS.md` and the operator's next action. **It is false.** A
stamp is `<sha>-dirty`; the base sha resolves normally. Checked after the push:

- **26 distinct base commits** across every manifest in the pushed tree
- **all 26 resolve, and all 26 are ancestors of `origin/rebuild/honest-v1`**

So a reader reaches the generating code at commit granularity. What `-dirty`
actually records is narrower and still real: the working tree carried
uncommitted edits at run time, so the *exact* source state is unrecoverable.
Corrected in all four places, and recorded as **CI-35**. **The check's verdict
was left unchanged** — correcting a false rationale is not relaxing a threshold,
and relaxing one to reach green is what this project forbids.

### What was resolved: 40 of the 62

`check_provenance.py --selftest` proved the gate resolves a manifested number by
writing a manifest holding a deliberately fake value (`SelfTestManifested =
0.4242`) — and never removed it. **Forty accumulated: 61% of the live provenance
store**, every one recording an uncommitted tree, and one of them leaking the
fake number into `paper/numbers.tex`, the generated file the manuscript reads
from. Nothing ever cited them and no manuscript sentence used the macro, so
nothing published was wrong.

The self-test now deletes its fixture and reindexes before returning; the forty
are retired to `superseded/`. `numbers.tex` went 564 → 563 macros. Recorded as
**CI-34**. Dirty manifests: **62 → 19**.

### The 19 that remain, and why

| run | wall | platform | regenerable here |
|---|---|---|---|
| `s4_construction_contrast_20260819T064027_20f44694` | 8,702 s | **Linux/AWS** | **NO** |
| `s4_construction_contrast_20260819T090813_46e9bd32` | 8,644 s | **Linux/AWS** | **NO** |
| `review_bounded_analyses_…131839_87899899` | 753 s | Windows | yes |
| `s3_score_threshold_verification_…084659_1e2b01b8` | 274 s | Windows | yes |
| `stage1_natural_streams_…114117_285582fc` | 192 s | Windows | yes |
| `s6_bocpd_corrected_ablation_…092655_a47acf51` | 155 s | Windows | yes |
| `s6_bocpd_corrected_ablation_…113456_f9869627` | 99 s | Windows | yes |
| `cicids_heldout_composition_…120420_ebb7c281` | 30 s | Windows | yes |
| `cicids_subsample_audit_…085704_3ed9b901` | 12 s | Windows | yes |
| `supplementary_macros` × 5, `s4_contrast_deliverables`, `s2_prevalence_relabelled`, `branch_binding_share`, `s5_verified_contributions`, `stage0_reproduction_checks` | 0 s each | Windows | yes |

**Two cannot be honestly re-stamped or regenerated.** The CICIDS
construction-contrast arms — the paper's central measurement, 4.8 hours combined
— ran on an **AWS Linux instance that has been decommissioned**. Re-running them
on this Windows machine would produce different values: this project has already
measured and recorded that cross-platform difference (**CI-16**; the round-3
review analyses reproduced the natural arm to 1.8e-05 rather than exactly). That
would change published headline numbers, which this round forbids. Re-stamping
them is not available either: `git_commit` means *HEAD at run time*, so writing
`afbb2c9` into them would assert that a run executed against a tree it never saw.

**This is the halt condition, and it is irreducible.**

### The other seventeen: a judgement, not an obstacle

They *could* be re-run here in about 25 minutes total. I did not, and this is
the judgement the brief asks me to flag:

- re-running changes every `run_id`, which forces repointing the claim ledger
  and retiring seventeen predecessors — substantial churn on a tree just made
  public;
- each re-derivation regenerates numbers the manuscript prints. Windows→Windows
  should be deterministic, but "should" is doing work there, and discovering
  otherwise on a round whose brief forbids content changes is the wrong place
  to find out;
- **and the gate still would not pass**, because of the two above.

So the cost is real, the benefit is cosmetic, and the outcome is unchanged. If
you would rather have 2 exceptions than 19, say so and I will do it — it is
about 25 minutes plus the ledger churn, and it makes the residual story much
tighter for a deposit description.

---

## P3 — The public repository, checked from outside

`git fetch` then reading the tree at `origin/rebuild/honest-v1`.

| check | result |
|---|---|
| Pushed HEAD | `083df8acb6e48c2f403218ae765260584c3a2fdb`, == local |
| Files in the pushed tree | **577** |
| Manuscript source | `paper/main.tex`, `paper/numbers.tex`, `paper/references.bib` ✓ |
| Manuscript PDF | `paper/main.pdf` ✓ |
| Scripts | 59 ✓ |
| Live manifests | 26 ✓ |
| Superseded manifests | 59, with `superseded/README.md` giving a reason for each ✓ |
| Claim ledger, scope decisions | ✓ |
| Findings documents | 10 ✓ |
| Tests | 12 ✓ |
| Package files | 115 ✓ |
| **Manifest commit SHAs resolve in the pushed history** | 84 manifests read from the pushed tree, **26 distinct base commits, all ancestors of the pushed branch, none unresolvable** |
| Sensitive content in the pushed tree | none — no `.pem`, `.env`, `data/raw` payload, `data/downloads`, `.venv`, or credentials. Only `data/raw/natural/EXPECTED_SHA256.txt`, a hash list |
| README references | **24 path references, all resolve; 0 broken** |

**Nothing a reader following the README would find broken.** The one thing they
*would* find, and should: the README now tells them which two of the eight
checks are repository-only, and that the Zenodo code zip needs
`manifests_bundle.zip` extracted into `results/manifests/` first.

---

## P4 — Rebuild in dependency order, gate, builds, tests, extractions

Rebuild order matters: the Zenodo package first, the DTRAP artifact last,
because running the gate regenerates `results/manifests/macro_index.json` and
would otherwise leave the artifact stale.

### Full gate — all eight checks, exit 0

```
python scripts/check_provenance.py      # exit 0
```

| check | result |
|---|---|
| provenance gate (orphans) | 563 manifested, 0 orphans, 0 mismatches, 0 ambiguous |
| claim ledger | 31 rows, every reference resolves |
| typed-literal scan | 14 files, clean in every enforced file |
| decimal consistency | **71** derived quantities equal the arithmetic on their printed operands |
| display width | 9 metric families, one width each |
| control characters | 5 LaTeX sources, no shell-escape damage |
| overfull boxes | 2 logs, nothing typeset past the measure |
| package freshness | 8 staged artifacts, all newer than their sources |

```
python scripts/check_manuscript_macros.py   # exit 0 — macros and citations resolve
python -m pytest -q                          # 72 passed
```

### Both builds

| build | exit | pages | undefined | overfull |
|---|---|---|---|---|
| `paper/main.pdf` (anonymous) | 0 | **17** | 0 | 0 |
| `packages/arxiv_v3/src/main.pdf` (named) | 0 | **17** | 0 | 0 |

### Documented instructions executed inside the extractions

**DTRAP artifact** — extracted to a temporary directory, commands run *inside*:

```
python scripts/check_provenance.py --ledger         exit=0
python scripts/check_provenance.py --literals       exit=0
python scripts/check_provenance.py --decimals       exit=0
python scripts/check_provenance.py --controlchars   exit=0
```

`findings_review_analyses.md`, `results/manifests/superseded/README.md` and
`CLAIM_LEDGER.md` all present; **0 self-test fixtures leaked into the artifact**.

**Zenodo code zip** — extracted, and the README's bundle step exercised:

```
# before the documented step
python scripts/check_provenance.py --ledger         exit=1     (expected)

# after: manifests_bundle extracted into results/manifests/
python scripts/check_provenance.py --ledger         exit=0
python scripts/check_provenance.py --literals       exit=0
python scripts/check_provenance.py --decimals       exit=0
python scripts/check_provenance.py --controlchars   exit=0
```

The documented sequence fails without the bundle and passes with it, which is
what the instruction promises.

---

## P5 — Deposit dry runs (assembled, nothing sent)

Three sheets written: **`ZENODO_DEPOSIT_SHEET.md`**, **`ARXIV_V3_SHEET.md`**,
**`DTRAP_SUBMISSION_SHEET.md`**. Each is fill-in order with final values, and
each states which fields become immutable.

Preparing them **found four live uses of a withdrawn title** — the framing
analysis A1 refuted and CI-21 removed:

| file | what it would have done |
|---|---|
| `packages/arxiv_v3/METADATA.md` | this is the *"new title" for the replacement form* — following it would have put the withdrawn claim **on arXiv, permanently** |
| `packages/zenodo/zenodo_metadata.md` | the deposit title and description |
| `README.md` | the repository headline, shipped inside **both** packages |
| `CITATION.cff` | the citation record, shipped in the deposit |

All four corrected. `packages/dtrap/COVER_LETTER.md` was worse: it named the
withdrawn title *and* told the editors that "reordering alone … inverts which of
the two deterministic methods under test wins" — **the claim A1 refuted** — and
described the posterior as "provably data-independent" without the below-the-cap
qualifier the manuscript now insists on. Rewritten to match the paper.

---

## State table

| item | value |
|---|---|
| Commit | `083df8acb6e48c2f403218ae765260584c3a2fdb` |
| Remote | `https://github.com/MichelYsf/rcbsid-paper.git`, branch `rebuild/honest-v1` |
| Build gate | **8/8, exit 0** |
| Macros | 563, 0 orphans, 0 ambiguous |
| Claim ledger | 31 rows, all references resolve |
| Derived-value consistency | 71 relations, all agree with printed operands |
| Tests | 72 passed |
| Builds | both 3-pass, exit 0, 0 undefined, 0 overfull, **17 pp** |
| Identity scans | anonymized PDF and source package: zero identity tokens |
| Artifact self-check | passes inside a fresh extraction |
| Corrected incidents | **CI-1 … CI-35** |
| Live run manifests | 25 (19 uncommitted-tree, 6 clean) |
| Publish-ready | **exit 1** — halted, see P2 |

---

## Deferred WORDING / NIT items, individually

Carried from the round-3 sweeps; none is a factual error.

1. **Protocol table "every metric"** — narrowed this round to exactly what
   `is_metric()` enforces, with exclusions named. *Resolved.*
2. **`DrawOne` seed width** — resolved this round; `is_metric` now reads the
   emitting run's declared desc and unit.
3. **`RevReproNaturalDelta` exponent form** — resolved; prints `0.000018`.
4. **`REBUILD_STATUS.md` "S7 and S8 remain"** — resolved; marked a dated
   snapshot superseded by `REBUILD_DONE.md`.
5. **`REVIEWER_KIT/manuscript_review.pdf` stale** — resolved; rebuilt to 17 pp
   and added to the freshness gate.
6. **`figures/fig2…fig6.pdf` are orphans** — the manuscript contains zero
   `\includegraphics`. Verified shipped in **no** package. Left in place: they
   are tracked history and deleting them is not required for anything.
7. **`check_decimals` docstring says "every quantity"** over a 71-entry
   enumerated set. The set is now partly derived from the macro file rather than
   hand-kept, but the docstring still generalises. NIT, unfixed.
8. **`ARTIFACT_ACCESS_STRATEGY.md` says "160 files"** against a 205-file zip.
   NIT, unfixed — never verified as a finding by any auditor.
9. **Personal path `C:\Users\CYBERWIZARD`** in 577 places, mostly manifest
   `declared_inputs`. Cosmetic; already public; rewriting archived manifests to
   scrub it would be a worse crime than the exposure.

---

## Judged and not fixed

- **The seventeen regenerable manifests** (P2). Cost/benefit and risk of
  changing published values on a no-content-change round. Yours to overturn.
- **Rewriting `git_commit` in any manifest.** It means *HEAD at run time*.
  Re-stamping would make a true record false, which is the opposite of what the
  invariant is for.
- **Relaxing `check_publish_ready` to reach green.** Explicitly forbidden, and I
  agree with the prohibition; I corrected its false *rationale* and left its
  *verdict* alone.
- **`figures/*.pdf`** — orphaned but harmless and unshipped.

---

## What remains for you, in order

**Nothing before ORCID.**

0. **ORCID** — sign in at https://orcid.org/signin and confirm the iD under your
   name reads **0009-0000-0664-8228**. (The `-8224` variant is a 404.)

1. **Decide the provenance question.** `--publish-ready` exits 1 because 19 live
   manifests ran on an uncommitted tree, two of them irreducibly. Either accept
   it — the disclosure paragraph is already written into
   `ZENODO_DEPOSIT_SHEET.md` Step 5 — or tell me to re-run the seventeen.

2. **Zenodo** — follow `ZENODO_DEPOSIT_SHEET.md` top to bottom. Zip
   `manifests_bundle/` first. Files are frozen at publication; metadata is not.
   Copy the **version** DOI.

3. **Propagate the DOI** — `CITATION.cff`, replace the `message:` block with a
   `doi:` field. Commit and push.

4. **arXiv v3** — follow `ARXIV_V3_SHEET.md`. Use the **NO VENUE CLAIM** comment
   variant; the other two in that file are retired and false. Confirm 17 pages
   in arXiv's own preview before submitting.

5. **DTRAP** — follow `DTRAP_SUBMISSION_SHEET.md`. The ACM waiver confirmation
   PDF is still not on this machine; retrieve it from email or cite the ticket.

6. *Optional* — retire the AWS IAM access key; `eu-central-1` holds nothing.

Nothing in steps 2–5 has been started. No deposit exists, no submission exists,
and no message has been sent to anyone.
