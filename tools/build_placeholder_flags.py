"""Generate simple flags for the A01-A10 placeholder countries."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
COLORS = {
    "A01": (155, 35, 45),
    "A02": (38, 93, 155),
    "A03": (45, 135, 74),
    "A04": (178, 132, 38),
    "A05": (112, 62, 148),
    "A06": (35, 143, 151),
    "A07": (176, 72, 126),
    "A08": (91, 105, 53),
    "A09": (132, 76, 46),
    "A10": (77, 77, 145),
}
SIZES = {
    "": (82, 52),
    "medium": (41, 26),
    "small": (10, 7),
}


def main() -> None:
    for folder, size in SIZES.items():
        target = ROOT / "gfx" / "flags" / folder
        target.mkdir(parents=True, exist_ok=True)
        for tag, color in COLORS.items():
            image = Image.new("RGBA", size, (*color, 255))
            draw = ImageDraw.Draw(image)
            border = max(1, round(size[1] / 26))
            draw.rectangle((0, 0, size[0] - 1, size[1] - 1), outline=(235, 235, 225, 255), width=border)

            if size[0] >= 41:
                font_size = 18 if size[0] == 82 else 9
                font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", font_size)
                box = draw.textbbox((0, 0), tag, font=font)
                x = (size[0] - (box[2] - box[0])) // 2
                y = (size[1] - (box[3] - box[1])) // 2 - box[1]
                draw.text((x + 1, y + 1), tag, font=font, fill=(0, 0, 0, 150))
                draw.text((x, y), tag, font=font, fill=(255, 255, 245, 255))

            image.save(target / f"{tag}.tga")


if __name__ == "__main__":
    main()
