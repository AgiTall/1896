"""Author's 1894 timeline: dated choices, outcomes and campaign integration."""
from pathlib import Path
from datetime import datetime, timedelta
import json, re
from build_chronicle_1893 import ROOT, write

SOURCE = ROOT/'docs/chronicle_1894_source.txt'
TAGS = 'A03 A01 A08 A01 A03 A03 A02 A06 A04 A10 A02 PHW A10 A03 A01 A05 A01 PHR A01 A02 A10 A06 A01 A03 A01 PSL A03 PHW A10 A02 A10 A06 A02 A04 A01 A04'.split()
WAR_GATES = {13: 'has_war_with = A03', 14: 'has_war_with = A10', 17: 'has_war_with = A03', 19: 'has_war_with = A03', 24: 'has_war_with = A10', 25: 'has_war_with = A03 334 = { is_owned_by = A01 }', 35: 'has_war_with = A03'}
E = {
1: ('add_fuel = -4000 navy_experience = 15 add_equipment_to_stockpile = { type = convoy_1 amount = -5 } add_timed_idea = { idea = CH94_escorts days = 90 }', 'add_equipment_to_stockpile = { type = convoy_1 amount = -10 } navy_experience = 25'),
2: ('add_stability = 0.04 add_political_power = -25', 'add_stability = -0.08 navy_experience = -15 add_political_power = 35'),
3: ('add_timed_idea = { idea = CH94_northern_faith days = 365 } add_war_support = 0.06', 'add_manpower = 1500 add_political_power = 25'),
4: ('set_country_flag = CH94_back_wilhelmina add_political_power = -40 add_timed_idea = { idea = CH94_royal_campaign days = 180 }', 'set_country_flag = CH94_keep_regency add_stability = 0.04 add_political_power = 20'),
5: ('add_stability = -0.06 add_war_support = 0.04 A10 = { add_manpower = 1000 add_war_support = 0.08 }', 'add_stability = 0.04 add_political_power = -35 A10 = { add_war_support = -0.05 }'),
6: ('add_political_power = -65 add_stability = 0.05 add_timed_idea = { idea = CH94_credit days = 120 }', 'add_stability = -0.08 add_timed_idea = { idea = CH94_naval_shortage days = 180 }'),
7: ('A01 = { remove_ideas = CH93_blockade add_timed_idea = { idea = CH94_corridors days = 90 } } add_political_power = -25', 'add_political_power = 25 A01 = { add_stability = -0.02 }'),
8: ('add_timed_idea = { idea = CH94_anathema days = 365 } add_war_support = 0.04', 'remove_ideas = CH94_anathema add_stability = 0.04 add_political_power = -25'),
9: ('add_political_power = -50 A02 = { add_manpower = 2000 add_stability = 0.02 }', 'A02 = { add_political_power = -30 add_tech_bonus = { name = CH94_research bonus = 0.25 uses = 1 category = industry } }'),
10: ('CH94_open_second_front = yes', 'set_country_flag = A10_borneo_opportunity_refused add_stability = 0.04 add_manpower = 1000'),
11: ('add_political_power = 35 add_stability = -0.02 add_timed_idea = { idea = CH94_singapore_market days = 180 }', 'add_stability = -0.06 add_manpower = -500 navy_experience = 10'),
12: ('CH94_hawaiian_republic = yes', 'CH94_hawaiian_succession = yes add_stability = -0.10 add_war_support = 0.06 add_timed_idea = { idea = CH94_legion_raids days = 120 }'),
13: ('army_experience = 20 add_manpower = -700 add_timed_idea = { idea = CH94_assault days = 45 }', 'add_timed_idea = { idea = CH94_siege days = 90 } A03 = { add_fuel = -3000 }'),
14: ('add_timed_idea = { idea = CH94_redeployment days = 90 } A01 = { add_timed_idea = { idea = CH94_respite days = 90 } } A10 = { add_war_support = -0.02 }', 'add_timed_idea = { idea = CH94_assault days = 60 } A10 = { add_timed_idea = { idea = CH94_respite days = 60 } }'),
15: ('add_equipment_to_stockpile = { type = infantry_equipment_0 amount = -500 } if = { limit = { country_exists = ATJ } ATJ = { add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 500 producer = A01 } } } add_manpower = 1000', 'add_manpower = -700 add_stability = -0.05 army_experience = 10'),
16: ('add_timed_idea = { idea = CH94_iron_legion days = 365 } navy_experience = 30 add_equipment_to_stockpile = { type = convoy_1 amount = 15 }', 'PHW = { add_timed_idea = { idea = CH94_legion_raids days = 180 } add_stability = -0.04 } navy_experience = 15'),
17: ('CH94_kuching_dutch = yes', 'if = { limit = { has_war_with = A03 } add_manpower = -700 A03 = { add_manpower = -400 army_experience = 10 } }'),
18: ('add_war_support = 0.05 add_stability = -0.04 A03 = { add_war_support = 0.04 }', 'CH94_haiti_cooperation = yes'),
19: ('if = { limit = { has_war_with = A03 } add_fuel = -6000 A03 = { navy_experience = 20 add_timed_idea = { idea = CH94_assault days = 30 } } }', 'if = { limit = { has_war_with = A03 } navy_experience = 25 add_fuel = -4000 A03 = { add_fuel = -8000 add_timed_idea = { idea = CH94_naval_shortage days = 90 } } }'),
20: ('set_country_flag = CH94_tesla_prototype add_tech_bonus = { name = CH94_research bonus = 0.5 uses = 1 category = industry } add_timed_idea = { idea = CH94_tesla days = 180 }', 'set_country_flag = CH94_tesla_accident add_political_power = -50 add_stability = -0.03'),
21: ('add_stability = 0.04 add_political_power = -20 add_equipment_to_stockpile = { type = convoy_1 amount = 5 }', 'add_stability = -0.05 add_manpower = -500 army_experience = 10'),
22: ('A02 = { add_political_power = -30 } add_manpower = 1000 add_stability = 0.05 add_timed_idea = { idea = CH94_corridors days = 90 }', 'add_stability = -0.08 add_manpower = -1000 add_political_power = 20'),
23: ('add_political_power = -40 add_stability = 0.05', 'add_stability = -0.08 add_manpower = -500 add_war_support = 0.04'),
24: ('if = { limit = { has_war_with = A10 } A10 = { add_timed_idea = { idea = CH94_blockade days = 120 } } add_fuel = -5000 }', 'if = { limit = { has_war_with = A10 } A10 = { add_equipment_to_stockpile = { type = convoy_1 amount = -8 } } add_fuel = -2000 }'),
25: ('CH94_burn_oil = yes', 'CH94_capture_oil = yes'),
26: ('CH94_sulu_cooperation = yes', 'navy_experience = 15 add_political_power = 25'),
27: ('CH94_ito_emergency = yes', 'add_war_support = -0.06 add_stability = 0.03 A09 = { add_political_power = 50 }'),
28: ('add_timed_idea = { idea = CH94_legion_raids days = 90 } add_stability = -0.04', 'A03 = { add_equipment_to_stockpile = { type = convoy_1 amount = -15 } add_timed_idea = { idea = CH94_legion_raids days = 90 } }'),
29: ('add_stability = -0.06 add_manpower = -500 PCB = { add_stability = -0.05 } army_experience = 10', 'add_political_power = -35 add_stability = 0.04 PCB = { add_stability = 0.05 }'),
30: ('CH94_tesla_secret = yes', 'CH94_tesla_sale = yes'),
31: ('add_war_support = 0.10 add_timed_idea = { idea = CH94_assault days = 90 } add_stability = -0.03', 'add_stability = 0.05 add_political_power = -25 add_war_support = -0.04'),
32: ('CH94_pobedonostsev_dies = yes add_stability = 0.06', 'CH94_pobedonostsev_dies = yes add_stability = -0.08 add_political_power = -30'),
33: ('add_political_power = -30 add_stability = 0.04 add_equipment_to_stockpile = { type = convoy_1 amount = 5 }', 'add_political_power = 15 add_timed_idea = { idea = CH94_blockade days = 60 } add_stability = -0.03'),
34: ('set_global_flag = CH94_peace_talks every_country = { limit = { OR = { tag = A01 tag = A03 tag = A10 } } add_war_support = -0.03 add_stability = 0.02 } add_political_power = -25', 'every_country = { limit = { OR = { tag = A01 tag = A03 tag = A10 } } add_war_support = 0.03 }'),
35: ('if = { limit = { has_war_with = A03 } A03 = { add_timed_idea = { idea = CH94_assault days = 45 } add_manpower = -500 } }', 'if = { limit = { has_war_with = A03 } add_timed_idea = { idea = CH94_defence days = 90 } army_experience = 15 }'),
36: ('every_country = { limit = { OR = { tag = A01 tag = A03 tag = A10 } has_war = yes } add_timed_idea = { idea = CH94_exhaustion days = 180 } }', 'every_country = { limit = { OR = { tag = A01 tag = A03 tag = A10 } } add_war_support = 0.05 add_manpower = 1000 }'),
}

