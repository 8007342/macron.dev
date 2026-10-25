---
title: "Make the check honest: real ink, offline voices, and truthful save badges"
slug: arabiya-honest-handwriting-and-offline-voices
summary: "How Arabiya (arabiya.tlatoani.net) went from accepting random scribbles and clipped cloud audio to verifying real Arabic letter shapes, generating 218 offline voice clips, and telling the truth about where progress is saved."
slogan: "Count the stroke and the dots, not just the ink."
audience: [humans, agents]
level: beginner
tags: [arabiya, testing, audio, cloudflare, ux, verification]
rank: 88
art: arabiya-ink-and-voices
sources: [2026-10-25-forge-harvest-arabiya-demon-attack-ranitas-and-tillandsias-v56-10-20-1.md, https://github.com/8007342/arabiya]
updated: 2026-10-25
---

When an AI builds a learning app or a game for you, its first instinct is to make everything look like it works on the very first try. Green checkmarks appear! Confetti falls!

Sometimes, though, the checkmark is **too polite**. While building [**Arabiya**](https://arabiya.tlatoani.net) ([`8007342/arabiya`](https://github.com/8007342/arabiya))—an interactive story that teaches beginners to read, hear, and trace Arabic—three "polite shortcuts" had to be replaced with honest engineering. Here is how to spot them in your own projects and what to ask your AI to do instead.

## 1. Test what should *fail*, not just what should pass

In Arabiya's early handwriting practice, you traced letters on a canvas. If you drew the letter carefully, you passed. Great!

Except if you scribbled a giant zigzag across the screen, or just tapped near the end of the line, **you also passed**. Why? Because the early grading code only counted how many points your finger drew and whether you finished near the end of the stroke.

**The fix:** Instead of counting points, Arabiya switched to a smaller, honest 4-letter tracing set (`ب ت ث ا`) that checks three real things:
- Did your pen actually cover the letter's path?
- Did you place the right number of distinct dots (one dot under *bā'*, two above *tā'*, three above *thā'*, none on *alif*)?
- Did you scribble extra ink everywhere else?

> **What to tell your AI:** *"Don't just test that a good answer passes. Write automated tests that try to cheat—scribbles, empty clicks, missing pieces—and prove the app rejects them."*

## 2. Generate voices once, verify them forever

Language apps need clear, warm audio. Early on, 41 of Arabiya's spoken lines were cut off mid-word or had robotic static from cloud voice generators, and nobody noticed until someone listened to them one by one.

**The fix:** Arabiya used a compact, open-weight neural voice model (**Kokoro-82M**) right inside the forge to regenerate the clips locally, and saved a cryptographic fingerprint (`SHA-256` hash) for all **218 MP3 files**. Every time the website builds, it checks all 218 files in a fraction of a second—no cloud API keys needed, and no broken audio can sneak back in.

## 3. Never show "Saved to the Cloud" until the cloud actually answers

Nothing breaks a user's trust faster than a badge that says *"Synced!"* when the user isn't actually signed in, or when the server rejected the save.

Arabiya now separates its progress badge into two plain-language truths:
- **"Saved on this device"** when you are playing as a guest or offline (stored in your browser's local storage).
- **Verified cloud sync** only after you sign in with Google and the server confirms your account ID.

### Bonus tip for Cloudflare Workers: bundle your server into one file

If your project uses a Cloudflare Worker with extra packages (like `jose` for verifying sign-in tokens), the forge's built-in preview tool (`wrangler`) might use a slightly older version than the one in your project and complain that it cannot find a package. Ask your AI to **pre-bundle the Worker into a single file with `esbuild`** before starting the preview. One self-contained file runs everywhere!

## Tlatoāni & Mācron

**Tlatoāni** *(drawing a cheerful smiley face on the Arabic tracing pad)*: "Look! Earlier this morning it gave me three gold stars for drawing a potato!"

**Mācron** *(holding up a magnifying glass over the three dots of ث)*: "That was before I learned the difference between *a lot of ink* and *the right letter*. Draw the boat curve and put three distinct dots on top—no potatoes allowed."
