---
name: brain-change-control
description: >-
  Load before making ANY change to a repository: code edits, config changes,
  dependency bumps, migrations, deletions, commits, pushes, or PRs. Defines the
  C0-C4 risk classification ladder (C0 Observe, C1 Isolated, C2 Behavioral,
  C3 High-impact, C4 Critical — old names Docs-only/Trivial/Standard/Risky/
  Forbidden kept as aliases), the per-class EVIDENCE FLOORS, and the
  doctrine-ledger step for discovering a target repo's own
  rules before applying universal defaults; is the HOME of the four
  non-negotiables (no "done" without executed proof, minimal diffs only, plan
  before code, never bypass safety rails) with full rationale; lists
  stop-and-ask action gates (destructive ops, deploys, secrets, outbound
  network access, migrations, force operations, mass deletions); gives the
  out-of-scope-work protocol and the commit/PR gating checklist. Also load
  when tempted to use --no-verify, --force, rm -rf, DROP TABLE, or to skip
  tests, or when a repo's rules, owners, or required evidence level are
  unknown.
---

# brain-change-control

Change control = deciding, BEFORE you edit anything, how dangerous a change is
and therefore how much proof, review, and rollback planning it must carry.
Discover the target repo's own rules first (§1.1), classify the change (§1.2),
then work to that class's gate and evidence floor (§1.3). When in doubt
between two classes, take the stricter one.

## 1. Classify the change

Classify every unit of work (a task, not each keystroke) before starting.
Definitions used throughout: **gate** = what must be true before you
commit/report done; **rollback plan** = the concrete command or action that
undoes the change if it's wrong; **blast radius** = the largest credible set
of files, systems, and people the change can affect; **doctrine** = a cited
rule specific to the target repo.

### 1.1 Discover local doctrine first (the doctrine ledger)

This skill ships universal defaults. A target repo may have stricter (or
merely different) rules of its own — discover them before applying defaults.
Precedence, top wins; **stricter always wins within a level**:

1. Platform, legal, and security constraints (system policy).
2. Explicit user instruction scoping this task.
3. Discovered repo doctrine (CONTRIBUTING, CODEOWNERS, CI gates, security
   policy, commit history).
4. This skill's universal defaults.

Never weaken a higher rule with a lower one. If two rules at the same level
conflict, stop and ask the user, citing both.

Discovery commands (verified — see Provenance):

POSIX / Git Bash:
```sh
git ls-files | grep -iE 'contributing|codeowners|security|readme'
grep -rniE 'must|never|required|forbidden|approval|rollback|migration|deploy' --include='*.md' .
git log --all -i -E --grep='revert|rollback|incident|hotfix' --oneline
```
PowerShell:
```powershell
Get-ChildItem -Recurse -Include *.md | Select-String -Pattern 'must|never|required|forbidden|approval|rollback|migration|deploy'
git log --all -i -E --grep='revert|rollback|incident|hotfix' --oneline
```

Also read the CI/release/migration config — the repo's *actual* gates live
there, not in prose. (Full onboarding protocol: `brain-codebase-discovery`;
discovered flag/config conventions: `brain-config-and-flags`.)

Record each discovered rule as one ledger row in your plan or report:

| Rule | Status | Source | Rationale |
|---|---|---|---|
| "Schema changes require a down-migration" | discovered doctrine | CONTRIBUTING.md, Migrations section | stated: 2024 data-loss incident |
| "Don't touch `payments/` in this task" | user instruction | task chat | not documented |
| "No force-push to shared branches" | universal default | this skill, NN4 | see §2 |

Statuses are exactly: `discovered doctrine`, `user instruction`,
`universal default`. Never infer an incident from a rule, and never promote
"common practice" into doctrine — if no rationale is stated, record
`not documented`.

### 1.2 The C0–C4 risk ladder

The alias column preserves this library's older class names; sibling skills
that say "Standard or Risky" mean C2 or C3.

