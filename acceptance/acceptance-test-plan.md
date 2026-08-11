# Acceptance Test Plan v0.1

## 1. Document control

```text
Product: TestCartographer
Test type: Product Acceptance Testing — External Validation Campaign
Process model: STLC-derived, evidence-driven
Plan version: 0.1
Status: active initial baseline
Initial product baseline: 49a45192a8ef58d736adb3a16a67d1b4add2f07c
Initial regression baseline: 469/469
```

The plan is intentionally versioned and revisable. New external evidence may
change requirements, test cases, priorities, or campaign sequencing.

## 2. Test object

The system under test is **TestCartographer**.

External websites/applications are validation targets and test environments.
They are not the system under test.

Primary acceptance question:

> Can TestCartographer help a technically capable testing professional acquire,
> verify, reuse, and maintain enough trustworthy frontend context to create
> maintainable Playwright/Python/pytest automation for a real application it
> does not control?

The external application must not be changed merely to make TestCartographer
pass.

## 3. Test basis

Initial test basis:

- `README.md`,
- `docs/product-scope.md`,
- `docs/roadmap.md`,
- `docs/validation-protocol.md`,
- `docs/sprint-16-validation-protocol.md`,
- `docs/known-limitations.md`,
- `docs/gaps.md`,
- `acceptance/requirements/acceptance-requirements.md`.

Conflicts in the basis are recorded and resolved; they are not silently
interpreted in whichever way makes the test pass.

## 4. Objectives

Determine whether TestCartographer:

1. works on frontend applications not created for the project,
2. preserves uncertainty instead of inventing application/business truth,
3. gathers useful browser/context evidence within bounded privacy/safety scope,
4. keeps the human authoritative at semantic and acceptance boundaries,
5. produces reviewable, maintainable automation structure rather than merely
   executable code,
6. produces automation that runs independently of TestCartographer,
7. preserves failures/findings before remediation,
8. supports linked retest and regression after justified corrections,
9. exposes operator effort, friction, confidence, and review burden,
10. keeps supported nominal workflows inside documented product interfaces
    rather than requiring manual repair of internal contracts/product state,
11. protects the original automation repository from unapproved/silent writes,
12. remains useful enough to justify deeper validation.

## 5. Sprint 17 scope

### Level 1 — simple external public target

Desired characteristics:

- publicly accessible,
- no authentication,
- conventional frontend semantics,
- small bounded process,
- no destructive action,
- low sensitivity,
- stable enough to repeat,
- not controlled by TestCartographer.

Purpose: expose assumptions hidden by controlled fixtures while keeping target
complexity low.

### Level 2 — dynamic external public target

Desired characteristics:

- script-heavy or asynchronous behavior,
- dynamic DOM/state or delayed interaction,
- lower target control,
- no credential requirement for Sprint 17,
- bounded and ethically safe interaction.

Purpose: challenge discovery, observation, synchronization assumptions, and
evidence handling after Level 1.

Concrete targets are selected only after this test basis is accepted.

## 6. Out of scope for Sprint 17

- API/SOM adaptation,
- credentialed authentication,
- SSO/MFA,
- enterprise/Salesforce readiness,
- unrestricted crawling,
- destructive transactions,
- arbitrary production-repository writes,
- universal framework/language support,
- autonomous defect verdicts,
- comparative productivity/ROI claims.

Timing and usability evidence may be collected, but no comparative productivity
claim is made from Sprint 17 alone.

## 7. Test approach

For every substantive scenario:

```text
test basis
-> acceptance requirement
-> test case
-> target/profile authorization
-> ValidationRun
-> evidence package
-> finding(s)
-> triage
-> smallest justified correction if needed
-> linked retest
-> regression
-> closure decision
```

Tests are risk- and evidence-driven rather than created to satisfy a fixed test
case count.

## 8. Entry criteria

