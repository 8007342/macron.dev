---
title: "Keep the playfield open during transitions"
slug: keep-the-playfield-open
summary: Put temporary game instructions where they preserve the space players need to see and act, then verify the placement during real transitions.
slogan: Leave room for the next move.
audience: [humans, agents]
level: beginner
tags: [gameplay, game-ui, transitions, mobile, usability, demon-attack]
rank: 68
art: play-the-meta
sources: [2026-10-29-forge-harvest-kumbia-demon-cannonball.md, https://github.com/8007342/demon_attack/commit/12099df0b128ffd5c7ded1452e1400fa9a0e1b82]
updated: 2026-10-29
---

A game often needs to tell the player that a boss is arriving, a wave is
changing, or a brief recovery window has opened. Showing that message is only
half the job: the player may still need to steer, dodge, aim, or collect
something while reading it.

Demon Attack's latest transition work gives boss arrival, wave-change, and
salvage moments their own overlays near the top of the screen. The main action
area stays visible. Its first-wave hint also yields to the boss arrival instead
of showing both messages over the same moment. These are code and layout choices;
the commit does not establish that players found them readable.

## Design around the action

- Show only the message relevant to the current game phase. Avoid stacking two
  instructions when one transition takes priority.
- Place brief status text near an edge where it does not cover the main action
  or touch controls. Check the actual layout: a top banner can still collide
  with a HUD or a small screen.
- Keep the message short, readable at the smallest supported viewport, and
  temporary when play continues beneath it.
- During implementation review, trigger each transition and confirm the text,
  playfield, and controls remain visible together. Test keyboard and touch paths
  separately when the game supports both.
- Treat automated layout checks and desktop browser inspection as evidence for
  those checks only. Ask people to review clarity and physical-device play before
  calling the design proven.

A useful transition tells the player what changed without stealing the space
needed for the next move.
