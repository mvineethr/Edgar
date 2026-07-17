---
name: brain-task-planning
description: >
  Load before starting any multi-step engineering task: implementing a feature,
  a fix touching 3+ files, a migration, a refactor, an integration, or any work
  expected to exceed ~10 tool calls or contain unknowns. Also load mid-task when
  you notice drift — you can't state the current step number, you're editing
  files the plan never mentioned, or you've repeated an approach that already
  failed. Covers: the trigger test for when a plan is required, the plan
  template (goal / constraints / non-goals / checkpointed steps / observable
  done-criteria / risks), decomposition heuristics (vertical slices,
  riskiest-unknown first, time-boxed spikes), long-task discipline (working
  log, re-anchoring ritual, explicit replan protocol), and cold-resume state so
  a fresh session can continue after context loss. Enforces non-negotiable #3
  ("plan before code"); full rationale in brain-change-control.
---

# brain-task-planning

Decomposition, plan format, and staying on track in long tasks. This skill is
the home of non-negotiable #3 in practice: **plan before code on any
multi-step work** (rationale and gating: `brain-change-control`).

The failure this skill defends against is **losing the plot**: starting
strong, then drifting into side-quests, re-solving solved problems, forgetting
what "done" meant, and burning a session with nothing verifiable to show. A
plan is not ceremony — it is the artifact that makes drift detectable.

**Definitions used below**
- **Checkpoint**: an observable (command output, HTTP status, test count, file
  diff, UI state) that proves a step worked. A feeling of progress is not a
  checkpoint.
- **Spike**: a time-boxed, throwaway investigation whose only deliverable is
  an answer to a question — never shipped code.
- **Unknown**: any fact you would have to guess to write the next step
  ("does the API paginate?", "which module owns retries?").

## 1. When a plan is required

Run this test before touching code. **Any single YES → write a plan first.**

| # | Trigger | YES if… |
|---|---------|---------|
| 1 | Files | The change will touch **3 or more files** |
| 2 | Unknowns | There is **more than 1 unknown** you'd have to guess |
| 3 | Behavior | **Any externally observable behavior changes** (API response, UI, CLI output, schema, config format) |
| 4 | Length | You expect **more than ~10 tool calls** or multiple edit-verify cycles |
| 5 | Risk class | The change classifies as **Standard or Risky** on the `brain-change-control` ladder |
| 6 | Recovery | You are resuming or untangling a previous failed attempt |

**No plan needed** when ALL of these hold: single obvious edit (typo, one-line
fix, rename local to one file), zero unknowns, no behavior change beyond the
explicit request, and verification is one command. Writing a plan for a
one-line diff is waste; skipping one for a migration is how sessions die.

Borderline case rule: if you spend more than a minute debating whether you
need a plan, you need a plan — the hesitation *is* the unknown.

For hard, ambiguous, multi-day problems (root cause unknown, success criteria
themselves unclear), a single plan is not enough — escalate to
`brain-campaign-playbook`. For "I don't know this repo at all", run
`brain-codebase-discovery` first; its output feeds the plan's Unknowns list.

## 2. The plan artifact

