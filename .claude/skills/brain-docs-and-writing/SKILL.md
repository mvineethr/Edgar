---
name: brain-docs-and-writing
description: >-
  House style for everything an engineering session writes: findings and
  completion reports, commit messages, PR descriptions, ADRs, doc-of-record
  updates, and external positioning (public claims, novelty, benchmarks).
  Load before writing any final report or summary, before committing
  (wording only; permission: brain-change-control), before opening a PR,
  when a behavior change means docs must be updated in the same change, when
  writing an ADR (format only — usage policy: brain-architecture-contract),
  when drafting anything public-facing claiming novelty, speed, or
  superiority, or when editing any brain-* skill (provenance and inventory
  sync). Covers: the outcome-first report format, house style
  with bad→good pairs, the commit convention, the What/Why/Proof/Risk/Rollback
  PR template, the doc-of-record rule, external positioning standards, and
  shipped REPORT/ADR/PR templates. Evidence standards and the evidence-state
  vocabulary → brain-validation-and-qa; LEARNINGS entries →
  brain-failure-archaeology.
---

# brain-docs-and-writing — reporting, commit/PR, and doc-of-record house style

**Jargon, defined once:**
- **Lede**: the most important fact of a piece of writing. "Burying the lede"
  = hiding it under background or narration.
- **Doc of record**: any document a future reader will trust as the truth
  about behavior — README, `docs/`, config reference, API docs, runbooks.
- **ADR (Architecture Decision Record)**: a short, immutable note capturing
  one significant decision, its context, and its consequences.
- **Proof-of-work block**: the command-plus-observed-output evidence format
  that must accompany every completion claim. Its format and the evidence
  hierarchy are owned by `brain-validation-and-qa`; this skill only tells you
  *where* it goes in each document type.

Everything here targets the same failure mode: prose that sounds finished
while hiding what actually happened. Writing that oversells, buries the
outcome, or narrates process instead of results directly feeds the harness
owner's #1 observed failure ("claiming done without proof") — the honest
format makes the missing proof visible.

## 1. Report format — outcome first

Every report (final session summary, findings write-up, investigation result)
uses the inverted pyramid: **outcome, then evidence, then detail**. Skeleton:
`templates/REPORT.md`.

**Rule 1 — the first sentence answers the question.** Whatever the user asked
("does it work?", "what's causing this?", "is the migration safe?"), sentence
one is the answer — including when the answer is "it failed" or "inconclusive".

**Rule 2 — never narrate your process chronologically.** "First I looked at X,
then I tried Y, then I noticed Z…" forces the reader to relive your session to
find the result. Chronology is only relevant when order itself is the finding
(e.g., a race condition, a bisect narrative — and even then, verdict first).

Bad (buried lede, process narration):

> I started by reading the auth middleware, then checked the session store
> configuration. After that I ran the integration tests, which surfaced some
> interesting behavior in the token refresh path. Digging further, I found
> that the refresh handler doesn't check expiry. So there might be a bug here.

Good (outcome → evidence → detail):

> **Found the cause: the token refresh handler never checks expiry**, so any
> stolen refresh token works forever. Evidence: `src/auth/refresh.ts:41` uses
> `verifySignature()` but not `checkExpiry()`; the repro in
> `tests/auth/refresh.test.ts` passes a token expired 30 days ago and gets a
> new session. Detail: introduced in commit `a1b2c3d` when refresh was split
> from login; login still checks expiry at `src/auth/login.ts:88`.

**Structure of a full report** (order fixed; sections after Evidence optional):

| Section | Contents |
|---|---|
| Outcome | 1–3 sentences; the answer/verdict, with numbers |
| Evidence | Proof the outcome is true: proof-of-work blocks, `file:line` citations |
| Detail | What changed and where; what was ruled out; decisions and why |
| Proposed follow-ups | Deferred-work ledger items (`brain-minimal-change` §4) |
| Open questions / residual risk | What you don't know, labeled as such |

## 2. House style rules

Apply to all writing — reports, commits, PRs, ADRs, doc updates, chat replies.

