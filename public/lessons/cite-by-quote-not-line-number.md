---
title: "Line numbers drift; words stay put: how tillandsias.org keeps its promises true"
slug: cite-by-quote-not-line-number
summary: "When your code changes, documentation links to 'line 42' silently rot. Here is how tillandsias.org anchors every technical claim to an exact quote—and checks them automatically on every release."
slogan: "Line numbers drift; words stay put."
audience: [humans, agents]
level: intermediate
tags: [tillandsias-org, documentation, verification, releases, writing]
rank: 79
art: quote-anchors-hold
sources: [2026-10-25-forge-harvest-arabiya-demon-attack-ranitas-and-tillandsias-v56-10-20-1.md, https://github.com/8007342/tillandsias.org, https://github.com/8007342/tillandsias]
updated: 2026-10-25
---

Every project has a website or a `README` that makes promises about how the software works. And in almost every project, six months later, half of those explanations are slightly out of date.

Someone adds ten lines of code at the top of a file, and suddenly your footnote pointing to `security.sh#L42` points to a blank comment instead of the firewall rule.

When [**tillandsias.org**](https://tillandsias.org) ([`8007342/tillandsias.org`](https://github.com/8007342/tillandsias.org)) was redesigned for the **`v56.10.20.1`** release, it solved two hard problems at once: **how to explain a complex system to five completely different kinds of readers**, and **how to make sure the footnotes never lie**.

## 1. Speak to the reader's curiosity, not just one technical level

If you write only for beginners, security auditors think you are hiding the details. If you write only for kernel engineers, newcomers bounce off the first paragraph.

`tillandsias.org` lets the reader pick their own lens right at the top of the page:
- **Like I'm 5:** The doll house, the single doorman, and the one-way post box.
- **Phone:** How Tillandsias compares to the sandbox on an iPhone or Android phone.
- **Power user:** Containers, mounts, and workflow commands.
- **Security:** Threat models, isolation boundaries, tmpfs credential files, and proxy enforcement.
- **MathWiz:** Formal invariants and verifiable properties.

Every tab describes the **exact same system**—nobody gets talked down to, and nobody has to wade through jargon they didn't ask for.

## 2. Anchor your footnotes to *quotes*, not line numbers

In the **Security** and **MathWiz** views, every claim links directly to the exact line of source code in the [`8007342/tillandsias`](https://github.com/8007342/tillandsias) repository that makes that claim true.

Wait—if Tillandsias ships a new release (`v56.10.17` → `v56.10.19` → `v56.10.20.1`), don't all the line numbers move?

Yes! That is why `tillandsias.org` stores **the exact code quote** alongside each footnote instead of trusting the old line number:
1. When a new release of Tillandsias is published, `scripts/release-refresh.sh` downloads the new source tree.
2. `scripts/anchors.py` searches each file for the **verbatim quote** (for example, the exact `podman run` isolation flag or proxy rule).
3. If the code moved from line `410` to line `438`, the script updates the GitHub link automatically.
4. **If the code was deleted or changed so the quote no longer exists**, the script stops and flags it immediately—forcing a human or agent to update the explanation so the website never makes a stale promise.

> **How you can use this:** Whenever you write a guide or test that points to another file, anchor it to a unique phrase or function signature that can be searched automatically, not a bare line number.

## Tlatoāni & Mācron

**Tlatoāni** *(holding a treasure map that says "walk 42 paces north from the cloud")*: "The cloud moved! Now 42 paces puts me inside a cactus!"

**Mācron** *(tapping the brass quote-anchor in his hand)*: "Never tie your rope to a line number, Tlatoāni. Tie it to the actual words carved in the rock—if the rock slides three feet to the left, the rope follows it."
