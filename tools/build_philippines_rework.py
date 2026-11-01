"""Assemble the Philippine campaign from the four authored focus modules.

Only A10 focus localisation keys are updated in the existing combined files.
Supporting gameplay scripts are ordinary, independently editable mod sources.
"""
from pathlib import Path
import json, re

R = Path(__file__).resolve().parents[1]
F = []

def focus(id, ru, en, x, y, parents, reward, desc_ru, desc_en, cost=4,
          icon='GFX_goal_generic_political_reform', available='', exclusive=(), ai=3, bypass=''):
    F.append(dict(id=id, name_ru=ru, name_en=en, desc_ru=desc_ru, desc_en=desc_en,
                  x=x, y=y, prerequisites=[[p] if isinstance(p,str) else p for p in parents],
                  reward=reward, cost=cost, icon=icon, available=available,
                  mutually_exclusive=list(exclusive), ai=ai, bypass=bypass))

focus('A10_island_congress','Конгресс в Кавите','The Cavite Congress',25,0,[],
      'A10R_initialize = yes add_political_power = 60 country_event = { id = A10R_congress.1 days = 1 }',
      'Манила потеряна, но делегаты островов продолжают прибывать в Кавите. Временный конгресс должен решить, кому подчиняются казна, порты и республиканские отряды.',
      'Manila has fallen, but island delegates still reach Cavite. The provisional congress must settle who commands the treasury, the ports and the republican detachments.',cost=1)
focus('A10R_provincial_rolls','Мандаты островных советов','Credentials of the Island Councils',22,1,['A10_island_congress'],
      'add_to_variable = { A10R_cohesion = 8 } add_stability = 0.03 A10R_refresh = yes',
      'Не каждый человек с печатью представляет свой остров. Проверка мандатов даст общему собранию опору в муниципалитетах и деревнях.',
      'A seal alone does not confer a mandate. Verifying credentials will root the assembly in the towns and villages.',cost=3)
focus('A10R_emergency_council','Казна правительства в изгнании','Treasury of the Exiled Government',28,1,['A10_island_congress'],
      'add_political_power = 50 add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 300 producer = A10 }',
      'Корабельные расписки и пожертвования эмигрантов нужно свести в одну кассовую книгу. Даже осаждённое правительство обязано платить своим служащим.',
      'Shipping receipts and emigrant donations must enter a single ledger. Even a government under siege must pay its clerks.',cost=3)
focus('A10_confederation','Договор свободных республик','Compact of Free Republics',15,3,['A10_island_congress'],
      'set_country_flag = A10_confederal_path remove_ideas = A10_separatism add_ideas = A10R_provisional_compact A10_release_PVI = yes A10_release_PSM = yes add_to_variable = { A10R_cohesion = 10 } A10R_refresh = yes',
      'Висайи и Самар сохранят свои собрания и казну. Взамен они признают общий конгресс, обязуются оборонять соседей и направлять делегатов в Кавите.',
      'The Visayas and Samar shall retain their assemblies and treasuries in return for a common congress, mutual defence and delegates to Cavite.',cost=3,exclusive=['A10W_oath','A10M_coup'],ai=20)
focus('A10_visayan_compact','Хартии Себу и Паная','Charters of Cebu and Panay',15,4,['A10_confederation'],
      'A10_release_PCB = yes A10_release_PPN = yes add_to_variable = { A10R_cohesion = 5 } add_stability = 0.03 A10R_refresh = yes',
      'Себуанские купцы требуют открытого судоходства, Панай — защиты земледельцев. Отдельные хартии объединят эти требования в обязательства республик.',
      'Cebu demands open shipping and Panay protection for its farmers. Separate charters shall bind these demands into republican obligations.',cost=3)
focus('A10_mindanao_compact','Две республики Минданао','The Two Mindanao Republics',15,5,['A10_visayan_compact'],
      'A10_release_PMD = yes A10_release_PNM = yes add_political_power = 35 country_event = { id = A10R_congress.2 days = 1 }',
      'Север и юг Минданао не согласны уступать власть далёкой столице. Гарантии местного права и вера в общую оборону могут привести их за один стол.',
      'Northern and southern Mindanao will not surrender authority to a distant capital. Local legal guarantees and mutual defence can bring them to one table.',cost=3)
