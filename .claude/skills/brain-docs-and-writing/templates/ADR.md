<!-- ADR-lite (Architecture Decision Record) writing format.
     This template owns HOW an ADR is written; brain-architecture-contract
     owns WHEN an ADR is required and how ADRs are numbered, stored, and
     superseded — consult it before creating one.
     One decision per file. Past decisions are immutable: a change of mind is
     a NEW ADR that supersedes this one, not an edit. -->

# ADR-<NNNN>: <decision as a short imperative or noun phrase>

- **Date**: <YYYY-MM-DD>
- **Status**: proposed | accepted | superseded by ADR-<NNNN>

## Context

<!-- The forces at play when the decision was made: the problem, the
     constraints (technical, time, team), and what was true of the system at
     the time. Written so a reader two years later understands the situation
     without asking anyone. Facts, not advocacy. -->

## Decision

<!-- One or two sentences, active voice, present tense: "We use X for Y."
     The decision itself — not the reasoning (next section). -->

## Why

<!-- The reasoning: alternatives considered and why each lost. Numbers over
     adjectives ("adds ~40ms p99" not "slower"). Label any unvalidated
     assumption as an assumption. -->

| Option | Why not chosen |
|---|---|
| <alternative A> | |
| <alternative B> | |

## Consequences

<!-- What becomes easier, what becomes harder, and what new obligations
     exist — including the negative consequences of the CHOSEN option; every
     real decision has some. These often become invariants in the
     architecture contract (brain-architecture-contract). -->

- Positive:
- Negative:
- New obligations:
