# Universal Skill Library

Sixteen repo-agnostic engineering disciplines, distilled from a real
project's session history. Every rule here was paid for by an actual
debugging session; the case studies are real incidents, anonymized.
Written to be followed MECHANICALLY — numbered procedures, explicit
rules where judgment was used — so they work with smaller/faster models
(Sonnet, Haiku, Opus), not just frontier ones.

## How to install in another project

Any of these work; the first is the highest-leverage:

1. **Reference from the project's CLAUDE.md** (recommended). Copy this
   folder into the repo (e.g. `skills/`) and add to CLAUDE.md:
   > Before starting work, read `skills/INDEX.md`. Load the skills it
   > recommends for the situation at hand and follow their procedures
   > mechanically.
2. **Global install**: put the folder under `~/.claude/` and reference
   it from `~/.claude/CLAUDE.md` so every project inherits it.
3. **Selective paste**: for a small task, paste only the 1–3 relevant
   skill files into context.

Two skills (read-the-briefing-first, keep-a-handover-log) assume the
project keeps a standing brief (CLAUDE.md) and a session log
(HANDOVER.md). If the project has neither, those skills tell you to
create them — do that first; everything else compounds on top.

## Ranking — quality bought per token spent

Skills that prevent silent, expensive bug classes with a short mechanical
rule rank highest. If you can only load a few, take them from the top.

| Rank | Skill | One-line contract |
| --- | --- | --- |
| 1 | [verify-in-reality.md](verify-in-reality.md) | Nothing is "done" until exercised against the real system with one value cross-checked against an independent source. |
| 2 | [sanity-check-numbers.md](sanity-check-numbers.md) | Every numeric field gets unit + baseline + authority written down, and one digit-for-digit external match. Catches the worst bug class: silently wrong numbers. |
| 3 | [tiered-reliability.md](tiered-reliability.md) | Name the tier (authoritative / decoration / fragile) before writing any error handling; decoration degrades visibly, never breaks the core. |
| 4 | [probe-before-building.md](probe-before-building.md) | One curl at a real, HARD case before any parser or integration is designed. |
| 5 | [debug-silent-failures.md](debug-silent-failures.md) | No error message? Manufacture one: walk layer boundaries extracting artifacts until one contradicts an assumption. Includes a seed catalog of known silent-failure patterns. |
| 6 | [fixtures-copy-reality.md](fixtures-copy-reality.md) | Mocks are trimmed copies of live responses, never hand-built; regression = fix the fixture until the old code fails, THEN fix the code. |
| 7 | [know-your-keys.md](know-your-keys.md) | Identify the true identity key before any group/diff/join; aggregate within snapshots first; verify "duplicates" are actually duplicates. |
| 8 | [read-the-briefing-first.md](read-the-briefing-first.md) | Hard rules + gotchas + newest log entry, then three written questions, BEFORE the first edit. |
| 9 | [never-guess-identifiers.md](never-guess-identifiers.md) | Every hardcoded ID, symbol, and URL gets one live round-trip before commit — graceful degradation guarantees your typo will be silent. |
| 10 | [gate-your-dependencies.md](gate-your-dependencies.md) | New components pass the identity gate (access model, license, functional fine print, runtime independence) before technical merit is even discussed. |
| 11 | [respect-rate-limits.md](respect-rate-limits.md) | One central HTTP helper owns throttle/retry/identity; reduce request count, never touch the throttle; retry only what can succeed. |
| 12 | [keep-a-handover-log.md](keep-a-handover-log.md) | Session close = log entry (asked/decided/changed/verified-with-values/open) + graduate durable facts to the standing brief. The mechanism that creates all other skills. |
| 13 | [single-source-view-layer.md](single-source-view-layer.md) | With 2+ frontends, every feature lands in one shared view layer first; frontends are thin wrappers that cannot disagree. |
| 14 | [cache-by-immutability.md](cache-by-immutability.md) | Key and TTL derive from when the data CAN change; failures are never cached; verify cold and warm paths live. |
| 15 | [scope-honestly.md](scope-honestly.md) | Classify every chunk (buildable / conditional / not-replicable / dangerous), reframe the dangerous, record every disposition. |
| 16 | [finish-autonomously.md](finish-autonomously.md) | Delegation grants sequencing, not scope; verify-existing before build-new; never revive what the user deferred. |

## Situational loading guide

- **Every session**: #8 at start; #12 at close.
- **Before any edit**: know your tier (#3) and, if multi-frontend, your
  layer (#13).
- **Adding a component or source**: #10 gate → #4 probe → #6 fixtures →
  #11 if it adds requests → #14 if it adds a cache.
- **Hardcoding any ID/symbol/URL**: #9.
- **Anything with numbers in it**: #2.
- **Comparing/joining/deduping data**: #7.
- **Before saying "done"**: #1, always.
- **Broken with no error**: #5 first.
- **Big vague request**: #15. **Open delegation**: #16.

The skills cite each other where they interlock. Together they describe
one loop: read the record → scope → probe → build in the right tier and
layer → test against real fixtures → verify in reality → write it down.
