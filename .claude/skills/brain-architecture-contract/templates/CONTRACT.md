# Architecture contract — <repo name>

<!--
What this file is: the repo's load-bearing decisions, invariants, and known
weak points. Read it BEFORE changing anything structural. Authoring and
maintenance rules: .claude/skills/brain-architecture-contract/SKILL.md.

Binding rules:
- Every invariant has a verification command that was actually run.
- This file is updated in the SAME change that alters any entry (gate:
  brain-change-control).
- Entries whose "why" no longer applies are deleted, not left to rot.
-->

**Last full verification** (all invariant commands run top to bottom):
YYYY-MM-DD by <name/agent>
**Verification cadence**: quarterly <!-- or the repo's own cadence -->

---

## 1. Load-bearing decisions

<!-- A decision other code silently depends on: changing it breaks distant
things with no local warning. Record WHY — the failure it prevents — or the
next confident engineer will "clean it up". One block per decision. If an ADR
exists, link it and keep this entry to a summary paragraph. -->

### D-001: <one-line name of the decision>

- **Date**: YYYY-MM-DD
- **Context**: <the situation that forced a choice — 1–3 sentences>
- **Decision**: <what was chosen, stated so a newcomer can comply with it>
- **Why (failure prevented)**: <the concrete failure this prevents; cite the
  incident, commit, or LEARNINGS entry if one exists>
- **Consequences**: <what this makes harder/impossible; what depends on it;
  what to re-evaluate if it's ever changed>
- **Links**: <ADR / issue / incident — optional>

<!-- EXAMPLE (delete after reading):
### D-001: All writes to `orders` go through `OrderRepository`
- Date: 2024-11-02
- Context: Two services wrote to `orders` directly; a race double-decremented
  inventory during the Nov 2024 sale.
- Decision: `OrderRepository` is the only module that issues INSERT/UPDATE on
  `orders`; it holds the row lock and the idempotency check.
- Why: Direct writes bypass the idempotency check → duplicate orders charged.
- Consequences: Bulk backfills must also route through the repository (slower);
  a raw-SQL migration touching `orders` needs explicit review.
- Links: LEARNINGS.md 2024-11-02; ADR-007.
-->

## 2. Invariants

<!-- A property that must ALWAYS hold, with the consequence of violating it.
No verification command → it is not an invariant; write the missing check
first or file it under §3 as unverifiable. The command must exit 0 / print the
expected value when the invariant holds. One block per invariant. -->

### I-001: <the property, stated as a testable sentence>

- **Scope**: <where it applies — table, module, layer, pipeline stage>
- **Why (consequence if violated)**: <the concrete failure — data corruption,
  double-charge, secret leak, silent model skew>
- **Enforced by**: <schema constraint / validator / CI step / nothing-but-convention>
- **Verify**: `<one-line command or single-test invocation>`
- **Expected**: <exit 0 / prints 0 / test passes>
- **Last verified**: YYYY-MM-DD

<!-- EXAMPLE (delete after reading):
### I-001: `orders.total_cents` is never negative
- Scope: `orders` table, all environments.
- Why: refund logic treats negative totals as credit owed → issues real money.
- Enforced by: CHECK constraint in migrations/001_init.sql; also asserted in
  OrderRepository.applyCredit.
- Verify: `psql "$DB_URL" -tAc "SELECT count(*) FROM orders WHERE total_cents < 0"`
- Expected: prints 0
- Last verified: 2026-07-10

### I-002: no `console.log` ships in `src/`
- Scope: src/ (production bundle).
- Why: past incident logged auth tokens to the browser console.
- Enforced by: lint rule `no-console` in CI (`npm run lint`).
- Verify: `! rg -q "console\.log" src/`   (PowerShell: `git grep -qE "console\.log" -- src; $LASTEXITCODE -ne 0`)
- Expected: exit 0 (PowerShell form prints `True`)
- Last verified: 2026-07-10
-->

## 3. Known-weak-points register

<!-- Acknowledged fragility, worded PLAINLY — write it so a newcomer avoids
it, not so the author looks careful. No euphemisms: "loses rows silently",
not "suboptimal edge-case handling". Every entry has a trigger and a blast
radius or it is an excuse, not a register entry. -->

| ID | Weak point (plain words) | Trigger conditions | Blast radius | Mitigation / watch | Accepted on |
|---|---|---|---|---|---|
| W-001 | <what actually goes wrong> | <exact conditions that fire it> | <what breaks, how far> | <workaround, alarm, or "none"> | YYYY-MM-DD |

<!-- EXAMPLE row (delete after reading):
| W-001 | CSV importer drops duplicate-key rows without reporting | any upload with a repeated `sku` column value | that upload's inventory counts silently wrong until next full sync | nightly reconciliation job alerts on >1% drift | 2025-03-14 |
-->

## Verification log

<!-- One line per full run of §2's commands. Failures are triaged as real
violation (bug) or stale entry (update/delete via change control). -->

| Date | Run by | Result | Notes |
|---|---|---|---|
| YYYY-MM-DD | <name/agent> | <n>/<n> pass | <failures and their triage> |
