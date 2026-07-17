# Skill: Test fixtures are copied from reality, never hand-built

## When to use
Every time you write or modify a test that mocks an external response
(SEC, Yahoo, Treasury, OpenFIGI, RSS). Also when a live bug appears in a
path that had green tests — the fixture is a prime suspect.

## Procedure
1. Get a real response: probe the live endpoint (see
   probe-before-building.md) and save the raw body.
2. Trim and anonymize it — remove bulk, keep structure. NEVER retype or
   restructure it. Deleting sibling entries is safe; "cleaning up" the
   nesting or namespaces is how fixtures lie.
3. Put the fixture in the test with a comment naming its source: endpoint,
   date fetched, and what real entity it came from.
4. When a bug is found LIVE that tests missed, do both, always in this
   order:
   a. Fix the fixture to reproduce reality (test should now FAIL).
   b. Fix the code (test goes green).
   If you can't make the old test fail with the corrected fixture, you
   haven't actually captured the bug.
5. Add a regression test named after the failure mode, e.g.
   `test_search_company_cik_parses_html_table`.

## Rules I was following
- A hand-built fixture encodes your *belief* about the API. Your belief and
  your parser come from the same head, so they agree even when both are
  wrong. Only a copied response breaks the loop.
- Fixture realism beats fixture readability. An ugly real XML namespace
  soup that catches bugs is worth ten tidy fake documents.
- Offline tests remain the only kind in `tests/` (all 108 are mocked) —
  the point is not to add network tests, it's to make the mocks truthful.

## Worked example (this project)
The Treasury yield-curve parser (2026-07-06 part 3). Treasury's OData feed
nests values under `<m:properties>` — the *metadata* namespace, not the
data (`d:`) namespace. The parser was written assuming `d:`, and the
hand-built fixture was written from the same assumption. Result: tests
green, live output `{}` — the exact worst case, because nothing looked
broken until the ECO screen rendered empty. The fix followed step 4: the
fixture was replaced with a copy of the real feed (old parser now failed
against it), then the parser was rewritten to match elements by local tag
name, namespace-agnostic. The full 9-point curve verified live (10y 4.48%
on 2026-07-06).

Same pattern earlier: the `output=atom` company-search mock was hand-built
"correct" XML, so it never contained SEC's server-side Perl-array-ref bug
(`ARRAY(0x55d6f0feff88)` as a title). The regression fixture is now a real
anonymized HTML table from the live site.

## Anti-patterns
- Writing the fixture after writing the parser, shaped to make it pass.
- "Fixing" a failing test by editing the fixture toward the code instead of
  checking which one matches the live API.
- Reusing a fixture across endpoints because they "look the same"
  (`recent` vs `files[]` pages: same family, different shapes — two
  fixtures required).
