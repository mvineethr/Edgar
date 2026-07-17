---
name: brain-failure-archaeology
description: >
  Mining a repository's history into a failure chronicle, plus the ongoing
  LEARNINGS convention for recording investigations so no battle is fought
  twice. Load when: asked to document why past approaches failed or "what has
  gone wrong in this repo"; onboarding into a repo with visible scar tissue
  (reverts, hotfix chains, files that get fixed over and over); after ANY
  investigation that took over 30 minutes, any revert, any surprising root
  cause, or any fix rejected in review for a non-style reason — those all
  trigger writing a LEARNINGS entry (template ships here); or when deciding
  where failure/post-mortem knowledge should live and how to search it. HOME of
  the LEARNINGS entry format and the docs/learnings/ convention. Provides git
  mining commands (reverts, fix churn, stalled branches, deleted files) in
  POSIX + PowerShell. Not for live debugging (brain-debugging-playbook), broad
  repo onboarding (brain-codebase-discovery), or recording architecture
  rationale (brain-architecture-contract).
---

# brain-failure-archaeology

**Failure chronicle** (also called LEARNINGS): the repo's record of
investigations — symptom, root cause, evidence, fix, and the wrong paths tried.
This skill teaches (A) how to mine an existing repo's history into that
chronicle, and (B) the convention for adding to it as you work.

## Why this is among the highest-leverage docs in a repo

An investigation costs hours; writing it up costs minutes; NOT writing it up
costs the full investigation again — re-paid by every future session (human or
model) that hits the same symptom. Sessions have no memory of each other; the
chronicle is the memory. The failure mode it prevents is specific and
expensive: a fresh session confidently re-implements an approach that was
tried, shipped, broke production, and was reverted eighteen months ago — the
repo knew, but nobody could hear it.

This is why **brain-debugging-playbook** step 0 is "consult the failure
chronicle before debugging anything." This skill is where the chronicle comes
from and how it stays alive.

---

## PART A — Mining an existing repo into a chronicle

Use this when a repo has history but no chronicle. Budget 30–60 minutes.
Every command below was executed and verified on the authoring machine
(Git Bash + PowerShell 5.1) against a repo with planted history; sample
outputs shown are real.

Two ground rules before mining:

- **Archaeology is read-only.** Never run `checkout`, `switch`, `reset`,
  `rebase`, `stash`, `clean`, or any other state-changing git command while
  mining — you are digging under the user's working tree.
- **Check for a shallow clone first**: `git rev-parse --is-shallow-repository`
  (verified both shells; prints `true`/`false`). A shallow clone silently
  truncates history — "no reverts found" there is a statement about the
  truncation, not the project.

### A1. Reverts and rollbacks — the loudest signal

A revert is a documented failure with the documentation missing. Find them:

```sh
# POSIX and PowerShell (identical)
git log -i --grep="revert" --oneline
git log -i --grep="rollback\|roll back" --oneline     # quote protects the pipe in PowerShell too
```

Verified output:

```
19b7c30 Revert "feat: enable eager caching"
```

For each hit, find what the revert undid and why:

```sh
git show 19b7c30            # full diff; the message names the reverted SHA
git show --stat 19b7c30     # just the file list
git show 970689b            # the ORIGINAL commit that got reverted — read its message and diff
```

Then look for the discussion: `git log --oneline 970689b~2..19b7c30` shows
what happened between feature and revert (hotfix attempts are common), and the
PR that contains the revert usually states the reason (see A4).

Caveat: a `Revert "…"` subject does not guarantee a full undo — conflict
resolution during the revert and follow-up edits are common. Compare the two
`git show` diffs before concluding the approach was cleanly withdrawn.

### A2. Fix churn — files that get fixed repeatedly

A file fixed five times has an undocumented design problem. Count fixes per
file:

```sh
# POSIX (Git Bash). The grep -v '^$' is REQUIRED: --format=format: emits a
# blank separator line per commit, and without the filter the top "file"
# in your ranking is the empty string.
git log -i --grep="fix" --format=format: --name-only | grep -v '^$' | sort | uniq -c | sort -rn | head -20
```

