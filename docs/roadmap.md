# Roadmap

## Roadmap rule

TestCartographer is developed through evidence-producing vertical slices.

In this roadmap, **Sprint** means a named, closed delivery increment rather than
a fixed Scrum timebox. The project is currently developed in a small
research/engineering workflow, so scope evidence and exit criteria define the
boundary more strongly than calendar duration.

A sprint is complete only when it produces one or more of:

- a working end-to-end capability,
- a controlled experiment,
- a validated contract,
- a documented decision based on evidence,
- an explicit scope boundary.

Creating folders, interfaces, or agent classes without exercising a useful
workflow is not sufficient.

The roadmap becomes less specific with distance. Sprints beyond the next one
are provisional or parked and must be reshaped using findings from earlier
work.

## System direction

`qa-automation-framework` and TestCartographer are separately executable modules
of one automation lifecycle.

```text
TestCartographer
→ context, discovery, LLM-assisted adaptation, maintenance, expansion

qa-automation-framework
→ accepted POM/fixtures/tests, configuration, execution, assertions, evidence
```

Normal test execution must remain independent of TestCartographer and a live
LLM. Creation, maintenance, and expansion may invoke TestCartographer and a
bounded LLM under human review.

See [`system-lifecycle.md`](system-lifecycle.md).

## Delivery stages

```text
product framing
→ context contract
→ human intake
→ guided browser observation
→ lifecycle alignment checkpoint
→ bounded LLM synthesis
→ framework workspace and handoff
→ first runnable test
→ creation-lifecycle evaluation
→ execution evidence
→ live LLM-guided intake from minimal context
→ guided multi-element process discovery
→ fixture-assisted integrated Creation Flow
→ human-triggered interactive Creation Flow
→ reactive maintenance
→ proactive frontend/context regression
→ expansion using the existing map
→ Checkpoint 14.5 documentation truth and roadmap reset
→ persistent ProjectProfile and bootstrap reuse
→ external-validation protocol
→ external public validation with increasing difficulty and decreasing control
→ credentialed validation and minimum authentication profiles
→ enterprise/Salesforce validation
→ comparative usability/economics
→ v1.0 decision
```

## Sprint overview

| Sprint or checkpoint | Focus | Status |
|---|---|---|
| Sprint 0 | Product framing and project boundaries | Done |
| Sprint 1 | Minimum context contract and local evidence model | Done |
| Sprint 2 | Deterministic human-guided process intake | Done |
| Sprint 3 | Bounded guided browser observation | Done |
| Architecture checkpoint A | Align the two-module lifecycle, maintenance modes, authentication directions, and enterprise validation target | Done in documentation |
| Sprint 4 | Bounded LLM synthesis and POM proposal | Done |
| Sprint 5 | Project workspace, framework mapping, and first reviewable adaptation plan | Done |
| Sprint 6 | First runnable framework test and creation-lifecycle evaluation | Done |
| Sprint 7 | Framework execution-evidence contract | Done |
| Sprint 8 | Live local-LLM guided intake from minimal context | Done |
| Sprint 9 | Guided multi-element process discovery | Done |
| Sprint 10 | Fixture-assisted integrated Creation Flow and effort summary | Done |
| Sprint 11 | Human-triggered interactive Creation Flow | Done |
| Sprint 12 | Human-triggered reactive maintenance from bounded execution evidence | Done — real operator acceptance verified |
| Sprint 13 | Proactive post-deployment frontend/context regression | Done — real operator acceptance verified |
| Sprint 14 | Expansion using the existing application map | Done — real operator acceptance verified |
| Checkpoint 14.5 | Documentation truth cleanup and validation-first roadmap reset | Done in documentation |
| Sprint 15 | Persistent ProjectProfile and bootstrap reuse/invalidation | Done — real operator acceptance verified |
| Sprint 16 | External-validation protocol and repeatable evidence package | Done — controlled real-operator rehearsal verified |
| Sprint 17 | External validation I — simple and dynamic public applications | Planned |
| Sprint 18 | External validation II — multi-page and difficult low-control public applications | Provisional |
| Sprint 19 | Authentication profiles and credentialed validation | Provisional |
| Sprint 20 | Enterprise/Salesforce validation | Provisional |
| Sprint 21 | Comparative usability/economics and v1.0 decision | Provisional |

## Sprint 0 — Product framing

**Status:** Done

### Goal

Turn an initial UI-explorer idea into a bounded product direction before
creating source-code architecture.

### Delivered

- product name and repository framing,
- problem statement,
- relationship with `qa-automation-framework`,
- intended user,
- initial UI/POM boundary,
- multi-source context model,
- evidence and provenance requirement,
- security and privacy boundary,
- usability and operation-time validation requirement,
- first vertical-slice direction,
- explicit non-goals and parked ideas.

### What Sprint 0 proves

The project has a coherent problem statement, scope, development discipline,
and validation direction.

### What Sprint 0 does not prove

Technical feasibility, context quality, LLM value, browser feasibility,
security, usability, or product value.

## Sprint 1 — Minimum context contract

**Status:** Done

### Goal

Define and validate the smallest local, provider-neutral contract that can
represent one useful UI process without pretending unknown information is
known.

### Delivered

- Python `src` package layout,
- strict Pydantic `ContextBundle` version `0.1`,
- one process with application, pages, components, elements, locators, steps,
  outcomes, symbolic data, evidence, questions, and conflicts,
- knowledge authority and sensitivity metadata,
- graph-integrity validation,
- deterministic JSON load/save,
- adaptation-readiness report,
- generated and tested context JSON Schema,
- valid, incomplete, conflicting, and invalid fixtures,
- 23 deterministic tests at Sprint 1 completion.

### Exit criteria

- [x] One complete reference process can be represented.
- [x] Missing information remains explicit.
- [x] Inference is structurally distinguishable from confirmed fact.
- [x] Conflicting evidence can remain valid without silent resolution.
- [x] Invalid references and structures are rejected.
- [x] The representation is human-reviewable JSON.
- [x] No browser or provider dependency is required.
- [x] Readiness identifies what human and later browser stages must resolve.

