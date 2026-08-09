# Sprint 15A — Persistent ProjectProfile architecture

## Status

Architecture accepted with Sprint 15A.1 corrections. No runtime implementation
and no commit yet.

Base repository state:

```text
1527e91e2b0e12e58c934af5dc2b3273533044ab
docs: reset roadmap around real validation
```

## Goal

Define the smallest durable project-wide configuration/authority boundary that
lets TestCartographer ask bootstrap questions once, reuse current answers across
later creation/maintenance/expansion runs, and reopen only affected parts after
relevant change.

The core separation is:

```text
ProjectProfile
→ project-wide reusable configuration and authority

ContextBundle
→ process-specific application/testing knowledge

runtime/session state
→ one interview/browser/execution run

secret/auth state
→ external sensitive runtime material
```

`ProjectProfile` must not become a second `ContextBundle` or a generic settings
dictionary.

---

# 1. Project-wide vs process-specific

## Project-wide — ProjectProfile v0.1

### Application identity

- application name,
- one active environment identifier/label,
- one active base URL / origin-level entry point.

Sprint 15 intentionally supports one active environment. Multi-environment
catalogues are deferred until validation proves the need.

Distinction:

```text
project base URL/origin
→ ProjectProfile

process starting route/page
→ ContextBundle / process discovery
```

### Workspace binding

Reuse the existing `WorkspaceProfile`.

Persist only:

```text
workspace_profile_id
workspace_profile_sha256
binding state/review metadata
```

Do not duplicate repository roots, budgets, ignore lists, or source content.

Do not persist machine-specific absolute repository paths.

### Guided-intake binding

Reuse the existing `GuidedIntakeProfile`.

Persist only:

```text
guided_intake_profile_id
guided_intake_profile_sha256
binding state/review metadata
```

This binding is **specifically for guided intake**.

Sprint 15 must not introduce a generic project-wide `provider/model` field that
implicitly becomes the configuration for every future LLM capability.

Future synthesis/diagnosis providers may later receive separate capability-
specific bindings if real validation requires them.

### Project data-boundary policy

Minimum provider-independent policy:

```text
external_processing_allowed
allowed_context_sensitivities
raw_application_content_persisted = false
raw_secret_values_persisted = false
```

Effective external-processing permission is the intersection of project policy
and the capability-specific provider profile.

A provider profile can narrow project policy; it cannot broaden it.

### Authentication declaration

Sprint 15 persists only the minimum non-secret bootstrap fact:

```text
authentication_state:
  - not_required
  - required_unresolved
  - configured_ref

auth_profile_ref: optional symbolic identifier
```

Do not encode `storage_state`, `login_recipe`, or `interactive` strategy choices
in ProjectProfile v0.1.

Those belong to the future `AuthProfile` implementation once credentialed
validation starts.

---

# 2. Process-specific — never ProjectProfile bootstrap

Keep in `ContextBundle` and process acquisition:

- process name,
- purpose,
- business risk,
- process role,
- preconditions,
- expected outcomes,
- steps,
- pages/components,
- elements/locators,
- process-specific symbolic test data,
- assertions,
- runtime ambiguity selections.

A value is not project-wide merely because two reference processes reused it.

---

# 3. ProjectProfile values and authority

Do **not** embed `KnowledgeText` directly.

`KnowledgeText.evidence_ids` belongs to the `ContextBundle` evidence graph.
ProjectProfile needs its own strict typed wrapper, conceptually:

```text
ProjectValue[T]
├── value
├── status
├── sensitivity
├── source
├── reviewed_at
└── review_reason
```

Reuse existing enums where semantics match:

```text
KnowledgeStatus
SensitivityLevel
```

but do not require ContextBundle evidence IDs.

For human bootstrap values the useful states are primarily:

```text
PROVIDED
CONFIRMED
UNKNOWN
STALE
CONFLICTING
```

Bindings use a separate smaller lifecycle:

```text
UNRESOLVED
CURRENT
REVIEW_REQUIRED
STALE
CONFLICTING
```

---

# 4. Things ProjectProfile must never store

The schema must make these structurally impossible.

## Secrets

