# Known limitations — thematic index

Things that are known to be incomplete, unimplemented, unverified, or outside
the current scope.

These are boundaries of the current project state, not hidden bugs. Full
reasoning lives in `LEARNINGS.md`; this file is a quick map, not a copy.

## Current implementation state

- **The repository implements only the local context boundary.** There is no
  user intake, browser integration, LLM protocol, Page Object proposal,
  framework adapter, or end-to-end test-generation workflow.
- **The working product flow remains incomplete.** Sprint 1 validates one
  contract, not application discovery or framework adaptation.
- **The package has no public CLI or UI.** Current use requires Python imports
  or direct fixture files.
- **No CI workflow is configured.** The current evidence is local deterministic
  test execution.

## Context model

- **Version `0.1` models exactly one process.** Shared pages, components,
  evidence, and application context may be duplicated across bundles.
- **The contract has been tested only against controlled fixtures.** It has not
  yet been exercised against a real project, real requirements, or real DOM.
- **Readiness rules are provisional.** They are deterministic but not yet
  validated as sufficient or appropriately strict for real POM adaptation.
- **Only text knowledge is authority-aware.** More complex typed business
  rules, assertion operators, state machines, and structured expected values
  are not modelled.
- **`UNKNOWN` does not represent not-applicable.** The first schema has no
  separate `NOT_APPLICABLE` state.
- **Confidence is a stored number, not a calibrated probability.** No
  calibration or interpretation policy exists.
- **The conflict model is simple.** It records one subject, evidence, and one
  resolution value; it does not model multi-claim argumentation or partial
  reconciliation.
- **No schema migration exists.** Only version `0.1` is accepted.
- **JSON is the only persistence format.** There is no database, concurrent
  update support, query layer, or merge strategy.

## Evidence and provenance

- **Evidence stores metadata and summary only.** Raw documents, DOM snapshots,
  screenshots, traces, and attachments are not captured or replayable.
- **Evidence authenticity is not verified.** `source_ref` is descriptive, and
  the optional SHA-256 digest is not automatically generated or checked.
- **Confirmation authority is not modelled.** The schema records status and
  evidence but not roles, approval policy, or who is permitted to confirm a
  business fact.
- **Source freshness is not calculated.** A value can be marked stale, but no
  automatic aging or supersession mechanism exists.
- **Conflicts are not discovered automatically.** They must currently be
  authored in JSON or constructed through Python.

## Human interaction

- **No guided intake exists.** A user must edit JSON or create models in Python.
- **No adaptive question selection exists.** Readiness issue codes are not yet
  mapped to user-facing questions.
- **No review workflow exists.** There is no accept, reject, correct, replace,
  or confirm interface.
- **No save/resume session exists beyond saving the final JSON bundle.**
- **No interaction metrics are collected.** Setup time, active user time,
  question count, correction rate, and perceived difficulty remain unmeasured.
- **The initial user is assumed to understand testing and automation.** No-code
  or non-technical use remains outside current scope.

## Application observation

- **No browser capture exists.** The tool cannot observe DOM, accessibility
  information, application state, network activity, screenshots, iframes, or
  Shadow DOM.
- **The reference `.test` application is fictional.** It is a data fixture, not
  a running target.
- **No locator is validated against a real browser.** Locator strategies and
  values are stored contract data only.
- **No page or component discovery exists.** Ownership relationships in the
  fixtures are manually authored.
- **Autonomous exploration is explicitly out of scope.** The first planned
  browser workflow remains human-guided.
- **Credentials and session handling are undefined.** Future browser work must
  keep secrets outside prompts, context files, logs, and source control.

## Test-data handling

- **Only symbolic requirements are stored.** The project cannot resolve,
  generate, provision, reset, or clean up actual test data.
- **No fixture mapping exists.** `symbolic_ref` is not connected to
  `qa-automation-framework` test data or fixtures.
- **Sensitivity classification is descriptive.** It does not enforce access or
  storage rules.
- **Credentials and real business values must remain outside the bundle.** No
  approved secret-store integration exists.

## LLM use

- **No LLM provider is integrated.** The project has no prompt, request schema,
  result schema, parser, replay adapter, timeout, retry, or budget controls.
- **No field is authorized for external processing.** Sensitivity does not equal
  permission.
