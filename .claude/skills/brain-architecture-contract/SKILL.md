---
name: brain-architecture-contract
description: >
  How to extract a repository's load-bearing design decisions, invariants, and
  known weak points into a contract document (docs/CONTRACT.md) — and keep it
  honest. Load when: asked to document a repo's architecture, invariants, or
  "rules of the system"; a deep audit or harness install needs the invariant
  layer written; you are about to simplify, delete, or "clean up" code that
  looks weird, redundant, or overcomplicated (Chesterton's fence protocol lives
  here); a change alters a recorded decision and the contract must be updated
  in the same change; or periodic contract re-verification is due. Provides
  precise definitions (load-bearing decision, invariant, known-weak-point),
  grep/git techniques for finding invariants in unfamiliar code, the contract
  template with mandatory per-invariant verification commands, and the honesty
  rules. Not for ADR formatting (brain-docs-and-writing), first-pass repo
  survey (brain-codebase-discovery), or proving a change correct
  (brain-proof-and-analysis).
---

# brain-architecture-contract

Every codebase has rules that are nowhere written down: the retry delay that
must stay above 500ms, the table that must never be written outside one
module, the double-check that looks redundant but guards a race. When those
rules live only in departed engineers' heads, every "cleanup" is Russian
roulette. This skill turns them into a **contract document** — a short file of
decisions and invariants that a zero-context engineer can read before touching
anything, with a verification command per invariant so the document can be
mechanically checked against reality.

The contract lives at `docs/CONTRACT.md` (or wherever the repo keeps its docs
of record — discovery of that location is **brain-docs-and-writing**'s
doc-of-record rule). The template ships in this skill's `templates/CONTRACT.md`.

## Definitions — use these words precisely

| Term | Definition | Test |
|---|---|---|
| **Load-bearing decision** | A design choice that other code silently depends on: changing it breaks things *far from the change site*, with no compile error or local test failure to warn you. | "If I changed this, would anything outside this file break without telling me?" Yes → load-bearing. |
| **Invariant** | A property of the system that must hold at all times, stated with the consequence of violating it. Not a preference, not a convention — a condition whose violation is a bug by definition. | Can you finish the sentence "if this is ever false, then ___" with a concrete failure (data corruption, double-charge, security hole)? If the blank is "it would be ugly", it's a style rule, not an invariant. |
| **Known-weak-point** | An acknowledged fragility the team has decided to live with, stated plainly: what it is, what triggers it, what breaks when it fires (blast radius). | It is written so a newcomer *avoids* it, not so the author looks careful. "Hand-rolled date parser breaks on non-Gregorian locales; triggered by any user with Thai locale; blast radius: their invoices render blank." |

Labeled examples across the three reference stacks:

- **TypeScript/React/Next**: decision — "all data fetching goes through
  `lib/api.ts`, never `fetch` in components" (load-bearing: the interceptor
  there attaches auth). Invariant — "no server-only import appears in a
  `"use client"` file; if violated, secrets bundle into the client JS."
- **Backend/API/SQL**: invariant — "`orders.total_cents >= 0`, enforced by a
  CHECK constraint; if violated, refund logic issues money." Decision —
  "idempotency keys are UNIQUE at the DB level, not checked in app code,
  because two app instances raced in 2024."
- **Data/ML/Python**: invariant — "training and serving share one feature
  transform in `features.py`; if they diverge, the model silently degrades
  (train/serve skew)." Weak point — "pipeline assumes input CSVs are UTF-8;
  a Latin-1 file doesn't fail, it produces mojibake feature values."

**A rule without a consequence is not an invariant.** Writing "must" without
"or else what" produces a document nobody trusts. And **an invariant without a
verification command is a hope, not an invariant** — every entry in the
contract carries a one-line command or test that checks it (see template).

## Finding invariants in an unfamiliar codebase

Four techniques, in the order of effort. Run these after (not instead of) a
**brain-codebase-discovery** survey — you need the map first. All commands
below were executed on the authoring machine (2026-07-10); tune the patterns
per stack and **verify your tuned pattern finds a known example before
trusting its silence**.

### Technique 1 — grep for enforcement

Existing enforcement code is the codebase confessing its invariants. Search
each enforcement layer:

```sh
# POSIX (Git Bash) — code-level guards: assertions, invariant comments, guard throws
rg -n "assert\(|invariant|must not|unreachable|panic!|precondition" --glob '!*test*' src/

# schema/DB constraints in migrations and SQL
rg -n -i "CHECK \(|UNIQUE|NOT NULL|FOREIGN KEY|ON DELETE" -g "*.sql" -g "*migration*"
```

```powershell
# PowerShell — git grep fallback (rg was NOT on the PowerShell PATH on the
# authoring machine; git grep works anywhere git does)
git grep -nE "assert\(|invariant|must not|unreachable" -- src
git grep -niE "CHECK \(|UNIQUE|NOT NULL|FOREIGN KEY|ON DELETE" -- "*.sql"
```

Per-stack pattern additions (starting points — verify against the repo):

| Stack | Add to the pattern | Enforcement it finds |
|---|---|---|
| TS/React/Next | `z\.object|\.parse\(|\.refine\(|invariant\(` | zod schemas, `tiny-invariant` calls |
| Backend/API/SQL | `@Valid|CONSTRAINT|TRIGGER|SERIALIZABLE|FOR UPDATE` | bean validation, DB triggers, locking discipline |
| Data/ML/Python | `pydantic|BaseModel|raise ValueError|pa\.Check|great_expectations` | pydantic models, pandera/GE data checks |

For each hit, record: the property being enforced, *where* it's enforced
(app code, schema, both), and what the guard's failure message says the
consequence is. A property enforced in app code only — not in the schema — is
itself a finding (any other writer can violate it).

### Technique 2 — interrogate the weird code

Oddly complex or seemingly redundant code usually guards an invariant that
isn't stated anywhere else. Candidates: an unexplained `sleep` or magic
constant, a lock around a "simple" read, a double-check that "can't be
necessary", a hand-rolled version of a library function, a catch block that
swallows one specific error. (**brain-codebase-discovery** §2.6 tells you to
flag these during survey; this is where you run them down.)

The protocol — **before simplifying weird code, find out what breaks**:

```sh
# 1. Who wrote these exact lines, and when? (blame follows renames by default)
git blame -L 40,60 -- src/payments.ts

# 2. Read the commit that introduced them — the message and the rest of the diff
git show <sha-from-blame>

# 3. Full history of that line range (traces across renames)
git log -L 40,60:src/payments.ts --oneline

# 4. Every commit that ever added/removed this token, repo-wide (pickaxe)
git log -S "RETRY_DELAY_MS" --oneline

# 5. Whole-file history across renames
git log -p --follow -- src/payments.ts
```

