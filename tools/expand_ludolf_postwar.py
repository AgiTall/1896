"""Expand only Ludolf's civilian postwar route; preserve Council and Crown routes."""
from pathlib import Path
import copy,re,shutil
from add_canon_countries import parse,value,dump
R=Path(__file__).resolve().parents[1]
def read(p):return (R/p).read_text(encoding='utf-8-sig')
def save(p,t,bom=False):
 path=R/p
 if path.exists():
  b=R/'tools/backups/ludolf_federation'/p;b.parent.mkdir(parents=True,exist_ok=True)
  if not b.exists():shutil.copy2(path,b)
 path.write_text(t,encoding='utf-8-sig' if bom else 'utf-8')
def setv(n,k,v):n[:]=[e for e in n if e[0]!=k]+[(k,'=',v)]
labels={}
def label(fid,ru,en,rd,ed):
 labels[fid]=(ru,en);labels[fid+'_desc']=(rd,ed)
if __name__=='__main__':
 p='common/national_focus/a01_focus.txt';t=parse(read(p));body=value(t,'focus_tree');fs={value(n,'id'):n for k,o,n in body if k=='focus'}
 root=fs['A01_ludolf_survives'];setv(root,'x','10');setv(root,'y','14');setv(root,'cost','5')
 setv(root,'completion_reward',parse('add_political_power = 35 add_ideas = A01_civilian_reform_mandate'))
 label('A01_ludolf_survives','Мандат на гражданские реформы','Mandate for Civilian Reform','Людольф сохраняет власть ради перехода от колониального режима к федерации. Гражданский мандат смягчит трудности переходного правительства.','Ludolf retains office to lead the transition from colonial rule to federation. A civilian mandate eases the transitional government’s burdens.')
 cabinet=fs['A01_pacific_settlement'];value(cabinet,'completion_reward').append(('A01_initialize_postwar_accounts_effect','=','yes'))
 def focus(fid,x,y,cost,parents,reward,ru,en,rd,ed,icon='GFX_goal_unique_A01_reconstruction_commission',extra=''):
  n=fs.get(fid)
  if n is None:n=[];body.append(('focus','=',n));fs[fid]=n
  n[:]=parse(f'''id = {fid} icon = {icon} x = {x} y = {y} cost = {cost}
   available = {{ has_country_flag = A01_ludolf_reform_path NOT = {{ has_country_flag = A01_admirals_seized_power }} }}
   cancel_if_invalid = yes continue_if_invalid = no ai_will_do = {{ factor = 1 }} search_filters = {{ FOCUS_FILTER_POLITICAL }}''')
  for group in parents:n.append(('prerequisite','=',[('focus','=',i) for i in group]))
  n.append(('completion_reward','=',parse(reward)))
  if extra:value(n,'available').extend(parse(extra))
  label(fid,ru,en,rd,ed);return n
 def f(fid,x,y,cost,parents,reward,ru,en,rd,ed,**kw):return focus(fid,x,y,cost,parents,reward,ru,en,rd,ed,**kw)
 f('A01_reconstruction_commission',6,15,5,[['A01_ludolf_survives']], 'set_country_flag = A01_postwar_accounts_audited add_political_power = 25',
 'Опись разрушений и обязательств','Audit Damage and Obligations','Комиссия сведёт расходы на восстановление, выплаты семьям и долги в единый реестр. Это откроет государственное финансирование и переговоры с ВТП.','Audit reconstruction costs, family compensation and existing loans before choosing a funding route.')
 f('A01_repair_ports',4,16,10,[['A01_reconstruction_commission']], 'remove_ideas = A01_postwar_destruction set_variable = { A01_reconstruction_costs = 0 } add_ideas = A01_restored_port_network add_political_power = -40',
 'Восстановить порты и мастерские','Restore Ports and Workshops','Ремонт снимает штраф разрушений: −10% строительства и −10% выпуска заводов. Восстановленные коммуникации дадут −5% расхода снабжения. Стоимость — 40 политической власти.','Remove the destruction penalties to construction and factory output. Restored communications reduce supply consumption by 5%. Costs 40 political power.')
 f('A01_families_compensation',8,16,5,[['A01_reconstruction_commission']], 'remove_ideas = A01_unpaid_families set_variable = { A01_family_compensation_costs = 0 } set_country_flag = A01_families_compensated add_stability = 0.03 add_political_power = -35',
 'Пенсии семьям погибших','Pensions for Bereaved Families','Установим выплаты вдовам, детям и инвалидам войны. Снимается штраф невыплаченных компенсаций; стабильность +3%. Стоимость — 35 политической власти.','Pay widows, children and disabled veterans. Remove unpaid compensation penalties and gain 3% stability. Costs 35 political power.')
 public=f('A01_public_recovery_fund',6,17,5,[['A01_repair_ports'],['A01_families_compensation']], 'remove_ideas = A01_postwar_budget_burden set_country_flag = A01_public_recovery_financed add_political_power = -50',
 'Государственный фонд восстановления','Public Recovery Fund','Завершим финансирование восстановления собственными средствами. Снимается бюджетная нагрузка, но долг ВТП сохраняется до отдельного погашения. Стоимость — 50 политической власти.','Finance reconstruction domestically and remove the postwar budget burden. WTC loans require separate repayment. Costs 50 political power.')
 wtc=f('A01_wtc_recovery_agreement',8,17,5,[['A01_reconstruction_commission']], 'set_country_flag = A01_wtc_recovery_signed add_timed_idea = { idea = A01_wtc_recovery_guarantees days = 365 }',
 'Соглашение о восстановлении с ВТП','WTC Recovery Agreement','Ранее предложенные нефть и каучук станут основой соглашения о финансировании ремонта, компенсаций и погашения займа. Взамен принимаем год коммерческих гарантий: −5% предела эффективности производства.','The earlier oil and rubber offer unlocks reconstruction financing and debt settlement. Accept one year of commercial guarantees: −5% production efficiency cap.',extra='custom_trigger_tooltip = { tooltip = A01_wtc_offer_required_tt has_completed_focus = A01_wtc_oil_and_rubber_offer country_exists = A04 }')
 f('A01_wtc_settlement',8,18,10,[['A01_wtc_recovery_agreement']], 'A01_settle_postwar_accounts_effect = yes',
 'Погасить обязательства через ВТП','Settle Obligations through the WTC','ВТП закрывает долг, финансирует ремонт и выплаты семьям. Снимаются финансовые и восстановительные штрафы, обязательства по оборонному займу; все три счётчика задолженности обнуляются.','Settle WTC debt, reconstruction costs and family compensation. Remove financial and destruction penalties, including defence loan servicing, and clear all three account balances.')
 f('A01_domestic_debt_redemption',4,18,10,[['A01_public_recovery_fund']], 'A01_clear_wtc_debt_effect = yes add_political_power = -75',
 'Выкупить долговые обязательства','Redeem the Debt Domestically','Погасим прежние займы без нового соглашения с ВТП. Снимаются штрафы оборонного займа, долг обнуляется. Стоимость — 75 политической власти.','Redeem existing loans without a new WTC agreement. Remove defence loan penalties and clear the debt balance. Costs 75 political power.')
 f('A01_recovery_investment',6,19,10,[['A01_wtc_settlement','A01_domestic_debt_redemption']], 'add_ideas = A01_recovery_investment_idea if = { limit = { owns_state = 1058 } 1058 = { add_extra_state_shared_building_slots = 1 add_building_construction = { type = industrial_complex level = 1 instant_build = yes } } }',
 'От восстановления к развитию','From Recovery to Development','После погашения обязательств начнём новые инвестиции: одна гражданская фабрика на Яве и +5% скорости строительства.','After settling obligations, invest in development: one civilian factory in Java and 5% construction speed.')
 # Military reform is placed between the economic and constitutional branches.
 f('A01_demobilise_colonial_army',10,15,5,[['A01_ludolf_survives']], 'remove_ideas = A01_coerced_service remove_ideas = A01_indonesian_refusal add_ideas = A01_army_transition add_war_support = -0.03',
 'Демобилизация и возвращение домой','Demobilisation and Homecoming','Завершим принудительный военный призыв и введём переходный порядок службы. Армии предстоит переучивание: −5% организации; поддержка войны −3%.','End coercive wartime service and begin military retraining. Transitional organisation penalty: 5%. War support falls by 3%.')
 f('A01_joint_officer_schools',10,16,10,[['A01_demobilise_colonial_army']], 'remove_ideas = A01_army_transition add_ideas = A01_joint_officer_corps army_experience = 15',
 'Совместные офицерские училища','Joint Officer Schools','Откроем офицерскую карьеру нидерландцам и индонезийцам. Переходный штраф снимается; организация +5%, время подготовки −5%, опыт армии +15.','Open officer careers to Dutch and Indonesians. Remove the transition penalty; gain 5% organisation, 5% faster training and 15 army experience.')
 f('A01_civilian_defence_ministry',12,16,5,[['A01_demobilise_colonial_army']], 'set_country_flag = A01_civilian_defence_ministry add_political_power = 25 add_to_variable = { A01_admirals_respect = -5 } clamp_variable = { var = A01_admirals_respect min = 0 max = 100 }',
 'Гражданское министерство обороны','Civilian Defence Ministry','Передадим бюджет и назначения гражданскому министру. Политическая власть +25; уважение адмиралов −5 пунктов.','Transfer budgets and appointments to a civilian minister. Gain 25 political power; admiral respect falls by 5 points.')
 f('A01_federal_defence_command',10,17,10,[['A01_joint_officer_schools'],['A01_civilian_defence_ministry']], 'add_ideas = A01_federal_defence_command_idea set_country_flag = A01_federal_army_reformed',
 'Единое федеральное командование','Unified Federal Command','Объединим штаб армии, флота и островных гарнизонов под гражданским контролем. Расход снабжения −5%, организация флота +5%.','Unify army, fleet and island garrison command under civilian control. Supply consumption falls by 5%; naval organisation rises by 5%.')
 f('A01_abolish_admirals_council',12,18,5,[['A01_federal_defence_command'],['A01_equal_citizenship']], 'remove_dynamic_modifier = A01_admirals_council set_country_flag = A01_admirals_council_abolished set_country_flag = A01_ludolf_crisis_resolved add_stability = 0.03',
 'Упразднить Совет адмиралов','Abolish the Council of Admirals','Совет лишится права ограничивать гражданское правительство. Его национальный модификатор удаляется; стабильность +3%. Морские офицеры сохраняют военную службу.','End the Council’s authority over civilian government. Remove its national modifier and gain 3% stability. Naval officers retain their military commissions.')
 # Constitutional branch.
 f('A01_autonomous_sultanates',14,15,5,[['A01_ludolf_survives']], 'A01_create_autonomous_sultanates_effect = yes add_ideas = A01_island_charter',
 'Соглашение с султанатами','Agreement with the Sultanates','Признаем местное самоуправление и договоримся об участии султанатов в будущей федерации. Действующий механизм создаёт автономные субъекты; позднее они смогут войти в общее государство.','Recognise local self-government and negotiate entry into the future federation. Autonomous subjects can later join the common state.')
 f('A01_island_representation',14,16,5,[['A01_autonomous_sultanates']], 'add_political_power = 25 add_ideas = A01_island_representation_idea',
 'Представительство островов','Representation of the Islands','Учредим представительство Явы, Суматры и автономных островов. Политическая власть +25; стабильность +3%.','Establish representation for Java, Sumatra and autonomous islands. Gain 25 political power and 3% stability.')
 f('A01_equal_citizenship',14,17,10,[['A01_island_representation']], 'remove_dynamic_modifier = A01_racial_divide set_country_flag = A01_equal_citizenship_established add_stability = 0.03',
 'Равное федеральное гражданство','Equal Federal Citizenship','Отменим правовое разделение нидерландцев и индонезийцев. Дух расового раскола удаляется, стабильность +3%.','End the legal divide between Dutch and Indonesians. Remove the racial divide modifier and gain 3% stability.')
 f('A01_federal_constitution',14,19,10,[['A01_equal_citizenship'],['A01_abolish_admirals_council']], 'set_country_flag = A01_federal_constitution_adopted add_ideas = A01_federal_constitution_idea',
 'Конституция двух народов','Constitution of Two Peoples','Закрепим равные права, полномочия островов и ответственность правительства перед парламентом. Конституция даст +5% стабильности и +0,05 политической власти в день.','Guarantee equal rights, island powers and parliamentary accountability. Gain 5% stability and 0.05 daily political power.')
 f('A01_elected_civil_service',12,20,5,[['A01_federal_constitution']], 'set_country_flag = A01_presidency_established remove_ideas = A01_civilian_reform_mandate add_ideas = A01_accountable_civil_service',
 'Ответственное гражданское правительство','Accountable Civilian Government','Заменим временный мандат постоянными правилами гражданской службы. Прирост политической власти +5%; расход политической власти на назначения −5%.','Replace the transitional mandate with accountable civil administration. Gain 5% political power generation and 5% cheaper political advisers.')
 f('A01_democratic_federation',14,21,10,[['A01_elected_civil_service']], 'A01_create_democratic_federation_effect = yes',
 'Демократическая Федерация Нидерландов и Индонезии','Democratic Federation of the Netherlands and Indonesia','Создадим общее демократическое государство. Собственные автономные султанаты войдут в федерацию; чужие и японские территории не передаются. Избирательная система потребует отдельных реформ.','Found a common democratic state. Our autonomous sultanates join the federation; foreign and Japanese territories are untouched. Elections require separate preparation.')
 f('A01_electoral_commission',12,22,5,[['A01_democratic_federation']], 'set_country_flag = A01_electoral_rolls_ready add_stability = 0.02',
 'Избирательная комиссия','Electoral Commission','Составим общие списки избирателей и гарантируем доступ островных общин к голосованию. Стабильность +2%.','Compile shared electoral rolls and guarantee island communities access to voting. Gain 2% stability.')
 f('A01_legalise_federal_parties',14,22,5,[['A01_democratic_federation']], 'set_country_flag = A01_federal_parties_legalised add_political_power = 25',
 'Легализовать федеральные партии','Legalise Federal Parties','Либералы, консерваторы и Народная партия получат равные права на участие в выборах. Политическая власть +25.','Give liberals, conservatives and the People’s Party equal electoral rights. Gain 25 political power.')
 f('A01_first_federal_election',12,23,5,[['A01_electoral_commission'],['A01_legalise_federal_parties']], 'country_event = { id = A01_postwar.3 days = 1 }',
 'Первые федеральные выборы','First Federal Election','Проведём первые выборы. Событие определит победившую партию и главу правительства; после объявления результата откроется только её ветка.','Hold the first federal election. The event selects the winning party and head of government; only that party’s branch becomes available.',extra='NOT = { has_country_flag = A01_first_election_held }')
 for fid,x,party,ru,en in [('A01_liberal_victory',8,'liberal','Победа Либералов','Liberal Victory'),('A01_conservative_victory',12,'conservative','Победа Консерваторов','Conservative Victory'),('A01_peoples_party_victory',16,'peoples','Победа Народной Партии','People’s Party Victory')]:
  n=f(fid,x,24,5,[['A01_first_federal_election']], 'add_political_power = 25',ru,en,'Победившая партия принимает мандат избирателей. Политическая власть +25. Продолжение партийной ветки пока не добавлено.','The victorious party accepts its electoral mandate. Gain 25 political power. Further party focuses will be developed later.',extra=f'has_country_flag = A01_first_election_held has_country_flag = A01_{party}_election_winner')
  n.append(('mutually_exclusive','=',[('focus','=',i) for i in ['A01_liberal_victory','A01_conservative_victory','A01_peoples_party_victory'] if i!=fid]))
 save(p,dump(t)+'\n')
 save('common/scripted_effects/A01_federal_recovery.txt','''A01_initialize_postwar_accounts_effect = {
 if = { limit = { NOT = { has_country_flag = A01_postwar_accounts_initialized } }
  set_country_flag = A01_postwar_accounts_initialized
  set_variable = { A01_reconstruction_costs = 40 } set_variable = { A01_family_compensation_costs = 20 }
  add_ideas = A01_postwar_destruction add_ideas = A01_unpaid_families add_ideas = A01_postwar_budget_burden
 }
}
A01_clear_wtc_debt_effect = {
 set_variable = { A01_wtc_debt = 0 }
 remove_ideas = A01_borneo_state_loan remove_ideas = A01_borneo_self_build remove_ideas = A01_borneo_debt_service
 clr_country_flag = A01_borneo_self_contract
 set_country_flag = A01_wtc_debt_repaid
}
A01_settle_postwar_accounts_effect = {
 A01_clear_wtc_debt_effect = yes
 set_variable = { A01_reconstruction_costs = 0 } set_variable = { A01_family_compensation_costs = 0 }
 remove_ideas = A01_postwar_destruction remove_ideas = A01_unpaid_families remove_ideas = A01_postwar_budget_burden
 add_ideas = A01_restored_port_network
 set_country_flag = A01_families_compensated set_country_flag = A01_wtc_recovery_financed
}
A01_create_democratic_federation_effect = {
 set_country_flag = A01_democratic_federation_established
 set_cosmetic_tag = A01_FEDERAL
 set_politics = { ruling_party = democratic elections_allowed = no }
 set_popularities = { democratic = 70 neutrality = 25 communism = 5 fascism = 0 }
 add_country_leader_role = { character = A01_ludolf_sloot_van_de_beele promote_leader = yes country_leader = { ideology = liberalism expire = "1965.1.1.1" traits = { } } }
 remove_ideas = A01_federal_transition remove_ideas = A01_island_charter remove_ideas = A01_island_representation_idea
 add_ideas = A01_democratic_federation_idea
 every_subject_country = { limit = { OR = { tag = A11 tag = A12 tag = A13 tag = A14 } } A01 = { annex_country = { target = PREV transfer_troops = yes } } }
}
''')
 ideas={
 'A01_postwar_destruction':'production_speed_buildings_factor = -0.10 industrial_capacity_factory = -0.10',
 'A01_unpaid_families':'stability_factor = -0.05 political_power_gain = -0.05',
 'A01_postwar_budget_burden':'consumer_goods_expected_value = 0.05 political_power_gain = -0.10',
 'A01_civilian_reform_mandate':'political_power_gain = 0.05',
 'A01_restored_port_network':'supply_consumption_factor = -0.05',
 'A01_wtc_recovery_guarantees':'production_factory_max_efficiency_factor = -0.05',
 'A01_recovery_investment_idea':'production_speed_buildings_factor = 0.05',
 'A01_army_transition':'army_org_factor = -0.05',
 'A01_joint_officer_corps':'army_org_factor = 0.05 training_time_army_factor = -0.05',
 'A01_federal_defence_command_idea':'supply_consumption_factor = -0.05 navy_org_factor = 0.05',
 'A01_island_representation_idea':'stability_factor = 0.03',
 'A01_federal_constitution_idea':'stability_factor = 0.05 political_power_gain = 0.05',
 'A01_accountable_civil_service':'political_power_factor = 0.05 political_advisor_cost_factor = -0.05',
 }
 save('common/ideas/A01_federal_recovery.txt','ideas = { country = {\n'+''.join(f'{i} = {{ picture = story_ludolf allowed = {{ original_tag = A01 }} removal_cost = -1 modifier = {{ {m} }} }}\n' for i,m in ideas.items())+'} }\n')
 # Election result is determined in the election event, never by focus selection.
 p='events/A01_postwar.txt'
 if not (R/p).exists():p=next(str(q.relative_to(R)) for q in (R/'events').glob('A01_postwar*.txt'))
 t=parse(read(p));ev=next(n for k,o,n in t if k=='country_event' and value(n,'id')=='A01_postwar.3')
 setv(ev,'trigger',parse('tag = A01 has_country_flag = A01_democratic_federation_established NOT = { has_country_flag = A01_first_election_held }'))
 setv(ev,'immediate',parse('set_country_flag = A01_first_election_held set_politics = { ruling_party = democratic elections_allowed = yes election_frequency = 48 } set_popularities = { democratic = 80 neutrality = 15 communism = 5 fascism = 0 }'))
 for suffix,party in [('a','liberal'),('b','conservative'),('c','peoples')]:
  opt=next(v for k,o,v in ev if k=='option' and value(v,'name')=='A01_postwar.3.'+suffix)
  opt[:]=[e for e in opt if e[0] not in ['add_stability','add_political_power']]
  opt.append(('set_country_flag','=',f'A01_{party}_election_winner'))
 mandate=next(n for k,o,n in t if k=='country_event' and value(n,'id')=='A01_postwar.1')
 opt=next(v for k,o,v in mandate if k=='option' and value(v,'name')=='A01_postwar.1.a')
 opt[:]=[e for e in opt if e[0]!='trigger']
 save(p,dump(t)+'\n')
 # Keep federal bonuses modest: the political and military reforms already supply benefits.
 p='common/ideas/A01_future_ideas.txt';t=parse(read(p));n=value(value(value(t,'ideas'),'country'),'A01_democratic_federation_idea')
 setv(n,'modifier',parse('stability_factor = 0.03 political_power_gain = 0.05 recruitable_population_factor = 0.05'));save(p,dump(t)+'\n')
 # Register labels in the established localisation files, updating existing overrides.
 extras={
 'A01_wtc_offer_required_tt':('Выполнено «Предложение для ВТП» и существует ВТП.','Complete An Offer for the WTC; the WTC must exist.'),
 'A01_FEDERAL_democratic':('Демократическая Федерация Нидерландов и Индонезии','Democratic Federation of the Netherlands and Indonesia'),
 'A01_FEDERAL_democratic_DEF':('Демократическая Федерация Нидерландов и Индонезии','the Democratic Federation of the Netherlands and Indonesia'),
 'A01_FEDERAL_democratic_ADJ':('Нидерландско-индонезийск.','Dutch-Indonesian'),
 'A01_indonesian_party':('Народная партия','People’s Party'),
 'A01_wtc_postwar_unlock_tt':('Открывает послевоенное соглашение с ВТП о восстановлении и погашении долгов.','Unlocks a postwar WTC agreement for reconstruction and debt settlement.'),
 }
 labels.update(extras)
 names={
 'A01_postwar_destruction':('Разрушенные порты и мастерские','Damaged Ports and Workshops'),
 'A01_unpaid_families':('Невыплаченные компенсации семьям','Unpaid Family Compensation'),
 'A01_postwar_budget_burden':('Расходы послевоенного восстановления','Postwar Recovery Costs'),
 'A01_civilian_reform_mandate':('Гражданский мандат Людольфа','Ludolf’s Civilian Mandate'),
 'A01_restored_port_network':('Восстановленная портовая сеть','Restored Port Network'),
 'A01_wtc_recovery_guarantees':('Коммерческие гарантии ВТП','WTC Commercial Guarantees'),
 'A01_recovery_investment_idea':('Инвестиции после восстановления','Post-Recovery Investment'),
 'A01_army_transition':('Армия в переходный период','Army in Transition'),
 'A01_joint_officer_corps':('Общий офицерский корпус','Joint Officer Corps'),
 'A01_federal_defence_command_idea':('Федеральное оборонное командование','Federal Defence Command'),
 'A01_island_representation_idea':('Представительство островов','Island Representation'),
 'A01_federal_constitution_idea':('Федеральная конституция','Federal Constitution'),
 'A01_accountable_civil_service':('Ответственная гражданская служба','Accountable Civil Service'),
 }
 for i,nameset in names.items():labels[i]=nameset;labels[i+'_desc']=('Последствия послевоенных обязательств и реформ. Изменяются соответствующими фокусами восстановления и федерализации.','Postwar obligations and reforms. Changed by the corresponding recovery and federalisation focuses.')
 labels['A01_postwar_destruction_desc']=('Ремонтные обязательства: [?A01_reconstruction_costs|0] пунктов. Снимается восстановлением портов или финансированием ВТП.','Reconstruction liabilities: [?A01_reconstruction_costs|0] points. Removed by port repairs or WTC financing.')
 labels['A01_unpaid_families_desc']=('Обязательства перед семьями: [?A01_family_compensation_costs|0] пунктов. Снимается выплатой пенсий или финансированием ВТП.','Family compensation liabilities: [?A01_family_compensation_costs|0] points. Removed by pensions or WTC financing.')
 for lang,index in [('russian',0),('english',1)]:
  remaining=dict(labels)
  for path in (R/'localisation'/lang).glob('*.yml'):
   s=path.read_text(encoding='utf-8-sig');changed=False
   for key,pair in labels.items():
    s,count=re.subn(r'^\s*'+re.escape(key)+r':\d* .*$',lambda m:f' {key}:0 "{pair[index]}"',s,flags=re.M)
    if count:remaining.pop(key,None);changed=True
   if changed:save(str(path.relative_to(R)),s,True)
  p=f'localisation/{lang}/pacific_content_l_{lang}.yml';save(p,read(p)+'\n'+''.join(f' {k}:0 "{v[index]}"\n' for k,v in remaining.items()),True)
