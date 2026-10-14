---
title: "Connection reset during CONNECT means the egress allowlist"
slug: proxy-connection-reset
summary: In a forge, curl failing with "Connection reset by peer" right after "CONNECT host:443" means the egress proxy refused that host. It is not DNS, TLS, or the site being down.
slogan: The door is fine. The guest list is short.
audience: [humans, agents]
level: beginner
tags: [proxy, networking, forge, tillandsias, curl, cloudflare, troubleshooting]
rank: 70
art: the-crab-is-right
sources: [2026-10-14-macbookair-forge-release-smoke-v56-10-14-1.md]
updated: 2026-10-14
---

> **Mācron:** macron.dev is down!
>
> **Tlatoāni:** For you. Ask GitHub whether it is down for everyone.

Forges send outbound HTTPS through a caching proxy (`HTTPS_PROXY` is set for
you). The proxy only tunnels to hosts on its allowlist. For any other host it
resets the connection during the `CONNECT`, before any TLS starts.

## Recognise it

```
curl -sv https://example.com/ 2>&1 | grep -E 'CONNECT|reset'
> CONNECT example.com:443 HTTP/1.1
* Recv failure: Connection reset by peer
```

If `https://github.com/` returns 200 on the same shell and the other host
resets, the cause is the allowlist.

## What to do

- Do not "fix" it by unsetting the proxy. The forge has no other route out.
- Look for a reachable source of the same truth. For example, to confirm a
  Cloudflare deploy of this site, read the **Workers Builds** check run on the
  commit through the GitHub API instead of fetching the site (see
  [measuring deploys](/lessons/measure-deploy-time.html)).
- If the host really is needed, ask the operator to allow it. Say which host
  and why.

The crab goes sideways and still gets there. When the front door is closed,
find the side path that leads to the same truth.

## For agents

Report "blocked by the forge egress allowlist", not "site down". The two
lead to very different actions.
