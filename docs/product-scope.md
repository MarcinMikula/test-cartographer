# Product scope

## Purpose

TestCartographer is an experimental LLM-assisted tool for collecting,
organizing, verifying, and maintaining the application context required to
adapt a reusable automation framework to a real project.

Together with
[`qa-automation-framework`](https://github.com/MarcinMikula/qa-automation-framework),
TestCartographer is intended to form one automation lifecycle with two
separately executable modules. The framework owns normal execution.
TestCartographer owns context acquisition, LLM-assisted adaptation, maintenance,
and expansion.

The product should help answer:

> What does the framework need to know about this application, process, risk,
> and environment before maintainable automation can be created?

## Current implemented boundary

Sprint 7 implements:

- a strict local context contract for one UI process,
- deterministic adaptation-readiness assessment,
- a stage-specific human-intake assessment,
- rule-based collection and review questions,
- evidence-linked provide and confirm actions,
- explicit unknown and skip behaviour,
- self-contained save/resume sessions,
- active, paused, complete, and blocked states,
- CLI start, run, status, and export commands,
- basic interaction and active-time metrics,
- committed and tested JSON Schemas for context and intake session,
- a separate bounded browser-observation contract and schema,
- Playwright verification of one existing locator against one authorized page,
- minimized selected-target capture and explicit human accept/reject review,
- evidence-backed locator promotion from `INFERRED` to `OBSERVED`,
- a bounded provider-neutral synthesis request built from ready context,
- deterministic prompt rendering and replay adapter,
- strict JSON proposal parsing and exact raw-output preservation,
- a logical POM proposal linked to authorized source IDs,
- deterministic proposal validation,
- separate protocol, validation, and human-review states,
- CLI request, replay, status, and review commands,
- a non-secret workspace inspection profile,
- bounded read-only inspection of one local framework root,
- relative-path, hash, size, and Python-symbol snapshots,
- deterministic root fingerprints,
- exact file/symbol adaptation operations,
- separate plan status and human review,
- CLI inspect, plan, status, and review commands,
- exact deterministic source patches with separate source review,
- snapshot-bounded sandbox application and first runnable framework test,
- creation-lifecycle evaluation,
- a standalone framework-side pytest execution-evidence collector,
- provider-neutral profile, record, and bundle contracts,
- explicit pass, test-failure, and infrastructure-error outcomes,
- bounded structural step and minimized URL evidence,
- deterministic readiness assessment for reactive maintenance,
- CLI evidence status and assessment commands.

The current package still cannot:

- generalize discovery and generation beyond controlled reference applications,
- safely modify the user's original `qa-automation-framework` repository,
- diagnose arbitrary root causes from execution evidence,
- perform reactive maintenance beyond one controlled locator drift,
- perform proactive maintenance,
- reuse a persistent bootstrap/project profile across separate runs with full
  invalidation semantics,
- prove that the mapping, generation, and maintenance conventions fit every
  project.

Implementation details are documented in:

- [`context-contract.md`](context-contract.md),
- [`intake-workflow.md`](intake-workflow.md),
- [`browser-observation.md`](browser-observation.md),
- [`synthesis-protocol.md`](synthesis-protocol.md),
- [`framework-adaptation-planning.md`](framework-adaptation-planning.md),
- [`source-delivery.md`](source-delivery.md),
- [`execution-evidence.md`](execution-evidence.md).

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
- which claims come from evidence and which are inferences,
- how the automation should change when the application changes.

## Product vision

TestCartographer should create and maintain a verified map between:

```text
business and testing knowledge
+ application structure and behaviour
+ project artefacts
+ repository and execution evidence
+ automation architecture
```

and use that map throughout the lifecycle of `qa-automation-framework`:

```text
create automation
→ execute independently in the framework
→ collect bounded execution evidence
→ maintain reactively or proactively
→ expand using the existing application map
```

The tool is not defined by the amount of code it generates. Its value depends
on whether it reduces repeated discovery and improves correctness,
traceability, maintainability, expansion efficiency, and the economics of
framework adaptation.

The human-guided creation model combines Cartographer evidence, bounded LLM
assistance, framework conventions, and human review. The project uses
**AItomatyzacja testów** as an informal shorthand for that AI-supported
automation-engineering workflow, not for fully autonomous test creation.

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

The current implementation does not yet model stakeholder identity or approval
authority.

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

Sprint 2 implements a deterministic first form of this path.

The tool asks from explicit gaps rather than presenting one fixed exhaustive
questionnaire. It separates providing a value from confirming it.

It does not yet interpret one free-form answer into multiple structured facts.

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

No project-artefact integration is currently implemented.

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

Sprint 3 implements one bounded guided observation of an existing target;
autonomous crawling remains outside the current scope.

#### Repository and execution evidence

The lifecycle may inspect or consume:

- existing Page Objects and components,
- fixtures and workflows,
- tests and test data,
- configuration,
- execution results,
- Playwright traces,
- screenshots,
- prior accepted decisions.

This prevents duplication and supports maintenance over multiple iterations.

Sprint 5 implements bounded read-only repository inspection. Sprint 7 implements
a provider-neutral execution-evidence contract and reference pytest collector.
Production framework installation, CI transport, and raw artefact policy remain
open.

### 2. Context modelling

The current contract models:

- application and environment,
- one process,
- purpose, risk, role, and preconditions,
- ordered UI steps,
- pages and components,
- elements and locator candidates,
- expected outcomes,
- symbolic test-data requirements,
- evidence and provenance,
- open questions,
- conflicts.

Potential future concepts include:

- authentication policy,
- business area,
- structured business rule,
- test condition,
- application state graph,
- assertion operator,
- automation artefact,
- resolved-question object,
- cross-process relationship.

Those concepts should be added only when a vertical slice requires them.

### 3. Knowledge status and provenance

Important knowledge must distinguish:

```text
OBSERVED
PROVIDED
INFERRED
CONFIRMED
UNKNOWN
STALE
CONFLICTING
```

Current knowledge metadata includes:

- value,
- status,
- evidence references,
- optional confidence,
- sensitivity,
- notes.

Current evidence metadata includes:

- source type and reference,
- summary,
- acquisition timestamp,
- sensitivity,
- optional digest.

An inference must never be silently presented as a confirmed business fact.

A human answer becomes `PROVIDED`; an explicit review action is required for
`CONFIRMED`.

### 4. Stage-specific readiness

The product should not use one undifferentiated notion of completeness.

Current stages are:

```text
structural validity
→ human-intake completion
→ full adaptation readiness
```

Structural validation rejects malformed data.

Human-intake assessment includes only questions a person can answer in the
current workflow.

Full adaptation readiness also requires application evidence such as an
observed primary locator.

Future stages may add:

- browser-observation readiness,
- LLM-request readiness,
- POM-proposal readiness,
- framework-handoff readiness.

### 5. Framework adaptation

Using sufficiently confirmed context, the product may later propose or prepare:

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

Generated output remains a draft until reviewed and executed.

Repository planning and controlled-copy source delivery are implemented for one POM slice. Direct production-repository adaptation is not implemented.

### 6. Review and traceability

A future proposed change should make it possible to answer:

- What source evidence supported this proposal?
- Which details were observed, supplied, inferred, or confirmed?
- Which assumptions remain unresolved?
- Which files will change?
- Which process and risk does the automation represent?
- What result must be verified?
- What requires human acceptance?

Sprint 2 proves the first local provide/confirm distinction and interaction
history. It does not yet review code or repository diffs.

### 7. Lifecycle maintenance and expansion

Maintenance has two distinct modes in the product direction. Sprint 7 now
implements the bounded evidence input; diagnosis and repair remain future work.

#### Reactive maintenance

A framework execution failure or explicit drift signal supplies bounded evidence
for Cartographer analysis:

```text
execution evidence
→ failure classification
→ targeted re-observation
→ context and impact update
→ reviewable patch
→ accepted framework retest
```

The Sprint 7 framework-side reference collector captures bounded structural
context without labelling a failed test as an application bug. Production
integration and richer policy-approved artefacts remain future work.

#### Proactive maintenance

Cartographer should also support scheduled or post-deployment re-observation of
an approved inventory. This frontend/context regression can detect changes in:

- mapped elements not touched by the current test pool,
- shared components,
- future automation targets,
- process areas whose existing tests still pass despite accumulating drift.

Proactive maintenance must remain bounded by approved origins, areas, actions,
authentication profiles, sensitivity rules, and time/page/cost budgets.

#### Expansion

Adding a new process repeats much of initial creation, but it should reuse the
existing application map, accepted Page Objects, components, fixtures,
configuration mappings, and prior decisions.

A future validation hypothesis is that later processes require fewer repeated
questions, observations, LLM tokens, duplicate artefacts, and review time than
the first process.

Autonomous repair and unrestricted crawling are not part of the first vertical
slice.

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

## System boundary — two modules of one lifecycle

### qa-automation-framework — execution plane

The adapted framework owns:

- reusable POM/SOM structure and project code,
- Page Objects and components,
- fixtures, workflows, and test data,
- environment configuration and secret retrieval,
- Playwright/pytest execution,
- assertions, reporting, and CI/CD,
- future bounded execution-evidence collection.

### TestCartographer — engineering and maintenance plane

TestCartographer owns:

- project-specific discovery and application mapping,
- structured context, questions, evidence, and provenance,
- bounded LLM-assisted architecture and test proposals,
- framework adaptation plans and reviewable patches,
- reactive and proactive change analysis,
- reuse of the application map during expansion.

The modules should cooperate through a concrete project workspace, non-secret
project/authentication profiles, accepted repository changes, and execution
evidence. Cartographer should not import pytest fixtures as its authentication
API, and neither module should copy secrets into context files.

The framework remains usable without TestCartographer or a live LLM during
ordinary execution.

See:

- [`system-lifecycle.md`](system-lifecycle.md),
- [`authentication-strategies.md`](authentication-strategies.md).

## Technical boundary

Current implementation:

- Python 3.11+,
- Pydantic v2,
- pytest,
- deterministic JSON,
- standard-library CLI,
- Playwright with Python as an optional browser dependency,
- human-authorized bounded observation of one selected target,
- provider-neutral synthesis replay with no live LLM dependency,
- bounded local framework inspection and read-only adaptation planning.

Still-open decisions include:

- production project profile beyond the Sprint 5 inspection profile,
- non-secret environment and authentication profiles,
- one-source/two-consumer secret resolution,
- the parked storage-state, login-recipe, and interactive-login strategies,
- safe credentialed browser sessions,
- greenfield discovery and element selection,
- raw evidence storage beyond the current no-raw-capture rule,
- external LLM provider,
- prompt and response protocol,
- general repository source editing and direct original-repository writing mechanism,
- richer review interface,
- database or cross-process storage.

## First end-to-end vertical-slice boundary

The first product-level slice should cover one small process.

```text
1. Select one process and one controlled target application.
2. Build or acquire a structurally valid context shell.
3. Collect and confirm human business and testing context.
4. Guide the browser through the selected flow.
5. Record bounded, reviewed application observations.
6. Expose remaining missing, conflicting, and inferred information.
7. Build a bounded LLM request from authorized context.
8. Propose Page Object and test artefacts.
9. Map the accepted proposal into qa-automation-framework.
10. Execute one test.
11. Review assumptions, evidence, code, and outcome.
12. Measure operator time and corrections.
```

Current progress after Sprint 6:

```text
Step 2 — controlled fixture only
Step 3 — implemented for the deterministic reference flow
Steps 4–5 — bounded for one selected existing locator
Steps 6–8 — bounded synthesis proposal implemented with replay
Step 9 — read-only file/symbol adaptation plan implemented
Step 10 — exact source patch and separate source review implemented
Step 11 — controlled-copy application and first runnable browser test implemented
Step 12 — creation-lifecycle evaluation implemented
Steps 10–12 — not implemented
```

Not required for the first product slice:

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
→ explicit external-processing authorization
→ minimum necessary context
→ bounded external LLM request
```

Requirements:

- credentials must not be included in prompts, context bundles, observations,
  generated documentation, or committed files,
- project configuration should contain secret references rather than values,
- the framework and Cartographer should consume one approved secret source
  through separate runtime adapters,
- raw application capture must not automatically be sent to a provider,
- data minimization must happen before external inference,
- source and sensitivity metadata must be retained where relevant,
- enterprise validation requires a safe environment and data policy.

The current implementation records sensitivity but does not enforce redaction,
authorization, retention, or external-processing policy.

## Product success criteria

A future usable version should demonstrate:

### Context quality

- required information is present or explicitly unknown,
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
- review states are visible,
- the result can be inspected through ordinary files and repository changes.

### Efficiency

- setup time is measured,
- active user time is measured,
- time to first runnable test is measured,
- LLM usage and cost are measured,
- update time after an application change is measured,
- effort for reactive versus proactive maintenance is measured,
- effort to add a second process using the existing application map is measured.

Sprint 3 measures intake interactions and active answer time, plus browser
capture duration, review duration, and capture/review action count. It still
does not measure complete setup or end-to-end operator time.

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
11. execute accepted tests independently through the framework,
12. consume bounded execution evidence for reactive maintenance,
13. perform bounded proactive post-deployment re-observation,
14. add a later process while reusing the existing application map,
15. operate through an approved credentialed enterprise flow,
16. demonstrate usable operation time and comparative value.

This is a product-level direction, not the current implemented capability.

## Validation ladder and enterprise target

Validation should progress from controlled mechanisms to realistic systems:

1. controlled local page,
2. simple public application,
3. modern dynamic public frontend,
4. controlled multi-page reference application,
5. credentialed enterprise-style system,
6. safe Salesforce environment.

Wikipedia-like pages and public portals are stepping stones. They do not prove
enterprise authentication, data handling, component-driven UI, complex process
state, or maintenance economics.

Salesforce remains a deliberate acceptance target, with a candidate Account
creation flow. It must use a safe non-production environment and an implemented
authentication, secret, authorization, data, and retention boundary.

## Out of scope until separately justified

- replacing test analysis or domain expertise,
- a universal no-code automation platform,
- a closed proprietary test representation,
- autonomous production-system exploration,
- fully autonomous business-correctness decisions,
- broad multi-language and multi-framework support,
- automatic Jira ingestion before a data-safety policy exists,
- merging TestCartographer and PhoenixQA,
- claiming time savings before controlled comparison.


## Live guided creation entry point

Sprint 8 adds a creation entry point before browser acquisition. The user can
start from a short automation request rather than a prepared context fixture. A
local LLM plans the interview over deterministic context gaps, while the human
remains the only source of application and business facts.

This capability belongs to the engineering plane:

```text
minimal request
→ guided interview
→ human-reviewed process brief
→ Sprint 9 browser discovery
```

It does not change the execution plane and does not make generated framework
tests depend on Ollama. Sprint 10 is the integrated-engine target: guided multi-element discovery feeds
the existing synthesis, planning, and delivery chain under fixture-supplied
human authority. The first human-operated external-demo target is Sprint 11.

## Sprint 9 scope increment

TestCartographer now includes bounded multi-element discovery for one authorized
page. The product may propose and verify several locator candidates, detect an
ambiguity, ask the human to choose, and apply an accepted process map to the
existing context contract. Whole-application crawling and autonomous element
selection remain explicitly outside product scope.

## Sprint 10 scope increment

TestCartographer now has one fixture-assisted integrated Creation Flow
connecting minimal request intake, bounded discovery, context confirmation, POM
proposal, repository planning, source delivery, and executable framework
verification. The run proves the engine mechanics when explicit human inputs and
decisions are supplied by controlled fixtures. It is not yet a human-operated
external demo and may not claim a fixed percentage of saved work.

## Sprint 11 scope increment

TestCartographer now connects a real operator to the existing entry and authority
points through an interactive CLI and visible browser. The operator must provide
the initial request, answer bootstrap and process-specific questions, confirm
one aggregate process-context summary, resolve ambiguity, and review artefacts.
No fixture may silently substitute for a required human decision in the
user-demo path. Later stages consume already collected context instead of
reopening it because the pipeline advanced.

The operator path uses an interactive CLI, a headed controlled browser, separate
artefact reviews, and an explicit sandbox-execution trigger. The current scope
remains one controlled public-catalog process. Persistent reuse of bootstrap
context across separate runs, arbitrary apps, authentication, downstream
editing, and resume from every review boundary are not included.


## Sprint 12 scope increment

TestCartographer now supports one human-triggered reactive-maintenance reference
flow. It can consume bounded evidence from one independently failed framework
test, authorize current-page re-observation without forcing a diagnosis, let the
operator select a current candidate, show one exact deterministic source repair,
and prove the accepted change in an isolated sandbox.

The scope remains one public local page, one changed test-id locator, one source
file, one test, no authentication, no LLM, and no original-repository write. It
does not add general failure diagnosis, application-defect classification,
context staleness propagation, multi-file repair, or proactive maintenance.