| Class | Alias (old name) | Definition | Examples | Gate to pass | Rollback plan required |
|---|---|---|---|---|---|
| **C0 Observe** | — (read-only) | Read-only inspection; no persistent change to the repo or any system | Reading code, `git log`, grep, answering questions, `--dry-run` runs | Confirm the target is in scope and sensitive output (secrets, PII) is not echoed into logs or reports | None |
| **C1 Isolated** | Docs-only / Trivial | Human-readable text only, OR a single-file behavior-preserving change a reviewer verifies in <1 min | README wording, typo in a `.md` or a string literal, CHANGELOG entry, bump a log level, rename a local variable, add one test case | Docs: render/preview; confirm no non-doc files in `git status --short`; spellcheck names and commands you cite. Code: build/typecheck passes; the ONE relevant test or manual check executed and cited (`brain-validation-and-qa`) | `git revert <sha>` |
| **C2 Behavioral** | Standard | Multi-file feature or bug fix inside existing architecture; no schema, auth, payment, or public-API surface changes | Add an endpoint handler, fix an off-by-one, add a React component, bounded config change, refactor confined to files the task already touches | Written plan first (`brain-task-planning`); tests for changed behavior executed; full proof-of-work block (`brain-validation-and-qa`); diff reviewed hunk-by-hunk against the plan | Revert commit identified in the PR description; feature independently revertable (no tangled commits) |
| **C3 High-impact** | Risky | Touches data, money, auth/authz, public API contracts, schema, build/release pipeline, or is hard to reverse | DB migration, dependency major-version bump, changing CI config, altering auth middleware, changing a serialized format | Everything in C2, PLUS: state blast radius in writing; test the rollback path itself before shipping; get human review (do not self-merge); stage/canary where the project supports it (`brain-run-and-operate`) | Written, TESTED rollback: down-migration executed against a copy, or pinned-version restore, or documented restore-from-backup steps |
| **C4 Critical** | Forbidden without human approval | Irreversible, outward-facing, or destructive beyond the repo | Production deploy, sending email/notifications, publishing packages, deleting data, force-push, rotating or committing secrets, mass file deletion | STOP. Present the exact command, the blast radius, and the rollback (or "none exists") to a human. Proceed only on explicit approval of that exact action | Human decides; if no rollback exists, say so explicitly before asking |

Rules of use:
- A task containing one C3 sub-change is a C3 task. Classification is max(),
  not average().
- Unknown impact raises the class by one until resolved — investigate, then
  reclassify.
- Reclassify upward the moment scope grows ("just a bug fix" that turns out to
  need a schema change is now C3 — stop and re-plan).
- Never lower a class because the diff is small. A one-line migration is
  still C3.
- Never split a change into smaller pieces to dodge a gate. Splitting for
  reviewability is good; splitting to avoid review is routing around change
  control.

### 1.3 Evidence floors per class

The minimum evidence that must exist — executed, not predicted — before you
report done. The proof-of-work format itself is defined in
`brain-validation-and-qa`.

| Class | Evidence floor |
|---|---|
| C0 | Cited sources: which files/commands you read or ran and what they showed |
| C1 | Exact diff reviewed; applicable syntax/format/link check; the one targeted test or manual check executed |
| C2 | C1 + tests for changed behavior executed including at least one negative case; full proof-of-work block; rollback walkthrough (revert command identified, commits separable) |
| C3 | C2 + blast radius stated in writing; rollback TESTED (down-migration on a copy, pinned restore, or equivalent); human review of the diff before merge; baseline comparison where the change is measurable |
| C4 | C3 + approval of the exact command immediately before execution; recovery rehearsal; explicit abort threshold stated in advance ("if X happens, stop and roll back") |

**Solo + AI calibration.** In a solo project, "approver", "reviewer", and
"responsible owner" all mean **the human user in this chat**: present the
evidence and the exact action, and wait for a yes. Do not simulate review
boards, independent reviewers, sign-off chains, named monitors, or staged
promotion ceremony — that multi-team apparatus is deliberately dropped. What
is NOT dropped: the full C3/C4 rigor above for destructive operations,
deploys, secret handling, and data migrations, regardless of team size.

## 2. The four non-negotiables (this is their home)

Every skill in this library enforces these where relevant; the full statement
and rationale live here only. Each incident below is an **archetype** — a
composite of a well-known industry failure pattern, not an event from this
project's history (this harness has no host project).

### NN1 — No "done" without executed proof

**Rule.** Never claim a task is done, fixed, working, or passing unless you can
cite a command you actually ran in this session and the output you actually
observed. "It should work", "the logic is correct", and "tests would pass" are
not completion states.

**Why (mechanism).** Code review and reasoning verify *intent*, not *behavior*.
The failure this prevents is plausible-but-wrong code: the change reads
correctly, but an unimported symbol, a stale build, a wrong path, or an
untested branch makes it dead on arrival. Unexecuted "done" converts your
confidence into the user's debugging session — the cost doesn't disappear, it
moves to someone with less context than you have right now.

