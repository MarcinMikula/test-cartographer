# TestCartographer

> Maps application context into maintainable test automation.

**TestCartographer** is an experimental LLM-assisted tool for collecting,
organizing, verifying, and maintaining the context needed to adapt a reusable
test automation framework to a real application.

Together with
[`qa-automation-framework`](https://github.com/MarcinMikula/qa-automation-framework),
TestCartographer is intended to form one automation lifecycle with two
separately executable modules. The framework owns normal test execution;
TestCartographer owns context acquisition, LLM-assisted adaptation, maintenance,
and expansion.

## Status

**Sprint 3 — bounded guided browser observation: complete**

**Architecture checkpoint A — two-module lifecycle alignment: complete in documentation**

Current evidence:

```text
66 tests passing with Playwright Chromium
controlled readiness transition verified end to end
```

The repository now provides three executable boundaries:

1. a strict, provider-neutral `ContextBundle` for one UI process,
2. a resumable deterministic intake for human-answerable context,
3. a bounded Playwright observation that verifies one selected locator and
   requires human acceptance before context changes.

The current workflow can:

- load a structurally valid but incomplete process context,
- derive an ordered question queue from explicit context gaps,
- collect free-text answers as `PROVIDED` human evidence,
- preserve explicit `UNKNOWN` and deferred questions,
- review and confirm supplied business values,
- keep browser-only blockers outside the human questionnaire,
- save after every interaction and resume later,
- export the current `ContextBundle`,
- measure question count, answer actions, and active response time,
- distinguish human-intake completion from full adaptation readiness,
- open one user-authorized page through Playwright,
- verify one existing primary locator against exactly one visible target,
- persist a minimized observation and require explicit accept/reject review,
- promote only an accepted locator to `OBSERVED`.

It still cannot autonomously explore an application, call an LLM, propose a
Page Object, generate a test, or modify `qa-automation-framework`.

## The problem

A reusable automation framework can provide architecture, conventions,
fixtures, Page Object Model patterns, and testing principles. It cannot know
the application that will eventually be automated.

A real project must still supply and validate knowledge about:

- the purpose and risk of the automated flow,
- business rules and expected outcomes,
- application pages, components, states, and navigation,
- DOM structure and locator candidates,
- user roles, permissions, environments, and test data,
- existing requirements, defects, test cases, and documentation,
- the current automation repository and its conventions,
- application changes that may invalidate existing automation.

This knowledge is usually fragmented across people, project artefacts, the
running application, and existing code. Simple code generation does not solve
that problem.

## Product direction

TestCartographer and `qa-automation-framework` are two modules of one lifecycle.

```text
TestCartographer
→ context, application map, evidence, LLM-assisted proposals, maintenance

qa-automation-framework
→ accepted POM, fixtures, data, tests, configuration, execution, assertions
```

The creation path combines human testing knowledge, bounded LLM assistance,
Cartographer evidence, and the framework's architecture. The project uses
**AItomatyzacja testów** as an informal shorthand for AI-supported automation
engineering, not fully autonomous test creation.

Normal test execution remains independent of TestCartographer and a live LLM.
Future maintenance reconnects the modules through bounded execution evidence,
reactive failure analysis, and scheduled post-deployment re-observation.

The first useful product is not expected to be an autonomous application
crawler or a one-prompt test-suite generator. It should understand one small,
human-guided process well enough to propose a maintainable POM representation,
help adapt `qa-automation-framework`, and produce one reviewed, runnable test.

See [`docs/system-lifecycle.md`](docs/system-lifecycle.md).

## Implemented architecture

### Context contract

`ContextBundle` version `0.1` models one UI process:

```text
ContextBundle
├── application
├── process
│   ├── purpose, risk, role, and preconditions
│   ├── ordered UI steps
│   └── observable expected outcomes
├── pages and reusable components
├── UI elements and locator candidates
├── symbolic test-data requirements
├── evidence and provenance references
├── open questions
└── conflicts and resolutions
```

The contract deliberately stores **symbolic test-data requirements**, not real
credentials or business values.

See [`docs/context-contract.md`](docs/context-contract.md).

### Deterministic intake

Sprint 2 adds a stage-specific workflow:

```text
structurally valid incomplete ContextBundle
→ deterministic required questions
→ PROVIDED human evidence
→ explicit review questions
→ CONFIRMED business context
→ saved session and exported ContextBundle
```

Question selection is rule-based. It does not use a free-form LLM interviewer.

The current human-answerable targets are:

- process purpose,
- business risk,
- user role,
- preconditions,
- expected outcomes,
- explicit open questions,
- conflict resolutions.

Browser-only issues such as an inferred or missing primary locator remain full
adaptation blockers but do not become questions for the human intake.

See [`docs/intake-workflow.md`](docs/intake-workflow.md).

### Bounded browser observation

Sprint 3 adds a separate `BrowserObservation` contract and CLI workflow:

```text
human-reviewed context
→ authorize one URL and one existing element ID
→ resolve one existing primary locator through Playwright
→ require exactly one visible target
→ persist only allowlisted target attributes
→ accept or reject the mapping
→ promote only an accepted locator to OBSERVED
```

The observation excludes input values, text content, HTML, screenshots, and
whole-page capture. It does not discover a workflow or generate selectors.

See [`docs/browser-observation.md`](docs/browser-observation.md).

## Structural validity, intake completion, and adaptation readiness

The project deliberately separates three questions.

### 1. Is the bundle structurally valid?

Pydantic validation rejects malformed structures, impossible actions, duplicate
identifiers, invalid ownership, dangling references, and invalid knowledge
states.

### 2. Is the human intake complete?

`assess_intake()` considers only issues that a tester or domain expert can
answer in the current workflow.

A session may be:

- `active` — another deterministic question is available,
- `paused` — the user stopped and can resume,
- `complete` — no non-deferred collection or review question remains and no
  human-intake blocker remains,
- `blocked` — required information remains unresolved but every current
  question was deferred or marked unknown.

### 3. Is the context ready for framework adaptation?

`assess_readiness()` also checks application and automation evidence.

A completed human intake can still be blocked because a primary locator has not
been observed. Sprint 3 resolves this only through accepted browser evidence.

## Quick start

### Requirements

- Python 3.11 or newer
- PowerShell commands below assume Windows

### Install

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,browser]"
python -m playwright install chromium
```

### Run tests

```powershell
python -m pytest
```

Expected Sprint 3 result after Chromium installation:

```text
66 passed
```

### Start a reference intake

The controlled Sprint 1 incomplete fixture is used as the input shell:

```powershell
test-cartographer intake start `
    --context testdata/context/incomplete/public_search_flow.json `
    --session .test-cartographer/public-search-session.json `
    --session-id intake_public_search
```

