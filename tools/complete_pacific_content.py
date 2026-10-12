from pathlib import Path
import re, json, shutil

ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT / 'tools/backups/pacific_before'
def write(path, text, bom=False):
    p=ROOT/path
    if p.exists() and not (BACKUP/path).exists():
        (BACKUP/path).parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,BACKUP/path)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text,encoding='utf-8-sig' if bom else 'utf-8')

loc={}
def label(key,ru,en,desc_ru=None,desc_en=None):
    loc[key]=(ru,en)
    if desc_ru: loc[key+'_desc']=(desc_ru,desc_en)

def focus(tag,key,ru,en,x,y,parents=(),reward='',icon='industry',cost=5,exclusive=None,available='',desc=None):
    ident=tag+'_'+key
    label(ident,ru,en,desc or f'{ru}. Последовательное развитие этой программы укрепит государство и подготовит его к борьбе за Тихий океан.',f'{en}. A sustained investment in this programme will strengthen our position in the Pacific.')
    return '\n focus = {\n'+f'  id = {ident}\n  icon = GFX_goal_pacific_{icon}\n  x = {x}\n  y = {y}\n  cost = {cost}\n'+''.join(f'  prerequisite = {{ focus = {tag}_{p} }}\n' for p in parents)+(f'  mutually_exclusive = {{ focus = {tag}_{exclusive} }}\n' if exclusive else '')+(f'  available = {{ {available} }}\n  cancel_if_invalid = yes\n' if available else '')+f'  ai_will_do = {{ factor = 1 }}\n  completion_reward = {{ {reward} }}\n }}\n'

def building(state,kind,n=1):
    return f'if = {{ limit = {{ owns_state = {state} }} {state} = {{ add_extra_state_shared_building_slots = {n} add_building_construction = {{ type = {kind} level = {n} instant_build = yes }} }} }}'

def infra(state):
    return f'if = {{ limit = {{ owns_state = {state} }} {state} = {{ add_building_construction = {{ type = infrastructure level = 1 instant_build = yes }} }} }}'