### What Sprint 1 proves

One bounded UI process can be stored, validated, and assessed without
collapsing uncertainty into parser failure or invented certainty.

### What Sprint 1 does not prove

That a user can fill the model efficiently, that browser evidence can populate
it, or that it is sufficient for POM generation.

## Sprint 2 — Deterministic human-guided intake

**Status:** Done

### Goal

Collect and review the human-answerable process context from a structurally
valid incomplete bundle without requiring manual JSON editing or a free-form
LLM interviewer.

### Delivered

- stage-specific `assess_intake()` report,
- deterministic collection question queue,
- review queue for `PROVIDED` and `OBSERVED` business values,
- answer actions for provide, confirm, unknown, and skip,
- explicit collection-to-review transition,
- human evidence creation with source, timestamp, sensitivity, and digest,
- self-contained `IntakeSession` version `0.1`,
- active, paused, complete, and blocked session states,
- save after every accepted interaction,
- deferred-question retry,
- interaction count and active-answer-time metrics,
- standard-library CLI for start, run, status, and export,
- generated and tested intake-session JSON Schema,
- `.gitattributes` line-ending policy,
- 47 deterministic tests across context, intake, persistence, schema, and CLI.

### Reference flow

```text
load incomplete public-search context
→ ask business risk
→ ask observable outcome
→ ask stored matching-rule question
→ review risk
→ review outcome
→ human intake complete
```

Expected final state:

```text
human-intake blockers = 0
human-intake warnings = 0
full adaptation blockers = 1
```

The remaining blocker is an intentionally inferred primary locator.

### Exit criteria

- [x] Questions are derived from current context state.
- [x] Browser-only issues are excluded from human intake.
- [x] Normal answers become `PROVIDED` evidence.
- [x] Explicit review changes values to `CONFIRMED`.
- [x] Unknown and skipped answers do not create infinite loops.
- [x] A required deferred answer can produce a visible `BLOCKED` state.
- [x] Sessions can be paused, saved, resumed, and retried.
- [x] Interaction count and active answer time are measured.
- [x] Current context can be exported independently.
- [x] No live LLM or browser is required.
- [x] Full adaptation readiness remains separate from intake completion.

### What Sprint 2 proves

A strict context model can drive a deterministic, resumable, reviewable, and
measurable human-intake workflow.

### What Sprint 2 does not prove

- greenfield creation of the context shell,
- usability with a real tester and real application,
- automatic semantic interpretation of long answers,
- rich mapping of arbitrary open-question answers,
- browser capture,
- locator correctness,
- LLM synthesis,
- framework adaptation,
- time savings or easier operation than alternatives.

## Sprint 3 — Bounded guided browser observation

**Status:** Done

### Goal

Add one small, reviewable application-evidence boundary to an existing
human-reviewed process without whole-page capture, autonomous navigation, or an
LLM.

### Delivered

- Playwright as an optional browser dependency,
- controlled local catalog reference page,
- strict `BrowserObservation` schema version `0.1`,
- one user-authorized URL, element ID, and existing primary locator per capture,
- deterministic mapping for role, label, test ID, placeholder, text, CSS, and
  XPath locator strategies,
- exact-one-match and visibility requirements,
- minimized source URL without credentials, query, or fragment,
- selected-target snapshot with an explicit DOM attribute allowlist,
- explicit exclusion of input values, text content, HTML, screenshots, and raw
  page capture,
- pending, accepted, and rejected review states,
- rejection reason and review/capture effort metrics,
- narrow context update that appends application evidence and promotes only the
  accepted locator to `OBSERVED`,
- replay fixtures and generated observation JSON Schema,
- CLI capture, status, and review commands,
- controlled end-to-end verification script,
- 66 passing tests with Chromium, including regression coverage for editability
  semantics.

### Reference flow

```text
human-reviewed context with one inferred locator
→ serve controlled page on loopback
→ Playwright verifies button:Search selects exactly one visible button
→ persist a minimized pending observation
→ human accepts the mapping
→ append APPLICATION evidence
→ promote the primary locator from INFERRED to OBSERVED
→ full adaptation readiness changes from one blocker to ready
```

### Exit criteria

- [x] One controlled local page can be opened through Playwright.
- [x] The user authorizes the URL and target element ID.
- [x] One selected element is captured without whole-page dumping.
- [x] Observation evidence is linked to the correct context and locator.
- [x] One primary locator moves from `INFERRED` to `OBSERVED` only after
      acceptance.
- [x] Input values, text content, HTML, screenshots, and raw page data are not
      persisted.
- [x] Capture and context update are replayable in deterministic tests.
- [x] Rejection leaves context unchanged.
- [x] The reference context reaches readiness through evidence rather than a
      manual status rewrite.
- [x] No LLM is used.

### What Sprint 3 proves

One existing locator can be verified against a real controlled page, represented
by a minimized provider-neutral observation, reviewed by a human, and applied
without changing business context or unrelated application structure.

### What Sprint 3 does not prove

- safe capture from arbitrary public or enterprise applications,
- greenfield element, page, component, or process discovery,
- free-form browser element selection,
- locator generation or ranking,
- credentialed workflows, iframe or Shadow DOM support,
- accessibility-tree, network, screenshot, or trace capture,
- POM proposal quality,
- external LLM safety or value,
- framework adaptation,
- usability or time savings.

### Gate to Sprint 4

Any LLM request must consume an explicitly selected and minimized projection of
confirmed context and accepted browser evidence. Raw pages, arbitrary session
state, credentials, and unrelated context remain outside the request.

## Architecture checkpoint A — Lifecycle and enterprise alignment

**Status:** Done in documentation before Sprint 4

### Goal

Clarify the long-term system before introducing LLM synthesis and framework
adaptation.

### Decisions recorded

