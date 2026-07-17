# Skill: Scope honestly before building

## When to use
Whenever the request is bigger than one module, vaguer than one sentence,
or asks to replicate a commercial product ("make it like X").

## Procedure
1. Split the request into chunks. Classify each as exactly one:
   - **BUILDABLE**: possible within the project's hard constraints
     (budget, licenses, keyless-ness, privacy — whatever they are).
   - **CONDITIONAL**: possible only with something optional (a free key,
     a user account). Build it, but gated: everything else must work
     without it.
   - **NOT-REPLICABLE**: requires licensed data, paid services, or
     violates a hard rule. Do not build. Say so explicitly.
   - **DANGEROUS**: introduces a risk class the project doesn't have
     (arbitrary code execution, storing credentials, PII). Do not build
     without an explicit user decision — and first try to REFRAME it
     into a safe equivalent that satisfies the intent.
2. If any chunk's classification depends on user intent, ask ONE
   clarifying question per ambiguity, with concrete options, before
   coding. Never ask questions the project docs already answer.
3. Record every disposition — including "not built, here's why" and
   "deferred by user" — where the next session will see it.
4. Build BUILDABLE chunks in the project's stated priority order unless
   the user reordered them. When time is short, the chunk closest to the
   project's core data wins over decoration.

## Rules
- "Make it like <commercial product>" never means replicating its
  licensed parts. It means building the equivalent EXPERIENCE on data
  you're allowed to use. State the boundary out loud; users accept it
  when told.
- A feature that only works with a forbidden dependency is worse than no
  feature — it breaks the project's promise.
- "Deferred by user" and "impossible" are different records. The next
  maintainer treats them differently; label them correctly.
- Reframing beats refusing: find the safe formulation that satisfies the
  actual intent.

## Case study
One request asked, in a single message, for: advanced analytics, four
new asset classes, screening, portfolio risk, corporate events, a
third-party charting integration, "quant scripting," and a brokerage
API. The scoping pass produced: analytics/screening/risk/events =
BUILDABLE (shipped, tests 48→106); one data source = CONDITIONAL (built
behind an optional free key, all screens complete without it);
brokerage = deferred by the user ("not now"), recorded as such; and
"quant scripting" — which as literally stated meant server-side
execution of user code, an RCE risk — was reframed as "expose the
Python library well," satisfying the intent with zero new risk. One
clarifying-question round settled all ambiguities; eleven modules
shipped; no hard rule bent.

## Anti-patterns
- Building the exciting 20% and silently dropping the rest.
- Asking the user to procure something so your implementation gets
  easier.
- Treating all chunks as equal priority when the project's docs already
  rank core data above decoration.
