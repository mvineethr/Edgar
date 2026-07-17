# Skill: Know the real key before you group, diff, or dedupe

## When to use
Any feature that compares, ranks, joins, merges, or deduplicates rows:
diffs across snapshots, cross-source joins, consensus/overlap logic, feed
merging.

## Procedure
1. Before writing any comparison, answer in writing: what is the TRUE
   identity key of a row in this dataset? (The stable issued identifier —
   not the display name, not a convenience alias.)
2. Check whether one snapshot can contain multiple rows with the same key.
   If yes (very common), the first step of any cross-snapshot operation is
   to AGGREGATE by key within each snapshot. Write that aggregation once
   and reuse it everywhere.
3. Check the opposite trap: rows that LOOK like duplicates but are
   distinct keys (share classes, regional variants, versioned records).
   Two rows can be CORRECT output. Verify the keys before "fixing."
4. When mapping keys across systems, never take the first match from a
   lookup service — results are ordered by the vendor's convenience.
   Define a preference rule (e.g., prefer the primary/home-market
   listing) and normalize notation for the target system.
5. Write one test for the multi-row-same-key case and one asserting that
   distinct-variant rows stay separate.

## Rules
- Aggregation comes BEFORE comparison, always. Diffing unaggregated
  snapshots produces phantom added/removed rows for every internal split.
- `{row.key: row for row in rows}` on raw data silently keeps only the
  last entry per key — the classic understatement bug.
- "Looks like a duplicate" is a hypothesis, not a finding. Check the keys.
  Document confirmed non-duplicates ("two rows here is CORRECT") so a
  future maintainer doesn't 'fix' them.
- Dedupe by key, never by display name — names vary in case, punctuation,
  and suffixes; keys don't.

## Case study
A portfolio-diff feature compared two quarterly filings. The naive design
(dict each filing by security ID, compare) fails twice on real data:
(1) one filer listed the same security across FIVE separate entries in a
single filing — a plain dict keeps only the last, understating the
position; the shipped design sums by ID within each filing first.
(2) The verified diff then showed two companies twice each — which looked
like a dedup bug but was CORRECT: different share classes with genuinely
different identifiers. It was investigated, confirmed, and documented as
correct output. The mapping half bit too: a lookup service returned a
stale delisted ticker as its FIRST result for one security; the fix was a
preference rule for the primary US listing, with a regression test.

## Anti-patterns
- Grouping by name because the key "isn't in the response" (probe again;
  it usually is).
- Collapsing distinct-key rows because a reviewer eyeballed them as dupes.
- Taking `results[0]` from any cross-reference service.
