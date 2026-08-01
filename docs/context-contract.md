# Context contract — version 0.1

## Purpose

The Sprint 1 contract defines the smallest local, provider-neutral structure
that can describe one UI process with enough testing, application, and
provenance context to support a future Page Object Model proposal.

It answers:

> What must TestCartographer know, what may remain unknown, and what must be
> rejected before any browser or LLM workflow is added?

The contract is implemented by:

```text
src/test_cartographer/context/models.py
```

Its generated JSON Schema is committed at:

```text
schemas/context-bundle-v0.1.schema.json
```

## Scope

Version `0.1` models:

- one application environment,
- one UI process,
- one ordered sequence of UI actions,
- process purpose, risk, role, and preconditions,
- observable expected outcomes,
- pages and reusable components,
- elements and locator candidates,
- symbolic test-data requirements,
- evidence references,
- knowledge status and sensitivity,
- open questions,
- unresolved or resolved conflicts.

It does not model:

- the whole application,
- multiple related processes,
- API or Service Object Model context,
- live browser objects,
- raw DOM snapshots,
- screenshots or attachments,
- LLM requests or responses,
- generated code,
- repository diffs,
- execution results.

## Why one process per bundle

The first unit is deliberately one process because it is:

- small enough for human review,
- large enough to include business purpose and expected outcome,
- large enough to cross page, component, element, data, and evidence
  boundaries,
- suitable for a future vertical slice into one runnable test,
- easier to version and invalidate than a premature whole-application model.

Future bundles may reference one another. Version `0.1` does not define that
relationship.

## Contract overview

```text
ContextBundle
├── metadata
│   ├── schema_version
│   ├── id and title
│   └── created_at / updated_at
├── ApplicationContext
│   ├── name
│   ├── environment
│   └── base_url
├── ProcessContext
│   ├── name, purpose, risk, and role
│   ├── preconditions
│   ├── ProcessStep[]
│   │   ├── page
│   │   ├── intent
│   │   ├── UIAction
│   │   └── expected_state
│   └── ExpectedOutcome[]
├── PageContext[]
├── ComponentContext[]
├── UIElement[]
│   └── LocatorCandidate[]
├── TestDataRequirement[]
├── Evidence[]
├── OpenQuestion[]
└── Conflict[]
```

## Strict contract rules

Every model uses:

```text
extra fields → rejected
mutation after validation → blocked
leading/trailing string whitespace → normalized
```

Identifiers use:

```text
^[a-z][a-z0-9_]{2,63}$
```

Examples:

```text
proc_search_catalog
page_catalog
el_search_input
loc_search_input_label
```

Identifiers are globally unique within one bundle.

## KnowledgeText

Important text is not stored as a naked string.

It is represented as:

```json
{
  "value": "Allow a visitor to find matching catalog items.",
  "status": "confirmed",
  "evidence_ids": ["ev_human_scope", "ev_spec_search"],
  "confidence": null,
  "sensitivity": "internal",
  "notes": null
}
```

This structure prevents the system from losing the difference between a value
and the authority supporting it.

### Knowledge statuses

| Status | Meaning | Value | Evidence | Confidence |
|---|---|---:|---:|---:|
| `observed` | directly observed in the application or execution | required | required | optional |
| `provided` | supplied by a person or artefact, not independently confirmed | required | required | optional |
| `inferred` | proposed through interpretation | required | required | required |
| `confirmed` | explicitly accepted as current for the process | required | required | optional |
| `unknown` | required information is not yet available | forbidden | forbidden | forbidden |
| `stale` | a previously supported value may no longer be current | required | required | optional |
| `conflicting` | available sources disagree and no value is selected | forbidden | at least two | forbidden |

`unknown` was added in Sprint 1 because an open question alone is not enough.
The field itself must state that no value is currently authorized.

### Status is not truth scoring

A `confirmed` value means that the project accepted it for the current context.
It does not mean universal correctness.

An `observed` value means that something was seen in one captured state. It does
not prove that the same value exists for every role, environment, or data set.

An `inferred` value preserves a model or human interpretation. It remains
separate from confirmed fact even when confidence is high.

## Evidence

Evidence stores provenance metadata, not arbitrary raw source content.

```json
{
  "id": "ev_app_catalog",
  "source_type": "application",
  "source_ref": "fixture:guided_catalog_observation_v1",
  "summary": "Observed search form, result region, and locator candidates.",
  "captured_at": "2026-08-01T08:45:00+02:00",
  "sensitivity": "public",
  "content_sha256": null
}
```

### Source types

- `human`
- `document`
- `application`
- `repository`
- `execution`
- `system`

### Why raw content is excluded

The first contract does not become a hidden data lake.

Raw source capture may later live in a controlled evidence store. The context
bundle retains only:

- a source reference,
- a short summary,
- a timestamp,
- a sensitivity level,
- an optional content digest.

This reduces accidental duplication of credentials, customer data, internal
HTML, or confidential project documents.

### Timestamp rule

All context and evidence timestamps must include a timezone offset.

Naive timestamps are rejected because later change analysis depends on knowing
when an observation occurred.

## Sensitivity

