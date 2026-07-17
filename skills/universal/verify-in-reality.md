# Skill: Verify in reality before calling anything done

## When to use
Before saying "done," "fixed," or "working" about ANY change. No exceptions.

## Procedure
1. Run the project's offline test suite first. Green tests are the entry
   ticket, not the finish line.
2. Exercise the changed path against the REAL system it targets:
   - API/CLI code: run the actual command against the live service.
   - Web UI: load the real page in a browser AND curl the underlying
     endpoint; check both layers.
   - Library code: call it from a real consumer, not just imports.
3. Compare at least one output value against an INDEPENDENT source you
   trust (official document, a second tool, the user's own screenshot).
   Match the digits, not just the order of magnitude.
4. Exercise the change the way a user would, not just the way the code
   runs: click through the flow, run the command twice (cold and warm),
   stack the feature to its limits.
5. Record what you verified: the command, the observed values, the date.
6. If live verification is impossible right now (needs a credential, needs
   specific timing), explicitly record the feature as UNTESTED. Never let
   it silently pass as done.

## Rules
- Mocks agree with the code by construction; only reality disagrees. A
  green offline suite proves internal consistency, nothing more.
- "Verified" means a specific artifact: a value you saw, matched against a
  value from elsewhere. "It loaded without errors" is not verification.
- Verify at the outermost layer that changed. A working API under a broken
  UI is still broken.
- The independent source must be truly independent. Cross-checking your
  own other endpoint proves nothing — both can share the bug.

## Case study
A financial-data project ran its very first live command after being built
entirely against mocks. That one command revealed the upstream API's
search feed was broken server-side (returning stringified internal object
references as titles). Four offline tests had been green the whole time,
because the mock data was hand-built "correctly." In the same project, a
chart replacement passed all 108 offline tests; live verification then
compared the last rendered price bar against the user's screenshot from a
different tool — digit-for-digit — before it was called done. Live checks
caught a real bug in essentially every working session of that project.

## Anti-patterns
- "Tests pass, shipping it."
- Verifying with the same fixture the code was written against.
- Declaring victory on the happy path only.