| Rule | Bad | Good |
|---|---|---|
| **Numbers over adjectives.** Adjectives hide the magnitude; a reader can't audit "much". | "The query is much faster now." | "Query p95: 2.3s → 0.4s (5.8x) over 100 runs against the seeded dev DB." |
| **No oversell.** Label speculation as speculation, candidates as candidates. A guess presented as fact poisons every downstream decision. | "This fixes the memory leak." (fix never exercised) | "Candidate fix for the memory leak: the listener in `poller.ts:52` is never removed. Not yet verified — the 10-min soak repro hasn't been rerun." |
| **Complete sentences over fragment chains.** Fragments drop the causal links, which are the actual information. | "Fixed bug. Null user. Added check. Tests pass." | "The crash occurred because `user` is null on first-ever login; I added a guard in `session.ts:34` and a regression test that fails on the parent commit." |
| **Define jargon at first use** — one parenthetical, then use the term freely. Audience is a zero-context reader. | "Enabled PPR on the dashboard route." | "Enabled PPR (Partial Prerendering — Next.js mode that serves a static shell and streams dynamic parts) on the dashboard route." |
| **Completion claims carry proof.** Every "done / fixed / works / passes" must be immediately followed by a proof-of-work block. | "All tests pass, feature is done." | The same claim followed by the executed command and observed output, per the proof-of-work format in `brain-validation-and-qa`. |

The no-oversell vocabulary — the prose terms **verified / candidate /
speculation / unknown** and the ledger states **VERIFIED / DECLARED /
INFERRED / CONFLICT / UNKNOWN** — is defined once, with the mapping between
the two, in `brain-validation-and-qa` (its home). Use it consistently, never
claiming a stronger term than the evidence state supports; "I don't know"
beats a confident wrong sentence.

## 3. Commit message convention

Format (enforced by convention, checked before every commit):

```text
<imperative subject, ≤72 chars, no trailing period>
<blank line>
<body: WHY this change exists — the problem, the constraint, the
rejected alternative. Wrap at ~72 columns.>

Refs: <issue/task ID>
```

- **Imperative subject**: completes "If applied, this commit will ___".
  "Fix expiry check in token refresh", not "Fixed…" / "Fixes…" / "fixing…".
- **≤72 characters** hard cap — longer subjects truncate in `git log --oneline`
  and most UIs.
- **Body explains WHY, not what.** The diff already shows what. The body
  carries what the diff can't: the problem observed, why this approach, what
  was rejected. A subject alone is fine for truly self-evident changes
  (typo fix); everything else gets a body.
- **Reference the issue/task** (`Refs: BUG-123`, `Fixes #45`) so the change
  traces to its request.
- **One logical change per commit.** If the subject needs "and", split it.
  What belongs in the diff at all is `brain-minimal-change`'s territory;
  whether you may commit right now is `brain-change-control`'s.
- **Match the repo's existing convention first** — if history uses
  Conventional Commits (`fix:`, `feat:` prefixes), follow it. Inspect:

  ```sh
  git log --format=%s -20    # POSIX and PowerShell (verified 2026-07-10)
  ```

Bad → good:

```text
fixed some auth stuff and cleaned up imports
```

```text
Fix token refresh accepting expired tokens

The refresh handler verified the signature but never called
checkExpiry(), so a stolen refresh token remained valid forever.
Introduced in a1b2c3d when refresh split from login. Chose to reuse
login's checkExpiry() rather than duplicating the window logic.

Refs: SEC-412
```

Subject-length self-check (verified 2026-07-10):

```sh
git log -1 --pretty=%s | awk '{ print length }'    # POSIX
```
```powershell
(git log -1 --pretty=%s).Length                    # PowerShell
```

## 4. PR description — What / Why / Proof / Risk / Rollback

Every PR body uses `templates/PR.md`. Five sections, all present — write
"None" rather than deleting a heading, so the reviewer sees the question was
considered:

| Section | Answers | Trap it prevents |
|---|---|---|
| What | The change, as an outcome, 1–3 sentences | File-by-file tours that restate the diff |
| Why | The problem + issue/task reference | Changes with no traceable request |
| Proof | Evidence it works: executed commands + output (`brain-validation-and-qa` format) | "CI will catch it"; non-negotiable #1 violations |
| Risk | Blast radius, who's affected, why acceptable | Reviewer discovering risk the author never weighed |
| Rollback | How to undo; what a revert does NOT undo (migrations, data written) | Irreversible changes shipped as if reversible |

