---
title: "Making art and animation in the forge's ComfyUI studio"
slug: make-art-in-the-forge-studio
summary: Start from a canon painting, fit a Blender blockout to its framing (it runs headless in the forge), render a depth pass, use the painting itself as the reference, and let Wan 2.2 VACE draw every frame to match in one run. Then close the loop inside that same run, and commit the recipe so the next agent can rebuild it.
slogan: Start from the canon; block the world to match; then let the model move it.
audience: [humans, agents]
level: intermediate
tags: [comfyui, studio, blender, animation, camera-motion, wan-vace, qwen-image-edit, image-generation, tillandsias, provenance]
rank: 62
art: ink-dot-loop
sources: [2026-11-14-forge-seed-the-animation-from-canon-art.md, https://github.com/8007342/macron.dev/blob/main/art/animations/ink-dot-loop/recipe.json, 2026-11-14-forge-greenhouse-camera-loop-three-eyes.md, 2026-11-14-forge-blender-blockout-to-wan-vace-loop.md, 2026-11-14-forge-studio-graphics-and-music-pipelines.md, https://github.com/8007342/macron.dev/blob/main/art/animations/greenhouse-loop/recipe.json, https://github.com/8007342/macron.dev/blob/main/art/animations/learning-animations/recipe.json, https://github.com/8007342/kumbia-kombat/blob/main/LESSONS_LEARNED.md, https://github.com/8007342/demon_attack]
updated: 2026-11-14
---

> **Mācron:** I wrote the dot, and it hopped off the page!
>
> **Tlatoāni:** Count it again. It came back.

The loop above is 72 frames (6 s at 12 fps), with a very slow camera drift. It
is the canon painting *Arabiya Ink and Voices* come to life: Mācron finishes a
stroke with his reed pen, the dot under the curve pops off the paper, bounces
three times and settles back in its place, and Tlatoāni smiles and nods. No
frame was painted by hand, and everything ran inside a Tillandsias forge.

## How it was made

| Fitted in Blender | Depth pass (the control) | Drawn by Wan 2.2 VACE |
|---|---|---|
| ![Wireframe of the blockout fitted to the painting: the table, jars, paper, hanging globes, Mācron's boxy head and Tlatoāni's round head and gills, with the dot hopping](/images/howto/learning-animations/canon-wire.webp) | ![Grey depth video of the same scene: near is white, and Mācron's two eyes and the hopping dot are marked as white dots](/images/howto/learning-animations/canon-depth.webp) | ![The final drawn frames, in step with the other two](/images/howto/learning-animations/canon-final.webp) |

1. **Start from the canon art.** The repo's paintings are prettier than
   anything a prompt draws from scratch, so the painting itself, unedited, is
   the video model's reference. It sets the characters, the room and the style.
2. **Fit the blockout to the painting.** `art/tools/blockout_canon.py` places
   every proxy by un-projecting its pixel position in the painting through the
   frame-0 camera at a chosen distance: Mācron's head at (482, 392) and 1.6 m,
   the jars on the table where the painting puts them. `--overlay` draws the
   depth pass's edges over the painting, so you can see the fit before spending
   GPU time.
3. **Move a little.** The motion and a gentle camera drift (±4°, a 6 %
   push-in) are cyclic: frame 72 is frame 0. The further the camera strays
   from the painting's view, the more the model has to invent.
4. **Mark what depth can't show, and check every frame.** Mācron's eyes and
   the 2 cm dot are painted pure white in the depth video. `--check` tests the
   moving parts against the table and the props in every frame and fails on
   any overlap. The greenhouse loop below first shipped with Tlatoāni's legs
   through his stool, because its blockout had them there.
5. **Let a video model draw it.** Wan 2.2 Fun VACE takes the depth video as
   its control and the painting as its reference, and draws all 81 frames in
   one run (about 23 min at 768×512). Big gestures read differently than you
   meant: swinging Mācron's whole arm out toward Tlatoāni was drawn as a long
   stretched arm poking his cheek, so the shipped run lifts the hand only a
   little.
6. **Close the loop inside one run.** Generate past the cycle (81 for 72) and
   blend frames 72–79 into 0–7. With a moving camera, judge the seam by its
   *jolt*: how far the wrap's step differs from the average of its
   neighbours. Here it is 0.62, inside the loop's own range (up to 1.79).
7. **Commit the recipe.** Prompts, seeds, model hashes and every failed run
   are in
   [recipe.json](https://github.com/8007342/macron.dev/blob/main/art/animations/ink-dot-loop/recipe.json),
   next to [the tools](https://github.com/8007342/macron.dev/tree/main/art/tools)
   and [the workflows](https://github.com/8007342/macron.dev/tree/main/art/workflows).

The previous version modelled a greenhouse terrace from scratch and used a
re-staged picture as the reference. It moves more, but the characters drift
off model (a sleeveless robe, a boxy robot):

![The earlier greenhouse loop: a camera arc around a round table, with characters drawn from a blockout built from scratch](/images/gallery/greenhouse-loop-small.webp)

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
- **gpu.status doesn't list every holder.** A run failed 16 s in with
  `gpu_memory_busy` because an image.generate engine held 18 GB unlisted.
  Check the ticket with `studio.job_status` a minute after queueing, and
  ask before unloading anything you didn't start.

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
