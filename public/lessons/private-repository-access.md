---
title: "Your private repository needs a session that can read it"
slug: private-repository-access
summary: Check access through the active connection before reviewing another project; ownership and previous sessions do not establish this session's repository access.
slogan: "The invitation needs a working key."
audience: [humans, agents]
level: beginner
tags: [github, private-repositories, authentication, github-app, tillandsias, troubleshooting, verification]
rank: 78
art: tillandsias-github-app
sources: [2026-10-18-forge-private-repository-review-boundary.md, https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api]
updated: 2026-10-18
---

You own a private project. Other Codex sessions have worked on it. You ask a
new session in another Tillandsias project to review its latest merges, and
GitHub says **404 Not Found**.

That happened during a request to turn kumbia-kombat sessions into macron.dev
lessons. The owner confirmed the repository was private. This session never
obtained the commits, so the result is an access lesson rather than a review
of the game's implementation.

## A 404 can mean the reader lacks access

GitHub deliberately returns 404 for private resources when the request is not
properly authenticated, to avoid disclosing their existence. Check the URL and
the active connection before concluding that a repository was deleted.
See [GitHub's explanation](https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api).

In this session, the shell CLI lacked authentication, the connected GitHub app
could not read the commit collection, and the forge mirror did not export the
project. Those observations did not identify the exact missing permission.

## Unblock the review

1. Confirm the repository owner and name with the operator.
2. Check that the GitHub connection being used includes this repository and
   has permission to read the history needed for the task. An owner may need
   to adjust the app installation's repository selection or reconnect access.
3. If using shell Git or the CLI, check that tool's authentication separately.
   A connected app does not establish that the shell has credentials.
4. If using a forge mirror, verify that it exports the target project. A
   working mirror for the current checkout does not establish cross-project access.
5. Retry a small read, such as the recent commit list, through the intended
   route before beginning the review. Then retrieve the relevant merges and diffs.

Keep the repository private. If connection access cannot be arranged, an
owner-provided export of relevant commit messages, diffs and discussions can
support a narrower review. Remove secrets and identify anything omitted. Do
not paste credentials into a conversation or public note.

## Say what was actually reviewed

An access failure can teach a useful lesson without revealing private source.
Record the failed route, the observed response and the next step. Do not invent
findings about commits you could not read. Previous sessions' access and the
operator's permission to work are different from the current tool's ability
to retrieve evidence.

The earlier [Lakanoa publication experience](checkpoint-real-gameplay-state.html)
showed the complementary boundary: reading a public repository did not grant
permission to push to it. Test the capability the task actually needs.
