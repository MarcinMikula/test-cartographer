# Sprint 17 Level 1 external validation report

## Executive summary

Sprint 17 Level 1 was the first product-acceptance exercise in which
TestCartographer was required to work against a real external application that
was not built for the project.

The goal was deliberately narrow. We did not try to prove that
TestCartographer can automate a complete website, handle arbitrary dynamic
interfaces, or replace a tester.

We wanted to answer a more fundamental question:

> Can TestCartographer take legitimate human testing intent, discover the
> required UI evidence on a real public page, turn that evidence into reviewable
> automation changes, apply them only to an isolated framework sandbox, and
> independently execute the generated test without hidden fixture-specific
> rescue?

Within the bounded Level 1 scope, the accepted answer is **yes**.

The passing scenario was `ACC-EXT-002`, executed as
`ACC-EXT-002-run-04` against the public GOV.UK Driving licence codes page.
The generated framework test was collected and executed independently and
finished `1/1 PASS`. The original automation framework remained unchanged. A
formal immutable evidence package was then built from the accepted run and
independently verified.

The result matters because the path to that PASS exposed several real product
problems. Those problems were recorded as findings before remediation instead
of being hidden behind manual workarounds.

For future roadmap discussions, this completed Level 1 may be referred to as
**Level 1A** only to distinguish it from the planned **Level 1B analyst-rich
validation**. Historical acceptance records retain the original `Level 1`
name.

## The short version

A reader who does not know the earlier sprints can understand the accepted flow
as:

```text
tester describes what should be checked and why
-> TestCartographer asks for missing process context
-> human confirms the business meaning
-> TestCartographer opens the authorized real page
-> browser discovery finds the required visible UI target
-> human reviews the discovered target
-> TestCartographer proposes POM/adaptation/source changes
-> human reviews each authority boundary
-> accepted changes are applied only to a framework sandbox
-> the generated Playwright test runs independently
-> 1/1 test passes
-> selected immutable evidence is packaged and verified independently
```

The operator did not provide the locator, Page Object class name, DOM selector,
or hidden implementation repair needed to force a pass.

## Why this validation was necessary

Before Sprint 17, TestCartographer had demonstrated many individual boundaries
in controlled conditions:

- deterministic and LLM-assisted intake,
- explicit human authority transitions,
- bounded browser observation and discovery,
- POM proposal and adaptation planning,
- exact patch review,
- sandbox-only source application,
- independent pytest execution,
- reactive maintenance,
- proactive regression,
- second-process expansion,
- persistent project bootstrap,
- immutable validation evidence packaging.

Those were important engineering proofs, but they did not yet answer the
external-validity question.

A system can be internally consistent and still depend on assumptions that hold
only in its own fixtures.

Sprint 17 therefore changed the system-under-test boundary:

```text
before
TestCartographer
-> controlled project fixtures
-> controlled browser targets
-> known reference automation shapes

Level 1
TestCartographer
-> external public application
-> real browser discovery
-> no target-specific fixture rescue
-> original framework protected from writes
```

## What we originally intended to test

The initial Level 1 scenario was `ACC-EXT-001`, a four-page GOV.UK navigation:

```text
/browse
-> /browse/driving
-> /browse/driving/driving-licences
-> /driving-licence-codes
```

Pre-execution analysis found that the current discovery contract models one
page/source URL at a time.

That was not treated as a reason to quietly simplify the historical test.
Instead:

```text
ACC-EXT-001
-> preserved
-> blocked by ACC-FIND-002 / Issue #2
-> multi-page discovery remains an explicit product limitation
```

A new independent scenario, `ACC-EXT-002`, was designed to test the smallest
external workflow that the product could legitimately support without
speculative multi-page implementation.

This distinction is important: the successful one-page scenario did not replace
or retroactively pass the original four-page scenario.

## Accepted Level 1 scenario

Target:

```text
application: GOV.UK
URL: https://www.gov.uk/driving-licence-codes
authentication: none
sensitivity: public
technical difficulty: simple
```

Operator intent:

```text
Automate opening the public GOV.UK Driving licence codes page and verify that
the page shows the heading "Driving licence codes".
```

The operator supplied legitimate testing context such as:

- application and process meaning,
- process purpose,
- user/business risk,
- role,
- precondition,
- expected observable outcome.

The operator did **not** supply a locator, Page Object class name, DOM selector,
or hidden implementation instruction.

The product therefore had to obtain the required browser evidence itself.

## What TestCartographer did

The accepted run followed the supported Creation Flow:

```text
human intent
-> guided intake
-> explicit confirmation
-> bounded external browser discovery
-> deterministic target selection
-> human discovery review
-> synthesis handoff
-> POM proposal review
-> adaptation-plan review
-> exact source-patch review
-> sandbox-only patch application
-> independent framework execution
-> creation evaluation
```

