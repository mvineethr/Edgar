---
name: brain-build-and-env
description: >-
  Load when you must set up, repair, or reason about a project's build
  environment: cloning an unfamiliar repo and needing install/build/test
  commands, deciding which package manager a repo uses (npm vs pnpm vs yarn vs
  bun; pip vs uv vs poetry), discovering pinned tool versions (.nvmrc,
  .python-version, .tool-versions, rust-toolchain.toml, engines), creating a
  Node/Python/Go/Rust environment from scratch, or hitting install/build
  failures that smell environmental (wrong version, lockfile conflict, CRLF
  damage, EBUSY/EPERM file locks, missing native libs, stale codegen, path
  or shell-syntax errors on Windows).
  HOME of the stack detection table (manifest → ecosystem → commands) and the
  Windows/POSIX traps table — siblings reference these here. Also covers
  lockfile discipline (npm ci vs npm install; never regenerate a lockfile to
  "fix" an install), and .env/secrets discipline including how to discover
  required env vars in an unfamiliar repo. NOT for running/operating the app —
  that is brain-run-and-operate.
---

# brain-build-and-env

Goal: given any repository, identify its stack, recreate a working build
environment, and PROVE it works with a canary command — before writing any
code. "Canary" = the smallest command whose success demonstrates the
environment is real (per non-negotiable #1, "no done without executed proof";
rationale in `brain-change-control`).

Order of operations in an unfamiliar repo:

1. Detect the stack (section 1) — look at manifest files in the repo root.
2. Check version pins (section 2) — BEFORE installing anything.
3. Read the repo's own docs first: `README.md`, `CONTRIBUTING.md`,
   `docs/development*`, `Makefile`/`justfile`/`Taskfile.yml` targets, and
   `.github/workflows/*.yml` (CI is executable documentation — the install and
   test commands CI runs are the ones that actually work).
4. Install using the recipe (section 3), respecting lockfiles (section 4).
5. Run the canary. Only then start the actual task.

## 1. Stack detection table (HOME of this fact)

Detect by manifest file in the repo root (and one level down in monorepos).
Multiple manifests = polyglot repo; set up each stack you will touch.

| Manifest file | Ecosystem | Install | Typical build / test |
|---|---|---|---|
| `package.json` | Node.js / JS / TS | See lockfile disambiguation below | `npm run build` / `npm test` (read the `scripts` field — it is the source of truth) |
| `pyproject.toml` | Python (modern) | `uv sync` if `uv.lock` exists; else `pip install -e .` in a venv | `pytest` / `python -m pytest`; check `[tool.*]` sections for task runners (hatch, poe, tox) |
| `requirements.txt` | Python (classic) | `pip install -r requirements.txt` in a venv | `pytest` or whatever README says |
| `Pipfile` / `Pipfile.lock` | Python (pipenv) | `pipenv install --dev` | `pipenv run pytest` |
| `uv.lock` | Python (uv) | `uv sync` | `uv run pytest` |
| `go.mod` | Go | `go mod download` (usually implicit) | `go build ./...` / `go test ./...` |
| `Cargo.toml` | Rust | `cargo fetch` (usually implicit) | `cargo build` / `cargo test` |
| `pom.xml` | Java (Maven) | `mvn install -DskipTests` (or `./mvnw` wrapper if present — prefer the wrapper) | `mvn test` |
| `build.gradle` / `build.gradle.kts` | Java/Kotlin (Gradle) | `./gradlew build -x test` (prefer wrapper over global `gradle`) | `./gradlew test` |
| `Gemfile` | Ruby | `bundle install` | `bundle exec rake test` / `bundle exec rspec` |
| `*.csproj` / `*.sln` | .NET | `dotnet restore` | `dotnet build` / `dotnet test` |
| `Dockerfile` | Any (containerized) | `docker build -t <name> .` | Container may BE the dev env — check README for devcontainer/compose usage |
| `docker-compose.yml` / `compose.yaml` | Multi-service | `docker compose up -d` (often just for deps: DB, cache) | `docker compose ps` to confirm services healthy |
| `Makefile` | Any (task runner) | `make` with no args or `make help` lists targets; common: `make install`, `make setup` | `make test` — read the Makefile, it usually wraps the real commands above |

### Node lockfile disambiguation — pick the package manager the repo chose

Wrong package manager = corrupted lockfile or phantom dependency drift. Check
in this order; the lockfile decides, not your habit:

| Present in repo root | Package manager | Install (CI-faithful) | Install (dev) |
|---|---|---|---|
| `package-lock.json` | npm | `npm ci` | `npm install` |
| `pnpm-lock.yaml` | pnpm | `pnpm install --frozen-lockfile` | `pnpm install` |
| `yarn.lock` | yarn | `yarn install --frozen-lockfile` (classic) / `yarn install --immutable` (berry, has `.yarnrc.yml`) | `yarn install` |
| `bun.lockb` or `bun.lock` | bun | `bun install --frozen-lockfile` | `bun install` |
| none | undetermined | Check `package.json` `packageManager` field; else ask or default to npm | — |

- The `packageManager` field in `package.json` (e.g. `"pnpm@9.1.0"`) is
  authoritative. Activate it with corepack: `corepack enable` then run the
  named manager (corepack 0.34.5 ships with Node 24, verified 2026-07-10;
  deprecated and slated for removal in newer Node majors — if `corepack` is
  missing, installing the manager globally (`npm install -g pnpm`) mutates
  the machine: ask first, the same gate section 2 applies to version
  managers).
- Two different lockfiles present = repo hygiene problem. Use the one matching
  `packageManager`; flag the stray lockfile as out-of-scope cleanup per
  `brain-change-control` — do not delete it as a drive-by.

## 2. Version pinning discovery

Check these BEFORE installing. A pin means the project is known-good at that
version and possibly broken elsewhere.

| File / field | Pins | Read it with |
|---|---|---|
| `.nvmrc`, `.node-version` | Node version | `cat .nvmrc` |
| `package.json` → `engines.node` | Node version range | look at the JSON |
| `.python-version` | Python version (pyenv / uv both honor it) | `cat .python-version` |
| `pyproject.toml` → `requires-python` | Python version range | look at the TOML |
| `.tool-versions` | Many tools at once (asdf / mise) | `cat .tool-versions` |
| `rust-toolchain.toml` / `rust-toolchain` | Rust toolchain (rustup honors it automatically) | `cat rust-toolchain.toml` |
| `go.mod` → `go` directive | Minimum Go version | `head go.mod` |
| `global.json` | .NET SDK version | `cat global.json` |

When the pinned version is NOT installed:

1. Use the version manager if one is present: `nvm install <ver> && nvm use
   <ver>` (nvm-windows syntax; POSIX nvm: `nvm install` reads `.nvmrc`
   automatically), `pyenv install <ver>`, `uv python install <ver>` (uv
   downloads Pythons itself), `rustup toolchain install <ver>`,
   `asdf install` / `mise install` (read `.tool-versions`).
2. If no version manager exists, STOP and ask before installing one or
   proceeding on a different version. **Never silently use a different MAJOR
   version** — subtle breakage (lockfile churn, syntax support, ABI) will
   surface later and be blamed on your code change.
3. Same minor/patch within the pinned major is usually fine for a dev task;
   say explicitly in your report which version you actually used vs the pin.

## 3. From-scratch environment recipes

Each recipe ends with a canary. Do not proceed past a failed canary — fix the
environment first (`brain-debugging-playbook` if the failure is mysterious).
Versions on the authoring machine, verified 2026-07-10: Node v24.13.0 /
npm 11.6.2, Python 3.13.5, uv 0.11.7, go 1.25.6, git 2.52.0.

### Node.js

```sh
node --version && npm --version     # confirm runtime matches section-2 pin
npm ci                              # or the manager/flags from section 1
npm test -- --help 2>/dev/null || npm run     # discover script names
```

