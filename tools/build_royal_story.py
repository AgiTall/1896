"""Reproducible expansion of the Dutch crown route; preserves one-time backups."""
from pathlib import Path
import json, shutil, re
from add_canon_countries import parse, value, dump
R = Path(__file__).resolve().parents[1]
L = {}
def loc(k, ru, en): L[k] = (ru, en)
def save(p, s):
    p = R/p
    if p.exists():
        b = R/'tools/backups/royal_story'/p.relative_to(R)
        b.parent.mkdir(parents=True, exist_ok=True)
        if not b.exists(): shutil.copy2(p,b)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding='utf-8-sig' if p.suffix=='.yml' else 'utf-8')
def read(p): return (R/p).read_text(encoding='utf-8-sig')
def setv(n,k,v): n[:]=[t for t in n if t[0]!=k]+[(k,'=',v)]
tree=parse(read('common/national_focus/a01_focus.txt')); body=value(tree,'focus_tree')
fs={value(n,'id'):n for k,o,n in body if k=='focus'}
if 'A01_royal_commission' in fs: raise SystemExit('Already applied; edit final scripts directly.')
royal={k:n for k,n in fs.items() if any(a=='allow_branch' for a,b,c in n) and 'A01_royal_path_revealed' in str(n)}
focus_art={}; new_ids=[]
def focus(fid,ru,en,desc,eng,x,y,parents,reward,art='parliament',available='',cost=5,exclusive=()):
    loc(fid,ru,en);loc(fid+'_desc',desc,eng)
    s=f'focus = {{ id = {fid} icon = GFX_{fid} x = {x} y = {y} cost = {cost} allow_branch = {{ has_country_flag = A01_royal_path_revealed }} '
    for parent in parents: s+=f'prerequisite = {{ focus = {parent} }} '
    if exclusive:s+='mutually_exclusive = { '+' '.join('focus = '+i for i in exclusive)+' } '
    if available:s+='available = { '+available+' } cancel_if_invalid = yes continue_if_invalid = no '
    s+='ai_will_do = { factor = 1 } search_filters = { FOCUS_FILTER_POLITICAL } completion_reward = { '+reward+' hidden_effect = { A01_update_spirit_categories = yes } } }'
    n=value(parse(s),'focus');body.append(('focus','=',n));fs[fid]=n;royal[fid]=n;new_ids.append(fid);focus_art[fid]=art
def append_reward(fid,s):value(fs[fid],'completion_reward').extend(parse(s))
positions={'A01_crown_above_factions':(34,14),'A01_royal_island_charter':(34,15),'A01_crown_island_council':(26,16),'A01_crown_legal_guarantees':(34,16),'A01_island_delegation':(26,17),'A01_emma_and_daughter':(34,17),'A01_wilhelmina_comes_of_age':(34,19),'A01_royal_guard_corps':(42,16),'A01_royal_naval_advisors':(42,18),'A01_summon_grand_council':(34,20),'A01_settle_crown_crisis':(34,24),'A01_royal_constitution':(30,25),'A01_royal_dictatorship':(38,25),'A01_crown_parliament':(30,26),'A01_crown_commonwealth':(30,31),'A01_crown_absolute_rule':(38,26),'A01_royal_secret_police':(42,26),'A01_crown_militarism':(38,31)}
for fid,(x,y) in positions.items():setv(fs[fid],'x',str(x));setv(fs[fid],'y',str(y))
for fid in royal:
    art='parliament'
    if any(s in fid for s in ('guard','militarism','dictatorship','absolute')):art='guard'
    elif 'naval' in fid:art='navy'
    elif any(s in fid for s in ('island','commonwealth')):art='sultanates'
    elif any(s in fid for s in ('crisis','secret','council')):art='tribunal'
    focus_art[fid]=art;setv(fs[fid],'icon','GFX_'+fid)

# The Guard now consists of actual units as well as the existing evolving modifier.
append_reward('A01_royal_guard_corps','A01_raise_royal_guard = yes')
append_reward('A01_summon_grand_council','set_country_flag = A01_admiralty_battle_open add_ideas = A01_admiralty_obstruction activate_mission = A01_admiralty_deadline')
setv(fs['A01_settle_crown_crisis'],'available',parse('has_country_flag = A01_wilhelmina_reigns has_country_flag = A01_admiralty_defeated has_country_flag = A01_island_settlement'))
append_reward('A01_settle_crown_crisis','remove_ideas = A01_admiralty_obstruction remove_mission = A01_admiralty_deadline set_country_flag = A01_admirals_council_abolished retire_character = A01_council_of_admirals country_event = { id = A01_royal_story.7 days = 1 }')
setv(fs['A01_settle_crown_crisis'],'prerequisite',parse('focus = A01_civilian_admiralty'))
fs['A01_settle_crown_crisis'].append(('prerequisite','=',parse('focus = A01_island_compact')))
append_reward('A01_royal_constitution','set_country_flag = A01_admirals_council_abolished')
fs['A01_crown_commonwealth'].append(('prerequisite','=',parse('focus = A01_responsible_cabinet')))
fs['A01_crown_commonwealth'].append(('prerequisite','=',parse('focus = A01_equal_subjects')))
setv(fs['A01_crown_commonwealth'],'available',parse('has_country_flag = A01_wilhelmina_reigns has_country_flag = A01_equal_citizenship_established has_country_flag = A01_prime_minister_elected'))

