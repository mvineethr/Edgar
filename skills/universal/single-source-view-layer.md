# Skill: One shared view layer — every frontend wraps the same functions

## When to use
Any project with more than one consumer of the same data (web UI + CLI,
web + API, human UI + AI/MCP tools). Also when two frontends disagree
about a number — they shouldn't be able to; if they do, someone violated
this skill.

## The pattern
```
data modules (typed objects, one per source/domain)
        ↓
view layer (plain dicts/lists, serialization-ready —
            THE single source of output shape)
   ↓              ↓             ↓
frontend A    frontend B    frontend C
(each a thin wrapper: parse args → call view → return)
```

## Procedure
1. New user-visible feature? Write it as a view-layer function returning
   plain, serialization-ready primitives. Inject service clients (pass
   them in via a bundle); don't construct them inside view functions.
2. Signal "not found" with one conventional exception (e.g.
   `LookupError`). Each frontend maps it mechanically (404, tool error,
   exit code). Never encode not-found as a special dict callers must
   string-parse.
3. Wrap the view thinly in each frontend. A wrapper longer than ~10 lines
   is doing view work in the wrong layer.
4. Rendering/display logic lives only in the frontend. Business logic
   that isn't view-shaped (math, diffing, aggregation) lives BELOW the
   views as pure functions with no I/O — the cheapest code to test.
5. Fix data problems at the lowest layer that owns them: units in the
   model, semantics in the data module, shape in the view — never as a
   display patch.

## Rules
- The reason for the layer: every consumer sees THE SAME numbers. A fix
  applied in one frontend's route silently leaves every other consumer
  (including AI agents) with the old bug.
- If a "pure" module wants an HTTP client, the design is wrong.
- The view layer is also your cheapest integration point: exposing a
  feature to a new frontend (an MCP tool, a CLI command) should cost a
  handful of wrapper lines.

## Case study
A dashboard project served both a browser UI and an MCP tool server for
AI agents. Because every feature landed as a shared view function first,
the tool server grew from 11 to 17 tools in one session at near-zero
cost — each new tool was a thin wrapper over an existing view. When chart
history needed richer data, the change was: data module grows a field,
view returns it, and BOTH frontends had it with no frontend-specific
plumbing. The docstring of the view module states the contract: "a
browser user and an AI agent always see the same numbers."

## Anti-patterns
- A web route calling a data client directly — now one frontend has a
  feature (and eventually a fix) the others don't.
- Returning model objects from views, forcing each frontend to know the
  types.
- A "small" tool with its own fetching logic. That's a second
  implementation that WILL drift.