```powershell
# PowerShell 5.1 equivalent (Where-Object { $_ } drops the blank lines)
git log -i --grep="fix" --format=format: --name-only | Where-Object { $_ } | Group-Object | Sort-Object Count -Descending | Select-Object -First 20 Count, Name
```

Verified output (both shells, same repo):

```
      3 parser.ts
      1 cache.ts
```

Read the actual fix commits for the top offenders
(`git log -i --grep="fix" --oneline -- <file>`): three fixes for the same
symptom is one chronicle entry, not three.

### A3. Dead ends — stalled branches and deleted files

Abandoned work is a wrong-path record nobody wrote down. Two probes:

```sh
# Branches by last activity, oldest tell the story (POSIX and PowerShell identical)
git branch -a --sort=-committerdate --format='%(committerdate:short) %(refname:short)'
```

Verified output:

```
2026-07-10 main
2026-07-10 spike/websocket-transport
```

A `spike/`, `experiment/`, or `try-` branch months behind the default branch
is a candidate dead end — `git log <default>..<branch> --oneline` shows what
it attempted; ask (or infer from A4) why it stopped.

```sh
# Files deleted from history — abandoned modules, killed features
git log --diff-filter=D --summary | grep -E '^commit|delete mode'          # POSIX
```

```powershell
git log --diff-filter=D --summary | Select-String -Pattern "^commit|delete mode"   # PowerShell
```

Verified output:

```
commit 19b7c30b4e8af18f8e7e1e6cfcd2e2329def220c
 delete mode 100644 risky-feature.ts
commit 3f4e629607ed96a08117f56b29f2ba9fcf9f151d
 delete mode 100644 legacy-adapter.ts
```

Deletion commit messages like "remove legacy adapter, approach abandoned" are
chronicle entries waiting to be written.

### A4. Issue-shaped artifacts

```sh
# Requires gh CLI authenticated (gh auth status). Verified against a live repo.
gh issue list --state closed --search "label:bug" --limit 50
gh pr list --state merged --search "revert" --limit 20
```

Also sweep for:

- **Post-mortem docs already in-tree**: `git ls-files | grep -iE 'postmortem|post-mortem|incident|learnings|retro'`
  (PowerShell: pipe to `Select-String -Pattern` instead of `grep -iE`).
- **TODO/FIXME with names or dates** — these are confessed open failures:

```sh
git grep -nE "TODO|FIXME"        # POSIX and PowerShell identical; verified
# Verified hit:  cache.ts:3:// FIXME(mvr, 2025-11-02): races under load
```

`git blame -L <line>,<line> <file>` dates the confession and names the author.

### A5. Turning a mined thread into a chronicle entry

For each thread that survives triage (a revert, a churn cluster, a dead
branch), write one entry using `templates/LEARNING.md` (shipped alongside this
skill), reconstructing:

1. **Symptom** — from the fix/revert commit messages and linked issues.
2. **Root cause mechanism** — from the diff of the final fix. If the mechanism
   is not recoverable from evidence, say so in the entry (`Status: open`,
   mechanism "not established") — an honest gap beats a guessed cause.
3. **Evidence** — the SHAs, issue numbers, and the mining commands you ran.
4. **Status** — settled (fixed, mechanism known), open (still bites), or
   superseded (the whole subsystem was replaced).
5. **Wrong paths** — the hotfix commits between first symptom and final fix,
   and any reverted or deleted attempts.

To trace one suspicious token, constant, or line range through history
(pickaxe, `git blame -L`, `git log -L`), use the technique-2 command block in
**brain-architecture-contract** — that skill is its home.

Triage rule: mine broadly, write selectively. Ten strong entries beat fifty
mechanical ones. Skip threads whose fix is self-evident from a one-line diff.
And label absence narrowly: "not found by these probes" is not "never
happened" — remote issue trackers, expired reflogs, squashed merges, and
pre-import history are all invisible here; the entry should say what was
searched.

---

## PART B — The ongoing convention

### Where the chronicle lives

- Default: `docs/learnings/` — one file per entry, named
  `YYYY-MM-DD-<slug>.md` (e.g. `2026-07-10-eager-caching-revert.md`).
