---
name: brain-run-and-operate
description: >-
  Load whenever you need to RUN a project or reason about a running one: finding
  the entrypoint (npm scripts, Makefile targets, Procfile, docker-compose
  services, Python entrypoints, README run instructions), starting a dev server
  in the background and PROVING it is up before claiming so, finding what is
  listening on a port and killing it cleanly by PID, handling port conflicts,
  tailing and filtering logs, correlating a request to a log line, telling
  generated artifacts from source (never hand-edit generated files), and
  discovering deploy configuration (CI workflows, vercel.json, netlify.toml,
  fly.toml, Dockerfile, k8s manifests). Also load when tempted to say "the
  server is running" without a cited HTTP response, when a port is already in
  use, or when asked to deploy — deploying requires explicit human approval
  (see brain-change-control). Environment setup belongs to brain-build-and-env;
  performance measurement to brain-diagnostics-and-tooling.
---

# brain-run-and-operate

How to find a project's entrypoints, run it without leaving a mess, read its
logs, respect its generated artifacts, and locate (but never trigger) its
deploy path. Assumes the environment already builds — if `npm install` /
`pip install` / toolchain setup is the problem, go to `brain-build-and-env`
first.

Give commands in both forms when they differ: **PS** = Windows PowerShell 5.1,
**POSIX** = bash/zsh (incl. Git Bash on Windows).

## 1. Entrypoint discovery

"Entrypoint" = the command a human runs to start, build, or test the project.
Check every artifact below that exists; a repo often has several (e.g. a
Makefile that wraps npm scripts). List what you find before running anything.

| Artifact | Exists-check | Enumerate with |
|---|---|---|
| `package.json` | repo root + workspaces (`packages/*/package.json`) | `npm pkg get scripts` (run in the dir containing the file) — prints the scripts object as JSON |
| `Makefile` | repo root | See extraction command below, or just read the file — targets are lines matching `name:` at column 0 |
| `Procfile` | repo root (Heroku/foreman convention) | Read it: each line is `procname: command` — `web:` is the HTTP server |
| `docker-compose.yml` / `compose.yaml` | repo root | `docker compose config --services` — prints one service name per line |
| `pyproject.toml` | repo root | Read `[project.scripts]` — each `name = "pkg.module:func"` becomes a console command after install |
| `__main__.py` | inside a package dir | `python -m <package>` runs it |
| `manage.py` | repo root (Django) | `python manage.py help` lists subcommands; `runserver` is the dev server |
| `README` | repo root | Read the "Getting started" / "Development" section — then VERIFY it against the artifacts above; READMEs drift (verification protocol: `brain-codebase-discovery`) |

**Makefile targets** — two options, verified:

```bash
# Option 1 (simplest): read declared targets straight from the file
grep -E '^[a-zA-Z0-9][a-zA-Z0-9_.-]*:' Makefile

# Option 2: ask make's database (includes generated/included targets)
make -qp 2>/dev/null | awk -F: '/^[a-zA-Z0-9][^ \t:#=]*:([^=]|$)/ {print $1}' | sort -u
```

Trap (hit while authoring this skill): do NOT use `grep` with `\t` inside a
bracket expression for this — in POSIX grep, `[^\t]` excludes the literal
letter `t`, silently dropping targets like `test`. awk interprets `\t` as a
real tab, so the awk form above is safe.

**Reading compound npm scripts.** A script's value is a shell command; expand
it before judging what it does:
- `"check": "npm run lint && npm run test"` — runs both, stops on first failure.
- `pre<name>` / `post<name>` scripts run automatically around `<name>`
  (`pretest` runs before `test`).
- Tool names (`next dev`, `vite`, `tsc -b`) resolve to `node_modules/.bin/` —
  the real behavior lives in that tool's config file, not the script line.
- A script that itself calls `concurrently` / `run-p` starts multiple
  processes; expect multiple ports.
- Wrapper scripts and task bodies can hide downloads, migrations, deletion, or
  daemonization — read the body before running an unfamiliar target, and treat
  `--dry-run` / `plan` / `preview` modes as potentially mutating until the
  tool's docs prove otherwise.

**Pick the entrypoint deliberately.** Prefer, in order: the README's stated dev
command (once verified it exists), a `dev`/`start` npm script or `make dev`,
`docker compose up` only if the README says development happens in containers.
Do not invent `npm start` because it's common — enumerate first.

## 2. Dev-server discipline

