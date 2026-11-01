"""Check actual building gates, starting prerequisites and train stockpiles."""
import re
import json
from apply_major_research import BEGIN as MAJOR_BEGIN, END as MAJOR_END, FORBIDDEN
from fix_1893_start import ROOT, GAME, BLOCKED, BASE, BEGIN, END, technology_data, repair_country_start
from integrate_great_war_research import blocks, clean, read

tech = technology_data()
buildings_source = read(ROOT / 'common/buildings/00_buildings.txt')
assert not (ROOT / 'common/buildings/00_buildings.txt').read_bytes().startswith(b'\xef\xbb\xbf'), 'Building database must be UTF-8 without BOM'
assert '\ufeff' not in buildings_source, 'Interior BOM prevents the engine from loading all building definitions'
buildings_text = clean(buildings_source)
buildings = {k: buildings_text[o+1:e-1] for k, s, o, e in blocks(buildings_text, 1)}
assert {'supply_node', 'rail_way', 'infrastructure', 'naval_base', 'arms_factory', 'industrial_complex'} <= set(buildings)
for key in BLOCKED:
    body = buildings[key]
    assert re.search(r'\bis_buildable\s*=\s*no\b', body), key
    assert re.search(r'\bdlc_allowed\s*=\s*\{\s*always\s*=\s*no\s*\}', body), key
    assert 'missing_tech_loc' not in body, key

registered = set()
for p in (ROOT / 'common/country_tags').glob('*.txt'):
    tags = re.findall(r'^\s*([A-Z0-9]{3})\s*=', clean(read(p)), re.M)
    assert not registered.intersection(tags), ('Duplicate country tags', p)
    registered.update(tags)
registered.discard('ZZZ')
game_tags = {tag for p in (GAME / 'common/country_tags').glob('*.txt')
             for tag in re.findall(r'^\s*([A-Z0-9]{3})\s*=', clean(read(p)), re.M)}
profiles = json.loads(read(ROOT / 'tools/major_research_profiles.json'))
checked = set()
for p in (ROOT / 'history/countries').glob('*.txt'):
    tag = p.name.split(' ', 1)[0]
    if tag == 'ZZZ':
        continue
    assert tag in registered | game_tags and tag not in checked, ('Unregistered or duplicate history', tag)
    original = read(p)
    text = clean(original)
    assert original.count(BEGIN) == original.count(END) == 1, tag
    if tag not in profiles:
        repaired, _ = repair_country_start(original, tag, tech)
        assert repaired == original, (tag, 'Shared baseline is not idempotent')
    grants = set()
    # All DLC alternatives must refer to real technologies; baseline must be
    # unconditional and available before the scenario date.
    for key, s, o, e in blocks(text):
        if key == 'set_technology':
            grants.update(re.findall(r'\b(\w+)\s*=\s*1\b', text[o+1:e-1]))
    assert set(BASE) <= grants, (tag, grants)
    for key in grants:
        assert key in tech, (tag, key)
        m = re.search(r'\bstart_year\s*=\s*(\d+)', tech[key])
        assert not m or int(m[1]) <= 1893, (tag, key, m[1])
        for name, s, o, e in blocks(tech[key], 1):
            if name == 'dependencies':
                deps = set(re.findall(r'\b(\w+)\s*=', tech[key][o+1:e-1]))
                assert deps <= grants, (tag, key, deps - grants)
    trains = []
    for key, s, o, e in blocks(text):
        if key == 'add_equipment_to_stockpile' and 'train_equipment_1' in text[o+1:e-1]:
            trains.append(text[o+1:e-1])
    assert len(trains) == 1 and re.search(r'\bamount\s*=\s*15\b', trains[0]), tag
    assert re.search(r'\bset_research_slots\s*=\s*[1-9]', text), tag
    checked.add(tag)
for key in BASE:
    assert key in tech
assert 'train_equipment_1' in tech['basic_train']
assert registered <= checked, ('Missing country histories', registered - checked)
bookmark = clean(read(ROOT / 'common/bookmarks/the_gathering_storm.txt'))
featured = {key.strip('"') for key, s, o, e in blocks(bookmark, 2)
            if re.fullmatch(r'"A\d\d"', key) and not re.search(r'\bminor\s*=\s*yes', bookmark[o+1:e-1])}
assert set(profiles) <= featured, ('Profile country missing from featured list', set(profiles) - featured)
for tag, profile in profiles.items():
    original = read(next((ROOT / 'history/countries').glob(f'{tag} - *.txt')))
    assert original.count(MAJOR_BEGIN) == original.count(MAJOR_END) == 1, tag
    text = clean(original)
    grants = set()
    for level in range(10):
        for key, s, o, e in blocks(text, level):
            if key == 'set_technology':
                grants.update(re.findall(r'\b(\w+)\s*=\s*1\b', text[o+1:e-1]))
    assert not (grants & FORBIDDEN), (tag, grants & FORBIDDEN)
    for group in ('technologies', 'naval_mtg', 'naval_legacy'):
        assert set(profile[group]) <= grants, (tag, group)
    for key in grants:
        assert key in tech, (tag, key)
        m = re.search(r'\bstart_year\s*=\s*(\d+)', tech[key])
        assert not m or int(m[1]) <= 1893, (tag, key)
    assert not {'narrow_gauge_railway', 'standard_gauge_railway'} <= grants, tag
    assert not {'concentrated_industry', 'dispersed_industry'} <= grants, tag
    profile_text = original.split(MAJOR_BEGIN)[1].split(MAJOR_END)[0]
    assert 'has_dlc = "Man the Guns"' in profile_text and 'else = {' in profile_text, tag
assert len({tuple(sorted(p['technologies'])) for p in profiles.values()}) == 6
print(f'PASS: {len(checked)} country histories, research prerequisites, 15 trains each, {len(BLOCKED)} blocked buildings.')
print('PASS: six distinct major profiles, both naval DLC branches, no future or forbidden starting grants.')
