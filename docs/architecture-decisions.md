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

## ADR-011 — Use deterministic question selection before an LLM interviewer

**Status:** Accepted in Sprint 2

### Decision

Generate human-intake questions from explicit context state and ordered Python
rules.

Do not use an LLM to select the next question in the first workflow.

### Rationale

The project first needs to prove:

- which gaps are human-answerable,
- which question follows which context state,
- how answers change the contract,
- how unknown and skipped answers avoid loops,
- when intake is complete or blocked.

An LLM would make those transitions harder to attribute and test.

### Consequences

- the same context produces the same question order,
- question wording and target paths are version-controlled,
- browser-only blockers are filtered from human intake,
- an LLM may later assist wording or interpretation without owning durable
  state transitions.

## ADR-012 — Separate collection from explicit confirmation

**Status:** Accepted in Sprint 2

### Decision

A normal human answer becomes `PROVIDED`.

After required collection is complete, the workflow creates review questions
for business values still marked `PROVIDED` or `OBSERVED`.

Only an explicit confirmation changes the value to `CONFIRMED`.

### Rationale

Supplying a statement and accepting it as the current project basis are
different actions.

Collapsing them would make the review requirement cosmetic and would remove a
useful boundary for later human or domain-expert approval.

### Consequences

- the reference intake has collection and review phases,
- corrections made during review return to `PROVIDED`,
- skipped review may leave warnings,
- future role-based approval can replace the current single-user confirmation
  without changing the core distinction.

## ADR-013 — Persist a self-contained intake session

**Status:** Accepted in Sprint 2

### Decision

Persist `IntakeSession` version `0.1` as deterministic JSON containing:

- the current `ContextBundle`,
- session state,
- interaction history,
- deferred question IDs,
- timestamps.

### Rationale

A resumable workflow must not depend on the original context file remaining
unchanged while the session is active.

Embedding the context also makes one file sufficient for status, resume, and
export operations.

### Consequences

- session files are larger than storing only a pointer,
- concurrent edits and merge semantics are not supported,
- sessions can be reviewed and archived independently,
- the generated session JSON Schema is committed and tested.

## ADR-014 — Record effort metrics without duplicating answer text

**Status:** Accepted in Sprint 2

### Decision

Store interaction metadata and active response duration, but do not copy normal
field answers into the interaction log.

The answer remains in `ContextBundle`; the interaction stores:

- question and target,
- answer action,
- asked and answered timestamps,
- active seconds.

### Rationale

The project needs early evidence about operator effort without multiplying
potentially sensitive content across session structures.

### Consequences

- question, action, and duration metrics are available,
- field values remain centralized in the context,
- generic open-question answers are retained in evidence summaries because
  contract version `0.1` has no separate answer field,
- subjective usability still requires a later evaluation instrument.

## ADR-015 — Use the Python standard library for the first CLI

**Status:** Accepted in Sprint 2

### Decision

Implement the first command-line interface with `argparse`, standard input, and
standard output.

### Rationale

The Sprint 2 hypothesis concerns intake state and question transitions, not a
terminal UI framework.

A third-party CLI or rich rendering dependency would not improve the evidence
needed from this slice.

### Consequences

- the CLI is intentionally plain,
- commands remain scriptable and integration-testable,
- a richer local UI may be introduced only after the workflow proves useful.

## Decisions deliberately deferred

- browser-capture library design,
- external LLM provider,
- prompt and response protocol,
- database,
- raw evidence store,
- cross-process graph,
- repository patching,
- POM proposal schema,
- project/workspace profile schema,
- authentication profile and secret-provider adapters,
- execution-evidence contract,
- reactive and proactive maintenance implementation,
- CI workflow,
- logging framework,
- rich terminal or web review interface,
- multi-user approval and identity model,
- context-shell creation from scratch.

These decisions should be introduced by the vertical slice that first needs
them.

## ADR-016 — Keep browser observation separate from ContextBundle

**Status:** Accepted in Sprint 3

### Decision

Persist browser capture and review in a separate `BrowserObservation` contract.
Apply only an accepted, minimal evidence projection to `ContextBundle`.

### Consequences

- pending and rejected captures do not pollute accepted context,
- raw Playwright objects never enter the provider-neutral model,
- observation replay and context evolution can be tested separately.

## ADR-017 — Verify one existing target instead of scanning a page

