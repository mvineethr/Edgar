---
name: brain-minimal-change
description: >-
  Minimum-viable-diff discipline and scope-creep defense. Load before editing
  any existing code, and again before committing, staging, or opening a PR.
  Triggers: fixing a bug, making a small feature change, touching a file that
  "could use cleanup", feeling the urge to rename/reformat/refactor/upgrade
  while doing something else, deciding whether to extract a shared helper,
  reviewing your own diff before submission, or when a reviewer says the diff
  is too big or contains unrelated changes. Covers: tracing every hunk to the
  request, scope-creep tripwires and their correct responses, the rule of
  three for abstractions, the deferred-work ledger for cleanup you did NOT do,
  and the pre-submit self-review commands (git diff --stat, staged/unstaged
  review). For classifying and gating a legitimately larger change, use
  brain-change-control instead.
---

# brain-minimal-change — minimum-viable-diff discipline

**Jargon, defined once:**
- **Diff / hunk**: the change set you will submit; a *hunk* is one contiguous
  block of changed lines as shown by `git diff` (each `@@ ... @@` section).
- **Scope creep**: any change in the diff that the request did not require.
- **Drive-by cleanup**: an improvement made "while you're in the file" —
  renames, reformatting, dead-code deletion, dependency bumps — that nobody
  asked for.

This skill enforces non-negotiable #2 (**minimal diffs only** — the full list
and its rationale live in `brain-change-control`). It exists because scope
creep is one of the harness owner's top observed failure modes: a bug fix
becomes a refactor avalanche, review cost explodes, the actual fix gets lost,
and reverts become impossible to do surgically.

## 1. The minimum-viable-diff doctrine

**Every hunk in the diff must trace to the request. The burden of proof is on
inclusion, not exclusion.**

That inversion is the whole doctrine. You never need to justify *leaving code
alone* — ugly code you didn't touch costs the reviewer nothing. You always
need to justify *touching* it. For each hunk, you must be able to complete
this sentence: "This hunk is required because the request said ____, and
without it ____ would break / the request would be unmet."

Acceptable justifications for a hunk:

| Justification | Example |
|---|---|
| Directly implements the request | The changed condition that fixes the reported bug |
| Mechanically forced by a required change | Callers updated because a required signature changed |
| Required proof of the change | A test that fails before the fix and passes after (see `brain-validation-and-qa`) |
| Explicitly requested by the user/task | "Also rename X" written in the task |

Not acceptable: "it was wrong anyway", "it's cleaner", "the linter flagged
it", "I was already in the file", "it will help later". Those are ledger
entries (section 4), not hunks.

**Corollaries:**
- Match the file's existing style, even where you dislike it. A minimal diff
  in a consistent-but-imperfect style beats a mixed-style file.
- Prefer the smallest change that is *correct*, not the smallest change that
  *appears to work* — minimal is not the same as superficial. If the real fix
  requires touching three files, touch three files; don't paper over it with
  a one-line hack at the symptom site (symptom-vs-cause triage lives in
  `brain-debugging-playbook`).
- New files count as diff. A new helper module is scope unless the request
  needs it.

## 2. Scope-creep tripwires

These are the exact thoughts that precede sprawl. When you catch yourself
thinking the left column, execute the right column — verbatim, no debate.

