# Known limitations — thematic index

Things known to be incomplete, unverified, fragile, or outside the current
scope.

These are current project boundaries, not hidden bugs. Full reasoning lives in
`LEARNINGS.md`; this file is a quick map, not a copy.

## Current implementation state

- **The repository implements context, deterministic human intake, one bounded
  browser-observation path, and one bounded synthesis replay path.** It has a
  logical POM proposal contract but no live provider, framework adapter, or
  runnable generated test.
- **The expected normal Windows result is 104 passing tests with Playwright
  Chromium.** The preparation environment runs 103 tests and skips one browser
  test because administrator policy blocks loopback navigation. No real-user or
  external-application evaluation has occurred.
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
- **Only the Sprint 4 reference projection is authorized.** The bounded request
  includes confirmed/observed public or internal values and excludes selected
  URLs, routes, raw provenance, notes, hashes, and repository data. This is not
  a complete enterprise authorization or redaction policy.
- **No threat model exists.** Prompt injection, malicious DOM content, poisoned
  artefacts, and unsafe attachments remain future concerns.
- **No encryption, access control, retention, or deletion workflow exists.**
- **Real enterprise systems must not be used yet.** Salesforce and Jira remain
  deferred until safe handling rules exist.

## LLM use

- **Live LLM support is narrow and local-only.** Sprint 8 integrates Ollama on a
  loopback HTTP endpoint for interview ordering and wording only. Synthesis,
  code generation, maintenance, and other providers still use deterministic
  logic or replay.
- **Protocol correctness is implemented.** The project has a bounded request,
  deterministic prompt, strict parser, exact raw-output preservation,
  deterministic proposal validator, run persistence, and human review.
- **Semantic model quality is unproven.** The committed proposal is a controlled
  fixture, not evidence that a live model creates maintainable POM boundaries.
- **Guided-run resume is identity-bound, not migration-aware.** A persisted run can resume only with the same profile, seed, session, and context IDs; there is no migration or merge workflow.
- **Only basic live-call bounds exist.** Sprint 8 has timeout, prompt/response
  character budgets, temperature, seed, and round limits. It has no automatic
  retry, token-budget accounting, model benchmark, or adaptive fallback.
- **Prompt injection and malicious context are not handled.** The request is
  minimized but not proven safe for arbitrary external or enterprise content.
- **One local model path is implemented, not generally validated.** The default
  acceptance profile uses `qwen2.5-coder:7b`, but no claim is made that this is
  the best interview model or that every Ollama model follows the schema well.
- **Accepted means review-approved proposal, not correct code or successful
  execution.**

## Framework adaptation

- **A logical POM proposal and repository-aware plan now exist.** Sprint 5 maps
  one accepted proposal to exact Page Object, component, fixture, and E2E test
  targets.
- **The first mapping convention is intentionally narrow.** Page Objects map to
  `pages/`, components to `components/`, fixtures to `tests/e2e/conftest.py`, and
  E2E tests to `tests/e2e/`. This is not proven universal.
- **The inspector persists metadata, not source code.** It records relative
  paths, hashes, sizes, and top-level Python symbols. It cannot understand full
  runtime behaviour, decorators, fixture scopes, or indirect imports.
- **Allowlisting is not secret detection.** The profile owner must exclude
  secret-bearing files. The current inspector has no credential or malicious
  source scanner.
- **The controlled framework fixture is not the full repository.** It mirrors
  relevant layers for deterministic replay but does not prove full-repository
  usefulness.
- **No generated code or repository diff exists.** Plan acceptance changes only
  the plan state and leaves framework files unchanged.
- **No test has been generated, collected, or executed.**

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

- **The first workspace and repository-planning contracts exist.** They cover
  a non-secret inspection profile, minimized snapshot, and adaptation plan, but
  not a full project/authentication profile or executable cross-repository flow.
- **Normal framework execution independence is a design requirement.** No
  generated framework project exists yet to demonstrate it.
- **No shared environment or authentication profile exists.** Framework fixtures
  and Cartographer browser sessions cannot yet consume one logical profile.
- **One-source/two-consumer secret handling is not implemented.** No secret
  provider, rotation, expiry, or audit boundary exists.
- **The three authentication strategies are parked, not supported.** Shared
  storage state, declarative login recipe, and interactive SSO/MFA login remain
  future directions.
- **The execution-evidence contract is still a reference integration.** Sprint 7
  proves the provider-neutral bundle and standalone collector, but production
  `qa-automation-framework` installation and CI retention remain future work.

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
- **Human-intake completion is not adaptation readiness.** The reference flow
  reaches readiness only after accepted browser evidence observes the final
  primary locator.
- **Adaptation readiness and external synthesis authorization are separate.** A
  ready local context may still contain supplied or sensitive values that the
  bounded request refuses.
- **An accepted POM proposal does not prove a correct test.** Framework mapping,
  source generation, meaningful assertions, execution, and maintenance still
  require evidence.

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

## Sprint 7 execution-evidence limitations

