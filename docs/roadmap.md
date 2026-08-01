# Roadmap

## Roadmap rule

TestCartographer is intentionally developed through evidence-producing vertical
slices.

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
Product framing
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
| Sprint 1 | Minimum context contract and local evidence model | Planned |
| Sprint 2 | Human-guided process intake | Provisional |
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

- product name and public repository framing,
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

### Exit criteria

- [x] The project is described as context acquisition and framework adaptation,
      not merely locator or test generation.
- [x] TestCartographer and `qa-automation-framework` have separate
      responsibilities.
- [x] Human input, project artefacts, running application, and repository
      evidence are recognized as complementary sources.
- [x] Observed, provided, inferred, and confirmed knowledge are conceptually
      distinct.
- [x] External LLM use is bounded by a local security and minimization
      requirement.
- [x] Ease of use and operation time are part of product success.
- [x] The first slice is limited to one human-guided process.
- [x] Jira, autonomous crawling, Salesforce, SOM, and healing are not Sprint 1
      requirements.
- [x] No premature code architecture has been committed.

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

**Status:** Planned

### Goal

Define and validate the smallest local, provider-neutral context contract that
can describe one useful UI automation flow without pretending unknown
information is known.

### Candidate scope

- select one small reference flow,
- define the minimum entities and fields required to describe it,
- represent process purpose, risk, preconditions, steps, expected result, page,
  component, element, locator candidate, and automation mapping,
- define evidence and provenance,
- define knowledge status and explicit unknowns,
- define basic sensitivity classification,
- serialize the model locally in a human-reviewable form,
- validate the contract against hand-created good, incomplete, conflicting, and
  invalid examples,
- add deterministic tests before any live LLM integration.

### Required decisions

- reference flow,
- schema technology,
- file versus database boundary,
- stable identifiers,
- required versus optional fields,
- status transitions,
- conflict representation,
- minimum provenance,
- minimum sensitivity metadata,
- contract versioning.

### Candidate exit criteria

- [ ] One complete reference process can be represented.
- [ ] Missing information remains explicit.
- [ ] LLM inference is structurally distinguishable from confirmed fact.
- [ ] Conflicting evidence can be stored without silent resolution.
- [ ] Invalid context is rejected deterministically.
- [ ] The representation is readable enough for human review.
- [ ] No provider-specific or browser-specific dependency is required.
- [ ] Tests demonstrate valid, incomplete, conflicting, and invalid fixtures.
- [ ] The contract identifies exactly what Sprint 2 must ask the user.

### Deliberate exclusions

- live LLM calls,
- browser automation,
- Jira,
- framework file generation,
- autonomous decisions,
- selector healing.

### Gate to Sprint 2

Do not build the interview workflow until the context contract demonstrates
which information is actually needed and how unknown answers are represented.

---

## Sprint 2 — Human-guided process intake

**Status:** Provisional

### Goal

Collect the minimum process, testing, and business context from a human and
produce a valid Sprint 1 context model.

### Candidate capability

```text
select process
→ answer adaptive questions
→ preserve unknowns
→ review collected context
→ save validated local model
```

### Questions to answer

- Can the tool avoid an exhaustive questionnaire?
- Which questions can be skipped based on previous answers?
- Can users distinguish facts from assumptions?
- How much active time does intake require?
- Which required fields still cannot be obtained from a human-friendly flow?

### Gate to Sprint 3

The intake must create a useful model without forcing the user to understand
the internal schema.

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

The captured information must be smaller and more useful than a raw DOM dump
and must preserve source, sensitivity, and process linkage.

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

The protocol must be deterministic around request construction and parsing.
A fluent LLM response is not enough.

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
