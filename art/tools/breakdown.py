"""Build the web assets for the "how it was made" breakdown.

usage: python breakdown.py BLOCKOUT_DIR FINAL_FRAMES_DIR OUT_DIR [--frames 48] [--fps 12]
                            [--name learning-animations-loop] [--width 640] [--prefix breakdown]
                            [--quality 82] [--light] [--light-quality 60]

BLOCKOUT_DIR holds wire/, clay/ and depth/ (from blockout.py); FINAL_FRAMES_DIR
holds the generated frames in order (PNG). Writes:
  NAME.webp                  the final loop (FRAMES frames, lossy, WIDTH px)
  NAME-small.webp            the same at 480 px wide (the site serves it to phones
                             and on lesson cards); with --light, every other frame
                             (half the fps, same duration) at q60 (--light-quality), to stay under ~1 MB
  PREFIX-wire.webp, PREFIX-depth.webp, PREFIX-final.webp
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
NAME = args[args.index("--name") + 1] if "--name" in args else "learning-animations-loop"
WIDTH = int(args[args.index("--width") + 1]) if "--width" in args else 640
PREFIX = args[args.index("--prefix") + 1] if "--prefix" in args else "breakdown"
LIGHT = "--light" in args
LQ = int(args[args.index("--light-quality") + 1]) if "--light-quality" in args else 60
Q = int(args[args.index("--quality") + 1]) if "--quality" in args else 82
os.makedirs(out, exist_ok=True)


def load(d, n):
    files = sorted(f for f in os.listdir(d) if f.endswith(".png"))[:n]
    assert len(files) == n, f"{d}: need {n} frames, found {len(files)}"
    return [Image.open(os.path.join(d, f)).convert("RGB") for f in files]


def save(frames, path, width, quality, step=1):
    h = round(frames[0].height * width / frames[0].width)
    fr = [f.resize((width, h), Image.LANCZOS) for f in frames]
    fr[0].save(path, save_all=True, append_images=fr[1:], duration=ms * step, loop=0, quality=quality, method=6)
    print(f"{path}: {len(fr)} frames, {width}x{h}, {os.path.getsize(path):,} bytes")


final = load(fin, N)
save(final, os.path.join(out, f"{NAME}.webp"), WIDTH, Q)
if LIGHT:
    save(final[::2], os.path.join(out, f"{NAME}-small.webp"), 480, LQ, step=2)
else:
    save(final, os.path.join(out, f"{NAME}-small.webp"), 480, Q - 4)
for name in ("wire", "depth"):
    save(load(os.path.join(blk, name), N), os.path.join(out, f"{PREFIX}-{name}.webp"), 320, 70)
save(final, os.path.join(out, f"{PREFIX}-final.webp"), 320, 72)
