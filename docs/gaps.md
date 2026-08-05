# Gaps — thematic index

Implementation gaps that prevent the current project from satisfying the
product-level direction.

This file tracks what is missing or insufficient. Chronological reasoning lives
in `LEARNINGS.md`, and accepted decisions live in
`docs/architecture-decisions.md`.

## Gap 1 — Minimum context contract

**Status:** CLOSED in Sprint 1

Sprint 1 introduced:

- `ContextBundle` version `0.1`,
- strict graph and knowledge validation,
- evidence and sensitivity metadata,
- deterministic JSON persistence,
- adaptation-readiness assessment,
- committed JSON Schema and controlled fixtures.

Remaining questions about real-world sufficiency are tracked separately rather
than reopening the implemented contract boundary.

## Gap 2 — Human-guided process intake

**Status:** CLOSED for the controlled Sprint 2 boundary

Sprint 2 introduced:

- deterministic stage-specific questions,
- collection and review phases,
- provide, confirm, unknown, and skip actions,
- self-contained persisted sessions,
- pause, resume, blocked, complete, and retry behaviour,
- interaction and active-time metrics,
- CLI start, run, status, and export commands.

This closure means the reference incomplete bundle can be completed without
manual JSON editing.

It does not mean greenfield context creation or real-user usability is proven.

## Gap 3 — Context-shell creation

**Status:** OPEN

**Target:** Sprint 3 or later, depending on evidence

The intake currently starts from a structurally valid bundle containing
pre-existing application, process-step, page, component, element, action, and
evidence structure.

The product cannot yet create that shell from:

- a new project description,
- a guided browser session,
- existing automation code,
- project artefacts.

A premature generic wizard would force the user to manually author browser
structure that Sprint 3 is intended to observe.

## Gap 4 — Guided browser observation

**Status:** CLOSED for the bounded Sprint 3 boundary

Sprint 3 introduced:

- Playwright browser capture for one authorized page and existing element ID,
- strict observation contract and schema version `0.1`,
- exact-one-match locator verification,
- selected-target attribute allowlist,
- explicit non-persistence of input values, page text, HTML, screenshots, and
  raw page data,
- human accept/reject review,
- narrow evidence-backed promotion from `INFERRED` to `OBSERVED`,
- deterministic replay and a real controlled-browser verifier.

This closure does not include greenfield discovery, arbitrary element picking,
locator generation, or enterprise-browser safety. Those remain separate gaps.

## Gap 5 — Rich resolution of arbitrary open questions

**Status:** OPEN

**Target:** Revisit after Sprint 4–6 evidence

`OpenQuestion` version `0.1` has no structured answer field.

Sprint 2 retains the prompt and response through:

- the interaction log,
- a human evidence summary,
- removal from the active open-question list.

This is sufficient for the controlled reference flow but may be inadequate for
mapping answers into:

- business rules,
- decision tables,
- test-data constraints,
- expected-result operators,
- domain-specific structures.

Do not revise the contract until real examples show the required shape.

## Gap 6 — Human identity and confirmation authority

**Status:** OPEN

**Target:** Before multi-user or enterprise use

The current session proves that an explicit confirmation action occurred. It
does not prove:

- who performed it,
- whether that person was authorized,
- whether a domain expert and automation engineer require separate approvals,
- whether confirmation expires after a change.

The first workflow is intentionally single-user and local.

## Gap 7 — Security, minimization, and evidence retention

**Status:** OPEN

**Target:** Continue in Sprint 4; mandatory before external LLM or enterprise data

Current sensitivity labels are descriptive only.

Missing controls include:

- redaction,
- capture allowlists,
- field-level external-processing authorization,
- secret detection,
- raw-evidence retention and deletion,
- access control,
- encryption,
- prompt-injection handling,
- malicious DOM or document handling.

Browser observation must not become an uncontrolled raw-data collector.

## Gap 8 — Bounded LLM protocol

**Status:** PARTIALLY CLOSED by Sprint 4

**Implemented:**

