---
name: brain-proof-and-analysis
description: >-
  First-principles proof methods for correctness claims: invariant
  identification and checking, differential testing (old vs new implementation),
  boundary enumeration, prediction-first estimation, complexity analysis before
  optimizing, failure-mode enumeration, and counterexample construction for
  refuting universal claims. Load this skill when a change must
  be argued correct rather than merely shown to run once — e.g. rewriting or
  optimizing existing logic, migrating data, changing algorithms, touching
  money/auth/concurrency/persistence, or whenever "it worked when I tried it"
  is not enough. Also load it when asked to prove, verify rigorously, analyze
  performance before optimizing, or state residual risk honestly. For routine
  run-it-and-cite-output verification use brain-validation-and-qa instead; for
  experiments on open questions use brain-research-methodology.
---

# brain-proof-and-analysis — from demonstration to proof

## The distinction this skill exists for

- **Demonstration**: "I ran it once and the output looked right." One input, one
  run, eyeball check. This is the floor, not the ceiling. `brain-validation-and-qa`
  owns how to run things and cite output as evidence.
- **Proof**: "It must behave correctly, and here is the argument plus the
  evidence." A proof has two parts: a *reasoning step* (why the code cannot be
  wrong in the ways that matter) and an *evidence step* (a check, executed, whose
  output confirms the reasoning). This skill owns the reasoning layer.

A demonstration answers "did it work?" A proof answers "under what conditions
does it work, and how do I know?" The four non-negotiables (home:
`brain-change-control`) require executed proof for any "done" claim; this skill
tells you how to construct one when a single passing run is not a sufficient
argument.

**Escalate from demonstration to proof when any of these hold:**

| Signal | Why demonstration fails |
|---|---|
| Replacing/rewriting existing behavior | The old behavior is the spec; one run can't show equivalence |
| Data migration or backfill | Errors are silent and permanent |
| Money, auth, permissions, deletion | Cost of a miss is asymmetric |
| Concurrency, caching, time zones, unicode | Bugs hide outside the happy path by construction |
| Performance work | "Feels faster" is not a measurement |
| The input space is large | One input samples ~0% of it |

## Method recipes

Each recipe: when to use → steps → what counts as success. Examples are
**illustrative** — drawn from three stacks (TypeScript/React, backend/SQL,
data/ML/Python) and not from any real project. Adapt names and paths.

### 1. Invariant identification and checking

**Jargon**: an *invariant* is a property that must hold for every row, every
state, every time — not just the case you tested.

**When**: any change that writes data, transforms records, or maintains derived
state (totals, counters, denormalized columns, caches).

