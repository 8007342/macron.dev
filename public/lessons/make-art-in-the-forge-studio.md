---
title: "Making art and animation in the forge's ComfyUI studio"
slug: make-art-in-the-forge-studio
summary: Block out the whole room and the camera path in Blender (it runs headless in the forge), render a depth pass, re-stage a canon picture as the style reference, and let Wan 2.2 VACE draw every frame to match in one run. Then close the loop inside that same run, and commit the recipe so the next agent can rebuild it.
slogan: Block the world first; then let the model draw it.
audience: [humans, agents]
level: intermediate
tags: [comfyui, studio, blender, animation, camera-motion, wan-vace, qwen-image-edit, image-generation, tillandsias, provenance]
rank: 62
art: greenhouse-loop
sources: [2026-11-14-forge-greenhouse-camera-loop-three-eyes.md, 2026-11-14-forge-blender-blockout-to-wan-vace-loop.md, 2026-11-14-forge-studio-graphics-and-music-pipelines.md, https://github.com/8007342/macron.dev/blob/main/art/animations/greenhouse-loop/recipe.json, https://github.com/8007342/macron.dev/blob/main/art/animations/learning-animations/recipe.json, https://github.com/8007342/kumbia-kombat/blob/main/LESSONS_LEARNED.md, https://github.com/8007342/demon_attack]
updated: 2026-11-14
---

> **Mācron:** I drew a ball, and it bounced off the page!
>
> **Tlatoāni:** It bounced because the table was there first.

The loop above is 72 frames (6 s at 12 fps), with the camera slowly arcing
around the table. Mācron draws in his flipbook, the ball pops off the page and
bounces three times, and Tlatoāni points and smiles. No frame was painted by
hand, and everything ran inside a Tillandsias forge.

## How it was made

| Blocked out in Blender | Depth pass (the control) | Drawn by Wan 2.2 VACE |
|---|---|---|
| ![Wireframe of the greenhouse terrace: pergola, hanging globes, shelves, round table, stool and both characters' simple shapes, with the camera arcing](/images/howto/learning-animations/room-wire.webp) | ![Grey depth video of the same scene: near is white, and Mācron's two eyes are marked as white dots](/images/howto/learning-animations/room-depth.webp) | ![The final drawn frames, in step with the other two](/images/howto/learning-animations/room-final.webp) |

1. **Start from a canon picture.** Qwen-Image-Edit re-staged *Chess Tlatoāni
   vs Mācron*: chessboard out, flipbook in, everything else kept. That still is
   the video model's identity and style reference, which is where the rich
   greenhouse comes from. A text prompt alone never drew these characters.
2. **Build the whole room and the camera path.**
   `art/tools/blockout_room.py` models the terrace from that picture: pergola,
   hanging globes, lantern, shelves of pots, a round table, a stool, the
   flipbook, the ball, and both characters from the canon's simple shapes.
   Contacts are computed, so nothing clips. The motion *and* the camera arc
   are cyclic: frame 72 is frame 0.
3. **Render a depth pass, and mark what depth can't show.** Near is white,
   with Blender's `Raw` view transform so values stay linear. Anything the
   model must keep has to show up in it. Mācron's eyes are a few centimetres
   deep at 2.5 m, about two grey levels, so two runs drew him with **three**
   eyes, even with "exactly two eyes" in the prompt. Painting the two eyes pure
   white in the depth video fixed it in every frame.
4. **Let a video model draw it.** Wan 2.2 Fun VACE takes the depth video as its
   control and the still as its reference, and generates all 81 frames in one
   run (about 31 min at 768×576), so nothing pops between frames. Seeds
   matter: the seed that fixed the eyes lost the ball's hop, so the shipped
   run went back to the seed that drew the hop.
5. **Close the loop inside one run.** Generate past the cycle (81 for 72) and
   blend frames 72–79 into 0–7. With a moving camera every frame differs a lot
   from the last, so judge the seam by its *jolt*: how far the wrap's step
   differs from the average of its neighbours. Here it is −0.06, against
   0.25 on average across the loop.
6. **Commit the recipe.** Prompts, seeds, model hashes and every failed run
   are in
   [recipe.json](https://github.com/8007342/macron.dev/blob/main/art/animations/greenhouse-loop/recipe.json),
   next to [the tools](https://github.com/8007342/macron.dev/tree/main/art/tools)
   and [the workflows](https://github.com/8007342/macron.dev/tree/main/art/workflows).

The previous version, a 48-frame loop with a fixed camera in a sparse room,
shows how far the room and the reference carry a shot:

![The earlier 48-frame loop: a simpler workshop, fixed camera](/images/gallery/learning-animations-loop-small.webp)

## Blender in a forge

There is no `blender` binary, but the `bpy` wheel runs headless:
`uv python install 3.13`, then a venv on persistent disk, then
`uv pip install bpy==5.3.0` (about 430 MB). Workbench, EEVEE and Cycles all
render on the CPU (about 10 min for 216 frames of the full room).
kumbia-kombat keys its dance poses on a Blender rig the same way.

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
- **A free GPU reading can be a lull.** `gpu.status` showed no holders between
  another project's back-to-back music cues, and a 31-minute video job landed
  in the middle of that batch. When someone has announced a batch, ask before
  queueing anything long, and say how long it will run.
- **New tray, old tools.** A tray update reaches a forge's host tools only when
  the forge is relaunched, so newly admitted models (here Qwen-Image and
  Real-ESRGAN) can be installed but out of reach. `tillandsias.lane_version`
  says which.

## Stills, sprites and music

- For a **still** with canon identity, re-stage a canon-close image with
  Qwen-Image-Edit (4 steps with the Lightning LoRA). Starting from text alone
  failed to draw either character with SDXL. Qwen-Image 2512 text-to-image
  and a Real-ESRGAN upscaler are admitted as of tray v56.11.14.3; neither has
  been tried here yet.
- For **cut-out sprites**, ask for a *plain flat light-grey background* and matte
  it with BiRefNet. The demon_attack forge reports clean edges in about 4 s.
- **Music** (ACE-Step 1.5) goes through the same admission. A graph with an
  unpinned volume node was refused before it ran.

## For agents

Read the character canon first, keep `status: reference` on what you make,
and measure your loop's steps and wrap instead of trusting your eye on a
contact sheet. If you cannot rebuild it from the repo, it is not finished.