Whether the PR may be opened at all — gating checklist, change class,
approvals — is owned by `brain-change-control`.

## 5. The doc-of-record rule

**Any behavior change updates the relevant docs IN THE SAME change.** Not a
follow-up PR, not a ledger entry — the same commit/PR, so docs and behavior
can never be true at different times. Doc hunks trace to the request exactly
like code hunks (`brain-minimal-change`); a behavior change's request
implicitly includes its docs.

"Behavior change" = anything a doc might assert: defaults, flags, CLI/API
shapes, env vars, error messages users match on, setup steps, ports, limits.

**Finding which docs mention the behavior you changed** — search for the
term(s) tied to your change (flag name, function, default value, error text).
All forms verified 2026-07-10:

```sh
rg -n -i "<term>" docs/ README.md          # the standard first sweep
rg -n -i "<term>" -g '*.md' .              # all markdown, when docs live elsewhere
```

Caveat: if a listed path doesn't exist (no `docs/` dir), `rg` prints an error
for that path, still searches the rest, and exits 2 — read the output, don't
trust the exit code alone. Fallbacks:

```sh
git grep -n -i "<term>" -- '*.md'          # tracked markdown only; POSIX + PowerShell
```
```powershell
Get-ChildItem -Recurse -Filter *.md | Select-String -Pattern "<term>"   # no rg/git needed
```

Then for each hit: update it, or state in the PR's Risk section why it's not
affected. Zero hits is also a finding — say "no docs mention `<term>`
(searched `*.md` via rg)" in the Proof section.

## 6. Shipped templates

| File | Use for | Format owner | Usage-policy owner |
|---|---|---|---|
| `templates/REPORT.md` | Findings / completion reports (section 1) | this skill | this skill |
| `templates/PR.md` | PR descriptions (section 4) | this skill | gating: `brain-change-control` |
| `templates/ADR.md` | ADR-lite: Context / Decision / Why / Consequences | this skill | when/how ADRs are used, numbered, superseded: `brain-architecture-contract` |

ADR writing rules (the format this skill owns): one decision per file;
decision stated in one or two active-voice sentences; alternatives listed with
why each lost (numbers over adjectives); consequences include the *negative*
ones of the chosen option — an ADR with no downsides is oversell. When an ADR
is required, how ADRs are numbered/stored, and the supersession rule are
`brain-architecture-contract`'s — consult it before creating one.

**Not shipped here**: a LEARNINGS entry template. Failure-pattern entries and
their convention live in `brain-failure-archaeology` — use its template.

## 7. External positioning and claims

Anything public-facing — README claims, release notes, blog posts, papers,
comparison pages — is held to a stricter bar than an internal report: a
stranger will act on it and cannot ask what you meant. Publishing is a
consequential action; whether you may publish at all is gated by
`brain-change-control`. This section owns the wording standard.

**Novel vs known.** Classify every idea before choosing words for it:

| Classification | Allowed wording | Requires |
|---|---|---|
| Known technique | "uses / implements / adapts X" | naming the technique |
| Project-specific combination | "combines X and Y for context Z" | accuracy, nothing more |
| Novelty claim ("novel", "first", "unique") | qualified scope only | a prior-art search you can cite: venues/queries, search date, closest work found, and the explicit difference from it |
| "State of the art" | measured comparison only | a benchmark against the actual current SOTA baseline (named, versioned), same workload and hardware, disclosed conditions |

Absence from your search means "not found in `<scope>` as of `<date>`", never
"does not exist". Bad → good:

> Bad: "The first framework to support streaming validation."
> Good: "We found no streaming validation in the six frameworks compared as
> of 2026-07; the closest, X v2, validates only on stream close."

> Bad: "Faster than state-of-the-art parsers."
> Good: "1.4x faster than simdjson 3.x (the fastest parser in our comparison)
> on workload W, same machine, median of 30 runs."

**Reproducibility standard for published results.** A published number must
carry enough for a stranger to reproduce it: environment (OS, hardware,
toolchain and dependency versions), seeds and known nondeterminism, exact
dataset identity and preprocessing, the exact commands run, the revision they
ran against, and whether the tree was dirty. Missing pieces downgrade the
result to "reported, not reproducible from this description" — or keep it
unpublished.

