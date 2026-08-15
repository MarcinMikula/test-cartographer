# ACC-FIND-008 — guided intake loses material catalogue intent

## Status

**OPEN — Level 1B intake/intent blocker preserved before remediation.**

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

## Correction boundary to design later

The product must retain material facts from the initial request and select
follow-up questions based on unresolved semantic needs, not merely fill a fixed
generic context checklist. Ambiguity may be clarified, explicitly deferred, or
kept UNKNOWN, but it must not disappear while the context becomes ready.

## Retest rule

Keep run-02 immutable. A later retest must use a new run identifier and either no
external answer assistance or disclosed literal translation only, without content
suggestions.
