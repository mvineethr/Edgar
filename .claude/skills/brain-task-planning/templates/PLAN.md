# Plan: <task title>

<!-- Copy this file to your plan location (suggested: .claude/plans/<YYYY-MM-DD>-<slug>.md).
     Fill every section before writing code. Delete these comments when done.
     Sections marked (append-only) grow during execution; never rewrite their history. -->

- **Date started**: <YYYY-MM-DD>
- **Requested by / source**: <user message, issue link, ticket id>

## Goal

<One sentence. What is true when this task is finished that is not true now.>

## Constraints

<!-- Hard limits the solution must respect. Examples: "no new dependencies",
     "must stay backward compatible with v2 API clients", "Windows + Linux". -->
- <constraint 1>
- <constraint 2>

## Non-goals

<!-- Things a reasonable person might assume are in scope but are NOT.
     This is the scope-creep fence — see brain-minimal-change. -->
- <explicitly out of scope 1>
- <explicitly out of scope 2>

## Known risks and unknowns

<!-- One line each: what could sink this plan, and how you'll find out early. -->
- RISK: <what> — probe: <how step N surfaces it early>
- UNKNOWN: <what you don't know yet> — resolved by: <spike / step N>

## Steps

<!-- Each step: small enough to verify independently, ordered riskiest-unknown first.
     Checkpoint = an observable (command output, HTTP status, file diff, UI state)
     that proves the step worked. "Code compiles" is a weak checkpoint; prefer behavior. -->

1. <action>
   - Checkpoint: <command to run> → expect <observable output>
2. <action>
   - Checkpoint: <observable>
3. <action>
   - Checkpoint: <observable>

## Done criteria

<!-- Numeric or observable only. Each one must be checkable by a fresh session
     with no memory of this conversation. Bad: "auth works". Good: "POST /login
     with valid creds returns 200 + Set-Cookie; invalid creds returns 401 (curl
     transcript attached)". Evidence standards live in brain-validation-and-qa. -->
- [ ] <criterion 1: command → expected observable>
- [ ] <criterion 2>
- [ ] Existing test suite still passes: <exact command> → <expected count/exit 0>

## Working log (append-only)

<!-- One line per meaningful action: timestamp, what, observed result.
     Format: "- HH:MM <did X> → <saw Y>". Append; never edit old lines. -->
- <HH:MM> plan written

## Deviations from plan (append-only)

<!-- Filled in only when reality diverges. Each entry: what the plan said,
     what actually happened, what changed in the plan, and why. -->
- <HH:MM> Step <N> assumed <X>; actually <Y>. Revised: <new step text>. Why: <reason>

## Resume state (overwrite freely — keep current)

<!-- The cold-resume block. Keep this accurate enough that a fresh session
     could continue with ONLY this file. Update after every step. -->
- DONE: <steps completed, with checkpoint results>
- VERIFIED: <which done-criteria already proven, and how>
- IN PROGRESS: <current step, exact state — files half-edited, branch name>
- NEXT: <the single next action>
- OPEN QUESTIONS: <anything unresolved that blocks or shapes remaining work>
