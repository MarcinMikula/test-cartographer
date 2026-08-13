# ACC-EXT-002 — Create automation for one external GOV.UK page

## Status

**PASSED — `ACC-EXT-002-run-04` on 2026-08-13.**

## Why this test exists

`ACC-EXT-001` remains the original four-page GOV.UK navigation scenario.

Pre-execution triage showed that the current discovery lifecycle is single-page.
Changing ACC-EXT-001 into a one-page test would rewrite the historical test
basis.

ACC-EXT-002 therefore provides the smallest independent Level 1 scenario that
can prove first external application validity without silently introducing a
multi-page discovery engine.

## Objective

Determine whether TestCartographer can use its nominal human-triggered Creation
Flow on one real external public page, discover the heading needed by the
process, create reviewable automation, apply it only to the isolated framework
sandbox, and execute it independently.

## Target

```text
application: GOV.UK
URL: https://www.gov.uk/driving-licence-codes
difficulty: simple
control: external_stable
authentication: none
sensitivity: public
```

This URL is inside the GOV.UK scope already authorized by the operator.

## Process intent

The operator intent should be semantically equivalent to:

> Automate opening the public GOV.UK Driving licence codes page and verify that
> the page presents the "Driving licence codes" heading.

Do not provide a locator, DOM selector, Page Object class name, or implementation
hint.

## Linked acceptance requirements

Primary:

```text
ACC-REQ-001
ACC-REQ-003
ACC-REQ-004
ACC-REQ-005
ACC-REQ-006
ACC-REQ-007
ACC-REQ-008
ACC-REQ-009
ACC-REQ-012
ACC-REQ-013
ACC-REQ-014
ACC-REQ-015
ACC-REQ-016
ACC-REQ-017
```

Conditional after a material correction/retest:

```text
ACC-REQ-010
ACC-REQ-011
```

Not the primary purpose:

```text
ACC-REQ-002
```

## Preconditions

- exact TestCartographer commit recorded,
- clean working tree,
- GOV.UK target authorization remains active,
- current policy/robots boundary remains compatible,
- no auth/forms/transactions/personal data,
- isolated acceptance output area,
- original qa-automation-framework repository remains read-only,
- local provider/browser prerequisites satisfied,
- Issue #1 correction merged into the product state being tested,
- Issue #2 multi-page limitation does not need to be fixed for this scenario.

## Expected discovery scope

The minimum useful application evidence is the native page heading:

```text
role/name:
heading / Driving licence codes
```

A valid implementation may retain other bounded visible candidates, but the
test must not require unrelated page scraping to succeed.

## Actions

1. Start the supported external Creation Flow.
2. Provide only the process intent and legitimate human context.
3. Open only the approved GOV.UK page.
4. Perform bounded browser discovery.
5. Review the selected heading evidence/locator.
6. Review the synthesized Page Object design.
7. Review the repository adaptation plan.
8. Review the exact source patch.
9. Apply only to the isolated framework sandbox/copy.
10. Trigger independent framework execution.
11. Verify the generated test passes without TestCartographer/live LLM at
    execution time.
12. Build and verify the acceptance evidence package.
13. Record operator effort/friction/confidence/reuse assessment.

If a stage cannot be reached, preserve the finding and stop. Do not rescue the
workflow by editing internal TestCartographer state.

## Acceptance oracle

PASS requires evidence that:

- the external URL is supplied through a supported product interface,
- TestCartographer, not the operator, obtains the required locator from bounded
  browser evidence,
- the native heading can be represented without fixture-specific catalog
  assumptions,
- unknown/ambiguous information remains explicit,
- the Page Object/source proposal is reviewable and semantically appropriate,
- no unnecessary component or symbolic test-data binding is invented merely
  because the old catalog demo required one,
- the original framework repository is unchanged,
- the sandbox-generated test independently verifies the observed/authorized
  heading semantics,
- the validation package verifies successfully.

A passing pytest test is insufficient if the flow required hidden catalog
fixtures, manual internal JSON repair, locator injection, unsafe capture, or
wrong architectural structure.

## Stop conditions

Use the existing campaign stop conditions.

Additionally stop if the proposed fix for Issue #1 still requires:

- the local catalog fixture,
- public-catalog discovery plan,
- `CatalogPage` / `CatalogSearchForm`,
- search-query test data,
- the fixed `test_search_catalog.py` target,
- a manual internal workaround not exposed through the supported product
  interface.

## Result

**PASS.**

Accepted external execution:

```text
acceptance test: ACC-EXT-002
passing run: ACC-EXT-002-run-04
tested product commit: bd6595ab89c5c4c2d1e6317ee372bfaa9a74462f
external target: https://www.gov.uk/driving-licence-codes
creation flow status: passed
tests collected / passed: 1 / 1
independent framework execution: true
original framework unchanged: true
component required: false
component generated: false
```

The run completed the supported bounded workflow from human intent through
external browser discovery, explicit reviews, sandbox application, and
independent framework execution.

The successful run also provided the real acceptance retest for:

- `ACC-FIND-003` / Issue #3 — single-target discovery contract,
- `ACC-FIND-004` / Issue #4 — componentless CreationEvaluation,
- `ACC-FIND-005` / Issue #5 — immutable/fail-closed output startup.

`ACC-FIND-006` / Issue #6 was discovered after the functional PASS as a
non-blocking stage-level LLM-call measurement error. It was preserved before
remediation and corrected deterministically in commit
`ab4f3f5e873f0849a2d418a9a0c6cf7ff8279839`; no additional GOV.UK execution
was required.

Formal Sprint 16 validation packaging was then built from the immutable run-04
evidence and independently verified:

```text
ValidationRun contract id: acc_ext_002_run_04
validation run fingerprint:
281c0eac510eacb98eeda16c3e5bae96c0c2cf87bc2c1739be9d4360bfcf7c96

target fingerprint:
85691211bcbde45eb885309a6518875392f084409a6d3a4b4db33a277dd875c0

package fingerprint:
2d297736725ee99363b1e37e69b7972fa284af8ada2083325849537b2ab69381

manifest entries: 7
independent package verification: passed
run-04 source evidence unchanged: true
```

Operator closure assessment:

```text
difficulty: hard
confidence in result: high
would reuse workflow: yes
prior target familiarity: automated_before
```

Timing interpretation is intentionally conservative. The Creation Flow recorded
`730.247` seconds of prompt-to-response/operator-response elapsed time and
`898.836` seconds total elapsed time. These values are useful burden evidence
but are not treated as proof of continuous human active work. No productivity or
time-savings claim is made.

`ACC-EXT-001` remains separately blocked by `ACC-FIND-002` / Issue #2 because
the original four-page scenario requires multi-page discovery. Passing
`ACC-EXT-002` does not claim that capability.
