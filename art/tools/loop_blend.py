"""Close a loop from a clip that runs past its cycle.

usage: python loop_blend.py CLIP_DIR CYCLE OVERLAP OUT_DIR

CLIP_DIR holds CYCLE + OVERLAP (or more) frames, generated in ONE run from a
control that repeats every CYCLE frames, so frames CYCLE..CYCLE+OVERLAP-1
show the same moments as frames 0..OVERLAP-1 (drawn a second time). Output
frame k (k < OVERLAP) mixes clip[CYCLE + k] into clip[k], with clip[k]'s
weight rising from 1/(OVERLAP+1) to OVERLAP/(OVERLAP+1); later frames are
copied unchanged. The wrap (out[CYCLE-1] -> out[0]) is then a step inside
the generated clip. The overlap should be a quiet beat (here: Mācron
drawing, ball at rest), so the mix only evens out line shimmer and never
blends two different poses.
"""
import os
import sys
from PIL import Image

src, cycle, overlap, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
files = sorted(f for f in os.listdir(src) if f.endswith(".png"))
assert len(files) >= cycle + overlap, (len(files), cycle + overlap)
os.makedirs(out, exist_ok=True)
load = lambda i: Image.open(os.path.join(src, files[i])).convert("RGB")
for k in range(cycle):
    frame = load(k)
    if k < overlap:
        frame = Image.blend(load(cycle + k), frame, (k + 1) / (overlap + 1))
    frame.save(os.path.join(out, f"{k:03d}.png"))
print(f"{cycle} frames, first {overlap} blended with their second drawing")
