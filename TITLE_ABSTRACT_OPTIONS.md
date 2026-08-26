# TITLE_ABSTRACT_OPTIONS — revised for the fresh-review round

**Binding constraint (operator amendment A).** No title, abstract, or claim may
attribute the rank change to ordering alone or causally exclude prevalence: the
held-out slices share only \CicidsHeldoutOverlapPct\% of their records, so
membership, prevalence and order move together. Stream assembly is an
uncontrolled experimental treatment. **"Not Attack Prevalence" is removed from
the title.**

Every candidate below is checked against CLAIM_LEDGER.md: each asserts only
what rows A1–A9 and I1–I16 carry, and none asserts an isolated causal factor.

## Titles

**T1 (current, in `paper/main.tex`).**
*Stream Assembly Is an Uncontrolled Treatment in Streaming Intrusion-Detection
Benchmarks*

Ledger check: asserts (a) that assembly is a treatment and (b) that it is
uncontrolled. (a) is supported by A2/I4; (b) by A3+A4+I10 jointly — membership,
prevalence and order all change. Asserts no isolated factor and no method
superiority. **Recommended**: it states the design fact that survived review,
and the design fact is the contribution.

**T2.**
*Same Records, Different Evaluation: Held-Out Membership, Prevalence and Order
Change Together When Benchmark Streams Are Assembled*

Ledger check: "same records" is A3/I9 (full multiset, verified permutation);
"different evaluation" is A4/I10; the three-way conjunction is exactly the
uncontrolled-treatment claim. Slightly more explicit than T1 about *why* the
treatment is uncontrolled, at the cost of length. Safe alternative if a referee
finds T1's "uncontrolled" too compressed.

**T3.**
*A Case Study and Mechanism Audit of Stream Assembly in CICIDS2017 and
LITNET-2020*

Ledger check: claims only a case study and an audit, both fully supported; adds
the two dataset names so no generalization is implied. This is the most
conservative option and matches the positioning amendment D mandates
("quantified case study and mechanism audit"). Use if the editors push back on
any generalization at all. Risk: undersells the method-identity audit, which a
reader of the earlier versions will look for.

## Abstracts

**Abstract A (current).** Ledger rows A1–A9. Leads with assembly-as-treatment,
states the joint change (overlap, both prevalences, the difference), calls the
ordering reversal a pipeline-level outcome, then the LITNET identity as an audit
check, then the scoped method-identity facts, then provenance.

**Abstract B (correction-forward).** Rows A1–A9 plus I5–I8, for use if the
editors prefer the correction history surfaced in the abstract:

> Earlier versions of this work reported streaming intrusion-detection results
> produced on assembled evaluation streams and described a scoring rule the
> released code did not implement. This version rebuilds the study from an
> adversarial audit and reports what survives. On CICIDS2017, holding the full
> record multiset identical and changing only the assembly order, a fixed
> positional split produces held-out samples sharing 32.5% of their records at
> prevalences 43 points apart, and the measured ordering of the two
> deterministic scorers reverses; because membership, prevalence and order move
> together, the design identifies the assembly pipeline as the treatment and no
> factor within it. On LITNET-2020, pooling three temporally disjoint captures
> reports an operating point that is the equal-weight mean of the per-capture
> held-out prevalences and corresponds to no capture. We further audit the
> evaluated detector against its description, and state separately what is
> proved (branch cancellation below the run-length cap), what is measured (a
> wandering posterior at and beyond it, where the evaluations live), and what
> the evaluation actually consumes (a function of P(r<=5)). Every number traces
> to an archived, hash-verified run manifest.

Ledger check for B: sentence 1–2 → I5–I8; 3 → A3+A4+A5 with the
non-identification clause; 4 → A6; 5 → A7 (scoped); 6 → A9.

## Recommendation

**T1 + Abstract A.** If the editors prefer the correction surfaced earlier,
switch to Abstract B without changing anything else. If a referee objects that
"uncontrolled treatment" is itself a strong framing, T2 says the same thing in
plainer words and T3 retreats to pure case study.