# Extend the existing alternate-history tree instead of replacing its story.
p=ROOT/'common/national_focus/a01_focus.txt'
base=((BACKUP/'common/national_focus/a01_focus.txt') if (BACKUP/'common/national_focus/a01_focus.txt').exists() else p).read_text(encoding='utf-8-sig').rstrip()
extra=[]
def dei(*args,**kw): extra.append(focus('A01',*args,**kw))
dei('java_development','План развития Явы','The Java Development Plan',24,0,reward=building(1058,'industrial_complex'),desc='Батавские верфи и яванские мастерские нуждаются в общем плане. Государственные заказы создадут промышленную основу обороны архипелага.')
dei('archipelago_shipping','Каботажные линии','Inter-island Shipping',22,1,['java_development'],'add_equipment_to_stockpile = { type = convoy_1 amount = 30 producer = A01 }',icon='batavia')
dei('sumatran_railways','Суматранские железные дороги','Sumatran Railways',24,1,['java_development'],infra(672)+infra(1049))
dei('surabaya_arsenal','Арсенал Сурабаи','The Surabaya Arsenal',26,1,['java_development'],building(1051,'arms_factory'))
dei('batavia_docks','Доковый комплекс Батавии','Batavia Dockyards',22,2,['archipelago_shipping'],building(1058,'dockyard',2),icon='batavia')
dei('rubber_processing','Переработка каучука','Rubber Processing',24,2,['sumatran_railways'],building(672,'industrial_complex'))
dei('local_rifles','Местное производство винтовок','Local Rifle Manufacture',26,2,['surabaya_arsenal'],'add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 1500 producer = A01 } add_army_experience = 15',icon='army')
dei('technical_college','Батавский технический институт','Batavia Technical Institute',24,3,['rubber_processing'],'add_research_slot = 1',cost=10)
dei('knil_reform','Реформа колониальной армии','Reform the Colonial Army',30,0,reward='add_army_experience = 20 add_ideas = A01_knil_training',icon='army',desc='Гарнизонная служба не готовит войска к современной войне. Единые учебные программы и постоянные полевые сборы превратят разрозненные части в боеспособную армию.')
dei('island_garrisons','Гарнизоны островов','Island Garrisons',28,1,['knil_reform'],'add_manpower = 12000 add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 1000 producer = A01 }',icon='army')
dei('marine_brigades','Морские бригады','Marine Brigades',32,1,['knil_reform'],'add_army_experience = 25 add_ideas = A01_island_defence',icon='batavia')
dei('jungle_supply','Снабжение в джунглях','Jungle Supply Services',30,2,['island_garrisons','marine_brigades'],'add_ideas = A01_jungle_supply',icon='army')
dei('coastal_watch','Береговая наблюдательная служба','Coastal Watch Service',30,3,['jungle_supply'],'add_war_support = 0.05 '+building(1051,'dockyard'),icon='batavia')
dei('equal_service','Равные условия службы','Equal Conditions of Service',34,5,['invest_in_mass_consumer_goods'],'set_country_flag = A01_indonesian_integration set_variable = { A01_racial_recruitable_population = -0.10 } set_variable = { A01_racial_stability = -0.10 } force_update_dynamic_modifier = yes',icon='batavia',exclusive='colonial_hierarchy',desc='Добровольцы из местного населения должны получать одинаковое жалованье и возможность продвижения. Такие уступки расширят кадровый резерв и ослабят недоверие к Батавии.')
dei('colonial_hierarchy','Сохранить колониальную иерархию','Preserve the Colonial Hierarchy',36,5,['invest_in_mass_consumer_goods'],'set_country_flag = A01_european_supremacy add_political_power = 100 add_stability = -0.05 add_ideas = A01_colonial_administration',icon='army',exclusive='equal_service')
dei('sultans_compact','Соглашение с султанами','The Sultans Compact',34,6,['equal_service'],'set_country_flag = A01_council_of_sultans_decision_unlocked add_stability = 0.05',icon='batavia')
dei('colonial_charter','Батавская хартия','The Batavian Charter',34,7,['sultans_compact'],'set_variable = { A01_racial_recruitable_population = 0 } set_variable = { A01_racial_stability = 0 } set_variable = { A01_racial_resistance_growth = 0 } set_variable = { A01_racial_factory_efficiency_gain = 0 } set_variable = { A01_racial_political_power_gain = 0 } force_update_dynamic_modifier = yes add_stability = 0.05',icon='batavia',cost=10,desc='Представительство островов, общая казна и равенство перед законом станут основой нового договора. Хартия завершит преобразование колониальной администрации в государство архипелага.')
dei('admiralty_shipyards','Верфи Адмиралтейства','Admiralty Shipyards',44,5,['direct_naval_rule'],building(1051,'dockyard',2),icon='batavia')
dei('naval_general_staff','Морской генеральный штаб','Naval General Staff',44,6,['admiralty_shipyards'],'add_navy_experience = 35 add_ideas = A01_naval_staff',icon='batavia')
dei('military_industry','Военные предприятия','Military Workshops',46,5,['direct_naval_rule'],building(335,'arms_factory',2),icon='industry')
dei('defence_in_depth','Оборона в глубину','Defence in Depth',46,6,['military_industry'],'add_ideas = A01_island_defence add_army_experience = 20',icon='army')
dei('archipelago_command','Единое командование архипелага','Unified Archipelago Command',45,7,['naval_general_staff','defence_in_depth'],'add_stability = 0.05 add_war_support = 0.10 add_command_power = 25',icon='batavia',cost=10)
dei('wartime_industry','Мобилизация промышленности','Industrial Mobilisation',40,9,['improve_bornean_fortifications'],building(1058,'arms_factory')+'add_ideas = A01_war_production',available='has_war_with = A03')
dei('secure_sea_lanes','Защита морских коммуникаций','Secure the Sea Lanes',42,8,['coastal_watch'],'add_equipment_to_stockpile = { type = convoy_1 amount = 40 producer = A01 } add_navy_experience = 25',icon='batavia')
dei('pacific_settlement','Тихоокеанское урегулирование','A Pacific Settlement',40,10,['wartime_industry'],'add_stability = 0.10 add_political_power = 100 remove_ideas = A01_war_production',icon='batavia',available='NOT = { has_war = yes } has_country_flag = A01_japanese_invasion_begun',desc='После войны предстоит восстановить порты, вернуть демобилизованных солдат к мирному труду и закрепить безопасность морских путей. Победа должна принести архипелагу устойчивый мир.')
write('common/national_focus/a01_focus.txt',base[:-1]+''.join(extra)+'\n}\n')

