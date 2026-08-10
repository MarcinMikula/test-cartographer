# Sprint 16 — external-validation protocol and repeatable evidence package

## Status

**DONE — controlled real-operator protocol rehearsal verified.**

Sprint 16 prepares TestCartographer for external validation. It does not itself
claim external application validity.

## Delivered

Sprint 16 introduces four strict validation contracts:

- `ValidationTargetProfile v0.1`,
- `ValidationFinding v0.1`,
- `ValidationRun v0.1`,
- `ValidationEvidenceManifest v0.1`.

The evidence identity chain is deliberately one-way:

```text
target_fingerprint
→ run_fingerprint
→ package_fingerprint
```

A TestCartographer validation run records exact product provenance. The
pre-closure Sprint 16 rehearsal additionally records a working-tree fingerprint
so uncommitted accepted Sprint 16 behavior is not falsely attributed to the
base commit.

The package builder/verifier boundary:

- accepts only explicit evidence sources,
- persists package-relative paths, never source absolute paths,
- refuses an existing destination,
- builds through a temporary directory,
- verifies source and copied SHA-256 values,
- enforces evidence file-count and byte budgets,
- enforces sensitivity policy,
- rejects symlink evidence,
- rejects missing evidence,
- rejects unmanifested files,
- validates target/run/manifest identity,
- validates target/run/package fingerprints,
- validates finding references,
- publishes the final package only after independent verification.

## Finding-before-fix rule

A failed or friction-producing run is historical evidence, not a mutable work
record.

```text
R1 @ product state A
→ persist finding F1
→ close and verify R1 package

then, if a product change is justified:

product state B
→ R2
→ predecessor_run_id = R1
→ addressed_findings = [R1/F1]
```

The original failed package is not rewritten into a passing package.

## Timing and operator evidence

Validation separates setup, intake, review, correction, system-wait, and total
elapsed time. Operator assessment separately records perceived difficulty,
confidence, willingness to reuse, and prior target familiarity.

These are observations, not productivity or causal claims.

## Stop conditions

The protocol supports explicit stop evidence for authentication not approved,
destructive action, sensitive-data boundaries, leaving approved scope,
rate-limit/anti-abuse signals, missing policy decisions, unrestricted capture
requirements, broken comparison validity, and uncertain retention safety.

A safe stop is valid validation evidence.

## Controlled Sprint 16D rehearsal

The real-operator rehearsal reused the existing project-controlled public
catalog fixture and the already-known sort-locator drift:

```text
catalog-sort
→ catalog-sort-control
```

This was a protocol specimen, not newly discovered external failure evidence.

The accepted corrected rehearsal verified:

```text
run_one_verified: true
run_two_verified: true
first_finding_preserved: true
predecessor_link_valid: true
package_fingerprint_order_stable: true
tamper_detection_fail_closed: true
final_operator_review_accepted: true
controlled_target: true
external_application_validity_proven: false
productivity_savings_claimed: false
product_remediation_proven: false
```

## Measurement issue discovered by the protocol

The first full rehearsal exposed a measurement defect:

```text
invalid Difficulty choice
→ reprompt occurred
→ summary incorrectly reported invalid_input_reprompts = 0
```

The authority boundary worked. The defect was limited to counting.

Before changing the harness, the issue was persisted in the local acceptance
archive as a `measurement_issue` with:

```text
authority_boundary_failed = false
measurement_failed = true
recorded_before_fix = true
```

Sprint 16D.1 changed only invalid-choice counting and added a regression test.
The corrected suite reached 469/469.

A later complete corrected rehearsal contained no invalid input and therefore
correctly reported `invalid_input_reprompts: 0`. The earlier invalid-input path
remains covered by the regression test and preserved pre-fix finding.

## Operator usability evidence

The first complete rehearsal recorded:

```text
difficulty: hard
confidence: high
would_reuse_workflow: uncertain
prior_target_familiarity: automated_before
```

The corrected complete rehearsal recorded:

```text
difficulty: hard
confidence: high
would_reuse_workflow: yes
prior_target_familiarity: automated_before
```

This is not interpreted as improvement or savings. The target was familiar and
the runs were sequential. The useful signal is simply that the protocol is
usable for Sprint 17 while current operator experience is still perceived as
hard.

## Acceptance evidence

Final Sprint 16 regression:

```text
validation-focused tests: 75/75
full regression: 469/469
```

Corrected controlled rehearsal archive:

```text
TestCartographer-local-artifacts/sprint-16/20260810-202642
```

Pre-fix measurement finding archive:

```text
TestCartographer-local-artifacts/sprint-16/20260810-201700/
harness-finding-invalid-choice-counter.json
```

## What Sprint 16 proves

Sprint 16 proves that TestCartographer can represent one bounded validation
target/run/finding/evidence package, preserve a first finding across a linked
rerun, produce deterministic package identity, and independently fail closed on
evidence tampering within a controlled real-operator rehearsal.

It also proves the validation process can expose a defect in its own measurement
harness and preserve that observation before the smallest correction.

## What Sprint 16 does not prove

Sprint 16 does **not** prove:

- external public application validity,
- dynamic/low-control validity,
- authentication or enterprise readiness,
- generalized maintenance,
- productivity savings,
- lower effort than Codegen/manual/general-purpose-LLM workflows,
- live-LLM semantic value,
- real production repository delivery.

Those remain evidence targets for Sprint 17 and later provisional validation
sprints.
