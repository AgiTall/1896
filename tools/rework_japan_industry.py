"""Install the author's branching industry once, preserving the surrounding campaign."""
from pathlib import Path
import re
import shutil
from clarify_japan_branches import blocks

R = Path(__file__).resolve().parents[1]
REMOVED = {'JPC_osaka_orders', 'JPC_war_workshops', 'JPC_pledged_yards', 'JPC_convoy_budget', 'JPC_replace_losses'}

def write(path, text):
    p = R / path
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        backup = R / 'tools/backups/japan_scarlet_20261019' / path
        if not backup.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, backup)
    p.write_text(text, encoding='utf-8-sig' if p.suffix == '.yml' else 'utf-8', newline='\n')

def edit(path, old, new):
    s = (R / path).read_text(encoding='utf-8-sig')
    assert old in s, (path, old)
    write(path, s.replace(old, new, 1))

LOC = {}
def loc(key, ru, en):
    LOC[key] = (ru, en)

def factory(state, kind, levels=1):
    return f'if = {{ limit = {{ owns_state = {state} }} {state} = {{ add_extra_state_shared_building_slots = {levels} add_building_construction = {{ type = {kind} level = {levels} instant_build = yes }} }} }}'

def node(name, ru, en, desc, endesc, x, y, parents, reward, cost=3, opposite=None, icon='GFX_goal_unique_A03_industrial_power', available=''):
    fid = 'JPI_' + name
    loc(fid, ru, en); loc(fid+'_desc', desc, endesc)
    parent = ' '.join('focus = '+p for p in parents.split())
    return f''' focus = {{
  id = {fid}
  icon = {icon}
  x = {x} y = {y} cost = {cost}
  prerequisite = {{ {parent} }}
  {'mutually_exclusive = { focus = JPI_'+opposite+' }' if opposite else ''}
  {'available = { '+available+' }' if available else ''}
  cancel_if_invalid = yes
  search_filters = {{ FOCUS_FILTER_INDUSTRY FOCUS_FILTER_NAVY }}
  ai_will_do = {{ factor = 20 }}
  completion_reward = {{ {reward} }}
 }}
'''

def main():
    path = 'common/national_focus/a03_focus.txt'
    source = (R/path).read_text(encoding='utf-8-sig')
    if 'id = JPI_closed_ports' in source:
        print('Scarlet industry already installed; edit current files directly.'); return
    kept=[]
    for _,_,b in blocks(source):
        fid=re.search(r'\bid\s*=\s*(\w+)',b)[1]
        if fid in REMOVED: continue
        x=int(re.search(r'\bx\s*=\s*(-?\d+)',b)[1]); y=int(re.search(r'\by\s*=\s*(\d+)',b)[1])
        if x>=8: x+=8
        if y>=6: y+=5
        b=re.sub(r'\bx\s*=\s*-?\d+',f'x = {x}',b,count=1)
        b=re.sub(r'\by\s*=\s*\d+',f'y = {y}',b,count=1)
        if fid=='JPD_industrial_power':
            b=b.replace('focus = JPC_replace_losses','focus = JPI_standard_node').replace('focus = JPC_convoy_budget','focus = JPI_scarlet_sails')
        if fid=='JPC_batavia_demands':
            b=b.replace('prerequisite = { focus = JPR_defence_budget }','prerequisite = { focus = JPR_defence_budget }\n prerequisite = { focus = JPI_southern_push }')
        if fid in {'JPF_madeira_table','JPC_wtc_mission'}:
            b=b.replace('available = {','available = { has_completed_focus = JPI_japanese_terms ',1)
        kept.append(' '+b)
    nodes=[]
    def add(*args,**kwargs): nodes.append(node(*args,**kwargs))
    add('closed_ports','Закрытые порты','Closed Ports',
        'Чужие контракты закрыты. Быстро строим собственные мастерские, принимая низкую точность станков. Новые договоры и кредиты ВТП недоступны; прежние долги остаются.',
        'Reject foreign contracts. Domestic workshops open quickly but lack precision. New WTC contracts and loans are blocked; existing debts remain.',2,2,'JPX_sea',
        'set_country_flag = JPI_autarky add_ideas = JPI_rough_industry '+factory(532,'arms_factory'),cost=2,opposite='japanese_terms')
    add('japanese_terms','Условия Японии','Japan’s Terms',
        'Палата получит заказ только по нашей цене. Редкие материалы поступят в японские порты, но списки закупок станут доступны её наблюдателям.',
        'The Chamber must accept our prices. Rare materials reach Japan, but its observers gain access to our procurement lists.',10,2,'JPX_sea',
        'set_country_flag = JPI_chamber_lists add_ideas = JPI_selective_imports add_political_power = -25',opposite='closed_ports')
    add('raw_register','Реестр сырья','Raw Materials Register',
        'Сводим внутренние запасы в единый реестр. Шахты и мастерские смогут работать без посредничества Палаты.',
        'Inventory domestic supplies so mines and workshops can operate without the Chamber.',2,3,'JPI_closed_ports',
        'add_tech_bonus = { name = JPI_raw_register bonus = 0.5 uses = 1 category = industry } add_political_power = 25',cost=2)
    add('unsigned_contracts','Контракты без подписи','Unsigned Contracts',
        'Заказы оформляют торговые дома. В порту появляются вольфрам и хром, а Палата сохраняет копии закупочных ведомостей.',
        'Trading houses place the orders. Tungsten and chromium reach our port; the Chamber retains copies of the manifests.',10,3,'JPI_japanese_terms',
        'if = { limit = { owns_state = 531 } 531 = { add_resource = { type = tungsten amount = 4 } add_resource = { type = chromium amount = 4 } } } set_country_flag = JPI_unsigned_orders',cost=2)
    add('kyushu_coal','Уголь Кюсю','Kyushu Coal',
        'Угольные причалы быстро снабдят паровую эскадру. Этот путь укрепляет тяжёлые корабли «Алых парусов».',
        'Coaling stations supply the steam squadron quickly. This route strengthens the heavy ships of Scarlet Sails.',0,4,'JPI_raw_register',
        'add_ideas = JPI_coal_bunkers add_fuel = 15000 navy_experience = 10',cost=2,opposite='oil_hunger',icon='GFX_goal_unique_A01_rubber_processing')
    add('oil_hunger','Нефтяной голод','Oil Hunger',
        'Нефти для новой программы почти нет. Борнео становится необходимостью: срок выхода сокращается на 30 дней, но нехватка топлива сохранится до победы.',
        'Oil is scarce. Borneo becomes a necessity: sailing is brought forward by 30 days, but fuel shortages persist until victory.',4,4,'JPI_raw_register',
        'add_ideas = JPI_oil_shortage set_country_flag = JPI_oil_priority JPI_accelerate_oil_effect = yes',cost=2,opposite='kyushu_coal',icon='GFX_goal_unique_A01_rubber_processing')
    add('proxy_machines','Станки через посредников','Machines through Intermediaries',
        'Подставные покупатели доставят станки быстрее. Вероятность раскрытия заказа — 35%; утечка ослабит секретность будущей эскадры.',
        'Front buyers deliver machinery quickly. There is a 35% chance of exposure, compromising the future squadron.',8,4,'JPI_unsigned_contracts',
        factory(532,'arms_factory')+' random_list = { 35 = { JPI_procurement_leak_effect = yes } 65 = { set_country_flag = JPI_orders_hidden } }',cost=2,opposite='copied_samples')
    add('copied_samples','Копии образцов','Copied Samples',
        'Разбираем образцы и воспроизводим узлы без признания источника. Это дольше; слабая агентурная сеть всё ещё оставляет 20% риска провала.',
        'Reverse-engineer samples without acknowledging their source. This takes longer; our limited intelligence network still leaves a 20% risk of exposure.',12,4,'JPI_unsigned_contracts',
        'add_tech_bonus = { name = JPI_copied_samples bonus = 0.75 uses = 2 category = industry } random_list = { 20 = { JPI_procurement_leak_effect = yes } 80 = { set_country_flag = JPI_orders_hidden } }',cost=4,opposite='proxy_machines')
    add('standard_node','Единый образец узла','Standardised Assembly',
        'Каким бы ни был источник материалов и станков, корабли получат взаимозаменяемые узлы. Достаточно завершить один из четырёх путей.',
        'Whatever the source of materials and machinery, our vessels need interchangeable assemblies. Any one of the four routes is sufficient.',6,5,
        'JPI_kyushu_coal JPI_oil_hunger JPI_proxy_machines JPI_copied_samples','add_ideas = JPD_standardized_industry '+factory(532,'industrial_complex'))
    add('kure_yards','Верфи Куре','Kure Shipyards',
        'Крупные стапели строят тяжёлые корабли с «щупальцами». Средств на дирижабельные эллинги уже не останется.',
        'Heavy slipways build armoured ships with tentacles. The airship programme must be abandoned.',3,6,'JPI_standard_node',
        'add_ideas = JPI_heavy_yards navy_experience = 20 '+factory(529,'dockyard',2),opposite='airship_hangars',icon='GFX_goal_unique_A03_merchant_marine')
    add('airship_hangars','Эллинги дирижаблей','Airship Hangars',
        'Дирижабли ускорят переброску и разведку берега. Получим 24 аппарата, но тяжёлая эскадра подкрепления не будет построена.',
        'Airships improve deployment and coastal reconnaissance. Receive 24 airships, but forgo the heavy reinforcement squadron.',9,6,'JPI_standard_node',
        'add_ideas = JPI_airship_service set_technology = { airship = 1 } add_equipment_to_stockpile = { type = airship_equipment_1 amount = 24 producer = A03 } if = { limit = { owns_state = 529 } 529 = { add_building_construction = { type = air_base level = 1 instant_build = yes } } }',opposite='kure_yards',icon='GFX_goal_unique_A03_combined_operations')
    add('quiet_coast','Тихий берег','Quiet Coast',
        'Переносные вышки Теслы устанавливаются на транспортах. Радиус около 500 метров прикрывает плацдарм. Без этого оборудования сценарная высадка на Борнео не начнётся.',
        'Portable Tesla towers aboard transports cover a beachhead of roughly 500 metres. The scripted Borneo landing cannot begin without this equipment.',6,7,'JPI_kure_yards JPI_airship_hangars',
        'set_country_flag = JPI_tesla_ready add_ideas = JPI_portable_towers add_equipment_to_stockpile = { type = convoy_1 amount = 20 producer = A03 } custom_effect_tooltip = JPI_towers_tt',icon='GFX_goal_unique_A03_southern_bases')
    add('scarlet_sails','Алые паруса','Scarlet Sails',
        'Эскадра принимает свой окончательный облик. Закрытые порты или торговля, уголь или нефтяной голод, посредники или копии, верфи или эллинги — каждый выбор определяет её снабжение, вооружение и секретность.',
        'The squadron takes its final form. Autarky or trade, coal or oil hunger, intermediaries or copies, shipyards or hangars: every choice shapes its supply, weapons and secrecy.',6,8,'JPI_quiet_coast',
        'JPI_scarlet_sails_effect = yes',cost=2,icon='GFX_goal_unique_A03_combined_operations')
    add('southern_push','Южный рывок','Southern Push',
        'Приказы готовы, вышки погружены. По истечении срока ультиматум запускает войну за Борнео; если срок уже прошёл, он будет предъявлен сейчас. Нефтяной путь дополнительно сокращает ожидание на 15 дней.',
        'Orders are ready and towers loaded. The ultimatum begins the Borneo war when the countdown expires, or immediately if it has already expired. The oil route cuts another 15 days from the wait.',6,9,'JPI_scarlet_sails',
        'set_country_flag = JPI_southern_ready if = { limit = { has_country_flag = JPI_oil_priority } JPS_accelerate_invasion_effect = yes } if = { limit = { has_country_flag = JPI_ultimatum_due } JPC_issue_ultimatum = yes } add_war_support = 0.03',cost=2,icon='GFX_goal_unique_A03_southern_strategy')
    header=source[:source.index(' focus = {')]
    write(path,header+'\n'.join(kept)+'\n # Branching industrial preparation\n'+''.join(nodes)+'}\n')
    write_support()
    integrate()
    loc('JPX_sea','Поддержать курс адмиралтейства','Support the Admiralty Course')
    loc('JPX_sea_desc','Адмиралтейство предлагает южный поход. Прежде чем выйти в море, предстоит выбрать промышленный курс и подготовить «Тихий берег».','The Admiralty proposes a southern expedition. Choose an industrial policy and prepare Quiet Coast before sailing.')
    for i,lang in enumerate(['russian','english']):
        p=f'localisation/{lang}/1896_main_l_{lang}.yml'; s=(R/p).read_text(encoding='utf-8-sig')
        for key,values in LOC.items():
            line=f' {key}:0 "{values[i]}"'
            if re.search(r'^ '+re.escape(key)+r':',s,re.M):
                s=re.sub(r'^ '+re.escape(key)+r':[^\n]*',lambda m:line,s,flags=re.M)
            else: s+='\n'+line
        write(p,s+'\n')
    print('Installed 14 industrial focuses; 65 focuses total.')

