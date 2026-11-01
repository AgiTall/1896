"""Scenario-specific integration repairs after the lossless subsystem import."""
from pathlib import Path
import json
import re
import shutil
from integrate_great_war_research import ROOT, BACKUP, blocks, read, backup

SOURCE = Path('D:/SteamLibrary/steamapps/workshop/content/394360/3365515312')
manifest_path = ROOT / 'tools/great_war_research_manifest.json'
manifest = json.loads(read(manifest_path))
changed = []

def write(p, text):
    backup(p)
    p.write_text(text, encoding='utf-8')
    changed.append(p.relative_to(ROOT).as_posix())

# Production restrictions belong to TGWR's French/Belgian/Luxembourg story,
# not this world. They are the only orphan idea references in the subsystem.
for p in (ROOT / 'common/units/equipment').glob('*.txt'):
    text = read(p)
    new = text
    for key,s,o,e in reversed(blocks(text, 2)):
        if key == 'can_be_produced' and 'idea_army_restrictions' in text[s:e]:
            new = new[:s] + new[e:]
    if new != text:
        write(p, new)

tech = {}
for p in (ROOT / 'common/technologies').glob('*.txt'):
    text = read(p)
    for key,s,o,e in blocks(text, 1):
        tech[key] = dict(file=p, body=text[s:e], year=int(re.search(r'start_year\s*=\s*(\d+)', text[s:e])[1]) if re.search(r'start_year\s*=\s*(\d+)', text[s:e]) else 1893)

# First-level support must not hide a later prerequisite penalty.
prerequisites = {k:set() for k in tech}
for key,rec in tech.items():
    for parent in tech:
        if re.search(r'leads_to_tech\s*=\s*' + re.escape(key) + r'\b', tech[parent]['body']):
            prerequisites[key].add(parent)
    for name,s,o,e in blocks(rec['body'], 1):
        if name == 'dependencies':
            prerequisites[key] |= set(re.findall(r'\b(\w+)\s*=', rec['body'][o+1:e-1])) & set(tech)
first_designs = ('tech_signal_company', 'scout_plane', 'basic_armored_car', 'basic_armored_car_chassis',
                 'basic_light_tank', 'basic_light_tank_chassis', 'basic_heavy_tank', 'basic_heavy_tank_chassis',
                 'basic_medium_tank', 'basic_medium_tank_chassis', 'engine_tech_1', 'armor_tech_1')
for key in first_designs:
    if key not in tech:
        continue
    pending = [key]
    visited = set()
    while pending:
        k = pending.pop()
        if k in visited:
            continue
        visited.add(k)
        tech[k]['year'] = min(tech[k]['year'], 1893)
        pending.extend(prerequisites[k])

# Remove reciprocal vanilla exchange paths from the optional legacy navy,
# preserving a forward chronology rather than circular cruiser exchanges.
for key,rec in tech.items():
    if rec['file'].name != 'naval.txt':
        continue
    body = rec['body']
    for name,s,o,e in reversed(blocks(body, 1)):
        if name == 'path':
            m = re.search(r'leads_to_tech\s*=\s*(\w+)', body[s:e])
            if m and m[1] in tech:
                target = m[1]
                if tech[target]['year'] < rec['year'] or (tech[target]['year'] == rec['year'] and
                        ('cruiser' in key and 'cruiser' in target) and key != target and
                        (('light' in key) != ('light' in target))):
                    body = body[:s] + body[e:]
    rec['body'] = body
# The inherited battlecruiser exchange loop is optional, not a prerequisite.
for key in ('improved_battleship',):
    rec = tech[key]
    rec['body'] = re.sub(r'path\s*=\s*\{[^}]*leads_to_tech\s*=\s*basic_battlecruiser[^}]*\}', '', rec['body'])

