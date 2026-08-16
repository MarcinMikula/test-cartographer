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
Runs 01 through 05 retain their historical results and immutable evidence.

`ACC-EXT-003-run-05` tested product commit
`782e11c8d4defea267510467e41377a2c5aef621` after the deterministic Issue #11
correction. The natural mission correctly named Toolshop, `hammer`, and
lowest-to-highest price ordering. Two guided-intake calls and one target-proposal
call completed through local Ollama. The proposal failed deterministic validation
at the safe diagnostic `schema:actions[1]:unsupported_validation_rule`.

The run remains **NOT ACCEPTED / PRODUCT–PROVIDER INTEGRATION FINDING**. The
Issue #11 behavior is a live PASS: an unallowlisted rule remained non-repairable,
no `RETRY` or second proposal call was offered, and the session ended `aborted`
without raw provider persistence. Issues #7 through #11 remain resolved. The new
`ACC-FIND-012` / Issue #12 records that the provider-facing schema and safe recovery
classifier do not cover the complete action-conditioned contract enforced by
local validators. Browser discovery never started, no framework sandbox was
created, and Toolshop was not contacted. Run-06 is unconsumed and unauthorized.

Acceptance requirements v0.2 are now the planned basis for Issue #12 closure
and any later run-06. ACC-REQ-018 through ACC-REQ-020 were derived from preserved
Sprint 17 evidence; they do not retroactively change the requirement basis,
evidence, or verdict of runs 01 through 05.

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

ACC-EXT-003-run-03
-> product commit c1d0237f12582e4d97a9e57cefe9dc3720d5ff27
-> operator entered application identity as the initial mission and shifted the
   next bootstrap answers
-> three live Ollama calls: 125.511 s collection, 89.841 s review, 93.721 s review
-> disclosed ChatGPT answer assistance put expected-result semantics into risk
-> guided intake and material-intent review completed
-> explicit stop: reviewed interaction targets are required for non-heading outcomes
-> operator session persisted aborted; browser discovery did not start
-> framework sandbox not created; target not contacted
-> result: NOT ACCEPTED / PRODUCT FINDING

ACC-EXT-003-run-04
-> product commit 9494ac1d33e4a5f0b76d22eaf7819c2f150c49f6
-> natural mission omitted the authorized hammer and cheapest-first semantics
-> no prepared answers or answer-content assistance; fixture_answers_used=false
-> three live Ollama calls: 121.355 s collection, 78.448 s review, 36.086 s target proposal
-> Issue #10 bridge invoked and proposal evidence persisted
-> proposal blocked before human review: invalid_target_contract
-> exact violated contract unavailable; raw provider response not persisted
-> operator session persisted aborted; browser discovery did not start
-> framework sandbox not created; target not contacted
-> result: NOT ACCEPTED / PRODUCT–PROVIDER INTEGRATION FINDING

ACC-EXT-003-run-05
-> product commit 782e11c8d4defea267510467e41377a2c5aef621
-> natural mission included Toolshop, hammer, and lowest-to-highest price ordering
-> no prepared answers or answer-content assistance; fixture_answers_used=false
-> three live Ollama calls: 123.879 s collection, 89.939 s review, 53.374 s target proposal
-> safe diagnostic: schema:actions[1]:unsupported_validation_rule
-> repairable=false; no RETRY prompt and no second target-proposal call
-> proposal blocked before human review; raw provider content not persisted
-> operator session persisted aborted; browser discovery did not start
-> framework sandbox not created; target not contacted
-> result: NOT ACCEPTED / ACC-FIND-012
```

Findings `ACC-FIND-007` through `ACC-FIND-011` remain resolved
deterministically. Run-05 live-corroborates the bounded Issue #11 behavior for a
non-repairable unallowlisted rule and exposes the separate open
`ACC-FIND-012` / Issue #12. Runs 01 through 05 remain immutable and **NOT ACCEPTED** where
recorded. No run-06 or product remediation is authorized by this preservation.

Before Issue #12 product code changes, a testware-only gate shall establish:

- acceptance requirements v0.2;
- finding-to-requirement separation between primary violations, corroborated
  guardrails, supporting traceability, and derived/revised requirements;
- a complete run-06 target-proposal and recovery oracle in ACC-EXT-003;
- unchanged historical run evidence and overall verdicts.

This gate performs no live provider call, browser execution, target contact, or
framework mutation and does not consume run-06.

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
through #11, and those deterministic corrections remain complete. Run-05 is new
evidence for `ACC-FIND-012` / Issue #12; preserving and linking it does not authorize a correction,
provider switch, or run-06. Level 1B remains not accepted.

## Level 2

No Level 2 target is authorized by this document.

Pracuj.pl remains one candidate because its public frontend is materially more
dynamic/script-heavy than the Level 1 GOV.UK target, but it is intentionally not
the only planned Level 2 application.

The current direction is to use multiple Level 2 public targets, including
Pracuj.pl plus two additional applications preferably from different functional
domains. Each target requires a separate scope, policy/robots review,
authorization, and test design before execution.

Level 1B execution has still not reached the authorized target. The lifecycle,
rich same-page engine, intent-preservation, reviewed-target bridge, and bounded
proposal-recovery findings remain resolved, but run-05 exposed the separate open
`ACC-FIND-012` / Issue #12 before browser discovery. Runs 03 through 05 remain
**NOT ACCEPTED**. Level 2 must not begin before this finding is separately
remediated if authorized and truthfully retested under a new run ID.

No further product correction is authorized merely because the validation is
planned.
