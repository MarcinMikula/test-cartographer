# ACC-FIND-003 — single-target discovery run is rejected by runtime contract

## Status

**OPEN — preserved before remediation.**

Related GitHub Issue: `#3 [ACCEPTANCE] ACC-EXT-002 — single-target discovery run is rejected by runtime contract`

## Discovery stage

```text
STLC phase: Test Execution
test case: ACC-EXT-002
external execution started: true
external target: https://www.gov.uk/driving-licence-codes
tested product commit: 44d98f6c957d09685bf3956783a3b11f3a57e179
run: ACC-EXT-002-run-01
result: FAILED
```

## Observation

The external single-page Creation Flow completed guided intake and the aggregate
human context review, then entered browser discovery.

The external plan correctly contained one discovery target for the reviewed
heading outcome. Browser discovery produced one `DiscoveryTargetResult`, but
construction of `ProcessDiscoveryRun` failed before discovery review because the
runtime contract still required at least two target results.

Observed failure:

```text
pydantic_core._pydantic_core.ValidationError:
1 validation error for ProcessDiscoveryRun
targets
Tuple should have at least 2 items after validation, not 1
```

The implementation is internally inconsistent:

```text
ProcessDiscoveryPlan.targets -> Field(min_length=1)
ProcessDiscoveryRun.targets  -> Field(min_length=2)
```

The exported `process-discovery-run-v0.1.schema.json` also still declares
`targets.minItems = 2`.

## Requirement impact

Primary: `ACC-REQ-016`.

Related: `ACC-REQ-005`, `ACC-REQ-008`, `ACC-REQ-009`.

Blocks execution of `ACC-EXT-002`.

## Classification

```text
evidence kind: failure
classification: PRODUCT BUG
severity for Sprint 17 Level 1: blocker
target verdict: none
GOV.UK defect: false
testware defect: false
```

The failure is in TestCartographer's own discovery-run contract and occurred
after the external target had been opened. It must not be attributed to GOV.UK.

## No-workaround rule

Do not rescue `ACC-EXT-002-run-01` by editing generated run JSON, injecting a
second fake target, changing the acceptance scenario, monkeypatching Pydantic,
or manually resuming from an internal stage.

## Smallest correction boundary

Align `ProcessDiscoveryRun.targets` with the already accepted single-target
`ProcessDiscoveryPlan` capability:

- allow one or more target results,
- regenerate the discovery-run JSON Schema,
- add a regression test proving a valid one-target run,
- preserve existing multi-target behavior and all other run validators.

No multi-page, auth, arbitrary interaction, or target-specific exception is
required.

## Retest rule

Keep `ACC-EXT-002-run-01` unchanged as failed evidence.

After the correction is committed on the remediation branch, execute
`ACC-EXT-002` again as a new immutable run (`ACC-EXT-002-run-02`) against the
new exact product commit.
