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

Level 1B has consumed three runs. Historical run-02 remains **NOT ACCEPTED /
PRODUCT FINDING** at product commit
`ac1d7b61033251377b9b49d970c50f6d8cdf91e9`.

Run-03 tested the resolved Issues #7–#9 state at product commit
`c1d0237f12582e4d97a9e57cefe9dc3720d5ff27`. Guided intake and review
completed through three live Ollama calls, but the flow stopped before browser
discovery because no reviewed interaction targets were available for the
non-heading outcome. The session truthfully persisted `aborted`; no framework
change or target contact occurred. `ACC-FIND-010` is open for the missing
interactive bridge, run-04 is unconsumed, and the external target is not
implicated.

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

## Level 1B interim requirement traceability

| Requirement | ACC-EXT-003 run-02 | Execution evidence |
|---|---|---|
| ACC-REQ-001 | NOT ACCEPTED | The initial cheapest-first intent was absent from the accepted context summary. |
| ACC-REQ-002 | NOT ESTABLISHED | Bootstrap questions were asked; no compatible persistent ProjectProfile reuse was demonstrated. |
| ACC-REQ-003 | NOT ACCEPTED | Relevant/suitable and ordering ambiguity was neither clarified nor retained as UNKNOWN. |
| ACC-REQ-004 | PASS WITH MATERIAL CAVEAT | Runtime provenance was persisted, but the operator used disclosed ChatGPT translation and limited answer-content assistance. |
| ACC-REQ-005 | NOT REACHED | Product capability validation failed before browser discovery. |
| ACC-REQ-006 | PARTIAL | The operator confirmed the displayed context, but the product had already omitted material initial intent. |
| ACC-REQ-007 | NOT ACCEPTED | The bounded LLM question plan did not address the material ambiguity in the mission. |
| ACC-REQ-008 | NOT REACHED | No synthesis or automation proposal was produced. |
| ACC-REQ-009 | NOT REACHED | No sandbox or independent test execution occurred. |
| ACC-REQ-010 | PASS TO FINDING-PRESERVATION GATE | Run-01 and run-02 were retained and hashed before any remediation. |
| ACC-REQ-011 | PENDING | Any external retest requires a new run identifier and a new exact product commit after authorized remediation. |
| ACC-REQ-012 | NOT ACCEPTED | The process failed closed functionally, but the terminated run retained an `active` operator-session state and no formal package exists. |
| ACC-REQ-013 | NOT ESTABLISHED | The run stopped before final operator assessment and complete runtime measurement. |
| ACC-REQ-014 | PASS | The failure is classified against TestCartographer; no Toolshop defect verdict is made. |
| ACC-REQ-015 | NOT ACCEPTED | The capability exception was not converted into a controlled terminal session state. |
| ACC-REQ-016 | NOT ACCEPTED | The nominal external interface supports heading outcomes only and cannot represent the authorized same-page process. |
| ACC-REQ-017 | PASS | The clean framework baseline remained unchanged and no sandbox was created. |

The run-02 `ACC-REQ-012` and `ACC-REQ-015` outcomes remain historical **NOT
ACCEPTED** evidence and are not rewritten by later unit/regression success. The
bounded Issue #9 correction proves the terminal-state contract deterministically;
future external execution may corroborate it but is not required to close the
lifecycle defect.

The run-02 `ACC-REQ-016` outcome is likewise retained as historical evidence.
Commit `3b8bb73bd665f8d5389ff2b6a1299c023a97392e` separately proves the reviewed
multi-action same-page capability with deterministic contract, proposal,
generation, and regression coverage. It resolves `ACC-FIND-007` without claiming
that run-02 passed or that the full Level 1B scenario is accepted.

The run-02 `ACC-REQ-001`, `ACC-REQ-003`, `ACC-REQ-006`, and `ACC-REQ-007`
outcomes also remain historical. Commit
`23d3f34be364163337e055f50548e2dfc35a6fd3` separately proves side-by-side
mission/context review, bounded review planning, targeted clarification,
operator-facing prompt persistence, explicit human material-intent confirmation,
and fail-closed unresolved-context handling. It resolves `ACC-FIND-008` without
claiming that run-02 passed or that the full Level 1B scenario is accepted.

## Level 1B run-03 requirement traceability