j=[]
def jap(*args,**kw): j.append(focus('A03',*args,**kw))
jap('imperial_council','Императорский совет','The Imperial Council',12,0,reward='add_political_power = 100',icon='japan',desc='Двор в Киото должен определить место империи в раздробленном Тихоокеанском мире. Совет согласует требования промышленников, армии и флота, прежде чем выбрать новый курс.')
jap('civil_government','Гражданское правительство','Civil Government',10,1,['imperial_council'],'add_stability = 0.05 add_ideas = A03_civil_government',icon='japan',exclusive='naval_government')
jap('naval_government','Кабинет морского ведомства','The Naval Cabinet',14,1,['imperial_council'],'add_war_support = 0.10 add_ideas = A03_naval_government',icon='japan',exclusive='civil_government')
jap('prefectural_reform','Префектурная реформа','Prefectural Reform',10,2,['civil_government'],'add_political_power = 100 add_stability = 0.05',icon='japan')
jap('commercial_diplomacy','Торговая дипломатия','Commercial Diplomacy',10,3,['prefectural_reform'],'add_ideas = A03_commercial_network',icon='industry')
jap('batavia_convention','Батавская конвенция','The Batavia Convention',10,4,['commercial_diplomacy'],'A01 = { country_event = { id = pacific.3 days = 2 } }',icon='japan',available='country_exists = A01 NOT = { has_war_with = A01 }',desc='Морские перевозчики заинтересованы в каучуке и нефти Ост-Индии. Предложим Батавии взаимные гарантии и торговый договор: безопасность поставок может стоить больше, чем завоевание.')
jap('pacific_prosperity','Тихоокеанское процветание','Pacific Prosperity',10,5,['batavia_convention'],building(531,'industrial_complex',2)+'add_stability = 0.05',available='has_country_flag = pacific_trade_accord',cost=10)
jap('southern_strategy','Южная стратегия','The Southern Strategy',14,2,['naval_government'],'add_navy_experience = 20 set_country_flag = A03_southern_strategy',icon='japan')
jap('resource_commission','Ресурсная комиссия','The Resource Commission',14,3,['southern_strategy'],'add_ideas = A03_resource_commission',icon='industry')
jap('batavia_ultimatum','Ультиматум Батавии','The Batavia Ultimatum',14,4,['resource_commission'],'A01 = { country_event = { id = pacific.4 days = 2 } }',icon='japan',available='country_exists = A01 NOT = { has_war_with = A01 } NOT = { has_country_flag = pacific_trade_accord }',desc='Военные требуют гарантированного доступа к нефтяным месторождениям Борнео. Батавия получит выбор между ограниченной экономической уступкой и подготовкой к войне.')
jap('southern_bases','Южные опорные пункты','Southern Forward Bases',16,5,['batavia_ultimatum'],building(647,'dockyard')+'add_equipment_to_stockpile = { type = convoy_1 amount = 25 producer = A03 }',icon='japan')
jap('southern_campaign','Южная кампания','The Southern Campaign',14,6,['batavia_ultimatum'],'declare_war_on = { target = A01 type = take_state_focus generator = { 334 1022 1024 1055 } } A01 = { set_country_flag = A01_japanese_invasion_begun }',icon='army',available='country_exists = A01 NOT = { has_war_with = A01 } NOT = { has_country_flag = pacific_trade_accord } A01 = { has_country_flag = A01_refused_japanese_ultimatum }',cost=10)
jap('southern_reconstruction','Восстановление южных владений','Reconstruct the Southern Territories',14,7,['southern_campaign'],building(1055,'industrial_complex')+'add_stability = 0.05',available='owns_state = 1055 NOT = { has_war_with = A01 }',cost=10)
jap('osaka_industry','Осакский промышленный район','The Osaka Industrial District',2,0,reward=building(531,'industrial_complex'))
jap('kansai_railways','Железные дороги Кансая','Kansai Railways',0,1,['osaka_industry'],infra(531)+infra(532))
jap('hiroshima_arsenal','Хиросимский арсенал','Hiroshima Arsenal',4,1,['osaka_industry'],building(529,'arms_factory'))
jap('steel_contracts','Контракты на сталь','Steel Contracts',0,2,['kansai_railways'],'add_ideas = A03_industrial_contracts')
jap('standard_rifles','Единый образец винтовки','Standard Service Rifle',4,2,['hiroshima_arsenal'],'add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 2000 producer = A03 } add_army_experience = 10',icon='army')
jap('imperial_university','Императорский технический университет','Imperial Technical University',2,3,['steel_contracts','standard_rifles'],'add_research_slot = 1',cost=10)
jap('electrical_workshops','Электротехнические мастерские','Electrical Workshops',2,4,['imperial_university'],building(532,'industrial_complex'))
jap('industrial_power','Промышленная держава','An Industrial Power',2,5,['electrical_workshops'],building(529,'arms_factory',2),cost=10)
jap('naval_programme','Императорская кораблестроительная программа','Imperial Naval Programme',22,0,reward=building(528,'dockyard'),icon='japan')
jap('kure_yards','Верфи Куре','Kure Naval Yards',20,1,['naval_programme'],building(529,'dockyard',2),icon='japan')
jap('merchant_marine','Торговый флот','Merchant Marine',24,1,['naval_programme'],'add_equipment_to_stockpile = { type = convoy_1 amount = 50 producer = A03 }',icon='industry')
jap('naval_academy','Императорская морская академия','Imperial Naval Academy',20,2,['kure_yards'],'add_navy_experience = 35 add_ideas = A03_naval_academy',icon='japan')
jap('island_supply','Снабжение островных баз','Supply the Island Bases',24,2,['merchant_marine'],'add_ideas = A03_island_supply',icon='army')
jap('fleet_exercises','Манёвры Объединённого флота','Combined Fleet Exercises',22,3,['naval_academy','island_supply'],'add_navy_experience = 40 add_war_support = 0.05',icon='japan')
jap('army_reorganisation','Реорганизация императорской армии','Reorganise the Imperial Army',30,0,reward='add_army_experience = 25 add_ideas = A03_army_reform',icon='army')
jap('conscription_register','Воинский учёт','The Conscription Register',28,1,['army_reorganisation'],'add_manpower = 20000 add_war_support = 0.05',icon='army')
jap('landing_forces','Десантные отряды','Naval Landing Forces',32,1,['army_reorganisation'],'add_army_experience = 25 add_ideas = A03_landing_force',icon='army')
jap('field_artillery','Полевая артиллерия','Field Artillery',28,2,['conscription_register'],building(530,'arms_factory'),icon='army')
jap('expeditionary_staff','Экспедиционный штаб','Expeditionary Staff',32,2,['landing_forces'],'add_command_power = 25 add_ideas = A03_expeditionary_staff',icon='army')
jap('combined_operations','Совместные операции','Combined Operations',30,3,['field_artillery','expeditionary_staff'],'add_army_experience = 25 add_navy_experience = 25 add_war_support = 0.05',icon='army',cost=10)
write('common/national_focus/a03_focus.txt','focus_tree = {\n id = A03_focus\n country = { factor = 0 modifier = { add = 100 tag = A03 } }\n default = no\n continuous_focus_position = { x = 1400 y = 1100 }\n'+''.join(j)+'}\n')

