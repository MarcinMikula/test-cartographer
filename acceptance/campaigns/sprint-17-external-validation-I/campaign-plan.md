# Sprint 17 — External Validation I campaign plan

## Status

**Planning active. Execution not started.**

Campaign testware baseline before this slice:

```text
3b939026fcf9592710581dbd4682893fd0ff2029
docs: establish product acceptance test foundation
```

The first execution run will bind the exact clean Git commit that exists after
the Level 1 planning/test-case slice is accepted and committed.

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

Pending operator authorization:

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

## First test case

`ACC-EXT-001` is the first Level 1 end-to-end acceptance test.

See:

```text
acceptance/test-cases/ACC-EXT-001.md
```

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

## Level 2

No Level 2 target is authorized by this document.

Pracuj.pl is a candidate because its current public frontend appears materially
more dynamic, but a separate policy/robots review and test design are required
before use.
