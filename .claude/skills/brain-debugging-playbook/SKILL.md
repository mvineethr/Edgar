---
name: brain-debugging-playbook
description: >
  Hypothesis-driven debugging loop for any bug, failure, or unexpected
  behavior. Load when a build breaks, a test fails (deterministic or flaky),
  output is wrong, an app crashes, hangs, or times out, performance regresses,
  CI fails what passes locally, an upgrade breaks something, logs are empty or
  contradictory, or it "works on my machine" only. Also load before any
  edit-and-rerun cycle, when tempted to guess at a fix, or when you need git
  bisect / data bisection / config bisection / minimal-repro technique.
  Provides: the reproduce-observe-classify-hypothesize-experiment-fix-prove
  loop, a failure-layer classification table (which layer is lying: command,
  env, deps, config, build, harness, logic, runtime, perf, data,
  observability), a hypothesis ledger for competing explanations, a symptom
  triage table with first-checks, fenced traps, and exit criteria for calling
  a bug fixed. Not for multi-day ambiguous unknowns (brain-campaign-playbook)
  or building diagnostic tooling (brain-diagnostics-and-tooling).
---

# brain-debugging-playbook

Debugging is applied science, not trial and error. Every action in a debugging
session either gathers a fact or tests a hypothesis. If an action does neither,
don't take it.

## Diagnosis authority is not fix authority

A request to explain or investigate a failure does not authorize edits,
dependency installs, service restarts, or cache deletion. During diagnosis,
never mutate the worktree as a diagnostic move: `git reset`, `git clean`,
`git checkout --`, and `git restore` are not experiments — they destroy the
evidence you are supposed to be reading. The one allowed shape is a fully
reversible round-trip you undo immediately (e.g. `git stash` → rerun →
`git stash pop` to answer "does it fail without my changes?"). Destructive
cleanup such as `git clean -fdx` stays behind the stop-and-ask gate in
**brain-change-control** §4 regardless of how convinced you are. Fixing
begins only at the FIX step below, after the mechanism is identified — and
only within whatever change authority the task actually granted.

## Step 0 — Consult the failure chronicle

Before debugging anything, check whether this battle was already fought:

```sh
# POSIX and PowerShell (identical)
git grep -il "<error keyword>" -- '*.md'
git log --oneline --grep="<error keyword>" -i
```

Look for `LEARNINGS.md`, `docs/failures*`, postmortems, or a failure chronicle
(the convention and how to build one live in **brain-failure-archaeology**).
If the chronicle explains this symptom, apply the recorded resolution and stop.
Never re-fight a settled battle — checking the chronicle typically costs under
a minute and can replace an entire investigation.

## The loop

This is the spine. Do the steps in order; skipping one is how sessions turn
into hours of guessing.

### 1. REPRODUCE — deterministically

You cannot debug what you cannot reproduce. Get to a single command that fails
the same way every time, and record it verbatim:

- Exact command, exact directory, exact input, exact error text.
- If it only fails sometimes, that is itself the first fact — see "flaky test"
  in the triage table. Measure the failure rate before anything else.
- If you cannot reproduce it locally, debug where it DOES reproduce (see the
  "wrong environment" trap).

### 2. OBSERVE — gather facts before touching code

No edits yet. Collect:

- The full error/stack trace, not a paraphrase.
- What changed recently: `git log --oneline -15`, `git status`, `git stash list`
  (uncommitted and stashed changes count as "changes").
- Whether it fails on a clean checkout of the last known-good commit.
- Relevant versions: runtime, package manager, OS (see **brain-build-and-env**
  for the stack-detection checklist).

Write the observations down as a numbered list. This list is the contract the
hypothesis must satisfy.

### 3. CLASSIFY — which layer is lying to you

The triage table below is symptom-first (what you see); this table is
layer-first (where the lie lives). The first visible error is often
downstream of the real fault — locate the earliest causal divergence and
explain later failures as consequences. Each layer has a first discriminator
and a forbidden shortcut that feels productive but destroys evidence or adds
variables:

| Layer | Typical evidence | First discriminator | Forbidden shortcut |
|---|---|---|---|
| **Command** | Not found, unknown task, wrong directory | Compare your invocation against docs, manifest, CI step | Installing a guessed tool |
| **Environment** | Version, OS, architecture, executable mismatch | Compare declared constraints vs a known-good run | Rewriting source to "fit" |
| **Dependencies** | Lock, resolution, or import failure | Compare manifest, lockfile, install mode, resolver output | Deleting the lockfile / global reinstall |
| **Configuration** | Behavior differs per env or flag | Trace definition, precedence, and effective value | Changing several settings at once |
| **Build / generation** | Compiler, linker, bundler, codegen failure | Identify the FIRST failing stage of the pipeline | Editing generated output |
| **Test harness** | Discovery, setup, or fixture failure | Run one known-good neighbor test under the same harness | Weakening the assertion |
| **Product logic** | Stable wrong output after clean setup | Find the first divergent intermediate value | Suppressing the error |
| **Runtime / integration** | Startup, protocol, permission, timing failure | Compare the lifecycle/dependency boundary with a control | Restarting shared services |
| **Performance / resource** | Latency, CPU, memory, or I/O anomaly | Measure the named resource under identical input | Optimizing by intuition |
| **Data / state** | Record-, migration-, ordering-, or cache-specific | Compare invariant metadata between affected and control | Editing or reseeding data |
| **Observability** | Missing or contradictory evidence | Verify clock, capture boundary, log level, correlation ID | Concluding "no bug" |

### 4. HYPOTHESIZE — a mechanism that explains ALL observations

A hypothesis is a causal sentence: "X happens because Y does Z under condition
W." Test it against every observation from step 2. A hypothesis that explains
observations 1 and 2 but not 3 is wrong — refine it or list a competitor. Keep
2–3 candidate hypotheses when the facts allow more than one story.

With 2+ competing hypotheses, keep a **hypothesis ledger** as the working
artifact — it stops you from re-testing dead hypotheses and forces the
prediction to be written BEFORE the run:

| ID | Hypothesis | Support | Contradictions | Prediction | One-variable experiment | Result | Status |
|---|---|---|---|---|---|---|---|
| H1 | Falsifiable causal sentence | Obs. #s | Obs. #s | "If true, X; otherwise Y" | Exact command/action | fill after run | open / rejected / supported |

Rank by explanatory power, not convenience. Reject a hypothesis when its
unique prediction fails in a valid experiment. A survivor is **supported, not
proven** — claim root cause only when one mechanism explains the affected
cases, the passing controls, the timing, AND the negative evidence.

### 5. Design a DISCRIMINATING EXPERIMENT

**Definition:** a discriminating experiment is a test whose predicted outcome
differs between competing hypotheses — whichever result you observe, at least
one hypothesis dies. An experiment consistent with all your hypotheses teaches
you nothing; don't run it.

**Example.** A web request returns stale data. H1: the server cache is
serving an old entry. H2: the client is not sending the changed parameter.
Discriminating experiment: hit the endpoint directly with `curl`
(PowerShell: `curl.exe`, not the `curl` alias for `Invoke-WebRequest`),
bypassing the client entirely. Stale via curl → H2 dies. Fresh via curl →
H1 dies. Either outcome of the one command eliminates a hypothesis.

Before running any experiment, state the prediction: "If H1 is true I will see
A; if H2 is true I will see B." (This prediction discipline is formalized in
**brain-proof-and-analysis**.) Change exactly one variable per experiment, and
compare like with like — a control run is only a control if it differs from
the failing run in exactly that one variable.