| Requirement | ACC-EXT-003 run-03 | Execution evidence |
|---|---|---|
| ACC-REQ-001 | NOT ACCEPTED | The operator entered application identity as the initial mission; the authorized hammer/cheapest-first mission was not supplied. |
| ACC-REQ-002 | NOT ESTABLISHED | Shifted bootstrap values were accepted; compatible persistent bootstrap reuse was not demonstrated. |
| ACC-REQ-003 | NOT ACCEPTED | Disclosed erroneous ChatGPT assistance supplied expected-result semantics to a risk clarification, and the mismatched value was confirmed. |
| ACC-REQ-004 | PASS WITH MATERIAL CAVEAT | Human, Ollama, and product provenance remained distinguishable, but the run includes operator error and answer-content assistance. |
| ACC-REQ-005 | NOT REACHED | The flow stopped before browser discovery and never contacted Toolshop. |
| ACC-REQ-006 | PARTIAL | Side-by-side review and explicit human confirmation occurred, but the operator confirmed materially corrupted context. |
| ACC-REQ-007 | INCONCLUSIVE | Three live bounded Ollama calls completed, but the wrong initial mission and assisted risk answer prevent a clean model-quality verdict. |
| ACC-REQ-008 | NOT REACHED | No reviewed rich-action proposal was produced by the nominal interactive path. |
| ACC-REQ-009 | NOT REACHED | No sandbox, generated target test, or independent execution existed. |
| ACC-REQ-010 | PASS TO FINDING-PRESERVATION GATE | The five run files and supplied archive were hashed before remediation. |
| ACC-REQ-011 | PENDING | Run-04 is permitted only after separately authorized ACC-FIND-010 remediation. |
| ACC-REQ-012 | PASS WITH LIMITATION | The five-file evidence set is immutable and hashed; no formal ValidationRun package exists. |
| ACC-REQ-013 | PARTIAL | Three model latencies were captured (125.511 s, 89.841 s, 93.721 s; 309.073 s total), but no final assessment was reached. |
| ACC-REQ-014 | PASS | The stop is classified against TestCartographer; no Toolshop defect verdict is made. |
| ACC-REQ-015 | PASS | The unhandled runtime error persisted the operator session as `aborted`. |
| ACC-REQ-016 | NOT ACCEPTED | Guided context could not cross the nominal interface into reviewed rich interaction targets. |
| ACC-REQ-017 | PASS | The fixed clean framework baseline remained unchanged and no sandbox was created. |

Run-03 is not a clean nominal retest of Issue #8. Its wrong initial mission,
shifted bootstrap answers, and disclosed ChatGPT content error are part of the
evidence, not facts to erase. They also do not explain the deterministic final
bridge failure. The live provider completed all three calls within the configured
600-second timeout; no provider switch is justified by this run alone.

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

ACC-FIND-007 / Issue #7
external single-page flow supports heading outcomes only
-> RESOLVED
-> run-02 stopped before browser discovery
-> fix commit 3b8bb73bd665f8d5389ff2b6a1299c023a97392e
-> reviewed FILL/CLICK/SELECT/CHECK/UNCHECK/final READ boundary
-> 25 focused / 500 full-suite tests PASS
-> no external retest required before Issue #8 remediation

ACC-FIND-008 / Issue #8
guided intake omitted material ambiguity and ordering intent
-> RESOLVED
-> run-02 accepted context lost cheapest-first semantics
-> fix commit 23d3f34be364163337e055f50548e2dfc35a6fd3
-> bounded review-plan clarification and human intent-coverage gate
-> 20 focused / 505 full-suite tests PASS
-> new external retest still required for Level 1B

ACC-FIND-009 / Issue #9
terminal exception leaves operator session active
-> RESOLVED
-> fix commit 5887f83b5159c8751ef9a5a5638f7dc9afd259ce
-> runtime exception persists aborted
-> KeyboardInterrupt persists interrupted
-> supported QUIT remains paused
-> 5 focused / 492 full-suite tests PASS
-> run-03 live-corroborated aborted after an unhandled ValueError

ACC-FIND-010
interactive guided flow cannot produce reviewed rich interaction targets
-> OPEN / Level 1B blocker
-> run-03 intake and material-intent review completed
-> nominal runner supplied no reviewed_targets
-> deterministic stop before browser discovery
-> target not contacted; run-04 not authorized
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

ACC-EXT-003
-> analyst-rich same-page catalogue process
-> run-01 operator-interrupted during intake
-> run-02 NOT ACCEPTED / PRODUCT FINDING before browser discovery
-> ACC-FIND-007 through ACC-FIND-009 resolved deterministically
-> run-03 NOT ACCEPTED / PRODUCT FINDING before browser discovery
-> blocked by open ACC-FIND-010; run-04 unconsumed
```

## Level 2

No test case or target authorized yet.
