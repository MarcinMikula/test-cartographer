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

**Status:** Accepted and implemented for the bounded Sprint 7 reference contract

### Decision

Place bounded execution-evidence collection in the
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

- Sprint 7 provides a standalone pytest collector and provider-neutral JSON
  contract without importing TestCartographer,
- persisted outcomes distinguish pass, call-phase failure, and infrastructure
  error but do not claim root cause,
- failure records use safe summaries, relative locations, and redacted hashes
  rather than raw exception messages or tracebacks,
- screenshots, traces, network references, page state, and captured output
  remain outside the default contract,
- deterministic readiness can reject incomplete traceability or missing step
  context before Sprint 8 analysis,
- the collector does not decide or apply repairs.

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


## ADR-035 — Separate source acceptance from proposal and placement acceptance

**Decision:** Exact generated source is persisted as a `CodePatch` and requires
its own explicit human decision. Sprint 4 proposal acceptance and Sprint 5
placement acceptance do not authorize a write.

**Why:** Logical correctness, repository placement, and exact implementation can
fail independently and require different review evidence.

**Consequence:** There are three review gates before controlled application.

## ADR-036 — Revalidate framework state before generation and application

**Decision:** Generation rescans the framework and requires the accepted snapshot
fingerprint. Application repeats fingerprint and target-hash preflight.

**Why:** A reviewed plan or patch becomes unsafe when the repository changes.

**Consequence:** Drift blocks silent reuse and requires re-inspection or explicit
reconciliation.

## ADR-037 — Apply the first patch to a clean copy, not the original repository

**Decision:** Sprint 6 applies source only to a controlled copy. The setup script
proves that the original framework Git status remains unchanged.

**Why:** The first creation proof should establish source quality and execution
before granting authority over user-maintained code.

**Consequence:** Direct original-repository patching remains a future boundary.

## ADR-038 — Keep runtime configuration out of generated source

**Decision:** The generated fixture reads the application URL from a named
environment variable. Symbolic test data must be explicitly bound through a
non-secret generation profile.

**Why:** A runnable example must not turn context or source artefacts into a
secret store.

**Consequence:** Missing runtime configuration fails visibly; no URL, username,
or password is embedded in the patch.

## ADR-039 — Require independent framework execution as creation evidence

**Decision:** The generated test must compile, be collected, and execute using
the framework without importing TestCartographer and without a live LLM call.

**Why:** Cartographer is an engineering module, not a runtime dependency for
normal test execution.

**Consequence:** Sprint 6 can claim a working creation prototype, not merely
valid generated Python.

## ADR-040 — Declare and validate generation-template framework prerequisites

**Decision:** `GenerationProfile` declares exact framework paths, symbols, and
symbol kinds required by its deterministic templates. The local snapshot is
validated before plan review and again before patch generation.

**Why:** Repository placement evidence does not prove that imported base
abstractions exist. A real acceptance run produced valid Python text with an
unresolvable `BaseComponent` import because this dependency was implicit.

**Consequence:** Incompatible or stale framework checkouts fail early with a
precise contract error. Automatic negotiation of alternative base abstractions
remains future scope.


## ADR-041 — Classify execution evidence by pytest phase, not assumed root cause

**Status:** Accepted and implemented in Sprint 7

### Decision

Persist `test_failure` only for a failed pytest call phase and
`infrastructure_error` for collection, setup, or teardown failures. Do not
serialize `application_bug`, `automation_bug`, or similar root-cause labels in
version `0.1`.

### Rationale

The execution framework knows which pytest phase failed. It usually does not
know why. Treating an assertion or Playwright exception as proof of an
application defect would recreate the false-certainty problem that the project
explicitly avoids in LLM judging and context modelling.

### Consequences

- classification is deterministic and replayable,
- infrastructure failures are not mixed with call-phase failures,
- Sprint 8 must support uncertainty and human review,
- a failed test remains a diagnostic signal rather than a bug record.

## ADR-042 — Persist redacted hashes and structural context instead of raw failure text

**Status:** Accepted and implemented in Sprint 7

### Decision

Store exception type, safe phase summary, relative location, bounded step
metadata, and SHA-256 of redacted bounded text. Do not persist raw exception
messages, raw tracebacks, stdout, stderr, input values, HTML, screenshots, or
traces in the default execution-evidence contract.

### Rationale

Assertion messages, Playwright traces, screenshots, and captured output can
contain credentials, personal data, business data, URLs, and NDA-protected
application content. Their diagnostic value does not make them safe by
default.

### Consequences

- the default bundle is smaller and safer to retain,
- equality and replay checks remain possible through redacted hashes,
- some diagnoses will require a separately reviewed artefact policy,
- the contract cannot silently expand by adding arbitrary raw strings.


