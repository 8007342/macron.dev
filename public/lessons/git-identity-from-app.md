---
title: "Who is the author? Check git identity before the first commit"
slug: git-identity-from-app
summary: In a Tillandsias forge, git's author and committer come from the GitHub App identity with no prompt. Three commands confirm it before you commit.
slogan: Know whose name you sign.
audience: [humans, agents]
level: beginner
tags: [git, identity, github-app, tillandsias, forge, release-smoke]
rank: 45
art: tillandsias-github-app
sources: [2026-10-14-macbookair-forge-release-smoke-v56-10-14-1.md]
updated: 2026-10-14
---

> **Mācron:** Who wrote this commit?
>
> **Tlatoāni:** Ask git. It will tell you before anyone else asks.

## Do it yourself

```
git var GIT_AUTHOR_IDENT
git var GIT_COMMITTER_IDENT
git config --show-origin --get-regexp '^user\.'
```

`--show-origin` shows *which file* set the identity, which is how you tell a
forge-provided identity from one left behind in a repository.

To test without touching your project, commit in a throwaway repository:

```
d=$(mktemp -d) && cd "$d" && git init -q \
  && git commit -q --allow-empty -m smoke \
  && git log -1 --format='author=%an <%ae> committer=%cn <%ce>'
```

## Expected in v56.10.14.1

There is no name or email prompt at startup. Author and committer both use
the App's noreply address, set in the forge's user-level git config.
