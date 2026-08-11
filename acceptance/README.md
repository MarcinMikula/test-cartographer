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

The acceptance phase starts after Sprint 16 closed the validation-evidence
protocol.

Initial test type:

> **Product Acceptance Testing — External Validation Campaign**

The process is STLC-derived and intentionally iterative. The initial
requirements and test cases are not treated as complete.

## Initial structure

Only artefacts needed now are created.

```text
acceptance/
├── README.md
├── acceptance-test-plan.md
├── stlc-workflow.md
├── requirements/
│   └── acceptance-requirements.md
├── test-cases/
│   └── ACC-EXT-001.md
└── campaigns/
    └── sprint-17-external-validation-I/
        ├── campaign-plan.md
        ├── target-selection.md
        └── traceability.md

added later when evidence requires them:
├── findings/
└── templates/
```

Empty structure is not committed merely to make the tree look complete.

## Sources of truth

```text
acceptance requirements/test basis
-> tracked on main under acceptance/

test cases and campaign records
-> tracked on main under acceptance/

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
