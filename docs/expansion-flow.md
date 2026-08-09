# Incremental expansion using the existing application map

Sprint 14 adds the first controlled second-process expansion path.

The capability starts from explicit human intent to automate something new
inside an already known project. It does not treat a proactive-regression
finding as authorization and it does not restart bootstrap intake.

## Reference flow

```text
accepted Search process and application map
+ accepted framework snapshot
+ human intent: add Sort
+ optional Sprint 13 freshness evidence
→ deterministic reuse/gap plan
→ reuse current accepted knowledge
→ ask only for missing Sort process meaning
→ re-observe the known-stale Sort control
→ reviewed candidate Sort ContextBundle
→ existing synthesis pipeline
→ existing repository-aware adaptation
→ extend existing CatalogPage
→ exact hash-bound source patch
→ human source review
→ fresh sandbox application
→ Search PASS + Sort PASS
→ deterministic ExpansionAssessment
```

## Contracts

Sprint 14 introduces four versioned expansion contracts:

- `ExpansionRequest` — human-triggered intent bound to the accepted base context
  and current framework snapshot,
- `ExpansionPlan` — deterministic per-item reuse/delta disposition,
- `ExpansionRun` — evidence and metrics from one completed expansion path,
- `ExpansionAssessment` — deterministic mechanical/controlled-demo readiness
  result.

Expansion does not introduce a second knowledge-status model. Existing
ContextBundle authority states remain authoritative.

The expansion workflow uses:

```text
REUSE
ASK_HUMAN
OBSERVE_NEW
REOBSERVE
REVIEW
BLOCKED
```

A required item that is known stale is not eligible for `REUSE`.

## Human authority

The reference real-operator flow contains seven explicit authority transitions:

1. start the human-triggered expansion,
2. accept the reuse/gap plan,
3. accept the candidate expanded context,
4. accept the validated synthesis proposal,
5. accept the repository-aware adaptation plan,
6. accept the exact source changes,
7. authorize application to a fresh sandbox and execution.

Only explicit `A` / `Accept` and `R` / `Reject` tokens are decisions. Invalid
input, including accidental control characters, records no authority transition
and causes a re-prompt.

Bootstrap/project context is not asked again. The reference Sort process asks
only three process-specific questions: purpose, risk, and expected outcome.

## Targeted re-observation

Sprint 13 produced accepted evidence that the mapped Sort test ID changed from
`catalog-sort` to `catalog-sort-control`. That evidence is useful input but is
not blindly trusted as current truth.

The Sprint 14 plan marks the required Sort element `REOBSERVE`. Headed Chromium
confirms the current locator before the candidate Sort ContextBundle is created.

The accepted base ContextBundle remains unchanged while the candidate context is
built and reviewed.

## Existing repository extension

The existing `CatalogPage` already contains Search behavior. Sort therefore
must not create a fake second page merely because new members are needed.

The adaptation layer adds `EXTEND_SYMBOL`:

```text
CatalogPage
+ apply_sort()
+ sort_results
```

Framework snapshots distinguish methods and `@property` members. A member-name
collision across kinds fails closed.

The existing `catalog_context` fixture is reused. One new
`test_sort_catalog.py` is created.

## Hash-bound delivery

Extending an existing class requires changing an existing file. Sprint 14 allows
`REPLACE_FILE` only as the deterministic consequence of an accepted
`EXTEND_SYMBOL`.

The replacement is bound to:

- the current framework snapshot/fingerprint,
- the exact pre-change source SHA-256,
- the accepted adaptation plan,
- explicitly reviewed missing members,
- deterministic generated source,
- exact source review,
- preflight source-drift validation.

If the source changes after inspection, application fails before any write.

The patch is applied only to a fresh sandbox. The original framework remains
unchanged.

## Acceptance evidence

The final Sprint 14D.2 Windows run recorded:

```text
339 tests passed
0 failures
0 errors
0 skipped

bootstrap questions repeated: false
process-specific questions: 3
reused knowledge items: 8
reobservations: 1

framework symbols reused: 1
framework symbols extended: 1
framework symbols added: 1
existing tests preserved: 1
new tests added: 1

operator authority transitions: 7
live LLM calls: 0
headed browser: true
fixture decisions: false

Search before expansion: PASS
Search after expansion: PASS
Sort after expansion: PASS

base context unchanged: true
original framework unchanged: true
stale knowledge silently reused: false
automatic context write: false
PhoenixQA healing: false
raw page persisted: false

expansion_verified: true
controlled_demo_ready: true
blockers: []
```

## Acceptance-quality correction

The first green real-operator run was not accepted blindly. Review found that
the generated Sort assertion message still referred to a Search query and that
the controlled expected value covered only part of the visible sorted result.

Sprint 14D.2 changed the controlled binding to the complete
`Alpha Beta Zulu` result, made the failure message expected-result-oriented,
added a verifier for this policy, reran the complete 339-test regression, and
repeated the real headed acceptance.

The generated reference test still uses containment rather than a general
list-order comparison. The current evidence therefore proves the controlled
reference behavior, not arbitrary sorting correctness.

## Explicit non-capabilities

Sprint 14 does not prove:

- expansion into arbitrary unknown application areas,
- persistent cross-run bootstrap/profile reuse and invalidation,
- authenticated or enterprise application expansion,
- broad component/Page Object conflict resolution,
- arbitrary existing-source rewriting,
- production repository writes or pull-request creation,
- general sort-oracle generation,
- measured productivity, cost, or time savings,
- live-model quality for expansion,
- PhoenixQA runtime healing,
- Salesforce readiness.
