# Human-triggered interactive Creation Flow

Sprint 11 connects a real operator to the Creation Flow engine proven in Sprint
10. It does not replace intake, discovery, synthesis, repository planning,
source delivery, or execution. It makes the existing authority boundaries
blocking and visible.

```text
operator enters one short automation request
→ local LLM orders and phrases one bounded collection plan
→ bootstrap context is collected once at the beginning of the run
→ process-specific context is collected once for the current process
→ one context summary is confirmed or a selected field is edited
→ headed Chromium shows bounded candidate labels
→ operator resolves one browser ambiguity
→ operator accepts or rejects discovery
→ operator confirms the synthesis handoff using the already collected context
→ operator reviews and accepts or rejects the POM proposal
→ operator reviews and accepts or rejects the repository plan
→ every exact source change is rendered in full with no omitted lines
→ operator reviews and accepts or rejects the exact source patch
→ operator triggers isolated framework execution
→ one generated Playwright test passes
```

## What changed after Sprint 10

Sprint 10 supplied all human actions from controlled fixtures. Sprint 11 uses
real blocking terminal input for the user-facing path:

- the initial request is typed by the operator,
- intake values are typed by the operator,
- five repeated review prompts are replaced by one aggregate context summary,
- no fixture answer fills a missing human decision,
- the discovery browser runs headed,
- the operator chooses the ambiguous candidate,
- review gates wait for explicit acceptance or rejection,
- framework execution requires a separate operator trigger.

The technical engine remains the one already verified in Sprint 10.

## Intake question classes

The interactive flow now distinguishes three question classes.

### Project bootstrap context

Application name, environment, and starting URL are asked at the beginning of
the run. Later stages consume the recorded context instead of asking for the
same values again.

Sprint 11 does not yet persist a reusable project bootstrap profile across
separate runs. A future increment may reuse confirmed bootstrap context until
an operator requests a change or the context becomes stale, conflicting, or
invalid after an environment, framework, provider, model, or authentication
change.

### Process-specific context

Process name, purpose, risk, role, precondition, and expected outcome are
collected for the current process. Once collected, purpose, risk, role,
precondition, and expected outcome are shown together in one summary.

The operator then chooses one of three explicit actions:

```text
Enter or CONFIRM — confirm all displayed process-context values
EDIT             — select one numbered field and replace its value
QUIT             — stop the controlled run
```

A successful aggregate confirmation produces five internal deterministic
`CONFIRM` transitions in `IntakeSession`, but only one real operator action in
`InteractiveOperatorSession`. This preserves evidence and readiness semantics
without pretending that the operator answered five separate prompts.

### Runtime ambiguity and authority review

Runtime questions are asked only when a real ambiguity or authority boundary
exists, such as two tied browser candidates, discovery acceptance, synthesis
handoff, POM review, repository-plan review, source-patch review, or execution.
The pipeline must not reopen already confirmed context merely because control
moves to another module.

## Safe command handling

Single-letter review commands are intentionally not accepted. This prevents an
input such as `C` from being stored accidentally as a business value after an
edit command.

During summary review use full commands:

```text
CONFIRM
EDIT
QUIT
CANCEL
```

Reserved control words are rejected as context values and the operator is
prompted again. Raw operator values are still excluded from the action ledger.

## CLI entry point

```powershell
test-cartographer creation interactive `
    --profile testdata/interactive_creation/profile/public_catalog_human_trigger.json `
    --output-dir .test-cartographer/sprint-11/live `
    --ollama-base-url http://127.0.0.1:11434 `
    --ollama-model qwen2.5-coder:7b `
    --ollama-timeout-seconds 600
```

The current slice is intentionally limited to the controlled public-catalog
search process. Pressing Enter for the starting URL accepts the locally served
reference page. The operator must still inspect the visible page and choose the
candidate that represents the intended process action.

## Operator action ledger

`InteractiveOperatorSession` stores the kind, target, decision category,
timestamps, and active duration of each operator action. It does not store raw
answer values.

The corrected reference flow records 18 real actions:

- 1 initial request,
- 9 intake answers,
- 1 aggregate context-summary confirmation,
- 1 synthesis-handoff confirmation,
- 1 ambiguity selection,
- 4 artefact-review decisions,
- 1 execution trigger.

Edits add extra real actions and are valid. Eighteen is the expected count for
the unchanged reference answers.

The underlying `IntakeSession` still records the five deterministic confirmation
transitions needed to promote the process facts to `CONFIRMED`. The operator
ledger records the single human decision that authorized them.

## Headed browser review

The discovery page remains open while the operator reviews candidates. Bounded
candidate IDs are added as visible labels and as temporary page annotations.
The browser collector still persists only allowlisted structural evidence; it
does not persist page HTML, screenshots, generic text, input values, cookies, or
storage state.

A visible browser is evidence that the operator had an opportunity to inspect
the page. It is not evidence that the selected element is universally correct.
The operator remains responsible for process meaning.

## Separate readiness assessment

The interactive assessment requires all of the following:

```text
operator session complete
interactive human trigger used
fixture answers not used
headed browser used
minimum intake answers present
one aggregate context-summary confirmation present
synthesis handoff confirmed
one ambiguity selected by the operator
all required review decisions recorded
Creation Flow mechanics verified
CreationFlowRun marked interactive and not fixture-assisted
```

A successful reference run reports:

```text
Human-trigger blockers: none
Human trigger verified: true
Ready for external user demonstration: true
```

The Sprint 10 fixture-assisted artefact continues to report external-demo
readiness as false. The new status cannot be enabled by configuration alone.

## Automated verifier versus manual acceptance

`scripts/verify_human_triggered_creation_flow.py` exercises the orchestration
with 18 scripted terminal inputs, a deterministic browser replay, and a local
Ollama-compatible test server. It verifies mechanics, contracts, aggregate
review, safe command handling through unit tests, and downstream execution
without a real user.

That verifier is not the acceptance artefact for Sprint 11.

The Sprint 11 setup must additionally produce a real:

```text
.test-cartographer/sprint-11/live/operator-session.json
.test-cartographer/sprint-11/live/creation-flow-run.json
```

from the operator-driven CLI, headed Chromium, and the configured local Ollama
model.

## Current review behaviour

The process-context summary supports aggregate confirmation or numbered field
editing. The four downstream artefact gates currently support accept or reject. The
source-patch gate renders every source line, target, symbol, and content hash;
a preview with ellipses is not sufficient for an `exact` acceptance claim.
Rejecting aborts the controlled run; in-flow editing and resume from an
arbitrary downstream stage are not implemented yet. A new controlled run is
required after rejection or `QUIT`.

The generated navigation-method docstring describes the method responsibility
(`Open the mapped page...`) instead of copying the operator's initial request
into production-facing source.

The persisted summary separates authority explicitly:

```text
LLM role: intake-question planning and ambiguity clarification only
POM and source generation: deterministic reviewed reference templates
```

If local-model ambiguity wording ends visibly incomplete, TestCartographer
replaces only that wording with a deterministic complete question that retains
the same candidate set and does not select a candidate.

## What Sprint 11 proves

- a real user can trigger the Creation Flow from a short request,
- bootstrap and process context are collected without repeated review prompts,
- the system blocks at every required human authority boundary,
- the user can see the browser evidence used for ambiguity resolution,
- fixture defaults cannot silently complete the interactive path,
- the existing engine can continue from real human decisions to a passing test,
- the final artefact distinguishes operator, LLM, browser, and deterministic
  work,
- exact patch acceptance is based on the full rendered source rather than a
  truncated preview.

## What Sprint 11 does not prove

- persistence and automatic reuse of bootstrap context across separate runs,
- usability for an unbriefed external participant,
- arbitrary application, multi-page, authenticated, or destructive flows,
- in-flow editing of generated POM, plan, or patch,
- resume after every downstream review boundary,
- live LLM POM generation,
- production application of the patch to the original framework,
- quantified savings versus manual discovery or Playwright Codegen,
- enterprise or Salesforce usefulness.

Sprint 11 makes the controlled prototype demonstrable by a real operator. It is
not yet evidence that the product generalizes or saves a fixed percentage of
work.