- TestCartographer and `qa-automation-framework` are separately executable
  modules of one automation lifecycle.
- The framework owns normal execution; TestCartographer owns context,
  LLM-assisted engineering, maintenance, and expansion.
- Creation is human-guided and LLM-assisted rather than fully autonomous.
- The framework remains independent of TestCartographer during normal runs.
- A future framework-side Execution Evidence Collector supplies bounded
  diagnostic input for maintenance.
- Maintenance has reactive and proactive modes.
- Proactive maintenance can re-observe approved areas after deployment windows,
  including mapped elements outside the current test pool.
- Expansion repeats creation but should reuse the existing application map,
  repository knowledge, and accepted conventions.
- Project configuration should store non-secret mappings and secret references,
  not credential values.
- Three authentication strategies are parked: shared storage state,
  declarative login recipe with in-memory secrets, and interactive login for
  SSO/MFA.
- Salesforce remains an intentional enterprise acceptance target.

### What the checkpoint proves

The product lifecycle, module boundaries, future maintenance modes, and
enterprise-validation direction are coherent enough to guide the next
contracts.

### What the checkpoint does not prove

No workspace profile, authentication contract, evidence collector, maintenance
workflow, expansion reuse, or Salesforce integration has been implemented.

## Sprint 4 — Bounded LLM synthesis and POM proposal

**Status:** Done

### Goal

Use only authorized, minimized, confirmed context and accepted observations to
produce a strict, reviewable POM proposal without mutating a repository or
claiming live-provider value.

### Delivered

- provider-neutral `BoundedSynthesisRequest` version `0.1`,
- field-level projection from a fully ready `ContextBundle`,
- default authorization of `PUBLIC` and `INTERNAL` values only,
- hard requirement for `CONFIRMED` or `OBSERVED` knowledge,
- explicit excluded-field catalogue and prohibited claims,
- deterministic prompt rendering from the exact request,
- provider-neutral `SynthesisAdapter` boundary,
- deterministic `ReplaySynthesisAdapter`,
- strict `PomProposal` version `0.1`,
- strict parser rejecting fences, invalid JSON, duplicate keys, schema drift,
  missing fields, and unexpected fields,
- exact raw-output preservation on success and failure,
- deterministic validation of page, component, method, action, locator,
  symbolic data, fixture, test, and outcome references,
- separate `PROTOCOL_ERROR`, `VALIDATION_REJECTED`, and `READY_FOR_REVIEW`
  states,
- explicit human `ACCEPTED` or `REJECTED` review,
- versioned `SynthesisRun` storing request, prompt hash, raw output, proposal,
  validation, and review,
- CLI commands for request construction, replay, status, and review,
- committed request, valid, malformed, overreaching, unknown-locator, and
  missing-step fixtures,
- deterministic synthesis replay verifier,
- three committed JSON Schemas,
- focused request, parser, validator, pipeline, review, IO, schema, and CLI
  tests.

### Exit criteria

- [x] A fully ready context can be projected into a bounded request.
- [x] Base URL, routes, raw source references, evidence hashes, timestamps,
      notes, browser state, and repository files remain outside the request.
- [x] Required non-authorized status or sensitivity blocks request creation.
- [x] The same request renders the same prompt.
- [x] Replay receives the exact request and prompt.
- [x] Raw output is preserved exactly, including outer whitespace.
- [x] Malformed protocol output remains separate from substantive rejection.
- [x] Invented locators, missing steps, secret claims, unknown outcomes, and
      prohibited claims are rejected deterministically.
- [x] A valid proposal remains pending until explicit human review.
- [x] Rejected or invalid proposals cannot be promoted through review.
- [x] No live provider is called.
- [x] No repository file is modified by synthesis.

### What Sprint 4 proves

One LLM-facing boundary can be explicit, minimized, versioned, replayable,
strictly parsed, deterministically validated, and separately reviewed before it
is allowed to influence framework adaptation.

### What Sprint 4 does not prove

- live-provider compliance or semantic quality,
- provider reliability, latency, cost, or privacy,
- prompt-injection resistance,
- correctness across varied applications,
- repository-specific POM placement,
- generated source code or execution,
- enterprise authentication or Salesforce readiness,
- usability or economic value.

### Gate to Sprint 5

Sprint 5 may consume only a human-accepted `SynthesisRun`. It must inspect a
real target copy of `qa-automation-framework` and produce a reviewable mapping
plan before any source file is written.

The accepted logical proposal must not be treated as proof that:

- named classes or fixtures already exist,
- proposed names fit repository conventions,
- file paths are known,
- framework configuration and secrets are resolved,
- the generated implementation would run.

## Sprint 5 — Project workspace and framework adaptation plan

**Status:** Done

### Goal

Map one human-accepted logical proposal into a concrete, bounded
`qa-automation-framework` workspace without writing files blindly.

### Delivered

- non-secret `WorkspaceProfile` version `0.1`,
- marker files, allowed roots, ignored names, and inspection budgets,
- read-only local workspace inspection,
- minimized `FrameworkSnapshot` version `0.1`,
- repository-relative paths, file hashes, sizes, and Python symbol metadata,
- deterministic root fingerprint,
- no persisted source contents, absolute paths, or secret values,
- `AdaptationPlan` version `0.1`,
- exact page, component, fixture, and E2E test target paths,
- `create_file`, `add_symbol`, and `reuse_symbol` operations,
- source-proposal traceability and operation dependencies,
- separate adaptation-plan review,
- CLI for inspect, plan, status, and review,
- controlled framework fixture and replay artefacts,
- three generated and tested JSON Schemas,
- standalone verifier proving byte-for-byte framework immutability,
- 128 tests expected with Chromium on the normal Windows environment.

### Exit criteria

