# Testing strategy

## Purpose

TestCartographer combines deterministic software with uncertain external inputs
such as human answers, browser observations, project documents, and future LLM
outputs.

The testing strategy keeps those concerns separate.

```text
deterministic contracts, state transitions, and persistence
→ exact fixtures and assertions

external interpretation and observation
→ controlled evidence and realistic evaluation later
```

Sprint 4 adds a bounded LLM-facing synthesis layer while preserving the
separation between deterministic contracts, provider output, proposal
authority, and human review.

## Current evidence

```text
104 tests expected with Playwright Chromium
controlled browser readiness transition verified
bounded synthesis replay and review transition verified
```

The preparation environment produced `103 passed, 1 skipped` because an
administrator policy blocks loopback browser navigation. The same browser test
already passed on the normal Windows development environment in Sprint 3.

The full result includes regression coverage for Playwright editability
semantics and the complete bounded synthesis request, parser, validator,
pipeline, persistence, CLI, and review boundary.

The test suite covers:

- context contract validation,
- adaptation readiness,
- deterministic JSON persistence,
- context JSON Schema drift,
- intake question selection,
- answer application,
- collection and review transitions,
- session lifecycle and metrics,
- session persistence,
- intake JSON Schema drift,
- command-line start, run, status, export, pause, and resume paths,
- browser-observation contract and schema drift,
- URL minimization and selected-target attribute allowlisting,
- locator strategy mapping, uniqueness, and visibility rules,
- pending, accepted, and rejected review states,
- evidence-backed context update and readiness transition,
- controlled Chromium execution against a loopback reference page,
- bounded synthesis request construction and minimization,
- deterministic prompt rendering,
- strict proposal parsing and duplicate-key rejection,
- exact raw-output preservation,
- substantive proposal validation,
- replay adapter request/prompt recording,
- protocol, validation, pending-review, accepted, and rejected run states,
- synthesis request/run persistence and JSON Schema drift,
- synthesis CLI request, replay, status, and review paths.

Passing tests prove the implemented rules for controlled fixtures. They do not
prove semantic correctness, usability, safety against arbitrary applications,
or product value.

## Test layers

### Context contract unit tests

Location:

```text
tests/unit/context/test_models.py
```

They verify:

- valid reference context loading,
- explicit unknown knowledge,
- status/value/evidence invariants,
- inferred-confidence requirement,
- conflicting-evidence requirement,
- strict rejection of extra fields,
- global identifier uniqueness,
- contiguous process-step order,
- action shape,
- reference integrity,
- page/component element ownership,
- action-target availability,
- primary-locator uniqueness,
- symbolic test-data uniqueness.

### Adaptation-readiness unit tests

Location:

```text
tests/unit/context/test_readiness.py
```

They prove:

- a complete fixture is ready,
- an incomplete fixture remains valid but blocked,
- a conflicting fixture remains valid but blocked,
- readiness reports are serializable.

### Context persistence tests

Location:

```text
tests/unit/context/test_io.py
```

They verify:

- load/save round trip,
- deterministic output,
- UTF-8 newline-terminated files.

### Context schema tests

Location:

```text
tests/unit/context/test_schema.py
```

They verify:

- committed JSON Schema matches the Pydantic model,
- the contract root rejects additional properties,
- schema version `0.1` is fixed.

### Intake question-rule tests

Location:

```text
tests/unit/intake/test_rules.py
```

They verify:

- stable collection order,
- browser-only blockers do not become human questions,
- stage-specific intake assessment,
- conflict priority,
- valid contexts produce no questions,
- unconfirmed supported values enter review,
- review begins only after required collection is resolved.

### Intake answer tests

Location:

```text
tests/unit/intake/test_answers.py
```

They verify:

- a supplied risk becomes `PROVIDED`,
- human evidence is appended,
- expected-outcome replacement targets the correct object,
- `UNKNOWN` remains explicit and unsupported,
- `SKIP` does not mutate context,
- open-question answers remain traceable,
- disallowed actions are rejected,
- conflict resolution becomes evidence-linked knowledge.

