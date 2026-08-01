# Gaps — thematic index

Concrete missing capabilities that block the intended product flow.

A gap describes something that must be designed, implemented, or tested. It is
not proof that the product idea is wrong. Full reasoning remains in
`LEARNINGS.md`.

## Gap 1 — No human intake workflow

**Status:** OPEN
**Target:** Sprint 2
**Blocks:** collecting real process context without hand-editing JSON

The contract defines what is needed, but the user must currently create or edit
the bundle manually.

Needed:

- gap-to-question mapping,
- answer validation,
- explicit unknown option,
- review before confirmation,
- resumable local session,
- question and time metrics.

## Gap 2 — Readiness rules are hand-selected and unvalidated on real projects

**Status:** OPEN
**Target:** Sprint 2–6
**Blocks:** justified claim that `ready=True` means sufficient context

Current rules are reasonable first constraints, not empirical proof.

Needed:

- exercise against multiple process examples,
- identify false blockers and missing blockers,
- separate readiness for observation, POM proposal, code generation, and final
  test acceptance if one boolean becomes insufficient.

## Gap 3 — No controlled browser target

**Status:** OPEN
**Target:** before Sprint 3
**Blocks:** reproducible guided-observation tests

The `.test` catalog fixture is JSON only.

Needed:

- a small deterministic local web page or selected existing controlled target,
- known DOM and accessibility structure,
- known overlays/states if required,
- resettable data,
- explicit expected capture output.

Do not begin with a public portal whose UI and legal constraints are outside
project control.

## Gap 4 — No browser observation boundary

**Status:** OPEN
**Target:** Sprint 3
**Blocks:** application-derived evidence

Undefined:

- what DOM/accessibility data is captured,
- what is filtered locally,
- how page and component boundaries are proposed,
- how actions are linked to process steps,
- how iframes and Shadow DOM are represented,
- what is persisted versus referenced.

## Gap 5 — No external LLM safety policy or protocol

**Status:** OPEN
**Target:** before Sprint 4
**Blocks:** safe live-provider use

Needed:

- field-level authorization,
- data minimization,
- redaction rules,
- sensitivity handling,
- provider-neutral request schema,
- prohibited content,
- raw request and response retention policy,
- malformed-output handling,
- cost and timeout bounds.

## Gap 6 — No POM proposal contract

**Status:** OPEN
**Target:** Sprint 4
**Blocks:** deterministic interpretation of LLM output

Needed:

- page and component proposal schema,
- methods and responsibilities,
- locator placement,
- test-data and fixture mapping,
- open questions and unsupported claims,
- strict parser,
- architecture validation.

## Gap 7 — No qa-automation-framework reader or writer

**Status:** OPEN
**Target:** Sprint 5
**Blocks:** actual framework adaptation

Needed:

- inspect target structure and conventions,
- identify existing pages/components/fixtures,
- avoid duplicate artefacts,
- create a reviewable change set,
- preserve human changes,
- execute the resulting project.

## Gap 8 — No execution-evidence model

**Status:** OPEN
**Target:** Sprint 5–6
**Blocks:** linking generated code to runtime result

Needed:

- command and environment metadata,
- test result,
- failure classification,
- trace/screenshot references,
- relation to context and generated files,
- sensitive-data handling.

## Gap 9 — No usability instrumentation

**Status:** OPEN
**Target:** begin Sprint 2
**Blocks:** final ease-of-use and time comparison

Needed from early prototypes:

- setup duration,
- active user duration,
- question count,
- navigation count,
- correction count,
- rejected proposals,
- retries,
- LLM requests and cost,
- time to first runnable test.

## Gap 10 — No schema migration strategy

**Status:** OPEN, NON-BLOCKING FOR SPRINT 2
**Target:** before incompatible contract change

Version `0.1` is fixed, but no migration mechanism exists.

Needed when the first incompatible change is justified:

- compatibility policy,
- version dispatch,
- migration functions,
- old fixture retention,
- failure message for unsupported versions.

## Gap 11 — No multi-process or shared application model

**Status:** PARKED
**Target:** after one-process vertical slice

Version `0.1` may duplicate application, page, or component context across
bundles.

Do not introduce a global graph until duplication or impact analysis creates a
measured problem.

## Gap 12 — No comparative baseline

**Status:** OPEN
**Target:** Sprint 6 and Sprint 9

No evidence exists for claims that TestCartographer is faster, easier, or
higher quality than:

- manual adaptation,
- ordinary DevTools/Codegen/general-LLM assistance.

The comparison must use equivalent scope and quality criteria.