- provider-neutral bounded request,
- confirmed/observed field authorization,
- default public/internal sensitivity boundary,
- explicit excluded fields and prohibited claims,
- deterministic prompt rendering,
- structured proposal schema,
- strict parser and duplicate-key rejection,
- exact raw-output preservation,
- malformed-output separation,
- replay adapter,
- deterministic proposal validator,
- human accept/reject review,
- CLI and versioned run persistence.

**Still open:**

- live provider adapter,
- provider timeout and retry policy,
- latency and token/cost accounting,
- provider-specific structured-output behaviour,
- prompt-injection and malicious-context handling,
- enterprise authorization for external processing,
- semantic quality evaluation across varied applications.

## Gap 9 — POM proposal and framework adaptation

**Status:** PARTIALLY CLOSED by Sprints 4–5

**Implemented:**

- strict logical Page Object and component proposals,
- method ownership and exact step mapping,
- authorized locator and symbolic-data references,
- symbolic fixture requirements without secret values,
- test intent and confirmed-outcome assertions,
- deterministic rejection of invented references and prohibited claims,
- explicit human review of the logical proposal.

**Implemented in Sprint 5:**

- bounded local framework inspection,
- non-secret workspace profile,
- relative paths, hashes, sizes, and Python symbol snapshot,
- exact file and symbol mapping,
- create-file, add-symbol, and reuse-symbol classification,
- source-to-target traceability,
- reviewable adaptation plan and separate acceptance.

**Still open after Sprints 5–6:**

- validate project-specific naming and fixture conventions against a full copy,
- safe writes to the original project repository,
- arbitrary source refactoring and merge-conflict handling,
- broader naming and fixture conventions,
- enterprise-scale framework compatibility.

## Gap 10 — Real usability and effort validation

**Status:** OPEN

**Target:** Collect incrementally; controlled comparison in Sprint 13

Sprint 2 records:

- interaction count,
- answer actions,
- active response seconds.

It does not yet measure:

- full setup time,
- time spent reading documentation,
- time spent reviewing exported context,
- correction effort outside the CLI,
- subjective difficulty,
- trust and confidence,
- manual baseline,
- DevTools/Codegen/general-LLM baseline.

Current metrics are instrumentation, not evidence of usability advantage.

## Gap 11 — CI and reproducible development environment

**Status:** OPEN

**Target:** Before the first public prototype milestone

The project currently has:

- editable local installation,
- version-ranged dependencies,
- local deterministic tests.

It lacks:

- GitHub Actions,
- dependency lock strategy,
- supported-platform matrix,
- automated schema-drift checks on push,
- package build verification.

CI is intentionally deferred until the core local workflow stabilizes enough to
justify maintaining it.

## Gap 12 — Greenfield application and element discovery

**Status:** OPEN

**Target:** Revisit after Sprint 4–6 evidence

Sprint 3 verifies an existing context locator. It cannot create pages,
components, elements, or candidate locators from an unknown application.

This remains distinct from bounded verification and should not be hidden inside
the LLM synthesis sprint.

## Gap 13 — Credentialed and complex browser contexts

**Status:** OPEN

**Target:** Before Salesforce or enterprise validation

Current browser evidence covers one public local page and one top-level DOM
target. Missing capabilities include:

- login and approved secret-provider integration,
- storage state and session lifecycle,
- one of the parked storage-state, login-recipe, or interactive-login paths,
- allowed-origin and action policy,
- iframes,
- Shadow DOM,
- multiple tabs,
- asynchronous application states,
- safe handling of sensitive URLs and attributes.

Authentication is documented separately from framework fixtures because both
modules need the same logical account and environment but have different
browser lifecycles.

## Gap 14 — Shared project workspace and framework mapping

**Status:** PARTIALLY CLOSED by Sprint 6

**Target:** Continue after the first execution-evidence slice

Sprint 5 now provides a first non-secret `WorkspaceProfile`, bounded local
inspection, a minimized `FrameworkSnapshot`, exact file/symbol planning, and
source-to-target traceability.

Still missing:

- a production project profile that covers environment, role, and symbolic data
  mappings without secret values,
- a full real-copy acceptance run against the current framework repository,
- storing accepted Cartographer state beside a concrete automation project,
- drift reconciliation when the framework changes after snapshot creation,
- source generation and safe application,
- proof that the first deterministic fixture and file conventions fit realistic
  adaptations.

## Gap 15 — Authentication profiles and one-source secret handling

**Status:** OPEN

**Target:** Before credentialed or enterprise validation

The framework and Cartographer may need the same environment and account, but no
shared lower-level authentication contract exists.

Missing capabilities include:

- non-secret `EnvironmentProfile` and `AuthProfile`,
- secret-provider references,
- approved origin and action policy,
- role and account verification,
- session expiry and refresh,
- sensitive Playwright storage-state handling,
- deletion and retention rules.

Three strategies are parked rather than selected:

1. shared Playwright storage state,
2. declarative login recipe with in-memory secrets,
3. interactive human login for SSO/MFA.

## Gap 16 — Framework execution-evidence collector

**Status:** PARTIALLY CLOSED by Sprint 7

**Implemented:**

- provider-neutral `ExecutionEvidenceProfile` and `ExecutionEvidenceBundle`,
- standalone pytest reference collector with no TestCartographer import,
- distinct pass, call-phase test failure, and setup/teardown infrastructure
  outcomes,
- complete links to context, process, synthesis, plan, patch, and source IDs,
- bounded structural step probe,
- minimized origin/path location,
- redaction-before-hashing and explicit raw-data exclusions,
- deterministic readiness assessment for reactive-maintenance intake,
- static replay and live subprocess verification.

**Still open:**

- installation and ownership in the production `qa-automation-framework` repo,
- xdist and multi-process aggregation,
- retries and flaky-run correlation,
- crash-safe streaming,
- policy-approved screenshot, trace, and network references,
- CI upload, retention, access control, and deletion,
- application-version metadata from real enterprise systems.

Collection belongs to the framework execution plane; diagnosis and context
evolution remain TestCartographer responsibilities.

## Gap 17 — Reactive maintenance workflow

**Status:** PARTIALLY CLOSED by Sprint 12 for one controlled locator drift

**Implemented:**

- consumption of a failed-run `ExecutionEvidenceBundle`,
- explicit infrastructure-error exclusion,
- deterministic readiness for re-observation without an application-bug or stale-
  locator claim,
- headed current-page re-observation,
- real operator candidate selection,
- one deterministic exact locator patch with full-source review,
- snapshot-bounded sandbox application,
- fail-before/pass-after framework retest,
- original-framework preservation,
- provider-neutral contracts, schemas, CLI, scripted regression, and real-
  operator acceptance gate.

**Still open:**

- arbitrary failure classification across application, automation, data,
  environment, timing, assertion, workflow, authentication, and context causes,
- automatic stale/conflicting knowledge transitions,
- impact analysis across shared components and tests,
- multi-file and semantic source repairs,
- in-flow editing and alternative candidate comparison,
- production repository application and pull-request integration,
- LLM-assisted diagnosis or repair,
- authenticated, multi-page, enterprise, and Salesforce validation,
- comparative maintenance effort and usability evidence.

The closed slice establishes a safe authority sequence: evidence permits
re-observation; current-page evidence plus human selection permits a repair
candidate; full-source human review permits sandbox application.

## Gap 18 — Proactive frontend/context regression

**Status:** OPEN

**Target:** After bounded maintenance and authentication profiles exist

The product cannot re-observe approved application areas after deployment
windows or on a schedule.

Missing controls include:

- observation inventory,
- approved application areas and origins,
- read-only or allowlisted actions,
- authentication profile,
- time, page, and cost budgets,
- change comparison and impact report,
- handling of mapped elements that are not exercised by current tests.

This gap is separate from test execution because a green test suite does not
prove that the broader mapped frontend is unchanged.

## Gap 19 — Reuse during automation expansion

**Status:** OPEN

