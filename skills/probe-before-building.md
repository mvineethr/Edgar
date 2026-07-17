# Skill: Probe the real API before writing code against it

## When to use
Before writing ANY parser, client, or integration against an external
endpoint — even one you "know," even one that's documented.

## Procedure
1. Before designing, hit the real endpoint once with `curl` (or a 5-line
   Python snippet) using the same headers production will use
   (`EDGAR_USER_AGENT` for SEC; browser UA for Yahoo).
2. Save the raw response to the scratchpad. This raw capture becomes your
   test fixture later (see fixtures-copy-reality.md).
3. Answer from the response, not from docs or memory:
   - Is it even accessible anonymously? (Status code first.)
   - What is the actual nesting? (Print the top two levels of keys.)
   - What are the units and types of the fields you care about?
4. Pick a *hard case* to probe, not an easy one: a long-history filer for
   pagination, a foreign issuer for ticker mapping, a multi-class company
   for CUSIP handling. The easy case never exposes the shape problem.
5. Only now write the parser, against the saved payload.

## Rules I was following
- Documentation describes the API the vendor intended; the probe shows the
  API that exists. When they disagree, the probe wins.
- One probe per *shape*, not per endpoint: `recent` and `files[]` pages are
  the same endpoint family with different shapes — both needed probing.
- If a probe returns 401/403 where docs say it's open, the wall is the
  finding. Redesign around it now, not after building.
- A probe is read-only and cheap. There is no situation in this project
  where probing first was slower than fixing a wrong parser later.

## Worked example (this project)
Two from the log:

1. **Pagination (2026-06-30).** Before implementing `list_13f_filings`
   pagination, the real submissions JSON for a long-history filer (Icahn,
   CIK 921669) was fetched live. The probe showed `filings.files[]` pages
   are **flat dicts** with the array-of-arrays shape directly, while
   `recent` is nested under `data["filings"]["recent"]`. Docs do not make
   this distinction; guessing would have produced a parser that worked on
   `recent` and silently returned nothing for pages. This is now a
   CLAUDE.md gotcha.

2. **Yahoo's auth wall (2026-07-06 part 3).** Before building events and
   options, the endpoints were probed live: `v7/finance/quote`,
   `v10/quoteSummary`, and `v7/finance/options` all returned 401
   anonymously. That single discovery reshaped the architecture: the
   cookie+crumb workaround became its own module (`yahoo_auth.py`), its
   consumers were put in the "fragile tier" that degrades instead of
   raising, and the screener was deliberately restricted to the still-open
   v8 chart endpoint. Building first and probing later would have meant
   retrofitting the reliability tiers onto finished code.

## Anti-patterns
- Writing a parser from an example response found in a blog post or in your
  own memory. Both age; the live API doesn't care.
- Probing with different headers than production uses (SEC behaves
  differently without a real User-Agent — that difference IS the data).
- Probing the happy path only. Chevron's CUSIP returning stale "CHV" before
  "CVX" was only found because a real portfolio, not a toy symbol, was used.
