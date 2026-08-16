# ACC-EXT-003 - Analyst-rich catalogue narrowing on Practice Software Testing

## Status

**NOT ACCEPTED / ACC-FIND-012 / ISSUE #12 OPEN; RUN-06 NOT AUTHORIZED.**

Runs 01 through 05 retain their historical evidence and verdicts. Run-05 tested
product commit `782e11c8d4defea267510467e41377a2c5aef621` from the correctly
scoped natural mission. Guided intake completed and the live proposal failed
before human review at `schema:actions[1]:unsupported_validation_rule`.
`ACC-FIND-007` through `ACC-FIND-011` remain resolved; the Issue #11 behavior is
live-corroborated rather than reopened. No formal ValidationRun package was
created, Level 1B remains **NOT ACCEPTED**, and run-06 is unconsumed and
unauthorized.

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

### ACC-EXT-003-run-03

Run-03 tested product commit
`c1d0237f12582e4d97a9e57cefe9dc3720d5ff27`. The operator mistakenly entered
application identity as the initial mission and shifted the following bootstrap
answers. The authorized hammer/cheapest-first mission was therefore not supplied
as the authoritative initial request.

Three real Ollama calls completed without timeout:

```text
collection  125.51060649997089 s
review       89.84137620002730 s
review       93.72105690004537 s
total       309.07303960004356 s
timeout     600 s per call
```

The first review asked for product-search/filtering risks. ChatGPT mistakenly
treated it as the earlier expected-outcome question and suggested: "Relevant
hammer products are visible in the catalogue, and the suitable results are
ordered from the lowest to the highest price." The operator supplied that text,
so the confirmed `risk` contains outcome semantics. This disclosed assistance
error and the operator's shifted answers make run-03 unsuitable as a clean live
verdict on Issue #8 or on Ollama question quality.

Guided intake nevertheless reached `complete`; the operator explicitly confirmed
the displayed context. The nominal flow then stopped with:

```text
ValueError: external public single-page creation requires reviewed interaction targets for non-heading outcomes
```

The operator session persisted `aborted` with twelve actions. Browser discovery
did not start, `headed_browser_used` is false, no CreationFlowRun or framework
sandbox was created, and TestCartographer did not contact Toolshop. This
live-corroborates the resolved Issue #9 lifecycle behavior while preserving a new
deterministic product finding at the guided-context/reviewed-target seam.

```text
01-guided-intake-run.json  EB3761988D587919057AAC9C46DF314660A380F602020D61F7F3C41B1CCF7967
01-intake-session.json      AD5DA212A9B2DA3CDA1A8C66FFB5D5B7BFBBAE81AE03D4BADF11EF0686C2D1DB
01-minimal-context.json     E77637BA26EB134B1CF30A0A187FA86CA5FAEC7F48B809AEAC6D91694B20225E
01-minimal-seed.json        70100D18F3B583E835BF9FC6A9FE5A8E4EEA5111860375542042EC7F08705D78
operator-session.json       57049E7E78207BE242E0F7888BD98B3F32F77DDDC9D8AFEC96EDDF326823FD61
supplied evidence ZIP       1F1BA2EF4455EF7E353D368FA082E052E34C14BCB7AAB1F3537C9482E1012F65
```

Run-03 is **NOT ACCEPTED / PRODUCT FINDING**, immutable, and not reusable.

### ACC-EXT-003-run-04

Run-04 tested product commit
`9494ac1d33e4a5f0b76d22eaf7819c2f150c49f6` after a fresh pre-run gate. The
fixed framework baseline remained exact and clean; historical runs 01–03 were
fingerprinted and preserved. No prepared answers or answer-content assistance
were allowed.

The operator naturally supplied a generic search/filter mission rather than the
authorized hammer/cheapest-first mission. Guided intake and material-intent
confirmation completed, but the accepted context consequently contained no
concrete search term, filter, or price-ordering outcome. This operator-scope
caveat means run-04 is not a clean end-to-end retest of the original scenario.
It does not reopen Issue #8 and does not explain the later product-contract
failure.

Three real Ollama calls completed without timeout:

```text
collection       121.35546079999767 s
review            78.44793169997865 s
target proposal   36.08576000004541 s
provider total   235.88915250002173 s
timeout          600 s per call
```

The Issue #10 bridge invoked the target-proposal call and persisted a minimized
proposal artefact. Its JSON parsed, but subsequent contract validation failed
before human review with:

```text
RuntimeError: external interaction-target proposal failed closed:
invalid_target_contract
```

The proposal contains zero targets, no review timestamp, zero operator edits,
and no raw provider response. It exposes no safe field/rule diagnostic and no
bounded repair/retry path, so the exact violated contract cannot be determined
from preserved evidence.

The operator session persisted `aborted` with eleven actions,
`headed_browser_used=false`, `fixture_answers_used=false`, and no CreationFlowRun
ID. Browser discovery did not start, no framework sandbox was created, and
Toolshop was not contacted. This live-corroborates Issue #9 and proves the Issue
#10 bridge is present while exposing the separate ACC-FIND-011 boundary.

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