- [x] One controlled framework workspace can be inspected locally.
- [x] The user supplies the approved profile and framework root.
- [x] Traversal is limited by marker, allowlist, count, and size constraints.
- [x] Source contents and absolute paths are not persisted.
- [x] Python classes, functions, bases, and method names are replayable.
- [x] One accepted proposal maps to exact framework files and symbols.
- [x] Existing targets are distinguished from new files and missing symbols.
- [x] Proposal acceptance does not imply adaptation-plan acceptance.
- [x] Plan acceptance changes only the plan state.
- [x] No generated source is included and no framework file is modified.
- [x] No live provider is required.

### What Sprint 5 proves

A repository-aware planning boundary can be deterministic, explainable,
replayable, and read-only before source generation is introduced.

### What Sprint 5 does not prove

- correctness of the first target-placement convention for every project,
- complete repository semantics,
- source generation or patch application,
- collection or execution success,
- secret detection,
- full enterprise-repository usefulness.

### Gate to Sprint 6

Sprint 6 may consume only a human-accepted adaptation plan tied to the exact
snapshot fingerprint. If the framework changes, it must be re-inspected and the
plan rebuilt or explicitly reconciled before source changes are proposed.

## Sprint 6 — First runnable test and creation-lifecycle evaluation

**Status:** Done

### Goal

Complete the first controlled creation lifecycle:

```text
accepted ContextBundle and observation
→ accepted logical POM proposal
→ accepted repository adaptation plan
→ exact source patch ready for review
→ explicit source acceptance
→ safe application to a clean framework copy
→ one independently runnable browser test
→ creation-lifecycle evaluation
```

### Delivered

- non-secret `GenerationProfile` version `0.1`,
- explicit public symbolic test-data binding,
- `CodePatch` version `0.1` with exact UTF-8 source and hashes,
- deterministic templates for one Page Object, one Component Object, one
  existing E2E fixture extension, and one E2E test,
- source AST safety checks for the bounded slice,
- separate patch preview, status, accept, and reject commands,
- stale snapshot and stale target-hash rejection,
- full preflight before any write,
- atomic temporary-file replacement and rollback,
- `PatchApplicationReport` version `0.1`,
- compile, exact pytest collection, and real-browser execution gate,
- `CreationEvaluation` version `0.1`,
- metrics for generated/modified/reused artefacts, correction count, compile,
  collection, execution, and time to first runnable test,
- explicit proof that ordinary execution uses neither TestCartographer nor a
  live LLM,
- controlled-copy and local-framework-copy acceptance paths,
- four generated and tested JSON Schemas,
- standalone verifier, CLI coverage, and deterministic replay fixtures,
- 159 tests expected with Chromium on the normal Windows environment.

### Exit criteria

- [x] Only an accepted Sprint 5 plan tied to the current fingerprint is used.
- [x] Test data is supplied through an explicit non-secret binding.
- [x] Exact source is a separate reviewable artefact.
- [x] Proposal, placement, and source acceptance remain separate.
- [x] Stale framework state blocks generation or application.
- [x] Existing `tests/e2e/conftest.py` is extended rather than replaced.
- [x] All target operations pass preflight before the first write.
- [x] Partial application is rolled back on write failure.
- [x] A clean framework copy compiles after application.
- [x] Pytest collects exactly one generated target test.
- [x] Real Chromium executes the target test in the normal Windows gate.
- [x] The test contains meaningful assertions outside Page Objects.
- [x] The resulting test runs without TestCartographer or a live LLM.
- [x] The original framework repository remains unchanged.
- [x] Creation timing and correction evidence is persisted.

### What Sprint 6 proves

The first end-to-end creation prototype can move from accepted application
evidence to a reviewed, applied, collected, and executed framework test while
preserving explicit authority boundaries and leaving the original framework
untouched.

### What Sprint 6 does not prove

- safe unattended writes to the original project repository,
- arbitrary AST edits or merge-conflict handling,
- general code quality across applications,
- live-provider quality or prompt-injection resistance,
- enterprise authentication and Salesforce usefulness,
- maintenance after application drift,
- superiority over manual, Codegen, or general-LLM workflows.

### Gate to Sprint 7

Sprint 7 may consume execution evidence only through an explicit bounded
contract. A failed test must not automatically be labeled an application bug,
and traces, screenshots, URLs, values, and secrets require separate policy.

## Sprint 7 — Framework execution-evidence contract

**Status:** Done

### Goal

Define and exercise one provider-neutral, privacy-bounded handoff from normal
pytest execution to future TestCartographer maintenance without making the
framework depend on TestCartographer or a live LLM.

### Delivered

- strict `ExecutionEvidenceProfile` version `0.1`,
- strict `ExecutionEvidenceBundle` and per-test record contract version `0.1`,
- standalone framework-side pytest reference collector,
- no TestCartographer imports in the collector process,
- three explicit outcomes: `passed`, `test_failure`, and
  `infrastructure_error`,
- deterministic phase rule for call versus setup/teardown failure,
- complete links to context, process, synthesis run, adaptation plan, code
  patch, and source IDs,
- bounded structural step probe without values or method arguments,
- URL minimization to origin and path,
- redaction-before-hashing for configured runtime secrets and common named
  secret assignments,
- exception type, safe summary, relative failure location, and redacted hashes
  instead of raw failure text,
- explicit non-persistence of input values, credentials, raw messages, raw
  tracebacks, stdout/stderr, HTML, screenshots, traces, and host names,
- record and step budgets,
- deterministic `assess_execution_evidence()` readiness report for later reactive maintenance,
- `evidence status` and `evidence assess` CLI commands,
- committed replay profile and three-outcome bundle,
- live subprocess verifier that intentionally produces one pass, one test
  failure, and one infrastructure error,
- two generated and tested JSON Schemas,
- 185 tests expected with Chromium on the normal Windows environment.

### Exit criteria

