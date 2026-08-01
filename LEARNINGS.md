# Learnings

Chronological project journal for TestCartographer.

This file records the path from problem to decision:

```text
problem
→ initial assumption
→ analysis
→ experiment or evidence
→ decision
→ consequence
→ open question
```

It is intentionally more detailed and chronological than the thematic files
under `docs/`. Those files describe the current state. This file preserves how
and why that state was reached.

---

## Sprint 0 — product framing

**Date:** 2026-08-01  
**Status:** Complete  
**Nature of work:** Product definition only; no implementation

### Starting idea

The project began as a possible LLM-based UI explorer or locator module for
`qa-automation-framework`.

The original practical question was:

> What information is needed to create correct, reusable, maintainable, and
> upgradeable automated tests based on the Page Object Model?

The first answer included several knowledge areas:

1. Page Object Model and broader frontend automation principles.
2. Testing methodology, including risk, test basis, expected results, and
   concepts associated with ISTQB.
3. Technical understanding of the tested application: pages, elements, DOM,
   overlays, scripts, states, and application behaviour.
4. Additional project, business, data, environment, and maintenance context
   that is easy to overlook when focusing only on code.

### First reframing: the missing input, not another framework

`qa-automation-framework` already provides a reusable structure. It explicitly
expects a real project to bring its own application behaviour, locators,
contracts, data, risks, and domain rules.

The new tool should therefore not duplicate the framework.

Its primary responsibility should be to collect and organize the project-
specific input required to adapt that framework correctly.

This changed the product from:

> an LLM that generates UI tests

to:

> a context-acquisition and framework-adaptation tool that may generate or
> propose automation artefacts only after it has enough verified context.

### Second reframing: locators are necessary but insufficient

A browser tool can inspect elements and propose Playwright locators. That does
not explain:

- why a process matters,
- what risk the test protects,
- which result is correct,
- what data and role are required,
- whether the scenario belongs at UI/E2E level,
- whether two screens represent separate Page Objects or one reusable
  component,
- whether a successful click produced a business-correct outcome.

A locator catalogue without process and testing meaning would recreate the
shallow part of code generation while leaving the difficult decisions to the
user.

The unit of useful knowledge is therefore not just an element. It is an
element, action, state, or outcome placed in application, process, testing, and
automation context.

Example:

```text
element: Save button
page: Account creation form
process: Create Account
role: Sales user
precondition: Required fields contain valid data
observable result: New Account record is created
risk: Record creation fails or stores incorrect data
automation mapping: AccountForm.save()
evidence: Observed in the application and confirmed by the tester
```

### Required knowledge dimensions

Sprint 0 identified six complementary dimensions.

#### Automation architecture

- POM responsibilities and boundaries,
- reusable components,
- fixtures and workflows,
- test-data separation,
- locator placement,
- assertion placement,
- code readability and maintainability.

#### Testing methodology

- test basis,
- purpose and risk,
- test conditions,
- positive and negative coverage,
- expected results,
- appropriate test level,
- traceability,
- useful evidence.

ISTQB may provide terminology and principles, but the product must not pretend
that mechanically applying syllabus terms creates good automation.

#### Application technology

- DOM and accessibility structure,
- pages and reusable components,
- dynamic rendering,
- overlays and loaders,
- iframes and Shadow DOM,
- application states,
- client-side validation,
- navigation and network-dependent behaviour.

#### Business and process context

- process purpose,
- business rules,
- roles and permissions,
- preconditions,
- required and invalid data,
- expected outcomes,
- exceptions,
- criticality.

#### Project context

- issues and acceptance criteria,
- existing tests,
- test-management artefacts,
- documentation,
- API specifications,
- environment rules,
- existing automation repository.

#### Operational context

- application and process changes,
- selector drift,
- outdated assumptions,
- failed executions,
- maintenance cost,
- human corrections,
- LLM cost and latency.

### Multi-path acquisition

The initial concept required at least three data-acquisition paths.

1. **Human input** for knowledge the tool cannot reliably discover.
2. **Project artefacts**, initially represented by Jira but potentially
   including test-management tools, requirements, and documentation.
3. **The running application**, explored under human guidance.

A fourth path was added during analysis:

4. **The existing repository and execution evidence**, because generated
   proposals must respect what already exists and should learn from traces,
   reports, and prior decisions rather than rediscovering everything.

No single source is authoritative by default. Jira may be outdated, the UI may
show only one state, existing code may contain technical debt, and an LLM may
infer incorrectly.

### Model before code

The most important intermediate output should be a structured, versioned
application-context model rather than immediate source code.

The model should eventually represent:

```text
application
├── environments and roles
├── authentication
├── processes
│   ├── purpose and risk
│   ├── preconditions
│   ├── steps and states
│   ├── business rules
│   └── expected outcomes
├── pages and components
│   ├── elements
│   ├── locator candidates
│   └── observed behaviour
├── test data
├── automation mapping
├── evidence and provenance
└── open questions and conflicts
```

The exact schema and storage mechanism remain deliberately undecided. They are
the subject of Sprint 1.

### Knowledge status and authority

The project must not silently convert model output into fact.

The working status vocabulary is:

```text
OBSERVED
PROVIDED
INFERRED
CONFIRMED
STALE
CONFLICTING
```

These labels are not yet a final schema. Their purpose is to preserve the
difference between evidence and interpretation.

An item may also need:

- source,
- acquisition time,
- confidence,
- sensitivity,
- reviewer,
- related process,
- related automation artefact.

### External LLM assumption and security correction

The project is expected to use a capable external LLM rather than make a weak
local model a mandatory first-class provider.

However, the fact that data is visible in a browser or available in Jira does
not make it public or safe to send to a cloud model.

