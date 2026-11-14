"""Pack a VACE "bridge" that regenerates the seam of a loop.

usage: python pack_bridge.py CLIP_DIR DEPTH_DIR OUT_CONTROL.png OUT_MASK.png

CLIP_DIR holds the 49 frames of a looping clip (frame 48 ~ frame 0) named so
that sorting gives their order; DEPTH_DIR holds the 48 blockout depth frames.
The bridge is 25 frames, matched to Wan's VAE grouping (1 + 4 + 4 ...):
  0-8    clip frames 35..43   kept (mask black)   - context before the seam
  9-16   depth for 44..47, 0..3 generated (white) - across the seam
  17-24  clip frames 4..11    kept (mask black)   - context after the seam
The final loop is then clip[4..43] + bridge[9..16] = 48 frames, and its wrap
(bridge[16] -> clip[4]) sits inside material the model saw as one clip.
"""
import os
import sys
from PIL import Image

clip_dir, depth_dir, out_c, out_m = sys.argv[1:5]
clip = sorted(f for f in os.listdir(clip_dir) if f.endswith(".png"))
depth = sorted(f for f in os.listdir(depth_dir) if f.endswith(".png"))
assert len(clip) >= 48 and len(depth) == 48, (len(clip), len(depth))
img = lambda d, f: Image.open(os.path.join(d, f)).convert("RGB").resize((640, 480), Image.LANCZOS)
black, white = Image.new("RGB", (640, 480), (0, 0, 0)), Image.new("RGB", (640, 480), (255, 255, 255))
frames, masks = [], []
for i in range(35, 44):
    frames.append(img(clip_dir, clip[i])); masks.append(black)
for t in (44, 45, 46, 47, 0, 1, 2, 3):
    frames.append(img(depth_dir, depth[t])); masks.append(white)
for i in range(4, 12):
    frames.append(img(clip_dir, clip[i])); masks.append(black)
assert len(frames) == 25
frames[0].save(out_c, save_all=True, append_images=frames[1:], duration=83, loop=0)
masks[0].save(out_m, save_all=True, append_images=masks[1:], duration=83, loop=0)
print("bridge: 9 kept + 8 generated + 8 kept = 25 frames")
