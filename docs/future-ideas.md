# Future ideas — parked after Checkpoint 14.5

This file stores ideas that are **not active roadmap commitments**.

Checkpoint 14.5 intentionally reduces speculative breadth. Ideas should move
into active work only when external validation or an explicit post-v1 product
decision demonstrates a need.

Chronological history remains in `LEARNINGS.md`.

## Post-v1 user interface evaluation

A local web/desktop/IDE review interface may eventually visualize:

- project/profile status,
- process context,
- evidence and freshness,
- unresolved questions,
- ambiguity choices,
- POM/adaptation proposals,
- exact source diffs,
- validation/maintenance history.

Do not build it before v1 value is known.

The question after v1 is not "would a GUI look better?" but:

> would a UI materially reduce learning cost, operator errors, cognitive load,
> or review time for a workflow that already demonstrates value?

Possible surfaces include a local web UI, VS Code, or Cursor integration.

## Jira and documentation evidence connectors

Potential evidence sources:

- Jira issues/defects,
- test-management cases,
- acceptance criteria,
- Confluence or other knowledge bases,
- requirements repositories,
- diagrams,
- architecture notes.

Imported content must remain evidence, not automatic truth.

Any connector needs authorization, minimization, provenance, freshness,
retention, conflict handling, and external-processing policy.

Do not build connectors before real validation demonstrates that manual/project
context acquisition is a material bottleneck.

## Accepted-change history and retrieval

Potentially store and retrieve:

- accepted proposal,
- supporting evidence,
- human review decision,
- final diff,
- execution result,
- later maintenance outcome.

This may become better retrieval material than raw model output.

Build only after repeated real adaptations show which historical decisions are
actually reusable.

## Application and impact graph

A richer graph could connect:

- processes,
- pages,
- components,
- elements,
- roles,
- data,
- risks,
- tests,
- automation symbols,
- accepted changes.

It may improve change-impact analysis and retrieval.

Do not introduce graph infrastructure before real validation demonstrates a
problem that the current bundle/reference model cannot solve economically.

## Additional LLM providers

Possible later adapters:

- other local OpenAI-compatible endpoints,
- LM Studio,
- approved enterprise model endpoints,
- Anthropic,
- OpenAI.

External providers require explicit minimization and authorization.

Provider count is not a product-quality metric. One validated provider is more
valuable than several unvalidated integrations.

## LLM evaluation through llm-qa-toolkit

A separate evaluation harness may assess outputs such as:

- missing-context detection,
- source-grounded classification,
- POM boundary proposals,
- unsafe certainty,
- change-impact explanations.

Evaluation requires trustworthy reference cases. An unsupported LLM judge
opinion is not ground truth.

## PhoenixQA interoperability

Potential future boundary:

```text
TestCartographer
→ accepted application/automation context and maintenance evidence

PhoenixQA
→ runtime recovery/healing evidence

explicit handoff
→ better diagnosis or maintenance proposal
```

Do not merge runtime dependencies merely because both projects touch failures.

## Visual and multimodal evidence

Screenshots or visual models may become useful for:

- overlays,
- occlusion,
- canvas-based controls,
- visual-only hierarchy,
- layout-dependent outcomes.

Multimodal capture increases privacy exposure, model cost, retention burden,
and review complexity.

Adopt only when external validation proves DOM/accessibility evidence
insufficient for an important target.

## Team review and approval

Enterprise use may eventually separate:

- collector,
- domain reviewer,
- automation reviewer,
- security reviewer,
- approver.

The v1 validation path remains single-user unless a real target requires
separate authority.

## Private / enterprise deployment modes

Potential deployment patterns:

- fully local,
- local orchestration with minimized approved cloud-model input,
- approved enterprise model endpoint,
- air-gapped customer-managed deployment.

Do not promise provider/deployment parity before empirical testing.

## Domain packs

Optional vocabularies or prompts might later help domains such as banking,
insurance, telecommunications, CRM, or e-commerce.

A domain pack must never silently become domain authority.

## Test-design assistance

Future assistance may suggest candidate techniques such as:

- equivalence partitioning,
- boundary values,
- decision tables,
- state transitions,
- risk-based prioritization.

This requires stronger structured business-rule evidence than the current UI/POM
map.

## Economics dashboard

If repeated validation creates enough data, a dashboard could summarize:

- setup time,
- active operator time,
- corrections,
- proposal acceptance/rejection,
- LLM usage/cost,
- maintenance effort,
- expansion effort.

Metrics must inform product decisions rather than become vanity reporting.

## Ideas removed from TestCartographer roadmap

### API / Service Object Model adaptation

API/SOM adaptation is **not part of TestCartographer's product direction**.

The product targets frontend/UI context and POM-oriented automation. API
automation may be explored separately in another project if ever needed.

### General multi-framework platform

Supporting arbitrary Selenium/Cypress/Robot/Playwright-language architectures
is not a current product goal.

### Autonomous whole-application exploration

Unrestricted autonomous crawling is not a v1 roadmap goal. Bounded guided
observation may evolve only from concrete validation needs.

### Model-based generation of arbitrary test suites

The current goal is reliable context-assisted automation for explicitly selected
processes, not autonomous generation of a whole application's test model.
