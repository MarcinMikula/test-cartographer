# TestCartographer

> Maps application context into maintainable test automation.

**TestCartographer** is an experimental LLM-assisted tool for collecting,
organizing, verifying, and maintaining the context needed to adapt a reusable
test automation framework to a real application.

The project is intended to complement
[`qa-automation-framework`](https://github.com/MarcinMikula/qa-automation-framework).

## Status

**Sprint 0 — product framing: complete**

The repository currently contains product documentation only. No executable
tool, browser integration, LLM workflow, persistence layer, or framework
adapter has been implemented yet.

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

## What TestCartographer should eventually do

### Acquire context

Collect relevant information through several complementary paths:

- adaptive questions answered by a tester or domain expert,
- project artefacts such as issues, test cases, requirements, and API
  documentation,
- human-guided observation of a running application,
- existing automation code, execution reports, traces, and screenshots.

### Model context

Organize knowledge about:

- applications and environments,
- roles and authentication,
- business processes and test conditions,
- pages, components, elements, and states,
- locator candidates and technical constraints,
- expected outcomes, risks, and test data,
- evidence, provenance, confidence, and unresolved questions.

### Adapt the framework

Use confirmed context to propose or prepare:

- Page Objects and reusable components,
- workflow helpers and fixtures,
- test-data models,
- selectors and locator placement,
- test skeletons and assertions requiring human review,
- documentation explaining assumptions and source evidence.

### Support maintenance

Later versions may detect and analyse changes such as:

- locator drift,
- DOM restructuring,
- changed required fields,
- moved or removed actions,
- changed workflows or business rules,
- automation artefacts affected by an application change.

The tool should explain impact and propose updates. Silent, unreviewed rewriting
is not the target.

## Relationship with qa-automation-framework

The projects have separate responsibilities.

| Project | Responsibility |
|---|---|
| `qa-automation-framework` | Provides reusable POM/SOM architecture, conventions, fixtures, testing principles, and adaptation guidance |
| TestCartographer | Collects and verifies project-specific context, then helps map it into that architecture |

The resulting automation must remain normal Python, Playwright, and pytest
code. It should be understandable, reviewable, version-controlled, and usable
without TestCartographer during ordinary test execution.

## Intended user

The initial user is a software tester or test automation engineer who:

- understands the tested process or can consult someone who does,
- can guide the tool through a selected application flow,
- can validate business assumptions and expected results,
- wants maintainable Playwright and pytest automation,
- accepts responsibility for final review and correctness.

The first versions are not intended to remove the need for testing knowledge,
application knowledge, or code review.

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

## First vertical-slice hypothesis

A small end-to-end slice should eventually prove this flow:

```text
select one process
→ collect minimum human context
→ observe the guided browser flow
→ store a small structured context model
→ identify missing or inferred information
→ propose Page Object and test artefacts
→ place them in qa-automation-framework
→ execute one test
→ review assumptions, evidence, and result
```

Jira ingestion, autonomous navigation, broad application modelling, and
self-healing are deferred until this narrower workflow provides evidence that a
dedicated tool adds value.

## Validation direction

The product must be compared against realistic alternatives:

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

Potential validation targets progress from simple public pages, through modern
dynamic frontends and a controlled reference application, to a safe
Salesforce-style enterprise flow.

## Roadmap

| Sprint | Focus | Status |
|---|---|---|
| 0 | Product framing, boundaries, success criteria, and first vertical-slice direction | Done |
| 1 | Minimum context contract and local evidence model | Planned |
| 2 | Human-guided process intake | Provisional |
| 3 | Guided browser observation | Provisional |
| 4 | Bounded LLM context synthesis and POM proposal | Provisional |
| 5 | Framework handoff and first runnable test | Provisional |
| 6 | Review, traceability, and first end-to-end evaluation | Provisional |
| 7+ | Maintenance, external sources, comparative validation, and hardening | Parked until evidence |

The detailed roadmap is intentionally provisional beyond Sprint 1. Each sprint
must be refined using evidence from the previous slice.

See [`docs/roadmap.md`](docs/roadmap.md).

## Documentation

| Document | Purpose |
|---|---|
| [`LEARNINGS.md`](LEARNINGS.md) | Chronological problem, reasoning, decisions, experiments, and conclusions |
| [`docs/product-scope.md`](docs/product-scope.md) | Product responsibility, users, inputs, outputs, boundaries, and success criteria |
| [`docs/roadmap.md`](docs/roadmap.md) | Sprint sequence, gates, and current delivery status |
| [`docs/known-limitations.md`](docs/known-limitations.md) | Current boundaries and missing evidence |
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
