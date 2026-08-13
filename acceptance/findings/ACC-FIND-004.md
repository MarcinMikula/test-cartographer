# ACC-FIND-004 — componentless external run is rejected by CreationEvaluation contract

## Status

**RESOLVED — verified by acceptance retest and regression evidence.**

Related GitHub Issue: `#4 [ACCEPTANCE] ACC-EXT-002 — componentless external run is rejected by CreationEvaluation contract`

## Discovery stage

```text
STLC phase: Test Execution
test case: ACC-EXT-002
external target: https://www.gov.uk/driving-licence-codes
tested product commit: 3cd9560149a922d62344d39c45fb9e289af93699
run: ACC-EXT-002-run-02
result: FAILED
prior finding retest: ACC-FIND-003 / Issue #3
```

## Progress proved before failure

The retest crossed the previously failing single-target discovery boundary and
continued through the intended external single-page workflow:

- guided intake and aggregate human context confirmation,
- headed browser discovery against the real GOV.UK target,
- one selected heading target with zero forced ambiguity decisions,
- discovery review,
- synthesis-handoff review,
- POM proposal review,
- repository adaptation-plan review,
- exact source-patch review,
- isolated sandbox execution trigger.

The generated patch was appropriately componentless for this bounded page-only
flow. It proposed a Page Object, one fixture, and one executable test, with no
component.

## Observation

After the operator accepted the execution trigger, TestCartographer failed while
constructing the final `CreationEvaluation`:

```text
pydantic_core._pydantic_core.ValidationError:
1 validation error for CreationEvaluation
  Value error, passed creation evaluation requires all execution and architecture checks
```

## Root cause

`build_creation_evaluation()` already treats component generation as conditional:
a component is required only when the accepted proposal contains components.

However `CreationEvaluation.validate_evaluation()` still requires
`component_generated == true` for every `PASSED` evaluation.

For this external single-page proposal:

```text
proposal.components = ()
component_generated = false
component required by builder = false
builder status = PASSED
model validator = rejects PASSED
```

This is an internal contract mismatch between the delivery-evaluation builder
and the persisted `CreationEvaluation` contract.

## Execution evidence interpretation

The runner performs compile, target collection, and target execution before
calling `build_creation_evaluation()`.

The builder can calculate `PASSED` only when collection, target execution,
verification results, required architecture checks, and original-framework
immutability are all satisfied.

Therefore the observed failure is evidence that the generated GOV.UK target test
had already successfully crossed execution before the final evaluation object
was rejected.

This does **not** make `ACC-EXT-002-run-02` a passing acceptance run. The run
remains FAILED because the product did not complete its supported workflow and
did not persist a valid final evaluation artefact.

## Requirement impact

Primary: `ACC-REQ-016`.

Related:

- `ACC-REQ-008`
- `ACC-REQ-009`

## Classification

```text
evidence kind: failure
classification: PRODUCT BUG
severity for Sprint 17 Level 1: blocker
GOV.UK defect: false
generated target-test failure: false
testware defect: false
```

## Coverage gap

Existing delivery-evaluation tests use the controlled public-search proposal,
which contains a component.

The external pipeline regression proves that the bounded external proposal
legitimately contains no component and reaches an exact source patch, but it
does not continue into `CreationEvaluation`.

## No-workaround rule

Do not rescue `ACC-EXT-002-run-02` by manually marking PASS, editing or inventing
`07-creation-evaluation.json`, adding a fake component, changing the acceptance
scenario, monkeypatching the validator, or manually resuming from an internal
stage.

## Smallest correction boundary

Represent whether component generation is required by the accepted proposal and
validate the implication rather than requiring a component universally:

```text
component_required = true
-> component_generated must be true for PASS

component_required = false
-> component_generated may be false for PASS
```

The builder should derive `component_required` deterministically from the
accepted proposal.

The correction must also preserve the component requirement for existing
component-bearing flows, regenerate `creation-evaluation-v0.1.schema.json`, and
add regression coverage for both componentless PASS and required-but-missing
component rejection.

## Retest rule

Keep `ACC-EXT-002-run-02` unchanged as failed evidence.

After remediation is committed and pushed, execute a new immutable
`ACC-EXT-002-run-03` against the new exact product commit.

## Related issue lifecycle

- Issue #1 remains open until the external Creation Flow completes end to end.
- Issue #2 remains open because multi-page discovery remains unsupported.
- Issue #3 remediation was successfully crossed by run-02.
- Issue #4 tracks this failure.

## Resolution

Status: RESOLVED.

`ACC-EXT-002-run-04` persisted a PASSED `CreationEvaluation` with `component_required=false` and `component_generated=false`, then completed independent framework execution with `1/1` tests passed.

Historical failed/incomplete evidence remains immutable and is not rewritten.
