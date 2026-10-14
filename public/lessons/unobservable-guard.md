---
title: "An unobservable guard is a missing guard"
slug: unobservable-guard
summary: If you cannot see whether a pre-push hook or CI gate is installed, assume it is not. Check, install it, and make its presence visible.
slogan: Trust the instrument you can read.
audience: [humans, agents]
level: beginner
tags: [git, hooks, ci, safety, tillandsias, forge]
rank: 60
art: measurements
sources: [2026-10-14-macbookair-forge-release-smoke-v56-10-14-1.md]
updated: 2026-10-14
---

> **Mācron:** I pushed. Nothing complained, so it passed!
>
> **Tlatoāni:** Or nothing was listening.

A gate that rejects bad pushes and a gate that does not exist look exactly the
same from the outside, until something bad gets through. Silence does not
mean approval.

## Do it yourself

```
ls "$(git rev-parse --git-path hooks)"      # what hooks this checkout has
git config --get core.hooksPath             # or where they really live
```

A Tillandsias forge states it at startup, in a machine-readable line:
`hooks: pre_push=absent pre_commit=absent`. When it says `absent`, every push
is unguarded, so run the project's checks yourself before pushing. On this
site that is `node scripts/check.mjs`.

## For agents

Read the startup context's hook line before you push, and say in your report
whether the push was guarded. "Pushed (no hooks installed, ran check
manually)" is an honest report. "Pushed, all green" is not, when nothing ran.
