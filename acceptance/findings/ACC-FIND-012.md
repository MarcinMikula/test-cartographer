# ACC-FIND-012 — provider-facing schema and recovery classifier do not cover the full action contract

## Status

**OPEN — preserved from immutable ACC-EXT-003-run-05 evidence and linked to GitHub Issue #12.**

```text
finding id: ACC-FIND-012
GitHub issue: #12
GitHub URL: https://github.com/MarcinMikula/test-cartographer/issues/12
test case: ACC-EXT-003
evidence-bearing run: ACC-EXT-003-run-05
observed product commit: 782e11c8d4defea267510467e41377a2c5aef621
observed on: 2026-08-16 Europe/Warsaw
result: NOT ACCEPTED / PRODUCT–PROVIDER CONTRACT FINDING
external target contacted: false
framework sandbox created: false
run-06 consumed: false
```

## Observation

Run-05 began from the correctly scoped natural mission:

> Automating the search and sort functionality in the public Toolshop catalog by
> searching for the keyword "hammer" and sorting the results from lowest to
> highest price.

No prepared answer sheet, fixture answers, or answer-content assistance was
used. Guided intake and material-intent confirmation completed. Three live local
Ollama calls completed within the 600-second per-call timeout:

```text
collection       123.87875819997862 s
review            89.93903379997937 s
target proposal   53.373939500015695 s
provider total   267.191731499974 s
```

The target-proposal JSON reached deterministic action-contract validation, then
failed before human review with the safe diagnostic:

```text
category: schema
field path: actions[1]
rule: unsupported_validation_rule
repairable: false
attempts: 1
```

Because the rule was unallowlisted and non-repairable, the Issue #11 correction
correctly did not enter `awaiting_repair`, offer `RETRY`, or perform a second
target-proposal call. The proposal remained `blocked` with zero accepted targets.
The operator session truthfully persisted `aborted` with eleven actions. Raw
provider prompts and responses were not persisted.

Browser discovery never started. Toolshop was not contacted. No CreationFlowRun,
framework sandbox, generated source, or target test exists. The clean fixed
framework baseline remained at
`4d916dea8190bc59ef8c9dd5aa78aa31dbbf16a6`.

## Evidence identity

```text
01-guided-intake-run.json
  size: 2645
  sha256: 3F027B5791BB1A7246E05BE5915785F6B4B69BE01582CEAD6BD82E0C9B887A1D
01-intake-session.json
  size: 18187
  sha256: C3E91E2378877B71ED17344C2E84055128B7DE2CAD9D7B1E30EB5EEADB47B7F5
01-minimal-context.json
  size: 4987
  sha256: 5EB22BA04412B3C87D8712F362FFEF501C2D004B032476B4B25761FE4FF61B2F
01-minimal-seed.json
  size: 424
  sha256: 126C7CBC16275B42A9FB55229B13A71B7D2E3BD17AC822AE6EFDA4912AFD0FFC
02-interaction-target-proposal.json
  size: 1677
  sha256: CD11AB03DAFB764A25FABF58C74BAA3DFC9EDB79E54C31C1862BB99FF069C3DE
operator-session.json
  size: 3964
  sha256: C919C003928CFE7C3A7D7A7EC26474C81AAACCB9D7AA3FBA30953B2715FAA7F8
terminal transcript
  size: 1442
  sha256: 27513CDEAF4F771D4C9931A0CB687F14EC73901E4BF1B9AC1F80EE8CFCE86390
```

The run directory contains exactly the six named files and no subdirectories.
The transcript is stored beside the immutable run directory. Run-05 is not
reusable.

## Classification

```text
category: product–provider integration / contract representation and recovery classification
severity: Level 1B blocker
target defect: no
Issue #11 regression: no
provider replacement justified: no
```

Primary violated requirements:

- ACC-REQ-008 — no valid proposal reached human review;
- ACC-REQ-016 — the nominal supported interface could not prevent or classify
  the complete action-conditioned contract mismatch.