focus('A01_sultans_at_the_palace','Султаны у дворцового стола','The Sultans at the Palace',
'Султаны готовы признать корону, но не нового генерал-губернатора под другим именем. Их делегации требуют ответа: кто собирает налоги, назначает судей и командует гарнизонами?','The sultans will recognise a crown, not another governor with a new title. Their delegates demand answers about taxes, judges and garrisons.',26,18,['A01_island_delegation'],'country_event = { id = A01_royal_story.1 days = 1 }','sultanates')
focus('A01_indonesian_petition','Петиция индонезийцев','The Indonesian Petition',
'Учителя, портовые рабочие и ветераны требуют места рядом с князьями. Государство не удержится на договоре только с наследственными дворами.','Teachers, dockworkers and veterans demand seats alongside the princes. A settlement with hereditary courts alone cannot sustain the state.',26,19,['A01_sultans_at_the_palace'],'country_event = { id = A01_royal_story.2 days = 1 }','citizenship')
focus('A01_equal_subjects','Подданные становятся гражданами','Subjects Become Citizens',
'Отменить отдельные гражданские разряды и открыть государственную службу индонезийцам. Придётся оплатить школы переводчиков и защитить реформу от колониальных собственников.','Abolish separate civil categories and open public service to Indonesians. Interpreter schools and opposition from colonial property owners make equality costly.',24,21,['A01_indonesian_petition'],'set_country_flag = A01_equal_citizenship_established remove_dynamic_modifier = { modifier = A01_racial_divide } remove_ideas = A01_island_discontent add_ideas = A01_equal_citizenship_royal add_political_power = -75 add_stability = -0.03','citizenship')
focus('A01_princely_guarantees','Гарантии наследственных дворов','Guarantees to the Princely Courts',
'Местное право и престолонаследие остаются за султанами; общий суд защищает жителей от произвольных поборов. Султаны получат влияние, но лишатся права закрывать дорогу гражданскому представительству.','Local law and succession remain with the sultans, while a common court protects residents against arbitrary taxation. Princes gain influence without a veto over civic representation.',28,21,['A01_indonesian_petition'],'add_to_variable = { A01_sultan_confidence = 2 } add_ideas = A01_princely_compact set_country_flag = A01_princes_guaranteed add_political_power = -50','sultanates')
focus('A01_island_compact','Договор короны и архипелага','Crown and Archipelago Compact',
'Земли, остающиеся под нашим управлением, получат согласованное устройство. Можно выпустить султанаты как автономных союзников или сохранить единую администрацию с местными хартиями. Японские владения и концессии договор не отменяет.','Choose autonomous sultanates or a unified administration under local charters. The treaty covers only land we hold and does not cancel Japanese ownership or concessions.',26,23,['A01_equal_subjects','A01_princely_guarantees'],'country_event = { id = A01_royal_story.3 days = 1 }','sultanates',cost=7)
focus('A01_royal_commission','Королевская комиссия по поражению','Royal Commission on the Defeat',
'Кто приказал оставить склады без прикрытия? Почему контракты получили родственники адмиралов? Открытое следствие даст доказательства, но Совет может приказать уничтожить архивы.','Who left the depots undefended, and why did admirals’ relatives receive contracts? A public inquiry can build a case before the Council destroys its archives.',34,21,['A01_summon_grand_council'],'add_to_variable = { A01_admiralty_evidence = 1 } set_country_flag = A01_royal_inquiry_open country_event = { id = A01_royal_story.4 days = 1 }','tribunal',cost=3)
focus('A01_win_the_captains','Отделить капитанов от Совета','Win Over the Captains',
'Мы выступаем против политического диктата, а не против морской службы. Гарантируем жалованье, пенсии и продвижение офицерам, которые признают гражданский контроль.','Guarantee pay, pensions and merit promotion to officers who accept civilian control. The fleet must choose between its profession and the Council.',42,21,['A01_royal_naval_advisors','A01_summon_grand_council'],'add_to_variable = { A01_fleet_loyalty = 2 } add_political_power = -50 navy_experience = 10','navy',cost=3)
resolutions=['A01_admirals_on_trial','A01_purge_the_admiralty','A01_admirals_retirement']
focus(resolutions[0],'Адмиралы перед судом','Admirals before the Court',
'Предъявить доказательства парламентским юристам и добиться персональных приговоров. Медленное следствие сохранит флот, но потребует трёх комплектов доказательств и поддержки капитанов.','Secure individual convictions through civilian courts. Preserve the fleet, but first gather three dossiers and two points of captain loyalty through decisions.',32,22,['A01_royal_commission','A01_win_the_captains'],'A01_defeat_admiralty = yes add_ideas = A01_civilian_justice add_stability = 0.04 country_event = { id = A01_royal_story.5 days = 1 }','tribunal','check_variable = { A01_admiralty_evidence > 2 } check_variable = { A01_fleet_loyalty > 1 }',exclusive=resolutions[1:])
focus(resolutions[1],'Ночь закрытых адмиралтейств','The Night of Sealed Admiralties',
'Гвардия займёт министерство и арестует руководителей Совета. Двух лояльных групп капитанов хватит, чтобы удержать гавани; массовые отстранения временно нарушат работу флота.','The Guard will seize the ministry and arrest the Council. Two loyal captain groups can hold the harbours, but mass dismissals will disrupt the fleet for a year.',36,22,['A01_royal_commission','A01_win_the_captains'],'A01_defeat_admiralty = yes set_country_flag = A01_admiralty_purged add_timed_idea = { idea = A01_purged_fleet days = 365 } add_stability = -0.08 navy_experience = -30 add_power_balance_value = { id = A01_crown_council_balance value = 0.25 } country_event = { id = A01_royal_story.6 days = 1 }','guard','has_country_flag = A01_royal_guard_established check_variable = { A01_fleet_loyalty > 1 }',exclusive=[resolutions[0],resolutions[2]])
focus(resolutions[2],'Пенсия вместо политического вето','Pensions instead of a Political Veto',
'Купить согласие на роспуск Совета гарантиями пенсий и неприкосновенности. Уходящие адмиралы сохранят связи в закупках: договор ещё придётся пересмотреть.','Trade pensions and immunity for dissolution. Retiring admirals retain procurement connections that a later civilian government must reform.',40,22,['A01_royal_commission','A01_win_the_captains'],'A01_defeat_admiralty = yes add_political_power = -125 add_ideas = A01_admiralty_pensions set_country_flag = A01_admiralty_bargain add_stability = 0.06','navy','has_political_power > 124',exclusive=resolutions[:2])
focus('A01_civilian_admiralty','Морское министерство вместо Совета','A Navy Ministry instead of the Council',
'Министр отвечает за бюджет перед гражданской властью, штаб занимается операциями. Победить адмиралов недостаточно: нужно создать учреждение, которое не станет новым Советом.','The minister answers to civilian government for budgets; the naval staff plans operations. Replace personal authority with accountable institutions.',34,23,[], 'add_ideas = A01_civilian_navy_ministry navy_experience = 15','navy','has_country_flag = A01_admiralty_defeated')
setv(fs['A01_civilian_admiralty'],'prerequisite',parse(' '.join('focus = '+p for p in resolutions)))
focus('A01_guard_academy','Академия королевской гвардии','Royal Guard Academy',
'Совместная подготовка голландских и индонезийских офицеров превратит дворцовую охрану в профессиональный корпус. Присяга связывает его с государством и короной.','Train Dutch and Indonesian officers together and turn palace guards into a professional corps sworn to the state and Crown.',46,17,['A01_royal_guard_corps'],'army_experience = 20 add_ideas = A01_guard_academy_idea','guard')
focus('A01_royal_academies','Королевские институты архипелага','Royal Institutes of the Archipelago',
'Учредить инженерный институт, школу гражданской службы и службу переводов. Учебные места откроются жителям островов, а не только семьям администрации.','Found an engineering institute, civil service school and translation bureau with places for island residents.',46,18,['A01_guard_academy','A01_crown_legal_guarantees'],'add_ideas = A01_royal_academies_idea add_tech_bonus = { name = A01_royal_academies bonus = 0.5 uses = 2 category = industry }','academy')
focus('A01_capital_of_two_worlds','Столица двух миров','Capital of Two Worlds',
'В изгнании столица стала домом короны. Построим правительственный квартал и предложим городу имя Новый Амстердам. Городской совет вправе сохранить Батавию или выбрать двойное название.','Build a government district and propose New Amsterdam as the capital’s name. The city council may retain Batavia or choose a dual name.',46,19,['A01_royal_academies'],'country_event = { id = A01_royal_story.8 days = 1 }','capital','owns_state = 1058 controls_state = 1058')
focus('A01_electoral_act','Избирательный закон архипелага','Archipelago Electoral Act',
'Определить устройство выборов: территориальный компромисс с князьями или равное гражданское представительство. Обе системы дадут парламенту право утверждать премьер-министра.','Choose territorial compromise with the princes or equal civic representation. Under either system parliament will approve the prime minister.',30,27,['A01_crown_parliament'],'country_event = { id = A01_royal_story.9 days = 1 }','parliament')
focus('A01_first_royal_election','Первые выборы при короне','The First Election under the Crown',
'Начинается 90-дневная кампания. Конституционный союз, партия порядка и индонезийская коалиция борются за большинство. Поддержка дворов и гражданские права повлияют на исход; агитация доступна в решениях.','A 90-day campaign pits the Constitutional Union, Order Party and Indonesian Coalition against one another. Court guarantees and civic rights affect the vote; campaign through decisions.',30,28,['A01_electoral_act'],'A01_start_royal_election = yes','parliament',cost=3)
focus('A01_responsible_cabinet','Премьер-министр отвечает парламенту','A Prime Minister Answerable to Parliament',
'Королева утверждает выбранного парламентом главу кабинета. Министры получают бюджетную ответственность, оппозиция — право запросов. Программа правительства зависит от победителя выборов.','The Queen appoints parliament’s chosen premier. Ministers become accountable for budgets and the opposition gains questioning rights. The winning party determines the cabinet programme.',30,29,['A01_first_royal_election'],'add_ideas = A01_responsible_cabinet_idea add_political_power = 75 set_country_flag = A01_responsible_royal_cabinet','parliament','has_country_flag = A01_prime_minister_elected')
focus('A01_reform_procurement','Разорвать адмиральские контракты','Break the Admirals’ Contracts',
'Открытые тендеры заменят семейные соглашения. Пенсионный договор будет исполнен, но бывший Совет утратит контроль над закупками.','Open tenders replace family contracts. Pensions will be honoured, but the former Council loses its hold over procurement.',34,29,['A01_responsible_cabinet'],'remove_ideas = A01_admiralty_pensions add_ideas = A01_open_procurement add_political_power = -75','tribunal')
focus('A01_island_officer_commissions','Офицерские патенты для островитян','Officer Commissions for Islanders',
'Откроем высшие командные должности индонезийцам. Султанские отряды и КНИЛ получат общую программу подготовки без ликвидации местных армий.','Open senior commissions to Indonesians and coordinate KNIL training with the sultanates without dissolving their armies.',22,25,['A01_island_compact','A01_guard_academy'],'add_ideas = A01_island_commissions army_experience = 25 every_subject_country = { limit = { OR = { tag = A11 tag = A12 tag = A13 tag = A14 } } add_ideas = A01_island_commissions army_experience = 10 }','guard')
focus('A01_royal_development_bank','Королевский банк развития','Royal Development Bank',
'Совместные займы оплатят дороги и училища. Инвестиции поступят в земли короны и автономные султанаты; японские владения останутся за пределами программы.','Joint loans fund roads and schools in Crown lands and autonomous sultanates, excluding Japanese possessions.',22,27,['A01_island_officer_commissions'],'add_ideas = A01_development_bank add_political_power = -75 every_subject_country = { limit = { OR = { tag = A11 tag = A12 tag = A13 tag = A14 } } add_ideas = A01_development_bank capital_scope = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } } } capital_scope = { add_extra_state_shared_building_slots = 1 add_building_construction = { type = industrial_complex level = 1 instant_build = yes } }','academy')
focus('A01_crown_provincial_diets','Провинциальные собрания при короне','Provincial Diets under the Crown',
'Даже указу нужна обратная связь. Создадим совещательные собрания островов с выборными гражданскими делегатами. Они не назначают кабинет, но могут оспаривать действия чиновников.','Even decrees require feedback. Establish island assemblies with elected civic delegates who can challenge officials, although they cannot appoint the cabinet.',36,27,['A01_crown_absolute_rule','A01_island_compact'],'add_ideas = A01_provincial_diets remove_ideas = A01_island_discontent add_political_power = -50','citizenship')
focus('A01_renew_the_fleet','Флот после политической бури','The Fleet after the Political Storm',
'Вернуть профессиональные экзамены, подготовить новых штабистов и закрыть вакансии. Реабилитация невиновных восстановит доверие; политические полномочия Совета не вернутся.','Restore professional examinations, train staff officers and fill vacancies. Rehabilitate innocent officers without restoring the Council’s political privileges.',42,28,['A01_civilian_admiralty'],'remove_ideas = A01_purged_fleet navy_experience = 30 add_tech_bonus = { name = A01_renew_the_fleet bonus = 0.5 uses = 1 category = naval_equipment }','navy')
courses=['A01_open_seas_kingdom','A01_homeland_in_exile','A01_archipelago_great_power']
ending_gate='has_country_flag = A01_crown_crisis_settled OR = { has_country_flag = A01_responsible_royal_cabinet has_completed_focus = A01_crown_provincial_diets }'
course_parent='A01_royal_development_bank'
focus(courses[0],'Королевство открытых морей','Kingdom of Open Seas',
'Будущее Нидерландов — торговое содружество, а не вечный реванш. Гарантируем автономным дворам рынки и морскую защиту, направив средства на мирное развитие.','Choose a trading commonwealth rather than permanent revanche. Guarantee markets and naval protection to autonomous partners and invest in civilian growth.',24,33,[course_parent],'add_ideas = A01_open_seas_idea add_stability = 0.05 country_event = { id = A01_royal_story.12 days = 1 }','capital',ending_gate,7,courses[1:])
focus(courses[1],'Нидерланды живут в изгнании','The Netherlands Endure in Exile',
'Сохранить память о потерянной метрополии, поддержать беженцев и готовить флот возвращения. Освобождение потребует сил и подходящего момента: один указ не вернёт родину.','Support refugees, preserve the lost homeland’s institutions and prepare a fleet for return. Liberation will require strength and opportunity.',30,33,[course_parent],'add_ideas = A01_exile_mission add_manpower = 12000 add_war_support = 0.05 country_event = { id = A01_royal_story.13 days = 1 }','navy',ending_gate,7,[courses[0],courses[2]])
focus(courses[2],'Держава архипелага','A Great Power of the Archipelago',
'Признать, что будущее страны находится на островах. Общая оборона и равный доступ к командованию дадут опору новой тихоокеанской державе, но военный бюджет потребует жертв.','Recognise that the nation’s future lies in the islands. Shared defence and equal access to command support a Pacific power at the cost of a heavier military budget.',36,33,[course_parent],'add_ideas = A01_archipelago_power add_war_support = 0.05 country_event = { id = A01_royal_story.14 days = 1 }','guard',ending_gate,7,courses[:2])
save('common/national_focus/a01_focus.txt',dump(tree)+'\n')

