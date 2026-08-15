# ACC-EXT-003 - Analyst-rich catalogue narrowing on Practice Software Testing

## Status

**AUTHORIZED / NOT EXECUTED.**

No ValidationRun exists for this test yet.

## Why this test exists

`ACC-EXT-002` proved the bounded external single-page Creation Flow on a simple,
well-defined GOV.UK heading scenario.

That success does not establish that TestCartographer can work effectively when
an experienced tester/analyst provides richer, less perfectly structured
process knowledge.

`ACC-EXT-003` therefore changes the dominant source of difficulty.

```text
ACC-EXT-002
-> technically simple
-> analytically simple
-> strongly bounded operator path

ACC-EXT-003
-> still bounded to one public catalogue page
-> analytically richer
-> natural operator language
-> real ambiguity
-> multiple UI actions/results
-> no prepared answer script
```

The purpose is not to make the operator intentionally adversarial.

The purpose is to stop leading TestCartographer by the hand.

## Target

```text
application: Practice Software Testing / Toolshop
URL: https://practicesoftwaretesting.com/
planned public version observed during design: v5.0
authentication: none
writes: none
sensitivity: public
```

See:

```text
acceptance/campaigns/sprint-17-external-validation-I/
level-1b-target-selection.md
```

## Initial operator mission

The run should begin from wording semantically equivalent to:

> I want to automate checking that a customer looking for a hammer can narrow
> the catalogue to relevant products and see the cheapest suitable options
> first. I care about the customer outcome, not how the page implements it.

Do not expand this into a prepared intake answer sheet.

The operator should answer subsequent questions naturally.

## Natural ambiguity to observe

The mission deliberately describes a customer outcome without defining exactly
what makes a catalogue result "relevant" or "suitable", and without naming the
UI controls that should implement the outcome.

A valid product response may:

- ask what relevance/suitability means when that distinction is material;
- derive only criteria that are explicitly supported by later operator answers;
- preserve unresolved criteria as UNKNOWN when the operator cannot decide;
- propose search, filtering, sorting, or another observed interaction only when
  the accepted context and browser evidence justify it.

The product must **not** silently invent a relevance rule or turn a UI control
into a business requirement merely because that control exists.

The observation point is therefore semantic handling of incomplete intent, not
whether one predetermined category-filter question was asked.

## Expected analytical behaviour

TestCartographer should help separate at least the following concepts when they
become relevant:

```text
user goal
process purpose
risk
role
preconditions
product/search test data
criteria for relevance/suitability
ordering preference
expected observable outcome
unknowns/assumptions
browser-observable evidence
automation implementation
```

The operator does not need to use those labels.

A good intake should derive structure from natural input without asking the
operator to speak in the internal data model.

## Linked acceptance requirements

Primary:

```text
ACC-REQ-001  bounded operator intent
ACC-REQ-002  ask only justified context; reuse compatible bootstrap where applicable
ACC-REQ-003  uncertainty remains explicit
ACC-REQ-004  authority and provenance
ACC-REQ-005  bounded browser discovery
ACC-REQ-006  human remains authoritative
ACC-REQ-007  bounded LLM role
ACC-REQ-008  reviewable automation
ACC-REQ-009  independent execution
ACC-REQ-012  fail-closed evidence
ACC-REQ-013  expose operator effort
ACC-REQ-014  product failure is not target defect
ACC-REQ-015  safe stop on insufficient authority/evidence
ACC-REQ-016  nominal supported interfaces only
ACC-REQ-017  protect original automation repository
```

Conditional if findings/corrections occur:

```text
ACC-REQ-010  preserve finding before remediation
ACC-REQ-011  traceable retest
```

## Preconditions

Before consuming the first ValidationRun ID:

- `main` is clean and exact product commit is recorded;
- the Level 1B target/scope is explicitly authorized by the operator;
- Practice Software Testing remains publicly accessible;
- a bounded read-only preflight confirms the chosen product term can exercise
  meaningful search/result/order behaviour;
- no login, registration, cart, checkout, contact, payment, or write flow is
  required;
- the original `qa-automation-framework` working repository is protected;
- local browser/provider prerequisites are ready;
- no product code is changed merely to make this scenario fit.