- [x] The framework-side collector runs without importing TestCartographer.
- [x] One pass, one call-phase failure, and one setup-phase error are captured.
- [x] Test failure is not labeled an application bug.
- [x] Reference records link to accepted Cartographer artefacts.
- [x] The last bounded POM step is retained without input values.
- [x] URL credentials, query, and fragment are excluded.
- [x] Raw exception messages and tracebacks are not persisted.
- [x] Captured output, HTML, screenshots, and traces are not persisted.
- [x] Bundle counts are validated against actual records.
- [x] Missing traceability or last-step context remains explicit.
- [x] Static replay and live subprocess collection both validate.
- [x] Deterministic assessment marks the reference failure bundle ready for
  future reactive-maintenance intake.
- [x] No live LLM is used.

### What Sprint 7 proves

A normal pytest process can produce a small, traceable and privacy-bounded
maintenance handoff that TestCartographer validates only after framework
execution has completed.

### What Sprint 7 does not prove

- root-cause diagnosis or application-bug classification,
- automatic repair,
- crash-safe evidence streaming,
- xdist aggregation, retries, or flaky-run correlation,
- approved screenshot, trace, or network artefact retention,
- CI upload and retention,
- production installation in `qa-automation-framework`,
- enterprise authentication or Salesforce usefulness.

### Gate to Sprint 8

Sprint 8 may use a live model only through a local, provider-bounded adapter.
The LLM may order and rephrase an allowlisted deterministic question set, but it
must not answer questions, create context facts, request secrets, or bypass
human confirmation. Raw prompts and raw responses must remain unpersisted.

## Sprint 8 — Live local-LLM guided intake from minimal context

**Status:** Done

### Goal

Start from one minimal human automation request, use a real local Ollama model to
plan a concise interview, keep the human authoritative for every fact, and
finish with a context ready for Sprint 9 guided process discovery.

### Delivered

- strict `MinimalContextSeed` version `0.1`,
- deterministic construction of a structurally valid unknown-heavy
  `ContextBundle`,
- new human-intake questions for application name, environment, starting URL,
  and process name,
- strict `GuidedIntakeProfile` and `GuidedIntakeRun` contracts version `0.1`,
- provider abstraction with replay and local Ollama adapters,
- loopback-only Ollama base URL and explicit rejection of cloud model names,
- local model preflight through version and installed-model endpoints,
- two structured-output interview phases: collection and confirmation,
- exact candidate-set validation with no invented, omitted, or duplicated
  question IDs,
- LLM authority limited to ordering and rephrasing questions,
- human answers applied through the existing evidence-producing intake engine,
- separate discovery-readiness assessment that does not claim full adaptation
  readiness,
- prompt/response hashes and latency without persisted raw prompts or responses,
- `intake seed`, `intake guide`, and `intake guide-status` CLI commands,
- deterministic replay verifier and mandatory live local-Ollama verifier,
- three generated and tested JSON Schemas,
- 209 tests expected with Chromium on the normal Windows environment.

### Reference flow

```text
one-sentence automation request
→ unknown-heavy ContextBundle
→ nine deterministic context gaps
→ local LLM orders and rephrases the interview
→ human supplies application and process facts
→ local LLM plans the confirmation pass
→ human confirms business-critical facts
→ ready for guided process discovery
→ full adaptation still blocked by missing browser evidence
```

### Exit criteria

- [x] A one-sentence seed creates a valid context without invented app facts.
- [x] Application, environment, URL, process, purpose, risk, role, precondition,
  and outcome gaps remain explicit.
- [x] A real local Ollama call uses structured JSON output.
- [x] The model receives an allowlisted question set and must return it exactly.
- [x] The model cannot write answers into `ContextBundle`.
- [x] Human answers remain `PROVIDED` until separately confirmed.
- [x] Confidential URL values are not included in model prompts or run records.
- [x] Raw prompts and raw model responses are not persisted.
- [x] Cloud endpoints and cloud model names are rejected.
- [x] Replay tests cover the same contract without requiring a model.
- [x] The final state is ready for guided discovery, not falsely adaptation-ready.

### What Sprint 8 proves

A local model can make the deterministic intake workflow conversational and
context-aware while the existing rules, evidence model, and human confirmation
retain authority over every stored fact.

### What Sprint 8 does not prove

- that one local model always asks the best question in the best order,
- semantic understanding of arbitrary long or contradictory answers,
- browser discovery of pages, elements, actions, and selectors,
- a complete human-operated Creation Flow,
- time savings against manual discovery or Playwright Codegen,
- prompt-injection resistance for arbitrary external content,
- enterprise authentication or Salesforce usefulness.

### Gate to Sprint 9

Sprint 9 may consume only human-reviewed context from Sprint 8. Browser
discovery must remain bounded to one authorized process and must ask the human
when page, component, element, action, or locator interpretation is ambiguous.

## Sprint 9 — Guided multi-element process discovery

**Status:** Done

### Delivered

```text
human-reviewed process brief
→ one authorized local page
→ four bounded semantic candidates
→ three process targets
→ two deterministic selections
→ one ambiguity between equal Search buttons
→ one local-LLM clarification question
→ one human element selection
→ accepted evidence-backed process map
→ full ContextBundle readiness
```

The slice remains bounded to one page, one component, three elements, four
process steps, one symbolic test-data requirement, and one expected result.
The model phrases but never resolves the ambiguity. See
[`process-discovery.md`](process-discovery.md).

### Gate to Sprint 10

Sprint 10 may orchestrate only the already accepted boundaries. It must begin
from a short request, retain human review points, finish with one runnable test,
and report elapsed model time plus explicit human actions. It must not hide
fixture data or claim measured savings before a comparison exists.

## Sprint 10 — Fixture-assisted integrated Creation Flow

**Status:** Done

### Delivered

```text
short human request
→ two live local-LLM intake plans
→ fixture-supplied human answers and confirmations
→ bounded Chromium discovery
→ one live local-LLM ambiguity question
→ fixture-supplied candidate selection
→ fixture-supplied synthesis handoff
→ strict deterministic POM proposal
→ read-only repository plan
→ fixture-supplied patch review
→ snapshot-bounded sandbox
→ one runnable Playwright test
→ effort and human-action summary
```

