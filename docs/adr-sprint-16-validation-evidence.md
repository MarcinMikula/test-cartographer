# ADR — Sprint 16 validation evidence must preserve the first failure

## Status

Proposed for Sprint 16.

## Context

Once external validation starts, a dangerous workflow would be:

```text
external run fails
→ product is changed immediately
→ rerun passes
→ only passing state is documented
```

That destroys the main reason for external validation.

## Decisions

1. **One product revision per ValidationRun.** A run binds one target/process,
   workflow kind, and product commit. Product behavior change requires a new run.
2. **Finding before remediation.** Persist the observed problem and close the
   evidence package before designing the fix.
3. **Findings record observation, not root-cause verdict.** Initial kinds are
   `failure`, `friction`, `unsupported_assumption`, `safety_stop`,
   `measurement_issue`.
4. **Difficulty and control are separate target axes.**
5. **Evidence packages contain minimized selected artefacts by relative path +
   hash**, not a general archive of raw browser/session/source data.
6. **Operator effort and system wait are measured separately.**
7. **Sprint 16 makes no productivity/savings claim.**
8. **Workflow identity is part of the contract** for later manual/Codegen+LLM/
   TestCartographer comparison.
9. **Prior target familiarity is evidence** because same-operator sequential
   comparisons have learning effects.
10. **Stopping is valid evidence.** The protocol must not reward completion by
    encouraging broader crawling, credential use, destructive activity, or
    unsafe retention.

## Rejected alternatives

- one mutable validation record across product fixes,
- a single PASS/FAIL score,
- screenshots/traces/raw page data by default,
- a benchmark dashboard before trustworthy run evidence,
- automatic LLM root-cause classification during finding capture.
