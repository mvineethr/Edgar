---
name: brain-campaign-playbook
description: >
  Decision-gated campaign structure for problems too hard for the ordinary
  debugging loop. Load when a problem is expected to take more than one session,
  has no reproducible starting point, is goal-shaped rather than bug-shaped
  ("make X 10x faster", "make CI reliable"), or has already survived two
  disciplined attempts with brain-debugging-playbook. Also load when resuming a
  campaign another session started, when an intermittent failure nobody has
  cracked lands on you, or when tempted to grab the first plausible fix.
  Provides: the campaign-vs-loop decision test, campaign anatomy (numeric
  mission, numbered phases with expected observations and explicit branches at
  each gate, ranked solution menu with obligations, fenced wrong paths,
  validation/promotion, abort criteria, campaign log), a complete worked
  example (flaky CI test), and templates/CAMPAIGN.md. Ordinary bugs →
  brain-debugging-playbook; open research questions →
  brain-research-methodology.
---

# brain-campaign-playbook

A **campaign** is a written, decision-gated attack plan for a problem that a
single debugging session cannot crack. Its defining property: **every step has
a predicted observation and pre-written branches** — "if you see X, go to
phase Y; if you see Z, hypothesis H is dead." You never decide what to do next
while staring at a surprising result; the campaign decided for you when you
were calm. Hard problems are exactly where sessions drift, guess, and
overclaim; the gates make drift visible and costly to ignore — at any moment you are
either executing a phase's commands, logging a gate result, or revising the
campaign document. Nothing else.

**Definitions used below**
- **Gate**: the checkpoint ending a phase — an expected observation (a number
  or exact output) plus explicit branches per outcome. A decision point, not
  narration.
- **Fenced path**: an approach recorded as forbidden, with the evidence that
  killed it. Attempting one without new logged evidence is a campaign
  violation.
- **Promotion**: turning a campaign finding into an adopted repo change,
  through normal change control.

## 1. Campaign or debugging loop?

Run this test. **Any single YES → open a campaign.**

| # | Trigger | YES if… |
|---|---------|---------|
| 1 | Duration | You expect the problem to take **more than one session** of work |
| 2 | Repro | There is **no reproducible starting point** — the failure is intermittent, environment-bound, or historical |
| 3 | Shape | The goal is **goal-shaped, not bug-shaped**: "make X 10x faster", "get flake rate to zero", "cut cold-start below 2 s" — nothing is "broken", something must become measurably better |
| 4 | History | **Two disciplined attempts** with the `brain-debugging-playbook` loop have already failed to produce a root-cause sentence |

All NO → an ordinary bug; use `brain-debugging-playbook` and skip the campaign
overhead (30–60 minutes of writing before any investigation — only justified
when the alternative is multiple sessions of undirected poking).

