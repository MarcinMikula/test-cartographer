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

**Sprint 6 — controlled source delivery and first runnable framework test: complete**

**Architecture checkpoint A — two-module lifecycle alignment: complete in documentation**

Current evidence:

```text
153 tests expected with Playwright Chromium
controlled browser readiness transition verified end to end
bounded synthesis replay and human-review transition verified end to end
read-only framework inspection and adaptation-plan review verified end to end
controlled source review, patch application, and first runnable test verified end to end
```

The repository now provides six executable boundaries:

1. a strict, provider-neutral `ContextBundle` for one UI process,
2. a resumable deterministic intake for human-answerable context,
3. a bounded Playwright observation that verifies one selected locator and
   requires human acceptance before context changes,
4. a bounded LLM-facing request, strict POM proposal protocol, replay adapter,
   deterministic validator, and separate human review state,
5. a bounded workspace profile, read-only framework snapshot, deterministic
   file/symbol adaptation plan, and separate human review state,
6. an exact source patch, separate source review, fingerprint preflight, atomic
   application to a snapshot-bounded framework sandbox, and creation-lifecycle evaluation.

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
- promote only an accepted locator to `OBSERVED`,
- project ready context into a minimized provider-neutral synthesis request,
- exclude URLs, routes, raw source references, notes, hashes, and secret values,
- replay one stored raw model output through a strict parser,
- distinguish protocol failure from substantive proposal rejection,
- validate page, component, method, locator, data, fixture, test, and outcome
  references deterministically,
- keep the logical proposal pending until explicit human acceptance,
- inspect one allowlisted local framework workspace without persisting source text
  or absolute paths,
- map an accepted proposal to exact page, component, fixture, and E2E test targets,
- distinguish create-file, add-symbol, and reuse-symbol operations,
- keep the adaptation plan pending until a separate human acceptance,
- generate an exact framework-specific patch from an accepted plan,
- preview and accept source separately from proposal and placement review,
- reject stale framework state before generation or application,
- apply the accepted patch atomically to a snapshot-bounded framework sandbox,
- compile, collect, and execute one generated Playwright test,
- record first-creation timing, correction, and independence evidence.

It still cannot autonomously explore an application, call a live LLM provider,
safely patch the user's original framework repository, handle arbitrary source
edits, or prove that the first generation and placement conventions generalize
to enterprise projects.

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

### Bounded LLM synthesis and POM proposal

Sprint 4 adds a provider-neutral synthesis boundary:

```text
ready confirmed/observed context
→ field-level authorization and minimization
→ deterministic prompt
→ replay adapter
→ exact raw output preservation
→ strict JSON parser
→ deterministic POM proposal validation
→ explicit human accept/reject review
```

The request excludes base URLs, routes, raw evidence references, evidence
hashes, timestamps, free-form notes, browser state, and repository files. The
proposal may reference only authorized page, component, step, element, locator,
symbolic data, and outcome IDs.

Sprint 4 uses replay rather than a live provider. Acceptance approves only the
logical proposal as input to Sprint 5 repository inspection; it does not write
files or claim execution success.

See [`docs/synthesis-protocol.md`](docs/synthesis-protocol.md).

### Framework workspace and adaptation plan

Sprint 5 adds a read-only repository-aware boundary:

```text
accepted logical POM proposal
+ non-secret WorkspaceProfile
+ allowlisted local framework copy
→ minimized FrameworkSnapshot
→ exact file/symbol AdaptationPlan
→ explicit human accept/reject review
```

The snapshot stores repository-relative paths, file hashes, sizes, and top-level
Python symbols. It does not persist source content, absolute paths, or secret
values. The plan distinguishes `create_file`, `add_symbol`, and `reuse_symbol`
and never writes to the framework.

See [`docs/framework-adaptation-planning.md`](docs/framework-adaptation-planning.md).

### Controlled source delivery and first runnable test

Sprint 6 consumes only a human-accepted adaptation plan tied to the current
framework fingerprint. It creates an exact `CodePatch`, keeps source review
separate, materializes a sandbox from exact accepted snapshot entries, applies
the accepted patch there, and records a `CreationEvaluation` after compile,
collection, and browser execution.