spirits=[
('A01_knil_training','Подготовка КНИЛ','KNIL Training','army','army_org_factor = 0.05 training_time_army_factor = -0.10'),
('A01_island_defence','Оборона архипелага','Archipelago Defence','army','army_defence_factor = 0.05'),
('A01_jungle_supply','Островная служба снабжения','Island Supply Service','industry','supply_consumption_factor = -0.10'),
('A01_colonial_administration','Колониальная администрация','Colonial Administration','batavia','political_power_gain = 0.15'),
('A01_naval_staff','Штаб Адмиралтейства','Admiralty Staff','batavia','navy_org_factor = 0.05 production_speed_dockyard_factor = 0.10'),
('A01_war_production','Оборонные заказы','Defence Orders','industry','industrial_capacity_factory = 0.10 consumer_goods_factor = 0.05'),
('A03_civil_government','Гражданский кабинет','Civil Cabinet','japan','political_power_gain = 0.15 stability_factor = 0.05'),
('A03_naval_government','Морской кабинет','Naval Cabinet','japan','production_speed_dockyard_factor = 0.10 war_support_factor = 0.05'),
('A03_commercial_network','Тихоокеанская торговая сеть','Pacific Trading Network','industry','production_speed_industrial_complex_factor = 0.10'),
('A03_resource_commission','Императорская ресурсная комиссия','Imperial Resource Commission','industry','production_factory_efficiency_gain_factor = 0.05'),
('A03_industrial_contracts','Промышленные контракты','Industrial Contracts','industry','production_speed_buildings_factor = 0.05'),
('A03_naval_academy','Морская академия','Naval Academy','japan','navy_org_factor = 0.05'),
('A03_island_supply','Островные конвои','Island Convoys','industry','supply_consumption_factor = -0.05'),
('A03_army_reform','Армейская реформа','Army Reform','army','army_org_factor = 0.05 training_time_army_factor = -0.10'),
('A03_landing_force','Императорские десантные силы','Imperial Landing Forces','army','special_forces_cap = 0.05'),
('A03_expeditionary_staff','Экспедиционный штаб','Expeditionary Staff','army','supply_consumption_factor = -0.05'),
('pacific_trade_accord_idea','Батавская торговая конвенция','Batavia Trade Convention','industry','production_speed_industrial_complex_factor = 0.05 stability_factor = 0.05'),
]
ideas='ideas = { country = {\n'
for key,ru,en,icon,mod in spirits:
    label(key,ru,en,ru+': постоянная программа, обеспечивающая подготовку кадров и согласованную работу государственных служб.',en+': a permanent programme coordinating training and government services.')
    tag=key[:3]
    allowed=f'original_tag = {tag}' if tag in ['A01','A03'] else 'OR = { original_tag = A01 original_tag = A03 }'
    ideas+=f'{key} = {{ picture = pacific_{icon} allowed = {{ {allowed} }} allowed_civil_war = {{ always = yes }} removal_cost = -1 modifier = {{ {mod} }} }}\n'
