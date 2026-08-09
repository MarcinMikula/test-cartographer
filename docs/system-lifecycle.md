# System lifecycle

## Purpose

TestCartographer and `qa-automation-framework` are separately executable modules
of one frontend automation lifecycle.

```text
TestCartographer
→ engineering and maintenance plane

qa-automation-framework
→ test execution plane
```

The separation is deliberate:

- normal tests run without TestCartographer,
- normal tests run without a live LLM,
- TestCartographer may inspect and evolve automation only through explicit
  context, evidence, review, and delivery boundaries,
- project/authentication knowledge should be shared through lower-level
  profiles rather than by importing pytest fixtures into TestCartographer.

## Target technical scope

The lifecycle targets:

- frontend/UI automation,
- Python,
- Playwright,
- pytest,
- Page Objects and components,
- process discovery,
- execution evidence,
- maintenance,
- incremental expansion.

API automation and Service Object Model adaptation are outside the product
scope.

## Plane 1 — TestCartographer engineering and maintenance

TestCartographer owns:

- human/process context acquisition,
- evidence and provenance,
- uncertainty and freshness,
- bounded browser observation/discovery,
- LLM-assisted proposal work,
- deterministic validation,
- repository inspection,
- adaptation planning,
- reviewed source delivery,
- execution-evidence interpretation,
- reactive/proactive maintenance proposals,
- reuse during expansion.

It does not own final business truth.

## Plane 2 — framework execution

The adapted framework owns:

- Page Objects/components,
- fixtures and data bindings,
- normal pytest/Playwright execution,
- assertions,
- environment/runtime configuration,
- authenticated test setup,
- ordinary CI/reporting,
- bounded execution-evidence collection.

The framework must remain independently runnable.

## Phase 1 — project/bootstrap establishment

The intended future entry point is a persistent non-secret `ProjectProfile`.

```text
ProjectProfile
├── application
├── environment
├── framework/workspace
├── provider/model configuration
├── sensitivity/external-processing policy
├── authentication strategy/reference
└── provenance/version/review
```

This profile does not yet exist as a complete implemented lifecycle.

It is the next priority because later creation, maintenance, and expansion
cannot scale if every flow asks the same bootstrap questions again.

Project-wide values are reused while current.

They reopen only after explicit change, stale/conflicting evidence, or a
configuration change that can affect correctness.

## Phase 2 — create one automation process

The implemented controlled lifecycle is:

```text
human process knowledge
→ context gaps
→ guided intake
→ bounded browser discovery
→ accepted ContextBundle
→ bounded synthesis request
→ reviewed POM proposal
→ repository snapshot
→ reviewed adaptation plan
→ exact reviewed CodePatch
→ snapshot-bounded sandbox
→ Playwright/pytest execution
```

Human authority remains required for process meaning, risk, expected outcomes,
ambiguity, and acceptance.

## Phase 3 — execute independently

```text
accepted automation repository
+ project configuration
+ external secrets
→ pytest / Playwright
→ assertions and reports
→ bounded ExecutionEvidenceBundle
```

Framework execution does not import TestCartographer.

A failed test remains evidence of failure, not an automatic application-defect
verdict.

## Phase 4 — reactive maintenance

The controlled proven slice is:

```text
framework test failure
→ bounded execution evidence
→ maintenance readiness
→ headed re-observation
→ human candidate selection
→ exact reviewed locator repair
→ fresh sandbox
→ fail-before / pass-after
```

This proves one locator-drift case only.

Broader maintenance will be extended from real failures observed during external
validation rather than from a speculative exhaustive taxonomy.

## Phase 5 — proactive frontend/context regression

The controlled proven slice is:

```text
human-triggered approved inventory
→ independent current framework test remains green
→ bounded re-observation
→ mapped uncovered element drifts
→ mapped-context-stale finding
→ review-only report
```

No scheduler, automatic context mutation, or autonomous repair is currently
required.

## Phase 6 — incremental expansion

Sprint 14 proves:

```text
explicit human second-process intent
→ reuse/gap plan
→ reuse current accepted knowledge
→ re-observe stale mapped target
→ ask only new process-specific questions
→ review candidate ContextBundle
→ reuse existing synthesis/adaptation/delivery pipeline
→ EXTEND_SYMBOL existing Page Object
→ exact hash-bound replacement + new test
→ fresh sandbox
→ old Search PASS + new Sort PASS
```

This is the first proof that the application map can provide value after the
first process.

## Phase 7 — external validation campaign

Checkpoint 14.5 changes the project from architecture-first expansion to
**validation-first learning**.

Validation increases along two axes.

### Axis A — technical difficulty

```text
simple public page
→ dynamic/script-heavy frontend
→ multi-page/component state
→ difficult/scraping-resistant frontend
→ credentialed application
→ enterprise-style system
→ Salesforce
```

### Axis B — control over the target

```text
controlled fixture
→ externally hosted simple target
→ public application we do not own
→ dynamic/low-control application
→ credentialed external target
→ enterprise target with policy constraints
```

The decrease in control is as important as increasing frontend complexity.

A real target is valuable precisely because TestCartographer cannot modify the
application to make its own assumptions pass.

## Validation development rule

Once the campaign begins:

```text
real target
→ run current product
→ observe failure/friction
→ classify evidence
→ record gap
→ implement smallest justified change
→ rerun the same validation
```

Do not add a major abstraction merely because it seems theoretically useful.

This rule applies especially to:

- maintenance failure classes,
- impact analysis,
- graph modelling,
- additional evidence types,
- new browser capabilities,
- repository delivery workflows.

## Phase 8 — authentication and enterprise validation

Credentialed validation eventually requires shared lower-level configuration:

```text
EnvironmentProfile
+ AuthProfile
+ SecretProvider references
```

Both modules interpret the same logical profile through separate runtime
adapters.

Possible authentication strategies remain:

1. sensitive Playwright storage state,
2. declarative login recipe with in-memory secrets,
3. headed interactive human login for SSO/MFA.

Only the strategy required by a selected real target should be implemented
first.

## Phase 9 — Salesforce validation

A provisional safe acceptance flow remains:

```text
login
→ Accounts
→ create Account
→ save
→ verify
```

Use an approved non-production environment only.

Salesforce is a validation target, not a product dependency.

## Phase 10 — comparative validation and v1.0 decision

The final pre-v1 question is operational:

> Is the tool useful enough to justify its complexity?

Compare realistic testing-professional workflows:

```text
normal manual automation aids
vs.
DevTools/Playwright Codegen + general-purpose LLM
vs.
TestCartographer-assisted workflow
```

Measure quality and economics together.

The product should be simplified, narrowed, or stopped if it consistently
increases work without compensating quality/traceability/maintenance benefits.

A graphical/IDE interface should be evaluated only after this core-value
decision.
