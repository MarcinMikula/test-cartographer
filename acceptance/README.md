# TestCartographer product acceptance

This directory contains the versioned testware used to decide whether
TestCartographer is acceptable as a product on applications that were not built
for TestCartographer.

It is deliberately separate from:

```text
docs/       -> product, architecture, lifecycle, and current-state documentation
tests/      -> automated tests of TestCartographer implementation
acceptance/ -> product acceptance basis, scenarios, campaigns, and closure
```

Full validation evidence packages remain outside the repository under the local
acceptance artefact area. GitHub Issues are the operational source of truth for
actionable bugs/findings.

## Current phase

The first external product-acceptance slice is complete.

```text
Sprint 17 Level 1
target: GOV.UK
scenario: ACC-EXT-002
passing run: ACC-EXT-002-run-04
result: PASS
independent framework execution: 1/1 PASS
formal evidence package: VERIFIED
```

The human-readable result and its limits are summarized in:

```text
campaigns/sprint-17-external-validation-I/level-1-validation-report.md
```

The detailed acceptance oracle and execution record remain in
`test-cases/ACC-EXT-002.md`, while requirement-by-requirement evidence remains in
the campaign `traceability.md`.

Level 1B execution continues as `ACC-EXT-003` on Practice Software
Testing / Toolshop. Runs 01 through 05 retain their historical evidence and
verdicts.

`ACC-EXT-003-run-05` tested product commit
`782e11c8d4defea267510467e41377a2c5aef621` from a correctly scoped natural
mission containing Toolshop, `hammer`, and lowest-to-highest price ordering. Two
guided-intake calls and one target-proposal call completed through the configured
local Ollama provider. The proposal reached deterministic contract validation,
then failed closed at `schema:actions[1]:unsupported_validation_rule`. The rule
was correctly non-repairable under the Issue #11 contract, so no `RETRY` prompt
or second proposal call occurred.

`ACC-FIND-007` through `ACC-FIND-011` remain resolved. Run-05 live-corroborates
the Issue #9 aborted lifecycle, Issue #10 bridge, and Issue #11 safe diagnostic
and non-repairable fail-closed behavior. It exposes the separate
`ACC-FIND-012` / Issue #12: the provider-facing proposal schema and safe recovery classifier
do not cover the full action-conditioned contract enforced locally. The session
ended `aborted`; browser discovery did not start, no framework sandbox was
created, and Toolshop was not contacted. Level 1B remains **NOT ACCEPTED**.
Run-06 is unconsumed and unauthorized pending separate remediation
authorization and a later fresh pre-run gate.

Level 2 remains reserved for materially more dynamic/script-heavy public
applications. Pracuj.pl is one candidate, not the only planned Level 2 target.

## Current structure

```text
acceptance/
|-- README.md
|-- acceptance-test-plan.md
|-- stlc-workflow.md
|-- requirements/
|   `-- acceptance-requirements.md
|-- test-cases/
|   |-- ACC-EXT-001.md
|   |-- ACC-EXT-002.md
|   `-- ACC-EXT-003.md
|-- findings/
|   |-- ACC-FIND-001.md
|   |-- ACC-FIND-002.md
|   |-- ACC-FIND-003.md
|   |-- ACC-FIND-004.md
|   |-- ACC-FIND-005.md
|   |-- ACC-FIND-006.md
|   |-- ACC-FIND-007.md
|   |-- ACC-FIND-008.md
|   |-- ACC-FIND-009.md
|   |-- ACC-FIND-010.md
|   |-- ACC-FIND-011.md
|   `-- ACC-FIND-012.md
`-- campaigns/
    `-- sprint-17-external-validation-I/
        |-- campaign-plan.md
        |-- target-selection.md
        |-- level-1b-target-selection.md
        |-- traceability.md
        `-- level-1-validation-report.md
```

Empty structure is not committed merely to make the tree look complete.

## Sources of truth

```text
acceptance requirements/test basis
-> tracked on main under acceptance/

test cases and campaign records
-> tracked on main under acceptance/

human-readable campaign result
-> campaign validation reports

immutable ValidationRun/evidence packages
-> TestCartographer-local-artifacts/

actionable bug/finding lifecycle
-> GitHub Issues

product correction
-> short-lived fix/* branch when code behavior changes
```

A `ValidationFinding` is immutable evidence from a particular run. A GitHub
Issue is a mutable operational record used to triage and resolve an actionable
problem. They are related but not interchangeable.

The validation report is not a replacement for immutable evidence,
requirement traceability, or the test case. Its purpose is to make the result
understandable to a reader who did not participate in the campaign.

## Testware evolution rule

Acceptance testware is expected to evolve.

A real finding may justify:

- adding an acceptance requirement,
- splitting an overly broad requirement,
- clarifying wording or evidence expectations,
- adding a new test case,
- changing test priority,
- documenting a legitimate product limitation,
- adding a regression/retest condition.

This is controlled learning, not automatically scope creep.

Rules:

1. Never rewrite historical execution evidence to match a newer requirement.
2. Requirement IDs are never reused for a different meaning.
3. Material requirement changes update requirement history.
4. A test case records the requirement/test basis used when it was designed.
5. New requirements are tested from the point they become active; prior runs are
   not retroactively declared failed without an explicit closure rationale.
6. Testware-only slices may be committed incrementally to `main`.
7. Product-code fixes use short-lived branches when a real product change is
   justified.

## Finding-to-requirement traceability taxonomy

A finding must not treat every relevant requirement as failed. Use four
separate relationships:

```text
Primary violated requirements
-> requirements directly contradicted by the observed product behavior

Guardrails corroborated
-> safety, authority, provenance, integrity, or write-boundary requirements
   that continued to hold while the finding occurred

Supporting / traceability requirements
-> requirements that govern evidence, remediation, retest, measurement, or a
   downstream result without being directly violated by the finding

Requirements derived or revised
-> new or revised acceptance obligations justified by the preserved evidence
```

Run-level requirement outcomes and finding-level relationships are different
views. A run may remain **NOT ACCEPTED** while several guardrails receive PASS
evidence. Reclassifying a relationship or requirement interpretation does not
change immutable evidence, run identity, or the historical overall verdict.

When a later requirement version clarifies an earlier run, record both the
historical basis and the newer interpretation. Do not silently rewrite the old
classification and do not retroactively fail a run against a requirement that
was not active at execution time.

## Acceptance is not "all green"

Campaign closure may be:

```text
PASS
PASS WITH LIMITATIONS
NOT ACCEPTED
INCONCLUSIVE / MORE EVIDENCE REQUIRED
```

At run level, a correct `BLOCKED`, `REVIEW`, `UNKNOWN`, or safe stop may
demonstrate desired behavior when evidence or authorization is genuinely
insufficient.

A passing generated pytest test alone is not sufficient product acceptance.
