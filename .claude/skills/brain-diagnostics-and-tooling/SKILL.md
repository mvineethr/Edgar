---
name: brain-diagnostics-and-tooling
description: >
  Measurement techniques and shipped, tested timing scripts for backing any
  quantitative claim with a number. Load whenever about to say "faster",
  "slower", "bigger", or "more reliable"; before/after any optimization; when
  comparing two implementations, configs, or runs; when timing a command
  (Measure-Command, time, hyperfine, the shipped timeit scripts), counting
  lines/matches/rows/bytes, diffing two runs' outputs, profiling CPU (node
  --cpu-prof, cProfile, devtools), or timing HTTP with curl -w. Also load
  before adding temporary print/log instrumentation (the DIAG: marker
  protocol and its mandatory removal). Provides the bounded
  diagnostic contract (decision, baseline+delta, budget), measurement
  doctrine (N>=5 runs, warm vs cold, median over mean, identity), validity
  checks before trusting a number, and an interpretation guide for honest
  comparison. Not for the debugging loop
  (brain-debugging-playbook), evidence format (brain-validation-and-qa), or
  pre-optimization analysis (brain-proof-and-analysis).
---

# brain-diagnostics-and-tooling

## Doctrine: measure, don't eyeball

Every claim of "faster", "slower", "bigger", or "more reliable" requires a
number, and every number requires a method: how many runs (N), warm or cold,
and how much the runs varied. "It feels snappier" is not evidence; neither is
one run of each version. A number without a method is an anecdote with digits.

**Before running anything, state the bounded diagnostic contract** — one
line each, written down before the first measurement:

1. **The decision this evidence must support.** "If X is confirmed we do Y,
   otherwise Z." A measurement with no decision attached is procrastination
   with digits.
2. **One baseline and one controlled delta.** Change exactly one variable
   between them; two simultaneous changes make the comparison unreadable.
3. **The cheapest tool that can disprove the leading hypothesis.** A line
   count or one timing run before a profiler; a profiler before a rewrite.
4. **A budget** — time, scope, and output size. When it is spent, report
   what you have and what you would measure next, instead of overrunning.

Minimum method for any timing claim:

1. **N ≥ 5 runs** per variant. One run measures your machine's mood, not the
   code. Five is the floor at which a median means something.
2. **Report the median, not the mean.** Timing noise is one-sided — GC pauses,
   antivirus scans, and disk cache misses only ever add time. One 500 ms
   stall in five 100 ms runs drags the mean to 180 ms while the median stays
   honest at ~100 ms.
3. **State warm vs cold.** A *cold* run pays one-time costs (disk cache, JIT,
   connection setup, module import); a *warm* run doesn't. First run after
   boot or after a cache clear is cold; subsequent identical runs are warm.
   Measure whichever the user actually experiences — and never compare a cold
   run of A against a warm run of B. Use warmup runs (discarded) to force the
   warm state deliberately.
4. **Report the distribution, not a lone average.** Min/median/max, or at
   least "spread was X%". If the spread swamps the difference you're
   claiming, you have no claim (see Interpretation guide below).
5. **Record identity with every measurement.** Revision (commit SHA or
   artifact version), tool/runtime version, and workload (input size,
   dataset, flags). A number that can't be tied to what was measured can't
   be compared with anything later — and comparison is the whole point.

This skill is the home of measurement *technique*. What counts as acceptable
*evidence* in a report is defined in **brain-validation-and-qa**; deciding
*whether* to optimize at all (complexity analysis, prediction-first) is
**brain-proof-and-analysis**.

## Shipped timing scripts

Two dependency-free harnesses ship in `scripts/`. Both run a command N times
(default 5), print each run, and report min/median/mean/max in ms, with a
warning when spread exceeds 20% of the median. Both were executed and
verified on the authoring machine 2026-07-10.

### scripts/timeit.ps1 (PowerShell 5.1+)

```powershell
.\scripts\timeit.ps1 -Command "git status" -Runs 5
.\scripts\timeit.ps1 "npm run build" -Runs 3 -Warmup 1   # 1 discarded warmup run
```

Verified output (authoring machine, `-Command "Start-Sleep -Milliseconds 80" -Runs 5`):

