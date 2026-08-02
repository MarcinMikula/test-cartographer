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
are provisional or parked and must be reshaped using findings from earlier
work.

## System direction

`qa-automation-framework` and TestCartographer are separately executable modules
of one automation lifecycle.

```text
TestCartographer
→ context, discovery, LLM-assisted adaptation, maintenance, expansion

qa-automation-framework
→ accepted POM/fixtures/tests, configuration, execution, assertions, evidence
```

Normal test execution must remain independent of TestCartographer and a live
LLM. Creation, maintenance, and expansion may invoke TestCartographer and a
bounded LLM under human review.

See [`system-lifecycle.md`](system-lifecycle.md).

## Delivery stages

```text
product framing
→ context contract
→ human intake
→ guided browser observation
→ lifecycle alignment checkpoint
→ bounded LLM synthesis
→ framework workspace and handoff
→ first runnable test
→ creation-lifecycle evaluation
→ execution evidence
→ reactive maintenance
→ proactive frontend/context regression
→ expansion using the existing map
→ enterprise authentication and validation
→ comparative validation
→ v1.0 decision
```

## Sprint overview

| Sprint or checkpoint | Focus | Status |
|---|---|---|
| Sprint 0 | Product framing and project boundaries | Done |
| Sprint 1 | Minimum context contract and local evidence model | Done |
| Sprint 2 | Deterministic human-guided process intake | Done |
| Sprint 3 | Bounded guided browser observation | Done |
| Architecture checkpoint A | Align the two-module lifecycle, maintenance modes, authentication directions, and enterprise validation target | Done in documentation |
| Sprint 4 | Bounded LLM synthesis and POM proposal | Done |
| Sprint 5 | Project workspace, framework mapping, and first reviewable adaptation plan | Provisional |
| Sprint 6 | First runnable framework test and creation-lifecycle evaluation | Provisional |
| Sprint 7 | Framework execution-evidence contract | Parked |
| Sprint 8 | Reactive maintenance from execution evidence | Parked |
| Sprint 9 | Proactive post-deployment frontend/context regression | Parked |
| Sprint 10 | Expansion using the existing application map | Parked |
| Sprint 11 | External artefacts, authentication profiles, and enterprise safety | Parked |
| Sprint 12 | Validation ladder culminating in a safe Salesforce flow | Parked |
| Sprint 13 | Comparative usability, effort, quality, and v1.0 decision | Parked |

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
- 66 passing tests with Chromium, including regression coverage for editability
  semantics.

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

## Architecture checkpoint A — Lifecycle and enterprise alignment

**Status:** Done in documentation before Sprint 4

### Goal

Clarify the long-term system before introducing LLM synthesis and framework
adaptation.

### Decisions recorded

- TestCartographer and `qa-automation-framework` are separately executable
  modules of one automation lifecycle.
- The framework owns normal execution; TestCartographer owns context,
  LLM-assisted engineering, maintenance, and expansion.
- Creation is human-guided and LLM-assisted rather than fully autonomous.
- The framework remains independent of TestCartographer during normal runs.
- A future framework-side Execution Evidence Collector supplies bounded
  diagnostic input for maintenance.
- Maintenance has reactive and proactive modes.
- Proactive maintenance can re-observe approved areas after deployment windows,
  including mapped elements outside the current test pool.
- Expansion repeats creation but should reuse the existing application map,
  repository knowledge, and accepted conventions.
- Project configuration should store non-secret mappings and secret references,
  not credential values.
- Three authentication strategies are parked: shared storage state,
  declarative login recipe with in-memory secrets, and interactive login for
  SSO/MFA.
- Salesforce remains an intentional enterprise acceptance target.

### What the checkpoint proves

The product lifecycle, module boundaries, future maintenance modes, and
enterprise-validation direction are coherent enough to guide the next
contracts.

### What the checkpoint does not prove

No workspace profile, authentication contract, evidence collector, maintenance
workflow, expansion reuse, or Salesforce integration has been implemented.

## Sprint 4 — Bounded LLM synthesis and POM proposal

**Status:** Done

### Goal

Use only authorized, minimized, confirmed context and accepted observations to
produce a strict, reviewable POM proposal without mutating a repository or
claiming live-provider value.

