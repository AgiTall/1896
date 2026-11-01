"""Player-led political preparation, mutually exclusive policies and consistent focus art."""
from extend_japan_story import R,read,write,span
import re,json
L={}
def loc(k,ru,en):L[k]=[ru,en]
def named(k,ru,en,rd,ed):loc(k,ru,en);loc(k+'_desc',rd,ed)
def replace_block(part,key,body):
 m=re.search(r'\b'+key+r'\s*=\s*\{',part)
 if not m:return part[:-1]+f' {key} = {{ {body} }}\n}}'
 i=m.end();depth=1
 while depth:
  depth+=(part[i]=='{')-(part[i]=='}');i+=1
 return part[:m.start()]+f'{key} = {{ {body} }}'+part[i:]
def main():
 p='common/national_focus/a03_focus.txt';s=read(p)
 if '# JPX canonical gateway' in s:
  raise SystemExit('Japan now has political gateways. Refusing to overwrite their prerequisites and layout; edit the current files or prepare_japan_paths.py.')
 def change(fid,cost=None,parent=None,xy=None,reward=None,available=None,icon=None,exclusive=None):
  nonlocal s
  a,b=span(s,fid);part=s[a:b]
  for k,v in [('cost',cost),('x',xy[0] if xy else None),('y',xy[1] if xy else None)]:
   if v is not None:part=re.sub(r'\b'+k+r'\s*=\s*\d+',f'{k} = {v}',part,count=1)
  if parent is not None:part=replace_block(part,'prerequisite',' '.join('focus = '+f for f in parent))
  if reward is not None:part=replace_block(part,'completion_reward',reward)
  if available is not None:part=replace_block(part,'available',available)
  if exclusive:part=replace_block(part,'mutually_exclusive','focus = '+exclusive)
  if icon:part=re.sub(r'\bicon\s*=\s*\w+',f'icon = GFX_goal_unique_{icon}',part,count=1)
  s=s[:a]+part+s[b:]
 change('A03_imperial_council',cost=2,reward='JPF_initialize_effect = yes JPN_north_initialize_effect = yes JPL_initialize_effect = yes if = { limit = { NOT = { has_country_flag = JPC_chapter_1 } } set_country_flag = JPC_chapter_1 country_event = { id = japan_canon.1 days = 1 } } add_political_power = 25')
 change('JPC_state_guarantees',cost=5,parent=['A03_imperial_council'],xy=(4,1),available='',reward='JPA_negotiate_guarantees_effect = yes')
 change('JPC_northern_protocol',cost=5,parent=['A03_imperial_council'],xy=(12,1),available='country_exists = A08 NOT = { has_war_with = A08 }',reward='JPA_negotiate_north_effect = yes')
 change('JPC_manila_priority',cost=5,parent=['A03_imperial_council'],xy=(28,1),available='',reward='set_country_flag = JPA_manila_prepared JPL_manila_priority_effect = yes add_to_variable = { JPL_garrison_burden = -10 } JPL_refresh_effect = yes add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 300 producer = A03 }')
 change('JPC_batavia_demands',cost=5,parent=['A03_imperial_council'],xy=(20,1),available='',reward='set_country_flag = JPA_dutch_prepared add_command_power = 15 navy_experience = 10')
 change('JPC_one_war_cabinet',cost=5,parent=['JPC_state_guarantees','JPC_northern_protocol','JPC_manila_priority','JPC_batavia_demands'],xy=(20,5),available='has_war_with = A01')
 change('JPC_no_short_war',available='has_war_with = A01')
 change('JPC_1895_accounts',available='has_war_with = A01')
 change('JPC_honshu_depots',parent=['JPN_north_civilian_holds','JPN_north_emergency_calendar'],xy=(12,3))
 change('JPC_garrison_accounts',parent=['JPL_convoy_timetable','JPL_names_and_units'],xy=(28,3))
 change('JPC_osaka_orders',parent=['JPF_public_accounts','JPF_small_subscription'],xy=(4,3))
 change('JPC_iwasaki_accounts',xy=(4,4))
 change('JPF_bond_register',xy=(4,5))
 # Three substantive policy pairs. Common downstream institutions accept either sibling.
 change('JPF_public_accounts',cost=5,parent=['JPC_state_guarantees'],xy=(2,2),exclusive='JPF_small_subscription')
 change('JPF_small_subscription',cost=2,parent=['JPC_state_guarantees'],xy=(6,2),exclusive='JPF_public_accounts',reward='set_country_flag = JPF_subscription_open set_country_flag = JPA_private_credit add_to_variable = { JPF_debt_pressure = 10 } add_to_variable = { JPF_budget_confidence = 5 } add_equipment_to_stockpile = { type = convoy_1 amount = 20 producer = A03 } JPF_refresh_effect = yes')
 change('JPF_delivery_calendar',parent=['JPF_public_accounts','JPF_small_subscription'])
 change('JPN_north_civilian_holds',cost=4,parent=['JPC_northern_protocol'],xy=(10,2),exclusive='JPN_north_emergency_calendar')
 change('JPN_north_emergency_calendar',cost=2,parent=['JPC_northern_protocol'],xy=(14,2),exclusive='JPN_north_civilian_holds',reward='set_country_flag = JPN_north_emergency_schedule add_to_variable = { JPN_north_fleet_irritation = -8 } add_to_variable = { JPN_north_trust = -5 } JPN_north_refresh_effect = yes')
 change('JPL_convoy_timetable',cost=4,parent=['JPC_manila_priority'],xy=(26,2),exclusive='JPL_names_and_units',reward='set_country_flag = JPA_manila_first add_ideas = JPA_manila_escorts JPL_escort_allocation_effect = yes add_to_variable = { JPL_garrison_burden = -8 } JPL_refresh_effect = yes')
 change('JPL_names_and_units',cost=2,parent=['JPC_manila_priority'],xy=(30,2),exclusive='JPL_convoy_timetable',reward='set_country_flag = JPA_borneo_first set_country_flag = JPL_rotation_board add_ideas = JPA_borneo_escorts add_to_variable = { JPL_garrison_burden = 8 } add_to_variable = { JPL_garrison_fatigue = 5 } JPL_refresh_effect = yes navy_experience = 15')
 change('JPL_limited_mandate',parent=['JPL_supply_board','JPL_quartermaster_school'])
 # After the war, private creditors can finally be brought under public scrutiny.
 a,b=span(s,'JPF_return_small_savings');part=s[a:b]
 if 'JPF_reform_accounts_effect' not in part:part=part.replace('completion_reward = {','completion_reward = { JPF_reform_accounts_effect = yes',1)
 s=s[:a]+part+s[b:]
 icons={
 'JPF_bond_register':'A01_governors_secretariat','JPF_public_accounts':'A01_constitution','JPF_small_subscription':'A01_invest_in_mass_consumer_goods','JPF_excise_bargain':'A01_civilian_procurement','JPF_delivery_calendar':'A01_naval_budget_compromise','JPF_coal_not_glory':'A03_merchant_marine','JPF_madeira_table':'A01_wtc_oil_and_rubber_offer','JPF_royalty_register':'A01_rubber_processing','JPF_return_small_savings':'A01_reconstruction_commission','JPF_civil_budget':'A01_pacific_settlement',
 'JPN_north_supply_register':'A01_prepare_bornean_logistics','JPN_north_civilian_holds':'A01_archipelago_shipping','JPN_north_emergency_calendar':'A01_naval_general_staff','JPN_north_inspection_channel':'A01_officers_audience','JPN_north_tokyo_auditors':'A01_governors_secretariat','JPN_north_admiralty_hearing':'A01_admirals_council_coup','JPN_north_imperial_arbitration':'A03_imperial_council','JPN_north_postwar_audience':'A01_last_chance_to_negotiate','JPN_north_permanent_protocol':'A01_sultans_compact','JPN_north_keep_distance':'A01_federal_defence_compact',
 'JPL_port_and_mountains':'A01_jungle_supply','JPL_convoy_timetable':'A01_secure_sea_lanes','JPL_names_and_units':'A01_island_garrisons','JPL_municipal_buyers':'A01_civilian_procurement','JPL_payroll_inquiry':'A01_governors_secretariat','JPL_supply_board':'A01_prepare_bornean_logistics','JPL_quartermaster_school':'A01_technical_college','JPL_medical_rotation':'A01_equal_service','JPL_limited_mandate':'A01_colonial_charter','JPL_borneo_is_not_luzon':'A03_expeditionary_staff',
 'JPC_state_guarantees':'A01_naval_budget_compromise','JPC_iwasaki_accounts':'A01_governors_secretariat','JPC_one_war_cabinet':'A03_expeditionary_staff','JPC_casualty_returns':'A01_equal_service','JPC_wtc_mission':'A01_wtc_oil_and_rubber_offer','JPC_no_short_war':'A01_wartime_industry','JPC_imperial_inspection':'A01_officers_audience','JPC_1895_accounts':'A01_civilian_procurement','JPC_hold_until_talks':'A01_admiralty_diplomacy','JPC_count_the_cost':'A01_reconstruction_commission','JPC_oil_promise':'A01_rubber_processing','JPC_partial_demobilisation':'A01_fleet_of_recovery','JPC_three_heads_again':'A03_imperial_council'}
 for fid,icon in icons.items():change(fid,icon=icon)
 # Continuous focuses use absolute GUI pixels, not focus grid coordinates.
 s=re.sub(r'continuous_focus_position\s*=\s*\{[^}]+\}','continuous_focus_position = { x = 100 y = 3300 }',s)
 if '# JPA player-led preparation' not in s:s='# JPA player-led preparation\n'+s
 write(p,s)
 # Calendar brings external threats and reminders. It no longer completes domestic bargains.
 p='common/on_actions/JPC_canonical.txt';s=read(p)
 s=re.sub(r'if = \{ limit = \{ date > 1893\.1\.1 NOT = \{ has_country_flag = JPC_chapter_1 \}  \}[^\n]+\n','',s)
 s=re.sub(r'if = \{ limit = \{ date > 1893\.1\.31[^\n]+\n','if = { limit = { date > 1893.1.31 NOT = { has_country_flag = JPA_finance_warning } NOT = { has_country_flag = JPC_guarantees_signed } } set_country_flag = JPA_finance_warning country_event = { id = japan_agency.1 days = 1 } }\n',s)
 s=re.sub(r'if = \{ limit = \{ date > 1893\.2\.28[^\n]+\n','if = { limit = { date > 1893.2.28 NOT = { has_country_flag = JPA_north_warning } NOT = { has_country_flag = JPC_north_signed } } set_country_flag = JPA_north_warning country_event = { id = japan_agency.2 days = 1 } }\n',s)
 write(p,s)
 p='common/scripted_effects/JPC_canonical.txt';s=read(p)
 if 'JPA_emergency_compromises_effect = yes' not in s:s=s.replace('set_country_flag = JPC_ultimatum_sent','JPA_emergency_compromises_effect = yes\n  set_country_flag = JPC_ultimatum_sent')
 write(p,s)
 write('common/scripted_effects/JPA_agency.txt','''JPA_negotiate_guarantees_effect = {
 remove_ideas = JPA_forced_guarantees
 if = { limit = { NOT = { has_country_flag = JPC_chapter_2 } }
  set_country_flag = JPC_chapter_2 country_event = { id = japan_canon.2 days = 1 }
 }
 else = { add_to_variable = { JPF_debt_pressure = -5 } add_to_variable = { JPF_budget_confidence = 5 } JPF_refresh_effect = yes }
}
JPA_negotiate_north_effect = {
 remove_ideas = JPA_unwritten_neutrality
 if = { limit = { NOT = { has_country_flag = JPC_chapter_3 } }
  set_country_flag = JPC_chapter_3 country_event = { id = japan_canon.3 days = 1 }
 }
 JPN_north_protocol_focus_effect = yes
 add_to_variable = { JPN_north_trust = 10 } JPN_north_refresh_effect = yes
}
JPA_emergency_compromises_effect = {
 # Canonical war proceeds, but incomplete domestic work has a persistent price.
 JPF_initialize_effect = yes JPN_north_initialize_effect = yes JPL_initialize_effect = yes
 if = { limit = { NOT = { has_country_flag = JPC_guarantees_signed } }
  set_country_flag = JPC_guarantees_signed set_country_flag = JPA_finance_forced
  remove_ideas = JPC_bad_loans add_ideas = JPC_guarantees add_ideas = JPA_forced_guarantees
  add_to_variable = { JPF_debt_pressure = 12 } add_to_variable = { JPF_budget_confidence = -8 }
 }
 if = { limit = { NOT = { has_country_flag = JPC_north_signed } }
  set_country_flag = JPC_north_signed set_country_flag = JPA_north_forced
  add_ideas = JPC_north_neutral add_ideas = JPA_unwritten_neutrality
  add_to_variable = { JPN_north_trust = -15 } add_to_variable = { JPN_north_fleet_irritation = 10 }
  if = { limit = { country_exists = A08 NOT = { has_war_with = A08 } }
   diplomatic_relation = { country = A08 relation = non_aggression_pact }
   A08 = { set_country_flag = JPC_northern_neutrality country_event = { id = japan_canon.33 days = 1 } }
  }
 }
 if = { limit = { NOT = { has_country_flag = JPA_manila_prepared } }
  add_to_variable = { JPL_garrison_burden = 10 } add_to_variable = { JPL_garrison_fatigue = 10 }
 }
 if = { limit = { NOT = { has_country_flag = JPA_dutch_prepared } }
  add_timed_idea = { idea = JPA_hasty_orders days = 120 }
 }
 JPF_refresh_effect = yes JPN_north_refresh_effect = yes JPL_refresh_effect = yes
 country_event = { id = japan_agency.3 days = 1 }
}
JPA_refresh_policy_effect = {
 if = { limit = { has_country_flag = JPA_manila_first has_war_with = A10 NOT = { has_idea = JPA_manila_escorts } } add_ideas = JPA_manila_escorts }
 if = { limit = { has_country_flag = JPA_borneo_first has_war_with = A01 NOT = { has_idea = JPA_borneo_escorts } } add_ideas = JPA_borneo_escorts }
}
''')
 write('common/on_actions/JPA_agency.txt','on_actions = { on_daily = { effect = { A03 = { JPA_refresh_policy_effect = yes } } } }\n')
 # Standard daily/monthly hooks fire per country; country-specific hooks must run once.
 for p in (R/'common/on_actions').glob('JP*.txt'):
  text=read(p.relative_to(R));text=re.sub(r'\bon_daily\s*=', 'on_daily_A03 =',text);text=re.sub(r'\bon_monthly\s*=', 'on_monthly_A03 =',text);write(p.relative_to(R),text)
 p='common/on_actions/WTC_credit.txt'
 write(p,'''on_actions = {
 on_startup = { effect = {
  A04 = { WTC_board_initialize_effect = yes WTC_check_cover_effect = yes }
  every_country = { limit = { NOT = { tag = A04 } } WTC_initialize_effect = yes }
 } }
 on_daily = { effect = {
  if = { limit = { tag = A04 } WTC_board_initialize_effect = yes WTC_check_cover_effect = yes }
  else = { WTC_initialize_effect = yes }
 } }
 on_monthly = { effect = { if = { limit = { NOT = { tag = A04 } } WTC_monthly_effect = yes } } }
}
''')
 write('common/ideas/JPA_agency.txt','''ideas = { country = {
 JPA_forced_guarantees = { picture = jpc_credit removal_cost = -1 modifier = { consumer_goods_factor = 0.03 political_power_gain = -0.05 } }
 JPA_unwritten_neutrality = { picture = jpc_fleet removal_cost = -1 modifier = { stability_factor = -0.03 political_power_gain = -0.05 } }
 JPA_hasty_orders = { picture = jpc_fleet removal_cost = -1 modifier = { navy_org_factor = -0.04 naval_coordination = -0.04 } }
 JPA_manila_escorts = { picture = jpc_fleet removal_cost = -1 cancel = { NOT = { has_war_with = A10 } } modifier = { navy_org_factor = -0.03 } }
 JPA_borneo_escorts = { picture = jpc_fleet removal_cost = -1 cancel = { NOT = { has_war_with = A01 } } modifier = { navy_org_factor = 0.04 naval_coordination = 0.03 } }
} }
''')
 # A standing Philippine priority provides sustained relief, with fleet costs while that war lasts.
 p='common/scripted_effects/JPL_luzon.txt';s=read(p)
 needle='add_to_variable = { JPL_garrison_burden = 2 }\n'
 if 'has_country_flag = JPA_manila_first' not in s:s=s.replace(needle,needle+'  if = { limit = { has_country_flag = JPA_manila_first } add_to_variable = { JPL_garrison_burden = -2 } }\n',1)
 write(p,s)
 # The forced settlement cannot also grant a favourable free negotiation event.
 p='common/scripted_effects/JPF_finance.txt';s=read(p).replace('has_country_flag = JPC_guarantees_signed NOT = { has_country_flag = JPF_guarantee_queued }','has_country_flag = JPC_guarantees_signed NOT = { has_country_flag = JPA_finance_forced } NOT = { has_country_flag = JPF_guarantee_queued }');write(p,s)
 p='common/scripted_effects/JPA_agency.txt';s=read(p).replace('remove_ideas = JPA_forced_guarantees','remove_ideas = JPA_forced_guarantees clr_country_flag = JPA_finance_forced');write(p,s)
 events=[]
 for n,ru,en,rd,ed in [
 (1,'Ивасаки больше не ждёт','Iwasaki Will Wait No Longer','Флот просит денег, но гарантий будущей нефти ещё нет. Пока кабинет не завершит переговоры, Мицубиси продолжит перекладывать на него текущие расходы. Фокус «Государственные гарантии» занимает 35 дней. Если отложить его до ультиматума, кредит придётся принять на навязанных условиях.','The fleet needs money without an oil guarantee. State Guarantees takes 35 days. Delay it until the ultimatum and Mitsubishi will dictate emergency terms.'),
 (2,'Север требует письменного ответа','The North Demands an Answer','Сайго не станет воевать за Борнео. Вопрос в том, будет ли его нейтралитет согласованным договором или односторонним решением. Северный протокол требует 35 дней работы кабинета. Пока министры заняты Севером, нельзя одновременно готовить Манилу.','Saigo will not fight for Borneo. A negotiated protocol takes 35 cabinet days; unilateral neutrality needs none, but damages trust. Time spent on the North cannot also prepare Manila.'),
 (3,'Настало время предъявить счета','The Preparation Bill Falls Due','Ультиматум отправлен. Договорённости, которыми занимался кабинет, вступают в силу на согласованных условиях. Пропущенные направления оплачиваются вынужденными уступками Мицубиси, недоверием Севера, перегрузкой Манилы или спешкой флота. Поздние фокусы позволят исправлять последствия, но уже во время войны.','The ultimatum has gone. Negotiated arrangements retain their terms. Neglected priorities bring forced guarantees, northern mistrust, Manila overload or hurried fleet orders. Late focuses can repair the damage, during the war.')]:
  loc(f'japan_agency.{n}.t',ru,en);loc(f'japan_agency.{n}.d',rd,ed);loc(f'japan_agency.{n}.a','Кабинет отвечает за свой выбор.','The cabinet answers for its choices.')
  events.append(f'country_event = {{ id = japan_agency.{n} title = japan_agency.{n}.t desc = japan_agency.{n}.d picture = GFX_jpc_council is_triggered_only = yes trigger = {{ tag = A03 }} option = {{ name = japan_agency.{n}.a ai_chance = {{ factor = 100 }} }} }}')
 write('events/JPA_agency.txt','add_namespace = japan_agency\n'+'\n'.join(events)+'\n')
 for k,r,e,rd,ed in [
 ('JPA_forced_guarantees','Гарантии, продиктованные Осакой','Guarantees Dictated by Osaka','Кабинет не успел договориться до ультиматума. Завершение фокуса государственных гарантий снимет навязанные условия.','The cabinet missed the ultimatum deadline. Completing State Guarantees removes the imposed terms.'),
 ('JPA_unwritten_neutrality','Односторонний северный нейтралитет','Unilateral Northern Neutrality','Сайго объявил условия сам. Завершить Северный протокол, чтобы заменить диктат договором.','Saigo set the terms himself. Complete the Northern Protocol to negotiate a settlement.'),
 ('JPA_hasty_orders','Приказы в последний момент','Last-minute Orders','Ультиматум предъявлен без согласованного плана действий флота.','The ultimatum went out without an agreed fleet plan.'),
 ('JPA_manila_escorts','Манила получает охранение','Manila Receives the Escorts','Гарнизон разгружен, но борнейская эскадра работает меньшими силами.','Manila’s burden falls while the Borneo squadron operates with fewer ships.'),
 ('JPA_borneo_escorts','Главные силы у Борнео','Main Forces off Borneo','Флот сохраняет готовность ценой более тяжёлой службы на Лусоне.','The fleet retains readiness at the cost of harder service on Luzon.')]:named(k,r,e,rd,ed)
 updates={
 'A03_imperial_council_desc':('До ультиматума 120 дней. Совет занимает 14, каждый из четырёх подготовительных приоритетов — ещё 35. Успеть всё невозможно. Выберите, какие соглашения довести до конца, а какие последствия встретить уже на войне.','There are 120 days until the ultimatum. The council takes 14; each of four preparations takes 35. There is not enough time for everything. Choose which agreements to finish before war.'),
 'JPC_state_guarantees_desc':('35 дней переговоров обеспечат обещанную Мицубиси нефтяную монополию на согласованных условиях. Без фокуса майский ультиматум заставит принять более дорогие гарантии: давление +12, доверие −8 и дополнительная гражданская нагрузка до пересмотра договора.','35 days secure Mitsubishi’s promised oil monopoly on negotiated terms. Missing the deadline forces pressure +12, confidence −8 and an additional civilian burden until renegotiation.'),
 'JPC_northern_protocol_desc':('35 дней на договор о нейтралитете Хоккайдо и графике снабжения. Север не даст дивизий, но получит основания доверять Токио. Пропустить переговоры — значит встретить май с односторонними условиями Сайго и потерей доверия.','35 days negotiate Hokkaido’s neutrality and supplies. No northern divisions join the war. Skipping talks brings unilateral terms and lost trust in May.'),
 'JPC_manila_priority_desc':('Выделить 35 дней на гарнизон до начала второго фронта. Фокус снижает нагрузку, даёт 300 винтовок и открывает дальнейшие меры. Если не успеть к маю, нагрузка и усталость дополнительно вырастут на 10.','Spend 35 days preparing the garrison. Reduce burden, receive 300 rifles and open further measures. Missing May adds 10 burden and 10 fatigue.'),
 'JPC_batavia_demands_desc':('За 35 дней согласовать требования, цели и порядок выхода эскадр. Этот фокус не ускоряет ультиматум; он предотвращает 120 дней штрафов за спешные приказы. Время можно потратить на Мицубиси, Север или Манилу вместо флота.','Spend 35 days coordinating demands and fleet orders. The ultimatum date stays fixed; preparation prevents 120 days of hurried-order penalties. That time could instead go to Mitsubishi, the North or Manila.'),
 'JPC_one_war_cabinet_desc':('После начала войны собрать кабинет военного времени за 35 дней. Достаточно завершить любой один из четырёх подготовительных приоритетов; все остальные можно продолжить позже.','Form a wartime cabinet in 35 days once war begins. Any one of the four preparations is sufficient; the others may be finished later.'),
 'JPF_public_accounts_desc':('35 дней на независимую отчётность: давление −6, доверие +10, затем долг растёт на 1 меньше ежемесячно. Открываются публикации счетов. Исключает быстрый аванс Мицубиси.','35 days for independent accounts: pressure −6, confidence +10, then one less monthly debt growth. Unlocks published accounts. Excludes Mitsubishi’s quick advance.'),
 'JPF_small_subscription_desc':('За 14 дней получить 20 транспортов и доступ к подписке: давление +10, доверие +5. Независимую отчётность придётся отложить до послевоенного расчёта с вкладчиками. Исключает публичный контроль кредита.','In 14 days receive 20 transports and open subscriptions: pressure +10, confidence +5. Independent audits wait until postwar redemption. Excludes public credit control.'),
 'JPN_north_civilian_holds_desc':('28 дней на гражданские фрахты. Открывает три хлебных каравана с меньшим раздражением адмиралтейства. Исключает соглашение об отсрочках: Север получает приоритет исполнения поставок.','28 days to arrange civilian charters. Opens three grain convoys with less naval resentment. Excludes postponements; northern deliveries take priority.'),
 'JPN_north_emergency_calendar_desc':('За 14 дней закрепить две военные отсрочки. Раздражение флота −8, доверие Севера −5. Исключает гражданские хлебные караваны: корабли нужны южной кампании.','In 14 days authorise two wartime postponements. Naval resentment −8, northern trust −5. Excludes civilian grain charters; ships serve the southern campaign.'),
 'JPL_convoy_timetable_desc':('28 дней на постоянный приоритет Манилы. Снизить нагрузку сейчас и её месячный рост на 2, оплачивая охранение и теряя часть организации флота. Исключает приоритет Борнео.','28 days to prioritise Manila. Reduce burden now and monthly growth by 2, paying for escorts and losing fleet organisation. Excludes Borneo priority.'),
 'JPL_names_and_units_desc':('За 14 дней закрепить главные силы за Борнео. Флот получает организацию и координацию; нагрузка Манилы +8, усталость +5. Гарнизон сможет проводить ротации и проверять ведомости, но постоянного охранения не получит. Исключает приоритет Манилы.','In 14 days reserve the main force for Borneo. Gain fleet organisation and coordination; Manila burden +8, fatigue +5. Open rotations and payroll inquiries instead of permanent escorts. Excludes Manila priority.')}
 for k,(ru,en) in updates.items():loc(k,ru,en)
 loc('JPF_public_accounts','Публичный контроль кредита','Public Control of Credit');loc('JPF_small_subscription','Быстрый аванс Мицубиси','Mitsubishi’s Quick Advance')
 loc('JPL_convoy_timetable','Эскорты для Манилы','Escorts for Manila');loc('JPL_names_and_units','Главные силы — Борнео','Main Forces for Borneo')
 loc('JPC_1895_accounts','Смета затяжной войны','The Protracted War Budget')
 loc('JPC_1895_accounts_desc','Пересмотреть военную смету, когда кабинет сочтёт прежние расчёты несостоятельными. Ожидание определённого календарного года не требуется: цена пересмотра — время фокуса.','Revisit the war budget when the cabinet judges its old estimates inadequate. There is no calendar-year lock; the review costs focus time.')
 loc('JPC_no_short_war_desc','Признать, что быстрого решения не будет, и открыть программу восполнения потерь. Это политическое решение можно принять во время войны, не ожидая наступления 1894 года.','Acknowledge that there will be no quick settlement and open replacement programmes. The cabinet can decide during the war without waiting for 1894.')
 # One established localisation file contains every story key, including new files created during debug play.
 for lang,i in [('russian',0),('english',1)]:
  merged={}
  for p in sorted((R/f'localisation/{lang}').glob('*.yml')):
   if any(x in p.name for x in ['JPC','JPS','WTC','JPA']):
    for k,v in re.findall(r'^\s+([^ :]+):\d+\s+"(.*)"\s*$',read(p.relative_to(R)),re.M):merged[k]=v
  merged.update({k:v[i] for k,v in L.items()})
  content='l_'+lang+':\n'+'\n'.join(f' {k}:0 "{v.replace(chr(34),chr(39))}"' for k,v in merged.items())+'\n'
  write(f'localisation/{lang}/zzzzzz_JPC_canonical_l_{lang}.yml',content,True)
  write(f'localisation/{lang}/zzzzzzzzz_JPA_agency_l_{lang}.yml','l_'+lang+':\n'+'\n'.join(f' {k}:0 "{v[i]}"' for k,v in L.items())+'\n',True)
 # Stable load behaviour for retained national-spirit assets, with proper shine masks.
 for p in ['interface/JPS_story.gfx','interface/JPC_canonical.gfx']:
  s=read(p)
  if 'legacy_lazy_load' not in s:s=s.replace('texturefile = "','legacy_lazy_load = no texturefile = "')
  write(p,s)
 p='common/ai_strategy_plans/A01_canonical.txt';s=read(p)
 a=s.index('A03_southern_canonical_plan');prefix=s[:a];tail=s[a:]
 plan=re.search(r'ai_national_focuses = \{ ([^}]+)',tail)[1].split()
 front=['A03_imperial_council','JPC_state_guarantees','JPC_northern_protocol','JPC_manila_priority','JPC_one_war_cabinet']
 # Historical AI takes one member of each mutually exclusive policy pair.
 remove={'JPF_small_subscription','JPN_north_emergency_calendar','JPL_names_and_units'}
 plan=front+[x for x in plan if x not in front and x not in remove]
 tail=re.sub(r'ai_national_focuses = \{ [^}]+','ai_national_focuses = { '+' '.join(plan)+' ',tail);write(p,prefix+tail)
 write('tools/japan_agency_manifest.json',json.dumps({'focus_count':84,'deadline_days':120,'council_days':14,'priority_days':35,'all_four_priorities_days':154,'exclusive_pairs':[['JPF_public_accounts','JPF_small_subscription'],['JPN_north_civilian_holds','JPN_north_emergency_calendar'],['JPL_convoy_timetable','JPL_names_and_units']],'art_references':icons,'continuous_focus_position':[100,3300],'requires_restart_for_new_assets_and_localisation':True},ensure_ascii=False,indent=2))
 print('Reworked four competing preparations, three exclusive policies, 43 icon assignments and localisation.')
if __name__=='__main__':
 main()
 from clarify_japan_branches import apply
 apply()
