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
→ guided observation
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
| Sprint 2 | Human-guided process intake | Planned |
| Sprint 3 | Guided browser observation | Provisional |
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
- core responsibilities,
- initial UI/POM boundary,
- knowledge-source model,
- evidence and provenance requirement,
- security and privacy boundary,
- usability and operation-time validation requirement,
- first vertical-slice direction,
- explicit non-goals and parked ideas,
- chronological project journal.

### What Sprint 0 proves

The project has a coherent problem statement, scope, development discipline,
and validation direction.

### What Sprint 0 does not prove

- technical feasibility,
- context-schema quality,
- LLM accuracy,
- browser-capture feasibility,
- data safety,
- framework-generation quality,
- time savings,
- usability,
- maintainability,
- product value.

---

## Sprint 1 — Minimum context contract

**Status:** Done

### Goal

Define and validate the smallest local, provider-neutral context contract that
can describe one useful UI automation flow without pretending unknown
information is known.

### Delivered

- Python package with `src` layout,
- strict Pydantic context contract version `0.1`,
- explicit knowledge statuses including `UNKNOWN`,
- basic sensitivity classification,
- evidence and provenance references,
- one-process model with purpose, risk, role, preconditions, steps, and
  expected outcomes,
- pages, reusable components, elements, and locator candidates,
- symbolic test-data requirements without real values,
- open-question and conflict representation,
- deterministic cross-reference and ownership validation,
- readiness report separate from structural validation,
- deterministic JSON load/save,
- committed generated JSON Schema,
- complete, incomplete, conflicting, and invalid fixtures,
- 23 deterministic tests,
- context-contract, architecture-decision, testing-strategy, gap, limitation,
  and learning documentation.

### Exit criteria

- [x] One complete reference process can be represented.
- [x] Missing information remains explicit.
- [x] Inference is structurally distinguishable from confirmed fact.
- [x] Conflicting evidence can be stored without silent resolution.
- [x] Invalid context is rejected deterministically.
- [x] The representation is human-reviewable JSON.
- [x] No provider-specific or browser-specific dependency is required.
- [x] Tests exercise complete, incomplete, conflicting, and invalid fixtures.
- [x] The contract exposes concrete gaps that Sprint 2 can ask about.
- [x] The JSON Schema is generated and protected against drift.

### What Sprint 1 proves

- one bounded UI process can be expressed as a strict typed graph,
- explicit unknown and conflicting context does not need to be discarded,
- structural validity and automation readiness can be assessed separately,
- evidence and basic sensitivity metadata can travel with individual claims,
- deterministic fixtures can test the context boundary without a browser or
  LLM.

### What Sprint 1 does not prove

- that the contract is sufficient for a real application,
- that a tester can fill it efficiently,
- that readiness rules match real adaptation needs,
- that browser observations can populate it safely,
- that an LLM can use it to propose a good POM,
- that framework adaptation will work,
- that the tool saves time or is easy to operate.

### Main finding

A useful intake workflow cannot be designed as a generic questionnaire first.
It should consume a valid-but-incomplete context and ask questions that resolve
specific readiness blockers or required unknown fields.

---

## Sprint 2 — Human-guided process intake

**Status:** Planned

### Goal

Allow a tester to create, review, save, and resume one valid process context
without editing JSON or understanding internal model classes.

### Proposed vertical slice

```text
start from a minimal context shell
→ ask one concrete question at a time
→ map each answer to a typed field
→ allow explicit "unknown"
→ surface conflicts instead of overwriting
→ show current blockers and warnings
→ review proposed confirmations
→ save and resume the local bundle
```

### Scope boundary

Sprint 2 should use deterministic, rule-based question selection first.

A free-form LLM interviewer is not required to prove the intake workflow.
The product should learn which questions and transitions are necessary before
adding probabilistic conversation.

### Candidate implementation

- a small local command-line workflow,
- intake-session model separate from the durable context bundle,
- question catalogue keyed to missing context and readiness codes,
- answer types such as text, confirmation, selection, and explicit unknown,
- conflict creation when a new answer disagrees with retained evidence,
- review step before changing knowledge to `CONFIRMED`,
- local save/resume,
- interaction metrics.

### Required decisions

- which minimal shell fields exist before intake,
- question ordering,
- how provided answers become evidence,
- how corrections and replacements work,
- when a new answer creates a conflict,
- how confirmation is represented,
- which readiness blockers belong to human intake and which require browser
  evidence,
- what timing data is collected without invading privacy.

### Candidate exit criteria

- [ ] A user can start one reference process without hand-editing JSON.
- [ ] The intake asks only questions relevant to current missing context.
- [ ] The user can answer `unknown` without inventing data.
- [ ] A contradictory answer is preserved as a conflict or explicitly replaces
      prior evidence through a reviewed action.
- [ ] The resulting bundle passes structural validation.
- [ ] Readiness changes are visible after each answer.
- [ ] The session can be saved and resumed.
- [ ] A final review is required before business-critical values become
      confirmed.