The lifecycle is: **start in background with logs to a file → verify with an
HTTP request → work → kill by PID → confirm the port is free.** Never skip the
verify or the kill.

### 2.1 Start in background, logs to a file

Never start a server in your foreground shell (it blocks you) and never let
its output vanish (you'll need it the moment something 500s).

```powershell
# PS — verified: returns a process object; capture $p.Id immediately
$p = Start-Process npm -ArgumentList 'run','dev' -WorkingDirectory . `
     -RedirectStandardOutput server.out.log -RedirectStandardError server.err.log `
     -PassThru -WindowStyle Hidden
$p.Id   # record this PID — it is your cleanup handle
```

```bash
# POSIX — standard usage (unverified on this authoring machine)
nohup npm run dev > server.log 2>&1 &
echo $!   # PID of the background job — record it
```

If your harness has a dedicated background-execution mechanism (e.g. a
`run_in_background` flag on the shell tool), prefer it over hand-rolled
backgrounding — it tracks the process for you. Still record where the logs go.

### 2.2 VERIFY it is actually up — non-negotiable

"Started the server" is not evidence; a process can be up while the app
crashed during boot. Claim the server is running only after an HTTP request
returned, and cite the status code (this is non-negotiable #1, "no done
without executed proof" — home: `brain-change-control`; proof-of-work format:
`brain-validation-and-qa`).

```powershell
# PS 5.1 — verified (both returned 200 against a local test server)
(Invoke-WebRequest -Uri http://localhost:3000/ -UseBasicParsing).StatusCode
curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:3000/
```

```bash
# POSIX / Git Bash — verified in Git Bash on Windows
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/
```

Notes:
- PS 5.1 needs `-UseBasicParsing`; without it Invoke-WebRequest can hang on IE
  engine dependencies. In PowerShell, `curl` is an alias for Invoke-WebRequest —
  write `curl.exe` to get real curl.
- Servers take seconds to boot. Poll instead of sleeping once:

```powershell
# PS — verified: loops until the port answers or 30 s elapse
$deadline = (Get-Date).AddSeconds(30)
do { Start-Sleep -Milliseconds 300
     $up = Test-NetConnection localhost -Port 3000 -InformationLevel Quiet -WarningAction SilentlyContinue
} until ($up -or (Get-Date) -gt $deadline)
```

- A TCP connect (port open) is weaker evidence than an HTTP 200 (app booted).
  Use the port poll to wait, then the HTTP request to claim.
- 404 from the right server still proves the server is up; 200 from the wrong
  path proves nothing about your route. Hit a URL that exercises your change.
- No HTTP surface (worker, queue consumer, batch job)? Verify via its own
  observable — a readiness log line, an artifact produced, a row written. If
  you cannot verify readiness at all, report exactly "started, readiness
  unverified" — never "running".

### 2.3 Find what is listening on a port

```powershell
# PS — both verified
netstat -ano | findstr :3000                       # last column = PID
Get-NetTCPConnection -LocalPort 3000 -State Listen # OwningProcess column = PID
Get-Process -Id <PID>                              # what is that PID?
```

```bash
# POSIX — standard usage (unverified here; lsof is absent from Git Bash)
lsof -i :3000            # macOS/Linux; PID column
ss -ltnp | grep :3000    # Linux; shows pid= in the process field
```

### 2.4 Kill cleanly — never leave orphaned servers

Every server you start, you stop — before reporting the task done. An orphaned
dev server steals the port from the next session and keeps stale code live.

```powershell
# PS — verified: after Stop-Process the port poll returned False
Stop-Process -Id <PID> -Force
```

```bash
# POSIX — standard usage (unverified here)
kill <PID>          # polite (SIGTERM); give it a second
kill -9 <PID>       # only if it ignored SIGTERM
```

Then confirm: re-run the port check from 2.3 and cite that the port is free.
Kill the PID you recorded at start; if you lost it, recover it via the port
lookup. `taskkill /PID <pid> /F` is the cmd.exe equivalent on Windows.

Caveat: `npm run dev` may spawn a child (node) that survives killing the npm
wrapper. If the port is still busy after the kill, look up the port again —
the listener is the child; kill that PID.

Never kill by process NAME (`pkill node`, `taskkill /IM node.exe`,
`Stop-Process -Name node`) — that terminates every matching process on the
machine, including sessions and services you do not own. PID only.

### 2.5 Port conflicts

Symptom: `EADDRINUSE`, "address already in use", or your "fresh" server serves
stale behavior. Protocol:

1. Identify the holder (2.3) and what it is (`Get-Process -Id` / `ps -p <PID>`).
2. If it's a leftover from YOUR session: kill it (2.4) and restart.
3. If it's not yours (another user's process, a system service, unknown): do
   NOT kill it — that's someone else's state. Run on another port instead
   (`PORT=3001 npm run dev` on POSIX; `$env:PORT=3001; npm run dev` in PS —
   the variable name is project-specific; check the README or the dev script).
