# Skill: Cache policy follows the data's mutability — and never cache failure

## When to use
Adding any cache, choosing a key or TTL, or debugging stale/missing data.
Every cache decision derives from ONE question: when, if ever, can this
data change?

## Procedure
1. Classify the data:
   - **Immutable** (filed documents, content-addressed blobs, tagged
     releases): key by the immutable ID, cache forever.
   - **Slow-moving** (fundamentals, configs, directory listings): cache
     with a TTL derived from how often it CAN change (per day, per hour) —
     not from vibes.
   - **Live** (quotes, statuses, feeds): don't disk-cache at all.
   - **User-owned** (preferences, watchlists, layouts): store client-side
     or per-user; it's not server data.
2. Pick the key so a NEW version of the data gets a NEW key (the
   document's own permanent ID, not "latest for X" — the latter goes
   stale; the former can't).
3. Never write a failure into the cache. A network error must leave NO
   entry, so the next run retries. Caching a failure converts a transient
   outage into permanent data loss.
4. If you need negative caching, distinguish "known-absent" (a verified
   fact — cacheable) from "failed-to-fetch" (an accident — never
   cacheable).
5. After adding a cache, verify BOTH paths live: cold (correct, slower)
   and warm (same data, fast). A cache that never hits and one that
   serves stale garbage look identical in offline tests.

## Rules
- "Forever" is only legal when the KEY embeds immutability. Cache the
  content of an immutable object forever; never cache the answer to a
  mutable query forever.
- The cache exists to protect rate limits and the user's time, in that
  order. If a cache would ever serve wrong data to save a request, the
  TTL is wrong.
- A slow first run + fast subsequent runs (with the slowness stated
  honestly) beats hammering the upstream to speed up run one.

## Case study
A portfolio loader's first run took ~20 seconds: fetch a filing (rate-
limited), then resolve ~29 identifiers through a keyless service capped
at 5 lookups per 3 seconds. Both results were disk-cached — the filing
under its accession number (filings are immutable once filed → forever),
the identifier map keyed by the stable ID (listings effectively never
change → forever). Second load: instant, verified live. The one
deliberate hole: identifiers whose resolution FAILED are absent from the
cache and retried next run, while one entity that is genuinely
unmappable in the free tier simply renders blank each time — honest
absence, not a cached lie. A third cache (multi-MB fundamentals) got a
per-symbol-per-day TTL because "today" is exactly how fresh screening
needs to be.

## Anti-patterns
- Caching by mutable reference ("latest for X") instead of immutable ID.
- TTLs chosen by vibes ("an hour seems fine").
- Testing the cache only with mocks — the cold/warm check is two runs of
  one command; do it.