HELPERS = '''
CH94_open_second_front = {
 if = { limit = { country_exists = A03 is_subject = no NOT = { has_capitulated = yes } NOT = { has_war_with = A03 } NOT = { has_country_flag = A10_archipelago_peace_signed } NOT = { has_country_flag = A10_manila_peace_signed } NOT = { has_country_flag = A10R_defensive_armistice } }
  set_country_flag = A10_borneo_opportunity_taken
  add_war_support = 0.10
  declare_war_on = { target = A03 type = annex_everything }
 }
}
CH94_hawaiian_succession = {
 if = { limit = { has_character = PHW_canon_leader } retire_character = PHW_canon_leader }
}
CH94_hawaiian_republic = {
 CH94_hawaiian_succession = yes
 create_country_leader = { name = CH94_hawaii_council ideology = liberalism expire = "1965.1.1" traits = { } }
 set_popularities = { democratic = 70 neutrality = 30 }
 set_politics = { ruling_party = democratic elections_allowed = yes }
 set_cosmetic_tag = PHW_REPUBLIC
 add_stability = 0.05
}
CH94_kuching_dutch = {
 if = { limit = { has_war_with = A03 333 = { is_owned_by = A01 is_controlled_by = A03 } }
  333 = { set_state_controller = A01 }
  add_manpower = -500 army_experience = 20
 }
}
CH94_haiti_cooperation = {
 add_stability = 0.04
 if = { limit = { country_exists = A10 } give_military_access = A10 A10 = { give_military_access = PHR add_manpower = 1000 add_political_power = 20 } }
}
CH94_sulu_cooperation = {
 if = { limit = { country_exists = A10 } give_military_access = A10 A10 = { give_military_access = PSL } }
 if = { limit = { country_exists = A03 A10 = { has_war_with = A03 } NOT = { has_war_with = A03 } is_subject = no } declare_war_on = { target = A03 type = annex_everything } }
 add_war_support = 0.05
}
CH94_burn_oil = {
 if = { limit = { has_war_with = A03 334 = { is_owned_by = A01 is_controlled_by = A01 } NOT = { has_global_flag = CH94_oil_destroyed } }
  set_global_flag = CH94_oil_destroyed
  334 = { add_resource = { type = oil amount = -15 } }
  add_fuel = -5000
 }
}
CH94_capture_oil = {
 if = { limit = { has_war_with = A03 334 = { is_owned_by = A01 } NOT = { has_global_flag = CH94_oil_destroyed } }
  334 = { set_state_controller = A03 }
  A03 = { add_fuel = 5000 }
 }
}
CH94_ito_emergency = {
 if = { limit = { has_character = A03_naval_commander }
  add_country_leader_role = { character = A03_naval_commander promote_leader = yes country_leader = { ideology = despotism expire = "1965.1.1" traits = { } } }
 }
 set_country_flag = CH94_martial_law
 add_war_support = 0.06 add_stability = -0.04
}
CH94_tesla_secret = {
 if = { limit = { has_country_flag = CH94_tesla_prototype }
  remove_ideas = CH94_tesla
  add_ideas = CH94_tesla
 }
 else = { add_political_power = -40 add_tech_bonus = { name = CH94_research bonus = 0.25 uses = 1 category = industry } }
}
CH94_tesla_sale = {
 if = { limit = { has_country_flag = CH94_tesla_prototype country_exists = A04 }
  add_political_power = 75
  A04 = { add_political_power = -75 add_ideas = CH94_tesla }
 }
 else = { add_political_power = -25 A04 = { add_tech_bonus = { name = CH94_research bonus = 0.25 uses = 1 category = industry } } }
}
CH94_pobedonostsev_dies = {
 if = { limit = { has_character = A06_pobedonostsev } retire_character = A06_pobedonostsev }
 remove_ideas = CH94_anathema
 set_country_flag = CH94_pobedonostsev_dead
}
'''

