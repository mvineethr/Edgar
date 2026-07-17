# Skill: One view layer — every feature lands in views.py first

## When to use
Adding any user-visible data or feature. Also when a dashboard number and
an MCP tool result disagree (they shouldn't be able to — if they do, someone
violated this skill).

## The architecture (memorize the flow)
```
client/market/news/... (data modules, typed objects)
        ↓
views.py  (plain dicts/lists, JSON-ready — THE single source of shape)
   ↓                    ↓
dashboard.py         mcp_server.py
(Flask: thin routes) (FastMCP: thin tools)
   ↓
dashboard.html (single file, vanilla JS — rendering only)
```

## Procedure
1. New feature? Write it as a function in `views.py` that returns plain
   dicts/lists. All service clients come in via the `Services` bundle —
   don't construct clients inside view functions.
2. Raise `LookupError` for "no such manager/ticker". Flask maps it to 404;
   the MCP server maps it to a tool error. Never encode not-found as a
   special dict the caller must string-parse.
3. Then wrap it twice, thinly: a Flask route in `dashboard.py` and (if it
   makes sense for an AI agent) a tool in `mcp_server.py`. Each wrapper
   should be a handful of lines — parse args, call the view, return.
4. UI logic goes in `dashboard.html` only. `dashboard.py` is wiring;
   if you're writing HTML strings or display formatting in Python, stop.
5. Business logic that isn't view-shaped (diffing, aggregation, math) goes
   further down, in its own module (`diff.py`, `indicators.py`, `risk.py`),
   as pure functions with no HTTP — those are the cheapest things in the
   codebase to test.

## Rules I was following
- The reason for the layer is stated in `views.py`'s docstring: "a browser
  user and an AI agent always see the same numbers." Any fix applied in a
  Flask route instead of the view silently leaves the MCP tool (and
  therefore every AI agent) with the old bug.
- Fix data problems at the lowest layer that owns them: units in
  `models.py`, day-change semantics in `market.py`/views — never as a
  display patch in JS.
- Pure-math modules (`indicators.py`, `risk.py`, `diff.py`) take arrays and
  dataclasses, not clients. If a "pure" module wants a client, the design
  is wrong.

## Worked example (this project)
The MCP server grew from 11 to 17 tools in one session (2026-07-06 part 3:
corporate events, Fed calendar, macro snapshot, screener, options chain,
portfolio risk). Each new tool was nearly free because the feature was
built as a view first — `views.security_view`, the macro view, etc. — and
both `dashboard.py` and `mcp_server.py` just wrapped it. When OHLCV history
was added for KLineChart (2026-07-07), the change was: `market.py` grows
`Quote.history_open`, `views.security_view` returns the arrays, and both
frontends got the data with no frontend-specific plumbing. One change,
two consumers, guaranteed agreement.

## Anti-patterns
- A Flask route that calls `EdgarClient` directly. Now the browser has a
  feature the MCP server doesn't, and the next fix lands in one place only.
- Returning model objects from views. Views return JSON-ready primitives so
  both wrappers can serialize without knowing the types.
- Adding an MCP tool with its own data-fetching logic "because it's just a
  small tool." That's a second implementation that will drift.
