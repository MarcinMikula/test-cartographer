# Product scope

## Purpose

TestCartographer is an experimental **UI/POM-focused, LLM-assisted quality-engineering
tool** for collecting, organizing, verifying, reusing, and maintaining the
application context required to adapt a reusable Playwright/Python/pytest
automation framework to a real frontend application.

Together with
[`qa-automation-framework`](https://github.com/MarcinMikula/qa-automation-framework),
it forms one lifecycle with two separately executable modules:

```text
TestCartographer
→ engineering and maintenance plane
→ context, discovery, evidence, adaptation, maintenance, expansion

qa-automation-framework
→ execution plane
→ accepted Page Objects, fixtures, tests, assertions, execution evidence
```

Normal test execution must not require TestCartographer or a live LLM.

## Product question

The product should help answer:

> What does the automation framework need to know about this application,
> process, risk, evidence, and environment before maintainable frontend
> automation can be created, maintained, or expanded?

The difficult part is not merely locating a button. Project-specific truth is
distributed across people, the running application, automation code, execution
evidence, requirements, and prior accepted decisions.

TestCartographer therefore treats uncertainty, provenance, freshness, and
review authority as first-class concerns.

## Intended users

The initial target users are technically capable testing professionals who use
AI as part of their engineering workflow, especially:

- test automation engineers using AI-assisted automation,
- senior manual testers who understand the application and can review generated
  Playwright/Python output,
- test analysts and quality engineers who own process intent, risk, expected
  results, and test evidence,
- hybrid testing roles that combine strong application knowledge with assisted
  automation rather than full-time software development.

The product is **not optimized as a general software-development assistant for
application developers**. Developers may use it, but they are not the primary
design baseline: they often already have direct repository knowledge, coding
tools, compilers, IDE assistance, and project-specific implementation context.

A no-code product for non-technical users is outside the v1 target.

## Core value hypothesis

The product is useful only if maintaining an accepted application/automation map
reduces repeated discovery or unsupported assumptions while keeping the human
review burden economically reasonable.

The intended lifecycle is:

```text
collect context
→ verify and review it
→ create automation
→ execute independently
→ collect bounded evidence
→ maintain after drift
→ expand by reusing current knowledge
```

The value hypothesis is not "AI writes code." It is:

> verified context and accepted history should make later automation work more
> correct, traceable, maintainable, and less repetitive.

This hypothesis is **not yet proven economically**.

## Current implemented boundary — after Sprint 14

The repository currently provides controlled, executable slices for:

- strict `ContextBundle` modelling with explicit knowledge states, provenance,
  sensitivity, questions, conflicts, and readiness checks,
- deterministic human intake and review,
- local-LLM-guided question ordering/phrasing while humans remain factual
  authority,
- bounded Playwright observation,
- guided multi-element process discovery with explicit ambiguity handling,
- bounded synthesis request, strict POM proposal protocol, deterministic
  validation, and separate human review,
- read-only repository inspection and framework snapshots,
- repository-aware adaptation planning,
- exact reviewed source patches with hash/fingerprint preflight,
- sandbox-only application and real Playwright/pytest execution,
- framework-side bounded execution evidence,
- one real-operator reactive-maintenance locator-repair slice,
- one real-operator proactive frontend/context-regression slice,
- one real-operator incremental expansion slice that reuses accepted knowledge,
  re-observes stale frontend evidence, extends an existing Page Object, and runs
  the existing and new process together.

The Sprint 14 closure baseline is:

```text
339 tests passed
Search before expansion: PASS
Search after expansion: PASS
Sort after expansion: PASS
original framework unchanged: true
```

These results prove the controlled mechanisms. They do **not** prove external
application generality, enterprise readiness, or productivity savings.

## Authority model

Different sources are authoritative for different facts.

### Human authority

Humans remain responsible for facts that browser state or an LLM cannot safely
establish, including:

- process purpose,
- business risk,
- expected business outcomes,
- role and permission meaning,
- domain rules,
- acceptance or rejection of ambiguous interpretation.

A human can still confirm a wrong fact; TestCartographer records the authority
transition but does not magically prove business truth.

### Application evidence

Browser evidence can establish bounded technical observations such as:

- current element identity,
- locator candidates,
- visibility and selected allowlisted attributes,
- observed state needed by an authorized process.

Application evidence does not automatically establish business meaning.

### LLM authority

An LLM may propose, organize, summarize, or map authorized evidence. It must not
silently become the source of project truth.

Critical outputs remain subject to deterministic parsing/validation and human
review.

### Deterministic authority

Deterministic rules protect structural and safety boundaries such as:

- schema integrity,
- reference integrity,
- authorized status/sensitivity,
- repository fingerprints,
- source hashes,
- allowed operations,
- collision detection,
- preflight before write,
- exact acceptance state.

These rules are guardrails inside the product, not the target user's competing
workflow.

## Persistent project knowledge — highest-priority missing core

Sprint 14 proves reuse inside one controlled expansion flow, but the product
still lacks a persistent project/bootstrap profile with full invalidation
semantics.

The next core boundary should persist project-wide facts such as:

```text
ProjectProfile
├── application identity
├── environment
├── framework/workspace mapping
├── provider/model configuration
├── sensitivity and external-processing policy
├── authentication strategy/reference
└── provenance, version, and review state
```

Bootstrap/project questions should be collected once and reused later.

They should reopen only when:

- the operator explicitly changes them,
- evidence marks them stale or conflicting,
- the application or environment changes,
- framework/provider/model/authentication/policy changes can affect correctness,
- new evidence requires review.

This is a core scalability requirement, not a post-v1 convenience.

## Frontend/POM scope

The product's target technical area is **frontend/UI automation and Page Object
Model adaptation**.

The v1 direction remains:

- Python,
- Playwright,
- pytest,
- Page Objects/components,
- UI process discovery,
- UI maintenance and expansion.

### Explicitly outside TestCartographer scope

The following are not roadmap goals for this product:

- API automation and Service Object Model (SOM) adaptation,
- a universal test framework for every language/tool,
- a general software-development coding agent,
- autonomous ownership of business truth,
- automatic application-defect verdicts from a failed test,
- unrestricted whole-application crawling.

API/SOM work may exist as a separate future project, but it must not expand the
scope of TestCartographer.

## Repository-write boundary

Current acceptance applies reviewed changes only to fresh snapshot-bounded
sandboxes.

This is intentional.

A future real-project workflow needs a safe handoff from:

```text
reviewed patch
→ verified sandbox
→ explicit delivery decision
→ real automation repository
```

The eventual mechanism may be exported patches, explicit application to a
working copy, or a dedicated branch/PR workflow. Direct unattended writes to a
production branch are not a v1 requirement.

The exact solution should be driven by external validation rather than designed
in the abstract.

## Maintenance boundary

Current reactive maintenance proves one locator-drift repair. Current proactive
regression proves one bounded mapped-element drift while a framework test
remains green.

The project must **not** pre-implement an exhaustive taxonomy of imagined
maintenance failures.

During real validation:

```text
real failure
→ collect bounded evidence
→ determine what the current model can/cannot explain
→ record the actual gap
→ implement the smallest justified extension
→ repeat validation
```

This evidence-first rule applies to timing, state, data, workflow,
authentication, assertion, and other failure classes.

## Authentication and enterprise boundary

Credentialed and enterprise validation require a shared lower-level project
configuration for TestCartographer and the framework without sharing pytest
fixtures as APIs.

The intended direction remains:

```text
EnvironmentProfile
+ AuthProfile
+ SecretProvider references
→ framework execution adapter
→ TestCartographer browser adapter
```

Secrets are references, not values stored in project context.

SSO/MFA may legitimately require interactive human login. Human participation
in such flows is not considered a product failure when organization policy or
identity-provider design requires it.

## Validation-first development after Sprint 14

The project has enough controlled architecture to begin challenging its
assumptions on targets it does not control.

The post-checkpoint roadmap therefore prioritizes:

1. persistent project/bootstrap reuse,
2. repeatable external-validation protocol,
3. increasingly difficult public applications,
4. increasingly low-control application targets,
5. authentication and credentialed validation,
6. enterprise/Salesforce validation,
7. comparative usability/economics and the v1.0 decision.

Once real validation begins, a major abstraction should not be implemented only
because it seems theoretically useful. It should be justified by a concrete
failure, friction point, or missing capability observed during validation.

## Product kill criterion

Technical sophistication does not justify the product by itself.

If real comparison shows that TestCartographer:

- requires excessive setup,
- asks too many low-value questions,
- creates more correction/review work than it removes,
- has a learning curve disproportionate to its benefit,
- consistently takes materially longer than simpler workflows without
  compensating quality gains,

then the correct response is simplification, scope reduction, or stopping the
product direction.

A future graphical or IDE interface should be evaluated only after v1 core
workflow value is demonstrated. A GUI cannot rescue a fundamentally inefficient
workflow.