ideas={
'A01_admiralty_obstruction':('Обструкция адмиралов','Admiralty Obstruction','Закупки задерживаются, капитаны получают противоречивые приказы. Завершите борьбу через суд, чистку или соглашение.','Procurement stalls and captains receive conflicting orders. Resolve the struggle through trial, purge or agreement.','tribunal','political_power_gain = -0.15 navy_org_factor = -0.05'),
'A01_purged_fleet':('Флот после чистки','The Purged Fleet','Отстранения оставили штабные вакансии. Через год флот восстановится; специальный фокус может ускорить восстановление.','Dismissals leave staff vacancies. Recovery takes a year or the fleet renewal focus.','navy','navy_org_factor = -0.12 naval_coordination = -0.10'),
'A01_admiralty_pensions':('Цена адмиральской отставки','The Price of Admiralty Retirement','Бывшие адмиралы получают пенсии и сохраняют закупочные связи. Парламент может пересмотреть контракты.','Retired admirals receive pensions and retain procurement connections until parliamentary reform.','tribunal','consumer_goods_expected_value = 0.03 political_power_gain = -0.05'),
'A01_civilian_justice':('Гражданский суд над властью','Civilian Justice','Личная ответственность офицеров установлена судом, а не массовыми отстранениями.','Courts established individual responsibility without mass dismissals.','tribunal','stability_factor = 0.04 political_power_gain = 0.05'),
'A01_civilian_navy_ministry':('Королевское морское министерство','Royal Navy Ministry','Военный штаб отделён от гражданского бюджета. Адмиральского политического вето больше нет.','Operational command is separated from civilian budgeting. The admirals no longer hold a political veto.','navy','navy_org_factor = 0.04 production_speed_dockyard_factor = 0.05'),
'A01_equal_citizenship_royal':('Общее гражданство','Common Citizenship','Голландцы и индонезийцы получают равный доступ к гражданской службе и командованию.','Dutch and Indonesian citizens share access to public service and military commissions.','citizenship','recruitable_population_factor = 0.05 stability_factor = 0.03'),
'A01_princely_compact':('Договор с княжескими дворами','Compact with the Princely Courts','Корона гарантирует местное право и престолонаследие, а дворы признают общий суд.','The Crown guarantees local law and succession; the courts recognise common justice.','sultanates','stability_factor = 0.04 political_power_gain = -0.05'),
'A01_island_discontent':('Острова ждут ответа','The Islands Await an Answer','Петиция отложена. Снять недовольство можно общим гражданством или представительством.','The petition was postponed. Common citizenship or representation can settle the grievance.','citizenship','stability_factor = -0.05 political_power_gain = -0.05'),
'A01_guard_academy_idea':('Школа королевской гвардии','Royal Guard School','Общий офицерский корпус готовит голландских и индонезийских кадетов.','A joint officer school trains Dutch and Indonesian cadets.','guard','army_org_factor = 0.03 training_time_army_factor = -0.05'),
'A01_royal_academies_idea':('Королевские институты','Royal Institutes','Инженеры, переводчики и гражданские служащие получают образование в самом архипелаге.','Engineers, translators and civil servants train in the archipelago.','academy','research_speed_factor = 0.03'),
'A01_island_commissions':('Общий офицерский корпус','Joint Officer Corps','Доступ к командованию определяется подготовкой, а не происхождением.','Training, rather than ancestry, determines access to command.','guard','army_org_factor = 0.03 army_defence_factor = 0.03'),
'A01_development_bank':('Банк развития архипелага','Archipelago Development Bank','Общие кредиты финансируют дороги, школы и местные предприятия.','Shared credit funds roads, schools and local enterprises.','academy','production_speed_buildings_factor = 0.06 consumer_goods_expected_value = 0.02'),
'A01_responsible_cabinet_idea':('Ответственный кабинет','Responsible Cabinet','Королева назначает премьер-министра по парламентскому большинству. Бюджет требует одобрения депутатов.','The Queen appoints the parliamentary majority’s premier. Deputies approve the budget.','parliament','political_power_gain = 0.08 stability_factor = 0.03'),
'A01_open_procurement':('Открытые государственные заказы','Open Public Procurement','Общественный контроль ограничивает семейные флотские контракты.','Public oversight curbs family procurement contracts.','tribunal','production_speed_dockyard_factor = 0.05 consumer_goods_expected_value = -0.02'),
'A01_provincial_diets':('Провинциальные собрания','Provincial Diets','Гражданские делегаты контролируют чиновников при сохранении королевского кабинета.','Civic delegates scrutinise officials while the Crown retains its cabinet.','citizenship','stability_factor = 0.04 political_power_gain = 0.03'),
'A01_open_seas_idea':('Корона торговых морей','Crown of the Trading Seas','Торговля, гражданское строительство и договорные отношения определяют курс королевства.','Trade, civilian construction and negotiated partnership define the kingdom.','capital','production_speed_industrial_complex_factor = 0.10 consumer_goods_expected_value = -0.03 war_support_factor = -0.05'),
'A01_exile_mission':('Миссия королевства в изгнании','Mission of the Exiled Kingdom','Беженцы сохраняют институты потерянной родины; верфи готовят флот возвращения.','Refugees preserve the lost homeland’s institutions while shipyards prepare the fleet of return.','navy','production_speed_dockyard_factor = 0.10 war_support_factor = 0.08 consumer_goods_expected_value = 0.03'),
'A01_archipelago_power':('Тихоокеанская корона','Pacific Crown','Общая оборона островов стала главным делом государства.','Shared island defence is the state’s principal mission.','guard','army_defence_factor = 0.05 navy_org_factor = 0.05 consumer_goods_expected_value = 0.04'),
'A01_pm_constitutional':('Премьер-министр: Конституционный союз','Prime Minister: Constitutional Union','Кабинет торговых городов и юристов: открытый бюджет, инженерные школы и гражданская служба.','A cabinet of trading cities and lawyers: transparent budgets, engineering schools and public service.','parliament','political_power_gain = 0.08 research_speed_factor = 0.02'),
'A01_pm_order':('Премьер-министр: Партия порядка','Prime Minister: Order Party','Кабинет умеренных монархистов и княжеских делегатов: местные гарантии и морская безопасность.','Moderate monarchists and princely delegates favour local guarantees and maritime security.','sultanates','stability_factor = 0.04 production_speed_dockyard_factor = 0.05'),
'A01_pm_indonesian':('Премьер-министр: Индонезийская коалиция','Prime Minister: Indonesian Coalition','Кабинет гражданских делегатов островов: училища, равные назначения и развитие внутренних округов.','Island civic delegates prioritise schools, equal appointments and inland development.','citizenship','recruitable_population_factor = 0.03 production_speed_buildings_factor = 0.05'),
}
s='ideas = { country = {\n'
for key,(ru,en,desc,eng,art,mods) in ideas.items():
    loc(key,ru,en);loc(key+'_desc',desc,eng)
    s+=f'{key} = {{ picture = royal_{art} allowed = {{ always = yes }} removal_cost = -1 modifier = {{ {mods} }} }}\n'