- Small repos (roughly: under ~20 contributors-months of history): a single
  `LEARNINGS.md` at repo root with the same per-entry structure, newest first.
- If the repo already has a post-mortem convention, use it — one home, not two.
  Do not create a second chronicle next to an existing one.

Entries are normal files: adding one is a docs-only change under
**brain-change-control**, and its prose follows **brain-docs-and-writing**
house style (numbers over adjectives, no oversell).

### Triggers — when an entry MUST be written

| Trigger | Why it qualifies |
|---|---|
| Any investigation > 30 minutes | The cost is already sunk; the write-up is the only way to amortize it |
| Any revert (yours or one you perform) | A revert is a failure record with no record |
| Any "that was surprising" moment | Surprise means the mental model was wrong — the next session's will be too |
| Any fix rejected in review for a non-style reason | The rejection reason is a wrong-path entry someone else already paid for |

### Quality bar — an entry is not done until

- **Mechanism stated.** Not "fixed by upgrading X" but WHY upgrading X fixed
  it. If you cannot state the mechanism, the status is `open`, not `settled`.
- **Evidence cited.** Commands run, output excerpts, commit SHAs, issue
  numbers. (Same standard as **brain-validation-and-qa** proof-of-work.)
- **Wrong paths listed with reasons.** They are half the value: the fix stops
  one repeat; the wrong-path list stops all the others.
- **Searchable symptom.** The exact error text appears verbatim somewhere in
  the entry — that string is what a future session will grep for.

---

## Consulting and maintaining the chronicle

**Search it before debugging** (this is brain-debugging-playbook step 0):

```sh
rg -i "<symptom keyword>" docs/learnings/          # if ripgrep is installed
git grep -il "<symptom keyword>" -- "*.md"         # always available; verified both shells
```

```powershell
Select-String -Path docs\learnings\*.md -Pattern "<symptom keyword>" -SimpleMatch   # verified
```

Search for the error text first, then for the subsystem name. A hit with
`Status: settled` means apply the recorded resolution; a hit with `open` means
you are adding to an existing entry, not starting a new one.

**Update stale entries by superseding, never deleting.** If a settled entry no
longer holds (subsystem rewritten, dependency replaced), set its status to
`superseded by <new entry>` and write the new entry. History of what was
believed and when is itself evidence; deleting it re-opens the trap the entry
was guarding. Never rewrite an old entry's conclusion in place — a future
reader must be able to tell what was known at the time of each fix.

## When NOT to use this skill

- **Live debugging of a current failure** — use **brain-debugging-playbook**
  (it will send you back here at step 0, and again at the end if the
  investigation crossed a Part B trigger).
- **General onboarding into an unfamiliar repo** — use
  **brain-codebase-discovery**; it does light history-mining as part of recon
  and defers deep failure mining to this skill.
- **Recording why the architecture is the way it is** (invariants, load-bearing
  decisions, ADRs) — use **brain-architecture-contract**. Rule of thumb: the
  chronicle records what went WRONG and why; the contract records what must
  stay TRUE and why.
- **Report/commit/PR wording** — use **brain-docs-and-writing**.

## Provenance and maintenance

- Merged with the Sol library 2026-07-12: absorbed the read-only-mining rule,
  the shallow-clone check (`git rev-parse --is-shallow-repository`, verified
  both shells 2026-07-12), the partial-revert caveat (A1), and the
  narrow-absence rule (A5).
- Authored 2026-07-10 on Windows 11 (PowerShell 5.1 + Git Bash, git 2.x,
  gh 2.81.0). All git commands verified in both shells against a scratch repo
  with planted reverts, fix churn, a stalled branch, and deleted files;
  `gh issue list --search` verified against a live GitHub repo.
- What may drift: `gh` search syntax (re-verify: `gh issue list --state closed
  --search "label:bug" --limit 5` in any repo with issues); `rg` availability
  (re-verify: `rg --version`; fall back to `git grep -il` shown above);
  the `--format=format:` blank-line behavior is long-stable git but re-check
  the churn pipeline output starts with a filename, not a count of blanks.
- One-line self-test in any repo: `git log -i --grep="revert" --oneline`
  returns hits in a repo with reverts, or nothing without error.
