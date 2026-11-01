"""Build the author's 24-event 1895 continuation, preserving prior outcomes."""
from datetime import datetime,timedelta
import json,re
from build_chronicle_1893 import ROOT,write

SOURCE=ROOT/'docs/chronicle_1895_source.txt'
TAGS='A04 A10 A01 PHW A01 A06 A03 A02 PSL A02 A01 A10 A01 A01 A02 A06 A06 A03 A04 PHW A01 PHR A04 A04'.split()
GATES={2:'country_exists = A03 A03 = { controls_state = 327 }',5:'has_war_with = A03',9:'has_war_with = A03',13:'has_war_with = A03',14:'has_war_with = A03 1023 = { is_owned_by = A01 }',18:'controls_state = 327'}
E={
1:('CH95_restructure = yes','CH95_punish_clients = yes'),
2:('add_manpower = 2500 add_war_support = 0.06 A03 = { add_stability = -0.04 } add_timed_idea = { idea = CH95_uprising days = 90 }','add_manpower = 750 army_experience = 15 A03 = { add_fuel = -2500 }'),
3:('add_political_power = -35 army_experience = 20 add_timed_idea = { idea = CH95_local_officers days = 365 }','add_stability = -0.04 army_experience = 10 add_political_power = 20'),
4:('CH95_hawaii_republic = yes','CH95_hawaii_regency = yes'),
5:('CH94_kuching_dutch = yes','add_manpower = -600 A03 = { add_manpower = -300 army_experience = 10 }'),
6:('add_political_power = -40 navy_experience = 25 add_timed_idea = { idea = CH95_naval_reform days = 180 } A02 = { add_political_power = 20 }','add_political_power = 20 add_timed_idea = { idea = CH95_isolation days = 180 }'),
7:('add_political_power = -65 add_stability = 0.05 add_timed_idea = { idea = CH95_state_guarantee days = 180 }','add_stability = -0.08 add_timed_idea = { idea = CH95_naval_crisis days = 180 }'),
8:('add_political_power = 30 add_stability = -0.02 add_timed_idea = { idea = CH95_port_market days = 180 }','add_manpower = -400 add_stability = -0.05 navy_experience = 10'),
9:('CH94_sulu_cooperation = yes add_timed_idea = { idea = CH95_escorts days = 120 }','navy_experience = 20 A03 = { add_equipment_to_stockpile = { type = convoy_1 amount = -10 } } A10 = { add_equipment_to_stockpile = { type = convoy_1 amount = -5 } }'),
10:('CH95_mobile_tesla = yes','CH95_tesla_tower = yes'),
11:('add_political_power = -30 add_manpower = 2000 set_country_flag = CH95_aceh_autonomy','add_manpower = -700 add_stability = -0.05 army_experience = 10'),
12:('add_stability = 0.04 add_political_power = -20 add_equipment_to_stockpile = { type = convoy_1 amount = 5 }','add_stability = -0.05 add_manpower = -500 army_experience = 10'),
13:('A03 = { navy_experience = 20 add_fuel = -4000 } add_timed_idea = { idea = CH95_blockade days = 60 }','navy_experience = 25 add_fuel = -3000 A03 = { add_fuel = -6000 add_timed_idea = { idea = CH95_naval_crisis days = 90 } }'),
14:('add_manpower = -700 add_timed_idea = { idea = CH95_defence days = 60 }','CH95_brunei_retreat = yes'),
15:('add_political_power = -35 add_manpower = 1000 add_stability = 0.03 set_country_flag = CH95_ceylon_relief','add_stability = -0.04 add_timed_idea = { idea = CH95_refugees days = 90 }'),
16:('add_timed_idea = { idea = CH95_anathema days = 180 } add_war_support = 0.03','remove_ideas = CH94_anathema remove_ideas = CH95_anathema add_stability = 0.04 add_political_power = -20'),
17:('CH95_pobedonostsev_legacy = yes add_stability = 0.05','CH95_pobedonostsev_legacy = yes add_stability = -0.07 add_political_power = -25'),
18:('add_stability = -0.06 add_war_support = 0.04 A10 = { add_manpower = 750 add_war_support = 0.07 }','add_stability = 0.04 add_political_power = -30 A10 = { add_war_support = -0.04 }'),
19:('CH95_arms_embargo = yes','CH95_war_loans = yes'),
20:('remove_ideas = CH94_legion_raids remove_ideas = CH95_legion_raids set_country_flag = CH95_legion_truce add_stability = 0.04','add_timed_idea = { idea = CH95_legion_raids days = 120 } add_equipment_to_stockpile = { type = convoy_1 amount = -5 } navy_experience = 15'),
21:('add_stability = 0.04 add_political_power = -25 set_country_flag = CH95_admiral_compromise','add_stability = -0.07 navy_experience = -15 add_political_power = 30'),
22:('add_war_support = 0.04 add_stability = -0.03','CH94_haiti_cooperation = yes'),
23:('CH95_peace_conference = yes','set_global_flag = CH95_talks_rejected every_country = { limit = { OR = { tag = A01 tag = A03 tag = A10 } has_war = yes } add_war_support = 0.03 }'),
24:('every_country = { limit = { OR = { tag = A01 tag = A03 tag = A10 } has_war = yes } add_timed_idea = { idea = CH95_exhaustion days = 180 } add_war_support = -0.05 } set_global_flag = CH95_peace_ready','every_country = { limit = { OR = { tag = A01 tag = A03 tag = A10 } has_war = yes } add_war_support = 0.05 add_manpower = 1000 }'),
}
HELPERS='''
CH95_restructure = {
 add_political_power = -40
 WTN_initialize_effect = yes
 add_to_variable = { WTN_liquidity = -10 }
 WTN_update_ledger_effect = yes
 every_country = { limit = { has_country_flag = WTC_ledger_open NOT = { tag = A04 } check_variable = { WTC_debt > 0 } }
  add_to_variable = { WTC_debt = -10 }
  WTC_refresh_effect = yes
  add_stability = 0.02
 }
}
CH95_punish_clients = {
 add_political_power = 40
 every_country = { limit = { has_country_flag = WTC_ledger_open check_variable = { WTC_debt > 70 } }
  add_timed_idea = { idea = CH95_blockade days = 90 }
  add_stability = -0.03
 }
}
CH95_hawaii_republic = {
 if = { limit = { NOT = { has_country_flag = CH95_hawaii_settled } }
  if = { limit = { NOT = { has_government = democratic } } CH94_hawaiian_republic = yes }
  set_country_flag = CH95_hawaii_settled
  add_stability = 0.03
 }
}
CH95_hawaii_regency = {
 if = { limit = { has_character = PHW_canon_leader } retire_character = PHW_canon_leader }
 create_country_leader = { name = CH95_planter_council ideology = despotism expire = "1965.1.1.1" traits = { } }
 set_popularities = { neutrality = 70 democratic = 30 }
 set_politics = { ruling_party = neutrality elections_allowed = no }
 drop_cosmetic_tag = yes
 set_country_flag = CH95_hawaii_settled
 add_political_power = 25
}
CH95_mobile_tesla = {
 set_country_flag = CH94_tesla_prototype
 set_country_flag = CH95_tesla_mobile
 remove_ideas = CH95_tesla_tower
 add_ideas = CH95_tesla_mobile
 add_political_power = -40
}
CH95_tesla_tower = {
 set_country_flag = CH94_tesla_prototype
 set_country_flag = CH95_tesla_stationary
 remove_ideas = CH95_tesla_mobile
 add_ideas = CH95_tesla_tower
 add_political_power = -35
}
CH95_brunei_retreat = {
 if = { limit = { has_war_with = A03 1023 = { is_owned_by = A01 is_controlled_by = A01 } }
  1023 = { set_state_controller = A03 }
  add_manpower = 400
  add_war_support = -0.03
 }
}
CH95_pobedonostsev_legacy = {
 if = { limit = { has_character = A06_pobedonostsev } retire_character = A06_pobedonostsev }
 set_country_flag = CH94_pobedonostsev_dead
 set_country_flag = CH95_pobedonostsev_legacy_settled
 remove_ideas = CH94_anathema
 remove_ideas = CH95_anathema
}
CH95_arms_embargo = {
 every_country = { limit = { OR = { tag = A01 tag = A03 tag = A10 } has_war = yes }
  add_timed_idea = { idea = CH95_embargo days = 120 }
 }
}
CH95_war_loans = {
 WTN_initialize_effect = yes
 if = { limit = { check_variable = { WTN_liquidity > 19 } }
  add_to_variable = { WTN_liquidity = -20 }
  every_country = { limit = { OR = { tag = A01 tag = A03 } has_war = yes }
   WTC_initialize_effect = yes
   add_to_variable = { WTC_debt = 15 }
   add_political_power = 35
   add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 500 producer = A04 }
   WTC_refresh_effect = yes
  }
  WTN_update_ledger_effect = yes
  add_political_power = 30
 }
 else = { set_global_flag = ch95_19_inactive }
}
CH95_peace_conference = {
 set_global_flag = CH95_peace_conference_open
 add_political_power = -30
 every_country = { limit = { OR = { tag = A01 tag = A03 tag = A10 } has_war = yes }
  set_country_flag = CH95_invited_to_peace
  add_war_support = -0.04 add_stability = 0.02
 }
}
'''