def write_support():
    ideas={
        'rough_industry':('Грубые мощности','Rough Production','industrial_capacity_factory = 0.08 production_factory_max_efficiency_factor = -0.05'),
        'selective_imports':('Закупки под наблюдением Палаты','Procurement under Chamber Scrutiny','production_factory_max_efficiency_factor = 0.05 consumer_goods_factor = 0.02'),
        'coal_bunkers':('Угольные бункеры Кюсю','Kyushu Coal Bunkers','naval_supply_consumption_factor = -0.08'),
        'oil_shortage':('Нефть любой ценой','Oil at Any Cost','fuel_gain_factor = -0.15 war_support_factor = 0.05'),
        'heavy_yards':('Стапели Куре','Kure Slipways','industrial_capacity_dockyard = 0.10 shore_bombardment_bonus = 0.10'),
        'airship_service':('Дирижабельная служба','Airship Service','naval_invasion_prep_speed = 0.20 navy_org_factor = -0.05'),
        'portable_towers':('Переносные вышки Теслы','Portable Tesla Towers','amphibious_invasion = 0.10'),
        'exposed_orders':('Раскрытые закупки','Exposed Procurement','naval_coordination = -0.05'),
        'scarlet_iron':('Алые паруса: тяжёлые корабли','Scarlet Sails: Heavy Ships','naval_damage_factor = 0.08'),
        'scarlet_sky':('Алые паруса: дирижабли над берегом','Scarlet Sails: Airships over the Coast','naval_invasion_prep_speed = 0.15'),
    }
    text='ideas = { country = {\n'
    for name,(ru,en,mod) in ideas.items():
        key='JPI_'+name;loc(key,ru,en)
        loc(key+'_desc','Результат выбранного промышленного курса Японии.','A consequence of Japan’s chosen industrial programme.')
        text+=f' {key} = {{ picture = jpc_fleet removal_cost = -1 modifier = {{ {mod} }} }}\n'
    write('common/ideas/JPI_industry.txt',text+'} }\n')
    loc('JPI_towers_tt','Переносные вышки готовы. Их радиус около 500 м представлен бонусом высадки; отдельной зоной на карте он не отображается.','Portable towers are ready. Their roughly 500 m coverage is represented by a landing bonus, not a separate map area.')
    loc('JPI_leak_tt','Сведения о заказах утекли: секретность эскадры снижена на 180 дней.','Procurement details leaked: squadron secrecy is compromised for 180 days.')
    write('common/scripted_effects/JPI_industry.txt','''# Country scope: Japan.
JPI_accelerate_oil_effect = {
 if = { limit = { has_country_flag = JPI_oil_priority NOT = { has_country_flag = JPI_oil_clock_applied } has_active_mission = A03_japanese_invasion_countdown A01 = { has_active_mission = A01_japanese_invasion_countdown } }
  set_country_flag = JPI_oil_clock_applied
  JPS_accelerate_invasion_effect = yes
  JPS_accelerate_invasion_effect = yes
 }
}
JPI_procurement_leak_effect = {
 set_country_flag = JPI_orders_exposed
 add_timed_idea = { idea = JPI_exposed_orders days = 180 }
 add_political_power = -25
 custom_effect_tooltip = JPI_leak_tt
}
JPI_scarlet_sails_effect = {
 if = { limit = { has_completed_focus = JPI_kure_yards } add_ideas = JPI_scarlet_iron }
 else = { add_ideas = JPI_scarlet_sky add_equipment_to_stockpile = { type = airship_equipment_1 amount = 12 producer = A03 } }
 if = { limit = { has_completed_focus = JPI_closed_ports } add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 500 producer = A03 } }
 else = { add_equipment_to_stockpile = { type = convoy_1 amount = 15 producer = A03 } }
 if = { limit = { has_completed_focus = JPI_kyushu_coal } add_fuel = 20000 navy_experience = 15 }
 if = { limit = { has_completed_focus = JPI_oil_hunger } add_command_power = 20 }
 if = { limit = { has_completed_focus = JPI_proxy_machines } add_equipment_to_stockpile = { type = convoy_1 amount = 10 producer = A03 } }
 if = { limit = { has_completed_focus = JPI_copied_samples } add_tech_bonus = { name = JPI_copied_samples bonus = 0.5 uses = 1 category = industry } }
 if = { limit = { has_country_flag = JPI_orders_exposed } add_timed_idea = { idea = JPI_exposed_orders days = 180 } }
 if = { limit = { has_country_flag = JPI_orders_hidden } add_command_power = 10 }
 country_event = { id = japan_industry.1 days = 1 }
}
''')
    write('common/on_actions/JPI_industry.txt','''on_actions = { on_daily_A03 = { effect = { A03 = {
 JPI_accelerate_oil_effect = yes
 if = { limit = { has_country_flag = JPI_ultimatum_due has_country_flag = JPI_southern_ready NOT = { has_country_flag = JPC_ultimatum_sent } } JPC_issue_ultimatum = yes }
 if = { limit = { has_country_flag = A03_borneo_victory has_idea = JPI_oil_shortage } remove_ideas = JPI_oil_shortage }
} } } }
''')
    loc('japan_industry.1.t','Алые паруса','Scarlet Sails');loc('japan_industry.1.a','Эскадра готова.','The squadron is ready.')
    event='add_namespace = japan_industry\ncountry_event = {\n id = japan_industry.1 title = japan_industry.1.t picture = GFX_1896_event_navy is_triggered_only = yes\n'
    for branch in ['kyushu_coal','oil_hunger','proxy_machines','copied_samples']:
        for fleet in ['kure_yards','airship_hangars']:
            key=f'japan_industry.1.{branch}_{fleet}'
            ru={'kyushu_coal':'Закрытые порты дали грубую, но самостоятельную промышленность. Уголь Кюсю наполнил бункеры.', 'oil_hunger':'Закрытые порты дали собственные мастерские, но нефтяные цистерны пусты. Борнео нужен, чтобы продолжать поход.', 'proxy_machines':'Палата видит наши закупки. Подставные дома быстро доставили чужие станки; их следы могут выдать приготовления.', 'copied_samples':'Палата знает списки материалов, но происхождение скопированных узлов мы не признаём. Медленная работа не исключила провала слабой агентурной сети.'}[branch]
            en={'kyushu_coal':'Closed ports produced rough but independent industry. Kyushu coal fills the bunkers.', 'oil_hunger':'Closed ports provided our own workshops, but the oil tanks are empty. Borneo is needed to sustain the expedition.', 'proxy_machines':'The Chamber sees our procurement. Front companies quickly delivered foreign machinery, leaving a trail that may expose our preparations.', 'copied_samples':'The Chamber knows our materials lists, but we deny the origin of copied assemblies. Slow work did not eliminate the risks of our limited intelligence network.'}[branch]
            ru+=' Тяжёлые алые корабли Куре разворачивают «щупальца».' if fleet=='kure_yards' else 'Алые дирижабли идут над берегом; их скорость оплачена отказом от тяжёлого подкрепления.'
            en+=' Heavy scarlet ships from Kure extend their tentacles.' if fleet=='kure_yards' else ' Scarlet airships pass above the coast; their speed was bought by forgoing heavy reinforcements.'
            loc(key,ru+' Транспорты несут переносные вышки для первого плацдарма.',en+' Transports carry portable towers for the first beachhead.')
            event+=f' desc = {{ trigger = {{ has_completed_focus = JPI_{branch} has_completed_focus = JPI_{fleet} }} text = {key} }}\n'
    write('events/JPI_industry.txt',event+' option = { name = japan_industry.1.a }\n}\n')

