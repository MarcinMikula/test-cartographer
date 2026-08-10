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

---

## Sprint 1 — minimum context contract and local evidence model

**Date:** 2026-08-01
**Status:** Complete
**Nature of work:** First executable contract slice; no browser or LLM

### Starting question

Sprint 0 ended with a broad but bounded direction:

> Before TestCartographer can collect application context, it must define the
> smallest honest structure capable of storing one useful process.

The first implementation question was not:

> Which agents and integrations should be created?

It was:

> What information must survive between human input, future browser evidence,
> future LLM interpretation, and eventual framework adaptation?

### Initial risk: building a documentation dump

A context model can easily become a large bag of fields:

```text
page
selector
step
expected result
notes
```

That would allow data storage but would not solve the central trust problem.
The system would still be unable to answer:

- where a value came from,
- whether it was observed or inferred,
- whether it is current,
- whether sources disagree,
- whether absence means unknown or omitted,
- whether the bundle is sufficient for the next stage.

The first contract therefore needed to represent not only information, but the
status and authority of that information.

### Decision: model one process, not an application

The first contract contains exactly one process.

This was chosen because one process is the smallest boundary that still forces
us to connect:

- business purpose,
- risk,
- role and preconditions,
- ordered interaction,
- pages and reusable components,
- elements and locator candidates,
- test data,
- expected outcomes,
- evidence and unresolved questions.

A whole-application model would immediately require:

- global identity,
- cross-process ownership,
- shared component lifecycle,
- merge semantics,
- stale-data propagation,
- partial updates,
- database queries.

None of those problems is needed to prove the first useful workflow.

### Decision: use a strict typed contract

Pydantic v2 was selected for contract version `0.1`.

Required properties included:

- runtime validation,
- nested types,
- closed enums,
- cross-field rules,
- cross-reference integrity,
- deterministic JSON,
- JSON Schema generation.

The runtime dependency is justified because validation is the product of this
sprint, not incidental infrastructure.

The package uses a `src` layout:

```text
src/test_cartographer/
```

No CLI, agent abstraction, browser package, or provider layer was created.

### First model attempt: plain values plus source lists

A simpler design could have stored:

```json
{
  "purpose": "Find matching products",
  "purpose_sources": ["jira-123", "tester"]
}
```

This was rejected because it does not distinguish:

- observed,
- supplied,
- inferred,
- confirmed,
- stale,
- conflicting,
- absent.

It also encourages `null` to carry too many meanings.

### Decision: KnowledgeText

Important text values use one shared contract:

```text
value
+ status
+ evidence_ids
+ confidence
+ sensitivity
+ notes
```

This is verbose by design.

The goal is not minimal JSON size. The goal is to prevent context from becoming
more certain as it passes through the system.

### Addition to the Sprint 0 vocabulary: UNKNOWN

Sprint 0 proposed:

```text
OBSERVED
PROVIDED
INFERRED
CONFIRMED
STALE
CONFLICTING
```

Implementation exposed a missing state:

```text
UNKNOWN
```

An open question alone is insufficient. The affected field must explicitly
state that no authorized value currently exists.

Rules:

```text
UNKNOWN
→ no value
→ no evidence
→ no confidence

CONFLICTING
→ no selected value
→ at least two evidence references
→ no confidence

INFERRED
→ value required
→ evidence required
→ confidence required
```

This makes absence and disagreement machine-readable.

### Evidence boundary

Evidence version `0.1` stores:

- identifier,
- source type,
- source reference,
- summary,
- timezone-aware capture time,
- sensitivity,
- optional SHA-256 digest.

It deliberately does not store:

- raw HTML,
- DOM snapshots,
- screenshots,
- Jira descriptions,
- attachments,
- network payloads.

The context bundle should not accidentally become an uncontrolled copy of all
source data.

This decision reduces exposure but does not make the bundle safe. Internal URLs
and confidential summaries may still be sensitive.

### Sensitivity is not authorization

The first contract classifies values and evidence as:

```text
PUBLIC
INTERNAL
CONFIDENTIAL
RESTRICTED
```

The model does not yet decide whether a value may be sent to an external LLM.

This distinction is important:

```text
classification
!=
processing permission
```

Future provider requests need an explicit authorization and minimization
boundary.

### Test data: requirement, not value

The process must describe data needed by an action, but context JSON must not
become a credential or customer-data store.

The solution is `TestDataRequirement`:

```text
id
name and description
symbolic_ref
sensitivity
```

A `fill` or `select` action references the requirement by ID.

Example:

```text
data_search_query
→ symbolic_ref: valid_search_query
```

A future framework adapter may map that requirement to:

- fixture,
- builder,
- configuration,
- secret store,
- approved test-data service.

Sprint 1 stores no real value.

### Pages, components, and element ownership

The first model needed to avoid treating every element as a page-level field.

The contract therefore supports:

```text
PageContext
→ direct elements
→ reusable components

ComponentContext
→ owned elements
```

Each element has one `owner_id`.

Validation rejects:

- unknown owners,
- duplicate ownership,
- mismatch between owner ID and owner element list.

This already forces a future collector to decide whether an element belongs to
a page or a reusable component instead of producing one flat locator list.

### New integrity rule found during implementation

Initial cross-reference validation confirmed that a process step targeted an
existing element.

That was insufficient.

An existing element might belong to another page or to a component not present
on the step page.

The final rule is:

```text
a step target must be
- directly owned by the step page, or
- owned by a component listed on the step page
```

A test was added for this case.

This is an example of why implementing a typed contract before an LLM prompt is
valuable. The inconsistency becomes deterministic and testable.

### Action vocabulary

The first contract supports:

```text
NAVIGATE
FILL
CLICK
SELECT
CHECK
UNCHECK
READ
```

It is intentionally smaller than Playwright's API.

The contract describes process intent, not every possible browser operation.

Action-shape rules include:

```text
NAVIGATE
→ no target
→ no data

FILL / SELECT
→ target required
→ symbolic test-data requirement required

CLICK / CHECK / UNCHECK / READ
→ target required
→ no test-data reference
```

Keyboard, upload, drag-and-drop, download, popup, and multi-tab actions remain
future additions only when a selected process needs them.

### Expected outcome versus expected step state

The model contains both:

```text
ProcessStep.expected_state
```

and:

```text
ProcessContext.expected_outcomes
```

They have different roles.

`expected_state` describes the observable state after one process action and
may help synchronization or diagnosis.

`expected_outcome` describes what the automation ultimately needs to protect.

Example:

```text
step state
→ results region refreshed

process outcome
→ results heading contains the query and only matching items are shown
```

The contract does not yet define assertion operators.

### Critical separation: structural validity and readiness

An early temptation was to reject every context containing unknown or
conflicting values.

That would be harmful.

Unknown and conflicting context are valid knowledge states. They should be
stored so the next workflow can resolve them.

The implementation uses:

```text
ContextBundle validation
→ can the structure be understood without guessing?

assess_readiness(context)
→ is the valid context supported enough for framework adaptation?
```

This allows:

```text
valid + ready
valid + incomplete
valid + conflicting
invalid
```

as four distinct states.

### Initial readiness policy

Business-critical fields:

- purpose,
- risk,
- role,
- preconditions,
- expected outcomes.

For zero-warning readiness, they should be `CONFIRMED`.

`OBSERVED` or `PROVIDED` creates a warning because business meaning still lacks
explicit acceptance.

`INFERRED`, `UNKNOWN`, `STALE`, or `CONFLICTING` blocks.

Technical step intent and expected state accept:

- observed,
- provided,
- confirmed.

An inferred technical value warns; unknown, stale, or conflicting values block.

Every action target requires one primary locator. The primary locator must be:

- observed, or
- confirmed.

An unresolved conflict and a blocking open question also block readiness.

This policy is provisional. It is a first deterministic hypothesis, not an
empirically validated completeness standard.

### Reference flow

Sprint 1 uses a fictional public catalog search flow:

```text
open catalog
→ enter query
→ submit search
→ read results
→ verify query heading and matching items
```

The domain was selected because it is:

- understandable,
- public-data friendly,
- large enough to include a reusable search component,
- large enough to include symbolic input data and expected outcomes,
- independent from a real changing website.

The `.test` URL is not a running application.

### Fixture matrix

Four fixtures were created.

#### Complete

```text
testdata/context/valid/public_search_flow.json
```

Expected:

```text
structurally valid
+ zero readiness issues
```

#### Incomplete

```text
testdata/context/incomplete/public_search_flow.json
```

Contains:

- unknown risk,
- unknown expected outcome,
- inferred primary locator,
- blocking open question.

Expected:

```text
structurally valid
+ readiness blocked
```

#### Conflicting

```text
testdata/context/conflicting/public_search_flow.json
```

Contains two sources disagreeing about the submit-button locator and no
selected resolution.

Expected:

```text
structurally valid
+ readiness blocked
```

#### Invalid

```text
testdata/context/invalid/missing_evidence_reference.json
```

Contains a knowledge value referencing evidence absent from the bundle.

Expected:

```text
rejected during structural validation
```

### Deterministic persistence

`load_context()` and `save_context()` provide the first local persistence
boundary.

Output is:

- UTF-8,
- indented,
- newline-terminated,
- deterministic for the same model,
- suitable for Git review.

SQLite was not added.

The project does not yet know enough about:

- query patterns,
- concurrent updates,
- history,
- cross-process reuse,
- evidence volume.

A database before those needs appear would be architecture by imagination.

### JSON Schema

Pydantic generates:

```text
schemas/context-bundle-v0.1.schema.json
```

A test verifies that the committed schema equals the current model schema.

This provides a provider-neutral artifact for future:

- review UI,
- browser collector,
- LLM request builder,
- integration tests,
- external tooling.

The JSON Schema is not a replacement for semantic documentation or readiness
rules.

### Test results

Sprint 1 finishes with:

```text
23 passed
```

Coverage includes:

- valid fixture,
- knowledge-status invariants,
- strict extra-field rejection,
- global ID uniqueness,
- step ordering,
- action shape,
- dangling references,
- element ownership,
- action-target page availability,
- primary-locator uniqueness,
- symbolic test-data uniqueness,
- valid-but-incomplete readiness,
- valid-but-conflicting readiness,
- deterministic serialization,
- JSON Schema drift.

### What green tests mean

They prove that the implemented contract behaves consistently for controlled
examples.

They do not prove:

- that the contract is complete for a real application,
- that users understand it,
- that the questions required to fill it are acceptable,
- that browser evidence maps cleanly to pages and components,
- that LLM synthesis will be accurate,
- that generated automation will be maintainable,
- that the tool is faster or easier than normal assistance.

### Main design conclusion

Sprint 1 changes how Sprint 2 should be approached.

The next step should not be a broad questionnaire such as:

```text
Describe your application.
Describe your process.
List all expected outcomes.
List all elements.
```

The contract and readiness report already expose specific missing information.

The intake should therefore work from concrete gaps:

```text
risk_not_confirmed
→ ask what failure or loss justifies this automation

outcome_not_confirmed
→ ask what observable result proves success

blocking_question_open
→ ask the stored question
```

This makes deterministic question selection the correct first experiment.

A free-form LLM interviewer may later improve wording or handle unstructured
answers, but it should not define the durable state transition rules.

### Sprint 1 decisions

1. Use Python 3.11+ with a `src` package layout.
2. Use Pydantic v2 as the strict runtime contract implementation.
3. Define context schema version `0.1`.
4. Model one UI process per bundle.
5. Store local context as deterministic human-readable JSON.
6. Preserve status, evidence, confidence, and sensitivity with important text
   values.
7. Add `UNKNOWN` as an explicit status.
8. Keep unresolved conflicts structurally valid.
9. Separate structural validation from adaptation readiness.
10. Store symbolic test-data requirements, not actual values.
11. Store evidence metadata without raw source payloads.
12. Require timezone-aware timestamps.
13. Validate page/component ownership and action-target availability.
14. Commit and test the generated JSON Schema.
15. Defer browser, LLM, Jira, POM proposal, and framework mutation.

### Open questions carried into Sprint 2

- What is the smallest context shell from which an intake can start?
- Which readiness codes should produce human questions?
- Which blockers require browser evidence and should not be asked of a human?
- How should a human answer become `PROVIDED` evidence?
- What explicit review changes `PROVIDED` into `CONFIRMED`?
- When should a new answer replace old context, and when should it create a
  conflict?
- How should corrections preserve history?
- What interaction format is simplest for the first experiment?
- How should active time be measured without recording unnecessary user data?
- Can the reference process be completed through deterministic questions
  without requiring schema knowledge?

### Sprint 1 conclusion

