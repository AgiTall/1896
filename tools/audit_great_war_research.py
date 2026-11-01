"""Reference and era audit. Reports integration defects without hiding them."""
from pathlib import Path
import json
import re
from integrate_great_war_research import ROOT, blocks, clean, read, tokens

GAME = Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
errors = []
warnings = []

def definitions(folder, level=1):
    result = {}
    for p in (ROOT / folder).rglob('*.txt'):
        if folder == 'common/units/equipment' and any(x in p.parts for x in ('modules', 'upgrades')):
            continue
        text = read(p)
        if folder == 'common/units/equipment' and not re.search(r'\bequipments\s*=', clean(text)):
            continue
        try:
            for key,s,o,e in blocks(text, level):
                if key == 'limit':
                    continue
                if key in result:
                    errors.append(f'Duplicate {folder}: {key} ({p.name})')
                result[key] = (p, text[s:e])
        except ValueError as exc:
            errors.append(f'{p}: {exc}')
    return result

tech = definitions('common/technologies')
equip = definitions('common/units/equipment')
modules = definitions('common/units/equipment/modules')
for key,(p,body) in modules.items():
    for ref in re.findall(r'\bparent\s*=\s*(\w+)', clean(body)):
        if ref not in modules:
            errors.append(f'{key}: missing module parent {ref}')
units = {}
for p in (ROOT / 'common/units').glob('*.txt'):
    text = read(p)
    for key,s,o,e in blocks(text, 1):
        units[key] = (p, text[s:e])
tactics = definitions('common', 0) if False else {k for k,s,o,e in blocks(read(ROOT / 'common/combat_tactics.txt'))}
edges = {k: set() for k in tech}
dates = {}
for key,(p,body) in tech.items():
    body = clean(body)
    m = re.search(r'\bstart_year\s*=\s*(\d+)', body)
    dates[key] = int(m[1]) if m else 1893
    for target in re.findall(r'\bleads_to_tech\s*=\s*(\w+)', body):
        if target not in tech:
            errors.append(f'{key}: missing tech path {target}')
        else:
            edges[key].add(target)
    for label, pool in [('enable_equipments', equip), ('enable_subunits', units), ('enable_equipment_modules', modules), ('sub_technologies', tech)]:
        for name,s,o,e in blocks(body, 1):
            if name != label:
                continue
            listing = body[o+1:e-1]
            for _,ss,oo,ee in reversed(blocks(listing)):
                listing = listing[:ss] + listing[ee:]
            for token in tokens(listing):
                ref = token[0]
                if ref not in pool:
                    errors.append(f'{key}: missing {label} {ref}')
                elif label == 'sub_technologies':
                    edges[key].add(ref)
    for dep,s,o,e in blocks(body, 1):
        if dep == 'dependencies':
            for ref in re.findall(r'\b(\w+)\s*=', body[o+1:e-1]):
                if ref not in tech:
                    errors.append(f'{key}: missing dependency {ref}')
                else:
                    edges[ref].add(key)
    for ref in re.findall(r'\benable_tactic\s*=\s*(\w+)', body):
        if ref not in tactics:
            errors.append(f'{key}: missing tactic {ref}')

for key,(p,body) in equip.items():
    for ref in re.findall(r'\b(?:archetype|parent)\s*=\s*(\w+)', clean(body)):
        if ref not in equip:
            errors.append(f'{key}: missing equipment parent {ref}')
for key,(p,body) in units.items():
    for match in re.finditer(r'\bneed\s*=\s*\{([^}]+)\}', clean(body)):
        for ref in re.findall(r'\b(\w+)\s*=', match[1]):
            if ref not in equip:
                errors.append(f'{key}: missing needed equipment {ref}')

incoming = set().union(*edges.values())
roots = set(tech) - incoming
for key in roots:
    if dates[key] > 1893 and 'is_special_project_tech = yes' not in clean(tech[key][1]):
        errors.append(f'First research has ahead-of-time penalty: {key} ({dates[key]})')
for parent,children in edges.items():
    for child in children:
        if dates[child] < dates[parent]:
            warnings.append(f'Date inversion: {parent} ({dates[parent]}) -> {child} ({dates[child]})')

visited = set()
def visit(k, stack):
    if k in stack:
        warnings.append('Alternative research paths form a cycle: ' + ' -> '.join(stack + [k]))
        return
    if k in visited:
        return
    for child in edges[k]:
        visit(child, stack + [k])
    visited.add(k)
