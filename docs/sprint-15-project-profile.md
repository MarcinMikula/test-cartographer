# Sprint 15 — Persistent ProjectProfile and bootstrap reuse

## Status

**Done — real operator acceptance verified on Windows.**

Sprint 15 closes the P0 core gap identified at Checkpoint 14.5: persistent
project/bootstrap configuration that survives separate runs, reuses current
accepted values, and selectively reopens only affected dependencies.

## Implemented boundary

```text
ProjectProfile v0.1
├── application
│   ├── name
│   ├── one active environment
│   └── base URL/origin
├── WorkspaceProfile binding: ID + canonical SHA-256
├── GuidedIntakeProfile binding: ID + canonical SHA-256
├── project data-boundary policy
├── minimal authentication declaration/reference
├── revision
├── configuration_fingerprint
└── bounded event ledger
```

`ProjectProfile` is not a second `ContextBundle`. Process purpose, risk, role,
preconditions, outcomes, pages, elements, locators, assertions, and
process-specific test data remain process context.

The default local state is:

```text
.test-cartographer/project-profile.json
```

It is strict, non-secret, ignored by Git, validated on load, and has no arbitrary
metadata escape hatch.

## Authority and bindings

Project-wide values use `ProjectValue`; they do not reuse ContextBundle
`KnowledgeText.evidence_ids`.

Existing `WorkspaceProfile` and capability-specific `GuidedIntakeProfile`
contracts remain authoritative. ProjectProfile stores only their accepted ID and
canonical hash. Runtime binding drift fails closed.

`configuration_fingerprint` covers effective reusable configuration and excludes
the audit event ledger:

```text
assessment/audit event only
→ fingerprint unchanged

accepted project mutation
→ revision increments
→ fingerprint changes
```

A tampered current profile fails fingerprint validation before compatibility
classification.

## Context projection

A current profile is projected into the ordinary `ContextBundle` before the
normal IntakeSession.

The projection uses bounded `SYSTEM` evidence:

```text
project_profile:<profile_id>@<revision>#<configuration_fingerprint>
```

No second intake engine is introduced.

A current profile therefore satisfies the application name/environment/base-URL
bootstrap while process-specific questions remain part of the normal intake.

## Selective compatibility

Supported dispositions:

```text
COMPATIBLE
REVIEW_REQUIRED
REOBSERVE
RESNAPSHOT
BLOCKED
```

Accepted semantics:

```text
environment/base URL changed
→ browser/application evidence REOBSERVE
→ business context COMPATIBLE
→ workspace COMPATIBLE
→ guided intake COMPATIBLE

WorkspaceProfile changed
→ repository work RESNAPSHOT
→ business context COMPATIBLE

GuidedIntakeProfile changed
→ future guided use REVIEW_REQUIRED
→ accepted human business truth remains reusable

time alone
→ no automatic staleness
```

## Real operator acceptance

The Windows acceptance used separate Python processes.

### Run A

```text
bootstrap questions first run: 3
operator profile review actions: 1
revision: 1
profile ready: true
secret values persisted: false
raw auth state persisted: false
```

Invalid accept/reject input was re-prompted rather than interpreted as a
decision.

### Run B — later creation

```text
profile loaded from disk: true
revision used: 1
bootstrap questions asked: 0
process name/purpose/risk/role questions preserved: true
workspace binding reused: true
guided-intake binding reused: true
```

### Run C — later expansion

```text
profile loaded from disk: true
revision used: 1
bootstrap questions asked: 0
process-specific questions preserved: true
workspace binding reused: true
guided-intake binding reused: true
```

### Run D — changed environment/base URL

```text
revision: 1 → 2
configuration fingerprint changed: true
environment/browser evidence: REOBSERVE
business context: COMPATIBLE
workspace: COMPATIBLE
guided intake: COMPATIBLE
unrelated fields re-asked: 0
resnapshot required: false
blockers: []
```

## Regression closure

After real acceptance, with the persistent revision-2 profile still present:

```text
394 tests
394 passed
0 failures
0 errors
0 skipped
```

## What Sprint 15 proves

- project bootstrap survives separate runs,
- current bootstrap is reused without repeated application questions,
- process-specific intake stays separate,
- exact workspace/guided bindings fail closed on drift,
- environment/base-URL change invalidates browser evidence selectively,
- accepted business meaning is not erased by unrelated configuration change,
- tampered profile state fails closed,
- the real human-triggered Creation Flow runner consumes the same persistent
  ProjectProfile boundary.

## What Sprint 15 does not prove

- external-application usability or savings,
- multi-environment project configuration,
- team/shared profile synchronization,
- long-lived schema migration,
- authenticated browser execution,
- `AuthProfile` / `SecretProvider`,
- secret-manager integration,
- TTL-based freshness,
- production-repository delivery,
- need for a multi-process application graph,
- external application generality.

Sprint 16 therefore moves to the external-validation protocol rather than
another speculative core abstraction.
