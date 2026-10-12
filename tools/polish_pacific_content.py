from pathlib import Path
import re,json
from complete_pacific_content import ROOT,write,label,loc,focus

# Valid starting locations are checked against state ownership by the validator.
p=ROOT/'history/units/A03_1877.txt'
write(str(p.relative_to(ROOT)),p.read_text().replace('location = 4142','location = 4142'))

# Both navies receive finite, modest fleets. Ship designs use the installed
# game's hull/module definitions, with separate legacy and MtG OOBs.
for tag,port,cruisers,escorts in [('A01',7381,2,6),('A03',1136,4,10)]:
    hp=f'history/countries/{tag} - Placeholder.txt'
    original=ROOT/'tools/backups/pacific_before'/hp
    history=(original if tag=='A01' and original.exists() else ROOT/hp).read_text(encoding='utf-8-sig')
    design='''
if = {
 limit = { has_dlc = "Man the Guns" }
 set_technology = { early_ship_hull_light = 1 early_ship_hull_cruiser = 1 basic_battery = 1 basic_torpedo = 1 basic_light_battery = 1 basic_medium_battery = 1 }
 create_equipment_variant = {
  name = "Pacific Escort" type = ship_hull_light_1 parent_version = 0
  modules = { fixed_ship_battery_slot = ship_light_battery_1 fixed_ship_anti_air_slot = empty fixed_ship_fire_control_system_slot = ship_fire_control_system_0 fixed_ship_radar_slot = empty fixed_ship_engine_slot = light_ship_engine_1 fixed_ship_torpedo_slot = ship_torpedo_1 mid_1_custom_slot = empty rear_1_custom_slot = empty }
 }
 create_equipment_variant = {
  name = "Pacific Cruiser" type = ship_hull_cruiser_1 parent_version = 0
  modules = { fixed_ship_battery_slot = ship_light_medium_battery_1 fixed_ship_anti_air_slot = empty fixed_ship_fire_control_system_slot = ship_fire_control_system_0 fixed_ship_radar_slot = empty fixed_ship_engine_slot = cruiser_ship_engine_1 fixed_ship_armor_slot = ship_armor_cruiser_1 mid_1_custom_slot = ship_torpedo_1 mid_2_custom_slot = empty rear_1_custom_slot = empty }
 }
 set_naval_oob = "TAG_pacific_naval"
}
else = {
 set_technology = { early_destroyer = 1 early_light_cruiser = 1 }
 set_naval_oob = "TAG_pacific_naval_legacy"
}
'''.replace('TAG',tag)
    write(hp,history+'\n'+design)
    for legacy in [False,True]:
        ships=''
        for kind,count in [('cruiser',cruisers),('escort',escorts)]:
            typ=('light_cruiser_1' if kind=='cruiser' else 'destroyer_1') if legacy else ('ship_hull_cruiser_1' if kind=='cruiser' else 'ship_hull_light_1')
            version='' if legacy else f'version_name = "Pacific {"Cruiser" if kind=="cruiser" else "Escort"}"'
            for i in range(1,count+1):
                ships+=f'ship = {{ name = "{tag} {kind.title()} {i}" definition = {"light_cruiser" if kind=="cruiser" else "destroyer"} start_experience_factor = 0.20 equipment = {{ {typ} = {{ amount = 1 owner = {tag} {version} }} }} }}\n'
        write(f'history/units/{tag}_pacific_naval'+('_legacy' if legacy else '')+'.txt',f'units = {{ fleet = {{ name = "{tag} Pacific Fleet" naval_base = {port} task_force = {{ name = "{tag} Main Squadron" location = {port}\n'+ships+'} } }\n')