Sprint 1 closes the first executable boundary.

TestCartographer can now store one process without collapsing uncertainty into
certainty and can deterministically state why a valid bundle is not ready.

It still cannot collect that context from a user.

Sprint 2 should prove that a tester can move a bundle from incomplete toward
reviewed context through a small, resumable, measurable intake workflow.

---

## Sprint 2 — deterministic human-guided process intake

**Date:** 2026-08-01

**Status:** Complete

**Nature of work:** Deterministic collection, review, session, CLI, and metrics;
no browser and no LLM

### Starting question

After Sprint 1, the project could represent and validate one process but could
not collect the missing context from a user.

The planned wording created an important clarification question:

> Does Sprint 2 mean that the tool interviews a human using non-LLM,
> deterministic rules?

Yes.

The purpose of Sprint 2 is not to build an intelligent conversational agent.
It is to prove the durable state machine underneath any future conversational
layer.

Working flow:

```text
current ContextBundle
→ identify human-answerable gap
→ select deterministic question
→ accept one explicit answer action
→ update context and evidence
→ reassess
→ save session
```

### Why an LLM was excluded

A free-form LLM interviewer could make the first demonstration look more
natural, but it would hide several product questions:

- Which fields are actually required?
- Which blockers should be asked of a person?
- Which blockers require browser evidence?
- What does an answer change in the model?
- How does the tool avoid repeated questions?
- When is collection complete?
- When is explicit review required?
- What is the difference between incomplete and structurally invalid?

The deterministic workflow provides exact answers that can later constrain an
LLM.

The future model may help:

- rephrase a question,
- interpret a long answer,
- propose several field values,
- detect likely contradictions.

It should not silently own the persistent state transitions.

### First scope correction: intake cannot honestly start from nothing yet

The Sprint 1 context contract requires:

- an application,
- a process,
- at least one page,
- at least one element and locator candidate,
- ordered steps,
- evidence.

A human-only intake cannot discover those browser structures reliably.

Creating placeholder pages, elements, and locators from a few generic questions
would either:

- force the user to author technical JSON indirectly, or
- invent application structure before observing the application.

Sprint 2 therefore starts from a **structurally valid but incomplete bundle**.

The controlled incomplete fixture already contains the application/process
shell and deliberately leaves:

- business risk unknown,
- expected outcome unknown,
- one blocking open question,
- one primary locator inferred rather than observed.

This allows Sprint 2 to prove human context collection while preserving a real
browser-specific blocker for Sprint 3.

### Stage-specific readiness became necessary

The existing `assess_readiness()` combines:

- business context,
- process context,
- open questions,
- conflicts,
- step usability,
- locator evidence.

Using the full report directly would produce a bad questionnaire:

```text
primary_locator_not_observed
→ ask the tester to type a locator
```

That would move browser discovery back onto the human and weaken the product
concept.

Sprint 2 introduced `assess_intake()` as a stage-specific view of the full
report.

It includes only current human-answerable issues:

- purpose,
- risk,
- role,
- preconditions,
- expected outcomes,
- conflicts,
- open questions.

It excludes locator and browser-state blockers.

This creates three distinct states:

```text
structural validity
→ human-intake completion
→ full adaptation readiness
```

A bundle may complete human intake and still be correctly blocked for
adaptation.

### Deterministic question order

The first collection queue is stable:

```text
unresolved conflicts
→ process purpose
→ business risk
→ user role
→ preconditions
→ expected outcomes
→ stored open questions
```

Only values with these statuses require collection:

```text
UNKNOWN
INFERRED
STALE
CONFLICTING
```

Already confirmed fields are not asked again.

The same context state produces the same queue.

### Collection and confirmation must remain separate

The first simple design could have treated every typed answer as confirmed.

That would violate the product principle that providing information and
accepting it as the current test basis are different decisions.

Sprint 2 therefore uses two phases.

#### Collection

A normal text answer creates:

```text
status = PROVIDED
value = human answer
evidence = HUMAN intake evidence
```

#### Review

When required collection is resolved, the tool asks review questions for
human-answerable values still marked:

```text
PROVIDED
OBSERVED
```

`:confirm` changes the displayed value to `CONFIRMED` and appends separate
confirmation evidence.

A correction typed during review remains `PROVIDED` and appears again for
confirmation.

This gives the future product a clean place for:

- domain-expert approval,
- separate automation review,
- role-based confirmation,
- expiring confirmations after application changes.

Those richer policies are not implemented yet.

### Answer actions

The workflow supports four persisted answer actions.

#### Provide

Normal text supplies or replaces a value.

For a `KnowledgeText` target:

- the value becomes `PROVIDED`,
- prior selected value and evidence are replaced for that claim,
- a new human evidence item is added,
- a SHA-256 digest of the answer is retained.

#### Confirm

`:confirm` is available only when a current value exists.

It:

- preserves the current value,
- changes status to `CONFIRMED`,
- retains previous evidence,
- appends human confirmation evidence.

#### Unknown

`:unknown` explicitly states that the information is not available.

For a knowledge field:

```text
value = null
status = UNKNOWN
evidence = none
```

The question is deferred for the active session so the CLI does not
immediately ask it again.

#### Skip

`:skip` leaves context unchanged and defers the question.

This distinction matters:

```text
UNKNOWN
→ the user explicitly says the answer is not known

SKIP
→ the user chooses not to answer now
```

Both avoid an immediate loop, but only `UNKNOWN` changes the knowledge field.

### Stable question IDs across collection and review

An early implementation used separate IDs such as:

```text
q_process_risk
q_review_process_risk
```

This created a loop risk.

If a user marked the review question unknown, the context returned to an
unknown collection state with a different question ID. Deferring the review ID
would not defer the newly regenerated collection ID.

The design was corrected so one target keeps one stable question ID across
collection and review.

The interaction history still records the actual prompt and action, so the two
phases remain distinguishable without changing identity.

### Session states

`IntakeSession` version `0.1` supports:

```text
ACTIVE
PAUSED
COMPLETE
BLOCKED
```

#### Active

At least one non-deferred collection or review question exists.

#### Paused

The user enters `:quit` or interrupts input. State is saved without recording a
fake answer.

#### Complete

No current non-deferred question remains and human-intake blockers are zero.

A complete session may still contain:

- a skipped review warning,
- browser-only adaptation blockers.

#### Blocked

Human-intake blockers remain, but all current questions are deferred.

The user can reopen them explicitly with `--retry-deferred`.

This avoids both infinite repetition and false completion.

### Self-contained persistence

The session embeds the complete current `ContextBundle` rather than storing
only a path.

Advantages:

- one file is enough to resume,
- the original input cannot change underneath an active session,
- status and export use the same state,
- session history remains attached to the context it changed.

Trade-offs:

- contexts are duplicated across session files,
- concurrent sessions do not merge,
- no database query layer exists,
- retention remains the user's responsibility.

The session is saved after:

- creation,
- every accepted answer action,
- pause,
- resume or deferred reset.

### Open-question contract limitation

`OpenQuestion` version `0.1` contains:

- an ID,
- prompt,
- related IDs,
- blocking flag.

It has no generic structured answer field.

Changing the context schema during Sprint 2 solely to anticipate every kind of
question would have been premature.

The bounded solution is:

1. retain the prompt and answer in a human evidence summary,
2. remove the resolved question from the active list,
3. retain prompt, target, and action in session history.

This preserves the reference answer but does not map it automatically into a
business-rule object.

The limitation is documented and carried forward rather than hidden.

### Interaction metrics

The product requirement includes final evaluation of difficulty and operation
time.

Sprint 2 begins instrumentation early.

Each interaction stores:

- sequence,
- question ID and kind,
- prompt,
- target path,
- answer action,
- asked and answered times,
- active response seconds.

Calculated session metrics include:

- interaction count,
- provided count,
- confirmed count,
- unknown count,
- skipped count,
- total active response time.

Normal answer text is not duplicated in the interaction log. It already lives
in the context.

Current timing does not include:

- installation and setup,
- reading documentation,
- consulting another person,
- reviewing exported JSON,
- future code review.

It is instrumentation, not proof that the tool is easy or fast.

### CLI boundary

The first CLI uses only the Python standard library.

Commands:

```text
test-cartographer intake start
test-cartographer intake run
test-cartographer intake status
test-cartographer intake export
```

The CLI deliberately remains plain.

The sprint hypothesis concerns:

- state transitions,
- persistence,
- traceability,
- question burden,
- review behaviour.

A rich terminal or web framework would add presentation work before those
behaviours are validated.

### Line-ending policy

The first Sprint 1 commit exposed Windows LF/CRLF warnings and trailing-space
checks.

Sprint 2 adds `.gitattributes` with explicit text treatment:

- Python, Markdown, JSON, TOML, YAML use LF,
- PowerShell scripts use CRLF.

This does not change product behaviour, but it removes avoidable repository
noise and makes future sprint packages safer to apply on Windows.

### Test results

Sprint 2 finishes with:

```text
47 passed
```

The total includes the 23 Sprint 1 tests and new coverage for:

- deterministic question order,
- stage-specific intake filtering,
- review queue transition,
- evidence-linked answers,
- explicit unknown,
- skip without mutation,
- conflict resolution,
- open-question resolution,
- session states,
- deferred retry,
- pause and resume,
- active-time metrics,
- deterministic session persistence,
- intake JSON Schema drift,
- CLI start, run, status, export, and quit paths.

### Manual CLI demonstration

The controlled incomplete fixture was run through:

```text
risk answer
→ expected-outcome answer
→ matching-rule answer
→ risk confirmation
→ expected-outcome confirmation
```

Final status:

```text
State: complete
Human-intake blockers: 0
Human-intake warnings: 0
Full adaptation blockers: 1
Interactions: 5
Provided: 3
Confirmed: 2
```

The remaining blocker is the inferred submit-button locator.

This is the intended result.

Sprint 2 must not ask the user to convert an inferred locator into observed
evidence.

### What green tests mean

They prove that controlled context state can drive a deterministic, resumable,
reviewable, and measurable human workflow.

They do not prove:

- that a real tester finds the questions clear,
- that the context shell can be created efficiently,
- that the question set is sufficient for a real process,
- that arbitrary answers are mapped into the right domain structures,
- that browser evidence can be collected safely,
- that LLM assistance improves the workflow,
- that POM generation will be maintainable,
- that TestCartographer saves time.

### Sprint 2 decisions

1. Keep question selection deterministic and non-LLM.
2. Start from a structurally valid incomplete context shell.
3. Add stage-specific human-intake assessment.
4. Do not ask humans to supply browser-only evidence.
5. Use a stable question identity per context target.
6. Separate collection (`PROVIDED`) from review (`CONFIRMED`).
7. Preserve explicit `UNKNOWN` separately from `SKIP`.
8. Defer answered-unknown and skipped questions to prevent loops.
9. Use visible `BLOCKED` state when required context remains deferred.
10. Persist a self-contained session containing current context and history.
11. Save after every accepted interaction.
12. Record active answer time and action counts without duplicating normal
    answer text.
13. Retain generic open-question answers through evidence and session history
    without changing context schema `0.1` yet.
14. Use a standard-library CLI.
15. Commit and test intake-session JSON Schema version `0.1`.
16. Add explicit Git line-ending policy.
17. Keep browser, LLM, Jira, POM proposal, and framework mutation outside the
    sprint.

### Open questions carried into Sprint 3

- What controlled local application should replace the fictional `.test`
  target?
- What is the smallest safe browser observation for one selected element?
- How does the user identify or authorize the next element/action?
- Should capture prioritize accessibility data, selected DOM fragments,
  Playwright locator inspection, or a combination?
- What information must be excluded before persistence?
- How should entered test-data values be prevented from appearing in evidence?
- What exactly changes a locator from `INFERRED` to `OBSERVED`?
- How should browser observations propose page or component ownership without
  silently changing confirmed context?
- Is a separate observation contract required before updating
  `ContextBundle`?
- Which parts can be replayed deterministically without opening a live external
  website?
- Does Sprint 3 also need a minimal context-shell builder, or can that remain a
  later integration boundary?
- How will browser interaction time be added to the existing effort metrics?

### Sprint 2 conclusion

Sprint 2 closes the first human-interaction boundary.

TestCartographer can now take a controlled incomplete process context, ask only
human-answerable questions, preserve uncertainty, require explicit review,
save and resume work, and show why the result is or is not complete.

The project still knows application structure only because the fixture supplied
it.

Sprint 3 should add one bounded, human-controlled browser observation and use
real evidence to resolve the remaining locator blocker without introducing an
LLM.

---

## Sprint 3 — bounded guided browser observation

**Date:** 2026-08-01
**Status:** Complete
**Nature of work:** Application-evidence boundary; no LLM or framework generation

### Starting point

Sprint 2 could complete all human-answerable context for the controlled public
catalog process.

The resulting `ContextBundle` still had exactly one full-readiness blocker:

```text
primary_locator_not_observed
```

The Search button locator existed as:

```text
strategy: role
value: button:Search
status: INFERRED
```

This was an intentional boundary. Human intake must not convert a technical
locator hypothesis into application evidence.

### Sprint question

The smallest useful browser question was:

> Can TestCartographer verify one existing locator against one real controlled
> page, persist only minimized evidence, require human acceptance, and remove
> the blocker without changing unrelated business context?

The sprint deliberately did not ask:

- how to explore an unknown application,
- how to generate locators,
- how to model every element,
- how to authenticate,
- how to infer page/component ownership,
- how to generate a POM.

### Separate observation contract

Adding browser fields directly to `ContextBundle` would mix three different
states:

1. temporary capture,
2. human review,
3. accepted application context.

Sprint 3 therefore introduced `BrowserObservation` version `0.1` as a separate
provider-neutral artefact.

The observation can be:

```text
PENDING
ACCEPTED
REJECTED
```

A pending or rejected observation cannot update context.

### User control

The first CLI does not click through an application or offer autonomous
navigation.

The user explicitly supplies:

- context file,
- page URL,
- existing context element ID,
- output observation file,
- sensitivity classification,
- optional browser mode and timeout.

The tool then uses the selected element's existing primary locator.

This is intentionally narrower than an in-browser picker. It proves the
capture and authority boundary before adding a richer interaction model.

### Locator verification

The existing locator vocabulary is translated deterministically into
Playwright operations.

For the reference target:

```text
button:Search
→ page.get_by_role("button", name="Search", exact=True)
```

Capture requires:

- exactly one match,
- a visible target,
- a valid selected-target snapshot.

Zero matches, multiple matches, and invisible matches are failures. A browser
command that returns any element is not sufficient evidence.

### Minimized selected-target snapshot

The original roadmap mentioned bounded DOM and accessibility information.
During implementation, this was narrowed further.

The persisted target snapshot contains only:

- tag name,
- visible state,
- enabled state,
- editable state,
- allowlisted attributes when present.

Allowlisted attributes:

```text
id
role
aria-label
name
placeholder
type
data-testid
```

The observation explicitly records that it did not persist:

```text
input value
text content
HTML
screenshot
raw page
```

A controlled HTML fixture deliberately contains the input value:

```text
do-not-persist-this-input-value
```

Tests prove that the value, `innerHTML`, and `textContent` do not appear in the
serialized observation.

### URL minimization

The browser may navigate to a URL containing a query or fragment, but the
persisted source URL removes both.

Credentials embedded in URLs are rejected.

This reduces accidental leakage, but it is not a complete privacy policy. URL
paths and allowlisted attributes can still be sensitive.

### Review before authority

A successful browser capture creates only `PENDING` evidence.

The user must choose:

```text
ACCEPTED
or
REJECTED with a reason
```

Acceptance verifies again that:

- context ID matches,
- element ID exists,
- locator ID exists,
- locator remains primary,
- strategy and value still match the captured observation.

Only then does the tool:

1. append one `APPLICATION` evidence record,
2. store the capture digest,
3. change the selected locator value to `OBSERVED`,
4. update the context timestamp,
5. rerun adaptation readiness.

It does not modify:

- process purpose,
- risk,
- role,
- preconditions,
- process steps,
- expected outcomes,
- page/component ownership,
- unrelated elements or locators.

### Controlled reference application

The fictional `.test` URL from earlier fixtures was not suitable as browser
evidence.

Sprint 3 adds a dependency-free local HTML page and serves it through a
standard-library HTTP server on an ephemeral loopback port.

The page includes:

- search input,
- Search submit button,
- results heading,
- results list.

The search input contains a deliberate value that must never enter observation
persistence.

### Replay versus live browser evidence

The sprint has two validation paths.

#### Deterministic path

Fakes and committed observation fixtures verify:

- locator mapping,
- exact-one-match rules,
- visibility rules,
- URL minimization,
- attribute allowlisting,
- JSON persistence,
- schema stability,
- review transitions,
- context application,
- CLI behaviour.

#### Real browser path

A Chromium integration test and
`scripts/verify_browser_observation.py` verify:

```text
serve controlled local page
→ open through Playwright
→ match one visible Search button
→ create minimized observation
→ accept it
→ apply it
→ readiness changes from one blocker to ready
```

The container used to prepare the sprint could launch Chromium but its
administrator policy blocked navigation even to `127.0.0.1`, producing
`ERR_BLOCKED_BY_ADMINISTRATOR`.

The deterministic suite therefore completed with:

```text
64 passed
1 browser integration test skipped by environment policy
```

The sprint package installs Chromium and runs the separate browser verifier in
the user's normal Windows environment before commit. The browser claim is not
treated as proven until that verifier succeeds there.

### Real Chromium validation exposed an editability assumption

The first normal Windows run opened the controlled page and resolved the Search
button correctly, but capture failed while calling:

```text
locator.is_editable()
```

Playwright does not define `is_editable()` for every visible element. It throws
for a button because the API is limited to native editable controls,
`[contenteditable]`, and ARIA roles that support `aria-readonly`.

The deterministic fake used during package preparation returned `False` for the
button instead of reproducing Playwright's exception. The mock therefore proved
the local code path but concealed an invalid assumption about the real API.

The capture boundary was corrected to:

1. inspect only tag name, explicit role, and `contentEditable` locally,
2. call Playwright's `is_editable()` only when the selected element supports
   that state,
3. persist `editable = false` for elements such as buttons,
4. add regression tests proving that a button skips the API call and a native
   input still uses it.

This is a useful Sprint 3 learning: real browser verification must remain a
commit gate even when deterministic replay and fake-based tests are extensive.

### Effort metrics

`BrowserObservation` records:

- capture duration,
- review duration,
- capture timestamp,
- review timestamp,
- one capture authorization action,
- one later review action when reviewed.

These are instrumentation only. They do not yet measure complete setup time or
compare TestCartographer with manual work.

### Pytest import collision

Adding another test folder with files named `test_models.py`, `test_io.py`, and
`test_schema.py` exposed pytest's default module-name collision in the current
directory structure.

The project now uses:

```text
--import-mode=importlib
```

This is a repository-level test-collection fix, not a browser feature.

### Sprint 3 decisions

1. Keep browser observation separate from `ContextBundle`.
2. Verify one existing target instead of scanning the page.
3. Require the user to authorize URL and element ID.
4. Use the existing primary locator; do not generate one.
5. Require exactly one visible match.
6. Persist an allowlisted selected-target snapshot only.
7. Exclude input values, text, HTML, screenshots, and raw page data.
8. Minimize persisted URLs and reject embedded credentials.
9. Require human acceptance before `OBSERVED` status.
10. Make rejection explicit and context-preserving.
11. Apply only a narrow locator-and-evidence update.
12. Use direct Playwright sync API as an optional dependency.
13. Use a controlled local HTML page before public websites.
14. Commit and test observation schema version `0.1`.
15. Preserve deterministic replay separately from live browser execution.
16. Record capture/review effort without storing duplicated page content.
17. Add `--import-mode=importlib` to prevent test module-name collisions.
18. Guard Playwright editability checks by element semantics instead of calling
    `is_editable()` for every selected target.
19. Keep LLM, discovery, authentication, POM generation, and framework mutation
    outside the sprint.

### What Sprint 3 proves

Subject to successful browser verification in the normal development
environment, the slice proves that one existing locator can be:

- verified against one real controlled page,
- represented by minimized evidence,
- reviewed explicitly,
- promoted from `INFERRED` to `OBSERVED`,
- used to remove the final reference readiness blocker.

### What Sprint 3 does not prove

- safe capture from arbitrary pages,
- correct redaction of all sensitive data,
- greenfield discovery,
- locator quality beyond one current exact match,
- locator resilience after application changes,
- multi-step browser guidance,
- authentication or credential handling,
- iframe or Shadow DOM support,
- POM proposal quality,
- LLM usefulness,
- framework adaptation,
- generated test correctness,
- usability or time savings.

### Open questions carried into Sprint 4

- What exact subset of confirmed context and accepted observation evidence may
  enter an external LLM request?
- Should URL paths and allowlisted attributes be included by default or require
  explicit field authorization?
- What POM proposal structures are needed before code generation?
- How should a proposal represent pages, components, methods, locator choices,
  fixtures, tests, assumptions, and open questions?
- Which proposal claims must cite specific context or observation IDs?
- How should malformed provider output remain separate from semantically poor
  proposals?
- Should raw provider output be retained locally, and under which sensitivity
  and retention rules?
- Can deterministic replay prove protocol behaviour before any live provider
  call?
- What human review states are required before Sprint 5 may modify a framework
  copy?
- Does the first LLM slice need a live provider, or should it stop at strict
  request rendering, parser, and replay?

### Sprint 3 conclusion

TestCartographer now has its first application-evidence boundary.

The tool still does not understand an unknown application. It can, however,
take one human-reviewed context hypothesis, verify one selected locator through
Playwright, minimize the evidence, require acceptance, and update readiness
without silently rewriting business meaning.

Sprint 4 should use this bounded context as input to a provider-neutral POM
proposal protocol. It must not bypass the safety boundary by sending raw pages
or entire session files to an LLM.

---

## Architecture checkpoint A — one lifecycle, two modules

**Date:** 2026-08-02
**Status:** Complete in documentation
**Nature of work:** Product and roadmap alignment after Sprint 3; no runtime implementation

### Trigger

After the bounded browser-observation slice, the relationship between
TestCartographer and `qa-automation-framework` required a more precise model.

Earlier wording described TestCartographer as a companion that supplies context
to the framework. That was directionally correct but too weak.

The intended product is one automation lifecycle with two separately executable
modules:

```text
TestCartographer
→ engineering and maintenance plane

qa-automation-framework
→ test-execution plane
```

The framework provides the runnable POM architecture. TestCartographer supplies
and maintains the project-specific knowledge, evidence, and changes needed to
create, extend, and maintain that automation.

### Creation is AI-assisted engineering, not one-click generation

The creation flow was clarified as:

```text
human testing and domain knowledge
+ Cartographer context and observations
+ bounded LLM assistance
+ qa-automation-framework conventions
→ POM, components, fixtures, data, and tests
→ human review and acceptance
→ framework execution
```

The user has informally called this model **AItomatyzacja testów** for years.
The term is useful as a memorable description, but it must not imply that the
LLM owns business correctness or can generate an accepted suite without human
review.

### Normal execution remains independent

Ordinary test execution should require:

```text
framework
+ accepted code
+ project configuration
+ approved secrets
→ pytest / Playwright
```

It should not require TestCartographer or a live LLM.

This preserves deterministic operation, normal CI/CD, understandable code, and
the ability to use the adapted framework even when Cartographer is not running.

### Execution should still feed maintenance

Independence does not mean isolation.

Real test suites fail, but a failed test is not automatically an application
bug. It may indicate:

- an application defect,
- an automation defect,
- changed application behaviour,
- stale or invalid test data,
- environment failure,
- stale Cartographer context,
- an unsupported state.

A future framework-side component should therefore collect bounded diagnostic
context. The working name is **Execution Evidence Collector**, which is more
accurate than "bug logger".

Collection belongs to the framework because it knows the executed test,
fixture, Page Object, method, action, locator, environment, and exception.
Diagnosis, context evolution, impact analysis, and patch proposals belong to
TestCartographer.

### Maintenance has reactive and proactive modes

The original maintenance description focused on failures.

That is insufficient because the current test pool may not touch every mapped
or relevant frontend element. A shared component or future automation target
can change while all existing tests remain green.

The product direction now separates:

#### Reactive maintenance

```text
failed run or explicit drift signal
→ execution evidence
→ targeted Cartographer analysis and re-observation
→ context and impact update
→ reviewable patch
→ framework retest
```

#### Proactive maintenance

```text
deployment window or schedule
→ approved observation inventory
→ bounded read-only re-observation
→ comparison with accepted context
→ stale/conflicting/change findings
→ impact report and optional patch proposal
```

This proactive mode is a form of frontend/context regression. It does not grant
permission to crawl an enterprise application without scope or limits.

A future run needs approved origins, application areas, actions, budgets,
authentication, sensitivity, and retention rules.

### Expansion is creation with reusable prior knowledge

Adding a new process is structurally similar to initial creation:

```text
new process
→ missing human context
→ application observation
→ LLM-assisted proposal
→ human review
→ framework extension
```

The difference is that TestCartographer should already know some environments,
roles, pages, components, locators, fixtures, naming conventions, and accepted
decisions.

A future product hypothesis is that adding the second process requires:

- fewer repeated questions,
- fewer repeated observations,
- fewer duplicate artefacts,
- smaller LLM input,
- lower cost,
- less review and implementation time.

This must be measured rather than assumed.

### Shared configuration without copied secrets

Both modules may need the same environment and account, especially for
credentialed systems such as Salesforce.

The intended direction is one approved secret source with two runtime
consumers, not two copied configurations.

```text
secret source
├── framework runtime adapter
└── TestCartographer runtime adapter
```

A future non-secret project profile should contain logical mappings and secret
references, not actual credentials.

TestCartographer should not import pytest fixtures as its authentication API.
Fixtures remain execution-plane details. Both modules should eventually
interpret lower-level concepts such as `EnvironmentProfile`, `AuthProfile`, and
`SecretProvider` references.

### Three authentication strategies parked

Three directions are retained without selecting a universal default:

1. **Shared Playwright storage state** for framework execution and Cartographer
   sessions.
2. **Declarative login recipe** using secrets resolved only in memory and an
   explicit success condition.
3. **Interactive human login** for SSO/MFA flows that should not be scripted.

The choice may differ by environment, identity provider, and company policy.

### Salesforce remains a deliberate acceptance target

Simple pages such as Wikipedia-like sites and modern public portals are useful
for proving narrow mechanisms and increasing frontend difficulty.

They are not representative of the final commercial target.

A safe Salesforce environment remains an intentional enterprise validation
level because it can exercise:

- authentication and session reuse,
- dynamic component-driven UI,
- complex navigation and state,
- enterprise data restrictions,
- difficult synchronization and locator decisions,
- realistic creation, execution, maintenance, and expansion.

A candidate flow remains:

```text
login
→ open Accounts
→ create an Account
→ save
→ verify the record
```

Salesforce must not be used before safe non-production access, secret and
session handling, allowed actions, test data, external-LLM boundaries, and
cleanup are defined.

### Decisions

1. Treat TestCartographer and `qa-automation-framework` as two separately
   executable modules of one automation lifecycle.
2. Keep normal framework execution independent of Cartographer and a live LLM.
3. Use Cartographer context and bounded LLM assistance to support human-guided
   creation and adaptation.
4. Plan a future framework-side Execution Evidence Collector.
5. Separate reactive maintenance from proactive post-deployment
   frontend/context regression.
6. Evaluate expansion as reuse of the existing application map.
7. Plan a shared non-secret project/workspace profile rather than fixture
   coupling.
8. Keep one approved secret source with separate framework and Cartographer
   consumers.
9. Park storage-state, login-recipe, and interactive-login strategies.
10. Retain Salesforce as a major enterprise acceptance target.

### Consequences for the roadmap

The roadmap now extends beyond initial POM generation:

```text
Sprint 4 — bounded LLM synthesis
Sprint 5 — project workspace and framework mapping
Sprint 6 — first runnable test and creation evaluation
Sprint 7 — execution-evidence contract
Sprint 8 — reactive maintenance
Sprint 9 — proactive frontend/context regression
Sprint 10 — expansion using the existing map
Sprint 11 — enterprise authentication and safety
Sprint 12 — validation ladder culminating in Salesforce
Sprint 13 — comparative validation and v1.0 decision
```

Only Sprint 4 is planned. Later slices remain provisional or parked and must be
reshaped using evidence.

### What this checkpoint proves

The product lifecycle and module boundaries are coherent enough to guide the
next contracts without treating framework adaptation as the end of the
project.

### What this checkpoint does not prove

It does not implement or validate:

- project/workspace profiles,
- authentication or secret providers,
- storage-state reuse,
- login recipes,
- interactive SSO/MFA sessions,
- framework adaptation,
- execution-evidence collection,
- reactive or proactive maintenance,
- expansion reuse,
- Salesforce readiness,
- better usability or economics.

---

## Sprint 4 — bounded LLM synthesis and POM proposal

**Date:** 2026-08-02
**Status:** Complete
**Nature of work:** First LLM-facing protocol, replay, deterministic validation,
and human review; no live provider and no repository mutation

### Starting point

Sprint 3 ended with a ready reference context:

```text
human-confirmed process context
+ accepted application observation
+ every primary locator OBSERVED
→ full adaptation readiness
```

The next risk was not whether an LLM could produce plausible Python. The risk
was whether TestCartographer would send too much context, accept fluent but
unsupported output, or silently turn a model response into framework truth.

Sprint 4 therefore focused on the protocol around the model rather than on a
provider integration.

### First boundary: request construction, not prompt improvisation

The source `ContextBundle` contains information that is useful locally but is
not required for the first POM proposal:

- base URL,
- page routes,
- raw evidence source references,
- evidence capture timestamps and hashes,
- free-form notes,
- browser state,
- repository details that have not been inspected.

Passing the whole context to a provider would make minimization implicit and
hard to test.

The sprint introduces `BoundedSynthesisRequest` version `0.1` as the only
authorized LLM input.

Request construction requires:

- full adaptation readiness,
- `CONFIRMED` or `OBSERVED` knowledge,
- allowed sensitivity,
- existing evidence references,
- one observed primary locator per included element.

The request records excluded paths and reasons. Exclusion is therefore visible
rather than hidden inside prompt-building code.

### Reference fixture needed one more confirmation

The post-observation reference context was ready according to the existing
readiness rules, but `application.name` still had status `PROVIDED`.

The synthesis boundary deliberately accepts only `CONFIRMED` and `OBSERVED`
values. The dedicated synthesis-ready fixture therefore records explicit
confirmation of the application name instead of weakening the request rule.

This revealed an important distinction:

> Adaptation readiness and external-LLM authorization are related but not
> identical gates.

A context may be usable locally while a stricter external boundary still
requires an explicit confirmation or sensitivity decision.

### Prompt is a serialization of authority

The provider-neutral prompt is deterministic and contains only:

- fixed protocol instructions,
- the exact `BoundedSynthesisRequest` JSON.

There is no hidden repository context, browser session, prior conversation, or
arbitrary adapter metadata.

The prompt requires exactly one JSON object and prohibits Markdown fences,
commentary, unsupported identifiers, and claims of:

- execution success,
- business correctness,
- locator stability,
- repository fit,
- security or compliance approval.

### Proposal is logical, not repository-specific

`PomProposal` version `0.1` describes:

- Page Object candidates linked to authorized page IDs,
- component-object candidates linked to authorized component IDs,
- methods linked to exact process steps,
- actions linked to authorized elements, locators, and symbolic data,
- symbolic fixture requirements,
- one test intent and outcome-linked assertions,
- optional review questions,
- explicit claim flags.

It intentionally does not contain:

- repository paths,
- generated source code,
- credential values,
- claims that code ran,
- claims that the proposal fits an uninspected framework copy.

Sprint 5 must inspect the actual target repository before any file placement is
proposed.

### Protocol failure and substantive rejection are different

The strict parser rejects:

- empty output,
- Markdown fences,
- non-object roots,
- invalid JSON,
- duplicate keys,
- schema-version drift,
- missing or unexpected fields.

Those outcomes become `PROTOCOL_ERROR`.

A structurally valid proposal may still reference an invented locator, omit a
step, map the wrong action, include a secret claim, omit an outcome, or claim
execution success. Those outcomes become `VALIDATION_REJECTED`.

This separation matters operationally:

```text
malformed model output
≠
well-formed but unacceptable architecture proposal
```

The first is an adapter/protocol reliability problem. The second is a proposal
quality or authority problem.

### Raw output preservation exposed a contract bug

The shared `ContractModel` strips outer whitespace from all strings. That is
useful for identifiers and normal text, but it changed `SynthesisRun.raw_output`
and violated the requirement to preserve exact provider output.

The first test run caught the difference: the trailing newline from the replay
fixture disappeared.

`SynthesisRun` now overrides string stripping so raw output is preserved 1:1.
Nested structured contracts retain their strict trimming rules.

Lesson:

> A generally helpful normalization rule can corrupt forensic protocol data.

Raw provider output needs a deliberately different storage policy from normal
validated text.

### Exclusion names are not leaked values

Another early test asserted that the substring `content_sha256` must not appear
anywhere in the serialized request. The request intentionally listed
`evidence[*].content_sha256` in `excluded_fields`, so the test confused the name
of an excluded field with transmission of its value.

The corrected test inspects minimized evidence objects and verifies that they
do not contain `content_sha256` or `source_ref` keys.

Lesson:

> Data-minimization tests should inspect structure and values, not ban the
> vocabulary used to explain exclusions.

### Deterministic POM validation

The validator checks the proposal against the exact request:

- request and context IDs,
- page and component coverage,
- method ownership,
- exactly-once process-step coverage,
- action kind,
- target element,
- primary locator,
- symbolic test data,
- fixture role/environment mapping,
- absence of secret values,
- test references,
- outcome assertion coverage,
- assertion-related elements,
- prohibited claim flags,
- review-question references.

The validator does not decide whether a class name is elegant or whether a
business expert likes the abstraction. It enforces the authority and coverage
boundary that can be checked deterministically.

### Replay before live provider

`ReplaySynthesisAdapter` records the exact request and prompt and returns stored
raw output.

This proves:

- request rendering,
- adapter boundary,
- raw preservation,
- strict parsing,
- deterministic validation,
- run persistence,
- human review,
- CLI orchestration.

It does not prove that any live model follows the protocol or creates good POM
boundaries.

Starting with replay keeps provider behaviour from masking flaws in the local
contract.

### Human acceptance remains a separate authority stage

A valid run reaches `READY_FOR_REVIEW`, not `ACCEPTED`.

Only a validated proposal can be accepted or rejected. Protocol failures and
validation-rejected proposals cannot be promoted through the review function.
Rejection requires a reason.

Acceptance means only:

> The logical POM proposal is approved as input to target-repository inspection
> and framework mapping.

It does not mean that files should be written or that tests will pass.

### Test result

The complete suite produced:

```text
103 passed
1 browser test skipped in the preparation environment because loopback
navigation is blocked by administrator policy
```

On the normal Windows environment with Playwright Chromium, the expected result
is:

```text
104 passed
```

The standalone synthesis verifier confirmed:

```text
ready context
→ bounded request
→ deterministic prompt
→ replay raw output
→ strict parse
→ valid POM proposal
→ explicit acceptance
```

No live provider was called and no repository file was modified.

### Sprint 4 decisions

1. A live provider may consume only `BoundedSynthesisRequest`, never an
   arbitrary `ContextBundle` or browser/session object.
2. Only confirmed and observed values enter the default request.
3. Public and internal values are the default allowed sensitivity set;
   disallowed required values block construction.
4. Excluded paths and prohibited claims are part of the request contract.
5. The first proposal is logical and source-linked, not repository-specific.
6. Exact raw output must be preserved.
7. Protocol failure remains separate from substantive proposal rejection.
8. Proposal references and coverage are validated deterministically.
9. A valid proposal remains pending until human review.
10. Replay is required before any live-provider claim.
11. Sprint 4 does not write or patch `qa-automation-framework`.

### Open questions carried into Sprint 5

- What is the minimum non-secret project/workspace profile?
- How should TestCartographer inspect a concrete framework copy?
- How should logical page, component, fixture, data, and test concepts map to
  existing files and symbols?
- How should existing artefacts and duplicate responsibilities be detected?
- What plan format can explain exact proposed file and symbol changes without
  writing them?
- How should proposal acceptance and repository-plan acceptance remain separate?
- Which framework conventions are deterministic, and which require human or LLM
  judgement?

### Sprint 4 conclusion

The project now has a complete local boundary around an LLM proposal without
having integrated an LLM.

That is intentional. The sprint proves that a future model can be constrained
by explicit authority, strict structure, deterministic checks, preserved raw
output, and human review.

The next uncertainty is no longer prompt parsing. It is mapping an accepted
logical proposal into a real `qa-automation-framework` workspace without
inventing file placement or duplicating existing architecture.


---

## Sprint 5 — Project workspace and framework adaptation plan

### Starting question

Sprint 4 ended with a human-accepted logical POM proposal. The proposal knew
which application pages, components, methods, fixtures, process steps, locators,
and outcomes were authorized. It deliberately did not know where those concepts
belonged in a concrete `qa-automation-framework` repository.

The next uncertainty was therefore not code generation. It was repository
placement:

> Can TestCartographer inspect a bounded framework workspace and produce an
> exact, reviewable file/symbol plan without reading the whole repository into a
> model or modifying any file?

