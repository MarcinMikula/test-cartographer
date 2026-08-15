# Sprint 17 Level 1B - target selection

## Status

**PROPOSED FOR OPERATOR REVIEW - not executed.**

This document designs the next external acceptance slice. It does not authorize
product changes and it does not claim that the target has already been executed
by TestCartographer.

## Candidate application

```text
application: Practice Software Testing / Toolshop
current public application: https://practicesoftwaretesting.com/
observed version during planning: v5.0
owner/project: Testsmith
application type: public demo/training e-commerce application
authentication for proposed scope: none
writes for proposed scope: none
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

The proposed execution is intentionally limited to a small human-triggered,
headed-browser interaction on an application explicitly intended for software
testing practice.

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

## Proposed browser boundary

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

Current working term:

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

No product change is authorized by this design.

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