**Three-strikes rule:** three consecutive experiments that fail to
discriminate (every hypothesis still alive) means you are probing the wrong
thing. Stop experimenting. Reassess the failure layer (step 3), the evidence
quality (is the observability layer itself lying?), and the assumptions baked
into your hypotheses. If the bug still resists after that reassessment, treat
it as a campaign-scale unknown — **brain-campaign-playbook**.

### 6. FIX — the root cause, minimally

Fix the mechanism identified in steps 4/5, nothing else. Keep the diff minimal
(**brain-minimal-change**); resist drive-by cleanup while the repro still
exists to protect you. This is where diagnosis authority ends and fix
authority must exist (see the boundary at the top of this skill).

### 7. PROVE — the fix and the absence of regression

- Re-run the exact reproduction command from step 1; show it now passes.
- Run the surrounding test suite; show no new failures.
- Cite commands and observed output in the proof-of-work format defined in
  **brain-validation-and-qa** (that skill is the home of the evidence
  hierarchy — never claim "fixed" without executed proof).

## Symptom → triage table

First three things to check, in order, per symptom. Commands are identical in
POSIX shells and PowerShell unless a PS form is shown.

| Symptom | Check 1 | Check 2 | Check 3 |
|---|---|---|---|
| **Build failure** | Read the FIRST error, not the last — later errors are usually cascade. POSIX: `<build-cmd> 2>&1 \| head -50`; PS: `<build-cmd> \| Select-Object -First 50` | Rule out stale artifacts: preview `git clean -ndx`; `git clean -fdx` is a stop-and-ask destructive op (**brain-change-control** §4) — show the human the preview and get approval, or delete only the listed build-output dirs; then rebuild | Diff toolchain vs known-good: `node --version`, `python --version`, etc.; compare against lockfile/CI config (**brain-build-and-env**) |
| **Deterministic test failure** | Run only that test, verbose (e.g. `npx vitest run path/to/x.spec.ts`, `pytest path/to/test_x.py::test_name -x -vv`) and read actual-vs-expected in full | Is it the test or the code? `git log --oneline -10 -- <test-file> <code-under-test>` — which moved last? | Does it fail without your local changes? `git stash` → rerun → `git stash pop` |
| **Flaky test** | Measure the rate: POSIX `for i in $(seq 20); do <test-cmd> \|\| echo "FAIL $i"; done`; PS `1..20 \| ForEach-Object { <test-cmd>; if ($LASTEXITCODE -ne 0) { "FAIL $_" } }` | Alone vs in suite: run solo, then full suite — order/shared-state dependence if results differ | Grep the test for the usual suspects: time/`sleep`, randomness without a seed, real network, parallelism, shared files/DB rows |
| **Works on my machine** | Diff runtime + tool versions between both machines (exact, not major-version) | Diff env vars and config: POSIX `env \| sort > mine.txt` on each, then `diff`; PS `Get-ChildItem env: \| Sort-Object Name` | Fresh `git clone` into a new directory (or container) on YOUR machine — if it fails there, your working copy was the variable |
| **Local pass, CI fail** | Preserve the CI evidence before rerunning anything: job log, runner image/OS, exact revision, artifacts | Diff the command actually run — CI step vs your local invocation (flags, working directory, env vars, path case-sensitivity, concurrency) | Only then diff environments (works-on-my-machine row applies once the commands match) |
| **Failure after upgrade** | Capture old and new manifests + lockfiles side by side before touching anything | Isolate the one variable: old version passes, new fails, everything else identical | Read the changelog/migration notes for the failing surface; rolling back is a CHANGE, not a diagnostic — route through **brain-change-control** |
| **Performance regression** | Get a number, not a feeling: POSIX `time <cmd>`; PS `Measure-Command { <cmd> }` — 3+ runs, note variance (**brain-diagnostics-and-tooling** for profilers) | Prove it regressed: same measurement on a known-good ref (`git switch --detach <good-sha>`) | Bisect between good and bad refs (recipe below) — perf bugs rarely announce themselves in diffs |
| **Wrong output** | Pin the exact smallest failing input and write expected-vs-actual side by side | Trace the data: log the value at each stage boundary and find the FIRST stage where it is already wrong | Boundary suspects: encoding/CRLF, timezone/DST, locale, off-by-one, integer overflow, float equality |
| **Crash / exception** | Capture the full stack trace and exact message — never a paraphrase or screenshot-crop | Identify the offending VALUE at the throw site (null? empty? out of range?) via log or debugger | Find where the bad value ORIGINATED — the throw site is the victim, not the culprit; walk callers upward |
| **Hang / timeout** | Get a stack dump of the stuck process (`py-spy dump --pid <pid>`, `jstack <pid>`, `dotnet-stack ps` + report; **brain-diagnostics-and-tooling**) | Check the classic causes at the stuck frame: lock ordering/deadlock, unawaited promise/future, blocking I/O with no timeout | Binary-search the hang: add progress logs at midpoints of the suspected span and rerun — halve until cornered |
| **Empty / contradictory logs** | Fix the evidence path BEFORE theorizing: verify log level, output stream/redirection, capture boundary, clock and timezone | Push a known-good event through the same route and confirm it appears where you are looking | Never conclude "no bug" from missing evidence — absent logs are an observability-layer failure (layer table, step 3), a bug in its own right |

