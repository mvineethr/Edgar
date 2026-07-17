---
name: brain-research-methodology
description: >-
  Hypothesis-driven lifecycle for open questions: HUNCH → HYPOTHESIS (numeric
  prediction written BEFORE running anything) → isolated EXPERIMENT → ANALYSIS →
  adversarial refutation → ADOPTED via brain-change-control or RETIRED via
  brain-failure-archaeology. Load when evaluating "let's try library X", a
  performance idea, an architectural experiment, an ML/data experiment, or any
  better/faster/cheaper claim before committing to build it; when tempted to
  adopt a result from one good run; when an experiment has
  lingered undecided (zombie); or when writing success criteria for research
  work. Provides the state machine with exit criteria, the evidence bar
  (predict numbers first; one mechanism explains ALL observations; refutation
  pass with attack checklist), a self-deception catalog, hygiene rules, and
  the falsifiable milestone format. Verifying a normal change →
  brain-validation-and-qa; known problem → brain-campaign-playbook.
---

# brain-research-methodology — from hunch to accepted result

This skill is the discipline that turns "I bet X would be faster" into either
an adopted change or a documented dead end. It applies to performance ideas,
"let's try library/framework X", architectural experiments, ML/data
experiments, and any claim of improvement that has not yet earned the right to
touch product code. The core rule: **an idea is worthless until it predicts a
number, and a result is worthless until someone has tried to kill it.**

**Definitions used below**
- **Hunch**: an idea with no numeric prediction attached. Cheap, unlimited,
  fine to have — forbidden to act on directly.
- **Hypothesis**: a hunch upgraded with a written, numeric, falsifiable
  prediction and a proposed mechanism (the *why*).
- **Zombie experiment**: an experiment that ran but was never driven to
  ADOPTED or RETIRED — branch still open, conclusion never written. Zombies
  are debt: the next session re-tries the same idea blind or, worse, half
  remembers a "result" that was never validated.

## 1. The idea lifecycle — a state machine

Every idea is in exactly one state. Every idea terminates in exactly one of
two states: **ADOPTED** or **RETIRED**. There is no third ending.

```
HUNCH → HYPOTHESIS → EXPERIMENT → ANALYSIS → REFUTATION → ADOPTED
                          ↑            |          |
                          └── new hypothesis ─────┘        → RETIRED
```

| State | Entry requirement | Exit requirement |
|---|---|---|
| HUNCH | An idea exists | Written numeric prediction + mechanism → HYPOTHESIS, or discard (no record needed — hunches are free) |
| HYPOTHESIS | Prediction written BEFORE any experiment runs (see §2 rule 1) | Experiment designed: one variable, defined inputs, isolation plan → EXPERIMENT |
| EXPERIMENT | Isolated from product code (see below); hygiene rules of §4 | Raw outputs captured; runs complete → ANALYSIS |
| ANALYSIS | Raw data in hand | One mechanism explains ALL observations (§2 rule 2) → REFUTATION; or mechanism fails → back to HYPOTHESIS (a *new* one) or RETIRED |
| REFUTATION | A candidate result exists | Dedicated kill-pass (§2 rule 3) survived → ADOPTED path; any attack lands → back to ANALYSIS/HYPOTHESIS or RETIRED |
| ADOPTED | Refutation survived | Ships as a minimal diff through `brain-change-control` — research grants zero exemptions from the four non-negotiables |
| RETIRED | Any state can retire an idea | Written entry in the failure-chronicle format of `brain-failure-archaeology`: what was tried, the numbers observed, why it died — so it is not re-tried blindly |

**Isolation (EXPERIMENT entry requirement, non-negotiable):** experiments run
behind a feature flag, on a branch, or in a scratch directory — never
interleaved with product changes. An experiment mixed into a feature diff can
neither be cleanly measured nor cleanly reverted, and it smuggles unvalidated
code past change control. If the experiment needs product code modified,
branch first; if it only needs a harness, use a scratch dir and record its
path.

**No zombies:** before ending any session that ran an experiment, the idea
must be moved to a terminal state or its exact resume point logged (working-log
discipline: `brain-task-planning`). "We got some interesting numbers" with no
conclusion is a zombie. When you inherit one, treat its old numbers as hunch
fuel, not results — re-run before believing.

