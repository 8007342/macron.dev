"""Build the web assets for the "how it was made" breakdown.

usage: python breakdown.py BLOCKOUT_DIR FINAL_FRAMES_DIR OUT_DIR [--frames 48] [--fps 12]

BLOCKOUT_DIR holds wire/, clay/ and depth/ (from blockout.py); FINAL_FRAMES_DIR
holds the generated frames in order (PNG). Writes:
  learning-animations-loop.webp        the final loop (FRAMES frames, lossy)
  learning-animations-loop-small.webp  the same at 480 px wide
  breakdown-wire.webp, breakdown-depth.webp, breakdown-final.webp
                                       320 px loops of each stage, in step
This only packs and scales frames: no pixel of the final loop is painted here.
"""
import os
import sys
from PIL import Image

blk, fin, out = sys.argv[1], sys.argv[2], sys.argv[3]
args = sys.argv[4:]
N = int(args[args.index("--frames") + 1]) if "--frames" in args else 48
FPS = float(args[args.index("--fps") + 1]) if "--fps" in args else 12.0
ms = round(1000 / FPS)
os.makedirs(out, exist_ok=True)


def load(d, n):
    files = sorted(f for f in os.listdir(d) if f.endswith(".png"))[:n]
    assert len(files) == n, f"{d}: need {n} frames, found {len(files)}"
    return [Image.open(os.path.join(d, f)).convert("RGB") for f in files]


def save(frames, path, width, quality):
    h = round(frames[0].height * width / frames[0].width)
    fr = [f.resize((width, h), Image.LANCZOS) for f in frames]
    fr[0].save(path, save_all=True, append_images=fr[1:], duration=ms, loop=0, quality=quality, method=6)
    print(f"{path}: {len(fr)} frames, {width}x{h}, {os.path.getsize(path):,} bytes")


final = load(fin, N)
save(final, os.path.join(out, "learning-animations-loop.webp"), 640, 82)
save(final, os.path.join(out, "learning-animations-loop-small.webp"), 480, 78)
for name in ("wire", "depth"):
    save(load(os.path.join(blk, name), N), os.path.join(out, f"breakdown-{name}.webp"), 320, 70)
save(final, os.path.join(out, "breakdown-final.webp"), 320, 72)