If the question is open-ended with no adoptable change at the end ("which
architecture should we pick?"), that is research — use
`brain-research-methodology`. A campaign always terminates in either a
promoted change or an honest abort report.

## 2. Campaign anatomy

The campaign lives in one file: copy `templates/CAMPAIGN.md` (in this skill's
directory) to `.claude/campaigns/<YYYY-MM-DD>-<slug>.md` in the target repo
(location and gitignore conventions as for plans in `brain-task-planning`).
Seven sections, each with a quality bar; a campaign missing any section is not
ready to execute.

### 2.1 MISSION — one sentence, one number

One sentence stating what will be true at the end, plus a **numeric success
criterion declared before any investigation starts**. "Judged by eye",
"noticeably better", and "seems stable" are banned. If you cannot measure it
yet, phase 0 is building the measurement (`brain-diagnostics-and-tooling`).
Declaring the number up front is the prediction discipline of
`brain-research-methodology`: a criterion chosen after seeing results is a
rationalization, not a criterion.

Bar: a fresh session with no memory of this conversation can run one command
and answer "is the mission accomplished?" yes or no.

**No threshold shopping.** The criterion may be revised only as a logged
campaign revision — reason recorded, before further validation runs — never
quietly relaxed after a near-miss. The same rule binds per-phase predictions:
never rewrite one to fit observed data; the observation gets logged against
the original prediction, and the new expectation is a new, dated entry.

### 2.2 NUMBERED PHASES — commands, expected observation, branches

Each phase is:

1. **Commands** — exact, copy-pasteable, POSIX + PowerShell where they differ.
2. **Expected observation at the gate** — a number or exact output predicted
   *before running*.
3. **Branches** — "if X instead → phase Y / abandon hypothesis Z." Every
   plausible outcome has a pre-written next move.

Bar: at every gate, at least one hypothesis dies or one branch is taken — a
gate whose outcome changes nothing is narration; delete it. A result matching
no branch is a mandatory stop: log the surprise, revise the campaign document,
then continue. Never improvise past a gate. Order phases by information per
unit cost — measure, isolate, discriminate hypotheses, fix last; the single
most common campaign mistake is starting at "fix".

### 2.3 SOLUTION MENU — ranked candidates with obligations

Before any fixing, list the candidate approaches, ranked, each with its
**obligations**: what must be derived, measured, or proven *before that
approach may be attempted*. Typical obligations: "root-cause mechanism
confirmed at phase 4 gate", "cost measured at < N ms overhead", "differential
test against current behavior written" (see `brain-proof-and-analysis`).

Bar: no approach is attempted while any of its obligations is undischarged.
This is the anti-"grab the first idea" mechanism: the menu forces you to see
options two and three before committing to one; the obligations force evidence
before effort.

### 2.4 FENCED WRONG PATHS — forbidden without new evidence

Approaches already known to fail, each with the evidence why (a measurement, a
dated past attempt, a mechanism argument). Mine repo history for these before
inventing them — prior failed attempts live in old PRs, reverted commits, and
postmortems (`brain-failure-archaeology`).

Bar: each fence cites evidence, not vibes. Reopening a fence requires logging
new evidence first — write the evidence, then unfence, never the reverse.

### 2.5 VALIDATION AND PROMOTION — how a finding becomes a change

A campaign result is promoted only when:

1. The MISSION's numeric criterion is met, with executed proof in the
   proof-of-work format of `brain-validation-and-qa` — **never on a single
   lucky run**; the criterion itself must encode repetition or sample size.
2. The change ships as a minimal diff through the normal gates of
   `brain-change-control` — a campaign grants zero exemptions.
3. The log records the mechanism sentence and links the promoting commit/PR;
   durable lessons go to the LEARNINGS convention (`brain-failure-archaeology`).
4. The measured benefit is explained by the confirmed mechanism. A change
   that helps for reasons you cannot explain — numbers good, predicted
   mechanism refuted — is not promotable: you don't know when it will stop
   helping. Form a new hypothesis and let a fresh prediction survive new runs
   first.

### 2.6 ABORT CRITERIA — how the campaign ends honestly

Declared up front, checked at every gate:

- **Budget exhausted** — sessions, hours, or run-count spent (pick concrete
  numbers when writing the campaign).
- **Criterion unreachable** — evidence shows the numeric target cannot be met
  within the campaign's constraints.
- **Premise falsified** — the problem is not what the mission assumed (e.g.
  the "flaky test" turns out to be a flaky runner image you don't control).

On abort, write an abort report (format: `brain-docs-and-writing`): what was
established with evidence, what was ruled out (these become fences for the
next campaign), exact resume state, recommendation. An honest abort with three
dead hypotheses is a **successful outcome** — the next campaign starts three
moves ahead. Overclaiming partial progress as success is the failure mode this
section exists to prevent.

### 2.7 CAMPAIGN LOG — so any session can resume cold

Append-only log at the bottom of the campaign file: one entry per session —
date, phase, commands run, **observed numbers** (never "looked fine"), gate
outcomes and branches taken, updated resume state (current phase, next command
verbatim, open questions). This is the cold-resume discipline of
`brain-task-planning` §5 applied to a multi-session artifact; its resume-state
hygiene rules apply unchanged.

Resuming cold: read the whole file, re-run the last gate's command to confirm
recorded state still holds, then execute the logged NEXT action. Never restart
phase 0 because re-reading feels slower than re-doing — it is not.

## 3. Worked example — flaky integration test

**Illustrative** — all numbers, file names, and outcomes below are invented
to show the required shape and concreteness; the commands are real.

---

### MISSION

`tests/integration/order-sync.spec.ts` fails ~1 in 20 CI runs with no code
change; make it deterministically green by fixing the root cause.
**Success criterion: 200 consecutive local runs green AND 50 consecutive CI
runs green, with a root-cause sentence and a regression test that forces the
failure mode.** (Why 200: at 5% failure, P(200 straight greens) = 0.95²⁰⁰ ≈
0.004%, so a 200-streak proves the rate collapsed; 20 greens is 36% likely by
pure luck and proves nothing.)

### PHASE 0 — Baseline: measure the failure rate

```sh
# CI failure rate over recent history (GitHub Actions)
gh run list --workflow ci.yml --limit 240 --json conclusion \
  | jq '[.[] | select(.conclusion=="failure")] | length'
```

```sh
# POSIX — local rate, 100 runs
pass=0; fail=0
for i in $(seq 1 100); do
  if npx vitest run tests/integration/order-sync.spec.ts >/dev/null 2>&1
  then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL run $i"; fi
done
echo "pass=$pass fail=$fail"
```

```powershell
# PowerShell — local rate, 100 runs
$fail = 0
1..100 | ForEach-Object {
  npx vitest run tests/integration/order-sync.spec.ts *> $null
  if ($LASTEXITCODE -ne 0) { $fail++; "FAIL run $_" }
}
"failures: $fail / 100"
```

**Expected at gate:** CI ≈ 12 failures / 240 runs (5%); local 2–10 failures /
100 runs (within ~2x of CI).
**Branches:**
- Local rate 2–10% → repro is local and cheap → **phase 1**.
- Local 0 failures / 100 → failure is environment-bound → **phase 1B**
  (reproduce under CI-like conditions; abandon any hypothesis that requires a
  purely local mechanism).
- Local rate > 25% → the environment delta makes it *worse* locally — an even
  cheaper repro; note the delta as evidence and go to **phase 1**.

*(Invented result: CI 12/240; local 6/100 → phase 1.)*

### PHASE 1 — Isolation: solo vs suite, stable vs shuffled

```sh
# solo (as above, 100 runs) vs full suite, 20 runs
for i in $(seq 1 20); do npx vitest run >/dev/null 2>&1 || echo "SUITE FAIL $i"; done
# order sensitivity (vitest; flag is standard documented usage — re-verify)
npx vitest run --sequence.shuffle
```

**Expected at gate:** a clean signature matching exactly one branch below.
**Branches:**
- Fails solo at ≈ the same rate → suite ordering and cross-test shared state
  are **dead** (fence H4, abandon H2a "polluted by earlier test") → phase 2.
- Passes solo 100/100 but fails in suite → mechanism is ordering or shared
  state → phase 2, prioritize H2/H4 experiments.
- Fails only when shuffled → ordering dependence proven → skip fan-out, go
  directly to phase 3 with H4 only.

*(Invented result: fails solo 5/100 → ordering fenced; phase 2.)*

### PHASE 2 — Capture one failure with full artifacts

Run until first failure, keeping logs only for it:

```sh
i=0
while :; do
  i=$((i+1))
  if ! npx vitest run tests/integration/order-sync.spec.ts > "run-$i.log" 2>&1
  then echo "captured failure on run $i -> run-$i.log"; break; fi
  rm "run-$i.log"
done
```

Before looping, add `DIAG:`-marked instrumentation at suspect boundaries
(timestamps around awaits, row counts before asserts) — marker protocol and
mandatory removal step: `brain-diagnostics-and-tooling`.

**Expected at gate:** a failure captured within ~60 runs (5% rate → P(no
failure in 60) ≈ 4.6%), log shows which assertion fails and with what values.
**Branches:**
- Failure captured → phase 3.
- 300 instrumented runs, no failure → the instrumentation changed timing;
  that is itself evidence **for** a timing hypothesis (H1). Log it, retry with
  the cheapest single probe; if still clean, go to phase 3 with H1 promoted
  to prime suspect.

*(Invented result: failure on run 23; assertion `expected 3 orders, got 2`;
DIAG timestamps show the assert ran 8 ms after the sync call returned.)*

### PHASE 3 — Hypothesis fan-out with discriminating experiments

Each experiment states its predicted number before running
(`brain-research-methodology`); one variable per experiment.

| H | Mechanism | Discriminating experiment | Prediction if TRUE | Prediction if FALSE |
|---|---|---|---|---|
| H1 timing/race | Assert runs before an async write commits | Run the 100-loop under CPU load (`npx vitest run ... &` × 4 concurrently, or a busy loop in another shell) | Failure rate rises ≥ 3x (to ≥ 15/100) | Rate unchanged (±2) |
| H2 shared state | Test reuses DB rows/files across runs; leftover state from a *previous run* | Point the test at a freshly created schema per run (`DB_SCHEMA=t_$i` env var) vs shared | Fresh-schema runs: 0/100; shared: ~5/100 | Both ~5/100 |
| H3 external dep | Test hits a real network service that intermittently 5xxs | `grep -rn "http" tests/integration/order-sync.spec.ts` + run with network blocked (offline mode / firewall rule) | Blocked runs fail 100% or hang → real dep confirmed | Blocked runs pass → no live network in path |
| H4 ordering | Earlier test pollutes state | *Already dead* — fenced at phase 1 gate | — | — |

**Gate:** at least one hypothesis survives with a confirming number and the
others have disconfirming numbers.
**Branches:**
- Exactly one survivor → phase 4.
- Two survivors → design one more experiment whose predictions differ between
  them (discriminating-experiment definition: `brain-debugging-playbook`);
  never proceed with two live hypotheses.
- Zero survivors → the fan-out missed the mechanism; return to phase 2,
  capture two more failures, mine failing-vs-passing log diffs for a new
  hypothesis. Log the dead fan-out — it fences four paths for whoever resumes.

*(Invented result: under load 19/100 fail; fresh schema still fails 6/100;
network grep clean and blocked runs pass. H1 survives alone.)*

### PHASE 4 — Root-cause confirmation: control the failure

A hypothesis is confirmed when you can turn the failure **on and off at will**
by controlling the variable — not merely correlate with it.
- Force ON: insert a 50 ms delay in the suspected window (after `syncOrders()`
  returns, before its background write settles). **Prediction: 100/100 fail.**
- Force OFF: explicitly await the write barrier in the test.
  **Prediction: 0/200 failures under CPU load.**

**Gate:** both predictions hit → write the root-cause sentence: *"The test
asserts order count after `syncOrders()` resolves, but the implementation
fires a final upsert without awaiting it, so under CPU pressure the assert
reads the table before the third row commits."* → the SOLUTION MENU's
obligations are now dischargeable; pick from it, then VALIDATION AND PROMOTION.
**Branch:** forcing ON does not reach ~100% → the window is wrong or there
are two races; halve the suspected span with DIAG timestamps (binary-search
technique: `brain-debugging-playbook`) and repeat phase 4.

### SOLUTION MENU (ranked)

| # | Approach | Obligations before attempting |
|---|---|---|
| 1 | Fix the source: `await` the final upsert inside `syncOrders()` | Phase 4 gate passed; confirm no caller depends on the fire-and-forget behavior (`grep -rn "syncOrders(" src/ tests/`); minimal diff per `brain-minimal-change` |
| 2 | If fire-and-forget is intentional API: expose a completion promise and await it in the test | Evidence that production callers rely on non-blocking behavior; differential test old-vs-new (`brain-proof-and-analysis`) |
| 3 | Poll-until-consistent helper in the test with hard 5 s ceiling | Only if 1 and 2 are architecturally blocked — record why in the log; ceiling justified by measured worst-case commit latency × 10 |

### FENCED WRONG PATHS

| Fenced path | Evidence |
|---|---|
| Add test retries (`retry: 2`) | Masks the symptom; the same unawaited write can drop orders in production. PR #312 (2025-11, invented) added retries to a sibling test; flake "vanished" and resurfaced as a prod data-loss incident |
| Increase test timeout | Timeout was already raised 5 s → 15 s (invented commit `a1b2c3d`); rate stayed ~5% (11/240 before, 12/240 after) — the failure is a wrong value, not slowness |
| Skip/quarantine the test | The test guards order consistency; quarantining trades a red build for silent data loss |
| Pin test order | Ordering was disconfirmed at phase 1 (fails solo 5/100) |

### VALIDATION AND PROMOTION

```sh
# POSIX — the mission criterion, local half
n=0
while [ $n -lt 200 ]; do
  npx vitest run tests/integration/order-sync.spec.ts >/dev/null 2>&1 \
    || { echo "FAIL at run $((n+1)) — streak reset, mission not met"; exit 1; }
  n=$((n+1)); echo "green $n/200"
done
```

```powershell
# PowerShell
$n = 0
while ($n -lt 200) {
  npx vitest run tests/integration/order-sync.spec.ts *> $null
  if ($LASTEXITCODE -ne 0) { "FAIL at run $($n + 1) - streak reset"; break }
  $n++; "green $n/200"
}
```

Plus: regression test forcing the race (the phase-4 ON switch, made
deterministic) fails on old code, passes on the fix; 50 consecutive CI runs
green (`gh run list` as in phase 0); all `DIAG:` instrumentation removed; diff
shipped through `brain-change-control` with proof-of-work per
`brain-validation-and-qa`; LEARNINGS entry recorded.

### ABORT CRITERIA

- Budget: 3 sessions or ~6 focused hours, whichever first.
- No failure captured after 500 instrumented local runs AND phase 1B (CI-like
  reproduction) also fails → abort; report the rate measurements and fences,
  recommend CI-side instrumentation as the next campaign's phase 0.
- Premise check: if phase 0 shows CI failures correlate with a specific runner
  image or infra incident window, "our test is flaky" is falsified → abort,
  open an infra ticket with the evidence.

*(End of worked example.)*

## 4. When NOT to use this skill

| Situation | Use instead |
|---|---|
| Ordinary bug: reproducible, likely single-session | `brain-debugging-playbook` — the loop, without campaign overhead |
| Open research question, no adoptable change as the end state | `brain-research-methodology` |
| Multi-step but well-understood build work | `brain-task-planning` — a plan, not a campaign |
| Building the measurement/instrumentation itself | `brain-diagnostics-and-tooling` |
| Deciding whether the eventual fix may ship | `brain-change-control` |
| Formatting the final report or abort report | `brain-docs-and-writing` |

## Provenance and maintenance

- Authored 2026-07-10 on Windows 11 (PowerShell 5.1 + Git Bash).
- Merged with the Sol library 2026-07-12: absorbed the no-threshold-shopping
  rule (§2.1) and the works-but-mechanism-refuted promotion bar (§2.5 item 4).
- Verified on the authoring machine 2026-07-10: the POSIX repro-rate loop
  (`for i in $(seq 1 N)` with pass/fail counters) and the PowerShell loop
  (`1..N | ForEach-Object` with `$LASTEXITCODE`), both against a synthetic
  flaky command — loop mechanics only.
- NOT executed here (standard documented usage; re-verify in target repo):
  `npx vitest run` invocations, `gh run list --workflow <file> --limit N
  --json conclusion` + `jq` filter, `vitest --sequence.shuffle`, the
  capture-on-first-failure and consecutive-green loops as full pipelines.
- May drift: vitest CLI flags per major version; `gh run list` JSON fields.
  The worked example's numbers are invented — never quote them as data.
  `.claude/campaigns/` mirrors `brain-task-planning`'s plan location; keep in
  sync if either moves.
- One-line re-verification: run the phase-0 loop with the target repo's real
  test command substituted, N=5, before relying on it.