## Current pre-execution gate

Recorded on 2026-08-15 (Europe/Warsaw):

```text
operator target/scope authorization: PASS
bounded read-only target preflight: PASS
ValidationRun ID consumed: no
product change authorized: no
```

The preflight confirmed that the public catalogue, the working term `hammer`,
and public price-ascending ordering remain sufficient for the intended process
semantics without authentication or a write action. It does not freeze exact
products, counts, prices, selectors, or prepared intake answers.

Still required immediately before the first run:

- integrate the accepted testware to `main`;
- verify that `main` is clean and record its exact product commit;
- verify local browser/provider prerequisites and framework-sandbox protection;
- allocate a fresh ValidationRun ID only after all gates pass.

## Operator freedom rule

This test intentionally removes the answer script used implicitly by earlier
controlled acceptance work.

During intake the operator may:

- answer with several facts in one response,
- provide a useful aside or assumption,
- correct themselves,
- say something is optional,
- say they do not know,
- reject TestCartographer's interpretation,
- answer in a way that is semantically useful but does not mirror the prompt
  wording.

This behaviour is not automatically a test failure.

It is the input condition Level 1B is designed to evaluate.

## Intended operator profile

TestCartographer is not intended for arbitrary end users.

This acceptance scenario assumes an operator with sufficient technical,
project, and testing-methodology background to reason about process intent,
risk, assumptions, ambiguity, expected outcomes, and review decisions.

For the current product direction, the minimum realistic operator profile is
approximately a senior-level software tester / test analyst.

The operator is not expected to provide implementation details such as
selectors, DOM structure, Page Object design, or source-code changes.

A future GUI may reduce interaction burden, but it would not remove this
competence boundary.

## Operator priming limitation

The operator participated in Level 1B test design and therefore knows the
high-level acceptance concerns before execution.

During the ValidationRun the operator should work only from the initial mission
and normal TestCartographer prompts, without consulting the detailed acceptance
oracle or preparing follow-up answers.

This does not invalidate the scenario as acceptance evidence for the intended
expert-operator workflow. It only means that the result must not be presented
as a blinded evaluation of first-time problem discovery or question
discoverability.

## Operator anti-rescue rule

The operator must not provide:

- locators/selectors,
- DOM node details,
- source-code targets,
- class/method names,
- product IDs,
- hidden JSON edits,
- direct API answers used to bypass UI evidence,
- manually edited ContextBundle values after the supported intake boundary,
- framework source edits.

If the flow cannot continue without such intervention, preserve the finding.

## Authorized same-page process envelope

The final accepted process may legitimately include:

```text
open catalogue
-> narrow the catalogue using interactions justified by accepted context
-> establish the accepted cheapest-first result semantics
-> observe a meaningful result set
-> verify an outcome tied to the operator's accepted intent
```

This is an envelope, not a mandated implementation sequence.

TestCartographer should determine the exact automation representation from
accepted context and browser evidence.

## Minimum meaningful automation outcome

A PASS may not be based only on:

```text
page opened
heading visible
search control visible
sort control visible
```

The generated test must exercise the accepted process and assert a meaningful
post-interaction outcome.

Depending on the final human-approved context, useful result semantics may
include evidence such as:

- the requested catalogue narrowing visibly changed the result set;
- a known/reasonable matching product remains visible after narrowing;
- displayed result prices follow the accepted ascending-price rule;
- an explicitly required filter is visibly active and affects the result state.

The exact oracle must come from the final accepted context and observable UI,
not be silently invented by the implementation.

## Question-quality review

Level 1B adds a manual qualitative review of the intake conversation.

For each material question, the operator/reviewer may classify it as:

```text
NECESSARY
USEFUL
REDUNDANT
CONFUSING
LEADING
IMPLEMENTATION_LEVEL
REPEATED_BOOTSTRAP
MISSED_CLARIFICATION
```

This is acceptance testware, not a new product telemetry contract.

Do not add product fields merely to support this review before the run.

The post-run review should pay special attention to:

- questions that the operator could not reasonably answer;
- repeated questions whose answer was already supplied;
- questions that ask for implementation rather than business/process knowledge;
- missed clarification of relevance/suitability when it was required to support the claimed assertion;
- places where the LLM appears to infer a fact that the human never authorized.

## Acceptance oracle

### PASS

PASS requires evidence that:

- the supported Creation Flow starts from the natural mission without an
  internal prepared fixture;
- the operator is not required to translate their knowledge into selectors or
  source-code structure;
- material ambiguity is clarified, explicitly deferred, or kept UNKNOWN;
- supplied facts retain human provenance/authority;
- TestCartographer does not silently invent business or catalogue facts;
- browser discovery stays within the authorized catalogue page/scope;
- the process model contains multiple meaningful actions/results rather than a
  static-page check;
- POM/adaptation/source proposals are reviewable;
- the generated automation asserts meaningful accepted process semantics;
- patch application is confined to the isolated framework sandbox;
- independent framework execution succeeds;
- the evidence package verifies fail-closed;
- no unrecorded manual rescue occurred.

### PASS WITH LIMITATIONS

A limited pass may be justified when the final automation is correct and
traceable but the interaction exposes non-blocking usability/intake weaknesses,
for example:

- redundant but harmless questions,
- awkward phrasing,
- excessive confirmation burden,
- a confusing question successfully corrected through the supported interface,
- conservative over-questioning that does not change authority or truth.

Such friction must be recorded rather than ignored.

### NOT ACCEPTED / PRODUCT FINDING

Material failure includes behaviour such as:

- silently inventing a meaning for relevance/suitability that the operator never authorized;
- inventing expected results or business rules;
- requiring locator/source knowledge from the operator;
- losing or contradicting already supplied material context;
- repeatedly asking project/bootstrap questions without a valid invalidation
  reason;
- requiring manual internal JSON/source/state surgery;
- producing a trivial static assertion that does not represent the accepted
  process;
- writing unexpectedly to the original automation repository;
- reporting PASS despite unresolved evidence/authority required for the claimed
  assertion.

### BLOCKED / INCONCLUSIVE

Use a truthful blocked/inconclusive outcome if:

- the public target changes materially before/during the run;
- the chosen search term no longer yields enough evidence for the designed
  process;
- the target becomes unavailable or introduces authentication;
- authorization or evidence becomes insufficient;
- an external target issue prevents a meaningful product verdict.

Do not convert these automatically into TestCartographer defects.

## Finding discipline

Any material finding follows the established campaign rule:

```text
observe
-> preserve
-> classify
-> record issue if actionable
-> only then remediate
-> new run ID where external retest is applicable
```

The run that exposed the finding remains immutable.

## Evidence expectations

In addition to normal Sprint 16/17 evidence, retain enough minimized evidence to
review the analyst-rich interaction:

- initial mission,
- ordered questions actually asked,
- operator answers/authority transitions already allowed by product policy,
- ambiguity handling,
- question count and reprompts,
- operator post-run question-quality review,
- accepted process context,
- browser discovery targets,
- proposal/plan/source reviews,
- independent execution,
- operator difficulty/confidence/reuse assessment.

Do not introduce raw page dumps, screenshots, secrets, or raw provider payloads
merely for this test unless separately justified by policy.

## Product-change gate

This testware does not authorize implementation work.

If the product performs poorly with natural analyst input, first determine
whether the evidence indicates:

```text
intake/reasoning defect
question-selection defect
missing product requirement
operator guidance/UX problem
expected limitation
target/testware problem
```

A GUI or structured-choice fields may later be considered as post-v1.0 UX
hypotheses. They are not the default fix and are not in current v1.0 acceptance
scope.

## Exit evidence

At closure we should be able to answer, from evidence rather than impression:

1. Did TestCartographer understand the operator's actual process intent?
2. Which questions materially improved the context?
3. Which questions were redundant, confusing, or implementation-level?
4. Did it preserve or resolve material ambiguity in what "relevant/suitable" meant?
5. Did it invent anything?
6. Did the final process model become clearer than the operator's initial
   unstructured statement?
7. Did the generated automation represent that accepted model?
8. Did it run independently without manual rescue?
9. What product limitation did this test reveal that Level 1 could not reveal?
