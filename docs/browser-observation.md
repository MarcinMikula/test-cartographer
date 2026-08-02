# Bounded browser observation

## Purpose

Sprint 3 adds the first application-derived evidence boundary.

The feature verifies one locator already present in one `ContextBundle`. It does
not scan an application, discover a workflow, generate a locator from arbitrary
DOM, or update context without review.

```text
human-reviewed ContextBundle
→ user authorizes one page and one element ID
→ Playwright resolves the existing primary locator
→ exactly one visible target is required
→ a minimized observation is persisted
→ the user accepts or rejects the mapping
→ only an accepted observation may update the locator to OBSERVED
```

## Contract

`BrowserObservation` version `0.1` stores:

- context, element, and locator identifiers,
- a minimized source URL,
- capture timestamp, duration, and sensitivity,
- locator strategy, value, uniqueness, and visibility,
- selected element tag, visibility, enabled/editable state,
- an allowlisted set of attributes,
- a deterministic capture digest,
- pending, accepted, or rejected review state,
- review timestamp, reason, duration, and derived user-action count.

It explicitly records that these were not persisted:

- input value,
- text content,
- HTML,
- screenshot,
- raw page capture.

The committed schema is:

```text
schemas/observation-v0.1.schema.json
```

## Allowlisted attributes

Only the selected target may contribute:

```text
id
role
aria-label
name
placeholder
type
data-testid
```

Unknown attributes returned by the browser are discarded. The implementation
does not persist `value`, `innerHTML`, `outerHTML`, or `textContent`.

This is minimization, not a complete privacy guarantee. Allowlisted attribute
values can still contain sensitive data and therefore retain a sensitivity
classification.

## Locator verification

The current locator vocabulary maps to Playwright as follows:

| Context strategy | Playwright resolution |
|---|---|
| `role` | `get_by_role(role, name=name, exact=True)` using `role:name` |
| `label` | `get_by_label(value, exact=True)` |
| `test_id` | `get_by_test_id(value)` |
| `placeholder` | `get_by_placeholder(value, exact=True)` |
| `text` | `get_by_text(value, exact=True)` |
| `css` | `locator(value)` |
| `xpath` | `locator("xpath=...")` |

Capture fails when:

- the context element does not exist,
- there is not exactly one primary locator,
- the locator value is unusable,
- the locator matches zero or more than one element,
- the selected target is not visible,
- the browser snapshot is malformed.

A locator is not promoted merely because the browser command executed. The
observation must still be accepted by a human.

## Review and context update

A new observation starts as `pending`.

The user may:

- accept the mapping and apply it to a context copy,
- reject it with a mandatory reason.

Acceptance performs a deliberately narrow change:

1. verify that context, element, locator strategy, and locator value still match,
2. append one `APPLICATION` evidence record with the observation digest,
3. change only the target locator value from its prior status to `OBSERVED`,
4. preserve the process, business meaning, page ownership, and other elements,
5. rerun full adaptation readiness.

Rejection changes only the observation record. It does not modify context.


## Authorization and authentication boundary

In Sprint 3, "user-authorized" means that the operator explicitly supplies the
URL and existing context element ID to the CLI. It does not mean the tool has a
persistent identity, permission model, allowed-domain registry, or credential
policy.

The current implementation supports only an unauthenticated controlled local
page. Credentialed discovery and maintenance will require a separate project
and authentication boundary.

Parked directions are:

1. shared Playwright storage state,
2. declarative login recipe with secrets resolved only in memory,
3. interactive human login for SSO/MFA.

Those strategies should be consumed through a future non-secret `AuthProfile`
and approved secret provider. They must not place credentials or session state
inside `BrowserObservation` or `ContextBundle`.

See [`authentication-strategies.md`](authentication-strategies.md).

## CLI

Capture one controlled target:

```powershell
test-cartographer observe capture `
    --context testdata/context/observation_ready/public_search_flow.json `
    --url http://127.0.0.1:8765/public_catalog.html `
    --element-id el_search_submit `
    --observation .test-cartographer/search-submit-observation.json `
    --observation-id obs_search_submit `
    --sensitivity public
```

Review status:

```powershell
test-cartographer observe status `
    --observation .test-cartographer/search-submit-observation.json
```

Accept and create an updated context file:

```powershell
test-cartographer observe review `
    --observation .test-cartographer/search-submit-observation.json `
    --decision accepted `
    --reason "The target and locator mapping are correct." `
    --context testdata/context/observation_ready/public_search_flow.json `
    --output-context .test-cartographer/public-search-observed.json
```

Reject without changing context:

```powershell
test-cartographer observe review `
    --observation .test-cartographer/search-submit-observation.json `
    --decision rejected `
    --reason "The locator selected the wrong button."
```

## Controlled reference verification

The repository contains a dependency-free local fixture:

```text
testdata/browser/public_catalog.html
```

The verification script serves it on an ephemeral loopback port, opens it with
Chromium through Playwright, captures the existing inferred Search button
locator, accepts the observation, and asserts that full readiness changes from
one blocker to ready.

```powershell
python scripts/verify_browser_observation.py
```

This verifies one narrow application-evidence path. It does not prove safe use
against arbitrary public or enterprise applications.

## Explicit exclusions

Sprint 3 does not provide:

- autonomous crawling,
- free-form element picking in a browser UI,
- whole-page DOM or accessibility archives,
- screenshots,
- network capture,
- entered test-data capture,
- locator generation from arbitrary pages,
- page/component ownership changes,
- business-rule inference,
- LLM calls,
- POM generation,
- framework modification,
- selector healing,
- credentialed or enterprise sessions,
- formal user identity or authorization policy.
