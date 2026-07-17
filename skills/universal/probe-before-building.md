# Skill: Probe the real API before writing code against it

## When to use
Before writing ANY parser, client, or integration against an external
endpoint — even one you "know," even one that's documented.

## Procedure
1. Before designing, hit the real endpoint once with `curl` (or a 5-line
   script) using the SAME headers/auth production will use.
2. Save the raw response. This capture becomes your test fixture later
   (see fixtures-copy-reality.md).
3. Answer from the response, not from docs or memory:
   - Is it accessible with the auth you planned? (Status code first.)
   - What is the actual nesting? (Print the top two levels of keys.)
   - What are the units and types of the fields you care about?
4. Probe a HARD case, not an easy one: an entity with long history for
   pagination, a foreign/edge-case record for mapping, a multi-variant
   record for key handling. The easy case never exposes the shape problem.
5. Only now write the parser, against the saved payload.

## Rules
- Documentation describes the API the vendor intended; the probe shows the
  API that exists. When they disagree, the probe wins.
- One probe per SHAPE, not per endpoint — paginated pages and "recent"
  blocks from the same API family often have different structures.
- If a probe returns 401/403 where docs say open access, the wall is the
  finding. Redesign around it NOW, not after building.
- A probe is read-only and cheap. It is never slower than fixing a wrong
  parser later.

## Case study
Two from one project. (1) Before implementing pagination over a filings
API, the developer fetched a real long-history filer's data live. The
probe showed paginated pages were FLAT dicts while the "recent" block was
nested one level deeper — a distinction absent from the docs. Guessing
would have produced a parser that worked on recent data and silently
returned nothing for older pages. (2) Before building two new features on
a market-data vendor, the target endpoints were probed and ALL returned
401 anonymously — the vendor had walled them since the docs were written.
That single discovery reshaped the architecture: the auth workaround got
its own module, its consumers were designated "degrade, never crash," and
an unrelated feature was deliberately restricted to the one endpoint that
remained open.

## Anti-patterns
- Writing a parser from an example response in a blog post or from memory.
  Both age; the live API doesn't care.
- Probing with different headers than production uses — behavioral
  differences per header ARE data.
- Probing only the happy path.