```
run 1: 131.6 ms
run 2: 84.4 ms
run 3: 94.7 ms
run 4: 95.0 ms
run 5: 94.8 ms
command : Start-Sleep -Milliseconds 80
runs=5  min=84.4 ms  median=94.8 ms  mean=100.1 ms  max=131.6 ms
WARNING: spread (max-min) exceeds 20% of median - rerun with more runs or on a quieter machine before comparing.
```

Note how run 1 (cold) is 39% slower than the median and the mean is dragged
5 ms above the median — the doctrine's rules 2 and 3, visible in real output.

### scripts/timeit.sh (bash; Git Bash on Windows works)

```sh
./scripts/timeit.sh -n 5 'git status'
./scripts/timeit.sh -n 3 -w 1 'npm run build'    # -w = discarded warmup runs
```

Verified output (authoring machine, `-n 5 'sleep 0.08'`):

```
run 1: 241 ms
run 2: 220 ms
run 3: 202 ms
run 4: 202 ms
run 5: 224 ms
command : sleep 0.08
runs=5  min=202 ms  median=220.0 ms  mean=217.8 ms  max=241 ms
```

Caveats for both scripts:

- **Constant per-run overhead.** Each run spawns a shell (`bash -c` /
  `Invoke-Expression`). On the authoring machine that is ~140 ms per run in
  Git Bash on Windows (an 80 ms sleep measured ~220 ms). The overhead is
  constant, so A-vs-B comparisons remain valid, but absolute numbers for
  sub-100 ms commands are dominated by it — prefer commands that run ≥ a few
  hundred ms, or loop the operation inside the command.
- Command stdout is discarded so output rendering doesn't pollute the timing;
  a failing command aborts with a non-zero exit (verified: `timeit.sh -n 2
  'false'` exits 1).
- `timeit.sh` needs GNU `date` for ms resolution (present in Git Bash and
  Linux); on BSD/macOS `date` it degrades to 1 s resolution and says so.

## Timing by hand

When you don't want the script, one-liners:

```powershell
# PowerShell — wall-clock of anything, in ms
(Measure-Command { npm test }).TotalMilliseconds
```

```sh
# bash — real = wall clock; user/sys = CPU time split
time npm test
```

Run each ≥5 times yourself and take the median — the one-liners don't do it
for you; the shipped scripts do.

**hyperfine** is a purpose-built benchmark runner (auto warmup, statistics,
A/B comparison) — but check for it, don't assume it:

```powershell
Get-Command hyperfine            # PowerShell
```
```sh
command -v hyperfine             # POSIX
```

Not installed on the authoring machine, so its usage is standard documented
form — re-verify where you find it: `hyperfine --warmup 3 'cmd-a' 'cmd-b'`
compares two commands with 3 discarded warmups each.

## Counting

Numbers for "bigger/smaller/more" claims. All verified on the authoring
machine 2026-07-10 except where noted.

| What | POSIX | PowerShell |
|---|---|---|
| Matches of a pattern | `rg -c "pattern" file` (fallback: `grep -c "pattern" file`) | `(Select-String -Path file -Pattern "pattern").Count` |
| Lines in a file | `wc -l < file` | `(Get-Content file \| Measure-Object -Line).Lines` |
| File size (bytes) | `wc -c < file` | `(Get-Item file).Length` |
| Files matching a glob | `ls *.log \| wc -l` | `(Get-ChildItem *.log).Count` |
| DB row counts | `SELECT COUNT(*) FROM t;` via the project's SQL client (not machine-verifiable here) | same |

CSV row count = line count minus 1 for the header (and beware embedded
newlines in quoted fields — count with a real CSV parser if the number is
load-bearing). `rg` on this machine is the ripgrep bundled with the agent
tooling; plain machines may need `grep -c` instead.

## Diffing two runs

To claim "the output didn't change" (or to see exactly what did), never
eyeball two scrollbacks. Redirect both runs to files, then diff:

```sh
# POSIX / Git Bash — works OUTSIDE a git repo too (verified)
mycmd --old > run_a.txt 2>&1
mycmd --new > run_b.txt 2>&1
git diff --no-index run_a.txt run_b.txt    # exit 0 = identical, exit 1 = differs
```

```powershell
# PowerShell
mycmd --old | Out-File run_a.txt -Encoding utf8
mycmd --new | Out-File run_b.txt -Encoding utf8
Compare-Object (Get-Content run_a.txt) (Get-Content run_b.txt)
```

Two verified traps:

- **`Compare-Object` is case-insensitive by default** — it reported `b` and
  `B` as equal on this machine. Add `-CaseSensitive` when case matters. It
  also compares as unordered sets of lines, not positionally; `git diff
  --no-index` is the stricter tool.
- `git diff --no-index` exits 1 when files differ — in scripts, that is a
  signal, not an error.

## Profiling entrypoints (pointers, not tutorials)

Profile only after a measurement proves there is something to chase
(**brain-proof-and-analysis** covers deciding whether to optimize). One
standard entrypoint per stack:

- **Node (backend/API or build tooling):** `node --cpu-prof --cpu-prof-dir .
  app.js` writes a `CPU.*.cpuprofile` file on exit (verified here with
  `node -e`); open it in Chrome DevTools → Performance (or VS Code) to see
  the hot-function flame chart.
- **Python (data/ML):** `python -m cProfile -s cumtime script.py` prints
  every function with call counts, sorted by cumulative time (verified here).
  Read the top ~10 rows of `cumtime`; ignore the noise below. For long
  scripts, `-o out.prof` then `python -m pstats out.prof`.
- **Browser (TypeScript/React/Next):** DevTools → Performance tab → record →
  perform the slow user action → stop. Read the flame chart top-down; the
  Summary pane splits scripting vs rendering vs painting. Not
  machine-verifiable here — standard documented usage.

## HTTP timing

`curl -w` prints connection-phase timings after the request. Format string
verified on the authoring machine 2026-07-10:

```sh
# POSIX (PowerShell: use curl.exe — plain `curl` aliases Invoke-WebRequest)
curl -s -o /dev/null -w "dns=%{time_namelookup}s connect=%{time_connect}s tls=%{time_appconnect}s ttfb=%{time_starttransfer}s total=%{time_total}s http=%{http_code}\n" https://example.com
```

Verified output:

```
dns=0.039502s connect=0.054278s tls=0.095726s ttfb=0.130451s total=0.130541s http=200
```

Read it left to right: `ttfb - tls` ≈ server think time; `total - ttfb` ≈
body transfer. Run it ≥5 times like any other timing — DNS caching makes run
1 cold. For endpoint A-vs-B claims, wrap it in the shipped timeit scripts.

## Temporary instrumentation protocol

When you add print/log lines to see what code is doing (the *when* is defined
in **brain-debugging-playbook**, "when to instrument instead of read"):

1. **Prefix every temporary line with a unique marker** — `DIAG:` — in the
   message text: `console.log("DIAG: order total", total)`,
   `print(f"DIAG: rows={len(rows)}")`, `Write-Host "DIAG: retry $n"`.
2. **Find your markers** in output and in code at any time:
   `rg -n "DIAG:"` (PowerShell fallback: `Get-ChildItem -Recurse -File |
   Select-String "DIAG:"`).
3. **MANDATORY removal before done.** Instrumentation is scaffolding, not
   product; leaving it in violates minimal-diff discipline
   (**brain-minimal-change**). Remove every marked line, then verify:

   ```sh
   rg "DIAG:"        # must print NOTHING and exit 1 (verified: exit 1 on no match)
   ```

   Cite that empty result in your report per **brain-validation-and-qa**. If
   a log line proved so valuable it should stay, that is a scope decision:
   strip the `DIAG:` prefix, convert it to a proper log statement, and
   account for it as part of the diff — don't silently leave scaffolding.

A marker only works if it is unique — `rg "DIAG:"` must return zero matches
on the untouched codebase before you start (check once, first).

## Bisection

All bisection recipes — `git bisect` manual and automated (`git bisect run`
exit-code contract: 0 = good, 125 = skip, other 1–127 = bad), data bisection,
config bisection — live in **brain-debugging-playbook**. One addition it
doesn't cover: a session recorded with `git bisect log > bisect.log` can be
resumed after a `git bisect reset` (or a crash) with `git bisect replay
bisect.log` — standard documented usage, not executed here.

## Before you trust a number

A 30-second validity check on the measurement itself, before interpreting it:

- **Units** — ms vs s vs µs, bytes vs KiB; the classic 1000x embarrassment.
- **Clocks** — wall vs CPU time; two machines' timestamps aren't comparable
  unless you proved the clocks are aligned.
- **Sampling rate and dropped events** — a sampling profiler or a log
  pipeline that dropped events shows false absence, not absence.
- **Cache state** — warm vs cold (doctrine rule 3), plus OS file cache, DNS,
  connection pools, JIT.