Version `0.1` uses a minimal four-level classification:

- `public`
- `internal`
- `confidential`
- `restricted`

Sensitivity metadata does not authorize external processing.

It only records a minimum local classification. A future bounded LLM request
must apply an additional explicit authorization and minimization policy.

## ApplicationContext

The application block identifies:

- the application,
- the environment,
- the base URL known for the selected flow.

These are knowledge values because environment and URL information may be
unknown, stale, confidential, or conflicting.

Version `0.1` does not store credentials or browser sessions.

## ProcessContext

A process contains:

- a readable name,
- purpose,
- risk,
- actor or role,
- at least one precondition,
- at least one ordered process step,
- at least one expected outcome.

### Purpose and risk are separate

Purpose answers:

> What useful outcome is this flow intended to provide?

Risk answers:

> What product or project risk justifies automating or verifying it?

A browser path without these fields may still be executable, but it is not yet
a justified test flow.

### Step order

Steps must:

- start at `1`,
- remain contiguous,
- appear in the declared order.

A sequence such as `1, 2, 4` is rejected rather than silently normalized.

## UIAction

The first vocabulary is intentionally small:

- `navigate`
- `fill`
- `click`
- `select`
- `check`
- `uncheck`
- `read`

Rules:

| Action | Target element | Test-data reference |
|---|---:|---:|
| `navigate` | forbidden | forbidden |
| `fill` | required | required |
| `select` | required | required |
| `click` | required | forbidden |
| `check` | required | forbidden |
| `uncheck` | required | forbidden |
| `read` | required | forbidden |

The action model is a process description, not a Playwright command API.

## Pages, components, and elements

### PageContext

A page declares:

- its name and route,
- direct page-owned elements,
- reusable components available on the page.

### ComponentContext

A component declares:

- its name,
- the elements it owns.

A component is not tied to one page. This keeps the first model compatible with
reusable headers, search forms, navigation bars, or modal components.

### UIElement ownership

Each element has exactly one owner:

```text
page or component
```

The owner must match the page/component element list.

The contract rejects:

- unknown owners,
- one element declared by multiple owners,
- an element whose `owner_id` disagrees with the owner list.

### Action-target availability

A process step may target an element only when that element is:

- directly owned by the step page, or
- owned by a component listed on the step page.

This prevents a structurally valid identifier from pointing to an element that
is not available in the declared UI state.

## Locator candidates

A locator candidate contains:

- an identifier,
- strategy,
- knowledge-aware value,
- whether it is the selected primary candidate.

Supported strategies:

- `role`
- `label`
- `test_id`
- `placeholder`
- `text`
- `css`
- `xpath`

An element must contain at least one candidate and may contain at most one
primary candidate.

### Why CSS and XPath remain allowed

The contract records candidate evidence; it does not claim that every
application exposes ideal semantic locators.

Readiness and later architecture rules may prefer semantic strategies. The
storage contract must still represent an unavoidable CSS or XPath candidate
without losing provenance.

## TestDataRequirement

The bundle stores test-data requirements, not real values.

Example:

```json
{
  "id": "data_search_query",
  "name": { "...": "..." },
  "description": { "...": "..." },
  "symbolic_ref": "valid_search_query",
  "sensitivity": "public"
}
```

Actions reference the requirement by `id`.

The future framework adapter may map `symbolic_ref` to a fixture, factory,
configuration key, or test-data model.

Requirements:

- IDs must be valid and unique,
- symbolic references must be unique,
- actual credentials or business values must not be embedded in the contract.

## Expected outcomes

An expected outcome describes an observable result and may reference related UI
elements.

It should express the result the test protects, not merely repeat that an
action completed.

Weak:

```text
The button was clicked.
```

Stronger:

```text
The results heading contains the submitted query and the list contains only
matching catalog items.
```

Version `0.1` does not yet model assertion operators or comparison data.

## Open questions

An open question contains:

- a concrete question,
- related entity IDs,
- whether it blocks adaptation.

Open questions do not replace explicit `unknown` knowledge. They explain how a
known gap should be resolved.

A non-blocking question produces a readiness warning. A blocking question
prevents readiness.

## Conflicts

A conflict records:

- the disputed subject,
- a description,
- at least two evidence sources,
- a knowledge-aware resolution.

An unresolved resolution uses:

```json
{
  "value": null,
  "status": "unknown",
  "evidence_ids": [],
  "confidence": null,
  "sensitivity": "internal",
  "notes": null
}
```

The context remains structurally valid, but readiness is blocked.

## Structural validation

`ContextBundle` rejects:

- unknown fields,
- unsupported schema versions,
- duplicate global IDs,
- duplicate symbolic test-data references,
- dangling page, component, element, data, or evidence references,
- invalid action shapes,
- invalid knowledge-status combinations,
- non-contiguous process steps,
- inconsistent element ownership,
- unavailable action targets,
- multiple primary locators,
- naive timestamps,
- invalid conflict evidence.

Structural validation answers:

> Can the system understand this context without guessing how it is shaped?

## Readiness assessment

`assess_readiness()` answers a different question:

> Is the structurally valid context sufficiently supported for a future
> framework-adaptation proposal?