# Fit the old and new focus branches into a compact layout.
fp='common/national_focus/a01_focus.txt'; t=(ROOT/fp).read_text()
t=t.replace('continuous_focus_position = { x = 50 y = 1000 }','continuous_focus_position = { x = 1100 y = 1450 }')
def shift(m): return m.group(1)+str(int(m.group(2))-22)
t=re.sub(r'(\bx = )(\d+)',shift,t) # continuous position is in pixels, fix separately below
t=t.replace('x = 1078 y = 1450','x = 1100 y = 1450')
t=t.rsplit('}',1)[0]+focus('A01','admiralty_diplomacy','Дипломатия канонерок','Gunboat Diplomacy',23,8,['archipelago_command'],'if = { limit = { country_exists = A03 NOT = { has_war_with = A03 } } A03 = { country_event = { id = pacific.1 days = 2 } } }',icon='batavia',desc='Адмиралы уверены, что усиленный флот заставит Японию считаться с Батавией. Предложим торговые гарантии с позиции силы, сохранив готовность защищать Борнео.')+'}\n'

# Give each branch a readable visual vocabulary using existing shipped art,
# while reserving generated emblems for national/political milestones.
icons={
'java_development':'GFX_goal_pacific_industry','archipelago_shipping':'GFX_goal_generic_construct_naval_dockyard','sumatran_railways':'GFX_goal_generic_construct_infrastructure',
'surabaya_arsenal':'GFX_goal_generic_construct_mil_factory','batavia_docks':'GFX_goal_generic_construct_naval_dockyard','rubber_processing':'GFX_focus_generic_rubber_plantations',
'local_rifles':'GFX_goal_generic_small_arms','technical_college':'GFX_goal_generic_scientific_exchange','knil_reform':'GFX_goal_pacific_army','island_garrisons':'GFX_goal_generic_allies_build_infantry',
'marine_brigades':'GFX_goal_generic_amphibious_assault','jungle_supply':'GFX_goal_generic_construct_infrastructure','coastal_watch':'GFX_goal_generic_navy_doctrines_tactics',
'colonial_charter':'GFX_goal_pacific_batavia','admiralty_shipyards':'GFX_goal_generic_construct_naval_dockyard','military_industry':'GFX_goal_generic_construct_mil_factory',
'defence_in_depth':'GFX_goal_generic_fortify_city','wartime_industry':'GFX_goal_generic_construct_mil_factory','secure_sea_lanes':'GFX_goal_generic_navy_doctrines_tactics',
'osaka_industry':'GFX_goal_pacific_industry','kansai_railways':'GFX_goal_generic_construct_infrastructure','hiroshima_arsenal':'GFX_goal_generic_construct_mil_factory',
'steel_contracts':'GFX_goal_generic_production','standard_rifles':'GFX_goal_generic_small_arms','imperial_university':'GFX_goal_generic_scientific_exchange','electrical_workshops':'GFX_goal_generic_construct_civ_factory',
'industrial_power':'GFX_goal_generic_production','kure_yards':'GFX_goal_generic_construct_naval_dockyard','merchant_marine':'GFX_goal_generic_construct_naval_dockyard',
'naval_academy':'GFX_goal_generic_navy_doctrines_tactics','island_supply':'GFX_goal_generic_construct_infrastructure','fleet_exercises':'GFX_goal_generic_navy_doctrines_tactics',
'conscription_register':'GFX_goal_generic_allies_build_infantry','landing_forces':'GFX_goal_generic_amphibious_assault','field_artillery':'GFX_goal_generic_army_artillery','expeditionary_staff':'GFX_goal_generic_army_doctrines',
'resource_commission':'GFX_goal_generic_oil_refinery','southern_bases':'GFX_goal_generic_construct_naval_dockyard','southern_campaign':'GFX_goal_pacific_army','southern_reconstruction':'GFX_goal_generic_construct_civ_factory',
'A01_constitution':'GFX_goal_pacific_batavia','A01_wtc_oil_and_rubber_offer':'GFX_goal_pacific_industry','A01_admirals_council_coup':'GFX_goal_pacific_batavia'}
def replace_icons(text):
    for key,icon in icons.items():
        pattern=r'(id = '+(re.escape(key) if key.startswith('A01_') else r'A0[13]_'+re.escape(key))+r'\s+icon = )\S+'
        text=re.sub(pattern,lambda m:m.group(1)+icon,text)
    return text
