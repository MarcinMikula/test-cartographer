# ACC-FIND-001 — Creation Flow is bound to controlled catalog fixture

## Status

**OPEN — preserved before remediation design.**

GitHub Issue: `#1 [ACCEPTANCE] ACC-EXT-001 — Creation Flow is bound to controlled catalog fixture`

## Discovery stage

```text
STLC phase: Environment / Target Setup
test case: ACC-EXT-001
external execution started: false
external target contacted by TestCartographer: false
tested product commit: 13ef8cbbac66b3971a7b8378e4f1efb761eb2563
```

## Observation

The public `creation interactive` entry point is not yet able to run the nominal
Creation Flow against an externally supplied application/process.

The current runner still couples the flow to the controlled catalog reference:
local browser fixture, fixed catalog discovery plan, catalog-search synthesis
shape, catalog Page Object names, public-search generation profile, and catalog
test target.

Changing only the URL would not make ACC-EXT-001 a truthful external Creation
Flow.

## Requirement impact

Primary: `ACC-REQ-016`.

Related: `ACC-REQ-001`, `ACC-REQ-005`, `ACC-REQ-008`, `ACC-REQ-009`.

Blocks validation gap: `V-1 — External public application validity`.

## Initial classification

```text
evidence kind: failure
operational triage: product limitation / product defect candidate
severity for Sprint 17 Level 1: blocker
target verdict: none
```

This is not a GOV.UK defect and not a failure observed on GOV.UK.

## No-workaround rule

Do not rescue the run through monkeypatching, test-only fixture substitution,
manual internal JSON repair, locator injection, or direct runner editing during
the same acceptance run.

## Smallest correction boundary

The correction should make the existing Creation Flow support one bounded
externally configured process while preserving current human authority, bounded
browser observation, explicit reviews, sandbox delivery, and evidence rules.

It does not need to solve arbitrary workflows, Level 2 dynamics, authentication,
API/SOM, production-repository delivery, broad crawling, or a multi-process
application graph.

## Retest rule

After a justified product correction, keep this finding unchanged and execute
ACC-EXT-001 as a new run against a new exact product commit.
