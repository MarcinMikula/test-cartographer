# Framework execution evidence — contract v0.1

## Purpose

Sprint 7 defines the first bounded handoff from normal
`qa-automation-framework` execution back to TestCartographer maintenance.

The framework-side collector answers:

```text
What executed?
Where did it stop?
Was the outcome a pass, a test failure, or an infrastructure error?
Which accepted context and generated artefacts does the test belong to?
What is the last safe structural step we can use for later analysis?
```

It deliberately does **not** answer:

```text
Is this an application bug?
Which repository file should be changed?
Should a selector be healed?
Should the failure be ignored or retried?
```

Those are maintenance-analysis questions for later sprints.

## Two-module boundary

The reference pytest collector is a standalone framework-side file. It imports
pytest and the Python standard library, but it does not import TestCartographer.

```text
qa-automation-framework + collector
→ ExecutionEvidenceBundle JSON
→ ordinary pytest process ends

later

TestCartographer
→ validates and assesses the bundle
→ decides whether failure evidence is sufficient for maintenance intake
```

Normal framework execution therefore remains independent of:

- the TestCartographer package,
- a running Cartographer process,
- an LLM provider,
- network access to an AI service.

## Outcome vocabulary

Version `0.1` distinguishes exactly three persisted outcomes.

### `passed`

The test call completed and setup/teardown did not fail.

A pass record contains no failure object.

### `test_failure`

The pytest `call` phase failed.

This means the executable test did not satisfy its assertion or interaction
contract. It does **not** mean the application is defective. Possible causes
still include:

- application behavior,
- stale automation,
- invalid test data,
- a test-code defect,
- an incorrect expectation,
- an environment problem that surfaced during the test call.

### `infrastructure_error`

Collection, setup, or teardown failed.

Examples include:

- a required fixture cannot prepare the environment,
- a browser or local service cannot start,
- a test module cannot be collected,
- cleanup fails after a test.

The classification is phase-based and deterministic. It is not an LLM
judgment.

## Precedence rule

When more than one phase fails, version `0.1` uses this priority:

```text
setup or teardown failure
→ infrastructure_error

otherwise call failure
→ test_failure

otherwise successful call and teardown
→ passed
```

This rule avoids silently treating environment and fixture failures as product
defects.

## Evidence profile

`ExecutionEvidenceProfile` version `0.1` contains only non-secret collection
policy:

- framework ID,
- environment label,
- include-passed policy,
- record and step budgets,
- failure-text hashing budget,
- names of environment variables whose values must be redacted in memory,
- default traceability IDs,
- sensitivity,
- explicit non-persistence flags.

The profile may contain a variable name such as `SALESFORCE_PASSWORD`. It must
not contain that variable's value.

## Record contract

Each `ExecutionEvidenceRecord` contains:

- run and profile IDs,
- test node ID, relative path, name, line, and markers,
- one of the three outcomes,
- phase-aware failure summary when applicable,
- bounded structural step history,
- framework/runtime version metadata,
- traceability to accepted Cartographer artefacts,
- explicit privacy flags.

## Traceability

The reference contract can link a framework test to:

- `ContextBundle`,
- process,
- accepted synthesis run,
- accepted adaptation plan,
- accepted code patch,
- source proposal/method/assertion IDs.

Traceability may be supplied through:

1. non-secret profile defaults for one bounded run,
2. a per-test `cartographer` marker,
3. a module-level `TRACEABILITY` tuple generated with the test.

A record cannot claim `complete=true` unless all required high-level IDs are
present. Missing fields remain explicit.

## Bounded step probe

The framework plugin exposes an optional `execution_probe` fixture.

A test, Page Object, component, or fixture may report only structural metadata:

- step ID,
- Page Object class,
- method name,
- action kind,
- target element ID,
- locator ID,
- current application URL for minimization.

The API does not accept:

- input values,
- method arguments,
- credentials,
- response bodies,
- page HTML,
- arbitrary dictionaries.

The reference profile retains at most eight steps per test. Sprint 8 can use
the last safe step to narrow re-observation without reconstructing the whole
session.

## URL minimization

Given:

```text
https://user:password@example.test/catalog?query=Example#results
```

only this may be persisted:

```text
origin: https://example.test
path: /catalog
```

Credentials, query, and fragment are structurally marked as not persisted.

## Failure minimization

The collector does not persist the raw exception message or raw traceback.

It stores:

- exception type,
- deterministic safe summary such as `AssertionError during call`,
- relative failure location where available,
- SHA-256 of bounded redacted text,
- redaction count,
- truncation flag.

The digest is calculated after configured runtime secrets and common named
secret assignments are redacted in memory.

This preserves replay and equality checks without placing assertion values,
credentials, or full stack traces into the evidence contract.

## Explicitly excluded by default

Version `0.1` persists none of the following:

- input values,
- method arguments,
- credentials or environment values,
- raw exception messages,
- raw tracebacks,
- captured stdout or stderr,
- full URLs with query or fragment,
- page HTML or raw DOM,
- screenshots,
- Playwright traces,
- network bodies,
- host names.

A future policy may authorize separate artefact references, but those artefacts
must not be smuggled into this contract as unrestricted strings.

## Bundle contract

`ExecutionEvidenceBundle` represents one pytest run and contains:

- started/completed timestamps,
- bounded records,
- pass/test-failure/infrastructure counts,
- truncated-record count,
- collector identity and version,
- proof that no raw artefacts or live LLM were used.

Counts are validated against actual records. A producer cannot claim one test
failure while serializing two.

## Maintenance-readiness assessment

`assess_execution_evidence()` is deterministic.

A failure record is actionable for Sprint 8 only when it contains:

- failure details,
- complete high-level traceability,
- at least one bounded structural step.

The whole bundle is ready for reactive-maintenance intake when:

- at least one failure exists,
- every failure is actionable,
- no record was dropped by the bundle budget.

Readiness does not mean the failure has been diagnosed.

## Reference verifier

Run:

```powershell
python scripts/verify_execution_evidence_contract.py
```

The verifier launches a separate pytest process with a standalone collector and
three controlled outcomes:

```text
one pass
one call-phase test failure
one setup-phase infrastructure error
```

It then loads the resulting JSON through TestCartographer and verifies:

- all three outcomes remain distinct,
- every record has complete traceability,
- the last POM step is retained,
- URL credentials/query/fragment are absent,
- secret values are absent,
- raw failure text and output are absent,
- the failure bundle is ready for Sprint 8 intake,
- pytest execution did not require TestCartographer or an LLM.

## CLI

Inspect a bundle:

```powershell
test-cartographer evidence status `
    --bundle testdata/execution/bundle/reference_outcomes.json
```

Assess maintenance readiness:

```powershell
test-cartographer evidence assess `
    --bundle testdata/execution/bundle/reference_outcomes.json
```

## Exit criteria

- [x] A framework-side collector runs without importing TestCartographer.
- [x] `passed`, `test_failure`, and `infrastructure_error` remain distinct.
- [x] A call-phase failure is not labeled an application bug.
- [x] Each reference record links to context, process, synthesis, plan, patch,
  and source IDs.
- [x] The last bounded POM step is retained without values or arguments.
- [x] URL credentials, query, and fragment are removed.
- [x] Raw exception messages, tracebacks, output, HTML, screenshots, and traces
  are not persisted.
- [x] Record and step budgets are explicit.
- [x] Static replay and a live subprocess verifier both validate the contract.
- [x] Deterministic readiness identifies whether failure evidence is sufficient
  for Sprint 8 intake.
- [x] No live LLM is used.

## What Sprint 7 proves

A normal pytest framework process can emit a small, provider-neutral,
privacy-bounded and traceable execution artefact that TestCartographer can
validate later without coupling the test run to Cartographer or an LLM.

## What Sprint 7 does not prove

- root-cause diagnosis,
- application-bug classification,
- automatic repair,
- screenshot/trace/network retention policy,
- crash-safe streaming if pytest is forcibly terminated,
- xdist/multiprocess aggregation,
- retries and flaky-test correlation,
- CI upload and retention,
- installation in the production framework repository,
- enterprise authentication or Salesforce usefulness.
