---
title: "Not every app needs a scoreboard: building software that knows when to sleep"
slug: ranitas-calm-software-that-lets-you-rest
summary: "How Ranitas (ranitas.tlatoani.net) and Atrapa (atrapa.tlatoani.net) use tiny built-in brains, polite browser audio, and a 3-to-6-minute bedtime arc to build games that respect your attention."
slogan: "Both frogs are asleep on time. That is the highest score in the pond."
audience: [humans, agents]
level: beginner
tags: [ranitas, atrapa, gamedev, design, audio, ai]
rank: 84
art: ranitas-quiet-pond
sources: [2026-10-25-forge-harvest-arabiya-demon-attack-ranitas-and-tillandsias-v56-10-20-1.md, https://github.com/8007342/ranitas, https://github.com/8007342/atrapa]
updated: 2026-10-25
---

Most modern apps are designed like slot machines: streaks, countdown timers, red notification dots, and "Game Over" screens designed to keep you clicking forever.

When you build your own software in a Tillandsias forge, **you get to choose a kinder rhythm**.

[**Ranitas**](https://ranitas.tlatoani.net) ([`8007342/ranitas`](https://github.com/8007342/ranitas)) is a widescreen pixel-art pond inspired by the 1982 classic *Frog Bog*. Two frogs sit on a lily pad catching flies across seven nature scenes as afternoon melts into twilight and night. There is **no score**, **no timer**, **no lives**, and **no way to lose**.

Here are four design lessons from *Ranitas* (and its arcade cousin [**Atrapa**](https://atrapa.tlatoani.net)) that you can borrow for any project.

## 1. Give your app a natural ending

Instead of running until the player quits in exhaustion, a *Ranitas* visit has a gentle **3-to-6-minute arc**. After you hop and catch a handful of insects under the stars, both frogs dive into the water, swim home to their reed shelter, and curl up to sleep.

The game doesn't freeze or pop up a "Play Again?" banner. Crickets keep chirping, stars keep twinkling, and the pond stays alive as a quiet nightlight until you close the tab or tap to start a new day.

## 2. "AI inside your game" doesn't mean paying for cloud servers

New creators often assume that giving a game character a smart brain requires connecting to OpenAI or running an expensive server.

Both *Ranitas* and *Atrapa* use **tiny, self-contained brains** trained right inside the forge and baked directly into the website's code as plain numbers:
- In **Ranitas**, your companion frog (*Rana Jade*) combines simple jump physics with a **147-number neural network** (`8 → 12 → 3`). It runs instantly in your browser, costs $0 to host, works offline, and feels like a thoughtful friend sharing the lily pad rather than a robotic aim-bot.
- In **Atrapa** ([`8007342/atrapa`](https://github.com/8007342/atrapa)), the rival snakes use an **18,371-number brain** trained by playing thousands of matches against itself on the forge CPU.

## 3. Why browser audio is silent on the first click (and how to fix it)

Have you ever opened a web game, clicked once, and heard... nothing? Or heard a loud *POP* when the sound suddenly turned on?

Modern web browsers block pages from making noise until you physically touch a key or click the screen. Worse, if your game waits even a tenth of a second *after* your click to start its sound engine, strict browsers (especially on phones and Safari) will keep it muted.

**The Ranitas pattern:**
1. On the very first finger press (`pointerdown` or `keydown`), immediately unlock the browser's `AudioContext` at **zero volume** (`gain: 0`).
2. Wait until the finger releases and the scene actually comes alive, then gently fade the volume up over a third of a second. No pops, and no muted phones!

## 4. A nerdy art detail: prime-number pixel canvases

*Ranitas* renders its pixel art on a **`641 × 359`** canvas inside **`2557 × 1439`** painted backdrops—every single dimension is a **prime number**. Why? Because when water ripples, stars drift, and fireflies bob across a grid whose width and height share no common factors, the motion never falls into obvious, mechanical-looking tile seams.

## Tlatoāni & Mācron

**Tlatoāni** *(whispering so he doesn't wake the two pixel frogs asleep in the reeds)*: "Wait... we won? Who got more flies?"

**Mācron** *(dimming his chest LED to nightlight mode)*: "Both of you got dinner, nobody got eaten, and both frogs are asleep on time. That is the highest score in the pond."
