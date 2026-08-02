# Future ideas

Ideas that may become useful later but are intentionally outside the active
scope.

This file prevents ideas from being lost without turning them into implied
commitments. An idea should move into the roadmap only when earlier evidence
shows a concrete need.

Full reasoning and the point at which an idea appeared belong in
`LEARNINGS.md`.

## Jira and test-management ingestion

Import selected:

- issues,
- acceptance criteria,
- defects,
- test cases,
- links and attachments,
- project metadata.

Before implementation, define:

- authorization,
- data minimization,
- redaction,
- provenance,
- retention,
- stale-content handling,
- conflict handling,
- whether cloud LLM processing is permitted.

Do not treat Jira as the automatic source of truth.

## Documentation and knowledge connectors

Possible sources:

- Confluence or other knowledge bases,
- OpenAPI specifications,
- architecture diagrams,
- requirements repositories,
- test evidence stores.

The product should retrieve only the context required by the active process,
not create an uncontrolled enterprise-data mirror.

## API and Service Object Model adaptation

Extend the context model and framework adapter to support:

- endpoints and operations,
- authentication,
- request and response contracts,
- service dependencies,
- test-data setup,
- Service Object boundaries,
- API and integration test proposals.

This should reuse the same evidence and human-review principles without forcing
UI and API concepts into one abstraction.

## Autonomous application exploration

Allow the tool to propose and execute navigation beyond explicit human steps.

Possible safeguards:

- approved domains and routes,
- read-only mode,
- action allowlist,
- destructive-action denylist,
- page and time budgets,
- loop detection,
- data-entry restrictions,
- human approval gates.

Build only if guided exploration proves valuable but too labor-intensive.

## Visual and multimodal context

Use screenshots or visual models when DOM and accessibility information are
insufficient, for example:

- overlays,
- visual hierarchy,
- off-screen or occluded elements,
- canvas-based interfaces,
- layout-dependent workflows.

Multimodal input increases privacy exposure and cost. It should not be included
only because the provider supports images.

## Application graph

Represent relationships among:

- processes,
- pages,
- components,
- elements,
- roles,
- data,
- risks,
- tests,
- automation artefacts.

A graph may improve impact analysis and context retrieval. It is not required
until simpler representations demonstrate a concrete limitation.

## Change-impact analysis

Compare stored and current context to identify:

- changed locators,
- moved components,
- new required fields,
- changed states,
- changed process order,
- stale tests,
- affected fixtures and data.

The first form should produce a reviewable impact proposal rather than rewrite
the repository automatically.

## PhoenixQA interoperability

Possible future relationship:

```text
TestCartographer
→ stores application and automation context

PhoenixQA
→ detects or recovers from runtime action failure

shared evidence
→ improves diagnosis and maintenance proposals
```

Do not merge the projects or create a shared runtime dependency until both
boundaries are stable.

## Accepted-change history

Store:

- proposal,
- source evidence,
- reviewer decision,
- final diff,
- execution result,
- later maintenance outcome.

This may provide higher-quality retrieval examples than raw model outputs.

## LLM evaluation through llm-qa-toolkit

Use a dedicated evaluation harness to assess selected TestCartographer outputs,
such as:

- missing-context detection,
- source-grounded classification,
- POM boundary proposals,
- unsafe certainty,
- change-impact explanations.

Evaluation requires trustworthy reference cases and cannot rely only on another
LLM's unsupported opinion.

## Private or enterprise deployment

Potential modes:

- fully local orchestration with a cloud model receiving minimized context,
- approved enterprise model endpoint,
- air-gapped deployment with a sufficiently capable local model,
- customer-managed storage and retention.

Do not promise provider parity before empirical testing.

## Plugin architecture

Potential extension points:

- issue trackers,
- documentation sources,
- browsers,
- LLM providers,
- context stores,
- framework targets,
- review interfaces.

A plugin system should follow multiple proven integrations, not precede them.

## IDE integration

Possible Cursor or VS Code workflow:

- review missing context,
- start a guided capture,
- inspect proposed mappings,
- preview diffs,
- accept or reject changes.

An IDE interface is secondary to a stable provider-neutral core workflow.

## Web review interface

A local review UI could visualize:

- process steps,
- pages and components,
- evidence,
- unresolved questions,
- generated artefacts,
- proposed changes.

Do not build a large frontend before the review model is proven through a
simpler interface.

## Team review and approval

Support separate roles for:

- collector,
- domain reviewer,
- automation reviewer,
- security reviewer,
- approver.

The first product remains single-user and local.

## Authentication strategies for credentialed systems

Three strategies are parked for systems such as Salesforce:

1. **Shared Playwright storage state** used by framework execution and
   Cartographer discovery through separate browser contexts.
2. **Declarative login recipe** that resolves approved secrets in memory,
   performs the login, verifies success, and may create short-lived storage
   state.
3. **Interactive human login** in a headed browser for SSO/MFA flows that should
   not be automated.

The strategies share common principles:

- project files contain secret references, not values,
- the framework and Cartographer consume one approved secret source through
  separate runtime adapters,
- storage state is sensitive and ignored by Git,
- allowed origins, actions, retention, and session expiry are explicit,
- pytest fixtures remain execution-plane details rather than Cartographer APIs.

See [`authentication-strategies.md`](authentication-strategies.md).

## Framework execution-evidence collector

Add a bounded collector to `qa-automation-framework` that exports useful
maintenance context without assuming every failed test is an application bug.

Potential evidence:

- test, step, Page Object, and method identifiers,
- action, locator, and failure classification,
- minimized page/element state,
- environment and application-version metadata,
- policy-approved trace, screenshot, or network references,
- links to the relevant Cartographer context.

Collection belongs to the framework execution plane. Diagnosis, context
updates, impact analysis, and patch proposals belong to TestCartographer.

## Proactive frontend/context regression

Run bounded re-observation after deployment windows or on an approved schedule,
even when current tests remain green.

The observation inventory may include:

- elements used by current tests,
- shared components,
- mapped elements not yet used by tests,
- areas planned for future automation.

This is not unrestricted crawling. It requires approved areas, read-only or
allowlisted actions, authentication profiles, sensitivity rules, and budgets.

## Expansion using the existing application map

Add a second process while reusing existing:

- pages and components,
- locators and observations,
- environment and authentication mappings,
- fixtures and test-data patterns,
- naming conventions and accepted decisions.

Measure whether reuse reduces repeated questions, observations, duplicate code,
LLM input, cost, and review time.

## Salesforce validation case

Use a safe Salesforce Developer Edition, Trailhead-style environment, or other
approved non-production Salesforce environment for an enterprise validation
flow:

```text
login
→ open Accounts
→ create an Account
→ save
→ verify the record
```

Salesforce is deliberately retained as a major acceptance target because it can
exercise:

- credentialed access and session reuse,
- dynamic component-driven UI,
- complex navigation and application state,
- enterprise data restrictions,
- difficult locator and synchronization decisions,
- realistic creation, execution, maintenance, and expansion workflows.

Simple public pages and modern public portals remain earlier validation levels.
They prove useful mechanisms but cannot establish enterprise readiness.

This is a validation target, not a product dependency or early sprint scope.

## Broader framework targets

Possible later support:

- other Playwright languages,
- Selenium,
- Cypress,
- Robot Framework,
- alternative Python framework layouts.

Generalization should follow a proven Playwright/Python implementation.

## Test-maintenance economics dashboard

Track:

- initial adaptation time,
- active operator time,
- LLM usage,
- number of accepted and rejected proposals,
- correction rate,
- change-detection time,
- maintenance time saved or added.

Metrics should support product decisions, not become vanity reporting.

## Reusable domain packs

Provide optional domain vocabularies or question sets for areas such as:

- e-commerce,
- CRM,
- banking,
- insurance,
- telecommunications.

A domain pack must not silently claim domain authority. It should help ask
better questions and still require project-specific evidence.

## Controlled recommendation of test level

Use available architecture and risk context to suggest whether a scenario may
be better covered through:

- unit,
- component,
- API,
- integration,
- UI/E2E,
- test-support automation rather than a test.

The tool should explain the recommendation and preserve human ownership.

## Test-design assistance

Suggest candidate coverage using techniques such as:

- equivalence partitioning,
- boundary value analysis,
- decision tables,
- state transitions,
- risk-based prioritization.

This requires stronger business and rule context than UI capture alone can
provide.

## Model-based test generation

Generate multiple test paths from the application-context model.

This is deliberately parked. The project must first prove that the model is
accurate, reviewable, and economical to maintain for one process.

## Self-improving retrieval

Use previously accepted context and changes to reduce repeated questioning and
improve proposals.

Safeguards are required to prevent stale or project-specific decisions from
being treated as universal truth.