IDEAS = {
'escorts': ('Охрана транспортов', 'Конвойные силы поддерживают снабжение.', 'convoy_escort_efficiency = 0.15'),
'northern_faith': ('Проповедь Сайго', 'Религиозный подъём на Хоккайдо укрепляет готовность к войне.', 'war_support_factor = 0.05 recruitable_population_factor = 0.05'),
'royal_campaign': ('Сторонники Вильгельмины', 'Двор собирает сторонников юной королевы.', 'political_power_gain = 0.15'),
'credit': ('Экстренные кредиты Мицубиси', 'Государство поддерживает производство за счёт казны.', 'industrial_capacity_factory = 0.05'),
'naval_shortage': ('Кризис снабжения флота', 'Потери и нехватка средств сдерживают морские операции.', 'navy_org_factor = -0.10'),
'corridors': ('Гуманитарные коридоры', 'Морские поставки облегчают положение населения и армии.', 'supply_consumption_factor = -0.05'),
'anathema': ('Анафема Тесле', 'Церковь препятствует внедрению новых технологий.', 'research_speed_factor = -0.05'),
'singapore_market': ('Сингапурский город-базар', 'Соглашение с торговыми сетями расширяет оборот порта.', 'production_speed_industrial_complex_factor = 0.05'),
'legion_raids': ('Набеги Легиона', 'Нападения на торговые пути повышают стоимость снабжения.', 'supply_consumption_factor = 0.10'),
'siege': ('Осада Манилы', 'Армия концентрирует силы для длительной осады.', 'max_planning_factor = 0.10'),
'assault': ('Подготовка штурма', 'Командование сосредоточило резервы для наступления.', 'army_attack_factor = 0.05'),
'redeployment': ('Переброска на Филиппины', 'Перевозка частей создаёт временные трудности со снабжением.', 'supply_consumption_factor = 0.10'),
'respite': ('Передышка на фронте', 'Ослабление давления позволяет восстановить силы.', 'army_org_regain = 0.05'),
'iron_legion': ('Железный Легион', 'Объединение американских морских сил улучшает координацию.', 'naval_coordination = 0.05'),
'tesla': ('Глушитель Теслы', 'Работающий прототип поддерживает исследования и организацию экспедиций.', 'research_speed_factor = 0.03'),
'blockade': ('Тотальная блокада', 'Нарушение поставок снижает выпуск и осложняет снабжение.', 'industrial_capacity_factory = -0.05 supply_consumption_factor = 0.10'),
'defence': ('Оборона южного Борнео', 'Войска закрепляются на подготовленных позициях.', 'army_defence_factor = 0.05'),
'exhaustion': ('Истощение войны', 'Продолжительные боевые действия подрывают поддержку войны и производство.', 'war_support_factor = -0.05 industrial_capacity_factory = -0.05'),
}

def main():
    assert SOURCE.exists(), SOURCE
    blocks = re.split(r'\*\*(\d+)\. (.*?)\*\*', SOURCE.read_text(encoding='utf-8-sig'))
    events, loc = ['add_namespace = ch94\n'], ['l_russian:']
    scheduler = ['CH94_tick = {', ' if = { limit = { date > 1893.12.31 date < 1895.1.1 }']
    manifest = []
    def l(key, value):
        loc.append(f' {key}:0 "{value.replace(chr(34), chr(39))}"')
    for pos in range(1, len(blocks), 3):
        n, title, body = int(blocks[pos]), blocks[pos+1], blocks[pos+2]
        date = re.search(r'\*\*Дата:\*\* (\d+\.\d+\.\d+)', body)[1]
        dt = datetime.strptime(date, '%d.%m.%Y')
        choices = re.findall(r'\*\*Вариант [12]:\*\* «(.*?)» \((.*?)\)\.', body)
        canon = re.search(r'\*\*Канон:\*\* (.*?)\.', body)[1].split(' (')[0]
        # The author's short "Союз" names the longer option at event 26.
        canonical = next(i for i,c in enumerate(choices) if c[0] == canon or (n == 26 and i == 0 and canon == 'Союз'))
        assert len(choices) == 2 and dt.year == 1894
        tag, key, prev = TAGS[n-1], f'ch94.{n}', dt-timedelta(days=1)
        scheduler.append(f'  if = {{ limit = {{ date > {prev.year}.{prev.month}.{prev.day} NOT = {{ has_global_flag = ch94_queued_{n} }} }} set_global_flag = ch94_queued_{n} if = {{ limit = {{ country_exists = {tag} }} {tag} = {{ country_event = {{ id = {key} }} }} }} else = {{ set_global_flag = ch94_{n}_skipped every_country = {{ limit = {{ is_ai = no }} country_event = {{ id = ch94.{200+n} }} }} }} }}')
        l(key+'.t', title)
        l(key+'.d', f'{date}. '+ ' '.join(c[1]+'.' for c in choices))
        events.append(f'country_event = {{\n id = {key}\n title = {key}.t\n desc = {key}.d\n picture = GFX_1896_event_talks\n is_triggered_only = yes\n fire_only_once = yes\n timeout_days = 3')
        for i,(label,desc) in enumerate(choices):
            letter = 'ab'[i]
            l(key+'.'+letter, label)
            l(key+'.news_'+letter, f'{date}. {title}. Решение: «{label}». {desc}.')
            effect = E[n][i]
            if n in WAR_GATES:
                effect = f'if = {{ limit = {{ {WAR_GATES[n]} }} {effect} }} else = {{ set_global_flag = ch94_{n}_inactive }}'
            events.append(f' option = {{ name = {key}.{letter} ai_chance = {{ factor = {100 if i == canonical else 0} }} set_global_flag = ch94_{n}_{letter}\n {effect}\n hidden_effect = {{ every_country = {{ limit = {{ is_ai = no NOT = {{ tag = ROOT }} }} country_event = {{ id = ch94.{100+n} }} }} }}\n }}')
        events.append('}\n')
        l(key+'.inactive', f'{date}. {title}. Изменение военной обстановки сделало эту операцию неактуальной. Боевые действия по этому плану не проводились.')
        events.append(f'country_event = {{ id = ch94.{100+n} title = {key}.t desc = {{ text = {key}.inactive trigger = {{ has_global_flag = ch94_{n}_inactive }} }} desc = {{ text = {key}.news_a trigger = {{ has_global_flag = ch94_{n}_a NOT = {{ has_global_flag = ch94_{n}_inactive }} }} }} desc = {{ text = {key}.news_b trigger = {{ has_global_flag = ch94_{n}_b NOT = {{ has_global_flag = ch94_{n}_inactive }} }} }} picture = GFX_1896_event_talks is_triggered_only = yes option = {{ name = ch94.read }} }}')
        # An eliminated actor gets a neutral report, with no powers given to a random state.
        l(key+'.absent', f'{date}. {title}. Из-за изменения политической карты участник этого эпизода больше не существует как отдельная держава. Историческая развилка утратила актуальность.')
        events.append(f'country_event = {{ id = ch94.{200+n} title = {key}.t desc = {key}.absent picture = GFX_1896_event_talks is_triggered_only = yes immediate = {{ set_global_flag = ch94_{n}_skipped }} option = {{ name = ch94.read }} }}')
        manifest.append(dict(id=n, date=date, title=title, tag=tag, canonical=canonical+1))
    scheduler += [' }', '}']
    l('ch94.read', 'Мир меняется.')
    l('CH94_research', 'Исследования Теслы')
    l('CH94_hawaii_council', 'Совет Гавайской республики')
    for suffix in ('', '_DEF', '_democratic', '_democratic_DEF'):
        l('PHW_REPUBLIC'+suffix, 'Гавайская республика')
    l('PHW_REPUBLIC_ADJ', 'Гавайск.')
    ideas = ['ideas = { country = {']
    for key,(name,desc,modifier) in IDEAS.items():
        l('CH94_'+key,name); l('CH94_'+key+'_desc',desc)
        ideas.append(f' CH94_{key} = {{ picture = jpc_credit modifier = {{ {modifier} }} }}')
    ideas.append('} }')
    write('events/chronicle_1894.txt','\n'.join(events)+'\n')
    write('common/scripted_effects/chronicle_1894.txt','\n'.join(scheduler)+'\n'+HELPERS)
    write('common/on_actions/chronicle_1894.txt','on_actions = { on_startup = { effect = { CH94_tick = yes } } on_daily = { effect = { CH94_tick = yes } } }\n')
    write('common/ideas/chronicle_1894.txt','\n'.join(ideas)+'\n')
    write('localisation/russian/chronicle_1894_l_russian.yml','\n'.join(loc)+'\n',True)
    write('tools/chronicle_1894_manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    integrate()
    print(f'Built {len(manifest)} choices, 36 outcome reports and 36 absent-actor reports for 1894.')

def integrate():
    p = ROOT/'events/A10_philippines.txt'
    text = p.read_text(encoding='utf-8-sig')
    # Avoid the existing seven-days-after-Borneo automatic second front.
    needle = 'trigger = {\n  tag = A10'
    text = text.replace(needle, 'trigger = {\n  date > 1894.12.31\n  tag = A10', 1)
    p.write_text(text, encoding='utf-8')

def finalize_current_revision():
    main()
    if (ROOT / 'docs/chronicle_revision_source.json').exists() and (ROOT / 'common/national_focus/BLV_campaign.txt').exists():
        from apply_chronicle_revision import main as apply_revision
        apply_revision()

if __name__ == '__main__':
    finalize_current_revision()