### Delivered

- provider-neutral `BoundedSynthesisRequest` version `0.1`,
- field-level projection from a fully ready `ContextBundle`,
- default authorization of `PUBLIC` and `INTERNAL` values only,
- hard requirement for `CONFIRMED` or `OBSERVED` knowledge,
- explicit excluded-field catalogue and prohibited claims,
- deterministic prompt rendering from the exact request,
- provider-neutral `SynthesisAdapter` boundary,
- deterministic `ReplaySynthesisAdapter`,
- strict `PomProposal` version `0.1`,
- strict parser rejecting fences, invalid JSON, duplicate keys, schema drift,
  missing fields, and unexpected fields,
- exact raw-output preservation on success and failure,
- deterministic validation of page, component, method, action, locator,
  symbolic data, fixture, test, and outcome references,
- separate `PROTOCOL_ERROR`, `VALIDATION_REJECTED`, and `READY_FOR_REVIEW`
  states,
- explicit human `ACCEPTED` or `REJECTED` review,
- versioned `SynthesisRun` storing request, prompt hash, raw output, proposal,
  validation, and review,
- CLI commands for request construction, replay, status, and review,
- committed request, valid, malformed, overreaching, unknown-locator, and
  missing-step fixtures,
- deterministic synthesis replay verifier,
- three committed JSON Schemas,
- focused request, parser, validator, pipeline, review, IO, schema, and CLI
  tests.

### Exit criteria

- [x] A fully ready context can be projected into a bounded request.
- [x] Base URL, routes, raw source references, evidence hashes, timestamps,
      notes, browser state, and repository files remain outside the request.
- [x] Required non-authorized status or sensitivity blocks request creation.
- [x] The same request renders the same prompt.
- [x] Replay receives the exact request and prompt.
- [x] Raw output is preserved exactly, including outer whitespace.
- [x] Malformed protocol output remains separate from substantive rejection.
- [x] Invented locators, missing steps, secret claims, unknown outcomes, and
      prohibited claims are rejected deterministically.
- [x] A valid proposal remains pending until explicit human review.
- [x] Rejected or invalid proposals cannot be promoted through review.
- [x] No live provider is called.
- [x] No repository file is modified by synthesis.

### What Sprint 4 proves

One LLM-facing boundary can be explicit, minimized, versioned, replayable,
strictly parsed, deterministically validated, and separately reviewed before it
is allowed to influence framework adaptation.

### What Sprint 4 does not prove

- live-provider compliance or semantic quality,
- provider reliability, latency, cost, or privacy,
- prompt-injection resistance,
- correctness across varied applications,
- repository-specific POM placement,
- generated source code or execution,
- enterprise authentication or Salesforce readiness,
- usability or economic value.

### Gate to Sprint 5

Sprint 5 may consume only a human-accepted `SynthesisRun`. It must inspect a
real target copy of `qa-automation-framework` and produce a reviewable mapping
plan before any source file is written.

The accepted logical proposal must not be treated as proof that:

- named classes or fixtures already exist,
- proposed names fit repository conventions,
- file paths are known,
- framework configuration and secrets are resolved,
- the generated implementation would run.

## Sprint 5 — Project workspace and framework adaptation plan

**Status:** Provisional

### Goal

Map an accepted proposal into a concrete copy of `qa-automation-framework`
without writing files blindly.

### Candidate scope

- inspect the target framework repository,
- define the first non-secret project/workspace profile,
- map logical environment, role, data, page, component, fixture, and test
  concepts to existing framework structures,
- detect existing artefacts and duplication risks,
- prepare a reviewable file-level adaptation plan,
- keep secret values and authenticated state outside context and proposals,
- record source-to-target traceability,
- require human acceptance before file changes.

### Gate to Sprint 6

The plan must identify exactly which files and symbols will change and why,
without assuming that a generated class or fixture belongs in the target
architecture merely because it is syntactically valid.

## Sprint 6 — First runnable test and creation-lifecycle evaluation

**Status:** Provisional

### Goal

Complete the first creation lifecycle:

```text
Cartographer context and observations
→ bounded LLM proposal
→ accepted framework adaptation
→ one runnable test
→ framework execution
→ review and measurement
```

