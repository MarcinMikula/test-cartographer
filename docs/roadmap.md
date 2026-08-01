# Roadmap

## Roadmap rule

TestCartographer is developed through evidence-producing vertical slices.

A sprint is complete only when it produces one or more of:

- a working end-to-end capability,
- a controlled experiment,
- a validated contract,
- a documented decision based on evidence,
- an explicit scope boundary.

Creating folders, interfaces, or agent classes without exercising a useful
workflow is not sufficient.

The roadmap becomes less specific with distance. Sprints beyond the next one
are provisional and must be reshaped using findings from earlier work.

## Delivery stages

```text
product framing
→ context contract
→ human intake
→ guided browser observation
→ bounded LLM synthesis
→ framework handoff
→ end-to-end review
→ maintenance and integrations
→ comparative validation
→ v1.0 decision
```

## Sprint overview

| Sprint | Focus | Status |
|---|---|---|
| Sprint 0 | Product framing and project boundaries | Done |
| Sprint 1 | Minimum context contract and local evidence model | Done |
| Sprint 2 | Deterministic human-guided process intake | Done |
| Sprint 3 | Guided browser observation | Planned |
| Sprint 4 | Bounded LLM synthesis and POM proposal | Provisional |
| Sprint 5 | Framework handoff and first runnable test | Provisional |
| Sprint 6 | Review, traceability, and first end-to-end evaluation | Provisional |
| Sprint 7 | Change awareness and maintenance proposal | Parked |
| Sprint 8 | External artefact ingestion and security expansion | Parked |
| Sprint 9 | Comparative usability and quality validation | Parked |
| Sprint 10 | v1.0 hardening and release decision | Parked |

## Sprint 0 — Product framing

**Status:** Done

### Goal

Turn an initial UI-explorer idea into a bounded product direction before
creating source-code architecture.

### Delivered

- product name and repository framing,
- problem statement,
- relationship with `qa-automation-framework`,
- intended user,
- initial UI/POM boundary,
- multi-source context model,
- evidence and provenance requirement,
- security and privacy boundary,
- usability and operation-time validation requirement,
- first vertical-slice direction,
- explicit non-goals and parked ideas.

### What Sprint 0 proves

The project has a coherent problem statement, scope, development discipline,
and validation direction.

### What Sprint 0 does not prove

Technical feasibility, context quality, LLM value, browser feasibility,
security, usability, or product value.

## Sprint 1 — Minimum context contract

**Status:** Done

### Goal

Define and validate the smallest local, provider-neutral contract that can
represent one useful UI process without pretending unknown information is
known.

### Delivered

- Python `src` package layout,
- strict Pydantic `ContextBundle` version `0.1`,
- one process with application, pages, components, elements, locators, steps,
  outcomes, symbolic data, evidence, questions, and conflicts,
- knowledge authority and sensitivity metadata,
- graph-integrity validation,
- deterministic JSON load/save,
- adaptation-readiness report,
- generated and tested context JSON Schema,
- valid, incomplete, conflicting, and invalid fixtures,
- 23 deterministic tests at Sprint 1 completion.

### Exit criteria

- [x] One complete reference process can be represented.
- [x] Missing information remains explicit.
- [x] Inference is structurally distinguishable from confirmed fact.
- [x] Conflicting evidence can remain valid without silent resolution.
- [x] Invalid references and structures are rejected.
- [x] The representation is human-reviewable JSON.
- [x] No browser or provider dependency is required.
- [x] Readiness identifies what human and later browser stages must resolve.

### What Sprint 1 proves

One bounded UI process can be stored, validated, and assessed without
collapsing uncertainty into parser failure or invented certainty.

### What Sprint 1 does not prove

That a user can fill the model efficiently, that browser evidence can populate
it, or that it is sufficient for POM generation.

## Sprint 2 — Deterministic human-guided intake

**Status:** Done

### Goal

Collect and review the human-answerable process context from a structurally
valid incomplete bundle without requiring manual JSON editing or a free-form
LLM interviewer.

### Delivered

- stage-specific `assess_intake()` report,
- deterministic collection question queue,
- review queue for `PROVIDED` and `OBSERVED` business values,
- answer actions for provide, confirm, unknown, and skip,
- explicit collection-to-review transition,
- human evidence creation with source, timestamp, sensitivity, and digest,
- self-contained `IntakeSession` version `0.1`,
- active, paused, complete, and blocked session states,
- save after every accepted interaction,
- deferred-question retry,
- interaction count and active-answer-time metrics,
- standard-library CLI for start, run, status, and export,
- generated and tested intake-session JSON Schema,
- `.gitattributes` line-ending policy,
- 47 deterministic tests across context, intake, persistence, schema, and CLI.

### Reference flow

```text
load incomplete public-search context
→ ask business risk
→ ask observable outcome
→ ask stored matching-rule question
→ review risk
→ review outcome
→ human intake complete
```

Expected final state:

```text
human-intake blockers = 0
human-intake warnings = 0
full adaptation blockers = 1
```

The remaining blocker is an intentionally inferred primary locator.

### Exit criteria

