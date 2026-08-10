# Sprint 16 acceptance blueprint — validation protocol and repeatable evidence

## Goal

Enter Sprint 17 with a repeatable, privacy-bounded validation evidence mechanism
that preserves failures before later fixes.

Sprint 16 is accepted for **validation infrastructure**, not external validity.

## Slice plan

### Sprint 16A — protocol and authority

Deliver documentation only:

- `docs/validation-protocol.md`,
- validation-evidence ADR,
- this acceptance blueprint.

No product code and no commit.

### Sprint 16B — strict contracts and persistence

Implement the smallest provider-neutral model set:

```text
ValidationTargetProfile v0.1
ValidationRun v0.1
ValidationFinding v0.1 (nested)
ValidationEvidenceManifest v0.1
```

Required:

- strict Pydantic models,
- no extra fields/arbitrary metadata,
- deterministic JSON IO,
- canonical one-way target → run → package fingerprints,
- minimized target URL,
- one product-ref per run,
- predecessor/addressed-finding references,
- timing categories,
- operator familiarity/difficulty evidence,
- relative-path + SHA-256 evidence records,
- generated/tested JSON Schemas.

No browser, LLM, or external target required.

### Sprint 16C — package builder and fail-closed verifier

The local package boundary must:

- consume a closed ValidationRun,
- select only allowed persisted artefact kinds,
- reject absolute paths,
- reject missing/hash-drifted files,
- reject forbidden default-sensitive artefact classes,
- produce deterministic package fingerprint,
- materialize only approved safe artefacts,
- independently verify an existing package.

Real packages live outside the repository.

### Sprint 16D — controlled protocol rehearsal

Use the existing controlled local catalog.

Required proof:

1. target classified `project_controlled`,
2. run tied to exact current Git commit,
3. timing categories recorded,
4. first run/finding remains immutable,
5. second run can reference first run/finding,
6. both packages remain independently verifiable,
7. package fingerprint stable across filesystem ordering,
8. tampered artefact/hash fails closed,
9. forbidden artefact class fails closed,
10. full product regression remains green,
11. operator reviews instructions/timing practicality.

Truthful closure output:

```text
validation protocol implemented: true
repeatable evidence package verified: true
first-failure preservation verified: true
controlled rehearsal verified: true
external application validity proven: false
productivity savings claimed: false
```

## Planned enums

Difficulty:

```text
simple
dynamic_async
multi_page_stateful
difficult
enterprise_constrained
```

Control:

```text
project_controlled
external_stable
external_low_control
policy_constrained
```

Authentication:

```text
none
required
unknown
```

Workflow:

```text
testcartographer
manual_automation_aids
codegen_plus_general_llm
```

Completion:

```text
completed
incomplete
stopped
```

Finding:

```text
failure
friction
unsupported_assumption
safety_stop
measurement_issue
```

## Timing

```text
elapsed_seconds
setup_active_seconds
intake_active_seconds
review_active_seconds
correction_active_seconds
system_wait_seconds
```

No `time_saved` field.

## Default excluded evidence

- credentials,
- cookies/storage state,
- raw HTML,
- screenshots,
- traces,
- network dumps,
- raw prompts/responses,
- arbitrary source trees,
- unrestricted terminal logs.

## Contract invariants

At minimum test:

- extra fields and invalid enums rejected,
- target URL credentials/query/fragment rejected or minimized by explicit rule,
- absolute evidence path rejected,
- duplicate finding IDs rejected,
- predecessor cannot equal current run,
- addressed finding must name predecessor run,
- negative timing rejected,
- package hash stable,
- missing/changed artefact fails,
- forbidden artefact class fails default packaging,
- old run remains valid after later rerun creation.

## Commit policy

No Sprint 16 commit until architecture, contracts, package mechanics, controlled
rehearsal, docs closure, full suite, and exact allowlist are accepted.
