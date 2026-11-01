"""British Leviathan campaign. Local authoring source, no legacy migrations.

Preserves the Australian federation, WTC ledger, Maltese sovereignty and shared
SEN custody flags. Naval OOBs have separate Man the Guns and legacy versions.
"""
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
LOC={'russian':{},'english':{}};FOCUSES=[];IDEAS=[];EVENTS=['add_namespace = blv_campaign'];FX=[];TR=[];DEC=[]

def write(path,text,bom=False):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text.rstrip()+'\n',encoding='utf-8-sig' if bom else 'utf-8')

def loc(key,ru,en):
    for lang,text in [('russian',ru),('english',en)]:
        assert key not in LOC[lang],key
        LOC[lang][key]=text

def focus(key,ru,en,rd,ed,x,y,parents=(),reward='add_political_power = 30',gate='',excludes=(),cost=5,icon='GFX_goal_generic_national_unity',ai=5):
    fid='BLV_'+key;loc(fid,ru,en);loc(fid+'_desc',rd,ed)
    prereq=' '.join(f'prerequisite = {{ focus = BLV_{p} }}' for p in parents)
    exclusion=' '.join(f'mutually_exclusive = {{ focus = BLV_{p} }}' for p in excludes)
    available=f'available = {{ {gate} }}' if gate else ''
    FOCUSES.append(dict(id=fid,x=x,y=y,parents=['BLV_'+p for p in parents],script=f' focus = {{ id = {fid} icon = {icon} x = {x} y = {y} cost = {cost} {prereq} {exclusion} {available} cancel_if_invalid = yes ai_will_do = {{ factor = {ai} }} completion_reward = {{ {reward} BLV_refresh = yes }} }}'))

def chain(rows,x,y,parent,icon='GFX_goal_generic_national_unity'):
    for i,row in enumerate(rows):
        key,ru,en,rd,ed,reward,*extra=row
        focus(key,ru,en,rd,ed,x,y+2*i,parents=(parent,),reward=reward,gate=extra[0] if extra else '',icon=icon)
        parent=key

def idea(key,ru,en,rd,ed,mods):
    key='BLV_'+key+'_spirit';loc(key,ru,en);loc(key+'_desc',rd,ed)
    IDEAS.append(f' {key} = {{ picture = generic_pp_unity_bonus removal_cost = -1 modifier = {{ {mods} }} }}')

def fx(key,body):FX.append(f'BLV_{key} = {{\n{body}\n}}')
def trigger(key,body):TR.append(f'BLV_{key} = {{ {body} }}')

def event(n,ru,en,rd,ed,options,gate='tag = A02',hidden=False):
    key=f'blv_campaign.{n}'
    if hidden:
        EVENTS.append(f'country_event = {{ id = {key} hidden = yes is_triggered_only = yes immediate = {{ {rd} }} }}');return
    loc(key+'.t',ru,en);loc(key+'.d',rd,ed)
    rows=[f'country_event = {{ id = {key} title = {key}.t desc = {key}.d picture = GFX_1896_event_talks is_triggered_only = yes timeout_days = 20 trigger = {{ {gate} }}']
    for i,(ar,ae,body,chance,*optgate) in enumerate(options):
        k=key+'.'+'abcd'[i];loc(k,ar,ae)
        cond=f'trigger = {{ {optgate[0]} }}' if optgate else ''
        rows.append(f' option = {{ name = {k} {cond} ai_chance = {{ {chance} }} {body} }}')
    EVENTS.append('\n'.join(rows+['}']))

def building(kind,state=None):
    scope=f'{state}' if state else 'capital_scope'
    return f'{scope} = {{ if = {{ limit = {{ is_owned_by = ROOT is_controlled_by = ROOT }} add_extra_state_shared_building_slots = 1 add_building_construction = {{ type = {kind} level = 1 instant_build = yes }} }} }}'

def bonus(cat='industry',value='0.5'):
    return f'add_tech_bonus = {{ name = BLV_research bonus = {value} uses = 1 category = {cat} }}'

def opening_and_politics():
    focus('leviathan','Империя после Исхода','An Empire After the Exodus','Лондон потерян, но флот, корона и колониальные станции уцелели. Правительство на Бермудах должно решить, какую Британию оно сохраняет.','London is lost. The fleet, Crown and overseas stations survive; the government in Bermuda must decide what kind of Britain to preserve.',26,0,reward='BLV_initialize = yes add_political_power = 40')
    focus('audit','Гроссбух уцелевшей империи','The Surviving Empire Ledger','Свести расходы флота, запасы станций и обязательства перед Палатой. Запасы и связность империи станут основой дальнейших решений.','Audit fleet spending, station reserves and Chamber obligations. Reserves and imperial cohesion underpin later decisions.',26,2,parents=('leviathan',),reward='add_to_variable = { BLV_reserve = 10 } add_political_power = 30')
    focus('hamilton','Совещание в Гамильтоне','The Hamilton Conference','Адмиралы, двор и делегаты колоний спорят о полномочиях. Начинается шестимесячный конституционный спор; поддержку групп можно менять решениями.','Admirals, the Court and colonial delegates dispute authority. A six-month constitutional debate opens with decisions to influence each bloc.',26,4,parents=('audit',),reward='BLV_open_council = yes custom_effect_tooltip = BLV_council_tt')
    focus('commission','Королевская комиссия о снабжении','Royal Supply Commission','Двор получит проверенные отчёты о станциях. Комиссия усиливает корону, но её материалы доступны любому будущему кабинету.','An independent supply audit strengthens the Crown and informs any future cabinet.',26,6,parents=('hamilton',),reward='add_to_variable = { BLV_crown = 2 } add_to_variable = { BLV_cohesion = 5 }')
    paths=[
      ('admiralty','Мандат адмирала Фишера','Admiral Fisher\'s Mandate','Фишер получает власть над морским бюджетом. Корона остаётся символом, а решения принимают профессиональные морские ведомства.','Fisher controls the naval budget while the Crown retains its formal position.',20,'BLV_admiralty','BLV_admiralty > 3','admiralty'),
      ('constitution','Ответственный кабинет империи','A Responsible Imperial Cabinet','Представители станций и колоний получат контроль бюджета. Компромисс укрепляет империю, но требует расходов на местные гарантии.','Representatives control the budget; local guarantees strengthen the empire but cost resources.',26,'BLV_delegates','BLV_delegates > 3','constitution'),
      ('crown','Чрезвычайные полномочия короны','Emergency Powers of the Crown','Корона подчинит себе соперничающие ведомства. Приказы станут исполняться быстрее, но удержание колоний потребует постоянных затрат.','The Crown subordinates rival departments. Orders become firmer, but colonial control remains costly.',32,'BLV_crown','BLV_crown > 3','crown')]
    for key,ru,en,rd,ed,x,_,cond,route in paths:
        focus(key,ru,en,rd,ed,x,8,parents=('commission',),reward=f'BLV_choose_{route} = yes',gate=f'NOT = {{ has_country_flag = BLV_path_chosen }} check_variable = {{ {cond} }}',excludes=tuple(p[0] for p in paths if p[0]!=key),cost=7,ai=8 if key=='admiralty' else 3)
    chain([
      ('naval_cabinet','Кабинет морских специалистов','A Cabinet of Naval Specialists','Подчинить закупки единому профессиональному ведомству.','Unify procurement under a professional department.','add_ideas = BLV_procurement_spirit'),
      ('merit','Назначения по службе','Appointments by Service','Открыть подготовку офицеров способным выходцам из станций.','Train capable officers from the overseas stations.','army_experience = 15 navy_experience = 15 add_to_variable = { BLV_cohesion = 5 }'),
      ('strategic_reserve','Стратегический резерв Адмиралтейства','An Admiralty Strategic Reserve','Выделить запасы для дальних операций вместо расширения придворных расходов.','Set aside reserves for distant operations.','add_to_variable = { BLV_reserve = 20 } add_stability = -0.02'),
      ('naval_state','Государство морской службы','The Naval Service State','Закрепить власть профессионального кабинета и постоянный порядок снабжения.','Consolidate the naval cabinet and permanent supply administration.','set_country_flag = BLV_naval_state add_ideas = BLV_naval_state_spirit')],20,10,'admiralty')
    chain([
      ('imperial_budget','Бюджет под парламентским контролем','Parliamentary Budget Control','Публичные сметы уменьшат влияние посредников и двора.','Public estimates curb intermediaries and Court spending.','add_to_variable = { BLV_cohesion = 8 } add_political_power = 35'),
      ('rights','Хартии островных граждан','Charters for Island Citizens','Гарантировать местным жителям доступ к суду и оплачиваемой службе.','Guarantee access to courts and paid public service.','add_ideas = BLV_island_rights_spirit add_to_variable = { BLV_reserve = -10 }'),
      ('delegates','Постоянная конференция колоний','A Standing Colonial Conference','Связать ответственность кабинета с голосами колониальных делегатов.','Link cabinet accountability to colonial representation.','add_to_variable = { BLV_cohesion = 10 } set_country_flag = BLV_dominion_policy'),
      ('maritime_commonwealth','Содружество свободных морей','A Commonwealth of Free Seas','Сделать добровольные соглашения основой империи. Австралийская федерация получит поддержку, но не будет создана без местных голосований.','Build the empire on negotiated consent. Support Australian federation without bypassing colonial votes.','add_ideas = BLV_maritime_commonwealth_spirit')],26,10,'constitution')
    chain([
      ('royal_secretariat','Единый королевский секретариат','A Unified Royal Secretariat','Поставить переписку станций под единый надзор короны.','Bring station correspondence under one royal office.','add_ideas = BLV_royal_secretariat_spirit'),
      ('crown_guard','Морская гвардия короны','The Crown Marine Guard','Сформировать одну подготовленную морскую пехотную часть на Бермудах.','Raise a trained marine battalion group in Bermuda.','BLV_raise_guard = yes'),
      ('loyal_governors','Присяга губернаторов','The Governors\' Oath','Лояльность местных кабинетов придётся подкреплять снабжением.','Back local loyalty with material support.','add_to_variable = { BLV_cohesion = 10 } add_to_variable = { BLV_reserve = -15 }'),
      ('imperial_prerogative','Сохранить имперскую прерогативу','Preserve Imperial Prerogative','Закрепить право короны сопротивляться отделению. Дипломатические решения остаются за игроком; чужие правительства не присоединяются автоматически.','Preserve the Crown\'s right to resist secession without automatically annexing foreign governments.','set_country_flag = BLV_royal_prerogative add_ideas = BLV_imperial_prerogative_spirit')],32,10,'crown')

def economy_and_finance():
    chain([
      ('rationing','Снабжать флот каждый месяц','Supply the Fleet Every Month','Составить постоянные сметы вместо чрезвычайных сборов. Это уменьшит ежемесячный расход запасов.','Replace emergency levies with regular estimates, reducing monthly reserve expenditure.','set_country_flag = BLV_regular_budget add_to_variable = { BLV_reserve = 10 }'),
      ('bermuda_workshops','Мастерские Гамильтона','Hamilton Workshops','Разместить безопасное производство рядом с правительством.','Establish safe production near the government.',building('industrial_complex')),
      ('coal_depots','Угольные склады дальних станций','Coaling Depots for Distant Stations','Создать распределённый запас топлива. Склады пополняют имперский резерв каждый месяц.','Distributed depots replenish the imperial reserve each month.','set_country_flag = BLV_depots_ready add_fuel = 15000'),
      ('machine_tools','Станки для островной промышленности','Machine Tools for Island Industry','Поддержать инженерную школу и обслуживание оборудования.','Support engineering and equipment maintenance.',bonus()),
      ('ordnance','Островные оружейные заказы','Island Ordnance Orders','Обеспечить гарнизоны местными винтовками.','Supply garrisons with locally made rifles.',building('arms_factory')),
      ('nz_industry','Новозеландские мастерские','New Zealand Workshops','Перенести часть гражданских заказов на безопасные острова Новой Зеландии.','Place civilian orders in safe New Zealand.',building('industrial_complex',284),'284 = { is_owned_by = ROOT is_controlled_by = ROOT }'),
      ('cable_school','Школа кабельных инженеров','A School of Cable Engineers','Снизить зависимость от иностранных специалистов связи.','Train domestic cable engineers.',bonus()),
      ('island_economy','Промышленность океанской державы','An Oceanic Industrial Economy','Объединить островные предприятия общими стандартами и заказами.','Unify island firms through common standards and orders.','add_ideas = BLV_island_industry_spirit')],4,4,'audit','GFX_goal_generic_construct_civ_factory')
    chain([
      ('credit_audit','Цена полиса Ламберта','The Price of Lambert\'s Policy','Британия начинает с тяжёлым долгом ВТП. Проверить обязательства без обнуления существующей задолженности.','Audit Britain\'s heavy Chamber debt without resetting its existing ledger.','WTC_initialize_effect = yes set_country_flag = WTN_relations_open add_political_power = 30'),
      ('chamber_desk','Представительство Палаты при казне','A Chamber Desk at the Treasury','Открыть обычные соглашения ВТП; Палата сохраняет право отказать.','Open normal Chamber compacts, subject to its approval.','set_country_flag = WTN_compact_desk_open custom_effect_tooltip = WTN_open_compact_tt')],10,4,'audit','GFX_goal_generic_political_pressure')
    focus('independent_accounts','Собственный морской расчёт','Independent Maritime Accounts','Оплатить сокращение долга и подготовить собственные расчёты. Этот путь не создаёт флот из ничего и не отменяет существующих долгов.','Pay down debt and develop independent accounts without cancelling the ledger.',8,8,parents=('chamber_desk',),excludes=('lambert_compact',),reward='add_political_power = -50 add_to_variable = { WTC_debt = -15 } WTC_refresh_effect = yes set_country_flag = BLV_own_accounts')
    focus('lambert_compact','Договор флота и Палаты','A Fleet and Chamber Compact','Поддержать морскую охрану Палаты в обмен на договорное обслуживание. Кредитные соглашения заключаются через существующие переговоры.','Back Chamber shipping protection and pursue service agreements through its existing negotiations.',12,8,parents=('chamber_desk',),excludes=('independent_accounts',),reward='clr_country_flag = WTN_cover_revoked set_country_flag = BLV_chamber_course A04 = { WTC_check_cover_effect = yes } add_to_variable = { BLV_reserve = 10 }')
    focus('insurance','Адмиралтейское страховое бюро','An Admiralty Insurance Office','Собственная страховка уменьшает уязвимость транспорта. Учреждение бюро потребует средств и не простит старые долги.','Domestic insurance protects shipping but requires funds and does not forgive debt.',8,10,parents=('independent_accounts',),reward='add_to_variable = { BLV_reserve = -10 } add_ideas = BLV_insurance_spirit')
    focus('revoke_cover','Отозвать морское прикрытие Палаты','Withdraw Chamber Naval Cover','Отозвать британское прикрытие взысканий ВТП. Это изменит действующую мировую систему санкций и ухудшит наши отношения с кредитором.','Withdraw naval cover for Chamber enforcement, changing its live global sanctions system.',8,12,parents=('insurance',),reward='set_country_flag = WTN_cover_revoked A04 = { WTC_check_cover_effect = yes } add_stability = -0.03')
    focus('service_contracts','Договоры обслуживания станций','Station Service Contracts','Использовать договорные поставки, не передавая Палате суверенитет.','Use negotiated supply contracts without ceding sovereignty.',12,10,parents=('lambert_compact',),reward='add_timed_idea = { idea = WTN_british_contract days = 360 } add_to_variable = { BLV_reserve = 15 }')
    focus('debt_settlement','Свести имперские обязательства','Settle Imperial Obligations','Погасить часть задолженности за счёт бюджетных средств. Регулярные платежи остаются доступны отдельными решениями.','Pay down liabilities with budget funds; recurring repayments remain available.',10,14,parents=('credit_audit',),gate='has_political_power > 74',reward='add_political_power = -75 add_to_variable = { WTC_debt = -20 } WTC_refresh_effect = yes add_to_variable = { BLV_cohesion = 5 }')

def fleet_and_army():
    chain([
      ('fleet_register','Перепись уцелевших эскадр','Register the Surviving Squadrons','Свести Атлантическую и Восточную эскадры в общий реестр. Стартовые корабли выдаются один раз и не дублируются этим фокусом.','Unify Atlantic and Eastern squadron records. This focus does not duplicate the starting fleet.','navy_experience = 20 add_to_variable = { BLV_reserve = 5 }'),
      ('bermuda_dock','Доковый комплекс Бермуд','Bermuda Dock Facilities','Расширить ремонтную базу Атлантической эскадры.','Expand repair facilities for the Atlantic squadron.',building('dockyard')+' 696 = { if = { limit = { is_owned_by = ROOT is_controlled_by = ROOT } add_building_construction = { type = naval_base province = 13010 level = 2 instant_build = yes } } }'),
      ('engine_rooms','Реформа машинных команд','Reform the Engine-Room Service','Сократить простои и обучить механиков парового флота.','Train steam-fleet engineers and reduce downtime.','add_ideas = BLV_engine_rooms_spirit '+bonus('naval_equipment'))],46,4,'audit','GFX_goal_generic_navy_doctrines_tactics')
    focus('battle_line','Сосредоточенная линия броненосцев','A Concentrated Ironclad Line','Ставка на решающее сражение усиливает тяжёлые корабли, но связывает часть снабжения.','A decisive battle doctrine strengthens capital ships but consumes reserves.',44,10,parents=('engine_rooms',),excludes=('cruiser_routes',),reward='add_ideas = BLV_battle_line_spirit add_to_variable = { BLV_reserve = -10 } navy_experience = 25',icon='GFX_goal_generic_navy_doctrines_tactics')
    focus('cruiser_routes','Крейсеры на торговых путях','Cruisers on the Trade Routes','Распределённые крейсерские силы защищают снабжение вместо концентрации всего флота.','Dispersed cruisers protect supply routes.',48,10,parents=('engine_rooms',),excludes=('battle_line',),reward='add_ideas = BLV_cruiser_routes_spirit navy_experience = 20',icon='GFX_goal_generic_navy_doctrines_tactics')
    focus('naval_staff','Единый морской оперативный штаб','A Joint Naval Operations Staff','Штаб согласует действия эскадр обеих доктрин.','Coordinate squadrons under either naval doctrine.',46,12,parents=('fleet_register',),reward='add_ideas = BLV_naval_staff_spirit navy_experience = 15',icon='GFX_goal_generic_navy_doctrines_tactics')
    chain([
      ('convoy_service','Океанская служба конвоев','Ocean Convoy Service','Выделить транспорты и обучить службы сопровождения.','Commission transports and train escort services.','add_equipment_to_stockpile = { type = convoy_1 amount = 20 } add_ideas = BLV_escorts_spirit'),
      ('singapore_docks','Сингапурский ремонтный узел','Singapore Repair Station','Развивать базу только при действительном британском контроле Сингапура.','Develop the base only while Singapore is owned and controlled by Britain.',building('dockyard',1021),'1021 = { is_owned_by = ROOT is_controlled_by = ROOT }'),
      ('fleet_logistics','Флот, который может оставаться в море','A Fleet That Can Stay at Sea','Согласовать ремонт, уголь и пополнение запасов.','Coordinate repair, coal and replenishment.','add_to_variable = { BLV_reserve = 20 } add_ideas = BLV_fleet_logistics_spirit')],46,14,'naval_staff','GFX_goal_generic_navy_doctrines_tactics')
    chain([
      ('garrison_audit','Гарнизоны без смены','Garrisons Awaiting Relief','Проверить службу в Гибралтаре, Сингапуре и Гонконге. Песнь делает постоянную ротацию необходимостью.','Audit Gibraltar, Singapore and Hong Kong garrisons; the Song makes rotation essential.','army_experience = 10 set_country_flag = BLV_rotation_open'),
      ('rotation','Регулярная смена гарнизонов','Regular Garrison Rotation','Оплатить безопасное возвращение заболевших и подготовку смен.','Fund relief crews and medical evacuation.','add_to_variable = { BLV_reserve = -10 } add_ideas = BLV_rotation_spirit'),
      ('marines','Морская пехота дальних станций','Marines for Distant Stations','Создать одну морскую пехотную группу и общую программу подготовки.','Raise one marine group and standardise training.','BLV_raise_guard = yes '+bonus('land_doctrine','0.25')),
      ('field_hospitals','Госпитали эвакуационного флота','Evacuation Fleet Hospitals','Связать передовые перевязочные пункты с безопасными островными госпиталями.','Link forward medical posts to safe island hospitals.','add_ideas = BLV_field_hospitals_spirit'),
      ('colonial_service','Оплачиваемая колониальная служба','Paid Colonial Service','Готовить местных специалистов снабжения и офицеров.','Train local supply specialists and officers.','add_to_variable = { BLV_cohesion = 8 } add_manpower = 1500'),
      ('amphibious_staff','Штаб экспедиционных операций','Expeditionary Operations Staff','Научить штабы снабжать небольшой десант, а не обещать мгновенное покорение континента.','Train staff to supply limited landings rather than promise instant continental conquest.','add_ideas = BLV_expedition_staff_spirit army_experience = 20')],54,6,'hamilton','GFX_goal_generic_army_doctrines')

def empire_and_pacific():
    chain([
      ('station_census','Голоса дальних станций','Voices of the Distant Stations','Выслушать кабинеты и гарнизоны, от которых зависит морская сеть.','Hear the governments and garrisons sustaining the maritime network.','add_to_variable = { BLV_cohesion = 8 }'),
      ('australian_dossier','Австралийское досье','The Australian Dossier','Шесть правительств требуют разных гарантий. Британия должна отвечать на их проекты, а не создавать федерацию за них.','Six governments seek different guarantees. Britain must answer their proposals rather than create federation for them.','set_country_flag = BLV_australia_dossier add_political_power = 25'),
      ],38,6,'hamilton')
    focus('dominion_charters','Разрешить договорную федерацию','Permit a Negotiated Federation','Открыто поддержать австралийскую хартию. Местные референдумы и решения Сиднея сохраняются.','Support the Australian charter while preserving local referendums and Sydney\'s decisions.',40,10,parents=('australian_dossier',),excludes=('colonial_red_line',),reward='set_country_flag = BLV_dominion_policy add_to_variable = { BLV_cohesion = 5 }')
    focus('nz_ports','Новозеландские порты империи','Imperial Ports in New Zealand','Поддержать самостоятельное снабжение британских владений в Новой Зеландии.','Support supplies to Britain\'s New Zealand possessions.',38,12,parents=('australian_dossier',),gate='284 = { is_owned_by = ROOT is_controlled_by = ROOT }',reward=building('dockyard',284))
    focus('pacific_stations','Станции Фиджи и Новой Гвинеи','Fiji and New Guinea Stations','Согласовать ротацию и снабжение дальних гарнизонов.','Coordinate relief and supply for distant garrisons.',38,14,parents=('nz_ports',),reward='add_to_variable = { BLV_reserve = 10 } add_to_variable = { BLV_cohesion = 5 }')
    focus('colonial_red_line','Предел колониальных уступок','The Limit of Colonial Concessions','Отказаться от автоматической поддержки новых хартий. Британский игрок по-прежнему сможет принять конкретное предложение Австралии.','Withdraw automatic support for new charters; the British player may still accept individual Australian proposals.',36,10,parents=('australian_dossier',),excludes=('dominion_charters',),gate='has_country_flag = BLV_crown_path',reward='set_country_flag = BLV_hard_empire clr_country_flag = BLV_dominion_policy add_war_support = 0.05')
    focus('australia_sovereignty','Признать самостоятельное Содружество','Recognise a Sovereign Commonwealth','Признать существующую австралийскую федерацию, если она ещё является нашим подданным. Соседние колонии не освобождаются и не присоединяются без согласия.','Recognise an existing Australian federation while leaving other colonies and their votes intact.',40,16,parents=('dominion_charters',),gate='country_exists = A07 A07 = { is_subject_of = A02 has_country_flag = AUC_commonwealth_proclaimed } NOT = { has_war_with = A07 }',reward='BLV_recognise_australia = yes')
    focus('reconquest','Планы возвращения мятежного доминиона','Plans to Recover a Breakaway Dominion','Подготовить повод к войне против независимой Австралии после избрания жёсткого курса. Войну объявляет игрок.','Prepare a war goal against an independent Australia under the coercive imperial policy. The player declares war.',36,18,parents=('colonial_red_line',),gate='has_country_flag = BLV_hard_empire is_subject = no country_exists = A07 A07 = { is_subject = no } NOT = { has_war_with = A07 } NOT = { is_in_faction_with = A07 }',reward='create_wargoal = { type = puppet_wargoal_focus target = A07 }',cost=7)
    chain([
      ('malacca','Свободный проход через Малакку','Free Passage Through Malacca','Объявить защиту морских коммуникаций британской задачей, не аннексируя чужие берега.','Protect sea communications without annexing foreign coasts.','add_war_support = 0.03 add_to_variable = { BLV_reserve = 5 }'),
      ('batavia_oil','Нефтяной договор с Батавией','A Batavian Oil Agreement','Предложить Людольфу договор поставок. Голландское правительство может отказаться; поставки зависят от сохранения нефтяного региона.','Offer Ludolf a supply agreement. The Dutch may refuse, and deliveries require control of the oil region.','BLV_request_oil = yes','country_exists = A01 NOT = { has_war_with = A01 }'),
      ('philippine_mission','Миссия на Филиппины','A Mission to the Philippines','Предложить взаимный военный доступ филиппинскому правительству. Это не вступление в его войны.','Offer reciprocal military access without entering Philippine wars.','BLV_request_philippines = yes','country_exists = A10 NOT = { has_war_with = A10 }'),
      ('pacific_deterrent','Тихоокеанское сдерживание','Pacific Deterrence','Согласовать действия Восточной эскадры и береговых постов.','Coordinate the Eastern squadron and coastwatchers.','add_ideas = BLV_pacific_deterrent_spirit navy_experience = 15'),
      ('japanese_note','Нота японскому Адмиралтейству','A Note to the Japanese Admiralty','Потребовать гарантий свободного судоходства. Токио может согласиться или отвергнуть требование.','Request free-navigation guarantees; Tokyo may accept or refuse.','BLV_request_navigation = yes','country_exists = A03 NOT = { has_war_with = A03 }'),
      ('war_plans','Планы войны на восточных морях','Eastern Seas War Plans','Подготовить кампанию за Манилу, если Япония всё ещё владеет ею и отвергла нашу ноту. Это повод к войне, а не автоматическое объявление.','Prepare a Manila war goal while Japan owns it and has rejected the British note. War is not automatic.','create_wargoal = { type = take_state_focus target = A03 generator = { 327 } }','is_subject = no country_exists = A03 has_country_flag = BLV_navigation_refused NOT = { has_war_with = A03 } NOT = { is_in_faction_with = A03 } 327 = { is_owned_by = A03 }'),
      ('eastern_supply','Снабжение Восточной эскадры','Supply the Eastern Squadron','Подготовить уголь, ремонт и пополнение к длительному походу.','Prepare coal, repair and replenishment for a prolonged deployment.','add_to_variable = { BLV_reserve = 20 } add_equipment_to_stockpile = { type = convoy_1 amount = 10 }')],62,6,'hamilton','GFX_goal_generic_navy_doctrines_tactics')

def science_and_arctic():
    chain([
      ('song_records','Закрытые журналы Песни','Classified Song Logs','Сопоставить отчёты гарнизонов, сохраняя разведывательные сведения в британском архиве.','Compare garrison records while retaining classified intelligence in the British archive.','set_country_flag = SEN_survey_done add_to_variable = { SEN_readiness = 20 }'),
      ('instruments','Приборы островных лабораторий','Instruments for Island Laboratories','Оснастить измерительную службу на Бермудах. Это не переносит Теслу с Мальты и не создаёт второго учёного.','Equip a Bermuda measurement service without moving or duplicating Tesla.','set_country_flag = SEN_laboratory_done add_to_variable = { SEN_science = 15 } '+building('industrial_complex')),
      ('malta_license','Договор с лабораторией Святого Ангела','A Saint Angelo Laboratory Agreement','Запросить научную переписку у действительного хранителя лаборатории Теслы. Её хозяин может отказать.','Request research correspondence from Tesla\'s actual host, who may refuse.','BLV_request_license = yes','has_global_flag = SEN_tesla_alive'),
      ('ungudja','Папка Унгуджи','The Unguja File','Разведка представит закрытый доклад. Другим странам останется известно лишь карантинное объяснение.','Intelligence presents a private report; other countries receive no classified findings.','country_event = { id = blv_campaign.10 days = 1 }'),
      ('clinical_rules','Правила работы с невосприимчивыми','Rules for Work with the Immune','Учредить контроль над обращением с Альфа. Политика сыворотки будет выбрана отдельно.','Regulate treatment of the immune; serum policy is chosen separately.','add_to_variable = { SEN_science = 10 } set_country_flag = BLV_clinical_review')],70,4,'audit','GFX_goal_generic_scientific_exchange')
    focus('serum_contract','Лицензированный Фонд Дюбуа','A Licensed Dubois Foundation','Разрешить закупки сыворотки. Эффект временный, расходует запасы и не позволяет безопасно заселить континенты.','Permit serum purchases. Temporary protection costs reserves and cannot make continents habitable.',68,14,parents=('clinical_rules',),excludes=('ethical_research',),reward='set_country_flag = BLV_serum_contract add_to_variable = { BLV_cohesion = -8 } add_to_variable = { SEN_science = 10 }')
    focus('ethical_research','Независимая врачебная комиссия','An Independent Medical Commission','Запретить принудительный сбор крови и поддержать добровольные исследования. Быстрого доступа к сыворотке не будет.','Prohibit coerced blood collection and support voluntary research, foregoing quick serum access.',72,14,parents=('clinical_rules',),excludes=('serum_contract',),reward='set_country_flag = BLV_ethical_research add_to_variable = { BLV_cohesion = 8 } add_ideas = BLV_medical_commission_spirit')
    focus('calibration','Калибровка глушителей','Calibrate the Suppressors','Проверить точность приборов и обучить инженеров. Ранние глушители защищают отдельные объекты, а не целые регионы.','Calibrate instruments and train engineers. Early suppressors protect individual sites, not whole regions.',70,16,parents=('instruments',),gate='BLV_tesla_access = yes',reward='add_to_variable = { SEN_science = 15 } set_country_flag = BLV_calibrated')
    focus('research_school','Адмиралтейская школа измерений','An Admiralty Measurement School','Наладить непрерывную подготовку специалистов, пока Тесла и артефакт сохраняют собственную судьбу.','Train specialists continuously while Tesla and the artifact retain independent custody and fate.',70,18,parents=('calibration',),reward='add_ideas = BLV_measurement_school_spirit '+bonus())
    chain([
      ('greenland_watch','Датская администрация Гренландии','The Danish Administration of Greenland','Сохранить формальную датскую администрацию и британское снабжение. Гренландия уже находится под британским контролем на карте мода.','Maintain Danish civil administration and British supplies in Greenland, already represented under British ownership.','add_to_variable = { SEN_security = 10 } add_to_variable = { SEN_readiness = 10 }'),
      ('arctic_depots','Полярные склады и зимовки','Polar Depots and Winter Stations','Подготовить зимнюю одежду, уголь и сменные команды.','Prepare winter clothing, coal and relief crews.','add_to_variable = { SEN_readiness = 20 } add_to_variable = { BLV_reserve = -10 }'),
      ('russian_note','Гренландская нота Рейкьявику','A Greenland Note to Reykjavik','Предложить обмен наблюдениями России. Согласие даст научное сотрудничество, а не право на русские земли.','Offer Russia an exchange of observations without territorial demands.','BLV_request_russia = yes','country_exists = A06 NOT = { has_war_with = A06 }'),
      ('scientific_cargo','Охрана научного груза','Protect the Scientific Cargo','Подготовить охрану и хранение, прежде чем трогать неизвестное устройство.','Prepare security and storage before disturbing an unknown device.','add_to_variable = { SEN_security = 20 }'),
      ('polar_mandate','Мандат полярной экспедиции','A Polar Expedition Mandate','Разрешить реальные экспедиционные проекты. Раскопки доступны с 1898 года и требуют контроля Гренландии.','Authorise expedition projects. Excavation opens in 1898 and requires Greenland control.','set_country_flag = BLV_arctic_open add_to_variable = { SEN_readiness = 15 } custom_effect_tooltip = BLV_arctic_tt'),
      ('archive','Архив резонансных частот','An Archive of Resonant Frequencies','Сохранить полученные данные независимо от дальнейшей судьбы предмета. Получение артефакта и его расшифровка выполняются отдельными проектами.','Preserve acquired knowledge independently of the object. Recovery and decoding require separate projects.','add_to_variable = { SEN_science = 10 } set_country_flag = BLV_archive_ready')],78,6,'hamilton','GFX_goal_generic_scientific_exchange')
    chain([
      ('remember_home','Родина за горизонтом','Home Beyond the Horizon','Собрать карты и реестры изгнанников, не объявляя мёртвые земли безопасными.','Gather maps and exile records without declaring dead lands safe.','add_political_power = 30 set_country_flag = BLV_return_open'),
      ('coastal_trials','Испытания у мёртвого берега','Trials off the Dead Coast','Снарядить измерительные рейсы. Континент не становится пригодным для жизни от одного фокуса.','Prepare measurement voyages; one focus cannot make the homeland habitable.','add_to_variable = { SEN_readiness = 15 }'),
      ('long_range','Глушитель дальнего действия','A Long-Range Suppressor','К 1900 году артефакт и доступ к Тесле позволяют поставить долгий опыт. Нужны научная база и сохранившиеся спектральные данные.','From 1900, artifact access and Tesla cooperation permit a long trial with sufficient scientific preparation.','set_country_flag = BLV_prototype_open custom_effect_tooltip = BLV_prototype_tt','date > 1899.12.31 BLV_tesla_access = yes BLV_artifact_access = yes check_variable = { SEN_science > 59 }'),
      ('pioneer_station','Первая станция возвращения','The First Return Station','После успешного прототипа подготовить небольшой береговой узел. Проект требует времени, приборов и ротации; вся Британия не передаётся нам автоматически.','After a successful prototype, prepare a small coastal station. The project costs time and supplies and does not automatically transfer Britain.','set_country_flag = BLV_station_open custom_effect_tooltip = BLV_station_tt','has_country_flag = SEN_advanced_knowledge')],86,20,'research_school','GFX_goal_generic_scientific_exchange')

def spirits():
    rows=[
      ('admiralty','Кабинет Фишера','Fisher\'s Cabinet','Морское ведомство руководит государственными расходами.','The naval cabinet directs state spending.','navy_org_factor = 0.04 stability_factor = -0.02'),
      ('constitution','Ответственный имперский кабинет','Responsible Imperial Cabinet','Ответственность бюджета укрепляет согласие станций.','Budget accountability strengthens station consent.','political_power_gain = 0.10 stability_factor = 0.04'),
      ('crown','Королевский чрезвычайный совет','Royal Emergency Council','Корона принимает на себя прямую ответственность за империю.','The Crown assumes direct responsibility for the empire.','political_power_gain = 0.15 war_support_factor = 0.03'),
      ('procurement','Адмиралтейские закупки','Admiralty Procurement','Единые заказы сокращают производственные задержки.','Unified orders reduce production delays.','production_factory_efficiency_gain_factor = 0.05'),
      ('naval_state','Государство морской службы','Naval Service State','Постоянная служба поддерживает боеспособность.','Permanent service supports readiness.','naval_coordination = 0.05 consumer_goods_factor = 0.02'),
      ('island_rights','Хартии островных граждан','Island Citizens\' Charters','Местные жители получают гарантии суда и службы.','Local residents receive legal and service guarantees.','stability_factor = 0.04 recruitable_population_factor = 0.05'),
      ('maritime_commonwealth','Содружество свободных морей','Commonwealth of Free Seas','Добровольные соглашения укрепляют морскую сеть.','Negotiated consent sustains the maritime network.','political_power_gain = 0.10 production_speed_industrial_complex_factor = 0.05'),
      ('royal_secretariat','Королевский секретариат','Royal Secretariat','Единая переписка сокращает ведомственные задержки.','Unified correspondence reduces departmental delay.','political_power_gain = 0.10'),
      ('imperial_prerogative','Имперская прерогатива','Imperial Prerogative','Удержание станций требует расходов на гарнизоны.','Holding stations demands garrison expenditure.','army_defence_factor = 0.04 consumer_goods_factor = 0.03'),
      ('island_industry','Островная промышленная сеть','Island Industrial Network','Общие стандарты ускоряют расширение предприятий.','Shared standards speed industrial expansion.','production_speed_industrial_complex_factor = 0.06'),
      ('insurance','Адмиралтейское страховое бюро','Admiralty Insurance Office','Собственная страховка уменьшает зависимость перевозок.','Domestic insurance supports shipping independence.','convoy_escort_efficiency = 0.05 consumer_goods_factor = 0.02'),
      ('engine_rooms','Обученные машинные команды','Trained Engine-Room Crews','Подготовленные механики поддерживают организацию флота.','Trained engineers sustain fleet organisation.','navy_org_factor = 0.04'),
      ('battle_line','Линия броненосцев','The Ironclad Line','Сосредоточение усиливает боевые корабли.','Concentration strengthens capital ships.','navy_capital_ship_attack_factor = 0.05'),
      ('cruiser_routes','Крейсерское прикрытие путей','Cruiser Route Protection','Распределённые силы улучшают охранение.','Dispersed forces improve escorts.','convoy_escort_efficiency = 0.10'),
      ('naval_staff','Морской оперативный штаб','Naval Operations Staff','Штаб координирует дальние эскадры.','The staff coordinates distant squadrons.','naval_coordination = 0.05'),
      ('escorts','Океанская служба конвоев','Ocean Convoy Service','Сопровождение поддерживает регулярность поставок.','Escorts sustain regular supplies.','convoy_escort_efficiency = 0.08'),
      ('fleet_logistics','Согласованное снабжение флота','Coordinated Fleet Logistics','Службы запасов уменьшают расход снабжения.','Reserve services reduce supply consumption.','supply_consumption_factor = -0.04'),
      ('rotation','Смена гарнизонов','Garrison Rotation','Ротация уменьшает истощение передовых частей.','Rotation reduces forward-unit exhaustion.','army_org_regain = 0.04'),
      ('field_hospitals','Эвакуационные госпитали','Evacuation Hospitals','Дальняя медицинская служба возвращает людей в строй.','Medical evacuation returns personnel to service.','army_org_regain = 0.03'),
      ('expedition_staff','Штаб экспедиционных операций','Expeditionary Staff','Специалисты готовят снабжение малых десантов.','Specialists prepare small landing forces.','max_planning_factor = 0.05'),
      ('pacific_deterrent','Восточная система сдерживания','Eastern Deterrence System','Станции и эскадры действуют по общему плану.','Stations and squadrons follow a common plan.','navy_org_factor = 0.03 army_defence_factor = 0.03'),
      ('medical_commission','Независимая врачебная комиссия','Independent Medical Commission','Медицинские гарантии укрепляют доверие к исследованиям.','Medical safeguards strengthen trust in research.','stability_factor = 0.03'),
      ('measurement_school','Адмиралтейская школа измерений','Admiralty Measurement School','Постоянная подготовка инженеров поддерживает исследования.','Continuing engineering training supports research.','research_speed_factor = 0.03'),
      ('supply_crisis','Станции без запасов','Stations Without Supplies','Истощённые запасы нарушают работу эскадр.','Depleted reserves disrupt squadron operations.','navy_org_factor = -0.10 supply_consumption_factor = 0.05'),
      ('imperial_strain','Империя теряет связность','Imperial Cohesion Frays','Невыполненные обязательства ослабляют общий кабинет.','Unfulfilled obligations weaken the cabinet.','political_power_gain = -0.15 stability_factor = -0.04'),
      ('oil_contract','Договорные поставки Батавии','Batavian Contract Deliveries','Поставки действуют лишь пока партнёр удерживает нефтяной регион и не воюет с нами.','Deliveries require a friendly partner controlling the oil region.','consumer_goods_factor = 0.02'),
      ('serum','Временная сыворотка Дюбуа','Temporary Dubois Serum','Короткий курс помогает полевой группе, но не делает материк безопасным.','A brief course helps field crews but does not make the continent safe.','army_org_regain = 0.03'),
      ('prototype','Испытанный дальний глушитель','A Tested Long-Range Suppressor','Прототип защищает отдельный узел. Развёртывание требует оборудования и постоянного обслуживания.','A prototype protects a single site and requires equipment and maintenance.','research_speed_factor = 0.02'),
      ('coastal_station','Опытная береговая станция','Experimental Coastal Station','Небольшой узел сохраняется за счёт непрерывного снабжения и смены людей.','A small site survives through continuous supply and rotation.','research_speed_factor = 0.02 consumer_goods_factor = 0.03')]
    for row in rows:idea(*row)

def mechanics():
    trigger('is_britain','tag = A02 exists = yes has_capitulated = no')
    trigger('tesla_access','has_global_flag = SEN_tesla_alive OR = { has_country_flag = SEN_tesla_host AND = { has_country_flag = SEN_research_license any_country = { has_country_flag = SEN_tesla_host has_capitulated = no NOT = { has_war_with = A02 } } } }')
    trigger('artifact_access','NOT = { has_global_flag = SEN_artifact_destroyed } has_global_flag = SEN_artifact_found OR = { AND = { has_country_flag = SEN_artifact_holder any_state = { has_state_flag = SEN_artifact_site is_controlled_by = A02 } } has_global_flag = SEN_open_spectrum }')
    trigger('oil_live','has_country_flag = BLV_oil_signed country_exists = A01 NOT = { has_war_with = A01 } A01 = { has_capitulated = no } 334 = { is_owned_by = A01 is_controlled_by = A01 }')
    trigger('license_possible','BLV_is_britain = yes has_global_flag = SEN_tesla_alive NOT = { has_country_flag = BLV_license_pending } NOT = { has_country_flag = SEN_research_license } NOT = { has_country_flag = SEN_tesla_host } any_country = { has_country_flag = SEN_tesla_host has_capitulated = no NOT = { has_war_with = A02 } }')
    fx('initialize','''if = { limit = { BLV_is_britain = yes NOT = { has_country_flag = BLV_initialized } }
 set_country_flag = BLV_initialized set_variable = { BLV_reserve = 55 } set_variable = { BLV_cohesion = 50 }
 set_variable = { BLV_admiralty = 2 } set_variable = { BLV_crown = 2 } set_variable = { BLV_delegates = 2 }
 WTC_initialize_effect = yes
 if = { limit = { NOT = { has_country_flag = SEN_initialized } } set_country_flag = SEN_initialized set_variable = { SEN_science = 0 } set_variable = { SEN_readiness = 0 } set_variable = { SEN_security = 20 } set_variable = { SEN_exposure = 0 } }
 if = { limit = { NOT = { has_global_flag = SEN_world_initialized } }
  set_global_flag = SEN_world_initialized
  if = { limit = { NOT = { has_global_flag = SEN_tesla_lost } }
   set_global_flag = SEN_tesla_alive
   if = { limit = { NOT = { any_country = { has_country_flag = SEN_tesla_host } } }
    if = { limit = { country_exists = MLT } MLT = { set_country_flag = SEN_tesla_host } 116 = { set_state_flag = SEN_tesla_site } }
    else = { set_country_flag = SEN_tesla_host capital_scope = { set_state_flag = SEN_tesla_site } }
   }
  }
 }
}
BLV_initialize_fleet = yes
BLV_refresh = yes''')
    fx('refresh','''if = { limit = { tag = A02 has_country_flag = BLV_initialized }
 hidden_effect = {
  clamp_variable = { var = BLV_reserve min = 0 max = 100 } clamp_variable = { var = BLV_cohesion min = 0 max = 100 }
  clamp_variable = { var = BLV_admiralty min = 0 max = 10 } clamp_variable = { var = BLV_crown min = 0 max = 10 } clamp_variable = { var = BLV_delegates min = 0 max = 10 }
  clamp_variable = { var = SEN_science min = 0 max = 100 } clamp_variable = { var = SEN_readiness min = 0 max = 100 } clamp_variable = { var = SEN_security min = 0 max = 100 } clamp_variable = { var = SEN_exposure min = 0 max = 100 }
 }
 if = { limit = { check_variable = { BLV_reserve < 20 } } add_ideas = BLV_supply_crisis_spirit } else = { remove_ideas = BLV_supply_crisis_spirit }
 if = { limit = { check_variable = { BLV_cohesion < 25 } } add_ideas = BLV_imperial_strain_spirit } else = { remove_ideas = BLV_imperial_strain_spirit }
 if = { limit = { BLV_oil_live = yes } add_ideas = BLV_oil_contract_spirit } else = { remove_ideas = BLV_oil_contract_spirit }
}''')
    fx('monthly','''if = { limit = { BLV_is_britain = yes has_country_flag = BLV_initialized }
 if = { limit = { has_country_flag = BLV_regular_budget } add_to_variable = { BLV_reserve = -1 } } else = { add_to_variable = { BLV_reserve = -2 } }
 if = { limit = { has_country_flag = BLV_depots_ready } add_to_variable = { BLV_reserve = 2 } }
 if = { limit = { check_variable = { BLV_reserve < 20 } } add_to_variable = { BLV_cohesion = -3 } }
 else_if = { limit = { check_variable = { BLV_reserve > 49 } } add_to_variable = { BLV_cohesion = 1 } }
 if = { limit = { has_country_flag = BLV_hard_empire has_war = yes } add_to_variable = { BLV_cohesion = -1 } }
 if = { limit = { BLV_oil_live = yes } add_fuel = 3000 }
 if = { limit = { has_country_flag = SEN_return_done } add_to_variable = { BLV_reserve = -2 } add_to_variable = { SEN_exposure = 2 } }
 if = { limit = { check_variable = { BLV_reserve < 10 } NOT = { has_country_flag = BLV_crisis_cooldown } }
  set_country_flag = { flag = BLV_crisis_cooldown days = 180 } country_event = { id = blv_campaign.4 days = 1 }
 }
 BLV_refresh = yes
}''')
    fx('open_council','''if = { limit = { BLV_is_britain = yes NOT = { has_country_flag = BLV_council_open } }
 set_country_flag = BLV_council_open set_country_flag = { flag = BLV_debate_pending days = 210 }
 country_event = { id = blv_campaign.1 days = 1 } country_event = { id = blv_campaign.2 days = 180 }
}''')
    fx('extend_debate','''if = { limit = { BLV_is_britain = yes NOT = { has_country_flag = BLV_path_chosen } }
 add_stability = -0.03 set_country_flag = { flag = BLV_debate_pending days = 210 } country_event = { id = blv_campaign.2 days = 180 }
}''')
    for route in ('admiralty','constitution','crown'):
        political_change=''
        if route=='constitution':
            political_change='''if = { limit = { has_character = A02_canon_leader }
 add_country_leader_role = { character = A02_canon_leader promote_leader = yes country_leader = { ideology = conservatism expire = "1965.1.1.1" traits = { } } }
} set_popularities = { democratic = 65 neutrality = 35 } set_politics = { ruling_party = democratic elections_allowed = yes }'''
        fx('choose_'+route,f'''if = {{ limit = {{ BLV_is_britain = yes NOT = {{ has_country_flag = BLV_path_chosen }} }}
 set_country_flag = BLV_path_chosen set_country_flag = BLV_{route}_path clr_country_flag = BLV_debate_pending
 remove_ideas = PZ_british_admiralty add_ideas = BLV_{route}_spirit
 {political_change}
}}''')
    fx('recognise_australia','''if = { limit = { BLV_is_britain = yes country_exists = A07 NOT = { has_war_with = A07 } A07 = { is_subject_of = A02 has_country_flag = AUC_commonwealth_proclaimed } }
 set_autonomy = { target = A07 autonomy_state = autonomy_free end_wars = no end_civil_wars = no }
 A07 = { set_country_flag = AUC_sovereignty_recognized clr_country_flag = AUC_sovereignty_pending if = { limit = { is_in_faction_with = A02 } leave_faction = yes } country_event = { id = auc_campaign.4 days = 1 } }
 add_to_variable = { BLV_cohesion = 5 }
}''')
    for suffix,target,n,pending in [('oil','A01',5,'oil'),('philippines','A10',6,'philippines'),('navigation','A03',7,'navigation'),('russia','A06',8,'russia')]:
        fx('request_'+suffix,f'''if = {{ limit = {{ BLV_is_britain = yes country_exists = {target} NOT = {{ has_war_with = {target} }} NOT = {{ has_country_flag = BLV_{pending}_pending }} }}
 set_country_flag = {{ flag = BLV_{pending}_pending days = 45 }} {target} = {{ country_event = {{ id = blv_campaign.{n} days = 1 }} }}
}}''')
    fx('request_license','''if = { limit = { BLV_license_possible = yes }
 set_country_flag = { flag = BLV_license_pending days = 45 }
 every_country = { limit = { has_country_flag = SEN_tesla_host has_capitulated = no NOT = { has_war_with = A02 } } country_event = { id = blv_campaign.9 days = 1 } }
}''')
    fx('raise_guard','''if = { limit = { BLV_is_britain = yes NOT = { has_country_flag = BLV_guard_raised } 696 = { is_owned_by = A02 is_controlled_by = A02 } }
 set_country_flag = BLV_guard_raised load_oob = BLV_campaign_guard army_experience = 10
}''')

def diplomatic_events():
    event(1,'Кому отвечает Адмиралтейство','To Whom Does the Admiralty Answer?','Фишер требует единого морского бюджета, двор — верховного контроля, делегаты — ответственного кабинета. Первый выбор усиливает одну из групп. Окончательное решение принимается политическим фокусом.','Fisher wants a unified naval budget, the Court supreme control, and delegates an accountable cabinet. Back one bloc before choosing a political focus.',[
      ('Фишер знает нужды флота','Fisher knows the fleet', 'add_to_variable = { BLV_admiralty = 1 }','factor = 60'),
      ('Корона должна связать ведомства','The Crown must unite departments','add_to_variable = { BLV_crown = 1 }','factor = 20'),
      ('Бюджет требует представительства','Spending requires representation','add_to_variable = { BLV_delegates = 1 }','factor = 20')])
    event(2,'Совещание требует решения','The Conference Demands a Settlement','Спор затянулся. Ни одна сторона не должна превращать нехватку поддержки в мгновенный переворот: можно продлить переговоры, заплатив потерей доверия.','The debate has dragged on. Extend talks at a cost in public confidence rather than trigger an automatic coup.',[
      ('Продолжить переговоры','Continue the talks','BLV_extend_debate = yes','factor = 100')],gate='tag = A02 NOT = { has_country_flag = BLV_path_chosen } has_country_flag = BLV_council_open')
    event(4,'Станции требуют снабжения','The Stations Demand Supplies','На складах почти не осталось резервов. Срочная закупка за политическое влияние поддержит эскадры; урезание обязательств сбережёт бюджет, но ударит по доверию станций.','Depots are nearly empty. Emergency spending restores supplies; reducing commitments preserves the budget at the cost of station confidence.',[
      ('Оплатить срочную закупку','Pay for emergency supplies','add_political_power = -40 add_to_variable = { BLV_reserve = 20 } BLV_refresh = yes','factor = 80','has_political_power > 39'),
      ('Сократить дальние обязательства','Reduce distant commitments','add_to_variable = { BLV_reserve = 10 } add_to_variable = { BLV_cohesion = -8 } add_war_support = -0.03 BLV_refresh = yes','factor = 20')])
    # Every answer rechecks live relationships because the event may remain open.
    agreements=[
      (5,'Нефтяной договор с Левиафаном','An Oil Agreement with the Leviathan','Британия предлагает оплачиваемые поставки топлива. Договор действует, пока мы удерживаем Баликпапан и не воюем с британцами.','Britain offers paid fuel deliveries while we control Balikpapan and remain at peace.','A01','oil','BLV_oil_signed','add_political_power = 30'),
      (6,'Британская миссия на Филиппинах','A British Mission in the Philippines','Левиафан предлагает взаимный доступ к военным базам. Мы не становимся его подданными и не вступаем автоматически в новые войны.','The Leviathan offers reciprocal military access without subordination or automatic entry into wars.','A10','philippines','BLV_philippine_accord','give_military_access = A02 A02 = { give_military_access = A10 }'),
      (7,'Британская нота о судоходстве','Britain\'s Navigation Note','Британия требует гарантий для торговых судов. Принятие снизит напряжение; отказ даст британцам основание готовить конфликт. Территории этим соглашением не передаются.','Britain seeks merchant-shipping guarantees. Acceptance eases tensions; refusal permits British war preparations. No territory changes hands.','A03','navigation','BLV_navigation_signed','add_political_power = 20'),
      (8,'Обмен полярными наблюдениями','An Exchange of Polar Observations','Британские наблюдатели предлагают обмен данными. Артефакт и территории не передаются.','British observers offer research exchange without transferring the artifact or territory.','A06','russia','BLV_russian_accord','add_political_power = 20')]
    for n,ru,en,rd,ed,target,pending,signed,extra in agreements:
        valid=f'has_capitulated = no country_exists = A02 NOT = {{ has_war_with = A02 }} A02 = {{ has_capitulated = no has_country_flag = BLV_{pending}_pending }}'
        if pending=='oil':valid+=' 334 = { is_owned_by = A01 is_controlled_by = A01 }'
        accept=f'if = {{ limit = {{ {valid} }} {extra} A02 = {{ clr_country_flag = BLV_{pending}_pending set_country_flag = {signed} add_to_variable = {{ BLV_cohesion = 2 }} BLV_refresh = yes }} }}'
        refuse=f'A02 = {{ clr_country_flag = BLV_{pending}_pending set_country_flag = BLV_{pending}_refused }}'
        event(n,ru,en,rd,ed,[('Принять ограниченное соглашение','Accept the limited agreement',accept,'factor = 70'),('Отклонить предложение','Decline the proposal',refuse,'factor = 30')],gate=f'tag = {target} {valid}')
    event(9,'Лицензия для британских инженеров','A Licence for British Engineers','Адмиралтейство просит научную переписку с лабораторией Теслы. Передаются записи и право сотрудничества, а не сам учёный.','The Admiralty requests correspondence with Tesla\'s laboratory. Approval grants research cooperation, not custody of Tesla.',[
      ('Открыть научную переписку','Open research correspondence','if = { limit = { has_country_flag = SEN_tesla_host has_capitulated = no has_global_flag = SEN_tesla_alive NOT = { has_war_with = A02 } A02 = { has_country_flag = BLV_license_pending } } A02 = { clr_country_flag = BLV_license_pending set_country_flag = SEN_research_license add_to_variable = { SEN_science = 10 } } }','factor = 80'),
      ('Сохранить закрытый порядок','Keep the laboratory closed','A02 = { clr_country_flag = BLV_license_pending set_country_flag = BLV_license_refused }','factor = 20')],gate='has_country_flag = SEN_tesla_host has_global_flag = SEN_tesla_alive country_exists = A02 NOT = { has_war_with = A02 } A02 = { has_country_flag = BLV_license_pending }')
    event(10,'Унгуджа — только для Адмиралтейства','Unguja — Admiralty Eyes Only','Закрытый доклад: около семи процентов наблюдавшихся жителей сохраняют необычную устойчивость к Песни. Известие нельзя включать в открытые бюллетени. Мир продолжает видеть британский карантин, а не разведывательные выводы.','A classified report finds unusual resistance among roughly seven percent of observed residents. Keep the intelligence out of public bulletins; outsiders know only of the quarantine.',[
      ('Хранить доклад под грифом','Keep the report classified','set_country_flag = BLV_ungudja_file add_to_variable = { SEN_science = 5 }','factor = 100')])

def timed_projects():
    # Science uses the shared SEN flags so a later world-system build sees the same
    # Tesla, artifact, knowledge and physical custody rather than duplicate objects.
    projects=[
      ('excavation','Вскрыть гренландское хранилище','Open the Greenland Chamber','Работать 60 дней подо льдом, сохраняя контроль Гренландии. Артефакт может быть найден только один раз.','Work for 60 days while retaining Greenland control. The artifact can be found only once.',60,60,75,'has_country_flag = BLV_arctic_open check_variable = { SEN_readiness > 39 } date > 1898.1.31 101 = { is_owned_by = A02 is_controlled_by = A02 } NOT = { has_global_flag = SEN_artifact_found } NOT = { has_global_flag = SEN_artifact_destroyed }','BLV_claim_artifact = yes'),
      ('decode','Расшифровать полярные записи','Decode the Polar Records','Потратить 90 дней на расшифровку при сохранении доступа к артефакту и Тесле.','Spend 90 days decoding while retaining artifact and Tesla access.',90,75,75,'BLV_artifact_access = yes BLV_tesla_access = yes check_variable = { SEN_security > 29 } NOT = { has_country_flag = BLV_decoded }','set_country_flag = BLV_decoded set_country_flag = SEN_spectral_copy add_to_variable = { SEN_science = 25 }'),
      ('prototype','Испытать дальний глушитель','Test a Long-Range Suppressor','Девяностодневное испытание потребует 100 комплектов вспомогательного оборудования и доступа к обоим источникам знаний.','A 90-day trial requires 100 support equipment and continuing access to both sources of knowledge.',90,100,100,'has_country_flag = BLV_prototype_open date > 1899.12.31 BLV_artifact_access = yes BLV_tesla_access = yes check_variable = { SEN_science > 59 } check_variable = { SEN_security > 39 } NOT = { has_country_flag = SEN_advanced_knowledge }','set_country_flag = SEN_advanced_knowledge add_ideas = BLV_prototype_spirit'),
      ('station','Снарядить береговую станцию','Equip the Coastal Station','За 90 дней подготовить небольшой береговой узел с постоянным питанием. Это не массовое заселение и не автоматическая аннексия Британских островов.','Prepare a small powered coastal site over 90 days. This neither resettles nor annexes the British Isles.',90,100,200,'date > 1900.12.31 has_country_flag = BLV_station_open has_country_flag = SEN_advanced_knowledge NOT = { has_country_flag = SEN_return_done } check_variable = { SEN_exposure < 61 } check_variable = { SEN_readiness > 69 }','set_country_flag = SEN_return_done add_ideas = BLV_coastal_station_spirit')]
    for key,ru,en,rd,ed,days,pp,equip,req,reward in projects:
        flag='BLV_'+key+'_active';requirement='BLV_'+key+'_requirements'
        trigger(key+'_requirements','BLV_is_britain = yes check_variable = { BLV_reserve > 4 } '+req)
        fx('finish_'+key,f'''if = {{ limit = {{ has_country_flag = {flag} {requirement} = yes }}
 {reward} add_to_variable = {{ BLV_reserve = -5 }} BLV_refresh = yes
}} clr_country_flag = {flag}''')
        decision(key,ru,en,rd,ed,pp,'has_completed_focus = BLV_song_records',f'NOT = {{ has_country_flag = {flag} }} {requirement} = yes has_equipment = {{ support_equipment > {equip-1} }} check_variable = {{ BLV_reserve > 19 }}',f'set_country_flag = {flag} add_equipment_to_stockpile = {{ type = support_equipment amount = -{equip} }} add_to_variable = {{ BLV_reserve = -10 }}',duration=days,remove=f'BLV_finish_{key} = yes',cancel=f'NOT = {{ {requirement} = yes }}',cancel_effect=f'clr_country_flag = {flag}',cooldown=0,ai=2)
    fx('claim_artifact','''if = { limit = { BLV_is_britain = yes 101 = { is_owned_by = A02 is_controlled_by = A02 } NOT = { has_global_flag = SEN_artifact_found } NOT = { has_global_flag = SEN_artifact_destroyed } }
 every_country = { clr_country_flag = SEN_artifact_holder }
 every_state = { limit = { has_state_flag = SEN_artifact_site } clr_state_flag = SEN_artifact_site }
 set_global_flag = SEN_artifact_found set_country_flag = SEN_artifact_holder 101 = { set_state_flag = SEN_artifact_site }
 add_to_variable = { SEN_science = 10 } country_event = { id = blv_campaign.11 days = 1 }
}''')
    event(11,'Предмет из гренландского льда','The Object from the Greenland Ice','Артефакт найден, но он не выключает Песнь. Его необходимо охранять и расшифровать. Можно открыть спектральные данные миру или сохранить закрытый архив. Сам предмет остаётся единственным.','The artifact is found, but does not silence the Song. It needs security and decoding. Share the data or retain a private archive; the object remains unique.',[
      ('Сохранить закрытый архив','Keep a private archive','set_country_flag = SEN_private_archive add_to_variable = { SEN_security = 10 }','factor = 80'),
      ('Поделиться проверенными данными','Share verified data','if = { limit = { has_country_flag = SEN_artifact_holder NOT = { has_global_flag = SEN_artifact_destroyed } } set_global_flag = SEN_open_spectrum every_country = { limit = { NOT = { tag = ZZZ } } set_country_flag = SEN_spectral_copy } }','factor = 20')],gate='tag = A02 has_country_flag = SEN_artifact_holder NOT = { has_global_flag = SEN_artifact_destroyed }')
    # Physical custody follows control of its actual marked site. Learned science
    # and spectral copies are intentionally not erased by loss of the object.
    fx('custody','''if = { limit = { has_global_flag = SEN_artifact_found NOT = { has_global_flag = SEN_artifact_destroyed } }
 every_state = { limit = { has_state_flag = SEN_artifact_site }
  controller = { if = { limit = { exists = yes NOT = { tag = ZZZ } NOT = { has_country_flag = SEN_artifact_holder } }
   every_country = { clr_country_flag = SEN_artifact_holder } set_country_flag = SEN_artifact_holder
  } }
 }
}
if = { limit = { has_global_flag = SEN_tesla_alive }
 every_state = { limit = { has_state_flag = SEN_tesla_site }
  controller = { if = { limit = { exists = yes NOT = { tag = ZZZ } NOT = { has_country_flag = SEN_tesla_host } }
   every_country = { clr_country_flag = SEN_tesla_host } set_country_flag = SEN_tesla_host
  } }
 }
}''')

def decision(key,ru,en,rd,ed,cost,visible,gate,reward,cooldown=90,ai=1,duration=0,remove='',cancel='',cancel_effect=''):
    did='BLV_'+key;loc(did,ru,en);loc(did+'_desc',rd,ed)
    timed=f'days_remove = {duration} cancel_trigger = {{ {cancel} }} cancel_if_not_visible = yes cancel_effect = {{ {cancel_effect} }} remove_effect = {{ {remove} }}' if duration else ''
    DEC.append(f' {did} = {{ icon = generic_naval cost = {cost} days_re_enable = {cooldown} fire_only_once = no {timed} visible = {{ tag = A02 {visible} }} available = {{ {gate} }} complete_effect = {{ {reward} BLV_refresh = yes }} ai_will_do = {{ factor = {ai} }} }}')

def decisions():
    for bloc,ru,en in [('admiralty','капитанов','Captains'),('crown','двора','the Court'),('delegates','делегатов','Delegates')]:
        decision('support_'+bloc,'Поддержка '+ru,'Support '+en,'Поднять влияние группы на один пункт. Для выбора её политического пути требуется четыре пункта.','Raise this bloc\'s influence by one. Its political path requires four.',35,'has_country_flag = BLV_council_open NOT = { has_country_flag = BLV_path_chosen }','has_capitulated = no',f'add_to_variable = {{ BLV_{bloc} = 1 }}',cooldown=30)
    decision('supply_purchase','Закупить запасы для станций','Buy Station Supplies','Расходовать политическое влияние на пополнение общего резерва.','Spend political power to replenish the imperial reserve.',45,'has_country_flag = BLV_initialized','check_variable = { BLV_reserve < 81 }','add_to_variable = { BLV_reserve = 20 }',cooldown=60,ai=2)
    decision('station_grants','Выплатить жалованье дальним гарнизонам','Pay the Distant Garrisons','Передать 10 пунктов запаса станциям и укрепить связность на 10 пунктов.','Spend 10 reserve points to gain 10 cohesion.',30,'has_country_flag = BLV_initialized','check_variable = { BLV_reserve > 9 } check_variable = { BLV_cohesion < 91 }','add_to_variable = { BLV_reserve = -10 } add_to_variable = { BLV_cohesion = 10 }',cooldown=90)
    decision('license_again','Возобновить переговоры с лабораторией','Renew Laboratory Talks','Повторить запрос действительному хранителю Теслы.','Repeat the request to Tesla\'s current host.',40,'has_completed_focus = BLV_malta_license','BLV_license_possible = yes','BLV_request_license = yes',cooldown=180)
    for key,ru,en,fxname,gate in [
      ('oil_again','Возобновить переговоры с Батавией','Renew Batavian Talks','oil','country_exists = A01 NOT = { has_war_with = A01 } NOT = { has_country_flag = BLV_oil_pending } NOT = { has_country_flag = BLV_oil_signed }'),
      ('navigation_again','Повторить ноту Токио','Renew the Tokyo Note','navigation','country_exists = A03 NOT = { has_war_with = A03 } NOT = { has_country_flag = BLV_navigation_pending } NOT = { has_country_flag = BLV_navigation_signed }')]:
        decision(key,ru,en,'Повторить ограниченное дипломатическое предложение; адресат может отказать.','Renew the limited offer; the other government may refuse.',35,'has_country_flag = BLV_initialized',gate,f'BLV_request_{fxname} = yes',cooldown=180)
    decision('serum_purchase','Приобрести короткий курс сыворотки','Purchase a Brief Serum Course','Израсходовать 8 пунктов запаса на семь дней поддержки полевой группы.','Spend 8 reserve points for seven days of field support.',25,'has_country_flag = BLV_serum_contract','check_variable = { BLV_reserve > 7 } NOT = { has_idea = BLV_serum_spirit }','add_to_variable = { BLV_reserve = -8 } add_timed_idea = { idea = BLV_serum_spirit days = 7 }',cooldown=30)
    decision('field_rotation','Сменить полевые команды','Rotate the Field Crews','Снизить накопленное воздействие Песни на 25 пунктов, потратив 5 пунктов резерва.','Reduce Song exposure by 25 at a cost of 5 reserve points.',35,'has_completed_focus = BLV_song_records','check_variable = { SEN_exposure > 0 } check_variable = { BLV_reserve > 4 }','add_to_variable = { SEN_exposure = -25 } add_to_variable = { BLV_reserve = -5 }',cooldown=60)

def naval_oobs():
    ship_names={
      'atlantic': {'Ironclad':['Royal Sovereign','Hood'],'Cruiser':['Blake','Blenheim','Edgar','Royal Arthur'],'Escort':['Lightning','Decoy','Havock','Hornet','Ferret','Lynx','Boxer','Rocket']},
      'eastern': {'Ironclad':['Centurion','Barfleur'],'Cruiser':['Grafton','Hawke','Gibraltar','Crescent'],'Escort':['Daring','Defender','Teazer','Hasty','Dasher','Speedy','Charger','Hunter']},
    }
    modules={
      'Ironclad':('ship_hull_heavy_1','battleship','fixed_ship_battery_slot = ship_heavy_battery_1 fixed_ship_anti_air_slot = empty fixed_ship_fire_control_system_slot = ship_fire_control_system_0 fixed_ship_engine_slot = heavy_ship_engine_1 fixed_ship_armor_slot = ship_armor_bb_1 front_1_custom_slot = ship_heavy_battery_1 mid_1_custom_slot = empty mid_2_custom_slot = empty rear_1_custom_slot = empty','battleship_1'),
      'Cruiser':('ship_hull_cruiser_1','light_cruiser','fixed_ship_battery_slot = ship_light_medium_battery_1 fixed_ship_fire_control_system_slot = ship_fire_control_system_0 fixed_ship_engine_slot = cruiser_ship_engine_1 fixed_ship_armor_slot = ship_armor_protected_cruiser_1 fixed_ship_secondaries_slot = empty mid_1_custom_slot = empty mid_2_custom_slot = empty rear_1_custom_slot = empty','light_cruiser_1'),
      'Escort':('ship_hull_light_1','destroyer','fixed_ship_battery_slot = ship_light_battery_1 fixed_ship_radar_slot = empty fixed_ship_engine_slot = light_ship_engine_1 fixed_ship_torpedo_slot = ship_torpedo_1 mid_1_custom_slot = empty rear_1_custom_slot = empty','destroyer_1')}
    variants='\n'.join(f'create_equipment_variant = {{ name = "Leviathan {name}" type = {typ} parent_version = 0 modules = {{ {mods} }} }}' for name,(typ,_,mods,_) in modules.items())
    for fleet,port in [('atlantic',13010),('eastern',12299),('eastern_reserve',13010)]:
        for legacy in (False,True):
            ships=[]
            for kind,count in [('Ironclad',2),('Cruiser',4),('Escort',8)]:
                typ,definition,_,old=modules[kind]
                for i in range(count):
                    version='' if legacy else f'version_name = "Leviathan {kind}"'
                    equipment=old if legacy else typ
                    ship_name=ship_names['eastern' if fleet.startswith('eastern') else 'atlantic'][kind][i]
                    ships.append(f'ship = {{ name = "HMS {ship_name}" definition = {definition} start_experience_factor = 0.25 equipment = {{ {equipment} = {{ amount = 1 owner = A02 {version} }} }} }}')
            suffix='_legacy' if legacy else ''
            write(f'history/units/BLV_campaign_{fleet}{suffix}.txt',f'units = {{ fleet = {{ name = "Leviathan {fleet.title()} Fleet" naval_base = {port} task_force = {{ name = "{fleet.title()} Squadron" location = {port}\n'+'\n'.join(ships)+'\n} } }')
    fx('initialize_fleet','''if = { limit = { BLV_is_britain = yes NOT = { has_country_flag = BLV_fleet_initialized } 696 = { is_owned_by = A02 is_controlled_by = A02 } }
 set_country_flag = BLV_fleet_initialized
 if = { limit = { has_dlc = "Man the Guns" }
'''+'set_technology = { early_ship_hull_heavy = 1 basic_heavy_battery = 1 }\n'+variants+'''
  load_oob = BLV_campaign_atlantic
  if = { limit = { 1021 = { is_owned_by = A02 is_controlled_by = A02 } } load_oob = BLV_campaign_eastern } else = { load_oob = BLV_campaign_eastern_reserve }
 } else = {
  load_oob = BLV_campaign_atlantic_legacy
  if = { limit = { 1021 = { is_owned_by = A02 is_controlled_by = A02 } } load_oob = BLV_campaign_eastern_legacy } else = { load_oob = BLV_campaign_eastern_reserve_legacy }
 }
 add_fuel = 100000
}''')
    write('history/units/BLV_campaign_guard.txt','division_template = { name = "Leviathan Marine Guard" regiments = { marine = { x = 0 y = 0 } marine = { x = 0 y = 1 } marine = { x = 0 y = 2 } } }\nunits = { division = { name = "Leviathan Marine Guard" location = 13010 division_template = "Leviathan Marine Guard" start_experience_factor = 0.20 start_equipment_factor = 0.75 } }')

def main():
    opening_and_politics();economy_and_finance();fleet_and_army();empire_and_pacific();science_and_arctic();spirits();mechanics();diplomatic_events();timed_projects();decisions();naval_oobs()
    import sys
    from british_story_links import configure, sync
    icon_groups={
      'neutrality_focus':('crown','royal_secretariat','loyal_governors','imperial_prerogative','commission'),
      'intelligence_exchange':('ungudja','song_records','scientific_cargo','archive'),
      'construct_naval_dockyard':('bermuda_dock','singapore_docks','nz_ports'),
      'navy_battleship':('battle_line','naval_state'),
      'navy_cruiser':('cruiser_routes','convoy_service','fleet_register'),
      'improve_relations':('batavia_oil','philippine_mission','japanese_note','russian_note','malta_license','dominion_charters','australia_sovereignty'),
      'demand_territory':('reconquest','war_plans','colonial_red_line'),
      'defence':('garrison_audit','rotation','field_hospitals'),
      'construct_mil_factory':('ordnance',),
    }
    for icon,ids in icon_groups.items():
        for row in FOCUSES:
            if row['id'][4:] in ids:row['script']=re.sub(r'icon = \w+',f'icon = GFX_goal_generic_{icon}',row['script'],count=1)
    legacy=ROOT/'common/national_focus/WTN_BRI_focus.txt'
    if legacy.exists():
        text=legacy.read_text(encoding='utf-8-sig')
        text=re.sub(r'country = \{ factor = 0(?: modifier = \{ add = 100 tag = [A-Z0-9]+ \})* \}','country = { factor = 0 }',text,count=1)
        legacy.write_text(text,encoding='utf-8')
    loc('BLV_research','Исследования Адмиралтейства','Admiralty Research')
    loc('BLV_imperial_government','Правительство Левиафана','Government of the Leviathan')
    loc('BLV_imperial_government_desc','Запасы станций: [?BLV_reserve|0]/100\\nСвязность империи: [?BLV_cohesion|0]/100\\n\\nВлияние — Адмиралтейство: [?BLV_admiralty|0], корона: [?BLV_crown|0], делегаты: [?BLV_delegates|0]. Для выбора пути нужно 4 пункта.\\n\\nНаука: [?SEN_science|0], готовность экспедиций: [?SEN_readiness|0], охрана: [?SEN_security|0], воздействие Песни: [?SEN_exposure|0].','Station reserves: [?BLV_reserve|0]/100\\nImperial cohesion: [?BLV_cohesion|0]/100\\n\\nInfluence — Admiralty: [?BLV_admiralty|0], Crown: [?BLV_crown|0], delegates: [?BLV_delegates|0]. A political path needs 4 points.\\n\\nScience: [?SEN_science|0], expedition readiness: [?SEN_readiness|0], security: [?SEN_security|0], Song exposure: [?SEN_exposure|0].')
    for key,ru,en in [
      ('BLV_council_tt','Откроется спор о власти на 180 дней. Влияние групп видно в решениях.','Opens a 180-day constitutional debate; bloc influence is shown in decisions.'),
      ('BLV_arctic_tt','Откроется шестидесятидневный проект раскопок с 1898 года. Потеря Гренландии отменяет проект.','Opens a 60-day excavation project from 1898; losing Greenland cancels it.'),
      ('BLV_prototype_tt','Откроется отдельный проект на 90 дней. Доступ к артефакту и Тесле проверяется повторно.','Opens a separate 90-day project; artifact and Tesla access are rechecked.'),
      ('BLV_station_tt','Откроется опытный проект береговой станции с 1901 года. Британские острова автоматически не передаются.','Opens an experimental coastal-station project from 1901; the British Isles are not automatically transferred.')]:loc(key,ru,en)
    configure(sys.modules[__name__])
    write('common/national_focus/BLV_campaign.txt','focus_tree = { id = BLV_campaign country = { factor = 0 modifier = { add = 200 tag = A02 } } default = no continuous_focus_position = { x = 100 y = 2500 }\n'+'\n'.join(row['script'] for row in FOCUSES)+'\n}')
    write('common/ideas/BLV_campaign.txt','ideas = { country = {\n'+'\n'.join(IDEAS)+'\n} }')
    write('common/scripted_effects/BLV_campaign.txt','\n\n'.join(FX))
    write('common/scripted_triggers/BLV_campaign.txt','\n'.join(TR))
    write('events/BLV_campaign.txt','\n\n'.join(EVENTS))
    write('common/decisions/BLV_campaign.txt','BLV_imperial_government = {\n'+'\n'.join(DEC)+'\n}')
    write('common/decisions/categories/BLV_campaign.txt','BLV_imperial_government = { icon = generic_political_discourse visible = { tag = A02 has_country_flag = BLV_initialized } }')
    write('common/on_actions/BLV_campaign.txt','on_actions = { on_startup = { effect = { A02 = { BLV_initialize = yes BLV_custody = yes } } } on_daily = { effect = { if = { limit = { tag = A02 } BLV_custody = yes BLV_refresh = yes } } } on_monthly = { effect = { if = { limit = { tag = A02 } BLV_monthly = yes } } } }')
    for lang,entries in LOC.items():write(f'localisation/{lang}/BLV_campaign_l_{lang}.yml','l_'+lang+':\n'+'\n'.join(f' {k}:0 "{v.replace(chr(34),chr(39))}"' for k,v in entries.items()),True)
    write('tools/british_campaign_manifest.json',json.dumps(dict(focuses=[{k:v for k,v in f.items() if k!='script'} for f in FOCUSES],events=len(EVENTS)-1,ideas=len(IDEAS),decisions=len(DEC),starting_ships=28),ensure_ascii=False,indent=2))
    sync()
    from focus_shapes import apply as apply_shapes
    apply_shapes()
    print(f'Built British campaign: {len(FOCUSES)} focuses, {len(EVENTS)-1} events, {len(IDEAS)} spirits, {len(DEC)} decisions and 28 starting ships.')

if __name__=='__main__':main()
