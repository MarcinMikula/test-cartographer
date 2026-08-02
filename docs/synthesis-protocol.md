# Bounded LLM synthesis protocol

## Status

Implemented in Sprint 4.

The current implementation validates the complete request, replay, parser,
proposal-validation, and human-review boundary without calling a live model.

## Purpose

Sprint 4 introduces the first LLM-facing boundary in TestCartographer.

The boundary does not send an arbitrary `ContextBundle`, browser session, DOM,
prompt history, or repository to a provider. It creates one explicit,
provider-neutral projection containing only the context needed to propose Page
Object Model boundaries for one process.

```text
ready ContextBundle
→ authorized field projection
→ deterministic prompt
→ provider-neutral adapter
→ raw output
→ strict parser
→ deterministic proposal validation
→ human review
→ accepted or rejected proposal
```

The accepted result is still a logical proposal. It does not modify
`qa-automation-framework` or prove that generated code would run.

## Contracts

Sprint 4 adds three versioned contracts.

### `BoundedSynthesisRequest` version `0.1`

The request contains:

- application and process identifiers,
- confirmed application, environment, process, purpose, risk, and role values,
- confirmed preconditions,
- ordered process steps,
- observed expected states,
- confirmed outcomes,
- observed pages, reusable components, elements, and primary locators,
- symbolic test-data requirements,
- minimized evidence summaries,
- explicit excluded fields,
- explicit prohibited claims,
- requested proposal schema version.

It does not contain:

- base URLs,
- page routes,
- credentials or secret values,
- raw evidence source references,
- evidence hashes or capture timestamps,
- free-form knowledge notes,
- confidence values for inferred material,
- raw pages, DOM, HTML, screenshots, traces, or browser state,
- repository files or arbitrary adapter metadata.

Only `CONFIRMED` and `OBSERVED` knowledge is eligible. The default request
allows `PUBLIC` and `INTERNAL` values. Required `CONFIDENTIAL` or `RESTRICTED`
values cause request construction to fail rather than being silently sent.

### `PomProposal` version `0.1`

The structured proposal contains logical, source-linked concepts:

- Page Object proposals linked to authorized page IDs,
- component-object proposals linked to authorized component IDs,
- methods linked to authorized process steps,
- actions linked to authorized elements, locators, and symbolic test data,
- symbolic fixture requirements,
- one test intent linked to the process,
- assertions linked to confirmed outcomes,
- optional human-review questions,
- explicit claim flags.

The proposal does not contain repository paths, generated source code, secret
values, execution results, or a claim that the target framework has already
been inspected.

### `SynthesisRun` version `0.1`

A run preserves:

- the exact bounded request,
- a SHA-256 digest of the deterministic prompt,
- the exact raw adapter output, including leading or trailing whitespace,
- the parsed proposal when parsing succeeds,
- protocol failure when parsing fails,
- deterministic validation issues,
- human review status and timing.

## Request construction

`build_synthesis_request()` first requires full adaptation readiness.

A completed human intake is insufficient if a primary locator is still
`INFERRED`. The reference request is created from the post-Sprint-3 context in
which accepted browser evidence has promoted every primary locator to
`OBSERVED`.

Request construction fails when:

- readiness has blockers,
- a required field is not `CONFIRMED` or `OBSERVED`,
- a required value exceeds the allowed sensitivity set,
- referenced evidence is missing,
- a required primary locator is missing.

The request records excluded paths and reasons so minimization remains visible
and reviewable.

## Deterministic prompt

`render_synthesis_prompt()` serializes only the bounded request with sorted JSON
keys and fixed instructions.

There is no hidden conversation memory, arbitrary system context, repository
content, or browser state. The same request produces the same prompt text.

The prompt requires:

- exactly one JSON object,
- proposal schema version `0.1`,
- no Markdown fences or commentary,
- only authorized identifiers and values,
- no prohibited claims,
- treatment of the output as a proposal requiring validation and review.

## Adapter boundary

`SynthesisAdapter` exposes one operation:

```python
def execute(request: BoundedSynthesisRequest, prompt: str) -> str:
    ...
```

Sprint 4 implements only `ReplaySynthesisAdapter`.

Replay records the exact request and prompt and returns a stored raw output.
This proves the protocol and pipeline without claiming live-provider
compliance, reliability, latency, cost, privacy, or semantic quality.

A live adapter is deliberately deferred.

## Strict parsing

`parse_pom_proposal()` rejects:

- empty output,
- Markdown code fences,
- non-object roots,
- invalid JSON,
- duplicate object keys at any nesting level,
- schema-version drift,
- missing required fields,
- unexpected fields,
- invalid identifiers, class names, method names, or enums.

These are protocol failures. They are distinct from a structurally valid
proposal that makes unsupported or unauthorized choices.

Raw output is preserved on both success and failure.

## Deterministic proposal validation

A parsed proposal is validated against the exact request.

The validator checks:

- request and context identity,
- exact authorized page and reusable-component coverage,
- method ownership,
- exactly-once process-step coverage,
- action-kind consistency,
- target-element consistency,
- primary-locator consistency,
- symbolic test-data consistency,
- fixture references and absence of secret values,
- test references to every proposed method and fixture,
- confirmed-outcome assertion coverage,
- assertion-element consistency,
- prohibited claim flags,
- validity of open-question references.

A proposal may be structurally valid yet receive
`VALIDATION_REJECTED`. For example, it may:

- reference an invented locator,
- omit a process step,
- assert an unknown outcome,
- include secret values,
- claim successful execution or repository fit.

This is a substantive proposal rejection, not a parser failure.

## Human review

A validated proposal starts as:

```text
READY_FOR_REVIEW
```

Only that state may be reviewed.

The reviewer may produce:

- `ACCEPTED`, with optional rationale,
- `REJECTED`, with a mandatory reason.

Protocol failures and deterministically rejected proposals cannot be accepted
through the review function.

Acceptance does not write files. It records that the logical POM boundaries are
approved as input for Sprint 5 repository inspection and framework mapping.

## CLI workflow

Build a minimized request:

```powershell
test-cartographer synthesize request `
    --context testdata/context/synthesis_ready/public_search_flow.json `
    --request .test-cartographer/public-search-request.json `
    --request-id synreq_public_search_local
```

Replay a stored raw output:

```powershell
test-cartographer synthesize replay `
    --request .test-cartographer/public-search-request.json `
    --raw-output testdata/synthesis/raw/valid_public_search.json `
    --run .test-cartographer/public-search-run.json `
    --run-id synrun_public_search_local
```

The committed reference output uses request ID `synreq_public_search`. When a
different request ID is used, the replay fixture must be updated to reference
that exact ID. The validator intentionally rejects mismatches.

Inspect status:

```powershell
test-cartographer synthesize status `
    --run .test-cartographer/public-search-run.json
```

Accept a validated proposal:

```powershell
test-cartographer synthesize review `
    --run .test-cartographer/public-search-run.json `
    --decision accepted `
    --reason "POM boundaries are acceptable for framework mapping." `
    --review-seconds 15
```

## Reference verifier

Run:

```powershell
python scripts/verify_synthesis_replay.py
```

The verifier proves:

- a ready context can be projected into a bounded request,
- excluded URL, route, raw-source, note, and hash values do not enter the prompt,
- replay receives the exact request and deterministic prompt,
- strict parsing succeeds for the reference JSON,
- deterministic proposal validation succeeds,
- the proposal remains pending before human review,
- explicit acceptance creates an accepted run,
- no live provider is used,
- no repository file is modified.

## What Sprint 4 proves

- The first LLM-facing input can be explicit, minimized, versioned, and
  provider-neutral.
- Raw model output can be preserved exactly.
- Protocol failures can remain separate from substantive proposal rejection.
- POM proposals can be linked deterministically to confirmed context,
  observations, steps, locators, data requirements, and outcomes.
- Prohibited claims can be represented and rejected deterministically.
- Human acceptance can remain a separate authority stage.
- The complete flow can be replayed without a live provider.

## What Sprint 4 does not prove

- live-provider compliance with the protocol,
- semantic quality across varied applications,
- superiority of one model or provider,
- prompt-injection resistance,
- safe transmission of enterprise context,
- acceptable latency or cost,
- correct framework-specific file placement,
- generated source-code correctness,
- execution success,
- Salesforce readiness,
- usability or time savings.

These limits are intentional gates to later sprints.


## Sprint 5 handoff

An accepted `SynthesisRun` is now a required input to the read-only adaptation
planner. Acceptance does not supply file paths. Sprint 5 combines the logical
proposal with a separately approved `WorkspaceProfile` and exact
`FrameworkSnapshot`, then requires another human decision over the resulting
`AdaptationPlan`.

This preserves the distinction between logical architecture approval and
repository-placement approval.