write('common/ideas/pacific_ideas.txt',ideas+'} }\n')

# A bilateral negotiation: the receiving player/AI chooses the result.
events='add_namespace = pacific\n'
def event(n,ru,en,dr,de,options):
    global events
    key=f'pacific.{n}'
    label(key+'.t',ru,en); label(key+'.d',dr,de)
    events+=f'country_event = {{ id = {key} title = {key}.t desc = {key}.d picture = GFX_report_event_A01_japan_rejects_dutch_offer is_triggered_only = yes\n'
    for suffix,r,e,effect,weight in options:
        label(key+'.'+suffix,r,e)
        events+=f' option = {{ name = {key}.{suffix} ai_chance = {{ factor = {weight} }} {effect} }}\n'
    events+='}\n'
accord='set_country_flag = pacific_trade_accord add_ideas = pacific_trade_accord_idea A03 = { set_country_flag = pacific_trade_accord add_ideas = pacific_trade_accord_idea } non_aggression_pact = A03'
event(1,'Предложение Батавии','An Offer from Batavia','Батавия предлагает гарантированные поставки каучука в обмен на взаимное ненападение. Промышленники поддерживают соглашение, но морское ведомство требует контроля над источниками сырья.','Batavia offers guaranteed rubber deliveries in exchange for mutual non-aggression. Industrialists support the agreement; the naval ministry demands control of the resources.',[
('a','Подписать торговое соглашение.','Sign the trade agreement.','set_country_flag = pacific_trade_accord add_ideas = pacific_trade_accord_idea non_aggression_pact = A01 A01 = { set_country_flag = pacific_trade_accord add_ideas = pacific_trade_accord_idea country_event = { id = pacific.2 days = 1 } }',40),
('b','Нам нужны гарантии иного рода.','We require different guarantees.','A01 = { country_event = { id = A01_japan.1 days = 1 } }',60)])
event(2,'Конвенция подписана','The Convention Is Signed','Договор с Японией обеспечивает рынки сбыта и взаимные гарантии ненападения. Порты готовятся принять первые торговые суда.','The agreement with Japan secures export markets and mutual guarantees of non-aggression. The ports are preparing for the first merchant ships.',[('a','Дипломатия принесла результат.','Diplomacy has prevailed.','add_stability = 0.05',100)])
event(3,'Японская торговая миссия','A Japanese Trade Mission','Японские представители предлагают торговую конвенцию и взаимное ненападение. Принятие договора обеспечит инвестиции, но свяжет нашу торговлю с империей.','Japanese representatives offer a trade convention and mutual non-aggression. Accepting will secure investment while tying our commerce to the empire.',[('a','Принять условия.','Accept the terms.',accord,65),('b','Наши порты останутся независимыми.','Our ports will remain independent.','A03 = { add_political_power = 50 }',35)])
event(4,'Требования морского ведомства','The Naval Ministry Demands','Япония требует привилегированного доступа к сырью Борнео. Отказ запустит шестимесячный отсчёт до вторжения; уступка позволит сохранить мир ценой экономического влияния.','Japan demands privileged access to Bornean resources. Refusal starts a six-month invasion countdown; concessions preserve peace at the cost of economic influence.',[('a','Уступить ради мира.','Concede to preserve peace.',accord+'add_political_power = -75',30),('b','Готовить острова к обороне.','Prepare the islands for defence.','if = { limit = { NOT = { has_country_flag = A01_refused_japanese_ultimatum } } country_event = { id = A01_japan.1 days = 1 } }',70)])
write('events/pacific_diplomacy.txt',events)
# Route the pre-existing focus offer to Japan rather than deciding for it in Batavia.
p=ROOT/'common/national_focus/a01_focus.txt'; t=p.read_text(encoding='utf-8')
t=t.replace('country_event = {\n                id = A01_japan.1\n                days = 2\n            }','if = { limit = { country_exists = A03 NOT = { has_war_with = A03 } } A03 = { country_event = { id = pacific.1 days = 2 } } }')
write('common/national_focus/a01_focus.txt',t)