Current readiness rules include:

- purpose, risk, role, preconditions, and expected outcomes require human
  confirmation for zero-warning readiness,
- unknown, inferred, stale, or conflicting business-critical values block,
- provided or observed business-critical values warn until confirmed,
- process-step intent and expected state must be usable,
- each action target requires one primary locator,
- a primary locator must be observed or confirmed,
- unresolved conflicts block,
- blocking open questions block,
- non-blocking questions warn.

Readiness returns deterministic issues:

```json
{
  "code": "primary_locator_not_observed",
  "severity": "blocker",
  "path": "elements.el_search_submit.locators.loc_search_submit_role.value",
  "message": "A primary locator must be observed in the application or explicitly confirmed before framework adaptation.",
  "related_ids": ["el_search_submit", "loc_search_submit_role"]
}
```

Readiness does not mutate the context or ask an LLM to fill gaps.

## Fixture matrix

### Valid and ready

```text
testdata/context/valid/public_search_flow.json
```

Demonstrates:

- complete one-process model,
- page/component ownership,
- symbolic test data,
- observed primary locators,
- confirmed business context,
- zero readiness issues.

### Valid but incomplete

```text
testdata/context/incomplete/public_search_flow.json
```

Demonstrates:

- explicit unknown risk,
- unknown expected outcome,
- inferred primary locator,
- blocking open question,
- structural validity without readiness.

### Valid but conflicting

```text
testdata/context/conflicting/public_search_flow.json
```

Demonstrates:

- two sources disagreeing about a locator,
- no prematurely selected value,
- unresolved conflict,
- structural validity without readiness.

### Invalid

```text
testdata/context/invalid/missing_evidence_reference.json
```

Demonstrates deterministic rejection of a knowledge value referencing evidence
that is not included in the bundle.

## Serialization

Use:

```python
from test_cartographer.context import load_context, save_context

context = load_context("context.json")
save_context(context, "context.normalized.json")
```

Output is:

- UTF-8,
- indented,
- deterministic for the same model,
- newline-terminated,
- human-reviewable in Git.

## JSON Schema

Export:

```powershell
python scripts/export_context_schema.py
```

The committed schema is checked against the Python model by:

```text
tests/unit/context/test_schema.py
```

Any intentional contract change must update:

1. Python models,
2. JSON Schema,
3. fixtures,
4. tests,
5. this document,
6. schema or package version when compatibility changes.

## Deferred decisions

Version `0.1` does not decide:

- long-term database storage,
- cross-process relationships,
- raw evidence storage,
- schema migrations,
- external LLM authorization,
- browser-capture format,
- generated POM proposal format,
- repository handoff format,
- execution evidence model.

These remain future vertical slices rather than fields added speculatively to
the first contract.

## Sprint 2 intake use

Sprint 2 does not change context schema version `0.1`.

It adds a separate `IntakeSession` contract that embeds and updates one valid
`ContextBundle`.

### Human-answerable fields

The deterministic intake currently maps questions to:

- `process.purpose`,
- `process.risk`,
- `process.role`,
- `process.preconditions`,
- `process.expected_outcomes[].statement`,
- `conflicts[].resolution`,
- `open_questions[]`.

Normal text answers to `KnowledgeText` targets become:

```text
status = PROVIDED
value = supplied text
evidence_ids = new human evidence
```

An explicit review confirmation changes the same field to:

```text
status = CONFIRMED
value = unchanged
evidence_ids = previous evidence + confirmation evidence
```

`UNKNOWN` remains a valid value state and therefore does not make the bundle
structurally invalid.

### Intake completion is not contract validity

A bundle can be:

```text
structurally valid
+ human intake incomplete
```

or:

```text
structurally valid
+ human intake complete
+ adaptation readiness blocked
```

The second state is expected after Sprint 2 when business context is confirmed
but application evidence, such as an observed primary locator, is still
missing.

### Open-question limitation

`OpenQuestion` version `0.1` has no generic answer field.

When the Sprint 2 intake receives a supplied answer, it:

- creates human evidence retaining the prompt and response,
- removes the question from the active open-question tuple,
- preserves the interaction in `IntakeSession` history.

This is a bounded compatibility approach, not a final domain-modelling
solution.

If real project questions need structured answers, the context schema should be
versioned rather than adding arbitrary unvalidated dictionaries.

### Session schema

The separate intake-session JSON Schema is committed at:

```text
schemas/intake-session-v0.1.schema.json
```

It does not replace the context schema. It represents workflow state around an
embedded context.

## Sprint 3 browser-evidence boundary

`ContextBundle` remains version `0.1`. Browser runtime objects and raw captures
are not added to it.

Sprint 3 introduces a separate `BrowserObservation` version `0.1`. After human
acceptance, only a narrow projection enters the context:

- one new `APPLICATION` evidence item,
- the existing target locator value changes to `OBSERVED`,
- its evidence references include the new observation evidence,
- `updated_at` changes to the review timestamp.

Process purpose, risk, role, preconditions, steps, expected outcomes, ownership,
and unrelated elements remain unchanged.

This preserves the distinction between an observation artefact and the current
accepted context state.
