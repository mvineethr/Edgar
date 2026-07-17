# <one-line symptom, stated as observed — not as diagnosis>

- **Date**: YYYY-MM-DD
- **Status**: settled | open | superseded by <path or entry title>

## Symptom

One or two sentences: what was observed, where, and under what conditions.
Include the exact error text if there was one — future sessions will search
for it verbatim.

## Root cause (mechanism)

One sentence stating the MECHANISM, not the remedy. "Upgrading X fixed it" is
not a root cause; "X < 2.3 truncated multi-byte keys at the 255-byte boundary,
corrupting cache lookups for non-ASCII IDs" is.

## Evidence

Commands actually run and what they showed. Cite commit SHAs, issue/PR
numbers, and log excerpts — enough that a skeptic can re-verify.

```
<command>
<relevant output excerpt>
```

## Fix

What changed and where. Commit ref(s): `<sha>` / PR #NNN.

## Wrong paths tried

Half the value of this entry. For each dead end: what was tried, and WHY it
failed or was rejected. This is what stops the next session from re-walking
the same road.

- Tried <approach>: failed because <reason>.
- Tried <approach>: worked but rejected in review because <reason>.
