# TestCartographer

> Maps application context into maintainable test automation.

**TestCartographer** is an experimental LLM-assisted tool for collecting,
organizing, verifying, and maintaining the context needed to adapt a reusable
test automation framework to a real application.

The project is intended to complement
[`qa-automation-framework`](https://github.com/MarcinMikula/qa-automation-framework).

## Status

**Sprint 1 — minimum context contract: complete**

The repository now contains a strict, provider-neutral local model for one UI
process.

Current evidence:

```text
23 deterministic tests passing
```

The implemented slice can:

- load and save one versioned process context as JSON,
- distinguish observed, provided, inferred, confirmed, unknown, stale, and
  conflicting knowledge,
- retain evidence references and basic sensitivity classification,
- reject malformed structures and dangling references,
- keep incomplete and conflicting contexts structurally valid,
- assess whether a valid context is ready for framework adaptation,
- export a committed JSON Schema for contract version `0.1`.

It cannot yet interview a user, observe a browser, call an LLM, generate a Page
Object, or modify `qa-automation-framework`.

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

## Sprint 1 contract

The current contract models one process and a bounded set of related context:

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

## Structural validity is not readiness

Sprint 1 separates two questions.

### Is the context structurally valid?

Pydantic validation checks, among other things:

- strict fields and schema version,
- globally unique entity identifiers,
- contiguous process-step order,
- valid action shape,
- page, component, element, test-data, and evidence references,
- element ownership,
- action-target availability on the declared page,
- locator-selection invariants,
- knowledge-status rules,
- timezone-aware timestamps.

Invalid input is rejected.

### Is the context ready for adaptation?

A valid bundle may still contain:

- explicit unknowns,
- unresolved conflicts,
- inferred business facts,
- unconfirmed expected outcomes,
- an unobserved primary locator,
- blocking open questions.

`assess_readiness()` reports deterministic blockers and warnings without
silently completing or rewriting the context.

```python
from test_cartographer.context import assess_readiness, load_context

context = load_context("testdata/context/valid/public_search_flow.json")
report = assess_readiness(context)

assert report.ready is True
```

## Reference fixtures

Sprint 1 includes four controlled JSON fixtures:

| Fixture | Structural result | Readiness result | Purpose |
|---|---:|---:|---|
| `valid/public_search_flow.json` | valid | ready | complete reference process |
| `incomplete/public_search_flow.json` | valid | blocked | explicit unknowns and open question |
| `conflicting/public_search_flow.json` | valid | blocked | conflicting locator evidence |
| `invalid/missing_evidence_reference.json` | rejected | not assessed | dangling provenance reference |

The fictional `.test` application is only a contract fixture. It is not yet a
browser target or evidence of an executable automation flow.

## Quick start

### Requirements

- Python 3.11 or newer
- PowerShell commands below assume Windows

### Create and activate a virtual environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install the project

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Run tests

```powershell
python -m pytest
```

Expected Sprint 1 result:

```text
23 passed
```

### Re-export the JSON Schema

```powershell
python scripts/export_context_schema.py
python -m pytest tests/unit/context/test_schema.py
```

The schema snapshot test prevents the Python contract and committed JSON Schema
from drifting silently.

## Current project structure

```text
test-cartographer/
├── docs/
│   ├── architecture-decisions.md
│   ├── context-contract.md
│   ├── future-ideas.md
│   ├── gaps.md
│   ├── known-limitations.md
│   ├── product-scope.md
│   ├── roadmap.md
│   └── testing-strategy.md
├── schemas/
│   └── context-bundle-v0.1.schema.json
├── scripts/
│   └── export_context_schema.py
├── src/
│   └── test_cartographer/
│       ├── __init__.py
│       └── context/
│           ├── __init__.py
│           ├── enums.py
│           ├── io.py
│           ├── models.py
│           └── readiness.py
├── testdata/
│   └── context/
│       ├── conflicting/
│       ├── incomplete/
│       ├── invalid/
│       └── valid/
├── tests/
│   └── unit/
│       └── context/
├── LEARNINGS.md
├── LICENSE
├── README.md
└── pyproject.toml
```

## Relationship with qa-automation-framework

The projects have separate responsibilities.

| Project | Responsibility |
|---|---|
| `qa-automation-framework` | Provides reusable POM/SOM architecture, conventions, fixtures, testing principles, and adaptation guidance |
| TestCartographer | Collects and verifies project-specific context, then helps map it into that architecture |

The resulting automation must remain normal Python, Playwright, and pytest
code. It should be understandable, reviewable, version-controlled, and usable
without TestCartographer during ordinary test execution.

## Guiding principles

1. **Context before code.** A generated interaction is not yet a meaningful
   automated test.
2. **Evidence before certainty.** Observations, supplied facts, and LLM
   inferences must remain distinguishable.
3. **Human ownership of correctness.** The tool may propose; evidence and human
   review decide.
4. **Architecture-aware generation.** Elements and actions must be mapped to
   appropriate Page Objects, components, workflows, fixtures, or tests.
5. **Small vertical slices.** Prove one complete process before adding broad
   integrations or autonomous behaviour.
6. **Security before cloud inference.** Browser-visible or Jira-accessible data
   is not automatically safe to send to an external model.
7. **Usability is part of quality.** A correct tool still fails if operating it
   takes more effort than a realistic alternative.
8. **Generated code must survive without the generator.** No hidden LLM runtime
   dependency is required for normal execution.

## Initial scope

The initial product direction is deliberately narrow:

- UI automation,
- Playwright with Python,
- pytest,
- Page Object Model,
- one selected process at a time,
- human-guided exploration,
- local collection and preprocessing,
- external LLM use only after a safe input boundary is defined,
- explicit human review before framework changes are accepted.

Service Object Model and API context may be added later, but they are not part
of the first vertical slice.

## Explicit non-goals for the first vertical slice

The first implementation will not attempt to:

- autonomously explore an entire application,
- generate a complete test suite from one prompt,
- replace a tester or domain expert,
- infer business correctness without a reliable test basis,
- integrate with every issue tracker or test-management system,
- support every browser framework or programming language,
- become a general test-management platform,
- reproduce a full enterprise model-based automation suite,
- silently repair or rewrite automation without review,
- reuse PhoenixQA as a hidden dependency.

## Validation direction

The product must eventually be compared against realistic alternatives:

```text
manual framework adaptation
vs.
human-led adaptation with DevTools, Playwright Codegen, and a general LLM
vs.
adaptation with TestCartographer
```

Evaluation must include more than test execution success:

- functional correctness,
- POM quality and code readability,
- reusability and maintainability,
- traceability to source information,
- unsupported assumptions and human corrections,
- setup and operation time,
- time to the first runnable test,
- number and quality of user interactions,
- time required to update automation after a change,
- LLM usage and cost,
- perceived difficulty and user confidence.

## Roadmap

| Sprint | Focus | Status |
|---|---|---|
| 0 | Product framing, boundaries, and validation direction | Done |
| 1 | Minimum context contract and local evidence model | Done |
| 2 | Human-guided process intake | Planned |
| 3 | Guided browser observation | Provisional |
| 4 | Bounded LLM context synthesis and POM proposal | Provisional |
| 5 | Framework handoff and first runnable test | Provisional |
| 6 | Review, traceability, and first end-to-end evaluation | Provisional |
| 7+ | Maintenance, external sources, comparative validation, and hardening | Parked until evidence |

See [`docs/roadmap.md`](docs/roadmap.md).

## Documentation

| Document | Purpose |
|---|---|
| [`LEARNINGS.md`](LEARNINGS.md) | Chronological problem, reasoning, decisions, experiments, and conclusions |
| [`docs/context-contract.md`](docs/context-contract.md) | Contract concepts, invariants, fixtures, and readiness boundary |
| [`docs/architecture-decisions.md`](docs/architecture-decisions.md) | Accepted implementation decisions and consequences |
| [`docs/testing-strategy.md`](docs/testing-strategy.md) | Current deterministic test layers and future evidence gates |
| [`docs/gaps.md`](docs/gaps.md) | Concrete missing capabilities and their dependencies |
| [`docs/product-scope.md`](docs/product-scope.md) | Product responsibility, users, inputs, outputs, boundaries, and success criteria |
| [`docs/roadmap.md`](docs/roadmap.md) | Sprint sequence, gates, and current delivery status |
| [`docs/known-limitations.md`](docs/known-limitations.md) | Current boundaries and unsupported claims |
| [`docs/future-ideas.md`](docs/future-ideas.md) | Useful ideas intentionally parked outside current scope |

## Related projects

- [`qa-automation-framework`](https://github.com/MarcinMikula/qa-automation-framework)
  — the reusable framework skeleton TestCartographer is intended to adapt.
- [`PhoenixQA`](https://github.com/MarcinMikula/PhoenixQA)
  — a separate experiment in runtime recovery and selector healing.
- [`llm-qa-toolkit`](https://github.com/MarcinMikula/llm-qa-toolkit)
  — a separate evaluation harness that may later inform validation of
  LLM-produced decisions.
- [`defect-pilot`](https://github.com/MarcinMikula/defect-pilot)
  — a separate defect-driven retest workflow.

## License

MIT License. See [`LICENSE`](LICENSE).