Browser discovery recorded 16 bounded candidates.

The required native heading was selected as:

```text
role: heading
name: Driving licence codes
selection: deterministic
```

The accepted evidence did not require raw page HTML, screenshots, generic
page-text dumps, input values, raw prompts, or raw provider responses.

## What automation was produced

The accepted patch created a page object and a test around the observed heading
and extended the framework fixture layer needed for external target execution.

The generated solution was intentionally componentless because the observed
process did not justify inventing a reusable UI component merely to satisfy an
older fixture convention.

Independent execution recorded:

```text
tests collected: 1
tests passed: 1
meaningful assertion: true
independent framework execution: true
original framework unchanged: true
component required: false
component generated: false
```

This matters because the success criterion was not "TestCartographer says the
patch looks valid". The generated test had to run with the framework itself.

## What failed before the accepted run

The most valuable part of Level 1 was not the final green test. It was the set
of incorrect assumptions uncovered on the way there.

### ACC-FIND-001 - controlled catalog fixture binding

The nominal interactive Creation Flow was still coupled to the internal catalog
reference scenario.

```text
classification: product limitation / acceptance blocker
result: resolved
```

The product could not honestly start the external scenario through its supported
interface. The finding was preserved before remediation.

### ACC-FIND-002 - multi-page discovery unsupported

The original four-page scenario exceeded the implemented single-page discovery
contract.

```text
classification: open product limitation
result: still open
```

Passing `ACC-EXT-002` does not claim multi-page support.

### ACC-FIND-003 - single-target discovery run rejected

After external single-page support was introduced, the runtime model still
required at least two discovery targets even though the accepted plan could
legitimately contain one.

```text
classification: product bug
result: resolved
```

The contract was corrected and retested.

### ACC-FIND-004 - componentless creation evaluation rejected

The external process did not require a reusable component, but the final
evaluation model still treated component generation as universally mandatory.

```text
classification: product bug
result: resolved
```

The evaluation contract was changed to preserve a fail-closed default while
allowing explicitly justified componentless creation.

### ACC-FIND-005 - destructive output collision

A later acceptance attempt exposed a more serious lifecycle bug: if the chosen
run output directory already existed, the runner attempted to remove it before
starting.

```text
classification: product bug / acceptance-evidence integrity concern
result: resolved
```

The consumed run identifier was not reused. Startup was changed to fail closed
when an output directory already exists, preserving historical material and
requiring a new run ID.

### ACC-FIND-006 - live LLM call metric mismatch

The successful run later exposed a measurement problem: browser-discovery
reported an LLM call from configured provider mode even though no discovery
guidance turn had occurred.

```text
classification: measurement issue
functional impact: non-blocking
result: resolved
```

The functional PASS remained immutable. The metric was corrected
deterministically and covered by regression tests without rewriting run-04.

## The accepted functional run

The first completed external scenario was:

```text
acceptance test: ACC-EXT-002
run: ACC-EXT-002-run-04
tested product commit: bd6595ab89c5c4c2d1e6317ee372bfaa9a74462f
creation flow: PASS
tests collected / passed: 1 / 1
```

Recorded process characteristics included:

```text
real operator actions: 17
live LLM calls: 1
discovery candidates: 16
selected discovery targets: 1
full traceability: true
measured savings claimed: false
```

Operator assessment:

```text
difficulty: hard
confidence in result: high
would reuse workflow: yes
prior target familiarity: automated_before
```

Timing is interpreted conservatively. The run recorded
prompt-to-response/operator-response elapsed time, not proven continuous human
active work. No time-savings or productivity claim is made.

## Functional run versus final accepted repository state

The external functional run and the final repository closure are deliberately
distinguished.

```text
external functional run-04 tested product commit:
bd6595ab89c5c4c2d1e6317ee372bfaa9a74462f

post-run deterministic measurement correction:
ab4f3f5e873f0849a2d418a9a0c6cf7ff8279839

Level 1 closure integrated to main:
c467c1fc63041078be0c1aad98e4dd42e9336287

full local regression on the closure tree:
490 passed
```

No new GOV.UK run was required for `ACC-FIND-006` because that correction changed
deterministic measurement aggregation, not browser selection, generated
automation, acceptance logic, or the already completed functional behavior.

This prevents two different claims from being conflated:

- what exact product state performed the real external run;
- what exact repository state became the accepted post-remediation baseline.

## Independent evidence package

After the functional run, a formal validation package was built from selected
immutable evidence outside the Git repository.

Key package identity:

```text
ValidationRun id: acc_ext_002_run_04

validation run fingerprint:
281c0eac510eacb98eeda16c3e5bae96c0c2cf87bc2c1739be9d4360bfcf7c96

target fingerprint:
85691211bcbde45eb885309a6518875392f084409a6d3a4b4db33a277dd875c0

package fingerprint:
2d297736725ee99363b1e37e69b7972fa284af8ada2083325849537b2ab69381

manifest entries: 7
independent verification: PASS
run-04 source evidence changed by packaging: false
```

The package intentionally contains minimized selected evidence rather than a raw
browser dump.

Historical failed attempts and finding/retest relationships remain in acceptance
records rather than being fabricated into contract fields that did not exist at
the time of those earlier attempts.

## What Level 1 proves

Within its bounded scope, Level 1 provides evidence that TestCartographer can:

1. start from legitimate operator intent rather than a prepared catalog fixture;
2. keep the human authoritative for business context and review decisions;
3. use a live local LLM only inside its bounded intake role;
4. discover the required UI target on a real external public page;
5. keep browser evidence minimized;
6. distinguish deterministic discovery from LLM-guided work;
7. produce reviewable POM, adaptation, and source artefacts;
8. avoid inventing an unnecessary component when evidence does not justify one;
9. apply accepted source changes only to an isolated framework sandbox;
10. execute the generated test independently of TestCartographer and the live
    LLM;
11. preserve failed/incomplete runs and findings instead of rewriting history;
12. package selected run evidence deterministically and verify it fail-closed.

This is the first external evidence that the nominal Creation Flow can cross the
controlled-fixture boundary and produce working automation for a real
application.

## What Level 1 does not prove

The result is intentionally narrow.

It does **not** prove:

- multi-page discovery,
- automation of a complete application,
- dynamic or heavily scripted frontend robustness,
- stateful/write workflows,
- authentication, SSO, or MFA handling,
- arbitrary enterprise SPA behavior,
- full application crawling,
- correct behavior with a large or messy business process,
- that every stop condition works,
- that project-bootstrap reuse is established by this particular run,
- that the current operator interaction model is optimal,
- productivity or time savings.

`ACC-EXT-001` remains blocked by the open multi-page limitation.

## Why the result is useful despite the limitations

Level 1 was intentionally small enough that failures could be attributed more
confidently to TestCartographer rather than to a highly complex target.

That strategy worked.

The external scenario exposed assumptions that controlled internal fixtures had
hidden:

- the Creation Flow was still catalog-specific,
- one-target discovery and evaluation contracts were overly rigid,
- component generation was accidentally universal,
- output lifecycle behavior could destroy historical run material,
- one metric represented configuration rather than actual runtime behavior.

Those are product lessons, not target-site defects.

The accepted run therefore provides more than a demo. It provides a concrete
external-validity checkpoint and a trustworthy baseline for harder validation.

## Next validation direction

The next step should not automatically be "make the website harder".

From this point we distinguish two partially independent dimensions:

```text
technical complexity
and
analytical/process complexity
```

### Planned Level 1B - analyst-rich validation

Level 1B will keep the target reasonably safe and public but give the operator
more freedom to behave like a real analyst/tester rather than following a
perfectly prepared short script.

Practice Software Testing is the current preferred target family, but it is not
authorized by this report. It requires separate target review, scope, test
design, and explicit authorization before execution.

The purpose is to see how TestCartographer reacts when the operator:

- provides richer business intent,
- mixes risk, assumptions, expectations, and context,
- is incomplete or imprecise in legitimate ways,
- creates genuine ambiguity,
- does not supply implementation hints,
- expects the product to decide what must be clarified and what can be reused.

No product change is authorized before that evidence exists.

If later evidence shows that TestCartographer handles a "chaotic
tester/analyst" poorly, GUI or selected structured-choice fields may be
considered only as post-v1.0 UX hypotheses. They are not part of the current
v1.0 acceptance scope.

### Planned Level 2 - dynamic/script-heavy validation

Pracuj.pl remains one Level 2 candidate because it represents a materially
richer scripted frontend.

Level 2 should not rely on one website. The current direction is to validate
against Pracuj.pl plus two additional dynamic public applications, preferably
from different functional domains.

Each target requires separate scope, policy/robots review, authorization, and
test design.

## Related acceptance records

Detailed sources of truth:

```text
acceptance/test-cases/ACC-EXT-001.md
acceptance/test-cases/ACC-EXT-002.md
acceptance/findings/ACC-FIND-001.md
acceptance/findings/ACC-FIND-002.md
acceptance/findings/ACC-FIND-003.md
acceptance/findings/ACC-FIND-004.md
acceptance/findings/ACC-FIND-005.md
acceptance/findings/ACC-FIND-006.md
acceptance/campaigns/sprint-17-external-validation-I/traceability.md
```

The immutable run and verified package remain outside the Git repository under
the local validation artefact area.
