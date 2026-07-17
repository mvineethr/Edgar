# Skill: Never guess an identifier — verify every ID, symbol, and URL live

## When to use
Hardcoding anything that names an external thing: entity IDs, tickers/
symbols, feed URLs, CDN paths, API hosts, preset lists. Identifiers LOOK
guessable — that's the trap. A wrong one either fails silently or, worse,
returns someone ELSE's data under a trustworthy label.

## Procedure
1. For every identifier you're about to hardcode, do one live round-trip
   BEFORE committing it, and confirm the response is the entity you meant
   (not just that something came back).
2. When a lookup returns multiple candidates (names are messy), pick by
   BEHAVIOR, not by name similarity: the candidate whose data matches
   what you're integrating (e.g., the entity that actually files the
   document type you need) is the right one.
3. When mapping identifiers across systems, apply a preference rule
   instead of taking the first result, and normalize notation for the
   consumer (`BRK/B` vs `BRK-B` style differences are everywhere).
4. URLs: `curl -I` the exact URL and require a 200 with plausible
   content-length before writing any integration code.
5. Write the verification into the commit/notes ("verified via <command>
   on <date>") so nobody re-verifies — or worse, un-verifies — later.

## Rules
- If your system degrades gracefully (blanks instead of errors — see
  tiered-reliability.md), the runtime will NEVER call out your typo.
  Graceful degradation makes live pre-verification mandatory.
- Verify at ADD time, once; stable identifiers are then trusted forever.
  The cost is one command; the failure is a user trusting wrong data.
- Memory and docs give you the FORMAT of an identifier; only a live
  round-trip gives you the VALUE. This applies doubly to anything an LLM
  (including you) recalls from training.
- An identifier with no valid mapping should render visibly absent, never
  with a guessed substitute.

## Case study
A project mapped security identifiers to tickers through a real lookup
API — no guessing anywhere — and STILL shipped a wrong row: the service
returned a stale, delisted ticker as its first result for one company, so
that row silently rendered without a price (graceful degradation hid it).
It was caught only by eyeballing a real portfolio row by row during live
verification. The standing rule that came out of it: every entity added
to the project's preset list must be resolved via the project's own live
search command first — stated in the docs as "verify each ID before
adding; never guess." A related entity with NO valid mapping in the free
tier renders blank by design — honest absence beats a plausible guess.

## Anti-patterns
- Adding five well-known entities to a preset list from memory in one
  commit. Each unverified ID is a wrong-data bug wearing a famous name.
- "Fixing" a blank row by trying symbol variants until something renders.
  Verify which is CORRECT, not which returns data.
- Copying identifiers from blog posts or model memory.