- [x] Sprint 16 validation protocol closed.
- [x] Evidence package and independent verifier accepted.
- [x] Finding-before-fix rule accepted.
- [x] Product baseline regression: 469/469.
- [x] `main` contains accepted Sprint 16 implementation.
- [ ] Acceptance Test Plan v0.1 accepted.
- [ ] Acceptance Requirements v0.1 accepted.
- [ ] STLC workflow accepted.
- [ ] First external target assessed and authorized.
- [ ] First test case designed before execution.

## 9. Suspension and stop conditions

Stop or leave execution incomplete when continuing requires:

- unapproved authentication,
- destructive/irreversible behavior,
- sensitive/prohibited data handling,
- leaving approved origin/process,
- bypassing anti-abuse/rate-limit controls,
- unrestricted crawling/capture,
- missing policy/authorization decision,
- unsafe evidence retention,
- a change that destroys comparability,
- target behavior that makes observation unsafe or meaningless.

A safety stop is evidence, not an automatic test failure.

## 10. Evidence policy

Committed testware contains requirements, test cases, campaign plans,
traceability, and summarized closure records.

Full validation packages remain outside the repository.

Default evidence must not include credentials, cookies/storage state, raw
HTML/page dumps, unrestricted screenshots/traces, raw prompts/model responses,
arbitrary source trees, unbounded terminal logs, or third-party personal data.

Sprint 16 package policy remains authoritative.

## 11. Finding and defect management

Existing finding kinds:

```text
failure
friction
unsupported_assumption
safety_stop
measurement_issue
```

After evidence is preserved, operational triage may classify action as:

```text
product defect
testware defect
requirement gap/change
known/accepted limitation
target condition
needs more evidence
no product change
```

Actionable items are tracked as GitHub Issues.

## 12. Git/change control

`main` remains source of truth for accepted product state and acceptance
testware. Testware may be committed in small slices.

When acceptance exposes a justified product change:

```text
main @ tested commit
-> preserve failed/incomplete run
-> short-lived fix/<finding> branch
-> smallest justified correction
-> product regression
-> linked acceptance retest
-> merge when evidence supports it
```

Not every finding creates a branch.

## 13. Metrics

Product/result evidence:

- requirement coverage,
- scenario completion,
- runnable test result,
- unsupported assumptions,
- deterministic validation failures,
- correction count,
- POM/component placement review,
- assertion quality review,
- finding type/triage,
- out-of-band/manual internal intervention required to complete the workflow,
- write target actually modified (sandbox/copy/original repository).

Operator evidence:

- setup active time,
- intake active time,
- review active time,
- correction active time,
- system wait time,
- total elapsed time,
- perceived difficulty,
- confidence,
- willingness to reuse,
- prior target familiarity.

Do not derive time saved, ROI, productivity uplift, or superiority to alternative
workflows yet.

## 14. Sprint 17 exit criteria

Sprint 17 can close when:

1. at least one Level 1 external public process has been executed through the
   acceptance protocol,
2. at least one Level 2 dynamic public process has been attempted under the same
   evidence discipline,
3. material first findings are preserved before correction,
4. justified fixes have linked retest evidence,
5. unresolved limitations are documented rather than hidden,
6. product regression is green for the accepted state,
7. requirements/test cases/traceability reflect what was learned,
8. operator usability evidence is recorded,
9. closure distinguishes proven behavior from remaining uncertainty.

A legitimate safety stop may satisfy an individual target attempt, but does not
automatically replace the need for suitable external functional evidence.

## 15. Closure decision

```text
PASS
PASS WITH LIMITATIONS
NOT ACCEPTED
INCONCLUSIVE / MORE EVIDENCE REQUIRED
```

Green pytest alone cannot determine the decision.

## 16. Plan evolution

Every material plan update should state:

- what changed,
- why,
- which finding/requirement/campaign triggered it,
- whether executed tests are affected,
- whether new regression/retest coverage is required.

The campaign should become more accurate over time, not merely larger.