Run-04 is **NOT ACCEPTED / PRODUCT–PROVIDER INTEGRATION FINDING**, immutable,
and not reusable. The Issue #11 closure was later integrated and run-05 was
consumed through a separate fresh pre-run gate; its evidence is recorded below.

### ACC-EXT-003-run-05

Run-05 tested integrated product commit
`782e11c8d4defea267510467e41377a2c5aef621` after a fresh pre-run gate. The
fixed framework baseline remained exact and clean; historical runs 01–04 were
fingerprinted and preserved. No prepared answers, fixture answers, or
answer-content assistance were allowed.

The natural initial mission explicitly requested public Toolshop catalogue
search for `hammer` and sorting from lowest to highest price. Guided intake and
the material-intent confirmation completed. Three real local Ollama calls
completed without timeout:

```text
collection       123.87875819997862 s
review            89.93903379997937 s
target proposal   53.373939500015695 s
provider total   267.191731499974 s
timeout          600 s per call
```

The target-proposal call persisted a minimized schema-v0.2 artefact. The proposal
then failed deterministic validation before human review:

```text
state: blocked
blocker: invalid_target_contract
category: schema
field path: actions[1]
rule: unsupported_validation_rule
repairable: false
attempt count: 1
accepted targets: 0
raw prompt persisted: false
raw response persisted: false
```

The Issue #11 behavior is a live PASS: the unallowlisted rule remained
non-repairable, so no `RETRY` decision or second target-proposal call occurred.
The operator session persisted `aborted` with eleven actions,
`headed_browser_used=false`, `fixture_answers_used=false`, and no CreationFlowRun
ID. Browser discovery did not start, no framework sandbox was created, and
Toolshop was not contacted.

```text
01-guided-intake-run.json       3F027B5791BB1A7246E05BE5915785F6B4B69BE01582CEAD6BD82E0C9B887A1D
01-intake-session.json          C3E91E2378877B71ED17344C2E84055128B7DE2CAD9D7B1E30EB5EEADB47B7F5
01-minimal-context.json         5EB22BA04412B3C87D8712F362FFEF501C2D004B032476B4B25761FE4FF61B2F
01-minimal-seed.json            126C7CBC16275B42A9FB55229B13A71B7D2E3BD17AC822AE6EFDA4912AFD0FFC
02-interaction-target-proposal.json
                                CD11AB03DAFB764A25FABF58C74BAA3DFC9EDB79E54C31C1862BB99FF069C3DE
operator-session.json           C919C003928CFE7C3A7D7A7EC26474C81AAACCB9D7AA3FBA30953B2715FAA7F8
terminal transcript             27513CDEAF4F771D4C9931A0CB687F14EC73901E4BF1B9AC1F80EE8CFCE86390
```

Run-05 is **NOT ACCEPTED / ACC-FIND-012 / Issue #12**, immutable, and not reusable. The
evidence does not persist the raw proposal value or identify the exact underlying
local validator. It establishes the distinct gap between the provider-facing
schema, local action-conditioned contract, and safe recovery classifier. Run-06
is unconsumed and unauthorized.

## ACC-FIND-012 preservation

The live response reached a deterministic local action rule that the supplied
proposal schema did not prevent and the safe classifier represented only as
`unsupported_validation_rule`. Because that fallback is deliberately
non-repairable, the bounded Issue #11 recovery path could not be reached.

This is not an Issue #11 regression: safe diagnostics, no-raw persistence,
non-repairable fail-closed behavior, and the aborted lifecycle all worked as
designed. It is also not a Toolshop defect and is not sufficient evidence to
replace Ollama. `ACC-FIND-012` / Issue #12 preserves the narrower
product–provider contract representation/classification gap. No remediation is
authorized by this record.

## ACC-FIND-011 deterministic remediation

The invalid-proposal diagnosability and recovery boundary was corrected by
product commit `37d5dac73a26c46b68ab2e2515efe7666de5696e`. The initial
target-proposal prompt and schema remain unchanged. Contract validation failures
now expose only a safe category, field path, and stable rule code, without raw
provider content or input values.

Only allowlisted, deterministically repairable failures enter `awaiting_repair`.
The operator must explicitly choose `RETRY` or `QUIT`; `RETRY` permits exactly
one repair call through the original provider instance. Per-attempt evidence
retains hashes and sizes, latency, validation outcome, and safe diagnostic data.
A valid repair proceeds to the existing human review. A second invalid response
stops blocked/aborted with no third attempt. Invalid JSON, duplicate keys,
locator-like content, and unallowlisted rules remain immediate fail-closed cases.
Browser, target, and framework authority remain unavailable until deterministic
validation and explicit human acceptance both succeed.

Thirty-eight focused and 527 full-suite tests passed. The correction used no
external target, live LLM call, framework sandbox, historical evidence change, or
new run identifier. It resolves `ACC-FIND-011` without changing the run-04 verdict
or accepting Level 1B. The closure is integrated and GitHub Issue #11 is closed.
Run-05 later live-corroborated the non-repairable path and exposed the separate
`ACC-FIND-012` boundary.

