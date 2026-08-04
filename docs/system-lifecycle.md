# System lifecycle

## Purpose

TestCartographer and `qa-automation-framework` are separately executable modules
of one automation lifecycle.

They are not intended to become one tightly coupled runtime application.
They cooperate through explicit project context, adaptation proposals,
repository changes, configuration references, and execution evidence.

```text
one automation lifecycle
├── TestCartographer
│   └── engineering and maintenance plane
│
└── qa-automation-framework
    └── test-execution plane
```

The separation is deliberate:

- normal tests must run without TestCartographer or a live LLM,
- TestCartographer must be able to inspect and evolve automation without
  becoming part of every pytest execution,
- secrets and authenticated sessions must be shared through explicit profiles
  and approved stores rather than copied between modules.

## Module responsibilities

### TestCartographer — engineering and maintenance plane

TestCartographer is responsible for the work required to create, extend, and
maintain automation:

- acquire human, project, application, repository, and execution context,
- preserve evidence, provenance, uncertainty, and review decisions,
- build and update the application map,
- use a bounded LLM to propose POM, component, fixture, workflow, data, and test
  changes,
- prepare reviewable adaptation plans and repository patches,
- analyse execution failures and application drift,
- perform bounded proactive re-observation after deployment windows,
- reuse existing knowledge when a new process is added.

The tool may automate substantial engineering work, but business correctness
and acceptance remain human responsibilities.

### qa-automation-framework — test-execution plane

The adapted framework is responsible for:

- normal Python, Playwright, and pytest code,
- Page Objects and reusable components,
- fixtures, workflows, test data, and environment configuration,
- secret retrieval and authenticated browser setup,
- test execution and assertions,
- CI/CD and ordinary reporting,
- bounded execution-evidence collection for maintenance handoff.

Once an adaptation is accepted, ordinary test runs must not require
TestCartographer or a live LLM.

## Shared project workspace

The long-term integration target is a concrete automation repository created
from or aligned with `qa-automation-framework`.

```text
project-automation/
├── pages/
├── components/
├── tests/
├── testdata/
├── configuration and fixtures
├── Playwright authentication state (ignored and sensitive)
└── .test-cartographer/
    ├── project profile
    ├── context bundles
    ├── observations
    ├── proposals
    └── accepted-change history
```

The exact layout is not implemented and must be validated against the real
framework before it becomes a contract.

The workspace should eventually contain a non-secret project profile that maps
logical Cartographer concepts to framework mechanisms, for example:

```text
environment ID
→ framework base-URL setting

actor role
→ authentication profile or fixture

symbolic test-data requirement
→ fixture, builder, or external source

page/component proposal
→ target framework file and class

expected outcome
→ test-level assertion proposal
```

TestCartographer should not import pytest fixtures as its browser-session API.
Both modules should instead interpret lower-level environment, authentication,
and secret-reference profiles.

## Lifecycle phase 1 — create automation

```text
human testing and domain knowledge
+ TestCartographer context and observations
+ bounded LLM synthesis
+ qa-automation-framework conventions
                        |
                        v
       reviewable POM, fixtures, data, and tests
                        |
                        v
                 human acceptance
                        |
                        v
                  framework execution
```

The user informally describes this AI-supported automation-engineering model as
**AItomatyzacja testów**.

The term does not mean fully autonomous test creation. It means that:

- TestCartographer supplies structured project knowledge and evidence,
- an LLM helps analyse and map that knowledge into automation artefacts,
- the framework supplies the target architecture,
- a human guides, reviews, corrects, and accepts the result.

## Lifecycle phase 2 — execute automation

```text
qa-automation-framework
+ accepted code
+ project configuration
+ external secrets
→ pytest / Playwright
→ assertions, reports, and execution evidence
```

This phase is autonomous relative to TestCartographer.

Sprint 7 implements a bounded provider-neutral **Execution Evidence Collector**
reference contract. The production framework integration should follow the same
boundary. The name is intentionally broader than "bug
logger" because a failed test may indicate:

- an application defect,
- an automation defect,
- changed application behaviour,
- invalid test data,
- an environment failure,
- stale project context,
- an unsupported state.

The implemented v0.1 evidence includes:

- test, step, Page Object, and method identifiers,
- attempted action and locator,
- pytest phase and outcome without root-cause claims,
- exception type, safe summary, redacted hashes, and relative failure location,
- minimized application origin/path and bounded structural step metadata,
- framework/runtime metadata,
- links back to the relevant ContextBundle and accepted automation artefacts.

