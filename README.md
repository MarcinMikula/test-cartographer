# TestCartographer

> Maps application context into maintainable test automation.

**TestCartographer** is an experimental LLM-assisted tool for collecting,
organizing, verifying, and maintaining the context needed to adapt a reusable
test automation framework to a real application.

The project is intended to complement
[`qa-automation-framework`](https://github.com/MarcinMikula/qa-automation-framework).

## Status

**Sprint 2 — deterministic human-guided intake: complete**

Current evidence:

```text
47 deterministic tests passing
```

The repository now provides two executable boundaries:

1. a strict, provider-neutral `ContextBundle` for one UI process,
2. a resumable command-line intake that fills and reviews the human-answerable
   part of that bundle without an LLM.

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
- distinguish human-intake completion from full adaptation readiness.

It still cannot observe a browser, call an LLM, propose a Page Object, generate
a test, or modify `qa-automation-framework`.

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

TestCartographer should build a verified, reusable map of the tested
application and use it to support controlled framework adaptation.

```text
human knowledge
+ project artefacts
+ guided application observation
+ existing repository and execution evidence
                         |
                         v
          structured application context
                         |
                         v
       qa-automation-framework adaptation
                         |
                         v
         reviewed and executable automation
```

The first useful product is not expected to be an autonomous application
crawler or a one-prompt test-suite generator.

The first useful product should understand one small, human-guided process well
enough to propose a maintainable Page Object representation and help create one
reviewed, runnable test in a copy of `qa-automation-framework`.

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

A completed human intake can still be blocked because, for example, a primary
locator has not been observed. That is expected before Sprint 3.

## Quick start

### Requirements

- Python 3.11 or newer
- PowerShell commands below assume Windows

### Install

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Run tests

```powershell
python -m pytest
```

Expected Sprint 2 result:

```text
47 passed
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

### Re-export contract schemas

```powershell
python scripts/export_context_schema.py
python scripts/export_intake_schema.py
python -m pytest tests/unit/context/test_schema.py `
    tests/unit/intake/test_intake_schema.py
```

## Current project structure

```text
test-cartographer/
├── docs/
│   ├── architecture-decisions.md
│   ├── context-contract.md
│   ├── intake-workflow.md
│   ├── testing-strategy.md
│   └── ...
├── schemas/
│   ├── context-bundle-v0.1.schema.json
│   └── intake-session-v0.1.schema.json
├── scripts/
│   ├── export_context_schema.py
│   └── export_intake_schema.py
├── src/test_cartographer/
│   ├── cli.py
│   ├── context/
│   └── intake/
├── testdata/context/
├── tests/
│   ├── integration/
│   └── unit/
├── LEARNINGS.md
├── LICENSE
├── README.md
└── pyproject.toml
```

## What Sprint 2 proves

- a strict context can drive a deterministic question queue,
- human answers can become evidence-linked knowledge without an LLM,
- required collection and explicit confirmation can remain separate phases,
- `UNKNOWN` and deferred answers do not create infinite question loops,
- a session can be saved after every interaction and resumed,
- operator effort can be measured without storing duplicate answer text in the
  interaction log,
- human-intake completion can remain separate from browser and adaptation
  readiness.

## What Sprint 2 does not prove

- that the context shell can be created from scratch without JSON,
- that the questions are sufficient or pleasant for a real tester,
- that open-question answers are mapped into a rich domain model,
- that browser evidence can be collected safely,
- that locator candidates are correct,
- that an LLM can synthesize a maintainable POM,
- that `qa-automation-framework` can be adapted automatically,
- that the tool saves time or effort compared with realistic alternatives.

## Relationship with qa-automation-framework

| Project | Responsibility |
|---|---|
| `qa-automation-framework` | Provides reusable POM/SOM architecture, conventions, fixtures, testing principles, and adaptation guidance |
| TestCartographer | Collects and verifies project-specific context, then helps map it into that architecture |

The resulting automation must remain normal Python, Playwright, and pytest
code. It should be understandable, reviewable, version-controlled, and usable
without TestCartographer during ordinary test execution.

## Roadmap

| Sprint | Focus | Status |
|---|---|---|
| 0 | Product framing and project boundaries | Done |
| 1 | Minimum context contract and local evidence model | Done |
| 2 | Deterministic human-guided process intake | Done |
| 3 | Guided browser observation | Planned |
| 4 | Bounded LLM synthesis and POM proposal | Provisional |
| 5 | Framework handoff and first runnable test | Provisional |
| 6 | First end-to-end evaluation | Provisional |
| 7+ | Maintenance, integrations, comparative validation, and hardening | Parked |

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
   must not require a live LLM.

## Documentation

| Document | Purpose |
|---|---|
| [`LEARNINGS.md`](LEARNINGS.md) | Chronological reasoning, experiments, decisions, and conclusions |
| [`docs/product-scope.md`](docs/product-scope.md) | Product responsibility, boundaries, and success criteria |
| [`docs/context-contract.md`](docs/context-contract.md) | Semantic contract version `0.1` |
| [`docs/intake-workflow.md`](docs/intake-workflow.md) | Sprint 2 question, answer, review, session, and CLI behaviour |
| [`docs/architecture-decisions.md`](docs/architecture-decisions.md) | Accepted implementation decisions |
| [`docs/testing-strategy.md`](docs/testing-strategy.md) | Current test layers and evidence limits |
| [`docs/gaps.md`](docs/gaps.md) | Open implementation gaps and closed slices |
| [`docs/known-limitations.md`](docs/known-limitations.md) | Current boundaries and unsupported claims |
| [`docs/future-ideas.md`](docs/future-ideas.md) | Parked ideas without delivery commitment |

## Related projects

- [`qa-automation-framework`](https://github.com/MarcinMikula/qa-automation-framework)
  — reusable framework skeleton to be adapted.
- [`PhoenixQA`](https://github.com/MarcinMikula/PhoenixQA)
  — separate runtime recovery and selector-healing experiment.
- [`llm-qa-toolkit`](https://github.com/MarcinMikula/llm-qa-toolkit)
  — separate LLM evaluation harness.
- [`defect-pilot`](https://github.com/MarcinMikula/defect-pilot)
  — separate defect-driven retest workflow.

## License

MIT License. See [`LICENSE`](LICENSE).