**Status:** Accepted in Sprint 3

### Decision

The first browser command requires one user-authorized URL and one existing
context element ID. It verifies that element's existing primary locator.

### Consequences

- the slice proves acquisition without pretending to solve discovery,
- page/component ownership remains unchanged,
- locator generation and arbitrary target selection remain future work.

## ADR-018 — Persist an allowlisted target snapshot only

**Status:** Accepted in Sprint 3

### Decision

Persist tag name, visibility, enabled/editable state, and only `id`, `role`,
`aria-label`, `name`, `placeholder`, `type`, and `data-testid` when present.
Explicitly exclude values, text, HTML, screenshots, and whole-page data.

### Consequences

- capture is reviewable and materially smaller than DOM dumping,
- the contract cannot reconstruct the page,
- allowlisted values still require sensitivity handling.

## ADR-019 — Human acceptance is required before OBSERVED

**Status:** Accepted in Sprint 3

### Decision

A successful locator match creates a pending observation. Only a later explicit
acceptance may append evidence and change the locator status to `OBSERVED`.

### Consequences

- browser execution and accepted meaning remain separate,
- rejection is auditable and leaves context unchanged,
- automated capture cannot silently claim authority.

## ADR-020 — Use direct Playwright library integration

**Status:** Accepted in Sprint 3

### Decision

Use the Playwright Python sync API directly as an optional dependency. Do not
introduce pytest-playwright into product code.

### Consequences

- CLI and verification scripts own browser lifecycle explicitly,
- unit tests can use protocol-compatible fakes,
- one integration test and verifier exercise Chromium,
- other browsers remain unsupported.

## ADR-021 — Treat the framework and Cartographer as two modules of one lifecycle

**Status:** Accepted at Architecture checkpoint A

### Decision

Treat `qa-automation-framework` and TestCartographer as separately executable
modules of one automation lifecycle.

- The framework owns accepted automation and normal execution.
- TestCartographer owns context acquisition, LLM-assisted adaptation,
  maintenance, and expansion.

### Rationale

The target is not a standalone locator database beside an unrelated framework.
The framework provides the execution architecture; Cartographer supplies and
maintains the project-specific knowledge and changes required to use it.

At the same time, coupling every test run to Cartographer or an LLM would make
execution slower, less deterministic, and operationally fragile.

### Consequences

- ordinary pytest execution remains independent of Cartographer and a live LLM,
- lifecycle integration happens through explicit profiles, repository changes,
  and evidence contracts,
- future roadmap work must cover creation, execution evidence, maintenance, and
  expansion rather than only initial code generation.

## ADR-022 — Use a shared project profile instead of fixture coupling

**Status:** Direction accepted; contract deferred

### Decision

Introduce a future non-secret project/workspace profile that maps logical
Cartographer concepts to framework mechanisms.

TestCartographer must not import or execute pytest fixtures merely to obtain
configuration, test data, or an authenticated browser session.

Both modules should instead interpret lower-level project concepts such as:

- `EnvironmentProfile`,
- `AuthProfile`,
- secret-provider references,
- framework target mappings,
- context and evidence locations.

### Rationale

Fixtures are execution-plane implementation details. Direct fixture coupling
would make Cartographer depend on pytest lifecycle and project-specific code,
while duplicated configuration would drift.

### Consequences

- one concrete automation repository becomes the shared workspace,
- framework fixtures and Cartographer sessions may consume the same logical
  profile through separate adapters,
- the profile stores secret references and mappings, not secret values,
- the exact schema and repository layout remain a Sprint 5 or later decision.

## ADR-023 — Keep one approved secret source with two runtime consumers

**Status:** Principle accepted; implementation deferred

### Decision

The framework and TestCartographer may need the same environment and account,
but secret values must not be copied into separate configurations.

Use one approved secret source with two consumers:

```text
secret store / environment / enterprise manager
├── framework runtime adapter
└── TestCartographer runtime adapter
```

### Rationale

Credential duplication increases leakage, rotation, and consistency risk.
Cartographer still needs authenticated access for systems such as Salesforce,
but `ContextBundle`, observations, prompts, generated documentation, and source
control are not appropriate secret stores.

### Consequences

- project files contain logical secret references only,
- secrets should be resolved in memory for the shortest practical time,
- authenticated Playwright storage state is treated as sensitive,
- three implementation strategies remain parked: shared storage state,
  declarative login recipe, and interactive login.

