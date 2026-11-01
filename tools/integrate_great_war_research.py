"""Import the TGWR research/combat subsystem, without its scenario or politics.

Explicit one-time migration. Source files are read-only. Backups stay local.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT / 'tools/backups/great_war_research'
TOKEN = re.compile(r'#[^\n]*|"(?:\\.|[^"\\])*"|[{}=]|[^\s{}=]+')


def tokens(text):
    return [m for m in TOKEN.finditer(text) if not m[0].startswith('#')]


def blocks(text, level=0):
    """Lossless named block spans; ignores braces inside strings/comments."""
    ts = tokens(text)
    depth = 0
    stack = []
    result = []
    for i, t in enumerate(ts):
        if t[0] == '{':
            named = i >= 2 and ts[i-1][0] == '='
            stack.append((ts[i-2][0] if named else None, ts[i-2].start() if named else t.start(), t.start(), depth))
            depth += 1
        elif t[0] == '}':
            if not stack:
                raise ValueError('Unexpected closing brace')
            name, start, opening, d = stack.pop()
            depth -= 1
            if d == level and name:
                result.append((name, start, opening, t.end()))
    if stack:
        raise ValueError('Unclosed brace')
    return sorted(result, key=lambda x: x[1])


def clean(text):
    return re.sub(r'#[^\n]*', '', text)


def read(p):
    return p.read_text(encoding='utf-8-sig')


def year(value):
    y = int(value)
    if y <= 1893:
        return y
    if y <= 1905:
        return 1893
    return max(1894, y - 14)


def redates(text):
    text = re.sub(r'\b(start_year|year)\s*=\s*(\d{4})', lambda m: m[1] + ' = ' + str(year(m[2])), text)
    text = re.sub(r'(\bdate\s*[<>=]+\s*"?)(\d{4})(\.\d+\.\d+)', lambda m: m[1] + str(year(m[2])) + m[3], text)
    return text


def backup(p):
    if p.exists():
        b = BACKUP / p.relative_to(ROOT)
        b.parent.mkdir(parents=True, exist_ok=True)
        if not b.exists():
            shutil.copy2(p, b)


def run(source, game):
    outputs = set()
    hashes = {}
    def write(rel, data, binary=False):
        p = ROOT / rel
        backup(p)
        p.parent.mkdir(parents=True, exist_ok=True)
        if binary:
            p.write_bytes(data)
        else:
            p.write_text(data, encoding='utf-8-sig' if p.suffix == '.yml' else 'utf-8')
        outputs.add(str(p.relative_to(ROOT)).replace('\\', '/'))

    def copy(p):
        rel = p.relative_to(source)
        data = p.read_bytes()
        hashes[rel.as_posix()] = hashlib.sha256(data).hexdigest()
        if p.suffix.lower() in ('.txt', '.gui', '.gfx', '.lua'):
            write(rel, redates(read(p)))
        else:
            write(rel, data, True)

    folders = ['common/technologies', 'common/technology_tags', 'common/units',
               'common/unit_tags', 'common/doctrines', 'common/terrain',
               'common/special_projects', 'common/equipment_groups',
               'interface/doctrines', 'interface/equipmentdesigner']
    for folder in folders:
        for p in sorted((source / folder).rglob('*')):
            if p.is_file():
                # Nation-specific naming is unrelated to combat integration.
                if folder == 'common/units' and any(x.startswith('names') or x == 'codenames_operatives' for x in p.relative_to(source / folder).parts[:-1]):
                    continue
                copy(p)
    copy(source / 'common/combat_tactics.txt')
    copy(source / 'common/script_constants/special_project_constants.txt')

    # Empty vanilla files omitted by TGWR's replace_path; keep them disabled.
    for p in (game / 'common/technologies').glob('*.txt'):
        if not (source / 'common/technologies' / p.name).exists():
            write('common/technologies/' + p.name, '# Replaced by Great War research integration.\n')

    techs = {}
    files = list((ROOT / 'common/technologies').glob('*.txt'))
    incoming = set()
    for p in files:
        text = read(p)
        for key, start, op, end in blocks(text, 1):
            body = text[start:end]
            techs[key] = (p, body)
            incoming.update(re.findall(r'leads_to_tech\s*=\s*(\w+)', clean(body)))
            for sub in re.findall(r'\bsub_technologies\s*=\s*\{([^}]+)\}', clean(body)):
                incoming.update(re.findall(r'\b\w+\b', sub))
            for name, s, o, e in blocks(body, 1):
                if name == 'dependencies':
                    incoming.add(key)
    roots = set(techs) - incoming
    first_support = {'tech_support', 'tech_engineers', 'tech_recon', 'tech_field_hospital',
                     'tech_logistics_company', 'tech_military_police', 'tech_signal_company',
                     'tech_maintenance_company', 'basic_howitzer', 'basic_field_gun'}
    baseline = roots | first_support
    dates = {}
    for p in files:
        text = read(p)
        for key, start, op, end in reversed(blocks(text, 1)):
            body = text[start:end]
            m = re.search(r'\bstart_year\s*=\s*(\d+)', clean(body))
            y = int(m[1]) if m else 1893
            if key in baseline:
                y = min(y, 1893)
            if m:
                body = re.sub(r'\bstart_year\s*=\s*\d+', 'start_year = ' + str(y), body, count=1)
            else:
                pos = body.index('{') + 1
                body = body[:pos] + '\n\t\tstart_year = ' + str(y) + body[pos:]
            dates[key] = y
            text = text[:start] + body + text[end:]
        write(p.relative_to(ROOT), text)

    # Combat parameters only: do not inherit TGWR's dates/diplomacy/country rules.
    lines = ['-- TGWR combat/supply/doctrine settings; scenario stays at 1893.\n']
    for p in (source / 'common/defines').glob('*.lua'):
        source_lines = read(p).splitlines()
        index = 0
        while index < len(source_lines):
            line = source_lines[index]
            index += 1
            code = line.split('--', 1)[0]
            balance = code.count('{') - code.count('}')
            while balance > 0 and index < len(source_lines):
                continuation = source_lines[index]
                index += 1
                line += '\n' + continuation
                code = continuation.split('--', 1)[0]
                balance += code.count('{') - code.count('}')
            if re.match(r'\s*NDefines\.(NMilitary|NNavy|NAir|NSupply|NRailwayGun|NDoctrines)\.', line):
                # Infrastructure scaling in TGWR assumes ten levels; our map has five.
                if any(k in line for k in ('INFRASTRUCTURE_MOVEMENT_SPEED_IMPACT', 'INFRA_ORG_IMPACT', 'INFRA_TO_SUPPLY', 'SUPPLY_FROM_DAMAGED_INFRA')):
                    continue
                lines.append(line)
            elif p.name == 'frontlineai_defines_test.lua' and re.match(r'\s*NDefines\.NAI\.', line):
                if not any(k in line for k in ('DIPLOMACY_', 'SEND_VOLUNTEER_', 'CALL_ALLY_', 'JOIN_ALLY_', 'LEND_LEASE')):
                    lines.append(line)
    write('common/defines/zz_1893_great_war_combat.lua', '\n'.join(lines) + '\n')

    # Import only the transitive helper blocks referenced by the subsystem.
    helpers = {}
    for category in ('scripted_triggers', 'scripted_effects', 'modifiers', 'modifier_definitions'):
        for p in (source / 'common' / category).glob('*.txt'):
            text = read(p)
            for key, start, op, end in blocks(text):
                helpers[key] = (category, text[start:end])
    selected = set()
    corpus = '\n'.join(read(ROOT / p) for p in outputs if p.endswith(('.txt', '.gui')))
    while True:
        words = set(re.findall(r'\b[A-Za-z_]\w*\b', clean(corpus)))
        new = (words & set(helpers)) - selected
        if not new:
            break
        selected |= new
        corpus += '\n' + '\n'.join(helpers[k][1] for k in new)
    for category in {helpers[k][0] for k in selected}:
        write('common/' + category + '/1893_great_war_dependencies.txt', '\n\n'.join(redates(helpers[k][1]) for k in sorted(selected) if helpers[k][0] == category) + '\n')

    # Research unlock templates are equipment dependencies, not country OOBs.
    for name in set(re.findall(r'\bload_oob\s*=\s*"?([\w-]+)', clean(corpus))):
        p = source / 'history/units' / (name + '.txt')
        if not p.exists():
            p = game / 'history/units' / (name + '.txt')
            if not p.exists():
                raise ValueError('Missing unlock OOB: ' + name)
            write('history/units/' + name + '.txt', redates(read(p)))
        else:
            copy(p)

    # The source uses the tank/ship designers. Retain working legacy branches
    # for games without NSB/MTG, and their equipment closure below.
    legacy = []
    for filename, dlc in [('naval.txt', 'Man the Guns'), ('armor.txt', 'No Step Back')]:
        original = redates(read(game / 'common/technologies' / filename))
        parts = []
        for key, start, op, end in blocks(original, 1):
            if key in techs:
                continue
            if filename == 'armor.txt' and key != 'gwtank':
                continue
            body = original[start:end]
            body = re.sub(r'\bstart_year\s*=\s*(\d+)', lambda m: 'start_year = ' + str(max(1893, int(m[1]) - 26)), body)
            body = re.sub(r'\bpath\s*=\s*\{[^}]*leads_to_tech\s*=\s*sp_\w+[^}]*\}', '', body)
            if key in ('heavy_battleship', 'torpedo_cruiser'):
                prerequisite = 'improved_battleship' if key == 'heavy_battleship' else 'basic_light_cruiser'
                at = body.index('{') + 1
                body = body[:at] + '\n dependencies = { ' + prerequisite + ' = 1 }\n' + body[at:]
            # Keep designer-specific legacy content hidden when DLC is enabled.
            pos = body.index('{') + 1
            body = body[:pos] + '\n allow_branch = { NOT = { has_dlc = "' + dlc + '" } }\n' + body[pos:]
            parts.append(body)
            legacy.append(key)
            techs[key] = (None, body)
        # Local @position variables preserve the inherited layout.
        variables = '\n'.join(re.findall(r'^\s*@\w+\s*=\s*[^\n]+', original, re.M))
        write('common/technologies/' + filename, 'technologies = {\n' + variables + '\n' + '\n'.join(parts) + '\n}\n')

    # Graphical folders for legacy modes use vanilla GUI containers.
    source_tags = read(ROOT / 'common/technology_tags/00_technology.txt')
    game_tags = read(game / 'common/technology_tags/00_technology.txt')
    source_categories = next((source_tags[o+1:e-1] for n,s,o,e in blocks(source_tags) if n == 'technology_categories'))
    game_categories = next((game_tags[o+1:e-1] for n,s,o,e in blocks(game_tags) if n == 'technology_categories'))
    missing_cats = set(re.findall(r'\b\w+\b', clean(game_categories))) - set(re.findall(r'\b\w+\b', clean(source_categories)))
    for n,s,o,e in reversed(blocks(source_tags)):
        if n == 'technology_categories':
            source_tags = source_tags[:e-1] + '\n' + '\n'.join(sorted(missing_cats)) + '\n' + source_tags[e-1:]
    # Restore armour_folder and naval_folder visibility without their DLCs.
    source_tags = re.sub(r'(armour_folder\s*=\s*\{.*?available\s*=\s*\{)\s*always\s*=\s*no', r'\1 NOT = { has_dlc = "No Step Back" }', source_tags, flags=re.S)
    source_tags = source_tags.replace('nsb_armour_folder = {\n\t\tledger = army', 'nsb_armour_folder = {\n\t\tavailable = { has_dlc = "No Step Back" }\n\t\tledger = army')
    source_tags = source_tags.replace('mtgnavalfolder = {\n\t\tledger = navy', 'mtgnavalfolder = {\n\t\tavailable = { has_dlc = "Man the Guns" }\n\t\tledger = navy')
    for n,s,o,e in blocks(game_tags, 1):
        if n == 'naval_folder':
            extra = game_tags[s:e]
            marker = source_tags.rfind('}')
            source_tags = source_tags[:marker] + '\n' + extra + '\n' + source_tags[marker:]
    write('common/technology_tags/00_technology.txt', source_tags)

    # Fill only missing vanilla equipment/module definitions actually referenced.
    def index_defs(base, folder, wrapper_level=1):
        result = {}
        for p in (base / folder).rglob('*.txt'):
            text = read(p)
            for key,s,o,e in blocks(text, wrapper_level):
                result[key] = text[s:e]
        return result
    write('common/units/equipment/zz_1893_legacy_compatibility.txt', 'equipments = {}\n')
    write('common/units/equipment/modules/zz_1893_legacy_compatibility.txt', 'equipment_modules = {}\n')
    write('common/units/zz_1893_legacy_compatibility.txt', 'sub_units = {}\n')
    equipment = index_defs(ROOT, 'common/units/equipment')
    modules = index_defs(ROOT, 'common/units/equipment/modules')
    vanilla_equipment = index_defs(game, 'common/units/equipment')
    vanilla_modules = index_defs(game, 'common/units/equipment/modules')
    required_eq = set()
    required_mod = set()
    unit_defs = {}
    for p in (ROOT / 'common/units').glob('*.txt'):
        for key,s,o,e in blocks(read(p), 1):
            unit_defs[key] = read(p)[s:e]
    vanilla_units = {}
    for p in (game / 'common/units').glob('*.txt'):
        text = read(p)
        for key,s,o,e in blocks(text, 1):
            vanilla_units[key] = text[s:e]
    tech_corpus = '\n'.join(read(p) for p in (ROOT / 'common/technologies').glob('*.txt'))
    needed_units = set()
    for label,s,o,e in blocks(tech_corpus, 2):
        if label == 'enable_subunits':
            needed_units |= set(re.findall(r'\b\w+\b', clean(tech_corpus[o+1:e-1]))) & set(vanilla_units)
    missing_units = needed_units - set(unit_defs)
    write('common/units/zz_1893_legacy_compatibility.txt', 'sub_units = {\n' + '\n'.join(vanilla_units[k] for k in sorted(missing_units)) + '\n}\n')
    scan = '\n'.join(read(p) for p in (ROOT / 'common/technologies').glob('*.txt'))
    scan += '\n' + '\n'.join(read(p) for p in (ROOT / 'history').rglob('*.txt'))
    scan += '\n' + '\n'.join(read(p) for p in (ROOT / 'common/units').glob('*.txt'))
    required_eq |= set(re.findall(r'\b(?:type|archetype|parent)\s*=\s*(\w+)', clean(scan))) & set(vanilla_equipment)
    for m in re.finditer(r'\benable_equipments\s*=\s*\{([^}]+)\}', clean(scan)):
        required_eq.update(re.findall(r'\b\w+\b', m[1]))
    for m in re.finditer(r'\bneed\s*=\s*\{([^}]+)\}', clean(scan)):
        required_eq.update(re.findall(r'\b(\w+)\s*=', m[1]))
    required_mod |= set(re.findall(r'\b\w+\b', clean(scan))) & set(vanilla_modules)
    eq_extra = {}
    mod_extra = {}
    while True:
        new_eq = required_eq - set(equipment) - set(eq_extra)
        new_mod = required_mod - set(modules) - set(mod_extra)
        found = False
        for key in new_eq & set(vanilla_equipment):
            body = redates(vanilla_equipment[key])
            eq_extra[key] = body
            required_eq.update(re.findall(r'\b(?:archetype|parent)\s*=\s*(\w+)', body))
            required_mod |= set(re.findall(r'\b\w+\b', body)) & set(vanilla_modules)
            found = True
        for key in new_mod & set(vanilla_modules):
            mod_extra[key] = redates(vanilla_modules[key])
            found = True
        if not found:
            break
    write('common/units/equipment/zz_1893_legacy_compatibility.txt', 'equipments = {\n' + '\n'.join(eq_extra.values()) + '\n}\n')
    write('common/units/equipment/modules/zz_1893_legacy_compatibility.txt', 'equipment_modules = {\n' + '\n'.join(mod_extra.values()) + '\n}\n')

    # Artillery references in our scenario now point at TGWR's field guns.
    aliases = {'gw_artillery': 'early_artillery', 'artillery_brigade': 'field_gun_brigade',
               'early_fighter': 'scout_plane', 'early_bomber': 'airship', 'gwtank_chassis': 'tank_design',
               'artillery_equipment_1': 'field_gun_equipment_0', 'artillery_equipment_2': 'field_gun_equipment_1',
               'artillery_equipment_3': 'field_gun_equipment_2', 'artillery_equipment': 'field_gun_equipment'}
    scenario_changes = []
    for folder in ('history/countries', 'history/units', 'common/national_focus', 'common/decisions', 'common/scripted_effects', 'events'):
        for p in (ROOT / folder).rglob('*.txt'):
            if p.relative_to(ROOT).as_posix() in outputs:
                continue
            text = read(p)
            new = re.sub(r'\b(' + '|'.join(aliases) + r')\b', lambda m: aliases[m[0]], text)
            if folder == 'history/units':
                new = re.sub(r'\bartillery\s*=', 'field_gun =', new)
            if folder == 'history/countries':
                # Keep existing grants for now, resolving IDs; baseline equipment
                # is deliberately granted, not the entire 1893 research tree.
                new = new.replace('early_fighter = 1', 'early_airplane = 1') if 'early_airplane' in techs else new
            if new != text:
                write(p.relative_to(ROOT), new)
                scenario_changes.append(p.relative_to(ROOT).as_posix())

    # Copy tech/doctrine/designer sprite definitions and their exact assets.
    interface_files = ['countrytechtreeview.gui', 'countrydoctrinetreeview.gui',
                       'Technologies.gfx', 'ww1_Technologies.gfx', 'ww_technologies.gfx',
                       'ww1_countrytechtreeview.gfx', 'ww1_doctrines.gfx', 'ww1_subuniticons.gfx',
                       'ww1_ship_modules_icons.gfx', 'ww1_ships_modules_icons.gfx', 'ww1_tank_modules_icons.gfx']
    interface_files += [p.name for p in (source / 'interface').glob('*_technologies.gfx')]
    for name in sorted(set(interface_files)):
        p = source / 'interface' / name
        if p.exists():
            text = read(p)
            if p.suffix == '.gui':
                text = re.sub(r'(\btext\s*=\s*")(18\d{2}|19\d{2})(")', lambda m: m[1] + str(year(m[2])) + m[3], text)
                if name == 'countrytechtreeview.gui':
                    vanilla_gui = read(game / 'interface/countrytechtreeview.gui')
                    for key,s,o,e in blocks(vanilla_gui, 2):
                        body = vanilla_gui[s:e]
                        if re.search(r'\bname\s*=\s*"(?:naval_folder|armour_folder)"', body):
                            if re.search(r'\bname\s*=\s*"' + re.search(r'name\s*=\s*"(\w+)"', body)[1] + r'"', text):
                                continue
                            # Place with other folder containers, inside the parent.
                            source_folder = next((x for x in blocks(text, 2) if 'name = "infantry_folder"' in text[x[1]:x[3]]), None)
                            if source_folder:
                                text = text[:source_folder[1]] + redates(body) + '\n' + text[source_folder[1]:]
            write('interface/' + name, text)
    gfx_index = {}
    for p in (source / 'interface').rglob('*.gfx'):
        text = read(p)
        for key,s,o,e in blocks(text, 1):
            body = text[s:e]
            m = re.search(r'\bname\s*=\s*"([^"]+)"', body)
            if m:
                gfx_index[m[1]] = body
    graphics_corpus = '\n'.join(read(ROOT / p) for p in outputs if p.endswith(('.txt', '.gui', '.gfx')))
    needed = set(re.findall(r'\bGFX_\w+', graphics_corpus))
    pictures = set(re.findall(r'\bpicture\s*=\s*"?(\w+)', clean(read(ROOT / 'common/combat_tactics.txt'))))
    needed |= {key for key in gfx_index if any(pic in key for pic in pictures) and ('tactic' in key or 'combat' in key)}
    existing = set(re.findall(r'\bname\s*=\s*"(GFX_[^"]+)"', '\n'.join(read(p) for p in (ROOT / 'interface').rglob('*.gfx'))))
    additional = {k: gfx_index[k] for k in needed - existing if k in gfx_index}
    write('interface/1893_combat_dependencies.gfx', 'spriteTypes = {\n' + '\n'.join(additional.values()) + '\n}\n')
    for p in list(outputs):
        if p.endswith(('.gfx', '.gui')):
            for texture in re.findall(r'\b(?:texturefile|file|effectFile)\s*=\s*"([^"]+)"', read(ROOT / p), re.I):
                asset = source / texture.replace('\\', '/')
                if asset.is_file():
                    copy(asset)
    # Equipment designer graphic DB resolves hull/chassis illustration variants.
    for p in (source / 'gfx/interface/equipmentdesigner/graphic_db').rglob('*'):
        if p.is_file():
            copy(p)
    for p in list(outputs):
        if p.endswith('.txt') and 'graphic_db' in p:
            for path in re.findall(r'"(gfx/[^"\n]+)"', read(ROOT / p)):
                asset = source / path
                if asset.is_file():
                    copy(asset)

    # Retain TGWR RU/EN wording for the research/combat subset only.
    patterns = ('research', 'equipment', 'equip_air', 'equip_naval', 'unit', 'doctrines',
                'ship_modules', 'tank_modules', 'designer', 'special_projects', 'modifiers', 'stats')
    for lang in ('russian', 'english'):
        local = {}
        all_local = {}
        for base in (game, source):
            for p in sorted((base / 'localisation' / lang).rglob('*.yml')):
                for line in read(p).splitlines():
                    m = re.match(r'\s*([^\s:#]+):\d*\s+"(.*)"', line)
                    if m:
                        all_local[m[1]] = m[2]
        for p in sorted((source / 'localisation' / lang).rglob('*.yml')):
            if any(word in p.name for word in patterns):
                for line in read(p).splitlines():
                    m = re.match(r'\s*([^\s:#]+):\d*\s+"(.*)"\s*$', line)
                    if m:
                        local[m[1]] = m[2]
        # Resolve technology labels through the source's equipment names when
        # it relies on implicit engine naming; otherwise inherit game wording.
        for p in (ROOT / 'common/technologies').glob('*.txt'):
            text = read(p)
            for key,s,o,e in blocks(text, 1):
                body = clean(text[s:e])
                if key not in local:
                    eq_match = re.search(r'\benable_equipments\s*=\s*\{\s*(\w+)', body)
                    ref = eq_match[1] if eq_match else key
                    local[key] = all_local.get(ref, all_local.get(key, key.replace('_', ' ').title()))
                if key + '_desc' not in local:
                    local[key + '_desc'] = all_local.get(key + '_desc', 'Развитие военных технологий и промышленности.' if lang == 'russian' else 'Development of military technology and industry.')
        # Include directly referenced descriptions/tooltips/tactics as well.
        words = set(re.findall(r'\b\w+\b', corpus)) | set(re.findall(r'\btactic_\w+', read(ROOT / 'common/combat_tactics.txt')))
        for key in words:
            for candidate in (key, key + '_desc'):
                if candidate in all_local and candidate not in local:
                    local[candidate] = all_local[candidate]
        for key,value in list(local.items()):
            local[key] = re.sub(r'\b(19\d{2})\b', lambda m: str(year(m[1])), value)
        write(f'localisation/{lang}/zzzzzzzzzz_great_war_research_l_{lang}.yml', 'l_' + lang + ':\n' + '\n'.join(' ' + k + ':0 "' + v + '"' for k,v in local.items()) + '\n')
        old = ROOT / f'localisation/{lang}/zzzzzzzzzz_research_industry_l_{lang}.yml'
        if old.exists():
            backup(old)
            old.unlink()

    # Replace paths make absent vanilla WWII definitions stay absent.
    descriptor = read(ROOT / 'descriptor.mod')
    replace = ['common/technologies', 'common/technology_tags', 'common/units',
               'common/doctrines/folders', 'common/doctrines/grand_doctrines',
               'common/doctrines/subdoctrines', 'common/doctrines/tracks',
               'common/special_projects', 'gfx/interface/equipmentdesigner/graphic_db']
    for path in replace:
        declaration = 'replace_path="' + path + '"'
        if declaration not in descriptor:
            descriptor += '\n' + declaration
    write('descriptor.mod', descriptor.strip() + '\n')

    # The initial generator is retired rather than allowed to overwrite integration.
    write('tools/great_war_research_manifest.json', json.dumps({
        'source': str(source), 'source_version': '0.15.19', 'start': '1893.1.1',
        'source_sha256': hashes, 'files': sorted(outputs), 'technology_dates': dates,
        'first_research': sorted(baseline), 'legacy_technologies': sorted(legacy),
        'helpers': sorted(selected), 'scenario_changes': scenario_changes,
        'date_policy': '1880/1890 kept; 1894–1905 -> 1893; later years -14; roots and first support <=1893',
    }, ensure_ascii=False, indent=2) + '\n')
    print(f'Integrated {len(dates)} TGWR technologies, {len(legacy)} legacy technologies, {len(selected)} helper blocks; {len(outputs)} files.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--game', type=Path, required=True)
    args = parser.parse_args()
    assert args.source.resolve() != ROOT.resolve()
    run(args.source, args.game)
