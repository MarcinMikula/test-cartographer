# ACC-FIND-005 — existing run output is destructively removed before startup

## Status

**RESOLVED — verified by acceptance retest and regression evidence.**

Related GitHub Issue: `#5 [ACCEPTANCE] ACC-EXT-002 — existing output directory is destructively removed before run start`

## Discovery stage

```text
STLC phase: Test Execution / pre-execution startup
test case: ACC-EXT-002
attempted run: ACC-EXT-002-run-03
tested product commit: 2192a758758cd2a21955fd6f920ce142eb194eed
intended external target: https://www.gov.uk/driving-licence-codes
guided intake started: false
external target contact: false
result: FAILED before nominal run start
```

## Observation

The operator started the external single-page Creation Flow with:

```text
output directory:
../TestCartographer-local-artifacts/validation/govuk/ACC-EXT-002-run-03
```

Startup failed immediately with:

```text
PermissionError: [WinError 5] Access denied
...
runner.py, in run_human_triggered_creation_flow
    shutil.rmtree(output)
```

The origin and prior contents of the already-existing `ACC-EXT-002-run-03`
directory are not established by the available evidence and must not be guessed.

## Confirmed product behavior

At the tested commit the interactive runner performs:

```python
output = Path(output_dir).resolve()
if output.exists():
    shutil.rmtree(output)
output.mkdir(parents=True)
```

Therefore a pre-existing operator-supplied run directory is treated as disposable
and recursively deleted before the nominal interactive flow starts.

The Windows permission error prevented complete removal of the directory, but
`shutil.rmtree()` can remove children before a later filesystem operation fails.
The integrity of the attempted `run-03` directory therefore cannot be assumed.

## Requirement impact

Primary:
- `ACC-REQ-010` — historical failed/incomplete evidence must not be rewritten.

Related:
- `ACC-REQ-011` — retest must use a new traceable run.
- `ACC-REQ-012` — evidence integrity must fail closed.
- `ACC-REQ-016` — nominal workflow must not require undocumented state surgery.

## Classification

```text
evidence kind: failure
classification: PRODUCT BUG
severity for Sprint 17 Level 1: blocker
GOV.UK defect: false
testware defect: false
guided intake started: false
external target contact: false
```

## No-workaround rule

Do not:
- reuse `ACC-EXT-002-run-03`,
- empty or delete the existing directory and claim the same run id,
- manually rescue or reconstruct `run-03`,
- bypass the collision by deleting historical acceptance evidence.

The attempted `run-03` identifier is consumed/unsafe for acceptance purposes.

## Smallest correction boundary

The interactive runner must never recursively delete a pre-existing
operator-supplied output directory during nominal startup.

Required behavior:

```text
parent directories may be created if missing
requested run directory must be created as a new directory
if requested run directory already exists -> stop before mutation
existing contents remain untouched
browser/external execution does not start
```

Prefer atomic final-directory creation using:

```python
output.mkdir(parents=True, exist_ok=False)
```

and convert `FileExistsError` into the runner's controlled
`InteractiveFlowStopped` boundary so the CLI emits a clear stop message and
non-zero controlled exit code.

## Regression coverage

1. Existing output directory:
   - controlled `InteractiveFlowStopped`,
   - sentinel file remains unchanged,
   - browser opener is not called.

2. Fresh output directory:
   - startup creates the new directory,
   - the flow reaches its first operator-input boundary normally.

Full product regression remains separate from these focused tests.

## Retest rule

Keep the attempted `ACC-EXT-002-run-03` untouched as failed/pre-execution evidence.

After remediation is committed and pushed, execute a new immutable:

```text
ACC-EXT-002-run-04
```

against the new exact product commit.

## Related issue lifecycle

- Issue #1 remains open until the external Creation Flow completes end to end.
- Issue #2 remains open because multi-page discovery remains unsupported.
- Issue #3 blocker was crossed by run-02.
- Issue #4 remediation remains awaiting a real external retest.
- Issue #5 tracks this independent output-integrity blocker.

## Resolution

Status: RESOLVED.

The collision behavior was corrected to fail closed without deleting existing output and was covered by focused regression; the new immutable `ACC-EXT-002-run-04` then started from a fresh output directory and completed successfully.

Historical failed/incomplete evidence remains immutable and is not rewritten.