Potentially sensitive material includes:

- customer and employee data,
- internal URLs and identifiers,
- credentials and session information,
- application architecture,
- confidential requirements and defects,
- hidden DOM values and network payloads.

The intended boundary is therefore:

```text
local acquisition
→ filtering and redaction
→ sensitivity classification
→ minimum necessary context
→ bounded external LLM request
```

This is a product requirement, not a later production-hardening task.

No provider, redaction algorithm, or security implementation was selected in
Sprint 0.

### The Tosca comparison

The concept has real similarities to model-based automation platforms:

- application scanning,
- reusable modules,
- centralized models,
- test construction from those models,
- maintenance after UI changes.

This comparison is useful because it names both the opportunity and the main
risk.

The goal is not to rebuild a closed enterprise automation platform.

The intended differences are:

- output remains ordinary Python, Playwright, and pytest code,
- the generated repository remains usable without the tool,
- Git diffs and human review stay central,
- business and testing meaning are explicit,
- the first slice models one process, not an entire system,
- the project does not begin with a proprietary universal abstraction over all
  technologies.

Working product framing:

> Tosca-like context modelling where useful, but as an open,
> architecture-aware adapter for normal code rather than a replacement
> ecosystem.

### Relationship with PhoenixQA

PhoenixQA addresses runtime recovery after an automation action fails,
especially selector and actionability problems.

TestCartographer addresses an earlier and broader problem:

- understand the application and process,
- collect context,
- map it into maintainable automation,
- later analyse how application changes affect that automation.

PhoenixQA may eventually contribute ideas or optional capabilities to a
maintenance workflow. It is not a dependency of the first vertical slice, and
the projects should not be merged before the boundaries are proven.

### Usability and operation time are product-quality attributes

A technically correct tool can still fail if the user must:

- answer an excessive questionnaire,
- manually describe every element,
- correct most LLM interpretations,
- perform complicated integration setup,
- wait longer than manual adaptation would take,
- learn a private modelling language before producing value.

Final validation must therefore include:

- setup time,
- time to first runnable test,
- active user time,
- number of questions and manual navigation actions,
- number of corrections and rejected proposals,
- time to update automation after a change,
- perceived difficulty,
- user confidence,
- LLM usage and cost.

These measurements should be collected from early prototypes rather than
reconstructed from memory at the end.

### Required comparison baselines

A future claim that TestCartographer saves time or improves quality needs a
baseline.

The intended comparison is:

```text
manual framework adaptation
vs.
human-led adaptation using DevTools, Playwright Codegen, and a general LLM
vs.
adaptation using TestCartographer
```

All paths should use the same target application, starting framework, scope,
acceptance criteria, and quality gates.

### Validation ladder

A likely progression is:

1. Simple public page for basic observation and mapping.
2. Modern dynamic frontend for overlays, loading, components, and unstable DOM.
3. Controlled reference application with known requirements and expected
   architecture.
4. Safe Salesforce environment for an enterprise-style flow such as:

```text
login
→ open Accounts
→ create an Account
→ save
→ verify the record
```

The Salesforce target is a long-term validation environment, not a Sprint 1
requirement.

### Smallest useful vertical slice

The long-term product is large. The first implementation must remain smaller
than the overall vision.

Working first-slice hypothesis:

```text
one selected process
→ minimum human context
→ human-guided browser observation
→ small local context model
→ explicit unknowns and inferences
→ proposed Page Object and test
→ handoff into qa-automation-framework
→ one execution
→ human review
```

Explicitly deferred from that slice:

- Jira integration,
- autonomous crawling,
- full application modelling,
- selector healing,
- multi-provider support,
- Salesforce,
- API/SOM adaptation,
- automatic repository-wide upgrades.

### Sprint 0 decisions

1. The product name is **TestCartographer**.
2. The project complements `qa-automation-framework`; it does not replace or
   duplicate it.
3. The primary product is verified, reusable application context plus a
   controlled adaptation workflow, not isolated test-script generation.
4. Initial scope is POM-oriented UI automation with Playwright, Python, and
   pytest.
5. Human guidance and acceptance are mandatory in the initial product.
6. A structured context model should precede code generation.
7. Knowledge provenance and status must be preserved.
8. External LLM quality may be used, but only behind a deliberate local
   minimization and safety boundary.
9. Usability, active user effort, and time are part of final product
   validation.
10. The first vertical slice must cover one process end to end before broad
    integrations are added.
11. PhoenixQA, Jira ingestion, API/SOM support, and autonomous maintenance are
    separate future directions, not Sprint 1 requirements.
12. No source-code architecture, persistence engine, provider, or framework-
    mutation mechanism was selected in Sprint 0.

### Open questions carried into Sprint 1

- What is the minimum context contract for one useful POM flow?
- Which fields are required, optional, or explicitly unknown?
- How should observations, supplied facts, inferences, and confirmations be
  represented?
- What is the smallest useful evidence and provenance model?
- Should the first persisted representation be human-readable files, SQLite,
  or a combination?
- What sensitive-data classification is required before any LLM request?
- Which information may be inferred, and which always requires human
  confirmation?
- What reference process will provide the first controlled fixture?
- What measurable exit criteria distinguish a useful context model from a
  documentation dump?

### Sprint 0 conclusion

Sprint 0 produced a bounded product direction and a deliberate implementation
stop point.

The project now has enough framing to avoid immediately building either:

- a locator scraper with exaggerated claims, or
- a broad, Tosca-like platform with no validated first workflow.

It does not yet provide evidence that the product is technically feasible,
faster than existing workflows, safer than ad-hoc LLM use, or worth maintaining.

The next step is not an agent hierarchy or Jira connector. It is a minimum,
testable context contract for one small process.