write(fp,replace_icons(t))
fp='common/national_focus/a03_focus.txt';write(fp,replace_icons((ROOT/fp).read_text()))

# No second countdown or surprise war after a signed convention.
fp='common/decisions/A01_inevitable_conflict.txt';original=ROOT/'tools/backups/pacific_before'/fp;t=(original if original.exists() else ROOT/fp).read_text(encoding='utf-8-sig')
t=t.replace('NOT = { has_war_with = A03 }','NOT = { has_war_with = A03 }\n            NOT = { has_country_flag = pacific_trade_accord }\n            country_exists = A03')
t=t.replace('has_war_with = A03\n\t\t}', 'OR = { has_war_with = A03 has_country_flag = pacific_trade_accord NOT = { country_exists = A03 } }\n\t\t}')
t=t.replace('set_country_flag = A01_japanese_invasion_begun\n\t\t}', 'if = { limit = { has_war_with = A03 } set_country_flag = A01_japanese_invasion_begun }\n\t\t}')
write(fp,t)
fp='events/A01_japan_events.txt';original=ROOT/'tools/backups/pacific_before'/fp;t=(original if original.exists() else ROOT/fp).read_text(encoding='utf-8-sig')
t=t.replace('id = A01_japan.1\n','id = A01_japan.1\n    trigger = { country_exists = A03 NOT = { has_war_with = A03 } NOT = { has_country_flag = pacific_trade_accord } NOT = { has_country_flag = A01_refused_japanese_ultimatum } }\n',1)
write(fp,t)
fp='events/pacific_diplomacy.txt';t=(ROOT/fp).read_text()
for n in [1,3,4]:
    target='A01' if n==1 else 'A03'
    t=t.replace(f'id = pacific.{n} title',f'id = pacific.{n} trigger = {{ country_exists = {target} NOT = {{ has_war_with = {target} }} NOT = {{ has_country_flag = pacific_trade_accord }} }} title')
write(fp,t)

