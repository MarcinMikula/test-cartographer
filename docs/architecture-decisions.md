# Architecture decisions

Accepted implementation decisions for TestCartographer.

This file records the current decision and its consequences. Full chronological
reasoning remains in `LEARNINGS.md`.

## ADR-001 — Use a Python `src` layout

**Status:** Accepted in Sprint 1

### Decision

Use:

```text
src/test_cartographer/
```

for importable product code and keep tests outside the package.

### Rationale

- separates importable code from repository files,
- supports editable installation,
- reduces accidental imports from the working directory,
- aligns the repository with normal Python packaging,
- prepares later CLI or integration entry points without creating them now.

### Consequences

- development setup uses `python -m pip install -e ".[dev]"`,
- `pyproject.toml` is the project and test configuration source,
- no application package is placed at repository root.

## ADR-002 — Use Pydantic v2 for contract validation

**Status:** Accepted in Sprint 1

### Decision

Implement context contract version `0.1` as strict Pydantic models.

### Rationale

The first slice needs:

- deterministic runtime validation,
- nested typed models,
- explicit enum vocabularies,
- cross-field and cross-reference validation,
- readable JSON serialization,
- generated JSON Schema.

Hand-written dictionary validation would add contract code without improving
the product hypothesis.

### Consequences

- Pydantic is the only runtime dependency in Sprint 1,
- unknown fields are rejected,
- contract objects are frozen after validation,
- contract changes must update the generated schema and fixtures,
- Pydantic is an implementation detail; later LLM and browser layers depend on
  the provider-neutral contract, not Pydantic internals.

## ADR-003 — Persist the first contract as human-readable JSON

**Status:** Accepted in Sprint 1

### Decision

Use deterministic UTF-8 JSON files for the first local persisted context.

### Rationale

JSON provides:

- direct Pydantic serialization,
- JSON Schema compatibility,
- readable Git diffs,
- fixture simplicity,
- no database lifecycle before access patterns are known.

### Consequences

- one bundle can be reviewed and versioned as one file,
- no query optimization, concurrent editing, or relational integrity beyond
  bundle validation is provided,
- SQLite remains a later option when multiple processes, evidence history, or
  change queries create a demonstrated need.

## ADR-004 — Model one process per ContextBundle

**Status:** Accepted in Sprint 1

### Decision

Contract version `0.1` contains exactly one process.

### Rationale

One process is the smallest useful boundary that includes:

- purpose and risk,
- ordered interaction,
- pages and components,
- expected outcomes,
- test data,
- evidence,
- readiness.

A whole-application graph would add unresolved identity, lifecycle, and merge
problems before the first POM flow is proven.

### Consequences

- cross-process reuse and relationships are deferred,
- repeated components may temporarily appear in more than one bundle,
- later aggregation must preserve bundle provenance and versioning.

## ADR-005 — Separate structural validity from adaptation readiness

**Status:** Accepted in Sprint 1

### Decision

Use two deterministic stages:

```text
Pydantic contract validation
→ ContextReadinessReport
```

### Rationale

Incomplete and conflicting context is valuable information.

Rejecting it as malformed would encourage callers to:

- invent values,
- remove conflicts,
- omit questions,
- treat absence of evidence as parser failure.

### Consequences

- malformed references and impossible structures are rejected,
- explicit unknowns and unresolved conflicts may be stored,
- readiness blockers and warnings are inspectable and serializable,
- future interview and LLM workflows can target specific readiness issues.

## ADR-006 — Preserve knowledge authority with every important text value

**Status:** Accepted in Sprint 1

### Decision

Use `KnowledgeText` rather than plain strings for business, process,
application, element, locator, and test-data descriptions.

### Rationale

The project must distinguish:

- observation,
- supplied information,
- inference,
- confirmation,
- unknown information,
- stale information,
- conflicting evidence.

A separate generic notes field would not preserve that distinction at the
actual claim.

### Consequences

- JSON is more verbose,
- each value can retain evidence and sensitivity,
- the system can block unsupported certainty deterministically,
- future UI and LLM layers must deliberately create a status rather than write
  bare text.

## ADR-007 — Add `UNKNOWN` as an explicit knowledge status

**Status:** Accepted in Sprint 1

### Decision

Extend the Sprint 0 working vocabulary with `UNKNOWN`.

### Rationale

An open question identifies what should be asked, but the relevant field still
needs a machine-readable state showing that no value exists.

Using `null` without a status would not distinguish:

- unknown,
- conflicting,
- intentionally not applicable,
- omitted by mistake.

### Consequences

- unknown values must contain no selected value, evidence, or confidence,
- not-applicable semantics remain deferred and must not be represented as
  unknown if the distinction later becomes necessary.

## ADR-008 — Store symbolic test-data requirements, not real values

**Status:** Accepted in Sprint 1

### Decision

`TestDataRequirement` contains a symbolic reference and descriptive context.
UI actions reference the requirement by ID.

### Rationale

The context contract should describe what data is needed without becoming a
secret store or embedding environment-specific customer data.

### Consequences

- a future adapter must map requirements to fixtures, builders, configuration,
  or approved secret stores,
- Sprint 1 cannot execute the process,
- credentials and concrete business values remain outside the bundle.

## ADR-009 — Keep evidence metadata local and exclude raw source content

**Status:** Accepted in Sprint 1

### Decision

Evidence contains source metadata, summary, sensitivity, timestamp, and an
optional digest. It does not contain raw DOM, documents, screenshots, or
attachments.

### Rationale

The minimum contract needs provenance, not uncontrolled duplication of source
data.

### Consequences

- evidence references may not be independently replayable yet,
- future raw-evidence storage requires separate access, retention, and
  redaction rules,
- context JSON is less likely to leak secrets but is not automatically safe.

## ADR-010 — Commit and test generated JSON Schema

**Status:** Accepted in Sprint 1

### Decision

Commit `context-bundle-v0.1.schema.json` and verify it equals the schema emitted
by the Python model.

### Rationale

The contract will later be consumed by:

- review tools,
- browser collectors,
- LLM protocol builders,
- external fixtures,
- framework adapters.

A committed schema makes the boundary visible outside Python.

### Consequences

- schema drift fails tests,
- intentional model changes require schema regeneration,
- the schema is a technical representation, while this document remains the
  semantic explanation.

## Decisions deliberately deferred

- CLI framework,
- browser-capture library design,
- external LLM provider,
- prompt protocol,
- database,
- raw evidence store,
- cross-process graph,
- repository patching,
- POM proposal schema,
- CI workflow,
- logging framework.

These decisions should be introduced by the vertical slice that first needs
them.
