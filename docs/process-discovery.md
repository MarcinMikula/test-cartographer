# Guided multi-element process discovery — Sprint 9

## Purpose

Sprint 9 converts the human-reviewed process brief produced by Sprint 8 into a
bounded, evidence-backed UI process map. It discovers several elements and
locator candidates on one explicitly authorized page without crawling the
application or allowing an LLM to choose a browser element.

## Reference flow

```text
Sprint 8 discovery-ready ContextBundle
→ one explicit discovery plan
→ one authorized local page
→ bounded semantic candidate scan
→ deterministic target ranking
→ two unique selections
→ one deliberate ambiguity
→ local LLM phrases one clarification question
→ human selects the intended candidate
→ separate discovery acceptance
→ observed page/component/elements/locators/steps
→ full ContextBundle readiness
```

The controlled reference process contains three targets:

1. search query input,
2. search action,
3. results region.

The page deliberately contains two visible buttons with the same accessible
name `Search`. Both are valid browser candidates and both have unique
`data-testid` locators. The ranking algorithm therefore records an ambiguity
instead of silently selecting one.

## Deterministic browser boundary

The scanner examines only an allowlisted set of potentially relevant elements:

```text
input
button
select
textarea
explicit role
explicit data-testid
list
table
aria-live region
```

It persists only bounded candidate descriptors:

- tag name,
- semantic role,
- bounded semantic name derived from label, `aria-label`, placeholder, button
  accessible text, test ID, ID, or name,
- allowlisted attributes,
- visibility, enabled, and editability state,
- generated locator candidates and their match counts.

It does not persist:

- input values,
- generic page text,
- raw HTML,
- the raw page,
- screenshots,
- network traffic,
- cookies or storage state.

## Ranking and ambiguity

Each target is defined by:

- a human-readable purpose,
- an action kind,
- expected semantic roles,
- ownership by the page or a declared component,
- optional symbolic test data,
- optional expected-outcome relationship.

The deterministic scorer uses:

- semantic-token overlap,
- role compatibility,
- action compatibility,
- availability of at least one unique locator.

A target becomes:

- `selected` when one candidate clearly leads,
- `ambiguous` when the leading candidates are within the configured score
  delta,
- `missing` when no candidate reaches the minimum score.

No LLM score or free-form model judgement participates in candidate ranking.

## LLM authority boundary

The local model receives only one minimized ambiguity packet:

- ambiguity ID,
- target description,
- action kind,
- exact candidate IDs,
- bounded candidate descriptors and locator summaries.

The model may:

- phrase one clarification question,
- explain why human confirmation is required.

The model may not:

- add, remove, or replace candidate IDs,
- choose a candidate,
- write a selector into context,
- request credentials, tokens, cookies, secrets, or input values,
- declare the discovery accepted or ready.

The returned JSON must preserve the exact ambiguity and candidate set. Raw
prompts and raw responses are hashed for traceability but are not persisted.

## Human authority and review

The human performs two independent decisions:

1. resolves each ambiguity by selecting one allowlisted candidate,
2. accepts or rejects the completed discovery run.

Only an accepted run can update the `ContextBundle`.

## Context update

The accepted reference discovery replaces the Sprint 8 placeholder with:

- one observed page,
- one observed search-form component,
- three observed UI elements,
- unique observed locator candidates,
- one symbolic test-data requirement,
- four process steps:
  - navigate,
  - fill,
  - click,
  - read,
- one expected outcome linked to the results region,
- application evidence for every discovered target.

The existing context readiness evaluator remains authoritative. Sprint 9 does
not introduce a separate shortcut to synthesis readiness.

## Measurements retained

The discovery run records:

- candidate count,
- target count,
- target rankings,
- deterministic selections,
- ambiguity count,
- human selections,
- provider turns,
- model and provider identity,
- prompt/response hashes and sizes,
- model latency,
- review time,
- privacy flags.

The reference run is expected to show:

```text
4 bounded candidates
3 process targets
2 deterministic selections
1 ambiguity
1 human element selection
1 local-LLM clarification turn
0 unresolved ambiguities
```

## What Sprint 9 proves

- a discovery-ready process brief can drive bounded browser discovery,
- several elements can be discovered in one authorized page session,
- locator candidates can be generated and checked for uniqueness,
- deterministic ambiguity detection can prevent false certainty,
- a local LLM can improve the human-facing question without becoming the
  selection authority,
- accepted discovery can make the existing context fully ready for POM
  synthesis.

## What Sprint 9 does not prove

- whole-application discovery,
- arbitrary multi-page navigation,
- authentication or SSO/MFA handling,
- reliable discovery on modern enterprise component systems,
- semantic correctness of every generated locator,
- automatic interaction with destructive controls,
- automatic resolution of missing targets,
- fixture-assisted end-to-end Creation Flow orchestration,
- human-triggered interactive Creation Flow,
- measured savings versus DevTools or Playwright Codegen,
- Salesforce usefulness.

Those claims remain outside Sprint 9 and are not implied by the controlled
reference page.
