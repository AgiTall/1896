"""Run checks for the current campaign without invoking migration generators.

Requires Python 3, Pillow and the installed HOI4 files used by the research
validators. The older Japanese campaign validators target archived trees.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
CHECKS = (
    ("Engine script regressions", "validate_engine_syntax_regressions.py"),
    ("1893 starting research and logistics", "validate_1893_start.py"),
    ("Research and warfare references", "audit_great_war_research.py"),
    ("Split-state building and port positions", "validate_canon_map_buildings.py"),
    ("Current Japanese focus tree", "validate_japan_mini.py"),
    ("Japanese protectorate negotiations", "validate_gameplay_polish.py"),
    ("Japanese maritime programme", "validate_jmc_maritime.py"),
    ("Japanese maritime course projects", "validate_jmc_operations.py"),
    ("Chamber debt book and island diplomacy", "validate_chamber_network.py"),
    ("Focus paths and research rewards", "validate_focus_polish.py"),
    ("Russian and English localisation", "validate_localisation_polish.py"),
    ("Dutch preparations and shared calendar", "validate_independent_preparations.py"),
    ("Borneo defence projects", "validate_borneo_defences.py"),
    ("Dutch crown and peace outcomes", "validate_crown_rework.py"),
    ("Dutch postwar finances and elections", "validate_federal_recovery.py"),
    ("Philippine campaign references and layout", "validate_philippines_rework.py"),
    ("Philippine republican agreements", "test_philippines_republics.py"),
    ("Philippine military paths", "test_philippines_military.py"),
    ("Philippine industry and supply", "A10D_validate_development.py"),
    ("Philippine Chamber agreements", "A10W_validate.py"),
)


def main():
    results = []
    for name, script in CHECKS:
        try:
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools" / script)],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=120, env={**os.environ, "PYTHONUTF8": "1"},
            )
            entry = {"name": name, "script": script, "passed": result.returncode == 0,
                     "exit_code": result.returncode}
            if not entry["passed"]:
                entry["output"] = result.stdout + result.stderr
        except (OSError, subprocess.TimeoutExpired) as exc:
            entry = {"name": name, "script": script, "passed": False, "output": str(exc)}
        results.append(entry)
        print(f"{'PASS' if entry['passed'] else 'FAIL'}: {name}", flush=True)
        if not entry["passed"]:
            print(entry["output"], flush=True)
    passed = sum(entry["passed"] for entry in results)
    report = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if passed == len(results) else "failed",
        "passed": passed,
        "total": len(results),
        "checks": results,
        "limitations": [
            "Static checks and bounded script models; HOI4 was not launched.",
            "No full campaign, combat balance or in-game visual verification.",
            "Archived campaign validators are not part of this current-content suite.",
        ],
    }
    output = ROOT / "tools/current_content_validation.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(results)} checks passed. Report: {output}")
    return int(passed != len(results))


if __name__ == "__main__":
    raise SystemExit(main())
