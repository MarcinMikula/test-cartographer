# ACC-FIND-007 — external single-page flow supports heading outcomes only

## Status

**OPEN — Level 1B blocker preserved before remediation.**

GitHub Issue: pending creation after the finding-preservation commit.

## Discovery context

```text
test case: ACC-EXT-003
evidence-bearing run: ACC-EXT-003-run-02
product commit: ac1d7b61033251377b9b49d970c50f6d8cdf91e9
framework baseline: 4d916dea8190bc59ef8c9dd5aa78aa31dbbf16a6
target: https://practicesoftwaretesting.com/
target contacted by TestCartographer: false
result: NOT ACCEPTED / PRODUCT FINDING
```

## Observation

Run-02 completed nine guided-intake questions and aggregate context confirmation.
Before browser discovery, `build_external_public_single_page_plan()` rejected the
accepted non-heading outcome:

```text
ValueError: external public single-page creation currently supports heading outcomes only
```

No browser discovery, synthesis, source generation, sandbox creation, or target
test execution occurred. The Practice Software Testing target is not implicated.

## Confirmed capability boundary

The external plan builder requires exactly one context page, exactly one expected
outcome, and outcome text containing `heading`. Its discovery target is a single
READ action with expected role `heading`.

The external deterministic proposal then requires exactly two steps:

```text
navigate
-> read one observed heading
```

The authorized Level 1B process requires a materially different same-page
interaction family: search/filter/sort, result-set observation, and a meaningful
post-interaction assertion.

## Classification

```text
kind: expected product limitation / requirement-to-capability gap
severity: Level 1B blocker
target defect: false
testware defect: false
fail-closed functional behavior: true
graceful terminal behavior: false (tracked separately by ACC-FIND-009)
```

Primary requirement: `ACC-REQ-016`.

Related requirements: `ACC-REQ-005`, `ACC-REQ-008`, `ACC-REQ-009`.

## No-workaround rule

Do not insert the word `heading` into operator answers, reduce the scenario to a
static assertion, handcraft a discovery plan, edit persisted context, substitute
a controlled fixture, or manually resume from an internal stage.

## Correction boundary to design later

Before a correction is authorized, decide the smallest coherent product boundary
for a reviewed multi-action same-page process. The design must preserve bounded
browser scope, human authority, observable evidence, sandbox-only writes, and
independent execution. It must not silently generalize to arbitrary crawling,
multi-page workflows, authentication, or writes.

Capability compatibility should also fail before consuming full intake effort
when the requested process is outside the implemented envelope.

## Retest rule

Keep run-02 immutable. After separate remediation authorization and commit, use a
new ACC-EXT-003 run identifier against the new exact product commit. Do not begin
Level 2 from this blocked state.