Copy `templates/PLAN.md` (in this skill's directory) to your plan location and
fill every section **before writing code**. Suggested location:
`.claude/plans/<YYYY-MM-DD>-<slug>.md` in the target repo (add `.claude/plans/`
to `.gitignore` unless the project's convention is to commit plans — check
before committing; see `brain-change-control`).

Required sections and the quality bar for each:

| Section | Bar |
|---|---|
| **Goal** | One sentence. What is true at the end that is not true now. If you need two sentences, you have two tasks — split them. |
| **Constraints** | Hard limits: compatibility, dependency policy, platforms, deadlines. Things that make otherwise-valid solutions invalid. |
| **Non-goals** | What a reasonable person might assume is in scope but is not. This is the scope-creep fence; enforcement discipline lives in `brain-minimal-change`. Minimum 1 entry — "none" is almost never true. |
| **Known risks and unknowns** | One line each, paired with the step or spike that surfaces it early. |
| **Steps** | Numbered. Each has a **checkpoint**. Sizing rules in §3. |
| **Done criteria** | Numeric/observable only: "`pytest -q` → 128 passed", "GET /health → 200 in <100ms", "bundle size delta ≤ +2 KB". Each must be checkable by a fresh session with no memory of this conversation. "Works", "clean", "improved" are banned words here. Evidence hierarchy and proof-of-work format: `brain-validation-and-qa`. |
| **Working log / Deviations / Resume state** | Execution-time sections; see §4 and §5. |

A plan whose done-criteria you cannot write is a plan you are not ready to
execute — the missing criterion is an unknown; add a spike for it.

### Checkpoint quality ladder (weakest → strongest)

1. "Code compiles / no editor squiggles" — near-worthless as a checkpoint.
2. "Unit test for the new path passes" — good.
3. "End-to-end command shows new behavior; old behavior tests still pass" — best.

Prefer the strongest checkpoint you can afford per step; the final step's
checkpoint should be at level 3.

## 3. Decomposition heuristics

**Vertical slices over horizontal layers.** A vertical slice cuts through
every layer to deliver one observable behavior end-to-end; a horizontal layer
builds one tier completely before touching the next. Slice vertically: each
slice is demoable and verifiable, and integration risk is paid down
continuously instead of all at the end.

| Stack (labeled example) | Horizontal (avoid) | Vertical (prefer) |
|---|---|---|
| TypeScript/React/Next | "Build all API routes, then all components, then wire up" | "One page: route + fetch + render for a single entity, end-to-end" |
| Backend/API/SQL | "Design full schema, then all endpoints, then auth" | "One endpoint: migration + handler + integration test for one resource" |
| Data/ML/Python | "Ingest everything, then all features, then model" | "One thin pipeline: 100 rows → 2 features → baseline metric printed" |

**Riskiest-unknown first.** Order steps so the thing most likely to sink the
plan is probed earliest, when the sunk cost is lowest. If step 6 depends on an
undocumented API behaving a certain way, a 15-minute probe of that API is
step 1 — not a hope embedded in step 6.

**Time-boxed spikes.** When an unknown blocks planning itself, add an explicit
spike step: a question, a time box (15–45 min), and a deliverable of *an
answer written into the plan* — never shipped code. When the box expires,
stop and record what you learned, even if incomplete; an expired spike that
yields "this approach won't work" is a success. Debugging-shaped unknowns use
the loop in `brain-debugging-playbook` instead of ad-hoc poking.

**Step sizing.** A step is correctly sized when all four hold:
1. It has exactly one checkpoint (two checkpoints → two steps).
2. It can fail without invalidating completed steps.
3. You can state before starting it what output you expect to observe.
4. It fits in roughly 5–15 tool calls. Bigger → split; if most steps are 1–2
   trivial calls, merge — plan overhead should stay under ~10% of task effort.

**Dependency check.** After drafting steps, scan for any step whose failure
would force redoing earlier ones. If found, reorder or add an earlier probe.

## 4. Long-task discipline: staying on the plan

A plan you never look at again is decoration. Three mechanisms keep it live.

### 4a. Working log

Maintain the **Working log** section of the plan file: one line per meaningful
action — timestamp, what you did, what you observed. Append-only; never edit
history.

```
- 14:32 ran migration 0042 → applied, 0 errors
- 14:38 pytest tests/api → 3 failures, all in test_pagination
- 14:51 root cause: off-by-one in cursor encode; fixed api/cursor.py:88
```

Append from the shell (both forms verified 2026-07-09 on the authoring
machine):

```powershell
# PowerShell
Add-Content -Path .claude\plans\2026-07-09-fix-auth.md -Value "- $(Get-Date -Format HH:mm) step 3 done: tests pass (12/12)" -Encoding utf8
```

```sh
# POSIX
printf '%s\n' "- $(date +%H:%M) step 3 done: tests pass (12/12)" >> .claude/plans/2026-07-09-fix-auth.md
```

(Editing the plan file directly with your file-edit tool is equally fine; the
commands matter less than the habit.)

### 4b. Re-anchoring ritual — every 10 actions

After roughly every **10 tool calls** (or whenever you complete a step,
whichever comes first), stop and run this 60-second ritual:

1. Re-read the plan's **Goal** and current **step**.
2. Ask: *is my last action in service of the current step?*
3. List any deviations: files touched that no step mentions, sub-problems
   adopted that no step contains, approaches retried that already failed once.
4. Zero deviations → log one working-log line, continue.
   Any deviation → invoke the replan protocol (4c). Do not "just finish this
   one thing first" — that sentence is the sound of the plot being lost.

Drift tells that must trigger the ritual immediately, off-schedule:
- You cannot state, without looking, which step number you are on.
- You are editing a file the plan never mentions.
- You are about to retry something that already failed, unchanged.
- You have thought "while I'm here, I might as well…" (`brain-minimal-change`).

### 4c. Replan protocol — when reality diverges

When a step fails, an assumption proves false, or scope shifts, **stop
executing**. Drifting silently — patching the trajectory without updating the
plan — is the failure mode; replanning is cheap, drift is not.

1. **Stop.** No further code edits.
2. **Diff plan vs reality.** In the **Deviations** section, write: what the
   plan said, what actually happened, in ≤3 lines.
3. **Revise.** Update steps/risks/done-criteria. Keep the Goal unless the
   user's actual request changed — if the *goal* itself moved, confirm with
   the user before proceeding.
4. **Record why.** One line: the reason for the revision, so a future reader
   (or resumed session) doesn't re-trust the falsified assumption.
5. Resume from the revised plan.

Three replans on the same step means the problem is misunderstood, not
mis-executed: stop, and either run a spike, `brain-debugging-playbook` (if
it's a defect), or escalate to `brain-campaign-playbook` (if the whole framing
is wrong).

## 5. Cold-resume resilience

Assume the session can die at any moment — context compaction, crash, handoff
to a different model, or the user returning next week. The test: **could a
fresh session, given only the plan file, continue without asking anything?**

Keep the plan's **Resume state** section current — overwrite it (unlike the
append-only log) after **every completed step** and immediately before any
risky/long operation:

- **DONE** — steps completed, each with its checkpoint result.
- **VERIFIED** — which done-criteria are already proven, and by what command.
- **IN PROGRESS** — exact state: branch name, files half-edited, the command
  you were about to run.
- **NEXT** — the single next action, concrete enough to execute verbatim.
- **OPEN QUESTIONS** — unresolved items that block or shape remaining work.

Resume-state hygiene rules:
- Facts, not vibes: "step 4 checkpoint passed: 12/12 tests" not "going well".
- Distinguish *done* from *verified* — code written but never run is neither.
- Name artifacts absolutely enough to find: branch, file paths, log locations.
- On resuming a cold plan: first re-run the most recent checkpoint to confirm
  the recorded state still holds, then continue from NEXT.

## When NOT to use this skill

| Situation | Use instead |
|---|---|
| Single obvious edit failing every trigger in §1 | Just do it; cite proof per `brain-validation-and-qa` |
| Deciding whether a change is allowed at all, or its risk class | `brain-change-control` |
| Keeping an in-flight diff small (the fence, not the plan) | `brain-minimal-change` |
| Hunting a defect with unknown cause | `brain-debugging-playbook` (its loop replaces plan steps for the hunt) |
| Multi-day ambiguous problem where success criteria are unclear | `brain-campaign-playbook` |
| First hour in an unfamiliar repo | `brain-codebase-discovery` (run it *before* planning) |
| Proving a finished change works | `brain-validation-and-qa` / `brain-proof-and-analysis` |
| Writing the final report/PR text | `brain-docs-and-writing` |

## Provenance and maintenance

- **Authored**: 2026-07-09, on Windows 11 (PowerShell 5.1 + Git Bash);
  revised 2026-07-10 (review pass: risk-class names aligned to the
  `brain-change-control` ladder).
- **Verified on authoring machine**: the `Add-Content` (PowerShell) and
  `printf >> ` (POSIX) log-append commands in §4a, including `mkdir -p` /
  `New-Item -ItemType Directory -Force` for creating `.claude/plans/`.
- **May drift**: the numeric thresholds (3 files, >1 unknown, ~10 tool calls,
  re-anchor every 10 actions, 15–45 min spike boxes) are calibrated defaults,
  not laws — tune per repo after observing a few sessions and record overrides
  in the project skill layer (see `brain-harness-bootstrap`). The suggested
  plan location `.claude/plans/` is a convention, not a requirement.
- **Re-verify in target repo**: `printf '%s\n' "test" >> /tmp/plan-test.md && cat /tmp/plan-test.md`
  (POSIX) or `Add-Content -Path $env:TEMP\plan-test.md -Value "test" -Encoding utf8; Get-Content $env:TEMP\plan-test.md`
  (PowerShell) — trivial, but confirms shell availability and write perms.
- **Cross-references to keep in sync**: `brain-change-control` (non-negotiable
  #3 home), `brain-minimal-change`, `brain-validation-and-qa`,
  `brain-debugging-playbook`, `brain-campaign-playbook`,
  `brain-codebase-discovery`, `brain-harness-bootstrap`.
