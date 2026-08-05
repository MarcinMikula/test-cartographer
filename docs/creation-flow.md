# Fixture-assisted integrated Creation Flow

Sprint 10 connects the previously accepted creation boundaries into one bounded,
fixture-assisted reference workflow.

```text
one short request
→ two live local-LLM intake plans
→ fixture-supplied human answers and confirmations
→ bounded Chromium discovery
→ one live local-LLM ambiguity question
→ fixture-supplied human candidate selection
→ accepted ContextBundle
→ fixture-supplied synthesis handoff review
→ strict POM proposal protocol
→ read-only repository plan
→ fixture-supplied patch review
→ snapshot-bounded sandbox
→ one collected and passing Playwright test
→ effort and provenance summary
```

## What Sprint 10 proves

The Creation Flow engine works from beginning to end when all required human
inputs and authority decisions are supplied through controlled fixtures. The
flow integrates real local-model calls, a real Chromium scan, strict context and
proposal contracts, repository-aware planning, source delivery, and a real
Playwright execution.

The result is an integration proof, not yet a human-operated product flow.

```text
Creation mechanics verified: true
Ready for human-trigger integration: true
Interactive human trigger used: false
Ready for external user demonstration: false
```

## What is live

The reference run performs three real local-Ollama calls:

1. collection-question planning,
2. confirmation-question planning,
3. phrasing one browser ambiguity.

The model may order or phrase allowlisted questions. It may not provide facts,
confirm facts, select a DOM candidate, accept a proposal, choose repository
write targets, or approve generated source.

The browser scan, repository inspection, generated patch, sandbox application,
compile, pytest collection, and Playwright test execution are also real.

## What is fixture-assisted

For repeatability, the verifier supplies the human side from reference data:

- 9 answers,
- 5 intake confirmations,
- 4 synthesis-handoff confirmations,
- 1 ambiguity resolution,
- 4 review decisions,
- 23 represented human actions in total.

These operations exercise real state transitions and authority gates, but no
operator types an answer, chooses a candidate, or approves an artefact during
the automated acceptance run.

The phrase `human acceptance` in verifier output means that the acceptance
transition was executed with fixture-supplied human authority. It does not mean
that the person running the setup made that decision interactively.

## What remains deterministic

POM synthesis in this reference flow uses a deterministic template that emits
one raw JSON proposal through the existing strict parser and semantic validator.
This is deliberately reported as a deterministic synthesis call, not as a live
LLM generation. The point of Sprint 10 is orchestration of accepted boundaries,
not silently expanding model authority.

The adaptation plan, generated Python, preflight hashes, sandbox materialization,
patch application, compile, pytest collection, and execution are deterministic.

## Synthesis handoff review

Sprint 10 exposed an integration gap between prior readiness boundaries. After
guided discovery, the context was ready according to the general
`ContextBundle` readiness rules, but four synthesis-required values still had
status `PROVIDED`:

- application name,
- environment,
- process name,
- inherited intent of `step_open_catalog`.

The synthesis request accepts only `CONFIRMED` or `OBSERVED` values. Sprint 10
therefore adds a separate human handoff review that confirms only these four
values and records one non-secret evidence item. The synthesis contract was not
weakened. In the reference verifier, these confirmations are fixture-supplied.

## Human trigger delivered in Sprint 11

Sprint 11 connects a real user to the already implemented entry and decision
points:

```text
user enters the short request
→ Cartographer displays a question and waits
→ user provides or confirms context
→ visible browser discovery runs
→ Cartographer displays ambiguous candidates and waits
→ user selects the intended element
→ Cartographer displays review artefacts and waits for approval
→ the existing engine continues to the passing test
```

The delivered interface is an interactive CLI with a visible browser and real
blocking prompts. It preserves the same contracts and authority boundaries.
It does not yet support resume from every downstream review stage or in-flow
editing of generated artefacts. See
[`interactive-creation-flow.md`](interactive-creation-flow.md).

## Privacy and claims

`CreationFlowRun` stores counts, durations, IDs, and proof flags. It does not
store raw prompts, raw model responses, or human answer values. The underlying
`IntakeSession` remains the explicit local source of human-provided context.

The flow does not claim a percentage of saved effort. It creates the evidence
needed for a later comparison against manual discovery and Playwright Codegen.

## Honest wording after Sprint 10

The project can currently be presented as:

> TestCartographer has a working fixture-assisted Creation Flow engine. Given
> explicit human context and decisions, it can connect bounded local-LLM
> assistance, browser discovery, context mapping, repository planning, reviewed
> source delivery, and a passing Playwright test in one traceable workflow.

The Sprint 10 artefact itself must not be presented as a human-operated demo.
Sprint 11 adds a separate operator-driven acceptance path; only a completed
Sprint 11 operator session may make the narrow controlled-demo claim.

The central conclusion is:

> The Creation Flow engine works from beginning to end. The next step is not to
> build a new engine, but to connect a real human to the existing entry and
> decision points.