## Fenced traps

Named so you can catch yourself mid-mistake. Each costs real time; the "do
instead" is always cheaper.

| Trap | Why it costs time | Do instead |
|---|---|---|
| **Shotgun debugging** (edit-and-rerun without a hypothesis) | Each blind edit adds a variable; after 3 edits you're debugging your edits, not the bug. Even a "lucky" fix teaches nothing and often masks the cause | Stop. Write down observations (loop step 2), then a mechanism sentence (step 4). No edit without a prediction of what it will change |
| **Fixing the symptom, not the cause** (e.g. adding a null check where it crashed) | The bad value still flows; it resurfaces elsewhere next week with a worse stack trace | Trace the value to its origin; fix where it FIRST becomes wrong. The null check may still be good defense — but it is not the fix |
| **Changing two variables at once** | When it starts working you don't know which change mattered; when it doesn't, you've doubled the search space | One change per run. If you already changed two, revert one and rerun |
| **Stale caches — ignored, or ritually deleted** | Ignored: an hour debugging code that isn't even running. Ritually deleted: destroys the evidence of WHAT was stale and can manufacture a pass with no cause found | When behavior defies the source you're reading, suspect caches — but inspect identity first (artifact timestamps/hashes, cache keys) and prefer a documented non-destructive bypass. To delete: `git clean -ndx` preview → targeted deletion of listed build dirs, `git clean -fdx` only with human approval (stop-and-ask, **brain-change-control** §4); tool caches via `npm ci`, `pip install --force-reinstall`, framework cache dirs |
| **Assuming the most recent change is the culprit** | Plausible-looking recent diffs anchor you; the real break may be 30 commits back, latent until now | Suspect recency as a HYPOTHESIS (test with `git stash` / revert), but if it fails, bisect (below) instead of code-staring |
| **Trusting the error message's reported location** | Line numbers lie after transpilation/minification, in generated code, with async stacks, macros, and off-by-one template errors; the true fault is often in the caller or the data | Treat the location as where the problem was DETECTED, not caused. Verify with a log line or breakpoint at that site before believing it |
| **Trusting names over behavior** | Names drift from what code does: `test_auth_timeout` may assert nothing about timeouts; `ensureCacheFresh()` may not | Read the invocation, setup, assertion, and implementation before reasoning from a name |
| **Comparing unlike runs** | Differences you "find" are artifacts of differing revision, input, environment, or ordering — false leads that eat hours | Freeze revision, input, environment, and protocol before comparing; a comparison is evidence only when exactly one variable differs |
| **Debugging the wrong environment** | Hours reproducing locally what only fails in CI/prod because the delta (env var, version, data, OS) IS the bug | First confirm your environment actually exhibits the bug. If not, the environment diff is your hypothesis space — enumerate it (works-on-my-machine and local-pass/CI-fail rows above) |
| **"One passing run means fixed"** | Absence of failure is not evidence of absence — especially for flaky, timing, and load-dependent bugs | Re-run at the scale of the measured failure rate (flaky-test row), and meet ALL the exit criteria below before claiming fixed |

