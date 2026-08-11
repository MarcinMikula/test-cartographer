# STLC workflow for TestCartographer acceptance

## 1. Purpose

This workflow adapts the Software Testing Life Cycle to TestCartographer's
product-acceptance campaign.

```text
Requirement Analysis
-> Test Planning
-> Test Design
-> Environment / Target Setup
-> Test Execution
-> Finding Triage
-> Correction + Retest + Regression
-> Test Closure
        \
         -> requirement/testware evolution when evidence justifies it
```

The cycle may loop backward when a real finding exposes a requirement or
test-design gap.

## 2. Requirement Analysis

Inputs:

- product scope,
- roadmap,
- limitations/gaps,
- prior findings,
- current acceptance requirements,
- campaign objective.

Activities:

- state desired product behavior,
- separate product requirements from target characteristics,
- identify safety/authority boundaries,
- identify missing/ambiguous criteria,
- review whether existing requirements remain valid.

Gate: do not design a test whose expected product behavior cannot be evaluated.

## 3. Test Planning

Define campaign objective, target class, scope, entry/exit criteria, evidence
policy, stop conditions, and required usability evidence.

Gate: the plan must not require unsafe/prohibited activity or claims the
campaign cannot support.

## 4. Test Design

Each test case should contain at least:

```text
ID
objective
linked requirement(s)
risk
preconditions
target/process boundary
operator actions
expected product behavior
acceptance oracle
required evidence
stop conditions
postconditions/cleanup
```

Minimum traceability:

```text
ACC-REQ
-> ACC test case
-> ValidationRun
-> ValidationFinding
-> GitHub Issue if actionable
-> fix commit/branch if any
-> linked retest run
-> campaign closure
```

Gate: the test case exists before execution. Exploratory observations may create
new tests, but are not silently rewritten as preplanned coverage.

## 5. Environment / Target Setup

Record target difficulty/control/authentication class, approved origin/process/
actions, prohibited actions, cleanup, sensitivity/evidence policy, and exact
TestCartographer product commit.

Gate: no execution without a bounded approved target profile.

Sprint 17 Level 1 authentication should be `none`.

## 6. Test Execution

Rules:

1. Execute against the bound product commit/state.
2. Record real operator decisions.
3. Do not modify the external target to accommodate the product.
4. Do not change TestCartographer mid-run and call it the same run.
5. Preserve minimized evidence.
6. Record timing/friction honestly.
7. Safe stop is allowed.

A generated pytest PASS does not erase poor POM quality. A genuine authorization
block may demonstrate correct safety behavior. A failed test does not
automatically prove a third-party application defect.

## 7. Finding Triage

Preserve first:

```text
observe
-> persist finding
-> close/verify run package
-> triage
```

Evidence kinds remain:

```text
failure
friction
unsupported_assumption
safety_stop
measurement_issue
```

Operational triage:

- PRODUCT DEFECT
- TESTWARE DEFECT
- REQUIREMENT GAP/CHANGE
- KNOWN/ACCEPTED LIMITATION
- TARGET CONDITION
- NEEDS MORE EVIDENCE
- NO PRODUCT CHANGE

Actionable work is tracked through GitHub Issues.

## 8. GitHub Issues

Suggested title:

```text
[ACCEPTANCE] <test-case-id> — <short finding>
```

Suggested labels when configured:

```text
acceptance
campaign:s17
finding:failure
finding:friction
finding:unsupported-assumption
finding:safety-stop
finding:measurement-issue
triage:product-defect
triage:testware
triage:requirement
triage:limitation
triage:target
triage:needs-evidence
```

Issue references should include test case, ValidationRun ID, finding ID, tested
commit, evidence package identity/location as appropriate, triage decision, and
correction/retest link when available.

Do not paste sensitive raw evidence into GitHub Issues for convenience.

## 9. Correction, Retest, Regression

Product correction:

```text
main @ tested commit
-> short-lived fix/<finding> branch
-> smallest justified change
-> implementation tests
-> full relevant regression
-> linked acceptance retest
-> merge when evidence supports it
```

A fix branch is not created for every finding.

Testware-only corrections may be committed as small slices on `main` when they
do not change product behavior. If the oracle changes materially, document
whether prior results remain comparable.

Retest uses a new ValidationRun and preserves the predecessor unchanged.

Acceptance retest asks: did the observed acceptance problem change?

Product regression asks: did the correction break already accepted behavior?

Both matter after a product fix.

## 10. Test Closure

Closure summarizes:

- requirements tested/not tested,
- test cases executed,
- targets,
- run outcomes,
- findings,
- product defects/fixes,
- testware/requirement changes,
- known limitations,
- operator effort/friction,
- regression state,
- evidence limitations,
- proven vs unproven behavior.

Decision:

```text
PASS
PASS WITH LIMITATIONS
NOT ACCEPTED
INCONCLUSIVE / MORE EVIDENCE REQUIRED
```

## 11. Testware Evolution Loop

```text
external evidence
-> finding
-> requirement/test-case gap discovered
-> testware review
-> smallest justified change
-> new/updated coverage
-> next run
```

New requirements are expected when controlled fixtures could not expose a real
external condition.

## 12. Commit discipline

Acceptance does not wait for one large end-of-sprint commit.

Preferred separation:

```text
testware evolution
-> small main commits

product correction
-> short-lived fix branch + evidence-backed merge

historical execution evidence
-> immutable local validation package
```

This preserves useful history without creating a permanent competing test
branch.
