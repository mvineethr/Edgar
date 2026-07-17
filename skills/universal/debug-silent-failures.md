# Skill: Debugging silent failures — generate an error where there is none

## When to use
Whenever something "doesn't work" with NO error message. Silent failures
cost more than loud ones because you debug the wrong layer first.

## Procedure
1. Do not touch code yet. List the layer boundaries between intent and
   symptom (e.g., source → build → CDN → browser global → render;
   or client → API route → upstream service → parser → UI).
2. At each boundary, starting closest to the EXTERNAL side, extract a
   concrete artifact:
   - URLs/scripts: `curl -I` the exact URL — status and content-length.
   - API routes: curl the route and read the RAW body (is it even JSON?).
   - Parsers: diff the test fixture against a freshly fetched response.
   - Globals/imports: check the symbol actually exists at runtime
     (`typeof lib !== "undefined"`), not just that the page loaded.
3. The first boundary whose artifact contradicts your assumption is where
   you debug. The symptom is usually two layers downstream of the cause.
4. After fixing, leave a tripwire: a regression test, a louder error, or a
   note in the project's gotcha list. The fix alone will be forgotten.
5. Maintain a per-project catalog of silent failures you've paid for, each
   entry = the tell + the mechanical check. It compounds.

## Known cross-project patterns (seed your catalog with these)
- **Third-party script URL wrong** → nothing renders, no console error.
  Wrong-but-plausible CDN paths 404 invisibly; the library's global loads
  as `undefined`. Check: curl the exact URL before writing integration
  code.
- **"Unexpected token '<'" in a web app** → a widget got an HTML error
  page where it expected JSON. An exception escaped the server's JSON
  error mapping. Debug the server, not the JavaScript.
- **Green tests + empty live output** → the fixture shares the code's bug.
  Diff fixture vs. fresh live response before touching the parser.
- **Connection resets on long-lived sessions** → servers recycle stale
  keep-alive sockets. Retry ConnectionError like a 5xx; if you see it raw,
  some path is bypassing your central HTTP helper.
- **Local tooling amnesia** (image/cache evicted, "not found" for a thing
  you just built) → rebuild before investigating auth or registries.
- **Plausibly-wrong numbers** → no error possible; only an external
  cross-check detects it (see sanity-check-numbers.md).

## Rules
- When there's no error, your job is to MANUFACTURE one: probe boundaries
  until some layer yields an artifact that contradicts an assumption.
- Never add retries/sleeps around a failure you haven't named. Retry is
  for transient faults you've identified, not for hope.
- Debug where data changes hands, not where the symptom appears.

## Case study
A charting library was integrated via CDN; the pane rendered empty, the
global was `undefined`, and the console was clean — the CDN returned a
silent 404 because the UMD build lived at `dist/umd/lib.min.js`, not
`dist/lib.min.js`. A boundary walk (curl the script URL: step 2) finds
this in 30 seconds; debugging the rendering code — where the symptom was —
burned real time. The permanent fix removed the boundary entirely:
vendoring the file into the app's own static directory. The incident then
went into the project's gotcha list, which is why it costs nothing now.

## Anti-patterns
- Debugging the layer where the symptom appeared.
- Interpreting infrastructure weirdness as auth problems.
- Fixing the bug but not recording the pattern.