```text
accepted plan
→ exact source patch
→ source preview and acceptance
→ fingerprint preflight
→ snapshot-bounded sandbox materialization
→ atomic application
→ pytest collection and execution
→ creation evaluation
```

The reference flow adds `CatalogPage`, `CatalogSearchForm`, `catalog_context`,
and `test_search_catalog`. The generated test runs with the framework alone; it
does not import TestCartographer and makes no live LLM call. The original local
framework remains unchanged during the acceptance run.

See [`docs/source-delivery.md`](docs/source-delivery.md).

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

Expected corrected Sprint 6 result after Chromium installation:

```text
156 passed
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

### Verify bounded synthesis replay

```powershell
python scripts/verify_synthesis_replay.py
```

The verifier builds the minimized request, confirms excluded values do not
enter the prompt, replays the committed proposal, validates every reference,
and records explicit human acceptance without calling a live provider or
modifying a repository.

### Build, replay, and review a POM proposal

Build a request from the committed synthesis-ready context:

```powershell
test-cartographer synthesize request `
    --context testdata/context/synthesis_ready/public_search_flow.json `
    --request .test-cartographer/public-search-request.json `
    --request-id synreq_public_search
```

Replay the committed raw output:

```powershell
test-cartographer synthesize replay `
    --request .test-cartographer/public-search-request.json `
    --raw-output testdata/synthesis/raw/valid_public_search.json `
    --run .test-cartographer/public-search-run.json `
    --run-id synrun_public_search
```

Review the validated proposal:

```powershell
test-cartographer synthesize review `
    --run .test-cartographer/public-search-run.json `
    --decision accepted `
    --reason "POM boundaries are acceptable for framework mapping." `
    --review-seconds 15
```


### Verify framework inspection and adaptation planning

```powershell
python scripts/verify_framework_adaptation_plan.py
```

The verifier copies the controlled framework fixture, fingerprints every file,
inspects it, builds and accepts the adaptation plan, and proves that the
framework tree remains byte-for-byte unchanged.

Inspect a real local copy without modifying it:

```powershell
test-cartographer adapt inspect `
    --profile testdata/adaptation/profile/qa_automation_framework.json `
    --framework-root C:\path\to\qa-automation-framework `
    --snapshot .test-cartographer\framework-snapshot.json `
    --snapshot-id snapshot_local_qaf
```

Create and review the repository plan:

```powershell
test-cartographer adapt plan `
    --profile testdata/adaptation/profile/qa_automation_framework.json `
    --snapshot .test-cartographer\framework-snapshot.json `
    --run testdata/synthesis/run/accepted_public_search.json `
    --plan .test-cartographer\public-search-adaptation-plan.json `
    --plan-id adapt_public_search

test-cartographer adapt review `
    --plan .test-cartographer\public-search-adaptation-plan.json `
    --decision accepted `
    --reason "Exact targets match the intended framework architecture."
```

### Verify controlled source delivery and the first runnable test

```powershell
python scripts/verify_first_runnable_test.py --require-browser
```

Build exact source only from the accepted plan and current framework snapshot:

```powershell
test-cartographer deliver build `
    --profile testdata/adaptation/profile/qa_automation_framework.json `
    --generation-profile testdata/delivery/profile/public_search_generation.json `
    --snapshot testdata/adaptation/snapshot/qa_automation_framework.json `
    --run testdata/synthesis/run/accepted_public_search.json `
    --plan testdata/adaptation/plan/accepted_public_search.json `
    --framework-root testdata/framework/reference `
    --patch .test-cartographer/public-search-code-patch.json `
    --patch-id patch_public_search

test-cartographer deliver preview `
    --patch .test-cartographer/public-search-code-patch.json
```

Exact source must then be accepted separately before `deliver apply` can write
to an explicitly supplied framework copy. See
[`docs/source-delivery.md`](docs/source-delivery.md) for the full preflight,
rollback, execution, and evaluation contract.

### Re-export contract schemas

```powershell
python scripts/export_context_schema.py
python scripts/export_intake_schema.py
python scripts/export_observation_schema.py
python scripts/export_synthesis_schemas.py
python scripts/export_adaptation_schemas.py
python scripts/export_delivery_schemas.py
python -m pytest tests/unit/context/test_schema.py `
    tests/unit/intake/test_intake_schema.py `
    tests/unit/observation/test_schema.py `
    tests/unit/synthesis/test_schema.py `
    tests/unit/adaptation/test_schema.py `
    tests/unit/delivery/test_schema.py
```

