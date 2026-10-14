"""Create lightweight display copies; keep the supplied reference artwork intact.

Run from any directory with Python and Pillow installed:
    python scripts/prepare-images.py

Outputs:
- public/images/{garden-chess,garden-chess-small,learning-together}.webp
  for the landing page.
- public/images/gallery/<id>.webp (longest side 1200) and
  <id>-small.webp (longest side 480) for every item listed in
  public/art/catalog.json, whose "source" field names the original in assets/.
"""

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public" / "images"
GALLERY = OUTPUT / "gallery"
CATALOG = ROOT / "public" / "art" / "catalog.json"
GALLERY_QUALITY = 72  # 80 gave ~6.7 MB for the gallery; 72 keeps it under ~6 MB


def save_copy(source, destination, longest_side, quality):
    with Image.open(source) as image:
        image = image.convert("RGB")
        image.thumbnail((longest_side, longest_side), Image.Resampling.LANCZOS)
        image.save(destination, "WEBP", quality=quality, method=6)
        print(f"{destination.relative_to(ROOT)}: {image.width}×{image.height}, "
              f"{destination.stat().st_size:,} bytes")


OUTPUT.mkdir(parents=True, exist_ok=True)
for source, name, width in (
    ("Chess Tlatoāni vs Mācron.png", "garden-chess", 1440),
    ("Chess Tlatoāni vs Mācron.png", "garden-chess-small", 720),
    ("Baby mācrons.png", "learning-together", 1000),
):
    save_copy(ROOT / "assets" / source, OUTPUT / f"{name}.webp", width, 82)

GALLERY.mkdir(parents=True, exist_ok=True)
total = 0
for item in json.loads(CATALOG.read_text(encoding="utf-8"))["items"]:
    for suffix, side in (("", 1200), ("-small", 480)):
        destination = GALLERY / f"{item['id']}{suffix}.webp"
        save_copy(ROOT / item["source"], destination, side, GALLERY_QUALITY)
        total += destination.stat().st_size
print(f"gallery total: {total:,} bytes")
