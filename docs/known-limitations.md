# Known limitations — thematic index

Things known to be incomplete, unverified, fragile, or outside the current
scope.

These are current project boundaries, not hidden bugs. Full reasoning lives in
`LEARNINGS.md`; this file is a quick map, not a copy.

## Current implementation state

- **The repository implements context and deterministic human intake only.**
  There is no browser integration, LLM protocol, Page Object proposal,
  framework adapter, or runnable generated test.
- **The current evidence is 47 deterministic tests around controlled
  fixtures.** No real-user or real-application evaluation has occurred.
- **The CLI is local and single-user.** It has no authentication, authorization,
  remote service, or team workflow.
- **No CI workflow is configured.** Verification is currently local.

## Context-shell boundary

- **Intake does not start from an empty project.** It requires a structurally
  valid `ContextBundle` containing an application, process, pages, elements,
  steps, and evidence shell.
- **The shell is currently authored as controlled fixture data.** The product
  cannot derive it from a browser, repository, requirement, or questionnaire.
- **Version `0.1` models one process.** Cross-process reuse and shared
  application graphs are unsupported.
- **No schema migration exists.** Only context version `0.1` and session version
  `0.1` are accepted.

## Human intake

- **Question selection is deterministic but narrow.** Only process purpose,
  risk, role, preconditions, expected outcomes, open questions, and conflict
  resolutions are supported.
- **The question catalogue is not configurable.** Rules and wording are coded
  in Python.
- **A free-form LLM interviewer is not implemented.** Long answers are stored as
  supplied text rather than semantically decomposed.
- **Question quality is unvalidated.** The prompts work for controlled fixtures
  but have not been evaluated with real testers or domain experts.
- **`UNKNOWN` and `SKIP` are session-local deferrals.** They prevent immediate
  loops but do not create assignments, reminders, owners, or deadlines.
- **A blocked session requires explicit retry.** There is no guided explanation
  of who should provide the missing information.
- **Review is field-level and single-user.** There is no separation between
  collector, domain reviewer, automation reviewer, and approver.
- **Confirmation records an action, not authority.** The tool does not verify
  identity or permission to confirm a business fact.
- **No undo command exists.** Corrections are made by answering a review
  question with replacement text or by editing/restarting outside the current
  CLI.

## Open-question resolution

- **`OpenQuestion` has no structured answer field.** Sprint 2 stores a supplied
  answer in human evidence, removes the active question, and preserves the
  prompt/action in session history.
- **The answer is not automatically mapped to a business rule or domain
  object.** A future contract version may be needed after real examples.
- **Open-question evidence summaries may contain supplied text.** They remain
  local but can still be sensitive and must not be assumed safe for external
  processing.

## Session persistence

- **Sessions embed a full context copy.** This is convenient and self-contained
  but duplicates data across sessions.
- **Concurrent editing is unsupported.** There is no locking, merge, or conflict
  detection between two session files.
- **Crash recovery is limited to the last successful save.** There is no journal
  or transactional file replacement strategy.
- **No session retention policy exists.** `.test-cartographer/` is ignored by
  Git, but deletion and archival remain user responsibilities.
- **Metrics are derived from recorded interactions.** They are not persisted as
  independent authoritative fields.

## Metrics and usability

- **Active seconds measure prompt-response time only.** They do not include
  setup, documentation reading, external research, JSON inspection, or later
  code review.
- **Piped or automated input may report near-zero active time.** The metric is
  meaningful only for real interactive use.
- **No subjective usability data is collected.** Difficulty, confidence, trust,
  and willingness to reuse remain unmeasured.
- **No baseline exists.** There is no comparison with manual adaptation,
  Playwright Codegen, DevTools, or a general LLM.
- **Question count is not automatically a quality metric.** Fewer questions may
  mean efficient intake or missing context.

## Context model

- **Only text knowledge is authority-aware.** Typed business rules, assertion
  operators, state machines, and structured expected values are not modelled.
- **`UNKNOWN` does not mean not applicable.** There is no separate
  `NOT_APPLICABLE` state.
- **Confidence is not calibrated.** It is stored metadata only.
- **Conflict handling is simple.** One subject, evidence set, and one resolution
  value are supported.
- **Validation checks structure, not truth.** A confirmed false or vague
  statement can still pass.
