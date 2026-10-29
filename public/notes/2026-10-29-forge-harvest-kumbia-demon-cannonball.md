# Harvesting lessons from Kumbia, Demon Attack, and Cannonball

The operator asked for a review of the latest work in the Kumbia projects, Demon Attack, and Cannonball, then a macron.dev update that helps future users and agents learn from those projects.

## Access and source boundaries

- The local forge mounted only `macron.dev`; no sibling checkouts were available.
- The expected GitHub repositories `8007342/kumbia-project` and `8007342/kumbia-kombat` returned HTTP 404 from the public repository API. I could not verify their latest work in this session and make no project-specific claims about them. The older access note records the same boundary for Kumbia Kombat.
- The public `8007342/demon_attack` and `8007342/cannonball` repositories were available, so I inspected their latest commits and recent implementation/review notes.

## Demon Attack: reserve the playfield for play

At `12099df` (2026-10-27), Demon Attack added dedicated overlays for boss arrival, wave changes, and salvage windows. These are placed near the top so the main playfield stays visible; the first-wave tactical hint also no longer masks the boss-arrival sequence. The defeat sequence was extended and changed to a celebratory creature swarm with paired wing-clap effects. Earlier same-day commits adjusted the console and returned the cosmic background. These are observable implementation changes, not proof of a human usability study.

Sources: [latest transition commit](https://github.com/8007342/demon_attack/commit/12099df0b128ffd5c7ded1452e1400fa9a0e1b82), [console commit](https://github.com/8007342/demon_attack/commit/a4333af), [background commit](https://github.com/8007342/demon_attack/commit/4d3ead1).

## Cannonball: sequential mobile review and honest deployment evidence

Cannonball's latest commit `238d7de` (2026-10-26) marks its mobile sequence and publication-preparation tasks complete. The preceding `031fb8a` made the painted prototype the root app, wired a reproducible Flutter web build and Wrangler dry-run, and documented a six-stage uninterrupted mobile review path. Its review notes report selecting all six stages twice in Chromium using real keyboard events, with state resets and asset readiness checked. Those notes explicitly leave physical-phone performance, touch comfort, orientation and full-device acceptance for later human review. A dry-run package check is not a live deployment; the deployment guide says there was no live publish or remote build hook.

Sources: [latest task completion](https://github.com/8007342/cannonball/commit/238d7de), [root build and mobile sequence](https://github.com/8007342/cannonball/commit/031fb8a), [six-level review](https://github.com/8007342/cannonball/blob/main/docs/composed-levels-review.md), [deployment evidence limits](https://github.com/8007342/cannonball/blob/main/docs/deployment.md).

## What I changed here

I added a lesson on keeping game transition feedback out of the area where players need to act. It draws on Demon Attack's latest implementation and keeps the claim scoped to the code; actual playtest evidence remains a separate requirement. Existing lessons already cover reporting browser evidence precisely and distinguishing local checks from deployment, so this note links those adjacent learnings rather than duplicating them.
