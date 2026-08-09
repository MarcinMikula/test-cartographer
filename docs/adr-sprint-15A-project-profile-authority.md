# ADR — Sprint 15A/15A.1 ProjectProfile authority and invalidation

## Context

Bootstrap context is currently collected inside one Creation Flow and Sprint 14
proves reuse inside one controlled expansion run. Cross-run project bootstrap
persistence is still missing.

## Decision

Introduce `ProjectProfile v0.1` as a persistent, non-secret project-wide
authority/index layer.

It does not replace `ContextBundle`, `WorkspaceProfile`, or
`GuidedIntakeProfile`.

## Ownership

ProjectProfile owns:

- application name,
- one active environment,
- one active base URL/origin,
- exact WorkspaceProfile binding,
- exact GuidedIntakeProfile binding,
- project external-processing/data-boundary policy,
- minimal authentication declaration/reference,
- revision/currentness/audit metadata.

ProjectProfile does not own process purpose, risk, role, outcomes, steps,
locators, assertions, source code, secrets, browser state, or raw LLM/browser
content.

## Project values

Do not reuse `KnowledgeText` directly because its evidence references belong to
the ContextBundle evidence graph.

Use a strict `ProjectValue` while reusing shared status/sensitivity enums where
semantics match.

## Capability-specific provider binding

ProjectProfile v0.1 references `GuidedIntakeProfile` specifically.

It does not define one universal provider/model for every future LLM task.

## Authentication declaration

Persist only:

```text
not_required
required_unresolved
configured_ref
```

and an optional symbolic `auth_profile_ref`.

Authentication strategy belongs to the later AuthProfile implementation.

## Fingerprints

Use:

```text
workspace_profile_sha256
guided_intake_profile_sha256
configuration_fingerprint
```

`configuration_fingerprint` hashes effective reusable configuration and excludes
the event ledger.

A raw file SHA is not the downstream compatibility identity.

## Revision

Revision increments only after an accepted profile-state mutation.

Detected drift/readiness assessment alone does not mutate the profile.

## Projection

New ContextBundle application bootstrap is a historical snapshot of one accepted
ProjectProfile revision.

Prefer existing SYSTEM `Evidence` provenance referring to profile
ID/revision/configuration fingerprint before changing ContextBundle schema.

## Invalidation

- environment/base URL drift → re-observe environment-bound application/browser
  evidence, keep business meaning unless contrary evidence exists,
- workspace binding drift → resnapshot/replan repository work,
- guided-intake binding drift → new calls use new binding; paused incompatible
  runs cannot silently resume,
- provider/model changes do not invalidate accepted human business truth,
- policy changes affect future external-processing authorization,
- auth declaration affects credentialed-runtime readiness,
- time alone does not create staleness.

Historical accepted artifacts are not automatically rewritten.

## Rejected alternatives

- one giant ProjectProfile containing process/application graph,
- direct `KnowledgeText` reuse without a ProjectProfile evidence model,
- copied WorkspaceProfile/GuidedIntakeProfile fields,
- generic global provider/model configuration,
- Sprint-15 authentication strategy design,
- full-file/event-ledger hash as compatibility identity,
- global invalidation after any change,
- TTL-based staleness.
