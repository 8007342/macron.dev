# A full greenhouse, a moving camera, and a robot with three eyes

The third note of the day. After the 48-frame loop, the user said it looked much
simpler than the art on the other pages and asked for refinements: a rich,
full room and maybe some camera movement. This is what that took, including
the three runs that didn't ship.

## Borrow the room from the canon

The other pages' art is dense: plants on every shelf, light through leaves,
a sea view. The quickest way to get that look was to start from a canon picture
rather than describe it. *Chess Tlatoāni vs Mācron* already shows the greenhouse
terrace with both characters, so Qwen-Image-Edit-2511 (Lightning, 4 steps)
re-staged it: chessboard out, an open flipbook with a red ball in, everything
else kept. Both seeds stayed on model; seed 302 shipped (seed 301 handed the
pencil to Tlatoāni). That still became the video model's identity and style
reference.

The Blender blockout was then rebuilt to match that picture, so the control and
the reference agree (kumbia-kombat's lesson again): a round table with a
runner, Tlatoāni on a stool at the left, Mācron on the tabletop, tiered
shelves of pots, a pergola, hanging globes, a lantern, vines, a low parapet
open to the view. The camera makes a slow arc of ±10° around the table and
pushes in by 30 cm at mid-loop, a periodic path, so frame 72 is frame 0 for
the camera too.

## Three eyes, twice

The first full run (81 frames at 768×576, about 31 min) was rich and steady,
but Mācron had **three** cyan eyes in every frame. The vines, modelled as chains
of spheres, came out as strings of red beads, and Tlatoāni's gills were small.

The second run fixed the vines (leaf shapes) and the gills, raised the eyes'
geometry, and put "exactly two glowing cyan eyes" in the prompt and "three
eyes" in the negative. Still three eyes. The reason is in the depth video:
at 2.5 m from the camera, a 3 cm bump is about two grey levels out of 255, so
the control said nothing about eyes and the model kept its own idea.

The fix was to say it in the control: in the depth pass, Mācron's two eye
objects get a pure-white emission instead of their depth, two bright dots on
his face. The third run drew two eyes in every frame. A control video doesn't
have to be pure depth; a small, deliberate hint in it was followed where the
prompt was ignored.

## Seeds still matter

That third run (seed 32) lost the story: the ball stayed as red marks on the
page, and Mācron's body picked up a camouflage pattern. The first two runs
(seed 31) had drawn the hop well, so the fourth run went back to seed 31 with
the eye hint kept, a slightly bigger ball with higher hops, and "a plain smooth
cream body" in the prompt. It drew two eyes, a plain body with a teal panel,
and a ball that visibly pops off the page and bounces. That one shipped.

## Judging a seam when the camera moves

With a static camera, the loop's wrap could be compared with the average
frame-to-frame change. With a moving camera, every step is large (mean 13 out
of 255, peaking near 17.6 where the arc is fastest), so that number says
nothing. What matters is whether the wrap's step looks like its neighbours'.
I measured *jolt*: each step minus the average of the two steps around it.
The blended wrap has a jolt of −0.06; the loop averages 0.25 and never goes
past 1.0. Without the blend, the wrap's jolt was −0.6.

## The studio side

- **A free reading can be a lull.** I queued the first long run when
  `gpu.status` showed no holders and 22.8 GB free, but another project was
  partway through a batch of 26 music cues; the gap between two cues looked
  like a free GPU. The coordinator let the job finish (the music fell back to
  tiled decoding), and I held further work until the batch was done and then
  announced each long run before queueing it.
- **One host-side timeout.** A run failed after 20 s with a container
  timeout before reaching ComfyUI; the identical resubmission ran.
- **New models, old tools.** The tray was updated mid-session to admit
  Qwen-Image text-to-image and a Real-ESRGAN upscaler, but a forge's host
  tools keep the old code until the forge is relaunched
  (`tillandsias.lane_version` reports this), so neither was used. The loop is
  rendered at 768×576 and published at 640×480 instead of being upscaled.
- Timings: the keyframe edit took 35 s for two seeds, the blockout about
  10 min of CPU for 216 renders, each Wan run about 31 min, and the web
  encode under a minute. The final loop is 2.9 MB as WebP at 640 px.

Everything that ran is in the repo: `art/tools/blockout_room.py`,
`art/workflows/wan-vace-room.json`, and
`art/animations/greenhouse-loop/recipe.json`, with prompts, seeds, hashes
and the runs that did not ship.
