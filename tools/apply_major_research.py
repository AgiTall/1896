"""Distinct starting knowledge for the six featured powers in the 1893 canon."""
import json
import re
from integrate_great_war_research import ROOT, blocks, clean, read

BEGIN = '# BEGIN MAJOR RESEARCH PROFILE 1893'
END = '# END MAJOR RESEARCH PROFILE 1893'
FORBIDDEN = {'airship', 'scout_plane', 'gwtank', 'tank_design',
             'early_ship_hull_submarine', 'early_submarine', 'radio',
             'chemical_warfare_tech', 'early_gas_mask', 'tech_trucks',
             'basic_armored_car', 'basic_armored_car_chassis'}


def apply_profiles():
    profiles = json.loads(read(ROOT / 'tools/major_research_profiles.json'))
    tech = {}
    for p in (ROOT / 'common/technologies').glob('*.txt'):
        text = read(p)
        for key, s, o, e in blocks(text, 1):
            tech[key] = clean(text[s:e])
    future = {key for key, body in tech.items()
              if (year := re.search(r'\bstart_year\s*=\s*(\d+)', body)) and int(year[1]) > 1893}

    def close(keys):
        result = set(keys)
        pending = list(result)
        while pending:
            key = pending.pop()
            assert key in tech, key
            for name, s, o, e in blocks(tech[key], 1):
                if name == 'dependencies':
                    for dep in re.findall(r'\b(\w+)\s*=', tech[key][o+1:e-1]):
                        if dep not in result:
                            result.add(dep)
                            pending.append(dep)
        for key in result:
            assert key not in FORBIDDEN, key
            year = re.search(r'\bstart_year\s*=\s*(\d+)', tech[key])
            assert not year or int(year[1]) <= 1893, key
        return sorted(result)

    report = {}
    for tag, profile in profiles.items():
        paths = list((ROOT / 'history/countries').glob(f'{tag} - *.txt'))
        assert len(paths) == 1, tag
        p = paths[0]
        text = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\s*', '', read(p), flags=re.S).rstrip()
        # Earlier compatibility grants accidentally supplied aircraft/tanks.
        # Remove these grants, keeping every DLC condition and fleet design.
        spans = []
        for level in range(10):
            spans += [span for span in blocks(text, level) if span[0] == 'set_technology']
        for key, s, o, e in sorted(spans, key=lambda x: x[1], reverse=True):
            body = text[o+1:e-1]
            for forbidden in FORBIDDEN | future:
                body = re.sub(r'\b' + forbidden + r'\s*=\s*1\b', '', body)
            text = text[:o+1] + body + text[e-1:]
        groups = {key: close(profile[key]) for key in ('technologies', 'naval_mtg', 'naval_legacy')}
        lines = [BEGIN, '# ' + profile['specialization'], 'set_technology = {']
        lines += [f'\t{key} = 1' for key in groups['technologies']]
        lines += ['}', 'if = {', '\tlimit = { has_dlc = "Man the Guns" }', '\tset_technology = {']
        lines += [f'\t\t{key} = 1' for key in groups['naval_mtg']]
        lines += ['\t}', '\telse = {', '\t\tset_technology = {']
        lines += [f'\t\t\t{key} = 1' for key in groups['naval_legacy']]
        lines += ['\t\t}', '\t}', '}', END]
        output = text + '\n\n' + '\n'.join(lines) + '\n'
        p.write_text('\n'.join(line.rstrip() for line in output.splitlines()) + '\n', encoding='utf-8-sig')
        report[tag] = dict(name=profile['name'], specialization=profile['specialization'], **groups)
    (ROOT / 'tools/major_research_manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Applied six distinct major-power research profiles (MTG and legacy fleets).')


if __name__ == '__main__':
    apply_profiles()
