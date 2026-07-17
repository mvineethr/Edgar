# Skill: Good-citizen HTTP — throttles, identity, and retry discipline

## When to use
Any change that adds, moves, or "optimizes" a call to someone else's
service — especially free/public APIs, where politeness is the only thing
keeping access open.

## Procedure
1. Centralize: route every request to a given service through ONE helper
   that owns the throttle, retry, and identity headers. Never create a
   side-channel request — it silently bypasses all three.
2. Identify yourself honestly if the service asks for it (real User-Agent
   with contact info where required). Enforce it in the client
   constructor so it can't be forgotten.
3. Set a self-throttle at or below the service's stated/soft limit, as a
   constant with a comment naming the source of the number. Treat it as a
   hard rule: it is never the performance knob.
4. When a feature needs N requests, reduce N — in this order: cache
   immutable data, batch where the API supports it, consolidate duplicate
   fetches, then accept the latency. If first-run is slow, make it a
   one-time cost with a cache and SAY it's slow.
5. Retry only what can succeed on retry: 429, 5xx, and transport-level
   ConnectionError (long-lived sessions get their keep-alive sockets
   recycled). Cap retries (~3), back off exponentially, honor
   `Retry-After`. Other 4xx raise immediately — a 404 is still a 404 on
   attempt three.

## Rules
- Rate limits on free services are good-citizen behavior, not technical
  ceilings. The endpoint would accept faster traffic today and block your
  users tomorrow.
- Latency is a UX problem with UX solutions (caching, messaging,
  precomputation) — never a justification for shaving a throttle.
- Throttle and retry are different defenses: throttle stops you being the
  problem; retry survives the upstream having one. Keep both.
- Parallelism around a politeness limit is just a complicated way to
  violate it.

## Case study
A screening feature needed a multi-megabyte fundamentals document per
symbol from a free government API, across a ~45-symbol universe. The
first implementation fetched each document TWICE (two consumers, two
fetches). The pre-release fix: one fetch shared by both consumers, plus a
per-symbol-per-day disk cache — volume halved, then mostly eliminated,
throttle untouched. Elsewhere in the same project, first-time loads took
~20 seconds because a keyless enrichment service allowed 5 lookups per
3 seconds; the accepted fix was a permanent cache making later loads
instant — not a faster hammer.

## Anti-patterns
- "Tests are slow, lower the throttle." Offline tests never hit the
  throttle — if they seem to, something is making real network calls from
  tests, and THAT is the bug.
- Retrying 404s or auth failures.
- Generic User-Agents on services that require identification — the block
  lands on your users, not on you.
