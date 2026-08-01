# Testing strategy

## Purpose

TestCartographer will combine deterministic software with uncertain external
inputs such as human answers, browser observations, project documents, and LLM
outputs.

The testing strategy must keep those concerns separate.

```text
deterministic contracts and validators
→ tested with exact fixtures and assertions

external interpretation and observation
→ tested later with controlled evidence and realistic cases
```

Sprint 1 tests only the deterministic local context contract.

## Current test layers

### Contract unit tests

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

### Readiness unit tests

Location:

```text
tests/unit/context/test_readiness.py
```

They prove:

- a complete fixture is ready,
- an incomplete fixture remains valid but blocked,
- a conflicting fixture remains valid but blocked,
- readiness reports are serializable.

### Persistence unit tests

Location:

```text
tests/unit/context/test_io.py
```

They verify:

- load/save round trip,
- deterministic output,
- UTF-8 newline-terminated files.

### Schema snapshot tests

Location:

```text
tests/unit/context/test_schema.py
```

They verify:

- committed JSON Schema matches the Pydantic model,
- the contract root rejects additional properties,
- schema version `0.1` is fixed.

## Current fixture strategy

Fixtures represent distinct semantic states rather than many arbitrary JSON
examples.

### Complete

```text
testdata/context/valid/public_search_flow.json
```

Expected:

```text
structurally valid
+ ready
```

### Incomplete

```text
testdata/context/incomplete/public_search_flow.json
```

Expected:

```text
structurally valid
+ explicit unknowns
+ readiness blockers
```

### Conflicting

```text
testdata/context/conflicting/public_search_flow.json
```

Expected:

```text
structurally valid
+ preserved disagreement
+ readiness blockers
```

### Invalid

```text
testdata/context/invalid/missing_evidence_reference.json
```

Expected:

```text
rejected during structural validation
```

This matrix prevents a common false equivalence:

```text
not ready != malformed
```

## Test command

```powershell
python -m pytest
```

Sprint 1 expected result:

```text
23 passed
```

## Test quality rules

- Tests use public package functions where possible.
- Fixture paths are explicit.
- Tests do not call a network, browser, database, or LLM.
- A test asserts one contract behaviour or closely related invariant.
- Invalid examples fail for a deliberate reason.
- Tests do not mock Pydantic internals.
- Generated JSON Schema is compared structurally, not as formatting text.
- A passing suite does not justify claims outside the deterministic contract.

## What current tests prove

The suite proves that:

- supported JSON is parsed into a strict typed model,
- malformed relationships are rejected,
- unknown and conflicting knowledge can be represented honestly,
- readiness assessment is deterministic for current rules,
- local serialization is stable,
- the committed JSON Schema matches the implementation.

## What current tests do not prove

The suite does not prove:

- the contract contains all information needed for a real POM,
- users can answer the required questions efficiently,
- browser evidence can populate the model correctly,
- locator candidates are stable in real applications,
- an LLM can map context into good architecture,
- business facts are correct,
- sensitive information is safe,
- TestCartographer saves time,
- the framework adapter will produce runnable tests.

## Sprint 2 testing direction

Human-guided intake should add tests for:

- question selection from readiness gaps,
- deterministic answer-to-context mapping,
- preserving unknown answers,
- rejecting contradictory user updates unless recorded as conflicts,
- resuming an incomplete intake,
- final review before confirmation,
- interaction metrics such as question count and active duration.

The first intake implementation should use scripted answers and replayable
sessions before any free-form LLM interviewer is added.

## Later browser-observation testing

A guided browser slice should separate:

```text
browser capture correctness
from
semantic mapping quality
```

Potential deterministic checks:

- captured page URL and timestamp,
- selected DOM/accessibility attributes,
- redaction before persistence,
- action/element/page reference mapping,
- reproducible capture fixtures,
- destructive-action restrictions.

Realistic application tests should be added only after a controlled local
fixture proves the capture boundary.

## Later LLM testing

A live LLM should not be the first test double for the protocol.

Expected progression:

1. deterministic request construction,
2. strict structured-result parsing,
3. replay adapter using stored raw outputs,
4. hand-labelled good, bad, incomplete, and overconfident outputs,
5. bounded live-provider smoke tests,
6. comparative evaluation against realistic alternatives.

LLM fluency must not be treated as evidence of architecture or domain
correctness.

## End-to-end validation

A future end-to-end evaluation should use the same:

- target application,
- selected process,
- starting `qa-automation-framework`,
- acceptance criteria,
- reviewer,
- quality rubric.

Compare:

```text
manual adaptation
vs.
DevTools + Playwright Codegen + general LLM
vs.
TestCartographer
```

Measure:

- correctness,
- POM quality,
- unsupported assumptions,
- human corrections,
- setup time,
- active user time,
- time to first runnable test,
- maintenance time after a controlled change,
- LLM cost and latency,
- perceived difficulty and trust.

## CI boundary

Sprint 1 does not add GitHub Actions.

CI becomes useful after the repository establishes its first stable local
installation workflow. Until then, local deterministic tests are the current
evidence gate.
