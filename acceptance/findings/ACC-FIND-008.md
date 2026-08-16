# ACC-FIND-008 — guided intake loses material catalogue intent

## Status

**RESOLVED — deterministic intent-preservation correction verified; historical run-02 remains NOT ACCEPTED.**

Related GitHub Issue: `#8 [ACCEPTANCE] ACC-EXT-003 — guided intake loses material catalogue intent`

## Discovery context

```text
test case: ACC-EXT-003
evidence-bearing run: ACC-EXT-003-run-02
product commit: ac1d7b61033251377b9b49d970c50f6d8cdf91e9
guided-intake questions: 9
aggregate context confirmation: completed
browser discovery: not started
result: NOT ACCEPTED / PRODUCT FINDING
```

## Initial mission

The operator asked for a customer looking for a hammer to narrow the catalogue
to relevant products and see the cheapest suitable options first, while keeping
the outcome independent of implementation details.

This contained two deliberately incomplete material concepts:

- what makes a result relevant/suitable;
- what observable ordering proves cheapest suitable options appear first.

## Observation

The question plan collected application, environment, URL, process name,
business outcome, risk, role, precondition, and one observable result. It asked
no material follow-up about relevance/suitability or ordering.

The confirmed context summary retained only products matching search/filter
criteria and at least one matching visible product. It omitted the initial
cheapest-first preference entirely. The product nevertheless treated the context
as ready for discovery.

## Question-quality classification

The questions were understandable and business-level. None requested locators,
DOM details, source targets, classes, methods, or API answers. The finding is not
overly technical questioning; it is `MISSED_CLARIFICATION` and material intent
loss.

## Operator-assistance caveat

The operator used ChatGPT for Polish-to-English translation and limited content
refinement during run-02. The run is not unassisted natural-input evidence and
must not be used for broad claims about operator effort or answer discoverability.

The core finding remains supported independently by persisted product evidence:
the initial mission contains ordering intent; the nine product-selected questions
do not address it; and the confirmed context summary omits it.

## Classification

```text
kind: question-selection defect / intent-preservation defect
severity: Level 1B blocker
silent invention observed: false
material omission observed: true
target defect: false
```

Primary requirements: `ACC-REQ-001`, `ACC-REQ-003`.

Related requirements: `ACC-REQ-004`, `ACC-REQ-006`, `ACC-REQ-007`,
`ACC-REQ-008`.

## No-workaround rule

Do not prepare a follow-up answer sheet, manually add ordering to persisted JSON,
teach the operator to mention every internal context field, or accept a static
heading/result-card assertion as equivalent to the initial mission.

## Deterministic correction

Product commit `23d3f34be364163337e055f50548e2dfc35a6fd3` adds a bounded
intent-preservation contract:

- the unchanged initial mission is displayed beside the structured context;
- a bounded review plan classifies every allowlisted context candidate through
  the existing answer-shape contract;
- only candidates requiring clarification are asked again;
- clarified answers use the normal answer-recording path, and the actual
  operator-facing question is persisted without raw provider prompts/responses;
- the human operator explicitly confirms material-intent coverage;
- invalid collection confirmations, unresolved context, and exhausted planning
  budgets fail closed.

Twenty focused and 505 full-suite tests passed. The correction used no external
target, live LLM call, framework sandbox, or run-03 identifier. This resolves the
product finding without changing the historical run-02 verdict or accepting
Level 1B.

## Run-03 live-retest caveat

Run-03 reached the new material-intent review on product commit
`c1d0237f12582e4d97a9e57cefe9dc3720d5ff27`, but it is not a clean nominal
retest of this finding. The operator entered application identity instead of the
authorized hammer/cheapest-first initial mission and shifted the next bootstrap
answers. ChatGPT then mistakenly supplied expected-result content for a risk
clarification, and the operator confirmed that semantic mismatch.

The review mechanism executed, but this evidence cannot decide whether the live
Ollama plan would preserve the correct intended mission. The deterministic
Issue #8 correction remains resolved; a clean live verdict is deferred until
run-04 after the separate ACC-FIND-010 bridge correction.

## Retest rule

Keep runs 02 and 03 immutable. Run-04 must use the separately corrected
interactive bridge and either no external answer assistance or disclosed literal
translation only, without content suggestions or prepared answers.