**RETIRED is a success outcome.** A documented dead idea with its numbers is
worth more than an undocumented "success": it fences a path forever (fence
mechanics: `brain-campaign-playbook`). Never let sunk cost push a dying idea
toward ADOPTED.

**Terminal states dispose of the experiment's scaffolding.** If the experiment
ran behind a feature flag or branch, ADOPTED means the flag/experiment-only
branches are removed (or given an explicit supported contract) and RETIRED
means the flag is removed and scratch state cleaned up — both through
`brain-change-control`. An experimental flag left enabled because results
"look good" is a zombie wearing production clothes.

## 2. The evidence bar — three hard rules

### Rule 1 — Predict the numbers before running

A hypothesis states specific numbers and a mechanism, in writing, before the
first experimental run:

> "I expect p95 latency to drop from ~800 ms to <300 ms because the N+1 query
> goes away — 5,000 extra round trips × ~0.1 ms each account for ~500 ms."

Not "it should be faster." The prediction names the metric (p95), the baseline
(~800 ms — measured, not remembered), the threshold (<300 ms), and the
mechanism whose arithmetic produces it. When no defensible point number
exists, predict an interval, a rank order, or at minimum a signed direction
with tolerance — and state why more precision is unavailable. "May improve"
is not a prediction. Prediction-first estimation technique:
`brain-proof-and-analysis`. Baseline and result measurement doctrine (N≥5
runs, warm vs cold, median over mean): `brain-diagnostics-and-tooling`.

**Corollary — surprises are hypotheses, not confirmations.** If the experiment
produces an unpredicted effect ("latency dropped AND memory halved — bonus!"),
the post-hoc explanation of the surprise is a NEW hypothesis at the top of the
state machine. It gets its own prediction and its own experiment. Explaining
data after seeing it is how every self-deception in §3 begins.

### Rule 2 — One mechanism must explain ALL observations

