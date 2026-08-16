# Live local-LLM guided intake

## Purpose

Sprint 8 provides the first creation entry point that does not require a
pre-filled `ContextBundle`.

```text
one short human request
→ MinimalContextSeed
→ structurally valid unknown-heavy ContextBundle
→ deterministic gap catalogue
→ local LLM interview plan
→ human answers and confirmation
→ ready for guided process discovery
```

The LLM improves the interaction. It does not become the authority for stored
application or business facts.

## Minimal seed

`MinimalContextSeed` stores only:

- a seed and context ID,
- a title,
- the human's initial automation request,
- timestamp and sensitivity.

`build_minimal_context()` creates the minimum graph needed by context schema
`0.1`: one placeholder page, one placeholder element and locator, one initial
navigation step, and one expected outcome. Unknown fields remain `UNKNOWN`.
The initial request is stored as `PROVIDED` process intent with human evidence.

The builder does not infer:

- application name,
- environment,
- starting URL,
- process name,
- purpose,
- risk,
- role,
- precondition,
- expected outcome,
- page structure, selectors, or element semantics.

## Question authority

The deterministic intake rules create the allowlisted candidate set. The model
receives candidate IDs, target paths, base prompts, a minimized summary of known
fields, and explicit prohibitions.

The model may:

- order all supplied questions,
- rephrase each question for the operator,
- explain why the question matters,
- recommend a short answer shape.

The model may not:

- omit or duplicate a candidate,
- invent a question ID or target path,
- answer a question,
- mutate `ContextBundle`,
- confirm a value,
- request passwords, tokens, cookies, or secret values,
- declare adaptation readiness.

Every returned plan is parsed strictly and must contain the exact candidate set.

## Two phases

### Collection

The first model call plans the unknown-field interview. Human text answers are
applied through the existing Sprint 2 intake engine and become `PROVIDED`
knowledge with human evidence.

### Review

After required collection is resolved, the deterministic rules expose review
questions only for business-critical values. A second model call plans the
confirmation interview. Only explicit `:confirm` actions produce `CONFIRMED`
knowledge.

Application name, environment, starting URL, and process name are usable as
human-provided metadata and do not require the same confirmation gate as
purpose, risk, role, preconditions, and outcomes.

## Local Ollama boundary

Sprint 8 implements one live provider: local Ollama.

The profile requires:

- `http` scheme,
- loopback host (`localhost`, `127.0.0.1`, or `::1`),
- no URL credentials, query, fragment, or nested API path,
- a non-cloud model name,
- structured output,
- raw-prompt and raw-response persistence disabled.

The adapter checks `/api/version` and `/api/tags`, then calls `/api/chat` with:

- `stream: false`,
- `think: false`,
- a JSON Schema in `format`,
- configured temperature and seed.

No cloud fallback exists.

## Minimized model input

The prompt may contain:

- the initial request when its sensitivity is allowed,
- known application and process text whose sensitivity is allowed,
- candidate IDs, kinds, paths, and base prompts,
- a safe current value for review when allowed.

The starting URL value is always excluded from model input. The model can ask
which URL discovery should use, but it does not receive or repeat that value in
a later review prompt.

## Persistence

`GuidedIntakeRun` stores:

- provider and model,
- phase and question IDs,
- prompt and response SHA-256 values,
- character counts,
- latency,
- whether a live provider was used.

It does not store:

- raw prompts,
- raw responses,
- generated question wording,
- initial-request text,
- human answer values,
- the application URL.

Human answers remain in the local `IntakeSession.context`, where existing
sensitivity and evidence rules apply.

## Readiness

Sprint 8 introduces a stage-specific result:

```text
ready_for_guided_discovery
```

It requires:

- a complete intake session,
- no remaining human-intake questions,
- no human-intake warnings,
- at least one provider planning turn.

It does not mean `assess_readiness(context).ready` is true. Placeholder pages,
elements, steps, states, and locators deliberately remain technical blockers for
Sprint 9.

## CLI

Create the starting context and session:

```powershell
test-cartographer intake seed `
    --seed testdata/guided_intake/seed/product_search.json `
    --context .test-cartographer/sprint-8/context.json `
    --session .test-cartographer/sprint-8/session.json
