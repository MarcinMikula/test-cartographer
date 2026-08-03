# Controlled source delivery

Implemented in Sprint 6 for one human-accepted adaptation plan and one
controlled `qa-automation-framework` copy.

## Purpose

Sprint 5 answers where accepted logical artefacts belong. Sprint 6 answers the
next question:

> Can TestCartographer turn the accepted plan into exact reviewable source,
> apply it safely to a controlled framework copy, and prove that pytest can
> collect and execute one meaningful browser test?

The delivery stage is deliberately separate from planning:

```text
accepted AdaptationPlan
+ unchanged framework fingerprint
+ explicit non-secret GenerationProfile
→ CodePatch ready for review
→ explicit patch acceptance
→ preflight against a clean framework copy
→ atomic application
→ independent framework execution
→ CreationEvaluation
```

Plan acceptance is not source-write authorization.

## Contracts

### `GenerationProfile` v0.1

The profile supplies the small amount of execution information that is not
present in the logical proposal:

- the environment-variable name that will contain the application URL,
- explicit symbolic-to-public test-data bindings,
- confirmation that no secret values are embedded,
- confirmation that no live LLM is used.

The reference profile binds `data_search_query` to the public value `Example`.
The application URL itself is resolved only at runtime from
`TEST_CARTOGRAPHER_CATALOG_URL`.

### `CodePatch` v0.1

A patch contains exact source changes and review metadata. Each source change
records:

- target path and symbol,
- `create_file` or `append_symbol`,
- the expected pre-change hash where applicable,
- exact UTF-8 source content,
- the resulting content hash,
- originating adaptation operation IDs.

The patch preserves source whitespace exactly. It is more sensitive than the
Sprint 5 structural snapshot because it intentionally contains generated code.

### `PatchApplicationReport` v0.1

The report records:

- the accepted patch and plan IDs,
- the expected and observed framework fingerprints,
- each applied path and resulting hash,
- application timing,
- the post-application fingerprint,
- explicit success state.

### `CreationEvaluation` v0.1

The evaluation records the first creation-lifecycle evidence:

- generated, modified, and reused artefact counts,
- review and application results,
- compile, collection, and execution exit codes and durations,
- collected and passed test counts,
- time to first runnable test,
- live-LLM call count,
- whether the original framework remained unchanged.

A passed evaluation requires all structural, review, application, collection,
execution, assertion-placement, independence, and immutability checks.

## Reference source change

The accepted public-search plan produces:

```text
pages/catalog_page.py
→ CatalogPage
→ create_file

components/catalog_search_form.py
→ CatalogSearchForm
→ create_file

tests/e2e/conftest.py
→ catalog_context
→ append_symbol

tests/e2e/test_search_catalog.py
→ test_search_catalog
→ create_file
```

The generated test uses the framework independently of TestCartographer. It:

1. receives a normal Playwright `Page` from `catalog_context`,
2. opens the runtime URL,
3. fills the observed search field,
4. activates the observed Search button,
5. reads the observed results region,
6. checks that the observed results heading is visible,
7. asserts that the submitted public query is present in the result.

Assertions remain in the test rather than the Page Object or Component Object.

## Safety boundaries

Before generation or application, the current framework is rescanned. Its
fingerprint must match the snapshot accepted by the adaptation plan.

Application then performs a complete preflight before writing:

- every path must stay inside an allowlisted root,
- create targets must still be absent,
- append targets must still match the expected hash,
- resulting content hashes must match the patch,
- unsupported operations are rejected.

Writes use temporary files and `os.replace`. If a later write fails, already
changed files are restored from their preflight bytes.

Sprint 6 intentionally applies the patch first to a snapshot-bounded sandbox,
not to the user's original framework repository. The sandbox is materialized
only from file and directory entries present in the accepted `FrameworkSnapshot`.
Files outside the approved workspace roots are not copied merely because they
exist elsewhere in the source repository. The setup script compares the
original repository's Git status before and after the complete acceptance run.

This boundary was strengthened after the first real Windows acceptance run.
The initial setup used a broad repository copy. An out-of-scope
`tests/conftest.py`, absent from the accepted snapshot, was copied into the
sandbox and influenced pytest collection. The corrected workflow copies exact
snapshot entries and verifies that the materialized fingerprint still matches
before patch application.

## Generation-profile framework contract

A structurally valid snapshot is not automatically compatible with every source
template. Sprint 6 templates inherit from `BasePage` and `BaseComponent`, so the
`GenerationProfile` now declares these prerequisites explicitly as file, symbol,
and symbol-kind requirements.

The setup validates the contract immediately after read-only inspection and
before presenting the adaptation plan for acceptance. `build_code_patch()`
repeats the check. A missing file, missing symbol, or wrong symbol kind blocks
generation rather than producing an unresolved import.

This boundary was added after a real Windows run reached pytest collection with
a generated import of `components.base_component.BaseComponent` but a local
snapshot that did not include that framework primitive.

## Review boundaries

There are now three independent human decisions:

```text
Sprint 4 — accept the logical POM proposal
Sprint 5 — accept exact repository placement
Sprint 6 — accept exact generated source
```

Only the third decision authorizes application, and only to the explicitly
supplied target copy.

## Replay and live execution

Deterministic tests use controlled fixtures for generation, review, stale-state
rejection, atomic application, rollback, schema round trips, and evaluation.

The standalone verifier additionally:

1. materializes only the accepted framework snapshot entries,
2. proves out-of-scope repository files are absent,
3. applies the accepted patch,
4. compiles the bounded sandbox,
5. requires pytest to collect exactly one generated test,
6. serves the controlled local application,
7. executes the generated test with real Chromium where the environment allows,
8. creates a passed creation evaluation,
9. proves the original framework fixture remained byte-for-byte unchanged.

The Windows setup repeats the flow against a snapshot-bounded sandbox materialized
from the user's local `qa-automation-framework` after explicit plan and patch
acceptance.

## What Sprint 6 proves

- accepted logical and repository plans can be realized as exact source,
- generated source can be reviewed separately before writing,
- stale framework state blocks generation and application,
- one existing fixture file can be extended without replacing it,
- the controlled patch can be applied atomically to a snapshot-bounded framework sandbox,
- files outside the accepted snapshot cannot influence sandbox pytest collection,
- the resulting framework can compile, collect, and run one meaningful browser
  test,
- normal execution does not require TestCartographer or a live LLM,
- creation-lifecycle timings and correction counts can be recorded,
- the original framework repository can remain unchanged during acceptance.

## What Sprint 6 does not prove

- safe automatic modification of the user's original framework repository,
- general source editing for arbitrary existing classes and imports,
- semantic quality from a live LLM,
- handling of merge conflicts or concurrent edits,
- enterprise authentication, secrets, or Salesforce support,
- usefulness across multiple processes and applications,
- maintenance after a later application change,
- superiority over manual, Codegen, or general-LLM adaptation.


## Sprint 7 handoff

The Sprint 6 generated test already carries a module-level `TRACEABILITY` tuple.
Sprint 7's framework-side collector can combine those source IDs with a
non-secret execution profile containing the accepted context, process,
synthesis-run, adaptation-plan, and code-patch IDs.

This avoids changing source-delivery authority: accepting generated code still
does not authorize evidence collection, raw failure retention, or maintenance.
Those are separate runtime and analysis policies. Mixed suites will eventually
need per-test generated metadata rather than one profile default.