Never:

- passwords,
- tokens,
- API keys,
- MFA codes,
- client secrets,
- private keys,
- authorization headers.

## Browser/auth state

Never:

- cookies,
- local/session storage,
- Playwright storage-state content,
- browser/page/context objects,
- raw login responses.

A future `auth_profile_ref` is symbolic only.

## Raw runtime/model material

Never:

- raw HTML,
- screenshots,
- traces,
- network dumps,
- raw operator transcript,
- raw LLM prompts/responses,
- temporary ports,
- one-run browser state.

## Process truth

Never duplicate:

- purpose,
- risk,
- outcomes,
- steps,
- locators,
- assertions,

merely to make ProjectProfile self-contained.

No arbitrary `metadata: dict[str, Any]` escape hatch in v0.1.

---

# 5. Conceptual v0.1 shape

```text
ProjectProfile
├── schema_version
├── id
├── revision
├── created_at
├── updated_at
├── application
│   ├── name: ProjectValue
│   ├── environment: ProjectValue
│   └── base_url: ProjectValue
├── workspace_binding
├── guided_intake_binding
├── data_policy
├── authentication_declaration
├── configuration_fingerprint
└── event_ledger
```

The full serialized file may have its ordinary file SHA, but downstream
compatibility uses `configuration_fingerprint`.

---

# 6. configuration_fingerprint

This is separate from a raw JSON/document hash.

It is a canonical SHA-256 over **effective reusable configuration**, including:

- profile ID/revision,
- application bootstrap values/status/sensitivity that affect reuse,
- workspace binding ID/hash/state,
- guided-intake binding ID/hash/state,
- project data policy,
- authentication declaration/reference.

It excludes purely historical/audit material such as:

- event ledger entries,
- write formatting,
- transient serialization details.

Reason:

> appending an audit event must not masquerade as a configuration change.

A revision changes only after an accepted profile-state change. Read-only
compatibility assessment does not increment revision.

---

# 7. Revision and event ledger

Accepted profile mutations create monotonically increasing revisions.

```text
rev 1 → initial accepted bootstrap
rev 2 → accepted environment/base URL change
rev 3 → accepted guided-intake binding change
```

A deterministic detected mismatch does **not** automatically rewrite the profile
or create a revision.

It creates a compatibility/readiness result.

Only human-accepted resolution updates the profile revision.

Bounded event metadata:

```text
sequence
timestamp
event kind
affected paths
reason code
previous revision
new revision
```

No secret/raw answer values.

---

# 8. Persistence

Default local path:

```text
.test-cartographer/project-profile.json
```

Rationale:

- local project engineering state,
- survives separate runs,
- ignored by Git,
- no database/service required,
- aligns with existing workspace direction.

Committed fixtures may live under:

```text
testdata/project_profile/
```

No cloud/team sync in Sprint 15.

---

# 9. Projection into ContextBundle

A process context receives a snapshot/projection of current bootstrap values.

```text
accepted ProjectProfile rev N
→ deterministic bootstrap projection
→ ContextBundle ApplicationContext
```

Do not make ContextBundle fields dynamically reference a mutable ProjectProfile.

Projection provenance should use the existing `Evidence` mechanism where
possible, for example a bounded SYSTEM evidence source referring to:

```text
project_profile:<profile_id>@<revision>#<configuration_fingerprint>
```

This avoids changing `ContextBundle` merely to add a second provenance system.

If implementation proves this insufficient, change the contract only with a
specific test demonstrating why.

---

# 10. Selective invalidation

Invalidation affects **future reuse eligibility**, not accepted history.

## Explicit operator change

Accepted change:

- new revision,
- new configuration fingerprint,
- bounded event,
- only dependent compatibility changes.

## Application name

Usually identity/label review only.

Must not automatically invalidate browser evidence solely because a display
name changed.

## Environment/base URL

Future application/browser evidence tied to the old environment:

```text
→ REOBSERVE / REVIEW_REQUIRED
```

Still compatible unless contrary evidence exists:

```text
purpose
risk
expected outcomes
framework structure
guided-intake configuration
```

## WorkspaceProfile ID/hash change