**Target:** After the first complete creation lifecycle

No second process has been added using the existing application map.

The project has no evidence that prior knowledge reduces:

- repeated human questions,
- repeated browser observation,
- duplicate Page Objects or components,
- LLM context size and cost,
- review and implementation time.

Expansion must be evaluated as reuse rather than another independent demo.

## Gap 20 — Enterprise validation and Salesforce acceptance

**Status:** OPEN

**Target:** After authentication, security, maintenance, and framework handoff

Only a controlled local page has been exercised.

The validation ladder still lacks:

- simple public application evidence,
- modern dynamic public frontend evidence,
- controlled multi-page application evidence,
- credentialed enterprise-style reference evidence,
- a safe Salesforce flow.

Salesforce remains a deliberate acceptance target because simple pages cannot
validate enterprise authentication, component-driven UI, data restrictions,
complex process state, or realistic maintenance economics.

## Gap 21 — Framework-contract negotiation

**Status:** OPEN

**Target:** After the first deterministic creation proof

Sprint 6 now validates exact required framework primitives, but it cannot yet
negotiate alternatives such as a differently named base component, composition
instead of inheritance, or project-specific constructor signatures.

Future adaptation must distinguish:

- a stale or incomplete checkout,
- a compatible framework with different conventions,
- a genuinely unsupported architecture.


## Gap 18 — Guided multi-element browser discovery

**Status:** Open
**Target:** Sprint 9

Sprint 8 can turn a minimal request into a human-reviewed process brief, but the
technical graph still contains explicit placeholders. The tool cannot yet guide
the user through several actions, identify page/component boundaries, collect
multiple elements, propose locator candidates, or ask an ambiguity question
based on live browser evidence.

## Gap 19 — Integrated creation orchestration and effort evidence

**Status:** CLOSED in Sprint 10 for fixture-assisted mechanics
**Target:** Sprint 10

The individual creation contracts now run as one traceable reference workflow
from short request through interview, browser discovery, proposal, repository
plan, patch, runnable test, and effort summary. Required human actions are
represented by fixtures, and no percentage of saved work is claimed.

## Closed in Sprint 9

- A discovery-ready Sprint 8 context can drive a real bounded browser scan.
- Several target elements and unique locator candidates can be collected in one
  session.
- Equal semantic candidates create an explicit ambiguity instead of false
  certainty.
- A local LLM can phrase the ambiguity while the human remains selection
  authority.
- Accepted discovery can replace the technical placeholder and satisfy the
  existing full-readiness gate.

## Gap 22 — Human-triggered interactive Creation Flow

**Status:** CLOSED in Sprint 11 for the controlled reference process
**Target:** Sprint 11

Sprint 11 now:

- accepts the initial request from the operator,
- separates one-time run bootstrap questions from process-specific questions,
- displays generated collection questions and waits for answers,
- replaces five repeated process reviews with one aggregate context summary,
- requires explicit confirmation at authority boundaries,
- opens a headed browser and labels ambiguous candidates,
- waits for the operator to select the intended element,
- displays discovery, POM proposal, and adaptation plan for review,
- renders every exact patch source line and hash before patch acceptance,
- requires a separate operator trigger before sandbox execution,
- persists an operator-action ledger without raw answer values,
- refuses to treat scripted fixture input as the manual acceptance artefact.

Still open beneath this closed slice:

- persistent reuse of confirmed bootstrap context across separate runs, with
  explicit invalidation on operator request, staleness, conflict, or relevant
  configuration change,
- resume from arbitrary downstream stages,
- in-flow editing of POM, plan, and patch,
- validation with an unbriefed external participant,
- arbitrary, multi-page, authenticated, and enterprise applications.

## Post-Sprint-11 validation gaps

- Compare the same process through manual discovery, Playwright Codegen, a
  general-purpose LLM, and TestCartographer.
- Validate a second public application before making breadth claims.
- Implement one approved authentication strategy before protected-system demos.
- Decide whether live POM synthesis adds value over the deterministic template
  without reducing reliability or authority clarity.
