---
name: brain-codebase-discovery
description: >
  Time-boxed onboarding protocol for a repository you have never seen — the
  incoming-principal-engineer routine. Load when dropped into an unfamiliar
  codebase, when asked "what is this repo / how does it work / how do I run
  it", before making any change in a project you have not worked in during
  this session, or when a task requires knowing the stack, entrypoints, test
  command, or conventions and you don't. Provides three depth levels
  (10-minute recon, 1-hour survey, deep audit), exact git/rg mining commands
  with what to look for in their output (POSIX + PowerShell), CI-config and
  docs discovery with a doctrine-source priority order (which rule-bearing
  files bind you, in what order), the read-only-survey discipline, the
  verify-the-README discipline, and a discovery report template. Not for setting up the environment itself (brain-build-and-env),
  running the app (brain-run-and-operate), deep failure-history mining
  (brain-failure-archaeology), or writing the invariants contract
  (brain-architecture-contract).
---

# brain-codebase-discovery

You've just been handed a repo you've never seen. Resist the urge to start
editing. A principal engineer's first hour in a codebase is spent building a
map — because time spent mapping is typically repaid many times over by not
debugging changes made on wrong assumptions. This skill is that first hour, compressed into commands.

**Rule zero: the repo is the truth; the README is a claim.** Everything a doc
says gets verified against code, config, CI, and an actually-executed command
before you rely on it.

**Rule one: the survey itself is read-only.** Don't install, migrate, "fix"
things in passing, or mutate git state while mapping (running the test suite,
1.3, is the sanctioned exception). Capture a baseline before you start and
compare after — identical output, modulo artifacts your own test run created,
proves the survey changed nothing:

```sh
# POSIX (Git Bash) — GIT_OPTIONAL_LOCKS=0 keeps the read from taking repo locks
GIT_OPTIONAL_LOCKS=0 git status --porcelain=v1 --branch
```

```powershell
# PowerShell
$env:GIT_OPTIONAL_LOCKS='0'; git status --porcelain=v1 --branch
```

Secret-bearing paths (`.env`, `*.pem`, `*.key`, `id_rsa*`, anything named
`credentials`/`secrets`) are record-existence-only: note that they exist in
the report; never read or quote their contents.

## Pick a depth level

| Level | Time box | Question it answers | When |
|---|---|---|---|
| 1. Recon | ~10 min | What is this, and how do I run its tests? | Any task in an unfamiliar repo — always do at least this |
| 2. Survey | ~1 hour | Architecture, conventions, history, risk areas | Multi-file changes, reviews, estimating work |
| 3. Deep audit | half day+ | Full picture feeding a permanent doc layer | Installing the harness — output feeds **brain-harness-bootstrap** |

Each level includes the ones above it. Stop when the time box expires and
record open questions rather than overrunning — unanswered questions in the
report are a valid output.

## Level 1 — 10-minute recon

### 1.1 Identify the stack (2 min)

List the root and glob for manifests. The manifest tells you the language,
package manager, and usually the test runner.

```sh
# POSIX (Git Bash)
ls -a
git ls-files | grep -E '(^|/)(package\.json|pnpm-workspace\.yaml|pyproject\.toml|requirements.*\.txt|setup\.py|Cargo\.toml|go\.mod|pom\.xml|build\.gradle.*|.*\.csproj|.*\.sln|Gemfile|composer\.json|Makefile|Dockerfile|docker-compose.*)$'
```

```powershell
# PowerShell
Get-ChildItem -Force -Name
git ls-files | Select-String -Pattern '(^|/)(package\.json|pnpm-workspace\.yaml|pyproject\.toml|requirements.*\.txt|setup\.py|Cargo\.toml|go\.mod|pom\.xml|build\.gradle.*|.*\.csproj|.*\.sln|Gemfile|composer\.json|Makefile|Dockerfile|docker-compose.*)$'
```

Look for: multiple manifests (monorepo or polyglot — note which directory owns
which), lockfiles (tells you the exact package manager: `pnpm-lock.yaml` vs
`package-lock.json` vs `yarn.lock`), and `Makefile`/`justfile`/`Taskfile.yml`
(often the real command entry point regardless of stack). The full
manifest→stack→toolchain table lives in **brain-build-and-env** — go there to
actually set the environment up; here you only need identification.