The flow records three live local-model turns, 23 represented human actions,
browser and verification time, generated and modified files, and the passing
test result. Fixture assistance is explicit. POM synthesis remains a
deterministic reference template traversing the existing strict protocol; it is
not mislabeled as a live model call.

Sprint 10 also closes an authority mismatch discovered during integration:
general context readiness still allowed four synthesis-required `PROVIDED`
values while the synthesis boundary requires `CONFIRMED` or `OBSERVED`. A
separate human synthesis-handoff review confirms those values without weakening
the synthesis contract. In the automated verifier, that human authority is
represented by fixtures. See [`creation-flow.md`](creation-flow.md).

Sprint 10 proves:

```text
Creation mechanics verified: true
Ready for human-trigger integration: true
Interactive human trigger used: false
Ready for external user demonstration: false
```

It does not claim a fixed percentage of saved work until comparative
measurements exist.

## Sprint 11 — Human-triggered interactive Creation Flow

**Status:** Done

### Goal

Connect a real operator to the existing Creation Flow engine without rebuilding
its technical stages.

```text
real user enters a short automation request
→ Cartographer asks bootstrap context once at the start of the run
→ Cartographer asks process-specific context once
→ one aggregate context summary is confirmed or a numbered field is edited
→ visible browser discovery runs
→ ambiguous candidates are shown to the user
→ user selects the intended element
→ ContextBundle, POM proposal, adaptation plan, and patch are shown for review
→ the user accepts, rejects, or edits at each authority boundary
→ the existing engine produces and runs the Playwright test
```

### Delivered

- interactive `creation interactive` CLI entry point,
- real operator-provided initial request,
- blocking intake answers plus one aggregate context-summary confirmation,
- headed Chromium candidate review with visible bounded labels,
- real ambiguity selection,
- separate discovery, synthesis-handoff, POM, repository-plan, source-patch,
  and execution decisions,
- `InteractiveOperatorSession` audit contract without raw answer values,
- separate interactive readiness assessment,
- generated JSON Schemas,
- direct CLI and `python -m` tests,
- scripted 18-prompt mechanics verifier that explicitly does not replace the
  manual operator gate,
- safe full-word `CONFIRM`, `EDIT`, `QUIT`, and `CANCEL` commands that cannot be
  stored accidentally as business context.

### Exit criteria

- [x] The initial request comes from the operator, not a fixture.
- [x] Bootstrap and process-specific questions are displayed and answered interactively.
- [x] The flow blocks until required answers and one aggregate context confirmation are supplied.
- [x] Browser discovery is headed and labels bounded candidates for review.
- [x] Ambiguous candidates are presented and selected by the operator.
- [x] POM and repository plan are shown before acceptance.
- [x] Every source line and content hash is shown before exact patch acceptance.
- [x] No fixture silently replaces a missing human decision.
- [x] The final report distinguishes human, LLM, browser, and deterministic work.
- [x] Incomplete local-model ambiguity wording is closed deterministically without selecting a candidate.
- [x] Navigation docstrings describe method responsibility rather than copying the raw operator request.
- [x] `Ready for external user demonstration` is true only for a completed real
  operator session linked to a non-fixture CreationFlowRun.
- [ ] Resume from an arbitrary downstream review boundary is supported.
- [ ] Generated POM, plan, or patch can be edited in-flow instead of accepting or
  rejecting and starting a new controlled run.
- [ ] Confirmed bootstrap context is persisted and reused across separate runs
  until the operator requests a change or staleness/conflict invalidates it.

### What Sprint 11 proves

The existing Creation Flow engine can be operated from a real terminal trigger,
can stop at every required human authority boundary, can keep browser evidence
visible during ambiguity resolution, and can continue from real operator
decisions to one passing test.

### What Sprint 11 does not prove

- usability for an unbriefed external participant,
- generalization beyond the controlled one-page catalog,
- multi-page or authenticated workflows,
- downstream edit/resume ergonomics,
- measured savings versus manual work or Playwright Codegen.

See [`interactive-creation-flow.md`](interactive-creation-flow.md).

## Sprint 12 — Human-triggered Reactive Maintenance Flow

**Status:** Implemented; real operator run is the acceptance gate

### Goal

Prove one bounded reactive-maintenance path without treating a failed test as a
diagnosis.

```text
one existing framework test
→ controlled locator drift
→ one call-phase test failure
→ bounded framework execution evidence
→ deterministic re-observation readiness
→ real operator authorizes headed re-observation
→ real operator selects the current control
→ deterministic one-file locator patch
→ every source line reviewed
→ fresh snapshot-bounded sandbox
→ one passing framework retest
```

### Delivered

- strict reactive-maintenance profile, evidence-assessment, diagnosis, patch,
  action-ledger, run, and assessment contracts,
- five generated and tested JSON Schemas,
- independent framework execution before and after repair through the Sprint 7
  standalone pytest collector,
- explicit infrastructure-error exclusion,
- evidence disposition `reobservation_required` rather than an automatic stale-
  locator verdict,
- headed Chromium current-page candidate review,
- real operator candidate selection,
- deterministic one-occurrence locator patch with before/after hashes,
- full exact source rendering before acceptance,
- snapshot-bounded sandbox materialization and hash preflight,
- one controlled test failure before repair and one clean pass after repair,
- original-framework fingerprint and target-hash preservation,
- `maintenance interactive`, `maintenance status`, and `maintenance assess` CLI
  commands,
- scripted mechanics verifier that explicitly does not replace the real-
  operator gate,
- 285 tests passed with Chromium in the Windows acceptance environment.

### Exit criteria