- **No redaction or minimization engine exists.** The security processing
  sequence remains a documented requirement.
- **No LLM claim has been validated.** There is no evidence that a model can
  identify gaps, resolve mappings, propose POM boundaries, or generate useful
  code from the contract.
- **Local-model support is not promised.** It may be explored later, but Sprint
  1 has no provider abstraction.
- **Cost and latency are unmeasured.**

## Security and privacy

- **Security requirements are unenforced.** There is no access control,
  encryption, redaction, retention, deletion, audit log, or external-request
  allowlist.
- **Context JSON may still contain sensitive descriptions or URLs.** Excluding
  raw evidence reduces risk but does not make a bundle safe by default.
- **No threat model exists.** Prompt injection, malicious DOM content,
  untrusted attachments, and poisoned project artefacts remain future topics.
- **Jira and enterprise integrations are not implemented.**
- **Real enterprise systems must not be used yet.** Salesforce and other
  realistic targets are deferred until safe environments and handling rules
  exist.

## Structural validation

- **Validation checks structure, not truth.** A confirmed false statement can
  still pass the contract.
- **Semantic quality is not proven.** A syntactically valid purpose, risk, or
  outcome may still be vague or useless.
- **Locator quality preference is not enforced.** CSS and XPath remain allowed;
  there is no semantic-locator ranking or stability score.
- **Readiness is not stage-specific.** The current report answers one general
  adaptation-readiness question. Later stages may require separate readiness
  profiles for intake, observation, proposal, and code handoff.
- **No rule engine or configurable policy exists.** Readiness rules are coded in
  Python.

## Framework adaptation

- **TestCartographer cannot read or modify `qa-automation-framework`.**
- **No POM proposal schema exists.** There is no representation of candidate
  pages, component classes, methods, fixtures, or tests.
- **No architecture validator checks generated code.**
- **No generated test exists.**
- **Repository coexistence is untested.** The project does not yet know how to
  avoid duplicates, preserve human edits, or produce reviewable patches.
- **Ordinary test-execution independence remains a requirement, not evidence.**

## Scope boundaries

- **Initial scope is UI/POM only.** API discovery and Service Object Model
  adaptation remain parked.
- **Playwright, Python, and pytest are the intended first stack.** No browser
  runtime dependency is installed yet.
- **One process at a time is the current unit.** Whole-application modelling is
  not supported.
- **The tool does not own business correctness.** A reliable test basis and
  human confirmation remain necessary.
- **The tool is not a test-management system.**
- **The tool is not a full model-based automation platform.**
- **The tool is not a PhoenixQA replacement.** Runtime healing and initial
  adaptation remain separate concerns.

## Maintenance and change support

- **No change detection exists.**
- **No context-staleness automation exists.**
- **No impact analysis exists.**
- **No selector or workflow repair exists.**
- **No accepted-change history exists.**

All maintenance capabilities remain future work after the first creation flow
is proven.

## Validation and evidence

- **Current evidence is 23 deterministic tests around controlled fixtures.**
  This proves the implemented contract behaviours only.
- **No reference web application has been selected or built.**
- **No controlled baseline has been run.**
- **No comparison exists against manual adaptation or ordinary LLM-assisted
  work.**
- **No claim of time savings, quality improvement, or easier operation is
  justified.**
- **A ready context does not prove a correct automated test.** It means only
  that current deterministic blockers are absent.
- **A passing generated test would not by itself prove correctness.** Quality
  also requires meaningful assertions, source traceability, appropriate
  architecture, and maintenance evidence.

## Packaging and production readiness

- **The project is experimental.**
- **The package is not published.** Editable local installation is the only
  documented setup.
- **Dependency locking is not implemented.** `pyproject.toml` declares version
  ranges, not a reproducible lock file.
- **There is no release, compatibility matrix, support policy, installation
  installer, telemetry policy, or production-readiness claim.**
- **The MIT license permits use but does not imply fitness for any particular
  purpose.**

## Next boundary to resolve

Sprint 2 should create a deterministic human-guided intake that fills the
contract without requiring manual JSON editing.

Do not begin browser capture, live LLM calls, Jira integration, or framework
generation before the intake demonstrates how gaps, corrections, conflicts,
and confirmations are handled.
