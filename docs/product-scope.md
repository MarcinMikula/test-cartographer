# Product scope

## Purpose

TestCartographer is an experimental LLM-assisted tool for collecting,
organizing, verifying, and maintaining the application context required to
adapt a reusable automation framework to a real project.

It is designed as a companion to
[`qa-automation-framework`](https://github.com/MarcinMikula/qa-automation-framework).

The product should help answer:

> What does the framework need to know about this application, process, risk,
> and environment before maintainable automation can be created?

## Current implemented boundary

Sprint 1 implements only the local context boundary for one UI process.

The current package can:

- validate one versioned `ContextBundle`,
- preserve evidence, knowledge status, and basic sensitivity metadata,
- represent explicit unknowns and unresolved conflicts,
- validate page, component, element, locator, test-data, and evidence references,
- distinguish structural validity from adaptation readiness,
- persist deterministic human-readable JSON,
- export JSON Schema version `0.1`.

The current package cannot:

- collect answers through a user workflow,
- observe a browser,
- call an LLM,
- propose a POM,
- modify `qa-automation-framework`,
- execute a generated test.

Current implementation details are documented in
[`context-contract.md`](context-contract.md).

## Problem statement

A reusable framework can define:

- project structure,
- POM and SOM conventions,
- fixtures and configuration patterns,
- test organization,
- automation principles,
- quality gates.

It cannot supply project-specific truth.

That truth is distributed across:

- testers and domain experts,
- issue trackers and test-management tools,
- requirements and documentation,
- the running application,
- API specifications,
- existing automation code,
- execution traces and reports.

The difficult work is not only discovering how to click an element. It is
collecting enough reliable context to decide:

- why an automation flow exists,
- which risk it protects,
- what the expected result is,
- which data and permissions are required,
- what should be represented by pages, components, workflows, fixtures, and
  tests,
- what remains unknown,
- which claims come from evidence and which are model inferences,
- how the automation should change when the application changes.

## Product vision

TestCartographer should create and maintain a verified map between:

```text
business and testing knowledge
+ application structure and behaviour
+ project artefacts
+ automation architecture
```

and use that map to support reviewed adaptation of
`qa-automation-framework`.

The tool is not defined by the amount of code it generates. Its value depends
on whether it reduces repeated discovery and improves the correctness,
traceability, maintainability, and efficiency of framework adaptation.

## Intended user

The initial target user is a software tester or test automation engineer who:

- understands the selected process or can consult a domain expert,
- can guide the tool through the application,
- can review Python, Playwright, and pytest output,
- can confirm business rules and expected results,
- owns the final automation decision.

The initial product assumes a technically capable user. A no-code interface for
non-technical users is outside the first scope.

## Stakeholders

Potential stakeholders include:

- test automation engineers,
- manual testers and test analysts,
- domain experts,
- application developers,
- product owners,
- security and data-protection reviewers,
- maintainers of `qa-automation-framework`.

Not every stakeholder must directly operate the tool. Some provide or validate
specific parts of the context.

## Core responsibilities

### 1. Context acquisition

The product should eventually collect information from four complementary
paths.

#### Human input

For information that cannot be safely or reliably inferred:

- process purpose,
- business rules,
- risk and priority,
- expected outcomes,
- valid and invalid data,
- environment restrictions,
- acceptance or rejection of inferred information.

The interaction should be adaptive. The tool should ask for missing information
when needed instead of presenting one fixed exhaustive questionnaire.

#### Project artefacts

Possible sources include:

- Jira issues,
- test cases,
- acceptance criteria,
- requirements,
- project documentation,
- defect reports,
- diagrams,
- OpenAPI specifications,
- environment notes.

Imported content is evidence, not automatic truth. It may be incomplete,
conflicting, or stale.

#### Running application

During a human-guided browser session, the tool may observe:

- pages and reusable components,
- elements and locator candidates,
- DOM and accessibility structure,
- states and transitions,
- validation behaviour,
- overlays and loaders,
- iframes and Shadow DOM,
- relevant network activity,
- visible outcomes.

The first scope is guided exploration, not autonomous crawling.

#### Repository and execution evidence

The tool should eventually inspect:

- existing Page Objects and components,
- fixtures and workflows,
- tests and test data,
- configuration,
- execution results,
- Playwright traces,
- screenshots,
- prior accepted decisions.

This prevents duplication and supports maintenance over multiple iterations.

### 2. Context modelling

The product should organize information into a structured application model.

Expected concepts include:

- application,
- environment,
- role,
- authentication,
- business area,
- process,
- precondition,
- test condition,
- step,
- page,
- component,
- element,
- application state,
- locator candidate,
- business rule,
- expected outcome,
- risk,
- test data,
- automation artefact,
- evidence,
- unresolved question,
- conflict.

The final schema is not decided in Sprint 0.

### 3. Knowledge status and provenance

The system must distinguish at least conceptually between:

```text
OBSERVED
PROVIDED
INFERRED
CONFIRMED
STALE
CONFLICTING
```

Important information may need:

- source type and source identifier,
- acquisition timestamp,
- reviewer,
- confidence,
- sensitivity classification,
- related process or application area,
- related automation artefact,
- superseded or conflicting evidence.

An LLM inference must never be silently presented as a confirmed business fact.

### 4. Framework adaptation

Using sufficiently confirmed context, the product may propose or prepare:

- Page Objects,
- reusable component objects,
- workflow helpers,
- fixtures,
- test-data structures,
- selectors,
- test cases,
- documentation,
- configuration changes.

The tool should understand the target architecture:

```text
browser mechanics
→ BasePage / BaseComponent

application-facing actions and observable state
→ concrete Page Objects / Components

repeated orchestration or test support
→ workflows / fixtures

verification intent and business assertions
→ tests
```

Generated output is a draft until reviewed and executed.

### 5. Review and traceability

A proposed change should make it possible to answer:

- What source evidence supported this proposal?
- Which details were observed, supplied, or inferred?
- Which assumptions remain unconfirmed?
- Which files will change?
- Which process and risk does the automation represent?
- What result must be verified?
- What requires human acceptance?

### 6. Maintenance support

Later versions may:

- compare current observations with stored context,
- detect potential locator or structure changes,
- identify affected Page Objects and tests,
- detect changed required fields or process steps,
- mark context as stale or conflicting,
- propose bounded updates,
- retain a review history.

Autonomous repair is not part of the first vertical slice.

## Relationship with testing methodology

The product should use testing principles to support:

- identification of the test basis,
- risk selection,
- test conditions,
- expected results,
- positive and negative coverage,
- appropriate test level,
- test-data needs,
- traceability.

ISTQB terminology may help establish a common vocabulary. The tool should not
treat the syllabus as an algorithm for generating tests.

Knowing how to interact with a page is different from knowing what should be
tested and why.

## Relationship with qa-automation-framework

### qa-automation-framework provides

- reusable POM/SOM structure,
- automation conventions,
- fixtures and configuration patterns,
- testing and adaptation guidance,
- maintainability principles.

### TestCartographer provides

- project-specific discovery,
- structured context,
- missing-context questions,
- evidence and provenance,
- architecture-aware adaptation proposals,
- later change-impact support.

The framework remains usable without TestCartographer after adaptation.

## Initial technical boundary

The first implementation direction is:

- Python,
- Playwright,
- pytest,
- Page Object Model,
- a local context representation,
- a capable external LLM behind a bounded input contract,
- local data minimization and preprocessing,
- human review before accepting changes.

The following remain open decisions:

- package architecture,
- persistence technology,
- LLM provider,
- prompt and response protocol,
- browser-observation mechanism,
- repository-writing mechanism,
- review interface.

## First vertical-slice boundary

The first end-to-end slice should cover one small process.

Expected flow:

```text
1. Select one process and one target application.
2. Collect minimum business and testing context from a human.
3. Guide the browser through the selected flow.
4. Record a bounded set of observations.
5. Build a small structured context model.
6. expose missing, conflicting, and inferred information.
7. Propose Page Object and test artefacts.
8. Map the proposal into a copy of qa-automation-framework.
9. Execute one test.
10. Review assumptions, evidence, code, and outcome.
```

Not required for the first slice:

- Jira integration,
- autonomous application exploration,
- complete application inventory,
- API/SOM adaptation,
- selector healing,
- Salesforce,
- multi-user workflow,
- production deployment,
- automatic merge or silent code modification.

## Security and privacy boundary

Browser-visible and Jira-accessible information may still be confidential.

Potentially sensitive data includes:

- credentials and tokens,
- session identifiers,
- customer and employee data,
- internal URLs,
- business identifiers,
- confidential requirements,
- hidden DOM values,
- network payloads,
- application architecture.

The intended processing sequence is:

```text
local acquisition
→ filtering and redaction
→ sensitivity classification
→ minimum necessary context
→ bounded external LLM request
```

Requirements:

- credentials must not be included in prompts or committed files,
- raw application capture must not automatically be sent to a provider,
- data minimization must happen before external inference,
- source and sensitivity metadata must be retained where relevant,
- enterprise-system validation requires an explicit safe environment and data
  policy.

No implementation currently enforces these requirements.

## Product success criteria

A future usable version should demonstrate:

### Context quality

- required information is present or explicitly marked unknown,
- source and status are traceable,
- unsupported assumptions are visible,
- conflicting information is not silently resolved.

### Automation quality

- one runnable test is produced,
- Page Object and component boundaries are maintainable,
- selectors are centralized appropriately,
- test intent remains readable,
- assertions protect the intended result,
- generated code can be maintained without the tool.

### Workflow quality

- the process is understandable to the intended user,
- questions are relevant and not excessive,
- manual corrections are measurable,
- the result can be reviewed through ordinary repository changes.

### Efficiency

- setup time is measured,
- active user time is measured,
- time to first runnable test is measured,
- LLM usage and cost are measured,
- update time after an application change is measured.

### Comparative value

TestCartographer should be compared with:

1. manual framework adaptation,
2. human-led adaptation using DevTools, Playwright Codegen, and a general LLM,
3. the dedicated TestCartographer workflow.

The tool is successful only if its quality and efficiency justify its added
process and infrastructure.

## Product-level Definition of Done

The long-term product direction is achieved when, for a selected process,
TestCartographer can:

1. collect context from more than one source,
2. identify missing and conflicting information,
3. guide application observation,
4. build a structured and versioned context model,
5. preserve evidence, provenance, and inference status,
6. propose a maintainable POM structure,
7. adapt `qa-automation-framework`,
8. produce and execute a runnable test,
9. explain assumptions and sources,
10. support human correction and acceptance,
11. analyse a later application change,
12. demonstrate usable operation time and comparative value.

This is a product-level direction, not the current implemented capability.

## Out of scope until separately justified

- replacing test analysis or domain expertise,
- a universal no-code automation platform,
- a closed proprietary test representation,
- autonomous production-system exploration,
- fully autonomous business correctness decisions,
- broad multi-language and multi-framework support,
- automatic Jira ingestion before a data-safety policy exists,
- merging TestCartographer and PhoenixQA,
- claiming time savings before controlled comparison.
