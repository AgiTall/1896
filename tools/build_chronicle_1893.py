"""Build the dated 1893 chronicle from the author's supplied timeline."""
from pathlib import Path
from datetime import datetime, timedelta
import re, json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r'C:\Users\AgiTall\.codex\attachments\0f640bbf-4df2-481e-8dba-eee556f56ce0\Вставленный текст.txt')

def write(path, text, bom=False):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8-sig' if bom else 'utf-8')

# Each pair supplies actual game effects, in the author's option order.
E = {
1: ('add_political_power = -40 add_stability = 0.05 A01 = { add_political_power = 30 }', 'add_political_power = 60 A01 = { add_stability = -0.04 }'),
2: ('add_political_power = -35 add_stability = 0.03', 'add_war_support = 0.05 add_stability = -0.04 A10 = { add_war_support = 0.05 }'),
3: ('navy_experience = 25 army_experience = -10', 'army_experience = 15 add_stability = -0.04'),
4: ('A02 = { give_military_access = A06 } A06 = { give_military_access = A02 }', 'A02 = { add_political_power = 15 } A06 = { add_political_power = 15 }'),
5: ('add_manpower = -500 add_war_support = 0.05 PHR = { add_manpower = -300 add_stability = -0.05 }', 'add_stability = 0.04 PHR = { add_stability = 0.05 }'),
6: ('A02 = { add_political_power = -25 add_equipment_to_stockpile = { type = convoy_1 amount = -5 } }', 'A02 = { add_equipment_to_stockpile = { type = convoy_1 amount = 5 } }'),
7: ('add_political_power = -60 add_stability = 0.05 add_fuel = 5000', 'add_stability = -0.08 navy_experience = -20'),
8: ('add_political_power = 50 add_stability = -0.05', 'add_stability = 0.05 add_political_power = -20'),
9: ('add_political_power = 35 add_fuel = -3000 A04 = { add_fuel = 3000 }', 'add_political_power = 60 A03 = { add_fuel = 3000 }'),
10: ('add_manpower = 1500 add_political_power = -40 army_experience = 15', 'A08 = { add_manpower = 1500 army_experience = 15 } add_stability = -0.03'),
11: ('add_political_power = -35 add_tech_bonus = { name = CH93_research bonus = 0.25 uses = 1 category = industry }', 'A02 = { add_timed_idea = { idea = CH93_patrols days = 180 } add_fuel = -3000 }'),
12: ('add_manpower = 2500 add_political_power = -30 add_stability = -0.02', 'add_stability = 0.03 add_political_power = 15'),
13: ('add_stability = 0.03', 'add_war_support = 0.05 A03 = { add_war_support = 0.06 add_equipment_to_stockpile = { type = convoy_1 amount = -3 } }'),
14: ('add_war_support = 0.04 navy_experience = 15', 'add_fuel = 2000 add_political_power = 20'),
15: ('add_timed_idea = { idea = CH93_patrols days = 240 } add_political_power = -25', 'add_political_power = 25 A04 = { add_political_power = -15 }'),
16: ('CH93_cede_borneo = yes', 'set_country_flag = A01_refused_japanese_ultimatum add_war_support = 0.08 A03 = { set_country_flag = JPC_ultimatum_sent }'),
17: ('add_stability = -0.05 add_war_support = 0.05 A10 = { add_manpower = 1000 add_war_support = 0.06 }', 'add_stability = 0.04 add_political_power = -25 A10 = { add_war_support = -0.04 }'),
18: ('add_manpower = 1500 add_stability = -0.03', 'add_stability = 0.03 add_political_power = -30'),
19: ('A01 = { add_timed_idea = { idea = CH93_blockade days = 120 } } add_fuel = -5000 navy_experience = 15', 'A01 = { add_equipment_to_stockpile = { type = convoy_1 amount = -10 } } add_fuel = -2000'),
20: ('add_political_power = 35 A03 = { add_political_power = -35 }', 'if = { limit = { country_exists = A03 NOT = { has_war_with = A03 } } declare_war_on = { target = A03 type = annex_everything } }'),
21: ('navy_experience = 25 add_equipment_to_stockpile = { type = convoy_1 amount = 10 }', 'navy_experience = 15 A02 = { add_equipment_to_stockpile = { type = convoy_1 amount = -10 } }'),
22: ('PHW = { add_timed_idea = { idea = CH93_patrols days = 180 } } navy_experience = 15', 'PHW = { add_stability = -0.08 } add_war_support = 0.05'),
23: ('add_stability = -0.06 add_war_support = 0.03', 'add_political_power = -40 add_stability = 0.05'),
24: ('add_political_power = -40 add_tech_bonus = { name = CH93_research bonus = 0.5 uses = 1 category = industry }', 'add_timed_idea = { idea = CH93_patrols days = 90 }'),
25: ('CH93_start_war = yes army_experience = 15 navy_experience = 15', 'CH93_start_war = yes A01 = { add_timed_idea = { idea = CH93_blockade days = 120 } }'),
26: ('add_manpower = 2000 add_political_power = -30 add_stability = 0.02', 'add_manpower = -500 add_stability = -0.05 army_experience = 10'),
27: ('add_stability = -0.03 add_political_power = 30', 'add_stability = 0.04 add_political_power = -20'),
28: ('A01 = { add_timed_idea = { idea = CH93_embargo days = 90 } } A03 = { add_timed_idea = { idea = CH93_embargo days = 90 } }', 'add_political_power = 60 A01 = { add_political_power = 40 } A03 = { add_political_power = 40 }'),
29: ('add_stability = -0.06 add_war_support = 0.04 A10 = { add_war_support = 0.08 add_manpower = 500 }', 'add_political_power = -30 add_stability = 0.03'),
30: ('every_country = { add_timed_idea = { idea = CH93_patrols days = 60 } }', 'add_political_power = -30 add_tech_bonus = { name = CH93_research bonus = 0.25 uses = 1 category = industry }'),
31: ('add_manpower = -400 add_war_support = 0.06 army_experience = 20', 'add_manpower = 400 add_war_support = -0.04'),
32: ('add_stability = -0.04 PCB = { add_political_power = 25 }', 'add_political_power = 40 add_stability = -0.04 PCB = { add_political_power = -25 }'),
33: ('add_political_power = 25 A01 = { add_equipment_to_stockpile = { type = convoy_1 amount = 10 } }', 'A03 = { add_timed_idea = { idea = CH93_blockade days = 90 } } add_fuel = -5000'),
34: ('A01 = { add_manpower = 500 add_stability = 0.02 } A03 = { add_manpower = 500 add_stability = 0.02 }', 'A03 = { army_experience = 20 add_war_support = 0.05 } A01 = { add_manpower = -400 add_stability = -0.03 }'),
35: ('navy_experience = 25 add_war_support = 0.05 add_stability = -0.03', 'add_political_power = -30 add_stability = 0.04'),
36: ('every_country = { add_war_support = 0.03 }', 'every_country = { add_stability = 0.02 add_war_support = -0.02 }'),
}
TAGS = 'A04 A03 A01 A02 A05 A04 A03 A10 A01 A03 A04 A04 A01 A05 A02 A01 A03 A02 A03 PSL A02 PHW A01 A02 A03 A01 A06 A04 A03 A04 A01 A10 A02 A04 A01 A04'.split()