### Why source generation stayed out of scope

It would have been tempting to combine repository inspection, class generation,
patching, and pytest execution in one sprint. That would have hidden several
independent failure modes:

- the repository snapshot could be wrong,
- the target path could be wrong,
- an existing class or fixture could be duplicated,
- generated code could be invalid,
- a valid patch could still fail at runtime.

Sprint 5 therefore stops before source code. It proves the placement boundary
first.

### Workspace profile as an inspection policy

The first `WorkspaceProfile` is intentionally non-secret and small. It defines:

- root marker files,
- allowlisted repository roots,
- ignored names,
- maximum entry count,
- maximum file size.

The framework root itself is supplied at runtime. Its absolute path is not
stored in the snapshot.

This was an important product decision. A general recursive repository scan
would be easier to code, but it would be harder to justify in an enterprise
workspace. The allowlist makes missing context visible and reviewable instead
of treating full-repository ingestion as harmless.

### Snapshot metadata versus source contents

The inspector reads allowlisted files locally, hashes them, and parses Python
with the standard-library `ast` module. The persisted snapshot stores only:

- relative paths,
- file sizes,
- SHA-256 hashes,
- top-level classes and functions,
- class bases and method names.

It does not persist source text, absolute paths, or secret values.

This does not mean the inspector can prove that inspected files were safe. It
has no secret scanner. The profile owner must exclude secret-bearing files.
The privacy flags describe persisted output, not universal safety of the input
workspace.

### Deterministic repository fingerprint

The root fingerprint is calculated from sorted entry metadata rather than the
capture timestamp. The same repository state therefore produces the same
fingerprint even when inspected later.

The fingerprint becomes a future stale-plan guard:

```text
accepted plan
+ unchanged snapshot fingerprint
→ eligible for Sprint 6 source proposal

accepted plan
+ changed framework fingerprint
→ re-inspect and reconcile before writing
```

Sprint 5 records this rule but does not yet apply patches.

### First mapping convention

For the first POM-only slice, accepted logical artefacts map to:

```text
Page Object       → pages/<class_name>.py
Component Object  → components/<class_name>.py
Fixture           → tests/e2e/conftest.py
E2E test           → tests/e2e/<test_name>.py
```

Class names are converted to snake_case for filenames. The planner checks the
snapshot and classifies each target as:

- `create_file`,
- `add_symbol`,
- `reuse_symbol`.

This is a deterministic convention, not a universal architecture truth. A full
framework adaptation may place fixtures differently or reuse an existing page
boundary. That is why plan review is separate from proposal review.

The first draft mapped fixtures to `tests/conftest.py`. A final check against the
current framework structure showed that its browser fixtures live in
`tests/e2e/conftest.py`. The mapping, controlled fixture, snapshot, plan, tests,
and documentation were corrected before packaging. This is concrete evidence
for the Sprint 5 premise: repository placement must be derived from the inspected
framework rather than remembered or guessed.

### Two acceptance stages are necessary

Sprint 4 acceptance means:

> The logical POM proposal is acceptable as a representation of the authorized
> process.

Sprint 5 acceptance means:

> The exact repository file and symbol targets are acceptable for the inspected
> framework state.

Neither decision means that source code has been generated or that tests pass.

### Controlled framework fixture

The committed framework fixture mirrors the relevant current skeleton layers:

- root markers,
- `pages/`,
- `components/`,
- `tests/e2e/`,
- `testdata/`.

It is deliberately not a vendored copy of the full framework. A small fixture
keeps replay stable and avoids making TestCartographer tests depend on another
repository's network availability or unrelated changes.

The production-facing CLI still accepts a real local framework root. A full
real-copy acceptance run remains a separate evidence step before the mapping
contract is treated as mature.

### Reference plan

The accepted public-search proposal maps to:

```text
pages/catalog_page.py             → CatalogPage
components/catalog_search_form.py → CatalogSearchForm
tests/e2e/conftest.py             → catalog_context
tests/e2e/test_search_catalog.py  → test_search_catalog
```

The page, component, and test targets are `create_file` operations. The existing
E2E `conftest.py` produces `add_symbol` for `catalog_context`. A separate test
exercises `reuse_symbol` when the exact symbol already exists.

### Read-only verifier

The standalone verifier:

1. copies the controlled framework to a temporary directory,
2. hashes the complete tree,
3. inspects the workspace,
4. builds the adaptation plan,
5. records human acceptance,
6. hashes the tree again,
7. requires exact byte-for-byte equality.

The verifier confirms that plan acceptance changes only Cartographer state.

### Test result

The full suite in the preparation environment produced:

```text
127 passed
1 browser test skipped because loopback navigation is blocked by administrator
policy in the preparation environment
```

The expected normal Windows result with Playwright Chromium is:

```text
128 passed
```

The standalone Sprint 5 verifier produced:

```text
Controlled qa-automation-framework workspace inspected read-only.
Only relative paths, file hashes, sizes, and Python symbols were persisted.
Accepted POM proposal mapped to exact page, component, fixture, and test targets.
Human acceptance changed only the adaptation-plan state.
No generated source code was included and no framework file was modified.
```

### Sprint 5 decisions

1. Framework inspection requires an explicit non-secret profile.
2. Absolute local paths are invocation data, not persisted contract data.
3. Traversal is bounded by markers, allowlists, ignored names, file count, and
   file size.
4. The snapshot stores structure and hashes, not source contents.
5. Python files are parsed, not imported or executed.
6. The same repository state must produce the same fingerprint.
7. Only an accepted Sprint 4 run may enter adaptation planning.
8. Logical proposal acceptance and repository-plan acceptance are separate.
9. Exact target operations remain traceable to proposal IDs.
10. Sprint 5 includes no generated source and performs no framework write.
11. A changed framework fingerprint invalidates silent reuse of the old plan.
12. The first file-placement convention remains provisional until Sprint 6 and
    realistic framework acceptance provide evidence.

### Open questions carried into Sprint 6

- What bounded source context is required to generate each accepted operation?
- Should code generation produce complete files, AST edits, or reviewable
  patches?
- How should the tool prove that the framework still matches the accepted
  fingerprint before applying changes?
- How should an existing fixture or class be extended without overwriting human
  code?
- How should imports and `__init__.py` exports be planned?
- Which verification commands are mandatory before a patch can be accepted?
- How should failed collection or execution feed corrections back into the
  proposal and plan?
- What is the smallest meaningful assertion for the first runnable test?

### Sprint 5 conclusion

TestCartographer can now move from an accepted application-level proposal to an
exact repository-aware implementation plan without mutating the framework.

The next uncertainty is source realization: generating and applying the
smallest reviewable patch, then proving that one meaningful framework test can
run independently of TestCartographer and a live LLM.


## Sprint 6 — Controlled source delivery and first runnable framework test

### The final gap was not “generate Python”

After Sprint 5, target files and symbols were known. The remaining uncertainty
was authority and execution:

> Can an accepted plan become exact reviewable source, can that source be
> applied without silently overwriting human work, and can the resulting
> framework test run without TestCartographer?

A direct `plan → write files` path was rejected. It would have collapsed three
independent decisions: whether the logical model is right, whether repository
placement is right, and whether the exact implementation is acceptable.

### Three review gates

The complete creation flow now has separate acceptance for:

1. the logical POM proposal,
2. the exact framework file/symbol plan,
3. the exact generated source patch.

This is more ceremony than a one-prompt generator, but it creates a traceable
authority chain and exposes where a correction belongs.

### Explicit test-data binding was required

The accepted logical proposal names `data_search_query`; it does not supply a
concrete runtime value. A runnable test cannot invent that value silently. The
first `GenerationProfile` therefore maps the symbolic requirement to the public
reference value `Example` and separately names the environment variable holding
the application URL.

This preserves the earlier rule: ContextBundle and model-facing artefacts are
not secret stores. The generation profile is an explicit execution decision.

### Generated code is a more sensitive artefact than repository metadata

Sprint 5 snapshots could remain source-free. Sprint 6 must preserve exact source
for human review and deterministic application. `CodePatch` therefore overrides
global string stripping and stores exact whitespace and resulting hashes.

This improves replay but raises the data classification. A source patch can
contain proprietary names or logic even when it contains no credential. It must
be stored locally and reviewed as code, not treated like harmless metadata.

### A real AST guard found a false positive

The first source safety checker rejected `self.open()` because it searched for
the name `open` without distinguishing a direct built-in call from an object
method. The rule was narrowed to reject direct `ast.Name` calls only.

Lesson: security-flavoured static checks need semantic precision. A broad string
or name match can block ordinary framework APIs while still giving a false sense
of safety. The current guard is useful for the bounded templates, not a proof
that arbitrary generated Python is safe.

### Meaningful assertion forced the page contract to grow

The first generated page exposed the results region but omitted the observed
results heading. The runnable test needed both a content assertion and a visible
heading check, so `CatalogPage` gained the heading locator already authorized by
the accepted proposal.

This was a useful correction: “code compiles” is weaker than “the test expresses
the accepted outcome.” Assertion design feeds back into the Page Object surface.

### Existing fixture files require append semantics

The current framework already has `tests/e2e/conftest.py`. Sprint 6 therefore
uses `append_symbol`, validates the original file hash, and preserves its bytes
before adding `catalog_context`. It does not replace the file or create a second
conftest.

The generated fixture starts and closes its own Playwright context for this
controlled reference slice. That lets the copied framework run through the
TestCartographer verification environment without making the generated test
import TestCartographer. This is a reference implementation, not yet the final
fixture convention for every adapted project.

### Preflight must finish before the first write

All create and append operations are checked before any target changes. A later
failure triggers rollback from captured preflight bytes. Temporary files and
`os.replace` avoid exposing partially written individual files.

This does not solve concurrent editing or merge conflicts. It does establish a
minimum transaction-like boundary for the controlled copy.

### The original framework remains outside the write boundary

The acceptance workflow inspects the user's real local framework, builds and
reviews a plan and patch, then materializes a bounded sandbox and applies only
inside that sandbox. Git status of the original is compared before and after.

The first real Windows acceptance run exposed an important mismatch: the
inspection profile allowed `tests/e2e`, but the setup used broad `robocopy /E`
and therefore also copied an out-of-scope `tests/conftest.py`. Pytest loaded that
parent conftest and failed before collecting the generated test. The patch had
been applied correctly; the sandbox boundary was wrong.

The correction is stronger than excluding one filename. The sandbox is now
materialized from the exact entries stored in the accepted `FrameworkSnapshot`.
Every source file is rechecked against its stored size and SHA-256, the resulting
sandbox is rescanned, and its fingerprint must match before patch application.
Files not inspected cannot silently participate in acceptance execution.

Lesson: a bounded analysis followed by an unbounded copy is not bounded in
practice. Execution evidence is trustworthy only when the execution workspace
is derived from the same authority boundary as the plan.

This distinction matters. Sprint 6 proves that generated automation can run in
the accepted workspace slice; it does not yet prove compatibility with every
plugin and file in the full framework repository or that Cartographer should be
allowed to edit a working project repository directly.

### “Runnable” requires independent execution

The first framework test is not considered runnable merely because Python parses.
The gate requires:

- successful framework compilation,
- exact pytest collection of one target test,
- execution with real Chromium in the normal Windows environment,
- meaningful assertions in the test layer,
- no import of TestCartographer,
- no live LLM call.

This is the first point at which the project can honestly claim a working
creation prototype: accepted evidence has become a framework test that the
framework can execute on its own.

### Creation evaluation is evidence, not a benchmark yet

`CreationEvaluation` records generated, modified, and reused artefacts; review
and application status; compile, collection, and execution timing; correction
count; and time to first runnable test.

One controlled result is not comparative evidence. The same measurements later
need manual, Codegen/general-LLM, and TestCartographer-assisted paths across more
realistic applications.

### Sprint terminology

The roadmap uses “Sprint” as a named, closed delivery increment with exit
criteria, tests, documentation, and a commit. It is not a claim that the project
follows formal timeboxed Scrum. In a larger team these contracts and stories
could span several calendar sprints.

### Sprint 6 decisions

1. Plan acceptance does not authorize source writes.
2. Exact source is a separately reviewed `CodePatch`.
3. Runtime URL and concrete public test data require explicit generation input.
4. Generation and application both reject stale framework fingerprints.
5. Append operations require an exact pre-change file hash.
6. All operations pass preflight before the first write.
7. A failed multi-file application rolls back earlier changes.
8. The first acceptance write occurs only in a sandbox materialized from exact accepted snapshot entries.
9. A runnable result requires compile, collection, real execution, and assertion
   evidence.
