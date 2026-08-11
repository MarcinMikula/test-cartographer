# Sprint 17 Level 1 — target selection

## Status

**AUTHORIZED by operator:** GOV.UK public informational navigation.

Research date: 2026-08-11.

No acceptance execution has started.

## Selection gates

A Level 1 target must satisfy all mandatory gates:

1. application is external to TestCartographer and cannot be modified by the
   project,
2. public access without authentication,
3. bounded read-only process,
4. no destructive or irreversible action,
5. no personal/sensitive data required,
6. no anti-bot or access-policy bypass,
7. selected paths/actions are compatible with published automation/crawling
   policy,
8. process is repeatable enough for a linked retest,
9. conventional enough to isolate basic external-validity assumptions before
   dynamic complexity is added,
10. useful enough to exercise real context/discovery/POM decisions.

## Candidate review

### GOV.UK — SELECTED

Candidate process:

```text
Services and information
→ Driving and transport
→ Driving licences
→ Driving licence codes
→ verify "Driving licence codes" heading
```

Why selected:

- genuine public service website, not an automation sandbox,
- no login is required for the selected informational pages,
- selected process is read-only and non-transactional,
- pages expose conventional link/heading semantics,
- GOV.UK explicitly documents that site scraping is allowed when `robots.txt`
  is respected,
- current `robots.txt` does not block the selected `/browse/...` or
  `/driving-licence-codes` paths.

Important boundary:

GOV.UK `robots.txt` currently disallows `/search/all*`.

Therefore the acceptance process **must not use GOV.UK site search**, even
though search would otherwise be an attractive first scenario.

References checked:

- https://www.gov.uk/help/reuse-govuk-content
- https://www.gov.uk/help/terms-conditions
- https://www.gov.uk/robots.txt
- https://www.gov.uk/browse
- https://www.gov.uk/browse/driving
- https://www.gov.uk/browse/driving/driving-licences
- https://www.gov.uk/driving-licence-codes

### Open Library — REJECTED for Level 1

Functional fit was good: public search, no login, real external application.

Rejected because current official Open Library API guidance says HTML pages
should not be scraped and directs automated consumers to API endpoints instead.
The distinction between low-volume browser testing and scraping is not clear
enough to make this a good first policy-safe acceptance target.

Reference:

- https://openlibrary.org/developers/api

This is a target-suitability decision, not a TestCartographer failure.

### Books to Scrape — REJECTED as primary external-validity evidence

The site explicitly identifies itself as a sandbox/demo for web scraping.

That makes it useful for mechanics but weak evidence for the question:

> Does TestCartographer work on a real application that was not created to
> accommodate automation/scraping?

Reference:

- https://books.toscrape.com/

### Python documentation — RESERVE

Current Python documentation is public, no-auth, current-version paths are not
blocked by its `robots.txt`, and it is a genuine external documentation site.

Its search page requires JavaScript, which makes it more dynamic than necessary
for the first Level 1 scenario. It remains a useful reserve target.

References:

- https://docs.python.org/3/
- https://docs.python.org/3/search.html
- https://docs.python.org/robots.txt

### Wikimedia/Wikipedia — RESERVE, policy/configuration caveat

Wikimedia permits automated access subject to applicable policies, but its
current User-Agent policy expects automated agents to identify themselves and
warns against bot-like behavior using an ordinary browser User-Agent.

That introduces a transport/configuration concern unrelated to the basic Level
1 product question, so it is not the first target.

Reference:

- https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy/en

### Pracuj.pl — CANDIDATE FOR LEVEL 2 ONLY

Current public pages expose search inputs, filtering, sorting, result cards and
dynamic content. This is closer to the intended Sprint 17 Level 2 challenge.

It is not approved yet. Terms/robots/access policy must be reviewed separately
before any automated acceptance run.

## Selected target classification

```text
target: GOV.UK
technical difficulty: simple
control: external_stable
authentication: none
sensitivity: public
destructive action: none
write action: none
expected cleanup: none
```

## Approved path candidate

Pending explicit operator authorization, the target scope is limited to:

```text
https://www.gov.uk/browse
https://www.gov.uk/browse/driving
https://www.gov.uk/browse/driving/driving-licences
https://www.gov.uk/driving-licence-codes
```

Do not:

- use `/search/all`,
- open print variants,
- follow service/login/application flows,
- leave `www.gov.uk`,
- submit forms,
- provide personal data,
- perform transactions,
- crawl unrelated pages.

## Authorization gate

Operator authorization was recorded on 2026-08-11 (Europe/Warsaw).

Accepted: GOV.UK as Level 1 target, the four-page bounded process, and read-only
navigation plus bounded observation. Prohibited boundaries remain unchanged.

Authorization does not start external execution. Environment preflight found
`ACC-FIND-001`, which blocks the nominal Creation Flow before GOV.UK is contacted.
