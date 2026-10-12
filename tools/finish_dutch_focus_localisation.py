"""Use readable prewar conditions and audit Dutch focus/idea localisation."""
from pathlib import Path
import re
from add_canon_countries import parse, value, dump

R = Path(__file__).resolve().parents[1]
old = parse('NOT = { has_war_with = A03 has_country_flag = A01_borneo_war_started }')[0]
new = parse('custom_trigger_tooltip = { tooltip = A01_before_japanese_war_tt NOT = { has_war_with = A03 has_country_flag = A01_borneo_war_started } }')[0]

if __name__ == '__main__':
    p = R/'common/national_focus/a01_focus.txt'
    tree = parse(p.read_text(encoding='utf-8-sig'))
    count = 0
    for k, op, focus in value(tree, 'focus_tree'):
        if k != 'focus':
            continue
        available = next((v for key, op, v in focus if key == 'available'), [])
        if old in available:
            available[available.index(old)] = new
            count += 1
    assert count == 28
    p.write_text(dump(tree)+'\n', encoding='utf-8')
    labels = {
      'russian': ('Война с Японской империей ещё не началась', 'Управление укреплений Борнео', 'Военные инженеры готовят портовые оборонительные позиции. На 180 дней скорость строительства сухопутных и береговых укреплений повышается на 15%. Программа не даёт общего бонуса к защите армии.'),
      'english': ('The war with the Japanese Empire has not yet begun', 'Borneo Fortification Directorate', 'Military engineers prepare port defences. Land and coastal fort construction speed increases by 15% for 180 days. The program grants no general army defence bonus.'),
    }
    for lang, (condition, name, desc) in labels.items():
        # Keep these entries in an established, already loaded localisation file.
        p = R/f'localisation/{lang}/pacific_content_l_{lang}.yml'
        text = p.read_text(encoding='utf-8-sig')
        text += f'\n A01_before_japanese_war_tt:0 "{condition}"\n A01_borneo_fortification_directorate:0 "{name}"\n A01_borneo_fortification_directorate_desc:0 "{desc}"\n'
        p.write_text(text, encoding='utf-8-sig')
        # Remove duplicate keys while retaining the standalone source file.
        p = R/f'localisation/{lang}/A01_borneo_defences_l_{lang}.yml'
        p.write_text(f'l_{lang}:\n # Borneo entries are maintained in pacific_content_l_{lang}.yml.\n', encoding='utf-8-sig')
    print('Localized all 28 prewar conditions and the directorate in established RU/EN files.')
