# ACC-EXT-001 — Create automation for bounded GOV.UK navigation

## Status

**AUTHORIZED — execution blocked by ACC-FIND-001 during preflight.**

## Objective

Determine whether the existing human-triggered TestCartographer Creation Flow
can create and execute maintainable automation for one simple external public
navigation process without fixture-specific rescue, unsafe evidence capture, or
implicit mutation of the original automation repository.

## Linked acceptance requirements

Primary coverage:

```text
ACC-REQ-001  start from bounded operator intent
ACC-REQ-003  preserve uncertainty
ACC-REQ-004  preserve authority/provenance
ACC-REQ-005  bounded browser discovery
ACC-REQ-006  human authority
ACC-REQ-007  bounded LLM authority
ACC-REQ-008  reviewable automation design
ACC-REQ-009  independent execution
ACC-REQ-012  evidence integrity
ACC-REQ-013  operator effort/friction
ACC-REQ-014  no automatic target-defect verdict
ACC-REQ-015  safe stop
ACC-REQ-016  nominal workflow without internal state surgery
ACC-REQ-017  protect original automation repository
```

Conditional coverage if a material finding/correction occurs:

```text
ACC-REQ-010  preserve finding before remediation
ACC-REQ-011  linked retest after justified correction
```

Not a primary objective of this first new-project run:

```text
ACC-REQ-002  cross-run/project bootstrap reuse
```

`ACC-REQ-002` should receive stronger coverage during a later same-application
second process or repeat Creation Flow.

## Risk addressed

Controlled fixtures may have hidden assumptions about:

- page/element semantics,
- discovery target shapes,
- navigation steps,
- locator conventions,
- POM placement,
- initial project/profile setup,
- operator workflow,
- source delivery.

A simple external process should expose basic assumptions without conflating
them with authentication or highly dynamic frontend behavior.

## Target

Application:

```text
GOV.UK
```

Classification:

```text
difficulty: simple
control: external_stable
authentication: none
sensitivity: public
```

Start URL:

```text
https://www.gov.uk/browse
```

Allowed process URLs:

```text
https://www.gov.uk/browse
https://www.gov.uk/browse/driving
https://www.gov.uk/browse/driving/driving-licences
https://www.gov.uk/driving-licence-codes
```

## Process intent supplied to TestCartographer

The operator intent should be semantically equivalent to:

> Automate a public GOV.UK navigation flow that starts from Services and
> information, opens Driving and transport, then Driving licences, then Driving
> licence codes, and verifies the final page heading is "Driving licence codes".

Do not provide locators, DOM details, Page Object names, or hidden implementation
hints in the initial request.

## Business/process context the operator may authoritatively provide

Reasonable human facts:

```text
application: GOV.UK
environment: public website
purpose: verify the documented navigation path reaches driving licence codes
risk: navigation/content structure drift could prevent a user reaching the
      intended informational page
role: unauthenticated public visitor
precondition: GOV.UK public informational pages are available
expected outcome: final page presents the "Driving licence codes" heading
```

The operator should not claim facts that have not been observed or that belong
to TestCartographer/application technical evidence.

## Preconditions

Before execution:

- clean TestCartographer Git state,
- exact pre-execution commit recorded,
- product version recorded,
- current 469-test regression baseline known from Sprint 16 closure,
- Acceptance Test Plan/Requirements/STLC baseline committed,
- this test case committed,
- target selection explicitly authorized by operator,
- GOV.UK robots/policy boundary rechecked if materially changed,
- a clean isolated acceptance project/output area chosen,
- previous controlled-catalog ProjectProfile/state not silently reused as if it
  belonged to GOV.UK,
- original `qa-automation-framework` repository path identified and protected
  from implicit writes,
- local Ollama/provider requirements for the nominal Creation Flow satisfied if
  the documented flow requires them.

## Critical pre-execution observation: profile preparation

The current public CLI exposes:

```text
test-cartographer creation interactive
  --profile <path>
  --output-dir <path>
  [--framework-root ...]
  ...
```

Before the run, determine the **documented supported way** to obtain the profile
for a new external project.

Do not manually construct an internal profile JSON merely to make ACC-EXT-001
start unless manual profile authoring is explicitly the supported operator
workflow.

If no supported preparation path exists, record the condition before adding a
test-only workaround. This is relevant to `ACC-REQ-016`.

## Test actions

1. Confirm/record the exact TestCartographer Git commit.
2. Create or select a clean isolated acceptance output/project state using only
   supported interfaces.
3. Start the nominal human-triggered Creation Flow.
4. Provide only the bounded process intent and legitimate human context.
5. Authorize only the selected `www.gov.uk` process.
6. Allow TestCartographer to perform its intended bounded discovery.
7. Resolve only genuine human-review/ambiguity questions.
8. Review logical POM proposal.
9. Review framework adaptation placement.
10. Review generated source patch exactly.
11. Confirm any application step writes only to the allowed sandbox/copy.
12. Trigger framework execution when the reviewed workflow reaches that gate.
13. Verify normal test execution does not require TestCartographer/live LLM.
14. Build/verify the Sprint 16 validation evidence package for the run.
15. Record operator difficulty, confidence, willingness to reuse, and observed
    out-of-band intervention.

If the workflow cannot reach a later step, stop there, preserve the evidence,
and triage. Do not skip ahead manually.

## Expected product behavior / acceptance oracle

### PASS evidence for reached stages

The product should:

- start from operator intent without a complete handcrafted ContextBundle,
- keep unknown technical facts explicit until evidence/review resolves them,
- stay within the four approved pages/actions,
- not use GOV.UK search,
- not navigate into login/transaction/service flows,
- not capture broad raw page content by default,
- preserve source authority and human decisions,
- propose a reviewable POM/component/action structure,
- not require the operator to author locators or internal state as rescue,
- generate source that corresponds to the approved process,
- keep the original framework repository unchanged,
- execute accepted automation independently in its allowed sandbox/copy,
- verify the final page heading semantically as "Driving licence codes",
- produce independently verifiable acceptance evidence.

### Acceptance concerns even if pytest passes

Record a finding if a green test required:

- manual internal JSON repair,
- manual locator injection outside intended review,
- direct editing of generated TestCartographer state,
- hidden fixture substitution,
- broad capture contrary to policy,
- unsafe or out-of-scope navigation,
- poor/wrong Page Object placement,
- materially wrong assertion semantics,
- unreviewed write to original framework,
- unsupported business/application assumptions.

## Stop conditions

Stop rather than rescue if continuing requires:

- leaving approved `www.gov.uk` scope,
- using `/search/all`,
- authentication,
- form/transaction submission,
- personal/sensitive data,
- destructive actions,
- policy/robots bypass,
- unrestricted crawling,
- manual TestCartographer source edit during the same run,
- evidence retention outside accepted policy.

## Postconditions

- no target-side data mutation,
- no account/session created,
- no cleanup expected on GOV.UK,
- original automation repository unchanged unless a future separately accepted
  handoff mechanism is explicitly invoked,
- all acceptance evidence kept in the local validation-artifact area.

## Result

Not executed yet.

The first execution result must reference:

```text
ValidationRun ID:
product commit:
evidence package fingerprint:
operator assessment:
findings:
GitHub Issues:
```
