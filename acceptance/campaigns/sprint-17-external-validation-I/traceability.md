# Sprint 17 External Validation I — traceability

## Status

**Level 1 external single-page acceptance executed and closed.**

Passing scenario:

```text
ACC-EXT-002
run: ACC-EXT-002-run-04
tested product commit: bd6595ab89c5c4c2d1e6317ee372bfaa9a74462f
target: https://www.gov.uk/driving-licence-codes
result: PASS
independent target tests: 1/1
formal evidence package: VERIFIED
package fingerprint:
2d297736725ee99363b1e37e69b7972fa284af8ada2083325849537b2ab69381
```

The original `ACC-EXT-001` four-page scenario remains **BLOCKED** by
`ACC-FIND-002` / Issue #2 because multi-page discovery is not implemented.

## Level 1 requirement traceability

| Requirement | ACC-EXT-002 closure | Execution evidence |
|---|---|---|
| ACC-REQ-001 | PASS | Run-04 started from bounded operator intent and completed guided intake. |
| ACC-REQ-002 | NOT PRIMARY / NOT ESTABLISHED | Same-project bootstrap reuse was not the purpose of this scenario; do not infer proof from run-04. |
| ACC-REQ-003 | PASS within observed scope | No unsupported ambiguity was silently promoted; reviewed context/discovery completed without forced ambiguity. |
| ACC-REQ-004 | PASS | Human answers, browser discovery, deterministic selection, LLM-guided intake, reviews, and generated artefacts remain distinguishable in persisted evidence. |
| ACC-REQ-005 | PASS | Browser work stayed on the approved GOV.UK page; bounded candidates were persisted without raw page, screenshot, HTML, input-value, or generic page-text retention. |
| ACC-REQ-006 | PASS | Explicit human confirmation/review gates were used through intake, discovery, synthesis, patch review, and execution trigger. |
| ACC-REQ-007 | PASS | Live LLM use was bounded to guided intake; discovery selection was deterministic and execution required no live LLM. |
| ACC-REQ-008 | PASS | Page Object, adaptation plan, exact source patch, fixture, test, and assertion intent were reviewable before application/execution. |
| ACC-REQ-009 | PASS | Generated target test executed independently in the framework sandbox; `1/1` passed. |
| ACC-REQ-010 | PASS | ACC-FIND-001/003/004/005/006 were preserved before remediation; ACC-FIND-002 remains open and preserved; historical failed/incomplete runs were not rewritten. |
| ACC-REQ-011 | PASS through acceptance traceability | Corrections used new run identifiers where external retest was applicable: `run-01 -> run-02`; the correction after run-02 was intended for run-03, but run-03 was consumed before nominal execution by ACC-FIND-005, so `run-04` became the actual completed retest. The formal Sprint 16 package for run-04 is standalone and does not encode the pre-package historical predecessor chain. |
| ACC-REQ-012 | PASS | Formal run-04 package independently verified target/run identity, manifest, SHA-256 integrity, sensitivity policy, expected files, and absence of hidden/unmanifested files. |
| ACC-REQ-013 | PASS WITH CAVEAT | Timing and operator assessment were captured (`hard`, `high`, `reuse=yes`), with no savings claim. Recorded `730.247s` is interpreted as prompt-to-response/operator-response elapsed time, not proof of continuous active work. |
| ACC-REQ-014 | PASS | Product failures were recorded as TestCartographer findings; none were converted into a GOV.UK defect verdict. |
| ACC-REQ-015 | NOT TRIGGERED | No auth, destructive action, sensitive-data boundary, scope escape, rate-limit, or policy stop was encountered in run-04. Passing this scenario does not claim coverage of every stop condition. |
| ACC-REQ-016 | PASS after remediation | Run-04 completed the nominal supported external single-page workflow without manual internal JSON/source/state surgery. |
| ACC-REQ-017 | PASS | CreationEvaluation records the original automation framework as unchanged; patch application was confined to the approved sandbox/copy. |

## Finding / retest chain

```text
ACC-FIND-001 / Issue #1
catalog-fixture binding
-> RESOLVED by bounded external single-page Creation Flow
-> ACC-EXT-001 still separately blocked by ACC-FIND-002

ACC-FIND-002 / Issue #2
multi-page discovery unsupported
-> OPEN
-> blocks ACC-EXT-001 only

ACC-FIND-003 / Issue #3
single-target ProcessDiscoveryRun rejected
-> RESOLVED
-> run-02 crossed boundary
-> run-04 final end-to-end PASS

ACC-FIND-004 / Issue #4
componentless CreationEvaluation rejected
-> RESOLVED
-> run-04 component_required=false / component_generated=false / PASS

ACC-FIND-005 / Issue #5
existing output could be destructively removed
-> RESOLVED
-> focused fail-closed regression
-> run-04 used a new immutable output id and completed

ACC-FIND-006 / Issue #6
browser-discovery live LLM calls overcounted
-> RESOLVED
-> finding commit 657bad79d991e66b8f48f586fc2d212cd50688e6
-> fix commit ab4f3f5e873f0849a2d418a9a0c6cf7ff8279839
-> no new external run required
```

## Formal evidence package

Location is intentionally outside the repository:

```text
TestCartographer-local-artifacts/validation/govuk/
  ACC-EXT-002-run-04/
  ACC-EXT-002-run-04-package/
```

Contract identity:

```text
ValidationRun id: acc_ext_002_run_04
validation run fingerprint:
281c0eac510eacb98eeda16c3e5bae96c0c2cf87bc2c1739be9d4360bfcf7c96

target fingerprint:
85691211bcbde45eb885309a6518875392f084409a6d3a4b4db33a277dd875c0

package fingerprint:
2d297736725ee99363b1e37e69b7972fa284af8ada2083325849537b2ab69381

manifest entries: 7
independent verification: PASS
run-04 source evidence changed by packaging: false
```

The package was built after run-04 from selected immutable evidence. The
package's `ValidationRun` is standalone because earlier acceptance attempts
predated formal ValidationRun packaging; historical predecessor/retest links are
therefore retained in this traceability record and the finding documents rather
than fabricated inside the contract.

## Level 1 scenario status

```text
ACC-EXT-001
-> four-page GOV.UK navigation
-> BLOCKED by ACC-FIND-002 / Issue #2

ACC-EXT-002
-> single-page GOV.UK heading verification
-> PASS via ACC-EXT-002-run-04
-> formal evidence package VERIFIED
```

## Level 2

No test case or target authorized yet.