Canary: `npm run build` if a build script exists, else `node -e
"require('./package.json')"` plus the smallest test:
`npx vitest run <one-test-file>` / `npx jest <one-test-file>`.

### Python (venv — stdlib, always available)

POSIX:
```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt    # or: pip install -e ".[dev]"
python -c "import sys; print(sys.prefix)"   # canary: prints path INSIDE .venv
```
PowerShell (verified 2026-07-10):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -c "import sys; print(sys.prefix)"
```
If `Activate.ps1` is blocked by execution policy, run
`Set-ExecutionPolicy -Scope Process RemoteSigned` first, or skip activation
and call `.\.venv\Scripts\python.exe` explicitly — activation is convenience,
not magic.

### Python (uv — preferred when `uv.lock` or `[tool.uv]` exists)

```sh
uv sync                 # creates .venv, installs pinned Python + deps
uv run python -c "import sys; print(sys.prefix)"   # canary
uv run pytest -x        # or the smallest test
```
(`uv venv .venv` alone also works for a bare venv — verified 2026-07-10.)

### Go

```sh
go version              # match against go.mod directive
go build ./...          # canary: compiles everything, downloads modules
go test ./... -count=1 -run TestNothingMatches   # cheap full-compile of tests
```

### Rust — UNVERIFIED on authoring machine (no rustup installed); standard documented usage

```sh
rustup show             # confirms toolchain; honors rust-toolchain.toml
cargo build             # canary
cargo test --no-run     # compile tests without running them
```

### Beyond the package manager — native deps, codegen, install hooks

- **Native dependencies** (OS libraries, headers, compilers, drivers) are not
  installed by the language package manager. Evidence for what a repo needs
  lives in its Dockerfile/devcontainer `apt-get`/`apk` lines and CI install
  steps — read those before debugging a cryptic build of anything with a C
  extension (`node-gyp`, `psycopg2`, `sharp`, `cryptography`). A successful
  `npm install`/`pip install` does not prove native linkage worked; only the
  canary does.
- **Codegen before build**: if the repo has generated sources (protobuf,
  GraphQL codegen, ORM clients, OpenAPI stubs), run the generation step before
  building — stale generated output produces phantom type/build errors.
  Telling generated from source files: `brain-run-and-operate` §4.
- **Installs execute code.** Lifecycle hooks (npm `postinstall`, Python build
  backends, Gradle plugins) run arbitrary code during "install". For an
  unfamiliar or untrusted dependency this deserves a pause, not a silent
  bypass — disabling hooks (npm's documented `--ignore-scripts`; not
  machine-verified here) breaks packages that need them, so treat it as a
  deliberate, reported choice.

## 4. Lockfile discipline

A lockfile is a recorded, reviewed decision about exact dependency versions.
Treat modifying one as a **dependency change**, not an install detail.

- **Never delete or regenerate a lockfile to "fix" a failing install.** That
  converts an environment problem into an unreviewed mass dependency bump —
  classify per `brain-change-control` (dependency bumps are Standard at
  minimum, Risky for major versions) and gate it accordingly. First suspect
  instead: wrong package manager (section 1), wrong runtime version
  (section 2), stale cache (`npm cache verify`), corporate proxy/registry.
- **CI-faithful vs mutating installs.** `npm ci` installs EXACTLY the
  lockfile and fails loudly on any mismatch with `package.json`; `npm install`
  will happily rewrite the lockfile to make things fit. Use the `ci` form for
  setup and reproduction; use the mutating form only when you intend to change
  dependencies. Equivalents: `pnpm install --frozen-lockfile`,
  `yarn --frozen-lockfile` / `--immutable`, `bun install --frozen-lockfile`,
  `uv sync --locked`, `pipenv install --deploy`, `bundle install` with
  `bundle config set frozen true`, `cargo build --locked`.
- If a lockfile changed in your `git status` and you didn't intend a
  dependency change, restore it (`git checkout -- <lockfile>`) and rerun the
  frozen install.

## 5. Windows/POSIX traps table

Each row: symptom → cause → fix. This is the HOME of these facts.

| Symptom | Cause | Fix |
|---|---|---|
| Diff shows every line changed; `^M` in files; bash script fails with `\r: command not found` | CRLF/LF conversion; `core.autocrlf=true` (Windows default; true on this machine) checks out CRLF | Respect the repo's `.gitattributes` if present. For a broken script: `git checkout -- <file>` after adding `*.sh text eol=lf` to `.gitattributes`, or `dos2unix <file>`. Never mass-convert line endings as a drive-by (see `brain-minimal-change`) |
| Path works on Windows, breaks in CI (or vice versa) | `\` vs `/` separators; Windows-only drive letters | Use `/` everywhere — Windows APIs and Node/Python accept it. Build paths with `path.join` (Node) / `pathlib` (Python), never string concat |
| File found locally, "not found" on Linux CI | Case-insensitive NTFS vs case-sensitive ext4; import says `Utils.ts`, file is `utils.ts` | Match the exact on-disk casing; `git mv utils.ts utils2.ts && git mv utils2.ts Utils.ts` to change casing in git on Windows |
| `The token '&&' is not a valid statement separator` | PowerShell 5.1 has no `&&`/`\|\|` | In PS 5.1: `cmdA; if ($?) { cmdB }`. Or run the one-liner in Git Bash where `&&` works |
| `$VAR` empty in PowerShell, `%VAR%` printed literally in bash | Env var syntax differs per shell | bash: `$VAR` / `VAR=x cmd`; PowerShell: `$env:VAR` / `$env:VAR='x'; cmd`; cmd.exe: `%VAR%`. There is no inline `VAR=x cmd` form in PowerShell |
| `ENAMETOOLONG` / `Filename too long` on checkout or install | Windows 260-char path limit; deep `node_modules` | `git config --global core.longpaths true`; enable OS long paths (admin): registry `LongPathsEnabled=1`; clone to a short root like `C:\src` |
| `EBUSY`, `EPERM`, `Access is denied` deleting/renaming during install or build | Another process holds the file: editor, dev server, antivirus, Explorer preview, OneDrive sync | Stop dev servers/watchers, close handles, retry. Recurring: exclude the repo dir from Defender/OneDrive. Do NOT escalate to `rm -rf` with force flags as a reflex (`brain-change-control` stop-and-ask list) |
| `./script.sh` does nothing or opens in an editor on Windows | Shebang (`#!/usr/bin/env bash`) only works in a POSIX shell | Run via Git Bash (`bash script.sh`) or use the repo's `.ps1`/`.cmd` sibling if provided. When authoring cross-platform scripts, ship both forms or use a Node/Python entrypoint |
| Quoted args mangled (`"it's"` / JSON on the command line) | bash and PowerShell quote/escape rules differ; PS 5.1 re-parses native-command args | Prefer writing payloads to a temp file over inline quoting; in PS use single-quoted here-strings `@'...'@` for literals |
| File written from PowerShell has mangled non-ASCII chars (em-dashes, accents) or an unexpected BOM | PowerShell 5.1's default output encoding is not UTF-8 (`Out-File`/`>` write UTF-16; `Add-Content` uses ANSI) | Pass `-Encoding utf8` explicitly on `Out-File`/`Set-Content`/`Add-Content` in PS 5.1 (PowerShell ≥6 defaults to UTF-8) |
| `curl` in PowerShell ignores flags like `-s`/`-w`, returns an object, or errors on standard curl syntax | In PS 5.1 `curl` is an alias for `Invoke-WebRequest`, not the curl binary | Call `curl.exe` explicitly in PowerShell; plain `curl` works in Git Bash/POSIX shells |
| Build works in WSL, claimed as "works on Windows" (or vice versa) | WSL is a Linux environment with its own filesystem, toolchain, and case sensitivity | Never present WSL results as native-Windows verification or vice versa — state which environment each command ran in, and run the canary in the one the task targets |