The collector belongs to the execution plane, while validation, maintenance
readiness, analysis, and context updates belong to TestCartographer. Raw traces,
screenshots, network data, and captured output remain outside v0.1.

## Lifecycle phase 3 — reactive maintenance

Reactive maintenance begins with a failed execution or another explicit drift
signal.

```text
framework execution failure
→ bounded execution evidence
→ TestCartographer analysis
→ re-observation with the same project/authentication profile
→ context update and impact analysis
→ reviewable patch
→ human acceptance
→ framework retest
```

The maintenance flow must distinguish application defects from automation,
data, environment, and context problems before proposing a change.

## Lifecycle phase 4 — proactive maintenance

Maintenance must not depend only on current test failures.

An existing suite can miss changed elements because:

- the affected path is not currently covered,
- a shared component changed outside the executed scenario,
- an element is mapped but not yet used by a test,
- a deployment changed future automation targets,
- a test still passes while semantic or structural drift accumulates.

TestCartographer should therefore eventually support scheduled or
post-deployment **frontend/context regression**:

```text
deployment window or explicit schedule
→ approved observation inventory
→ bounded read-only re-observation
→ comparison with accepted application context
→ stale/conflicting/change findings
→ impact report and optional patch proposal
```

This is not permission to crawl an entire enterprise application without
limits. A proactive run needs:

- approved origins and application areas,
- an explicit observation inventory,
- read-only or allowlisted actions,
- time, page, and cost budgets,
- an authentication profile,
- sensitivity and retention rules,
- human review of findings.

## Lifecycle phase 5 — expand automation

Adding a new process resembles initial creation:

```text
new process
→ collect missing human and application context
→ reuse existing application map and repository knowledge
→ bounded LLM proposal
→ human review
→ framework extension and execution
```

The important difference is reuse.

TestCartographer should already know some of the:

- environments and roles,
- authentication profiles,
- pages and reusable components,
- accepted locators,
- fixtures and test-data patterns,
- naming and architecture conventions,
- prior review decisions,
- evidence and maintenance history.

A future product hypothesis is that the second and later processes require less
user effort, fewer repeated questions, lower LLM cost, and fewer duplicate
artefacts than the first process.

## Lifecycle phase 6 — enterprise validation

Simple and public pages are useful for proving narrow mechanisms. They are not
the final product target.

The validation ladder should increase deliberately:

1. controlled local page,
2. simple public application,
3. modern dynamic public frontend,
4. controlled multi-page reference application,
5. credentialed enterprise-style system,
6. safe Salesforce environment as a major acceptance target.

Salesforce is deliberately retained because it exercises realistic concerns:

- authentication and session reuse,
- dynamic component-driven UI,
- complex navigation and application state,
- enterprise data restrictions,
- difficult locator and synchronization decisions,
- reusable business processes such as Account creation.

No real production or confidential system should be used before the
authentication, secret, minimization, authorization, and retention boundaries
are implemented and approved.

## Current implementation boundary

After Sprint 6, TestCartographer implements:

- one-process context modelling,
- deterministic human intake,
- one bounded human-reviewed Playwright observation,
- one minimized provider-neutral synthesis request,
- strict replayed POM proposal parsing and validation,
- explicit human review of a logical proposal,
- one non-secret workspace inspection profile,
- bounded read-only framework inspection,
- one minimized repository snapshot and fingerprint,
- one exact file/symbol adaptation plan,
- one exact source patch with separate review,
- atomic application to a clean framework copy,
- one independently runnable browser test,
- one persisted creation-lifecycle evaluation,
- separate human review of repository placement.

It does not yet implement:

- a live LLM provider,
- general source editing or direct writes to the original framework,
- enterprise-ready generated automation,
- shared environment or authentication profiles,
- execution evidence collection,
- reactive or proactive maintenance,
- expansion reuse,
- enterprise validation.


## Creation-demo sequence after Sprint 7

The creation plane is now deliberately prioritized before maintenance:

```text
Sprint 8: minimal request + local-LLM guided human intake
→ Sprint 9: bounded multi-element browser discovery
→ Sprint 10: one external-demo end-to-end creation flow
→ later: reactive and proactive maintenance
```

Ollama participates only while Cartographer is collecting creation context. The
accepted generated test remains independent of both TestCartographer and a live
model during normal framework execution.
