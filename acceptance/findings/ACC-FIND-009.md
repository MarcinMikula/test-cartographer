# ACC-FIND-009 — terminal interruption leaves operator session active

## Status

**OPEN — evidence-lifecycle finding preserved before remediation.**

GitHub Issue: pending creation after the finding-preservation commit.

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

## Correction boundary to design later

Once the operator ledger exists, every terminal process path must persist a
truthful non-active state before re-raising or returning. The product must
distinguish at least:

- supported operator pause/quit;
- operator interrupt;
- product/runtime abort;
- completed flow.

The correction must preserve the original exception, partial evidence, output
immutability, and non-resumable fresh-run rule unless resume is separately
designed and authorized.

## Regression and retest boundary

Focused regression should cover an exception after intake and an operator
interrupt after ledger creation. A future ACC-EXT-003 retest can confirm truthful
terminal behavior if another stop occurs, but run-01 and run-02 remain immutable.
