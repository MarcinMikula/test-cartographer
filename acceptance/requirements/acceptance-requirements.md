# Acceptance Requirements v0.2

## 1. Purpose

These requirements define the initial product acceptance basis for external
validation. They are **not assumed complete**.

Real external execution is expected to expose missing, ambiguous, overly broad,
or unnecessary requirements.

## 2. Requirement lifecycle

Statuses:

```text
ACTIVE
REVISED
RETIRED
DEFERRED
```

Rules:

1. IDs are stable and never reused.
2. Material meaning changes create a revision entry and may require test-case
   review.
3. A newly discovered requirement receives a new ID.
4. Historical runs remain tied to the basis recorded at execution time unless
   closure explicitly re-evaluates them.
5. Requirements describe desired behavior/acceptance quality, not speculative
   implementation.

## 3. Active requirements

### ACC-REQ-001 — Start from bounded operator intent
**Status:** ACTIVE · **Priority:** Critical

TestCartographer shall begin a new UI automation process from bounded
operator-provided intent without requiring a pre-authored complete
`ContextBundle`. Unknown facts remain explicit.

### ACC-REQ-002 — Ask only justified context
**Status:** ACTIVE · **Priority:** High

The product shall request missing context needed by the current process while
reusing accepted compatible project/bootstrap knowledge. Already accepted
project-wide questions shall not be repeated without an invalidation reason.

### ACC-REQ-003 — Preserve uncertainty
**Status:** ACTIVE · **Priority:** Critical

Unknown, ambiguous, stale, conflicting, or unsupported information shall not be
silently converted into confirmed truth. Explicit unknown/review/blocked/
conflicting outcomes are valid.

### ACC-REQ-004 — Preserve authority and provenance
**Status:** ACTIVE · **Priority:** Critical

Material context used for automation shall retain enough provenance to
distinguish human-provided truth, application observation, deterministic
validation, and LLM proposal.

### ACC-REQ-005 — Keep browser discovery bounded
**Status:** ACTIVE · **Priority:** Critical

Browser discovery/observation shall remain within approved target, process,
actions, and evidence-minimization boundaries. Unrestricted crawling or broad
raw-page capture shall not be required for the tested scope.

### ACC-REQ-006 — Keep the human authoritative
**Status:** ACTIVE · **Priority:** Critical

Where semantic meaning, ambiguity resolution, or acceptance cannot be
established safely, explicit human authority is required. Invalid/accidental
input shall not cross an accept/reject authority boundary.

### ACC-REQ-007 — Bound LLM authority
**Status:** ACTIVE · **Priority:** Critical

An LLM may organize, phrase, propose, or map authorized evidence, but shall not
silently become factual authority for business rules, expected outcomes,
credentials, authorization, or unsupported application state.

### ACC-REQ-008 — Produce reviewable automation design
**Status:** ACTIVE · **Priority:** High

The accepted process shall result in automation structure reviewable for Page
Object/component placement, locator meaning, action placement, symbolic data,
assertion intent, and unnecessary duplication. Execution success alone is not
sufficient.

### ACC-REQ-009 — Produce independently executable automation
**Status:** ACTIVE · **Priority:** Critical

Accepted generated/adapted tests shall run through the automation framework
without requiring TestCartographer or a live LLM during normal execution.

### ACC-REQ-010 — Preserve findings before remediation
**Status:** ACTIVE · **Priority:** Critical

Failure, friction, unsupported assumption, safety stop, or measurement issue
shall be preserved before product correction is designed. Later runs shall not
rewrite historical failed/incomplete evidence.

### ACC-REQ-011 — Support traceable retest
**Status:** ACTIVE · **Priority:** High

A justified correction shall be retested in a new run linked to the prior
run/finding where applicable. Product regression remains separate from
acceptance retest.

### ACC-REQ-012 — Fail closed on evidence integrity
**Status:** ACTIVE · **Priority:** Critical

Evidence verification shall reject material identity, hash, policy,
sensitivity, missing-file, or unmanifested-file inconsistencies.

### ACC-REQ-013 — Expose operator effort honestly
**Status:** ACTIVE · **Priority:** High

The workflow shall expose enough timing and subjective evidence to identify
excessive setup, intake, review, correction, waiting, or cognitive burden,
without converting it into unsupported productivity claims.

### ACC-REQ-014 — Do not turn product failure into target defect verdict
**Status:** ACTIVE · **Priority:** Critical

A failed TestCartographer workflow or generated test shall not automatically be
classified as an application defect. Triage preserves uncertainty among product
defect, testware defect, unsupported assumption, target condition, limitation,
and insufficient evidence.

### ACC-REQ-015 — Stop safely when authorization/evidence is insufficient
**Status:** ACTIVE · **Priority:** Critical

