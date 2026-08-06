# Proactive frontend/context regression

Sprint 13 adds the first controlled proof that TestCartographer can detect
automation-relevant frontend drift even when the current framework test remains
green.

## Proven vertical slice

```text
accepted application map and observation inventory
→ human authorizes one bounded post-deployment run
→ the same independent framework test passes on baseline and current frontend
→ Cartographer re-observes two approved mapped elements
→ one covered element remains stable
→ one mapped but currently uncovered element exposes locator drift
→ deterministic change-impact report
→ human accepts the review-only report
```

The controlled deployment changes the `Sort results` locator from
`catalog-sort` to `catalog-sort-control`. The current framework test automates
only Search, so it remains green before and after the change. Proactive
re-observation still marks the mapped Sort element as stale context.

## Authority and safety boundary

The real operator makes exactly three blocking decisions:

1. authorize the proactive run,
2. authorize the exact accepted inventory and budget,
3. accept or reject the complete change-impact report.

The run reuses accepted bootstrap and process context. It does not restart
intake. The inventory is explicit, human accepted, public, no-auth, route
allowlisted, and limited to one page and two elements.

## Persisted evidence

The run persists only strict structured evidence:

- expected and current bounded locator descriptors,
- semantic and expected visible-match counts,
- allowlisted element attributes,
- stable, locator-drift, missing, or ambiguous disposition,
- current-test risk versus mapped-context staleness,
- framework probe counts before and after,
- operator and privacy flags.

Raw page content, HTML, screenshots, input values, credentials, console output,
traces, and live-model prompts or responses are not persisted.

## Explicit non-capabilities

Sprint 13 does not:

- schedule or trigger itself from a deployment system,
- crawl an application or expand the accepted inventory,
- authenticate to a protected application,
- claim that detected drift is an application defect,
- update ContextBundle status automatically,
- generate or apply a locator patch,
- call an LLM,
- prove enterprise-scale regression or operational savings.

A detected change is review evidence. Maintenance or map updates remain a
later, separately authorized transition.
