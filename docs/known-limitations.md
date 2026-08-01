# Known limitations — thematic index

Things that are known to be incomplete, unimplemented, unverified, or outside
the current scope.

These are boundaries of the current project state, not hidden bugs. Full
reasoning lives in `LEARNINGS.md`; this file is a quick map, not a copy.

## Current implementation state

- **The repository contains documentation only.** There is no Python package,
  command-line interface, browser integration, context model, persistence
  layer, LLM protocol, framework adapter, or test suite.
- **No end-to-end workflow exists.** The flow described in the README and
  roadmap is a product hypothesis, not a demonstrated capability.
- **No source-code architecture has been selected.** Names such as agent,
  collector, mapper, adapter, or knowledge base are conceptual responsibilities
  only.

## Context model

- **The minimum context contract is undefined.** The project lists candidate
  concepts but has not decided which are required for one useful process.
- **The working knowledge statuses are not a schema.** `OBSERVED`, `PROVIDED`,
  `INFERRED`, `CONFIRMED`, `STALE`, and `CONFLICTING` still need definitions,
  transitions, and validation rules.
- **Evidence and provenance are requirements, not implemented features.** There
  is no source identifier, timestamp, reviewer, confidence, or supersession
  model.
- **Persistence is undecided.** Human-readable files, SQLite, or a hybrid model
  remain open options.
- **There is no versioning or migration strategy.** No context created by the
  project exists yet.

## Human interaction

- **No guided interview exists.** The project has not tested whether adaptive
  questions can collect enough context without burdening the user.
- **No usability evidence exists.** Setup time, active user time, correction
  rate, perceived difficulty, and user confidence have not been measured.
- **The initial user is assumed to be technically capable.** Non-technical and
  no-code use is out of current scope.
- **Human review is a product rule without an interface.** No acceptance,
  rejection, correction, or audit workflow exists.

## Application observation

- **No browser capture exists.** The tool cannot currently observe DOM,
  accessibility information, application state, network activity, screenshots,
  iframes, or Shadow DOM.
- **Autonomous exploration is explicitly out of scope.** The first planned
  workflow is human-guided and limited to one selected process.
- **Credentials and session handling are undefined.** Future browser work must
  keep secrets outside prompts, stored context, and source control.
- **The boundary between useful observation and raw data dumping is unproven.**
  No experiment shows what minimum capture is sufficient for POM mapping.

## LLM use

- **No LLM provider is integrated.** The project expects a capable external
  model but has selected no provider or model.
- **There is no bounded request or structured response protocol.** Prompt
  construction, authorization, parsing, retries, and malformed-output handling
  are undefined.
- **No LLM claim has been validated.** The project has no evidence that an LLM
  can produce useful context synthesis, POM boundaries, locator choices, or
  missing-context questions.
- **Local-model support is not promised.** A local provider may be explored
  later but is not a Sprint 1 requirement.
- **Cost and latency are unmeasured.** No token, request, wall-clock, or budget
  policy exists.

## Security and privacy

- **Security requirements are documented but unenforced.** There is no
  redaction, sensitivity classification, minimization, allowlist, retention, or
  deletion implementation.
- **Browser-visible data is not treated as safe by default.** This is a design
  rule only; no code currently prevents unsafe transmission.
- **Jira and enterprise integrations are not implemented.** No access-control,
  attachment, or confidential-data policy has been tested.
- **Real enterprise systems must not be used yet.** Salesforce and other
  realistic targets are deferred until safe environments and handling rules
  exist.

## Framework adaptation

- **TestCartographer cannot modify `qa-automation-framework`.** No repository
  reader, mapping engine, diff generator, or file writer exists.
- **POM quality rules are documented only at a high level.** No deterministic
  validator currently checks generated Page Object, component, fixture, or test
  boundaries.
- **No generated test exists.** The project has not produced or executed even
  one framework adaptation.
- **Repository coexistence is untested.** The project does not yet know how to
  avoid duplicating existing objects or overwriting human changes.
- **Ordinary test execution independence is a requirement, not evidence.** No
  generated project exists to show that it runs without the LLM tool.

## Scope boundaries

- **Initial scope is UI/POM only.** API discovery and Service Object Model
  adaptation are parked.
- **Playwright, Python, and pytest are the only intended first stack.** Other
  languages and browser frameworks are unsupported.
- **One process at a time is the intended first unit.** Whole-application
  modelling is not planned for the first vertical slice.
- **The tool does not own business correctness.** A reliable test basis and
  human confirmation remain necessary.
- **The tool is not a test-management system.**
- **The tool is not a full model-based automation platform.**
- **The tool is not a PhoenixQA replacement.** Runtime healing and initial
  framework adaptation remain separate concerns.

## Maintenance and change support

- **No change detection exists.**
- **No context-staleness mechanism exists.**
- **No impact analysis exists.**
- **No selector or workflow repair exists.**
- **No accepted-change history exists.**

All maintenance capabilities remain future work after the first creation flow
is proven.

## Validation and evidence

- **No reference application has been selected.**
- **No controlled baseline has been run.**
- **No comparison exists against manual adaptation or ordinary LLM-assisted
  work.**
- **No claim of time savings, quality improvement, or easier operation is
  justified.**
- **The proposed validation ladder is provisional.** Wikipedia-like pages,
  modern job portals, a controlled app, and Salesforce represent increasing
  difficulty, but exact targets and legal/technical feasibility remain
  undecided.
- **A passing generated test would not by itself prove correctness.** Quality
  also requires meaningful assertions, source traceability, appropriate
  architecture, and maintenance evidence.

## Licensing and production readiness

- **The project is experimental.**
- **There is no release, package, installation process, CI workflow, support
  policy, compatibility matrix, or production-readiness claim.**
- **The MIT license permits use but does not imply fitness for any particular
  purpose.**

## Next boundary to resolve

Sprint 1 should define and test the smallest provider-neutral context contract
for one process.

Do not begin broad agent architecture, Jira integration, autonomous crawling,
or framework generation before that contract exists.
