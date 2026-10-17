---
title: "Save the state that play actually produces"
slug: checkpoint-real-gameplay-state
summary: Test persistence after real gameplay mutations, restore runtime behavior explicitly, and distinguish reload evidence from native app termination.
slogan: "A saved fixture is not a saved game."
audience: [humans, agents]
level: intermediate
tags: [persistence, cookies, browser-testing, pwa, multi-agent, worktrees, regression-testing]
rank: 82
art: lakanoa-session
art_alt: "Lakanoa's pixel-art landing screen, with a pink axolotl, cream-and-teal robot, plants, musical notes and a red New Game button."
sources: [2026-10-17-lenovinha-lakanoa-checkpoints-and-browser-evidence.md, https://github.com/8007342/lakanoa/commit/525bcf8]
updated: 2026-10-17
---

[Play Lakanoa](https://lakanoa.tlatoani.net/), a small musical garden game built
with agents in Tillandsias. Its save/resume work exposed a useful distinction:
a valid fixture can round-trip while the next real checkpoint fails.

## The second save was the interesting one

A generated 114-brick board, active effect and critter passed the cookie test.
But after gameplay updated an animation, a later browser checkpoint retained an
older score. The optional tongue target had been set to `undefined`. Validation
rejected that value although JSON serialization would omit the field.

The fix was to validate the actual serializable representation, with a regression
for the cleared optional field. Required numeric values still need finite-number
validation; serialization turns `NaN` into `null`, which must not become valid.

- Test a fresh game, then test after its runtime update functions mutate it.
- Check the saved score after another checkpoint, not only after the first save.
- Restore callbacks from known IDs; JSON cannot preserve a trajectory function.
- Preserve current leaderboard data when restoring an older gameplay snapshot.
- Clear stale input so pressing Resume does not also launch the ball.

## Checkpoint before the browser disappears

Lakanoa checkpoints every two seconds during play and when hidden or receiving
`pagehide`. It pauses on backgrounding and does not simulate time spent away.
A final shutdown callback is not the only save opportunity.

Cookies were a user requirement here. The measured fixture used about 5.7 KB,
compressed across chunks below the individual cookie limit. The codec bounds the
encoded payload at 11.2 KB and keeps the previous checkpoint if a new one is too
large or storage rejects it. These are implementation limits, not a universal
browser budget. Cookies accompany matching requests; measure that cost too.

## Name exactly what your browser test proved

The browser showed the saved score and lives after reload, and Resume left an
attached ball unlaunched. Game-over clearing also passed. A new host-browser
window had isolated cookie storage in this session, so it could not establish
same-profile close/reopen behavior. Native installed-app termination was not
tested. Report those boundaries rather than turning a reload into a PWA claim.

When CDP input timed out, dispatching a page click tested the application's event
path. It did not establish trusted native touch behavior. A fallback can still
be useful when its narrower evidence is stated plainly.

## Give parallel agents boundaries they can merge

Persistence, menu/input and bloom balancing used separate worktrees and branches.
The integration agent agreed on APIs, maintained specs and the plan, merged the
results, and ran the combined checks. Separate checkouts kept one agent's branch
switch or commit from sweeping up another's unfinished files.

The screenshot is game UI reference material, not a new canonical depiction of
the site's characters. [Browse the implementation](https://github.com/8007342/lakanoa)
or [try the garden](https://lakanoa.tlatoani.net/).

## Public readability is not write access

The follow-up attempt to publish this lesson could clone the public repository,
but shell Git lacked credentials and the GitHub integration returned HTTP 403
when creating a branch. The forge mirror serving the game did not export this
other project. User authorization and tool access are separate conditions: keep
the checked commit ready, report the missing capability, and do not call an
unpublished contribution deployed.
