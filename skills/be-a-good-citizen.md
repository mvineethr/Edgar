# Skill: Good-citizen HTTP — throttles, identity, and retry discipline

## When to use
Any change that adds, moves, or "optimizes" an HTTP call. This project's
entire data supply is free public endpoints; the only thing keeping them
usable is that we don't abuse them.

## The standing numbers (do not change without a written reason)
- SEC: ~10 req/s soft cap → fixed-interval throttle of 0.12s in
  `client.py::_get` (`_MIN_INTERVAL_SECONDS`).
- Yahoo: 0.25s between requests.
- OpenFIGI keyless: batches of 5, one batch per 3s.
- Retries: max 3, exponential backoff (1s base, doubling), honor
  `Retry-After` when present. 429 and 5xx retry; other 4xx raise
  immediately — a 404 will still be a 404 on attempt three.

## Procedure
1. Route every SEC request through `EdgarClient._get`. Never create a
   side-channel `requests.get` to SEC — it bypasses throttle, retry, and
   the User-Agent.
2. Never weaken the `EdgarClient` constructor's User-Agent validation
   (must contain "@"). SEC requires a name + contact email; anonymous or
   generic UAs get blocked, and the block hits the user, not you.
3. When a feature needs N requests, reduce N before touching the
   throttle. Order of preference: cache (immutable data), batch (OpenFIGI
   takes 5 per call), consolidate (one fetch reused), then accept the
   latency. The throttle itself is never the knob.
4. If a first-run operation is slow because of a throttle, make it a
   one-time cost with a disk cache and SAY it's slow ("~1 min first run"),
   rather than speeding it up by hammering.
5. Retry only what can succeed on retry: 429, 5xx, and transport-level
   `ConnectionError` (SEC resets stale keep-alive sockets — WinError
   10054 — and a fresh connection almost always works).

## Rules I was following
- These limits are good-citizen behavior, not technical ceilings. The
  endpoints would accept faster traffic today and then rate-limit or ban
  the project's users tomorrow. CLAUDE.md lists "keep every self-throttle"
  as a hard rule for that reason.
- Latency is a UX problem with UX solutions (caching, progress messaging,
  precomputation). It is never a justification for shaving a throttle.
- Retry-after-backoff and self-throttle are different defenses: the
  throttle prevents us being the problem; the retry survives the upstream
  having a problem. Keep both; neither substitutes for the other.

## Worked example (this project)
The screener (2026-07-06 part 3) needed SEC XBRL companyfacts per symbol —
multi-megabyte responses across a ~45-name universe. The first
implementation fetched companyfacts TWICE per symbol (once for metrics,
once for shares outstanding). The fix before first release was
consolidation: ONE fetch per symbol, both consumers reading from it, plus
a per-ticker-per-day disk cache (`screener_cache.json`). Total request
volume halved and then mostly eliminated on repeat runs — throttle
untouched.

Same philosophy on the portfolio path: first load of a manager takes ~20s
because OpenFIGI keyless allows 5 CUSIPs per 3s. The accepted solution is
the forever-cache (`cusip_tickers.json`) making every later load instant —
not a faster hammer on OpenFIGI.

## Anti-patterns
- "The tests are slow, let me lower `_MIN_INTERVAL_SECONDS`." Tests are
  offline; the throttle never affects them. If it seems to, something is
  making real network calls from tests — that's the bug.
- Retrying 404s or auth failures. Wasted requests against an answer that
  won't change.
- Adding a parallel fetch pool over a throttled client. Parallelism around
  a politeness limit is just a complicated way to violate it.