## Current project structure

```text
test-cartographer/
├── docs/
│   ├── context-contract.md
│   ├── intake-workflow.md
│   ├── browser-observation.md
│   ├── synthesis-protocol.md
│   ├── framework-adaptation-planning.md
│   ├── source-delivery.md
│   └── ...
├── schemas/
│   ├── context-bundle-v0.1.schema.json
│   ├── intake-session-v0.1.schema.json
│   ├── observation-v0.1.schema.json
│   ├── synthesis-request-v0.1.schema.json
│   ├── pom-proposal-v0.1.schema.json
│   ├── synthesis-run-v0.1.schema.json
│   ├── workspace-profile-v0.1.schema.json
│   ├── framework-snapshot-v0.1.schema.json
│   ├── adaptation-plan-v0.1.schema.json
│   ├── generation-profile-v0.1.schema.json
│   ├── code-patch-v0.1.schema.json
│   ├── patch-application-v0.1.schema.json
│   └── creation-evaluation-v0.1.schema.json
├── scripts/
│   ├── export_*_schemas.py
│   ├── verify_browser_observation.py
│   ├── verify_synthesis_replay.py
│   ├── verify_framework_adaptation_plan.py
│   ├── verify_first_runnable_test.py
│   └── record_creation_evaluation.py
├── src/test_cartographer/
│   ├── context/
│   ├── intake/
│   ├── observation/
│   ├── synthesis/
│   ├── adaptation/
│   └── delivery/
├── testdata/
├── tests/
├── LEARNINGS.md
├── README.md
└── pyproject.toml
```

## What Sprint 6 proves

- an accepted logical proposal and accepted repository plan can become exact,
  traceable source,
- exact source remains a separate human-review artefact,
- framework drift is checked before generation and application,
- create and append operations are fully preflighted before the first write,
- an existing fixture file can be extended without replacing it,
- the patch can be applied atomically to a snapshot-bounded framework sandbox with rollback,
- files outside the accepted snapshot cannot affect pytest collection,
- the resulting framework compiles and pytest collects one generated test,
- real Chromium executes the generated test in the normal Windows gate,
- the test contains meaningful assertions in the test layer,
- normal execution requires neither TestCartographer nor a live LLM,
- the original framework remains unchanged during acceptance,
- creation timing, correction, review, and execution evidence is replayable.

## What Sprint 6 does not prove

- safe unattended modification of the original framework repository,
- arbitrary source refactoring or merge-conflict handling,
- general code quality across applications and architectures,
- live-provider quality or prompt-injection resistance,
- enterprise authentication, secret handling, or Salesforce usefulness,
- maintenance after application drift,
- superiority over manual, Codegen, or general-LLM workflows.

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
| 4 | Bounded LLM synthesis and POM proposal | Done |
| 5 | Project workspace and framework adaptation plan | Done |
| 6 | First runnable framework test and creation-lifecycle evaluation | Done |
| 7 | Framework execution-evidence contract | Planned |
| 8–10 | Reactive/proactive maintenance and expansion reuse | Parked |
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
| [`docs/synthesis-protocol.md`](docs/synthesis-protocol.md) | Sprint 4 bounded request, replay, strict parsing, proposal validation, and review |
| [`docs/framework-adaptation-planning.md`](docs/framework-adaptation-planning.md) | Sprint 5 workspace profile, read-only snapshot, exact file/symbol plan, and review |
| [`docs/source-delivery.md`](docs/source-delivery.md) | Sprint 6 exact source proposal, review, safe-copy application, execution, and evaluation |
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


## Sprint 6 result

The first controlled creation lifecycle is now executable:

```text
accepted application evidence
→ accepted logical proposal
→ accepted framework placement
→ exact source review
→ safe-copy application
→ compile and pytest collection
→ real Playwright execution
→ creation evaluation
```

Expected normal Windows result: `159 passed`. The generated target remains a
small public-search reference test, but it is a real framework test with a
meaningful assertion and no TestCartographer or live-LLM runtime dependency.
The original `qa-automation-framework` repository is not modified by the Sprint
6 acceptance workflow.
