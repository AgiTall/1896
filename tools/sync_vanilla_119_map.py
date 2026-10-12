from __future__ import annotations

import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ROOT = Path(
    r"C:\Users\AgiTall\Documents\Paradox Interactive\Hearts of Iron IV\mod\1896"
)
GAME = Path(r"D:\SteamLibrary\steamapps\common\Hearts of Iron IV")


def assert_exact_path(actual: Path, expected: Path) -> None:
    if actual.resolve() != expected.resolve():
        raise RuntimeError(f"Unexpected path: {actual.resolve()} (expected {expected.resolve()})")


def backup(directories: list[Path]) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive = ROOT.parent / f"1896_states_and_supply_before_1.19_{timestamp}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for directory in directories:
            for path in sorted(directory.rglob("*")):
                if path.is_file():
                    output.write(path, path.relative_to(ROOT))
    return archive


def replace_txt_directory(source: Path, target: Path) -> tuple[int, int]:
    assert_exact_path(target, ROOT / target.relative_to(ROOT))
    source_files = sorted(source.glob("*.txt"))
    target_files = sorted(target.glob("*.txt"))
    if not source_files:
        raise RuntimeError(f"No source files in {source}")

    # Targets are resolved and checked before individual files are removed.
    for path in target_files:
        if path.resolve().parent != target.resolve():
            raise RuntimeError(f"Refusing to remove unexpected path: {path}")
        path.unlink()
    for path in source_files:
        shutil.copy2(path, target / path.name)
    return len(target_files), len(source_files)


def verify_state_ids(directory: Path) -> None:
    ids: dict[int, Path] = {}
    for path in directory.glob("*.txt"):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        match = re.search(r"(?m)^\s*id\s*=\s*(\d+)(?:\s*#.*)?\s*$", text)
        if not match:
            raise RuntimeError(f"Missing state id: {path.name}")
        state_id = int(match.group(1))
        if state_id in ids:
            raise RuntimeError(f"Duplicate state id {state_id}: {ids[state_id].name}, {path.name}")
        ids[state_id] = path
    expected = set(range(1, 1082))
    if set(ids) != expected:
        raise RuntimeError(
            f"State ID mismatch; missing={sorted(expected - set(ids))}, extra={sorted(set(ids) - expected)}"
        )


def main() -> None:
    assert_exact_path(ROOT, EXPECTED_ROOT)
    if not GAME.is_dir():
        raise RuntimeError(f"HOI4 directory not found: {GAME}")

    states = ROOT / "history" / "states"
    supply = ROOT / "map" / "supplyareas"
    archive = backup([states, supply])
    old_states, new_states = replace_txt_directory(GAME / "history" / "states", states)
    old_supply, new_supply = replace_txt_directory(GAME / "map" / "supplyareas", supply)
    verify_state_ids(states)
    print(
        f"Backup: {archive}\n"
        f"States: {old_states} -> {new_states}\n"
        f"Supply areas: {old_supply} -> {new_supply}"
    )


if __name__ == "__main__":
    main()
