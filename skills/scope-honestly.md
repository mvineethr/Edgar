# Skill: Scope honestly before building

## When to use
Whenever the request is bigger than one module, vaguer than one sentence, or
asks for something a commercial product does ("make it like Bloomberg").

## Procedure
1. Split the request into chunks. For each chunk, classify it as exactly one:
   - **FREE-BUILDABLE**: possible with keyless/free APIs under the hard rules.
   - **OPTIONAL-KEY**: possible only with a free-but-registered key (FRED,
     OpenFIGI). Build it, but it must be optional and everything else must
     work without it.
   - **NOT-REPLICABLE**: requires licensed data, paid APIs, or violates a
     hard rule. Do not build. Say so explicitly in your summary.
   - **DANGEROUS**: introduces a risk class the project doesn't have (e.g.
     server-side execution of user code). Do not build without an explicit
     user decision.
2. If the classification of any chunk depends on user intent, ask ONE
   clarifying question per ambiguity — with concrete options — before coding.
   Do not ask questions whose answer is already in CLAUDE.md.
3. Write the scope decision into your working notes so it lands in
   HANDOVER.md later ("Schwab = not now", "quant scripting = the library
   itself, not server-side code execution").
4. Build the FREE-BUILDABLE chunks in the priority order from CLAUDE.md's
   Next features list unless the user reordered them.

## Rules I was following
- "Exceeding Bloomberg" never means replicating Bloomberg's licensed feeds
  (real-time L2, chat, execution). It means building the classic *screens*
  on free data. State the boundary out loud; users accept it when told.
- A feature that only works with a paid key is worse than no feature — it
  breaks the project's core promise. There is no exception path.
- When the user says "not now" to a chunk (Schwab), record it as *deferred by
  user*, not as impossible — the distinction matters to whoever reads the
  handover next.
- When a request smells like a security hole, reclassify rather than refuse:
  "quant scripting" became "expose the Python library well," which satisfied
  the intent with zero RCE risk.

## Worked example (this project)
Session 2026-07-06 part 3, the ask was: advanced analytics, fixed income, FX,
derivatives, macro, screening, portfolio/risk, corporate events, technical
studies, TradingView, quant scripting, and the Schwab Trader API — in one
message. The scoping pass produced: indicators/risk/screener/macro/events =
FREE-BUILDABLE (built, tests 48→106); FRED = OPTIONAL-KEY (built behind
`FRED_API_KEY`, everything works without it); Schwab = deferred by user;
server-side quant scripting = DANGEROUS, reframed as "the library itself is
the scripting API." One AskUserQuestion round settled all four ambiguities.
Eleven modules shipped and nothing violated a hard rule.

## Anti-patterns
- Building the exciting 20% and silently dropping the rest. Every chunk gets
  an explicit disposition, including "not built, here's why."
- Asking the user to get an API key so your implementation gets easier.
- Treating "options" and "13F holdings" as equally important. SEC data is
  authoritative; market data is decoration. When time is short, the SEC-side
  chunk wins.