## ADR-021 — Use a local LLM as an interview planner, not a fact authority

**Status:** Accepted for Sprint 8.

### Decision

The first live provider is a loopback-only Ollama adapter. It receives an
allowlisted deterministic question set and may only order and rephrase those
questions. Human answers continue through the existing intake evidence and
confirmation transitions.

### Rationale

A free-form agent that can create fields or fill answers would combine model
fluency with factual authority before the project has evidence that the model is
competent or the input is safe. Restricting the model to conversational planning
gives immediate usability value while preserving deterministic coverage and
human ownership.

### Consequences

- the LLM cannot omit, duplicate, or invent question IDs,
- the starting URL is never included in model input,
- raw prompts and responses are not persisted,
- a replay provider remains mandatory for deterministic tests,
- live acceptance requires an installed local model,
- guided-discovery readiness remains separate from adaptation readiness.

## ADR-022 — Make creation-demo readiness precede maintenance implementation

**Status:** Accepted after Sprint 7.

The product sequence is Sprint 8 live intake, Sprint 9 guided process discovery,
Sprint 10 fixture-assisted integrated Creation Flow, and Sprint 11
human-triggered interactive Creation Flow. Reactive and proactive maintenance
remain planned but move behind this block. The reason is product validation: the
central promise is reducing expensive context discovery and creation work, so
the first external demonstration must include a real operator trigger before the
project expands its maintenance surface.

## ADR — Browser ranking, LLM phrasing, and human selection are separate authorities

**Status:** Accepted in Sprint 9

For multi-element discovery, Playwright collects bounded facts and deterministic
code ranks candidates. When the leading candidates are too close, the local LLM
may phrase one question over the immutable candidate set. Only a human may
select the intended candidate, and a separate human decision accepts the final
discovery.

This prevents three unsafe shortcuts:

- treating a unique locator as proof of process meaning,
- allowing an LLM to select a DOM element from a verbal description,
- applying browser findings to context without review.

## AD-S10-1 — keep synthesis authority strict during Creation Flow

**Decision:** Add a separate human synthesis-handoff confirmation for remaining
`PROVIDED` synthesis-required values instead of allowing the orchestrator to weaken or
bypass the synthesis request contract.

**Reason:** Module-local readiness and downstream provider authority are
separate concerns. Silent status promotion would destroy provenance.

## AD-S10-2 — label deterministic and live intelligence separately

**Decision:** The Creation Flow records three live local-LLM calls and one
separate deterministic synthesis-template call.

**Reason:** Integration-proof credibility depends on distinguishing measured
model activity from deterministic templates and replayable fixtures.


## AD-S10-3 — separate engine verification from user-demo readiness

**Decision:** A fixture-assisted Creation Flow may prove the complete engine but
may not set external user-demo readiness to true. The deterministic assessment
reports three separate states:

- creation mechanics verified,
- ready for human-trigger integration,
- ready for external user demonstration.

**Reason:** Fixtures are valid for repeatable integration testing, but they do
not prove that a real operator can start the flow, understand the questions,
resolve ambiguity, or review artefacts. Sprint 11 must connect the human to the
existing entry and decision points instead of rebuilding the engine.


## AD-S11-1 — connect the operator without rebuilding the engine

**Decision:** Sprint 11 wraps the accepted Sprint 10 engine with blocking CLI
prompts, a headed browser review, and an operator-action ledger. It does not
create a second creation pipeline.

**Reason:** The missing product evidence was human participation, not another
generation mechanism. Reusing the existing contracts keeps fixture-assisted and
interactive runs comparable.

## AD-S11-2 — separate scripted prompt coverage from manual acceptance

**Decision:** Automated tests may use scripted input to cover all prompt paths,
but only a completed live `InteractiveOperatorSession` with
`fixture_answers_used=false` and `headed_browser_used=true` satisfies the
external-demo readiness gate.

**Reason:** Automated input is valuable regression evidence but cannot prove
that a real operator saw, understood, and answered the interface.

## AD-S11-3 — audit operator actions without duplicating raw context

**Decision:** The operator ledger records action kind, target, decision category,
timestamps, and active duration. Raw answer values remain in the existing local
intake/context artefacts and are not copied into the ledger.

**Reason:** The product needs evidence that human authority was exercised without
creating another sensitive-data store.

## AD-S11-4 — headed browser is mandatory for the controlled demo gate

**Decision:** The interactive reference profile requires headed Chromium and
keeps candidate labels visible during ambiguity selection and discovery review.

**Reason:** A terminal-only candidate ID is insufficient evidence that the
operator could inspect the application state behind the decision.

## AD-S11-5 — separate bootstrap, process context, and runtime authority questions