The workflow shall permit blocked/stopped outcomes when continuation requires
unauthorized authentication, destructive behavior, unsafe data handling, scope
escape, policy bypass, or unjustified evidence retention.

### ACC-REQ-016 — Keep nominal workflows inside supported product interfaces
**Status:** ACTIVE · **Priority:** High

For a supported nominal creation, maintenance, or expansion workflow, the
operator shall not be required to manually author or repair TestCartographer
internal contract JSON, edit TestCartographer source code, or perform
undocumented state surgery merely to reach the intended next product step.

Explicit review of generated automation/source and documented environment or
configuration steps remain allowed.

**Acceptance concern:** The intended testing professional should operate and
review the product workflow, not debug its internal persistence/contracts as a
normal prerequisite.

### ACC-REQ-017 — Protect the original automation repository from implicit writes
**Status:** ACTIVE · **Priority:** Critical

Within the currently accepted product boundary, TestCartographer shall not
silently apply generated source changes to the operator's original automation
repository.

Source application shall remain limited to an explicitly approved bounded
sandbox/copy unless a future reviewed real-repository handoff mechanism is
separately implemented and accepted.

**Acceptance concern:** A successful automation result must not depend on
unreviewed mutation of the user's source-of-truth repository.

### ACC-REQ-018 — Preserve material operator intent across transformations
**Status:** ACTIVE · **Priority:** Critical

The initial operator mission shall remain authoritative across intake,
structuring, planning, proposal, review, and execution preparation. Each
transformation shall retain material intent or explicitly clarify, defer, or
block on any material part that cannot be represented safely.

Human confirmation shall be based on a review that makes the unchanged initial
mission and the transformed context meaningfully comparable.

**Acceptance concern:** A syntactically complete context is not acceptable when
it silently omits, weakens, or replaces a material part of the operator's
original goal.

### ACC-REQ-019 — Persist truthful workflow lifecycle
**Status:** ACTIVE · **Priority:** Critical

Persisted workflow and operator-session state shall truthfully represent normal
completion, supported pause/quit, operator interruption, product failure, and
fail-closed blockage. A process that has terminated shall not remain recorded as
actively running.

The persisted state shall distinguish terminal outcomes from states that may be
resumed through a supported interface.

**Acceptance concern:** Preserved evidence must not require a reader to infer
whether a run is still active after its process has already ended.

### ACC-REQ-020 — Keep machine-assisted proposal boundaries consistent and recoverable
**Status:** ACTIVE · **Priority:** Critical

For each supported machine-assisted proposal shape, the provider-facing
contract, deterministic local validation, safe diagnostic classification, and
repairability decision shall represent the same material rules.

Bounded deterministic mismatches may enter only an explicit human-authorized
recovery path. Unknown, unsafe, syntactically invalid, duplicate-key,
locator-like, or otherwise unallowlisted failures shall remain fail-closed.
Raw provider prompts, responses, and rejected values shall not be persisted
merely to make recovery diagnosable.

No proposal may receive browser, target, framework, or source-change authority
before the complete deterministic contract passes and the operator explicitly
accepts the proposal.

**Acceptance concern:** A supported nominal flow must not expose a contract to
the provider that is weaker than the contract enforced after the provider has
responded, leaving a deterministic correction unreachable through the supported
operator interface.

## 4. Not baselined yet

Known future areas are not turned into detailed requirements without real
target evidence:

- credential lifecycle / `AuthProfile`,
- SSO/MFA,
- enterprise/Salesforce constraints,
- broad impact analysis,
- multi-process shared graph,
- comparative economics,
- team approval,
- visual/multimodal evidence.

## 5. Initial campaign view

```text
Sprint 17 Level 1
-> ACC-REQ-001 ... ACC-REQ-020 as applicable

Sprint 17 Level 2
-> same basis
-> increased emphasis on ACC-REQ-003/005/008/013/014/015
-> add/revise only when real evidence justifies it
```

One scenario may cover several requirements; a critical requirement may require
multiple focused scenarios.

## 6. Change history

| Version | Change | Evidence/reason |
|---|---|---|
| 0.1 | Initial baseline: 17 ACTIVE requirements | Sprint 16 closure and pre-execution critical review of the acceptance basis |
| 0.2 | Added ACC-REQ-018 through ACC-REQ-020; existing requirement wording and IDs unchanged | ACC-FIND-008 exposed material-intent loss, ACC-FIND-009 exposed an unrepresented lifecycle-state obligation, and ACC-FIND-010 through ACC-FIND-012 exposed a recurring proposal-contract/recovery boundary |

Version 0.2 becomes the active basis before Issue #12 product remediation and
ACC-EXT-003 run-06. It does not retroactively declare runs 01 through 05 failed
against requirements that were not active when those runs were executed.

The next version is determined by materiality, not sprint cadence.
