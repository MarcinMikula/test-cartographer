# ACC-FIND-007 — external single-page flow supports heading outcomes only

## Status

**RESOLVED — deterministic rich same-page capability verified.**

Related GitHub Issue: `#7 [ACCEPTANCE] ACC-EXT-003 — external single-page flow supports heading outcomes only`

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

## Historical capability boundary

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

## Implemented correction

Product commit `3b8bb73bd665f8d5389ff2b6a1299c023a97392e` implements the
smallest authorized deterministic boundary for a reviewed multi-action process
on one public page.

The correction:

- preserves the existing navigate/read-heading contract;
- accepts two to six reviewed discovery targets using `FILL`, `CLICK`, `SELECT`,
  `CHECK`, `UNCHECK`, and exactly one final outcome `READ`;
- requires declared page/component owners, supported semantic roles, and
  symbolic non-secret test data for `FILL` and `SELECT`;
- rejects incomplete or unsupported shapes before browser discovery or source
  generation;
- generates deterministic Page Object and Component methods without deriving
  actions, locators, prices, counts, or business rules from free text.

Issue #8 remains responsible for preserving the initial mission, clarifying
material ambiguity, and supplying reviewed structured intent to this capability.

## Verification

```text
focused Issue #7 tests: 25 passed
full regression suite: 500 passed
external target contacted: false
live LLM/Ollama invoked: false
run-03 consumed: false
```

The tests cover legacy heading compatibility, rich discovery-plan validation,
deterministic proposal validation, Page Object/Component generation, and the
expanded action vocabulary. They do not rewrite or convert the historical
run-02 verdict into a pass.

## Retest rule

Keep run-02 immutable. Do not consume a new ACC-EXT-003 run identifier until the
separate Issue #8 blocker is corrected and closed. The later retest must use the
new exact integrated product commit. Do not begin Level 2 from this blocked
state.