## 6. Secrets and .env discipline

- **Never commit a secret.** `.env` belongs in `.gitignore`; check before
  creating one: `git check-ignore .env` (silent exit 0 = ignored). If you find
  a committed secret, stop and report it — rotating is a human decision
  (`brain-change-control` stop-and-ask).
- **`.env.example` convention**: a committed template listing required var
  NAMES with placeholder or empty values. Setup = `cp .env.example .env` then
  fill in real values. If you add a new required env var in a change, add it
  to `.env.example` in the same diff.
- **Discovering required env vars in an unfamiliar repo** (pattern verified
  with ripgrep 14.1.1 on 2026-07-10 against JS/Python/Go samples):

  Find every read site:
  ```sh
  rg -n "process\.env|os\.environ|os\.getenv|os\.Getenv|std::env::var|ENV\[" .
  ```
  Extract just the variable names, deduplicated:
  ```sh
  rg -o --no-filename "(process\.env|os\.environ(\.get)?|os\.getenv|os\.Getenv|std::env::var|ENV)[(\[. ]+['\"]?([A-Z][A-Z0-9_]+)" -r '$3' . | sort -u
  ```
  (The extraction only catches UPPER_SNAKE names — the overwhelming
  convention; fall back to the first command for anything dynamic.) Also
  check: `.env.example`, `docker-compose.yml` `environment:` blocks, CI
  workflow `env:` blocks, and any config-schema module (zod/pydantic
  settings classes) — the schema is the most complete inventory when it
  exists.
