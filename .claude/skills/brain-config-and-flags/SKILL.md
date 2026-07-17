---
name: brain-config-and-flags
description: >
  Discover, trace, catalog, and verify every configuration axis in a repo:
  env vars, CLI flags, config files, feature flags, build modes/profiles, and
  per-environment overrides — defaults, allowed values, precedence (which
  source wins when several set the same key), guards, consumers, and
  production-vs-experimental status. Load when asked "what controls this
  behavior?"; when auditing or inventorying config; when adding,
  removing, or renaming a flag/env var/config key; when the value in effect
  doesn't match what you set (precedence bug); when rolling out or
  deprecating an option; or when checking drift between code and the catalog
  (docs/CONFIG.md). Provides enumeration commands for unfamiliar repos, the
  per-axis catalog entry format (HOME of the config-catalog method used by
  brain-harness-bootstrap Phase 4), effective-value tracing per stack, the
  add-a-new-flag checklist, and drift re-verification. NOT for env setup
  (brain-build-and-env), running the app (brain-run-and-operate), or reading
  secret values (never).
---

# brain-config-and-flags — map every input that selects behavior

A **configuration axis** is any input that can change what the software does
without changing its source code: an environment variable, CLI flag, config
file key, feature flag, build mode/profile, or per-environment override.
This skill builds an evidence-backed catalog of those axes and keeps it true.
Treat the repo as unknown until its own artifacts prove otherwise: every fact
in the catalog cites a `file:line`, an executed command's output, or a commit.

## 1. Vocabulary — define once, use everywhere

| Term | Definition |
|---|---|
| Axis | One independently resolved input that selects behavior (see list above) |
| Declaration | The code or schema that names the axis and defines its type, validation, and default |
| Provider | A source that supplies a value: config file, environment, CLI, remote flag service, build define |
| Consumer | The code that reads the resolved value and changes behavior because of it |
| Default | The value that actually executes when no provider wins — never infer it from an example file |
| Precedence | The ordered rule deciding which provider wins when several set the same key, including merge-vs-replace semantics |
| Guard | Whatever catches an invalid or misused value: schema validation, startup assert, CI check — or NONE |
| Feature flag | A runtime axis meant to vary behavior independently of a release (kill switches included) |
| Drift | Disagreement between the catalog and reality: stale entries, missing entries, wrong defaults |

Two rules that prevent most config bugs in reports:

- **Declaration ≠ supplied value ≠ resolved value ≠ observed behavior.**
  Evidence for one does not prove the others. A schema default can be
  overridden by a parser; a deployment template can prevent a code default
  from ever running. Say which of the four you actually verified.
- **Precedence is a first-class fact, not a footnote.** "Which source wins?"
  must be answered from the loading code that executes, not from framework
  folklore. Typical (but never assumed) order: CLI flag > env var > local
  config file > shared config file > built-in default. Note merge behavior:
  deep merge, shallow merge, first-wins, last-wins.

## 2. Enumerate the axes in an unfamiliar repo

Run all of these from the repo root and union the results. Hits are
candidates, not an inventory — trace each one (§3) before cataloging.
All commands verified on the authoring machine unless flagged.

**1. Env vars** — use the read-site discovery and name-extraction patterns in
`brain-build-and-env` §6 (their home; not restated here). Also from §6: check
`.env.example`, compose `environment:` blocks, CI `env:` blocks, and any
config-schema module — when a schema exists, it is the most complete
inventory.

**2. Config files** — same command both shells (`rg` is ripgrep):

```sh
git ls-files | rg -i '(^|/)(\.env|config|configs|settings|flags?|features?|experiments?|profiles?|overrides?)([./_-]|$)|\.(ya?ml|json|toml|ini|conf|properties|xml)$'
```

Extend with what discovery found (`*.csproj`, Helm `values.yaml`,
`app.config`, …). `git ls-files` omits untracked/ignored files — a local
`.env` will not appear; that does not mean it is absent.

**3. Config schemas** — the highest-value find; a typed schema declares
names, types, and defaults in one place:

```sh
rg -n -i "z\.object|zod|BaseSettings|pydantic|convict|ajv|joi\.|jsonschema" .
```

**4. CLI flags** — two angles. Definition sites:

```sh
rg -n -i "argparse|add_argument|click\.option|yargs|commander|clap::|pflag\.|cobra\.|flag\.(String|Bool|Int)" .
```

Then run each entrypoint's help and capture it (entrypoints per
`brain-run-and-operate`): `node dist/cli.js --help`,
`python -m <package> --help`, `<binary> --help`. NOT executed on the
authoring machine — entrypoint-specific; run against the target's real
entrypoints. Help output is a claim; the parser code is the fact — diff them
(undocumented flags are drift, §6). A literal scan catches flags mentioned in
docs, scripts, and CI that the parser scan misses:

```sh
rg -n --hidden -g '!**/.git/**' -g '!**/node_modules/**' -e '--[a-z][a-z0-9-]+' --only-matching . | sort -u
```

**5. Feature flags**:

```sh
rg -n -i "feature[_-]?flag|isEnabled|kill[_-]?switch|LaunchDarkly|unleash|growthbook|statsig|flagsmith" .
```

Add the project's own flag-helper name once the first hit reveals it. If a
remote flag service is in use, the dashboard state is a provider you cannot
see from the repo — record `remote state not inspected` rather than guessing.

**6. Build modes / profiles** — manifest scripts (`package.json` scripts,
Makefile targets, cargo profiles, tox envs, dotnet configurations) plus mode
variables the env-var pass surfaced (`NODE_ENV`, `DEBUG`, `RAILS_ENV`, …).

**7. CI and deployment env blocks** — CI-set variables are providers too:

```sh
rg -n -A3 '^\s*env(ironment)?:' .github .gitlab-ci.yml docker-compose.yml 2>/dev/null
```

(Adjust paths to the CI system discovery found.)

## 3. The catalog — one entry per axis (HOME of this format)

The catalog lives at **`docs/CONFIG.md`** in the target repo (or the repo's
existing config doc if one is already the doc-of-record —
`brain-docs-and-writing`; never create a second home). One entry per axis;
every field evidenced:

```markdown
### <AXIS_NAME>  (env var | CLI flag | config key | build mode | feature flag)
- Type / allowed values: <type; enum/range/pattern; what happens on an invalid value>
- Default: <value> — evidence: <file:line or executed command + output>
- Precedence: <ordered providers for this key, merge rule> — evidence: <file:line of loading code>
- Status: production | experimental | deprecated — evidence: <commit/PR/annotation/usage>
- Guard: <validation, CI check, or startup assert that catches misuse> — or NONE (flag it)
- Consumer: <symbol or file:line that reads it, and the behavior it changes>
- Verify: <one command that shows the current effective value>
```

Entry discipline:

- **Status comes from evidence, not names.** An option named `experimental_x`
  may be load-bearing in production; a default-off flag may be production-
  reachable. Cite the annotation, rollout PR, or deployment artifact.
- **A guard of NONE is a finding.** Flag it in the entry; adding the guard is
  a separate, gated change (`brain-change-control`).
- **Unknown stays unknown.** If you cannot prove the default or precedence,
  write `UNKNOWN — <what evidence is needed>` rather than a plausible guess.
- **Never record secret values.** For secret-bearing axes record the name,
  expected shape, and source class only (discipline: `brain-build-and-env`
  §6). `SECRET — value not inspected` is a complete entry.

## 4. Trace the effective configuration

To answer "what value is actually in effect right now": walk the precedence
chain and then confirm with a dump from the running process — the dump is the
only ground truth. Per stack (all verified on the authoring machine
2026-07-11 except where flagged):

| Stack | Dump technique |
|---|---|
| Node | `node -e "console.log(JSON.stringify({KEY: process.env.KEY ?? '(unset)'}))"` — or the app's own config module: `node -e "console.log(require('./src/config'))"` (path varies; unverified) |
| Python | `python -c "import os; print(os.environ.get('KEY'))"` — or import the settings module and print it |
| Shell env (POSIX) | `printenv KEY` |
| Shell env (PowerShell) | `$env:KEY` — all at once: `Get-ChildItem Env:` |
| Layered config files | Find a `--show-origin`-style dump. Model: `git config --list --show-origin` prints every key with the file that supplied it — the ideal precedence walk; look for the target stack's equivalent |
| docker compose | `docker compose config` prints the fully-merged effective file (and fails loudly on invalid config — verified as a validator here) |
| Web app | A debug/health endpoint that echoes non-secret config, if one exists — never add one without gating (`brain-change-control`) |

**The prod-parity trap**: testing with a different configuration than
production tests a different program. Before claiming a config-sensitive fix
works, state which axis values were in effect during the proof run
(`brain-validation-and-qa` proof-of-work) and how they compare to
production's. "Works with `DEBUG=1`" is not evidence it works with `DEBUG=0`
if any consumer branches on it.

## 5. Add a new axis — the checklist

A config change that alters runtime behavior is at least **Standard** class;
touching auth, data, money, or pipeline config is **Risky**
(`brain-change-control` §1 — classify before you start).