### Candidate scope

- create or update the agreed Page Object, component, fixture, data, and test
  artefacts,
- execute the test without a live LLM dependency,
- preserve traceability from context and proposal to code,
- record corrections and rejected proposals,
- measure setup time, active user time, time to first runnable test, LLM usage,
  and review effort,
- assess architecture quality and meaningful assertions.

Sprint 6 is the earliest point at which the project may claim a working
creation prototype.

## Sprint 7 — Framework execution-evidence contract

**Status:** Parked

### Direction

Coordinate a framework-side Execution Evidence Collector that can export
bounded, high-value diagnostic context without declaring every failure an
application bug.

Candidate evidence:

- test, step, Page Object, and method identifiers,
- action and locator,
- exception and failure classification,
- minimized element/page state,
- environment and application-version metadata,
- approved trace/screenshot/network references,
- links to Cartographer context and accepted artefacts.

This is a cross-repository workstream. The collector executes with the
framework; Cartographer consumes and analyses its output.

## Sprint 8 — Reactive maintenance

**Status:** Parked

### Direction

Use failed-execution evidence to:

- distinguish likely application, automation, data, environment, and context
  problems,
- re-observe the affected application area,
- mark context stale or conflicting,
- identify affected automation artefacts,
- prepare a reviewable patch,
- rerun the framework test after acceptance.

## Sprint 9 — Proactive frontend/context regression

**Status:** Parked

### Direction

Support bounded scheduled or post-deployment re-observation even when current
framework tests remain green.

The first version should use:

- an approved observation inventory,
- selected application areas,
- read-only or allowlisted actions,
- explicit authentication and sensitivity profiles,
- time/page/cost budgets,
- change and impact reports rather than silent repairs.

## Sprint 10 — Expansion using the existing map

**Status:** Parked

### Direction

Add a second process and measure whether existing context reduces:

- repeated human questions,
- repeated browser discovery,
- duplicate pages and components,
- LLM input size and cost,
- review and implementation time.

This is the first direct validation of the application's reusable map as a
product asset rather than a one-process document.

## Sprint 11 — External artefacts, authentication profiles, and enterprise safety

**Status:** Parked

### Direction

Potential scope:

- Jira and documentation ingestion,
- non-secret `EnvironmentProfile` and `AuthProfile`,
- secret-provider references,
- one or more of the parked authentication strategies,
- allowed-origin and action policy,
- retention, deletion, and session-expiry rules,
- SSO/MFA constraints,
- safe credentialed browser observation.

No strategy is the default until exercised against a controlled credentialed
application.

## Sprint 12 — Validation ladder culminating in Salesforce

**Status:** Parked

### Direction

Progress through increasingly realistic targets:

1. controlled local page,
2. simple public application,
3. modern dynamic public frontend,
4. controlled multi-page application,
5. credentialed enterprise-style reference system,
6. safe Salesforce environment.

A candidate Salesforce acceptance flow is:

```text
login
→ open Accounts
→ create an Account
→ save
→ verify the created record
```

Salesforce is a deliberate final-level target because simple sites cannot
validate enterprise authentication, component-driven UI, data restrictions,
complex process state, or maintenance economics.

## Sprint 13 — Comparative validation and v1.0 decision

**Status:** Parked

### Direction

Compare the same process and quality gates across:

```text
manual framework adaptation
vs.
DevTools + Playwright Codegen + general LLM
vs.
TestCartographer-assisted adaptation
```

Measure:

- functional and assertion correctness,
- POM and component quality,
- unsupported assumptions,
- human corrections,
- setup and active user time,
- time to first runnable test,
- maintenance time after a controlled change,
- effort to add a second process,
- LLM usage and cost,
- perceived difficulty, confidence, and willingness to reuse.

v1.0 should be declared only if the system demonstrates useful quality and
operational economics, not merely a completed feature list.

## Roadmap change policy

When evidence invalidates a planned sprint:

1. record the finding in `LEARNINGS.md`,
2. update the relevant gap or limitation,
3. redirect the roadmap rather than preserving the original plan for
   appearance,
4. state what the evidence proves and what it does not prove.

The roadmap is a working hypothesis, not a promise to implement every parked
direction.
