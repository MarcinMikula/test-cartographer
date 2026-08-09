# Checkpoint 14.5 — documentation truth cleanup and validation-first roadmap reset

## Why this checkpoint exists

Sprint 14 completed a long architecture-building phase:

```text
context
→ intake
→ browser evidence
→ synthesis
→ repository adaptation
→ source delivery
→ independent execution evidence
→ reactive maintenance
→ proactive regression
→ incremental expansion
```

The project now has enough controlled lifecycle coverage that adding more
features by speculation would increase complexity faster than product evidence.

Checkpoint 14.5 therefore changes the development mode:

> from building the lifecycle we think we need
> to challenging the lifecycle we already built on applications we do not
> control.

This checkpoint changes documentation and planning only. It does not add product
runtime behavior.

## Documentation problem found

After Sprint 14:

- `README.md` and the Sprint 14 roadmap section were current,
- several cross-project documents still contained older "current state"
  statements from much earlier sprints,
- `known-limitations.md` still contained historical claims such as 104 tests,
  no runnable generated test, and no framework adapter,
- `product-scope.md` described its current implementation boundary at Sprint 7,
- `gaps.md` mixed closed historical slices, stale targets, and duplicate gap
  numbering.

For a product built around freshness and evidence, stale current-state
documentation is itself a governance defect.

## Documentation rule

After this checkpoint:

- `LEARNINGS.md` owns chronological reasoning,
- `architecture-decisions.md` owns accepted durable decisions,
- `product-scope.md` states the current product boundary,
- `known-limitations.md` is a replace-in-place current-state index,
- `gaps.md` is a prioritized current gap index,
- `future-ideas.md` contains only genuinely parked ideas,
- `roadmap.md` describes active/provisional delivery direction.

Do not preserve obsolete statements in current-state indexes for historical
reasons. Git history and `LEARNINGS.md` already preserve history.

## Updated product focus

TestCartographer remains a **frontend/UI/POM tool**.

Primary intended users are AI-assisted testing professionals:

- automation testers,
- senior manual testers with strong application/domain knowledge,
- test analysts,
- quality engineers.

A general application developer is not the comparison baseline.

Deterministic rules remain internal guardrails.

API/SOM adaptation is removed from the TestCartographer product roadmap.

## Highest-priority core gap

Persistent project/bootstrap knowledge becomes the next core priority.

The product needs a versioned `ProjectProfile` with selective invalidation so
that later flows do not repeatedly ask application/environment/framework/model/
policy/authentication bootstrap questions.

Sprint 14 demonstrates reuse but not durable cross-run lifecycle.

## Validation-first roadmap

The reset roadmap is:

```text
Checkpoint 14.5
documentation truth + roadmap reset

Sprint 15
persistent ProjectProfile + bootstrap reuse/invalidation

Sprint 16
validation protocol/readiness and repeatable evidence package

Sprint 17
external validation I:
simple public + dynamic public targets

Sprint 18
external validation II:
multi-page + difficult/low-control public targets

Sprint 19
minimum authentication profiles + credentialed validation

Sprint 20
enterprise/Salesforce validation

Sprint 21
comparative usability/economics + v1.0 decision
```

Numbers beyond Sprint 15 are provisional and may change when evidence changes.

## Validation dimensions

Every validation target should be classified on at least two axes.

### Technical difficulty

- simple/static,
- dynamic/script-heavy,
- multi-page/component/state,
- difficult/scraping-resistant,
- credentialed,
- enterprise/component-heavy.

### Degree of control

- controlled local fixture,
- externally hosted but predictable target,
- public application not owned by the project,
- low-control/dynamic public application,
- credentialed external system,
- enterprise system constrained by security/identity policy.

The second axis prevents the project from confusing fixture compatibility with
product generality.

## Evidence-first development rule

After external validation begins, no major new abstraction should be built only
because the team can imagine needing it.

Use:

```text
real validation
→ concrete failure/friction
→ evidence
→ current-model assessment
→ smallest justified implementation
→ repeat the validation
```

This applies to maintenance classes, graph modelling, impact analysis, browser
capture, source editing, authentication strategies, and evidence types.

## Human factors

Human participation is not automatically technical debt.

The product intentionally retains human authority for:

- business truth,
- risk,
- expected outcomes,
- semantic ambiguity,
- access authorization,
- review of consequential changes.

SSO/MFA may legitimately require interactive human login.

The problem to eliminate is **low-value repetitive human work**, not every human
decision.

## v1 value and kill criterion

Technical completion is insufficient.

Before v1.0, TestCartographer must demonstrate on external applications that the
workflow is useful for its intended testing professionals.

The project should be reconsidered if it proves:

- significantly slower without compensating quality gains,
- difficult to learn or operate,
- dominated by repetitive review,
- correction-heavy,
- more complex than simpler tools for the same outcome.

A future UI/IDE layer is postponed until after the core workflow is evaluated.
A better interface may improve a useful workflow; it cannot make an
economically poor workflow valuable.

## Checkpoint acceptance

This checkpoint is accepted when:

- current-state documents contain no known pre-Sprint-14 false claims,
- gaps use the new `CORE / VALIDATION / ENTERPRISE / PARKED / OUT-OF-SCOPE`
  taxonomy,
- ProjectProfile is the next P0 core gap,
- roadmap is validation-first,
- external validation explicitly increases both difficulty and lack of control,
- API/SOM is explicitly outside TestCartographer product scope,
- UI remains post-v1 evaluation,
- the product source/test/schema surface is unchanged,
- the existing 339-test baseline remains green.