### Intake session tests

Location:

```text
tests/unit/intake/test_session.py
```

They verify:

- initial session classification,
- deterministic next-question selection,
- transition from collection to review,
- explicit confirmation,
- completion of human intake while full adaptation remains blocked,
- blocked state after deferred required knowledge,
- retry of deferred questions,
- pause and resume without history loss,
- interaction and active-time metrics.

### Intake persistence tests

Location:

```text
tests/unit/intake/test_intake_io.py
```

They verify deterministic session JSON round trips.

### Intake schema tests

Location:

```text
tests/unit/intake/test_intake_schema.py
```

They verify that the committed session schema equals the current Python model
and fixes session contract version `0.1`.

### CLI integration tests

Location:

```text
tests/integration/test_intake_cli.py
```

They exercise:

- session creation,
- status reporting,
- context export,
- a complete collection and review flow,
- active-time recording,
- pause through `:quit`,
- persistence after interactive actions.

The tests inject input, time, and output functions. They do not depend on a real
terminal or sleep delays.

## Fixture strategy

The context fixtures represent semantic states rather than many arbitrary JSON
examples.

### Complete

```text
testdata/context/valid/public_search_flow.json
```

Expected:

```text
structurally valid
+ adaptation ready
+ no human-intake questions
```

### Incomplete

```text
testdata/context/incomplete/public_search_flow.json
```

Contains:

- unknown risk,
- unknown expected outcome,
- inferred primary locator,
- blocking open question.

Expected at session start:

```text
structurally valid
+ three human-intake blockers
+ one browser/adaptation blocker beyond intake
```

Expected after deterministic collection and review:

```text
human intake complete
+ zero human-intake blockers
+ zero human-intake warnings
+ one remaining full-adaptation blocker
```

### Conflicting

```text
testdata/context/conflicting/public_search_flow.json
```

Expected:

```text
structurally valid
+ conflict-resolution question first
+ adaptation blocked
```

### Invalid

```text
testdata/context/invalid/missing_evidence_reference.json
```

Expected:

```text
rejected during structural validation
```


### Observation-ready

```text
testdata/context/observation_ready/public_search_flow.json
```

Expected before capture:

```text
human intake complete
+ exactly one full-readiness blocker
+ inferred Search button locator
```

Expected after accepted observation:

```text
locator status = OBSERVED
+ APPLICATION evidence appended
+ full adaptation ready
```

### Browser and observation replay

```text
testdata/browser/public_catalog.html
testdata/observation/pending/search_submit.json
testdata/observation/accepted/search_submit.json
```

The HTML contains a deliberate input value that tests assert is absent from
serialized observation data. Replay fixtures exercise persistence and review
without requiring a browser.

## State-transition testing principles

### Test immutable input and returned output

Answer application returns a new validated `ContextBundle`.

Tests assert that the original object remains unchanged where relevant.

### Test negative and deferred states

The workflow must not be tested only through the successful path.

Required states include:

- explicit unknown,
- skipped question,
- paused session,
- blocked session,
- retry of deferred questions,
- unsupported answer action.

### Test stage separation

A completed human intake must not automatically imply full adaptation
readiness.

The reference test explicitly requires:

```text
human intake complete = true
full adaptation ready = false
```

until browser evidence resolves the inferred locator.

### Test persistence after transitions

A session is intended to save after every accepted action. Integration tests
reload the persisted file and compare it with returned state.

## Schema snapshot policy

The repository commits:

```text
schemas/context-bundle-v0.1.schema.json
schemas/intake-session-v0.1.schema.json
schemas/observation-v0.1.schema.json
schemas/synthesis-request-v0.1.schema.json
schemas/pom-proposal-v0.1.schema.json
schemas/synthesis-run-v0.1.schema.json
```

Any intentional contract change must:

1. update the Python model,
2. regenerate the corresponding schema,
3. update fixtures and tests,
4. document compatibility and versioning consequences.

Silent schema drift is a test failure.

## Current execution commands

Full suite:

```powershell
python -m pytest
```

Schema regeneration and focused verification:

```powershell
python scripts/export_context_schema.py
python scripts/export_intake_schema.py
python scripts/export_observation_schema.py
python scripts/export_synthesis_schemas.py
python -m pytest tests/unit/context/test_schema.py `
    tests/unit/intake/test_intake_schema.py `
    tests/unit/observation/test_schema.py `
    tests/unit/synthesis/test_schema.py
```

Boundary verifiers:

```powershell
python scripts/verify_browser_observation.py
python scripts/verify_synthesis_replay.py
```

Compilation check:

```powershell
python -m compileall -q src tests
```

## Lifecycle validation model

The long-term test strategy must follow the complete two-module lifecycle rather
than stop at code generation.

### Creation validation

Validate:

- bounded context and observation input,
- LLM request authorization and minimization,
- POM/fixture/test proposal quality,
- framework mapping and reviewable patches,
- one runnable test with meaningful assertions,
- time to first runnable test and human correction effort.

### Independent execution validation

Validate that the adapted `qa-automation-framework` project:

- installs and runs without TestCartographer,
- does not require a live LLM,
- resolves configuration and secrets through its own execution path,
- produces ordinary pytest/Playwright results,
- can emit bounded execution evidence without changing test semantics.

### Reactive maintenance validation

Inject controlled failure classes such as:

- application defect,
- changed locator or DOM structure,
- stale test data,
- environment failure,
- automation bug,
- stale context.

Measure whether the system classifies the problem, selects the right evidence,
updates context safely, proposes an appropriate patch, and supports retest.

### Proactive maintenance validation

After a controlled deployment change, re-observe an approved inventory that
contains both:

- elements touched by current tests,
- mapped elements not touched by the current suite.

Verify that the system can identify relevant drift without unrestricted
crawling or silent repair.

### Expansion validation

Add a second process using the existing application map and compare against the
first process:

- number of human questions,
- number of new observations,
- duplicate Page Objects/components avoided,
- LLM input and cost,
- review and implementation time.

### Enterprise validation ladder

Progress through:

1. controlled local page,
2. simple public application,
3. modern dynamic public frontend,
4. controlled multi-page reference application,
5. credentialed enterprise-style system,
6. safe Salesforce environment.

Simple pages prove narrow mechanisms only. Salesforce remains a deliberate
acceptance target for authentication, dynamic component-driven UI, data
restrictions, complex state, and realistic maintenance economics.

Before credentialed validation, tests must cover:

- authentication profile parsing,
- secret-reference resolution without persistence,
- storage-state sensitivity and deletion,
- allowed-origin and action policies,
- session expiry and refresh,
- external-LLM minimization and authorization.

## What current tests do not cover

- a real terminal operated by a real tester,
- subjective clarity of question wording,
- actual setup time outside the measured prompt window,
- concurrent session editing,
- session corruption recovery,
- authorization of who may confirm facts,
- arbitrary external, dynamic, credentialed, iframe, or Shadow DOM applications,
- cross-browser execution beyond Chromium,
- redaction and secret handling,
- live LLM provider requests, latency, cost, or semantic quality,
- generated source code,
- `qa-automation-framework` adaptation or independent execution,
- framework-side execution-evidence collection,
- reactive or proactive maintenance,
- expansion using an existing application map,
- credentialed enterprise or Salesforce validation,
- comparative usability, maintenance economics, or time savings.

## Sprint 3 browser test layers

- unit tests verify URL minimization, locator mapping, selected-target
  allowlisting, review transitions, and narrow context updates,
- replay fixtures verify deterministic observation persistence,
- CLI integration tests verify capture/status/review behaviour without browser
  nondeterminism,
- one Chromium integration test opens the controlled local page,
- `scripts/verify_browser_observation.py` verifies the full local browser path
  and readiness transition.

The first real Windows Chromium run also exposed a gap that fake-based tests did
not catch: `locator.is_editable()` throws for a button instead of returning
`False`. The regression suite now verifies both sides of the boundary:

- non-editable element types such as `button` do not call `is_editable()`,
- supported targets such as native `input` elements still use Playwright's
  editability check.

This is why the standalone real-browser verifier remains a required commit gate
rather than an optional demonstration.

The next test boundary is the provider-neutral LLM request and strict proposal
parser. Live provider quality must remain separate from deterministic protocol
correctness.


## Sprint 4 synthesis test layers

### Request-projection tests

`tests/unit/synthesis/test_request.py` verifies:

- only confirmed and observed values are authorized,
- public and internal values are accepted by default,
- not-ready context is rejected,
- unauthorized status and restricted required values are rejected,
- base URL, routes, raw source references, hashes, and source values are absent,
- symbolic data references remain without concrete values,
- deterministic prompt rendering does not reintroduce excluded values.

### Strict parser tests

`tests/unit/synthesis/test_parser.py` verifies:

- valid proposal parsing,
- empty output rejection,
- Markdown-fence rejection,
- non-object root rejection,
- invalid JSON rejection,
- duplicate-key rejection,
- schema-version drift rejection,
- unexpected-field rejection.

These are protocol tests, not proposal-quality tests.

### Proposal-validation tests

`tests/unit/synthesis/test_validation.py` verifies:

- the reference proposal passes,
- execution-success overreach is rejected substantively,
- invented locators are rejected,
- omitted steps are rejected,
- request-ID mismatch is rejected,
- secret-bearing fixtures are rejected,
- unknown or missing outcomes are rejected,
- non-blocking questions remain warnings.

### Pipeline and raw-preservation tests

`tests/unit/synthesis/test_pipeline.py` verifies:

- replay receives the exact request and deterministic prompt,
- raw output is preserved exactly,
- malformed output produces `PROTOCOL_ERROR`,
- well-formed overreach produces `VALIDATION_REJECTED`,
- valid output produces `READY_FOR_REVIEW`.

The first implementation attempt exposed that inherited string trimming removed
a trailing newline from raw output. A dedicated `SynthesisRun` configuration now
preserves raw text exactly.

### Human-review tests

`tests/unit/synthesis/test_review.py` verifies:

- only `READY_FOR_REVIEW` may be reviewed,
- acceptance and rejection are separate final states,
- rejection requires a reason,
- protocol and validation failures cannot be accepted.

### Persistence and schema tests

`tests/unit/synthesis/test_io.py` and `test_schema.py` verify:

- deterministic request and run round trips,
- exact raw-output persistence,
- committed request, proposal, and run schemas match the Python models.

### CLI integration and full replay verifier

`tests/integration/test_synthesis_cli.py` verifies request, replay, status, and
review commands.

`scripts/verify_synthesis_replay.py` verifies the complete local path:

```text
ready context
→ bounded request
→ deterministic prompt
→ replay output
→ strict parser
→ deterministic validation
→ explicit human acceptance
```

No live provider or repository mutation is involved.

### Remaining synthesis evidence gap

The deterministic suite proves the local protocol. It does not prove:

- that a live model follows it,
- that a model proposes good architecture across real applications,
- provider-specific structured-output behaviour,
- prompt-injection resistance,
- enterprise data safety,
- acceptable latency or cost.


## Sprint 5 adaptation test layers

### Workspace-profile and model tests

`tests/unit/adaptation/test_models.py` verifies safe relative paths, unique
allowlists, entry-shape rules, immutable privacy flags, and operation graph
constraints.

### Read-only scanner tests

`tests/unit/adaptation/test_scanner.py` verifies:

- marker and allowlist enforcement,
- deterministic snapshots and fingerprints,
- file-size budgets,
- Python class/function/base/method extraction,
- source-change detection,
- absence of source text and absolute paths from the snapshot,
- byte-for-byte workspace immutability.

The scanner parses source locally with `ast`; tests do not claim that metadata
extraction is equivalent to complete static analysis.

### Planner tests

`tests/unit/adaptation/test_planner.py` verifies:

- only an accepted synthesis run can be planned,
- snapshot/profile identity must match,
- exact Page Object, component, fixture, and test targets,
- deterministic operation dependencies,
- `create_file`, `add_symbol`, and `reuse_symbol` classification,
- no generated source or framework mutation flags.

### Review, persistence, and schema tests

Review tests preserve a separate plan authority stage and require a rejection
reason. IO tests verify deterministic round trips. Schema tests verify the
committed profile, snapshot, and plan schemas against the Pydantic models.

### CLI integration and standalone verifier

`tests/integration/test_adaptation_cli.py` exercises inspect, plan, status, and
review while hashing the controlled framework before and after.

`scripts/verify_framework_adaptation_plan.py` verifies:

```text
controlled framework copy
→ read-only snapshot
→ accepted Sprint 4 proposal
→ exact adaptation plan
→ human acceptance
→ unchanged framework fingerprint and bytes
```

### Remaining adaptation evidence gap

Current tests do not prove:

- mapping quality on a full project copy,
- semantic understanding of imports, decorators, or fixture scope,
- source generation or patch safety,
- pytest collection or execution in the target framework,
- usefulness on enterprise repositories,
- secret or malicious-source detection.


## Sprint 6 source-delivery test strategy

The source-delivery layer is tested at four levels.

### Contract and deterministic generation

Unit tests cover strict models, exact whitespace preservation, schema round
trips, explicit public test-data binding, traceability, deterministic source
hashes, forbidden source constructs, stale snapshot rejection, and declared
framework prerequisites. They verify missing files, missing symbols, and wrong
symbol kinds are rejected before source generation.

### Review and application safety

Tests prove that only an accepted patch can be applied, target paths remain
inside the workspace allowlist, create and append preconditions are checked
before writing, target hashes are respected, temporary replacement is atomic,
and a simulated later write failure rolls back earlier changes. Sandbox tests
also prove that only entries from the accepted snapshot are copied, stale source
bytes block materialization, and an out-of-scope parent `tests/conftest.py` is
excluded before pytest collection.

### Framework collection and execution

The integration gate first materializes a framework sandbox from exact snapshot
entries, applies the patch there, runs `compileall`, requires pytest to collect
exactly one generated target, serves
the controlled local page, and executes the test with Chromium where available.
The normal Windows setup requires the browser test rather than accepting a skip.

### Lifecycle evaluation

`CreationEvaluation` can report `PASSED` only when review, application, compile,
collection, execution, assertion placement, runtime independence, no-live-LLM,
and original-framework immutability all pass. The evaluation also stores timing
and correction evidence for later comparison with manual and general-LLM paths.

Expected normal Windows result after the corrected Sprint 6: `159 passed`. The
preparation environment reports `157 passed, 2 skipped` only because
administrator policy blocks the two real-browser loopback gates.

## Sprint 7 execution-evidence test strategy

The execution-evidence layer is tested at five levels.

### Contract tests

Unit tests validate:

- the closed pass/test-failure/infrastructure outcome vocabulary,
- outcome-to-phase consistency,
- failure-required and failure-forbidden states,
- exact bundle counts,
- traceability completeness and explicit missing fields,
- timezone-aware timestamps,
- unique IDs and source references,
- literal false privacy guarantees,
- non-secret profile budgets and secret-variable-name uniqueness.

### Minimization tests

Deterministic tests prove that:

- URL user information, query, and fragment are removed,
- configured runtime secret values are redacted in memory,
- common password/token/secret assignments are redacted,
- redacted bounded digests are stable,
- absolute paths outside the repository are not persisted.

### Maintenance-readiness tests

`assess_execution_evidence()` is tested against:

- a complete reference bundle with two actionable failures,
- missing high-level traceability,
- missing structural step context,
- truncated record budgets.

The assessment does not diagnose root cause. It answers only whether Sprint 8
has enough bounded evidence to begin analysis.

### Independent framework subprocess

`tests/integration/test_execution_evidence_reference.py` starts a separate
pytest process with the standalone reference plugin. Plugin autoload is disabled
and the collector's import path contains only the framework-side reference
module.

The nested run intentionally produces:

```text
one pass
one call-phase AssertionError
one setup-phase RuntimeError
```

The outer test expects the nested pytest exit code to be non-zero, then validates
the emitted JSON with TestCartographer.

This distinction is important: an intentionally failing framework run is the
input evidence, not a failed TestCartographer test.

### Leakage assertions

The generated evidence file is searched for values that must not survive:

- configured secret value,
- URL credentials,
- query and fragment,
- raw assertion message,
- raw setup error message.

Tests also require explicit false flags for raw tracebacks, captured output,
HTML, screenshots, and traces.

### Standalone verifier

```powershell
python scripts/verify_execution_evidence_contract.py
```

The verifier repeats the subprocess run, validates all three counts, checks
leakage exclusions, and requires deterministic readiness for Sprint 8.

Expected normal Windows result at Sprint 7 closure: `185 passed`.

The preparation environment reports `181 passed, 2 skipped` because its
administrator policy blocks the existing two loopback Chromium gates. The
execution-evidence verifier itself requires no browser and is not skipped.

### Evidence still missing

Sprint 7 tests do not prove:

- production plugin installation in `qa-automation-framework`,
- xdist or multi-process merging,
- crash-safe incremental writes,
- retries or flaky-test correlation,
- CI retention and access control,
- approved screenshot, trace, or network artefact references,
- root-cause diagnosis or correct repair.

### CLI module-entry regression gate

Commands exposed through `python -m test_cartographer.cli` must be tested through
a subprocess in addition to direct `main([...])` tests. Direct imports do not
prove that module-level definition order and the `__main__` entry point are
correct. Sprint 7 added subprocess coverage for `evidence status` and
`evidence assess` after the Windows acceptance run exposed this difference.


## Sprint 8 live guided-intake validation

Sprint 8 uses three complementary layers:

1. **Pure contract tests** validate local-only profiles, exact candidate sets,
   strict parsing, prompt minimization, seed construction, and readiness.
2. **Replay end-to-end verification** plans collection and review with stored
   structured outputs, applies controlled human answers, and proves discovery
   readiness without a model.
3. **Mandatory Windows live-provider verification** checks Ollama version and
   model availability, performs two `/api/chat` structured-output calls, prints
   the generated interview, applies controlled human answers, and verifies that
   raw prompt/response text and the URL are absent from `GuidedIntakeRun`.

The complete normal Windows test gate after Sprint 8 is `205 passed`. The live
Ollama verifier is an additional acceptance gate and is not replaced by a skip.
The preparation environment uses HTTP mock transport and replay because it has
no local Ollama daemon.

Subprocess coverage includes the actual `python -m test_cartographer.cli intake
seed` entry point. Interactive human input remains tested through the underlying
engine rather than automated terminal driving.

### Real local-provider latency

The live guided-intake gate uses a configurable per-call timeout and must report the configured value on timeout. A one-token Ollama smoke test is insufficient evidence for the bounded structured-output workload. Regression coverage therefore includes the timeout error contract, while real Windows acceptance exercises the full two-call provider flow.


### Local structured-output liveness regression

The Sprint 8 live gate must verify more than provider reachability. The request
payload is regression-tested for an explicit generated-token ceiling, model
keep-alive, bounded JSON-Schema text fields, preload behavior, and timeout-specific
errors. The real verifier must print progress before and after both provider
turns so a long non-streaming call is not silently confused with a completed or
idle process.
