# Framework adaptation planning

## Status

Implemented in Sprint 5 for one accepted logical POM proposal and one bounded
local `qa-automation-framework` workspace.

## Purpose

Sprint 4 ends with an accepted logical POM proposal. That proposal knows which
application pages, components, methods, fixtures, test intent, and assertions
are authorized by the context. It deliberately does not know where those
artefacts belong in a concrete automation repository.

Sprint 5 adds a separate repository-aware stage:

```text
accepted SynthesisRun
+ approved WorkspaceProfile
+ read-only FrameworkSnapshot
→ deterministic AdaptationPlan
→ explicit human review
```

The stage plans exact target files and symbols. It does not generate source
code and does not modify the framework.

## Contracts

### WorkspaceProfile

`WorkspaceProfile` version `0.1` is a non-secret inspection policy. It contains:

- a logical repository kind and label,
- required root marker files,
- allowed repository-relative roots,
- ignored directory names,
- file-count and file-size budgets.

It does not contain:

- an absolute local path,
- credentials,
- authentication state,
- environment values,
- source-code content.

The profile is supplied separately from `--framework-root`. The local absolute
path is used only for that invocation and is not persisted.

### FrameworkSnapshot

`FrameworkSnapshot` version `0.1` stores a minimized structural view:

- repository-relative file and directory paths,
- file sizes,
- SHA-256 digests,
- top-level Python classes and functions,
- class bases and method names,
- one deterministic root fingerprint.

The snapshot explicitly records that source contents, absolute paths, and
secret values were not persisted.

The inspector reads allowlisted files locally to hash and parse them. The
literal privacy flags do not prove that every inspected file was safe. The
profile owner remains responsible for excluding secret-bearing paths. Sprint 5
has no secret scanner.

### AdaptationPlan

`AdaptationPlan` version `0.1` links:

- one accepted synthesis run and proposal,
- one workspace profile,
- one exact framework snapshot fingerprint,
- ordered file/symbol operations,
- source proposal IDs,
- dependencies between operations,
- verification commands,
- carried open questions,
- a separate review decision.

Operation kinds are:

- `create_file` — the target path does not exist in the snapshot,
- `add_symbol` — the file exists but the required symbol does not,
- `reuse_symbol` — both target file and symbol already exist.

The first mapping convention is deliberately small:

| Logical proposal artefact | Framework target |
|---|---|
| Page Object | `pages/<class_name_in_snake_case>.py` |
| Component Object | `components/<class_name_in_snake_case>.py` |
| Fixture | `tests/e2e/conftest.py` |
| E2E test | `tests/e2e/<test_name>.py` |

This convention is not claimed to fit every project. Human review is required
before Sprint 6 may generate or apply source changes.

The target is aligned with the current framework structure, where browser E2E
fixtures live under `tests/e2e/conftest.py`. This path was verified rather than
inferred from a generic pytest convention.

## Bounded inspection

The inspector:

1. resolves the supplied local root,
2. verifies required marker files,
3. traverses only allowlisted roots,
4. rejects symlinked inspected entries,
5. enforces file-count and file-size budgets,
6. parses Python files with `ast`,
7. persists metadata rather than source text,
8. calculates a deterministic repository fingerprint.

It does not:

- run repository code,
- import inspected modules,
- execute pytest,
- follow symlinks,
- inspect Git history,
- infer architecture from prose,
- detect credentials or malicious source,
- modify any inspected file.

## Separate authority stages

Sprint 5 preserves two distinct approvals:

```text
Sprint 4 proposal acceptance
→ logical POM boundary approved

Sprint 5 adaptation-plan acceptance
→ exact repository targets approved
```

Accepting the proposal does not authorize repository placement. Accepting the
adaptation plan still does not write code. Sprint 6 must introduce a separate
source-generation and application boundary.

## CLI workflow

Inspect one local framework copy:

```powershell
test-cartographer adapt inspect `
    --profile testdata/adaptation/profile/qa_automation_framework.json `
    --framework-root C:\path\to\qa-automation-framework `
    --snapshot .test-cartographer\framework-snapshot.json `
    --snapshot-id snapshot_local_qaf
```

Create a plan from an accepted synthesis run:

```powershell
test-cartographer adapt plan `
    --profile testdata/adaptation/profile/qa_automation_framework.json `
    --snapshot .test-cartographer\framework-snapshot.json `
    --run testdata/synthesis/run/accepted_public_search.json `
    --plan .test-cartographer\public-search-adaptation-plan.json `
    --plan-id adapt_public_search
```

Review the plan:

```powershell
test-cartographer adapt review `
    --plan .test-cartographer\public-search-adaptation-plan.json `
    --decision accepted `
    --reason "Exact targets match the intended framework architecture."
```

Review changes only the plan state. It prints and preserves the invariant:

```text
Framework files were not modified.
```

## Controlled reference workspace

The committed `testdata/framework/reference/` fixture is a small controlled
workspace that mirrors relevant current framework layers:

- root markers,
- `pages/` with `BasePage` and an existing Page Object,
- `components/` with an existing component,
- `tests/e2e/`,
- `testdata/`.

It is not a vendored copy of the full framework and is not proof that every
current or future framework file is understood. The production-facing command
accepts a real local framework root; the controlled fixture keeps tests
replayable and independent of network access or cross-repository mutation.

## Reference result

For the accepted public-search proposal, the controlled snapshot produces:

```text
pages/catalog_page.py                 → CatalogPage
components/catalog_search_form.py     → CatalogSearchForm
tests/e2e/conftest.py                 → catalog_context
tests/e2e/test_search_catalog.py      → test_search_catalog
```

The page, component, and test targets are `create_file` operations. The existing
`tests/e2e/conftest.py` produces `add_symbol` for `catalog_context`. Separate tests
also cover `reuse_symbol` when the exact target symbol already exists.

## What Sprint 5 proves

- a local framework copy can be inspected through a bounded allowlist,
- the persisted snapshot can exclude source text and absolute paths,
- repository state can be replayed through hashes and Python symbols,
- an accepted proposal can map deterministically to exact files and symbols,
- existing target symbols can be distinguished from missing files or symbols,
- proposal review and repository-plan review remain separate,
- acceptance can leave the framework byte-for-byte unchanged.

## What Sprint 5 does not prove

- semantic correctness of the first mapping convention,
- compatibility with every valid framework customization,
- full analysis of imports, decorators, fixtures, typing, or runtime behavior,
- detection of secret-bearing or malicious source files,
- correct generated Python code,
- safe patch creation or merge-conflict handling,
- successful pytest collection or execution in the target framework,
- usefulness on a full enterprise repository,
- live LLM quality, authentication, maintenance, or Salesforce readiness.