Including the negative and awkward ones. A result that explains 4 of 5 data
points is not 80% done; it is unfinished, because the 5th point is where the
real mechanism is hiding. Before leaving ANALYSIS, write the mechanism as one
sentence and check it against every observation you made — the speedup on
dataset A, the *absence* of speedup on dataset B, the memory blip on run 3.
For each observation: *explained*, or *investigated and attributed* (e.g. "run
3's blip reproduces with the change reverted — pre-existing, not ours"), or
the analysis is not done. "Probably noise" is banned — quantify the noise
instead (variance interpretation: `brain-diagnostics-and-tooling`).

### Rule 3 — Assigned adversarial refutation

Before an idea may leave REFUTATION for ADOPTED, run one dedicated pass —
ideally a second agent/session or a colleague, minimally yourself in an
explicitly adversarial sitting — whose ONLY job is to kill the result. Not to
"double-check": to destroy. The refuter works this checklist and must write a
one-line disposition per attack:

| # | Attack | What to do |
|---|---|---|
| 1 | Confound hunting | Did anything else change between baseline and result — dependency versions, data volume, machine load, time of day, a colleague's commit? Diff the environment records (§4). |
| 2 | Measurement error | Is the instrument measuring what the claim says? Timer around the wrong span, cache hit counted as compute, p95 computed over too few samples to be stable. Re-derive the metric from raw outputs. |
| 3 | Warm-cache effects | Was baseline cold and candidate warm (or vice versa)? Re-run both orderings; interleave runs A,B,A,B rather than AAAA,BBBB. |
| 4 | Cherry-picked inputs | Would the result hold on inputs that did NOT inspire the hypothesis? Run on at least one held-out input set (see §3 row 4). |
| 5 | Regression elsewhere | Faster here, slower/worse where? Check the metrics the hypothesis did NOT mention: memory, error rate, other endpoints, build time, bundle size. |
| 6 | Does it replicate fresh | Clean checkout, fresh shell/session, re-run from the recorded commands. A result that only reproduces in the original session's dirty state is not a result. |

Any attack that lands sends the idea back to ANALYSIS (if repairable) or
RETIRED (if fatal). A result nobody tried to kill is a rumor with a chart.

## 3. Self-deception catalog

Each row: how you fool yourself → the countermeasure. These are not
hypothetical; they are the default behavior of a motivated experimenter.

| # | Self-deception | What it looks like | Countermeasure |
|---|---|---|---|
| 1 | Cherry-picking the best run | "Best of 7 was 210 ms — under threshold!" | Decide the statistic (median of N≥5) before running; report ALL runs; the raw outputs in the scratch dir make selective quoting auditable |
| 2 | Moving the threshold after seeing data | Predicted <300 ms, got 340 ms, "well, <350 is still a big win" | The prediction was written down first (§2 rule 1); a miss is a miss — either the mechanism is wrong or incomplete. New threshold ⇒ new hypothesis, new run |
| 3 | Changing two things at once | Swapped the library AND enabled its cache; improvement attributed to whichever you prefer | One variable per experiment (§4); if you already changed two, run the two intermediate configurations before concluding anything |
| 4 | Testing on the data that inspired the hypothesis | The slow query that motivated the idea is the only benchmark input | Split inputs: the motivating case tunes, a held-out set decides. In ML this is train/test leakage; the same logic applies to benchmarks |
| 5 | Survivor-only analysis | "Median improved" — computed only over runs that finished; the candidate also doubled the timeout rate | Count and report failures/timeouts/errors as first-class results; a run that didn't finish is data, not an outlier to drop |
| 6 | "It's noisy" as an excuse | Inconvenient runs waved off as noise; convenient ones counted | Quantify the noise: report spread (min/median/max) across N runs of the UNCHANGED baseline first; only differences larger than that spread mean anything (`brain-diagnostics-and-tooling`) |
| 7 | Comparison fishing | Ran 6 metrics × 4 seeds × 3 slices, reported the one combination that moved | Declare ONE primary metric and comparison in the hypothesis; everything else is exploratory — a moved exploratory number is a new hunch, not a result. With enough comparisons, something always "wins" by chance |
| 8 | Scope shrinking after a miss | Failed on the full workload, so "it works — for small inputs", declared post hoc | The original claim is RETIRED as stated; the narrower claim is NEW research with its own written prediction. Never re-scope silently after seeing where it failed |

Shared root cause: deciding what the answer is, then arranging the evidence.
Every countermeasure is a version of "commit to the decision rule before you
see the data."

## 4. Experiment hygiene

1. **One variable at a time.** Each experimental arm differs from baseline in
   exactly one respect. Matrix of changes → run the matrix, not the diagonal.
2. **Fixed seeds and inputs where possible.** Pin randomness and input data so
   runs are comparable. Verified on the authoring machine (2026-07-10) — same
   output both invocations:

   ```bash
   python -c "import random; random.seed(42); print([random.randint(0,99) for _ in range(3)])"
   # [81, 14, 3] — identical on repeat
   ```

   For ML: also seed numpy/torch and record dataset versions/hashes. Where
   true fixing is impossible (network, prod traffic), raise N and report
   spread instead.
3. **Record the environment.** Versions, commit, machine, date — into the
   scratch dir, at experiment time, not from memory later. Verified on the
   authoring machine (2026-07-10); extend the list with whatever your stack
   adds (`npm ls <pkg>`, `pip show <pkg>`, GPU driver):

   ```sh
   # POSIX / Git Bash — run from the repo under test
   { date -u +%Y-%m-%dT%H:%M:%SZ; git rev-parse HEAD; git status --porcelain | head -5; \
     uname -sm; node --version; python --version; } > "$EXP_DIR/env.txt" 2>&1
   ```

   ```powershell
   # PowerShell 5.1
   & { Get-Date -Format o; git rev-parse HEAD; git status --porcelain | Select-Object -First 5;
       node --version; python --version } | Out-File "$expDir\env.txt" -Encoding utf8
   ```

   A non-empty `git status --porcelain` means the tree was dirty — record it;
   an experiment on uncommitted state is hard to replicate (refutation attack
   #6 will land).
4. **Keep the raw outputs, not just conclusions.** The scratch dir retains
   every run's output files, logs, and the exact commands used. Conclusions
   get re-examined; raw data cannot be regenerated after the environment
   moves on. Name the dir so it self-documents:
   `scratch/exp-<YYYY-MM-DD>-<slug>/`. Temporary instrumentation added to code
   follows the `DIAG:` marker protocol of `brain-diagnostics-and-tooling`,
   including its mandatory removal step.

## 5. Where good ideas come from

Hunches are free but not uniformly distributed. Rich hunting grounds, in
rough order of yield:

1. **Unexplained anomalies** — failure-chronicle entries with status=open
   (`brain-failure-archaeology`): someone already paid to observe something
   weird; the explanation is an experiment waiting to run.
2. **Measurements that surprised** — any prediction-vs-measurement gap ≥10×
   that got shelved ("a surprise is a finding": `brain-proof-and-analysis`).
3. **The gap between what CI enforces and what docs claim** — README says
   "sub-second responses", no test asserts it; docs promise idempotency, no
   test sends the request twice. Each gap is a free hypothesis: "the claim is
   false and nobody noticed."
4. **Boring numbers nobody has looked at** — bundle size, table row counts,
   cold-start time, cache hit rate, p99 of the second-most-used endpoint.
   Measure five of them; at least one will be indefensible.

## 6. The falsifiable milestone format

Research work is scoped by results, not effort. The milestone sentence:

> **"You have a result when** \<numeric observable\> **on** \<defined input\>
> **by** \<defined date\>."

Examples:
- "You have a result when median import time over 5 runs of the 2.1 GB
  reference dump is under 90 s, by Friday."
- "You have a result when the candidate ranker's offline NDCG@10 on the
  held-out eval set beats baseline by ≥0.02, by end of sprint."

**If you cannot write that sentence, the idea is still a hunch** — go back to
§1 and either upgrade it or discard it. The date matters: it is the zombie
guard. When the date arrives without the observable, the milestone forces a
decision — retire, or consciously re-scope with a new written milestone (once;
a milestone re-scoped twice is a zombie wearing a calendar). This is the same
declare-the-number-first discipline as a campaign MISSION
(`brain-campaign-playbook`), scaled down to a single idea.

## 7. When NOT to use this skill

| Situation | Use instead |
|---|---|
| Verifying a normal change works ("does my fix pass?") | `brain-validation-and-qa` — run it and cite output; no hypothesis lifecycle needed |
| Structured assault on a known problem (flaky CI, "make X 10× faster" with a target) | `brain-campaign-playbook` — a campaign ends in a promoted change; research ends in a decision |
| Proving a specific change correct (invariants, differential tests) | `brain-proof-and-analysis` — proving a *change* is proof; testing an *idea* is research |
| A bug you don't understand yet | `brain-debugging-playbook` — its loop borrows this skill's predict-first rule, but lives there |
| Choosing timers, profilers, run counts | `brain-diagnostics-and-tooling` owns how to measure; this skill owns what the measurement must decide |
| Shipping an adopted result | `brain-change-control` (gates) + `brain-minimal-change` (diff scope) |
| Writing the retirement entry or final report | `brain-failure-archaeology` (entry format) / `brain-docs-and-writing` (report style) |

Rough boundary with siblings: **debugging** restores intended behavior;
**campaigns** hit a declared target; **research** decides whether an idea is
true. Only research routinely ends well in "no".

## Provenance and maintenance

- Authored 2026-07-10 on Windows 11 (PowerShell 5.1 + Git Bash), Node
  v24.13.0, Python 3.13.5, git 2.x (Git for Windows).
- Merged with the Sol library 2026-07-12: absorbed the interval/rank-order
  prediction fallback (§2 rule 1), self-deception rows 7–8 (comparison
  fishing, scope shrinking), and flag/scaffolding disposition on terminal
  states (§1).
- Verified on the authoring machine 2026-07-10: the POSIX and PowerShell
  environment-record snippets (both produce the timestamp/versions file; in a
  repo with no commits `git rev-parse HEAD` errors — harmless, the error is
  captured) and the Python fixed-seed one-liner (identical output `[81, 14, 3]`
  across invocations on CPython 3.13.5; the exact numbers may differ across
  Python versions — only the repeatability matters).
- NOT verified here: nothing — the example latency/NDCG numbers in §2 and §6
  are invented illustrations, never data.
- What may drift: sibling skill names if `.claude/skills/README.md`'s
  inventory changes; the retirement-entry format owned by
  `brain-failure-archaeology` (this skill defers to it — if that skill's
  format changes, only the reference here needs checking); the refutation
  checklist (§2 rule 3) should grow a row whenever a new way a result fooled
  a session is discovered — coordinate with the LEARNINGS convention in
  `brain-failure-archaeology`.
- Re-verification one-liners: rerun the Python seed one-liner twice and
  compare; run either env-record snippet in the target repo and confirm the
  file contains a timestamp, a commit SHA, and tool versions.
