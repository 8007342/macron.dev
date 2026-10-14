---
title: "Measure the deploy, then batch your pushes"
slug: measure-deploy-time
summary: A Cloudflare Workers Builds deploy of this site takes minutes per push to main, so measure push-to-build time from the GitHub check run and batch work on a branch instead of pushing many small commits.
slogan: Count the steps before you take them.
audience: [humans, agents]
level: intermediate
tags: [cloudflare, workers-builds, deploy, ci, git, branches, measurement]
rank: 65
art: restaurant-at-the-end-of-the-universe
sources: [2026-10-14-macbookair-forge-release-smoke-v56-10-14-1.md, /deploys/log.jsonl]
updated: 2026-10-14
---

> **Mācron:** Seven fixes, seven pushes! Very productive.
>
> **Tlatoāni:** Seven deploys. We will eat at the end of the universe.

macron.dev deploys through **Cloudflare Workers Builds**. Every push to
`main` builds and publishes the site. The operator observes about 16–20
minutes from push to live. Pushes to other branches build too (as
non-production builds).

## Measure it (from inside a forge)

A forge's egress proxy cannot fetch macron.dev, but Workers Builds posts a
**check run** on every GitHub commit it builds, and `api.github.com` answers
without a token:

```
scripts/deploy-time.sh <sha> <pushed-at UTC> [branch]
```

It polls the check run and prints one JSON line. Append that line to
[`/deploys/log.jsonl`](/deploys/log.jsonl), which is append-only and
`merge=union` like the notebook. It measures **push → build finished**.
Edge propagation adds a little more time, which a forge cannot observe.

## What we measured so far

| Commit | Branch | Push → build done | Result |
|---|---|---|---|
| 03a46e1 | main | 12m37s | success |
| cfb4bbc | fleet-knowledge-base | 9m39s | failure |

**Branch builds fail.** Both branch builds seen so far (d091abe and cfb4bbc)
ended in `failure`, and both deployed fine once merged into `main`. The check
run carries no reason, and only the Cloudflare dashboard shows the log. Until
someone with dashboard access fixes the non-production build, a branch build
tells you *how long a build takes*, not *whether your change is good*. Run
`node scripts/check.mjs` and serve `public/` locally to check it.

## Batch it

1. Work on a branch: `git switch -c <topic>`.
2. Push the branch once to check that it builds.
3. Merge into `main` **once**, with all the work together.
4. Measure the main deploy and append it to the log.

## For agents

Do not push to `main` to "see if it works". Run `node scripts/check.mjs`
locally, push a branch, and read its check run.
