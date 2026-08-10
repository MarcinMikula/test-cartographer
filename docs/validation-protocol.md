# External validation protocol — v0.1 design

## Purpose

Sprint 16 defines how TestCartographer will be challenged on applications it
does not control without losing the evidence that made a later fix necessary.

The protocol exists to make Sprint 17+ runs repeatable, comparable, attributable
to one product state, explicit about operator effort, and resistant to hindsight
rewriting. It is validation infrastructure, not a new automation capability.

## Core rule

A validation failure or friction point must be persisted **before** a product fix
is designed.

```text
run current product
→ observe failure/friction
→ persist finding
→ close evidence package
→ only then design the smallest justified change
→ create a new product revision
→ rerun as a new ValidationRun
```

An old failed or blocked run is historical evidence. It is never rewritten into
a passing run after the product changes.

## Unit of validation

One `ValidationRun` represents exactly:

```text
one ValidationTargetProfile
+ one bounded process/task
+ one TestCartographer product commit
+ one workflow kind
+ one operator execution
```

Changing executable product behavior creates a new run. A rerun may reference an
earlier run and the exact findings it intends to test.

Before the Sprint 16 closure commit, the controlled rehearsal binds the current
base commit plus a SHA-256 over the exact accepted Sprint 16 repository scope.
This avoids falsely attributing uncommitted Sprint 16 behavior to the base
commit. Normal Sprint 17+ external validation should use a clean committed
product state and omit the working-tree fingerprint.

## Target classification

Technical difficulty:

```text
simple
dynamic_async
multi_page_stateful
difficult
enterprise_constrained
```

Degree of project control:

```text
project_controlled
external_stable
external_low_control
policy_constrained
```

These axes remain independent. A technically simple external page can provide
stronger external-validity evidence than a difficult fixture maintained by the
project.

## ValidationTargetProfile v0.1 — planned contract

Minimum fields:

- schema version and profile ID,
- human-readable target label,
- bounded origin/path without credentials, query, or fragment,
- difficulty and control classifications,
- authentication requirement,
- bounded process/task label,
- allowed and prohibited/destructive actions,
- cleanup requirement when relevant,
- operator authorization statement,
- target-profile fingerprint.

No arbitrary metadata dictionary. The profile is not a DOM snapshot and does
not claim that an external target is stable.

## Workflow kinds

```text
testcartographer
manual_automation_aids
codegen_plus_general_llm
```

Sprint 17 may execute TestCartographer first. The other values keep later
comparison evidence structurally compatible.

## ValidationRun v0.1 — planned contract

A run binds:

- run ID,
- target-profile ID + fingerprint,
- workflow kind,
- exact product base Git commit/version and, only for an accepted uncommitted rehearsal state, a working-tree fingerprint,
- predecessor run ID for a rerun,
- finding IDs intentionally addressed by that rerun,
- timestamps and runtime/environment summary,
- operator-effort and system-wait metrics,
- findings,
- final completion state,
- explicit stop reason when stopped,
- canonical run fingerprint.

Default persistence excludes credentials, raw browser pages/HTML, raw LLM
prompts/responses, screenshots, traces, cookies/storage state, and unrestricted
source dumps.

Identity is deliberately one-way:

```text
target_fingerprint
→ run_fingerprint
→ package_fingerprint
```

`ValidationRun` does not embed `package_fingerprint`; otherwise package identity
would depend circularly on content that itself contains the package identity.

## Completion is not diagnosis

Keep completion narrow:

```text
completed
incomplete
stopped
```

A stopped run is not automatically proof of a TestCartographer defect.

## ValidationFinding v0.1 — planned nested contract

Minimum fields:

- finding ID,
- observed timestamp,
- lifecycle stage,
- kind,
- concise human observation,
- evidence references,
- whether execution could continue,
- stop-condition reference when applicable.

Lifecycle stage:

```text
bootstrap
intake
browser_discovery
context_review
synthesis
repository_mapping
source_review
delivery
execution
maintenance
expansion
general
```

Finding kind:

```text
failure
friction
unsupported_assumption
safety_stop
measurement_issue
```

These labels describe what happened; they are not root-cause verdicts.