10. Normal framework execution must not import TestCartographer or call an LLM.
11. Creation metrics are persisted for later comparative validation.
12. Files outside the accepted snapshot are excluded from the execution sandbox.
13. Direct original-repository modification remains outside Sprint 6 authority.
14. Generation profiles declare required framework files, symbols, and symbol kinds.
15. Framework-contract compatibility is checked before plan review and again before source generation.

### Real acceptance finding: generated imports require an explicit framework contract

The second Windows acceptance run proved the snapshot-bounded sandbox fix, but
then failed during pytest collection because generated `CatalogSearchForm`
imported `components.base_component.BaseComponent` while the selected local
framework snapshot did not contain that file and symbol.

The deterministic template had an implicit assumption that was stronger than
the inspected evidence. A snapshot can be internally valid and still be
incompatible with a specific generation template.

Correction:

- `GenerationProfile` now declares exact required framework files and symbols,
- the local snapshot is checked before the placement plan is shown for review,
- source generation repeats the same contract check,
- missing or wrong-kind symbols block the workflow before code is proposed,
- the error tells the user to select or synchronize a compatible framework
  checkout rather than generating imports that cannot resolve.

Lesson: repository awareness is not only target-path awareness. Generation must
validate the framework API it intends to inherit from or import.

### Open questions carried into Sprint 7

- What is the minimum useful failure-evidence contract?
- Which URL, DOM, screenshot, trace, network, and value fields are allowed?
- How will credentials and business data be redacted before persistence?
- How will evidence distinguish test defects, framework defects, environment
  failures, and application defects?
- How will execution evidence link back to ContextBundle, proposal, plan, patch,
  and exact framework revision?
- What evidence should trigger Cartographer analysis automatically and what
  still requires user authorization?

### Sprint 6 conclusion

TestCartographer can now move from accepted application knowledge to an exact,
reviewed source patch and one independently runnable framework test in a
snapshot-bounded sandbox. The next uncertainty is no longer creation. It is how ordinary framework
execution should return bounded, high-value evidence for maintenance without
turning every failure into an assumed application bug or leaking sensitive data.

## Sprint 7 — Framework execution evidence

### A failed test is an observation, not a bug verdict

The first design temptation was to build a “bug logger”. That name already
assumes too much. A failed test can come from the application, automation code,
test data, configuration, fixtures, environment, an incorrect expectation, or
stale context.

Sprint 7 therefore persists only three execution outcomes:

```text
passed
test_failure
infrastructure_error
```

The distinction is based on pytest phase, which the framework actually knows:

- call failure becomes `test_failure`,
- collection/setup/teardown failure becomes `infrastructure_error`.

Neither outcome states root cause. This preserves evidence without converting a
technical signal into false certainty.

### Framework execution must remain independent

The reference collector is a standalone pytest plugin containing only standard
library and pytest imports. The framework process writes provider-neutral JSON.
TestCartographer loads and assesses that JSON only after pytest has finished.

This proves a stronger form of independence than calling Cartographer from a
fixture:

```text
framework execution
→ JSON contract
→ later Cartographer analysis
```

The adapted automation remains usable even when TestCartographer and every LLM
provider are unavailable.

### Raw failure text was excluded deliberately

Exception messages, assertion introspection, tracebacks, captured output,
screenshots, and Playwright traces can contain credentials, personal data,
business values, full URLs, DOM content, and NDA-protected information.

The default record keeps:

- exception type,
- safe phase summary,
- relative failure location,
- SHA-256 of bounded redacted message and traceback text,
- redaction and truncation metadata.

The raw strings are not serialized. Diagnostic richness can be added later only
through a separate artefact policy; it should not enter v0.1 as an unrestricted
string field.

### A useful step probe must not become a data logger

Maintenance needs more than a node ID and exception type. It needs to know the
last relevant application interaction. But accepting arbitrary dictionaries or
method arguments would recreate the raw-data problem.

The Sprint 7 probe accepts only structural fields:

- step ID,
- Page Object,
- method,
- action,
- target element ID,
- locator ID,
- URL for minimization.

It does not accept input values or arguments. The reference bundle therefore
identifies `CatalogSearchForm.submit_search` and the observed locator without
persisting the search value.

### URL minimization is part of the contract, not caller discipline

A supplied URL may contain user information, query values, tokens, filters, or
fragments. The collector reduces it to origin and path before serialization.

```text
https://user:password@example.test/catalog?query=Example#results
→ https://example.test + /catalog
```

The JSON also contains literal false flags for credentials, query, and fragment
persistence. This makes the privacy claim machine-checkable.

### Traceability can combine run defaults and generated source IDs

A bounded run can provide non-secret defaults for context, process, synthesis,
adaptation, and patch IDs. The generated test already carries a module-level
`TRACEABILITY` tuple with proposal, method, and assertion IDs.

The reference collector combines both. This allows Sprint 7 to link execution
back to creation without changing ordinary test assertions or importing
Cartographer.

The limitation is explicit: a mixed suite will eventually need per-test
generated metadata rather than one profile default.

### Maintenance readiness is not diagnosis readiness

`assess_execution_evidence()` requires every failure record to contain:

- failure details,
- complete high-level traceability,
- at least one bounded step,
- no truncated records.

When those conditions are met, the bundle is ready to enter Sprint 8. That does
not mean Cartographer knows what failed or what should change. It means the next
analysis has a trustworthy starting basis.

### Sprint 7 decisions

1. Execution collection belongs to the framework; analysis belongs to
   TestCartographer.
2. The collector must not import TestCartographer or call an LLM.
3. Version 0.1 classifies by pytest phase, not assumed root cause.
4. `test_failure` must never be presented as synonymous with application bug.
5. Raw exception messages, tracebacks, stdout, stderr, HTML, screenshots, and
   traces are excluded by default.
6. Known runtime secrets are redacted in memory before bounded hashes are
   calculated.
7. Step evidence is structural and does not accept values or method arguments.
8. URLs are minimized to origin and path before persistence.
9. Record and step budgets are part of the profile.
10. Missing traceability and missing step context remain explicit blockers.
11. Static replay and a live intentionally failing pytest subprocess are both
    required.
12. Sprint 8 may analyse validated evidence but must retain uncertainty and
    human review.

### Open questions carried into Sprint 8

- What diagnosis vocabulary avoids false certainty while remaining useful?
- When should evidence produce REVIEW, INSUFFICIENT_EVIDENCE, or a targeted
  re-observation request?
- How should Cartographer choose the smallest affected observation area?
- Which failure types justify marking context `STALE` or `CONFLICTING`?
- How should automation, application, data, and environment hypotheses be
  ranked without treating an LLM as an authority?
- What additional artefacts can be authorized safely, and who approves them?
- How will a repaired proposal be linked to the original evidence and retest?

### Sprint 7 conclusion

The execution plane can now return a bounded, traceable, provider-neutral
maintenance handoff while remaining autonomous relative to TestCartographer.
The next uncertainty is not evidence collection. It is whether Cartographer can
use that evidence to guide a safe, reviewable reactive-maintenance workflow
without guessing root cause or applying silent repairs.

## Sprint 7 acceptance finding — imported CLI tests did not exercise the module entry point

The first real Windows setup passed all 183 tests and generated valid execution
evidence, but `python -m test_cartographer.cli evidence status` failed with a
`NameError`. The execution-format helpers existed below the module's
`if __name__ == "__main__"` block. Direct tests imported and called `main()`, so
the module finished defining every helper before the command ran; the real
module entry point executed earlier and exposed the ordering defect.

The correction moves the entry-point block to the physical end of `cli.py` and
adds subprocess regression tests for both `evidence status` and
`evidence assess`. A CLI contract is not fully tested when only its Python
function is invoked; at least one test must execute the shipped module boundary.


# Sprint 8 — live local-LLM guided intake from minimal context

## Product priority changed after Sprint 7

Execution evidence made reactive maintenance technically possible, but the
central product promise is reducing the expensive discovery and creation work
that happens before a maintainable test exists. The roadmap therefore moved
reactive and proactive maintenance behind three creation-focused increments:

```text
Sprint 8 — live guided intake
Sprint 9 — guided multi-element process discovery
Sprint 10 — fixture-assisted integrated Creation Flow
Sprint 11 — human-triggered interactive Creation Flow
```

This is not cancellation of maintenance. It is sequencing product proof around
the capability that a future external user should see first.

## Starting from nothing still requires a structural shell

`ContextBundle` version `0.1` requires at least one page, element, locator
candidate, process step, outcome, and evidence item. A literally empty bundle is
therefore invalid by design. Sprint 8 introduces `MinimalContextSeed` and a
deterministic builder that creates explicit unknown placeholders rather than
loosening the graph contract or inventing application facts.

The seed contains one short human automation request. The generated context
knows that the request exists, but it does not know the application name,
environment, URL, process name, purpose, risk, role, precondition, or result.

## The LLM should improve conversation without receiving factual authority

The first live-model design question was whether the model should generate
questions freely, infer answers, or only operate on deterministic gaps. Free
question generation would make coverage, traceability, and authority difficult
to prove. Direct inference would recreate the false-certainty problem already
identified in `llm-qa-toolkit`.

The accepted boundary is narrower:

```text
deterministic candidate set
→ LLM orders and rephrases every candidate
→ human answers
→ deterministic intake records evidence
→ human confirms business-critical values
```

The model cannot omit, duplicate, or invent IDs and cannot call context-update
code. This gives the user a conversational interviewer while preserving the
existing deterministic completeness guarantee.

## Two model calls are enough for the first useful slice

Calling the model for every single question would add latency, cost, and more
protocol failure points without proving additional product value. Sprint 8 asks
the model for one complete collection plan and one complete confirmation plan.
The human still sees and answers one question at a time.

This creates a useful compromise:

- the model can prioritize the interview globally,
- structured output validates one exact plan,
- the local 7B model performs only two short generations,
- the deterministic engine can replay the flow without a provider.

## Application metadata and business authority need different review rules

The first implementation attempted to add explicit confirmation questions for
application name and starting URL. That caused previously valid Sprint 2
fixtures to reopen unnecessary review questions. The correction keeps
application name, environment, URL, and process name usable as human-provided
metadata, while retaining confirmation for purpose, risk, role, preconditions,
and expected outcomes.

This preserves backward compatibility and reflects the stronger authority
requirement of business meaning versus discovery configuration.

## Local-only means more than using a localhost default

The profile contract enforces:

- HTTP only,
- loopback host only,
- no URL credentials, query, or fragment,
- no model name containing `cloud`,
- no automatic cloud fallback.

The adapter disables environment proxy inheritance and uses Ollama's native
structured-output chat endpoint. The application URL is collected from the
human but excluded from model input even during the confirmation phase.

## Raw prompt persistence conflicts with minimization

A full prompt log would make debugging easier, but it would duplicate the
initial request and selected context values into another artefact. Sprint 8
stores only provider/model identity, phases, candidate and planned IDs, hashes,
character counts, and latency. Exact generated wording is shown to the human but
not retained in `GuidedIntakeRun`.

The trade-off is explicit: the run proves which contract and question set were
used, but not a verbatim forensic replay of the model conversation.

## Preparation and acceptance evidence

The preparation environment has no local Ollama daemon. The provider contract
was exercised through `httpx.MockTransport`, and the complete live verifier was
run against a local fake server implementing Ollama's version, tags, and chat
response shapes. Deterministic replay completed the full collection and review
workflow.

The normal Windows acceptance gate additionally requires a real local Ollama
installation and the configured model. It performs two real structured-output
chat calls. A replay pass cannot substitute for that gate.

## Sprint 8 decisions

1. Keep the Sprint 2 deterministic intake engine as the authority.
2. Add a minimal seed instead of weakening `ContextBundle` structure.
3. Use local Ollama as the first and only live provider.
4. Default acceptance to the already used `qwen2.5-coder:7b` model.
5. Reject remote endpoints and cloud model names.
6. Let the model order and rephrase only an exact allowlisted question set.
7. Use one collection-plan call and one review-plan call.
8. Never send the starting URL value to the model.
9. Persist hashes and metrics, not raw prompts or responses.
10. Define readiness for guided discovery separately from full adaptation
    readiness.
11. Keep browser graph acquisition and ambiguity handling in Sprint 9.
12. Reserve quantitative time-saving claims for post-Creation-Flow comparison.

## Open questions carried into Sprint 9

- How should the human authorize and start one multi-step browser process?
- Should the tool observe actions performed by the user, guide the user through
  planned actions, or support both modes?
- How will it identify page and component boundaries without whole-page dumping?
- How should several locator candidates be ranked and presented for review?
- What ambiguity should trigger a human question rather than an LLM inference?
- How will authenticated sessions plug into discovery without implementing the
  full enterprise auth roadmap early?
