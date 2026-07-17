# Skill: Finishing autonomously when the user says "go ahead"

## When to use
When the user delegates open-endedly ("use your judgment," "go ahead and
finish," "close it out"). This grants SEQUENCING authority, not SCOPE
authority. The discipline is knowing which decisions you now own.

## Procedure
1. Build the worklist from the record, not from imagination:
   - Open items from the newest session-log entry.
   - The roadmap, in its listed priority order.
   - Anything marked "untested" that can now be tested.
2. For each item, complete the full loop before moving on: implement →
   offline tests → live verification → record. Fewer items fully
   verified beats many items half-done.
3. Sequencing rule: verifying and hardening EXISTING promises comes
   before new features. Anything shipped-but-never-verified is item #1 —
   it's a latent broken promise.
4. Decisions you own: order of work, implementation approach, test
   coverage, refactors required to do the work cleanly.
5. Decisions you still do NOT own: scope additions beyond the roadmap,
   anything touching a hard rule, spending the user's money or identity
   (creating accounts, signing up for keys), removing user-visible
   functionality, and reviving anything the user explicitly deferred —
   "not now" stays not-now until THEY reopen it.
6. Hand back a clean state: tests green, live checks recorded, and a log
   entry precise enough to resume cold.

## Rules
- Delegation RAISES the verification bar. With nobody watching, live
  verification is the only reviewer in the room — run it on everything.
- When an item is bigger than expected, shrink the batch, not the
  quality.
- If blocked on a user-only input (a credential, a purchase decision),
  route around it: mark the item untested, take the next item, surface
  the blocker in the handover. Don't stall; don't fake it.
- Never end a delegated session with a question you could have answered
  by probing, testing, or reading the record.

## Case study
Told literally "nothing going through my head, go ahead and finish," one
session chose this order: (1) live-verify the never-verified core API
path FIRST — which immediately found a real upstream parsing bug, fixed
with a regression test; (2) close the three explicitly-open hardening
items from the brief, probing a real hard case before writing the
pagination code; (3) build the roadmap's #1 feature; (4) grow tests
4 → 11 and write a handover including a precise recipe for the one item
left open. Note what was NOT done: no invented scope, a
performance-tempting rate limit left untouched per the hard rules, and
the untestable item documented rather than hand-waved. That is the shape
of a good autonomous finish.

## Anti-patterns
- Treating "use your judgment" as "build what seems cool." The roadmap
  IS the user's standing judgment; yours fills the gaps.
- Declaring done at green tests (see verify-in-reality.md).
- Batching five features to 80% instead of two to verified-done.