# Japan needs a functioning start rather than an empty country history.
write('common/characters/A03.txt','''characters = {
 A03_imperial_council = { name = A03_imperial_council_name country_leader = { ideology = despotism expire = "1965.1.1.1" traits = { } } }
 A03_naval_commander = { name = A03_naval_commander_name navy_leader = { skill = 3 attack_skill = 3 defense_skill = 3 maneuvering_skill = 3 coordination_skill = 3 traits = { } } }
 A03_army_commander = { name = A03_army_commander_name corps_commander = { skill = 3 attack_skill = 3 defense_skill = 3 planning_skill = 3 logistics_skill = 3 traits = { } } }
}
''')
label('A03_imperial_council_name','Императорский совет Киото','Kyoto Imperial Council')
label('A03_naval_commander_name','Командование Объединённого флота','Combined Fleet Command')
label('A03_army_commander_name','Штаб Западной армии','Western Army Headquarters')
hist='''capital = 531
oob = "A03_1877"
recruit_character = A03_imperial_council
recruit_character = A03_naval_commander
recruit_character = A03_army_commander
set_research_slots = 3
set_stability = 0.60
set_war_support = 0.40
set_politics = { ruling_party = neutrality elections_allowed = no }
set_popularities = { neutrality = 85 democratic = 15 }
add_ideas = limited_conscription
add_ideas = civilian_economy
add_ideas = limited_exports
set_convoys = 100
set_technology = { infantry_weapons = 1 tech_support = 1 marines = 1 early_ship_hull_light = 1 early_ship_hull_cruiser = 1 }
if = { limit = { has_dlc = "Man the Guns" } set_technology = { mtg_transport = 1 } }
else = { set_technology = { transport = 1 } }
'''
write('history/countries/A03 - Placeholder.txt',hist)
oob='division_template = { name = "Imperial Infantry" regiments = { infantry = { x = 0 y = 0 } infantry = { x = 0 y = 1 } infantry = { x = 0 y = 2 } infantry = { x = 1 y = 0 } infantry = { x = 1 y = 1 } infantry = { x = 1 y = 2 } } }\nunits = {\n'
for i,prov in enumerate([7072,11960,4142,4094,7212,10055],1):
    oob+=f'division = {{ name = "{i}. Imperial Infantry" location = {prov} division_template = "Imperial Infantry" start_experience_factor = 0.15 start_equipment_factor = 0.80 }}\n'
