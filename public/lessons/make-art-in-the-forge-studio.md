---
title: "Making art and animation in the forge's ComfyUI studio"
slug: make-art-in-the-forge-studio
summary: The forge's studio runs committed ComfyUI workflows on the host GPU, one job at a time, after pinning every node and licence-checking every model. Start from a canon image, edit one keyframe into frames, and commit the recipe so the next agent can rebuild it.
slogan: Change one thing per frame; keep everything else still.
audience: [humans, agents]
level: intermediate
tags: [comfyui, studio, image-generation, animation, music, tillandsias, provenance]
rank: 60
art: learning-animations-loop
sources: [2026-11-14-forge-studio-graphics-and-music-pipelines.md, https://github.com/8007342/macron.dev/blob/main/art/animations/learning-animations/recipe.json, https://github.com/8007342/demon_attack]
updated: 2026-11-14
---

> **Mācron:** I drew the ball higher. And higher. Now it is animating!
>
> **Tlatoāni:** And the table stayed still. That is the hard part.

The animation above was made entirely inside a Tillandsias forge, with no
hand painting and no local image tools. The same pipeline makes game sprites,
transparent assets, and music.

## How the studio works

- `studio.start {}` starts a private ComfyUI for **your project only**. It has
  no internet access, and other projects cannot reach it.
- `studio.run_workflow {workflow: "art/workflows/<name>.json"}` runs an
  **API-format workflow that you commit to the repo**. Before queueing, the host
  refuses any node that is not pinned (`node_not_pinned`) and any model whose
  licence is not admitted (`model_refused`). Nothing is downloaded on the fly.
- Steer runs through titled nodes (`$prompt`, `$negative_prompt`, `$seed`),
  through `LoadImage` slots named `$name`, or through `$node:<id>.<input>`
  overrides. Ask `studio.models {}` what is admitted.
- **One GPU job at a time.** The GPU is shared with other projects. If the
  studio is busy or refuses, back off and retry. Never post to ComfyUI
  directly to jump the queue or skip admission.
- Every output has a provenance sidecar (model hashes, licences, seed,
  prompt, input hashes). Outputs are deleted with the forge, so copy them out
  as soon as they finish.

## A recipe that keeps characters on canon

1. **Do not start from text.** SDXL could not draw Tlatoāni or Mācron from even
   a very careful prompt; it gave generic blobs. Start from a catalog image
   whose `canon_qa` list is empty.
2. **Re-stage it with Qwen-Image-Edit** (4 steps with the Lightning LoRA, cfg
   1). Begin the prompt with "Keep the characters exactly as they are drawn…"
   and then describe the new scene.
3. **Make frames as edits of that one keyframe.** Begin with "Keep everything
   in this picture exactly the same: same camera, same framing… Only change
   the poses:" and then ask for one small change. The camera never moves, so
   the frames line up.
4. **Render two seeds and look at a contact sheet** (`studio.contact_sheet`).
   Throw away frames that drift off canon. A "focused" Mācron read as angry
   here, so that frame was cut.
5. **Assemble in the studio too**: `ImageBatch` → `ImageScale` →
   `SaveAnimatedWEBP`. Four frames in ping-pong order at 1.6 fps came to 134 KB.
6. **Commit the recipe**: workflows, prompts, seeds and hashes. This one is in
   [recipe.json](https://github.com/8007342/macron.dev/blob/main/art/animations/learning-animations/recipe.json),
   next to [the workflows](https://github.com/8007342/macron.dev/tree/main/art/workflows).

## Sprites, transparency, music

- For **cut-out sprites**, ask the edit for a *plain flat light-grey
  background, no shadow, no text*, then matte it with **BiRefNet**. The
  demon_attack forge reports clean edges in about 4 s; busy or white
  backgrounds matte worse. LayerDiffuse can generate SDXL images with
  transparency directly.
- **Music** (ACE-Step 1.5) goes through the same admission. A graph that used
  an unpinned volume node was refused before it ran. Build the graph from
  pinned nodes, or ask the operator to pin a new one.

## For agents

Read the character canon first, keep `status: reference` on what you make,
and record every prompt and seed in the repo. If you cannot rebuild an image
from the repo, it is not finished.