**Archetypal incident.** An engineer fixes a null-pointer bug, eyeballs the
diff, reports "fixed", and closes the ticket. The fix is in a code path behind
a feature flag that's off in every environment; the crash recurs in production
that night, and the on-call engineer spends three hours rediscovering context
the original engineer had for free. One `curl` against a local run would have
caught it in thirty seconds.

**When tempted, do this instead.** Run the smallest command that would fail if
you were wrong (the evidence hierarchy and proof-of-work format are in
`brain-validation-and-qa`). If you genuinely cannot execute (no env, no creds),
say exactly that: "implemented but NOT verified — blocked on X" is an honest
and acceptable status. "Done" is not.

### NN2 — Minimal diffs only

**Rule.** Touch only the files and lines the task requires. Do not reformat,
rename, restructure, "modernize", or fix unrelated issues in the same change —
propose them instead (see §3). Full diff discipline lives in
`brain-minimal-change`.

**Why (mechanism).** Every extra hunk multiplies review cost and dilutes the
signal: a reviewer facing 40 changed files skims all of them instead of
scrutinizing the 3 that matter, and the bug hides in the noise. Extra hunks
also destroy revertability — when the mixed change breaks something, reverting
it takes the wanted fix down with the drive-by cleanup, and `git bisect`
lands on a commit that did five things.

**Archetypal incident.** A two-line bug fix ships inside a PR that also
reformats the file and renames three helpers "while in there". A subtle
behavior change in one renamed helper breaks a caller in another module.
Bisect fingers the commit, but the commit does five things; the revert
reintroduces the original bug; untangling takes a day. The two-line version
would have been reviewed in minutes and reverted in seconds.

**When tempted, do this instead.** Record the cleanup as an out-of-scope
proposal (§3) and keep the diff at task scope. If the cleanup is genuinely a
*prerequisite* (you cannot make the fix without it), say so, and put it in its
own commit — or its own PR — ahead of the fix.

### NN3 — Plan before code (any multi-step work)

**Rule.** For any task needing more than one obvious edit, write the plan
before touching code: intended outcome, files to change, verification step,
and rollback. Plan format and decomposition method live in
`brain-task-planning`.

**Why (mechanism).** Without a written plan, discoveries made mid-task
silently mutate the goal — you start fixing a bug and end up refactoring the
module, because each next step looked locally reasonable. A written plan is
the fixed point you diff your behavior against; drift becomes visible instead
of ambient. It's also the only artifact that lets someone else (or you,
post-compaction) tell whether the work is on track.

**Archetypal incident.** Asked to add a field to an API response, an engineer
starts editing, notices the serializer is "messy", rewrites it, which breaks
two other endpoints, which leads to touching their tests… Four hours later the
original one-field task is still not done and the working tree has 23 modified
files no one asked for. A three-line plan ("edit schema X, edit serializer
line Y, run test Z") would have bounded the whole job at twenty minutes.

**When tempted, do this instead.** If the task feels too small to plan, prove
it: write the one-line plan ("edit file F, verify with command C"). If you
can't state it in one line, it wasn't too small to plan.

### NN4 — Never bypass safety rails

**Rule.** Never use `--no-verify`, never force-push (`--force`,
`--force-with-lease`) to shared branches, never skip/disable/delete failing
tests to get green, never bypass required reviews, never disable hooks, linters,
or CI checks to make a change land. A failing rail is information, not an
obstacle.

**Why (mechanism).** Rails encode past incidents — each hook, required check,
and branch protection exists because its absence once cost something. Bypassing
one substitutes your in-the-moment judgment (missing that history) for the
accumulated judgment of everyone who added the rail. Worse, bypasses are
invisible: a green build that skipped tests looks identical to a green build
that ran them, so the safety signal everyone downstream relies on is silently
counterfeit.

**Archetypal incident.** A pre-push hook keeps failing on a "flaky" test, so an
engineer pushes with `--no-verify` to make a deadline. The test wasn't flaky —
it was the only test covering a race in the session store, and the change had
made the race likelier. The bug ships, intermittent logouts follow for a week,
and because the build was green, nobody looks at that commit for days.

**When tempted, do this instead.** Treat the rail's failure as the task: fix
the test, satisfy the hook, or get the review. If the rail itself is genuinely
broken (e.g., hook fails on a machine-specific path), that's a C3 change to
the rail — fix it through change control with human approval, in its own
change, never inline with the work it blocked.

## 3. Out-of-scope work protocol

You WILL notice worthwhile work the task didn't ask for — dead code, missing
tests, confusing names, outdated docs. The protocol: **record it, propose it,
don't do it.** (Why not do it: NN2; the diff-scope mechanics are in
`brain-minimal-change`.)

