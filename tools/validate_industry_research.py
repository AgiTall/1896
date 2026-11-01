"""Check the research graph, compatibility IDs, dates, localisation and GUI scope."""
from pathlib import Path
import json
import re
import argparse
from build_industry_research import block_end

ROOT = Path(__file__).resolve().parents[1]
if (ROOT / 'tools/great_war_research_manifest.json').exists():
    import subprocess
    import sys
    raise SystemExit(subprocess.call([sys.executable, str(ROOT / 'tools/audit_great_war_research.py')]))
parser = argparse.ArgumentParser()
parser.add_argument('--game', type=Path, required=True)
args = parser.parse_args()
text = (ROOT / 'common/technologies/industry.txt').read_text(encoding='utf-8-sig')
manifest = json.loads((ROOT / 'tools/industry_research_manifest.json').read_text(encoding='utf-8'))
blocks = {}
for m in re.finditer(r'^\t([a-z_0-9]+) = \{', text, re.M):
    assert m[1] not in blocks, m[1]
    blocks[m[1]] = text[m.start():block_end(text, text.index('{', m.start()))]
assert set(blocks) == set(manifest)
assert set(blocks) == set(re.findall(r'^\t([a-z_0-9]+) = \{', (args.game / 'common/technologies/industry.txt').read_text(encoding='utf-8-sig'), re.M))
edges = {}
for key, body in blocks.items():
    year = int(re.search(r'start_year\s*=\s*(\d+)', body)[1])
    assert year == manifest[key]['year'], key
    assert 1890 <= year <= 1918
    targets = re.findall(r'leads_to_tech\s*=\s*(\w+)', body)
    edges[key] = targets
    for target in targets:
        assert target in blocks, (key, target)
        assert manifest[target]['year'] >= year, (key, target)
    assert 'name = industry_folder' in body
    for year in re.findall(r'date\s*>\s*"?(\d{4})', body):
        assert int(year) < 1920, (key, year)

def visit(key, stack):
    assert key not in stack, ('cycle', key)
    for target in edges[key]:
        visit(target, stack | {key})

for key in blocks:
    visit(key, set())
for lang in ('russian', 'english'):
    p = ROOT / f'localisation/{lang}/zzzzzzzzzz_research_industry_l_{lang}.yml'
    assert p.read_bytes().startswith(b'\xef\xbb\xbf')
    loc = p.read_text(encoding='utf-8-sig')
    for key in blocks:
        assert re.search(r'^ ' + key + r':0 ".+"$', loc, re.M), key
        assert re.search(r'^ ' + key + r'_desc:0 ".+"$', loc, re.M), key

def industry_span(gui):
    pos = gui.index('name = "industry_folder"')
    start = gui.rfind('containerWindowType', 0, pos)
    end = block_end(gui, gui.index('{', start))
    return gui[:start], gui[start:end], gui[end:]

old = industry_span((args.game / 'interface/countrytechtreeview.gui').read_text(encoding='utf-8-sig'))
new = industry_span((ROOT / 'interface/countrytechtreeview.gui').read_text(encoding='utf-8-sig'))
assert old[0] == new[0] and old[2] == new[2], 'Other tabs were modified'
active = re.sub(r'#[^\n]*', '', new[1])
assert not re.search(r'text\s*=\s*"19[3-4]\d"', active)
assert 'XOR = {\n\t\t\tdispersed_industry' in blocks['concentrated_industry']
assert 'XOR = {\n\t\t\tconcentrated_industry' in blocks['dispersed_industry']
assert len([v for v in manifest.values() if v['year'] <= 1893]) >= 5
print(f'PASS: {len(blocks)} IDs, dates, acyclic graph, industry choices, RU/EN and isolated GUI changes.')