All five run identically in Git Bash and PowerShell. Then search the failure
chronicle and `LEARNINGS.md` for the file/token (**brain-failure-archaeology**
owns that layer) — a past incident referencing the weird code is the strongest
evidence you'll get. What you learn becomes either a contract entry (it guards
something — write the invariant) or licensed simplification (it guards
nothing — but that's a change, gated by **brain-change-control**).

### Technique 3 — CI gates as revealed preferences

What CI refuses to merge is what the team *actually* enforces — regardless of
what the README claims. Locations and discovery commands are in
**brain-codebase-discovery** §2.3; from each config, extract the checks:

```sh
# POSIX — every enforced step in GitHub Actions / GitLab CI
rg -n "run:|script:" .github/workflows/ .gitlab-ci.yml 2>/dev/null
```

```powershell
# PowerShell
Get-ChildItem .github\workflows -Filter *.yml | Select-String -Pattern "run:|script:"
```

Classify each gate: type checks, tests, lint rules, schema-drift checks,
bundle-size budgets, license scans. A *custom* CI step (a bespoke script, not
a stock linter) is almost always a hand-built invariant check — read the
script and write down what property it protects. Also note the inverse:
invariants people *talk* about that CI does not check are candidates for the
weak-points register.

### Technique 4 — data-flow tracing

Invariants cluster at trust boundaries. Trace one representative request or
job end-to-end and mark three points:

1. **Entrypoints** — where outside data enters (HTTP handlers, queue
   consumers, CLI args, file readers). Find them via the entrypoint discovery
   in **brain-run-and-operate**.
2. **Trust boundaries** — the exact line where unvalidated input becomes
   trusted (after a zod/pydantic parse, after auth middleware, after an
   allowlist check). Everything downstream *assumes* the boundary held: that
   assumption is an invariant. If you cannot find the boundary, the invariant
   is "callers validate" — which is a weak point, write it as one.
3. **Persistence** — what is assumed true of data being written (and
   therefore of all data already in the store). Schema constraints enforce
   some of it (technique 1); the rest is app-enforced and breaks the moment a
   migration script or admin console writes directly.

At each stage of the trace, also ask: what can *partially* succeed here, and
what retries, deduplicates, or compensates when it does? Invariants cluster at
partial-failure points ("the webhook may fire twice; the handler must be
idempotent") just as densely as at trust boundaries — and they are the ones
least likely to be written down.

One traced flow typically yields 3–5 contract entries; more flows hit
diminishing returns fast.

## Writing the contract

Copy `templates/CONTRACT.md` (in this skill's directory) to the repo's docs
location and fill it. Binding rules:

- **Every invariant gets a verification command** — a one-liner or single
  test invocation that exits 0 / prints an expected value when the invariant
  holds. Verified idioms:

  ```sh
  # POSIX — forbidden-pattern invariant: succeeds only when no match exists
  ! rg -q "console\.log" src/
  ```

  ```powershell
  # PowerShell — same check via git grep exit code
  git grep -qE "console\.log" -- src; if ($LASTEXITCODE -ne 0) { "OK" } else { "VIOLATION" }
  ```

  For data invariants, a query returning a violation count expected to be 0
  (`SELECT count(*) FROM orders WHERE total_cents < 0` — standard SQL, not
  machine-verified here); for behavioral ones, a single named test
  (single-test invocation recipes: **brain-validation-and-qa**). If you
  cannot write the check, either write the missing test first or file the
  entry under known-weak-points as "unverifiable" — do not list it as an
  invariant.
- **Run every verification command once before shipping the contract** and
  record the date. A contract whose checks were never executed violates
  non-negotiable #1 (**brain-change-control**).
- Decisions record *why* (the failure the decision prevents), not just
  *what*. "We use X" without the failure it prevents will be "cleaned up" by
  the next confident engineer. When the why cannot be recovered from evidence
  (no commit message, no ADR, author gone), write `rationale: unknown` rather
  than inventing a plausible one — a guessed rationale gets confidently
  "corrected" later. Where a measurable condition would justify revisiting a
  decision ("if p95 exceeds N ms", "if we outgrow one region"), record it as a
  one-line *revisit trigger* so the decision expires on evidence, not on mood. If the repo keeps ADRs, the contract entry is
  one paragraph linking to the ADR — the ADR *writing format* is owned by
  **brain-docs-and-writing** (`templates/ADR.md`); ADR *usage policy* lives
  here:
  - **When an ADR is required**: any Standard-or-above change (per the
    `brain-change-control` ladder) that alters a load-bearing decision, picks
    between competing architectures, or adds/removes a system dependency.
    Trivial and docs-only changes never need one.
  - **Numbering and storage**: sequential `NNNN-short-slug.md` in the repo's
    ADR directory (`docs/adr/` by default; use the existing convention if one
    exists).
  - **Supersession**: ADRs are immutable once accepted — changing your mind
    is a NEW ADR that names and supersedes the old one; the old ADR gets a
    "superseded by NNNN" header line and is never deleted.
- Weak points are worded plainly — "the importer loses rows on duplicate keys
  and does not report it" — never euphemized ("suboptimal handling of edge
  cases"). Each needs trigger conditions and blast radius, or it's an excuse,
  not a register entry.
- Keep it under ~2 pages. Ten entries people trust beat sixty they skim. If
  everything is load-bearing, nothing is.

## Keeping it honest

A stale contract is worse than none: none makes people investigate; a stale
one makes them confidently wrong.

- **Same-change rule**: any change that alters a recorded decision or
  invariant updates the contract *in the same commit/PR* — this is part of
  the change's gate (**brain-change-control**), same as tests. A PR that
  invalidates a contract entry without touching the contract is incomplete.
- **Periodic re-verification** (quarterly, or per the repo's cadence): run
  every invariant's verification command top to bottom; update the
  `last verified` date on each; any failure is triaged as either a real
  violation (a bug — **brain-debugging-playbook**) or a stale entry (update
  or delete it, via change control). The template's header carries the last
  full-verification date so staleness is visible at a glance.
- **Deletion is honest maintenance.** An entry whose "why" no longer applies
  gets removed, with the removal reasoned in the commit message — not left to
  rot because deleting documentation feels wrong.

## Chesterton's fence protocol

*Chesterton's fence*: don't remove a fence until you know why it was put up.
The operational checklist — mandatory before deleting or simplifying any code
you don't fully understand, and cheap enough to run every time:

1. [ ] State what the code appears to do, and why it looks removable.
2. [ ] Check the contract (`docs/CONTRACT.md`) and `LEARNINGS.md` / failure
   chronicle for the file, function, or constant. Hit → stop; you found the
   fence's purpose.
3. [ ] Run technique 2 above: `git blame -L` → `git show <sha>` →
   `git log -S "<token>" --oneline`. Read the introducing commit's message
   and full diff.
4. [ ] Search issues/PRs for the token or filename if the repo has them
   (`gh search issues "<token>" --repo <owner>/<repo>` — standard `gh` usage;
   not machine-verified on the authoring machine).
5. [ ] Write one sentence: "This fence was built because ___, and that reason
   no longer applies because ___." **Both blanks filled with evidence** (a
   commit, an incident entry, a test) — "the reason is probably obsolete" or
   "blame shows nothing interesting" fills neither blank.
6. [ ] If you cannot fill the blanks: leave the fence. Add it to the contract
   as a suspected invariant with what you did learn, so the next person
   starts further ahead. Absence of evidence for the fence's purpose is not
   evidence the fence is useless.
7. [ ] If you can fill the blanks: remove it as a normal gated change
   (**brain-change-control**), citing the evidence in the commit message, and
   update the contract in the same change if it had an entry.

## When NOT to use this skill

| Situation | Use instead |
|---|---|
| First pass over an unfamiliar repo (stack, entrypoints, conventions) | **brain-codebase-discovery** — the contract is written *after* its survey |
| Writing or formatting an ADR | **brain-docs-and-writing** (owns `templates/ADR.md`) |
| Proving a specific change preserves an invariant | **brain-proof-and-analysis** (invariant checking, differential tests) |
| Mining incident history / writing LEARNINGS entries | **brain-failure-archaeology** — this skill consumes that chronicle |
| Deciding whether a change may proceed at all | **brain-change-control** |
| Verifying a completed change before claiming done | **brain-validation-and-qa** |
| Generating the whole project-skill layer at install time | **brain-harness-bootstrap** (calls into this skill for the contract step) |

## Provenance and maintenance

- Merged with the Sol library 2026-07-12: absorbed the rationale-unknown
  honesty rule and per-decision revisit triggers ("Writing the contract"), and
  the partial-failure/compensation questions in technique 4.
- Revised 2026-07-10 (review pass: ADR usage policy — when required,
  numbering, supersession — homed here).
- Authored 2026-07-10 on Windows 11, git 2.52.0.windows.1, ripgrep 14.1.1,
  PowerShell 5.1 + Git Bash. Verified against a scratch repo on this machine:
  both enforcement greps (rg and git-grep forms), the CI-gate extraction
  (both forms), `git blame -L`, `git show`, `git log -L <range>:<file>`
  (traced across a rename), `git log -S`, `git log -p --follow`, and both
  forbidden-pattern exit-code idioms. Not machine-verified (standard
  documented usage, marked inline): the SQL violation-count query, the
  `gh search issues` example, the per-stack pattern additions table.
- May drift: rg/git-grep flag behavior, the per-stack enforcement patterns as
  validation libraries evolve (zod/pydantic/pandera), CI config conventions.
- Re-verify quickly in a target repo:
  `rg -n "assert\(|invariant" src/ | head -5` (or `git grep -nE
  "assert\(|invariant" -- src` in PowerShell) and
  `git log -S "someToken" --oneline | head -3` — each should return hits on a
  known example before you trust the technique's silence.
