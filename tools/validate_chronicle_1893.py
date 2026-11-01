"""Static chronicle checks, including a daily scheduling simulation."""
from pathlib import Path
from datetime import datetime, timedelta
import json, re
R = Path(__file__).resolve().parents[1]
rows = json.loads((R/'tools/chronicle_1893_manifest.json').read_text(encoding='utf-8'))
assert len(rows) == 36
events = (R/'events/chronicle_1893.txt').read_text(encoding='utf-8')
loc = (R/'localisation/russian/chronicle_1893_l_russian.yml').read_text(encoding='utf-8-sig')
keys = set(re.findall(r'^\s+([\w.]+):0', loc, re.M))
ids = re.findall(r'\bid = (ch93\.\d+)', events)
definitions = re.findall(r'^country_event = \{\s*id = (ch93\.\d+)', events, re.M)
assert len(definitions) == len(set(definitions)) == 72
assert set(ids) <= set(definitions)
assert set(re.findall(r'(?:title|text|name) = (ch93\.[\w.]+)',events)) <= keys
for folder in ('events', 'common/scripted_effects', 'common/on_actions', 'common/ideas'):
    for p in (R/folder).glob('*chronicle_1893.txt'):
        s = re.sub(r'"[^"\n]*"|#[^\n]*', '', p.read_text(encoding='utf-8-sig'))
        depth = 0
        for c in s:
            depth += (c == '{') - (c == '}')
            assert depth >= 0, p
        assert depth == 0, p
for start in (datetime(1893,1,1), datetime(1893,7,1)):
    day, seen, fired = start, set(), []
    while day.year == 1893:
        for row in rows:
            due = datetime.strptime(row['date'], '%d.%m.%Y')
            if day >= due and row['id'] not in seen:
                seen.add(row['id']); fired.append((row['id'], day))
        day += timedelta(days=1)
    assert len(fired) == 36
    if start.month == 1:
        assert all(day == datetime.strptime(rows[n-1]['date'], '%d.%m.%Y') for n,day in fired)
assert (R/'localisation/russian/chronicle_1893_l_russian.yml').read_bytes().startswith(b'\xef\xbb\xbf')
assert 'date > 1893.12.31 has_completed_focus' in (R/'common/scripted_effects/borneo_war_effects.txt').read_text()
print('PASS: 36 dates, 72 unique events, localization, balanced blocks, once-only scheduling and legacy war guard. No engine playthrough performed.')