## Finding-before-fix invariant

```text
Run R1 @ commit A
→ finding F1 persisted
→ R1 package closed

engineering change
→ commit B

Run R2 @ commit B
→ predecessor_run_id = R1
→ addressed_findings = [R1/F1]
```

The first run remains independently verifiable.

## Timing definitions

Record separately:

```text
elapsed_seconds
setup_active_seconds
intake_active_seconds
review_active_seconds
correction_active_seconds
system_wait_seconds
```

Derived operator-active time is setup + intake + review + correction.

Correction time is active work caused by incorrect/incomplete/unusable product
output. Intended normal review is not correction.

System wait covers LLM, browser, deterministic generation, execution, and
packaging waits.

Do not claim time saved without a baseline.

## Operator assessment

After a run, permit small subjective fields:

```text
difficulty: easy | moderate | hard | blocked
confidence_in_result: low | medium | high
would_reuse_workflow: yes | uncertain | no
prior_target_familiarity: new_to_operator | seen_before | automated_before
```

These remain explicitly subjective evidence.

## Stop conditions

Stop rather than silently widen scope when:

- authentication is required but not approved,
- the action becomes destructive or irreversible,
- sensitive/prohibited data would need to be entered or persisted,
- the target leaves the approved origin/process boundary,
- anti-abuse/rate-limit behavior indicates the run should not continue,
- a policy decision is required but absent,
- unrestricted crawling/data capture would be needed,
- continuing would invalidate run comparability,
- the operator cannot determine what evidence is safe to retain.

Stopping is valid validation evidence.

## External-target conduct

Sprint 17 public validation remains bounded and human-guided. Do not crawl
broadly, create intentional load, bypass access controls, defeat anti-bot
protections, submit destructive transactions, or persist third-party user data.

## Evidence package

Sprint 16C implements the local builder/verifier boundary for this shape.

The builder refuses to overwrite an existing destination, materializes through a
temporary directory, and publishes the package only after independent
verification succeeds. The verifier rejects missing/hash-drifted evidence,
unmanifested files, broken target/run/manifest identity, unknown finding
references, and evidence outside the active sensitivity policy.

Planned local shape:

```text
validation/
└── <target-id>/
    └── <run-id>/
        ├── validation-target-profile.json
        ├── validation-run.json
        ├── evidence-manifest.json
        └── evidence/
            └── selected safe artefacts only
```

Manifest entries contain relative path, SHA-256, artefact kind, sensitivity,
producer, and run/finding relationship. No absolute paths.

Default permitted inputs are already minimized TestCartographer artefacts such
as ContextBundle, intake/session summaries, minimized observations,
synthesis/adaptation summaries, execution evidence, and operator action
summaries.

Default excluded evidence includes credentials, cookies/storage state, raw HTML,
screenshots, traces, network dumps, raw prompts/responses, arbitrary source
trees, and unrestricted terminal logs.

Package identity is a deterministic fingerprint over target-profile fingerprint,
canonical run content, and sorted included artefact paths/hashes.

## Baseline procedure for later comparison

For useful comparison:

1. same bounded process objective,
2. same acceptance criteria,
3. tool/product versions recorded,
4. prior target familiarity recorded,
5. same safety/data boundary,
6. setup/operator/wait/correction metrics recorded,
7. result quality reviewed separately,
8. each workflow keeps its own evidence package.

Potential later workflows:

```text
A. testing professional + ordinary manual automation aids
B. testing professional + Playwright Codegen/DevTools + general-purpose LLM
C. testing professional + TestCartographer
```

The goal is not to prove C wins.

## Quality review

A passing generated test is not enough. Review at least assertion meaning,
POM/component maintainability, unsupported assumptions, lost context, hidden
manual repair, and independent framework execution.

## Sprint 16 rehearsal

Sprint 16 rehearses the protocol on the existing controlled local catalog.

That proves protocol/package mechanics only:

```text
external validity proven: false
protocol mechanics proven: true
```

## Sprint 17 gate

Sprint 17 starts only when one repeatable validation package can be created and
verified without changing the product under test during the run.

The first external target should be public/no-auth and bounded enough that a
failure is not dominated by credential or enterprise-policy complexity.