## ADR-024 — Separate reactive and proactive maintenance

**Status:** Accepted as product direction; implementation deferred

### Decision

Model maintenance as two separate lifecycle modes.

1. **Reactive maintenance** begins with a failed execution or explicit drift
   signal.
2. **Proactive maintenance** performs bounded scheduled or post-deployment
   re-observation of an approved inventory, even when tests remain green.

### Rationale

A test suite observes only the paths it executes. Shared components, mapped but
unused elements, future automation targets, or untested application areas can
change without failing the current pool.

### Consequences

- the roadmap includes both execution-evidence analysis and proactive
  frontend/context regression,
- proactive runs require approved scope, actions, budgets, authentication, and
  sensitivity policy,
- neither mode authorizes unrestricted crawling or silent repair.

## ADR-025 — Collect execution evidence in the framework, analyse it in Cartographer

**Status:** Accepted as product direction; implementation deferred

### Decision

Place future bounded execution-evidence collection in the
`qa-automation-framework` execution plane. TestCartographer consumes that
evidence for diagnosis, context evolution, impact analysis, and patch
proposals.

Use the broader term **Execution Evidence Collector** rather than assuming each
failed test is an application bug.

### Rationale

The framework knows the executed test, fixture, Page Object, method, action,
locator, environment, and exception at failure time. Cartographer owns the
application map and maintenance reasoning. Keeping those responsibilities
separate preserves normal execution independence while providing valuable
maintenance input.

### Consequences

- a future cross-repository evidence contract is required,
- failure evidence must distinguish application, automation, data, environment,
  and stale-context possibilities,
- screenshots, traces, network references, and page state remain policy-bound,
- the collector does not itself decide or apply repairs.

## ADR-026 — Treat expansion as reuse validation, not another greenfield demo

**Status:** Accepted as product direction; implementation deferred

### Decision

After the first complete process, validate a second process using the existing
application map, accepted automation, project profiles, and prior decisions.

### Rationale

The product's long-term value depends on reducing repeated work. A tool that is
useful only for the first process but cannot reuse knowledge is a generator,
not a maintained application map.

### Consequences

- expansion receives its own roadmap slice,
- validation should measure repeated questions, observations, LLM input,
  duplicate artefacts, and review time,
- stale knowledge must not be reused as automatic truth.

## ADR-027 — Project ready context into a bounded synthesis request

**Status:** Accepted and implemented in Sprint 4

### Decision

A live or replay synthesis adapter may receive only
`BoundedSynthesisRequest` version `0.1`.

Do not pass an arbitrary `ContextBundle`, browser object, page capture, session,
repository, or conversation history to the adapter.

The request builder:

- requires full adaptation readiness,
- includes only `CONFIRMED` and `OBSERVED` values,
- allows `PUBLIC` and `INTERNAL` sensitivity by default,
- fails on disallowed required values,
- includes minimized evidence summaries,
- records excluded paths and reasons,
- records prohibited claims.

### Rationale

External-model authority should be explicit and testable. Passing a broad local
model and relying on prompt instructions to ignore sensitive or irrelevant
fields would make the effective data boundary hidden and provider-dependent.

### Consequences

- `application.base_url`, page routes, raw source references, hashes,
  timestamps, notes, browser state, and repository files remain outside Sprint
  4 requests,
- local readiness and external authorization remain separate gates,
- later enterprise profiles may define a different approved sensitivity set,
  but must do so explicitly,
- a missing authorized value blocks the request rather than encouraging model
  invention.

## ADR-028 — Preserve exact raw output and separate protocol failure

**Status:** Accepted and implemented in Sprint 4

### Decision

Store the exact adapter output in `SynthesisRun.raw_output` without trimming or
normalization.

Treat empty output, Markdown fences, non-object roots, invalid JSON, duplicate
keys, schema drift, missing fields, and unexpected fields as protocol failures.

### Rationale

Provider reliability, parser behaviour, replay, debugging, and future audits
require the original output. Normalizing it would destroy evidence about what
the adapter actually returned.

Malformed output is operationally different from a well-formed proposal that
violates project constraints.

### Consequences

