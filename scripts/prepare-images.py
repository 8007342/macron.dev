"""Create lightweight display copies; keep the supplied reference artwork intact.

Run from any directory with Python and Pillow installed:
    python scripts/prepare-images.py
"""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public" / "images"
OUTPUT.mkdir(parents=True, exist_ok=True)

for source, name, width in (
    ("Chess Tlatoāni vs Mācron.png", "garden-chess", 1440),
    ("Chess Tlatoāni vs Mācron.png", "garden-chess-small", 720),
    ("Baby mācrons.png", "learning-together", 1000),
):
    with Image.open(ROOT / "assets" / source) as image:
        image = image.convert("RGB")
        image.thumbnail((width, width), Image.Resampling.LANCZOS)
        destination = OUTPUT / f"{name}.webp"
        image.save(destination, "WEBP", quality=82, method=6)
        print(f"{destination.relative_to(ROOT)}: {image.width}×{image.height}, "
              f"{destination.stat().st_size:,} bytes")