IDEAS={
'uprising':('Всеобщее восстание на Лусоне','Массовое сопротивление усиливает мобилизацию.','recruitable_population_factor = 0.05'),
'local_officers':('Индонезийские офицеры KNIL','Местным офицерам открыто командование ротами.','army_org_regain = 0.05'),
'naval_reform':('Реформа русского флота','Британские инженеры помогают модернизировать флот.','navy_org_factor = 0.05'),
'isolation':('Отказ от иностранных технологий','Консервативные круги ограничивают обмен знаниями.','research_speed_factor = -0.04'),
'state_guarantee':('Государственная гарантия Мицубиси','Казна поддерживает работу промышленности.','industrial_capacity_factory = 0.05'),
'naval_crisis':('Флот без финансирования','Дефицит средств и потери сдерживают морские операции.','navy_org_factor = -0.10'),
'port_market':('Сингапурский договор','Компромисс с торговыми сетями расширяет оборот порта.','production_speed_industrial_complex_factor = 0.05'),
'escorts':('Координация морских рейдов','Общее планирование улучшает действия на торговых путях.','naval_coordination = 0.05'),
'tesla_mobile':('Корабельный глушитель Теслы','Мобильный прибор помогает работе экспедиций в море.','navy_org_factor = 0.04 research_speed_factor = 0.02'),
'tesla_tower':('Стационарная башня Теслы','Усиленная защита баз поддерживает исследования на островах.','army_defence_factor = 0.04 research_speed_factor = 0.03'),
'blockade':('Блокада клиентских островов','Перекрытые поставки затрудняют снабжение и производство.','supply_consumption_factor = 0.10 industrial_capacity_factory = -0.05'),
'defence':('Оборона Брунея','Гарнизон удерживает подготовленные позиции.','army_defence_factor = 0.05'),
'refugees':('Закрытые порты Цейлона','Кризис беженцев усиливает напряжение.','stability_factor = -0.03'),
'anathema':('Новый церковный запрет','Собор осуждает глушители Теслы.','research_speed_factor = -0.05'),
'embargo':('Оружейное эмбарго ВТП','Ограничения поставок замедляют вооружение.','production_factory_efficiency_gain_factor = -0.10'),
'legion_raids':('Бой с Легионом','Морские набеги нарушают снабжение Гавайев.','supply_consumption_factor = 0.10'),
'exhaustion':('Истощение 1895 года','Потери и длительная война подрывают производство и поддержку войны.','industrial_capacity_factory = -0.05 war_support_factor = -0.05'),
}

