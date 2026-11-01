"""One-time Riau split. Population is apportioned by province pixel area."""
import json
import re
from PIL import Image
from integrate_great_war_research import ROOT, blocks, read

TARGET = ROOT / 'history/states/1086 - Riau Islands.txt'


def main():
    if TARGET.exists():
        raise SystemExit('Riau already exists; refusing to split population twice.')
    source = [(ROOT / 'history/states/1049-Medan and Riouw.txt', 12113),
              (ROOT / 'history/states/334-Kalimantan Barat.txt', 13298)]
    colors = {}
    for line in read(ROOT / 'map/definition.csv').splitlines():
        f = line.split(';')
        if f[0].isdigit():
            colors[int(f[0])] = tuple(map(int, f[1:4]))
    image = Image.open(ROOT / 'map/provinces.bmp').convert('RGB')
    areas = {color: count for count, color in image.getcolors(20000)}
    population = 0
    records = []
    cores = set()
    for p, province in source:
        original = read(p)
        text = original
        match = re.search(r'\bprovinces\s*=\s*\{([^}]+)\}', text)
        provinces = list(map(int, re.findall(r'\d+', match[1])))
        assert province in provinces
        before = int(re.search(r'\bmanpower\s*=\s*(\d+)', text)[1])
        transferred = round(before * areas[colors[province]] / sum(areas[colors[n]] for n in provinces))
        population += transferred
        records.append(dict(state=int(re.search(r'\bid\s*=\s*(\d+)', text)[1]),
                            province=province, population_before=before, transferred=transferred))
        cores.update(re.findall(r'\badd_core_of\s*=\s*(\w+)', text))
        remaining = re.sub(r'\b' + str(province) + r'\b', '', match[1])
        text = text[:match.start(1)] + remaining + text[match.end(1):]
        text = re.sub(r'(\bmanpower\s*=\s*)\d+', lambda m: m[1] + str(before-transferred), text)
        for name, s, o, e in reversed(blocks(text, 3)):
            if name == str(province):
                assert re.search(r'naval_base\s*=\s*1', text[o+1:e-1])
                text = text[:s] + text[e:]
        backup = ROOT / 'tools/backups/riau' / p.name
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(original, encoding='utf-8')
        p.write_text(text, encoding='utf-8')
    core_lines = '\n'.join(f'  add_core_of = {tag}' for tag in sorted(cores))
    TARGET.write_text(f'''state = {{
 id = 1086
 name = "STATE_1086"
 manpower = {population}
 state_category = pastoral
 history = {{
  owner = A01
{core_lines}
  set_resistance = 0
  set_compliance = 60
  buildings = {{
   infrastructure = 1
   13298 = {{ naval_base = 1 }}
   12113 = {{ naval_base = 1 }}
  }}
 }}
 provinces = {{ 13298 12113 }}
 local_supplies = 0.0
}}
''', encoding='utf-8')
    for lang, label in [('russian', 'Острова Риау'), ('english', 'Riau Islands')]:
        p = ROOT / f'localisation/{lang}/pz_new_states_l_{lang}.yml'
        p.write_text(read(p).rstrip() + f'\n STATE_1086:0 "{label}"\n', encoding='utf-8-sig')
    # A state must belong to one strategic region: move the Borneo island to
    # Sumatra together with the other Riau province.
    for filename, add in [('159-Borneo.txt', False), ('187-Sumatra.txt', True)]:
        p = ROOT / 'map/strategicregions' / filename
        text = read(p)
        match = re.search(r'\bprovinces\s*=\s*\{([^}]+)\}', text)
        body = match[1]
        if add:
            body = body.rstrip() + ' 13298\n\t'
        else:
            body = re.sub(r'\b13298\b', '', body)
        p.write_text(text[:match.start(1)] + body + text[match.end(1):], encoding='utf-8')
    (ROOT / 'tools/riau_state_manifest.json').write_text(json.dumps(dict(state=1086, population=population, sources=records), indent=2) + '\n', encoding='utf-8')
    print(f'Created Riau (1086): population {population}; no extra resources or factories.')


if __name__ == '__main__':
    main()
