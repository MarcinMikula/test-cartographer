# Known limitations — thematic index

Things known to be incomplete, unverified, fragile, or outside the current
scope.

These are current project boundaries, not hidden bugs. Full reasoning lives in
`LEARNINGS.md`; this file is a quick map, not a copy.

## Current implementation state

- **The repository implements context, deterministic human intake, and one
  bounded browser-observation path.** There is no LLM protocol, Page Object
  proposal, framework adapter, or runnable generated test.
- **The current suite contains 66 passing tests with Playwright Chromium,
  including one controlled local browser flow and editability regression
  coverage.** No real-user or external-application evaluation has occurred.
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

- **Observation verifies an existing locator only.** It does not discover an
  unknown page, component, element, process, or locator.
- **The user selects the URL and existing context element ID through CLI
  arguments.** There is no in-browser picker or guided multi-step navigation.
- **Only one top-level selected target is captured.** Iframes, Shadow DOM,
  multiple tabs, dynamic waits, and credentialed sessions are unsupported.
- **The snapshot is deliberately narrow.** It stores tag, visibility,
  enabled/editable state, and allowlisted attributes; it does not store page
  text, element text, input values, HTML, screenshot, trace, or network data.
- **Editability is queried only for element semantics supported by Playwright.**
  Native input controls, contenteditable elements, and supported ARIA roles use
  Playwright's check; elements such as buttons are recorded as non-editable
  instead of invoking an unsupported API state.
- **Minimization is not proof of privacy.** Allowlisted attributes and URL paths
  can still contain confidential information.
- **Only exact uniqueness and visibility are verified.** Locator stability,
  semantic quality, future resilience, and business correctness are not proven.
- **Acceptance is single-user and local.** Identity and authority are not
  verified.
- **The local reference page is not a realistic modern application.** It proves
  the browser boundary, not production readiness.
- **Autonomous exploration remains out of scope.**

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
- **Playwright, Python, and pytest are the only implemented browser stack.**
  Other languages and automation frameworks are unsupported.
- **One process at a time is the current unit.** Whole-application modelling is
  unsupported.
- **The tool does not own business correctness.** Human confirmation can still
  confirm a wrong assumption.
- **The tool is not a test-management system.**
- **The tool is not a full model-based automation platform.**
- **The tool is not a PhoenixQA replacement.** Runtime healing and initial
  adaptation remain separate concerns.

## Two-module lifecycle integration

- **The framework and Cartographer are aligned in documentation only.** There is
  no shared project workspace, profile, repository adapter, or cross-module
  protocol.
- **Normal framework execution independence is a design requirement.** No
  generated framework project exists yet to demonstrate it.
- **No shared environment or authentication profile exists.** Framework fixtures
  and Cartographer browser sessions cannot yet consume one logical profile.
- **One-source/two-consumer secret handling is not implemented.** No secret
  provider, rotation, expiry, or audit boundary exists.
- **The three authentication strategies are parked, not supported.** Shared
  storage state, declarative login recipe, and interactive SSO/MFA login remain
  future directions.
- **No execution-evidence contract exists between repositories.** The framework
  cannot yet provide bounded failure context to Cartographer.

## Maintenance and change support

- **No reactive maintenance workflow exists.** Failed framework runs cannot be
  classified, re-observed, mapped to context, or converted into a reviewable
  patch.
- **No proactive maintenance exists.** Cartographer cannot run bounded
  post-deployment frontend/context regression against an approved observation
  inventory.
- **No change detection or automatic staleness calculation exists.**
- **No impact analysis exists.**
- **No selector or workflow repair exists.**
- **No accepted-change history beyond current intake and observation evidence
  exists.**
- **No second-process expansion has been evaluated.** The project has no proof
  that its application map reduces repeated work.

## Validation and claims

- **Only a controlled local HTML reference page has been exercised.** No simple
  public, dynamic public, controlled multi-page, credentialed, or enterprise
  application has been validated.
- **No controlled baseline has been run.**
- **No claim of time savings, easier operation, higher code quality, cheaper
  maintenance, or faster expansion is justified.**
- **Human-intake completion is not adaptation readiness.** Sprint 2 explicitly
  leaves one browser locator blocker in the reference flow.
- **Adaptation readiness would not prove a correct test.** Meaningful assertions,
  architecture quality, execution, and maintenance still require evidence.

- **Salesforce is a future acceptance target, not current support.** A safe
  environment, authentication strategy, secret policy, data policy, cleanup,
  and external-LLM boundary must exist first.
- **Public pages are stepping stones only.** They cannot validate enterprise
  authentication, data restrictions, complex business state, or maintenance
  economics.

## Packaging and production readiness

- **The project is experimental.**
- **The package is not published.** Editable local installation is documented.
- **Dependencies are version-ranged, not locked.**
- **There is no release, installer, compatibility matrix, support policy,
  telemetry policy, or production-readiness claim.**
- **The MIT license does not imply fitness for a particular purpose.**

## Next boundary to resolve

Architecture checkpoint A aligns the long-term lifecycle, but no new runtime
capability is introduced. Sprint 4 should define a bounded, provider-neutral
LLM request and structured POM proposal protocol using only explicitly
authorized confirmed context and accepted observations.

Do not send raw pages, credentials, arbitrary context files, or unrestricted
browser evidence to a provider.
