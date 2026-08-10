# Gaps — current prioritized index

This file lists missing capabilities or missing evidence **after Sprint 16**.

Chronological history belongs in `LEARNINGS.md`.
Current product boundaries belong in `product-scope.md`.
Known limitations belong in `known-limitations.md`.

## Taxonomy

Every open item belongs to one of five categories:

- **CORE** — needed for the intended product architecture before broad
  validation can scale.
- **VALIDATION** — evidence that must be collected from increasingly realistic
  applications; do not close these with more controlled fixtures alone.
- **ENTERPRISE** — capabilities required only when moving into authenticated,
  sensitive, or enterprise targets.
- **PARKED** — potentially useful, but implementation requires validation
  evidence first.
- **OUT-OF-SCOPE** — deliberately not part of TestCartographer's product
  direction.

## CORE gaps

### Gap C-1 — Persistent ProjectProfile and bootstrap invalidation

**Category:** CORE  
**Priority:** P0  
**Status:** CLOSED for the bounded v0.1 slice in Sprint 15  
**Evidence:** real operator + separate disk-backed runs + 394/394 regression

Implemented:

- strict non-secret `ProjectProfile v0.1`,
- local `.test-cartographer/project-profile.json` persistence,
- dedicated `ProjectValue`,
- exact WorkspaceProfile and capability-specific GuidedIntakeProfile ID/hash bindings,
- monotonic accepted revisions and bounded event ledger,
- configuration fingerprint distinct from audit/event history,
- normal ContextBundle bootstrap projection using SYSTEM evidence,
- zero repeated application bootstrap questions on compatible later creation and expansion runs,
- selective `REOBSERVE / RESNAPSHOT / REVIEW_REQUIRED / BLOCKED` compatibility,
- fail-closed fingerprint tamper and binding-drift checks.

Remaining multi-environment/team/authentication/migration questions are tracked
under their actual validation/enterprise gaps rather than keeping C-1 open.

### Gap C-2 — Durable shared application-map reuse

**Category:** CORE  
**Priority:** P1  
**Status:** OPEN, validate before enlarging the model

The current `ContextBundle` remains process-oriented. The project can reuse
accepted facts between controlled flows but does not yet provide a durable
multi-process application graph.

Do not introduce a graph database or large model merely for architectural
symmetry. First validate whether persisted ProjectProfile + existing bundles and
references are insufficient on real multi-process applications.

### Gap C-3 — Safe handoff from verified sandbox to real automation repository

**Category:** CORE / validation-derived  
**Priority:** P1 after external validation exposes the delivery need  
**Status:** OPEN

Current delivery proves reviewed source, preflight, sandbox application, and
execution while preserving the original framework.

A real workflow eventually needs an explicit handoff such as:

```text
verified patch
→ human delivery decision
→ export/apply to working copy or branch
→ normal repository review/PR
```

The exact mechanism should be selected from real project use, not designed
speculatively. Direct unattended writes to a production branch are not a
requirement.

## VALIDATION gaps

### Gap V-1 — External public application validity

**Category:** VALIDATION  
**Status:** OPEN  
**Target:** Sprint 17+

Sprint 16 now provides the repeatable target/run/finding/evidence protocol and controlled rehearsal needed to record this evidence consistently.

Run the existing lifecycle on an application not created for TestCartographer.

The first level should expose ordinary assumptions hidden by controlled
fixtures without adding authentication complexity.

### Gap V-2 — Dynamic and low-control frontend validity

**Category:** VALIDATION  
**Status:** OPEN  
**Target:** Sprint 17–18

Increase difficulty and reduce control over the target:

- script-heavy/dynamic frontend,
- asynchronous states,
- multi-page/component behavior,
- changing structure,
- scraping-resistant or otherwise difficult public frontend.

The important property is not only technical difficulty. TestCartographer must
not be able to "fix the application" to make its own assumptions pass.

### Gap V-3 — Real usability and operational economics

**Category:** VALIDATION  
**Status:** OPEN  
**Target:** collect during validation; decide in Sprint 21

Measure the same target processes across realistic tester workflows, for
example:

```text
testing professional + normal manual automation aids
vs.
testing professional + DevTools/Playwright Codegen + general-purpose LLM
vs.
testing professional + TestCartographer
```

Measure:

- full setup and learning time,
- active operator time,
- correction/review effort,
- time to first runnable test,
- assertion and POM quality,
- unsupported assumptions,
- maintenance effort after change,
- second-process expansion effort,
- subjective difficulty/confidence/willingness to reuse,
- LLM latency and cost where applicable.

The v1 decision depends on quality **and** economics.

### Gap V-4 — Live-LLM semantic value

**Category:** VALIDATION  
**Status:** OPEN

Determine whether live LLM assistance helps the intended testing professional
with:

- question formulation/ordering,
- context interpretation,
- POM boundaries,
- change explanations,
- diagnosis where evidence is sufficient.

Deterministic rules remain product guardrails, not the comparison baseline.

### Gap V-5 — Maintenance beyond controlled locator drift

**Category:** VALIDATION  
**Status:** OPEN

Do not pre-build an exhaustive maintenance taxonomy.

Collect real failures during external validation, then extend only the
capabilities that actual evidence requires.

Potential classes such as timing, state, data, workflow, assertion,
authentication, and environment remain hypotheses until observed.

### Gap V-6 — Real change-impact needs

