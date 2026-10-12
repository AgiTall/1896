"""Build the Clausewitz bitmap font used for country labels on the map."""

from __future__ import annotations

import struct
from pathlib import Path

from PIL import Image, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "gfx" / "fonts"
SOURCE_TTF = FONT_DIR / "Preciosa.ttf"
OUTPUT_FNT = FONT_DIR / "hoi_mapfont4.fnt"
OUTPUT_DDS = FONT_DIR / "hoi_mapfont4.dds"

FONT_SIZE = 78
LINE_HEIGHT = 78
BASELINE = 67
PADDING = 4
ATLAS_WIDTH = 2048
ATLAS_HEIGHT = 1024
INK_RGB = (18, 3, 2)
INK_ALPHA = 233


def glyph_ids() -> list[int]:
    # The current HOI4 map font covers ASCII, Latin Extended and Cyrillic.
    return list(range(32, 127)) + list(range(160, 384)) + list(range(1024, 1280))


def split_free_rectangles(
    free_rectangles: list[tuple[int, int, int, int]],
    used: tuple[int, int, int, int],
) -> list[tuple[int, int, int, int]]:
    ux, uy, uw, uh = used
    result: list[tuple[int, int, int, int]] = []

    for fx, fy, fw, fh in free_rectangles:
        if ux >= fx + fw or ux + uw <= fx or uy >= fy + fh or uy + uh <= fy:
            result.append((fx, fy, fw, fh))
            continue

        if ux > fx:
            result.append((fx, fy, ux - fx, fh))
        if ux + uw < fx + fw:
            result.append((ux + uw, fy, fx + fw - ux - uw, fh))
        if uy > fy:
            result.append((fx, fy, fw, uy - fy))
        if uy + uh < fy + fh:
            result.append((fx, uy + uh, fw, fy + fh - uy - uh))

    pruned: list[tuple[int, int, int, int]] = []
    for index, rect in enumerate(result):
        x, y, w, h = rect
        if w <= 0 or h <= 0:
            continue
        if any(
            index != other_index
            and x >= ox
            and y >= oy
            and x + w <= ox + ow
            and y + h <= oy + oh
            for other_index, (ox, oy, ow, oh) in enumerate(result)
        ):
            continue
        pruned.append(rect)
    return pruned


def pack(rectangles: list[dict[str, object]]) -> None:
    free = [(0, 0, ATLAS_WIDTH, ATLAS_HEIGHT)]
    for glyph in sorted(rectangles, key=lambda item: (item["height"], item["width"]), reverse=True):
        width = int(glyph["width"])
        height = int(glyph["height"])
        candidates = [rect for rect in free if width <= rect[2] and height <= rect[3]]
        if not candidates:
            raise RuntimeError(f"Preciosa glyph atlas does not fit {ATLAS_WIDTH}x{ATLAS_HEIGHT}")
        x, y, _, _ = min(candidates, key=lambda rect: (rect[1], rect[0], rect[2] * rect[3]))
        glyph["x"] = x
        glyph["y"] = y
        free = split_free_rectangles(free, (x, y, width, height))