```

Run the local interview:

```powershell
test-cartographer intake guide `
    --seed testdata/guided_intake/seed/product_search.json `
    --session .test-cartographer/sprint-8/session.json `
    --profile testdata/guided_intake/profile/ollama_local_qwen.json `
    --run .test-cartographer/sprint-8/run.json
```

Inspect readiness:

```powershell
test-cartographer intake guide-status `
    --session .test-cartographer/sprint-8/session.json `
    --run .test-cartographer/sprint-8/run.json
```

## Verification

Two verifiers exist:

- `verify_guided_intake_replay.py` proves deterministic orchestration without a
  model,
- `verify_live_guided_intake.py` requires a real installed local Ollama model
  and performs one collection-plan call and one confirmation-plan call.

The live verifier uses controlled human answers so it tests model integration,
not model authority over facts.

## Current limits

- only Ollama is live; other providers remain unimplemented,
- question planning and bounded semantic-action proposals are model-assisted,
- arbitrary free-text answer interpretation is not implemented,
- no retry or repair loop exists for repeated invalid model output,
- an existing run can resume only with the same profile, seed, session, and context IDs,
- model quality is not benchmarked,
- the seed still creates technical placeholders because `ContextBundle` 0.1 is
  a complete graph contract,
- guided browser discovery starts in Sprint 9,
- time savings are not yet measured.

## Local inference timeout

The live verifier defaults each `/api/chat` call to 600 seconds. Local structured output can be much slower than a one-token smoke prompt, especially when a quantized model is split between CPU and GPU and must satisfy a multi-item JSON Schema. The timeout is an explicit acceptance parameter rather than an assumption about operator hardware. Values above 600 seconds remain rejected by `GuidedIntakeProfile`.


## Bounded generation and model residency

The live provider uses separate limits for separate failure modes:

- `timeout_seconds` limits how long the HTTP caller waits,
- `max_output_tokens` limits generation to 768 tokens by default,
- JSON Schema limits each generated question to 180 characters and each reason
  to 240 characters,
- `keep_alive_seconds` keeps the model resident for 900 seconds by default so
  the collection and review turns do not race against automatic unloading.

Before the first guided `/api/chat` request, the provider sends an empty local
`/api/generate` request to preload the selected model. The verifier prints the
start and completion of each planning turn. Streaming remains disabled because
the response must be validated as one complete JSON document, but the operator
can now distinguish model loading, collection planning, and review planning.

The timeout is not treated as an output budget. Increasing it does not justify
unbounded generation.

## Material-intent review

Guided intake now uses a bounded review-planning turn after generic collection.
The model compares the unchanged initial request with every current review value
and classifies each allowlisted candidate through its answer shape:

- `confirmation` means the current value is ready for human confirmation;
- `short_phrase`, `sentence`, or `bullets` means the candidate requires a
  targeted clarification.

The model still cannot add, remove, or retarget questions. Only non-confirmation
candidates are asked again, and every answer passes through `record_answer()`.
After corrections, the review is replanned within the existing round budget.

Before discovery, the operator sees the initial request beside the structured
summary and explicitly confirms that all material intent is preserved. Missing
or unresolved intent therefore cannot disappear merely because a provider plan
was fluent. Invalid output, unknown/deferred required context, or round-budget
exhaustion stops the flow fail-closed.

The actual operator-facing clarification prompt is retained in the normal
`IntakeInteraction` record. Raw provider prompts and responses remain excluded.


## Human-reviewed external target proposal

After material-intent confirmation, a non-heading external flow may make one
separate structured Ollama call that proposes two through six same-page semantic
actions. The provider is limited to the existing action/role vocabulary and
symbolic non-secret data references. It cannot provide selectors, locators,
concrete data values, additional pages, prices, counts, or application facts.

The proposal persists model, latency, hashes, and character counts without raw
prompts or responses. It remains ready_for_review and has no browser authority
until the operator accepts it. The operator may edit fields, add or remove
bounded steps, reject it, or quit. Every candidate is revalidated before it can
become reviewed_targets.

There is no silent retry, cloud fallback, or automatic acceptance. Invalid model
output fails closed and remains evidence about the configured provider.