focus('A10_united_command','Общий штаб республик','The Republican Joint Staff',15,6,['A10_mindanao_compact'],
      'add_ideas = A10_common_army set_country_flag = A10R_war_ready add_war_support = 0.07 add_to_variable = { A10R_cohesion = 5 } A10R_refresh = yes',
      'Командиры сохранят свои знамёна, но морские переправы, склады и распоряжения штаба станут общими. Спор о старшинстве не должен решать исход боя.',
      'Commanders may keep their banners, but crossings, depots and staff orders must be shared. Seniority disputes must not decide a battle.',cost=3,icon='GFX_goal_generic_army_doctrines')
focus('A10R_common_treasury','Взносы вместо поборов','Contributions Instead of Exactions',15,7,['A10_united_command'],
      'add_ideas = A10R_common_treasury_spirit add_political_power = 40 add_to_variable = { A10R_cohesion = 5 } A10R_refresh = yes',
      'Общий бюджет получит заранее согласованные взносы, а не случайные реквизиции. Республикам придётся отвечать за обещанное перед остальными островами.',
      'Agreed contributions must replace arbitrary requisitions. Each republic shall account to the other islands for its promises.')
focus('A10R_republican_court','Суд межостровных споров','Court of Inter-Island Arbitration',13,8,['A10R_common_treasury'],
      'add_ideas = A10R_arbitration add_to_variable = { A10R_cohesion = 8 } A10R_refresh = yes',
      'Таможенный спор или задержанный пароход больше не будут поводом для вооружённого столкновения. Решение общего суда обязует даже влиятельные семьи.',
      'A customs dispute or detained steamer must cease to be a cause for armed confrontation. The common court shall bind even the powerful families.')
focus('A10R_language_charters','Языки общего дома','Languages of the Common House',17,8,['A10R_common_treasury'],
      'add_stability = 0.05 add_to_variable = { A10R_cohesion = 8 } set_country_flag = A10R_languages_guaranteed A10R_refresh = yes',
      'Петиции на тагальском, себуанском и других островных языках получат одинаковую силу. Переводчики соединят делегатов лучше, чем запрет родной речи.',
      'Petitions in Tagalog, Cebuano and the other island languages shall have equal standing. Interpreters can unite delegates better than prohibitions.')
focus('A10R_tenant_guarantees','Договор с арендаторами','A Covenant with the Tenants',13,9,['A10R_republican_court'],
      'add_ideas = A10R_tenant_rights add_to_variable = { A10R_cohesion = 6 } country_event = { id = A10R_congress.3 days = 1 } A10R_refresh = yes',
      'Сельские отряды защищают не одни флаги. Ограничение долговых взысканий и письменные договоры аренды дадут семьям причину доверять республикам.',
      'The village detachments fight for more than flags. Limits on debt seizures and written leases shall give their families reason to trust the republics.')
focus('A10R_civilian_inspectors','Гражданские комиссары при штабе','Civilian Commissioners to the Staff',17,9,['A10R_language_charters'],
      'add_political_power = 50 add_to_variable = { A10R_cohesion = 6 } add_stability = 0.03 A10R_refresh = yes',
      'Общий штаб отвечает перед конгрессом. Комиссары проверят ведомости снабжения и жалобы деревень, не присваивая себе командование полками.',
      'The joint staff answers to congress. Commissioners shall inspect supply rolls and village complaints without assuming command of regiments.')
focus('A10R_assembly_of_islands','Собрание всех островов','Assembly of All the Islands',15,10,['A10R_tenant_guarantees','A10R_civilian_inspectors'],
      'add_to_variable = { A10R_cohesion = 10 } add_stability = 0.05 set_country_flag = A10R_constitutional_debate A10R_refresh = yes country_event = { id = A10R_congress.4 days = 1 }',
      'Временное соглашение выдержало первые испытания. Теперь делегаты спорят, достаточно ли договора республик или народу нужен общий федеральный закон.',
      'The provisional compact has survived its first trials. Delegates now dispute whether a treaty of republics is enough or the people require federal law.')
