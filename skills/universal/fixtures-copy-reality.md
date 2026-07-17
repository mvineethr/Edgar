# Skill: Test fixtures are copied from reality, never hand-built

## When to use
Every time you write or modify a test that mocks an external response.
Also whenever a live bug appears in a path that had green tests — the
fixture is a prime suspect.

## Procedure
1. Get a real response: probe the live endpoint and save the raw body.
2. Trim and anonymize it — remove bulk, keep structure. NEVER retype or
   restructure it. Deleting sibling entries is safe; "cleaning up" nesting
   or namespaces is how fixtures lie.
3. Put the fixture in the test with a comment naming its source: endpoint,
   date fetched, what real entity it came from.
4. When a bug is found LIVE that tests missed, do both, in this order:
   a. Fix the FIXTURE to reproduce reality — the test must now FAIL.
   b. Fix the code — the test goes green.
   If you can't make the old test fail with the corrected fixture, you
   haven't captured the bug.
5. Name the regression test after the failure mode
   (`test_search_parses_html_table`, not `test_search_2`).

## Rules
- A hand-built fixture encodes your BELIEF about the API. Your belief and
  your parser come from the same head, so they agree even when both are
  wrong. Only a copied response breaks the loop.
- Fixture realism beats fixture readability. Ugly real namespace soup that
  catches bugs is worth ten tidy fake documents.
- Keeping tests offline is good; the goal is not network tests, it's
  truthful mocks.

## Case study
A government OData feed nested its values under the *metadata* XML
namespace, not the data namespace. A parser was written assuming the data
namespace — and its hand-built fixture was written from the same
assumption. Result: tests green, live output `{}`. The worst case,
because nothing looked broken until a live screen rendered empty. The fix
followed the procedure: fixture replaced with a copy of the real feed
(old parser now failed against it), then the parser rewritten to match by
local tag name. Same project, same lesson earlier: a hand-built mock of a
search API was "correct" XML, so it never contained the server-side bug
(internal object refs rendered as titles) that every real response had.

## Anti-patterns
- Writing the fixture after the parser, shaped to make it pass.
- "Fixing" a failing test by editing the fixture toward the code instead
  of checking which one matches the live API.
- Reusing one fixture across endpoints that "look the same."
