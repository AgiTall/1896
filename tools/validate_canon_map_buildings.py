"""Check nudger building assignments after the canonical state splits.

Run with --repair to transfer positions into their current states.
"""
from pathlib import Path
import re
import sys
from collections import Counter
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPLIT_STATES = {315, 327, 628, 334, 1049, 1082, 1083, 1084, 1085, 1086}


def validate(repair=False):
    province_states = {}
    for path in (ROOT / "history/states").glob("*.txt"):
        text = path.read_text(encoding="utf-8-sig")
        state = int(re.search(r"\bid\s*=\s*(\d+)", text)[1])
        provinces = re.search(r"\bprovinces\s*=\s*\{([^}]+)\}", text)[1]
        for province in re.findall(r"\d+", re.sub(r"#.*", "", provinces)):
            province_states[int(province)] = state
    colors = {}
    for row in (ROOT / "map/definition.csv").read_text(encoding="utf-8-sig").splitlines():
        fields = row.split(";")
        if fields[0].isdigit():
            colors[tuple(map(int, fields[1:4]))] = int(fields[0])
    image = Image.open(ROOT / "map/provinces.bmp").convert("RGB")
    path = ROOT / "map/buildings.txt"
    original = path.read_bytes()
    rows = original.decode("utf-8-sig").splitlines(keepends=True)
    failures = []
    ports = Counter()
    for index, row in enumerate(rows):
        fields = row.split(";")
        if len(fields) < 5 or not fields[0].isdigit():
            continue
        state = int(fields[0])
        if state not in SPLIT_STATES:
            continue
        pixel = (int(float(fields[2])), image.height - 1 - int(float(fields[4])))
        province = colors.get(image.getpixel(pixel))
        target = province_states.get(province)
        # Offshore spawn positions lie in sea provinces without a state.
        if target is None:
            continue
        if target != state:
            failures.append((index + 1, state, target, province))
            if repair:
                assert target in SPLIT_STATES, failures[-1]
                fields[0] = str(target)
                rows[index] = ";".join(fields)
                state = target
        if fields[1] == "naval_base_spawn" and state == target:
            ports[province] += 1
    moved = {p for p, s in province_states.items() if s in {1082, 1083, 1084, 1085, 1086}}
    if repair and failures:
        backup = ROOT / "tools/backups/canon_map_buildings/buildings.txt"
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            backup.write_bytes(original)
        path.write_bytes("".join(rows).encode("utf-8"))
        print(f"Reassigned {len(failures)} building positions; backup: {backup}")
        return validate()
    assert not failures, f"Incorrect map building states: {failures}"
    assert moved <= ports.keys(), f"Missing port positions: {sorted(moved - ports.keys())}"
    print(f"PASS: building positions match province states; all {len(moved)} moved provinces have port positions.")


if __name__ == "__main__":
    validate(repair="--repair" in sys.argv)
