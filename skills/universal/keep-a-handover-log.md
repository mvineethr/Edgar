# Skill: Close every session by writing the handover

## When to use
At the end of every working session, and immediately after any live-found
bug (write it down while the pain is fresh). Continuity lives in two
files with different jobs:
- **Session log** (HANDOVER.md or similar) — the narrative: what happened
  this session and why. Newest entry first.
- **Standing brief** (CLAUDE.md or similar) — what is ALWAYS true. Only
  durable facts graduate here.
If the project has neither, create them; it pays back within two sessions.

## Procedure — the session-close checklist
1. Run the test suite one last time; note the count (track it over time:
   "tests 106 → 108").
2. Prepend a session-log entry with exactly these sections:
   - **What was asked** — the request, including scope decisions and who
     made them ("X = not now" — user's call, not yours).
   - **Decisions** — non-obvious choices WITH the reason, especially
     rejected alternatives.
   - **Changes** — per-module, one line each.
   - **Verified live** — dated, with actual commands and the ACTUAL
     VALUES observed. Values, so a future session can re-run and compare.
   - **Open** — unfinished/untested/deferred items with enough context to
     pick up cold, ideally naming the first command to run.
3. Update the standing brief only where standing truth changed:
   - New live-found bug → one line in the gotcha list, phrased as trap +
     rule.
   - Feature shipped and verified → status section.
   - Priorities changed → roadmap.
4. Anything built but NOT verified live gets flagged as UNTESTED in both
   files. Never let it pass silently as done.
5. Record correct-but-surprising output explicitly ("two rows here is
   CORRECT because ...") so a future maintainer doesn't 'fix' it.

## Rules
- Write for someone with NO memory of the session — which is literally
  the next session's reality (yours included).
- Gotchas earn their place by cost: real, paid-for lessons only. Don't
  dilute with hypotheticals; don't omit anything that burned an hour.
- "Verified live" entries must be falsifiable: date + command + observed
  value. "It works" cannot be re-checked; "9-point curve on 2026-07-06,
  10y at 4.48%" can.
- Session narrative in the brief, or standing rules only in the log, are
  both failures: wrong file = invisible at the moment it's needed.

## Case study
One project's log entry recorded: the exact delegation received, each
work item with its reasoning (including why an API was probed against a
specific hard case before coding), a live-found bug with its regression
test's name, the test count delta, the exact commands run with the
config used, and an Open section precise enough that a months-later
session could resume an untested edge case cold — it even specified the
verification recipe ("find an old record via <command>, fetch it live,
confirm the error message is useful, not a raw traceback"). Every
subsequent session was measurably faster because of entries like it —
and the project's entire gotcha list, the most valuable file in the
repo, was built one entry at a time this way.

## Anti-patterns
- Writing the handover from memory a day later — the numbers and dead
  ends are gone.
- An Open section that says "polish remaining."
- Recording what changed but not WHY the rejected alternative was
  rejected (the next person will re-try it).
