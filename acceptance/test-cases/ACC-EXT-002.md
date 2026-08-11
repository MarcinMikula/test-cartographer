# ACC-EXT-002 — Create automation for one external GOV.UK page

## Status

**DESIGNED — not executed.**

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

Not executed yet.
