---
name: brain-harness-bootstrap
description: >
  The meta-skill that turns an installed brain harness into a target repo's
  institutional memory by generating its <project>-* skill layer. Load when
  asked to "bootstrap the harness", "generate project skills", or "capture
  what the retiring expert knows"; when .claude/skills/ has brain-* skills
  but no <project>-* skills (right after install); or when regenerating a
  stale project layer. Provides: preconditions (incl. the greenfield branch),
  the five owner questions, the six-phase pipeline (discovery → failure
  archaeology → architecture contract → config catalog → campaign →
  operations) naming the brain-* skill behind each phase, optional Phases 7–8
  (domain reference for theory-heavy repos; research frontier when the owner
  names a beyond-SOTA ambition), the quality bar for generated skills, the
  FACTUAL / DOCTRINE / USABILITY review pass plus fix pass, the maintenance
  loop, and the report format. NOT for daily engineering (individual brain-*
  skills) or the initial copy into a repo (repo-root install scripts).
---

# brain-harness-bootstrap — generate a repo's project-specific skill layer

Imagine the repo's most senior engineer is retiring next week and has agreed
to write down everything: the failures that cost months, the invariants nobody
dares state aloud, every config knob and which ones are booby-trapped, and how
things actually build and ship. This skill is that handoff, performed by a
session instead of a person — it mines the repo's own history and code, asks
the human owner only what the repo cannot tell it, and writes the result as
`<project>-*` skills next to the portable brain-* doctrine.

This skill is an **orchestration script over the library**: each phase names
the brain-* skill that supplies the method and adds only sequencing, inputs,
outputs, and done-criteria. The config-catalog method formerly in Phase 4 has
moved to its own sibling, `brain-config-and-flags`; the only methods living
HERE are the two optional generators of Phases 7–8 (domain reference,
research frontier), which have no standalone sibling.

**Definitions**
- **Harness**: the brain-* skill library installed in the target repo's
  `.claude/skills/` (with its README, which carries the authoring standard).
- **Project skill layer**: the generated `<project>-*` skills. `<project>` is
  a short lowercase slug of the repo name (alphanumeric and hyphens, e.g.
  `acme-api` → `acme-api-operations`).
- **Bootstrap session**: one or more working sessions executing this pipeline,
  with a plan and working log per `brain-task-planning`.

## 0. Preconditions — check before starting