for key in tech:
    visit(key, [])

for p in (ROOT / 'history/countries').glob('*.txt'):
    text = read(p)
    for key,s,o,e in blocks(text, 1) + blocks(text, 2) + blocks(text, 0):
        if key == 'set_technology':
            for ref in re.findall(r'\b(\w+)\s*=', clean(text[o+1:e-1])):
                if ref not in tech:
                    errors.append(f'{p.name}: missing granted technology {ref}')
    for ref in re.findall(r'\btype\s*=\s*(\w+)', clean(text)):
        if ref not in equip:
            errors.append(f'{p.name}: missing variant equipment {ref}')

for p in (ROOT / 'history/units').glob('*.txt'):
    text = read(p)
    for level in (1, 2, 3):
        for key,s,o,e in blocks(text, level):
            if key in ('regiments', 'support'):
                body = clean(text[o+1:e-1])
                for ref in re.findall(r'\b(\w+)\s*=\s*\{\s*x\s*=', body):
                    if ref not in units:
                        errors.append(f'{p.name}: missing template unit {ref}')
    for ref in re.findall(r'\btype\s*=\s*(\w+)', clean(text)):
        if ref not in equip and ref not in ('army', 'navy'):
            errors.append(f'{p.name}: missing OOB equipment {ref}')

# Check visual assets against the installed game as fallback.
for p in (ROOT / 'interface').rglob('*'):
    if p.suffix in ('.gfx', '.gui'):
        text = clean(read(p))
        for path in re.findall(r'\btexturefile\s*=\s*"([^"]+)"', text, re.I):
            path = path.replace('\\', '/')
            if not (ROOT / path).exists() and not (GAME / path).exists():
                warnings.append(f'{p.name}: missing texture {path}')

manifest = json.loads(read(ROOT / 'tools/great_war_research_manifest.json'))
for path in manifest['files']:
    p = ROOT / path
    if p.suffix in ('.txt', '.gui', '.gfx'):
        try:
            blocks(read(p))
        except ValueError as exc:
            errors.append(f'{path}: {exc}')
for lang in ('russian', 'english'):
    p = ROOT / f'localisation/{lang}/replace/zzzzzzzzzz_great_war_research_l_{lang}.yml'
    assert p.read_bytes().startswith(b'\xef\xbb\xbf')
    loc = read(p)
    for key in tech:
        if not re.search(r'^\s*' + re.escape(key) + r':', loc, re.M):
            # Vanilla fallbacks are supplied by the installed game's localisation.
            warnings.append(f'{lang}: inherited/missing technology label {key}')
for key in manifest.get('first_designs', []):
    if key in dates and dates[key] > 1893:
        errors.append(f'Initial prototype research has ahead-of-time penalty: {key} ({dates[key]})')
for key in ('howitzer', 'howitzer_brigade', 'field_gun', 'field_gun_brigade', 'machine_gun_company'):
    assert key in units, key
for key in ('howitzer_equipment_0', 'field_gun_equipment_0'):
    assert key in equip, key
assert dates['basic_howitzer'] <= 1893
assert dates['basic_field_gun'] <= 1893
assert dates['tech_support'] <= 1893
assert dates['tech_engineers'] <= 1893
assert 'date = 1893.1.1.12' in read(ROOT / 'common/bookmarks/the_gathering_storm.txt')
imported_names = {Path(p).name for p in manifest['files']}
existing_warnings = [w for w in warnings if ': missing texture ' in w and w.split(':',1)[0] not in imported_names]
warnings = [w for w in warnings if w not in existing_warnings]
report = dict(technologies=len(tech), equipment=len(equip), modules=len(modules), units=len(units),
              tactics=len(tactics)-1, first_research=len(roots), errors=sorted(set(errors)),
              warnings=sorted(set(warnings)), existing_asset_warnings=sorted(set(existing_warnings)))
(ROOT / 'tools/great_war_research_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('errors','warnings','existing_asset_warnings')}, ensure_ascii=False))
print('ERRORS',len(report['errors']))
for message in report['errors'][:100]:
    print(message)
print('WARNINGS',len(report['warnings']))
for message in report['warnings'][:35]:
    print(message)
print('Existing asset warnings outside this subsystem:',len(report['existing_asset_warnings']))
raise SystemExit(bool(errors))
