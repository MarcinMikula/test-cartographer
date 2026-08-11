# ACC-FIND-002 — Multi-page discovery is outside current implemented capability

## Status

**OPEN LIMITATION — GitHub Issue #2.**

## Origin

Discovered during pre-remediation analysis of ACC-FIND-001.

No external TestCartographer execution had started.

## Observation

`ProcessDiscoveryPlan v0.1` models one `page_id` and one `source_url`.
`apply_accepted_discovery()` materializes one discovered page and places the
resulting steps on that page.

The original ACC-EXT-001 four-page GOV.UK navigation therefore requires a new
multi-page discovery capability rather than a small external-target correction.

## Decision

Do not implement multi-page discovery inside the first external-validity fix.

Preserve ACC-EXT-001 as blocked and use ACC-EXT-002 as the smallest single-page
Level 1 scenario.

## Tracking

```text
GitHub Issue: #2
external target verdict: none
product change in this slice: none
```