# Propagate prerequisite chronology to dependent nodes, not to independent
# branches. Hidden placeholders use their parent's date as well.
edges = {k:set() for k in tech}
for key,rec in tech.items():
    edges[key] |= set(re.findall(r'leads_to_tech\s*=\s*(\w+)', rec['body'])) & set(tech)
    for name,s,o,e in blocks(rec['body'], 1):
        if name == 'sub_technologies':
            edges[key] |= set(re.findall(r'\b\w+\b', rec['body'][o+1:e-1])) & set(tech)
    for parent in prerequisites[key]:
        edges[parent].add(key)
for _ in range(len(tech)):
    modified = False
    for parent,children in edges.items():
        for child in children:
            if tech[child]['year'] < tech[parent]['year']:
                tech[child]['year'] = tech[parent]['year']
                modified = True
    if not modified:
        break
else:
    raise AssertionError('Chronology did not converge')
for p in (ROOT / 'common/technologies').glob('*.txt'):
    text = read(p)
    for key,s,o,e in reversed(blocks(text, 1)):
        body = tech[key]['body']
        if re.search(r'start_year\s*=', body):
            body = re.sub(r'start_year\s*=\s*\d+', 'start_year = ' + str(tech[key]['year']), body, count=1)
        else:
            at = body.index('{')+1
            body = body[:at] + '\n start_year = ' + str(tech[key]['year']) + body[at:]
        text = text[:s] + body + text[e:]
    write(p, text)

# Printed headers are separate from the actual ahead-of-time calculation.
# Initial aircraft and chassis rows now correspond to the 1893 prototypes.
gui_path = ROOT / 'interface/countrytechtreeview.gui'
gui = read(gui_path)
for key,s,o,e in reversed(blocks(gui, 2)):
    body = gui[s:e]
    if re.search(r'name\s*=\s*"(?:air_techs_folder|nsb_armour_folder)"', body):
        values = [int(v) for v in re.findall(r'\btext\s*=\s*"(\d{4})"', body)]
        if values:
            earliest = min(values)
            if earliest > 1893:
                body = re.sub(r'(\btext\s*=\s*")' + str(earliest) + r'(")', r'\g<1>1893\2', body)
        gui = gui[:s] + body + gui[e:]
write(gui_path, gui)

# Tactic pictures are also addressed by filename directly by the engine.
for p in (SOURCE / 'gfx/interface/landcombat/tactics').glob('*'):
    if p.is_file():
        target = ROOT / p.relative_to(SOURCE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        changed.append(target.relative_to(ROOT).as_posix())

# Repair a missing source texture with the matching existing submarine art.
gfx = ROOT / 'interface/Technologies.gfx'
text = read(gfx)
missing = 'gfx/interface/technologies/ship_hull_coastal_submarine.dds'
if missing in text:
    candidates = sorted((ROOT / 'gfx/interface/technologies').glob('*submarine*.dds'))
    assert candidates
    replacement = next((p for p in candidates if 'coastal' in p.name), candidates[0]).relative_to(ROOT).as_posix()
    write(gfx, text.replace(missing, replacement))

# Both descriptor copies must advertise the same replace_path declarations.
launcher = ROOT.parent / '1896.mod'
if launcher.exists():
    saved = BACKUP / 'launcher_1896.mod'
    if not saved.exists():
        shutil.copy2(launcher, saved)
    text = read(launcher)
    for declaration in re.findall(r'^replace_path=.*$', read(ROOT / 'descriptor.mod'), re.M):
        if declaration not in text:
            text += '\n' + declaration
    launcher.write_text(text.strip()+'\n', encoding='utf-8')

manifest['files'] = sorted(set(manifest['files']) | set(changed))
manifest['technology_dates'] = {k:v['year'] for k,v in sorted(tech.items())}
manifest['first_designs'] = list(first_designs)
manifest['finishing_repairs'] = ['scenario production restrictions removed', 'support prerequisites <=1893',
    'monotonic research dates', 'legacy naval exchange cycles removed', 'tactic pictures included', 'launcher descriptor synchronized']
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Finished chronology, production restrictions, graphics and launcher registration.')
