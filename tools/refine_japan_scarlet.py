"""Apply the author's second industrial outline to the installed Scarlet branch."""
from pathlib import Path
import re
from rework_japan_industry import R, LOC, loc, node, write
from clarify_japan_branches import blocks
from add_canon_countries import parse, value

def get(n,k,d=None):return next((v for key,o,v in n if key==k),d)

def main():
    p='common/national_focus/a03_focus.txt';s=(R/p).read_text(encoding='utf-8-sig')
    if 'id = JPI_electrical_bureau' in s:
        print('Second outline already installed.');return
    names={
        'JPX_sea':('Курс императорского адмиралтейства','Course of the Imperial Admiralty'),
        'JPI_closed_ports':('Опора на собственные силы','Reliance on Our Own Strength'),
        'JPI_japanese_terms':('Диктовать условия торговли','Dictate the Terms of Trade'),
        'JPI_raw_register':('Инвентаризация ресурсов империи','Inventory the Empire’s Resources'),
        'JPI_unsigned_contracts':('Тайные торговые соглашения','Secret Trade Agreements'),
        'JPI_kyushu_coal':('Угольные бассейны Кюсю','Kyushu Coalfields'),
        'JPI_oil_hunger':('Чёрное золото Юга','Black Gold of the South'),
        'JPI_proxy_machines':('Закупки через третьих лиц','Purchases through Third Parties'),
        'JPI_copied_samples':('Японские образцы машин','Japanese Machine Designs'),
        'JPI_standard_node':('Стандартизация производства','Standardise Production'),
        'JPI_kure_yards':('Расширение верфей Курэ','Expand the Kure Shipyards'),
        'JPI_airship_hangars':('Небесные верфи','Sky Shipyards'),
        'JPI_quiet_coast':('Береговые электрические станции','Coastal Electrical Stations'),
        'JPI_southern_push':('Операция «Нанъё»','Operation Nanyō'),
    }
    for key,(ru,en) in names.items(): loc(key,ru,en)
    descriptions={
        'JPX_sea':('Адмиралтейство требует подготовки к южному походу. После Исхода промышленная самостоятельность стала вопросом выживания: известные принципы электрической защиты и воздухоплавания ещё предстоит воплотить в японских образцах.','The Admiralty demands preparations for a southern expedition. After the Exodus, industrial independence is a matter of survival: known principles of electrical protection and aeronautics still need working Japanese prototypes.'),
        'JPI_closed_ports':('Императорские заказы останутся в японских мастерских. Военные заводы строятся на 10% быстрее, но предельная эффективность производства снижена на 10%. Новые договоры ВТП запрещены; прежние долги остаются.','Imperial orders stay in Japanese workshops. Military factories are built 10% faster, but maximum production efficiency falls by 10%. New WTC contracts are prohibited; existing debts remain.'),
        'JPI_japanese_terms':('Чужие знания принимаются на японских условиях. Промышленные исследования ускорены на 10%, но потребительские расходы и уязвимость при нехватке импортного сырья растут. Палата видит закупочные ведомости.','Foreign knowledge is accepted on Japanese terms. Industrial research is 10% faster, but consumer costs and penalties from resource shortages increase. The Chamber sees our procurement lists.'),
        'JPI_kyushu_coal':('Паровые машины остаются опорой эскадры. Разработка бассейнов Кюсю ускоряет строительство верфей на 15%, но обслуживание угольной сети увеличивает расход морского снабжения на 10%.','Steam remains the squadron’s foundation. Developing Kyushu coalfields speeds dockyard construction by 15%, but maintaining the coal network increases naval supply consumption by 10%.'),
        'JPI_oil_hunger':('Флот пока идёт на угле, но будущие двигатели потребуют нефтепереработки. Даём два 100%-ных бонуса исследованиям переработки; переоснащение снижает выпуск военных заводов на 10% на 180 дней. Срок южного похода сокращается на 30 дней.','The fleet still burns coal, but future engines will need oil refining. Gain two 100% refining research bonuses; retooling reduces military factory output by 10% for 180 days. The southern expedition is brought forward by 30 days.'),
        'JPI_kure_yards':('Расширяем существующие стапели Курэ и готовим тяжёлую эскадру. Выпуск кораблей растёт на 10%, но изъятие специалистов повышает производственную стоимость авиации на 10%. Небесные верфи придётся оставить без средств.','Expand Kure’s existing slipways and prepare a heavy squadron. Ship output rises by 10%, but transferring specialists increases aircraft production cost by 10%. The sky shipyards must go unfunded.'),
        'JPI_airship_hangars':('Известные принципы воздухоплавания воплотятся в собственной серии из 24 дирижаблей. Их производственная стоимость снижается на 15%; выпуск кораблей падает на 10%, тяжёлая эскадра подкрепления не строится.','Apply known aeronautical principles to a domestic series of 24 airships. Their production cost falls by 15%; ship output falls by 10%, and the heavy reinforcement squadron is not built.'),
        'JPI_quiet_coast':('После исследований, изготовления образца и береговых испытаний переносные станции можно грузить на транспорты. Поле радиусом около 500 метров укроет первый плацдарм от Песни. Без станций сценарная высадка на Борнео невозможна.','After research, prototyping and coastal trials, portable stations can be loaded aboard transports. A field roughly 500 metres across in radius shields the first beachhead from the Song. The scripted Borneo landing requires these stations.'),
        'JPI_scarlet_sails':('В бухте собирается итог всей промышленной программы. Курэ даёт «Железные алые паруса», небесные верфи — «Алые небеса». Постоянные свойства и описание национального духа учитывают уголь, нефтяную ставку, закупки или собственные образцы; раскрытые заказы оставляют след.','The entire industrial programme comes together in the harbour. Kure creates Iron Scarlet Sails; sky shipyards create Scarlet Skies. The national spirit’s lasting properties and description reflect coal, the oil wager, purchases or domestic designs; exposed orders leave their mark.'),
        'JPI_southern_push':('Нанъё — южный поход императорского адмиралтейства. Испытанные электрические станции и готовая эскадра открывают путь к Борнео. Ультиматум будет предъявлен по истечении срока подготовки, либо сразу, если тот уже прошёл. Нефтяная программа сокращает действующий таймер ещё на 15 дней.','Nanyō is the Imperial Admiralty’s southern expedition. Tested electrical stations and a prepared squadron open the way to Borneo. The ultimatum is issued when preparations expire, or immediately if already overdue. The oil programme cuts another 15 days from an active countdown.'),
    }
    for key,(ru,en) in descriptions.items():loc(key+'_desc',ru,en)
    new=[]
    for _,_,b in blocks(s):
        fid=re.search(r'\bid\s*=\s*(\w+)',b)[1]
        y=int(re.search(r'\by\s*=\s*(\d+)',b)[1])
        if (fid.startswith('JPI_') and y>=7) or (not fid.startswith('JPI_') and y>=11):
            b=re.sub(r'\by\s*=\s*\d+',f'y = {y+3}',b,count=1)
        if fid=='JPI_quiet_coast':
            b=b.replace('prerequisite = { focus = JPI_kure_yards focus = JPI_airship_hangars }','prerequisite = { focus = JPI_coastal_trials }')
            b=b.replace('completion_reward = {','available = { has_country_flag = JPI_tesla_tested }\n  completion_reward = {',1)
        if fid=='JPI_oil_hunger':
            b=b.replace('add_ideas = JPI_oil_shortage','add_timed_idea = { idea = JPI_oil_shortage days = 180 } add_tech_bonus = { name = JPI_oil_hunger bonus = 1.0 uses = 2 category = synth_resources }')
        new.append(' '+b)
    new.append(node('electrical_bureau','Электротехническое бюро','Electrical Engineering Bureau',
        'Принцип глушителя уже известен. Японские инженеры должны рассчитать собственную установку, пригодную для качки и солёного воздуха. Это развитие технологий нашего изменённого мира, а не обычная электрификация.',
        'The suppression principle is known. Japanese engineers must design a unit that can withstand a rolling ship and salt air. This develops the technologies of our altered world, rather than ordinary electrification.',
        6,7,'JPI_kure_yards JPI_airship_hangars','set_country_flag = JPI_tesla_design add_tech_bonus = { name = JPI_electrical_bureau bonus = 0.5 uses = 1 category = industry }',cost=2))
    new.append(node('portable_prototype','Переносной опытный образец','Portable Prototype',
        'Лабораторная схема превращается в разборную вышку, генератор и изолированные кабели. Образец ещё нельзя доверять десантникам: сначала нужны испытания.',
        'The laboratory design becomes a collapsible tower, generator and insulated cables. The prototype must pass trials before it can be entrusted to landing troops.',
        6,8,'JPI_electrical_bureau','set_country_flag = JPI_tesla_prototype add_political_power = -25',cost=2))
    new.append(node('coastal_trials','Испытания на побережье','Coastal Trials',
        'Высаживаем испытательную команду, разворачиваем вышку с транспорта и проверяем защиту от Песни. Только подтверждённая устойчивость поля позволит заказать береговую серию.',
        'Land a test party, deploy the tower from a transport and test its protection against the Song. Only a stable field will justify ordering the coastal production series.',
        6,9,'JPI_portable_prototype','set_country_flag = JPI_tesla_tested navy_experience = 10',cost=2,icon='GFX_goal_unique_A03_southern_bases'))
    write(p,s[:s.index(' focus = {')]+'\n'.join(new)+'\n}\n')
    ideas_and_finale()
    p='common/ai_strategy_plans/A01_canonical.txt';s=(R/p).read_text(encoding='utf-8-sig')
    write(p,s.replace('JPI_kure_yards JPI_quiet_coast','JPI_kure_yards JPI_electrical_bureau JPI_portable_prototype JPI_coastal_trials JPI_quiet_coast'))
    # Update the eight event texts to the new terminology without changing their routes.
    substitutions={'Закрытые порты':'Опора на собственные силы','Уголь Кюсю':'Уголь бассейнов Кюсю','корабли Куре':'корабли Курэ','вышки для первого плацдарма':'испытанные электрические станции для первого плацдарма'}
    for index,lang in enumerate(['russian','english']):
        p=f'localisation/{lang}/1896_main_l_{lang}.yml';s=(R/p).read_text(encoding='utf-8-sig')
        for key,values in LOC.items():
            line=f' {key}:0 "{values[index]}"'
            if re.search(r'^ '+re.escape(key)+r':',s,re.M): s=re.sub(r'^ '+re.escape(key)+r':[^\n]*',lambda m:line,s,flags=re.M)
            else:s+='\n'+line
        if lang=='russian':
            lines=[]
            for line in s.splitlines():
                if line.startswith(' japan_industry.1.'):
                    for old,new in substitutions.items():line=line.replace(old,new)
                lines.append(line)
            s='\n'.join(lines)
            s=s.replace('собственные мастерские, но нефтяные цистерны пусты. Борнео нужен, чтобы продолжать поход.','собственные мастерские. Паровой флот ещё держится на угле, но будущая нефтяная программа требует месторождений Борнео.')
        else:
            s=s.replace('Closed ports provided our own workshops, but the oil tanks are empty. Borneo is needed to sustain the expedition.','Domestic workshops sustain a coal-fired fleet, while our future oil programme requires the fields of Borneo.')
        write(p,s+'\n')
    print('Refined 68-focus tree: 17 industrial focuses, prototype chain and eight final spirit variants.')

