# ACC-FIND-009 — terminal interruption leaves operator session active

## Status

**RESOLVED — deterministic product correction and regression evidence preserved.**

Related GitHub Issue: `#9 [ACCEPTANCE] ACC-EXT-003 — terminal interruption leaves operator session active`

## Discovery context

Primary evidence:

```text
test case: ACC-EXT-003
run: ACC-EXT-003-run-02
product commit: ac1d7b61033251377b9b49d970c50f6d8cdf91e9
terminal cause: unhandled heading-only ValueError
persisted operator-session state after termination: active
recorded operator actions: 11
```

Corroborating non-product-verdict attempt:

```text
run: ACC-EXT-003-run-01
terminal cause: operator KeyboardInterrupt during intake
persisted operator-session state after termination: active
recorded operator actions: 4
```

## Observation

Run-02 terminated with an unhandled capability exception after guided intake.
The output directory and partial evidence remained preserved, but the persisted
operator session still claimed `active` after the process no longer existed.

Run-01 independently shows the same stale-active outcome after an operator
terminal interruption. Run-01 is not a product-verdict run, but it demonstrates
that the lifecycle gap is broader than the heading-only exception path.

## Classification

```text
kind: lifecycle / evidence-state defect
severity: Level 1B evidence blocker
historical output preserved: true
false PASS reported: false
truthful terminal session state: false
target defect: false
```

Primary requirements: `ACC-REQ-012`, `ACC-REQ-015`.

Related requirements: `ACC-REQ-010`, `ACC-REQ-016`.

## No-workaround rule

Do not edit `operator-session.json`, mark either run complete, delete/reuse the
output directories, or fabricate a CreationFlowRun/ValidationRun artefact.

## Authorized correction and implementation

The operator authorized the smallest Issue #9-only lifecycle correction after
the finding and GitHub Issue were durably preserved. Product commit
`5887f83b5159c8751ef9a5a5638f7dc9afd259ce` now ensures that:

- supported operator `QUIT` remains `paused`;
- `KeyboardInterrupt` persists `interrupted`;
- an unhandled product/runtime exception persists `aborted`;
- a successful flow still persists `complete`;
- only an existing persisted `active` session may be transitioned;
- the original exception is re-raised after best-effort persistence.

The schema and lifecycle documentation include the new `interrupted` state.
Issues #7/#8, the external-flow outcome contract, and the LLM question planner
were not changed.

## Regression and retest result

Validation on 2026-08-16 (Europe/Warsaw) recorded:

```text
focused tests: 5 passed in 0.71s
full suite: 492 passed in 53.12s
historical run-01/run-02 changed: false
external run consumed: no
run-03 consumed: no
live LLM/Ollama invoked: no
original framework changed: false
```

The deterministic regression covers both evidence-bearing failure classes and
the supported pause path. A later ACC-EXT-003 execution may corroborate the
contract if it terminates early, but no deliberate external failure or new run
is required to close this lifecycle defect. Run-01 and run-02 remain immutable.
