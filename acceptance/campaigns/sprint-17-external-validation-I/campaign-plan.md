# Sprint 17 — External Validation I campaign plan

## Status

**Level 1 external single-page acceptance executed and closed.**

Accepted external scenario:

```text
ACC-EXT-002
target: https://www.gov.uk/driving-licence-codes
passing run: ACC-EXT-002-run-04
result: PASS
independent framework execution: 1/1 PASS
formal evidence package: VERIFIED
```

The original `ACC-EXT-001` four-page GOV.UK scenario remains preserved and
blocked by `ACC-FIND-002` / GitHub Issue #2 because multi-page discovery is not
implemented.

The human-readable closure is in `level-1-validation-report.md`. Detailed
requirement evidence remains in `traceability.md`, and the exact acceptance
oracle/result remains in `../../test-cases/ACC-EXT-002.md`.

For subsequent planning, this completed Level 1 may be treated as **Level 1A**
only to distinguish it from the planned **Level 1B analyst-rich validation**.
Historical Level 1 records keep their original naming.

Practice Software Testing / Toolshop remains the authorized Level 1B target.
Execution started on 2026-08-15 against product commit
`ac1d7b61033251377b9b49d970c50f6d8cdf91e9`. `ACC-EXT-003-run-01` was
consumed by an operator terminal interruption during intake. The evidence-bearing
`ACC-EXT-003-run-02` completed guided intake and then stopped before browser
discovery with the explicit heading-only capability error. Its result remains
**NOT ACCEPTED / PRODUCT FINDING**, and no target defect verdict is made.

The independently authorized Issue #7 capability correction is implemented by
commit `3b8bb73bd665f8d5389ff2b6a1299c023a97392e` and verified by 25 focused and
500 full-suite tests. Issue #9 is also resolved. The Issue #8 intent-preservation
correction is implemented by commit
`23d3f34be364163337e055f50548e2dfc35a6fd3` and verified by 20 focused and
505 full-suite tests. All three corrections required no new external run or live
LLM call. Level 1B remains not accepted until a later new-run retest.

No Level 2 target is authorized yet.

## Campaign objective
Challenge TestCartographer on external public frontend applications it does not
control, while preserving the Sprint 16 evidence discipline.

Sprint 17 has two levels:

```text
Level 1
→ simple external public application/process

Level 2
→ dynamic/script-heavy external public application/process
```

Level 1 must be completed or truthfully stopped/closed before Level 2 is used to
drive product changes.

## Level 1 selected target

Historical authorized Level 1 target:

```text
application: GOV.UK
start: https://www.gov.uk/browse
process:
  Services and information
  → Driving and transport
  → Driving licences
  → Driving licence codes
expected observable outcome:
  final page heading is "Driving licence codes"
```

Target classification:

```text
difficulty: simple
control: external_stable
authentication: none
sensitivity: public
```

See `target-selection.md`.

## Level 1 purpose

The first test deliberately avoids search, authentication, forms, transactions,
and dynamic complexity.

The question is not whether TestCartographer can survive every web architecture.
It is:

> Can the existing nominal Creation Flow operate truthfully on one small
> external public process without fixture-specific help, internal state surgery,
> unsafe capture, or mutation of the original automation repository?

## Operator role

The operator acts as the intended testing professional and factual/review
authority.

The operator may:

- provide process purpose/risk/expected outcome,
- accept/reject semantic interpretations,
- resolve genuine ambiguity,
- review POM/adaptation/source proposals,
- authorize bounded browser actions,
- trigger execution.

The operator should **not** repair internal TestCartographer JSON/contracts,
edit TestCartographer source, inject discovered selectors manually into hidden
state, or otherwise rescue the nominal flow outside documented interfaces.

If such intervention appears necessary, preserve it as evidence and triage
against `ACC-REQ-016`.

## Product state rule

One ValidationRun binds one exact TestCartographer repository state.

A product-code change after a finding requires a new run/product commit.

Testware-only planning commits before execution are allowed, but the actual run
must record the exact final pre-execution commit.

## Framework write boundary

The existing original `qa-automation-framework` working repository is not an
allowed silent write target.

Expected delivery remains the currently accepted bounded sandbox/copy behavior.

Any unexpected write to the original framework is a critical concern against
`ACC-REQ-017`.

## Level 1 execution evidence

Required evidence should include, when produced safely:

- ValidationTargetProfile,
- ValidationRun,
- evidence manifest,
- minimized relevant ContextBundle/intake reference,
- ProjectProfile reference or project-state reference,
- minimized browser/discovery evidence,
- synthesis/adaptation summaries,
- bounded reviewed source patch,
- execution evidence,
- operator summary.

