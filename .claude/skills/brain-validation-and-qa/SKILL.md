---
name: brain-validation-and-qa
description: >-
  Evidence hierarchy, the canonical evidence-state vocabulary
  (VERIFIED/DECLARED/INFERRED/CONFLICT/UNKNOWN), proof-of-work format, and
  per-artifact verification recipes. This skill is the HOME of the
  proof-of-work format that non-negotiable #1 ("no done without executed
  proof") requires, and of the evidence-state terms other skills reference.
  Load it BEFORE claiming anything is "done", "fixed", "works", "passes", or
  "faster"; before reporting task completion to a user; when labeling how
  well-evidenced a claim is; when deciding how to verify a CLI tool, HTTP API,
  web UI, database migration, data pipeline, or library change; when adding a
  test to an unfamiliar repo and needing single-test invocation commands
  (vitest/jest/pytest/go test); or when designing negative tests. Also load
  when tempted to write "it should work" — that phrase is banned as evidence.
  For arguing correctness beyond a passing run use brain-proof-and-analysis;
  for experiments on open questions use brain-research-methodology.
---

# brain-validation-and-qa — evidence, proof-of-work, and verification recipes

**Jargon**: *verification* = running the artifact and observing behavior;
*evidence* = the observed output of a command you actually executed. Reasoning
about code is analysis, not evidence.

## 1. Evidence hierarchy

Strongest to weakest. When you report status, state which level your evidence
reaches. Prefer the highest level you can afford; never report a claim at a
higher level than the evidence supports.

| Level | Evidence | What it proves |
|---|---|---|
| 1 | Executed regression test (automated, checked into the repo, run now) | The behavior is correct AND stays checked on every future run |
| 2 | Executed end-to-end manual scenario (real entrypoint, real inputs, observed output) | The whole path works today for the inputs tried |
| 3 | Executed unit test (run now, targeting the changed code) | The changed unit behaves as specified in isolation |
| 4 | Typecheck / lint / build pass | The code is well-formed; says nothing about behavior |
| 5 | Code reading ("I traced the logic") | You believe it; the machine has not confirmed it |
| 6 | Similarity ("the same pattern works elsewhere") | Weak analogy; the differences are exactly where bugs live |

**"It should work" is not evidence at any level.** Neither is "the diff is
small", "I've done this before", or "the tests probably cover it". If your best
evidence is level 5–6, say so explicitly and either upgrade it by executing
something, or hand the residual risk to the user in plain words.

A compile/build success (level 4) is the *entry ticket* to verification, not
verification. A change that builds but was never run is unverified.

### Evidence states — the canonical vocabulary (HOME)

Every claim you record or report carries exactly one of five states. This
table is the vocabulary's single home; other skills (`brain-docs-and-writing`,
reports, ledgers) reference it instead of redefining it. The narrative terms
are the words used in prose; the states label claims in tables and ledgers.

| State | Meaning | Narrative term in prose | Hierarchy level |
|---|---|---|---|
| VERIFIED | Executed here and the result observed | "verified" — cite the proof-of-work block | 1–3 |
| DECLARED | A project doc, config, or person asserts it; not executed here | quote the source ("the README states…"), never a bare "works" | n/a — a source, not a run |
| INFERRED | Deduced from indirect evidence (code reading, analogy) | "candidate" (specific, plausible, undemonstrated) or "speculation" (mechanism believed, never observed) | 5–6 |
| CONFLICT | Two sources disagree (doc vs code, test vs observed behavior) | state both sides; never pick one silently | — |
| UNKNOWN | No usable evidence either way | "unknown" — say so | — |

Rules: a claim enters at UNKNOWN and moves up only on evidence. DECLARED
becomes VERIFIED only by executing the thing here — a second document that
agrees is still DECLARED. Preserve CONFLICTs in reports rather than resolving
them by preference. Fail closed: when a required check cannot be run (missing
tool, env, fixture), the claim stays DECLARED/UNKNOWN — inability to run a
check is never a pass.

## 2. Proof-of-work format (HOME)

Non-negotiable #1 — "no done without executed proof" — is defined operationally
here (rationale and gating live in `brain-change-control`). Any statement
containing **"done", "fixed", "works", "passes", "faster"** (or equivalents:
"resolved", "complete", "verified", "green") MUST be accompanied by a
proof-of-work block:

```
CLAIM: <the specific statement being made>
COMMAND: <the exact command actually run, copy-pasteable>
OBSERVED OUTPUT: <quoted output, trimmed to the decisive lines>
INTERPRETATION: <why this output supports exactly this claim, and what it does NOT prove>
```

Rules:

- **COMMAND is what you ran, not what one could run.** If you didn't run it,
  there is no proof-of-work block and no completion claim.
- **OBSERVED OUTPUT is quoted, never paraphrased.** Trim to the lines that
  decide the claim (pass counts, status codes, row counts, timings). "Tests
  passed" without the runner's own summary line is a paraphrase.
- **Output must postdate the change.** A test run from before your last edit
  proves nothing about the current code. Re-run after the final edit.
- **INTERPRETATION states the limits.** One passing scenario proves that
  scenario, not the input space. If the claim needs more (rewrites, migrations,
  money/auth), escalate to `brain-proof-and-analysis`.
- One block per claim. "Everything works" is several claims; prove each or
  narrow the claim.
- **Name the exact suite and scope.** Never write "all tests pass" when a
  subset ran. "The 13 tests in `orders.test.ts` pass" is honest; "all tests
  pass" after a filtered run is not.

Filled example (backend/API stack, illustrative):

```
CLAIM: The 500 on GET /api/orders?status=archived is fixed.
COMMAND: npx vitest run -t "archived orders" src/routes/orders.test.ts
OBSERVED OUTPUT:
  Test Files  1 passed (1)
       Tests  1 passed | 12 skipped (13)
COMMAND: curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:3000/api/orders?status=archived"
OBSERVED OUTPUT:
  200
INTERPRETATION: The new regression test for the archived filter passes and the
live endpoint returns 200 where it previously returned 500. Evidence level 1 + 2
for this query; other status values were not re-tested.
```

## 3. Verification recipes by artifact type

Pick the recipe for what you changed. Commands verified on the authoring
machine 2026-07-10 unless marked "documented usage — re-verify in target repo".
Placeholders in `<angle brackets>`; example paths are illustrative.

### CLI tool

Run it with real arguments — the actual binary/entrypoint, not the unit around it.

```sh
# POSIX — run, then check exit code
./mytool convert --input sample.csv --output out.json
echo "exit=$?"
```
```powershell
# PowerShell — native exe exit code
.\mytool.exe convert --input sample.csv --output out.json
"exit=$LASTEXITCODE"
```

Verify: exit code 0, expected output file/stdout exists and spot-check its
content. Then one negative case (see §4).

### HTTP API

Assert status AND body — a 200 with an error payload is a failure.

```sh
# POSIX curl — status code only (verified: returns e.g. "200")
curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:3000/api/health"

# Status + body together
curl -s -w "\nHTTP %{http_code}\n" -X POST "http://localhost:3000/api/items" \
  -H "Content-Type: application/json" -d '{"name":"test-item"}'
```
```powershell
# PowerShell 5.1 (verified)
$r = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -UseBasicParsing
"status=$($r.StatusCode)"; $r.Content

# Parsed body assertion
$body = Invoke-RestMethod -Uri "http://localhost:3000/api/items" -Method Post `
  -ContentType "application/json" -Body '{"name":"test-item"}'