### 1.2 Read the front matter (3 min)

Open, in order: `README.md` (skim: purpose, run/test instructions — treat as
claims), `CONTRIBUTING.md`, `CLAUDE.md` / `AGENTS.md` / `.cursorrules`, and
`.claude/skills/` (a prior harness install or project skills — if present,
read them before anything else; someone already did this work).

### 1.3 Find and RUN the test command (5 min)

Extract the claimed test command from the manifest (`scripts.test` in
package.json, `[tool.pytest.ini_options]` in pyproject.toml, `make test`) —
then execute it. This is the core discipline, not an optional extra:

- **Passes** → you have a verified baseline and a regression net. Record the
  exact command and runtime in the report.
- **Fails or errors** → a finding, not a blocker. Record verbatim output. A
  repo whose tests fail on a clean checkout tells you the README is stale,
  CI runs something different (see 2.3), or setup is required
  (**brain-build-and-env**).
- **No tests found** → also a finding; it changes how much verification any
  change here needs (**brain-proof-and-analysis**).

If a full run is slow, time-box it: run one test file or the fastest suite,
and note "full suite unverified" in the report. Never write "tests: `npm
test`" in a report without having run it — that violates non-negotiable #1
(home: **brain-change-control**).

## Level 2 — 1-hour survey

Budget: ~15 min structure, ~20 min history, ~15 min CI + docs, ~10 min
writing the report. All `git log` commands below work identically in Git Bash
and PowerShell unless a separate form is shown.

### 2.1 Structure and entrypoints (~15 min)

- Map the tree: `git ls-files | head -100` and directory sizes:

  ```sh
  # POSIX — file count per top-level directory
  git ls-files | cut -d/ -f1 | sort | uniq -c | sort -rn
  ```

  ```powershell
  # PowerShell
  git ls-files | ForEach-Object { ($_ -split '/')[0] } | Group-Object | Sort-Object Count -Descending | Select-Object Count, Name
  ```

- Find entrypoints: `main`/`index`/`app` files, `bin`/`main` fields in
  package.json, `[project.scripts]` in pyproject.toml, `func main()` in Go.
  How to actually launch them is **brain-run-and-operate**'s territory.
- Test-to-code ratio (calibrates how safe changes are):

  ```sh
  # POSIX — test files vs total tracked files
  git ls-files | grep -icE '(^|/)(tests?|specs?|__tests__)(/|$)|\.(test|spec)\.' ; git ls-files | wc -l
  ```

  ```powershell
  # PowerShell
  (git ls-files | Select-String -Pattern '(^|/)(tests?|specs?|__tests__)(/|$)|\.(test|spec)\.').Count; (git ls-files).Count
  ```

  Under ~1:10 in application code means most behavior is unprotected — plan
  extra verification for any change.
- Generated vs. source: read `.gitignore` (what's built where), and check
  suspicious large/uniform files for `@generated` / "DO NOT EDIT" / "This
  file was automatically generated" headers before ever editing them.
  Editing generated output is a classic wasted hour.

### 2.2 Git history mining (~20 min)

This is the survey pass only — one screen of output per command, extract the
signal, move on. Deep mining (blame archaeology, incident chronicles, bisect
forensics) is **brain-failure-archaeology**.

| Command | What to look for |
|---|---|
| `git log --oneline -30` | Commit-message convention (conventional commits? ticket IDs?), current themes, commit granularity, merge vs rebase culture |
| `git log --stat --since="3 months ago" \| head -80` | Which files/dirs are actively worked; big `--stat` footprints flag churny areas |
| `git shortlog -sn --since="1 year ago" HEAD` | Bus factor. One name dominating = one person's mental model is the real documentation |
| `git log --diff-filter=D --summary \| grep "delete mode"` (PS: `\| Select-String "delete mode"`) | What was removed — abandoned subsystems, migrations away from old approaches. Don't reintroduce what was deliberately deleted |
| `git branch -a --sort=-committerdate --format="%(committerdate:short) %(refname:short)" \| head -20` | Stalled branches = abandoned or in-flight work; check before starting anything similar |
| `git log -i --grep="revert" --oneline` | Reverts mark changes the codebase rejected. Several reverts touching one area = a trap; read those commits before working there |

**Verified gotcha (2026-07-10):** `git shortlog` with no revision argument
reads commit data from **stdin** when not attached to a terminal — in a
script or agent shell it silently prints nothing. Always append `HEAD`.

### 2.3 CI discovery (~5 min)

CI configs contain the REAL build/test commands — the ones that must pass —
which regularly differ from the README's claims. Locations to check:

```sh
# POSIX
ls .github/workflows/ .gitlab-ci.yml .circleci/ azure-pipelines.yml Jenkinsfile .buildkite/ bitbucket-pipelines.yml 2>/dev/null
```

```powershell
# PowerShell
Get-ChildItem -Force .github\workflows, .gitlab-ci.yml, .circleci, azure-pipelines.yml, Jenkinsfile, .buildkite, bitbucket-pipelines.yml -ErrorAction SilentlyContinue
```

From each workflow, extract: the exact test/build/lint command lines (`run:`
steps in GitHub Actions, `script:` in GitLab), the language/toolchain
versions pinned there (often more accurate than the README), required
services (databases, containers), and env vars the steps expect. If CI's test
command differs from the manifest's, CI wins — record both and the
discrepancy as a finding.

### 2.4 Hotspot mining (~5 min)

Debt markers — where the bodies are buried:

```sh
# POSIX — list, per-file counts, and total
rg -n "TODO|FIXME|HACK|XXX" | head -40
rg -c "TODO|FIXME|HACK|XXX" | sort -t: -k2 -rn | head -10
rg --count-matches "TODO|FIXME|HACK|XXX" | awk -F: '{s+=$NF} END {print s}'
```

```powershell
# PowerShell — git grep fallback (see note below)
git grep -nE "TODO|FIXME|HACK|XXX" | Select-Object -First 40
(git grep -cE "TODO|FIXME|HACK|XXX" | ForEach-Object { [int]($_ -split ':')[-1] } | Measure-Object -Sum).Sum
```

Note: `rg -c` counts matching **lines**, `--count-matches` counts matches.
On this authoring machine `rg` was on the Git Bash PATH but not the
PowerShell PATH — `git grep -nE` / `-cE` is the fallback that works anywhere
git does. Absolute counts matter less than clusters: one file with 15 FIXMEs
is a finding.

Most-churned files (churn correlates strongly with defect density; a file
that is both churned and TODO-dense is your top risk area):

```sh
# POSIX (Git Bash) — blank-line filter is required or "" tops the list
git log --format=format: --name-only | grep -v '^$' | sort | uniq -c | sort -rn | head -20
```

```powershell
# PowerShell
git log --format=format: --name-only | Where-Object { $_ } | Group-Object | Sort-Object Count -Descending | Select-Object -First 20 Count, Name
```

Both forms verified on this machine 2026-07-10. Add `--since="1 year ago"`
after `git log` on old repos so ancient history doesn't drown current signal.

### 2.5 Docs discovery (~5 min)

```sh
# POSIX
ls README* CONTRIBUTING* ARCHITECTURE* CHANGELOG* LEARNINGS* docs/ doc/ adr/ docs/adr/ docs/decisions/ .claude/skills/ 2>/dev/null
```

```powershell
# PowerShell
Get-ChildItem -Force README*, CONTRIBUTING*, ARCHITECTURE*, CHANGELOG*, LEARNINGS*, docs, doc, adr, .claude\skills -ErrorAction SilentlyContinue
```

**Doctrine-source priority.** Some files don't just describe the repo — they
bind how you must work in it. Read rule-bearing sources in this order; when
they conflict, the higher row wins, and the conflict itself is a finding:

| Priority | Source | Carries |
|---|---|---|
| 1 | Explicit user/session instructions | Overrides everything below |
| 2 | `CLAUDE.md`/`AGENTS.md`, `CONTRIBUTING*`, `SECURITY*`, `CODEOWNERS` | Rules written for contributors and agents: scope limits, approval gates, required checks, ownership |
| 3 | README + manifests | Claimed purpose and commands (verify — rule zero) |
| 4 | CI / release / deploy configs | What must actually pass (2.3 — CI beats README) |
| 5 | Test configs and test trees | Behavior the repo actively enforces |
| 6 | Git history | Unwritten convention: commit style, what gets reverted (2.2) |

A discovered rule that should bind future changes doesn't stay in the survey
report — record it in the doctrine ledger (home: **brain-change-control**).

ADRs (Architecture Decision Records — short docs recording why a decision was
made) and `LEARNINGS.md` are the highest-value reads: they encode intent that
code can't. Check doc freshness against history before trusting one:
`git log -1 --format="%cs" -- README.md` vs. the repo's last commit date. A
README last touched two years ago in an active repo is a claim generator, not
a reference.

### 2.6 Read the weird code

While skimming, flag code that looks wrong but is clearly deliberate: a
redundant-looking double-check, an unexplained `sleep`, a lock around a
"simple" read, a hand-rolled version of a library function, an oddly specific
constant. Weirdness that survived review usually guards an invariant.
Record each as a "suspected invariant" in the report — do NOT clean it up
(**brain-minimal-change**). Turning suspected invariants into a verified
contract doc is **brain-architecture-contract**'s job.

## Level 3 — deep audit

Everything above, un-time-boxed, plus: run the full test suite and the real
build; trace one request/invocation end-to-end through the code; read the
top-5 churned files fully; follow **brain-failure-archaeology** for the
history deep-dive and **brain-architecture-contract** for invariant
extraction. The audit's discovery report is a required input to
**brain-harness-bootstrap**, which turns it into the repo's permanent
project-skill layer — write it knowing it will be consumed, not skimmed.

## Output: the discovery report

Fill `templates/DISCOVERY.md` (in this skill's directory). Rules:

- Every run/test/build command in the report was **executed**, with outcome
  noted (non-negotiable #1). Unexecuted commands go under "Open questions".
- Distinguish **observed** (I ran/read X) from **claimed** (README says Y)
  from **suspected** (this pattern implies Z).
- README-vs-reality discrepancies are findings — list them, don't fix them
  (out-of-scope-work protocol: **brain-change-control**).
- Recon level: fill the first three sections only; that's a valid report.

## When NOT to use this skill

| Situation | Use instead |
|---|---|
| Environment won't build / need toolchain setup | **brain-build-and-env** |
| Need to launch the app, find logs, dev servers | **brain-run-and-operate** |
| Mining history for past failures/incidents in depth | **brain-failure-archaeology** |
| Writing the invariants/decisions contract doc | **brain-architecture-contract** |
| Repo you already know; task is a change | **brain-task-planning** + **brain-minimal-change** |
| Chasing a specific bug | **brain-debugging-playbook** |
| Installing the harness itself | **brain-harness-bootstrap** (it calls back into this skill's deep audit) |

## Provenance and maintenance

- Authored 2026-07-10 on Windows 11, git 2.52.0.windows.1, ripgrep 14.1.1,
  PowerShell 5.1 + Git Bash. All git/rg/PowerShell pipelines above were
  executed against a scratch repo on this machine, including the shortlog
  stdin gotcha, the churn blank-line filter, and both churn forms.
- Merged with the Sol library 2026-07-12: rule one (read-only survey +
  status baseline, both forms executed here 2026-07-12), secret-path
  hygiene, and the doctrine-source priority table.
- May drift: git flag behavior (`shortlog` stdin behavior, `branch --format`
  field names), rg flag names, CI config locations as new CI systems appear,
  the manifest filename list as ecosystems evolve.
- Re-verify quickly in a target repo: `git log --format=format: --name-only |
  grep -v '^$' | sort | uniq -c | sort -rn | head -5` (churn),
  `git shortlog -sn HEAD | head -3` (authors), `rg --version || git grep
  --version` (which search tool exists).
