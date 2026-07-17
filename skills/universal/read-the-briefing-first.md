# Skill: Read the project's briefing before touching anything

## When to use
At the start of every session, before your first edit, and before
answering "how does X work" about the repo.

## Procedure
1. Read the project's standing brief (CLAUDE.md / CONTRIBUTING / docs
   README — whatever the repo uses) completely. Prioritize two kinds of
   content: **hard rules** (constraints that override convenience) and
   **gotchas** (recorded traps). Treat every gotcha as a bug you will
   personally reintroduce if you don't know it.
2. Read the newest entry of the project's session log / handover file if
   one exists. It says what state the code was left in, what was
   verified, and what's open.
3. Restate the task in one sentence, then answer three questions IN
   WRITING before any edit:
   - Which modules/areas will this touch?
   - Which hard rule is closest to being violated by the obvious
     approach?
   - Which recorded gotcha is closest to the data I'm about to handle?
4. Check the roadmap/next-features list. If the task matches an item,
   its ordering and margin notes are instructions, not suggestions.
5. Only then open source files.

## Rules
- A gotcha list is PAID-FOR knowledge — each entry typically cost a live
  debugging session. Never "simplify" code in a way that deletes the
  reason a gotcha exists.
- If the brief and the code disagree, assume you misread the code unless
  the newest log entry says the code moved past the brief.
- If your plan requires relaxing a hard rule, stop: the plan is wrong,
  not the rule.
- If the project has NO brief or gotcha list, creating one is part of
  your job (see keep-a-handover-log.md).

## Case study
Task: "add more indicators to the chart." The obvious approach — a
popular free charting widget with hundreds of built-in studies — had
already been tried, shipped, and ripped out of the project, because its
free tier capped stacked indicators behind a subscription, violating the
project's no-paywalled-components hard rule. Both the rule and the
removal reason were in the brief. Reading it first turns a doomed
half-day into a two-minute course correction toward the approach that
actually shipped (an Apache-2.0 library, vendored).

## Anti-patterns
- Grepping for a function and editing it without knowing which
  reliability tier or layer it lives in.
- Treating the user-facing README as the dev brief.
- Skimming past the log's "verified live" sections — they contain the
  exact commands you'll need to verify your own change.