write('history/units/A03_1877.txt',oob+'}\n')

# Repeatable decisions with an actual price and cooldown.
dec=''
for tag in ['A01','A03']:
    cat=tag+'_pacific_preparations'
    label(cat,'Подготовка к тихоокеанской войне','Pacific Preparations')
    dec+=f'{cat} = {{ icon = generic_military allowed = {{ original_tag = {tag} }} visible = {{ always = yes }}\n'
    for key,ru,en,cost,effect in [('training','Полевые сборы','Field Exercises',50,'add_army_experience = 10'),('convoys','Заказать торговые суда','Commission Merchant Ships',75,f'add_equipment_to_stockpile = {{ type = convoy_1 amount = 10 producer = {tag} }}'),('reserves','Подготовить резервистов','Train Reservists',75,'add_manpower = 5000')]:
        ident=tag+'_pacific_'+key
        label(ident,ru,en,'Программа финансируется из государственных средств. После завершения потребуется 90 дней на подготовку следующего цикла.','A state-funded programme. After completion, a 90-day cooldown is required before another cycle.')
        dec+=f'{ident} = {{ icon = generic_prepare_civil_war cost = {cost} days_remove = 30 days_re_enable = 90 available = {{ has_capitulated = no }} remove_effect = {{ {effect} }} ai_will_do = {{ factor = 1 }} }}\n'
    dec+='}\n'
write('common/decisions/pacific_preparations.txt',dec)

for lang,index in [('russian',0),('english',1)]:
    text='l_'+lang+':\n'+''.join(f' {key}:0 {json.dumps(value[index],ensure_ascii=False)}\n' for key,value in loc.items())
    write(f'localisation/{lang}/pacific_content_l_{lang}.yml',text,True)
write('tools/pacific_content_manifest.json',json.dumps({'new_indies_focuses':len(extra),'japan_focuses':len(j),'spirits':len(spirits),'localisation_keys':len(loc)},indent=2))
print(f'Written: {len(extra)} Indies additions, {len(j)} Japan focuses, {len(spirits)} spirits, bilateral diplomacy and decisions.')
