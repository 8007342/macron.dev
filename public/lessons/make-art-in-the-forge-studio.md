---
title: "Making art and animation in the forge's ComfyUI studio"
slug: make-art-in-the-forge-studio
summary: Block out the world in Blender (it runs headless in the forge), render a depth pass, and let Wan 2.2 VACE draw every frame to match in one run. Then close the loop inside that same run, and commit the recipe so the next agent can rebuild it.
slogan: Block the world first; then let the model draw it.
audience: [humans, agents]
level: intermediate
tags: [comfyui, studio, blender, animation, wan-vace, image-generation, tillandsias, provenance]
rank: 62
art: learning-animations-loop
sources: [2026-11-14-forge-blender-blockout-to-wan-vace-loop.md, 2026-11-14-forge-studio-graphics-and-music-pipelines.md, https://github.com/8007342/macron.dev/blob/main/art/animations/learning-animations/recipe.json, https://github.com/8007342/kumbia-kombat/blob/main/LESSONS_LEARNED.md, https://github.com/8007342/demon_attack]
updated: 2026-11-14
---

> **Mācron:** I drew a ball, and it bounced off the page!
>
> **Tlatoāni:** It bounced because the table was there first.

The loop above is 48 frames (4 s at 12 fps). Mācron draws in his flipbook,
the ball hops off the page three times and settles back, and Mācron cheers and
looks up at Tlatoāni, who nods. No frame was painted by hand, and everything
ran inside a Tillandsias forge.

## How it was made

| Blocked out in Blender | Depth pass (the control) | Drawn by Wan 2.2 VACE |
|---|---|---|
| ![Wireframe of the greenhouse, table, flipbook, ball and both characters' simple shapes](/images/howto/learning-animations/breakdown-wire.webp) | ![Grey depth video of the same scene: near is white](/images/howto/learning-animations/breakdown-depth.webp) | ![The final drawn frames, in step with the other two](/images/howto/learning-animations/breakdown-final.webp) |

1. **Build the little world, not just the characters.** `art/tools/blockout.py`
   models a greenhouse corner, a table, a stool, a flipbook, a ball, and both
   characters from the canon's simple shapes. Mācron sits *on* the tabletop and
   the ball squashes against the page, so nothing clips. The motion is computed
   per frame and is cyclic: frame 48 is frame 0.
2. **Render a depth pass.** Near is white and far is black, with Blender's
   `Raw` view transform so the values stay linear. Anything the model must keep
   track of has to be thick enough to show up in depth. A 6 mm pencil didn't,
   so Mācron kept losing it until it was thickened.
3. **Let a video model draw it.** Wan 2.2 Fun VACE takes the depth video as its
   control and one drawn frame as the identity reference, and it generates the
   whole clip at once, so nothing pops between frames. Multi-frame PNGs go
   straight into core `LoadImage`, with no custom nodes.
4. **Close the loop inside one run.** Generate a few frames past the cycle (57
   for 48). Frames 48–56 redraw the moments of 0–8, so blend them into 0–7
   during a quiet beat. The wrap then measures 0.7 (mean change per frame, 0–255),
   below the loop's average step of 1.1. Pinning end frames and splicing runs
   both failed: any two separate generations differ by about 5.
5. **Commit the recipe.** Prompts, seeds, model hashes and every failed
   attempt are in
   [recipe.json](https://github.com/8007342/macron.dev/blob/main/art/animations/learning-animations/recipe.json),
   next to [the tools](https://github.com/8007342/macron.dev/tree/main/art/tools)
   and [the workflows](https://github.com/8007342/macron.dev/tree/main/art/workflows).

## Blender in a forge

There is no `blender` binary, but the `bpy` wheel runs headless:
`uv python install 3.13`, then a venv on persistent disk, then
`uv pip install bpy==5.3.0` (about 430 MB). Workbench, EEVEE and Cycles all
render on the CPU. kumbia-kombat keys its dance poses on a Blender rig the
same way.

## How the studio works

- `studio.start {}` starts a private ComfyUI for **your project only**. It has
  no internet access, and other projects cannot reach it.
- `studio.run_workflow` (blocking) or `studio.queue_workflow` (returns a
  ticket) runs an **API-format workflow committed to the repo**. Before
  queueing, the host refuses unpinned nodes (`node_not_pinned`) and
  unadmitted model licences (`model_refused`).
- Steer runs through titled nodes (`$prompt`, `$negative_prompt`, `$seed`),
  `LoadImage` slots named `$name`, and `$node:<id>.<input>` overrides. Put a
  marker word in your prompt and check ComfyUI's history to confirm it
  arrived; kumbia-kombat once lost a whole batch to an override that never
  reached the model.
- **The first use of a big model downloads it.** Wan's ~41 GB took about 25 min
  before the first job reached ComfyUI. Don't cancel it.
- **One GPU, several studios, no arbiter.** If another project runs short jobs
  back to back, yours can fail with `VRAM grow failed` even when the GPU looks
  free. Back off and retry, and ask the operator's coordinator for a window.
  Never jump the queue.

## Stills, sprites and music

- For a **still** with canon identity, re-stage a canon-close image with
  Qwen-Image-Edit (4 steps with the Lightning LoRA). Starting from text alone
  failed to draw either character.
- For **cut-out sprites**, ask for a *plain flat light-grey background* and matte
  it with BiRefNet. The demon_attack forge reports clean edges in about 4 s.
- **Music** (ACE-Step 1.5) goes through the same admission. A graph with an
  unpinned volume node was refused before it ran.

## For agents

Read the character canon first, keep `status: reference` on what you make,
and measure your loop's steps and wrap instead of trusting your eye on a
contact sheet. If you cannot rebuild it from the repo, it is not finished.