**Decision:** The interactive Creation Flow classifies questions into three
scopes:

1. bootstrap context required to start the run,
2. process-specific context required for the selected scenario,
3. runtime ambiguity or review questions justified by an unresolved authority
   boundary.

Confirmed values must be consumed by later modules rather than asked again only
because the pipeline advanced. Sprint 11 replaces five individual process-review
prompts with one aggregate summary. One operator confirmation authorizes the
five deterministic `CONFIRM` transitions required by the existing context
contract.

**Reason:** Internal state transitions are not automatically separate user
interactions. Repeating known facts increases cognitive load and creates the
appearance that modules do not share context.

**Consequence:** The interactive reference run uses one LLM collection-planning
turn instead of separate collection and review turns. The expected operator
action count falls from 22 to 18 without weakening evidence, provenance, or
human authority.

## AD-S11-6 — control commands cannot be accepted as context values

**Decision:** Aggregate review uses full-word `CONFIRM`, `EDIT`, `QUIT`, and
`CANCEL` commands. Exact control tokens, including their former single-letter
forms, are rejected when a context value is expected.

**Reason:** The first manual run demonstrated that `E` followed by `C` could
store `C` as a replacement business value. A command grammar must not overlap
silently with the value grammar.

## AD-S11-7 — persistent bootstrap reuse is a separate future contract

**Decision:** Sprint 11 guarantees that bootstrap values are asked once within a
single Creation Flow and reused by later stages. Reuse across separate runs is
parked until a project-profile contract defines ownership, explicit edits,
staleness, conflict, environment changes, framework/provider/model changes, and
authentication changes.

**Reason:** Reusing configuration can reduce repeated questioning, but stale
bootstrap data can make discovery and generated tests wrong with high
confidence. Persistence therefore needs invalidation semantics, not only a cache.

### ADR: exact acceptance requires full source visibility

**Decision:** a source patch may be described as `exact` only when every source
line in every change is rendered to the operator before the decision. A six-
line preview plus ellipsis can support preview approval, not exact acceptance.

For the already completed Sprint 11 intake, correction is performed by a
separate patch re-review over persisted accepted artefacts. This avoids
repeating context collection or local-model calls while preserving a real human
authority boundary. The corrected patch is applied only to a new sandbox and is
executed again.


## AD-S12-1 — failed-test evidence grants re-observation, not diagnosis

**Decision:** A traced call-phase failure may authorize only bounded current-page
re-observation. It may not by itself create a stale-locator verdict, an
application-bug claim, or a source patch.

**Reason:** Pytest reports where execution failed, not why the system is wrong.
Keeping evidence assessment separate from diagnosis prevents false certainty and
preserves infrastructure, data, environment, application, and automation causes.

## AD-S12-2 — repair candidacy requires current evidence and human selection

**Decision:** Sprint 12 creates `repair_candidate` only after headed re-observation
shows that the old locator is absent and the operator selects one current unique
candidate with the expected role and name.

**Reason:** A unique DOM match is not proof of process meaning. Browser facts and
human intent are separate authorities.

## AD-S12-3 — begin maintenance without an LLM

**Decision:** Evidence assessment, candidate filtering, one-occurrence locator
replacement, and verification are deterministic. Sprint 12 uses no LLM.

**Reason:** The first maintenance slice should establish whether evidence and
current-page observation are sufficient for one narrow repair before expanding
model authority into root-cause analysis or source generation.

## AD-S12-4 — accepted maintenance patches remain sandbox-only

**Decision:** The exact full source and before/after hashes are shown to the
operator, but acceptance permits application only to a fresh snapshot-bounded
sandbox. The original framework target hash and repository fingerprint must stay
unchanged.

**Reason:** Fail-before/pass-after is useful repair evidence without yet granting
TestCartographer production-repository write authority.

## Sprint 13 decisions — proactive regression remains review-only

1. A green current test suite is not evidence that every approved mapped
   frontend element remains current.
2. Proactive regression starts from an explicit, human-accepted observation
   inventory; it does not crawl or silently widen scope.
3. The first slice is human-triggered post-deployment observation, not a
   scheduler or CI webhook integration.
4. Public no-auth pages are the only supported authentication boundary in
   Sprint 13; enterprise profiles remain parked.
5. Locator drift on an uncovered mapped element is classified as stale map
   context, not as a failed test or an application defect.
6. The report is review-only: no context write, code patch, or PhoenixQA
   recovery is triggered automatically.
7. The reference framework test must remain independently green on both
   baseline and deployed pages to prove the distinct value of proactive
   observation.
8. Ollama and every other LLM provider remain outside this deterministic
   slice; model choice is not a product constraint.
