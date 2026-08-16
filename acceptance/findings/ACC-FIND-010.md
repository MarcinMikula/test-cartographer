# ACC-FIND-010 — interactive guided flow cannot produce reviewed rich interaction targets

## Status

**RESOLVED — deterministic reviewed-target bridge verified; historical run-03 remains NOT ACCEPTED.**

Related GitHub Issue: `#10 [ACCEPTANCE] ACC-EXT-003 — interactive guided
flow cannot produce reviewed rich interaction targets`

## Discovery context

```text
test case: ACC-EXT-003
evidence-bearing run: ACC-EXT-003-run-03
product commit: c1d0237f12582e4d97a9e57cefe9dc3720d5ff27
framework baseline: 4d916dea8190bc59ef8c9dd5aa78aa31dbbf16a6
guided intake: complete
material-intent review: complete
browser discovery: not started
framework sandbox: not created
target contacted: false
operator-session state: aborted
result: NOT ACCEPTED / PRODUCT FINDING
```

## Observation

The Issue #7 correction supports bounded reviewed `FILL`, `CLICK`, `SELECT`,
`CHECK`, `UNCHECK`, and final `READ` actions. Run-03 nevertheless reached the
external plan builder without reviewed interaction targets. The nominal
interactive runner supplied accepted process context only, and plan construction
failed closed with:

```text
ValueError: external public single-page creation requires reviewed interaction targets for non-heading outcomes
```

No browser discovery or target contact occurred. The target and framework are not
implicated.

## Evidence integrity

```text
01-guided-intake-run.json  eb3761988d587919057aac9c46df314660a380f602020d61f7f3c41b1ccf7967
01-intake-session.json      ad5da212a9b2da3cda1a8c66ffb5d5b7bfbbae81ae03d4badf11ef0686c2d1db
01-minimal-context.json     e77637ba26eb134b1cf30a0a187fa86ca5faec7f48b809aeac6d91694b20225e
01-minimal-seed.json        70100d18f3b583e835bf9fc6a9fe5a8e4eea5111860375542042ec7f08705d78
operator-session.json       57049e7e78207be242e0f7888bd98b3f32f77dddc9d8afec96eddf326823fd61
supplied evidence ZIP       1f1ba2ef4455ef7e353d368fa082e052e34c14bcb7aab1f3537c9482e1012f65
```

The operator session contains twelve actions, `headed_browser_used=false`, and
no CreationFlowRun ID. Guided intake contains three live Ollama calls:

| Phase | Latency | Prompt chars | Response chars |
|---|---:|---:|---:|
| collection | 125.511 s | 2,937 | 2,461 |
| review 1 | 89.841 s | 3,214 | 1,927 |
| review 2 | 93.721 s | 3,234 | 1,971 |

All calls completed below the configured 600-second timeout. Raw provider
prompts and responses were not persisted.

## Operator and assistance caveat

The operator entered application identity as the initial mission and shifted the
following bootstrap answers. ChatGPT then mistakenly interpreted the risk
clarification as an expected-outcome question and supplied answer content that
the operator used. The confirmed risk therefore contains expected-result
semantics.

This contamination prevents a clean live verdict about the Issue #8 correction
or Ollama's ability to preserve the authorized hammer/cheapest-first mission. It
does not cause or remove the deterministic missing-target bridge failure.

## Classification

```text
kind: interactive integration / reviewed-target bridge defect
severity: Level 1B blocker
rich external engine absent: false
nominal reviewed-target bridge absent: true
provider timeout or hang: false
target defect: false
```

Primary requirements: `ACC-REQ-008`, `ACC-REQ-016`.

Related requirements: `ACC-REQ-003`, `ACC-REQ-004`, `ACC-REQ-006`,
`ACC-REQ-007`, `ACC-REQ-010`, `ACC-REQ-012`, `ACC-REQ-014`, `ACC-REQ-015`,
`ACC-REQ-017`.

## Live lifecycle corroboration

The unhandled ValueError persisted the operator session as `aborted`. This is a
live PASS of the Issue #9 terminal-state correction and does not reopen
`ACC-FIND-009`.

## No-workaround rule

Do not inject `reviewed_targets` into JSON, prepare selectors/actions outside the
supported review interface, edit the framework, reuse run-03, downgrade the
scenario to a heading assertion, or blame the external target.

## Authorized correction and deterministic verification

After the finding and Issue #10 were durably preserved, the operator separately
authorized the smallest reviewed-target bridge. Product commit
`12ce4485a817a5c28bf2d2d8331087ec86b331c0` now:

- derives a bounded proposal of two through six same-page actions from accepted
  process context;
- presents the proposal for explicit operator inspection, editing, rejection, or
  acceptance;
- converts only accepted actions into `reviewed_targets`;
- preserves the supported action family and symbolic non-secret test-data
  contracts;
- fails closed on invalid or unaccepted plans before browser authority exists.

Validation recorded 27 focused and 516 full-suite passing tests. It used no
external target, live LLM call, framework sandbox, or run-04 identifier. This
resolves the deterministic product finding without changing the historical
run-03 verdict or accepting Level 1B.

## Retest rule

Keep runs 01–03 immutable. After this closure is integrated, run-04 may be created
only through a fresh pre-run gate. It must be nominal and use no prepared answers
or answer-content assistance. GOV.UK regression and Expand Testing BookStore
follow only after that Level 1B retest.
