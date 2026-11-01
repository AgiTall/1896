"""Repair era building availability and every country's starting research.

Run after the TGWR integration/repair scripts. The reference mod stays read-only.
"""
from pathlib import Path
import json
import re
from integrate_great_war_research import ROOT, blocks, clean, read

GAME = Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
BLOCKED = ('rocket_site', 'nuclear_reactor', 'nuclear_reactor_heavy_water',
           'commercial_nuclear_reactor', 'nuclear_facility')
BASE = ('infantry_weapons', 'construction0', 'basic_railways', 'basic_train')
BEGIN = '# BEGIN 1893 START RESEARCH AND TRAINS'
END = '# END 1893 START RESEARCH AND TRAINS'


def technology_data():
    result = {}
    for p in (ROOT / 'common/technologies').glob('*.txt'):
        text = read(p)
        for key, s, o, e in blocks(text, 1):
            result[key] = clean(text[s:e])
    return result


def repair_country_start(text, tag, tech):
    """Apply the shared baseline without rewriting a country's other history."""
    text = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\s*', '', text, flags=re.S).rstrip()
    prerequisites = {}
    for key, body in tech.items():
        prerequisites[key] = set()
        for name, s, o, e in blocks(body, 1):
            if name == 'dependencies':
                prerequisites[key].update(re.findall(r'\b(\w+)\s*=', body[o+1:e-1]))
    grants = set(BASE)
    for key, s, o, e in blocks(text, 0):
        if key == 'set_technology':
            grants.update(re.findall(r'\b(\w+)\s*=\s*1\b', clean(text[o+1:e-1])))
    pending = list(grants)
    while pending:
        key = pending.pop()
        if key not in tech:
            raise ValueError(f'{tag}: unknown starting technology {key}')
        for dep in prerequisites[key] - grants:
            grants.add(dep)
            pending.append(dep)
    additions = set(BASE)
    for key in grants:
        additions.update(prerequisites[key])
    for key in additions:
        year = re.search(r'\bstart_year\s*=\s*(\d+)', tech[key])
        if year and int(year[1]) > 1893:
            raise ValueError(f'{tag}: future prerequisite {key}')
    lines = [BEGIN]
    if not re.search(r'\bset_research_slots\s*=', clean(text)):
        lines.append('set_research_slots = 2')
    lines += ['set_technology = {']
    lines += [f'\t{key} = 1' for key in sorted(additions)]
    lines += ['}', f'add_equipment_to_stockpile = {{ type = train_equipment_1 amount = 15 producer = {tag} }}', END]
    return text + '\n\n' + '\n'.join(lines) + '\n', sorted(additions)


def main():
    # Keep current engine definitions, including naval logistics and valid slots.
    # No technology/project exists to unlock nuclear weapons in this scenario.
    # Some installed files contain multiple leading BOMs. After prepending a
    # comment a leftover BOM becomes an illegal token inside the game script.
    text = read(GAME / 'common/buildings/00_buildings.txt').lstrip('\ufeff')
    for key, s, o, e in reversed(blocks(text, 1)):
        if key not in BLOCKED:
            continue
        body = text[o+1:e-1]
        for name, ss, oo, ee in reversed(blocks(body)):
            if name in ('dlc_allowed', 'missing_tech_loc', 'country_modifiers', 'state_modifiers'):
                body = body[:ss] + body[ee:]
        body = re.sub(r'(?m)^\s*(?:is_buildable|hide_if_missing_tech)\s*=\s*\w+\s*$', '', body)
        text = text[:o+1] + '\n\t\tis_buildable = no\n\t\tdlc_allowed = { always = no }\n\t\thide_if_missing_tech = yes\n' + body + text[e-1:]
    target = ROOT / 'common/buildings/00_buildings.txt'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('# 1893: modern rocket/nuclear buildings are unavailable.\n' + text, encoding='utf-8')

    tech = technology_data()
    countries = []
    for p in sorted((ROOT / 'history/countries').glob('*.txt')):
        tag = p.name.split(' ', 1)[0]
        if tag == 'ZZZ':  # map placeholder, not a playable state
            continue
        text, additions = repair_country_start(read(p), tag, tech)
        p.write_text(text, encoding='utf-8-sig')
        countries.append(dict(tag=tag, added_technologies=additions, trains=15))
    report = dict(blocked_buildings=list(BLOCKED), baseline=list(BASE), countries=countries)
    (ROOT / 'tools/1893_start_manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Fixed {len(countries)} countries; 15 trains each; {len(BLOCKED)} modern buildings disabled.')
    from apply_major_research import apply_profiles
    apply_profiles()


if __name__ == '__main__':
    main()