## ACC-FIND-010 preservation

The rich same-page engine from Issue #7 accepts human-reviewed action targets,
but the nominal interactive runner calls external-plan construction without
providing `reviewed_targets`. The plan therefore rejects every non-heading
outcome before browser discovery. This is a separate bridge/integration finding,
not evidence that the Issue #7 engine regressed.

No manual JSON injection, selector rescue, or framework edit was used. Historical
run-03 remains immutable.

## ACC-FIND-010 deterministic remediation

The missing interactive bridge was corrected by product commit
`12ce4485a817a5c28bf2d2d8331087ec86b331c0`. Accepted process context now
produces a bounded proposal of two through six same-page actions for explicit
operator inspection, editing, rejection, or acceptance. Only accepted actions
become `reviewed_targets`; invalid or unaccepted plans fail closed before browser
authority exists.

Twenty-seven focused and 516 full-suite tests passed. The correction used no
external target, live LLM call, framework sandbox, historical evidence change, or
new run identifier. It resolves `ACC-FIND-010` without changing the run-03 verdict
or accepting Level 1B. Run-04 later proved that the bridge executed; its separate
invalid-proposal recovery failure is preserved as `ACC-FIND-011`.

## ACC-FIND-007 deterministic remediation

The heading-only capability gap was corrected by product commit
`3b8bb73bd665f8d5389ff2b6a1299c023a97392e`. The external single-page engine
now preserves the legacy heading flow and accepts a reviewed bounded sequence of
same-page `FILL`, `CLICK`, `SELECT`, `CHECK`, `UNCHECK`, and final outcome `READ`
actions with declared owners, semantic roles, and symbolic non-secret test data.

Twenty-five focused and 500 full-suite tests passed. The correction used no
external target, live LLM call, framework sandbox, or new run identifier. It
resolves `ACC-FIND-007` without changing the historical run-02 result. Run-03
confirms that the rich engine exists and historically exposed the separate
interactive bridge later corrected for `ACC-FIND-010` / Issue #10.

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
1B. Run-03 was contaminated by shifted answers and answer assistance. Run-04 had
no such assistance, but its operator-supplied mission omitted the authorized
hammer/cheapest-first intent. Run-05 used the correct natural mission and reached
material-intent confirmation before the separate target-proposal contract stop;
neither later failure reopens the resolved finding.

## ACC-FIND-009 deterministic remediation

The stale-active lifecycle defect was corrected by product commit
`5887f83b5159c8751ef9a5a5638f7dc9afd259ce`. Regression proves that unhandled
runtime failures persist `aborted`, `KeyboardInterrupt` persists `interrupted`,
and supported `QUIT` remains `paused`, while the original exception is re-raised.

Five focused and 492 full-suite tests passed. No external target contact, new
run identifier, live LLM call, framework sandbox, or historical evidence change
was required. Runs 03 through 05 later live-corroborated `aborted` after distinct
unhandled failures; the lifecycle correction still does not accept Level 1B.

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

### Run-03 question-quality result

Run-03 cannot serve as the nominal question-quality retest because the operator
supplied the wrong initial mission and shifted bootstrap answers, and ChatGPT
mistakenly proposed outcome content for the product's risk clarification. The
product then accepted the semantically mismatched confirmed risk.

The evidence still truthfully records three live model calls and their timings,
including two bounded review turns. All completed within the configured timeout;
the process did not hang in Ollama. This run therefore does not justify moving to
a stronger paid provider. It also cannot establish that Ollama would preserve the
correct hammer/cheapest-first mission. The deterministic reviewed-target bridge
failure occurred after intake and remains provider-independent.

### Run-04 question-quality result

Run-04 used no prepared answer sheet or answer-content assistance. The questions
were understandable and stayed at process level, but the operator's initial
mission itself omitted the authorized product term and ordering outcome. The
product accepted a coherent but generic search/filter context without requesting
concrete criteria. Record this as a material run/intake observation; do not open
a second finding until a correctly scoped later run can distinguish operator
scope drift from question-selection behavior.

The third Ollama call produced schema-guided JSON that failed the target
contract. This is the first credible signal that the local model may be part of
the limitation, but the generic product diagnostic and absent bounded recovery
prevent a fair provider-only verdict. No provider switch is justified by run-04
alone.

### Run-05 question-quality and proposal result

Run-05 used no prepared answer sheet or answer-content assistance, and its first
mission correctly included Toolshop, `hammer`, and lowest-to-highest price
ordering. The nine collection questions were understandable and stayed at
process level. The unchanged mission remained authoritative beside the structured
context, and the operator confirmed material-intent coverage.

The third Ollama call again produced a proposal that failed the full local action
contract. This is relevant model-quality evidence. However, the supplied schema
did not prevent the action-conditioned mismatch and the safe classifier could
identify it only as `unsupported_validation_rule`, making bounded recovery
unreachable. Record both sides of the boundary; run-05 alone still does not
justify replacing Ollama.

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
