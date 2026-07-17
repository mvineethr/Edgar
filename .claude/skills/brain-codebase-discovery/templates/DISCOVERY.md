# Discovery report — <repo name>

- Date: <YYYY-MM-DD>
- Depth: recon | survey | deep audit
- Commit surveyed: `git rev-parse --short HEAD` → <sha>, branch <name>
- Author of this report: <who/what>

## Stack

<!-- From manifest detection. Identification only; setup details belong to
     brain-build-and-env. -->

| Facet | Value | Evidence (file) |
|---|---|---|
| Language(s) / runtime | | |
| Package manager | | (lockfile) |
| Frameworks | | |
| Monorepo? | yes/no | |
| CI system | | |

## Verified commands

<!-- Non-negotiable #1: only commands you actually ran, with observed
     outcome. Unrun commands go under Open questions. -->

| Purpose | Exact command | Outcome (observed) |
|---|---|---|
| Test | | e.g. "142 passed, 3 skipped, 41s" or verbatim error |
| Build | | |
| Lint/format | | |

## Entrypoints

<!-- main/index/bin/app files; what each starts. Launch details:
     brain-run-and-operate. -->

- <path> — <what it is>

## Conventions observed

<!-- From code + last 30 commits: commit-message style, naming, layout,
     error-handling patterns, test placement. Observed, not aspirational. -->

-

## History signals

| Signal | Finding |
|---|---|
| Active areas (3-month `--stat`) | |
| Bus factor (`shortlog -sn HEAD`) | |
| Top churned files | |
| Notable deletions (`--diff-filter=D`) | |
| Stalled branches | |
| Revert clusters | |
| TODO/FIXME clusters | |

## Suspected invariants

<!-- Weird-but-deliberate code implying a rule. Do not clean up; candidates
     for brain-architecture-contract. -->

- <file:line> — <what it does> — <what rule it probably guards>

## Risks and discrepancies

<!-- Includes README-vs-reality findings. Report, don't fix
     (brain-change-control out-of-scope protocol). -->

- <claim vs. observed reality, with evidence>

## Open questions

<!-- Unverified claims, commands not yet run, areas not explored. A
     time-boxed report with open questions beats an overrun one. -->

- [ ]
