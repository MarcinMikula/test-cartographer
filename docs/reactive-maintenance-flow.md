# Reactive Maintenance Flow

## Purpose

Sprint 12 adds the first bounded, human-triggered reactive-maintenance slice.
It starts from evidence produced by an independently executed framework test and
ends with the same test passing in an isolated sandbox after an exact reviewed
source change.

The governing rule is:

> A failed test is evidence, not a diagnosis.

The flow must not infer that the application is defective, the locator is stale,
or source code should be changed merely because pytest reported a failure.

## Controlled reference flow

```text
existing framework test
→ changed controlled page breaks one test-id locator
→ standalone framework collector records bounded execution evidence
→ deterministic assessment checks traceability and last-step match
→ operator authorizes current-page re-observation
→ headed Chromium shows current candidates
→ operator selects the intended current control
→ deterministic diagnosis becomes a repair candidate
→ exact one-file source patch is displayed in full
→ operator accepts or rejects the patch
→ reviewed patch is applied to a fresh snapshot-bounded sandbox
→ framework test runs again
→ one failure before becomes one pass after
```

The accepted project and process context are reused. Sprint 12 does not ask the
bootstrap or process-intake questions again.

## Authority boundaries

### Framework execution

The framework owns normal pytest and Playwright execution. Its standalone
collector produces an `ExecutionEvidenceBundle` without importing
TestCartographer or using an LLM.

### Evidence assessment

Deterministic rules may establish only that evidence is sufficient for bounded
re-observation. The assessment checks:

- exactly one target call-phase test failure,
- no infrastructure error for the target run,
- complete links to the accepted context, process, synthesis, plan, patch, and
  source IDs,
- a bounded last step matching the expected action, element, and locator IDs.

A successful assessment reports `reobservation_required`. It does not report a
stale locator or an application bug.

### Current-page re-observation

Playwright collects a bounded candidate set from one authorized page. The
operator sees a headed browser and selects the current control. Only after the
old locator is absent and a current unique candidate is selected may the run
create a `repair_candidate` diagnosis.

### Patch review

The reference repair is deterministic and limited to one exact source file and
one locator occurrence. Before acceptance the CLI displays:

- target path and symbol,
- before and after SHA-256 hashes,
- every source line,
- no preview ellipsis.

The operator may accept or reject. The original framework is never changed.

### Retest

The accepted patch is applied only to a fresh sandbox materialized from the
allowlisted framework snapshot. Hash preflight must match the reviewed source.
The same independent framework execution and evidence collector then prove one
clean pass with no test failure or infrastructure error.

## Human interaction

The controlled real-operator run has five blocking actions:

1. start maintenance,
2. authorize re-observation from the evidence assessment,
3. select the current candidate in headed Chromium,
4. accept the exact full-source patch,
5. authorize sandbox application and retest.

Scripted input covers the same mechanics in regression tests but cannot satisfy
the real-operator acceptance gate.

## LLM boundary

Sprint 12 uses no LLM. Failure assessment, candidate filtering, patch creation,
and verification are deterministic. This is intentional: the slice tests whether
bounded evidence and current-page observation are sufficient for one narrow
repair before introducing model authority into maintenance.

## Persisted artefacts

A successful run writes locally under `.test-cartographer/sprint-12/live/`:

```text
01-before-execution-evidence.json
02-maintenance-evidence-assessment.json
03-maintenance-diagnosis.json
04-maintenance-patch-pending.json
04-maintenance-patch-accepted.json
05-after-execution-evidence.json
reactive-maintenance-run.json
reactive-maintenance-summary.md
sandbox/qa-automation-framework/
```

The contracts do not persist raw failure messages, tracebacks, stdout/stderr,
HTML, screenshots, Playwright traces, raw pages, input values, credentials, or
raw operator values.

## What Sprint 12 proves

For one controlled locator drift:

- a real framework failure can feed TestCartographer through bounded evidence,
- infrastructure failure is not treated as a repair candidate,
- evidence grants re-observation rather than a diagnosis,
- the current page can provide a bounded replacement candidate,
- the human remains candidate and patch authority,
- one exact deterministic source change can be reviewed and applied only to a
  sandbox,
- the test can fail before and pass after while the original framework remains
  unchanged,
- ordinary framework execution remains independent of TestCartographer and an
  LLM.

## What Sprint 12 does not prove

It does not prove:

- diagnosis of arbitrary test failures,
- detection of application defects,
- repair of data, environment, timing, workflow, assertion, or authentication
  problems,
- automatic context staleness/conflict updates,
- impact analysis across multiple tests and shared components,
- multi-file or semantic source repair,
- LLM-assisted maintenance,
- direct writes to the user's repository,
- authenticated, multi-page, enterprise, or Salesforce maintenance,
- usability for an unbriefed external participant,
- measured maintenance-time savings.

## Nested pytest failure validation

The pre-repair subprocess is not classified from a single platform exit code.
The process must be non-zero, while the bounded evidence bundle must prove:

```text
passed = 0
test_failure = 1
infrastructure_error = 0
records = 1
```

This keeps failure semantics provider-neutral and prevents a browser/setup error
from becoming a repair candidate. The nested pytest environment removes
inherited pytest control variables and uses an absolute test path. When the
precondition is rejected, diagnostics include the process exit code, evidence
counts, and bounded stdout/stderr; these diagnostics are not persisted in the
evidence contract.

### Nested framework pytest configuration

The maintenance runner invokes the framework test with both an explicit root and
an explicit configuration file:

```text
-c <framework>/pytest.ini
--rootdir <framework>
```

`--rootdir` alone does not guarantee that pytest selects the framework's own
configuration. Without `-c`, parent-repository options such as `--strict-markers`
may leak into the nested run and turn a valid framework marker into a collection
error. A collection error is infrastructure evidence and must never be treated as
the expected pre-repair test failure.