Guardrails corroborated:

- ACC-REQ-004 — human, provider, validation, hashes, and lifecycle provenance
  remained distinguishable without raw content;
- ACC-REQ-006 and ACC-REQ-007 — the rejected LLM proposal received no
  accept/reject, factual, or browser authority;
- ACC-REQ-012 — minimized evidence retained the safe category, path, fallback
  rule, hashes, sizes, latency, and terminal state;
- ACC-REQ-014 — neither Toolshop nor the framework was blamed;
- ACC-REQ-015 — the unknown rule remained non-repairable and failed closed;
- ACC-REQ-017 — the original and fixed-baseline framework checkouts remained
  unchanged;
- ACC-REQ-019 — later v0.2 terminology describes the already truthful aborted
  lifecycle without changing run-05's historical basis.

Supporting / traceability requirements:

- ACC-REQ-003 — unresolved suitability semantics remained a separate caveat;
- ACC-REQ-010 and ACC-REQ-011 — preservation and future run-06 retest;
- ACC-REQ-013 — the three live provider latencies were retained.

Requirements derived or revised:

- ACC-REQ-020 — acceptance requirements v0.2 makes the complete, consistent,
  safely diagnosable, and bounded-recovery proposal contract an explicit closure
  requirement for Issue #12 and any later run-06. It is not retroactively used
  to fail run-05.

The product contract is split across the schema supplied to the provider, local
action-conditioned validators, and the safe validation-rule classifier. Run-05
proves that a parsed action-level proposal can reach a locally enforced rule that
the supplied schema did not prevent and the classifier can identify only through
the non-repairable fallback `unsupported_validation_rule`. This makes the bounded
human recovery path unreachable for the observed proposal.

The exact raw value and exact local validator are intentionally unavailable from
the minimized evidence. Do not infer or reconstruct them. The defensible finding
is the contract-coverage gap, not a claim about one hidden provider value.

The live Ollama response did fail the full product contract. That is relevant
provider-quality evidence, but it is not sufficient to replace the provider:
TestCartographer did not expose the complete action-conditioned contract in a way
that either prevented the value or classified the deterministic correction as a
bounded repair rule.

## Expected behavior

For every supported action shape, deterministic action-conditioned requirements
should be represented consistently across provider guidance/schema, local
validation, and safe recovery classification. A repairable semantic mismatch
should reach an explicit operator `RETRY`/`QUIT` choice under the one-repair
budget. Truly unknown, unsafe, invalid-JSON, duplicate-key, locator-like, or
otherwise unallowlisted failures must remain immediate fail-closed cases.

No proposal may receive browser, target, or framework authority before it passes
the complete deterministic contract and explicit human review.

## Candidate correction boundary — not authorized

The smallest plausible correction should:

1. express each supported action-conditioned rule in the provider-facing schema
   or equally explicit prompt contract where the JSON Schema dialect permits it;
2. assign stable safe codes to every deterministic local cross-field validator
   instead of relying on message-substring fallback;
3. mark only bounded, deterministic semantic corrections repairable;
4. preserve the current no-raw-prompt/no-raw-response evidence boundary;
5. keep invalid JSON, duplicate keys, locator-like content, and genuinely unknown
   rules non-repairable;
6. test every validator-to-safe-diagnostic mapping and every allowed recovery
   transition;
7. keep browser, target, and framework authority unavailable until a valid
   proposal is explicitly accepted.

This section records a candidate boundary only. It does not authorize product
changes, a provider switch, external execution, or run-06.

## Retest rule

Run-05 is immutable and not reusable. Any retest requires a separately authorized
correction, a new exact product commit, a fresh pre-run gate, and a new run-06
directory. No prepared answers or answer-content assistance may be introduced.
The natural mission must continue to contain Toolshop, `hammer`, and
lowest-to-highest price ordering.