save('common/ideas/A01_royal_story.txt',s+'} }\n')

effects='''A01_raise_royal_guard = {
 if = { limit = { NOT = { has_country_flag = A01_guard_units_raised } }
  set_country_flag = A01_guard_units_raised
  load_oob = A01_royal_guard
 }
}
A01_defeat_admiralty = {
 set_country_flag = A01_admiralty_defeated
 remove_mission = A01_admiralty_deadline
 remove_ideas = A01_admiralty_obstruction
 retire_character = A01_council_of_admirals
 set_country_flag = A01_admirals_council_abolished
 remove_dynamic_modifier = { modifier = A01_admirals_council }
}
A01_start_royal_election = {
 if = { limit = { NOT = { has_country_flag = A01_royal_campaign_active } }
  remove_mission = A01_royal_election_term
  set_country_flag = A01_royal_campaign_active
  set_variable = { A01_vote_constitutional = 3 }
  set_variable = { A01_vote_order = 3 }
  set_variable = { A01_vote_indonesian = 3 }
  if = { limit = { has_country_flag = A01_princes_guaranteed } add_to_variable = { A01_vote_order = 2 } }
  if = { limit = { has_country_flag = A01_equal_citizenship_established } add_to_variable = { A01_vote_indonesian = 2 } }
  if = { limit = { has_country_flag = A01_civic_electoral_law } add_to_variable = { A01_vote_constitutional = 1 } add_to_variable = { A01_vote_indonesian = 1 } }
  if = { limit = { has_country_flag = A01_territorial_electoral_law } add_to_variable = { A01_vote_order = 2 } }
  activate_mission = A01_royal_election_campaign
  country_event = { id = A01_royal_story.10 days = 1 }
 }
}
A01_finish_royal_election = {
 clr_country_flag = A01_royal_campaign_active
 remove_mission = A01_royal_election_campaign
 remove_ideas = A01_pm_constitutional
 remove_ideas = A01_pm_order
 remove_ideas = A01_pm_indonesian
 clr_country_flag = A01_pm_constitutional_winner
 clr_country_flag = A01_pm_order_winner
 clr_country_flag = A01_pm_indonesian_winner
 if = { limit = {
   check_variable = { var = A01_vote_indonesian value = A01_vote_order compare = greater_than_or_equals }
   check_variable = { var = A01_vote_indonesian value = A01_vote_constitutional compare = greater_than_or_equals }
  } add_ideas = A01_pm_indonesian set_country_flag = A01_pm_indonesian_winner
 }
 else_if = { limit = { check_variable = { var = A01_vote_order value = A01_vote_constitutional compare = greater_than_or_equals } }
  add_ideas = A01_pm_order set_country_flag = A01_pm_order_winner
 }
 else = { add_ideas = A01_pm_constitutional set_country_flag = A01_pm_constitutional_winner }
 set_country_flag = A01_prime_minister_elected
 add_stability = 0.03
 activate_mission = A01_royal_election_term
 country_event = { id = A01_royal_story.11 days = 1 }
}
'''
# Explicit creation avoids the federal route's flags and obsolete balance of power.
effects+='A01_charter_crown_sultanates = {\n'
for tag,state in [('A11',1055),('A12',334),('A13',1022),('A14',1050)]:
    effects+=f'''if = {{ limit = {{ owns_state = {state} NOT = {{ country_exists = {tag} }} }}
 {state} = {{ add_core_of = {tag} }}
 {tag} = {{ transfer_state = {state} set_politics = {{ ruling_party = neutrality elections_allowed = no }} }}
 set_autonomy = {{ target = {tag} autonomy_state = autonomy_puppet freedom_level = 0.35 }}
}}
if = {{ limit = {{ {tag} = {{ is_subject_of = A01 }} }} {tag} = {{ add_ideas = A01_princely_compact }} }}
'''
effects+='if = { limit = { has_country_flag = A01_borneo_treaty } A01_borneo_resource_rights_effect = yes }\nset_country_flag = A01_sultanates_chartered\n}\n'
save('common/scripted_effects/A01_royal_story.txt',effects)
regiments=' '.join(f'infantry = {{ x = {i//3} y = {i%3} }}' for i in range(6))
save('history/units/A01_royal_guard.txt',f'''division_template = {{ name = "Koninklijke Garde" regiments = {{ {regiments} }} priority = 2 }}
units = {{ division = {{ name = "1. Koninklijke Garde" location = 7381 division_template = "Koninklijke Garde" start_experience_factor = 0.3 start_equipment_factor = 0.8 }} }}
''')