Repository-dependent artifacts:

```text
FrameworkSnapshot → RESNAPSHOT
unfinished adaptation/patch reuse → REVIEW_REQUIRED/BLOCKED
```

Does not trigger process/business re-intake.

## GuidedIntakeProfile ID/hash change

Future guided-intake calls use the newly accepted binding.

A paused run tied to the old binding cannot silently resume under the new
profile.

Already human-confirmed business facts and accepted/executed code remain
historical accepted evidence.

## Project policy change

Stricter policy:

```text
future external/model projection → re-authorize/block as required
```

More permissive policy:

```text
explicit human acceptance required
```

Never interpret a more permissive setting as permission to send data
automatically.

## Authentication declaration/reference

Affects credentialed runtime readiness.

Does not invalidate unrelated process meaning or framework structure.

## Time alone

No TTL-based invalidation in Sprint 15.

```text
old ≠ stale
```

Staleness needs evidence, explicit change, binding mismatch, or known relevant
configuration change.

---

# 11. Compatibility instead of cascading mutation

Prefer:

```text
current ProjectProfile
+ historical artifact provenance
→ CompatibilityReport
```

Dispositions:

```text
COMPATIBLE
REVIEW_REQUIRED
REOBSERVE
RESNAPSHOT
BLOCKED
```

Do not eagerly rewrite every historical ContextBundle or accepted artifact.

---

# 12. Bootstrap UX

## First project run

Ask only missing project-wide values.

Show one aggregate summary for acceptance.

Avoid field-by-field confirmation spam when one bounded summary can authorize
the project bootstrap.

## Later creation/expansion

```text
load profile
→ validate bindings/hashes
→ assess readiness
→ project current bootstrap
```

If current:

```text
bootstrap_questions_asked = 0
```

Then collect only process-specific information.

## Invalidated section

Reopen only the affected field/binding and show the consequences.

Example:

```text
base URL changed
→ review environment/base URL
→ explain browser evidence requires re-observation
→ do not re-ask app name/workspace/guided-intake binding
```

---

# 13. Sprint 15 delivery slices

## 15A / 15A.1

Architecture and corrections.

## 15B

Implement:

- `ProjectProfile v0.1`,
- `ProjectValue`,
- binding/declaration/data-policy models,
- configuration fingerprint,
- persistence,
- revision/event validation,
- readiness/currentness,
- JSON Schema,
- fixtures/unit tests.

No Creation Flow integration yet.

## 15C

Implement:

- bootstrap projection,
- CompatibilityReport,
- selective invalidation,
- Creation Flow integration,
- Expansion integration,
- regression tests.

Prefer existing ContextBundle Evidence for profile projection provenance before
changing ContextBundle schema.

## 15D

Real operator acceptance across separate disk-backed runs.

Then documentation closure and one final Sprint 15 commit.

---

# 14. Non-goals

- auth/session execution,
- authentication strategy implementation,
- secret manager,
- Jira/Confluence,
- project database/cloud sync,
- multi-environment catalogue,
- arbitrary application graph,
- production repo writes,
- TTL freshness,
- GUI,
- API/SOM,
- extra LLM providers,
- autonomous crawling.

---

# 15. Architecture invariants

1. ProjectProfile owns project bootstrap, not process truth.
2. No secret/auth/browser runtime material can fit the schema.
3. Existing WorkspaceProfile and GuidedIntakeProfile are referenced by ID+hash.
4. The guided-intake binding is capability-specific, not a universal LLM config.
5. ProjectProfile uses its own `ProjectValue`, not ContextBundle `KnowledgeText`.
6. Downstream compatibility uses `configuration_fingerprint`, not event-ledger
   file hash.
7. Revision increments only on accepted state mutation.
8. Invalidation is selective.
9. Historical artifacts are not retroactively rewritten.
10. Environment/base URL change reopens browser evidence, not business meaning.
11. Workspace drift triggers resnapshot/replan, not re-intake.
12. Provider/model drift does not erase accepted human truth.
13. Auth strategy remains deferred to the future AuthProfile.
14. A later current-profile process can start with zero bootstrap questions.
