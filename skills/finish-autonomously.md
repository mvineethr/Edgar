# Skill: Finishing autonomously when the user says "go ahead"

## When to use
When the user delegates open-endedly ("nothing going through my head, go
ahead and finish", "use your judgment", "close it out"). This is a grant of
sequencing authority, not a grant of scope authority. The discipline is
knowing which decisions you now own and which you still don't.

## Procedure
1. Build the worklist from the record, not from imagination:
   - "Open" items from the top HANDOVER.md entry.
   - "Next features" from CLAUDE.md, in the listed priority order.
   - Anything marked "known-untested" that can now be tested.
2. For each item, do the full loop before moving on: implement → offline
   tests → live verification → record. Don't batch five half-done items;
   hand back fewer items in a fully-verified state.
3. Sequencing rule: verification and hardening of EXISTING promises come
   before new features. If something shipped-but-never-live-verified
   exists, that's item #1 — it's a latent broken promise.
4. Decisions you own under delegation: order of work, implementation
   approach, test coverage, refactors needed to do the work cleanly.
5. Decisions you still do NOT own: scope changes (adding a feature not on
   the roadmap), anything touching a hard rule, spending the user's money
   or identity (signing up for keys), removing user-visible functionality,
   and reviving anything the user explicitly deferred ("Schwab = not
   now" stays not-now until THEY reopen it).
6. Hand back a clean state: all tests green, live checks recorded, and a
   HANDOVER entry precise enough to resume cold (see
   write-the-handover.md). "Finish" means the next session starts easy.

## Rules I was following
- Delegation raises the bar for verification, not lowers it. With nobody
  watching over your shoulder, live verification is the only reviewer in
  the room — so it runs on everything (the 2026-06-30 session's first act
  under "go ahead and finish" was to live-verify the never-verified SEC
  path, which immediately found the atom-search bug).
- When an open item is bigger than expected, shrink the batch, not the
  quality. One verified feature beats three "done pending testing."
- If genuinely blocked on a user-only input (an API key, a paid decision),
  route around it: mark it untested, pick the next item, and surface the
  blocker in the handover — don't stall and don't fake it.

## Worked example (this project)
Session 2026-06-30: the instruction was literally "nothing going through
my head, go ahead and finish." The execution order chosen: (1) verify the
live SEC path for the first time ever — found and fixed the atom-search
bug plus regression test; (2) close CLAUDE.md's three explicitly-open
hardening items (retry/backoff, pagination — probed live against Icahn
first, Q/Q diff — the roadmap's #1 "actually interesting feature");
(3) grow tests 4 → 11; (4) write the handover, including a precise recipe
for the one item left open (pre-2013 SGML filings). Note what was NOT
done: no new scope invented, the throttle explicitly left alone per the
hard rule, and the untestable item documented rather than hand-waved.
That's the shape of a good autonomous finish.

## Anti-patterns
- Treating "use your judgment" as "build what seems cool." The roadmap
  order IS the user's standing judgment; yours fills the gaps.
- Ending the delegated session with a question you could have answered by
  probing, testing, or reading the record.
- Declaring done at green tests. Under delegation especially, done =
  verified live + recorded (see verify-live-before-done.md).
