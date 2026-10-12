"""Expand Dutch starting divisions while preserving deployments and readiness."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
oob = root / "history/units/A01_1877.txt"
text = oob.read_text(encoding="utf-8-sig")
units = text[text.index("units = {"):]

def template(name, unit, battalions, guns, priority):
    lines = ["division_template = {", f' name = "{name}"', " regiments = {"]
    for i in range(battalions):
        lines.append(f"  {unit} = {{ x = {i // 4} y = {i % 4} }}")
    for i in range(guns):
        lines.append(f"  artillery_brigade = {{ x = 4 y = {i} }}")
    lines.extend([" }", f" priority = {priority}", "}", ""])
    return "\n".join(lines)

oob.write_text(
    "# Large formations: 16+3 marines (41w), 16+4 KNIL (44w), 12+2 reserve (30w).\n"
    + template("Batavische Mariniers", "marine", 16, 3, 2)
    + template("KNIL-Infanterie", "infantry", 16, 4, 1)
    + template("Koloniale Landstorm", "infantry", 12, 2, 0)
    + "\n" + units,
    encoding="utf-8",
)
history = root / "history/countries/A01 - Placeholder.txt"
text = history.read_text(encoding="utf-8-sig")
if "gw_artillery = 1" not in text:
    text = text.replace("\tinfantry_weapons = 1", "\tinfantry_weapons = 1\n\tgw_artillery = 1", 1)
history.write_text(text, encoding="utf-8")
print("Updated three Dutch templates and starting artillery technology.")
