# Skill: Sanity-check units and semantics against known truth

## When to use
Any time a number enters or leaves the system: parsing a new field,
displaying a value, computing a percentage or change. Financial data is
where this project's two most embarrassing bugs lived.

## Procedure
1. For every numeric field you consume, write down (in the docstring or a
   comment) three things: **unit** (dollars? thousands? percent?),
   **as-of semantics** (close of when? relative to what?), and **the
   authority** (which spec or amendment defines it).
2. Find one value whose truth you know independently, and check your
   number against it at full precision:
   - Portfolio totals → the total the filer itself reports in the filing.
   - Fundamentals → the printed 10-K (Apple FY2024 revenue is $391.0B).
   - Prices/changes → a second source the user trusts.
3. Run the absurdity test on magnitude: if Berkshire's portfolio reads
   $263 *trillion*, the number is wrong no matter what the field name
   says. US GDP is ~$29T; no 13F total exceeds low hundreds of billions.
4. For any "change" or "delta" field from a third party, verify what the
   baseline actually is before displaying it. Vendors' baselines are
   routinely not what the name implies.
5. When semantics changed over time (regulatory amendments), record the
   cutoff date next to the parsing code AND in CLAUDE.md's gotchas.

## Rules I was following
- Field names are claims, not facts. `chartPreviousClose` is not
  yesterday's close; `<value>` labeled by decades of habit as thousands is
  whole dollars since Jan 2023.
- One digit-for-digit external match beats a thousand plausible-looking
  rows. Plausible is exactly what a 1000x error in a large portfolio looks
  like when you don't know the true total.
- When a unit fix lands, rename the field so stale assumptions can't
  survive silently: `value_usd_thousands` → `value_usd` forced every call
  site to be reviewed.

## Worked example (this project)
The 13F units bug (2026-07-06 part 1). The `<value>` field was parsed as
thousands of dollars — historically correct, and the field was even named
`value_usd_thousands`. But SEC's January 2023 amendment switched filers to
whole dollars. The tell was step 3: Berkshire's reported total,
263,095,703,570, only makes sense as $263B — read as thousands it would be
$263 *trillion*, several times US GDP. Everything displayed fine and
summed fine; only the external sanity check caught it. Fix: rename to
`value_usd` everywhere, fix labels, and document in the `Holding`
docstring that PRE-2023 filings genuinely did use thousands (so old
filings read 1000x LOW — the gotcha cuts both ways).

Second instance, same session family: Yahoo's `chartPreviousClose` is the
close before the *range start*, so "day change" was actually range drift —
AAPL showed "+10.18%" which was a 5-day move. Fix: with daily bars, use
the second-to-last bar as previous close, and display CHG (1D) and
CHG (RANGE) as explicitly distinct rows.

## Anti-patterns
- Trusting a field name or your own variable name over an external total.
- Sanity-checking only that numbers are "in a reasonable range." $263B and
  $263T are both "big numbers" if you don't anchor to a known truth.
- Fixing the unit at display time. Fix it at the model (`models.py`) so
  every consumer — CLI, dashboard, MCP — inherits the fix.
