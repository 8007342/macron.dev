---
title: "When MCP tools return empty replies, verify another way"
slug: forge-mcp-empty-replies-and-preview-routing
summary: MCP tools can return empty results in forges; don't loop-retry blindly. For local preview, *.localhost may not resolve inside the forge — reach the router's address with the right Host header. Treat verification as something you can do by hand.
slogan: "Empty replies mean 'try a different channel'."
audience: [humans, agents]
level: intermediate
tags: [mcp, forge, preview, routing, verification, troubleshooting, host-browser]
rank: 75
art: understand-movement
sources: [2026-10-15-macbookair-forge-forge-agent-mcp-preview-and-stale-pins.md, 2026-10-14-macbookair-forge-release-smoke-v56-10-14-1.md]
updated: 2026-10-15
---

> **Tlatoāni:** The tool said nothing. Again.
>
> **Mācron:** So we ask the network directly. Less chatty that way.

## When MCP returns empty

Sometimes in a Tillandsias forge, MCP tool calls return empty responses (no data, no error string you can use). Common cases seen: `publish_local`, `service_status`, `browser_open`, `browser_list_windows`.

Don't just retry in a tight loop. Instead:
- **Run the underlying action's alternative check.** If you published/checked a local preview, fetch it over HTTP and inspect bytes/headers.
- **Check the actual socket/wrapper** if the server claims CONNECTION_CLOSED (see [MCP server says CONNECTION_CLOSED? Run the wrapper by hand](./mcp-connection-closed.html)).
- **Move on with what you have.** Empty replies are a symptom of the lane/socket environment, not necessarily that your change is wrong.

## Preview routing inside a forge

Inside a forge, `*.localhost` names don't resolve to the router the way they do on the host. To verify a published local preview:
1. Find the address the router answers on from inside the forge (an internal address you do **not** publish; ask your lane/host session for it).
2. Fetch with the correct Host header: `curl -i -H 'Host: www.<project>.localhost' http://<router-address>:<port>/` (the port/route the project uses).
3. Look for 200s and compare byte sizes/signature of content. The router may 404 on old paths but serve `/` correctly.
4. Don't assume `localhost` works from inside the container/forge; try the router's address with the right Host header.

## Verification discipline

- **Prefer direct verification.** When tool replies are empty or unhelpful, do the end-to-end check yourself (curl/wget, compare sizes, grep for expected text).
- **Distinguish daily vs stable releases.** If you state "latest release", check GitHub's prerelease flag — `releases/latest` points to the latest stable (non-prerelease). Daily builds may be newer but marked prerelease.
- **Don't repeat stale pins.** Any hand-maintained version/date text should be qualified as "as of when this page was last built" or sourced from automation; otherwise it will go stale on the next promotion.

## Takeaway

Empty MCP replies aren't proof of failure. The forge's network/view of routing differs from the host. Verify by reaching the router's address with the right Host header, and keep claims about "latest" true by checking release metadata.
