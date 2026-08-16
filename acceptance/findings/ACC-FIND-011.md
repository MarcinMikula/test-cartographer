# ACC-FIND-011 — invalid target proposal cannot reach diagnosable bounded human recovery

## Status

**OPEN — Level 1B blocker preserved before remediation.**

Related GitHub Issue: `#11 [ACCEPTANCE] ACC-EXT-003 — invalid target
proposal cannot reach diagnosable bounded human recovery`

## Discovery context

```text
test case: ACC-EXT-003
evidence-bearing run: ACC-EXT-003-run-04
product commit: 9494ac1d33e4a5f0b76d22eaf7819c2f150c49f6
framework baseline: 4d916dea8190bc59ef8c9dd5aa78aa31dbbf16a6
guided intake: complete
material-intent confirmation: complete
target proposal state: blocked
target proposal blocker: invalid_target_contract
human target review: not reached
browser discovery: not started
framework sandbox: not created
target contacted: false
operator-session state: aborted
result: NOT ACCEPTED / PRODUCT–PROVIDER INTEGRATION FINDING
```

## Observation

The corrected Issue #10 bridge invoked a live target-proposal call and persisted
its minimized proposal record. The response was syntactically valid JSON: an
invalid JSON response would have been classified separately as `invalid_json`.
It nevertheless failed the target schema, semantic validation, or plan-building
contract and produced zero accepted targets.

The operator saw only:

```text
RuntimeError: external interaction-target proposal failed closed:
invalid_target_contract
```

No safe field path, validation category, or violated rule was available. The
proposal never reached the supported human review, edit, reject, or accept gate,
and no bounded repair/retry path was offered. The flow stopped safely before
browser authority and preserved the session as `aborted`.

## Evidence integrity

```text
01-guided-intake-run.json       98DFCE3AF74EF537D54B2BDFCE82C37C118875BDB84A3CCCE2D864719CF6B4EB
01-intake-session.json          42E2D6954A9CD902DE1AF465E920DDB32B9B12C3B7CB0FF29EA1C9A346BAE0D3
01-minimal-context.json         FE23AF3FA14B021557DAE0A29B0195BD9B0EAC30B752FE338BAF066CECF35B27
01-minimal-seed.json            08C789241E8951A208EAC2AA6B710637DAD7E184883103EC0971EDF03BA15C5A
02-interaction-target-proposal.json
                                DFCF6724BEF75E714D2F382988D9B95F9ACE4A9A88A1EC828CD0D8D14D82E3A9
operator-session.json           3B3C01CADFEDEE2F25B27CADBD5FFEC77E763528BDB3E0A067DD7D62A961DB57
supplied terminal transcript    1457A7B3B8AB605BAF4662F1CC58940D145A593096F0030EFC8B93948E6870FC
```

The run directory contains exactly six files and no subdirectories. Raw
provider prompts and responses were not persisted. The target proposal retains
prompt/response hashes and character counts, preserving privacy and integrity
without making the precise invalid field reconstructable.

## Live provider calls

| Phase | Latency | Prompt chars | Response chars |
|---|---:|---:|---:|
| collection | 121.355 s | 2,914 | 2,461 |
| review | 78.448 s | 3,525 | 1,577 |
| target proposal | 36.086 s | 1,946 | 622 |
| **provider total** | **235.889 s** |  |  |

All three calls completed below the configured 600-second timeout. The complete
shell interval was 1,297.873 seconds and includes human response/review time; it
is not provider latency. No timeout or hang was observed.

## Operator-scope caveat

Run-04 used no prepared answers, fixture answers, or answer-content assistance.
The operator nevertheless supplied a generic initial mission — searching and
filtering on Practice Software Testing — that omitted the authorized `hammer`
term and cheapest-first outcome. The accepted context consequently contained no
concrete search keyword, filter, or ordering rule.

This prevents run-04 from being a clean end-to-end retest of the original
ACC-EXT-003 scenario. It does not explain the later invalid target contract, does
not reopen ACC-FIND-008, and does not justify inventing missing business intent.

## Classification

```text
kind: product–provider integration / diagnosability and recovery defect
severity: Level 1B blocker
Issue #10 bridge absent: false
provider timeout or hang: false
syntactically invalid JSON: false
exact violated contract known: false
safe fail-closed behavior: true
truthful terminal lifecycle: true
target defect: false
```

Primary requirements: `ACC-REQ-008`, `ACC-REQ-016`.

Related requirements: `ACC-REQ-003`, `ACC-REQ-004`, `ACC-REQ-006`,
`ACC-REQ-007`, `ACC-REQ-010`, `ACC-REQ-012`, `ACC-REQ-013`, `ACC-REQ-014`,
`ACC-REQ-015`, `ACC-REQ-017`.

## Why this is one finding

The generic diagnostic and absent repair/retry path occur at the same failed
proposal-contract boundary. Splitting them would create two issues from one
operator-observable inability to recover safely. Preserve them together until
evidence shows independently actionable causes.

## Issue #10 and Issue #9 status

The target-proposal call and persisted proposal artefact prove the Issue #10
bridge executed. ACC-FIND-010 therefore remains resolved. The `aborted` operator
session is a live PASS of the Issue #9 correction, so ACC-FIND-009 also remains
resolved.

## No-workaround rule

Do not persist the raw provider response, inject or repair target JSON by hand,
ask the operator for selectors, edit framework state, reuse run-04, downgrade to
a heading-only scenario, blame Toolshop, silently switch providers, or make a
new LLM call solely to reconstruct the missing error.

## Smallest correction boundary to evaluate

After separate authorization, the smallest justified correction should:

1. retain a safe validation category and non-sensitive field/rule path without
   persisting raw prompts, raw responses, or operator values;
2. allow at most one bounded repair turn or equivalent operator-safe recovery
   when a proposal is structurally close enough to repair;
3. present only a valid proposal to human review;
4. preserve attempt count, latency, hashes, and safe validation outcome for
   every attempt;
5. keep every invalid or unaccepted proposal outside browser authority;
6. stop safely after the bounded recovery budget is exhausted.

This evidence is the first credible indication that the local model may be part
of the limitation, but it is not sufficient to replace Ollama. Product
diagnostics and bounded recovery must be addressed first. A later provider
comparison, if authorized, should use the same minimized prompt/schema and no
external target contact.

## Retest rule

Run-04 is immutable and not reusable. Do not authorize run-05 until this finding
and its GitHub Issue are durably linked, the correction is separately authorized,
implemented, regression-verified, and recorded in acceptance closure.

The later run must use a natural mission that actually expresses the authorized
hammer/cheapest-first customer outcome, without a prepared answer sheet or
answer-content assistance. Literal translation may remain allowed if disclosed.

## Authorization boundary

The finding-only commit is durable and Issue #11 is linked. This record still
authorizes no product change, provider switch, new external execution, run-05
identifier, or remediation.
