"""World Trade Chamber: country debt, maritime leverage and Dutch path entries."""
from extend_japan_story import R,read,write,edit_focus,span
import json,re
L={}
def loc(k,ru,en):L[k]=[ru,en]
def named(k,ru,en,rd,ed):loc(k,ru,en);loc(k+'_desc',rd,ed)
def main():
 write('common/scripted_effects/WTC_credit.txt','''# Current country owns its ledger. Mitsubishi liabilities remain independent.
WTC_initialize_effect = {
 if = { limit = { NOT = { tag = A04 } NOT = { has_country_flag = WTC_ledger_open } }
  set_country_flag = WTC_ledger_open set_variable = { WTC_debt = 10 }
  if = { limit = { tag = A01 } set_variable = { WTC_debt = 35 } }
  if = { limit = { tag = A02 } set_variable = { WTC_debt = 55 } }
  if = { limit = { tag = A03 } set_variable = { WTC_debt = 30 } }
  if = { limit = { tag = A07 } set_variable = { WTC_debt = 15 } }
  if = { limit = { tag = A09 } set_variable = { WTC_debt = 65 } }
  if = { limit = { tag = A10 } set_variable = { WTC_debt = 20 } }
 }
}
WTC_refresh_effect = {
 clamp_variable = { var = WTC_debt min = 0 max = 100 }
 if = { limit = { check_variable = { WTC_debt < 100 } } clr_country_flag = WTC_default_pending }
 if = { limit = { country_exists = A04 NOT = { has_war_with = A04 } }
  if = { limit = { check_variable = { WTC_debt > 90 } }
   add_ideas = WTC_cable_blackout
   if = { limit = { has_global_flag = WTC_british_cover } add_ideas = WTC_blacklist }
   else = { remove_ideas = WTC_blacklist }
   if = { limit = { NOT = { has_country_flag = WTC_sanctions_notice } }
    set_country_flag = { flag = WTC_sanctions_notice days = 180 } country_event = { id = wtc_credit.2 days = 1 }
   }
  }
  else = { remove_ideas = WTC_blacklist remove_ideas = WTC_cable_blackout }
  if = { limit = { check_variable = { WTC_debt > 70 } check_variable = { WTC_debt < 100 } NOT = { has_country_flag = WTC_concession_cooldown } }
   set_country_flag = { flag = WTC_concession_cooldown days = 180 } country_event = { id = wtc_credit.1 days = 3 }
  }
  if = { limit = { check_variable = { WTC_debt > 99 } NOT = { has_country_flag = WTC_default_pending } }
   set_country_flag = WTC_default_pending country_event = { id = wtc_credit.3 days = 7 }
  }
 }
 else = { remove_ideas = WTC_blacklist remove_ideas = WTC_cable_blackout clr_country_flag = WTC_default_pending }
}
WTC_borrow_effect = {
 WTC_initialize_effect = yes add_to_variable = { WTC_debt = 20 }
 set_country_flag = { flag = WTC_active_loan days = 180 }
 add_equipment_to_stockpile = { type = convoy_1 amount = 25 producer = A04 }
 A04 = { add_political_power = 15 } WTC_refresh_effect = yes
}
WTC_repay_effect = { add_to_variable = { WTC_debt = -12 } WTC_refresh_effect = yes }
WTC_concession_effect = {
 add_to_variable = { WTC_debt = -15 }
 add_timed_idea = { idea = WTC_port_concession days = 240 }
 A04 = { add_political_power = 20 } WTC_refresh_effect = yes
}
WTC_financial_coup_effect = {
 # The Chamber installs a local administrator; it cannot annex or rule provinces.
 create_country_leader = { name = WTC_receiver_name desc = WTC_receiver_desc ideology = despotism expire = "1970.1.1" }
 set_politics = { ruling_party = neutrality elections_allowed = no }
 add_popularity = { ideology = neutrality popularity = 0.30 }
 add_stability = -0.15 add_war_support = -0.05
 set_country_flag = WTC_receivership set_variable = { WTC_debt = 70 }
 add_ideas = WTC_local_receivership clr_country_flag = WTC_default_pending
 WTC_refresh_effect = yes
}
WTC_monthly_effect = {
 WTC_initialize_effect = yes
 if = { limit = { country_exists = A04 NOT = { has_war_with = A04 } NOT = { tag = A04 } }
  if = { limit = { check_variable = { WTC_debt > 0 } } add_political_power = -2 }
  if = { limit = { has_country_flag = WTC_active_loan } add_to_variable = { WTC_debt = 1 } }
  if = { limit = { has_war = yes check_variable = { WTC_debt > 29 } } add_to_variable = { WTC_debt = 1 } }
  if = { limit = { has_idea = WTC_port_concession } add_to_variable = { WTC_debt = -1 } }
  WTC_refresh_effect = yes
 }
}
WTC_board_initialize_effect = {
 if = { limit = { NOT = { has_country_flag = WTC_board_initialized } }
  set_country_flag = WTC_board_initialized set_variable = { WTC_old_guard = 45 } set_variable = { WTC_technocrats = 30 } set_variable = { WTC_secret_department = 25 }
  add_ideas = WTC_british_dependence country_event = { id = wtc_credit.10 days = 3 }
 }
}
WTC_check_cover_effect = {
 if = { limit = { country_exists = A02 A02 = { NOT = { has_war_with = A04 } has_capitulated = no } }
  set_global_flag = WTC_british_cover remove_ideas = WTC_unprotected_routes
 }
 else = { clr_global_flag = WTC_british_cover add_ideas = WTC_unprotected_routes }
}
''')
 write('common/on_actions/WTC_credit.txt','''on_actions = {
 on_startup = { effect = {
  A04 = { WTC_board_initialize_effect = yes WTC_check_cover_effect = yes }
  every_country = { limit = { NOT = { tag = A04 } } WTC_initialize_effect = yes }
 } }
 on_daily = { effect = {
  A04 = { WTC_board_initialize_effect = yes WTC_check_cover_effect = yes }
  every_country = { limit = { NOT = { tag = A04 } } WTC_initialize_effect = yes }
 } }
 on_monthly = { effect = { every_country = { limit = { NOT = { tag = A04 } } WTC_monthly_effect = yes } } }
}
''')
 defs={
 'WTC_silver_convoy':('credit','consumer_goods_factor = 0.02 convoy_escort_efficiency = 0.05','«Серебряный Конвой»','Silver Convoy','Страхование доступно только через Палату. Подписка оплачивает аварийные службы, но подчиняет судовладельцев единому страховщику.','Insurance is available only through the Chamber. Subscription funds emergency services while binding shipowners to one insurer.'),
 'WTC_cable_contract':('credit','political_power_gain = 0.05 naval_coordination = 0.03','Кабели Мадейры','Madeira Cables','Приоритет телеграфной связи по договору ВТП. Контроль кабеля остаётся у кредитора.','Priority telegraph access under a Chamber contract. The creditor retains the cable.'),
 'WTC_port_concession':('credit','consumer_goods_factor = 0.04 production_speed_buildings_factor = -0.05','Портовая концессия ВТП','Chamber Port Concession','Палата получает сборы, а не суверенитет над портом. Долг уменьшается дополнительно на 1 каждый месяц действия концессии.','The Chamber receives fees, not sovereignty. Debt falls by an additional point each month the concession remains active.'),
 'WTC_blacklist':('credit','trade_opinion_factor = -50 production_speed_buildings_factor = -0.10','Чёрный список Палаты','The Chamber’s Blacklist','При долге выше 90 британское прикрытие позволяет ВТП отлучать должника от торговых контрактов.','Above 90 debt, British cover allows the Chamber to deny trading contracts.'),
 'WTC_cable_blackout':('north','naval_coordination = -0.05 political_power_gain = -0.10','Телеграфное отлучение','Cable Exclusion','Палата задерживает коммерческие и дипломатические сообщения должника.','The Chamber delays the debtor’s commercial and diplomatic messages.'),
 'WTC_local_receivership':('credit','consumer_goods_factor = 0.06 stability_factor = -0.05','Местная долговая администрация','Local Receivership','При долге 100 кредиторы сменили кабинет. Территория остаётся под местным управлением; Палата собирает платежи через него.','At 100 debt, creditors replaced the cabinet. Local administrators retain territorial government and collect payments for the Chamber.'),
 'WTC_british_dependence':('fleet','political_power_gain = -0.05','Британский щит Мадейры','Madeira’s British Shield','У Палаты нет регулярной армии. Стражи Проливов — наёмники, британские флот и разведка обеспечивают дальнее принуждение.','The Chamber has no regular army. The Straits Guards are mercenaries; Britain supplies naval reach and intelligence.'),
 'WTC_unprotected_routes':('fleet','trade_opinion_factor = -25 political_power_gain = -0.15','Страховщик без эскорта','An Insurer Without Escorts','Британское прикрытие потеряно. Чёрный список не действует, долговой переворот срывается; кабельное давление остаётся.','British cover is lost. Blacklists and debt coups fail, while cable pressure remains.'),
 'WTC_technocratic_credit':('credit','research_speed_factor = 0.03','Лабораторные контракты Палаты','Chamber Laboratory Contracts','Молодые технократы оплачивают приборы и связь в обмен на доступ к разработкам.','Young technocrats fund instruments and communications in exchange for access to research.'),
 'WTC_pirate_channels':('luzon','convoy_escort_efficiency = 0.03 stability_factor = -0.02','Тайные лоцманские договоры','Secret Pilotage Treaties','Пиратам платят за безопасные коридоры. Покровительство тайного департамента дорого обходится репутации.','Pirates are paid for safe corridors. Secret Department patronage carries a reputational cost.'),
 'A01_european_overture':('credit','democratic_drift = 0.02','Европейская демократическая идея','European Democratic Idea','Первая программа сближения с Британией; переговоры об объединении ещё впереди.','An opening programme for union with Britain; negotiations still lie ahead.'),
 'A01_chamber_democrats':('credit','democratic_drift = 0.03 consumer_goods_factor = 0.01','Демократия торговых советов','Democracy of Trading Councils','Демократизация при опоре на Палату усиливает влияние кредиторов.','Democratisation through the Chamber strengthens creditors’ influence.')}
 write('common/ideas/WTC_credit.txt','ideas = { country = {\n'+'\n'.join(f'{k} = {{ picture = jpc_{v[0]} removal_cost = -1 modifier = {{ {v[1]} }} }}' for k,v in defs.items())+'\n} }\n')
 for k,v in defs.items():named(k,*v[2:])
 write('common/decisions/categories/WTC_credit.txt','''WTC_debt_ledger = { icon = generic_political_discourse allowed = { NOT = { original_tag = A04 } } visible = { has_country_flag = WTC_ledger_open country_exists = A04 NOT = { has_war_with = A04 } } }
WTC_board = { icon = generic_political_discourse allowed = { original_tag = A04 } visible = { has_country_flag = WTC_board_initialized } }
''')
 named('WTC_debt_ledger','Долговая книга ВТП','Chamber Debt Ledger','Долг: §Y[?WTC_debt|0]/100§!\\nОбслуживание ненулевого долга: 2 политической власти в месяц. Война при долге от 30 и действующий кредит добавляют по 1 ежемесячно.\\n§YВыше 70§! — требования концессий; §Rвыше 90§! — кабельные санкции и чёрный список; §R100§! — долговой переворот через местный кабинет. Чёрный список и переворот требуют британского прикрытия. Палата не присоединяет территории.','Debt: §Y[?WTC_debt|0]/100§!\\nNonzero debt costs 2 political power monthly. War with debt at 30 and active loans each add one monthly.\\n§YAbove 70§!: concession demands; §Rabove 90§!: cable sanctions and blacklisting; §R100§!: a financial coup through a local cabinet. Blacklisting and coups require British cover. The Chamber cannot annex territory.')
 named('WTC_board','Закрытый директорат Мадейры','Madeira’s Closed Directorate','«Ламберт» — подпись директората, личность за ней неизвестна.\\nСтарая гвардия: §Y[?WTC_old_guard|0]§!\\nМолодые технократы: §Y[?WTC_technocrats|0]§!\\nТайный департамент: §Y[?WTC_secret_department|0]§!\\nСтарая гвардия сохраняет страховую монополию; технократы ищут союз с Теслой; департамент ведёт разведку, операции ликвидации и переговоры с пиратами. Возвращение на континент вне системы кредитов разрушит их власть.','Lambert is the directorate’s signature; the person behind it is unknown.\\nOld Guard: §Y[?WTC_old_guard|0]§!\\nYoung Technocrats: §Y[?WTC_technocrats|0]§!\\nSecret Department: §Y[?WTC_secret_department|0]§!\\nBankers defend insurance monopolies; technocrats seek Tesla; the department handles intelligence, eliminations and pirate treaties. An independent return to the continent threatens them all.')
 dec=[]
 def decision(k,cost,avail,effect,ru,en,rd,ed,cool=120):
  dec.append(f'{k} = {{ icon = generic_political_discourse cost = {cost} days_re_enable = {cool} available = {{ {avail} }} complete_effect = {{ {effect} }} ai_will_do = {{ base = 1 }} }}');named(k,ru,en,rd,ed)
 decision('WTC_borrow',35,'check_variable = { WTC_debt < 80 } NOT = { has_country_flag = WTC_active_loan } NOT = { has_country_flag = WTC_receivership }','WTC_borrow_effect = yes','Взять морской кредит','Take Maritime Credit','25 транспортов; долг +20. В течение 180 дней проценты добавляют ещё 1 долга ежемесячно.','25 transports; debt +20. Interest adds one monthly for 180 days.',180)
 decision('WTC_repay',75,'check_variable = { WTC_debt > 0 }','WTC_repay_effect = yes','Выплатить часть долга','Repay Part of the Debt','Долг −12. Не требует новых уступок.','Debt −12, with no new concessions.',90)
 decision('WTC_concede',35,'check_variable = { WTC_debt > 14 } NOT = { has_idea = WTC_port_concession }','WTC_concession_effect = yes','Уступить портовые сборы','Concede Port Fees','Долг −15 и −1 ежемесячно на 240 дней. Концессия требует гражданских ресурсов и замедляет строительство; суверенитет сохраняется.','Debt −15, then −1 monthly for 240 days. Civilian costs and slower construction; sovereignty remains.',240)
 decision('WTC_naval_service',25,'country_exists = A02 NOT = { has_war_with = A02 } A02 = { has_war = yes } has_equipment = { convoy_1 > 9 } has_equipment = { infantry_equipment > 499 } check_variable = { WTC_debt > 11 }','add_equipment_to_stockpile = { type = convoy_1 amount = -10 } add_equipment_to_stockpile = { type = infantry_equipment amount = -500 } A02 = { add_equipment_to_stockpile = { type = convoy_1 amount = 10 producer = ROOT } add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 500 producer = ROOT } } add_to_variable = { WTC_debt = -12 } WTC_refresh_effect = yes','Отслужить долг британскому флоту','Service Debt Through Britain','Передать воюющей Британии 10 транспортов и 500 винтовок. Долг −12; Палата зависит от её флота.','Send wartime Britain 10 transports and 500 rifles. Debt −12; the Chamber depends on its navy.',180)
 decision('WTC_insure',40,'NOT = { has_idea = WTC_silver_convoy } check_variable = { WTC_debt < 91 }','add_timed_idea = { idea = WTC_silver_convoy days = 180 }','Застраховать Серебряный Конвой','Insure the Silver Convoy','Страховая подписка на 180 дней: эффективнее сопровождение за счёт гражданских ресурсов.','180-day insurance improves escort efficiency at a civilian cost.',180)
 decision('WTC_cables',40,'NOT = { has_idea = WTC_cable_contract } check_variable = { WTC_debt < 71 }','add_to_variable = { WTC_debt = 3 } add_timed_idea = { idea = WTC_cable_contract days = 180 } WTC_refresh_effect = yes','Арендовать приоритет кабеля','Lease Cable Priority','Долг +3. Координация флота и политическая связь улучшатся на 180 дней.','Debt +3; better naval coordination and political communications for 180 days.',180)
 decision('WTC_end_receivership',180,'has_country_flag = WTC_receivership check_variable = { WTC_debt < 21 } has_war = no','clr_country_flag = WTC_receivership remove_ideas = WTC_local_receivership add_stability = 0.05','Выкупить долговую администрацию','Redeem the Receivership','После войны при долге не выше 20 снять внешнее управление. Политический строй требует отдельного решения страны.','After war, with debt at 20 or below, end receivership. The country must resolve its political system separately.',180)
 write('common/decisions/WTC_credit.txt','WTC_debt_ledger = {\n'+'\n'.join(dec)+'\n}\n')
 board=[]
 for k,var,other,ru,en,effect in [
 ('old_guard','WTC_old_guard',['WTC_technocrats','WTC_secret_department'],'Поддержать Старую гвардию','Support the Old Guard','set_global_flag = WTC_guard_priority clr_global_flag = WTC_tech_priority clr_global_flag = WTC_secret_priority'),
 ('technocrats','WTC_technocrats',['WTC_old_guard','WTC_secret_department'],'Дать слово технократам','Hear the Technocrats','set_global_flag = WTC_tech_priority clr_global_flag = WTC_guard_priority clr_global_flag = WTC_secret_priority country_event = { id = wtc_credit.11 days = 7 }'),
 ('secret','WTC_secret_department',['WTC_old_guard','WTC_technocrats'],'Расширить тайный департамент','Expand the Secret Department','set_global_flag = WTC_secret_priority clr_global_flag = WTC_guard_priority clr_global_flag = WTC_tech_priority country_event = { id = wtc_credit.12 days = 7 }')]:
  effects=f'add_to_variable = {{ {var} = 10 }} '+ ' '.join(f'add_to_variable = {{ {o} = -5 }}' for o in other)+' '+effect+' '+' '.join(f'clamp_variable = {{ var = {v} min = 0 max = 100 }}' for v in [var]+other)
  board.append(f'WTC_board_{k} = {{ icon = generic_political_discourse cost = 50 days_re_enable = 180 available = {{ check_variable = {{ {var} < 91 }} }} complete_effect = {{ {effects} }} ai_will_do = {{ base = 1 }} }}')
  named('WTC_board_'+k,ru,en,'Влияние выбранной группы +10, двух остальных −5. Приоритеты влияют на страховые договоры, лабораторные проекты и пиратские каналы.','Chosen influence +10, both others −5. Priorities affect insurance, laboratory contracts and pirate channels.')
 write('common/decisions/WTC_board.txt','WTC_board = {\n'+'\n'.join(board)+'\n}\n')
 # Priority is operational: tech cooperation reaches borrowers; the Guard changes insurance cost.
 p='common/decisions/WTC_credit.txt';s=read(p).replace('add_timed_idea = { idea = WTC_silver_convoy days = 180 }','add_timed_idea = { idea = WTC_silver_convoy days = 180 } if = { limit = { has_global_flag = WTC_guard_priority } add_to_variable = { WTC_debt = 3 } WTC_refresh_effect = yes } if = { limit = { has_global_flag = WTC_tech_priority } add_timed_idea = { idea = WTC_technocratic_credit days = 180 } } if = { limit = { has_global_flag = WTC_secret_priority } add_timed_idea = { idea = WTC_pirate_channels days = 180 } }');write(p,s)
 named('WTC_insure','Застраховать Серебряный Конвой','Insure the Silver Convoy','Страховая подписка на 180 дней. Приоритет банкиров добавит 3 долга; технократы дадут лабораторный контракт; тайный департамент — пиратский коридор ценой репутации.','Insurance for 180 days. Banker priority adds 3 debt; technocrats grant laboratory contracts; secret priority grants a pirate corridor at a reputational cost.')
 # Event authoring keeps a fallback option available under every resource condition.
 es=[]
 def event(num,ru,en,rd,ed,trigger,opts):
  eid=f'wtc_credit.{num}';loc(eid+'.t',ru,en);loc(eid+'.d',rd,ed)
  body=f'country_event = {{ id = {eid} title = {eid}.t desc = {eid}.d picture = GFX_1896_event_trade is_triggered_only = yes trigger = {{ {trigger} }}\n'
  for suffix,r,e,tr,ef,ai in opts:
   loc(eid+'.'+suffix,r,e);body+=f' option = {{ name = {eid}.{suffix} trigger = {{ {tr} }} ai_chance = {{ factor = {ai} }} {ef} }}\n'
  es.append(body+'}\n')
 event(1,'Мадейра требует обеспечение','Madeira Demands Collateral','Долг превысил 70. Директор Ламберт требует уступить портовые сборы. Кабинет может заплатить политическую цену сейчас, передать часть доходов или отвергнуть требование и увеличить долг.','Debt has passed 70. Director Lambert demands port fees. Pay now, concede revenue or reject the demand and add to the debt.','country_exists = A04 check_variable = { WTC_debt > 70 } check_variable = { WTC_debt < 100 }',[
 ('a','Уступить сборы на восемь месяцев.','Concede fees for eight months.','','WTC_concession_effect = yes',65),('b','Оплатить обязательства сейчас.','Pay the obligations now.','political_power > 99','add_political_power = -100 add_to_variable = { WTC_debt = -15 } WTC_refresh_effect = yes',30),('c','Отвергнуть требование.','Reject the demand.','','add_to_variable = { WTC_debt = 3 } add_stability = -0.02 WTC_refresh_effect = yes',5)])
 event(2,'Отлучение от торговой книги','Exclusion from the Trade Book','Долг выше 90. Кабельные сообщения задерживаются. Если британский флот прикрывает Палату, страховые агенты заносят страну в чёрный список. Без британского щита ВТП сохраняет связь, но теряет силу морского принуждения.','Debt exceeds 90. Cable messages are delayed. British cover enables blacklisting; without that shield the Chamber retains cable leverage but loses maritime enforcement.','check_variable = { WTC_debt > 90 } country_exists = A04',[
 ('a','Искать деньги для выплаты.','Find money for repayment.','','add_war_support = -0.02',100)])
 event(3,'Последняя расписка','The Final Promissory Note','Долг достиг 100. Тайный департамент приготовил замену кабинету — местную долговую администрацию. Палата не может управлять нашими провинциями сама. Без британского прикрытия операция сорвётся; иначе спасением станет только чрезвычайный выкуп.','Debt has reached 100. The Secret Department has prepared a local receivership cabinet. The Chamber cannot govern our provinces itself. Without British cover the operation fails; otherwise only an emergency redemption can avert it.','country_exists = A04 check_variable = { WTC_debt > 99 }',[
 ('a','Принять долговую администрацию.','Accept the receivership.','has_global_flag = WTC_british_cover','WTC_financial_coup_effect = yes',90),('b','Выкупить долг чрезвычайным сбором.','Redeem the debt with an emergency levy.','has_global_flag = WTC_british_cover political_power > 199','add_political_power = -200 add_stability = -0.08 add_to_variable = { WTC_debt = -40 } clr_country_flag = WTC_default_pending WTC_refresh_effect = yes',10),('c','Без британских кораблей приказ бессилен.','Without British ships the order fails.','NOT = { has_global_flag = WTC_british_cover }','set_variable = { WTC_debt = 90 } clr_country_flag = WTC_default_pending WTC_refresh_effect = yes',100)])
 event(10,'Кто подписывает «Ламберт»?','Who Signs Lambert?','У директората три голоса и одна подпись. Банкиры требуют сохранить Серебряный Конвой; технократы ищут договор с Теслой; тайный департамент предлагает кабели, пиратов и исчезающие имена. Никто не знает, существует ли человек по имени Ламберт. Все знают, что без британского флота их приказы не дойдут дальше причала.','The directorate has three voices and one signature. Bankers defend Silver Convoy; technocrats seek Tesla; the secret department offers cables, pirates and disappearing names. Nobody knows whether Lambert is a person. Everybody knows their orders need British ships.','tag = A04',[
 ('a','Сохранить общую подпись.','Preserve the common signature.','','add_political_power = 25 set_global_flag = WTC_guard_priority',100)])
 event(11,'Тесла не просит разрешения','Tesla Does Not Ask Permission','Технократы предлагают оплачивать приборы и телеграфные лаборатории. Старая гвардия боится, что независимая энергия сделает страховщика ненужным. Новый приоритет откроет лабораторные контракты подписчикам Палаты.','Technocrats propose instruments and telegraph laboratories. The Old Guard fears independent power will bypass the insurer. Their priority opens laboratory contracts to subscribers.','tag = A04',[
 ('a','Дать лабораториям контракт.','Contract the laboratories.','','add_timed_idea = { idea = WTC_technocratic_credit days = 180 }',100)])
 event(12,'Пираты с правильными накладными','Pirates with the Right Waybills','Тайный департамент предлагает оплачивать безопасные коридоры тем, кто вчера нападал на них. Стражи Проливов обеспечат встречу, британская разведка — имена. Канал доступен страхователям, но слухи о договоре испортят репутацию.','The Secret Department offers to pay yesterday’s raiders for safe corridors. Straits Guards arrange meetings; British intelligence supplies names. Insured clients gain the channel at a reputational cost.','tag = A04',[
 ('a','Подписать договор без печати.','Sign without a seal.','','add_timed_idea = { idea = WTC_pirate_channels days = 180 }',100)])
 # Dutch starters are genuine exclusive openings; no unfinished downstream tree is advertised.
 event(20,'Письмо о европейской демократии','A Letter on European Democracy','Батавия предлагает Британии начать сближение европейских островных обществ. Это первый шаг к возможному объединению, но Лондон должен согласиться сам. Японский ультиматум остаётся в общем календаре.','Batavia proposes rapprochement between European island societies as a first step towards possible union. London must consent. The Japanese deadline remains unchanged.','tag = A01',[
 ('a','Отправить проект британскому кабинету.','Send the draft to the British cabinet.','','if = { limit = { country_exists = A02 NOT = { has_war_with = A02 } } A02 = { country_event = { id = wtc_credit.21 days = 7 } } }',100)])
 event(21,'Батавский проект объединения','Batavia’s Union Proposal','Нидерланды предлагают общий демократический курс и будущие переговоры об объединении. Принять делегацию не значит заранее передать ей флот, колонии или корону.','The Netherlands proposes a common democratic course and future union talks. Receiving a delegation commits neither fleet, colonies nor crown.','tag = A02 country_exists = A01 NOT = { has_war_with = A01 }',[
 ('a','Принять делегацию.','Receive the delegation.','','A01 = { set_country_flag = A01_british_dialogue_accepted add_stability = 0.02 } add_political_power = 15',75),('b','Ограничиться дипломатической перепиской.','Keep the exchange diplomatic.','','A01 = { set_country_flag = A01_british_dialogue_reserved add_political_power = 15 }',25)])
 event(22,'Демократия под страховой печатью','Democracy Under an Insurance Seal','Расширение торговых советов даст демократическим группам голос. Палата предлагает приоритет кабеля и страховой договор; за этим стоит ещё 10 пунктов долга. Сотрудничество с ВТП и рост демократии теперь становятся отдельным политическим курсом.','Trading councils give democratic groups a voice. The Chamber offers cable priority and insurance for another ten debt points. Chamber cooperation and democratic growth become a distinct political course.','tag = A01',[
 ('a','Закрепить договор торговых советов.','Ratify the trading councils’ contract.','','WTC_initialize_effect = yes add_to_variable = { WTC_debt = 10 } add_timed_idea = { idea = WTC_cable_contract days = 180 } add_timed_idea = { idea = WTC_silver_convoy days = 180 } WTC_refresh_effect = yes',100)])
 write('events/WTC_credit.txt','add_namespace = wtc_credit\n'+'\n'.join(es))
 loc('WTC_receiver_name','Комитет долгового урегулирования','Debt Settlement Committee');loc('WTC_receiver_desc','Местный кабинет, поставленный кредиторами Мадейры. Палата контролирует платежи, но не заменяет государственные учреждения.','A local cabinet installed by Madeira’s creditors. The Chamber controls payments without replacing state institutions.')
 s=read('common/national_focus/a01_focus.txt')
 for fid,x,ru,en,rd,ed,ef in [
 ('A01_european_democratic_unity',10,'Объединение европейской демократии','Union of European Democracy','Начать путь сближения и возможного объединения с Британией. Делегация проверит готовность Лондона, демократические круги получат поддержку. Это начальный фокус пути; выбор исключает Одинокого волка и курс ВТП.','Begin rapprochement and possible union with Britain. A delegation tests London’s willingness and strengthens democratic circles. This opening excludes Lone Wolf and the Chamber course.','set_country_flag = A01_european_democratic_path add_ideas = A01_european_overture add_popularity = { ideology = democratic popularity = 0.05 } country_event = { id = wtc_credit.20 days = 1 }'),
 ('A01_wtc_strengthening_path',22,'Усиление Всемирной торговой палаты','Strengthen the World Trade Chamber','Начать демократизацию через торговые советы и соглашение с Мадейрой. Приоритет кабеля и страховка требуют нового долга. Это начальный фокус пути; выбор исключает Одинокого волка и объединение с Британией.','Begin democratisation through trading councils and Madeira. Cable priority and insurance require new debt. This opening excludes Lone Wolf and British union.','set_country_flag = A01_chamber_democratic_path add_ideas = A01_chamber_democrats add_popularity = { ideology = democratic popularity = 0.05 } country_event = { id = wtc_credit.22 days = 1 }')]:
  named(fid,ru,en,rd,ed)
  if re.search(r'\bid\s*=\s*'+fid+r'\b',s):continue
  other='A01_wtc_strengthening_path' if x==10 else 'A01_european_democratic_unity'
  icon='GFX_goal_unique_A01_constitution' if x==10 else 'GFX_goal_unique_A01_wtc_oil_and_rubber_offer'
  s=s.rstrip()[:-1]+f''' focus = {{ id = {fid} icon = {icon} x = {x} y = 2 cost = 3
 prerequisite = {{ focus = A01_constitution }} mutually_exclusive = {{ focus = A01_lone_wolf_path focus = {other} }}
 available = {{ country_exists = {'A02' if x==10 else 'A04'} }} cancel_if_invalid = yes
 ai_will_do = {{ factor = 0 }} search_filters = {{ FOCUS_FILTER_POLITICAL }}
 completion_reward = {{ {ef} }}
 }}\n}}\n'''
 a,b=span(s,'A01_lone_wolf_path');part=s[a:b]
 if 'mutually_exclusive' not in part:part=part[:-1]+' mutually_exclusive = { focus = A01_european_democratic_unity focus = A01_wtc_strengthening_path }\n }'
 s=s[:a]+part+s[b:];write('common/national_focus/a01_focus.txt',s)
 # Integrate both existing Japanese credit offers without creating two independent free loans.
 p='events/JPF_finance.txt';s=read(p)
 if 'WTC_initialize_effect' not in s:s=s.replace('add_ideas = JPC_credit','WTC_initialize_effect = yes add_to_variable = { WTC_debt = 15 } WTC_refresh_effect = yes add_ideas = JPC_credit')
 write(p,s)
 p='events/JPC_canonical.txt';s=read(p)
 if 'WTC_initialize_effect' not in s:s=s.replace('A03 = { add_ideas = JPC_credit','A03 = { WTC_initialize_effect = yes add_to_variable = { WTC_debt = 15 } WTC_refresh_effect = yes add_ideas = JPC_credit')
 write(p,s)
 p='common/decisions/JPC_canonical.txt';s=read(p)
 if 'WTC_initialize_effect' not in s:s=s.replace('remove_ideas = JPC_credit','remove_ideas = JPC_credit WTC_initialize_effect = yes add_to_variable = { WTC_debt = -15 } WTC_refresh_effect = yes')
 write(p,s)
 for lang,i in [('russian',0),('english',1)]:
  write(f'localisation/{lang}/zzzzzzz_WTC_credit_l_{lang}.yml','l_'+lang+':\n'+'\n'.join(f' {k}:0 "{v[i].replace(chr(34),chr(39))}"' for k,v in L.items())+'\n',True)
 write('tools/wtc_credit_manifest.json',json.dumps({'debt_range':[0,100],'demands':'>70','sanctions':'>90','local_coup':100,'annexation':False,'borrowers':'every existing country except A04','events':len(es),'ideas':len(defs),'Dutch_openings':2},indent=2))
 print('Built global Chamber credit mechanics and two Dutch political openings.')
if __name__=='__main__':main()
