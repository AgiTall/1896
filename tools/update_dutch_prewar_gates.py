"""Restrict Dutch preparation focuses to the period before the first Japanese war."""
from pathlib import Path
import shutil
from add_canon_countries import parse, value, dump

R = Path(__file__).resolve().parents[1]

def excluded_branches(focuses):
    excluded = {'A01_dutch_literacy', 'A01_pacific_settlement'}
    # Revealed postwar roots need no visible prerequisite into the public tree.
    excluded |= {fid for fid,node in focuses.items() if any(
        k == 'allow_branch' and ('has_country_flag', '=', 'A01_royal_path_revealed') in v
        for k,op,v in node
    )}
    while True:
        added = {fid for fid, node in focuses.items() if any(
            value(v, 'focus') in excluded for k, op, v in node if k == 'prerequisite'
        )}
        if added <= excluded:
            return excluded
        excluded |= added

def save(relative, text):
    p = R/relative
    backup = R/'tools/backups/dutch_prewar_gates'/relative
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        shutil.copy2(p, backup)
    p.write_text(text, encoding='utf-8')

if __name__ == '__main__':
    path = 'common/national_focus/a01_focus.txt'
    tree = parse((R/path).read_text(encoding='utf-8-sig'))
    focuses = {value(v, 'id'): v for k, op, v in value(tree, 'focus_tree') if k == 'focus'}
    excluded = excluded_branches(focuses)
    assert 'A01_dutch_literacy' in focuses
    for fid, node in focuses.items():
        if fid in excluded:
            continue
        available = next((v for k, op, v in node if k == 'available'), None)
        if available is None:
            available = []
            node.append(('available', '=', available))
        if fid == 'A01_wartime_industry':
            available[:] = [entry for entry in available if entry != ('has_war_with', '=', 'A03')]
        gate = parse('NOT = { has_war_with = A03 has_country_flag = A01_borneo_war_started }')[0]
        if gate not in available:
            available.append(gate)
        for key, setting in (('cancel_if_invalid', 'yes'), ('continue_if_invalid', 'no')):
            node[:] = [entry for entry in node if entry[0] != key]
            node.append((key, '=', setting))
    save(path, dump(tree)+'\n')
    # Preserve the mobilisation benefit before the war, but end it when that war ends.
    path = 'common/ideas/pacific_ideas.txt'
    text = (R/path).read_text(encoding='utf-8-sig')
    old = 'A01_war_production = { cancel = { NOT = { has_war_with = A03 } }'
    new = 'A01_war_production = { cancel = { has_country_flag = A01_borneo_war_started NOT = { has_war_with = A03 } }'
    assert old in text
    save(path, text.replace(old, new, 1))
    for lang, desc in (
        ('russian', 'Оборонные заказы повышают выпуск заводов ценой дополнительных потребительских расходов. Программа начинается до войны с Японией, действует во время неё и снимается после заключения мира.'),
        ('english', 'Defence orders increase factory output at the cost of additional consumer goods requirements. The program begins before the war with Japan, continues during it and ends when peace returns.'),
    ):
        p = R/f'localisation/{lang}/pacific_content_l_{lang}.yml'
        lines = p.read_text(encoding='utf-8-sig').splitlines()
        lines = [f' A01_war_production_desc:0 "{desc}"' if line.lstrip().startswith('A01_war_production_desc:') else line for line in lines]
        p.write_text('\n'.join(lines)+'\n', encoding='utf-8-sig')
    print('Restricted:', len(focuses)-len(excluded), 'Exempt:', ', '.join(sorted(excluded)))