- **The collector is a reference implementation, not yet installed in the
  production framework repository.** It proves the contract and independent
  runtime boundary in a controlled pytest subprocess.
- **`test_failure` is not an application-bug verdict.** Version `0.1` classifies
  by pytest phase only. Sprint 8 must preserve uncertainty and support
  insufficient-evidence outcomes.
- **Raw failure text is intentionally absent.** The contract stores exception
  type, safe summary, relative location, and redacted hashes. Some diagnoses
  will require a separately authorized artefact policy.
- **No screenshots, traces, network bodies, DOM, HTML, stdout, or stderr are
  persisted.** Their future usefulness does not override the current privacy
  boundary.
- **The bounded step probe requires explicit instrumentation.** Tests without a
  probe may be valid evidence records but are not ready for automatic Sprint 8
  handoff.
- **Forced process termination may lose the bundle.** Version `0.1` writes the
  final bundle at pytest session finish; it is not crash-safe streaming.
- **No xdist, retry, rerun, or flaky-run correlation exists.** One record maps to
  one normal single-process pytest execution.
- **Profile defaults are suitable only for a bounded run.** Mixed suites will
  need per-test or generated traceability metadata.

## Next boundary to resolve

Sprint 8 should consume validated failure records without forcing a premature
root-cause verdict. It should target re-observation, mark context stale or
conflicting when justified, calculate impact, and keep diagnosis separate from
patch acceptance.

- **The Sprint 6 sandbox contains only accepted snapshot entries.** This prevents
  uninspected files such as a parent `tests/conftest.py` from influencing the
  generated-test acceptance gate. It also means the gate does not yet prove
  compatibility with every file and plugin in the full framework repository.
  Full-repository integration remains a later acceptance concern.

## Deterministic templates require declared framework primitives

Sprint 6 generation currently requires the selected snapshot to expose:

- `pages/base_page.py::BasePage` as a class,
- `components/base_component.py::BaseComponent` as a class.

The requirements are now explicit and validated before plan review. The tool
does not yet adapt its inheritance strategy automatically when a project uses
different base abstractions. Such a repository is reported as incompatible with
the selected generation profile rather than silently handled.

- **CLI entry-point coverage is intentionally selective.** Sprint 7 adds real
  subprocess coverage for the new execution-evidence commands after direct
  `main()` tests missed a module-definition-order defect. Older CLI commands are
  still primarily tested through direct dispatch and do not yet all have an
  equivalent `python -m` regression test. Tracked as future hardening rather
  than a Sprint 7 blocker.


## Sprint 8 guided-intake limitations

- **The LLM plans questions; it does not interpret answers.** Human text is
  stored as provided and later confirmed through deterministic rules.
- **The initial context is structurally minimal, not literally empty.** Context
  schema `0.1` requires one page, element, locator candidate, step, and outcome,
  so the seed builder creates explicit unknown placeholders.
- **The application URL is collected locally but never sent to the model.** This
  reduces exposure but does not make the session file non-sensitive.
- **Raw prompts and responses are intentionally absent.** Hashes support
  consistency and metrics, but exact forensic replay requires an independently
  retained authorized artefact that does not yet exist.
- **Only loopback Ollama is accepted.** There is no cloud fallback, OpenAI,
  Anthropic, LM Studio, or remote Ollama provider.
- **Question quality is unmeasured.** The model may produce awkward wording or
  suboptimal order while still satisfying the structural contract.
- **Prompt injection is only weakly exposed in this sprint.** The prompt contains
  a human initial request and known local context, but no arbitrary page or
  document content yet. Full hostile-content handling remains open.
- **Discovery readiness is not adaptation readiness.** Browser evidence, real
  pages, actions, elements, states, and locators are intentionally deferred to
  Sprint 9.

- **Local structured-output latency is hardware-dependent.** The Sprint 8 live gate permits up to 600 seconds per planning call. A model can answer a trivial prompt quickly and still require several minutes for the constrained nine-question JSON response. The current flow has no streaming progress or automatic fallback to a smaller model.


- **Live local-LLM progress is phase-level, not token-level.** Structured output
  remains non-streaming so the complete JSON document can be validated. The
  verifier now reports preload, collection, and review boundaries, but it does
  not display partial tokens. Local runtime failures still require inspection of
  `%LOCALAPPDATA%\Ollama\server.log`. Tracked as a possible future diagnostics
  improvement, not a Sprint 8 blocker.

## Sprint 9 discovery boundaries

- Discovery scans one explicit page only; it is not a crawler.
- The selector allowlist does not cover canvas, complex Shadow DOM, virtualized
  grids, custom accessibility trees, or arbitrary framework components.
- Semantic names are bounded values derived from specific accessibility and
  form attributes. Generic page text is not collected.
- Ranking is intentionally simple and has been validated only on the controlled
  catalog fixture.
- A `missing` target still requires a human to revise the discovery plan; the
  local LLM does not invent a new action or selector.
- One ambiguity is phrased by a local model, but the quality of that wording has
  not been compared across models.
- Authentication, multi-page navigation, destructive actions, and enterprise
  systems remain outside the slice.