- [x] Framework execution remains independent of TestCartographer and an LLM.
- [x] Exactly one target call-phase failure is captured before repair.
- [x] Infrastructure errors block maintenance rather than becoming repair candidates.
- [x] Failed-test evidence does not claim an application bug.
- [x] Evidence grants only bounded re-observation.
- [x] The old locator must be absent from current-page evidence.
- [x] A real operator selects the current candidate in headed Chromium.
- [x] Repair-candidate status appears only after current-page evidence and human selection.
- [x] Every source line and hash is shown before patch acceptance.
- [x] The accepted patch changes one controlled locator occurrence.
- [x] Patch application is limited to a fresh snapshot-bounded sandbox.
- [x] The original framework remains byte-for-byte unchanged at the target and fingerprint levels.
- [x] The same test passes after repair with no infrastructure error.
- [x] No live LLM or fixture decision is used in the real-operator path.
- [ ] Arbitrary failure classes, multi-file repairs, and context staleness propagation are supported.

### Final acceptance evidence

The Windows acceptance run completed with:

```text
285 passed
real operator actions: 5
failure before / pass after: 1 / 1
application bug claimed: false
live LLM used: false
original framework unchanged: true
reactive-maintenance blockers: none
```

### What Sprint 12 proves

One real failed framework test can feed a bounded maintenance handoff, obtain
current browser evidence and human authority, produce one exact sandbox-only
repair, and pass on retest without mislabelling the original failure.

### What Sprint 12 does not prove

- general root-cause diagnosis,
- application-defect detection,
- data, environment, timing, workflow, assertion, or authentication repair,
- automatic stale/conflicting context updates or impact analysis,
- multi-file or LLM-generated repairs,
- writes to the original repository,
- authenticated, enterprise, or Salesforce maintenance,
- measured time savings or broad usability.

See [`reactive-maintenance-flow.md`](reactive-maintenance-flow.md).

## Sprint 13 — Proactive frontend/context regression

**Status:** Done — real operator acceptance verified

### Goal

Prove one bounded proactive-maintenance distinction: a current independent
framework test may remain green while an approved mapped frontend element outside
that test pool has drifted.

### Implemented vertical slice

- one human-accepted public/no-auth observation inventory,
- one logical page, two controlled baseline/current routes, and two approved mapped elements,
- one framework Search test executed independently on baseline and current pages,
- one covered Search element that remains stable,
- one mapped but uncovered Sort element whose locator changes,
- deterministic unchanged/locator-drift/missing/ambiguous dispositions,
- current-test-risk versus mapped-context-stale impact classification,
- one full review-only impact report,
- exactly three real operator decisions,
- no bootstrap re-intake, LLM, raw page, bug claim, patch, or context mutation.

### Acceptance gate

The scripted verifier proves mechanics only. Sprint 13 closes only after a real
operator runs the headed flow and the persisted assessment reports no blockers.

### Deferred from the original direction

Scheduling, deployment hooks, authentication profiles, protected applications,
large inventories, automatic context-status transitions, maintenance handoff, and
enterprise validation remain later hypotheses. This is an intentional small
vertical slice, not a claim that the full parked direction is complete.

## Sprint 14 — Expansion using the existing map

**Status:** Done — real operator acceptance verified

### Goal

Prove one bounded incremental-expansion slice in which a second automated
process reuses accepted application/framework knowledge, collects only the
missing or stale delta, and reaches runnable code through the existing
creation/adaptation/delivery pipeline.

### Delivered vertical slice

- explicit human intent to add Sort beside an existing Search process,
- versioned `ExpansionRequest`, `ExpansionPlan`, `ExpansionRun`, and
  `ExpansionAssessment` contracts,
- separate workflow dispositions `REUSE`, `ASK_HUMAN`, `OBSERVE_NEW`,
  `REOBSERVE`, `REVIEW`, and `BLOCKED`,
- reuse of eight accepted application/framework knowledge items with no
  bootstrap re-intake,
- three process-specific human questions,
- targeted headed re-observation of the stale Sort locator from Sprint 13,
- immutable accepted base ContextBundle plus a separately reviewed candidate
  Sort ContextBundle,
- reuse of the existing synthesis, adaptation, and delivery pipeline,
- `EXTEND_SYMBOL` for adding only `apply_sort` and `sort_results` to the
  existing `CatalogPage`,
- method/property collision protection in framework snapshots,
- hash-bound `REPLACE_FILE` with source-drift preflight,
- one new Sort test and preservation of the existing Search test,
- sandbox-only application with the original framework unchanged,
- seven explicit real-operator authority transitions,
- no live LLM, PhoenixQA healing, raw-page persistence, or measured-savings
  claim.

### Acceptance evidence

The Sprint 14D.2 Windows closure gate recorded:

```text
339 passed
0 failures
0 errors
0 skipped

Search before expansion: PASS
Search after expansion: PASS
Sort after expansion: PASS

expansion_verified: true
controlled_demo_ready: true
blockers: []
```

### What Sprint 14 proves

A controlled second process can reuse accepted current knowledge, refresh one
known-stale frontend target, extend an existing Page Object through the same
reviewed creation pipeline, and execute beside the preserved first process.

### What Sprint 14 does not prove

- arbitrary new application areas,
- persistent cross-run bootstrap/profile invalidation,
- authenticated or enterprise expansion,
- production-repository writes,
- general source rewriting,
- a general-purpose sort oracle,
- broad usability or measured productivity savings.

See [`expansion-flow.md`](expansion-flow.md).

## Checkpoint 14.5 — Documentation truth cleanup and validation-first reset

**Status:** Done in documentation

### Goal

Synchronize current-state documentation with the actual Sprint 14 capability
and change the roadmap from speculative feature expansion to validation-first
learning.

### Decisions

- current-state indexes are rewritten rather than accumulating obsolete claims,
- gaps use `CORE / VALIDATION / ENTERPRISE / PARKED / OUT-OF-SCOPE`,
- persistent `ProjectProfile` becomes the next P0 core capability,
- API/SOM is removed from TestCartographer product scope,
- user-interface work is postponed until after core v1 value is evaluated,
- validation targets increase both technical difficulty and lack of project
  control,
- once external validation begins, major abstractions require concrete observed
  evidence.