focus('A10R_republics_forever','Союз равных республик','Union of Equal Republics',13,12,['A10R_assembly_of_islands'],
      'remove_ideas = A10R_provisional_compact add_ideas = A10R_confederal_covenant set_country_flag = A10R_permanent_confederation A10R_confederal_government = yes add_to_variable = { A10R_cohesion = 10 } A10R_refresh = yes',
      'Республики сохранят суверенные собрания, общую оборону и право голоса в союзном бюджете. Доверие между островами станет основой государства.',
      'The republics shall retain sovereign assemblies, common defence and a voice in the union budget. Trust between islands shall sustain the state.',exclusive=['A10R_federal_convention'],ai=15)
focus('A10R_rotating_presidency','Председательство по очереди','A Rotating Presidency',11,13,['A10R_republics_forever'],
      'add_political_power = 75 add_stability = 0.04 add_to_variable = { A10R_cohesion = 5 } A10R_refresh = yes',
      'Союзный председатель не будет принадлежать одному острову навечно. Очерёдность председательства даст малым республикам весомый голос.',
      'No island shall hold the union presidency forever. Rotation shall give the smaller republics an effective voice.')
focus('A10R_customs_union','Одна таможенная граница','A Single Customs Frontier',13,13,['A10R_republics_forever'],
      'add_ideas = A10R_customs_union_spirit add_to_variable = { A10R_cohesion = 5 } A10R_refresh = yes',
      'Между союзными портами исчезнут внутренние пошлины. Доходы внешней таможни будут распределяться по открытой ведомости, доступной каждой республике.',
      'Internal duties shall disappear between union ports. External customs revenues shall be divided through a ledger open to every republic.',icon='GFX_goal_generic_trade')
focus('A10R_republican_compact_end','Солнце над девятью республиками','Sun over the Nine Republics',12,15,['A10R_rotating_presidency','A10R_customs_union'],
      'add_ideas = A10R_republican_solidarity add_stability = 0.05 add_to_variable = { A10R_cohesion = 10 } A10R_refresh = yes country_event = { id = A10R_congress.8 days = 1 }',
      'Общая присяга не требует одинаковых законов на каждом острове. Союз обретает постоянные учреждения, сохраняя множество местных голосов.',
      'A common oath need not impose identical laws on every island. The union gains enduring institutions while preserving its many local voices.',available='check_variable = { A10R_cohesion > 49 }')
focus('A10R_federal_convention','Федеральный конвент','The Federal Convention',17,12,['A10R_assembly_of_islands'],
      'set_country_flag = A10R_federal_transition add_to_variable = { A10R_cohesion = -8 } country_event = { id = A10R_congress.5 days = 1 } A10R_refresh = yes',
      'Сторонники федерации предлагают общее гражданство и ответственное правительство. Ни одна республика не войдёт в новый строй без собственного согласия.',
      'Federalists propose common citizenship and responsible government. No republic shall enter the new order without its own consent.',exclusive=['A10R_republics_forever'],ai=2)
focus('A10R_bill_of_rights','Неприкосновенные права островов','An Entrenched Bill of Island Rights',17,13,['A10R_federal_convention'],
      'add_ideas = A10R_bill_of_rights_spirit add_to_variable = { A10R_cohesion = 8 } set_country_flag = A10R_federal_guarantees A10R_refresh = yes',
      'Местные языки, избираемые советы и свобода вероисповедания должны быть защищены от будущего большинства. Только так федеральный проект заслужит доверие.',
      'Local languages, elected councils and freedom of worship must be protected against future majorities. Only then can the federal project earn trust.')
focus('A10_federation','Провозгласить федерацию','Proclaim the Federation',17,14,['A10R_bill_of_rights'],
      'set_country_flag = A10_federal_path set_cosmetic_tag = A10_FED remove_ideas = PZ_philippine_confederation remove_ideas = A10R_provisional_compact add_ideas = A10_federal_administration add_stability = 0.05 country_event = { id = A10R_congress.6 days = 1 }',
      'Делегаты принимают федеральную конституцию. Присоединение республик остаётся предметом отдельных ратификаций; чужое молчание не будет считаться согласием.',
      'Delegates adopt a federal constitution. The accession of each republic remains subject to a separate ratification; silence shall never count as consent.',
      available='check_variable = { A10R_cohesion > 39 } OR = { check_variable = { A10R_federal_votes > 2 } NOT = { any_subject_country = { A10R_member_trigger = yes NOT = { A10R_republic_has_consented = yes } } } }')