**Steps**
1. Write down, in one sentence each, what must ALWAYS be true after your change.
   ("Every order total equals the sum of its line items." "No user has two
   active sessions." "Output row count equals input row count.")
2. For each invariant, write an executable check — an assertion, a query, or a
   script — that scans *real data*, not a hand-picked example.
3. Run the check before your change (baseline: does the invariant already hold?)
   and after. A pre-existing violation is a finding to report, not yours to fix
   silently (see `brain-minimal-change`).
4. Cite the check command and its output in your done-report
   (format: `brain-validation-and-qa`).

**Success** = each invariant stated in writing, each check executed over the
full relevant dataset, zero unexplained violations.

**Worked example (illustrative, backend/SQL)** — after changing order-total
calculation logic, prove the derived column is consistent:

```sql
-- Invariant: orders.total always equals the sum of its line items.
-- Success = zero rows returned.
SELECT o.id, o.total, SUM(li.qty * li.unit_price) AS computed
FROM orders o JOIN line_items li ON li.order_id = o.id
GROUP BY o.id, o.total
HAVING o.total <> SUM(li.qty * li.unit_price);
```

Run against a realistic dataset, not an empty dev DB (re-verify syntax against
the target's SQL dialect). Equivalent in-process pattern, verified on the
authoring machine (Python):

```bash
python -c "
for line in open('data.txt', encoding='utf-8'):
    s = line.rstrip('\n')
    assert s == s.strip(), f'invariant violated: untrimmed value {s!r}'
print('OK: invariant held')
"
```

### 2. Differential testing

**When**: rewriting, optimizing, or refactoring an implementation whose current
behavior is the spec — parser rewrite, query optimization, algorithm swap,
library upgrade that "shouldn't change output."

**Steps**
1. Keep both implementations callable at once (old function renamed, old branch
   checked out in a second worktree, or old binary saved).
2. Build an input corpus: real production-like data plus the boundary list from
   recipe 3. Bigger is better; generation can be random if seeded/recorded.
3. Run both on the same inputs; capture outputs to files; diff.
4. **Any difference must be explained or the change is wrong.** "Explained"
   means: you can state why the new output is correct and the old was buggy (or
   the difference is out-of-contract, e.g. unordered result order), in writing,
   per difference class. Unexplained diff = stop, investigate.

**Success** = corpus size stated, diff empty OR every difference class listed
with its written explanation.

**Worked example (illustrative, data/ML/Python)** — verified pattern on the
authoring machine (2026-07-09):

```bash
python old_scorer.py < corpus.jsonl > old_out.txt
python new_scorer.py < corpus.jsonl > new_out.txt
diff old_out.txt new_out.txt && echo "IDENTICAL"   # POSIX / Git Bash
```

```powershell
Compare-Object (Get-Content old_out.txt) (Get-Content new_out.txt)  # empty output = identical
```

In-process variant (TypeScript-ish, runs under node) when both versions live in
one repo:

```bash
node -e "
const { scoreOld } = require('./old'); const { scoreNew } = require('./new');
const inputs = require('./corpus.json');
let diffs = 0;
for (const x of inputs) {
  const a = JSON.stringify(scoreOld(x)), b = JSON.stringify(scoreNew(x));
  if (a !== b) { diffs++; console.log('DIFF', JSON.stringify(x).slice(0,80), a, 'vs', b); }
}
console.log(diffs === 0 ? 'IDENTICAL on ' + inputs.length + ' inputs' : diffs + ' diffs — explain each or the change is wrong');
"
```

For floating-point outputs, diff with a stated tolerance and justify the
tolerance; do not silently round.

### 3. Boundary enumeration

**When**: before declaring test coverage adequate for any function that takes
external input — API handlers, parsers, form fields, batch jobs.

**Steps**
1. Enumerate edges *systematically* from this checklist before writing tests,
   so coverage is an argument, not a vibe:
   - **Cardinality**: empty (0 items), exactly one, two, typical, max allowed, max + 1.
   - **Value edges**: 0, -1, min/max of the numeric type, NaN/Infinity where floats exist.
   - **Absence**: null, undefined/None, missing key, empty string vs whitespace-only string.
   - **Text**: unicode beyond ASCII (accents, CJK, emoji/surrogate pairs, RTL), very long strings, leading/trailing whitespace, embedded newlines and quotes.
   - **Time**: DST transitions, leap day, epoch 0, far future, timezone-naive vs -aware.
   - **Concurrency/repetition**: same request twice (idempotency), two writers at once, retry after partial failure.
   - **Delivery/crash faults** (anything with messages, queues, or retries): message duplicated, dropped, delayed, or reordered; crash before the write vs after the write but before the ack; restart mid-operation; version skew between sender and receiver.
   - **Ordering**: already-sorted, reverse-sorted, all-equal inputs.
2. For each edge: mark *tested*, *impossible* (say why — e.g. schema enforces
   non-null), or *untested* (goes in the residual-risk statement below).
3. Write the tests for every *tested* row; run them; cite output.

**Success** = the table exists in your report and every row has one of the
three dispositions. "I tested edge cases" without the table is a demonstration.

**Worked example (illustrative, TypeScript/React)** — a `<TagInput>` component
that splits comma-separated tags: enumerate `""` (renders empty state, no
crash), `"a"`, `"a,"` (trailing comma → no empty tag), `",,"`, 1000 tags
(virtualization or documented limit), `"café,日本語,👍"` (no mojibake, grapheme-safe
truncation), paste with `\r\n`, double-submit of the same tag (dedupe or
documented duplicate policy). Eight rows, eight dispositions, then the tests.

### 4. Prediction-first estimation

**When**: before ANY measurement — latency, row count, file size, memory,
request rate. Also before reading a profiler or query plan.

**Steps**
1. Back-of-envelope the expected number BEFORE measuring, from first principles:
   data size × per-item cost, table rows ÷ selectivity, payload × round trips.
   Write the prediction down with its arithmetic.
2. Measure (techniques and shipped scripts: `brain-diagnostics-and-tooling`).
3. Compare. Within ~2–3× of prediction: your model of the system is probably
   right. Off by 10×+: **a surprise is a finding, not noise** — either your
   model is wrong (you misunderstand the system; stop and fix your model before
   changing code) or the system is wrong (bug found). Never shrug and move on.

**Success** = prediction with arithmetic written *before* the measurement, the
measurement cited, and the discrepancy either <3× or explicitly investigated.

**Worked example (illustrative, backend/API)** — "the endpoint returns 5,000
rows of ~200 bytes ≈ 1 MB JSON; at ~50 ms server time + ~100 ms transfer on a
local link, predict ~150–300 ms." Measured: 4.2 s. That 14–28× gap is the
finding — it turned out each row triggered a separate query (a classic N+1:
5,000 extra round trips × ~0.8 ms ≈ 4 s, which the revised model predicts).
The prediction is what made the bug visible; without it, 4.2 s "looks normal."

### 5. Complexity analysis before optimizing

**When**: any task described as "make it faster" or any change justified by
performance. Never optimize what you haven't characterized.

**Steps**
1. State the asymptotic story: what is the dominant term as input grows —
   O(n)? O(n log n)? O(n²)? — and *which n* (rows, users, DOM nodes)?
2. Estimate constant factors: per-item cost class (ns for in-memory arithmetic,
   µs for a function call chain or allocation, ms for disk/network/DB round
   trip). A "better" asymptotic with a 1000× constant loses at real n.
3. Confirm empirically with a scaling probe: measure at n, 2n, 4n. Time ratio
   ≈2 per doubling → linear; ≈4 → quadratic. This is prediction-first (recipe 4)
   applied to growth rate.
4. Only then decide: if the current complexity already suffices at the maximum
   realistic n (state that n!), the correct optimization is none — record that
   and stop (see `brain-minimal-change`).
5. After optimizing, rerun the same probe and the differential test (recipe 2)
   — faster-but-wrong is wrong.

**Success** = asymptotic claim + constant-factor class + probe output at ≥3
sizes, before and after, plus unchanged correctness evidence.

**Worked example (illustrative, data/ML/Python)** — scaling probe, verified on
the authoring machine (2026-07-09):

```bash
python - <<'EOF'
import timeit
f = lambda xs: sorted(xs)              # replace with the function under test
for n in (100_000, 200_000, 400_000):
    t = timeit.timeit(lambda: f(list(range(n, 0, -1))), number=5) / 5
    print(f"n={n:>7}  t={t*1000:8.2f} ms")
EOF
# observed: 3.38 / 7.43 / 15.77 ms — ratio ~2.1 per doubling => ~linear (n log n's
# log factor is invisible at this range), matching the O(n log n) prediction.
```

(PowerShell 5.1 has no heredoc to stdin like this; put the script in a file and
run `python .\probe.py`.)

### 6. Failure-mode enumeration

**When**: before declaring risky work done — deploys, migrations, anything
touching shared state — and when reviewing your own design. The prompt is:
**"what has to be true for this to break?"**

**Steps**
1. List the assumptions your change silently relies on. Force at least one per
   category: input shape ("upstream always sends UTF-8"), environment ("the env
   var is set in prod"), ordering/timing ("the cron finishes before midnight"),
   scale ("the table stays under 1M rows"), external behavior ("the API returns
   429, never 503, when throttling").
2. Classify each: **checked** (code enforces or test covers it), **fragile**
   (plausibly false, unenforced), **safe** (argue why in one line).
3. For each fragile assumption, do one of: add a check/guard (if in scope —
   `brain-minimal-change` decides), verify it against reality now (grep the
   config, query the table size, read the API docs), or carry it into the
   residual-risk statement.
4. Fragile assumptions that hurt at 3 a.m. deserve an assertion that fails
   loudly at startup, not a comment.

**Success** = the assumption list exists with per-item dispositions; zero
fragile assumptions left both unguarded and unreported.

**Worked example (illustrative, TypeScript/React)** — a checkout form change
assumes: (a) `prices` prop is non-empty — fragile, guard with an early-return
empty state; (b) currency is always USD — fragile, verified false by grepping
the API client (EUR exists) → bug found before ship; (c) React 18 batching
semantics — safe, pinned dependency; (d) network idempotency on retry — fragile
and out of scope → residual risk, reported.

### 7. Counterexample construction

**When**: a universal claim is on the table — "this state can never occur",
"the sort is stable", "retries are idempotent" — and the cheapest move is to
try to refute it before investing in a positive argument.

**Steps**
1. Negate the claim mechanically: "for all x, P(x)" falls to a single x with
   not-P(x). The witness must satisfy every stated precondition — a witness
   outside the declared domain refutes nothing.
2. Search boundaries first (recipe 3's checklist is the menu): empty,
   duplicate, equal-timestamp collision, clock discontinuity, cancellation,
   retry, concurrent interleaving, partial state.
3. Minimize the witness: delete operations, fields, actors, and timing
   constraints while the failure persists. A two-element counterexample gets
   fixed; a 400-line flaky trace gets ignored.
4. Turn the minimal witness into a permanent test before fixing anything.

**Success** = either a minimal, reproducible witness (one is enough — the
claim is dead), or the searched boundary list recorded as evidence the claim
survived its cheapest attacks (which is support, not proof — say so).

## When full proof isn't feasible

Often it isn't: no staging data, can't run the legacy system, combinatorial
input space, clock ran out. The failure mode to avoid is **overclaiming** —
letting "I verified X and Y" imply Z is also covered.

State residual risk explicitly, in this shape:

> **Verified**: <checks run, with commands and outputs>.
> **Not verified**: <specific gap — e.g. "behavior under concurrent writes",
> "unicode keys", "datasets over 1M rows">.
> **Why not**: <blocker — no test env / out of scope / time-boxed>.
> **Exposure if wrong**: <who or what breaks, and how loudly>.
> **Cheapest next check**: <the one command or test that would close the gap>.

Rules:
- Never write "should work" — write what was checked and what wasn't.
- A named, bounded risk accepted by the user is fine; an unnamed risk is a lie
  of omission. If exposure is high (money/auth/data-loss), the decision to
  accept it belongs to the user, not you — surface it and ask (escalation
  gating: `brain-change-control`).
- Partial proof beats none: even one invariant check over real data upgrades a
  demonstration.

## When NOT to use this skill

- **Routine verification** — "run the tests / build / lint and cite the output
  for a normal change": `brain-validation-and-qa`. This skill is the layer you
  add when a passing run isn't a sufficient argument.
- **Open-ended experiments on ideas** — "would approach A beat approach B?",
  hypothesis lifecycles, adopt/retire decisions: `brain-research-methodology`.
  Rough boundary: proving a *change* correct is here; testing a *hypothesis*
  about what to build is research.
- **Finding a bug you don't understand yet**: `brain-debugging-playbook` (its
  hypothesis loop reuses prediction-first thinking; the loop itself lives there).
- **Choosing measurement tools/scripts**: `brain-diagnostics-and-tooling` owns
  the how-to-measure; this skill owns what the measurement must prove.

## Provenance and maintenance

- Authored 2026-07-09 on Windows 11 (PowerShell 5.1 + Git Bash), Node v24.13.0,
  Python 3.13.5, GNU diffutils 3.12.
- Merged with the Sol library 2026-07-12: absorbed the delivery/crash-fault
  row in the boundary checklist (recipe 3) and recipe 7 (counterexample
  construction and witness minimization). Recipe 7 is method, not commands —
  nothing new to machine-verify.
- Verified on the authoring machine: the Python invariant-assert one-liner, the
  node differential-diff loop pattern, `diff a b` (exit 1 on difference) and
  `Compare-Object` (empty output on identical), and the `timeit` scaling probe
  with the quoted timings. Timings are machine-specific — expect different
  absolute numbers; only the ratios matter.
- NOT verified here (no live DB on the authoring machine): the SQL invariant
  query — standard SQL, but re-verify dialect (`<>` vs `!=`, `HAVING` on
  aggregates) against the target database before relying on it.
- What may drift: runtime versions and flag behavior; the boundary checklist
  (append new edge classes as they bite — coordinate with the LEARNINGS
  convention in `brain-failure-archaeology`); sibling skill names if the
  inventory in `.claude/skills/README.md` changes.
- Re-verification one-liners: `node --version && python --version && diff --version`
  (Git Bash) / `node --version; python --version` (PowerShell); rerun any code
  block above verbatim — each prints an explicit OK/IDENTICAL/timing line.