- **Observer overhead** — profilers, verbose logging, and tracing slow down
  the thing they watch; if the overhead could rival the effect you're
  measuring, measure with and without instrumentation.

## Interpretation guide

Having numbers is not the same as having a conclusion.

- **Spread rule of thumb:** if `(max − min) > 20% of median`, the environment
  is too noisy for a fine-grained comparison — take more runs (N=10–20),
  close background hogs, or accept only coarse conclusions. The shipped
  scripts print a warning at exactly this threshold.
- **Comparing two medians honestly:** the claim "A is faster than B" needs
  the gap between medians to clearly exceed both spreads. Median A = 480 ms
  (spread 60) vs median B = 510 ms (spread 70) is *no detectable difference*
  — say that; do not call noise an improvement. A real gap gets quantified
  both ways, absolute and relative (480 → 510 ms = +30 ms ≈ +6%) — small
  absolute deltas can masquerade as impressive percentages and vice versa.
  Interleave the runs (A,B,A,B,...) if the machine's load is drifting over
  time.
- **Measure the user-visible operation, not a proxy.** The classic trap:
  micro-benchmark the function you optimized (2x faster!) while the
  end-to-end request is unchanged because that function was 3% of the total.
  Whenever possible, time the thing the user experiences — the full request,
  the full build, the full test suite — and only descend to micro-benchmarks
  to explain *why* the end-to-end number moved. Related trap: measuring with
  output rendering included (a console printing thousands of lines can cost
  more than the computation — the shipped scripts discard stdout for this
  reason; state it when it matters).
- **A one-sided miracle is a bug in the method.** If the new version is 40x
  faster, first suspect the measurement: did the work get cached, skipped,
  or deferred? Verify the fast run actually produced the same output
  (diff-two-runs, above) before celebrating.

## When NOT to use this skill

- **You're mid-bug-hunt deciding what to check next** — the
  reproduce/hypothesize/experiment loop and bisection recipes are
  **brain-debugging-playbook**; come here only for measurement mechanics.
- **You need to format or grade evidence for a report** — evidence hierarchy
  and proof-of-work format are **brain-validation-and-qa**.
- **You're deciding whether an optimization is worth doing or proving a
  rewrite correct** — complexity analysis, invariants, and differential
  testing are **brain-proof-and-analysis**.
- **You're running a structured experiment on an open question** (hypothesis
  → numbers → refutation) — lifecycle in **brain-research-methodology**;
  this skill supplies its instruments.
- **The thing you can't measure won't even run** — environment and build
  problems are **brain-build-and-env**.

## Provenance and maintenance

- Authored 2026-07-10 on Windows 11 (PowerShell 5.1.26100, Git Bash
  bash 5.2.37, GNU Awk 5.3.2, curl 8.x system build, node v24.13.0,
  Python 3.13.5, ripgrep 14.1.1 via agent tooling).
- Merged with the Sol library 2026-07-12: bounded diagnostic contract,
  doctrine rule 5 (measurement identity), and the before-you-trust-a-number
  checks — all doctrine/prose, no new commands; shipped scripts unchanged.
- Executed and verified here 2026-07-10: both shipped scripts (normal,
  warmup, and failure paths), `Measure-Command`, bash `time`, `rg -c`,
  `rg` exit-1-on-no-match, `Measure-Object -Line`, `Select-String .Count`,
  `(Get-Item).Length`, `git diff --no-index` (incl. exit 1), `Compare-Object`
  (incl. case-insensitivity trap), `python -m cProfile -s cumtime`,
  `node --cpu-prof`, the `curl -w` format string above.
- NOT executed here (standard documented usage; re-verify in the target
  repo): hyperfine (not installed — check before recommending), browser
  DevTools Performance tab, SQL `COUNT(*)`, `git bisect replay`,
  `python -m pstats`.
- What may drift: hyperfine CLI flags; node profiler flags across major
  versions (`node --help | grep cpu-prof`); the ~140 ms shell-spawn overhead
  figure is machine-specific — remeasure with `timeit.sh -n 5 'true'`.
- One-line re-verification: run both scripts against a sleep
  (`./scripts/timeit.sh -n 5 'sleep 0.2'` /
  `.\scripts\timeit.ps1 "Start-Sleep -Milliseconds 200"`) and confirm the
  medians land near 200 ms plus constant overhead.