# Professionally written descriptions replace the generator's drafting text.
descriptions={
'java_development':('Государственные заказы свяжут мастерские Батавии и предприятия Явы. Новые фабрики обеспечат архипелаг собственными промышленными товарами.','State orders will connect Batavia workshops with Java enterprises. New factories will supply the archipelago with locally produced goods.'),
'archipelago_shipping':('Островное государство живёт морем. Регулярные каботажные рейсы соединят удалённые порты и создадут резерв судов на случай войны.','An island state lives by the sea. Regular coastal services will connect remote ports and provide a reserve of merchant vessels in wartime.'),
'sumatran_railways':('Плантации и порты Суматры разделяют сотни километров труднопроходимой местности. Железнодорожное строительство сократит путь от склада до причала.','Difficult terrain separates Sumatra plantations from their ports. Railway construction will shorten the journey from warehouse to quay.'),
'surabaya_arsenal':('Сурабая станет центром ремонта оружия и выпуска боеприпасов. Армия не должна зависеть от каждого транспорта, прибывающего из Европы.','Surabaya will become a centre for arms repair and ammunition production. The army cannot depend on every transport arriving from Europe.'),
'batavia_docks':('Углубление гаваней и новые сухие доки позволят обслуживать эскадру в Батавии. Повреждённым кораблям больше не придётся искать ремонт за пределами наших вод.','Deeper harbours and new dry docks will service the squadron in Batavia. Damaged ships will no longer need to seek repairs abroad.'),
'rubber_processing':('Вывозить сырой каучук проще, чем развивать переработку, но прибыль остаётся за морем. Построим предприятия рядом с суматранскими плантациями.','Exporting raw rubber leaves much of the profit overseas. Processing plants beside the Sumatran plantations will keep more value at home.'),
'local_rifles':('Единые чертежи и взаимозаменяемые детали позволят собирать винтовки в местных мастерских. Первые партии поступят в гарнизоны архипелага.','Standard drawings and interchangeable parts will allow local workshops to assemble service rifles. The first batches will equip island garrisons.'),
'technical_college':('Колонии нужны инженеры, способные строить мосты, ремонтировать машины и проектировать корабли. Технический институт подготовит собственные научные кадры.','The colony needs engineers to build bridges, repair machinery and design ships. A technical institute will train our own scientific staff.'),
'island_garrisons':('Крупные гарнизоны на Яве не успеют отразить каждую высадку. Подготовим местные резервы и заранее распределим оружие между островами.','Large Java garrisons cannot respond to every landing. Local reserves and distributed arms depots will give each island a first line of defence.'),
'marine_brigades':('Для возвращения потерянных портов нужны части, способные высадиться с моря. Морские бригады будут обучаться вместе с корабельными командами.','Recovering a lost port requires troops trained to land from the sea. Marine brigades will exercise alongside ship crews.'),
'jungle_supply':('Без продовольствия и боеприпасов оборона джунглей быстро рассыпается. Складские команды и местные проводники наладят доставку за пределами дорог.','Jungle defences collapse without food and ammunition. Depot teams and local guides will carry supplies beyond the roads.'),
'coastal_watch':('Наблюдательные посты у проливов предупредят флот о приближении противника. Портовые мастерские обеспечат патрульным судам постоянное обслуживание.','Lookout posts beside the straits will warn the fleet of approaching enemies. Port workshops will keep patrol vessels in service.'),
'colonial_hierarchy':('Часть чиновников считает уступки угрозой порядку. Сохраним их поддержку, приняв политическую цену дальнейшего отчуждения местного населения.','Some officials see concessions as a threat to order. Keeping their support means accepting the political cost of further alienating the local population.'),
'sultans_compact':('Местные правители готовы обсуждать совместную оборону при условии уважения их полномочий. Постоянный совет даст переговорам официальный характер.','Local rulers will discuss common defence if their authority is respected. A permanent council will give negotiations an official forum.'),
'admiralty_shipyards':('Адмиральский режим направит казённые средства на расширение верфей Сурабаи. Контроль над морем потребует постоянного пополнения флота.','The admiralty government will finance an expansion of Surabaya shipyards. Sea control requires a steady programme of naval construction.'),
'naval_general_staff':('Разрозненные эскадры нуждаются в едином плане. Морской генеральный штаб согласует разведку, ремонт и боевое развёртывание.','Scattered squadrons need a common plan. A naval general staff will coordinate reconnaissance, repairs and operational deployment.'),
'military_industry':('Прямые заказы администрации позволят расширить яванские оружейные мастерские. Военные предприятия получат приоритет при распределении материалов.','Direct government orders will expand Java arms workshops. Military factories will receive priority in the allocation of materials.'),
'defence_in_depth':('Удержать каждую бухту невозможно. Подготовленные рубежи и резервы позволят сдержать противника после высадки и выиграть время для контрудара.','We cannot hold every bay. Prepared positions and reserves will contain a landing and buy time for a counterattack.'),
'archipelago_command':('Армия и флот должны защищать один архипелаг, а не собственные ведомственные интересы. Единое командование объединит планы обороны.','Army and navy defend the same archipelago. Unified command will bring their defensive plans together.'),
'wartime_industry':('Мирные контракты уступят место срочным оборонным заказам. Дополнительный выпуск оружия потребует отвлечь рабочих и материалы от гражданских нужд.','Urgent defence orders will replace peacetime contracts. Increased arms output will divert labour and materials from civilian needs.'),
'secure_sea_lanes':('Потеря транспортов может оказаться опаснее потери отдельного острова. Пополним торговый тоннаж и отработаем проводку конвоев через проливы.','Losing transports may be more dangerous than losing a single island. We will replace merchant tonnage and practise escorting convoys through the straits.'),
'civil_government':('Гражданские министры предлагают укрепить империю через устойчивые финансы и торговлю. Военные сохранят влияние, но не будут определять каждый государственный заказ.','Civilian ministers seek strength through sound finances and commerce. The military will retain influence without directing every government order.'),
'naval_government':('Морское ведомство берёт на себя руководство кабинетом. Безопасность проливов и снабжение заморских баз станут главными государственными задачами.','The naval ministry will lead the cabinet. Securing the straits and supplying overseas bases will become central state priorities.'),
'prefectural_reform':('Общие правила налогообложения и отчётности укрепят связь столицы с префектурами. Правительство получит средства для последовательной программы реформ.','Common tax and reporting rules will strengthen ties between the capital and the prefectures, funding a sustained programme of reform.'),
'commercial_diplomacy':('Торговые дома способны открыть двери, закрытые для военных делегаций. Поддержим постоянные представительства в главных портах Тихого океана.','Trading houses can open doors closed to military delegations. Permanent missions will represent our interests in the principal Pacific ports.'),
'pacific_prosperity':('Договор с Батавией обеспечил поставки сырья. Теперь промышленники Кансая смогут вкладывать средства в новые фабрики, рассчитывая на устойчивую торговлю.','The Batavia agreement has secured raw material supplies. Kansai industrialists can now invest in new factories backed by reliable trade.'),
'southern_strategy':('Южные морские пути ведут к сырью и опорным пунктам империи. Штаб флота подготовит общий план действий на случай провала дипломатии.','Southern sea routes lead to imperial resources and bases. The naval staff will prepare a common plan should diplomacy fail.'),
'resource_commission':('Промышленности нужен точный учёт запасов и поставок. Ресурсная комиссия согласует потребности заводов с возможностями торгового флота.','Industry needs reliable accounts of stocks and deliveries. A resource commission will match factory demand with merchant shipping capacity.'),
'southern_bases':('Палау станет промежуточной базой между метрополией и южными морями. Новые мастерские и транспортные суда поддержат длительную кампанию.','Palau will serve as a staging base between the home islands and the southern seas. Workshops and transports will sustain a prolonged campaign.'),
'southern_campaign':('Батавия отвергла требования империи. Флоту предстоит прикрыть десантную операцию, целью которой станут нефтяные районы Борнео.','Batavia has rejected imperial demands. The fleet must cover a landing operation aimed at the oil districts of Borneo.'),
'southern_reconstruction':('Захваченные нефтяные районы должны вернуться к работе. Восстановим мастерские, порты и гражданское производство Восточного Калимантана.','The occupied oil districts must resume production. We will restore workshops, ports and civilian industry in East Kalimantan.'),
'osaka_industry':('Осакские торговые дома и мастерские способны стать основой современной промышленности. Государство поддержит строительство крупных фабрик.','Osaka trading houses and workshops can underpin modern industry. The government will support construction of larger factories.'),
'kansai_railways':('Железные дороги соединят заводы Осаки с промышленными районами Нагои. Регулярные перевозки сократят расходы и ускорят развёртывание войск.','Railways will link Osaka factories with Nagoya industry. Regular transport will reduce costs and accelerate troop deployment.'),
'hiroshima_arsenal':('Хиросимские мастерские получат оборудование для серийного выпуска оружия. Расширение арсенала сократит зависимость армии от иностранных поставщиков.','Hiroshima workshops will receive machinery for series production. An expanded arsenal will reduce dependence on foreign arms suppliers.'),
'steel_contracts':('Долгосрочные контракты дадут металлургам уверенность в будущих заказах. Стабильные поставки металла ускорят строительство предприятий.','Long-term contracts will give steel producers confidence in future orders. Reliable metal supplies will accelerate industrial construction.'),
'standard_rifles':('Разнородные винтовки затрудняют снабжение полков. Единый образец оружия и общие требования к деталям упростят производство и ремонт.','Mixed rifle types complicate regimental supply. A standard service weapon and common parts will simplify production and repair.'),
'imperial_university':('Инженерные кафедры должны работать вместе с арсеналами и верфями. Новый университет обеспечит промышленность собственными специалистами.','Engineering faculties must work alongside arsenals and shipyards. A new university will provide industry with trained specialists.'),
'electrical_workshops':('Телеграфы, генераторы и измерительные приборы требуют новых производственных навыков. Создадим предприятия для растущей электротехнической отрасли.','Telegraphs, generators and instruments demand new manufacturing skills. Dedicated workshops will support the growing electrical industry.'),
'industrial_power':('Сеть арсеналов должна выпускать оружие в масштабах всей империи. Расширение предприятий Хиросимы завершит первую промышленную программу.','The arsenal network must produce arms on an imperial scale. Expanding Hiroshima factories will complete the first industrial programme.'),
'naval_programme':('Разовые закупки не создают сильного флота. Программа строительства в Нагасаки обеспечит регулярную закладку и ремонт кораблей.','Occasional purchases cannot build a strong navy. A Nagasaki construction programme will provide regular shipbuilding and repairs.'),
'kure_yards':('Гавани Куре подходят для создания крупного судостроительного центра. Расширенные доки позволят обслуживать растущую эскадру.','Kure harbours are suited to a major shipbuilding centre. Expanded docks will support the growing squadron.'),
'merchant_marine':('Без торговых судов заморские базы останутся без снабжения. Государственные заказы пополнят тоннаж и подготовят новые экипажи.','Overseas bases need merchant shipping to survive. Government orders will add tonnage and train new crews.'),
'naval_academy':('Офицерам необходимы общие знания навигации, артиллерии и управления соединениями. Академия введёт единые стандарты подготовки флота.','Officers need common instruction in navigation, gunnery and formation command. The academy will establish consistent training standards.'),
'island_supply':('Снабжение дальних гарнизонов требует точного расписания рейсов и запасных складов. Организуем постоянную службу островных конвоев.','Distant garrisons require scheduled sailings and reserve depots. A permanent island convoy service will coordinate their supply.'),
'fleet_exercises':('Корабли должны учиться действовать вместе до начала войны. Большие манёвры проверят связь, разведку и взаимодействие эскадр.','Ships must learn to operate together before war begins. Major manoeuvres will test communications, reconnaissance and squadron coordination.'),
'army_reorganisation':('Единые штаты и постоянные полевые сборы укрепят армию западных префектур. Опыт частей станет основой общих наставлений.','Standard establishments and regular field exercises will strengthen the western prefectural army. Unit experience will shape common manuals.'),
'conscription_register':('Полные списки военнообязанных позволят заранее подготовить пополнение. Резервисты пройдут обучение, прежде чем получат боевые назначения.','Complete service registers will allow replacements to be prepared in advance. Reservists will train before receiving operational assignments.'),
'landing_forces':('Борьба за острова требует особой подготовки. Десантные отряды освоят высадку, захват причалов и удержание плацдармов.','Island warfare requires specialised training. Landing forces will practise going ashore, seizing quays and holding bridgeheads.'),
'field_artillery':('Пехота нуждается в надёжной огневой поддержке. Расширение оружейных предприятий Сикоку обеспечит основу артиллерийского снабжения.','Infantry needs reliable fire support. Expanding Shikoku arms factories will underpin artillery supply.'),
'expeditionary_staff':('Заморская операция начинается с расчёта грузов и маршрутов. Экспедиционный штаб согласует перевозки, высадку и снабжение войск.','An overseas operation begins with cargo lists and routes. Expeditionary staff will coordinate transport, landings and troop supply.'),
'combined_operations':('Армейские и морские штабы проведут общие учения. Только согласованные действия позволят развить успех после захвата побережья.','Army and naval staffs will hold joint exercises. Coordinated action is essential to exploit a successful coastal landing.')}
for lang,index in [('russian',0),('english',1)]:
    p=f'localisation/{lang}/pacific_content_l_{lang}.yml';t=(ROOT/p).read_text(encoding='utf-8-sig')
    for key,desc in descriptions.items():
        t=re.sub(r'( A0[13]_'+key+r'_desc:0 ).*',lambda m:m.group(1)+json.dumps(desc[index],ensure_ascii=False),t)
    # The extra admiral focus is created after the first localisation write.
    for key in ['A01_admiralty_diplomacy','A01_admiralty_diplomacy_desc']:
        t+=f' {key}:0 {json.dumps(loc[key][index],ensure_ascii=False)}\n'
    write(p,t,True)
print('Naval OOBs, compact focus layout, art mapping, diplomacy guards and individual focus descriptions written.')
