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