**Category:** VALIDATION  
**Status:** OPEN

Current change detection does not provide broad impact analysis.

Use real application changes to determine whether impact can be handled through
existing traceability or whether a richer shared graph is justified.

### Gap V-7 — Repeated expansion evidence

**Category:** VALIDATION  
**Status:** OPEN

Repeat expansion across more than one additional process and across genuinely
new application areas.

Measure whether reuse actually reduces repeated questioning, observation,
duplicate code, review work, and model input.

## ENTERPRISE gaps

### Gap E-1 — EnvironmentProfile / AuthProfile / SecretProvider boundary

**Category:** ENTERPRISE  
**Status:** OPEN  
**Target:** Sprint 19 unless earlier validation forces it sooner

Implement the smallest shared lower-level authentication/configuration contract
required by a credentialed target.

Project files should contain secret references, not values.

### Gap E-2 — Credentialed browser lifecycle

**Category:** ENTERPRISE  
**Status:** OPEN

Validate at least one real strategy:

- shared sensitive Playwright storage state,
- declarative login recipe with in-memory secrets,
- interactive human login for SSO/MFA.

Do not implement all strategies before one is required.

### Gap E-3 — Enterprise security and retention

**Category:** ENTERPRISE  
**Status:** OPEN

Before sensitive validation, define and exercise:

- allowed origins/actions,
- data minimization,
- secret policy,
- storage-state handling,
- retention/deletion,
- external-LLM processing authorization,
- account/role restrictions,
- cleanup and repeatability.

### Gap E-4 — Salesforce validation

**Category:** ENTERPRISE / VALIDATION  
**Status:** OPEN  
**Target:** Sprint 20, provisional

Candidate safe flow:

```text
login
→ Accounts
→ create Account
→ save
→ verify
```

Use only an approved non-production environment and account.

## PARKED gaps / ideas

### Gap P-1 — User interface

**Category:** PARKED  
**Status:** POST-v1 EVALUATION

Do not build a GUI merely because the CLI becomes visually complex.

After v1 core value is evaluated, test whether a UI/IDE workflow would
materially reduce:

- cognitive load,
- review friction,
- learning time,
- operator errors.

A GUI must improve a valuable workflow, not hide an inefficient one.

### Gap P-2 — Jira/documentation connectors

**Category:** PARKED

External project artefacts may become evidence sources, but connectors are not
needed to prove the current core product.

### Gap P-3 — Accepted-change history and retrieval

**Category:** PARKED

Potentially valuable for future reuse and retrieval, but premature before
external validation shows which history is useful.

### Gap P-4 — Broader application/impact graph

**Category:** PARKED

Introduce only if repeated external validation demonstrates that existing
traceability cannot express real impact.

### Gap P-5 — Additional LLM providers

**Category:** PARKED

One validated provider boundary is more valuable than many unvalidated
adapters.

### Gap P-6 — PhoenixQA interoperability

**Category:** PARKED

Runtime healing and TestCartographer context/maintenance remain separate until
both boundaries prove a concrete interoperability need.

### Gap P-7 — Visual/multimodal evidence

**Category:** PARKED

Use only where DOM/accessibility evidence is demonstrably insufficient.
Multimodal capture increases cost and privacy exposure.

### Gap P-8 — Team approval workflow

**Category:** PARKED

Collector/domain/automation/security/approver roles may matter in enterprise
use, but current validation remains single-user.

## OUT-OF-SCOPE items

### Gap O-1 — API/SOM adaptation

**Category:** OUT-OF-SCOPE

TestCartographer targets frontend/UI/POM automation. API automation and Service
Object Model adaptation are not part of this product roadmap.

### Gap O-2 — Universal framework/language support

**Category:** OUT-OF-SCOPE

The product is not currently intended to become a universal Selenium/Cypress/
Robot/Playwright-language framework adapter.

### Gap O-3 — Autonomous whole-application crawler

**Category:** OUT-OF-SCOPE

Guided, bounded observation may expand where evidence justifies it. Unrestricted
autonomous application exploration is not a v1 product goal.

### Gap O-4 — Autonomous business truth or defect verdicts

**Category:** OUT-OF-SCOPE

The tool must not claim business correctness or application-defect authority
without trustworthy evidence and the appropriate human/source authority.

## Closed evidence slices

The following gaps are closed only for their deliberately bounded slices:

- Sprint 1 — strict context/evidence contract,
- Sprint 2 — deterministic human intake,
- Sprint 3 — bounded locator observation,
- Sprint 4 — bounded synthesis protocol,
- Sprint 5 — repository-aware adaptation planning,
- Sprint 6 — exact source delivery and first runnable test,
- Sprint 7 — independent execution-evidence handoff,
- Sprint 8 — local-LLM-guided intake,
- Sprint 9 — guided multi-element process discovery,
- Sprint 10 — integrated fixture-assisted Creation Flow,
- Sprint 11 — real-operator Creation Flow,
- Sprint 12 — one reactive locator-maintenance repair,
- Sprint 13 — one proactive mapped-element drift,
- Sprint 14 — one incremental second-process expansion,
- Sprint 15 — persistent project bootstrap reuse and selective invalidation,
- Sprint 16 — repeatable validation evidence protocol and controlled first-finding/rerun rehearsal.

"Closed" never means universally solved. The relevant VALIDATION gap remains
open until external evidence supports generalization.
