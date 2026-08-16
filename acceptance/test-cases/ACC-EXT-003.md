# ACC-EXT-003 - Analyst-rich catalogue narrowing on Practice Software Testing

## Status

**NOT ACCEPTED / PRODUCT FINDINGS RESOLVED; EXTERNAL RETEST PENDING.**

`ACC-EXT-003-run-01` was consumed by an operator terminal interruption during
intake. The evidence-bearing `ACC-EXT-003-run-02` completed guided intake and
then stopped before browser discovery. No formal ValidationRun package was
created. `ACC-FIND-007` through `ACC-FIND-009` are resolved by deterministic
corrections. The historical run-02 verdict remains unchanged, the scenario
remains **NOT ACCEPTED**, and no run-03 has been consumed.

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

## Pre-execution gate and execution record

All pre-execution gates passed on 2026-08-15 (Europe/Warsaw):

```text
operator target/scope authorization: PASS
bounded read-only target preflight: PASS
TestCartographer commit: ac1d7b61033251377b9b49d970c50f6d8cdf91e9
framework baseline: 4d916dea8190bc59ef8c9dd5aa78aa31dbbf16a6
framework baseline clean: true
historical framework checkout preserved: true
Ollama version/model: 0.32.9 / qwen2.5-coder:7b
headed browser prerequisite: PASS (Chromium 151.0.7922.34)
product change authorized: no
```

The target preflight confirmed that the public catalogue, the working term
`hammer`, and public price-ascending ordering remained sufficient without
authentication or a write action. It froze no exact products, counts, prices,
selectors, or prepared intake answers.

### ACC-EXT-003-run-01

Run-01 was interrupted by the operator with a terminal `KeyboardInterrupt`
during the fourth intake question. It provides no product verdict. The process
had persisted four operator actions and left the operator session `active`.

```text
01-guided-intake-run.json  FA40F3A6A3B5F78C2128410C4E67AAC0F6DA2E7AE89A3DDBC5FD7727358CEB3D
01-intake-session.json      38A6F9478E97525E8FA659686BBBB3E3D670D57DAC579C9375C6ED5C6EFFD5C3
01-minimal-context.json     50A26E91A3EEA879BBDA83711359D24F7B191D7B38DE1399701FD849238496D8
01-minimal-seed.json        9176338819191868D8B575C54C2DEABF21B8969A2D4EF9E39936EFDF9E7B38EB
operator-session.json       F607284064CE7A8B65F82AB307AD7B0B253786FD546B44450B817E10884F40D4
```

Run-01 is immutable and not reusable. Run-02 was partially primed because the
first four prompts had already been exposed.

### ACC-EXT-003-run-02

Run-02 completed nine guided-intake questions and one aggregate context
confirmation, persisting eleven operator actions. It then failed before browser
discovery with:

```text
ValueError: external public single-page creation currently supports heading outcomes only
```

The operator session remained `active` after process termination. Browser
discovery did not start, no framework sandbox was created, the clean framework
baseline remained unchanged, and no target or generated-test verdict exists.

```text
01-guided-intake-run.json  2D6F65FCE3F798E80A32D6B47A62D4D5670C3256E32EAD6A7ACD67D9688918F3
01-intake-session.json      1A27E75EC1DAC2D8367990359884941D89F22F5D893096A7879BA5719ED004A6
01-minimal-context.json     55958DC37C0C5393A089FD340810DD11120AE1591B56CE97A6D00B793CB55467
01-minimal-seed.json        3CFE32B449B59B00C19A27DA2158276FDBC945F81E0A2F1BE44AC49FB8D838CB
operator-session.json       A078DB724A349B5F4CEA40C54C4A55AB10E543FCC29CC340661FFB742C3C37AA
```

Run-02 is **NOT ACCEPTED / PRODUCT FINDING** and is immutable.

## ACC-FIND-007 deterministic remediation

The heading-only capability gap was corrected by product commit
`3b8bb73bd665f8d5389ff2b6a1299c023a97392e`. The external single-page engine
now preserves the legacy heading flow and accepts a reviewed bounded sequence of
same-page `FILL`, `CLICK`, `SELECT`, `CHECK`, `UNCHECK`, and final outcome `READ`
actions with declared owners, semantic roles, and symbolic non-secret test data.

Twenty-five focused and 500 full-suite tests passed. The correction used no
external target, live LLM call, framework sandbox, or new run identifier. It
resolves `ACC-FIND-007` without changing the historical run-02 result. The
intent-preservation defect is corrected separately below, and run-03 remains
unconsumed.

## ACC-FIND-008 deterministic remediation

The intent-preservation defect was corrected by product commit
`23d3f34be364163337e055f50548e2dfc35a6fd3`. The unchanged initial mission is
now reviewed beside the structured context; a bounded review plan selects only
targeted clarifications through the existing answer-shape contract; the actual
operator-facing prompt is persisted; and the human operator must explicitly
confirm material-intent coverage. Invalid confirmations, unresolved context, and
planning-budget exhaustion fail closed.

Twenty focused and 505 full-suite tests passed. The correction used no external
target, live LLM call, framework sandbox, or new run identifier. It resolves
`ACC-FIND-008` without changing the historical run-02 result or accepting Level
1B. Run-03 remains unconsumed pending the authorized external retest.

## ACC-FIND-009 deterministic remediation

The stale-active lifecycle defect was corrected by product commit
`5887f83b5159c8751ef9a5a5638f7dc9afd259ce`. Regression proves that unhandled
runtime failures persist `aborted`, `KeyboardInterrupt` persists `interrupted`,
and supported `QUIT` remains `paused`, while the original exception is re-raised.

Five focused and 492 full-suite tests passed. No external target contact, new
run identifier, live LLM call, framework sandbox, or historical evidence change
was required. Run-03 remains unconsumed; the lifecycle correction does not
accept Level 1B.

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

## Operator-assistance limitation observed in run-02

The operator used ChatGPT during intake to translate Polish answers into English.
Most business content originated with the operator, but the assistance also
refined the environment and role wording and proposed the precondition. The run
must therefore not be represented as unassisted natural-input evidence.

This limitation does not remove the deterministic heading-only failure, the
comparison between the original mission and accepted context, or the persisted
terminal-state observation. It does limit claims about operator effort and the
independent discoverability of good answers. A later retest should use either no
external assistance or disclosed literal translation only, without answer-
content suggestions.

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

### Run-02 question-quality result

The nine questions were understandable and remained at business/process level.
No locator, DOM, source-code, class, method, or API answer was requested.

| Question area | Review |
|---|---|
| Application | NECESSARY |
| Environment | NECESSARY |
| Starting URL | NECESSARY |
| Process short name | USEFUL |
| Business outcome | NECESSARY, but insufficient to preserve the full initial mission |
| Failure/risk | USEFUL |
| User role | USEFUL |
| Precondition | NECESSARY |
| Observable result | NECESSARY, but accepted without ordering semantics |

Material `MISSED_CLARIFICATION` observations:

- no question established what `relevant` or `suitable` meant;
- no question preserved or challenged the `cheapest suitable options first`
  ordering preference;
- no question tied visible result evidence to an accepted ascending-price rule;
- the aggregate context summary omitted the initial ordering requirement, yet
  the product accepted the context as ready for discovery.

The finding is omission/loss rather than silent invention. External answer
assistance limits broader claims about question discoverability, but these gaps
are directly visible by comparing the persisted initial mission, ordered
questions, and confirmed context summary.

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