See [`checkpoint-14.5.md`](checkpoint-14.5.md).

## Sprint 15 — Persistent ProjectProfile and bootstrap reuse

**Status:** Done — real operator acceptance verified

### Goal

Implement the missing project-wide persistence boundary that allows bootstrap
facts/configuration to be collected once, reused across later flows, and
selectively invalidated.

### Delivered

- strict non-secret `ProjectProfile v0.1`,
- dedicated `ProjectValue`,
- one active application environment + base URL/origin,
- exact `WorkspaceProfile` and capability-specific `GuidedIntakeProfile` ID/hash bindings,
- project data-boundary policy and minimal authentication declaration/reference,
- local deterministic JSON persistence and JSON Schema,
- accepted revision/event lifecycle and `configuration_fingerprint`,
- fail-closed fingerprint and binding-drift validation,
- normal ContextBundle bootstrap projection through SYSTEM evidence,
- `COMPATIBLE / REVIEW_REQUIRED / REOBSERVE / RESNAPSHOT / BLOCKED`,
- actual human-triggered Creation Flow runner wiring,
- real operator separate-process acceptance.

### Acceptance evidence

```text
Run A: revision 1; first bootstrap questions 3; secrets/auth state persisted false
Run B: later creation; bootstrap questions 0; process questions preserved
Run C: later expansion; bootstrap questions 0; workspace/guided bindings reused
Run D: revision 1 → 2; browser evidence REOBSERVE; business context COMPATIBLE;
       workspace COMPATIBLE; guided intake COMPATIBLE; unrelated fields re-asked 0

post-acceptance regression: 394 passed; 0 failures/errors/skipped
```

### What Sprint 15 proves

Bootstrap configuration can survive separate runs without becoming an unbounded
cache. Current values are reused silently while relevant change produces
selective compatibility consequences.

### What Sprint 15 does not prove

External-app usability/economics, multi-environment/team profile management,
authenticated execution, production repository delivery, or need for a shared
multi-process application graph.

See [`sprint-15-project-profile.md`](sprint-15-project-profile.md).

## Sprint 16 — External-validation protocol and evidence package

**Status:** Done — controlled real-operator rehearsal verified

### Goal

Prepare a repeatable validation method before challenging the product on
applications it does not control.

This sprint should be mostly validation infrastructure/protocol, not a new
feature bundle.

### Required outputs

- target classification by technical difficulty and degree of control,
- repeatable operator instructions,
- comparable evidence bundle,
- setup/active/correction/review timing definitions,
- failure/friction log,
- stop conditions,
- baseline procedure for later comparison,
- rule that a validation failure is recorded before its fix is designed.

### Non-goals

- speculative generalization for every expected external-app problem,
- enterprise authentication,
- GUI.

## Sprint 17 — External validation I: public applications

**Status:** Planned

### Goal

Run the existing product on external applications that were not built for
TestCartographer.

### Suggested levels

1. simple public application with conventional frontend semantics,
2. dynamic/script-heavy public frontend with asynchronous behavior.

The important evidence is whether existing assumptions survive when the project
cannot change the target page to accommodate them.

### Development rule

When a failure occurs:

```text
record evidence
→ classify limitation
→ design smallest justified change
→ rerun the same target
```

Do not hide the initial failure by immediately changing both product and target.

## Sprint 18 — External validation II: lower-control and more complex public targets

**Status:** Provisional

### Goal

Increase difficulty and decrease control further.

Potential characteristics:

- multi-page/component state,
- dynamic navigation,
- difficult synchronization,
- unstable or changing markup,
- scraping-resistant frontend behavior,
- process expansion across a new application area.

Use findings to drive maintenance generalization and impact-analysis scope.

## Sprint 19 — Authentication profiles and credentialed validation

**Status:** Provisional

### Goal

Implement only the minimum authentication/project-security boundary required by
a selected credentialed validation target.

Potential contracts:

```text
EnvironmentProfile
AuthProfile
SecretProvider references
```

Select the first authentication strategy from actual target requirements:

1. sensitive Playwright storage state,
2. declarative login recipe with in-memory secrets,
3. interactive human login for SSO/MFA.

Do not implement all three pre-emptively.

## Sprint 20 — Enterprise and Salesforce validation

**Status:** Provisional

### Goal

Challenge the validated product on an enterprise-style target and, when the
security/authentication boundary is ready, a safe Salesforce environment.

Candidate Salesforce flow:

```text
login
→ open Accounts
→ create an Account
→ save
→ verify the created record
```

Use only an approved non-production environment and bounded test data.

The purpose is validation, not Salesforce-specific product design.

## Sprint 21 — Comparative usability, economics, and v1.0 decision

**Status:** Provisional

### Goal

Decide whether TestCartographer is operationally useful, not merely technically
interesting.

Compare realistic testing-professional workflows:

```text
normal manual automation aids
vs.
DevTools/Playwright Codegen + general-purpose LLM
vs.
TestCartographer-assisted workflow
```

Measure:

- functional/assertion correctness,
- POM/component quality,
- unsupported assumptions,
- human corrections,
- setup and active user time,
- learning effort,
- time to first runnable test,
- maintenance effort after a real or controlled change,
- second-process expansion effort,
- LLM usage/cost,
- perceived difficulty, confidence, and willingness to reuse.

### v1.0 decision

v1.0 requires evidence that quality and operational economics justify the
workflow.

If the tool consistently increases work or complexity without compensating
benefit, simplify, narrow, or stop rather than declaring v1.0 from feature
count.

A GUI/IDE layer is evaluated only after this decision.

## Roadmap change policy

When evidence invalidates a planned sprint:

1. record the finding in `LEARNINGS.md`,
2. update the relevant gap or limitation,
3. redirect the roadmap rather than preserving the original plan for
   appearance,
4. state what the evidence proves and what it does not prove.

The roadmap is a working hypothesis, not a promise to implement every parked
direction.