1. **Record** in one line the moment you notice, so it doesn't leak into the
   diff and doesn't get lost. Use the repo's convention if one exists
   (issue tracker, `TODO.md`, LEARNINGS file — see `brain-failure-archaeology`);
   otherwise append to a `FOLLOWUPS.md` at the repo root:

   POSIX:
   ```sh
   printf '%s\n' "- [ ] 2026-07-09 candidate: extract duplicated retry logic (src/api/client.ts) — found during BUG-123" >> FOLLOWUPS.md
   ```
   PowerShell (note `-Encoding utf8`; PS 5.1 default is not UTF-8):
   ```powershell
   Add-Content -Encoding utf8 FOLLOWUPS.md "- [ ] 2026-07-09 candidate: extract duplicated retry logic (src/api/client.ts) - found during BUG-123"
   ```
   Format: date, `candidate:` label (per the no-oversell rule — it's unproven
   until scoped), what and where, what task surfaced it.

2. **Propose** at task end: list the candidates in your final report with a
   one-line cost/benefit each. The human decides which become tasks.

3. **If you already started it by accident**, evict it from the working tree
   before committing — `git stash push -m "out-of-scope: <what>"` for quick
   removal, or stage only the in-scope hunks. Never commit it mixed in.

Exception — do it now, without asking: the out-of-scope fix is required for
correctness of the in-scope change (e.g., the function you must call has a bug
that breaks your fix). Then it's in scope by definition; put it in its own
commit and say so in the report.

## 4. Stop-and-ask triggers

If an action matches a row below, STOP and ask a human first — even if it
technically fits the current task, and even if you're confident. Present: the
exact command, what it affects, and the rollback (or "irreversible").

| Trigger | Examples | Why you must ask |
|---|---|---|
| Destructive file/data operations | `rm -rf`, `Remove-Item -Recurse -Force`, `git clean -fdx`, `DROP TABLE`, `TRUNCATE`, `DELETE` without reviewed `WHERE` | Deletion has no undo outside backups you haven't verified exist; a wrong path or glob destroys work outside your mental model |
| Irreversible/outward-facing actions | Production deploy, publishing a package (npm/PyPI/crates), sending email or push notifications, posting to external APIs, creating public releases | Effects land on people and systems outside the repo; there is no `git revert` for an email or a version number burned on a public registry |
| Credentials & secrets | Reading, printing, committing, moving, or rotating API keys, tokens, `.env` contents, private keys | Exposure is instant and permanent (shell history, logs, git history all persist); rotation breaks every consumer you don't know about. Name the secret by identifier, never by value; test presence, don't print |
| Outbound network access & new dependencies | Installing a new package, calling an external API from a script or test, fetching remote resources mid-task | Data leaves the machine and supply-chain risk enters it. Ask with: exact destination, purpose, what data is sent, any credential used; for a dependency also source, version, license, and lockfile effect |
| Data migrations | Schema changes, backfills, anything running against a database with real data | Partial failure leaves data in a state neither old nor new code handles; "down" migrations often can't restore destroyed values |
| Force operations | `git push --force`/`--force-with-lease` to shared branches, `--hard` resets on work you didn't create, overwriting remote state | Rewrites history others have built on; their local state silently diverges and their work can be lost without any error shown to you |
| Mass changes | Codemods touching 50+ files, bulk renames, dependency lockfile regeneration beyond the one dep you bumped, mass deletions | Too large to review hunk-by-hunk, so errors ride in unreviewed; blast radius exceeds what any single test run proves safe |

These correspond to C4 in §1.2 (or promote a task into C3). "The user's
original request implies it" is not approval for the specific destructive
command — ask with the command in hand. And approval for one destructive
action never authorizes another: each C4 action gets its own yes.

Migration pattern — prefer **expand / migrate / contract**: (1) *expand* — add
the new structure alongside the old, compatible with both; (2) *migrate* —
move and verify the data (row counts, spot checks); (3) *contract* — remove
the old structure only after every consumer has moved. Keep new behavior
behind a default-off flag during the window (`brain-config-and-flags`). If no
rollback can exist, document a tested roll-forward instead and classify at
least C3.

## 5. Commit/PR gating checklist