def main():
    source = SOURCE.read_text(encoding='utf-8-sig')
    blocks = re.split(r'\*\*(\d+)\. (.*?)\*\*', source)
    events = ['add_namespace = ch93\n']
    loc = ['l_russian:']
    schedule = ['CH93_tick = {', ' if = { limit = { date > 1892.12.31 date < 1894.1.1 }']
    manifest = []
    def l(key, value):
        loc.append(f' {key}:0 "{value.replace(chr(34), chr(39))}"')
    for pos in range(1, len(blocks), 3):
        n, title, body = int(blocks[pos]), blocks[pos+1], blocks[pos+2]
        date_text = re.search(r'\*\*Дата:\*\* (\d+\.\d+\.\d+)', body)[1]
        dt = datetime.strptime(date_text, '%d.%m.%Y')
        choices = re.findall(r'\*\*Вариант [12]:\*\* «(.*?)» \((.*?)\)\.', body)
        canon = re.search(r'\*\*Канон:\*\* (.*?)\.', body)[1]
        assert len(choices) == 2
        canonical = next(i for i, c in enumerate(choices) if c[0] == canon)
        tag = TAGS[n-1]
        prev = dt - timedelta(days=1)
        schedule.append(f'  if = {{ limit = {{ date > {prev.year}.{prev.month}.{prev.day} NOT = {{ has_global_flag = ch93_queued_{n} }} }} set_global_flag = ch93_queued_{n} if = {{ limit = {{ country_exists = {tag} }} {tag} = {{ country_event = {{ id = ch93.{n} }} }} }} else = {{ random_country = {{ country_event = {{ id = ch93.{n} }} }} }} }}')
        key = f'ch93.{n}'
        l(key+'.t', title)
        l(key+'.d', f'{date_text}. '+ ' '.join(c[1]+'.' for c in choices))
        l(key+'.news_a', f'{date_text}. {title}. Принято решение: «{choices[0][0]}». {choices[0][1]}.')
        l(key+'.news_b', f'{date_text}. {title}. Принято решение: «{choices[1][0]}». {choices[1][1]}.')
        events.append(f'country_event = {{\n id = {key}\n title = {key}.t\n desc = {key}.d\n picture = GFX_1896_event_talks\n is_triggered_only = yes\n fire_only_once = yes\n timeout_days = 3')
        for i, (label, _) in enumerate(choices):
            letter = 'ab'[i]
            l(key+'.'+letter, label)
            events.append(f' option = {{ name = {key}.{letter} ai_chance = {{ factor = {100 if i == canonical else 0} }}\n set_global_flag = ch93_{n}_{letter}\n {E[n][i]}\n hidden_effect = {{ every_country = {{ limit = {{ NOT = {{ tag = ROOT }} }} country_event = {{ id = ch93.{100+n} }} }} }}\n }}')
        events.append('}\n')
        events.append(f'country_event = {{ id = ch93.{100+n} title = {key}.t desc = {{ text = {key}.news_a trigger = {{ has_global_flag = ch93_{n}_a }} }} desc = {{ text = {key}.news_b trigger = {{ has_global_flag = ch93_{n}_b }} }} picture = GFX_1896_event_talks is_triggered_only = yes option = {{ name = ch93.read }} }}\n')
        manifest.append(dict(id=n, date=date_text, title=title, tag=tag, canonical=canonical+1))
    schedule += [' }', '}']
    l('ch93.read', 'Мир меняется.')
    l('CH93_research', 'Исследования феноменов 1893 года')
    for key, name, desc in [('blockade','Морская блокада','Нарушение морских поставок затрудняет снабжение и торговлю.'),('patrols','Усиленные морские патрули','Флот сопровождает торговые суда и разыскивает угрозы.'),('embargo','Оружейное эмбарго ВТП','Ограничения поставок замедляют вооружение армии.')]:
        l('CH93_'+key, name); l('CH93_'+key+'_desc', desc)
    write('events/chronicle_1893.txt', '\n'.join(events))
    write('localisation/russian/chronicle_1893_l_russian.yml', '\n'.join(loc)+'\n', True)
    write('common/scripted_effects/chronicle_1893.txt', '\n'.join(schedule)+'''\n
CH93_cede_borneo = {
 set_country_flag = pacific_trade_accord
 A03 = { set_country_flag = pacific_trade_accord }
 1024 = { if = { limit = { is_owned_by = A01 } A03 = { transfer_state = 1024 } } }
 1023 = { if = { limit = { is_owned_by = A01 } A03 = { transfer_state = 1023 } } }
}
CH93_start_war = {
 if = { limit = { country_exists = A01 country_exists = A03 NOT = { has_global_flag = ch93_16_a } A01 = { NOT = { has_country_flag = A01_expansion_resolved } } NOT = { has_war_with = A01 } }
  set_country_flag = JPI_tesla_ready
  A03_prepare_southern_war_effect = yes
  add_timed_idea = { idea = A03_southern_blitz days = 180 }
  declare_war_on = { target = A01 type = take_state_focus generator = { 1023 1024 } }
  A01 = { set_country_flag = A01_japanese_invasion_begun }
 }
}
''')
    write('common/on_actions/chronicle_1893.txt', 'on_actions = { on_startup = { effect = { CH93_tick = yes } } on_daily = { effect = { CH93_tick = yes } } }\n')
    write('common/ideas/chronicle_1893.txt', '''ideas = { country = {
 CH93_blockade = { picture = jpc_credit modifier = { industrial_capacity_factory = -0.05 supply_consumption_factor = 0.10 } }
 CH93_patrols = { picture = jpc_fleet modifier = { convoy_escort_efficiency = 0.10 } }
 CH93_embargo = { picture = jpc_credit modifier = { production_factory_efficiency_gain_factor = -0.10 } }
} }
''')
    write('tools/chronicle_1893_manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    integrate_calendar()
    print(f'Built {len(manifest)} dated choices and {len(manifest)} world notifications.')

def integrate_calendar():
    # The chronicle owns the ultimatum in 1893; old focus callbacks resume later.
    p = ROOT / 'common/scripted_effects/JPC_canonical.txt'
    s = p.read_text(encoding='utf-8-sig')
    needle = 'limit = { has_completed_focus = JPR_defence_budget'
    s = s.replace(needle, 'limit = { date > 1893.12.31 has_completed_focus = JPR_defence_budget')
    p.write_text(s, encoding='utf-8')
    p = ROOT / 'common/scripted_effects/borneo_war_effects.txt'
    s = p.read_text(encoding='utf-8-sig')
    s = s.replace(needle, 'limit = { date > 1893.12.31 has_completed_focus = JPR_defence_budget')
    p.write_text(s, encoding='utf-8')
    p = ROOT / 'common/scripted_effects/JPS_calendar_clocks.txt'
    s = p.read_text(encoding='utf-8-sig')
    start = s.index('JPS_align_opening_clocks_effect = {')
    end = s.index('JPS_align_war_clocks_effect = {', start)
    rows = ['JPS_align_opening_clocks_effect = {']
    day, deadline = datetime(1893, 1, 1), datetime(1893, 9, 1)
    while day < deadline:
        before, after = day-timedelta(days=1), day+timedelta(days=1)
        delta = (deadline-day).days-365
        fmt = lambda d: f'{d.year}.{d.month}.{d.day}'
        rows.append(f' if = {{ limit = {{ date > {fmt(before)} date < {fmt(after)} }} add_days_mission_timeout = {{ mission = A01_japanese_invasion_countdown days = {delta} }} A03 = {{ add_days_mission_timeout = {{ mission = A03_japanese_invasion_countdown days = {delta} }} }} }}')
        day += timedelta(days=1)
    rows.append('}\n')
    s = s[:start]+'\n'.join(rows)+s[end:]
    s = s.replace('limit = { has_active_mission = A03_japanese_invasion_countdown', 'limit = { date > 1893.12.31 has_active_mission = A03_japanese_invasion_countdown')
    p.write_text(s, encoding='utf-8')

def finalize_current_revision():
    main()
    if (ROOT / 'docs/chronicle_revision_source.json').exists() and (ROOT / 'common/national_focus/BLV_campaign.txt').exists():
        from apply_chronicle_revision import main as apply_revision
        apply_revision()

if __name__ == '__main__':
    finalize_current_revision()