**Vocabulary.** The no-oversell terms and evidence states (section 2; home:
`brain-validation-and-qa`) apply verbatim to public claims. Before publishing,
run an adjective sweep: "revolutionary", "best", "seamless", "robust",
"enterprise-grade", "production-ready" go, unless each maps to an explicit,
measured criterion stated next to it.

## 8. Maintaining this harness's own docs

The harness eats its own doc-of-record rule. When you edit any
`.claude/skills/brain-*/SKILL.md`:

1. **Refresh its "Provenance and maintenance" date** — update the authored/
   updated date to today and note what changed, in the same commit as the
   edit.
2. **Keep the inventory table in `.claude/skills/README.md` in sync** — if a
   skill's scope, name, or one-liner changed, or a skill was added/removed,
   update its row in the same change.

Drift check — compares skill directories against the README table (POSIX /
Git Bash; verified 2026-07-10; empty output = in sync):

```sh
cd <repo-root>
diff <(ls -d .claude/skills/*/ | sed 's|.claude/skills/||; s|/$||' | sort) \
     <(rg -o '^\| `(brain-[a-z-]+)`' -r '$1' .claude/skills/README.md | sort)
```

Lines prefixed `<` are directories missing from the table; `>` are table rows
with no directory.

## When NOT to use this skill

- **Deciding what counts as evidence, formatting a proof-of-work block, or
  defining the evidence states**: `brain-validation-and-qa` owns the evidence
  hierarchy, the evidence-state vocabulary, and the block format; this skill
  only places them inside documents.
- **Writing a LEARNINGS entry** after a failure or surprising fix:
  `brain-failure-archaeology` owns that convention and template.
- **Deciding whether a decision warrants an ADR**, or where ADRs live in a
  repo: `brain-architecture-contract`. Come back here only for the prose.
- **Deciding whether you may commit/push/open the PR at all**: that gate is
  `brain-change-control`. This skill assumes the change already passed it.
- **Deciding what belongs in the diff** (including whether a doc edit is
  scope creep): `brain-minimal-change`.
- **Long-form user-facing documentation projects** (tutorial series, full doc
  sites): out of harness scope; this skill covers the writing an engineering
  change produces, not documentation as a product.

## Provenance and maintenance

- **Merged**: 2026-07-10 with the Sol library — absorbed its external
  positioning content as section 7 (novelty/SOTA claim standards, published
  reproducibility standard, adjective sweep); the no-oversell vocabulary
  definitions moved to their home in `brain-validation-and-qa` and are
  referenced from section 2. No new commands were added in the merge.
- **Revised**: 2026-07-10 (review pass: ADR usage policy deferred to its
  home, `brain-architecture-contract`).
- **Authored**: 2026-07-10, on Windows 11 (Git for Windows 2.52 / Git Bash,
  PowerShell 5.1, ripgrep 14.1.1).
- **Verified on the authoring machine**: `rg -n -i "<term>" docs/ README.md`
  (including missing-path behavior: error + exit 2 while still searching
  remaining paths), `rg -n -i "<term>" -g '*.md' .`,
  `git grep -n -i "<term>" -- '*.md'`, `git log --format=%s -20`,
  `git log -1 --pretty=%s | awk '{ print length }'`,
  `(git log -1 --pretty=%s).Length`, the `Get-ChildItem … | Select-String`
  fallback, and the section-8 `diff <(…) <(…)` drift check — all exercised in
  a scratch repo and/or this repo.
- **Not machine-verified (standard documented usage)**: none — every shipped
  command was executed here.
- **What may drift**: the 72-char subject cap is convention, not enforced by
  git — target repos may enforce different limits via commitlint/hooks
  (discover with `brain-codebase-discovery`); repos using Conventional Commits
  override section 3's subject wording; `rg` may be absent on target machines
  (fallbacks given in section 5); the section-8 drift check's regex assumes
  the README table keeps the ``| `brain-…` |`` row format.
- **Re-verify in a target repo**: `rg --version || git grep --version`;
  `git log --format=%s -20` to learn the local commit convention; run the
  section-5 sweep once with a known term to confirm doc layout.
