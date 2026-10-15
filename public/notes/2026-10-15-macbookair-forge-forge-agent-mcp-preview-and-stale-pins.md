# Forge agent learns about MCP empty replies, preview routing, and stale pins

An OpenCode agent (Tillandsias forge, fresh curl install v56.10.14.1, soft reset kept Vault store) updated tillandsias.org by naming the release installed vs the newest. The work and the rough edges are recorded here for the next agent.

## What worked
- Read AGENTS.md/docs/matrix/README.md first; verified claims against GitHub API and the site's scripts instead of repeating them.
- `fetch-checkouts.sh` (14 s) satisfied the checked-build gate; baseline checked build ~1 s; edit + rebuild ~1 s.
- Commit succeeded (`fa8560a6d5e884859ac4445ef740d6a180f6d2d0`, subject: "Name the release the install commands hand you, and that it is not the newest"); `npx agent-commit check --count 1` → OK. Push once (`93fbdba..fa8560a main -> main`), relay verified.
- Pre-commit hook ran `checked-build.sh` and refused a stale `index.html` (caught the generated nature of the file).

## What was awkward / gaps hit
- **Empty MCP tool replies.** Tool replies (`publish_local`, `service_status`, `browser_open`, `browser_list_windows`) all returned empty. This wasted time retrying and hunting for another way to verify.
- **localhost routing inside a forge.** `*.localhost` does not resolve to the router from inside a forge, so you cannot just hit `localhost` URLs. The agent verified the preview by fetching the router's address on the forge network directly, sending the site's virtual host as the `Host` header (the router 404s on the old docs path, 200 on `/`). The served byte size matched the regenerated file and the new text was present.
- **Stale hand-maintained release text.** The note on the install page named versions as of build time (`v56.10.14.1` newest daily/prerelease, `v56.10.13.1` stable served by `/releases/latest`). This is a build-time snapshot that will go stale on the next stable promotion — same class as site pins. They scoped it with "when this page was last built", but it's not self-updating. Also GitHub marks `v56.10.14.1` as prerelease so calling it "the latest release" without qualification would mislead; the honest edit had to distinguish daily vs stable.

## Rough timings
- recon/verification ~6–8 min; checkouts 14 s; baseline checked build ~1 s; edit + rebuild ~1 s; preview publish + verify ~2–3 min (mostly empty-reply retries and router discovery); commit ~2 s; push ~3 s. Total forge session ~406 s end to end; install 171 s; soft reset 14 s; push went live ~12–13 min later.

## Where agent learnings live, and why
Agent-session learnings live in the **notebook**, one note **per session** (`public/notes/<date>-<host>-<slug>.md` plus one manifest line), and are distilled into **lessons by topic** (`public/lessons/`). Harness and host are *attributes* of a note (`host`, and an optional `harness` on its manifest line) rather than separate trees, so there stays one convergent append-only set — that is why we chose **per session, not per harness**: a session is the natural unit of an append-only note, and tag/host attributes still let a later agent find all notes from a harness. This reuses the existing notes → lessons → comics pipeline in AGENTS.md instead of a parallel structure.

Two things to remember from this session: treat MCP tool replies as possibly empty (retrying is not verification — check another channel), and prefer direct network verification (the router's address with the right `Host` header, since `*.localhost` may not resolve from inside a forge).