events='add_namespace = A01_royal_story\n'
def event(num,ru,en,desc,eng,options,immediate=''):
    global events
    eid=f'A01_royal_story.{num}';loc(eid+'.t',ru,en);loc(eid+'.d',desc,eng)
    events+=f'country_event = {{ id = {eid} title = {eid}.t desc = {eid}.d picture = GFX_1896_event_council is_triggered_only = yes trigger = {{ original_tag = A01 has_country_flag = A01_royal_path_revealed }} '
    if immediate:events+='immediate = { '+immediate+' } '
    for i,(r,e,eff) in enumerate(options):
        key=eid+'.'+chr(97+i);loc(key,r,e);events+=f'option = {{ name = {key} {eff} }} '
    events+='}\n'
event(1,'Четыре двора и одна корона','Four Courts and One Crown',
'За столом лежат разные проекты хартий. Султанские послы требуют местных налогов и неприкосновенности престолов. Министры предлагают общий бюджет обороны. Эмма замечает, что договор должен защищать не только дворцы, но и тех, кто платит налоги. Можно обещать широкое самоуправление или начать с общей таможни.','The envoys demand local taxation and secure succession. Ministers propose a shared defence budget. Emma insists that the compact protect taxpayers as well as palaces. Broad self-government and a customs-first agreement offer different starting points.',[
('Гарантировать местное самоуправление.','Guarantee local self-government.','add_to_variable = { A01_sultan_confidence = 3 } add_political_power = -50 add_stability = 0.03'),
('Сначала общий бюджет и таможня.','Start with a common budget and customs.','add_to_variable = { A01_sultan_confidence = 1 } add_political_power = 25 add_stability = -0.02')])
event(2,'Кто представляет Индонезию?','Who Represents Indonesia?',
'На ступенях дворца учитель читает петицию на малайском, затем переводит её на голландский. Подписанты не просят новых князей: они хотят суд, школу и право стать офицером. Султанские делегаты опасаются, что гражданская палата вытеснит их дворы. Короне предстоит признать обе стороны или отложить решение.','A teacher reads the petition in Malay, then Dutch. Its signatories ask for courts, schools and officer commissions. Princely envoys fear a civic chamber will displace them. The Crown must recognise both claims or postpone an answer.',[
('Гражданские делегаты получат места.','Give civic delegates seats.','set_country_flag = A01_civic_delegates_recognised add_to_variable = { A01_civic_support = 2 } add_stability = 0.02 add_political_power = -35'),
('Сначала договоримся с дворами.','Reach an agreement with the courts first.','add_to_variable = { A01_sultan_confidence = 1 } add_ideas = A01_island_discontent add_political_power = 20')])
event(3,'Подписи под островным договором','Signatures on the Island Compact',
'На столе два приложения. Первое учреждает автономные султанаты с собственной администрацией и общей обороной под короной. Второе сохраняет единую страну, но закрепляет местное право, гражданское представительство и налоговые гарантии. Передавать можно только земли, которыми мы владеем. Японские права на Борнео сохраняются.','One annex establishes autonomous sultanates with local administrations and common defence. The other preserves a unified state with local law, civic representation and tax guarantees. Only Crown-owned land can be transferred; Japanese rights on Borneo remain.',[
('Автономные султанаты под общей короной.','Autonomous sultanates under one Crown.','A01_charter_crown_sultanates = yes set_country_flag = A01_island_settlement set_country_flag = A01_crown_autonomous_compact add_stability = 0.04'),
('Единая страна, гарантированные хартии.','One state with guaranteed charters.','set_country_flag = A01_island_settlement set_country_flag = A01_crown_unified_compact add_political_power = 50 add_stability = -0.03')])
event(4,'Архив, который приказали сжечь','The Archive Ordered Burned',
'Секретарь морского ведомства приносит копии контрактов и приказ о сожжении оригиналов. Адмиралы называют документы подделкой. Публичное слушание убедит гражданских делегатов; тайная проверка поможет защитить свидетелей. Обоим путям нужны дополнительные доказательства.','A clerk brings contract copies and an order to burn the originals. The admirals call them forgeries. Public hearings convince civic delegates; a confidential inquiry protects witnesses. Further evidence is needed either way.',[
('Открыть слушания.','Open the hearings.','add_to_variable = { A01_admiralty_evidence = 1 } add_stability = -0.02 add_political_power = 25'),
('Сначала защитить свидетелей.','Protect the witnesses first.','add_to_variable = { A01_admiralty_evidence = 1 } add_political_power = -25 add_to_variable = { A01_fleet_loyalty = 1 }')])
event(5,'Приговор не должен стать местью','A Verdict Must Not Become Revenge',
'Суд установил ответственность руководителей Совета за сокрытие контрактов и вмешательство в гражданское управление. Капитаны ждут решения о рядовых офицерах. Ограниченные приговоры сохранят опыт; расширенное следствие усилит корону, но потребует ещё одной перестройки штаба.','The court finds Council leaders responsible for concealing contracts and interfering in civilian government. Captains await the fate of junior officers. Limited sentences preserve experience; wider investigations strengthen the Crown but disrupt the staff.',[
('Наказывать только доказанные преступления.','Punish proven offences only.','navy_experience = 15 add_stability = 0.03'),
('Проверить весь высший штаб.','Investigate the entire senior staff.','add_timed_idea = { idea = A01_purged_fleet days = 180 } add_power_balance_value = { id = A01_crown_council_balance value = 0.15 }')])
event(6,'Утро без Совета','The Morning without the Council',
'Гвардия опечатала адмиралтейства. Арестованные руководители лишены политических должностей, но под подозрение попали десятки капитанов. Одни требуют немедленного суда, другие — бесконечной проверки лояльности. Флоту уже не хватает штабистов.','The Guard seals the admiralty offices. Council leaders lose their political offices, but dozens of captains also face suspicion. Some demand trials, others endless loyalty checks. The fleet already lacks staff officers.',[
('Ограничить чистку руководителями заговора.','Confine the purge to conspiracy leaders.','add_stability = 0.03 add_power_balance_value = { id = A01_crown_council_balance value = -0.10 }'),
('Продолжить проверку лояльности.','Continue the loyalty investigation.','add_stability = -0.03 add_power_balance_value = { id = A01_crown_council_balance value = 0.15 }')])
event(7,'Кому принадлежит победа?','Whose Victory Is This?',
'Адмиральское политическое вето отменено. Но гвардия, гражданские делегаты и султанские дворы по-разному понимают новый порядок. Королева может закрепить разграничение полномочий или опереться на личную присягу. Это решение задаст условия конституционного либо абсолютного пути.','The admirals’ political veto is gone, but guards, civic delegates and princely courts disagree about the new order. The Queen may divide powers or rely on personal allegiance. This determines access to constitutional or absolute rule.',[
('Победа закона: подготовить конституцию.','A victory for law: prepare a constitution.','set_power_balance = { id = A01_crown_council_balance set_value = 0 } add_stability = 0.03'),
('Победа короны: министры служат королеве.','A victory for the Crown: ministers serve the Queen.','set_power_balance = { id = A01_crown_council_balance set_value = 0.65 } add_war_support = 0.03')])
city='1058 = { add_extra_state_shared_building_slots = 1 add_building_construction = { type = industrial_complex level = 1 instant_build = yes } }'
event(8,'Как зовётся столица?','What Is the Capital Called?',
'Новый правительственный квартал открыт. Придворные предлагают Новый Амстердам — память о потерянной родине. Городской совет напоминает о торговцах, кварталах и языках, для которых Батавия давно стала домом. Корона может выбрать новое имя, сохранить старое или признать оба.','The government quarter opens. Courtiers propose New Amsterdam in memory of the lost homeland. City councillors speak for traders and neighbourhoods that call Batavia home. The Crown may rename the city, keep its name or recognise both.',[
('Новый Амстердам — столица короны.','New Amsterdam, capital of the Crown.','set_province_name = { id = 7381 name = A01_NEW_AMSTERDAM } 1058 = { set_state_name = A01_NEW_AMSTERDAM } set_country_flag = A01_new_amsterdam add_political_power = 25'),
('Батавия — имя нашего общего города.','Batavia, the name of our shared city.','add_stability = 0.04'),
('Новый Амстердам — Батавия.','New Amsterdam–Batavia.','set_province_name = { id = 7381 name = A01_DUAL_CAPITAL } 1058 = { set_state_name = A01_DUAL_CAPITAL } add_stability = 0.02')],city)
loc('A01_NEW_AMSTERDAM','Новый Амстердам','New Amsterdam');loc('A01_DUAL_CAPITAL','Новый Амстердам — Батавия','New Amsterdam–Batavia')
event(9,'Острова считают голоса','The Islands Count Their Votes',
'Княжеские делегаты требуют территориальных гарантий, иначе малые острова потеряются за населением Явы. Гражданская коалиция требует равного голоса. Конституционный союз предлагает компромисс. Выбранный закон изменит начальную поддержку партий; агитация сможет изменить результат.','Princely delegates demand territorial guarantees for small islands. Civic delegates demand equal votes. The Constitutional Union offers compromise. The electoral law changes initial party support; campaigning can still alter the result.',[
('Территориальные гарантии и гражданская палата.','Territorial guarantees and a civic chamber.','set_country_flag = A01_territorial_electoral_law add_stability = 0.03'),
('Равное гражданское представительство.','Equal civic representation.','set_country_flag = A01_civic_electoral_law add_political_power = -35 add_stability = 0.01')])
event(10,'Кампания без адмиральского вето','A Campaign without the Admirals’ Veto',
'Газеты печатают программы трёх блоков. Конституционный союз обещает открытый бюджет, Партия порядка — гарантии дворам и сильный флот, Индонезийская коалиция — школы и равные назначения. До голосования 90 дней. В решениях можно поддержать кампанию; каждый блок доступен для агитации раз в 30 дней.','Three blocs publish their programmes: transparent budgets, princely guarantees and naval strength, or schools and equal appointments. Voting is in 90 days. Campaign decisions support each bloc once every 30 days.',[('Пусть избиратели решат.','Let the electorate decide.','')])
event(11,'Королева принимает премьер-министра','The Queen Receives the Prime Minister',
'Председатель палаты приносит результаты выборов. Победивший блок получил право сформировать кабинет; его программа показана отдельным национальным духом. Королева утверждает назначение и требует соблюдения конституции. Следующая кампания начнётся через два года. При равной поддержке преимущество получает индонезийская коалиция, затем партия порядка — правило согласовано избирательной комиссией заранее.','The speaker delivers the results. The winning bloc forms the cabinet, whose programme appears as a separate national spirit. The Queen confirms its appointment under the constitution. The next campaign begins in two years. Pre-agreed ties favour the Indonesian Coalition, then the Order Party.',[('Назначить кабинет и открыть сессию.','Appoint the cabinet and open the session.','add_political_power = 50')])
event(12,'Корона на торговых путях','A Crown on the Trade Routes',
'Новая доктрина ставит безопасность перевозок и развитие островов выше походов за престижем. Дворы получают рынки, граждане — рабочие места. Военные предупреждают, что этот выбор уменьшит общественную готовность к войне.','Shipping security and island development take priority over prestige campaigns. Courts gain markets and citizens gain jobs, while public willingness to fight declines.',[('Море должно соединять.','The sea should connect us.','')])
event(13,'Родина на картах школьных классов','A Homeland on Classroom Maps',
'Беженцы открывают архив и училище потерянной метрополии. В правительстве подчёркивают: память не даёт права отнять будущее у индонезийцев. Флот возвращения будет строиться за счёт открытого бюджета, без обещаний лёгкой победы.','Refugees establish an archive and school for the lost homeland. Ministers insist that remembrance must not consume Indonesia’s future. A fleet of return will require an openly funded budget and offers no easy victory.',[('Сохранить родину и построить будущее.','Preserve the homeland and build a future.','')])
event(14,'Государство, обращённое к Тихому океану','A State Facing the Pacific',
'Морские карты теперь начинаются с Явы. Дворы, гражданские делегаты и военное министерство подписывают общий план обороны. Новая держава зависит от сотрудничества народов архипелага, а не только от голландского имени.','Naval maps now begin with Java. Courts, civic delegates and the military ministry sign a common defence plan. The new power rests on cooperation among the archipelago’s peoples.',[('Наше будущее здесь.','Our future is here.','')])
event(15,'Совет выигрывает время','The Council Buys Time',
'Срок следствия истёк, но Совет ещё держит ведомство. Это не конец королевского пути: парламентские юристы требуют новой сессии. Продление расследования обойдётся политическим капиталом, а капитаны станут осторожнее. Следующий срок — 180 дней.','The inquiry deadline expires while the Council still holds the ministry. The royal route remains open, but another 180-day session costs political capital and makes captains more cautious.',[
('Продлить следствие за счёт двора.','Fund another session from the court.','add_political_power = -75 add_to_variable = { A01_fleet_loyalty = -1 } activate_mission = A01_admiralty_deadline'),
('Выступить перед страной.','Appeal to the country.','add_stability = -0.05 add_to_variable = { A01_admiralty_evidence = 1 } activate_mission = A01_admiralty_deadline')])
save('events/A01_royal_story.txt',events)

cat='''A01_royal_institutions = { icon = generic_political_actions allowed = { original_tag = A01 } visible = { has_country_flag = A01_royal_path_revealed } }
A01_royal_ballot = { icon = generic_political_actions allowed = { original_tag = A01 } visible = { has_completed_focus = A01_first_royal_election } }
'''
save('common/decisions/categories/A01_royal_story.txt',cat)
loc('A01_royal_institutions','Корона, адмиралы и острова','Crown, Admirals and Islands')
loc('A01_royal_institutions_desc','Доказательства: §Y[?A01_admiralty_evidence|0]§! / 3. Лояльность капитанов: §Y[?A01_fleet_loyalty|0]§! / 2. Доверие дворов: §Y[?A01_sultan_confidence|0]§!.\nСуд требует доказательств и капитанов; чистка требует гвардии и капитанов. Доверие дворов снижает цену земельного договора.','Evidence: §Y[?A01_admiralty_evidence|0]§! / 3. Captain loyalty: §Y[?A01_fleet_loyalty|0]§! / 2. Court confidence: §Y[?A01_sultan_confidence|0]§!.\nTrial needs evidence and captains; purge needs the Guard and captains. Court confidence helps sustain the settlement.')
loc('A01_royal_ballot','Выборы премьер-министра','Election of the Prime Minister')
loc('A01_royal_ballot_desc','Поддержка блоков: Конституционный союз §Y[?A01_vote_constitutional|0]§!, Партия порядка §Y[?A01_vote_order|0]§!, Индонезийская коалиция §Y[?A01_vote_indonesian|0]§!.\nПобеждает блок с наибольшей поддержкой. При равенстве: индонезийская коалиция, затем партия порядка.','Bloc support: Constitutional Union §Y[?A01_vote_constitutional|0]§!, Order Party §Y[?A01_vote_order|0]§!, Indonesian Coalition §Y[?A01_vote_indonesian|0]§!.\nHighest support wins. Ties favour the Indonesian Coalition, then the Order Party.')
dec='A01_royal_institutions = {\n'
def decision(key,ru,en,desc,eng,cost,days,avail,effect,icon='generic_political_discourse'):
    global dec
    loc(key,ru,en);loc(key+'_desc',desc,eng)
    dec+=f'{key} = {{ icon = {icon} cost = {cost} days_re_enable = {days} visible = {{ {avail} }} available = {{ {avail} }} complete_effect = {{ {effect} }} ai_will_do = {{ factor = 2 }} }}\n'
battle='has_country_flag = A01_royal_inquiry_open NOT = { has_country_flag = A01_admiralty_defeated }'
decision('A01_audit_naval_contracts','Проверить флотские контракты','Audit Naval Contracts','Проверка счетов добавит один комплект доказательств.','Account audits add one evidence dossier.',35,30,battle,'add_to_variable = { A01_admiralty_evidence = 1 }')
decision('A01_secure_witnesses','Защитить свидетелей','Protect Witnesses','Охрана семей позволит капитанам выступить против Совета. +1 лояльности.','Family protection encourages captains to testify. +1 loyalty.',35,30,battle,'add_to_variable = { A01_fleet_loyalty = 1 }')
decision('A01_pay_the_captains','Выплатить жалованье капитанам','Pay the Captains','Гарантировать жалованье вместо раздачи политических должностей. +2 лояльности.','Guarantee pay rather than political offices. +2 loyalty.',65,60,battle,'add_to_variable = { A01_fleet_loyalty = 2 } navy_experience = 5','generic_navy')
decision('A01_meet_princely_envoys','Принять послов султанатов','Receive Princely Envoys','Обсудить сбор налогов и правосудие. +1 доверия дворов.','Discuss taxation and justice. +1 court confidence.',30,45,'has_completed_focus = A01_sultans_at_the_palace NOT = { has_country_flag = A01_island_settlement }','add_to_variable = { A01_sultan_confidence = 1 } add_stability = 0.01')
loc('A01_admiralty_deadline','Совет затягивает следствие','The Council Delays the Inquiry')
loc('A01_admiralty_deadline_desc','За 180 дней нужно завершить суд, чистку или договор об отставке. Просрочка потребует новой политической уступки, но не закроет ветку.','Resolve the trial, purge or retirement within 180 days. A missed deadline forces another concession without closing the route.')
dec+='''A01_admiralty_deadline = { icon = generic_political_discourse is_good = no days_mission_timeout = 180 activation = { has_country_flag = A01_admiralty_battle_open NOT = { has_country_flag = A01_admiralty_defeated } } visible = { has_country_flag = A01_admiralty_battle_open NOT = { has_country_flag = A01_admiralty_defeated } } cancel_trigger = { has_country_flag = A01_admiralty_defeated } timeout_effect = { country_event = { id = A01_royal_story.15 days = 1 } } }
}
A01_royal_ballot = {
'''
for suffix,ru,en in [('constitutional','Конституционный союз','Constitutional Union'),('order','Партия порядка','Order Party'),('indonesian','Индонезийская коалиция','Indonesian Coalition')]:
    decision('A01_campaign_'+suffix,'Агитация: '+ru,'Campaign: '+en,'Поддержка блока вырастет на 2. Решение доступно раз в 30 дней.','Bloc support rises by 2; available once every 30 days.',35,30,'has_country_flag = A01_royal_campaign_active',f'add_to_variable = {{ A01_vote_{suffix} = 2 }}')
loc('A01_royal_election_campaign','90 дней до голосования','90 Days until Voting')
loc('A01_royal_election_campaign_desc','После окончания кампании избирательная комиссия определит победивший блок по поддержке.','At campaign end, the electoral commission determines the winning bloc by support.')
loc('A01_royal_election_term','Срок полномочий кабинета','Cabinet Term')
loc('A01_royal_election_term_desc','Через 720 дней начнётся следующая кампания. Действующий кабинет работает до объявления нового результата.','The next campaign starts after 720 days. The incumbent serves until the next result.')
dec+='''A01_royal_election_campaign = { icon = generic_political_discourse is_good = yes days_mission_timeout = 90 visible = { has_country_flag = A01_royal_campaign_active } activation = { has_country_flag = A01_royal_campaign_active } timeout_effect = { A01_finish_royal_election = yes } }
A01_royal_election_term = { icon = generic_political_discourse is_good = yes days_mission_timeout = 720 visible = { has_country_flag = A01_prime_minister_elected NOT = { has_country_flag = A01_royal_campaign_active } } activation = { has_country_flag = A01_prime_minister_elected NOT = { has_country_flag = A01_royal_campaign_active } } timeout_effect = { A01_start_royal_election = yes } }
}
'''
save('common/decisions/A01_royal_story.txt',dec)
# Do not leave the older Crown struggle events periodically resurrecting the defeated Council.
p='events/A01_crown_struggle.txt';et=parse(read(p))
for k,o,n in et:
    if k=='country_event':value(n,'trigger').extend(parse('NOT = { has_country_flag = A01_admiralty_defeated }'))
save(p,dump(et)+'\n')
# Initialise explicit counters without changing existing regency/succession gates.
p='common/scripted_effects/A01_crown_struggle.txt';et=parse(read(p));init=value(value(et,'A01_initialize_crown_struggle'),'if')
init.extend(parse('set_variable = { A01_admiralty_evidence = 0 } set_variable = { A01_fleet_loyalty = 0 } set_variable = { A01_sultan_confidence = 0 } set_variable = { A01_civic_support = 0 }'))
save(p,dump(et)+'\n')
# Old descriptions must agree with the new flow, including every older duplicate.
updates={
'A01_settle_crown_crisis_desc':('Совет устранён, а островной договор подписан. Закрепим гражданское морское министерство и определим, кому принадлежит победа: конституции или личной власти королевы.','The Council is defeated and the island compact signed. Consolidate the civilian navy ministry and decide whether victory belongs to the constitution or personal royal authority.'),
'A01_royal_constitution_desc':('После устранения политической власти адмиралов корона примет конституцию. Парламент утвердит избирательный закон и изберёт премьер-министра.','After ending admiral political rule, the Crown adopts a constitution. Parliament will pass an electoral law and elect a prime minister.'),
'A01_royal_guard_corps_desc':('Сформировать отдельную дивизию королевской гвардии и создать военную опору реформ. Гвардия позволит силой устранить Совет, но чистка ослабит флот.','Raise a Royal Guard division to support reform. The Guard enables forcible dissolution of the Council, at the cost of fleet disruption.'),
}
for lang,index in [('russian',0),('english',1)]:
    for p in (R/f'localisation/{lang}').glob('*.yml'):
        s=p.read_text(encoding='utf-8-sig');old=s
        for key,v in updates.items():s=re.sub(r'(?m)^\s*'+re.escape(key)+r':\d*\s+".*"$',f' {key}:0 "{v[index]}"',s)
        if s!=old:save(str(p.relative_to(R)),s)
    escaped={k:v[index].replace('\n',r'\n') for k,v in L.items()}
    save(f'localisation/{lang}/zzzzzzzzzz_royal_story_l_{lang}.yml',f'l_{lang}:\n'+''.join(f' {k}:0 "{v}"\n' for k,v in escaped.items()))
save('tools/royal_story_manifest.json',json.dumps({'new_focuses':new_ids,'focus_art':focus_art,'ideas':{k:v[4] for k,v in ideas.items()},'palette':['orange','white','blue'],'event_count':15},ensure_ascii=False,indent=2))
print(f'Added {len(new_ids)} focuses, {len(ideas)} visible spirits and 15 events.')
