# Sprint 15 acceptance blueprint — disk persistence and selective invalidation

## Acceptance principle

Sprint 15 closes only if ProjectProfile changes observable operator behavior
across **separate process executions reading disk state**.

An in-memory object reused by one script is insufficient.

## Reference project

Use the existing public catalogue reference so Sprint 15 isolates persistence
rather than adding unrelated browser complexity.

Project bootstrap:

```text
application = Public Catalog
active environment = local_acceptance
base URL = controlled catalogue origin
WorkspaceProfile = current controlled framework profile
GuidedIntakeProfile = current approved local guided-intake profile
authentication_state = not_required
```

## Run A — first project bootstrap

Real operator supplies/reviews missing project values and accepts one aggregate
summary.

Expected:

```text
profile persisted
revision = 1
configuration_fingerprint present
project_profile_ready = true
secret_values_persisted = false
raw_auth_state_persisted = false
```

## Run B — separate later Creation Flow

Expected:

```text
profile_loaded_from_disk = true
profile_revision_used = 1
configuration_fingerprint_used = true
bootstrap_questions_asked = 0
process_specific_questions_asked > 0
```

Projected ApplicationContext values retain provenance to profile
ID/revision/fingerprint.

## Run C — separate expansion

Expected:

```text
bootstrap_questions_asked = 0
workspace_binding_reused = true
guided_intake_binding_reused = true
```

Process-specific delta remains separate.

## Selective invalidation experiment — environment/base URL

Explicitly accept an environment/base-URL change, creating revision 2.

Expected:

```text
browser/application evidence reuse = REOBSERVE or REVIEW_REQUIRED
purpose reuse = COMPATIBLE
risk reuse = COMPATIBLE
expected outcome reuse = COMPATIBLE
workspace binding = COMPATIBLE
guided-intake binding = COMPATIBLE
```

Unrelated bootstrap questions must not be re-asked.

## Workspace binding hash experiment

Keep the same WorkspaceProfile ID but change profile content/hash.

Expected before operator acceptance:

```text
workspace hash mismatch = true
binding = REVIEW_REQUIRED or STALE
FrameworkSnapshot reuse = RESNAPSHOT
profile revision unchanged
```

Only accepted resolution creates a new ProjectProfile revision.

## Guided-intake binding experiment

Change the referenced GuidedIntakeProfile/model and accept a new binding.

Expected:

```text
future guided-intake calls use new binding
paused incompatible old guided-intake run cannot silently resume
human-confirmed business facts invalidated = false
accepted executed code invalidated = false
```

Do not generalize this to every future LLM capability.

## Audit/fingerprint experiment

Append/read an audit event without changing effective accepted configuration.

Expected:

```text
configuration_fingerprint unchanged
```

An accepted configuration mutation must change revision and fingerprint.

## Security assertions

ProjectProfile/event ledger schema must have no field capable of containing:

- credentials/tokens/API keys/MFA codes,
- cookies/storage state,
- authorization headers,
- raw prompts/responses,
- HTML/screenshots/traces,
- browser objects.

No generic arbitrary metadata dictionary.

## Metrics

Record:

```text
bootstrap_questions_first_run
bootstrap_questions_reuse_run
profile_revisions_created
sections_reopened
unrelated_fields_reasked
compatibility_actions
operator_profile_review_actions
active_profile_review_seconds
```

Do not claim time savings from the controlled experiment.

## Required final properties

```text
separate disk-backed reuse proven
zero bootstrap questions on current-profile later run
process-specific questions preserved
configuration fingerprint bound into reuse provenance
environment/base URL invalidation selective
workspace hash drift fails closed without silent revision
guided-intake binding drift is capability-specific
business truth survives provider/model change
secrets/auth state absent
existing regression baseline remains green
new Sprint 15 tests green
real operator acceptance passes
```

## Not proven by Sprint 15

- multiple active environments,
- authenticated browser execution,
- AuthProfile strategy,
- secret managers,
- external application generality,
- team sync,
- TTL freshness,
- productivity savings,
- GUI,
- production repository delivery.
