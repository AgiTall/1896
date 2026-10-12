from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATES = ROOT / "history" / "states"

COUNTRY_HISTORY_LINE = re.compile(
    r"^[ \t]*(?:owner|controller|add_core_of|add_claim_by|remove_claim_by|transfer_state_to)[ \t]*=.*(?:\r?\n|$)",
    re.MULTILINE,
)
HISTORY_OPEN = re.compile(
    r"^(?P<indent>[ \t]*)history[ \t]*=[ \t]*(?:\r?\n[ \t]*)?\{[ \t]*(?:\r?\n|$)",
    re.MULTILINE,
)


def decode(raw: bytes) -> tuple[str, str]:
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig"), "utf-8-sig"
    try:
        return raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return raw.decode("cp1252"), "cp1252"


def main() -> None:
    changed = 0
    for path in sorted(STATES.glob("*.txt")):
        text, encoding = decode(path.read_bytes())
        newline = "\r\n" if "\r\n" in text else "\n"
        cleaned = COUNTRY_HISTORY_LINE.sub("", text)

        match = HISTORY_OPEN.search(cleaned)
        if not match:
            raise RuntimeError(f"No history block in {path.name}")

        indent = match.group("indent") + "\t"
        ownership = f"{indent}owner = ZZZ{newline}{indent}add_core_of = ZZZ{newline}"
        normalized = cleaned[: match.end()] + ownership + cleaned[match.end() :]

        if normalized != text:
            path.write_text(normalized, encoding=encoding, newline="")
            changed += 1

    print(f"Normalized {changed} of {len(list(STATES.glob('*.txt')))} state files")


if __name__ == "__main__":
    main()