$body.name   # expect: test-item
```

PS 5.1 trap (verified): `Invoke-RestMethod`/`Invoke-WebRequest` THROW on 4xx/5xx.
For expected-failure checks: `try { ... } catch { [int]$_.Exception.Response.StatusCode }`.

### Web UI

"It compiles" and "the dev server starts" are level 4. Actually load the page:

1. Start the dev server; confirm the "ready" line in its log (how to find the
   entrypoint: `brain-run-and-operate`).
2. Open the changed route in a browser/preview tool. Confirm the changed
   element renders with the new behavior — click it, submit it, read its text.
3. Check the browser console for new errors/warnings and the network tab for
   failed requests on that page. A rendering page with a red console is not done.
4. Quote what you observed ("clicked Save, toast 'Saved' appeared, POST /api/save
   returned 200") in the proof-of-work block. Screenshots are supporting
   evidence; the observed behavior description is the claim's core.

### Database migration

Documented usage — re-verify commands against the target repo's migration tool.

1. **Up** on a disposable/dev database, never first on shared data:
   `npx prisma migrate dev` / `alembic upgrade head` / repo's own script.
   Running a migration against real/shared data is a stop-and-ask trigger —
   get human approval first (`brain-change-control` §4).
2. **Verify schema**, don't trust the tool's "success":
   ```sh
   psql "$DATABASE_URL" -c "\d orders"          # Postgres: table shape
   ```
   ```powershell
   psql $env:DATABASE_URL -c "\d orders"
   ```
   Confirm the new column/index/constraint exists with the intended type.
3. **Down if supported** (`alembic downgrade -1`), then up again — proves the
   migration is reversible and re-runnable. If down is unsupported, say so in
   INTERPRETATION as residual risk.
4. Run one query the application actually issues against the new schema.

### Data pipeline

1. **Row counts in vs out**: count source rows, run the pipeline, count output
   rows. The relationship (equal / filtered by known rule / exploded by join)
   must be explainable; an unexplained delta is a bug until explained.
   ```sh
   wc -l input.csv        # POSIX
   ```
   ```powershell
   (Get-Content input.csv | Measure-Object -Line).Lines
   ```
   In SQL: `SELECT count(*) FROM staging_orders;` before and after.
2. **Spot-check records**: pick 3–5 specific input records (include an edge
   case: nulls, unicode, extreme values), trace each to its output row, verify
   field-by-field. Random eyeballing of output alone misses dropped records.
3. For transformations replacing existing logic, differential-test old vs new —
   home: `brain-proof-and-analysis`.

### Library change

Run the library's own tests AND one consumer example — passing unit tests with
a broken public API is common.

```sh
npm test                       # or: pytest / go test ./...
node -e "const {parseDate} = require('./dist/index.js'); console.log(parseDate('2026-07-10'))"
```
```powershell
npm test
node -e "const {parseDate} = require('./dist/index.js'); console.log(parseDate('2026-07-10'))"
```

The consumer example must import through the package's public entrypoint (as a
user would), not deep-import the source file you edited.

## 4. Negative testing — verify it fails when it should

A fix that can't fail can't be trusted: if you only ever feed it happy-path
input, you have not tested the fix, you have re-tested the happy path. For
every artifact, run at least one case that MUST fail, and confirm it fails the
right way (clear error, correct status, non-zero exit — not a crash or silent
success):

| Case | Example check |
|---|---|
| Wrong input | `./mytool convert --input nope.csv` → non-zero exit + readable error, not a stack trace |
| Missing env var | POSIX: `env -u DATABASE_URL ./run.sh` — PowerShell: `$env:DATABASE_URL=$null; .\run.ps1` → startup refuses with a named-variable message |
| Unauthorized | `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/api/admin` (no token) → expect 401/403, NOT 200 or 500 |
| Bad payload | POST malformed JSON → 400 with validation detail |

If you wrote a regression test for a bug: check that the test fails on the
pre-fix code (stash the fix or revert the line) and passes after. A test that
passes both ways tests nothing.

Two ways failures get laundered into passes — both banned:

- **Retry-until-green.** A failure followed by a pass under the same
  conditions is a flake *suspicion*, not a pass. Preserve both outcomes and
  investigate (timing, test ordering, shared state, seeds, clock/timezone);
  never use a retry as proof.
- **Regenerating snapshots/goldens to make a diff go away.** An
  expected-output file may change only alongside an explained behavior
  change; re-recording it to silence a failure converts a bug into a blessed
  bug.

## 5. Adding a test to an unfamiliar repo

1. **Locate the harness.** Look for test dirs (`tests/`, `__tests__/`,
   `*_test.go`, `*.test.ts`, `test_*.py`) and config: `vitest.config.*` /
   `jest.config.*` / `pyproject.toml [tool.pytest]` or `pytest.ini` / `go.mod`.
   Check `package.json` `"scripts".test` for the blessed invocation — use the
   repo's own runner and flags, not your habit.
2. **Find the closest existing test and mirror it** — same directory, same
   naming convention, same fixtures/setup imports. Do not introduce a second
   test style into someone's repo.
3. **Run JUST your test first** (fast feedback; verified invocations):
   ```sh
   npx vitest run -t "adds numbers" src/math.test.ts        # vitest: -t filters by test name
   npx jest src/math.test.js -t "adds numbers"              # jest: path arg + -t name filter
   python -m pytest tests/test_math.py::test_add -q         # pytest: file::function node id
   python -m pytest -q -k "add" tests/test_math.py          # pytest: -k keyword expression
   go test -run 'TestAdd$' -v ./pkg/math/                   # go: -run anchored regexp
   ```
   All forms identical in PowerShell (quote the `-run` regexp: `go test -run 'TestAdd$' ...`).
4. **Then run the suite** (or at least the changed package's slice) to prove
   you broke nothing else, and quote both results in proof-of-work.

## 6. Acceptance thresholds: numeric, and stated BEFORE measuring

Any claim of "faster", "smaller", "more accurate", or "good enough" needs a
number chosen *before* you measure. Deciding the threshold after seeing the
result is rationalization, not acceptance testing.

- Bad: "made the query faster" / Good: "target: p95 < 200ms on the dev dataset;
  measured 143ms (was 890ms)".
- Bad: "output looks right" / Good: "target: 0 row-count delta vs old pipeline
  on the sample file; measured 0".
- Write the threshold down (task plan, PR description, or the CLAIM line)
  before running the measurement, then report measured-vs-target.

Distinguish a **requirement** (an authoritative pass/fail rule the project
set) from a **baseline** (the value you measured before changing anything).
With only a baseline, report comparison ("890ms → 143ms"), not compliance
("meets the target") — compliance needs a requirement someone with authority
actually set.

The prediction discipline — commit to an expected number, then compare — is
owned by `brain-research-methodology`; measurement technique (warm-ups,
repetitions, honest timers) is owned by `brain-diagnostics-and-tooling`.

## When NOT to use this skill

- **Arguing correctness beyond "it ran and passed"** — rewrites, migrations,
  algorithm changes, money/auth/concurrency: `brain-proof-and-analysis`.
- **Something already failed and you're diagnosing why**:
  `brain-debugging-playbook` (this skill proves fixes; that one finds them).
- **Deciding whether a change may ship at all** (classification, gates,
  stop-and-ask triggers): `brain-change-control`.
- **Open experimental questions** ("which approach is better?") with
  hypothesis/refutation lifecycle: `brain-research-methodology`.
- **Building measurement tooling itself** (profilers, timers, probes):
  `brain-diagnostics-and-tooling`.
- **Finding the entrypoint/dev-server to verify against**:
  `brain-run-and-operate`.

## Provenance and maintenance

- Authored 2026-07-10 on Windows 11 (PowerShell 5.1 + Git Bash); revised
  2026-07-10 (review pass: stop-and-ask gate added to the migration recipe).
- Merged with the Sol library 2026-07-10: this file became the home of the
  evidence-state vocabulary (VERIFIED / DECLARED / INFERRED / CONFLICT /
  UNKNOWN, mapped to verified/candidate/speculation/unknown); absorbed the
  failure-laundering guardrails (§4) and the requirement-vs-baseline
  distinction (§6). No new commands were added in the merge.
- Verified on the authoring machine 2026-07-10: vitest 4.x (`vitest run -t`),
  jest 30.x (`jest <path> -t`), pytest 8.x (`::` node ids and `-k`),
  go 1.25 (`go test -run`), curl 8.x `-w "%{http_code}"`, PS 5.1
  `Invoke-WebRequest`/`Invoke-RestMethod` including throw-on-4xx behavior.
- NOT verified here (documented usage — re-verify in the target repo): prisma /
  alembic / psql migration commands; any repo-specific test script.
- What may drift: test-runner CLI flags across major versions; PowerShell 7+
  changes (`Invoke-*` gains `-SkipHttpErrorCheck`, so the throw-on-4xx trap is
  PS 5.1-specific).
- Re-verification one-liners: `npx vitest run -t x --help >/dev/null` (flag
  exists), `npx jest --help | grep -- ' -t'`, `python -m pytest --version`,
  `go help testflag | grep -A2 -- '-run'`, and rerun any §3 recipe against the
  target repo before relying on it.