def integrate():
    edit('common/scripted_effects/JPC_canonical.txt','JPC_issue_ultimatum = {','JPC_issue_ultimatum = {\n set_country_flag = JPI_ultimatum_due')
    edit('common/scripted_effects/JPC_canonical.txt','if = { limit = { country_exists = A01','if = { limit = { has_country_flag = JPI_tesla_ready has_country_flag = JPI_southern_ready country_exists = A01')
    edit('common/scripted_effects/borneo_war_effects.txt','NOT = { has_country_flag = A03_southern_force_prepared }','has_country_flag = JPI_tesla_ready NOT = { has_country_flag = A03_southern_force_prepared }')
    edit('common/scripted_effects/borneo_war_effects.txt','has_country_flag = JPC_ultimatum_sent country_exists','has_country_flag = JPC_ultimatum_sent has_country_flag = JPI_tesla_ready has_country_flag = JPI_southern_ready country_exists')
    # Transport tech is universal; expensive battleship OOBs belong only to Kure.
    edit('common/scripted_effects/borneo_war_effects.txt','   else = { set_technology = { transport = 1 early_battleship = 1 } load_oob = "A03_southern_reinforcements_legacy" }\n  }','  }\n  else = { set_technology = { transport = 1 early_battleship = 1 } load_oob = "A03_southern_reinforcements_legacy" }')
    edit('common/scripted_effects/borneo_war_effects.txt','if = { limit = { has_dlc = "Man the Guns" }','if = { limit = { has_dlc = "Man the Guns" } set_technology = { mtg_transport = 1 } }\n  else = { set_technology = { transport = 1 } }\n  if = { limit = { has_completed_focus = JPI_kure_yards }\n  if = { limit = { has_dlc = "Man the Guns" }')
    edit('common/scripted_effects/borneo_war_effects.txt','  load_oob = "A03_borneo_invasion"','  }\n  load_oob = "A03_borneo_invasion"')
    edit('common/scripted_effects/JPF_finance.txt','NOT = { has_country_flag = JPF_credit_queued }','NOT = { has_country_flag = JPF_credit_queued } has_completed_focus = JPI_japanese_terms')
    edit('events/JPF_finance.txt','trigger = { country_exists = A04 NOT = { has_war_with = A04 } }','trigger = { has_completed_focus = JPI_japanese_terms country_exists = A04 NOT = { has_war_with = A04 } }')
    edit('events/JPC_canonical.txt','trigger = { tag = A04 country_exists = A03 NOT = { has_war_with = A03 } }','trigger = { tag = A04 country_exists = A03 A03 = { has_completed_focus = JPI_japanese_terms } NOT = { has_war_with = A03 } }')
    # Retain repayment of inherited debt; disallow fresh contracts under autarky.
    path='common/decisions/WTC_credit.txt';s=(R/path).read_text(encoding='utf-8-sig')
    for name in ['WTC_borrow','WTC_concede','WTC_naval_service','WTC_insure','WTC_cables']:
        s=re.sub(r'('+name+r'\s*=\s*\{[^\n]*?available\s*=\s*\{)',r'\1 NOT = { has_country_flag = JPI_autarky }',s,count=1)
    write(path,s)
    # Keep prewar industry within the historical preparation window for AI Japan.
    path='common/ai_strategy_plans/A01_canonical.txt';s=(R/path).read_text(encoding='utf-8-sig');start=s.index('A03_southern_canonical_plan')
    def plan(m):
        old=[x for x in m[1].split() if x not in REMOVED and x not in {'A03_imperial_council','JPX_sea'}]
        route='A03_imperial_council JPX_sea JPI_closed_ports JPI_raw_register JPI_kyushu_coal JPI_standard_node JPI_kure_yards JPI_quiet_coast JPI_scarlet_sails JPI_southern_push'.split()
        return 'ai_national_focuses = { '+' '.join(route+old)+' }'
    write(path,s[:start]+re.sub(r'ai_national_focuses\s*=\s*\{([^}]+)\}',plan,s[start:],count=1))

if __name__=='__main__': main()
