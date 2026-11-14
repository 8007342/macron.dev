# From a Blender blockout to a 48-frame loop with Wan VACE, all inside a forge

This is a follow-up to the same day's studio note. The operator reviewed the
first animation (four Qwen-edited frames in ping-pong order) and was right:
it jumped between frames. They asked for 24–48 smooth frames with no identity
drift or pops, a Blender wireframe/armature path, and a truthful page.
This note covers what happened, failures included.

## Blender runs in a forge, as a Python wheel

There is no `blender` binary or shim in the forge, but the `bpy` wheel works
headless. bpy 5.3 needs Python 3.13, so the steps are `uv python install 3.13`
(uv refuses a managed download until you install that Python explicitly),
then a venv on persistent disk, then `uv pip install bpy==5.3.0` (about 430
MB). Workbench, EEVEE and Cycles all rendered headless on the CPU. The
kumbia-kombat project runs Blender the same way for its rig, which is where
the idea came from.

## The little world first, then the motion

Following the operator's hint, `art/tools/blockout.py` builds the whole
scene rather than just two figures: greenhouse posts and beams, glass globes,
potted plants, a table, a stool, an open flipbook, a red ball, and proxies of
both characters made from the canon's shapes. Contacts are computed: Mācron
sits on the tabletop, and the ball's squash keeps its bottom on the page, so
nothing clips. The motion is computed per frame and is cyclic by
construction (frame 48 is frame 0). Each frame renders three passes:
wireframe, clay, and linear depth.

Bugs found by looking at the renders, not by reasoning:
- The gill fronds pointed into the head (a sign error), and Tlatoāni faced away
  from the book (another sign error).
- Workbench cannot render its wireframe viewport mode. A Wireframe modifier
  can.
- The first depth pass came out nearly white. Blender's display transform
  brightens emission, so depth needs the `Raw` view transform and a near/far
  range fitted to the camera.
- At the first framing, the ball hop was invisible at 640 px. The camera came
  closer and the ball got bigger.

## Why Wan 2.2 VACE, and what did not work

- **A layout-matched keyframe with two-image Qwen-Image-Edit failed.**
  Picture 1 was the old keyframe and picture 2 the Blender clay render. Both
  seeds drew *two* robots and kept picture 1's table. This is kumbia-kombat's
  lesson that the prompt and the control image must agree, or the model draws
  both.
- **Frame-by-frame image editing was ruled out** before trying: kumbia-kombat
  needed a registration step to stop per-frame wander, and the first version
  here showed the same jumps.
- **Wan 2.2 Fun VACE 14B** (admitted, Apache-2.0) generates the clip as one
  video, so it is coherent over time. Its control was the 49-frame Blender
  depth video and its identity reference was the original keyframe. ComfyUI's
  core `LoadImage` reads every frame of a multi-frame PNG as a batch, so the
  control video and mask go in as two APNGs. No custom nodes were needed.

## Closing the loop (three tries)

I measured every clip as the mean absolute change between consecutive
grey frames (0–255), and then looked at the frames.

- **Pass A** (depth only, 49 frames) was smooth: the largest step was 3.2,
  with no spikes. But the last frame differed from the first by 4.3, a
  visible hitch at the wrap.
- **Pinning failed.** I pinned one frame at both ends (mask black means keep),
  but the ends still differed by 4.0. Wan's VAE packs frames in groups of
  four, and a kept frame is *redrawn*, not copied: every frame differed from
  the pin by about 10. A close look showed the real hitch: Mācron's pencil
  came and went. At 6 mm it never showed in the depth pass, so whether he
  held it was up to the model.
- **A bridge failed.** I regenerated the 8 frames across the seam between 9
  and 8 kept frames. The kept frames were redrawn as well (off by 5–6), so
  splicing two runs made two jumps (6.9 and 12.8) instead of one. The lesson:
  between two separate generations there is a redraw floor of about 4–6;
  inside one run, neighbours differ by about 1.
- **What worked: overlap inside one run.** I thickened the pencil and arms so
  depth carries them, then generated 57 frames of the 48-frame cycle in a
  single run. Frames 48–56 redraw the moments of 0–8 within the same run (only
  about 2 apart), and blending them into frames 0–7 during that quiet beat puts
  the wrap at **0.7**. That is smaller than the loop's average step (1.11); the
  largest step is 2.7, during the ball's hops. A blend is safe here because
  both drawings show the same pose; blending two *different* poses is what
  kumbia-kombat warns against.

## The studio side

- **First use of Wan downloads its weights.** `studio.models` listed the files
  as on disk, but the first run spent about 20 minutes (one cancelled attempt)
  plus 311 s (the next) fetching and hashing the two 17 GB experts and the
  6.7 GB text encoder before anything reached ComfyUI. A teammate on the host
  confirmed this. Do not cancel a first run, or the download may restart.
- **Two studios, one GPU, no arbiter.** Three Wan jobs failed within 4 s with
  `VRAM grow failed` in the text encoder. demon_attack's studio runs short
  jobs back to back on the same A5000, so `gpu.status` looks free between
  them. Doubling backoff found one gap, and the host coordinator then asked
  demon_attack to pause at a family boundary, which opened a window. Asking
  beat waiting.
- Warm Wan runs at 640×480 with 20 steps across the two experts took about
  8½ min for 49 frames, 4½ min for 25 and 10 min for 57. The Blender passes
  took about 5½ min on the CPU.
- The final loop is 48 frames at 12 fps: 1.24 MB as WebP at 640 px and
  0.66 MB at 480 px. The page's breakdown shows wireframe, depth and final
  loops in step, 320 px each.

Everything that ran is in the repo: `art/tools/` (blockout, packing, loop
blend, web encode), `art/workflows/wan-vace-loop.json`, and
`art/animations/learning-animations/recipe.json`, which records the prompts,
seeds, model hashes and every attempt that did not ship.