- `SynthesisRun` overrides the shared string-stripping configuration,
- nested structured models retain normal trimming and validation,
- protocol errors contain a parse-failure code and no parsed proposal,
- raw output is preserved on both success and failure,
- retry or provider policy can later distinguish malformed-output handling from
  proposal-quality handling.

## ADR-029 — Validate proposal authority deterministically before human review

**Status:** Accepted and implemented in Sprint 4

### Decision

A parsed `PomProposal` must pass deterministic validation against the exact
`BoundedSynthesisRequest` before it can reach human review.

The validator checks:

- request and context identity,
- authorized page and component coverage,
- method ownership,
- exactly-once process-step coverage,
- action, element, locator, and symbolic-data consistency,
- fixture role/environment mapping and absence of secret values,
- test references and confirmed-outcome coverage,
- prohibited claim flags,
- open-question references.

### Rationale

Human review should focus on architectural judgement rather than discover
simple referential errors, omitted steps, invented locators, or explicit
overreach that software can reject reliably.

### Consequences

- structurally valid but unacceptable proposals become
  `VALIDATION_REJECTED`,
- protocol and validation failure remain separate,
- only `READY_FOR_REVIEW` runs can be accepted or rejected,
- deterministic validation does not claim semantic elegance or business
  correctness,
- non-blocking questions may remain warnings for review.

## ADR-030 — Use replay before live providers and keep Sprint 4 read-only

**Status:** Accepted and implemented in Sprint 4

### Decision

Implement and validate the synthesis pipeline with
`ReplaySynthesisAdapter` before adding a live provider.

Sprint 4 produces a logical POM proposal only. It does not inspect, write, or
patch `qa-automation-framework`.

### Rationale

A live model would combine several uncertainties:

- request design,
- prompt rendering,
- provider behaviour,
- parser reliability,
- proposal validation,
- repository mapping.

Replay isolates the local protocol and makes malformed, overreaching, and valid
outputs deterministic.

Repository file placement requires knowledge of the actual target workspace and
must not be inferred from the logical proposal alone.

### Consequences

- Sprint 4 makes no provider-quality claim,
- provider adapters remain a future integration behind the same contract,
- an accepted proposal means only that logical boundaries may proceed to
  framework inspection,
- Sprint 5 must create a separate repository adaptation plan and review gate,
- normal framework execution remains independent of the synthesis adapter.


## ADR-031 — Inspect framework workspaces through an explicit allowlist

**Decision:** `WorkspaceProfile` defines root markers, allowed repository roots,
ignored names, and file-count/file-size budgets. The local absolute path is an
invocation parameter and is not persisted.

**Why:** Repository awareness is required for adaptation, but unconstrained
recursive ingestion would expand privacy, performance, and prompt-injection
risk before the project has evidence that it is useful.

**Consequence:** The first inspector can miss relevant files outside the
allowlist. That is preferable to silently scanning an entire enterprise
repository.

## ADR-032 — Persist repository structure, not source contents

**Decision:** `FrameworkSnapshot` stores repository-relative paths, sizes,
SHA-256 hashes, and top-level Python symbol metadata. It does not store source
text, absolute paths, or secret values.

**Why:** Sprint 5 needs duplicate detection, target selection, replay, and stale
snapshot detection. It does not need to preserve full source code in the
Cartographer contract.

**Consequence:** A later source-generation slice will need a separate bounded
read mechanism tied to exact approved files. The snapshot alone cannot explain
all runtime behaviour.

## ADR-033 — Separate logical proposal acceptance from repository-plan acceptance

**Decision:** An accepted Sprint 4 `SynthesisRun` may produce only a pending
`AdaptationPlan`. A second human decision is required for exact file and symbol
targets.

**Why:** A logical Page Object boundary can be reasonable while its file name,
fixture location, or relationship to existing symbols is wrong.

**Consequence:** Human review remains explicit at both authority boundaries.
Plan acceptance still does not authorize source writes.

## ADR-034 — Keep Sprint 5 read-only and source-free

**Decision:** Sprint 5 may classify operations as `create_file`, `add_symbol`,
or `reuse_symbol`, but may not include generated Python source or modify the
framework.

**Why:** Repository inspection, placement, source generation, patching, and
execution are separate uncertainties. Combining them would make failures hard
to attribute and review.

**Consequence:** Sprint 6 must verify that an accepted plan still matches the
same snapshot fingerprint before proposing or applying source changes.
