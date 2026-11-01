"""Check active focus/event text and RU/EN localisation file integrity."""
from pathlib import Path
import re
from validate_philippines_rework import parse, value, walk


ROOT = Path(__file__).resolve().parents[1]
ENTRY = re.compile(r'^\s*([^\s:]+):\d*\s+"(.*)"\s*(?:#.*)?$')
CYRILLIC = re.compile(r"[\u0400-\u04ff]")
MOD_KEY = re.compile(r"(?:A\d{2}|JPI_|JSM_|JTH_|JMC_)")


def uncomment(text):
    """Remove script comments while preserving quoted strings."""
    return re.sub(r'"(?:\\.|[^"\\])*"|#[^\n]*',
                  lambda match: "" if match[0].startswith("#") else match[0], text)


def main():
    errors = []
    languages = {}
    file_count = 0
    for language in ("russian", "english"):
        keys = set()
        for path in sorted((ROOT / "localisation" / language).rglob("*.yml")):
            file_count += 1
            relative = path.relative_to(ROOT)
            raw = path.read_bytes()
            if not raw.startswith(b"\xef\xbb\xbf"):
                errors.append(f"{relative}: missing UTF-8 BOM")
            try:
                lines = raw.decode("utf-8-sig").splitlines()
            except UnicodeDecodeError as exc:
                errors.append(f"{relative}: {exc}")
                continue
            if not lines or lines[0].strip() != f"l_{language}:":
                errors.append(f"{relative}: incorrect language header")
            local_keys = set()
            for number, line in enumerate(lines[1:], 2):
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                match = ENTRY.fullmatch(line)
                if not match:
                    errors.append(f"{relative}:{number}: invalid entry")
                    continue
                key, text_value = match.groups()
                if key in local_keys:
                    errors.append(f"{relative}:{number}: duplicate key {key}")
                local_keys.add(key)
                keys.add(key)
                # Imported replacement text may quote source material. The mod's
                # own English text should never display an untranslated RU value.
                if language == "english" and path.parent.name == "english" and CYRILLIC.search(text_value):
                    errors.append(f"{relative}:{number}: untranslated text in {key}")
        languages[language] = keys

    required = set()
    focus_count = 0
    for path in (ROOT / "common/national_focus").glob("*.txt"):
        for kind, operator, node in walk(parse(path.read_text(encoding="utf-8-sig"))):
            if kind in ("focus", "shared_focus") and isinstance(node, list):
                key = value(node, "id")
                if not isinstance(key, str):
                    errors.append(f"{path.relative_to(ROOT)}: focus definition missing id")
                    continue
                focus_count += 1
                key = key.strip('"')
                required.update((key, key + "_desc"))
    for path in (ROOT / "events").glob("*.txt"):
        text = uncomment(path.read_text(encoding="utf-8-sig"))
        required.update(re.findall(r"\b(?:title|desc|name)\s*=\s*([\w.]+)", text))
    for folder in ("common/national_focus", "common/decisions", "common/scripted_effects"):
        for path in (ROOT / folder).rglob("*.txt"):
            text = uncomment(path.read_text(encoding="utf-8-sig"))
            for key in re.findall(r"\b(?:name|text|custom_effect_tooltip|custom_trigger_tooltip)\s*=\s*([\w.]+)", text):
                if MOD_KEY.match(key):
                    required.add(key)
    for language, keys in languages.items():
        for key in sorted(required - keys):
            errors.append(f"{language}: missing active text {key}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"PASS: {file_count} RU/EN files, {focus_count} focus definitions, "
          f"{len(required)} active text keys; BOM, syntax, duplicates and English text checked")


if __name__ == "__main__":
    main()