1. **Harness installed.** From the target repo root:

   ```sh
   # POSIX — expect the full brain-* set (compare against the library README's inventory table)
   ls .claude/skills | grep -c '^brain-'
   ```
   ```powershell
   # PowerShell
   (Get-ChildItem .claude/skills -Directory -Filter 'brain-*').Count
   ```
   Zero or missing directory → stop; install first via the harness repo's
   `install.ps1` / `install.sh` or the plugin (see that repo's root README).
   This skill generates skills; it does not install the library.

2. **A git history to mine — or the greenfield branch.**

   ```sh
   # POSIX — total commits, and activity in the last year
   git rev-list --count HEAD
   git log --since="1 year ago" --oneline | wc -l
   git shortlog -sn --no-merges HEAD | head -10   # who to ask when the log is unclear
   ```
   ```powershell
   # PowerShell
   git rev-list --count HEAD
   (git log --since="1 year ago" --oneline | Measure-Object -Line).Lines
   git shortlog -sn --no-merges HEAD | Select-Object -First 10
   ```
   **Greenfield branch**: fewer than ~50 commits or only days of history means
   Part A mining (Phase 2) has nothing to find. Skip archaeology mining and
   the campaign unless the owner names a live problem; generate Phases 3, 4,
   6 — and 7 where triggered — from code alone; create the archaeology skill as a **stub** that
   ships only the ongoing-chronicle convention (`brain-failure-archaeology`
   Part B) plus one line stating why it is empty: "no history to mine as of
   <date> (<N> commits)". An honest stub beats invented history.

3. **An owner you can ask.** The five questions of §1 need a human. If none
   is available, proceed, mark every gap `OWNER-INPUT-PENDING`, and list the
   unanswered questions in the completion report (§6).

4. **A plan.** Bootstrap is multi-session-scale work: write the plan first
   (`brain-task-planning` — the §2 phases, six core plus any triggered
   optional ones, are your checkpointed steps)
   and keep a working log. Generated skills are new files shipped through the
   normal gates of `brain-change-control` (class C1 Isolated on its C0–C4
   ladder — old name "docs-only" — but still gated
   and committed only with approval per `brain-change-control`; message
   wording per `brain-docs-and-writing`).

## 1. The five owner questions — ask up front, in one batch

Ask only what the repo cannot tell you. Everything discoverable by command
(stack, test runner, commit history, config surface) you discover yourself —
wasting an owner's answer budget on `git log` questions is a bootstrap
failure. Send all five together; record answers **verbatim, with the date**,
in the working log.

| # | Question | What it feeds |
|---|----------|---------------|
| 1 | What is the hardest live problem in this repo right now — the thing you'd assign your best engineer? | Phase 5: the campaign's mission |
| 2 | What discipline rules do you enforce here that no document states? ("never do X on Fridays", "always regenerate Y after touching Z") | Phase 3: contract invariants; Phase 4: guards |
| 3 | Who will use these skills, and what do they NOT know that you know? | Audience calibration for every generated skill: which jargon to define, how much to spell out |
| 4 | Which past failures cost the most time? Roughly when, so I can find the commits. | Phase 2: mining targets and seed entries |
| 5 | What would "beyond state of the art" mean for this project — the ambition nobody has had time for? | Phase 5 stretch criteria; the go/skip trigger for Phase 8 (research frontier) |

**Treat answers as testimony, not ground truth.** Owner memory drifts like any
doc. Every checkable claim in an answer gets verified against the repo before
it is enshrined ("we reverted that in March" → find the revert commit and cite
it). Where testimony and repo disagree, record both and flag the discrepancy —
never silently pick one. Unverifiable answers enter skills labeled
`source: owner interview <date>`.

## 2. The generation pipeline

| Phase | Output | Method supplied by |
|---|---|---|
| 1 | Discovery report (input to all later phases) | `brain-codebase-discovery` (deep audit level) |
| 2 | `<project>-failure-archaeology` | `brain-failure-archaeology` Part A + owner Q4 |
| 3 | `<project>-architecture-contract` | `brain-architecture-contract` + owner Q2 |
| 4 | `<project>-config-and-flags` | `brain-config-and-flags` (the catalog method's home) |
| 5 | `<project>-campaign` | `brain-campaign-playbook` template + owner Q1/Q5 |
| 6 | `<project>-operations` | `brain-build-and-env` + `brain-run-and-operate`, applied concretely |
| 7 (optional) | `<project>-domain-reference` | **this skill, §2 Phase 7** (adapted from the Sol library) |
| 8 (optional) | `<project>-research-frontier` | **this skill, §2 Phase 8** + `brain-research-methodology` |

Order is load-bearing: discovery feeds everything; archaeology before the
contract because past failures reveal which invariants are load-bearing;
archaeology before the campaign because mined failures become its fenced
wrong paths; operations last so its commands have already been executed
during earlier phases. Phases 7 and 8 run after 1–6 when triggered: 7 needs
the discovery report's domain evidence; 8 needs owner Q5 and, where one was
generated, the domain reference. Do not duplicate the method skills' content into the
generated skills — a project skill states the project's FACTS and references
the brain-* skill for the METHOD.

### Phase 1 — Deep audit

Run `brain-codebase-discovery` at level 3 (deep audit). Save the discovery
report alongside the bootstrap plan. Done when: the report exists, every
claim in it that came from a doc was verified per that skill's
verify-the-README discipline, and open questions are listed rather than
guessed at.

### Phase 2 — `<project>-failure-archaeology`

Mine per `brain-failure-archaeology` Part A (reverts, fix-of-fix chains, hot
files, postmortems, issue/PR threads), prioritizing the eras and subsystems
from owner Q4. Every entry has all four fields:

**symptom → root cause → evidence (commit hash / PR / log excerpt) → status**
(fixed-and-guarded | fixed-unguarded | open | recurring).

An entry missing evidence is a rumor — either find the artifact or drop the
entry. Include the Part B ongoing-chronicle convention so future sessions
know where new learnings go. Done when: every owner-named failure is either
an evidenced entry or explicitly listed as "could not locate evidence", and
each entry's status was checked against current code (is the guard still
there?).

### Phase 3 — `<project>-architecture-contract`

Extract invariants and load-bearing decisions per
`brain-architecture-contract`. Fold in owner Q2's unwritten rules as
invariants with `source: owner interview <date>`. **Every invariant ships a
verification command, and every verification command was executed during
bootstrap with its output noted** — an invariant you cannot check is an
opinion. Done when: running all verification commands in sequence passes,
and each decision records what breaks if it is violated (Phase 2 entries are
your best evidence).

### Phase 4 — `<project>-config-and-flags`

Generate the project's config catalog by applying the method of
`brain-config-and-flags` — its home: the axis enumeration commands, the
per-axis catalog entry format, effective-value tracing, the add-a-new-axis
checklist, and drift detection all live there and are not restated here.
What is bootstrap-specific:

- **The output is a generated project skill**, `<project>-config-and-flags`,
  holding THIS repo's catalog entries — or referencing the repo's existing
  config doc-of-record if one already exists (never a second home).
- Owner Q2's unwritten rules become `Guard:` entries where they concern
  config ("always regenerate Y after touching Z").
- Ship the enumeration commands you actually ran in the generated skill's
  own Provenance section, so the §5 maintenance loop can diff for drift.

Done when: every enumerated axis has a complete entry, every `Default:` was
confirmed against current code, and every `Verify:` command was executed once.

### Phase 5 — `<project>-campaign`

Take owner Q1's hardest live problem through the campaign-vs-loop test in
`brain-campaign-playbook`. If it is campaign-shaped, generate the skill from
that playbook's `templates/CAMPAIGN.md`: numeric mission, decision-gated
phases, ranked solution menu with obligations, **fenced wrong paths seeded
from Phase 2 entries** (past failed approaches are pre-paid fences), abort
criteria, empty log. Owner Q5's ambition becomes stretch criteria here and
the go/skip decision for Phase 8 — labeled candidate, not commitment.
If the problem is bug-shaped instead, do NOT force a campaign: record the
problem and hand it to `brain-debugging-playbook`, and say so in the
completion report. Done when: a fresh session could open the campaign skill
and execute phase 0 without this conversation.

### Phase 6 — `<project>-operations`

How THIS repo builds, runs, tests, and deploys — `brain-build-and-env` and
`brain-run-and-operate` applied concretely. **Verified commands only**: every
command in this skill was executed during bootstrap and its observed output
(or exit code) noted next to it. Anything you could not run (e.g. production
deploy) is listed under "discovered but not executed" with the config file
that documents it — and the reminder that deploying requires explicit human
approval (`brain-change-control`). Done when: a fresh session can go from
clean clone to passing tests using only this skill.

### Phase 7 (optional) — `<project>-domain-reference`

The domain-theory knowledge pack a mid-level newcomer lacks: the field's
math, protocols, standards, or regulations AS THEY APPLY IN THIS REPO — not
a textbook chapter. **Trigger**: the repo implements substantive domain
theory (ML, cryptography, physics, finance, wire protocols, regulated data).
For a plain CRUD app, skip the phase and say so in the completion report — a
domain pack padded from general knowledge is worse than none. Signal check
(verified in Git Bash, ripgrep 14.1.1; same syntax in PowerShell where `rg`
is on PATH):

```sh
rg -n -i --hidden -g '!.git/*' 'rfc[ -]?[0-9]|specification|standard\b|regulation|equation|formula|theorem|doi:|arxiv|iso[ -][0-9]|ietf|nist|w3c' .
```

Zero or trivial hits plus no domain-heavy code in the Phase 1 report → skip.

**Mine** (never guess the domain from folder names or dependencies alone):
code comments citing equations or spec clauses; papers/RFCs/standards
referenced in the repo (the search above); schemas, fixtures, and golden
files that encode domain semantics; domain terms whose meaning in this repo
differs from the field's default (define each once); owner Q3's audience gap.

**Entry format — one per governing concept:**

```markdown
### <CONCEPT>
- Domain rule: <equation / protocol clause / standard section — source name,
  version, section>
- In this repo: <types, units, encoding, valid ranges> — <file:line>
- Evidence: <test, fixture, or executed example with observed output>
- Mapping: exact | subset/extension | DRIFT (repo disagrees with source) | open
```

Quality bar: every claim ties to a repo artifact or a cited external source
(publisher, version, section — never a search snippet or model memory);
units and precision stated, not collapsed; repo-vs-source disagreements are
reported as DRIFT, never silently resolved — a passing test can encode the
same misunderstanding; anything unprovable stays labeled open. Done when:
every entry has a repo anchor, and no entry could have been written by a
textbook author who never saw this repo.

### Phase 8 (optional) — `<project>-research-frontier`

Open problems where THIS project could plausibly advance the state of the
art. **Trigger**: owner Q5's answer. "Not a research project" is a complete
answer — skip the phase and say so in the completion report. Never
manufacture a frontier from repo complexity, TODOs, or one recent paper.

**Per-problem card — all four parts, or the problem doesn't ship:**

1. **The gap**: what the current baseline (named, versioned, dated) fails to
   do under stated conditions, with the evidence. "Not found in my search as
   of <date>" is honest; "doesn't exist" is not.
2. **This project's specific asset**: the cited artifact — dataset, eval
   harness, trace, architecture property (`file:line` or command output) —
   that makes testing the gap cheaper here than from scratch. No cited
   asset → the problem is a note, not a card.
3. **First three concrete steps IN THIS REPO**: exact paths and commands
   discovered in the repo (never invented runners), each with a predicted
   observation and a stop condition.
4. **A falsifiable milestone**: "you have a result when …" in the milestone
   format of `brain-research-methodology` §6 (its home — numeric, dated,
   with a retire condition; not restated here).

Every card is labeled **candidate** and feeds the `brain-research-methodology`
lifecycle; none is a commitment. Note each card's negative-result value —
what a failed test still buys (a bound, a counterexample, a decision saved).
Done when: a fresh session could execute step 1 of any card without this
conversation — or the phase is skipped with owner Q5's answer quoted.

## 3. Quality bar for generated skills

Generated skills meet the same authoring standard as the brain library — the
"Authoring standard" section of the library README installed alongside the
skills (trigger-rich `description:`, imperative runbook voice, tables,
density, "When NOT to use", "Provenance and maintenance"). Project-specific
deltas:

- **Ground truth only, with provenance per fact**: every claim carries a
  commit hash, `file:line`, executed command output, or
  `source: owner interview <date>`. No "probably", no "I believe".
- **Project paths ARE load-bearing** — unlike brain-* skills, project skills
  may and should cite absolute-within-repo paths, real service names, real
  flag names.
- **One home per fact, across BOTH layers**: project skills reference brain-*
  doctrine by name instead of restating it, and reference each other instead
  of duplicating (the operations skill cites the config catalog's axis names;
  it does not re-list defaults).
- **Fold in owner answers everywhere relevant** — Q3's audience answer sets
  the jargon-definition bar for the whole set.

## 4. The review pass — three reviews, then a fix pass

Run three SEPARATE reviews over the whole generated set, one checklist each.
Where the environment provides subagents, run them in parallel, each given
only its checklist and the skill paths; otherwise run them sequentially,
re-reading the skills fresh for each checklist rather than merging the three
into one skim. One combined pass reliably under-catches: factual errors hide
behind good prose, and doctrine violations hide behind correct facts.

**FACTUAL — re-verify everything against the repo**
- [ ] Every command in every generated skill executed during this review;
      exit code and key output noted (not "looks right").
- [ ] Every cited path exists (`git ls-files | grep -F "<path>"` /
      `Test-Path <path>`).
- [ ] Every cited commit/PR resolves (`git show <hash> --stat`; PR via the
      forge CLI or URL).
- [ ] Every config default in the catalog matches current code/schema.
- [ ] Every number (dates, counts, versions, rates) re-derived from source,
      not trusted from the draft.
- [ ] Owner-interview claims that state repo facts were checked against the
      repo; discrepancies are flagged in the text, not silently resolved.

**DOCTRINE — no contradictions, nothing routed around control**
- [ ] Nothing contradicts the four non-negotiables (home:
      `brain-change-control`) or any brain-* rule.
- [ ] No generated instruction routes around change control: no "just push",
      no "skip the flaky test", no auto-deploy, no `--no-verify`.
- [ ] One home per fact — no fact stated in two skills; cross-references by
      skill name instead.
- [ ] Doctrine is referenced, never restated with drift.
- [ ] No overclaiming: every unverified claim is labeled candidate / open /
      `OWNER-INPUT-PENDING`; every archaeology entry has a status.
- [ ] The skills agree with each other (operations' test command == the
      contract's verification commands where they overlap).

**USABILITY — would a cold session load and use this?**
- [ ] `description:` is trigger-rich: write down three realistic tasks in
      this repo; the right skill's description matches each without opening
      the body.
- [ ] Each skill is self-contained: actionable by a zero-context reader
      (owner Q3's audience) with no access to this bootstrap conversation.
- [ ] Scannable: tables and checklists over prose walls; within the library's
      density band.
- [ ] Commands copy-pasteable; both shells wherever they differ.
- [ ] No duplication across the set; no filler lines.
- [ ] "When NOT to use" present in every skill and names real siblings.

**Findings and fix pass.** Each finding: file, claim/line, checklist item,
severity — **blocking** (wrong fact, doctrine violation), **important**
(missing provenance, weak trigger, duplication, contradiction), **nice**
(wording). Apply all blocking and important findings, then re-run only the
FACTUAL items touched by the fixes. "Nice" findings go to a deferred-work
ledger (`brain-minimal-change`), not into an ever-growing polish loop.

## 5. The maintenance loop — bootstrap is a birth, not a funeral

The generated layer decays the day it ships unless sessions feed it. Put this
table (adapted) into the target repo's session guidance:

| Trigger | Action | Method |
|---|---|---|
| Significant session ends: root cause found, surprise hit, approach fenced | Append a chronicle entry to `<project>-failure-archaeology` | `brain-failure-archaeology` Part B |
| An architectural decision changes | Update `<project>-architecture-contract`; record the decision | `brain-architecture-contract`; ADR format in `brain-docs-and-writing` |
| A flag/env var/config key is added, removed, or repurposed | Re-run the enumeration; diff against the catalog; update entries | `brain-config-and-flags` (drift section) |
| A campaign gate is passed or the campaign aborts | Append to the campaign log; on promotion/abort, update archaeology | `brain-campaign-playbook` |
| A governing standard, schema, or cited paper version changes (if Phase 7 ran) | Update the affected `<project>-domain-reference` entries; re-check mapping labels | this skill, §2 Phase 7 |
| A frontier card's baseline ages past its search date, or its milestone date arrives (if Phase 8 ran) | Refresh, retire, or promote the card | `brain-research-methodology`; this skill, §2 Phase 8 |
| Quarterly | Run every generated skill's "Provenance and maintenance" re-verification one-liners; fix drift as C1 (docs-only) changes | each skill's own provenance section |

## 6. Completion deliverable — the honest handoff report

Report in the outcome-first house style of `brain-docs-and-writing`. Four
sections, in order:

1. **Inventory** — table of generated skills: name, one-line description,
   plus anything skipped (greenfield stub, bug-shaped non-campaign, skipped
   optional Phase 7/8) with the one-line reason.
2. **Verified** — what was actually executed as spot-check: which commands,
   in which skills, with which outcomes. Cite specifics; "all commands
   verified" without a list is banned phrasing.
3. **Uncertain / open** — every `OWNER-INPUT-PENDING`, every claim resting
   only on testimony, every command discovered but not executed, every
   discovery-report open question that survived. An empty section is
   suspicious, not impressive.
4. **Maintenance handoff** — the §5 table and the date the first quarterly
   re-verification is due.

## When NOT to use this skill

| Situation | Use instead |
|---|---|
| Daily engineering work in an already-bootstrapped repo | The individual brain-* and `<project>-*` skills |
| Harness not yet installed in the repo | The harness repo's root `install.ps1` / `install.sh`, or plugin install (harness repo README) — then return here |
| Onboarding yourself for a single task | `brain-codebase-discovery` level 1 or 2 |
| Recording one learning after a session | `brain-failure-archaeology` Part B directly — no re-bootstrap |
| Auditing or cataloging config outside a bootstrap | `brain-config-and-flags` directly |
| One project skill has drifted | §5 maintenance actions on that skill only |
| Authoring or editing the brain-* library itself | The library README's authoring standard + `brain-docs-and-writing` |

## Provenance and maintenance

- Revised 2026-07-12: merged with the Sol library. The Phase 4 config-catalog
  method moved to its new home, `brain-config-and-flags` (Phase 4 is now a
  thin orchestration step over it); optional Phases 7 (domain reference) and
  8 (research frontier) added, distilled from Sol's sol-domain-reference and
  sol-research-frontier — owner's decision: project-specific knowledge packs
  generated per-repo, not standalone portable skills. The library is now 17
  skills; change classes are cited as C0–C4 with the old names as aliases
  (`brain-change-control`).
- Originally authored 2026-07-10 on Windows 11 (PowerShell 5.1 + Git Bash),
  in the harness repo itself (which has no git history — commands needing
  one were verified in a synthetic scratch repo); revised 2026-07-10 (review
  pass: commit-approval attribution corrected to `brain-change-control`).
- Verified on the authoring machine — 2026-07-10, both shells where forms
  differ: the §0 harness-count check; `git rev-list --count HEAD`;
  `git log --since="1 year ago" --oneline` with line count;
  `git shortlog -sn --no-merges` — each against a scratch git repo.
  2026-07-12: the Phase 7 domain-signal `rg` search against a scratch repo
  seeded with matching and non-matching files (Git Bash, ripgrep 14.1.1;
  `rg` was not on the PowerShell PATH on the authoring machine — the command
  syntax itself is shell-independent).
- NOT executed here (run in the target repo): `git show <hash> --stat` and
  forge-CLI PR lookups in the FACTUAL checklist; the pipeline end-to-end
  (needs a real target repo and an owner). Phase 4 enumeration commands are
  owned and verified by `brain-config-and-flags`.
- May drift: sibling skill names and their internal section labels (the
  library README's inventory table is the source of truth); install script
  names in the harness repo root; the section numbers cited from siblings
  (`brain-research-methodology` §6 by Phase 8; `brain-config-and-flags`
  internals by Phase 4).
- One-line re-verification: in any bootstrapped repo, run the §0 precondition
  block and the Phase 7 signal search; both should run clean.