def ideas_and_finale():
    # Equipment modifiers use actual archetypes defined in the mod.
    aircraft=[]
    for p in (R/'common/units/equipment').glob('*.txt'):
        for fid,o,n in get(parse(p.read_text(encoding='utf-8-sig')),'equipments',[]):
            if isinstance(n,list) and get(n,'is_archetype')=='yes' and get(n,'interface_category')=='interface_category_air':aircraft.append(fid)
    assert {'airship_equipment','fighter_equipment'}<=set(aircraft)
    penalty='equipment_bonus = { '+' '.join(f'{fid} = {{ build_cost_ic = 0.10 instant = yes }}' for fid in sorted(set(aircraft)))+' }'
    base=[
        ('rough_industry','Самостоятельные мастерские','Independent Workshops','production_speed_arms_factory_factor = 0.10 production_factory_max_efficiency_factor = -0.10','',
         'Собственные заводы строятся быстро, но разнородное оборудование ограничивает эффективность.','Domestic factories grow quickly, but uneven machinery limits efficiency.'),
        ('selective_imports','Торговля на японских условиях','Trade on Japanese Terms','consumer_goods_factor = 0.03 production_lack_of_resource_penalty_factor = 0.15','research_bonus = { industry = 0.10 }',
         'Чужие знания ускоряют исследования. Импортная зависимость повышает цену снабжения и штраф при нехватке сырья; Палата видит списки заказов.','Foreign knowledge speeds research. Import dependence raises supply costs and resource shortage penalties; the Chamber sees our orders.'),
        ('coal_bunkers','Угольная программа Кюсю','Kyushu Coal Programme','production_speed_dockyard_factor = 0.15 naval_supply_consumption_factor = 0.10','',
         'Пароходы и новые верфи опираются на угольную сеть. Её обслуживание требует дополнительного морского снабжения.','Steamships and new yards depend on a coal network whose maintenance requires additional naval supplies.'),
        ('oil_shortage','Переоснащение нефтяной промышленности','Oil Industry Retooling','industrial_capacity_factory = -0.10','',
         'На 180 дней специалисты отвлечены от текущего выпуска к будущей нефтепереработке. Уголь остаётся топливной основой флота.','For 180 days, specialists are diverted from current output to future oil refining. Coal remains the fleet’s principal fuel.'),
        ('heavy_yards','Стапели Курэ','Kure Slipways','industrial_capacity_dockyard = 0.10',penalty,
         'Корабельные заказы получают лучших специалистов; производственная стоимость авиации повышена на 10%.','Shipbuilding receives our best specialists; aircraft production cost rises by 10%.'),
        ('airship_service','Небесные верфи','Sky Shipyards','industrial_capacity_dockyard = -0.10','equipment_bonus = { airship_equipment = { build_cost_ic = -0.15 instant = yes } airship_bomber_equipment = { build_cost_ic = -0.15 instant = yes } }',
         'Серийные эллинги снижают стоимость дирижаблей на 15%, отвлекая мощности от надводного флота.','Serial hangars reduce airship cost by 15%, diverting capacity from the surface fleet.'),
        ('portable_towers','Испытанные береговые станции','Tested Coastal Stations','amphibious_invasion = 0.10','',
         'Японский переносной образец прошёл береговые испытания. Электрическое поле прикрывает первый плацдарм от Песни.','The Japanese portable prototype has passed coastal trials. Its electrical field shields the first beachhead from the Song.'),
        ('exposed_orders','Раскрытые закупки','Exposed Procurement','naval_coordination = -0.05','',
         'Противник знает часть приготовлений. Эскадре приходится менять планы и способы связи.','The enemy knows some of our preparations. The squadron must change its plans and communications.'),
    ]
    text='ideas = { country = {\n'
    for name,ru,en,mod,extra,desc,endesc in base:
        key='JPI_'+name;loc(key,ru,en);loc(key+'_desc',desc,endesc)
        text+=f' {key} = {{ picture = jpc_fleet removal_cost = -1 modifier = {{ {mod} }} {extra} }}\n'
    result=''
    for branch,short in [('kyushu_coal','coal'),('oil_hunger','oil'),('proxy_machines','machines'),('copied_samples','copies')]:
        material_ru={'coal':'Угольная сеть Кюсю даёт запас хода и упорядоченное снабжение.', 'oil':'Средства вложены в будущее: нефтепереработка получает постоянный исследовательский приоритет.', 'machines':'Купленные станки ускоряют выпуск, но списки закупок известны Палате.', 'copies':'Собственные образцы улучшают надёжность техники; источник решений остаётся непризнанным.'}[short]
        material_en={'coal':'The Kyushu coal network provides endurance and organised supply.', 'oil':'Investment in the future gives oil refining a permanent research priority.', 'machines':'Purchased machinery increases output, but the Chamber knows our procurement lists.', 'copies':'Domestic designs improve equipment reliability; the source of these solutions remains unacknowledged.'}[short]
        for fleet,family in [('kure_yards','iron'),('airship_hangars','sky')]:
            key=f'JPI_scarlet_{family}_{short}'
            if family=='iron':
                ru,en='Железные алые паруса','Iron Scarlet Sails'
                mod='naval_damage_factor = 0.10 amphibious_invasion = 0.10'
                eq={'capital_ship':'max_strength = 0.15','screen_ship':'max_strength = 0.10'}
                intro='Тяжёлые алые корабли прикрывают десант: прочные корпуса, мощный огонь и захватные «щупальца». '
                intro_en='Heavy scarlet ships cover the landing: reinforced hulls, powerful guns and grappling tentacles. '
            else:
                ru,en='Алые небеса','Scarlet Skies'
                mod='naval_invasion_prep_speed = 0.25 amphibious_invasion = 0.05'
                eq={'airship_equipment':'air_range = 0.25 surface_detection = 0.20','airship_bomber_equipment':'air_range = 0.25 surface_detection = 0.20'}
                intro='Дирижабли дальней разведки ведут десант к берегу; надводный флот уступил им часть промышленной базы. '
                intro_en='Long-range reconnaissance airships guide the landing; the surface fleet has surrendered part of its industrial base. '
            if short=='coal': mod+=' naval_supply_consumption_factor = -0.05'
            if short=='machines':mod+=' industrial_capacity_dockyard = 0.05' if family=='iron' else ' industrial_capacity_factory = 0.03'
            if short=='copies':
                for k in eq:eq[k]+=' reliability = 0.10'
            extra='research_bonus = { synth_resources = 0.10 }' if short=='oil' else ''
            loc(key,ru,en);loc(key+'_desc',intro+material_ru,intro_en+material_en)
            equipment=' '.join(f'{k} = {{ {v} instant = yes }}' for k,v in eq.items())
            text+=f' {key} = {{ picture = jpc_fleet removal_cost = -1 modifier = {{ {mod} }} equipment_bonus = {{ {equipment} }} {extra} }}\n'
            result+=f' if = {{ limit = {{ has_completed_focus = JPI_{branch} has_completed_focus = JPI_{fleet} }} add_ideas = {key} }}\n'
    write('common/ideas/JPI_industry.txt',text+'} }\n')
    p='common/scripted_effects/JPI_industry.txt';s=(R/p).read_text(encoding='utf-8-sig')
    old=' if = { limit = { has_completed_focus = JPI_kure_yards } add_ideas = JPI_scarlet_iron }\n else = { add_ideas = JPI_scarlet_sky add_equipment_to_stockpile = { type = airship_equipment_1 amount = 12 producer = A03 } }'
    assert old in s
    s=s.replace(old,result+' if = { limit = { has_completed_focus = JPI_airship_hangars } add_equipment_to_stockpile = { type = airship_equipment_1 amount = 12 producer = A03 } }')
    write(p,s)

if __name__=='__main__':main()
