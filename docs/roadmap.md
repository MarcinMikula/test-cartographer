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
| Sprint 3 | Bounded guided browser observation | Done |
| Sprint 4 | Bounded LLM synthesis and POM proposal | Planned |
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

## Sprint 3 — Bounded guided browser observation

**Status:** Done

### Goal

Add one small, reviewable application-evidence boundary to an existing
human-reviewed process without whole-page capture, autonomous navigation, or an
LLM.

### Delivered

- Playwright as an optional browser dependency,
- controlled local catalog reference page,
- strict `BrowserObservation` schema version `0.1`,
- one user-authorized URL, element ID, and existing primary locator per capture,
- deterministic mapping for role, label, test ID, placeholder, text, CSS, and
  XPath locator strategies,
- exact-one-match and visibility requirements,
- minimized source URL without credentials, query, or fragment,
- selected-target snapshot with an explicit DOM attribute allowlist,
- explicit exclusion of input values, text content, HTML, screenshots, and raw
  page capture,
- pending, accepted, and rejected review states,
- rejection reason and review/capture effort metrics,
- narrow context update that appends application evidence and promotes only the
  accepted locator to `OBSERVED`,
- replay fixtures and generated observation JSON Schema,
- CLI capture, status, and review commands,
- controlled end-to-end verification script,
- 65 total tests when Chromium is available.

### Reference flow

```text
human-reviewed context with one inferred locator
→ serve controlled page on loopback
→ Playwright verifies button:Search selects exactly one visible button
→ persist a minimized pending observation
→ human accepts the mapping
→ append APPLICATION evidence
→ promote the primary locator from INFERRED to OBSERVED
→ full adaptation readiness changes from one blocker to ready
```

### Exit criteria

- [x] One controlled local page can be opened through Playwright.
- [x] The user authorizes the URL and target element ID.
- [x] One selected element is captured without whole-page dumping.
- [x] Observation evidence is linked to the correct context and locator.
- [x] One primary locator moves from `INFERRED` to `OBSERVED` only after
      acceptance.
- [x] Input values, text content, HTML, screenshots, and raw page data are not
      persisted.
- [x] Capture and context update are replayable in deterministic tests.
- [x] Rejection leaves context unchanged.
- [x] The reference context reaches readiness through evidence rather than a
      manual status rewrite.
- [x] No LLM is used.

### What Sprint 3 proves

One existing locator can be verified against a real controlled page, represented
by a minimized provider-neutral observation, reviewed by a human, and applied
without changing business context or unrelated application structure.

### What Sprint 3 does not prove

- safe capture from arbitrary public or enterprise applications,
- greenfield element, page, component, or process discovery,
- free-form browser element selection,
- locator generation or ranking,
- credentialed workflows, iframe or Shadow DOM support,
- accessibility-tree, network, screenshot, or trace capture,
- POM proposal quality,
- external LLM safety or value,
- framework adaptation,
- usability or time savings.

### Gate to Sprint 4

Any LLM request must consume an explicitly selected and minimized projection of
confirmed context and accepted browser evidence. Raw pages, arbitrary session
state, credentials, and unrelated context remain outside the request.

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
