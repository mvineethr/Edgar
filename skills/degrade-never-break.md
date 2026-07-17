# Skill: Reliability tiers — decoration degrades, it never breaks the core

## When to use
Any time you add a data source, call an existing one from a new place, or
handle an error. Every value in this system belongs to a tier, and the
tier dictates the error handling. Getting this wrong breaks the product's
core promise for the sake of a nice-to-have.

## The tiers (memorize)
1. **Authoritative — SEC EDGAR** (`client.py`, `fundamentals.py`).
   Failures here MAY raise. The Flask app maps `requests.RequestException`
   to a JSON 502; the CLI shows the error. This data is the product.
2. **Decoration — keyless market data** (`market.py`, `tickers.py`,
   `news.py`, `macro.py` keyless parts). Failures degrade to `None`,
   missing rows, or empty lists. A 13F view with no live prices is still
   a correct 13F view.
3. **Fragile — anything on `yahoo_auth.py`** (`events.py`, `options.py`).
   Yahoo can close the cookie+crumb hole any day, without notice. This
   tier must NEVER raise — not on 401, not on timeout, not on garbage
   JSON. Return `None` / "unavailable" and let the UI show a dash.

## Procedure
1. Before writing a `try/except` (or omitting one), name the tier of the
   data. The module map in CLAUDE.md tells you; `yahoo_auth.py`'s
   docstring restates the rule for tier 3.
2. Tier 2/3 functions return Optionals or empty collections. Their
   callers must render sensibly with those values — check the rendering,
   not just the return.
3. Never let a tier-2/3 failure abort a tier-1 view. If the portfolio
   loads but quotes fail, ship the portfolio with blank price cells.
4. When adding a tier-3 feature, build the "unavailable" rendering FIRST
   and test it by simulating auth failure. If the blank state looks
   broken, fix the UI before wiring real data.
5. Cache rules interact with tiers: never cache a tier-2/3 failure as if
   it were an answer (`cusip_tickers.json` deliberately does not persist
   network failures — a transient outage must not permanently blank a
   ticker).

## Rules I was following
- "SEC data is authoritative; market data is decoration" is a dependency
  rule, not a slogan: no tier-1 code path may have a tier-2/3 call on its
  critical path without a degrade branch.
- An unofficial workaround (cookie+crumb) is a loan, not an asset. Build
  as if it disappears tomorrow, because it has changed before.
- `YahooAuthSession.get()` returns `Optional[Response]` and refreshes the
  crumb exactly once on 401. One retry, then unavailable — no retry loops
  against a wall that isn't coming down this second.

## Worked example (this project)
When probing (2026-07-06 part 3) showed Yahoo had walled v7/quote,
v10/quoteSummary, and v7/options behind cookie+crumb, the response was
architectural, not tactical: `yahoo_auth.py` encapsulates the workaround;
`events.py` and `options.py` were designated fragile-tier with a hard
"degrade, never raise" contract; and the screener was deliberately built
on ONLY the still-open v8 chart endpoint plus SEC data — so the screener
survives even if the crumb trick dies entirely. Meanwhile options was
de-emphasized in the UI (off the F-key bar) precisely because it sits on
the most fragile foundation.

Related tier-1 hardening: SEC resets stale keep-alive connections
(WinError 10054, seen live from the dashboard's long-lived client), so
`_get` retries `ConnectionError` like a 5xx, and the Flask app converts
any surviving `RequestException` into a JSON 502 — because an HTML error
page reaching the widgets shows up as the baffling
"Unexpected token '<'" (see silent-failure-patterns.md).

## Anti-patterns
- A bare `resp.raise_for_status()` in a tier-3 module.
- Catching an exception in tier 2 and returning a fake value (0, "N/A" as
  a price). Missing must be *visibly missing*, never numerically wrong.
- Promoting tier-3 data into a tier-1 screen's critical path because "it
  usually works."