def write_dds(atlas: Image.Image) -> None:
    mipmaps = [atlas]
    # HOI4 1.19 ships this atlas as BGRA8 with exactly four mip levels.
    # Matching the vanilla header avoids the renderer silently rejecting the
    # replacement and falling back to the cached Tahoma map font.
    while len(mipmaps) < 4:
        width, height = mipmaps[-1].size
        mipmaps.append(
            mipmaps[-1].resize((max(1, width // 2), max(1, height // 2)), Image.Resampling.LANCZOS)
        )

    # Uncompressed BGRA8 DDS, matching HOI4's map atlas flags and layout.
    flags = 0x000A1007
    caps = 0x00401008
    header = (
        b"DDS "
        + struct.pack(
            "<7I",
            124,
            flags,
            ATLAS_HEIGHT,
            ATLAS_WIDTH,
            ATLAS_WIDTH * ATLAS_HEIGHT * 4,
            0,
            len(mipmaps),
        )
        + struct.pack("<11I", *([0] * 11))
        + struct.pack("<8I", 32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
        + struct.pack("<5I", caps, 0, 0, 0, 0)
    )
    with OUTPUT_DDS.open("wb") as stream:
        stream.write(header)
        for mipmap in mipmaps:
            stream.write(mipmap.tobytes("raw", "BGRA"))


def main() -> None:
    character_ids = glyph_ids()
    font = ImageFont.truetype(SOURCE_TTF, FONT_SIZE)
    fallback_font = ImageFont.truetype(Path("C:/Windows/Fonts/tahoma.ttf"), FONT_SIZE)
    missing_mask = font.getmask(chr(0x10FFFF), mode="L")
    missing_signature = (missing_mask.size, bytes(missing_mask))
    glyphs: list[dict[str, object]] = []

    for glyph_id in character_ids:
        character = chr(glyph_id)
        selected_font = font
        raw_mask = selected_font.getmask(character, mode="L")
        if character != " " and (raw_mask.size, bytes(raw_mask)) == missing_signature:
            selected_font = fallback_font
            raw_mask = selected_font.getmask(character, mode="L")
        left, top, right, bottom = selected_font.getbbox(character, anchor="ls")
        mask_core = Image.frombytes("L", raw_mask.size, bytes(raw_mask))
        core_width, core_height = mask_core.size
        width = max(1, core_width) + PADDING * 2
        height = max(1, core_height) + PADDING * 2
        glyphs.append(
            {
                "id": glyph_id,
                "character": character,
                "font": selected_font,
                "mask": mask_core,
                "width": width,
                "height": height,
                "xoffset": left - PADDING,
                "yoffset": BASELINE + top - PADDING,
                "xadvance": round(selected_font.getlength(character)),
            }
        )

    pack(glyphs)
    alpha = Image.new("L", (ATLAS_WIDTH, ATLAS_HEIGHT), 0)
    for glyph in glyphs:
        mask = glyph["mask"].point(lambda value: round(value * INK_ALPHA / 255))
        alpha.paste(mask, (int(glyph["x"]) + PADDING, int(glyph["y"]) + PADDING))

    atlas = Image.new("RGBA", (ATLAS_WIDTH, ATLAS_HEIGHT), (*INK_RGB, 0))
    atlas.putalpha(alpha)
    write_dds(atlas)

    kernings: list[tuple[int, int, int]] = []
    glyph_by_id = {int(glyph["id"]): glyph for glyph in glyphs}
    for first_id in character_ids:
        first_glyph = glyph_by_id[first_id]
        first = str(first_glyph["character"])
        selected_font = first_glyph["font"]
        first_length = selected_font.getlength(first)
        for second_id in character_ids:
            second_glyph = glyph_by_id[second_id]
            if second_glyph["font"] is not selected_font:
                continue
            second = str(second_glyph["character"])
            amount = round(selected_font.getlength(first + second) - first_length - selected_font.getlength(second))
            if amount:
                kernings.append((first_id, second_id, amount))

    lines = [
        f'info face="Preciosa" size={FONT_SIZE} bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=1 aa=1 padding={PADDING},{PADDING},{PADDING},{PADDING} spacing=1,1 outline=0',
        f"common lineHeight={LINE_HEIGHT} base={BASELINE} scaleW={ATLAS_WIDTH} scaleH={ATLAS_HEIGHT} pages=1 packed=0 alphaChnl=1 redChnl=0 greenChnl=0 blueChnl=0",
        'page id=0 file="hoi_mapfont4.dds"',
        f"chars count={len(glyphs)}",
    ]
    for glyph in sorted(glyphs, key=lambda item: item["id"]):
        lines.append(
            "char id={id:<4} x={x:<5} y={y:<5} width={width:<5} height={height:<5} "
            "xoffset={xoffset:<5} yoffset={yoffset:<5} xadvance={xadvance:<5} page=0 chnl=15".format(**glyph)
        )
    lines.append(f"kernings count={len(kernings)}")
    lines.extend(
        f"kerning first={first} second={second} amount={amount}"
        for first, second, amount in kernings
    )
    OUTPUT_FNT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