- [x] Questions are derived from current context state.
- [x] Browser-only issues are excluded from human intake.
- [x] Normal answers become `PROVIDED` evidence.
- [x] Explicit review changes values to `CONFIRMED`.
- [x] Unknown and skipped answers do not create infinite loops.
- [x] A required deferred answer can produce a visible `BLOCKED` state.
- [x] Sessions can be paused, saved, resumed, and retried.
- [x] Interaction count and active answer time are measured.
- [x] Current context can be exported independently.
- [x] No live LLM or browser is required.
- [x] Full adaptation readiness remains separate from intake completion.

### What Sprint 2 proves

A strict context model can drive a deterministic, resumable, reviewable, and
measurable human-intake workflow.

### What Sprint 2 does not prove

- greenfield creation of the context shell,
- usability with a real tester and real application,
- automatic semantic interpretation of long answers,
- rich mapping of arbitrary open-question answers,
- browser capture,
- locator correctness,
- LLM synthesis,
- framework adaptation,
- time savings or easier operation than alternatives.

## Sprint 3 — Guided browser observation

**Status:** Planned

### Goal

Add bounded application evidence to one existing human-reviewed process during
a user-controlled Playwright session.

### Working vertical slice

```text
completed human intake
→ open one controlled application page
→ user performs or authorizes one process action at a time
→ capture a minimized observation
→ propose page/component/element/locator mapping
→ user accepts or rejects the observation
→ update evidence and context
→ reassess full adaptation readiness
```

### Candidate scope

- choose a controlled local reference application,
- add Playwright as an optional browser dependency,
- define a browser-observation contract separate from raw Playwright objects,
- capture current URL, bounded DOM/accessibility details, visible state, and
  locator candidates for selected targets,
- link observations to existing process steps and element IDs,
- classify captured data before persistence,
- keep credentials and test-data values outside observations,
- support user acceptance or rejection of proposed mappings,
- preserve raw capture only if a safe local evidence boundary is defined,
- update the intentionally inferred locator in the reference context through
  actual observation,
- add deterministic replay fixtures for browser-derived observations,
- record observation time and user actions.

### Required design questions

- What is the smallest safe observation needed for one target element?
- Should the first interaction use Playwright locator inspection, accessibility
  snapshots, selected DOM fragments, or a combination?
- How does a user indicate the element corresponding to a process step?
- What data must be removed before persistence?
- What makes a locator candidate `OBSERVED` rather than merely generated?
- How are page and component ownership proposals reviewed?
- How does browser evidence avoid overwriting confirmed business context?
- What can be tested deterministically without launching a real external site?

### Candidate exit criteria

- [ ] One controlled local page can be opened through Playwright.
- [ ] The user remains in control of navigation and actions.
- [ ] One selected element observation is captured without raw whole-page
      dumping.
- [ ] Observation evidence is linked to the correct context entity.
- [ ] At least one primary locator moves from `INFERRED` to `OBSERVED` through
      real browser evidence.
- [ ] Secrets and entered test-data values are not persisted.
- [ ] Capture and context update can be replayed deterministically in tests.
- [ ] The reference context reaches full readiness only through evidence, not a
      manual status rewrite.
- [ ] No LLM is needed to prove the browser boundary.

### Deliberate exclusions

- autonomous crawling,
- Jira or documentation ingestion,
- cloud LLM requests,
- POM generation,
- framework file changes,
- Salesforce,
- self-healing,
- unrestricted screenshots or full DOM archives.

### Gate to Sprint 4

Do not send application context to an LLM until browser acquisition produces a
small, reviewable, sensitivity-aware observation contract.

## Sprint 4 — Bounded LLM synthesis and POM proposal

**Status:** Provisional

Possible scope:

- provider-neutral bounded request,
- explicit authorization and minimization,
- structured POM proposal result,
- strict parser and raw-output preservation,
- malformed-output separation,
- replay adapter before live provider claims,
- human review of Page Object and component boundaries.

## Sprint 5 — Framework handoff and first runnable test

**Status:** Provisional

Possible scope:

- inspect a clean `qa-automation-framework` copy,
- prepare a reviewable file-level change set,
- create or update Page Objects, components, fixtures, data, and one test,
- execute the test without a live LLM dependency,
- retain source-to-generated traceability.

## Sprint 6 — First end-to-end evaluation

**Status:** Provisional

Measure:

- correctness,
- architecture quality,
- unsupported assumptions,
- human corrections,
- setup time,
- active user time,
- time to first runnable test,
- LLM usage and cost,
- user confidence and perceived difficulty.

Sprint 6 is the earliest point at which the project may claim a working
end-to-end prototype.

## Sprints 7–10 — Parked directions

Potential later work includes:

- change awareness and maintenance proposals,
- Jira and documentation ingestion,
- comparative manual/Codegen/general-LLM/TestCartographer evaluation,
- Salesforce validation,
- security and retention hardening,
- release and v1.0 decision.

These are not commitments until earlier evidence justifies them.

## Roadmap change policy

When evidence invalidates a planned sprint:

1. record the finding in `LEARNINGS.md`,
2. update the relevant gap or limitation,
3. redirect the roadmap rather than preserving the original plan for
   appearance,
4. state what the evidence proves and what it does not prove.

The roadmap is a working hypothesis, not a promise to implement every parked
idea.
