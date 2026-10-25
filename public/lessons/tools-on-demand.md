---
title: "Missing a tool in the forge? Install it into user space"
slug: tools-on-demand
summary: Forges ship lean. Install missing language packages into user space (pip --user, npm global under the project cache), and expect shims such as magick to bootstrap Homebrew on first use.
slogan: Carry less. Fetch what the task asks for.
audience: [humans, agents]
level: beginner
tags: [forge, tillandsias, python, pillow, homebrew, imagemagick, tooling]
rank: 58
art: less-syntax-more-intent
sources: [2026-10-14-macbookair-forge-release-smoke-v56-10-14-1.md, 2026-10-25-forge-harvest-arabiya-demon-attack-ranitas-and-tillandsias-v56-10-20-1.md, https://github.com/8007342/atrapa, https://github.com/8007342/ranitas]
updated: 2026-10-25
---

> **Mācron:** There is no Pillow. I will write a PNG decoder.
>
> **Tlatoāni:** Or you could ask the shelf.

Like a Tillandsia, a forge carries very little and gets what it needs from
the air. Packages come in through the caching proxy, so installing them is
quick and safe.

## Do it yourself

- Python: `pip install --user Pillow` (worked in v56.10.14.1 and v56.10.20.1).
- CLI tools: some commands, such as `magick` or `flutter`, are **shims** or
  managed toolchains (`toolchain_prepare`). On the first call they download and
  extract their runtime—for example, `flutter --version` pauses for a few
  minutes at step `11/14` while extracting the SDK (~850 MB). Do not kill the
  command; later calls are instant.
- Flutter web builds: pass `--no-web-resources-cdn` (or bundle local fonts) so
  the app runs cleanly offline and inside strict CSP headers.
- Large temporary files: the project checkout (~1.5 GiB) and `/tmp` (~256 MiB)
  live on fast memory-backed `tmpfs`. Put multi-hundred-megabyte training logs,
  audio batches, or caches in `~/.cache/tillandsias-project`, which is backed
  by persistent disk.
- Prefer zero-dependency scripts for anything the project must run every
  time. This site's `scripts/build.mjs` uses only Node's standard library.

## For agents

Install the tool rather than reimplementing it, and write down in the
project's README what you installed, so the next agent knows it is needed.
