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

**Status:** OPEN

**Target:** Sprint 4

There is no:

- provider-neutral request,
- authorized context selector,
- prompt protocol,
- structured proposal schema,
- strict parser,
- malformed-output handling,
- replay adapter,
- timeout, retry, latency, or cost policy.

No live provider should be added before the local human and browser context is
bounded.

## Gap 9 — POM proposal and framework adaptation

**Status:** OPEN

**Target:** Sprints 4–6

The project cannot yet:

- propose Page Object or component boundaries,
- map actions to methods,
- map symbolic data to fixtures,
- inspect an existing target repository,
- avoid duplicate objects,
- generate reviewable file changes,
- execute a generated test.

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

**Status:** OPEN

**Target:** Sprint 5

The projects do not yet share a concrete automation workspace or a non-secret
project profile.

Missing capabilities include:

- locating and inspecting a target `qa-automation-framework` repository,
- mapping environments, roles, symbolic data, pages, components, fixtures, and
  tests to existing framework artefacts,
- detecting duplicate or conflicting files and symbols,
- preserving source-to-target traceability,
- storing accepted Cartographer state beside the concrete automation project
  without polluting normal test execution.

The project must validate the actual framework structure before freezing a
workspace schema.

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

**Status:** OPEN

**Target:** After the first runnable framework test

No framework-side collector currently exports bounded maintenance evidence.

A future contract should capture enough context to analyse a failure without
assuming it is an application bug, including:

- test, step, Page Object, and method identifiers,
- action and locator,
- exception and failure classification,
- minimized element/page state,
- environment and application-version metadata,
- policy-approved trace, screenshot, or network references,
- links to Cartographer context and accepted artefacts.

This is a cross-repository gap: collection belongs to the framework; analysis
belongs to TestCartographer.

## Gap 17 — Reactive maintenance workflow

**Status:** OPEN

**Target:** After execution evidence exists

The product cannot yet:

- consume a failed-run evidence package,
- distinguish likely application, automation, data, environment, and stale-
  context failures,
- target a re-observation,
- mark affected knowledge stale or conflicting,
- calculate change impact,
- prepare a reviewable patch,
- trigger or guide a framework retest after acceptance.

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
