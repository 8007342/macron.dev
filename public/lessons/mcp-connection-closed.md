---
title: "MCP server says CONNECTION_CLOSED? Run the wrapper by hand"
slug: mcp-connection-closed
summary: When an MCP server fails with CONNECTION_CLOSED, run its command yourself. The one line it prints usually names the real cause, often a socket that was never created.
slogan: The silence has a sentence in it.
audience: [humans, agents]
level: intermediate
tags: [mcp, tillandsias, forge, troubleshooting, sockets, host-browser]
rank: 85
art: understand-movement
sources: [2026-10-14-macbookair-forge-release-smoke-v56-10-14-1.md]
updated: 2026-10-14
---

> **Mācron:** The browser server is dead. Shall I reinstall everything?
>
> **Tlatoāni:** First, let it speak. Run it yourself and listen.

Claude Code reports `CONNECTION_CLOSED` whenever a stdio MCP server exits
before it finishes the handshake. That is a symptom, not a cause. Many MCP
servers in a Tillandsias forge are small shell wrappers that pipe stdio to a
Unix socket. If the socket is missing, the wrapper prints one JSON-RPC error
line and exits, and that line never reaches you.

## Do it yourself

1. List the servers and find the failing one's command:
   `claude mcp list`
2. Run that command by hand, with no input:
   `timeout 10 <command> </dev/null`
3. Read the single line it prints. In the host-browser case it was
   `TILLANDSIAS_CONTROL_SOCKET does not exist`.
4. Check the socket path that the environment names:
   `env | grep -i sock`, then `ls -la` on that directory.
5. An **empty, read-only** directory means the host never started the listener
   for your lane, or never mounted it into the forge. You cannot fix that from
   inside the forge. Report it to the host session or the operator, with the
   output from steps 1–4 (and no tokens).

## Known case: host-browser in macOS forges (v56.10.14.1)

The macOS guest build lacked the feature that starts the lane's MCP socket
listener, so the directory was mounted empty and `host-browser` (and with it
the browser and local-publish tools) was unavailable. Tracked as 1713-1dnx.

## For agents

Do not retry a dead MCP server in a loop, and do not conclude that the
capability "does not exist". Say that the server **failed to connect**, quote
the wrapper's one-line error, and move on with the tools you have.
