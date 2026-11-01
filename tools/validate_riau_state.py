"""Verify province ownership, ports, geography and split population totals."""
import json
import re
from integrate_great_war_research import ROOT, read, blocks

manifest = json.loads(read(ROOT / 'tools/riau_state_manifest.json'))
states = {}
province_states = {}
for p in (ROOT / 'history/states').glob('*.txt'):
    text = read(p)
    blocks(text)
    state = int(re.search(r'\bid\s*=\s*(\d+)', text)[1])
    assert state not in states, state
    states[state] = text
    for n in re.findall(r'\d+', re.search(r'\bprovinces\s*=\s*\{([^}]+)\}', text)[1]):
        province = int(n)
        assert province not in province_states, province
        province_states[province] = state
assert {p for p, s in province_states.items() if s == 1086} == {13298, 12113}
assert re.search(r'\bowner\s*=\s*A01', states[1086])
for province in (13298, 12113):
    assert re.search(str(province) + r'\s*=\s*\{\s*naval_base\s*=\s*1\s*\}', states[1086])
    regions = []
    for p in (ROOT / 'map/strategicregions').glob('*.txt'):
        text = read(p)
        listing = re.search(r'\bprovinces\s*=\s*\{([^}]+)\}', text)
        if listing and re.search(r'\b' + str(province) + r'\b', listing[1]):
            regions.append(int(re.search(r'\bid\s*=\s*(\d+)', text)[1]))
    assert regions == [187], (province, regions)
population = lambda text: int(re.search(r'\bmanpower\s*=\s*(\d+)', text)[1])
assert sum(r['population_before'] for r in manifest['sources']) == sum(population(states[r['state']]) for r in manifest['sources']) + population(states[1086])
for lang in ('russian', 'english'):
    assert 'STATE_1086:0' in read(ROOT / f'localisation/{lang}/1896_main_l_{lang}.yml')
assert not re.search(r'\bindustrial_complex\s*=', states[1086])
print('PASS: Riau 1086; two unique provinces, two preserved ports, one strategic region, population conserved.')