- **Readiness rules are provisional.** They are not proven sufficient for real
  POM adaptation.

## Evidence and provenance

- **Evidence stores metadata and summaries, not replayable raw sources.** No DOM
  snapshot, screenshot, trace, document, or attachment store exists.
- **Evidence authenticity is unverified.** A SHA-256 digest records content
  consistency but not source trust.
- **Source freshness is not calculated.** Values can be marked stale only by an
  external decision.
- **Conflicts are not discovered automatically.** They must be present in the
  input context or introduced by future acquisition logic.

## Application observation

- **No Playwright dependency or browser runtime is included.** The tool cannot
  open or inspect an application.
- **No locator has been validated against a real page.** Locator values remain
  contract fixture data.
- **No page, component, or element discovery exists.** Ownership is authored in
  the input shell.
- **No screenshot, DOM, accessibility, network, iframe, or Shadow DOM capture
  exists.**
- **No credential or session handling exists.** Future browser work must keep
  secrets outside prompts, context, logs, and source control.
- **Autonomous exploration is out of current scope.** Sprint 3 remains
  human-controlled.

## Security and privacy

- **Sensitivity labels do not enforce policy.** They are descriptive metadata.
- **No redaction or minimization engine exists.** Context and evidence may still
  contain confidential descriptions or URLs.
- **No field is authorized for cloud processing.** There is no external LLM
  request boundary.
- **No threat model exists.** Prompt injection, malicious DOM content, poisoned
  artefacts, and unsafe attachments remain future concerns.
- **No encryption, access control, retention, or deletion workflow exists.**
- **Real enterprise systems must not be used yet.** Salesforce and Jira remain
  deferred until safe handling rules exist.

## LLM use

- **No LLM provider is integrated.** There is no request schema, response
  schema, parser, replay adapter, timeout, retry, or budget control.
- **No LLM claim has been validated.** The project has no evidence that a model
  can interpret captured context or propose maintainable POM boundaries.
- **Local-model support is not promised.** Provider strategy remains open.
- **Cost and latency are unmeasured.**

## Framework adaptation

- **TestCartographer cannot inspect or modify `qa-automation-framework`.**
- **No POM proposal contract exists.** Pages, components, methods, fixtures, and
  tests are not represented as generated proposals.
- **No generated code or reviewable repository diff exists.**
- **No architecture validator checks proposed automation.**
- **No test has been generated or executed.**
- **Independence from a live LLM remains a requirement, not demonstrated
  evidence.**

## Scope boundaries

- **Initial scope is UI/POM only.** API and Service Object Model adaptation are
  parked.
- **Playwright, Python, and pytest are the intended first stack.** Browser
  support is not implemented yet.
- **One process at a time is the current unit.** Whole-application modelling is
  unsupported.
- **The tool does not own business correctness.** Human confirmation can still
  confirm a wrong assumption.
- **The tool is not a test-management system.**
- **The tool is not a full model-based automation platform.**
- **The tool is not a PhoenixQA replacement.** Runtime healing and initial
  adaptation remain separate concerns.

## Maintenance and change support

- **No change detection exists.**
- **No context-staleness automation exists.**
- **No impact analysis exists.**
- **No selector or workflow repair exists.**
- **No accepted-change history beyond current intake evidence exists.**

## Validation and claims

- **No real reference web application has been exercised.** The `.test` target
  is fictional fixture data.
- **No controlled baseline has been run.**
- **No claim of time savings, easier operation, or higher code quality is
  justified.**
- **Human-intake completion is not adaptation readiness.** Sprint 2 explicitly
  leaves one browser locator blocker in the reference flow.
- **Adaptation readiness would not prove a correct test.** Meaningful assertions,
  architecture quality, execution, and maintenance still require evidence.

## Packaging and production readiness

- **The project is experimental.**
- **The package is not published.** Editable local installation is documented.
- **Dependencies are version-ranged, not locked.**
- **There is no release, installer, compatibility matrix, support policy,
  telemetry policy, or production-readiness claim.**
- **The MIT license does not imply fitness for a particular purpose.**

## Next boundary to resolve

Sprint 3 should add a bounded, human-controlled browser observation that moves
one locator from inferred to observed through real application evidence.

Do not begin live LLM calls, Jira integration, framework generation, Salesforce,
or autonomous crawling before that browser boundary is safe, minimal, and
replayable.
