"""Repairs established by the first actual HOI4 1.19.3 debug load."""
from pathlib import Path
import json
import re
import shutil
from integrate_great_war_research import ROOT, BACKUP, blocks, read, backup

SOURCE = Path('D:/SteamLibrary/steamapps/workshop/content/394360/3365515312')
GAME = Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
mp = ROOT / 'tools/great_war_research_manifest.json'
manifest = json.loads(read(mp))
changed = set()

def write(rel, text):
    p = ROOT / rel
    backup(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8-sig' if p.suffix == '.yml' else 'utf-8')
    changed.add(p.relative_to(ROOT).as_posix())

def copy(p):
    target = ROOT / p.relative_to(SOURCE)
    backup(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, target)
    changed.add(target.relative_to(ROOT).as_posix())

# replace_path is folder-specific: every populated child folder needs its own
# declaration to keep vanilla nuclear/rocket projects and equipment out.
paths = ['common/units/equipment', 'common/units/equipment/modules',
         'common/special_projects/projects', 'common/special_projects/prototype_rewards',
         'common/military_industrial_organization/organizations', 'common/ai_equipment', 'common/ai_templates']
for rel in ('descriptor.mod',):
    text = read(ROOT / rel)
    for path in paths:
        line = f'replace_path="{path}"'
        if line not in text:
            text += '\n' + line
    write(rel, text.strip()+'\n')
launcher = ROOT.parent / '1896.mod'
if launcher.exists():
    text = read(launcher)
    for path in paths:
        line = f'replace_path="{path}"'
        if line not in text:
            text += '\n' + line
    launcher.write_text(text.strip()+'\n', encoding='utf-8')
copy(SOURCE / 'common/script_enums.txt')
copy(SOURCE / 'common/military_industrial_organization/organizations/00_generic_organization.txt')
write('common/scripted_triggers/1893_manufacturer_compatibility.txt', 'is_russian_tag = { original_tag = RUS }\n')
for name in ('generic_armored_cars.txt', 'generic_naval.txt', 'generic_tank.txt'):
    copy(SOURCE / 'common/ai_equipment' / name)
copy(SOURCE / 'common/ai_templates/generic.txt')
# The game initializes scientist skill tables for this specialization even
# when no nuclear projects exist. Register its empty compatibility category.
p = ROOT / 'common/special_projects/specialization/specializations.txt'
text = read(p)
if not any(k == 'specialization_nuclear' for k,s,o,e in blocks(text)):
    original = read(GAME / 'common/special_projects/specialization/specializations.txt')
    nuclear = next(original[s:e] for k,s,o,e in blocks(original) if k == 'specialization_nuclear')
    write(p.relative_to(ROOT), text + '\n' + nuclear + '\n')

# Parent definitions must precede children; missing module parents were not
# caught by the initial technology-only closure.
for rel, wrapper in [('common/units/equipment/zz_1893_legacy_compatibility.txt', 'equipments'),
                     ('common/units/equipment/modules/zz_1893_legacy_compatibility.txt', 'equipment_modules')]:
    p = ROOT / rel
    text = read(p)
    defs = {k:text[s:e] for k,s,o,e in blocks(text, 1)}
    if wrapper == 'equipment_modules':
        existing = set()
        for q in (ROOT / 'common/units/equipment/modules').glob('*.txt'):
            existing.update(k for k,s,o,e in blocks(read(q), 1))
        game_defs = {}
        for q in (GAME / 'common/units/equipment/modules').glob('*.txt'):
            qs = read(q)
            game_defs.update({k:qs[s:e] for k,s,o,e in blocks(qs, 1) if k != 'limit'})
        while True:
            parents = {m[1] for body in defs.values() for m in re.finditer(r'\bparent\s*=\s*(\w+)', body)}
            missing = parents - existing - set(defs)
            if not missing:
                break
            for key in missing:
                assert key in game_defs, key
                defs[key] = game_defs[key]
    ordered = []
    done = set()
    def visit(key):
        if key in done:
            return
        done.add(key)
        parent = re.search(r'\bparent\s*=\s*(\w+)', defs[key])
        if parent and parent[1] in defs:
            visit(parent[1])
        ordered.append(defs[key])
    for key in sorted(defs):
        visit(key)
    text = wrapper + ' = {\n' + '\n'.join(ordered) + '\n}\n'
    # TGWR's cruiser archetypes do not have a radar slot to inherit.
    if wrapper == 'equipments':
        # Source archetypes intentionally have fewer slots than vanilla WWII
        # hulls. Legacy aliases inherit those slots and only compatible defaults.
        source_equipment = {}
        for q in (ROOT / 'common/units/equipment').glob('*.txt'):
            if q == p:
                continue
            qs = read(q)
            source_equipment.update({k:qs[s:e] for k,s,o,e in blocks(qs, 1)})
        for k,s,o,e in reversed(blocks(text, 1)):
            body = text[s:e]
            archetype = re.search(r'\barchetype\s*=\s*(\w+)', body)
            if archetype and archetype[1] in source_equipment:
                archetype_body = source_equipment[archetype[1]]
                slot_blocks = [archetype_body[oo+1:ee-1] for kk,ss,oo,ee in blocks(archetype_body, 1) if kk == 'module_slots']
                if slot_blocks:
                    allowed = {kk for kk,ss,oo,ee in blocks(slot_blocks[0])}
                    for kk,ss,oo,ee in reversed(blocks(body, 1)):
                        if kk == 'module_slots':
                            body = body[:ss] + 'module_slots = inherit' + body[ee:]
                        elif kk == 'default_modules':
                            listing = body[oo+1:ee-1]
                            listing = re.sub(r'\b(\w+_slot)\s*=\s*(\w+)', lambda m: m[0] if m[1] in allowed else '', listing)
                            body = body[:oo+1] + listing + body[ee-1:]
            text = text[:s] + body + text[e:]
    write(rel, text)

# Foreign focus exceptions have no equivalent in this world's country trees.
# An unset flag retains their false condition without invalid focus references.
for folder in ('common/technologies', 'common/special_projects'):
    for p in (ROOT / folder).rglob('*.txt'):
        text = read(p)
        text = re.sub(r'\bhas_completed_focus\s*=\s*(?:GER_propose_joint_military_exercises|FRA_ww1_mechanized_effort|FRA_ww1_the_french_miracle|USA_maneuver_divison|GER_finance_rheinmetall)\b',
                      'has_country_flag = research_foreign_focus_exception_unavailable', text)
        write(p.relative_to(ROOT), text)

# Localisation overrides belong in replace/, avoiding duplicate vanilla keys.
for lang in ('russian', 'english'):
    old = ROOT / f'localisation/{lang}/zzzzzzzzzz_great_war_research_l_{lang}.yml'
    newrel = f'localisation/{lang}/replace/zzzzzzzzzz_great_war_research_l_{lang}.yml'
    if old.exists():
        write(newrel, read(old))
        backup(old)
        old.unlink()
        manifest['files'] = [p for p in manifest['files'] if p != old.relative_to(ROOT).as_posix()]
text = read(ROOT / 'interface/1893_combat_dependencies.gfx')
write('interface/1893_combat_dependencies.gfx', text.replace('gfx/texticons/locked.png', 'gfx/texticons/locked.dds'))

# Country-specific hull pictures are part of the source equipment graphic DB.
for p in (SOURCE / 'interface').glob('ww1_*_ships_icons.gfx'):
    copy(p)
    for texture in re.findall(r'\btexturefile\s*=\s*"([^"]+)"', read(p), re.I):
        asset = SOURCE / texture
        if asset.exists():
            copy(asset)

# HQ meshes are optional visuals; absent meshes must not leave broken pools.
for p in (ROOT / 'gfx/interface/equipmentdesigner/graphic_db').glob('*hq*.txt'):
    text = read(p)
    for key,s,o,e in reversed(blocks(text, 2)):
        if key == 'pool' and 'models' in text[s:e]:
            text = text[:s] + text[e:]
    write(p.relative_to(ROOT), text)

# Existing Pacific fleets must use slots and armour categories of WW1 hulls.
equipment_defs = {}
module_defs = {}
for folder,pool in [('common/units/equipment', equipment_defs), ('common/units/equipment/modules', module_defs)]:
    for p in (ROOT / folder).glob('*.txt'):
        text = read(p)
        pool.update({k:text[s:e] for k,s,o,e in blocks(text, 1)})
def hull_slots(key, seen=None):
    seen = set() if seen is None else seen
    if key in seen or key not in equipment_defs:
        return {}
    seen.add(key)
    body = equipment_defs[key]
    result = {}
    for prop in ('archetype', 'parent'):
        m = re.search(r'\b' + prop + r'\s*=\s*(\w+)', body)
        if m:
            result.update(hull_slots(m[1], seen))
    for label,s,o,e in blocks(body, 1):
        if label == 'module_slots':
            listing = body[o+1:e-1]
            for slot,ss,oo,ee in blocks(listing):
                cats = re.search(r'allowed_module_categories\s*=\s*\{([^}]+)\}', listing[ss:ee])
                result[slot] = set(re.findall(r'\b\w+\b', cats[1])) if cats else set()
    return result
for p in (ROOT / 'history/countries').glob('*.txt'):
    text = read(p)
    original = text
    variants = []
    for level in range(5):
        variants.extend(x for x in blocks(text, level) if x[0] == 'create_equipment_variant')
    for label,s,o,e in sorted(variants, key=lambda x:x[1], reverse=True):
        body = text[s:e]
        t = re.search(r'\btype\s*=\s*(\w+)', body)
        if not t or not t[1].startswith('ship_hull'):
            continue
        allowed = hull_slots(t[1])
        for name,ss,oo,ee in reversed(blocks(body, 1)):
            if name != 'modules':
                continue
            listing = body[oo+1:ee-1]
            def adapt(m):
                slot,module = m[1],m[2]
                if slot not in allowed:
                    return ''
                if module == 'ship_armor_cruiser_1':
                    module = 'ship_armor_protected_cruiser_1'
                if module != 'empty':
                    definition = module_defs.get(module, '')
                    cat = re.search(r'\bcategory\s*=\s*(\w+)', definition)
                    assert cat and cat[1] in allowed[slot], (p.name,t[1],slot,module)
                return slot + ' = ' + module
            listing = re.sub(r'\b(\w+)\s*=\s*(\w+)', adapt, listing)
            body = body[:oo+1] + listing + body[ee-1:]
        text = text[:s] + body + text[e:]
    if text != original:
        write(p.relative_to(ROOT), text)

# Grant the technology already embodied in the existing starting forces.
for tag in ('A01', 'A03'):
    p = ROOT / f'history/countries/{tag} - Placeholder.txt'
    text = read(p)
    if tag == 'A03' and 'early_artillery = 1' not in text:
        text = text.replace('infantry_weapons = 1', 'infantry_weapons = 1 early_artillery = 1', 1)
    if 'basic_coal_engine = 1' not in text:
        text += '\nif = { limit = { has_dlc = "Man the Guns" } set_technology = { basic_coal_engine = 1 } }\n'
    write(p.relative_to(ROOT), text)

manifest['files'] = sorted(set(manifest['files']) | changed)
manifest['engine_repairs'] = ['nested replace paths', 'WW1 equipment script enums', 'generic WW1 manufacturers',
    'topological legacy equipment order', 'module parent closure', 'foreign focus exceptions removed',
    'localisation replace folder', 'country hull illustrations', 'unavailable HQ mesh pools removed']
mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Engine integration repairs applied.')
