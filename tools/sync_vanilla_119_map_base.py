from __future__ import annotations

import shutil
import zipfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ROOT = Path(
    r"C:\Users\AgiTall\Documents\Paradox Interactive\Hearts of Iron IV\mod\1896"
)
GAME_MAP = Path(r"D:\SteamLibrary\steamapps\common\Hearts of Iron IV\map")


def assert_path(actual: Path, expected: Path) -> None:
    if actual.resolve() != expected.resolve():
        raise RuntimeError(f"Unexpected path: {actual.resolve()} (expected {expected.resolve()})")


def main() -> None:
    assert_path(ROOT, EXPECTED_ROOT)
    target = ROOT / "map"
    terrain_target = target / "terrain"
    assert_path(target, EXPECTED_ROOT / "map")
    assert_path(terrain_target, EXPECTED_ROOT / "map" / "terrain")
    if not GAME_MAP.is_dir():
        raise RuntimeError(f"Vanilla map not found: {GAME_MAP}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive = ROOT.parent / f"1896_map_base_before_1.19_{timestamp}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for path in sorted(target.iterdir()):
            if path.is_file():
                output.write(path, path.relative_to(ROOT))
        for path in sorted(terrain_target.rglob("*")):
            if path.is_file():
                output.write(path, path.relative_to(ROOT))

    source_files = sorted(GAME_MAP.glob("*"))
    source_files = [path for path in source_files if path.is_file()]
    for source in source_files:
        shutil.copy2(source, target / source.name)

    for path in sorted(terrain_target.rglob("*"), reverse=True):
        resolved = path.resolve()
        if terrain_target.resolve() not in resolved.parents:
            raise RuntimeError(f"Refusing to alter unexpected path: {path}")
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            path.rmdir()
    shutil.copytree(GAME_MAP / "terrain", terrain_target, dirs_exist_ok=True)

    print(
        f"Backup: {archive}\n"
        f"Map files synchronized: {len(source_files)}\n"
        f"Terrain files synchronized: {len(list(terrain_target.rglob('*.*')))}"
    )


if __name__ == "__main__":
    main()