Run this before every commit; the full list before every PR. Proof-of-work
format and evidence standards are defined in `brain-validation-and-qa` — cite
them, don't restate them. Commit-message and PR-description house style is in
`brain-docs-and-writing`.

Before committing:
- [ ] Change class stated (§1.2) and its gate and evidence floor (§1.3)
      actually passed — not "would pass".
- [ ] Repo doctrine consulted; any rule stricter than this skill's defaults
      followed and cited (§1.1).
- [ ] `git status --short` and `git diff` reviewed hunk-by-hunk: every hunk
      traces to the task; no stray files, debug prints, or drive-by edits (NN2).
- [ ] Verification executed and output observed (NN1); evidence captured in
      the proof-of-work format from `brain-validation-and-qa`.
- [ ] No secrets, tokens, or credentials in the diff
      (`git diff --staged | grep -iE 'api[_-]?key|secret|token|password'` as a
      cheap first pass — POSIX and Git-Bash-on-Windows).
- [ ] On a branch, not the default branch (`git rev-parse --abbrev-ref HEAD`).
- [ ] Hooks and checks ran and passed — not skipped (NN4).

Additionally before a PR:
- [ ] Description states: class, plan followed (or deviations), proof-of-work
      block, rollback plan (mandatory for C3+), and out-of-scope candidates
      recorded (§3).
- [ ] C3: rollback tested, blast radius stated, human review requested (the
      user in chat) — never self-merged.
- [ ] Commits are separable: each revertable without taking unrelated work
      with it.

## When NOT to use this skill

- **Deciding HOW to keep a diff small** → `brain-minimal-change` (this skill
  says *that* diffs must be minimal; that one says how).
- **Writing the plan itself** → `brain-task-planning`.
- **Choosing/formatting the verification evidence** → `brain-validation-and-qa`.
- **Flag mechanics, config precedence, guarded-rollout plumbing** →
  `brain-config-and-flags` (this skill says migrations and experiments must be
  guarded; that one says how).
- **Wording the commit/PR text** → `brain-docs-and-writing`.
- **Pure investigation with zero repo mutation** (reading code, answering
  questions) → `brain-codebase-discovery`; that work is C0 here, and change
  control proper starts when the working tree is about to change.
- **Long ambiguous campaigns needing decision gates beyond per-change gates**
  → `brain-campaign-playbook`.

## Provenance and maintenance

- Authored 2026-07-09/10 for the brain harness skill library (Fable);
  merged with the Sol library 2026-07-10. Absorbed from Sol's change-control:
  the C0–C4 ladder (old class names kept as aliases), per-class evidence
  floors, the doctrine ledger and precedence order, expand/migrate/contract,
  and the network-access and secret-handling gates — all recalibrated for a
  solo+AI workflow (approver = the human user in chat; multi-owner review
  chains and staged promotion ceremony dropped). All incidents in §2 remain
  labeled archetypes, not project history.
- Verified 2026-07-09 (Windows 11, Git Bash + PowerShell 5.1, throwaway repo):
  `git status --short`, `diff --stat`, `stash push -m`/`pop`,
  `revert --no-commit`/`--abort`, `rev-parse --abbrev-ref HEAD`,
  `checkout -b`, and both note-append forms.
- Verified 2026-07-11 (same machine, throwaway repo): both doctrine-discovery
  grep forms (`grep -rniE … --include='*.md'`, `Select-String`), the
  `git log --all -i -E --grep='revert|rollback|incident|hotfix' --oneline`
  alternation, and the `git ls-files | grep -iE …` doctrine-file filter.
  Sol's `rg`-based discovery commands were replaced with these verified
  forms; nothing in this skill is inherited unverified.
- What may drift: target repos may define their own change classes,
  CODEOWNERS, or branch protections — record them in the doctrine ledger; the
  stricter rule wins. `FOLLOWUPS.md` is only the default when no repo
  convention exists. PowerShell ≥6 defaults to UTF-8, so the `-Encoding utf8`
  caveat applies to 5.1.
- Re-verify: `git stash push -m t && git stash pop` in any repo confirms stash
  syntax; `git rev-parse --abbrev-ref HEAD` confirms branch detection;
  `Get-Content FOLLOWUPS.md -Tail 3` (PS) / `tail -n 3 FOLLOWUPS.md` (POSIX)
  confirms note appends; the three doctrine-discovery commands in §1.1 are
  their own re-verification (run them in any repo with a CONTRIBUTING.md).
