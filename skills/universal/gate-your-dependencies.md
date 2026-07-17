# Skill: Gate every new dependency against the project's identity constraints

## When to use
Evaluating any new data source, library, widget, embed, or service. Run
the gate BEFORE evaluating technical merit — a component that fails the
gate is rejected no matter how good it is.

## Procedure
1. Write down the project's identity constraints once (in the standing
   brief). Examples: "no required API keys," "open-source licenses only,"
   "must run offline," "no data leaves the user's machine," "no GPL in
   the core." These come from the project's promise to its users.
2. For each candidate component, check in order:
   - **Access model**: does it work under the project's constraint
     (keyless / free tier / self-hosted)? If it needs a credential the
     project forbids as required, it may only ever be an OPTIONAL
     enricher — everything must work without it.
   - **License**: compatible with the project's license policy?
   - **Functional fine print**: does the free tier cap something
     (volume, features, branding) that pushes YOUR users toward a
     subscription? A free-to-use component with paid limits inside your
     UX is a paywalled component. Reject it.
   - **Runtime independence**: does it phone home or load from a CDN at
     runtime? For load-bearing assets, vendor the file into the repo
     (with its LICENSE beside it) so a third party can't break you.
3. If a candidate fails, record WHAT it was and WHY in the project log so
   nobody re-evaluates it from scratch — or re-adopts it.
4. If a candidate passes conditionally ("optional key only"), implement
   the gate in code: the feature appears only when configured, and its
   absence leaves zero broken UI.

## Rules
- The identity constraint is absolute; there is no "we'll make the paid
  thing optional" path for a component whose CORE value requires payment.
  Don't even wrap it.
- License and business model are SEPARATE checks. Plenty of components
  pass the license sniff test and fail the paywall test in production.
- Unofficial-but-free sources are acceptable only in a degrade-never-
  break tier (see tiered-reliability.md), never as the authoritative
  path.
- "Temporarily" loading a vendorable asset from a CDN is how permanent
  fragility ships.

## Case study
An open-source terminal needed serious charting. A famous vendor's free
embed was integrated first — huge feature set, free to embed, worked in
one session. Then a user hit the functional fine print: the free widget
allowed 2 stacked indicators; more required a subscription. A paywall
inside an open-source tool violates its identity, so the embed was
removed entirely — not feature-flagged, removed — and replaced with an
Apache-2.0 library rendering the project's own data, vendored into the
repo after its CDN path burned a debugging session. Meanwhile a genuinely
useful keyed service (a free government data key) went in behind an
optional env var, with every screen complete without it. Same gate, two
different correct outcomes.

## Anti-patterns
- "It's free for our use case" — if any adjacent capability is paid,
  users WILL hit the wall.
- Adding a paid API as the default path with a free fallback (invert it:
  free is the path; keys enrich).
- Evaluating on features first and constraints second.
