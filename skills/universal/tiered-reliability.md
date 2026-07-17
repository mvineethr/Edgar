# Skill: Tiered reliability — decoration degrades, it never breaks the core

## When to use
Any time you add a data source, call one from a new place, or write (or
omit) error handling. Every value in a system belongs to a tier, and the
tier dictates the handling.

## Define the tiers for YOUR project (once, in its standing notes)
1. **Authoritative** — the data that IS the product. Failures may raise,
   loudly and structured (map to a JSON error/exit code, never a raw
   traceback or HTML error page reaching a consumer).
2. **Decoration** — enrichment from secondary sources. Failures degrade to
   `None`, missing rows, or empty lists. The core view must remain correct
   and usable without this tier.
3. **Fragile** — anything built on an unofficial workaround, undocumented
   endpoint, or vendor whim. Must NEVER raise — not on auth failure, not
   on timeout, not on garbage. Return "unavailable" and render a dash.

## Procedure
1. Before writing a `try/except` (or omitting one), name the tier of the
   data. If the project hasn't assigned tiers, assign them now and write
   them down.
2. Tier 2/3 functions return Optionals or empty collections; verify their
   CALLERS render sensibly with those values — check the rendering, not
   just the return.
3. Never let a tier-2/3 failure abort a tier-1 view. Core loads, prices
   blank: correct. Core fails because prices failed: bug.
4. For a new tier-3 feature, build the "unavailable" rendering FIRST and
   test it by simulating failure. If the blank state looks broken, fix the
   UI before wiring real data.
5. Never cache a tier-2/3 failure as if it were an answer — a transient
   outage must not become permanent data loss.

## Rules
- "X is authoritative; Y is decoration" is a dependency rule: no tier-1
  code path may have a tier-2/3 call on its critical path without a
  degrade branch.
- An unofficial workaround is a loan, not an asset. Build as if it
  disappears tomorrow.
- On auth failure in tier 3: refresh credentials exactly once, then report
  unavailable. No retry loops against a wall.
- Missing must be VISIBLY missing (blank, dash, "unavailable"), never a
  fake value (0, stale number). Numerically wrong beats absent as the
  worst outcome.

## Case study
A terminal app served regulatory filings (authoritative) enriched with
market quotes (decoration) and vendor analytics that required an
unofficial cookie workaround (fragile). When probing revealed the vendor
had walled three endpoints, the response was architectural: the workaround
got one module with a hard "return None, never raise" contract; its
consumers rendered dashes on failure; and a new screening feature was
deliberately built ONLY on the still-official endpoints so it would
survive the workaround dying entirely. Separately, the authoritative tier
mapped every network exception to a structured JSON 502 — because an HTML
error page reaching a JS widget produces the baffling
"Unexpected token '<'" instead of a diagnosable error.

## Anti-patterns
- A bare `raise_for_status()` in a fragile-tier module.
- Catching an exception and returning a fake value.
- Promoting fragile data into a core screen's critical path because "it
  usually works."
