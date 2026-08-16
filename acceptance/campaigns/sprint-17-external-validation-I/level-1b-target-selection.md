# Sprint 17 Level 1B - target selection

## Status

**AUTHORIZED / EXECUTION ATTEMPTED - stopped before target contact.**

This document records the authorized target boundary and execution attempts. It
does not itself authorize product changes. Runs 02 and 03 both stopped before
browser discovery, so neither makes a defect or correctness claim about Practice
Software Testing. Run-03 live-corroborated the resolved Issue #9 lifecycle
contract while exposing a separate interactive reviewed-target bridge gap.

## Candidate application

```text
application: Practice Software Testing / Toolshop
current public application: https://practicesoftwaretesting.com/
observed version during planning: v5.0
owner/project: Testsmith
application type: public demo/training e-commerce application
authentication for authorized scope: none
writes for authorized scope: none
```

Planning review on 2026-08-15 found that Testsmith explicitly presents
Practice Software Testing as an open-source application for learning software
testing and test automation.

Sources reviewed during planning:

```text
https://practicesoftwaretesting.com/
https://www.testsmith.io/en
https://api.practicesoftwaretesting.com/api/documentation
```

The public UI exposes a product catalogue backed by application data and
supports search/filter/sort behaviour suitable for a richer single-page process.

Direct robots.txt retrieval was not independently established during this
planning review. This design therefore does **not** authorize crawling,
high-volume scanning, API harvesting, account creation, or destructive actions.

The authorized execution is intentionally limited to a small human-triggered,
headed-browser interaction on an application explicitly intended for software
testing practice.

## Authorization and final preflight

Operator authorization was recorded on 2026-08-15 (Europe/Warsaw).

Authorized:

- Practice Software Testing / Toolshop as the Level 1B target;
- the initial operator mission defined below;
- bounded read-only catalogue search, filtering, sorting, and visible-result
  observation when justified by the accepted process context;
- the explicit non-destructive browser boundary defined below.

This authorization does not start an `ACC-EXT-003` ValidationRun and does not
authorize product changes.

A final bounded read-only target preflight on 2026-08-15 confirmed that:

- the public root loaded as Practice Software Testing / Toolshop v5.0;
- the working term `hammer` produced multiple visible relevant results;
- the public price-ascending sort produced ascending visible result prices after
  normal UI stabilization;
- the accepted catalogue process required no authentication or write action.

The preflight establishes target suitability only. It deliberately preserves no
exact result count, product list, price, selector, DOM target, or prepared intake
answer. No run identifier had been consumed at preflight time.

## Execution status

Three acceptance run identifiers were later consumed:

- `ACC-EXT-003-run-01` ended through an operator terminal interruption during
  guided intake and provides no product verdict;
- `ACC-EXT-003-run-02` completed guided intake and aggregate confirmation, then
  failed before browser discovery on the historical heading-only boundary;
- `ACC-EXT-003-run-03` completed guided intake and material-intent review, then
  failed before browser discovery because the interactive path supplied no
  reviewed interaction targets for the non-heading outcome.

Run-03 used product commit `c1d0237f12582e4d97a9e57cefe9dc3720d5ff27`
and three live Ollama calls. Its operator session ended `aborted`; no browser
discovery, target contact, framework sandbox, generated source, or target test
occurred. The attempted retest was materially contaminated by shifted operator
answers and disclosed erroneous ChatGPT answer-content assistance, so it does
not provide a clean live verdict on the resolved Issue #8 behavior.

The target preflight remains valid suitability evidence. Findings 007–010 are
resolved deterministically. Product commit
`12ce4485a817a5c28bf2d2d8331087ec86b331c0` supplies the reviewed-target
bridge and passed 27 focused and 516 full-suite tests without contacting the
target. The target is not implicated, and run-04 remains unconsumed pending a
fresh pre-run gate.

## Why this target fits Level 1B

Level 1 on GOV.UK deliberately minimized both technical and analytical
complexity.

Level 1B needs a different challenge:

```text
keep technical scope bounded enough to diagnose product behaviour
+
increase process/analytical ambiguity and operator freedom
```

Practice Software Testing is suitable because the proposed process can remain
on the catalogue page while still involving:

- an operator goal rather than a locator-level instruction,
- catalogue-narrowing intent,
- an ordering preference expressed as a customer outcome,
- natural ambiguity around what counts as a relevant/suitable result,
- multiple interactive targets,
- a result set rather than one static heading,
- observable state changes,
- list-level assertions,
- symbolic/concrete test-data decisions.

This makes the problem richer without using the still-unsupported multi-page
discovery capability as the primary source of failure.

## Proposed process envelope

Working process name:

```text
Find suitable catalogue products and show the cheapest relevant options first
```