focus('A10_gendarmerie','Федеральная служба порядка','A Federal Constabulary',16,15,['A10_federation'],
      'A10_federal_progress = yes add_manpower = 3000 add_to_variable = { A10R_cohesion = -3 } A10R_refresh = yes',
      'Служба порядка получит общий устав и запрет коллективных наказаний. Ей предстоит защищать дороги и суды, а не подменять собой местные советы.',
      'A common statute shall prohibit collective punishment. The constabulary must protect roads and courts without replacing local councils.')
focus('A10_local_administration','Выборные провинциальные советы','Elected Provincial Councils',18,15,['A10_federation'],
      'A10_federal_progress = yes add_stability = 0.05 add_to_variable = { A10R_cohesion = 5 } A10R_refresh = yes',
      'Федеральные чиновники будут работать вместе с избранными советами. Право распоряжаться школами и дорогами останется близко к тем, кто ими пользуется.',
      'Federal officials shall work alongside elected councils. Schools and roads must remain close to the people who use them.')
focus('A10_equal_citizenship','Единое гражданство','Equal Citizenship',17,16,['A10_gendarmerie','A10_local_administration'],
      'A10_federal_progress = yes set_country_flag = A10R_equal_rights add_ideas = A10R_federal_citizenship add_political_power = 50',
      'Гражданин одной провинции получит те же права в другой. Общий паспорт и равный доступ к государственной службе завершат спор о людях первого и второго разряда.',
      'A citizen of one province shall have equal rights in another. A common passport and equal access to public service will end distinctions of rank between islanders.')
focus('A10R_federal_parliament','Первый федеральный парламент','The First Federal Parliament',17,18,['A10_equal_citizenship'],
      'A10R_civilian_government = yes add_ideas = A10R_responsible_cabinet add_stability = 0.05 country_event = { id = A10R_congress.9 days = 1 }',
      'Палата населения и палата островов начнут совместную работу. Правительство будет отвечать перед избранными представителями, а армия — перед законом.',
      'A population chamber and an island chamber shall begin their work. The cabinet will answer to elected representatives and the army to the law.',available='has_war = no')
focus('A10R_civilian_commonwealth','Гражданская республика островов','A Civil Commonwealth of Islands',17,20,['A10R_federal_parliament'],
      'add_research_slot = 1 add_to_variable = { A10R_cohesion = 10 } A10R_refresh = yes',
      'Университеты, провинциальные советы и парламент станут опорой общего государства. Власть, выросшая из войны, учится жить доверием граждан.',
      'Universities, provincial councils and parliament shall sustain the common state. Authority born in war learns to live by the trust of its citizens.',icon='GFX_goal_generic_scientific_exchange',cost=6)
focus('A10_strike_japan','Вернуть северные гавани','Recover the Northern Harbours',28,21,['A10_landing_plans'],
      'declare_war_on = { target = A03 type = annex_everything }',
      'Пока императорские корабли связаны на юге, появляется возможность вернуть гавани Лусона. Штаб готовит переправы, а правительство принимает ответственность за войну.',
      'With imperial ships committed in the south, an opportunity opens to recover the Luzon harbours. The staff prepares crossings while the government accepts responsibility for war.',icon='GFX_goal_generic_major_war',cost=3,
      available='country_exists = A03 is_subject = no A03 = { has_war_with = A01 } has_country_flag = A10R_war_ready NOT = { has_war_with = A03 } NOT = { has_country_flag = A10_archipelago_peace_signed } NOT = { has_country_flag = A10_manila_peace_signed }',
      bypass='OR = { has_war_with = A03 has_country_flag = A10_archipelago_peace_signed has_country_flag = A10_manila_peace_signed NOT = { country_exists = A03 } }')