- Which effort metrics best capture manual discovery saved or added?
- What is the smallest real process that is impressive enough for Sprint 10 but
  still bounded enough for trustworthy acceptance?

### Final Sprint 8 hardening before delivery

The delivery review tightened four boundaries after the first complete implementation:

1. The Ollama URL must point to the loopback API root, not an arbitrary nested path.
2. A persisted guided run may resume only against the same profile, seed, session, and context identifiers.
3. Secret-request detection covers both the user-facing question and the model-provided reason.
4. Turn completion timestamps are captured after the provider response instead of before the live call.

Two regression tests were added, raising the normal Windows gate to `205 passed`.

## Sprint 8 acceptance correction — local structured output needs an environment-aware timeout

The first real Windows run proved that a warm `qwen2.5-coder:7b` model could answer a tiny prompt immediately while the bounded nine-question JSON-Schema request still exceeded the original 180-second HTTP read timeout. The model was visible in `ollama ps` and split across CPU/GPU, so this was not a missing-model or cold-start failure.

The acceptance boundary now exposes a per-call timeout, defaults the real verifier to 600 seconds, and reports the exact exceeded limit. The contract remains bounded: the profile still rejects values above 600 seconds. A local model being reachable is not the same as the full structured-output workload being fast enough for a fixed short gate.


## Sprint 8 acceptance correction — timeout is not an output budget

A second real Windows run showed that extending the HTTP read timeout from 180
seconds to 600 seconds did not solve the underlying problem. The model answered
a one-token CLI prompt immediately, but the real non-streaming structured-output
request remained silent while `ollama ps` moved the runner into `Stopping...`.

The request contract had two missing bounds:

1. `/api/chat` did not set `options.num_predict`, so generation had no explicit
   token ceiling.
2. `user_prompt` and `reason` had `minLength` but no JSON-Schema `maxLength`.

A timeout limits how long the caller waits; it does not limit how much output the
model attempts to generate. For local models, especially when split across CPU
and GPU, an unconstrained non-streaming response can look indistinguishable from
a hung process.

The corrected boundary now:

- preloads the selected model through the local API,
- keeps it loaded for 900 seconds across both planning turns,
- caps each response at 768 generated tokens,
- caps `user_prompt` at 180 characters and `reason` at 240 characters,
- prints progress before and after both real provider calls,
- retains the independent 600-second HTTP timeout as a final stop condition.

Operationally, cumulative CPU time from `Get-Process` is not proof that inference
is currently progressing. The model state reported by `ollama ps` and the Ollama
server log are more useful diagnostics. A runner left in `Stopping...` after an
interrupted request should be cleaned up before starting another acceptance run.

## Sprint 9 — bounded multi-element discovery and ambiguity authority

Sprint 8 proved that a real local LLM can guide a human interview from a minimal
request, but the resulting context still contained one technical placeholder.
Sprint 9 tested whether browser discovery could replace that placeholder with a
small process map without turning the tool into an unrestricted crawler.

The reference page intentionally contains two visible `Search` buttons. Both
have the same semantic role and accessible name, and both have unique test IDs.
This matters because uniqueness alone does not prove process meaning. A locator
can identify exactly one DOM node and still identify the wrong business
control.

The resulting design separates four authorities:

1. Playwright supplies bounded browser facts.
2. Deterministic scoring ranks candidates and detects ties.
3. The local LLM phrases a clarification question over an immutable candidate
   set.
4. The human selects the intended element and separately accepts the discovery.

The LLM never selects a candidate or writes a locator to context. This is a
concrete application of the wider judge-authority principle already identified
in other projects: a model may assist only where it has sufficient evidence and
an explicitly bounded decision role.

A second lesson is that Playwright Codegen-style uniqueness is only part of the
costly discovery work. The human still needs to decide which control belongs to
the process, which object owns it, which step uses it, and what observable state
proves success. Sprint 9 begins to structure that work instead of reducing the
problem to selector extraction.

The controlled slice remains deliberately narrow: one page, one component,
three targets, and one ambiguity. This is enough to prove the handoff into the
existing readiness and synthesis pipeline, but not enough to claim broad
application understanding or quantified effort reduction.

## Sprint 10 — orchestration exposed a readiness-authority mismatch

Connecting previously green vertical slices found a real contract mismatch.
After accepted browser discovery, general `ContextBundle` readiness was green,
but application name, environment, process name, and the inherited opening-step
intent still had status `PROVIDED`. The synthesis request correctly accepts only
`CONFIRMED` or `OBSERVED` facts.

The wrong fix would have been to weaken the synthesis boundary or silently
promote those values. Sprint 10 instead adds an explicit synthesis-handoff
review that confirms exactly those four values and records separate human
evidence. Integration readiness is not just the conjunction of module-local
readiness flags; adjacent authority contracts must also agree.

A second lesson is that an integrated Creation Flow needs an effort ledger, not
only a passing test. The reproducible verifier therefore counts fixture-represented
human answers, confirmations, ambiguity resolution, and review decisions. It
separates three live local-model turns from one deterministic synthesis-template
call and explicitly records that no comparative savings were measured.

A third lesson is that orchestration should not expand model authority merely to
look more impressive. Sprint 10 uses live LLM assistance where live boundaries
were already validated (intake and ambiguity phrasing), while POM synthesis
remains deterministic and transparently labeled. The integration proof is stronger because its claims match its evidence.

A fourth and more important product lesson emerged during human review of the
acceptance log: fixture-supplied human authority is not the same as a human
trigger. The engine genuinely reached a passing test, but the setup operator did
not answer the nine questions, confirm the five business facts, select the
ambiguous candidate, or approve the POM, plan, and patch. Phrases such as
`human acceptance` described state transitions executed with fixtures, not real
operator actions.

Therefore Sprint 10 proves a fixture-assisted integrated Creation Flow, not an
external user demo. The next step is not to build another engine. It is to
connect a real human to the existing entry and decision points through an
interactive CLI and visible browser. Readiness must be split explicitly into:

```text
Creation mechanics verified: true
Ready for human-trigger integration: true
Interactive human trigger used: false
Ready for external user demonstration: false
```

## Sprint 11 — human trigger is a separate product proof

Sprint 10 established that the complete Creation Flow engine can move from a
short request to a passing Playwright test. The acceptance discussion exposed a
critical distinction: a fixture can validly exercise a human-authority state
transition, but it cannot prove that a user saw the question, understood the
choice, or triggered the transition.

Sprint 11 therefore did not add another creation engine. It connected a real
operator to the existing entry and authority points through blocking CLI input
and a headed browser.

### What changed

- the operator types the initial request,
- nine intake answers are real terminal actions, followed by one aggregate
  process-context confirmation,
- the browser remains visible while candidate IDs are reviewed,
- the operator resolves the ambiguity,
- discovery, synthesis handoff, POM, repository plan, and patch all block for
  decisions,
- execution has its own trigger,
- a separate `InteractiveOperatorSession` audits action categories and timing
  without persisting raw values.

### Important testing distinction

The corrected scripted verifier covers all 18 blocking prompts and the whole downstream chain.
It is deliberately labelled as mechanics verification, not manual acceptance.
External-demo readiness requires a separate operator-generated session with no
fixture answers and a headed browser.


### Human review exposed prompt multiplication and an unsafe edit interaction

The first manual Sprint 11 run showed that connecting a human is not complete
when every internal state transition becomes a separate prompt. After nine
collection answers, the operator was asked five near-duplicate review questions.
Worse, entering `E` and then `C` caused `C` to be interpreted as a replacement
business value. The tool had preserved authority boundaries but exposed them
through an error-prone interface.

The correction separates three kinds of questions:

1. bootstrap context needed to start the run,
2. process-specific context needed for the current scenario,
3. runtime ambiguity or review questions that exist only at a real authority
   boundary.

The LLM now plans only the collection phase. The five process facts are rendered
as one deterministic summary. One operator confirmation authorizes five
underlying `CONFIRM` transitions, so the context contract remains unchanged
while the operator ledger records the truth: one human decision. Full-word
`CONFIRM`, `EDIT`, `QUIT`, and `CANCEL` commands replace ambiguous single-letter
review shortcuts, and reserved control words cannot be stored as context.

A further product rule is parked: confirmed project bootstrap context should be
asked once and reused across later Creation Flows until the operator requests a
change or evidence marks it stale, conflicting, or invalid after a relevant
configuration change. Sprint 11 enforces non-repetition inside one run; durable
cross-run reuse remains future work.

### New limitations surfaced

- accept/reject exists for downstream artefacts, but in-flow editing does not,
- pause does not yet resume from every downstream boundary,
- one controlled flow does not establish usability or generalization,
- an operator ledger proves participation, not the correctness of the supplied
  business facts.

The architectural conclusion remains:

> The Creation Flow engine works. Sprint 11 connects the real human trigger; the
> next product questions concern usability, breadth, maintenance, and measured
> value rather than basic orchestration.

### Exact authority requires exact display, not a preview label

The first successful real-operator run exposed a second authority mismatch.
The terminal called the gate an `exact code patch` review, but rendered only the
first six lines of each change followed by an ellipsis. The operator had proved
participation, but not acceptance of every generated source line.

Sprint 11 therefore adds a separate post-run re-review gate that reuses the
already accepted intake, discovery, synthesis, and repository plan. It
regenerates the corrected deterministic patch, renders every source line and
content hash, waits for one real acceptance, applies only to a fresh snapshot-
bounded sandbox, and reruns collection and execution. The nine intake answers
and two local-model calls are not repeated.

The same correction established three rules:

- a review label must match what the operator could actually inspect,
- the operator's raw initial request belongs in traceability, not as a method
  docstring,
- the summary must disclose that the LLM plans intake and phrases ambiguity,
  while POM and source generation remain deterministic reference templates.

Incomplete local-model ambiguity wording is now closed deterministically with
the same candidate set and no automatic selection.


## Sprint 12 acceptance — console text is not a machine contract

The full Windows suite reached 100% and exited successfully, but the acceptance
script still failed because pytest received `-q` from `pyproject.toml` and a
second `-q` from the script. At effective `-qq`, pytest omitted the textual
`285 passed` summary that the PowerShell gate expected.

The lesson is the same as with execution-evidence classification: presentation
output is not a stable machine contract. Sprint 12 now writes a JUnit report and
validates exact structural counts (`tests`, `failures`, `errors`, and `skipped`)
instead of parsing terminal wording. The console remains human-readable evidence;
the JUnit document is the acceptance source of truth.


## Sprint 12 final acceptance — the bounded maintenance chain is real

The corrected Windows acceptance run completed with `285 passed` and then
executed the manual Reactive Maintenance Flow with five real operator actions.
One existing framework test failed before repair and passed after the reviewed
sandbox-only locator change. The pre-repair bundle contained one
`test_failure` and zero `infrastructure_error` records.

The operator reviewed the current page in headed Chromium, selected
`cand_002` (`data-testid=catalog-search-submit`), reviewed every line of the
resulting source file, and separately triggered sandbox application and retest.
The original framework remained unchanged. No fixture decision or live LLM was
used, and the flow did not claim that the application contained a defect.

Final evidence:

```text
285 passed
real operator actions: 5
failure before / pass after: 1 / 1
application bug claimed: false
live LLM used: false
original framework unchanged: true
reactive-maintenance blockers: none
```

The product conclusion is deliberately narrow: TestCartographer can guide one
real operator through one controlled reactive locator-maintenance path from
bounded failed-run evidence to a passing sandbox retest. It still cannot
diagnose arbitrary failures, patch the original repository automatically, or
claim general maintenance effectiveness.

## Sprint 13 implementation — green tests and current maps answer different questions

The next maintenance proof must not simply repeat Sprint 12 with a different
trigger. Reactive maintenance starts from failed execution evidence. Proactive
regression must demonstrate value while the current framework test is still
green.

The controlled reference deployment therefore keeps the tested Search flow
unchanged and changes the locator of a separately mapped Sort control. The
framework test passes before and after. TestCartographer reuses an accepted
two-element inventory and detects one stable item plus one locator drift.

### Decision

Implement the first proactive slice as a human-triggered, review-only
post-deployment scan. Do not add a scheduler, authentication abstraction, LLM,
context mutation, or repair handoff before the core distinction is accepted by
a real operator.

### What the evidence can prove

- green automated tests do not establish freshness of the wider application map,
- approved mapped scope can be re-observed independently from ordinary test execution,
- uncovered locator drift can be surfaced as stale context without calling it an application bug,
- accepted project/process/bootstrap context can be reused without repeating intake.

