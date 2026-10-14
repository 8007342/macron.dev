---
title: "Missing a tool in the forge? Install it into user space"
slug: tools-on-demand
summary: Forges ship lean. Install missing language packages into user space (pip --user, npm global under the project cache), and expect shims such as magick to bootstrap Homebrew on first use.
slogan: Carry less. Fetch what the task asks for.
audience: [humans, agents]
level: beginner
tags: [forge, tillandsias, python, pillow, homebrew, imagemagick, tooling]
rank: 40
art: less-syntax-more-intent
sources: [2026-10-14-macbookair-forge-release-smoke-v56-10-14-1.md]
updated: 2026-10-14
---

> **Mācron:** There is no Pillow. I will write a PNG decoder.
>
> **Tlatoāni:** Or you could ask the shelf.

Like a Tillandsia, a forge carries very little and gets what it needs from
the air. Packages come in through the caching proxy, so installing them is
quick and safe.

## Do it yourself

- Python: `pip install --user Pillow` (worked in v56.10.14.1).
- CLI tools: some commands, such as `magick`, are **shims**. On the first call
  they bootstrap a userspace Homebrew, which takes a while. Later calls are
  fast.
- Prefer zero-dependency scripts for anything the project must run every
  time. This site's `scripts/build.mjs` uses only Node's standard library.

## For agents

Install the tool rather than reimplementing it, and write down in the
project's README what you installed, so the next agent knows it is needed.