focus('A10R_luzon_relief','Комитет помощи Лусону','The Luzon Relief Committee',11,7,['A10_united_command'],
      'add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 600 producer = A10 } add_manpower = 1500 add_war_support = 0.03',
      'Лодочники, связные и семьи беженцев знают побережье лучше любого штаба. Комитет свяжет местные отряды с республиканскими складами.',
      'Boatmen, couriers and refugee families know the coast better than any staff. Their committee shall connect local detachments with republican depots.',icon='GFX_goal_generic_allies_build_infantry')
focus('A10_luzon_charter','Хартия Северного Лусона','Charter of Northern Luzon',11,9,['A10R_luzon_relief'],
      'if = { limit = { NOT = { has_country_flag = A10_federal_path } } A10_release_PNL = yes } else = { A10_federal_progress = yes } add_to_variable = { A10R_cohesion = 5 } A10R_refresh = yes',
      'Освобождение не даёт Кавите права назначать северу хозяев. Местное собрание получит республиканскую хартию и место среди равных союзников.',
      'Liberation does not entitle Cavite to impose masters on the north. A local assembly shall receive a republican charter and a place among equal allies.',
      available='623 = { OR = { AND = { is_owned_by = A10 is_controlled_by = A10 } AND = { owner = { tag = PNL is_subject_of = A10 } is_controlled_by = PNL } } }',bypass='PNL = { is_subject_of = A10 }')
focus('A10_capital_charters','Манила и Батаан за общим столом','Manila and Bataan at the Common Table',11,11,['A10_luzon_charter'],
      'if = { limit = { NOT = { has_country_flag = A10_federal_path } } A10_release_PML = yes A10_release_PBT = yes } else = { A10_federal_progress = yes } add_stability = 0.05',
      'Манильский порт и батареи Батаана должны охранять весь архипелаг. Их отдельные хартии не позволят столице поглотить голоса остальных республик.',
      'Manila harbour and the Bataan batteries must guard the whole archipelago. Separate charters shall prevent the capital from swallowing the voices of the other republics.',
      available='327 = { OR = { AND = { is_owned_by = A10 is_controlled_by = A10 } AND = { owner = { tag = PML is_subject_of = A10 } is_controlled_by = PML } } } 1027 = { OR = { AND = { is_owned_by = A10 is_controlled_by = A10 } AND = { owner = { tag = PBT is_subject_of = A10 } is_controlled_by = PBT } } }')
focus('A10R_war_accounts','Счёт войны','Accounts of the War',22,21,['A10_island_congress'],
      'add_ideas = A10R_reconstruction add_political_power = 50 country_event = { id = A10R_congress.7 days = 1 }',
      'После последних выстрелов остаются сожжённые склады, вдовы и неоплаченные расписки. Комиссия восстановления начнёт с открытого подсчёта потерь.',
      'Burned warehouses, bereaved families and unpaid receipts remain after the guns fall silent. Reconstruction shall begin with an open accounting of the losses.',
      available='has_war = no OR = { has_country_flag = A10_archipelago_peace_signed has_country_flag = A10_manila_peace_signed has_country_flag = A10R_defensive_armistice NOT = { country_exists = A03 } }',icon='GFX_goal_generic_construct_civ_factory')
focus('A10R_veterans_land','Земля и пенсии ветеранам','Land and Pensions for Veterans',20,22,['A10R_war_accounts'],
      'add_stability = 0.06 add_war_support = -0.03 add_to_variable = { A10R_cohesion = 6 } A10R_refresh = yes',
      'Вернувшимся солдатам нужны не новые походы, а кров, работа и признание ран. Земельные комиссии разберут требования без изгнания крестьянских семей.',
      'Returning soldiers need shelter, work and care for their wounds. Land commissions shall examine their claims without expelling farming families.')
focus('A10_federal_reconstruction','Восстановить островные гавани','Rebuild the Island Harbours',24,22,['A10R_war_accounts'],
      'A10R_rebuild_harbour = yes A10_federal_progress = yes add_political_power = 25',
      'Мир не соединит острова, если пароходы не могут войти в гавань. Общие средства пойдут на причалы, карантинные станции и ремонтные мастерские.',
      'Peace cannot reconnect islands whose harbours remain unusable. Common funds shall restore quays, quarantine stations and repair workshops.',icon='GFX_goal_generic_construct_naval_dockyard')
focus('A10R_peace_generation','Поколение мира','A Generation of Peace',22,24,['A10R_veterans_land','A10_federal_reconstruction'],
      'remove_ideas = A10R_reconstruction add_ideas = A10R_island_recovery add_stability = 0.05 add_to_variable = { A10R_cohesion = 8 } A10R_refresh = yes',
      'Дети, выросшие среди гарнизонов и беженцев, должны узнать другую жизнь. Острова направят силы на школы, торговлю и возвращение разлучённых семей.',
      'Children raised among garrisons and refugees must learn another life. The islands shall turn to schools, trade and the reunion of divided families.',cost=6)

def esc(s):
    return s.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')

def generate():
    specs = list(F)
    for module in ['a10d_focuses.json','a10w_focuses.json','a10m_focuses.json']:
        specs.extend(json.loads((R/'tools'/module).read_text(encoding='utf-8-sig')))
    ids = {f['id'] for f in specs}
    assert len(ids)==len(specs)
    for f in specs:
        if f.get('icon') == 'GFX_goal_generic_political_reform':
            f['icon'] = 'GFX_goal_generic_national_unity'
        if f['id'] in ['A10W_oath','A10M_coup']:
            f['mutually_exclusive']=[x for x in ['A10_confederation','A10W_oath','A10M_coup'] if x!=f['id']]
        for group in f.get('prerequisites',[]):
            assert set(group)<=ids, (f['id'],group)
    lines=['# Generated by tools/build_philippines_rework.py from the authored modules.',
           'focus_tree = {',' id = A10_philippines',
           ' country = { factor = 0 modifier = { add = 100 tag = A10 } }',
           ' default = no',' continuous_focus_position = { x = 500 y = 2100 }']
    for f in specs:
        lines.extend([' focus = {',f"  id = {f['id']}",f"  icon = {f.get('icon','GFX_goal_generic_political_reform')}",
                      f"  x = {f['x']} y = {f['y']} cost = {f.get('cost',4)}"])
        for group in f.get('prerequisites',[]):
            lines.append('  prerequisite = { '+' '.join('focus = '+p for p in group)+' }')
        if f.get('mutually_exclusive'):
            lines.append('  mutually_exclusive = { '+' '.join('focus = '+p for p in f['mutually_exclusive'])+' }')
        if f.get('available'):lines.append('  available = { '+f['available']+' }')
        if f.get('bypass'):lines.append('  bypass = { '+f['bypass']+' }')
        historical = f['id']=='A10_confederation'
        lines.append('  ai_will_do = { factor = '+str(f.get('ai',3))+(' modifier = { factor = 100 is_historical_focus_on = yes }' if historical else '')+' }')
        lines.extend(['  completion_reward = { '+f['reward']+' }',' }'])
    lines.append('}')
    (R/'common/national_focus/a10_focus.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    for lang,code in [('russian','ru'),('english','en')]:
        new={}
        legacy=R/f'localisation/{lang}/1896_focus_l_{lang}.yml'
        text=legacy.read_text(encoding='utf-8-sig')
        for f in specs:
            if f['id'].startswith('A10M_'):
                continue  # This module authors its focus localisation alongside its events.
            for key,val in [(f['id'],f['name_'+code]),(f['id']+'_desc',f['desc_'+code])]:
                entry=f' {key}:0 "{esc(val)}"'
                pattern=r'^ '+re.escape(key)+r':\d+ .*?$'
                if re.search(pattern,text,re.M):text=re.sub(pattern,lambda m:entry,text,flags=re.M)
                else:new[key]=val
        legacy.write_text(text,encoding='utf-8-sig',newline='\n')
        out='l_'+lang+':\n'+''.join(f' {k}:0 "{esc(v)}"\n' for k,v in new.items())
        (R/f'localisation/{lang}/A10R_campaign_focus_l_{lang}.yml').write_text(out,encoding='utf-8-sig')
    (R/'tools/philippines_focus_manifest.json').write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    from focus_shapes import apply as apply_shapes
    apply_shapes()
    print(f'Assembled {len(specs)} Philippine focuses; legacy localisation updated without duplicate keys.')

if __name__=='__main__':generate()