| Tripwire thought | Correct response |
|---|---|
| "While I'm here, I'll also fix/clean/improve…" | Stop. Add it to the deferred-work ledger (section 4). Touch nothing. |
| "This name is bad; I'll rename it." | Rename only if the request is about naming. Otherwise: ledger. Renames ripple through every call site and bloat the diff worst of all. |
| "Let me reformat this file / run the formatter on it." | Format **only the lines you changed**. Never reformat untouched code — it destroys `git blame` and buries the real change. If the repo has a format-changed-lines-only hook, rely on it. |
| "This dependency is outdated; quick bump." | Never bundle dependency bumps with logic changes. A bump is its own change with its own risk class — route it through `brain-change-control` as a separate task. |
| "I see the same code twice; I'll extract a helper." | Not before the third occurrence (section 3). Ledger it. |
| "The linter/type-checker flags pre-existing issues in this file." | Fix only violations **on lines your change introduced or modified**. Pre-existing violations: ledger. Exception: if pre-existing failures block the commit hook, report that to the user rather than bypassing the hook (non-negotiable #4). |
| "This dead code should go." | Deleting dead code is a real change with real risk (it may not be dead). Ledger it. |
| "I'll just add a param/option for flexibility we'll need later." | Speculative generality is scope creep. Build for the current request only. |
| "The tests around this are weak; I'll beef them up." | Add only the tests that prove *your* change. Broader test hardening: ledger, as a proposed follow-up. |
| "This fix would be easier after a small refactor." | Sometimes true — but that makes it a **bigger change**, which gets gated, not smuggled (section 5). |

Rule of thumb: if you cannot point at the sentence in the request that demands
a hunk, the hunk goes in the ledger, not the diff.

## 3. The rule of three

**Duplication is cheaper than the wrong abstraction. Do not extract a shared
abstraction until the third occurrence.**

- **1st occurrence**: write it inline.
- **2nd occurrence**: copy it. Yes, really. Two instances are not enough
  evidence of the true axis of variation; an abstraction guessed from two
  cases usually guesses wrong, and a wrong abstraction is far harder to
  remove than duplication.
- **3rd occurrence**: now you have three real call sites showing what varies
  and what doesn't. Extraction is justified — **as its own task**, not as a
  rider on the change that created the third occurrence. Ledger it unless the
  request was the refactor itself.

An abstraction IS justified when **all** of these hold:
1. Three or more real (not anticipated) usages exist.
2. The duplicated code changes for the same reason in all sites — you keep
   fixing the same bug in N places.
3. The abstraction's interface is obvious from the existing sites, with zero
   speculative parameters.
4. The extraction is either the task itself or has been approved as one
   (route via `brain-change-control`).

Counter-signal: if the "shared" code needs flags/modes to serve its call
sites, the sites were never the same thing. Inline it back.

## 4. The deferred-work ledger

Everything the tripwire table told you not to do still has value — capture it
instead of doing it. The ledger converts "while I'm here" energy into
reviewable follow-up work.

**The full protocol (record → propose → don't do, with the note-append
commands and the `FOLLOWUPS.md` default) is HOMED in `brain-change-control`
§3 — follow it there.** This skill adds only the two diff-side rules:

- Each ledger entry must be actionable by someone with zero context from your
  session: **date, what, where (path), why it matters, and what triggered
  noticing it**. Label unproven improvement ideas as `candidate:`.
  (Failure-pattern findings belong in the LEARNINGS convention instead —
  home: `brain-failure-archaeology`.)
- **Never** encode deferred work as code comments like `// TODO: refactor
  this mess` sprinkled in the diff — that's still scope creep (new hunks) and
  it's where TODOs go to die.

## 5. When a bigger change IS right

Minimal-diff discipline is about *unauthorized* scope, not about pretending
big changes are never needed. A bigger change is legitimate when:

- The minimal fix would be built on a foundation that is actively wrong
  (fixing the symptom would hide the cause).
- You've hit the rule-of-three threshold and the duplication is causing real,
  recurring bugs.
- Security/correctness requires touching a wide surface (e.g., an injected
  query pattern repeated across handlers).
- The requested change is impossible without a structural change (e.g., the
  feature needs state where the architecture has none).

**The procedure is: stop, propose, get the gate — never just do it.**

1. Stop coding the expanded version. If you've started, stash or discard the
   expansion (`git stash`, or `git restore <file>` for unstaged files —
   verify with `git status --short` after).
2. Write a short proposal: what the request asked, why the minimal diff is
   insufficient (with evidence), what the bigger change touches, and the
   rollback story.
3. Route it through `brain-change-control` for classification and approval.
   That skill owns the change classes and gates; this skill's only job is to
   make sure you *arrive* there instead of unilaterally expanding scope.
4. If approved: the bigger change becomes the (new) request, and this skill
   applies to it — every hunk must trace to the *approved* scope.
5. If you can't get an answer: ship the minimal correct change now, ledger
   the rest.

## 6. Pre-submit self-review checklist

Run this before every commit/PR, in order. All git commands below are
identical in POSIX shells and PowerShell (verified on Git for Windows,
2026-07-09). `--staged` and `--cached` are synonyms. Add `--no-pager` after
`git` if output opens a pager in your terminal.

**Step 1 — bird's-eye view first. Read the file list before any hunk:**
```sh
git diff --stat HEAD        # all changes vs last commit (staged + unstaged)
git status --short          # includes untracked files (?? lines)
git ls-files --others --exclude-standard   # untracked files only — new files are diff too
```
For every file listed, answer: *why is this file in the diff?* A file you
can't explain is the first thing to investigate.

**Step 2 — hunk-by-hunk trace to the request:**
```sh
git diff --staged           # review what you're about to commit
git diff                    # review unstaged changes (should be empty or intentional leftovers)
```
For each `@@` hunk, complete the traceability sentence from section 1. Any
hunk that fails: unstage and revert it —
```sh
git restore --staged <file>   # unstage
git restore <file>            # discard unstaged changes to the file (destructive — be sure)
```
(then ledger whatever the hunk was trying to improve). For a file with mixed
wanted/unwanted hunks, `git add -p <file>` stages hunks interactively — human
terminals only; agents should instead revert the file and re-apply only the
required edit.

**Step 3 — targeted sniff tests:**
```sh
git diff -w --stat          # whitespace-ignoring; if a file drops out vs --stat, its changes are reformat-only → revert it
git diff HEAD --numstat     # per-file added/removed counts; outliers = likely creep
```

**Checklist (all must pass):**
- [ ] Every changed file has a one-line reason tied to the request.
- [ ] Every hunk passes the traceability sentence.
- [ ] No file appears only in `git diff -w`-invisible form (reformat-only).
- [ ] No renames, dep bumps, or new abstractions unless the request named them.
- [ ] Untracked/new files are all required by the request.
- [ ] Deferred items are in the ledger and mentioned in the report.
- [ ] The change is *proven*, not just small (evidence rules: `brain-validation-and-qa`).

## When NOT to use this skill

- **Greenfield scaffolding / new project setup**: there is no existing code
  to protect; "minimal" has no baseline. Use `brain-task-planning` to scope
  what to build, and `brain-build-and-env` for environment setup.
- **Explicitly requested refactors or cleanups**: the refactor *is* the
  request; the doctrine still applies but the traced scope is the refactor
  itself. Classify and gate it via `brain-change-control` first.
- **Deciding whether/how to gate a large change**: that machinery (change
  classes, approval gates, non-negotiables rationale) lives in
  `brain-change-control` — this skill only routes you there.
- **Exploratory spikes on a throwaway branch**: discipline the *landing*
  diff, not the exploration. See `brain-campaign-playbook` for decision-gated
  exploration on hard problems.
- **Debugging instrumentation**: temporary probes are governed by
  `brain-debugging-playbook` (including removing them before submit — this
  skill's checklist is your backstop when they leak into the diff).

## Provenance and maintenance

- **Authored**: 2026-07-09, on Windows 11 (Git for Windows / Git Bash and
  PowerShell 5.1); revised 2026-07-10 (review pass: deferred-work ledger
  mechanics deduplicated — protocol home is `brain-change-control` §3).
- **Verified on the authoring machine**: `git diff --stat HEAD`,
  `git diff --staged --stat`, `git diff`, `git status --short`,
  `git ls-files --others --exclude-standard`, `git diff HEAD --numstat`,
  `git diff -w --stat`, `git restore <file>`, `git restore --staged <file>` —
  all exercised in a scratch repo with staged, unstaged, untracked, and
  whitespace-only changes.
- **Not machine-verified (standard documented usage)**: `git add -p`
  (interactive; unusable in non-interactive agent sessions by design),
  `git stash`.
- **What may drift**: `git restore` requires git >= 2.23 (older repos/images:
  use `git checkout -- <file>` and `git reset HEAD <file>`); pager defaults
  and `--no-pager` behavior vary by git config; the deferred-work ledger
  location is per-repo convention — rediscover it via `brain-codebase-discovery`.
- **Re-verify in a target repo**: `git --version`, then
  `git --no-pager diff --stat HEAD` on any dirty checkout.
