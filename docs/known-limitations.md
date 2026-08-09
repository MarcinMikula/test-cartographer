# Known limitations — current-state index

This file describes what is **true now** after Sprint 14 and Checkpoint 14.5.
Chronological history belongs in `LEARNINGS.md`; implementation gaps belong in
`gaps.md`.

Do not append obsolete sprint-era statements here. When a limitation closes,
replace or remove it so this document remains a current-state map.

## Current evidence boundary

The current Windows closure baseline is:

```text
339 tests passed
Search before expansion: PASS
Search after expansion: PASS
Sort after expansion: PASS
```

The repository has controlled executable evidence for creation, independent
framework execution, reactive maintenance, proactive regression, and
incremental expansion.

However:

- the application targets are still controlled local reference applications,
- no external public application has completed the full validation lifecycle,
- no authenticated/enterprise application has completed it,
- no productivity or usability advantage has been demonstrated.

## CORE limitations

### No persistent cross-run ProjectProfile

Bootstrap/project knowledge can be reused inside controlled flows, but there is
no durable project profile with versioning, provenance, review, and selective
invalidation.

The product cannot yet reliably answer across separate runs:

- which application/environment/framework facts remain current,
- which bootstrap questions must not be repeated,
- which configuration change invalidates which accepted knowledge,
- whether provider/model/authentication/policy changes require review.

This is the highest-priority missing core capability.

### Application-map persistence remains process-oriented

`ContextBundle` version `0.1` is still centered on one process. Sprint 14 proves
reuse between an accepted Search context and a candidate Sort context, but it
does not yet provide a persistent whole-project graph of multiple processes,
pages, components, tests, and accepted changes.

A larger graph must not be introduced until real validation demonstrates that
the simpler representation is insufficient.

### Real repository handoff is not implemented

Accepted source changes are applied only to fresh snapshot-bounded sandboxes.

The product does not yet provide a production-project delivery workflow such as:

- export/apply patch,
- explicit working-copy application,
- branch creation,
- pull-request handoff.

Direct unattended writes to a production branch are not planned as a default.

## VALIDATION limitations

### External validity is intentionally open

No simple public, dynamic public, low-control public, credentialed, or
enterprise application has yet completed the end-to-end lifecycle.

Controlled fixtures prove mechanisms, not generality.

### Usability and economics are unproven

The project records selected interaction and active-time metrics, but there is
no controlled baseline for:

- setup time,
- learning effort,
- correction effort,
- total operator time,
- perceived difficulty,
- confidence/trust,
- willingness to reuse,
- time to first runnable test,
- maintenance effort,
- second-process expansion effort.

Fewer questions are not automatically better, and more automation is not
automatically more efficient.

### LLM semantic value is narrow and unproven

A local Ollama path is implemented for bounded interview/ambiguity phrasing.
Critical synthesis and source-generation acceptance remains heavily
deterministic/replay-driven.

The project has not demonstrated across external applications that a live LLM:

- proposes consistently maintainable POM boundaries,
- reduces human effort,
- improves context interpretation,
- diagnoses real failures safely.

The relevant comparison is between testing-professional workflows, not between
TestCartographer and an expert application developer.

### Maintenance generalization is deliberately unimplemented

Reactive maintenance currently proves one controlled locator drift.

Proactive regression currently proves one bounded mapped-element locator drift.

The product does not yet generalize to timing, state, data, authentication,
workflow, assertion, environment, or multi-file failure classes.

These should be discovered from real validation failures rather than invented
laboratorily in advance.

### Impact analysis is not implemented

The product can detect bounded changes but cannot yet calculate reliable
transitive impact across shared components, processes, Page Objects, fixtures,
tests, and context knowledge.

Whether a graph model is needed remains an empirical question.

### Expansion evidence is one controlled second process

Sprint 14 proves that reuse occurred for Search → Sort.

It does not prove:

- repeated expansion across many processes,
- reuse across genuinely new application areas,
- lower effort/cost than alternatives,
- authenticated expansion,
- enterprise-scale conflict handling.

## ENTERPRISE limitations

### No shared production authentication profile

`EnvironmentProfile`, `AuthProfile`, and `SecretProvider` contracts are design
directions, not implemented product boundaries.

There is no supported:

- shared storage-state lifecycle,
- declarative login recipe,
- secret-manager integration,
- session expiry/refresh,
- role verification,
- account rotation.

### SSO/MFA remains a policy-constrained boundary

Some enterprise flows may require headed interactive login. The product must
support this possibility rather than assuming every login is automatable.

### Security controls are incomplete

Current minimization and sensitivity metadata are not a complete enterprise
security system.

Still missing or unvalidated:

- external-processing authorization,
- robust secret detection,
- retention/deletion policies,
- access control,
- encryption at rest,
- prompt-injection handling,
- malicious DOM/document handling,
- enterprise audit requirements.

### No Salesforce acceptance

Salesforce remains a deliberate later validation target.

No production/confidential Salesforce system should be used without an approved
non-production environment, account policy, authentication strategy, data
policy, allowed-action policy, cleanup strategy, and external-LLM boundary.

## PLATFORM limitations

- The package is experimental and not published as a supported product release.
- Development and acceptance are local-first; no project CI pipeline is the
  source of truth.
- Python + Playwright + pytest is the only supported implementation stack.
- Dependencies are version-ranged rather than locked into a supported-platform
  matrix.
- The CLI is single-user and local; identity/authorization of reviewers is not
  verified.
- There is no team approval workflow.
- Schema migration/version-upgrade workflows remain minimal.
- Concurrent editing and merge of local project state are unsupported.

## PARKED, not current requirements

The following may be reconsidered only after core validation demonstrates a
need:

- web/desktop/IDE review interfaces,
- Jira and documentation connectors,
- accepted-change history/retrieval,
- broader change-impact graph,
- additional live LLM providers,
- PhoenixQA interoperability,
- visual/multimodal context,
- team review roles,
- domain packs,
- richer test-design assistance,
- economics dashboards.

## Explicitly OUT OF SCOPE

For TestCartographer v1 and current product direction:

- API automation / Service Object Model adaptation,
- a general multi-language/multi-framework automation platform,
- unrestricted autonomous whole-application crawling,
- autonomous business-truth authority,
- automatic application-defect verdicts from failed tests,
- a general-purpose software-development coding assistant.

## Human limits that are intentional

Not every human dependency should be automated away.

A human or authoritative external source remains necessary when the system lacks
evidence for:

- business rules,
- risk,
- expected business outcomes,
- intended user role,
- ambiguity between equally plausible UI meanings,
- authorization to access sensitive systems,
- final acceptance of high-impact changes.

`REVIEW`, `BLOCKED`, `UNKNOWN`, and insufficient evidence are legitimate
outcomes, not failures of ambition.
