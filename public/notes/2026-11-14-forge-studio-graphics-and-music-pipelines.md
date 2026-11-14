# Building graphics (and music) pipelines from a forge with the ComfyUI studio

The operator asked for a learnings note on the forge's host-side ComfyUI studio,
and for a small looping animation of Tlatoāni and Mācron learning to animate,
made with that studio and documented well enough to repeat. This note covers
what I did, what failed, and lessons relayed from the demon_attack forge, which
ran the same studio earlier the same week.

## The shape of the studio

- The forge has no GPU and no ComfyUI of its own. `studio.start {}` starts a
  ComfyUI container for **this project only**, on the project's own network
  (no host port, no internet egress). It took about 10 s to answer. It stops
  with the forge.
- `studio.run_workflow` takes a path to an **API-format workflow JSON committed
  in the project checkout**, not an ad-hoc graph. Before anything is queued,
  the host checks two things:
  - **Node admission:** every node `class_type` must be on a pinned allowlist,
    or the run is refused with `node_not_pinned`.
  - **Licence admission:** every model file must be pinned with an admitted
    licence, or the run is refused with `model_refused`. Nothing is downloaded
    on demand.
- Knobs reach the graph only through named slots: nodes titled `$prompt`,
  `$negative_prompt` and `$seed`; `LoadImage` nodes whose image is `$name`
  (bound with `inputs` or `init_image`); and `$node:<id>.<input>` overrides,
  which are also pin- and licence-checked.
- Every output gets a provenance sidecar with the engine version, the
  workflow's sha256, each model's repo, revision, sha256 and licence, each
  input's sha256, the seed and the prompt. That made the recipe below easy to
  write honestly.
- Outputs land in an ephemeral folder that is deleted when the forge shuts
  down. Copy what you keep straight away.
- `studio.models {}` lists what is admitted. On this run (tray 56.11.10.1) that
  was: SDXL base 1.0 and SDXL-Lightning, Animagine XL 4.0, the pixel-art-xl
  LoRA, LayerDiffuse transparency (SDXL), IP-Adapter plus, ControlNet union and
  OpenPose, Qwen-Image-Edit-2511 (with Lightning 4-step LoRAs), BiRefNet
  matting, FLUX.2-klein-4B, Wan 2.2 VACE, and ACE-Step 1.5 (music). Licences
  were Apache-2.0, MIT, OpenRAIL++ or CreativeML OpenRAIL-M. A teammate
  reported that Qwen-Image text-to-image and a Real-ESRGAN upscaler were still
  pending admission, so I did not use them.
- **One GPU job at a time.** The studio shares the host GPU queue with
  `image.generate` and with other projects' studios. A long batch from another
  project can make you wait. Back off and retry; never call ComfyUI directly
  to skip the queue. In this session the queue was free (`gpu_wait` 0 ms
  on every run), so I never had to retry.

## What I did, including what failed

1. **SDXL text-to-image keyframe: rejected.** I ran 4 seeds of a careful prompt
   built from the canon's prompt kernels. None of them drew an axolotl with
   gills or a cream robot with a screen face; they gave generic cute blobs. Text
   alone does not carry these characters.
2. **Qwen-Image-Edit from a canon-close image: worked.** I gave a catalog image
   whose canon QA list is empty (*Quote Anchors Hold*) to Qwen-Image-Edit-2511
   (fp8, Lightning 4-step LoRA, 4 steps, cfg 1, euler/simple, AuraFlow shift
   3) and asked for a new scene: both at a table with a paper flipbook. Both
   seeds kept the characters on canon.
3. **The first run was refused by ComfyUI's validator, not by admission.**
   `ImageScaleToTotalPixels` in ComfyUI v0.40 needs `resolution_steps`. The
   error named the missing input, so the fix was one line.
4. **Frames were pose edits of the keyframe.** Each prompt began "Keep
   everything in this picture exactly the same: same camera, same framing…
   Only change the poses:", followed by one small change. The camera never
   moved between frames, which is what makes a loop possible without a video
   model.
5. **One frame was rejected for tone.** A "ball squashes at the bottom" frame
   gave Mācron "focused" eyes that read as angry and made Tlatoāni look
   worried. The canon says non-scary, so I dropped it rather than ship a
   complete bounce.
6. **Assembly ran in the studio too.** Core `ImageBatch` → `ImageScale` →
   `SaveAnimatedWEBP` made a 4-frame ping-pong loop (1 → 2 → 3 → 2) at 1.6 fps:
   134 KB at 512 px wide and 123 KB at 480 px. No model and about 1 s of time.
   No local ImageMagick or Pillow was needed.

Timings: Qwen edits took about 13 s warm (about 22 s for the first of a
batch), SDXL took about 9 s an image, and assembly about 1 s.

The prompts, seeds, model hashes and workflow files are committed in
`art/animations/learning-animations/recipe.json` and `art/workflows/`.

## Lessons relayed from the demon_attack forge

The demon_attack forge shared these when asked. They are paraphrased, and I
did not verify them in this session:

- The same Qwen-Image-Edit settings worked for its game sprites (shift about
  3.1). It scaled sources to about 1 MP with nearest-exact to keep pixel edges
  crisp, then area-downscaled to game size.
- **BiRefNet** gives clean alpha in about 4 s when the edit prompt asks for a
  *plain flat light-grey background, no shadow, no text*. Busy or white
  backgrounds matte worse.
- SDXL earns its place for **seed-reproducible rebuilds** of art that already
  exists, not for new character fidelity.
- **Music hit node admission:** an ACE-Step graph that used
  `AudioAdjustVolume` was refused with `node_not_pinned`. The only fix was a
  host allowlist pin and a tray rebuild. Admission is a feature: plan the
  graph around pinned nodes, or ask the operator to pin one.
- Render two seeds and pick, because one seed tends to grow stray props. Keep
  the prompt and seed fixed across a unit's frames, and look at a contact
  sheet (`studio.contact_sheet`) before committing to a whole family. Run long
  batches serially with a checkpoint (commit or push) per family.

## What I did not test

I did not run ACE-Step music myself in this session, so the music details above
are second-hand. I did not use LayerDiffuse, BiRefNet or the Wan video model
either. A video model could give smoother in-betweens than four edited frames;
that is the next experiment.
