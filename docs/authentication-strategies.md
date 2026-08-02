# Authentication strategies — parked design directions

## Purpose

TestCartographer will eventually need authenticated access to systems such as
Salesforce. The same project automation repository also needs authentication
for normal framework execution.

The values are shared project concerns, but the modules have different browser
lifecycles:

- the framework authenticates to execute tests,
- TestCartographer authenticates to discover, re-observe, and maintain context.

The goal is one approved source of secret material and session policy with two
separate consumers, not two copied credential configurations.

This document records three parked strategies. None is implemented or selected
as the universal default.

## Common principles

Regardless of strategy:

- credentials must not enter `ContextBundle`, browser observations, LLM
  requests, generated documentation, or source control,
- project configuration stores secret references, not secret values,
- secrets should be resolved only when needed and kept in memory for the
  shortest practical time,
- authenticated Playwright state is sensitive and ignored by Git,
- allowed origins and application areas must be explicit,
- account permissions should be limited to the required environment and flow,
- SSO, MFA, customer policies, and enterprise secret managers may constrain the
  available strategy,
- TestCartographer and the framework should consume a shared lower-level
  `EnvironmentProfile`, `AuthProfile`, and `SecretProvider` contract rather than
  importing each other's fixtures.

## Strategy A — shared Playwright storage state

```text
approved login/bootstrap flow
→ sensitive Playwright storage state
→ framework browser context
→ TestCartographer browser context
```

Potential advantages:

- avoids repeated username/password entry,
- supports the same authenticated role across execution and discovery,
- keeps ordinary test runs fast,
- fits Playwright's existing browser-context mechanism.

Risks and open questions:

- storage state can allow account impersonation,
- expiration and refresh need explicit handling,
- one state file may not represent multiple roles or parallel workers safely,
- storage and deletion policy must be defined,
- some SSO flows may bind sessions to devices or additional state.

## Strategy B — declarative login recipe with in-memory secrets

```text
AuthProfile
+ secret references
+ login recipe
→ resolve secrets in memory
→ perform approved login
→ verify success condition
→ optional short-lived storage state
```

A profile may describe:

- login URL or route,
- logical username and password secret references,
- user role,
- allowed actions,
- success condition,
- optional session-state output location.

Potential advantages:

- explicit and replayable authentication workflow,
- one definition can be interpreted by both modules,
- credentials remain outside project context and repository files,
- useful for accounts that permit automated login.

Risks and open questions:

- login pages and MFA steps can change,
- secret handling and logging must be audited,
- the recipe itself may expose internal application details,
- not all enterprise identity providers allow scripted authentication.

## Strategy C — interactive human login

```text
headed browser
→ human completes SSO/MFA/login
→ authenticated browser context
→ optional approved storage-state capture
→ guided TestCartographer session
```

Potential advantages:

- works with SSO or MFA that should not be automated,
- avoids giving TestCartographer raw credentials,
- keeps a human in control of sensitive access.

Risks and open questions:

- less suitable for unattended maintenance,
- active user time increases,
- the resulting state remains sensitive,
- session expiry and role verification still need handling.

## Relationship with framework fixtures

A pytest fixture is an execution-plane implementation detail.
TestCartographer should not launch pytest or import a fixture just to obtain an
authenticated page.

The intended direction is:

```text
shared project profile
├── EnvironmentProfile
├── AuthProfile
└── SecretProvider references

framework fixture
→ interprets the profile for test execution

TestCartographer browser session
→ interprets the same profile for discovery and maintenance
```

The exact contracts and repository locations remain future design work.

## Salesforce acceptance target

Salesforce remains a deliberate enterprise acceptance target, not an early
implementation dependency.

A candidate safe flow is:

```text
login
→ open Accounts
→ create an Account
→ save
→ verify the created record
```

Before this validation, the project must establish:

- a safe non-production environment,
- approved accounts and roles,
- selected authentication strategy,
- secret and session retention rules,
- allowed origins and actions,
- test-data policy,
- external-LLM data boundary,
- cleanup and repeatability strategy.

Simple public pages and dynamic public portals remain useful stepping stones,
but they cannot validate enterprise authentication, data handling, or complex
business workflows.
