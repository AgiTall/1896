from pathlib import Path
import re
from add_canon_countries import parse, value

R = Path('..')
loc = {}
for p in (R / 'localisation' / 'russian').glob('*.yml'):
    for match in re.finditer(r'^\s*(\w+):(?:\d+)?\s*"(.*)"', p.read_text(encoding='utf-8-sig'), re.M):
        loc[match.group(1)] = match.group(2)

p1 = R / 'common/national_focus/a01_focus.txt'
tree1 = parse(p1.read_text(encoding='utf-8-sig'))
focuses1 = [f for k, o, f in value(tree1, 'focus_tree') if k == 'focus']

print(f"Total A01 focuses: {len(focuses1)}")
for f in sorted(focuses1, key=lambda f: (int(value(f, 'y')), int(value(f, 'x')))):
    fid = value(f, 'id')
    x = int(value(f, 'x'))
    y = int(value(f, 'y'))
    if y <= 6:
        ru = loc.get(fid, fid)
        prereqs = [v for k, o, n in f if k == 'prerequisite' for k2, o2, v in n if k2 == 'focus']
        print(f"y={y:2d} x={x:3d} {fid:<32} {ru:<35} prereqs={prereqs}")
