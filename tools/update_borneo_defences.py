"""Migrate the three existing Borneo focuses to a staged fortification program."""
from pathlib import Path
import re
import shutil
from add_canon_countries import parse, value, dump

R = Path(__file__).resolve().parents[1]

def save(relative, text, bom=False):
    p = R / relative
    backup = R / 'tools/backups/borneo_fortification_program' / relative
    backup.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and not backup.exists():
        shutil.copy2(p, backup)
    p.write_text(text, encoding='utf-8-sig' if bom else 'utf-8')

def setv(node, key, new):
    node[:] = [(k, op, new if k == key else old) for k, op, old in node]

def forts(level, land=False):
    effects = ''
    for pid in (10212, 10199, 12228):
        builds = [('coastal_bunker', level)] + ([('bunker', 1)] if land else [])
        for building, target in builds:
            effects += f'''if = {{
 limit = {{ owns_state = 1024 controls_province = {pid} }}
 1024 = {{ set_building_level = {{
  type = {building} level = {target}
  province = {{ id = {pid} level < {target} }}
 }} }}
}}'''
    return effects

if __name__ == '__main__':
    path = 'common/national_focus/a01_focus.txt'
    tree = parse((R/path).read_text(encoding='utf-8-sig'))
    focuses = {value(v, 'id'): v for k, op, v in value(tree, 'focus_tree') if k == 'focus'}
    first = focuses['A01_build_bornean_fortifications']
    last = focuses['A01_improve_bornean_fortifications']
    for fid in ('A01_build_bornean_fortifications', 'A01_prepare_bornean_logistics', 'A01_improve_bornean_fortifications'):
        setv(focuses[fid], 'available', parse('owns_state = 1024 controls_state = 1024'))
    setv(first, 'completion_reward', parse('add_timed_idea = { idea = A01_borneo_fortification_directorate days = 180 }' + forts(1)))
    setv(last, 'cost', '10')
    setv(last, 'completion_reward', parse(forts(2, land=True)))
    save(path, dump(tree) + '\n')
    save('common/ideas/A01_borneo_defences.txt', '''ideas = { country = {
 A01_borneo_fortification_directorate = {
  picture = pacific_army
  allowed = { original_tag = A01 }
  removal_cost = -1
  modifier = {
   production_speed_bunker_factor = 0.15
   production_speed_coastal_bunker_factor = 0.15
  }
 }
} }
''')
    translations = {
      'russian': ('localisation/russian/18XX_focus_l_russian.yml', {
        'A01_build_bornean_fortifications': 'Управление укреплений Борнео',
        'A01_build_bornean_fortifications_desc': 'Инженерное управление организует оборону Джесселтона, Сандакана и Тавау. В удерживаемых нами портах Сабаха береговые укрепления доводятся до первого уровня. На 180 дней строительство сухопутных и береговых укреплений ускоряется на 15%.',
        'A01_improve_bornean_fortifications': 'Борнейский оборонительный пояс',
        'A01_improve_bornean_fortifications_desc': 'Снабжение позволяет завершить оборону трёх портов Сабаха: береговые укрепления доводятся до второго уровня, сухопутные — до первого. Работы проводятся только в принадлежащих нам и удерживаемых портах. Более сильные укрепления сохраняются.',
      }),
      'english': ('localisation/english/pacific_content_l_english.yml', {
        'A01_build_bornean_fortifications': 'Borneo Fortification Directorate',
        'A01_build_bornean_fortifications_desc': 'Organise the defence of Jesselton, Sandakan and Tawau. Coastal forts in our controlled Sabah ports reach level one. Land and coastal fort construction is accelerated by 15% for 180 days.',
        'A01_improve_bornean_fortifications': 'Bornean Defensive Belt',
        'A01_improve_bornean_fortifications_desc': 'Complete the three Sabah port positions: coastal forts reach level two and land forts level one. Works require our ownership and control. Existing stronger forts are preserved.',
      }),
    }
    for lang, (relative, entries) in translations.items():
        text = (R/relative).read_text(encoding='utf-8-sig')
        for key, label in entries.items():
            text, count = re.subn(r'^\s*' + key + r':(?:0)? .*$', f' {key}:0 "{label}"', text, flags=re.M)
            assert count == 1, (key, count)
        save(relative, text, bom=True)
        label = 'Управление укреплений Борнео' if lang == 'russian' else 'Borneo Fortification Directorate'
        desc = 'Инженеры координируют строительство портовых оборонительных позиций. Временная программа действует 180 дней.' if lang == 'russian' else 'Engineers coordinate port defences through a temporary 180-day construction program.'
        save(f'localisation/{lang}/A01_borneo_defences_l_{lang}.yml', f'l_{lang}:\n A01_borneo_fortification_directorate:0 "{label}"\n A01_borneo_fortification_directorate_desc:0 "{desc}"\n', bom=True)