- **When a required secret is missing: ask, don't fabricate.** Never invent
  API keys, connection strings, or dummy tokens that let code silently run
  against the wrong backend. Acceptable without asking: obviously-local
  values the repo documents (e.g. `DATABASE_URL` pointing at the
  compose-provided local DB). Everything else: name the exact variable(s)
  and what they gate, then ask the human.

## 7. When NOT to use this skill

- **Starting/running the app, dev servers, logs, deploy** →
  `brain-run-and-operate`. This skill ends when the canary passes.
- **Understanding the codebase's structure and conventions** →
  `brain-codebase-discovery` (this skill only reads manifests and CI, not
  architecture).
- **A build that used to work now fails and the cause isn't an obvious
  env-setup step** → `brain-debugging-playbook` (hypothesis loop, not
  install-command roulette).
- **Deciding whether a dependency/lockfile change is allowed and how to gate
  it** → `brain-change-control`.
- **Proving your CHANGE works (tests, evidence format)** →
  `brain-validation-and-qa`; this skill only proves the ENVIRONMENT works.

## Provenance and maintenance

- Authored 2026-07-10 on Windows 11 (PowerShell 5.1 + Git Bash); revised
  2026-07-10 (review pass: PS-encoding and curl-alias rows added to the traps
  table — this table is their home; ask-first gate on global package-manager
  installs).
- Merged with the Sol library 2026-07-12: absorbed native-dependency/codegen/
  install-hook guidance (section 3) and the WSL-verification trap row.
  `--ignore-scripts` is standard documented npm usage, not machine-verified.
- Verified on the authoring machine 2026-07-10: Node v24.13.0, npm 11.6.2,
  corepack 0.34.5, Python 3.13.5 (`python -m venv` + in-venv canary),
  uv 0.11.7 (`uv venv`), go 1.25.6, git 2.52.0.windows.1 (`core.autocrlf`
  true), ripgrep 14.1.1 (both section-6 patterns), nvm-windows 1.1.11.
- NOT verified on the authoring machine (standard documented usage —
  re-verify in the target repo): all Rust/rustup/cargo commands, pnpm, yarn,
  bun, pipenv, Maven/Gradle, bundler, dotnet, docker commands, pyenv, asdf,
  mise.
- What will drift: tool version numbers above; corepack's bundling status in
  Node (deprecated as of Node 24, 2026-07); package-manager flag spellings
  (`--frozen-lockfile` vs `--immutable`); the Windows long-path story.
- Re-verify quickly: `node --version && npm --version && python --version &&
  git --version` plus one canary from section 3 for the stack you're using;
  rerun the section-6 rg extraction against a file containing a known
  `process.env.X` to confirm the pattern still matches.
