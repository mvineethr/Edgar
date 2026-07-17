# Skill: Sanity-check units and semantics against known truth

## When to use
Any time a number enters or leaves the system: parsing a new field,
displaying a value, computing a delta, percentage, or aggregate.

## Procedure
1. For every numeric field you consume, write down (docstring or comment):
   - **Unit** (dollars? thousands? percent? seconds? bytes?)
   - **As-of semantics** (measured when? relative to what baseline?)
   - **Authority** (which spec, doc, or standard defines it — and whether
     the definition ever changed over time).
2. Find one value whose truth you know independently and check your number
   against it at full precision (an official report, a printed document, a
   trusted second tool).
3. Run the absurdity test: does the magnitude survive comparison with a
   known-huge reference? (A single company's portfolio cannot exceed
   national GDP; a web request cannot take negative time; a percentage of
   a whole cannot exceed 100.)
4. For any "change"/"delta"/"previous" field from a third party, verify
   what the baseline ACTUALLY is before displaying it. Vendor baselines
   are routinely not what the field name implies.
5. When semantics changed over time (spec amendments, API versioning),
   record the cutoff date next to the parsing code AND in the project's
   standing notes.

## Rules
- Field names are claims, not facts. Verify against data, not naming.
- One digit-for-digit external match beats a thousand plausible-looking
  rows. "Plausible" is exactly what a 1000x error looks like when you
  don't know the true total.
- When you fix a unit, RENAME the field so stale assumptions can't
  survive: forcing every call site to be touched is the point.
- Fix units at the model/parsing layer, never at display time — every
  consumer must inherit the fix.

## Case study
A project parsed a regulatory filing's `<value>` field as thousands of
dollars — historically correct, and the variable was even named
`value_usd_thousands`. But a 2023 regulatory amendment had switched the
field to whole dollars. Everything displayed fine and summed fine; the
bug surfaced only via the absurdity test: the reported total,
263,095,703,570, only made sense as $263 billion — read as thousands it
would be $263 trillion, several times US GDP. Same project, second hit: a
chart API's `previousClose` field was the close before the *range start*,
not yesterday — so the "daily change" column was silently showing
month-long drift. Both bugs produced zero errors; only external anchors
caught them.

## Anti-patterns
- Trusting a field name or your own variable name over an external total.
- Checking numbers are merely "in a reasonable range" — anchor to a known
  true value instead.
- Patching the unit conversion in the UI.
