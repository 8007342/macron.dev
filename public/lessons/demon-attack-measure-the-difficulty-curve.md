---
title: "When five small knobs multiply, Wave 1 becomes a wall"
slug: demon-attack-measure-the-difficulty-curve
summary: "In Demon Attack (demonattack.tlatoani.net), five innocent-looking difficulty sliders multiplied together and turned the very first wave into a 112-hit marathon. A 30-second autopilot script found the math trap and cut campaign length in half."
slogan: "Measure all 318 waves before Wave 1 becomes a wall."
audience: [humans, agents]
level: beginner
tags: [demon-attack, gamedev, balance, simulation, ux, flutter]
rank: 86
art: demon-attack-wave-balance
sources: [2026-10-25-forge-harvest-arabiya-demon-attack-ranitas-and-tillandsias-v56-10-20-1.md, https://github.com/8007342/demon_attack]
updated: 2026-10-25
---

When you build a game with an AI assistant, it is tempting to ask for lots of richness: *"Add five difficulty modes! Add enemy reinforcements! Make late-stage routes tougher! Let big demons split into baby demons! Give elites armor and shields!"*

The AI will happily build every single one of those systems. And each system, on its own, will look completely reasonable in the code.

Then you press **Start** on Wave 1, and the first sixty seconds feel like fighting a brick wall. That is exactly what happened during the making of [**Demon Attack**](https://demonattack.tlatoani.net) ([`8007342/demon_attack`](https://github.com/8007342/demon_attack))—and the way it was fixed works for any game you build.

## The Trap: Five Reasonable Knobs That Multiply

On paper, Wave 1 of Demon Attack only started with **4 enemies** totaling **8 health points**. That sounds like a gentle 10-second warm-up.

Why did it actually take **73 hits on Normal** and **112 hits on Hard** to survive Wave 1?

Because five separate systems were quietly multiplying each other:
1. The **route settings** added 3 reinforcement waves (`+9` enemies).
2. Each reinforcement wave inherited **full escalated health** instead of sharing a wave budget.
3. Splitting demons spawned **child demons** when hit.
4. High-heat waves promoted ordinary demons into **shielded and armored elites** without a wave-wide cap.
5. **120 enemy bullets** rained down during that first wave, forcing the player to dodge instead of shoot.

`8 initial health` had quietly compounded into **9.1× to 14×** as much work before the player even reached Wave 2!

## The Fix: Have the Computer Play All 318 Waves Before You Do

Humans cannot manually playtest 53 waves across 6 difficulty modes every time a number changes. You get tired by Wave 4.

Instead, ask your AI to build two tiny command-line tools:
1. **A Wave Auditor** (`tools/analyze_difficulty.dart`): Prints a table showing the *true* total hits required for every wave once reinforcements, splits, shields, and armor are added up.
2. **A Robot Test Pilot** (`tools/profile_difficulty.dart`): A simulated player that flies through the entire campaign at super-speed using the real game rules and reports how many minutes each tour takes and how many times a human would lose a life.

Once the table made the hidden multiplier visible, fixing it was simple:
- Reinforcements and boss escorts now **share their parent wave's health pool** instead of multiplying it.
- Ordinary enemies are capped at **5 HP**, and elite promotions have a strict per-wave ceiling.
- Result: Wave 1 dropped from **73 hits → 17 hits** on Normal (and **112 → 21** on Hard), and the full Normal campaign went from an exhausting **110-minute slog** to a crisp **48-minute arcade adventure**.

## Watch Out for Whole-Number "Cliffs"

In retro arcade games, health and damage are usually whole numbers (`1, 2, 3...`). That creates hidden cliffs:
- If most enemies have **3 HP**, raising a weapon's damage from `1` to `2` cuts shots-to-kill from `3` to `2`.
- Raising that weapon's damage from `2` to `3` suddenly turns **every 3-HP enemy in the game into a one-shot kill**!
- Even trickier: if an elite enemy has **1 Shield + 1 Armor + 1 Hull**, and leftover damage does not spill over between layers, a gun that does `1` damage and a gun that does `99` damage **both take 3 shots** to defeat it.

## Teach One New Thing at a Time (in 7 Words)

Instead of making players read a manual before playing, Demon Attack pauses the incoming wave just offscreen for **4.5 seconds** the first time a new enemy or power-up appears, showing its pixel portrait and a 5–9 word tip (like *"Shatter shields before they recharge"*). You learn by playing, one surprise at a time.

## Tlatoāni & Mācron

**Tlatoāni** *(mashing the fire button with both gill-frills fluttering)*: "You told me Wave 1 had four little bats! Why have I been shooting for two minutes?!"

**Mācron** *(holding up a long printout from the Robot Test Pilot)*: "Good news: there were four bats. Bad news: they invited nine cousins, six split in half, and three put on titanium helmets. Let me cap the family reunion."
