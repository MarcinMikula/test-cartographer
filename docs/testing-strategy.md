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

Sprint 3 adds a bounded application-observation layer while preserving the
separation between deterministic contracts, browser execution, and human
authority.

## Current evidence

```text
66 tests passing with Playwright Chromium
controlled browser readiness transition verified
```

The full result includes regression coverage for Playwright editability
semantics on both non-editable buttons and native editable inputs.

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
- controlled Chromium execution against a loopback reference page.

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
python -m pytest tests/unit/context/test_schema.py `
    tests/unit/intake/test_intake_schema.py `
    tests/unit/observation/test_schema.py
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
- LLM requests, parsing, latency, cost, or semantic quality,
- POM proposal or generated source code,
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