4. Testing against a port without checking who owns it is how you "verify"
   against a stale server. If behavior looks impossibly old, check the port
   owner first (`brain-debugging-playbook`, stale-environment trap).

## 3. Log reading

### 3.1 Where logs are

In priority order: (1) the file YOU redirected to at start — this is why 2.1
mandates redirection; (2) files matching `*.log` in repo root, `logs/`,
`var/log/`, `tmp/`; (3) `docker compose logs <service>` for containerized
apps; (4) the framework's convention (Next.js and Vite print to stdout only —
if you didn't redirect, it's gone; Django honors its `LOGGING` setting;
Python's `logging` defaults to stderr).

### 3.2 Tailing

| Task | PS 5.1 | POSIX |
|---|---|---|
| Last N lines | `Get-Content server.log -Tail 50` (verified) | `tail -n 50 server.log` (verified in Git Bash) |
| Follow live | `Get-Content server.log -Tail 50 -Wait` (standard; blocks — use only in a disposable shell) | `tail -f server.log` (standard; blocks) |

In an agent context prefer repeated `-Tail 50` snapshots over `-Wait`/`-f`:
a blocking follow eats your shell.

### 3.3 Filtering for errors

```powershell
# PS — verified
Select-String -Path server.log -Pattern 'error|exception|fatal' | Select-Object -Last 20
```

```bash
# POSIX / Git Bash — verified
grep -inE 'error|exception|fatal|traceback|panic' server.log | tail -n 20
```

Read the FIRST error after your action, not the last line of the file — later
errors are usually cascade. For multi-line stack traces, grab context:
`grep -n -A 15 'Traceback' server.log` / `Select-String -Context 0,15`.

### 3.4 Correlating a request to a log line

1. Note the wall-clock time just before you send the request.
2. Send a request that is unique — a marker query param (`?probe=abc123`) or a
   distinctive path. Most HTTP access logs print the full path, so
   `grep abc123 server.log` finds exactly your request.
3. Match on the timestamp AND the marker; timestamps alone collide under any
   concurrent traffic. Mind timezone: many loggers write UTC while your shell
   clock is local.
4. If the app emits request IDs (common header: `X-Request-Id`), read the ID
   from the HTTP response headers and grep the log for it — strongest link.

## 4. Artifact conventions: generated vs source

"Generated" = produced by a build/codegen step from some source of truth.
Hand-editing a generated file is always wrong: the next build silently erases
your change. Identify the generator and change ITS input instead.

Signals that a file is generated (any one suffices):
- **Listed in `.gitignore`** — check with `git check-ignore -v <path>`
  (verified pattern; prints the ignoring rule) or read `.gitignore`.
- **Header comment** — first ~5 lines saying `GENERATED`, `DO NOT EDIT`,
  `@generated`, or "generated by X". Always read the top of an unfamiliar file
  before editing it.
- **Lives in a known build-output dir**: `dist/`, `build/`, `out/`, `.next/`,
  `target/` (Rust/Java), `bin/`+`obj/` (.NET), `__pycache__/`, `coverage/`,
  `node_modules/`, `.venv/`.
