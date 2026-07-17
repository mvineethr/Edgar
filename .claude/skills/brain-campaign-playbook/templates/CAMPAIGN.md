# Campaign: <short title>

<!-- Copy to .claude/campaigns/<YYYY-MM-DD>-<slug>.md and fill EVERY section
     before running any investigation command. Quality bars inline below;
     full definitions in brain-campaign-playbook. -->

- Opened: <YYYY-MM-DD>
- Status: ACTIVE | PROMOTED | ABORTED
- Budget: <N sessions / N hours / N runs — concrete numbers, set now>

## MISSION

<!-- One sentence: what is true at the end that is not true now. -->

**Success criterion (numeric, declared before any investigation):**

<!-- A fresh session must be able to run ONE command and answer yes/no.
     "Judged by eye" / "noticeably better" are banned. Encode repetition or
     sample size (e.g. "200 consecutive green runs", "p95 < 120 ms over 500
     requests") — a single lucky run can never satisfy it.
     If you can't measure it yet, Phase 0 is building the measurement
     (brain-diagnostics-and-tooling). -->

## PHASES

<!-- Each phase: exact commands + predicted observation + branches for every
     plausible outcome. A gate where no hypothesis can die and no branch can
     be taken is narration — delete it. Order by information per unit cost:
     measure → isolate → discriminate hypotheses → fix.
     If a result matches NO branch: STOP, log the surprise, revise this
     document, then continue. Never improvise past a gate. -->

### Phase 0 — <name, usually: baseline measurement>

**Commands:**

```sh
<exact command(s)>
```

**Expected at gate:** <predicted number / exact output, written BEFORE running>

**Branches:**
- If <expected> → phase 1.
- If <outcome X> → <go to phase Y / abandon hypothesis Z / revise premise>.
- If <outcome W> → <…>.

### Phase 1 — <name>

**Commands:**

**Expected at gate:**

**Branches:**

<!-- Add phases as needed. For a hypothesis fan-out phase, use a table:
     | H | Mechanism | Discriminating experiment | Prediction if TRUE | Prediction if FALSE |
     One variable per experiment; predictions written before running
     (brain-research-methodology). Do not leave a fan-out phase with two
     live hypotheses — add a discriminating experiment instead. -->

## SOLUTION MENU

<!-- Ranked candidate approaches. NOTHING here may be attempted while any of
     its obligations is undischarged — obligations are what must be derived,
     measured, or proven first (e.g. "root cause confirmed at phase N gate",
     "cost measured < X", "differential test written"). This table is the
     defense against grabbing the first idea. -->

| # | Approach | Obligations before attempting |
|---|---|---|
| 1 | | |
| 2 | | |

## FENCED WRONG PATHS

<!-- Approaches known to fail, each with EVIDENCE (measurement, dated past
     attempt, mechanism argument) — not vibes. Mine history first
     (brain-failure-archaeology). Reopening a fence requires logging new
     evidence in the CAMPAIGN LOG *before* acting on it. -->

| Fenced path | Evidence |
|---|---|
| | |

## VALIDATION AND PROMOTION

<!-- How the finding becomes an adopted change:
     1. Mission criterion met with executed proof (brain-validation-and-qa
        proof-of-work format) — never a single lucky run.
     2. Minimal diff through brain-change-control gates — a campaign grants
        zero exemptions.
     3. Root-cause/mechanism sentence + promoting commit/PR linked below;
        durable lesson recorded per the LEARNINGS convention.
     4. All temporary instrumentation (DIAG: markers) removed. -->

- Promotion command(s) and expected result:
- Regression test (fails on old code, passes on fix):
- Promoting commit/PR:

## ABORT CRITERIA

<!-- Checked at EVERY gate. An honest abort with dead hypotheses is a
     successful outcome; overclaiming partial progress is the failure mode. -->

- Budget exhausted: <restate the budget from the header>
- Criterion unreachable if: <evidence that would prove the target can't be met>
- Premise falsified if: <observation that would mean the problem isn't what
  MISSION assumes>

On abort, write the abort report (brain-docs-and-writing): established facts
with evidence, ruled-out paths (they become fences for the next campaign),
exact resume state, recommendation.

## CAMPAIGN LOG

<!-- Append-only; one entry per session. Observed NUMBERS, not summaries —
     "6 failures / 100 runs", never "looked flaky". Update resume state every
     session; hygiene rules per brain-task-planning §5.
     Resuming cold: read this whole file, re-run the last gate's command to
     confirm recorded state still holds, then execute NEXT verbatim. -->

### <YYYY-MM-DD> session 1

- Phase: <n>
- Ran: <command> → observed: <number / output>
- Gate outcome / branch taken:
- Hypotheses killed / fenced paths added:

**Resume state**
- Current phase: <n>
- NEXT (verbatim command or action):
- Open questions:
