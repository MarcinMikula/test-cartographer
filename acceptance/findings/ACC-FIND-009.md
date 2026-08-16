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

Primary violated requirements under the v0.2 interpretation:

- ACC-REQ-019 — a terminated process remained persisted as active.

At the run-02 basis, ACC-REQ-012 and ACC-REQ-015 were used as the nearest
available proxy requirements. Their historical linkage is retained, but neither
states the truthful terminal-lifecycle obligation precisely.

Guardrails corroborated:

- ACC-REQ-010 — partial evidence was preserved before remediation;
- ACC-REQ-014 — the stale state was not attributed to the external target;
- ACC-REQ-017 — the original framework remained unchanged.

Supporting / traceability requirements:

- ACC-REQ-011 — later live runs corroborate the deterministic correction;
- ACC-REQ-012 and ACC-REQ-015 — historical proxy mappings only;
- ACC-REQ-016 — the failure occurred in a nominal product workflow.

Requirements derived or revised:

- ACC-REQ-019 — acceptance requirements v0.2 now represent truthful persisted
  lifecycle explicitly. It does not retroactively alter the run-02 requirement
  basis or verdict.

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


## Run-03 live corroboration

Run-03 exercised the corrected lifecycle at product commit
`c1d0237f12582e4d97a9e57cefe9dc3720d5ff27`. After guided intake completed,
the runner raised the unhandled reviewed-target `ValueError`. The persisted
operator session truthfully ended `aborted` with twelve recorded operator
actions, `headed_browser_used=false`, and no `creation_flow_run_id`.

This is live corroboration of the Issue #9 correction, not a deliberate failure
created to retest it. Historical runs remain immutable and the finding remains
resolved.

## Run-04 live corroboration

Run-04 again exercised the corrected lifecycle at product commit
`9494ac1d33e4a5f0b76d22eaf7819c2f150c49f6`. After the target-proposal
contract failed, the persisted operator session ended `aborted` with eleven
actions, `headed_browser_used=false`, and no CreationFlowRun ID.

This is a second live corroboration of the Issue #9 correction. It does not
reopen the resolved finding and it does not convert the new proposal-contract
failure into a lifecycle defect.

## Run-05 live corroboration

Run-05 again persisted `aborted` after the non-repairable target-proposal rule
failed closed. Eleven operator actions were retained,
`headed_browser_used=false`, and no CreationFlowRun ID exists. This is a third
live corroboration of the lifecycle correction and does not reopen this finding.
