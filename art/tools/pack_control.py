"""Pack a Blender pass (one PNG per frame) into the multi-frame PNGs that
art/workflows/wan-vace-loop.json reads with LoadImage.

usage: python pack_control.py PASS_DIR LENGTH OUT_CONTROL.png OUT_MASK.png [--pin IMAGE]

The loop closes by construction: frame i of the control is pass frame
i % FRAMES, so with LENGTH = FRAMES + 1 the last control frame equals the
first and the clip can drop it and repeat seamlessly. The mask is all white
(VACE generates every pixel of every frame, guided by the control).

--pin IMAGE puts IMAGE on the first and the last frame and marks those two
frames black (keep) in the mask, so the generated clip must start and end on
exactly that picture: the seam of the loop disappears.
"""
import os
import sys
from PIL import Image

src, n, out_c, out_m = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
pin = sys.argv[sys.argv.index("--pin") + 1] if "--pin" in sys.argv else None
files = sorted(f for f in os.listdir(src) if f.endswith(".png"))
frames = [Image.open(os.path.join(src, files[i % len(files)])).convert("RGB") for i in range(n)]
white = Image.new("RGB", frames[0].size, (255, 255, 255))
black = Image.new("RGB", frames[0].size, (0, 0, 0))
masks = [white] * n
if pin:
    key = Image.open(pin).convert("RGB").resize(frames[0].size, Image.LANCZOS)
    frames[0] = frames[-1] = key
    masks = [black] + [white] * (n - 2) + [black]
frames[0].save(out_c, save_all=True, append_images=frames[1:], duration=83, loop=0)
masks[0].save(out_m, save_all=True, append_images=masks[1:], duration=83, loop=0)
print(f"{n} frames from {len(files)} ({frames[0].size[0]}x{frames[0].size[1]})")