## Bisection recipes

Bisection converts "I don't know where" into O(log n) experiments. Three
axes: history, data, config.

### Git bisect (history)

Verified end-to-end on this machine 2026-07-09 (synthetic 8-commit repo; found
the planted bad commit in 3 automated steps).

Manual walkthrough:

```sh
git bisect start
git bisect bad HEAD              # current state is broken
git bisect good <sha-or-tag>     # a ref you have VERIFIED works — verify, don't assume
# git checks out the midpoint. Build + run your repro command, then:
git bisect good                  # if it passed
git bisect bad                   # if it failed
git bisect skip                  # if it won't build for unrelated reasons
# repeat until: "<sha> is the first bad commit"
git bisect log                   # record the session for the report
git bisect reset                 # ALWAYS reset when done — returns to original HEAD
```

Automated with `git bisect run` — git runs your command at every midpoint and
uses its exit code: **0 = good, 125 = skip (can't test), any other 1–127 =
bad**:

```sh
git bisect start HEAD <good-sha>
git bisect run sh -c 'npm test -- --run login.spec.ts'   # works from Git Bash on Windows too (verified)
git bisect reset
```

Notes:
- The repro command must be self-contained (include the build if needed):
  `git bisect run sh -c 'npm ci --silent && npx vitest run x.spec.ts'`.
- Bisecting a perf regression: make the command a threshold check, e.g.
  `sh -c 'timeout 30 ./bench.sh'` (exit non-zero when too slow).
- Uncommitted changes block checkout — `git stash` first.

### Data bisection (halve the input)

When a large input triggers the bug, binary-search the input, not the code:

```sh
# POSIX — first half / second half of a line-oriented file
head -n 5000 big-input.csv > half.csv
tail -n +5001 big-input.csv > other-half.csv
```

```powershell
# PowerShell
Get-Content big-input.csv -TotalCount 5000 | Set-Content half.csv -Encoding utf8
Get-Content big-input.csv | Select-Object -Skip 5000 | Set-Content other-half.csv -Encoding utf8
```

Run the repro on each half; recurse into the failing half until one record
remains. If BOTH halves pass, the bug is an interaction (size, ordering, or a
boundary between records) — that is itself a discriminating observation.

### Config bisection (halve the flags)

When behavior differs between a working and a broken configuration (feature
flags, compiler options, settings files): diff the two configs, then apply
half the differing entries to the working config and retest. Recurse into
whichever half flips the behavior. Same log-n logic; the "input" is the set of
config deltas. Works for CLI flags too: run with half the flags removed.

## Minimal-repro construction

**Why:** a minimal repro shrinks the hypothesis space to what remains, makes
every experiment iteration seconds instead of minutes, is the seed of the
regression test (exit criteria below), and is the only acceptable format for
escalating to a library maintainer or teammate.

**How:**
1. Start from the deterministic repro (loop step 1).
2. Delete the largest thing you suspect is irrelevant (a module, a config
   block, half the input — data bisection applies). Rerun.
3. Bug still there → keep the deletion. Gone → restore it; that piece is
   load-bearing and now a prime suspect.
4. Stop when every remaining element is necessary: removing anything makes the
   bug vanish. Often this fits in one file.
5. For library/framework bugs, invert: start from a blank scratch project and
   ADD suspect pieces until the bug appears.

**When to instrument instead of read:** if you have read code for ~15 minutes
without producing a testable hypothesis, stop reading and make the program
tell you what it's doing — targeted log lines at stage boundaries, assertions
of what you believe must hold, or a debugger at the detection site. Reading
tells you what code SHOULD do; instrumentation tells you what it DID.
Technique catalog and tooling (structured logging, profilers, dump analysis)
live in **brain-diagnostics-and-tooling**.

## Exit criteria — when is a bug actually fixed?

A bug is fixed only when ALL of these hold:

1. **Root-cause sentence.** You can state the mechanism in one sentence:
   "The crash happened because X did Y under condition Z." — "it works now
   after I changed X" does not qualify; that is a correlation, not a cause.
2. **The fix explains every original observation** from loop step 2, including
   the weird ones and the negative evidence (cases that DIDN'T fail).
   Unexplained observations mean a second bug or a wrong diagnosis.
3. **A regression test exists** — usually the minimal repro promoted into the
   suite — and it fails without the fix, passes with it. If a test is
   genuinely impossible (e.g. requires vendor hardware), document why and what
   manual check replaces it, in the fix's commit/PR.
4. **Executed proof** of the fix and of no new failures, cited per
   **brain-validation-and-qa** — one passing run is not proof for a bug that
   failed intermittently (re-run at the measured rate's scale).

If you cannot meet 1, you have suppressed a symptom, not fixed a bug — say so
explicitly in your report rather than claiming a fix.

## When NOT to use this skill

- **Hard multi-day unknowns** — the bug resists a day of disciplined looping,
  spans systems, or has no reliable repro at all: escalate to
  **brain-campaign-playbook** (decision-gated campaign structure). The
  three-strikes rule (loop step 5) is the in-session tripwire for this.
- **Building the diagnostic tooling itself** (log pipelines, profilers,
  measurement scripts): **brain-diagnostics-and-tooling**.
- **Proving a fix / evidence format**: **brain-validation-and-qa**; deeper
  first-principles proof methods: **brain-proof-and-analysis**.
- **You don't understand the codebase yet**: run the onboarding protocol in
  **brain-codebase-discovery** first — debugging unfamiliar code without a map
  wastes the loop on geography.
- **The "bug" is an environment/setup failure** (can't install, can't build
  from scratch): **brain-build-and-env**.

## Provenance and maintenance

- Authored 2026-07-09 on Windows 11 (PowerShell 5.1 + Git Bash, git 2.x);
  revised 2026-07-10 (review pass: `git clean -fdx` routed through the
  stop-and-ask gate in **brain-change-control**).
- Merged with the Sol library 2026-07-10. Absorbed from Sol: the failure-layer
  classification table (loop step 3), the hypothesis ledger (step 4), the
  diagnosis-vs-fix authority boundary (top of skill), the three-strikes
  escalation rule (step 5), triage rows for local-pass/CI-fail,
  failure-after-upgrade, and empty/contradictory logs, and the traps for
  ritual cache deletion, trusting names, comparing unlike runs, and
  one-passing-run. The absorbed content is command-free doctrine (tables and
  rules); the merge added no new shell commands.
- Verified on the authoring machine 2026-07-09: full `git bisect` manual and
  `git bisect run sh -c '...'` walkthroughs (synthetic repo, planted bug
  found); `git clean -ndx`; `git log --oneline -- <path>`;
  `Measure-Command { ... }`; `Get-Content -TotalCount/-Tail`;
  POSIX `head`/`tail`/`time`.
- NOT executed here (standard documented usage; re-verify in the target repo):
  test-runner invocations (`vitest`, `pytest`), stack-dump tools (`py-spy`,
  `jstack`, `dotnet-stack`), `timeout`, `npm ci`, `curl.exe`.
- What may drift: test-runner CLI flags per project; stack-dump tool names per
  runtime; git bisect exit-code contract is stable but re-check
  `git bisect --help` if git major version changes.
- One-line re-verification: `git bisect start && git bisect reset` (no-op
  round-trip) and run any triage-table command against the target repo before
  relying on it.