Full packages remain outside the Git repository.

## Finding rule

If any problem occurs:

```text
observe
→ preserve evidence
→ close/verify current run where possible
→ triage
→ open GitHub Issue if actionable
→ only then design a correction
```

Do not rewrite the target or handcraft hidden internal state to get a green run.

## Level 1 test cases

`ACC-EXT-001` remains the originally designed four-page navigation scenario.
Pre-execution analysis found that it is blocked by current single-page discovery
capability; see `ACC-FIND-002` / GitHub Issue #2.

`ACC-EXT-002` is the smallest first executable external scenario:

```text
https://www.gov.uk/driving-licence-codes
→ open page
→ discover/represent "Driving licence codes" heading
→ generate/review/sandbox/execute
```

This is a test-design correction driven by evidence. ACC-EXT-001 is not
rewritten or retroactively simplified.

## Level 1 exit gate

Level 1 may move toward closure when:

- selected target/process was explicitly authorized,
- ACC-EXT-001 executed or truthfully stopped,
- first material findings were preserved,
- evidence package integrity was verified,
- POM/source/execution quality was reviewed where reached,
- operator difficulty/confidence/reuse evidence was recorded,
- no unrecorded internal rescue was used,
- original automation repository remained protected,
- requirements/traceability were updated from actual evidence.

A passing generated test does not by itself close Level 1.

## Level 1B - analyst-rich validation

`ACC-EXT-003` is the authorized Level 1B acceptance test.

Authorized target:

```text
Practice Software Testing / Toolshop
https://practicesoftwaretesting.com/
```

Operator authorization and the final bounded read-only target preflight were
recorded on 2026-08-15 (Europe/Warsaw). The public no-auth catalogue remains
available, the working term `hammer` produces multiple visible relevant results,
and the public price-ascending sort supports the intended outcome semantics after
normal UI stabilization. No write action is required.

This is target-suitability evidence only. It does not freeze an exact result
count, product list, price, implementation path, or locator. At preflight time it
had not consumed a run identifier.

Execution evidence now shows:

```text
ACC-EXT-003-run-01
-> operator terminal interruption during intake
-> no product verdict
-> immutable and not reusable

ACC-EXT-003-run-02
-> nine guided-intake questions and aggregate context confirmation
-> no clarification of relevant/suitable or cheapest-first semantics
-> accepted context omitted the initial ordering preference
-> explicit stop: external public single-page creation supports heading outcomes only
-> browser discovery not started
-> framework sandbox not created
-> result: NOT ACCEPTED / PRODUCT FINDING
```

The independent findings were preserved as `ACC-FIND-007` / Issue #7,
`ACC-FIND-008` / Issue #8, and `ACC-FIND-009` / Issue #9 before remediation.
Issues #7 through #9 are resolved by bounded deterministic corrections and
regression evidence. The historical run-02 result is unchanged, and no run-03
identifier has been consumed.

Primary purpose:

> Challenge TestCartographer with richer, imperfectly structured analyst/tester
> intent while keeping the browser target bounded enough to distinguish intake
> and context-modeling failures from unrelated frontend complexity.

The process remains catalogue-focused and non-destructive. The operator starts
from a natural mission around finding suitable products and ordering relevant
results by price rather than from a prepared selector/test-script description.

The design intentionally leaves the meaning of relevant/suitable results
incomplete and forbids a prepared follow-up answer sheet.

See:

```text
level-1b-target-selection.md
../../test-cases/ACC-EXT-003.md
```

This testware authorization did not itself authorize product code changes.
Execution evidence separately authorized bounded corrections for Issues #7
through #9. Those corrections are complete, but a new-run external retest remains
required before Level 1B can be accepted.

## Level 2

No Level 2 target is authorized by this document.

Pracuj.pl remains one candidate because its public frontend is materially more
dynamic/script-heavy than the Level 1 GOV.UK target, but it is intentionally not
the only planned Level 2 application.

The current direction is to use multiple Level 2 public targets, including
Pracuj.pl plus two additional applications preferably from different functional
domains. Each target requires a separate scope, policy/robots review,
authorization, and test design before execution.

Level 1B execution produced its first product evidence. The nominal flow did not
reach the authorized target because intake and capability boundaries stopped it
before browser discovery. The lifecycle, rich same-page capability, and
intent-preservation findings are resolved, but Level 1B remains open pending a
new-run retest; Level 2 must not begin from this untested correction state.

No further product correction is authorized merely because the validation is
planned.
