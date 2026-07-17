<!-- PR description template. Every section required; write "None" rather than
     deleting a heading, so reviewers see the question was considered.
     Writing rules: brain-docs-and-writing. Whether this PR may be opened at
     all (gating checklist): brain-change-control. -->

## What

<!-- 1–3 sentences: the change, stated as an outcome. "Adds X", "Fixes Y so
     that Z". Not a file-by-file tour — the diff already shows that. -->

## Why

<!-- The problem or request this solves, with a reference: issue/task ID,
     bug report, or user request. If a design decision needed judgment, one
     sentence on the alternative rejected and why. -->

Refs: <issue/task ID or link>

## Proof

<!-- Evidence it works: commands actually run and their observed output, per
     the proof-of-work format in brain-validation-and-qa. "CI will catch it"
     is not proof. Include the failing-before / passing-after pair for bug
     fixes. -->

```
<command>
<observed output — trimmed to the load-bearing lines>
```

## Risk

<!-- What could break, who is affected, and why the risk is acceptable.
     Name the blast radius: which callers/consumers/environments touch the
     changed surface. "None" is a legitimate answer for docs-only changes —
     but say it explicitly. -->

## Rollback

<!-- How to undo this if it breaks in production: usually
     `git revert <merge-commit>`. State anything revert does NOT undo:
     migrations applied, data written, caches warmed, config changed. If
     rollback needs more than one command, list the steps. -->