### What remains open

Real scheduling, authenticated applications, map reconciliation, semantic and
visual changes, maintenance handoff, false-positive rates, scale, and operational
economics remain unproven. The roadmap and number of future sprints remain
explicitly pivotable as this evidence arrives.

### Windows headed acceptance exposed a navigation-budget detail

The first real Sprint 13 acceptance attempt passed all 305 automated tests and
the scripted verifier, then timed out only when headed Chromium navigated to
the current controlled page under a 10-second limit. The same local server and
page had already passed both headless framework probes, so the failure was
classified as a demonstration-runtime timing problem, not a proactive-change
classification failure.

The controlled inventory now grants a still-bounded 30-second navigation
timeout for the Windows headed path. The operator-facing inventory summary also
prints navigation and locator timeouts, because an "exact budget" is not truly
reviewable when only page and element counts are shown. Navigation waits for an
HTTP commit and an attached body within one total deadline instead of coupling
the whole budget to a DOMContentLoaded event.

## Sprint 13 final acceptance — proactive drift detection works before test failure

The corrected Windows acceptance run completed with `305 passed`, zero
failures, zero errors, and zero skipped tests. The scripted mechanics run and
the real headed run produced the same two observation hashes and the same
classification result: one stable covered Search element and one uncovered
Sort locator drift classified as `mapped_context_stale`.

The authoritative acceptance artefact records:

```text
fixture_decisions_used: false
headed_browser_used: true
interactive_human_trigger_used: true
operator_action_count: 3
framework green before / after: true / true
stable mapped elements: 1
locator drift: 1
mapped-context stale candidates: 1
proactive-regression blockers: none
```

The framework source fingerprint was identical before and after the run.
Accepted project/process context and inventory were reused without repeating
bootstrap questions. The operator authorized the run, the exact inventory and
timeouts, and the complete review-only report. No application defect was
claimed; no patch or context mutation was generated; no live LLM or raw-page
persistence was used.

The product conclusion remains narrow: TestCartographer can guide a real
operator through one controlled proactive frontend/context regression slice
and surface approved mapped locator drift even while the current independent
framework test remains green. This does not yet prove scheduling, authenticated
or enterprise coverage, broad change detection, false-positive performance,
automatic map reconciliation, maintenance handoff, usability, or measured
savings.


## Sprint 14 — expansion is a reuse problem, not a second greenfield creation

### Starting hypothesis

The next process should not repeat bootstrap intake or rediscover application
and framework facts that are already accepted and current. Expansion needs a
small orchestration layer before the existing synthesis/adaptation/delivery
pipeline, not a second creation engine.

The reference request was intentionally explicit:

```text
Add a second automated process for sorting catalog results.
```

Search already existed. The catalog page and framework structure were known.
Sprint 13 had already produced evidence that the mapped Sort locator
`catalog-sort` had drifted to `catalog-sort-control`.

### Architecture correction after implementation started

The first design stopped too early at an `ExpansionPlan`. Implementation showed
that this would leave the product unable to deliver the second runnable process.
The accepted design was corrected before test closure:

```text
existing accepted knowledge
+ explicit human expansion intent
+ optional currentness/change evidence
→ reuse/gap decision
→ bounded delta collection
→ candidate expanded ContextBundle
→ existing synthesis pipeline
→ existing repository-aware adaptation
→ exact reviewed delivery
→ fresh sandbox execution
```

The existing ContextBundle knowledge states remain authoritative. Sprint 14
adds a separate workflow disposition only:

```text
REUSE
ASK_HUMAN
OBSERVE_NEW
REOBSERVE
REVIEW
BLOCKED
```

This avoids inventing a competing knowledge-status model.

### Existing classes require extension, not fake reuse

A concrete repository problem appeared immediately: `CatalogPage` already
existed, but Sort needed two members that Search did not need. Treating the
class as `REUSE_SYMBOL` would hide missing implementation; inventing a
`CatalogSortPage` would duplicate the page.

Sprint 14 therefore adds `EXTEND_SYMBOL`. The framework snapshot distinguishes
normal methods from `@property` members, rejects name-kind collisions, and
records only explicitly reviewed missing members. The reference extension is:

```text
CatalogPage
+ apply_sort()
+ sort_results
```

Delivery maps an accepted existing-class extension to `REPLACE_FILE`, but not
as a free-form rewrite. The replacement is bound to the inspected source hash,
the accepted plan, the reviewed missing members, deterministic generation, and
preflight source-drift rejection.

### 14D exposed a human-interface failure before a product failure

The first real operator attempt accidentally entered Ctrl+A (`^A`) at an
accept/reject prompt. The runner treated every value other than `A` as a
rejection and aborted the entire flow.

That policy was wrong. A human-guided authority boundary must be strict about
meaning without requiring perfect keyboard input.

The corrected rule is:

```text
A / Accept  → accept
R / Reject  → reject
anything else → no decision; explain and re-prompt
```

The final run deliberately exercised inputs such as `asd` and `123`; neither
was recorded as an authority transition. Only explicit acceptance advanced the
flow.

### Green execution was not enough: review the oracle too

The first successful 14D run exposed a second quality issue after all tests were
green. The generated Sort test used an assertion message copied from the Search
template and the controlled expected value covered only the prefix
`Alpha Beta`.

14D.2 corrected the message to an expected-result statement and changed the
controlled binding to the full `Alpha Beta Zulu` result. The closure gate then
reran the focused expansion/delivery regression, the complete 339-test suite,
and the real headed acceptance.

The current generator still uses a containment assertion and the synthesis
proposal still uses the word `fragment`. This is acceptable only for the
controlled reference slice because the complete expected string distinguishes
the before/after state. It is not evidence of a general-purpose sort oracle.

### Final real-operator evidence

The accepted run records:

```text
status: passed
expansion_verified: true
controlled_demo_ready: true
blockers: []

bootstrap_questions_repeated: false
process_specific_questions_asked: 3
reused_knowledge_item_count: 8
reobservation_count: 1

framework_symbols_reused: 1
framework_symbols_extended: 1
framework_symbols_added: 1
existing_tests_preserved: 1
new_tests_added: 1

operator_action_count: 7
active_operator_seconds: ~24.4
live_llm_calls: 0

interactive_human_trigger_used: true
headed_browser_used: true
fixture_decisions_used: false
base_context_unchanged: true
original_framework_unchanged: true
stale_knowledge_silently_reused: false
automatic_context_write_performed: false
phoenixqa_healing_used: false
raw_page_persisted: false
```

Before expansion the existing Search test passed. After applying the reviewed
patch to a fresh sandbox, Search and Sort both passed. The final closure
regression recorded exactly `339 passed`, zero failures, zero errors, and zero
skipped tests.

### Product conclusion

Sprint 14 provides controlled evidence for the original expansion hypothesis:
TestCartographer can reuse accepted application/framework knowledge, ask only
for genuinely new process context, refresh stale frontend knowledge, and extend
an existing automation structure through the same reviewed creation pipeline.

It does not prove that expansion is faster in general, that eight reused items
translate into business savings, that arbitrary existing classes can be edited
safely, or that this flow scales to authenticated enterprise systems.
## Checkpoint 14.5 — stop expanding theory faster than evidence

Sprint 14 completed the first controlled incremental-expansion proof and exposed
a strategic risk: the architecture was becoming broader faster than the project
was accumulating evidence from applications it does not control.

The checkpoint therefore changes the default development mode.

### Documentation truth

Several current-state documents still described much older implementation
boundaries. This matters in a project whose core model distinguishes current,
stale, conflicting, and unknown knowledge.

The documentation ownership rule is now:

```text
LEARNINGS
→ chronological reasoning

architecture-decisions
→ durable accepted decisions

product-scope
→ current product boundary

known-limitations
→ current limitations only

gaps
→ prioritized missing capability/evidence

future-ideas
→ parked ideas only

roadmap
→ current/provisional delivery direction
```

Historical statements must not remain in current-state indexes merely to
preserve chronology.

### Product focus

TestCartographer remains frontend/UI/POM focused. API/SOM adaptation is removed
from the product roadmap rather than carried as a future expansion obligation.

The primary comparison user is an AI-assisted testing professional, not an
expert application developer. Deterministic rules are safety and structure
inside TestCartographer, not a competing user persona.

### Core priority

Persistent project/bootstrap knowledge is promoted from a parked idea to the
highest-priority core gap.

Sprint 14 proved that reuse can occur, but not that project-wide bootstrap facts
survive correctly across runs with explicit invalidation.

The next core slice should therefore establish a versioned non-secret
`ProjectProfile` with project-wide/process-specific separation and selective
reopening after stale/conflicting/configuration-changing evidence.

### Validation-first rule

From the external-validation campaign onward, major abstractions require a
concrete observed need.

```text
real target
→ current product attempt
→ failure/friction evidence
→ smallest justified design change
→ repeat
```

This intentionally rejects a theory-first path where maintenance taxonomies,
application graphs, broad adapters, or evidence stores are built because they
might someday be useful.

The project has enough controlled architecture. Practice must now increasingly
shape theory.

### Validation ladder

The reset roadmap evaluates targets along two independent dimensions:

1. technical difficulty,
2. decreasing control over the target application.

A public application the project cannot modify is valuable even when its
business flow is simple, because it can expose assumptions hidden by controlled
fixtures.

### Human work and product economics

Human authority remains intentional for business truth, risk, expected outcome,
semantic ambiguity, access authorization, and consequential review.

The product should reduce low-value repetition, not eliminate every human
decision.

v1.0 requires evidence that the workflow is operationally worthwhile. If the
tool is materially slower, harder to learn, correction-heavy, or dominated by
review without compensating quality/traceability benefits, the correct response
is simplification, narrowing, or stopping.

A GUI/IDE layer remains post-v1 evaluation: it may improve usability after core
value exists, but it must not hide an inefficient workflow.

## Sprint 15 — persistence is useful only with selective invalidation

Checkpoint 14.5 identified repeated bootstrap configuration as the next P0 core
problem. Sprint 15 showed that solving it safely required more than saving a JSON
settings file.

The real operator acceptance demonstrated:

```text
first-run bootstrap questions: 3
later creation bootstrap questions: 0
later expansion bootstrap questions: 0
environment/base URL change: REOBSERVE
business context after change: COMPATIBLE
unrelated fields re-asked: 0
final revision: 2
post-acceptance regression: 394/394
```

A Sprint 15C test-design failure confirmed the fingerprint boundary. Tests that
mutated ProjectProfile while retaining the previous fingerprint were correctly
rejected by product code. The tests were corrected to create legal revisions,
and tamper rejection became an explicit regression test.

Lesson:

> Do not weaken a safety invariant because a test fixture constructed a state
> the real persistence boundary would reject.

The current local/single-user, one-environment profile is enough to start real
validation. Sprint 16 should test the evidence protocol rather than enlarge the
profile speculatively.

## Sprint 16 — validation protocol before external targets

### Build the evidence method before interpreting external failures

External validation would be weak if a failed run could be immediately modified
until it passed and the original observation disappeared. Sprint 16 therefore
made one validation run an immutable evidence unit tied to one target, workflow,
and product state.

The practical rule is:

```text
observe
→ persist finding
→ close/verify run package
→ only then design the smallest correction
→ rerun as a new linked run
```

### Difficulty and control are different target properties

A technically difficult target can still be project-controlled, while an
ordinary-looking external site can be low-control. Validation profiles therefore
keep technical difficulty and degree of control as independent axes.

### Package identity must be one-way

The accepted chain is:

```text
target_fingerprint
→ run_fingerprint
→ package_fingerprint
```

### A verifier must distrust its own builder

Verification re-loads target, run, and manifest, re-computes fingerprints and
file hashes, validates policy and finding references, and rejects unmanifested
files.

### Uncommitted acceptance code requires truthful provenance

The controlled pre-closure rehearsal records the base Git commit plus a
working-tree fingerprint over the exact accepted Sprint 16 repository scope.
Normal external validation after closure should run against a clean committed
product state.

### The validation process found a defect in itself

The first complete real-operator rehearsal exposed a measurement defect:
invalid choice input was reprompted correctly but not counted in the final
`invalid_input_reprompts` metric.

```text
authority boundary: worked
measurement: wrong
finding recorded before fix: yes
smallest correction: invalid-choice counter only
regression after correction: 469/469
```

### Usability evidence must not become a productivity claim

The operator rated the controlled workflow as hard while retaining high
confidence. Reuse intent was uncertain in the first complete rehearsal and yes
in the corrected complete rehearsal, but the target was already familiar and the
runs were sequential.

The next meaningful evidence must come from external public targets using the
same protocol.
