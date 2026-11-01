import json
from pathlib import Path
from inspect_coords import all_coords, wtp_map, conf_map, econ_map, mil_map, coup_map, root_postwar_map

R = Path(__file__).resolve().parent

# 1. Update a10w_focuses.json
a10w_path = R / 'a10w_focuses.json'
a10w = json.loads(a10w_path.read_text(encoding='utf-8'))
for f in a10w:
    if f['id'] in wtp_map:
        f['x'], f['y'] = wtp_map[f['id']]
a10w_path.write_text(json.dumps(a10w, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print("Updated a10w_focuses.json")

# 2. Update a10m_focuses.json
a10m_path = R / 'a10m_focuses.json'
a10m = json.loads(a10m_path.read_text(encoding='utf-8'))
for f in a10m:
    if f['id'] in coup_map:
        f['x'], f['y'] = coup_map[f['id']]
a10m_path.write_text(json.dumps(a10m, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print("Updated a10m_focuses.json")

# Also update A10M_build_content.py coordinate definitions so it stays consistent
a10m_build_path = R / 'A10M_build_content.py'
a10m_text = a10m_build_path.read_text(encoding='utf-8')
for fid, (nx, ny) in coup_map.items():
    key = fid.replace('A10M_', '')
    # replace 'key, ..., old_x, old_y'
    # we can re-generate the focus(...) calls or replace x, y
    pass

# 3. Update a10d_focuses.json
a10d_path = R / 'a10d_focuses.json'
a10d = json.loads(a10d_path.read_text(encoding='utf-8'))
for f in a10d:
    if f['id'] in econ_map:
        f['x'], f['y'] = econ_map[f['id']]
    elif f['id'] in mil_map:
        f['x'], f['y'] = mil_map[f['id']]
a10d_path.write_text(json.dumps(a10d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print("Updated a10d_focuses.json")

# 4. Update build_philippines_rework.py
rework_path = R / 'build_philippines_rework.py'
rework_text = rework_path.read_text(encoding='utf-8')

# The focuses defined in build_philippines_rework.py are F (Congress, Confederation, Postwar, strike_japan)
for fid, (nx, ny) in {**conf_map, **root_postwar_map, 'A10_strike_japan': mil_map['A10_strike_japan']}.items():
    # Replace in rework_text: focus('fid', ..., old_x, old_y, ...)
    import re
    pattern = rf"(focus\('{re.escape(fid)}'[^,\n]*,[^,\n]*,)\s*-?\d+\s*,\s*-?\d+\s*,"
    m = re.search(pattern, rework_text)
    if m:
        rework_text = re.sub(pattern, rf"\g<1>{nx},{ny},", rework_text, count=1)
    else:
        print(f"Warning: pattern not matched for {fid}")

rework_path.write_text(rework_text, encoding='utf-8')
print("Updated build_philippines_rework.py")
