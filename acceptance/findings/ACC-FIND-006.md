# ACC-FIND-006 — browser discovery stage overcounts live LLM calls

## Status

**RESOLVED — deterministic measurement correction verified by regression.**

Related GitHub Issue: `#6 [ACCEPTANCE] ACC-EXT-002 — browser discovery stage overcounts live LLM calls`

## Discovery context

```text
test case: ACC-EXT-002
run: ACC-EXT-002-run-04
product commit: bd6595ab89c5c4c2d1e6317ee372bfaa9a74462f
functional result: PASS
finding kind: measurement_issue
severity: non-blocking
```

## Observation

The completed Creation Flow reports the `browser_discovery` stage with:

```text
live_llm_calls: 1
```

while the persisted discovery run contains:

```text
ambiguities: []
guidance_turns: []
live_provider_used: false
```

The run-level total is `live_llm_call_count: 1`, which is consistent with the
single live Ollama guided-intake turn.

Therefore the browser-discovery stage overcounts one live LLM call that did not
occur.

## Confirmed cause

The stage metric is derived from configured provider mode:

```python
live=1 if provider_mode == "ollama" else 0
```

rather than from actual persisted discovery guidance turns.

The metric therefore answers whether Ollama mode was configured, not how many
live LLM calls occurred in that stage.

## Requirement impact

Primary:

- `ACC-REQ-013` — expose operator/system effort and runtime measurements
  accurately enough for acceptance interpretation.

## Classification

```text
kind: measurement_issue
functional acceptance impact: none
Sprint 17 Level 1 blocker: false
run-04 functional result remains: PASS
```

This finding does not invalidate:

- successful bounded discovery,
- accepted synthesis and adaptation,
- generated Page Object / fixture / test,
- independent sandbox execution,
- `1/1` target test result,
- Issue #4 retest PASS,
- Issue #5 retest PASS.

## Smallest correction boundary

Derive browser-discovery stage `live_llm_calls` from the actual persisted
guidance-turn count:

```python
live=len(discovery_run.guidance_turns)
```

Do not change provider behavior, ambiguity logic, discovery selection,
acceptance decisions, schemas, or historical run artifacts.

## Regression coverage

Prove at minimum:

1. zero guidance turns -> zero discovery live-LLM calls;
2. one guidance turn -> one discovery live-LLM call;
3. multiple guidance turns -> exact count, preventing boolean/provider-mode
   semantics from returning.

Full product regression remains required after the focused measurement tests.

## Retest strategy

No new GOV.UK external run is required.

This correction is deterministic aggregation over already persisted runtime
facts. Validate through focused unit regression and the full product suite.

`ACC-EXT-002-run-04` remains immutable and must not be rewritten.

## Resolution

Status: RESOLVED.

The finding was preserved in commit
`657bad79d991e66b8f48f586fc2d212cd50688e6` before remediation.

Commit `ab4f3f5e873f0849a2d418a9a0c6cf7ff8279839` changed browser-discovery
`live_llm_calls` to derive from the actual persisted `guidance_turns` count and
added focused regression coverage for zero, one, and multiple turns. The full
product regression also passed before commit.

The historical `ACC-EXT-002-run-04` artefact remains unchanged and therefore
retains the originally observed stage metric. Its functional PASS remains valid.
No new external GOV.UK run was required for this deterministic aggregation fix.