The operator starts from this **mission**, not from a prepared test-case script:

> I want to automate checking that a customer looking for a hammer can narrow
> the catalogue to relevant products and see the cheapest suitable options
> first. I care about the customer outcome, not how the page implements it.

This wording is deliberately useful but incomplete.

It contains:

- a user/business goal,
- a concrete product need,
- an outcome-level ordering preference,
- legitimate ambiguity around what "relevant" and "suitable" mean,
- no prescribed search/filter/sort control,
- no locator,
- no Page Object structure,
- no exact assertion implementation,
- no expected result count.

The operator must not memorize or reproduce pre-written follow-up answers.

## What the operator is allowed to do

The operator should behave like a real experienced tester/analyst.

Allowed:

- answer in natural language,
- add useful business context not present in the initial mission,
- notice that an earlier answer was incomplete and correct/clarify it,
- say "I do not know" where authority/evidence is genuinely missing,
- distinguish what is important from what is optional,
- mention risks, assumptions, expected outcomes, and alternate interpretations,
- reject a misleading interpretation,
- ask what a confusing TestCartographer question means,
- make a reasonable decision when TestCartographer exposes real ambiguity.

The operator is not expected to be perfectly concise or perfectly structured.

## What the operator must not do

Do not rescue the product by supplying its implementation.

Forbidden during nominal execution:

- CSS/XPath/role selectors supplied by the operator,
- DOM inspection used to hand TestCartographer a target,
- Page Object class/method names supplied as answers,
- direct source-code edits,
- hidden JSON/state repair,
- API calls used to bypass browser discovery,
- manually injected product IDs,
- manual framework edits,
- pre-written intake answers copied from this testware,
- changing the acceptance target merely to obtain a green run.

## Authorized browser boundary

Allowed:

```text
https://practicesoftwaretesting.com/
```

Allowed interaction family, if required by accepted process context:

- catalogue search,
- sort control,
- category filter,
- visible product result cards/list,
- visible product names/prices,
- normal non-destructive catalogue state.

Explicitly out of scope:

- navigation into product detail as a required step,
- cart,
- checkout,
- login,
- registration,
- favorites,
- contact form,
- payment,
- API testing,
- direct database/backend assertions,
- user creation,
- stateful writes,
- leaving the Practice Software Testing application,
- broad crawling.

If the supported Creation Flow itself navigates unexpectedly outside this
boundary, preserve evidence and stop.

## Preflight data rule

The exact public catalogue may change.

Before the first external ValidationRun, perform a read-only target preflight
only to establish that the chosen product term still yields enough visible
results to exercise the intended result/sort semantics.

Authorized working term:

```text
hammer
```

Do not encode an exact product count or exact price in the historical test basis
before the run.

If the term no longer supports a meaningful bounded process, record this as
target/testware drift and revise the test design before consuming a ValidationRun
ID. Do not misclassify ordinary target-data drift as a TestCartographer bug.

## Primary experiment question

> Can TestCartographer transform richer, imperfectly structured analyst/tester
> intent into coherent, evidence-backed automation without being led through a
> prepared implementation path?

This is the defining Level 1B question.

## Secondary questions

We also want evidence about whether TestCartographer:

1. distinguishes business intent from implementation detail;
2. asks useful missing-context questions instead of merely more questions;
3. recognizes material ambiguity in what counts as relevant/suitable instead
   of silently choosing criteria;
4. accepts explicit UNKNOWN where appropriate;
5. avoids inventing catalogue/business facts;
6. separates project/bootstrap context from process-specific context;
7. represents a multi-action same-page process coherently;
8. discovers the needed UI targets rather than asking the human for locators;
9. proposes maintainable automation with meaningful result assertions;
10. preserves human authority at review boundaries.

## Why this is not Level 2

The current objective is not to maximize frontend difficulty.

Even if the Toolshop UI uses dynamic/API-backed rendering, Level 1B is scoped so
that the **primary variable under test is analyst/process complexity**.

Level 2 will intentionally increase frontend/runtime complexity across multiple
dynamic public applications. Pracuj.pl remains one planned candidate, together
with two additional applications from other functional domains.

## Product-change rule

No product change is authorized by this testware or target authorization.
The Issue #9 lifecycle correction was separately authorized, implemented, and
regression-verified from preserved run evidence.

If execution exposes a failure:

```text
observe
-> preserve evidence
-> classify
-> decide whether it is product, testware, target, requirement, or expected limit
-> only then design the smallest justified correction
```

Potential future GUI or structured-choice-field work is explicitly outside v1.0
unless separately reprioritized later. Level 1B may create evidence for that
future discussion, but it must not trigger speculative GUI implementation.