1. **Choose and justify the default.** The default must be the safe /
   production value; write one line of reasoning in the catalog entry.
   Default-off is not automatically harmless — absence, empty, `0`, and
   `false` may mean different things; define which.
2. **Declare it in the repo's one config home** (schema module,
   `.env.example`, flag registry — whichever this repo treats as canonical).
   Never a second home.
3. **Add a guard**: schema validation, startup assert, or CI check that
   catches an invalid value before first unsafe use — or record NONE with a
   reason in the catalog entry.
4. **Env var → `.env.example` in the same diff** (same-diff rule:
   `brain-build-and-env` §6).
5. **Catalog entry** (§3 format) with every field evidenced, plus a test
   exercising the non-default path.
6. **Update the docs-of-record** that mention configuration (README setup
   section, ops runbook) in the same change (`brain-docs-and-writing`).
7. **Experimental flags default OFF and are labeled `candidate`** in the
   catalog. An experiment gets a lifecycle — hypothesis, numbers, adopt or
   retire (`brain-research-methodology`); a flag with no retirement plan is a
   permanent axis and must be justified as one.
8. **Verify precedence**: set the new key via two providers at once and
   confirm the documented winner wins (dump technique from §4). Cite the
   output.

Removing or renaming an axis is the same checklist in reverse, plus a
deprecation window if anything outside the repo (deploy configs, user
scripts) may supply the old name — search for the old name in CI and
deployment artifacts before deleting the alias.

## 6. Config drift — re-verify the catalog

Drift has two directions; check both:

| Direction | Meaning | Detection |
|---|---|---|
| Stale catalog | Entry exists; axis was removed/renamed in code | For each cataloged name: `rg -n "<AXIS_NAME>" .` — zero hits outside the catalog = stale |
| Uncataloged axis | Code axis with no entry | Re-run every §2 enumeration command; diff the union against the catalog's entry list |

Additions and removals both count as drift; so do changed defaults (re-check
each entry's `Default:` evidence against current code) and dead `Verify:`
commands (re-run them). Fix drift as a docs-only change unless the fix
touches code. Run this check when the maintenance loop triggers it — a
flag/env var/config key added, removed, or repurposed — and quarterly
(`brain-harness-bootstrap` §5).

Special case of stale: a flag whose consumer was deleted but whose
declaration survives. It parses, it validates, it does nothing. Detect by
checking each axis has a live consumer, not just a live declaration.

## 7. When NOT to use this skill

| Situation | Use instead |
|---|---|
| Setting up toolchain, dependencies, or `.env` for a build | `brain-build-and-env` (this skill maps axes; that one makes the environment work) |
| Starting the app, dev servers, logs, deploy | `brain-run-and-operate` |
| Reading or handling secret VALUES | Never — record names and shapes only; discipline is `brain-build-and-env` §6 |
| A live failure that might be config-related | `brain-debugging-playbook` (hypothesis loop first; return here when the question is "what does this axis do") |
| Deciding whether a config change is allowed and its gate | `brain-change-control` |
| Generating a target repo's project-specific config catalog during bootstrap | `brain-harness-bootstrap` Phase 4 — which applies THIS skill's method |
| Whether an experimental flag should graduate or retire | `brain-research-methodology` |

## Provenance and maintenance

- Authored 2026-07-11 for the brain core harness, adapted from the Sol
  library's config-and-flags runbook (2026-07-09) merged with the
  config-catalog method formerly in `brain-harness-bootstrap` Phase 4 (this
  skill is now that method's home).
- Verified on the authoring machine 2026-07-11 (Windows 11, PowerShell 5.1 +
  Git Bash, ripgrep 14.1.1, node v24, Python 3.13, git 2.52, docker compose):
  the §2 config-file / schema / CLI-parser / flag-literal / feature-flag /
  env-block searches, each against a scratch repo seeded with matching and
  non-matching files; the §4 Node/Python/printenv/`$env:`/
  `Get-ChildItem Env:` dumps; `git config --list --show-origin`;
  `docker compose config` (exercised as a validator).
- NOT executed here (run in the target repo): CLI `--help` enumeration
  (entrypoint-specific); app-specific config-module dumps; remote
  flag-service state inspection; debug/config endpoints.
- May drift: the flag-SDK vendor list in §2 step 5 (LaunchDarkly/unleash/
  growthbook/statsig/flagsmith) and the schema-library list in step 3
  (zod/pydantic/convict/ajv/joi) as ecosystems change; sibling skill names
  and section numbers (`brain-build-and-env` §6 is the load-bearing one).
- One-line re-verification: in any repo, run the §2 config-file search and
  one §4 dump; both should run clean. If `brain-harness-bootstrap` Phase 4
  stops referencing this skill as the method home, reconcile the two.
