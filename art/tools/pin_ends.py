"""Build a VACE control video and mask that pin one image at the first and
last frame (so the clip loops) and leave every frame between free.

usage: python pin_ends.py KEYFRAME LENGTH OUT_CONTROL.png OUT_MASK.png [W H]
Writes multi-frame (APNG) files; ComfyUI's LoadImage reads them as a batch.
Control: the keyframe on pinned frames, flat grey elsewhere.
Mask:    black (keep) on pinned frames, white (generate) elsewhere.
"""
import sys
from PIL import Image

key, n, out_c, out_m = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
w, h = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (640, 480)
k = Image.open(key).convert("RGB").resize((w, h), Image.LANCZOS)
grey, black, white = (Image.new("RGB", (w, h), c) for c in ((127, 127, 127), (0, 0, 0), (255, 255, 255)))
pinned = {0, n - 1}
ctrl = [k if i in pinned else grey for i in range(n)]
mask = [black if i in pinned else white for i in range(n)]
ctrl[0].save(out_c, save_all=True, append_images=ctrl[1:], duration=83, loop=0)
mask[0].save(out_m, save_all=True, append_images=mask[1:], duration=83, loop=0)