### Run or resume the intake

```powershell
test-cartographer intake run `
    --session .test-cartographer/public-search-session.json
```

Supported commands inside the session:

```text
:confirm  accept the displayed current value
:unknown  explicitly state that the answer is not known
:skip     defer the current question
:quit     save and pause the session
```

Answers entered as normal text become `PROVIDED`. When all required collection
questions are resolved, the tool enters a review phase and asks the user to
confirm or correct supplied business values.

### Inspect status

```powershell
test-cartographer intake status `
    --session .test-cartographer/public-search-session.json
```

The status includes:

- session state,
- human-intake blockers and warnings,
- full adaptation blockers,
- next deterministic question,
- interaction counts,
- active answer time.

### Retry deferred questions

```powershell
test-cartographer intake run `
    --session .test-cartographer/public-search-session.json `
    --retry-deferred
```

### Export the current context

```powershell
test-cartographer intake export `
    --session .test-cartographer/public-search-session.json `
    --context .test-cartographer/public-search-context.json
```


### Verify the controlled browser boundary

```powershell
python scripts/verify_browser_observation.py
```

The verifier serves the local reference page on loopback, opens it with
Chromium, validates the inferred Search button locator, accepts the observation,
and confirms that full readiness changes from one blocker to ready.

### Capture and review one observation

Start a local server in one terminal:

```powershell
python -m http.server 8765 --directory testdata/browser
```

Capture in another terminal:

```powershell
test-cartographer observe capture `
    --context testdata/context/observation_ready/public_search_flow.json `
    --url http://127.0.0.1:8765/public_catalog.html `
    --element-id el_search_submit `
    --observation .test-cartographer/search-submit-observation.json `
    --observation-id obs_search_submit `
    --sensitivity public
```

Accept and write an updated context copy:

```powershell
test-cartographer observe review `
    --observation .test-cartographer/search-submit-observation.json `
    --decision accepted `
    --reason "The target and locator mapping are correct." `
    --context testdata/context/observation_ready/public_search_flow.json `
    --output-context .test-cartographer/public-search-observed.json
```

### Re-export contract schemas

```powershell
python scripts/export_context_schema.py
python scripts/export_intake_schema.py
python scripts/export_observation_schema.py
python -m pytest tests/unit/context/test_schema.py `
    tests/unit/intake/test_intake_schema.py `
    tests/unit/observation/test_schema.py
```

## Current project structure

```text
test-cartographer/
├── docs/
│   ├── architecture-decisions.md
│   ├── context-contract.md
│   ├── intake-workflow.md
│   ├── browser-observation.md
│   ├── testing-strategy.md
│   └── ...
├── schemas/
│   ├── context-bundle-v0.1.schema.json
│   ├── intake-session-v0.1.schema.json
│   └── observation-v0.1.schema.json
├── scripts/
│   ├── export_context_schema.py
│   ├── export_intake_schema.py
│   ├── export_observation_schema.py
│   └── verify_browser_observation.py
├── src/test_cartographer/
│   ├── cli.py
│   ├── context/
│   ├── intake/
│   └── observation/
├── testdata/
│   ├── browser/
│   ├── context/
│   └── observation/
├── tests/
│   ├── integration/
│   └── unit/
├── LEARNINGS.md
├── LICENSE
├── README.md
└── pyproject.toml
```

## What Sprint 3 proves

- one existing locator can be resolved through Playwright against a controlled
  real page,
- exact uniqueness and visibility can be required before evidence is created,
- the selected target can be represented without values, page text, HTML,
  screenshots, or whole-page capture,
- capture and human acceptance can remain separate authority stages,
- rejection can leave context unchanged,
- accepted application evidence can promote one locator from `INFERRED` to
  `OBSERVED`,
- the final reference readiness blocker can be removed without changing
  business context or unrelated application structure.

## What Sprint 3 does not prove

- greenfield application, page, element, or locator discovery,
- safety against arbitrary public or enterprise applications,
- authentication, iframes, Shadow DOM, multiple tabs, or complex waits,
- long-term locator stability or semantic quality,
- complete redaction and privacy protection,
- LLM synthesis or POM proposal quality,
- `qa-automation-framework` adaptation,
- generated test correctness,
- easier operation or time savings compared with realistic alternatives.

## One lifecycle, two separately executable modules

| Module | Primary responsibility |
|---|---|
| `qa-automation-framework` | Execution plane: accepted POM/components, fixtures, test data, configuration, secret retrieval, pytest/Playwright execution, assertions, reports, and future bounded execution evidence |
| TestCartographer | Engineering and maintenance plane: context acquisition, application mapping, bounded LLM proposals, adaptation plans, change analysis, proactive re-observation, and expansion |

The modules cooperate through a future shared project workspace, non-secret
project/authentication profiles, repository changes, and execution evidence.
They should not share credentials by copying values or couple Cartographer to
pytest fixtures.

The resulting automation remains normal Python, Playwright, and pytest code. It
must be understandable, reviewable, version-controlled, and usable without
TestCartographer during ordinary execution.

See:

- [`docs/system-lifecycle.md`](docs/system-lifecycle.md),
- [`docs/authentication-strategies.md`](docs/authentication-strategies.md).

## Roadmap

| Sprint | Focus | Status |
|---|---|---|
| 0 | Product framing and project boundaries | Done |
| 1 | Minimum context contract and local evidence model | Done |
| 2 | Deterministic human-guided process intake | Done |
| 3 | Bounded guided browser observation | Done |
| Architecture checkpoint A | Two-module lifecycle, maintenance modes, authentication directions, and enterprise target | Done in documentation |
| 4 | Bounded LLM synthesis and POM proposal | Planned |
| 5 | Project workspace and framework adaptation plan | Provisional |
| 6 | First runnable framework test and creation-lifecycle evaluation | Provisional |
| 7–10 | Execution evidence, reactive/proactive maintenance, and expansion reuse | Parked |
| 11–13 | Enterprise authentication, Salesforce validation, comparative evaluation, and v1.0 decision | Parked |

See [`docs/roadmap.md`](docs/roadmap.md).

## Guiding principles

1. **Context before code.** A generated interaction is not yet a meaningful
   automated test.
2. **Evidence before certainty.** Observations, supplied facts, and inferences
   remain distinguishable.
3. **Human ownership of correctness.** Collection, review, and confirmation are
   explicit transitions.
4. **Architecture-aware generation.** Future output must fit Page Objects,
   components, workflows, fixtures, and tests deliberately.
5. **Small vertical slices.** Each sprint proves one boundary before the next
   uncertain layer is added.
6. **Security before cloud inference.** Browser-visible or Jira-accessible data
   is not automatically safe for an external model.
7. **Usability is part of quality.** Active user effort and operation time are
   measured from the first workflow.
8. **Generated code must survive without the generator.** Normal test execution
   must not require TestCartographer or a live LLM.
9. **Execution should feed maintenance without becoming maintenance.** The
   framework may collect bounded evidence; Cartographer analyses and evolves it.
10. **Maintenance is reactive and proactive.** Failed tests are one signal, but
    approved post-deployment re-observation must also detect uncovered drift.
11. **Enterprise relevance must be proven.** Public pages are stepping stones; a
    safe Salesforce flow remains a deliberate acceptance target.

## Documentation

| Document | Purpose |
|---|---|
| [`LEARNINGS.md`](LEARNINGS.md) | Chronological reasoning, experiments, decisions, and conclusions |
| [`docs/product-scope.md`](docs/product-scope.md) | Product responsibility, boundaries, and success criteria |
| [`docs/context-contract.md`](docs/context-contract.md) | Semantic contract version `0.1` |
| [`docs/intake-workflow.md`](docs/intake-workflow.md) | Sprint 2 question, answer, review, session, and CLI behaviour |
| [`docs/browser-observation.md`](docs/browser-observation.md) | Sprint 3 minimized Playwright capture, review, and context update |
| [`docs/system-lifecycle.md`](docs/system-lifecycle.md) | Creation, execution, reactive/proactive maintenance, expansion, and enterprise validation lifecycle |
| [`docs/authentication-strategies.md`](docs/authentication-strategies.md) | Parked storage-state, login-recipe, and interactive-login directions |
| [`docs/architecture-decisions.md`](docs/architecture-decisions.md) | Accepted implementation decisions |
| [`docs/testing-strategy.md`](docs/testing-strategy.md) | Current test layers and evidence limits |
| [`docs/gaps.md`](docs/gaps.md) | Open implementation gaps and closed slices |
| [`docs/known-limitations.md`](docs/known-limitations.md) | Current boundaries and unsupported claims |
| [`docs/future-ideas.md`](docs/future-ideas.md) | Parked ideas without delivery commitment |

## Related projects

- [`qa-automation-framework`](https://github.com/MarcinMikula/qa-automation-framework)
  — the execution-plane module and reusable framework skeleton that
  TestCartographer is intended to adapt and later help maintain.
- [`PhoenixQA`](https://github.com/MarcinMikula/PhoenixQA)
  — separate runtime recovery and selector-healing experiment.
- [`llm-qa-toolkit`](https://github.com/MarcinMikula/llm-qa-toolkit)
  — separate LLM evaluation harness.
- [`defect-pilot`](https://github.com/MarcinMikula/defect-pilot)
  — separate defect-driven retest workflow.

## License

MIT License. See [`LICENSE`](LICENSE).