- [ ] Question count and active elapsed time are recorded.
- [ ] Deterministic replay tests cover complete, incomplete, correction, and
      conflict paths.

### Deliberate exclusions

- browser automation,
- live LLM calls,
- Jira,
- framework file generation,
- autonomous decision-making,
- selector healing.

### Gate to Sprint 3

The intake must create useful business and testing context without requiring the
user to understand the JSON schema. Remaining blockers should identify exactly
what application evidence the guided browser slice must collect.

---

## Sprint 3 — Guided browser observation

**Status:** Provisional

### Goal

Add application evidence to one existing process model during a
human-controlled Playwright session.

### Candidate capability

- user opens or identifies a page,
- user performs or directs the next action,
- the tool captures a bounded observation,
- relevant pages, components, elements, states, and locator candidates are
  proposed,
- the user confirms or rejects mappings,
- observations are linked to process steps and evidence.

### Deliberate boundary

This is not autonomous crawling. The user remains responsible for navigation,
credentials, environment safety, and process intent.

### Gate to Sprint 4

Captured information must be smaller and more useful than a raw DOM dump and
must preserve source, sensitivity, and process linkage.

---

## Sprint 4 — Bounded LLM synthesis and POM proposal

**Status:** Provisional

### Goal

Use a capable LLM to transform a sanitized, authorized subset of the context
model into a structured POM proposal.

### Candidate capability

- build a provider-neutral bounded request,
- exclude secrets and unauthorized raw capture,
- ask for structured Page Object, component, method, locator, and open-question
  proposals,
- parse the response strictly,
- preserve raw output,
- reject malformed responses,
- keep model proposals separate from confirmed context,
- support replay without a live provider.

### Gate to Sprint 5

The protocol must be deterministic around request construction and parsing. A
fluent LLM response is not enough.

---

## Sprint 5 — Framework handoff and first runnable test

**Status:** Provisional

### Goal

Map one accepted proposal into a clean copy of
`qa-automation-framework` and produce one runnable test.

### Candidate capability

- inspect the target repository structure,
- avoid duplicating existing Page Objects or components,
- prepare a reviewable file-level change set,
- create or update Page Objects, test data, fixtures, and one test,
- keep assertions in the appropriate layer,
- execute the test,
- retain generated-to-source traceability.

### Gate to Sprint 6

The generated project must run as ordinary Python, Playwright, and pytest code
without a live LLM dependency.

---

## Sprint 6 — Review, traceability, and first end-to-end evaluation

**Status:** Provisional

### Goal

Exercise the complete first workflow and measure whether it produces useful,
reviewable automation.

### Candidate evaluation

- correctness of the flow and expected result,
- POM and component boundaries,
- locator quality,
- readability,
- unsupported assumptions,
- human corrections,
- setup time,
- active user time,
- time to first runnable test,
- LLM requests, latency, and cost,
- user confidence and perceived difficulty.

### First milestone

Sprint 6 is the earliest point at which TestCartographer may claim a working
end-to-end prototype.

It still cannot claim superiority over alternative workflows without a
controlled comparison.

---

## Sprint 7 — Change awareness and maintenance proposal

**Status:** Parked

Possible scope:

- repeat selected observation,
- compare current and stored context,
- mark stale or conflicting knowledge,
- identify affected automation artefacts,
- propose bounded changes,
- measure maintenance time.

No autonomous healing commitment is made.

---

## Sprint 8 — External artefact ingestion and security expansion

**Status:** Parked

Possible sources:

- Jira,
- test-management tools,
- requirements,
- OpenAPI,
- documentation repositories.

This sprint requires explicit access, minimization, provenance, retention, and
redaction policies. An integration should not be built merely because an API
exists.

---

## Sprint 9 — Comparative validation

**Status:** Parked

Compare:

```text
manual framework adaptation
vs.
DevTools + Playwright Codegen + general LLM
vs.
TestCartographer
```

Use the same:

- target application,
- process,
- framework starting point,
- acceptance criteria,
- quality gates.

Potential validation ladder:

1. simple public page,
2. modern dynamic frontend,
3. controlled reference application,
4. safe Salesforce environment.

Measure both output quality and operator effort.

---

## Sprint 10 — v1.0 hardening and release decision

**Status:** Parked

Possible scope:

- stable public contracts,
- security review,
- retention and deletion rules,
- CI and packaging,
- installation and onboarding,
- failure reporting,
- documentation,
- benchmark report,
- explicit supported and unsupported boundaries.

v1.0 should be declared only if the tool demonstrates value relative to its
operational cost. A completed feature list alone is not sufficient.

## Roadmap change policy

When evidence invalidates a planned sprint:

1. record the finding in `LEARNINGS.md`,
2. update the current limitation or gap,
3. redirect the roadmap rather than preserving the original plan for
   appearance,
4. state what the evidence proves and what it does not prove.

The roadmap is a working hypothesis, not a promise to implement every parked
idea.
