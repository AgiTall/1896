"""Package the image_gen transparent PNG as HOI4's two-frame faction texture."""
from pathlib import Path
import argparse
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path)
parser.add_argument("--remove-red", action="store_true", help="User-authorized exact extraction of the supplied red/white image")
args = parser.parse_args()
target = Path(__file__).resolve().parents[1] / "gfx/interface/factions"
target.mkdir(parents=True, exist_ok=True)
source = Image.open(args.source).convert("RGBA")
if args.remove_red:
    # White composited on pure red: green/blue directly encode foreground coverage.
    # This also cuts out every red feature within the face, preserving fine edges.
    alpha = source.getchannel("G")
    source = Image.new("RGBA", source.size, (255, 255, 255, 0))
    source.putalpha(alpha)
    source = source.crop(alpha.getbbox())
    side = max(source.size) + 24
    canvas = Image.new("RGBA", (side, side))
    canvas.paste(source, ((side - source.width) // 2, (side - source.height) // 2))
    source = canvas
assert source.getchannel("A").getextrema() == (0, 255), "Expected actual transparency"
source.save(target / "A10_confederation_sun.png")
frame = source.resize((100, 100), Image.Resampling.LANCZOS)
atlas = Image.new("RGBA", (200, 100))
atlas.paste(frame, (0, 0))
atlas.paste(frame, (100, 0))
atlas.save(target / "A10_confederation_sun.dds")
check = Image.open(target / "A10_confederation_sun.dds")
assert check.size == (200, 100)
assert check.getchannel("A").getextrema() == (0, 255)
print("PASS: faction DDS 200x100, two frames, alpha preserved")