def main():
    blocks=re.split(r'\*\*(\d+)\. (.*?)\*\*',SOURCE.read_text(encoding='utf-8-sig'))
    events=['add_namespace = ch95\n']; loc=['l_russian:']; manifest=[]
    schedule=['CH95_tick = {',' if = { limit = { date > 1894.12.31 date < 1896.1.1 }']
    def l(k,v):loc.append(f' {k}:0 "{v.replace(chr(34),chr(39))}"')
    for pos in range(1,len(blocks),3):
        n,title,body=int(blocks[pos]),blocks[pos+1],blocks[pos+2]
        date=re.search(r'\*\*Дата:\*\* (\d+\.\d+\.\d+)',body)[1]
        dt=datetime.strptime(date,'%d.%m.%Y'); prev=dt-timedelta(days=1)
        choices=re.findall(r'\*\*Вариант [12]:\*\* «(.*?)» \((.*?)\)\.',body)
        canon=re.search(r'\*\*Канон:\*\* (.*?)\.',body)[1]
        ci=next(i for i,c in enumerate(choices) if c[0]==canon)
        assert len(choices)==2 and dt.year==1895
        key,tag=f'ch95.{n}',TAGS[n-1]
        schedule.append(f'  if = {{ limit = {{ date > {prev.year}.{prev.month}.{prev.day} NOT = {{ has_global_flag = ch95_queued_{n} }} }} set_global_flag = ch95_queued_{n} if = {{ limit = {{ country_exists = {tag} }} {tag} = {{ country_event = {{ id = {key} }} }} }} else = {{ set_global_flag = ch95_{n}_skipped every_country = {{ limit = {{ is_ai = no }} country_event = {{ id = ch95.{200+n} }} }} }} }}')
        l(key+'.t',title); l(key+'.d',date+'. '+' '.join(c[1]+'.' for c in choices))
        special=''
        if n==4:
            l(key+'.continued_t','Гавайский вопрос о престолонаследии')
            l(key+'.continued_d',date+'. Калакауа умер в прошлом году. Гавайи решают, закрепить ли республику или передать власть совету плантаторов.')
            special='has_global_flag = ch94_12_a has_global_flag = ch94_12_b'
        if n==17:
            l(key+'.continued_t','Наследие Победоносцева')
            l(key+'.continued_d',date+'. После смерти Победоносцева его сторонники вновь раскололи церковь. Александр III решает, укрепить ли светскую власть или уступить давлению церковных фракций.')
            special='has_country_flag = CH94_pobedonostsev_dead'
        if n==6:
            choices[1]=(choices[1][0],'Консервативные церковные круги выступают против иностранных технологий')
            l(key+'.d_after',date+'. Александр III рассматривает модернизацию флота с британской помощью. После смерти Победоносцева его сторонники продолжают выступать против иностранных технологий.')
        if n==16:
            l(key+'.d_after',date+'. Новый собор рассматривает глушители Теслы. После смерти Победоносцева его сторонники требуют анафемы, но Александр III может запретить вмешательство церкви в науку.')
            choices[0]=(choices[0][0],'Сторонники Победоносцева добиваются осуждения Теслы и его глушителей')
        header=f'country_event = {{\n id = {key}\n'
        if special:
            cond=f'OR = {{ {special} }}' if n==4 else special
            header+=f' title = {{ text = {key}.continued_t trigger = {{ {cond} }} }} title = {{ text = {key}.t trigger = {{ NOT = {{ {cond} }} }} }}\n desc = {{ text = {key}.continued_d trigger = {{ {cond} }} }} desc = {{ text = {key}.d trigger = {{ NOT = {{ {cond} }} }} }}\n'
        elif n in (6,16):
            header+=f' title = {key}.t\n desc = {{ text = {key}.d_after trigger = {{ has_country_flag = CH94_pobedonostsev_dead }} }} desc = {{ text = {key}.d trigger = {{ NOT = {{ has_country_flag = CH94_pobedonostsev_dead }} }} }}\n'
        else:header+=f' title = {key}.t\n desc = {key}.d\n'
        header+=' picture = GFX_1896_event_talks\n is_triggered_only = yes\n fire_only_once = yes\n timeout_days = 3'
        events.append(header)
        for i,(label,desc) in enumerate(choices):
            letter='ab'[i]; l(key+'.'+letter,label)
            if n==4:desc=('Гавайи утверждают республиканское правление' if i==0 else 'Власть на Гавайях передаётся совету плантаторов')
            if n==17:desc=('Светская власть укрепляется после ухода Победоносцева' if i==0 else 'Споры о наследии Победоносцева раскалывают церковь')
            l(key+'.news_'+letter,f'{date}. Решение: «{label}». {desc}.')
            effect=E[n][i]
            if n in GATES:effect=f'if = {{ limit = {{ {GATES[n]} }} {effect} }} else = {{ set_global_flag = ch95_{n}_inactive }}'
            events.append(f' option = {{ name = {key}.{letter} ai_chance = {{ factor = {100 if i==ci else 0} }} set_global_flag = ch95_{n}_{letter}\n {effect}\n hidden_effect = {{ every_country = {{ limit = {{ is_ai = no NOT = {{ tag = ROOT }} }} country_event = {{ id = ch95.{100+n} }} }} }}\n }}')
        events.append('}\n')
        l(key+'.inactive',date+'. Изменение обстановки сделало этот план неосуществимым. Операция не проводилась.')
        l(key+'.absent',date+'. Участник этого эпизода больше не существует как отдельная держава. Историческая развилка утратила актуальность.')
        news_title=key+'.continued_t' if special else key+'.t'
        events.append(f'country_event = {{ id = ch95.{100+n} title = {news_title} desc = {{ text = {key}.inactive trigger = {{ has_global_flag = ch95_{n}_inactive }} }} desc = {{ text = {key}.news_a trigger = {{ has_global_flag = ch95_{n}_a NOT = {{ has_global_flag = ch95_{n}_inactive }} }} }} desc = {{ text = {key}.news_b trigger = {{ has_global_flag = ch95_{n}_b NOT = {{ has_global_flag = ch95_{n}_inactive }} }} }} picture = GFX_1896_event_talks is_triggered_only = yes option = {{ name = ch95.read }} }}')
        events.append(f'country_event = {{ id = ch95.{200+n} title = {key}.t desc = {key}.absent picture = GFX_1896_event_talks is_triggered_only = yes option = {{ name = ch95.read }} }}')
        manifest.append(dict(id=n,date=date,title=title,tag=tag,canonical=ci+1))
    assert len(manifest)==24
    schedule+=[' }','}']; l('ch95.read','Мир меняется.'); l('CH95_planter_council','Совет гавайских плантаторов')
    ideas=['ideas = { country = {']
    for key,(name,desc,modifier) in IDEAS.items():
        l('CH95_'+key,name); l('CH95_'+key+'_desc',desc)
        ideas.append(f' CH95_{key} = {{ picture = jpc_credit modifier = {{ {modifier} }} }}')
    ideas.append('} }')
    write('events/chronicle_1895.txt','\n'.join(events)+'\n')
    write('common/scripted_effects/chronicle_1895.txt','\n'.join(schedule)+'\n'+HELPERS)
    write('common/on_actions/chronicle_1895.txt','on_actions = { on_startup = { effect = { CH95_tick = yes } } on_daily = { effect = { CH95_tick = yes } } }\n')
    write('common/ideas/chronicle_1895.txt','\n'.join(ideas)+'\n')
    write('localisation/russian/chronicle_1895_l_russian.yml','\n'.join(loc)+'\n',True)
    write('tools/chronicle_1895_manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('Built 24 choices, 24 outcome reports and 24 absent-actor reports for 1895.')

def finalize_current_revision():
    main()
    if (ROOT / 'docs/chronicle_revision_source.json').exists() and (ROOT / 'common/national_focus/BLV_campaign.txt').exists():
        from apply_chronicle_revision import main as apply_revision
        apply_revision()

if __name__=='__main__':finalize_current_revision()
