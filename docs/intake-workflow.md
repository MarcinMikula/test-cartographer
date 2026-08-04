# Human-guided intake workflow — version 0.1

## Purpose

Sprint 2 adds a deterministic workflow for collecting and reviewing the
human-answerable part of one `ContextBundle`.

The workflow is deliberately implemented without an LLM.

It answers:

> Can a structurally valid but incomplete process context drive a small,
> resumable, measurable questionnaire without requiring the user to understand
> the JSON schema?

The implementation lives under:

```text
src/test_cartographer/intake/
```

The command-line entry point is:

```text
test-cartographer intake ...
```

## Starting boundary

The intake does not create a complete `ContextBundle` from nothing.

It starts from a bundle that is already structurally valid and contains the
minimum application, process, page, element, action, and evidence shell needed
by context contract version `0.1`.

That shell may still contain:

- unknown business risk,
- unknown expected outcome,
- explicit open questions,
- unresolved conflicts,
- inferred or unobserved application evidence.

This boundary avoids inventing browser structure during a human-only sprint.
Creating the shell from browser evidence belongs to later work.

## Why deterministic question selection comes first

A free-form LLM interviewer could:

- ask useful questions,
- rephrase unclear prompts,
- interpret long answers,
- combine several facts from one response.

It could also:

- skip required information,
- ask irrelevant questions,
- repeat itself,
- treat an inference as fact,
- hide whether the workflow or the model caused a result.

Sprint 2 therefore uses explicit rules:

```text
current ContextBundle
→ stage-specific readiness issues
→ ordered question definitions
→ validated answer action
→ immutable context update
→ new readiness assessment
```

This establishes the durable state transitions before adding probabilistic
conversation.

## Intake targets

The first workflow can ask about:

- process purpose,
- business or product risk,
- user role,
- preconditions,
- expected outcomes,
- explicit open questions,
- conflict resolutions.

It intentionally does not ask the user to supply:

- DOM structure,
- accessibility roles,
- locator values,
- page/component ownership discovered from code,
- network evidence,
- browser state transitions.

Those belong to guided application observation.

## Question phases

### Collection phase

A question is generated when a supported knowledge field is:

- `unknown`,
- `inferred`,
- `stale`,
- `conflicting`.

Explicit `OpenQuestion` items and unresolved `Conflict` items also enter the
collection queue.

The queue uses a stable order:

```text
unresolved conflicts
→ purpose
→ risk
→ role
→ preconditions
→ expected outcomes
→ explicit open questions
```

The order is deterministic for the same context.

### Review phase

When no collection question remains, the workflow creates review questions for
human-answerable values still marked:

- `provided`,
- `observed`.

A normal text answer from the collection phase becomes `PROVIDED`.

A later `:confirm` response changes the displayed value to `CONFIRMED` and adds
a separate human evidence record.

This keeps two different actions visible:

```text
supply a value
!=
review and accept a value
```

A correction entered during review remains `PROVIDED` and is presented again
for confirmation.

## Answer actions

### Provide

Any non-command text is treated as a supplied answer.

Result for a supported `KnowledgeText` field:

```text
status = PROVIDED
value = user text
evidence = new HUMAN evidence item
```

The interaction record does not duplicate the answer text. The value already
lives in the context, while the interaction log records the action, target,
timestamps, and active duration.

### Confirm

Command:

```text
:confirm
```

Available only when the question displays an existing value.

Result:

```text
status = CONFIRMED
value = unchanged
existing evidence = retained
new HUMAN confirmation evidence = appended
```

### Unknown

Command:

```text
:unknown
```

For a knowledge field, the value becomes explicit `UNKNOWN` with no selected
value or evidence reference.

The current question is deferred for the active session to avoid an immediate
loop.

If a required unknown remains and no other non-deferred question exists, the
session becomes `BLOCKED`.

### Skip

Command:

```text
:skip
```

The context is not changed.

The question is deferred for the active session.

A skipped review question may leave a warning while allowing human intake to
complete. A skipped required question leaves a blocker and can make the session
`BLOCKED`.

### Quit

Command:

```text
:quit
```

The current question is not answered. The session is saved as `PAUSED` and can
be resumed later.

## Open-question handling

Context contract version `0.1` represents an open question but has no generic
structured answer field.

Sprint 2 therefore handles a supplied answer by:

1. creating a human evidence item whose summary retains the question and
   answer,
2. removing the resolved `OpenQuestion` from the active open-question list,
3. preserving the original prompt and action in the intake interaction log.

This is intentionally bounded.

It proves resolution and traceability for the reference workflow, but it does
not prove that arbitrary answers are mapped into the correct business-rule or
domain structure.

A later contract version may introduce a richer resolved-question model if real
use cases demonstrate the need.

## Session contract

`IntakeSession` version `0.1` contains:

```text
IntakeSession
├── schema_version
├── session id
├── state
├── started_at / updated_at
├── embedded ContextBundle
├── interaction history
└── deferred question IDs
```

The embedded context makes the session self-contained and prevents the session
from depending on a separately edited context file while it is active.

The generated schema is committed at:

```text
schemas/intake-session-v0.1.schema.json
```

## Session states

### `active`

At least one current, non-deferred collection or review question exists.

### `paused`

The user explicitly quit or interrupted the CLI. The context and interaction
history are preserved.

### `complete`

No current non-deferred question remains and human-intake assessment has no
blockers.

A completed intake may still have:

- review warnings deliberately skipped by the user,
- browser-only adaptation blockers,
- no runnable automation.

### `blocked`

Human-intake blockers remain, but all currently generated questions are
deferred.

The user can reopen them with:

```powershell
test-cartographer intake run `
    --session <session.json> `
    --retry-deferred
```

## Intake assessment versus full readiness

`assess_intake()` filters the full readiness report to human-answerable issue
codes:

- `purpose_not_confirmed`,
- `risk_not_confirmed`,
- `role_not_confirmed`,
- `precondition_not_confirmed`,
- `outcome_not_confirmed`,
- `conflict_unresolved`,
- `blocking_question_open`,
- `nonblocking_question_open`.

It deliberately excludes browser and automation issues such as:

- `primary_locator_missing`,
- `primary_locator_not_observed`,
- unusable observed step state.

The CLI displays both reports so that a successful intake cannot be confused
with full framework-adaptation readiness.

## Evidence creation

Each supplied or confirmed knowledge answer creates local evidence with:

- `source_type = human`,
- a session and question reference,
- a short summary,
- an answer timestamp,
- inherited sensitivity,
- a SHA-256 digest of the answered or confirmed value.

The digest is traceability metadata, not authenticity proof.

`UNKNOWN` and `SKIP` do not create evidence pretending to support a value.

## Metrics

Each recorded interaction stores:

- sequence number,
- question ID and kind,
- prompt,
- target path,
- answer action,
- asked and answered timestamps,
- active response seconds.

The session calculates:

- total interaction count,
- provided count,
- confirmed count,
- unknown count,
- skipped count,
- total active seconds.

The metrics do not yet include:

- setup time outside the CLI,
- reading or review time after export,
- corrections made directly in JSON,
- subjective difficulty,
- perceived confidence,
- comparison with manual or general-LLM workflows.

## Persistence

The session is saved:

- after creation,
- after every accepted answer action,
- when paused,
- after resume-state changes.

Output is deterministic, UTF-8, indented JSON with a trailing newline.

## CLI commands

### Start

```powershell
test-cartographer intake start `
    --context testdata/context/incomplete/public_search_flow.json `
    --session .test-cartographer/public-search-session.json `
    --session-id intake_public_search
```

### Run or resume

```powershell
test-cartographer intake run `
    --session .test-cartographer/public-search-session.json
```

### Retry deferred questions

```powershell
test-cartographer intake run `
    --session .test-cartographer/public-search-session.json `
    --retry-deferred
```

### Status

```powershell
test-cartographer intake status `
    --session .test-cartographer/public-search-session.json
```

### Export context

```powershell
test-cartographer intake export `
    --session .test-cartographer/public-search-session.json `
    --context .test-cartographer/public-search-context.json
```

## Sprint 2 acceptance evidence

The controlled incomplete fixture produces this sequence:

```text
collect risk
→ collect expected outcome
→ answer explicit matching-rule question
→ review risk
→ review expected outcome
→ human intake complete
```

After confirmation:

```text
human-intake blockers = 0
human-intake warnings = 0
full adaptation blockers = 1
```

The remaining blocker is the intentionally inferred primary locator. Sprint 2
does not ask the user to convert it into observed application evidence.

## Known boundary

The current workflow proves deterministic state handling for one controlled
shell.

It does not prove:

- greenfield process creation,
- question quality for real projects,
- semantic interpretation of long answers,
- automatic conflict discovery,
- browser capture,
- LLM assistance,
- POM generation,
- time savings or usability advantage.


## Sprint 8 extension — live guided intake

The deterministic Sprint 2 engine remains the authority for gaps, answers,
evidence, state transitions, and completion. Sprint 8 wraps it with two local
LLM planning rounds:

```text
collection candidates → LLM order/wording → human answers
review candidates → LLM order/wording → human confirmation
```

A `MinimalContextSeed` can now create the starting session. The new application
and process metadata questions are application name, environment, starting URL,
and process name. Purpose, risk, role, preconditions, and outcomes retain the
explicit confirmation gate.

Use `intake guide` only with a local profile. The model output never directly
updates the context; every update still passes through `record_answer()`.