- **Known generated-by-name files**: lockfiles (`package-lock.json`,
  `poetry.lock`, `Cargo.lock` — regenerate via the package manager, never
  hand-edit), `*.min.js`, `*.pb.go`/`*_pb2.py` (protobuf), Prisma client,
  GraphQL codegen output, `*.snap` test snapshots (regenerate via the test
  runner's update flag).

Protocol when a change seems to require touching such a file: find the
generator (search the repo for the file's name in scripts/configs), change the
generator's input, re-run the generating command, and cite its output. If you
cannot find the generator, stop and say so — do not edit the output as a
shortcut. Committing regenerated files follows the repo's convention: if the
output dir is gitignored, never commit it.

## 5. Deploy discovery — and the hard gate

Know where deploys are configured so you can reason about them; FIND, don't
TRIGGER.

Where to look (read-only):

| Artifact | What it tells you |
|---|---|
| `.github/workflows/*.yml` | CI/CD; grep for `deploy`, `release`, `publish` jobs and their `on:` triggers (push to main? tags? manual `workflow_dispatch`?) |
| `vercel.json` / `.vercel/` | Vercel project; pushes to the linked branch may auto-deploy |
| `netlify.toml` | Netlify build command + publish dir |
| `fly.toml` | Fly.io app name and deploy config |
| `Dockerfile` + registry refs in CI | Image-based deploy; find where the image is pushed |
| `k8s/`, `helm/`, `*.yaml` with `kind: Deployment` | Kubernetes manifests |
| `Procfile`, `app.json` | Heroku-style platform |
| `serverless.yml`, `template.yaml`, `cdk.json`, `*.tf` | Serverless/IaC deploy paths |

One search covers most of it:

```bash
# Git Bash — verified pattern form
ls .github/workflows/ vercel.json netlify.toml fly.toml Dockerfile 2>/dev/null
grep -rilE 'deploy|publish|release' .github/workflows/ 2>/dev/null
```

**The hard gate.** Deploying is outward-facing and effectively irreversible:
it changes what other humans see and may be unrecallable (emails sent, caches
populated, versions published). Therefore — NEVER run `vercel --prod`,
`netlify deploy`, `fly deploy`, `git push` to an auto-deploying branch,
`docker push` to a shared registry, `npm publish`, `kubectl apply` against a
shared cluster, or any equivalent, without explicit human approval of that
exact command. This is a stop-and-ask trigger; the full protocol (present
command + blast radius + rollback, wait for approval) is in
`brain-change-control`. Two easy-to-miss cases: (a) pushing to `main` IS a
deploy if a workflow auto-deploys on push — check the `on:` triggers before
pushing; (b) "preview" deploys still publish to a public URL — they are
outward-facing too. Approval is per exact command, revision, and target
environment: an approval for one deploy is never reused for a retry, a
different branch, or a different target — ask again.

## 6. When NOT to use this skill

| Situation | Use instead |
|---|---|
| Dependencies won't install, toolchain/SDK missing, env vars unset, build fails before anything runs | `brain-build-and-env` |
| You need to MEASURE a running system (profiling, timing, resource usage) rather than just operate it | `brain-diagnostics-and-tooling` |
| First contact with an unfamiliar repo — orientation before running anything | `brain-codebase-discovery` |
| The server runs but behaves wrongly and you're diagnosing why | `brain-debugging-playbook` |
| Formatting the evidence that something works into a report | `brain-validation-and-qa` |
| Deciding whether an action needs human approval | `brain-change-control` |

## 7. Provenance and maintenance

Merged with the Sol library 2026-07-12: absorbed the wrapper/dry-run-may-mutate
caution (§1), non-HTTP readiness verification and the "started, readiness
unverified" honesty rule (§2.2), the kill-by-PID-only rule (§2.4), and the
per-command/revision/environment approval scope on the deploy gate (§5).

Authored 2026-07-10 on Windows 11 (PowerShell 5.1.26100, Git Bash, GNU Make
4.4.1, Docker 28.2.2, npm 10.x, Python 3.13). Verified end-to-end on that
machine: `npm pkg get scripts`; both Makefile-target extractions (incl. the
grep-`\t` trap); `docker compose config --services`; the full server lifecycle
(Start-Process w/ log redirection → port poll → Invoke-WebRequest and curl 200
→ `netstat -ano | findstr` → `Get-NetTCPConnection` → `Stop-Process` → port
confirmed free); `Get-Content -Tail`; `Select-String`; `tail -n`; `grep -inE`.

NOT verified on the authoring machine (standard documented usage; re-verify on
a POSIX target): `lsof -i`, `ss -ltnp`, `kill`, `nohup … &` / `$!`, `tail -f`,
`Get-Content -Wait`, `taskkill`, Heroku Procfile tooling, `manage.py`,
platform CLIs (vercel/netlify/fly/kubectl).

What may drift: `npm pkg get` (npm ≥ 7 only — fall back to reading
package.json); `docker compose` v2 subcommand syntax; PS 7 removes the
`-UseBasicParsing` requirement; the build-output-dir list as frameworks evolve;
deploy-config filenames as platforms evolve. Re-verify in a target repo with:
`npm pkg get scripts`, `docker compose config --services`, and one full
start→verify→kill cycle from section 2.
