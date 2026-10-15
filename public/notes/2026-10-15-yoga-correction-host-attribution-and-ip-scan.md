# Correction: the 2026-10-15 forge note ran on yoga, not a MacBook; and check.mjs does not catch private IPs

This note corrects
[2026-10-15-macbookair-forge-forge-agent-mcp-preview-and-stale-pins](./2026-10-15-macbookair-forge-forge-agent-mcp-preview-and-stale-pins.md),
which stays as written because notes are append-only.

## The host was wrong

That session ran on **yoga**, a Linux (Fedora Silverblue) host, in an
OpenCode forge whose container hostname was `forge-macron-dev`. Its note and
manifest line say `macbookair-forge`.

Nothing in Tillandsias told it so. The forge sets `TILLANDSIAS_MSG_HOST` to
the real host, and the agent never read it or ran `hostname`. It copied the
host from the previous note in this folder
(`2026-10-14-macbookair-forge-release-smoke-v56-10-14-1.md`), whose name
pattern it reused for its own file.

**For the next agent:** take your host from your own environment
(`TILLANDSIAS_MSG_HOST` in a Tillandsias forge, else `hostname`), never
from a neighbouring note. A wrong host poisons every comparison between
machines, because a reader trusts that field to say where something was
measured.

## check.mjs does not scan for private IP addresses

The same agent first published the forge's internal router address in its
note and lesson, then caught it against AGENTS.md's rule never to publish
internal addresses and replaced it with a generic placeholder.
`node scripts/check.mjs` passed both versions: it does not look for private or
internal IP addresses (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8).
Until it does, that rule depends on each agent remembering it. A check that
refuses those ranges in `public/` (outside fenced examples that are clearly
placeholders) would make it a guard instead of a memory.
