"""Authored compact focus layouts and small policy forks; stable IDs and outcomes.

Applied after source builders. Baseline coordinates are recorded once, so repeated
generation cannot progressively squeeze layouts or remove later content.
"""
from pathlib import Path
from collections import defaultdict
import json,re
from british_story_links import emit,nodes
from validate_philippines_rework import value,walk

ROOT=Path(__file__).resolve().parents[1]
LABELS={}

def setv(node,key,val):
    node[:]=[e for e in node if e[0]!=key];node.append((key,'=',str(val) if isinstance(val,(int,float)) else val))

def parents(f,*groups):
    f[:]=[e for e in f if e[0]!='prerequisite']
    for group in groups:f.append(('prerequisite','=',[('focus','=',key) for key in group]))

def ids(f):return [v for k,o,ns in f if k=='prerequisite' for a,b,v in ns if a=='focus']

def add(fs,key,ru,en,rd,ed,ps,reward,other=None,icon='GFX_goal_generic_national_unity'):
    LABELS[key]=(ru,en);LABELS[key+'_desc']=(rd,ed)
    if key not in fs:
        fs[key]=nodes(f'''id = {key} icon = {icon} x = 0 y = 0 cost = 3 ai_will_do = {{ factor = 4 }} completion_reward = {{ {reward} }}''')
    parents(fs[key],ps)
    if key.startswith('MNR_'):
        setv(fs[key],'available',nodes('MNR_home_secure = yes'));setv(fs[key],'cancel_if_invalid','yes')
    if other:setv(fs[key],'mutually_exclusive',[('focus','=',other)])
    return fs[key]

def pair(fs,prefix,parent,rows):
    keys=[prefix+'_'+x[0] for x in rows]
    for key,other,row in zip(keys,reversed(keys),rows):
        suffix,ru,en,rd,ed,fx=row
        add(fs,key,ru,en,rd,ed,(parent,),fx,other)
    return keys

def minor(fs,tag,profile):
    p='MNR_'+tag+'_';at=lambda key:fs[p+key]
    # The political choice now comes immediately after the opening focus.
    for route in ('civic','command'):parents(at(route),(p+'root',))
    programme=p+'common_programme'
    add(fs,programme,'Общий план местного правительства','A Common Government Programme','Согласовать хозяйственный план после выбора устройства власти. +35 политической власти и +5 доверия.','Agree a practical programme after settling the institutions. +35 political power and +5 confidence.',(p+'civic_settlement',p+'command_settlement'),'add_political_power = 35 add_to_variable = { MNR_mandate = 5 } MNR_refresh = yes')
    kind=profile['kind']
    names={
      'relief':('Общинные амбары','Community Granaries','Договоры поставщиков','Supplier Contracts'),
      'convoy':('Местные судовые мастерские','Local Marine Workshops','Контракты дальних перевозок','Long-Distance Shipping Contracts'),
      'customs':('Муниципальные сборщики','Municipal Customs Officers','Купеческое поручительство','Merchant Guarantees'),
      'survey':('Собственные землемеры','Our Own Surveyors','Заказать иностранные приборы','Order Foreign Instruments'),
      'repair':('Общинные ремонтные бригады','Community Repair Crews','Подряды торговых домов','Merchant Repair Contracts'),
      'finance':('Расчёты собственных домов','Settlement between Local Houses','Внешний расчётный агент','An External Clearing Agent'),
      'science':('Местная приборная школа','A Local Instrument School','Открытая переписка учёных','Open Scientific Correspondence'),
      'defence':('Мастерские поселений','Settlement Workshops','Внешние заказы снабжения','External Supply Orders')}[kind]
    eco=pair(fs,p+'economy',p+'economy0',[
      ('local',names[0],names[1],'Вложить средства в собственных специалистов: +10 запасов и одна скидка 25% на промышленное исследование.','Invest in local skills: +10 reserves and one 25% industry research bonus.','add_to_variable = { MNR_reserve = 10 } add_tech_bonus = { name = FSP_local_tools bonus = 0.25 uses = 1 category = industry } MNR_refresh = yes'),
      ('contracts',names[2],names[3],'Оплатить внешние заказы: +45 политической власти и 25 комплектов дополнительного оснащения. Договор с другой страной заключается отдельно.','Arrange outside orders: +45 political power and 25 support equipment. A bilateral agreement still requires separate consent.','add_political_power = 45 add_equipment_to_stockpile = { type = support_equipment_1 amount = 25 producer = ROOT }')])
    defence=pair(fs,p+'defence',p+'defence0',[
      ('garrison','Сначала защита поселений','Protect the Settlements First','Гарнизонный курс: +8 доверия общин и +5 опыта армии.','Garrison policy: +8 community confidence and +5 army XP.','add_to_variable = { MNR_mandate = 8 } army_experience = 5 MNR_refresh = yes'),
      ('mobile','Подвижный территориальный резерв','A Mobile Territorial Reserve','Подготовить мобильные части: +12 опыта армии и +5% поддержки войны.','Prepare mobile units: +12 army XP and +5% war support.','army_experience = 12 add_war_support = 0.05')])
    parents(at('economy0'),(programme,));parents(at('defence0'),(programme,));parents(at('contacts'),(programme,))
    parents(at('economy1'),eco);parents(at('defence1'),defence)
    parents(at('projects'),(p+'contacts',));parents(at('specialists'),(p+'projects',),(p+'chamber',))
    positions={'root':(10,0),'civic':(8,1),'command':(12,1),'civic_law':(8,2),'command_law':(12,2),'civic_settlement':(8,3),'command_settlement':(12,3),'common_programme':(10,4),
      'economy0':(2,5),'economy_local':(0,6),'economy_contracts':(4,6),'economy1':(2,7),'economy2':(2,8),
      'defence0':(10,5),'defence_garrison':(8,6),'defence_mobile':(12,6),'defence1':(10,7),'defence2':(10,8),
      'contacts':(18,5),'chamber':(16,6),'projects':(20,6),'specialists':(18,7),'goal':(10,10)}
    for key,(x,y) in positions.items():setv(at(key),'x',x);setv(at(key),'y',y)

def british(fs):
    choices=[
      ('budget','BLV_audit','BLV_hamilton',[
        ('subscriptions','Подписка островных общин','Island Community Subscriptions','Собрать добровольные средства: +8 запасов и +3 связности империи.','Collect subscriptions: +8 reserves and +3 cohesion.','add_to_variable = { BLV_reserve = 8 } add_to_variable = { BLV_cohesion = 3 } BLV_refresh = yes'),
        ('advance','Казначейский аванс Палаты','A Chamber Treasury Advance','Получить средства сейчас: +18 запасов, но долг Палате увеличится на 8.','Obtain immediate funds: +18 reserves, but Chamber debt increases by 8.','WTC_initialize_effect = yes add_to_variable = { WTC_debt = 8 } add_to_variable = { BLV_reserve = 18 } BLV_refresh = yes')]),
      ('yards','BLV_engine_rooms','BLV_naval_staff',[
        ('state','Казённая ремонтная служба','State Repair Service','Подготовить собственные ремонтные партии: +8 запасов.','Train state repair teams: +8 reserves.','add_to_variable = { BLV_reserve = 8 } BLV_refresh = yes'),
        ('contracts','Частные доковые контракты','Private Dock Contracts','Согласовать оплачиваемые работы: +35 политической власти и +4 опыта флота.','Arrange dock contracts: +35 political power and +4 naval XP.','add_political_power = 35 navy_experience = 4')]),
      ('rotation','BLV_rotation','BLV_marines',[
        ('medical','Врачи в каждой смене','Doctors with Every Relief','Медицинская ротация: +4 связности империи.','Medical relief: +4 imperial cohesion.','add_to_variable = { BLV_cohesion = 4 } BLV_refresh = yes'),
        ('depots','Складские команды смены','Relief Depot Teams','Учить снабженцев: +8 опыта армии и +5 запасов.','Train quartermasters: +8 army XP and +5 reserves.','army_experience = 8 add_to_variable = { BLV_reserve = 5 } BLV_refresh = yes')]),
      ('letters','BLV_instruments','BLV_malta_license',[
        ('open','Открытая переписка инженеров','Open Engineering Correspondence','Свободный обмен наблюдениями: +4 научной готовности. Условия мальтийской лицензии рассматриваются отдельно.','Exchange observations: +4 scientific readiness. Malta decides licensing separately.','add_to_variable = { SEN_science = 4 }'),
        ('sealed','Запечатанные исследовательские журналы','Sealed Research Journals','Ввести охрану записей: +6 научной безопасности.','Protect the records: +6 research security.','add_to_variable = { SEN_security = 6 }')])]
    for suffix,parent,join,rows in choices:
        keys=pair(fs,'BLV_'+suffix,parent,rows)
        old={'BLV_hamilton':'BLV_audit','BLV_naval_staff':'BLV_fleet_register','BLV_marines':'BLV_rotation','BLV_malta_license':'BLV_instruments'}[join]
        parents(fs[join],(old,),keys)
    # Rationing splits into industry and coal, then rejoins at machine tools.
    parents(fs['BLV_coal_depots'],('BLV_rationing',))
    parents(fs['BLV_machine_tools'],('BLV_bermuda_workshops',),('BLV_coal_depots',))
    parents(fs['BLV_nz_industry'],('BLV_machine_tools',))
    parents(fs['BLV_cable_school'],('BLV_ordnance',),('BLV_nz_industry',))
    parents(fs['BLV_russian_note'],('BLV_greenland_watch',))
    parents(fs['BLV_scientific_cargo'],('BLV_arctic_depots',),('BLV_russian_note',))
    parents(fs['BLV_battle_line'],('BLV_naval_staff',));parents(fs['BLV_cruiser_routes'],('BLV_naval_staff',))
    parents(fs['BLV_convoy_service'],('BLV_battle_line','BLV_cruiser_routes'))
    parents(fs['BLV_calibration'],('BLV_clinical_rules',),('BLV_serum_contract','BLV_ethical_research'))
    parents(fs['BLV_philippine_mission'],('BLV_malacca',))
    parents(fs['BLV_pacific_deterrent'],('BLV_batavia_oil',),('BLV_philippine_mission',))
    parents(fs['BLV_war_plans'],('BLV_pacific_deterrent',))
    parents(fs['BLV_eastern_supply'],('BLV_japanese_note',),('BLV_war_plans',))

def australian(fs,tag):
    p='AUC_'+tag+'_'
    root=next(k for k,v in fs.items() if not ids(v))
    branches=pair(fs,p+'opening',root,[
      ('parliament','Сначала местный парламент','The Local Parliament First','Публично обсудить условия будущего договора: +3% стабильности и +20 политической власти.','Debate future terms publicly: +3% stability and +20 political power.','add_stability = 0.03 add_political_power = 20'),
      ('delegates','Соглашение делегатов','A Delegate Agreement','Подготовить согласованные предложения: +40 политической власти. Это не согласие на присоединение.','Prepare agreed proposals: +40 political power. This does not consent to annexation.','add_political_power = 40')])
    target=p+('corowa' if tag=='A07' else 'demand');parents(fs[target],branches)
    if tag=='A07':
        coast=pair(fs,p+'defence',p+'staff',[
          ('territorial','Территориальные оборонные округа','Territorial Defence Districts','Развивать сухопутный резерв: +12 опыта армии.','Develop the land reserve: +12 army XP.','army_experience = 12'),
          ('maritime','Защита морских сообщений','Protect Maritime Communications','Подготовить экипажи и транспорты: +5 опыта флота и пять транспортов.','Prepare crews and shipping: +5 naval XP and five convoys.','navy_experience = 5 add_equipment_to_stockpile = { type = convoy_1 amount = 5 producer = ROOT }')])
        parents(fs[p+'coast'],coast);parents(fs[p+'yards'],coast)
        parents(fs[p+'convoys'],(p+'coast',),(p+'yards',))
        parents(fs[p+'deter'],(p+'japan',));parents(fs[p+'japan_goal'],(p+'partners',),(p+'deter',),(p+'commonwealth',))
        parents(fs[p+'research'],(p+'arsenal',),(p+'accounts',))
        # The log flags recruit_character in a focus as invalid. The character is
        # recruited at startup below; the later ministry only promotes him.
        reward=value(fs[p+'first_ministry'],'completion_reward')
        reward[:]=[e for e in reward if e[0]!='recruit_character']
    else:
        economy,middle,end=list(fs)[1:4]
        parents(fs[middle],(root,));parents(fs[end],(economy,),(middle,))
        parents(fs[p+'school'],(p+'rifles',))
        parents(fs[p+'services'],(p+'credit',),(p+'harbour',),(p+'school',))

def chamber(fs,treeid):
    root=next(k for k,v in fs.items() if not ids(v))
    common='WTN_common_registry' if 'WTN_common_registry' in fs else root
    keys=pair(fs,treeid+'_mandate',common,[
      ('public','Открытые сметы и поручения','Public Accounts and Mandates','Представить условия общинам: +3% стабильности и +20 политической власти. Долг сохраняется.','Present the terms publicly: +3% stability and +20 political power. Existing debt remains.','add_stability = 0.03 add_political_power = 20'),
      ('delegated','Полномочия постоянной делегации','Standing Delegation Mandate','Поручить переговоры специалистам: +40 политической власти. Новые договоры требуют отдельного согласия.','Empower negotiators: +40 political power. New agreements require separate consent.','add_political_power = 40')])
    for key,f in fs.items():
        if key not in keys and ids(f)==[common]:parents(f,keys)
    if 'WTN_credit_committee' in fs:
        for a,b,join in [('WTN_gold_reserves','WTN_arbitration','WTN_reserve_audit'),('WTN_silver_convoy','WTN_insured_ports','WTN_market_rules'),('WTN_cable_survey','WTN_malta_correspondence','WTN_measurement_fund'),('WTN_cable_watch','WTN_strait_wardens','WTN_pirate_contacts')]:
            parent=ids(fs[a])[0];parents(fs[b],(parent,));parents(fs[join],(a,),(b,))
    elif treeid=='WTN_RUS_focus':
        parents(fs['WTN_RUS_programme_3'],('WTN_RUS_programme_1',))
        parents(fs['WTN_RUS_programme_4'],('WTN_RUS_programme_2',),('WTN_RUS_programme_3',))

def japan(fs):
    rows=[
      ('workshop_policy','JSM_steel','JSM_workshops',[
        ('guilds','Соглашение с мастеровыми','An Agreement with the Artisans','Сохранить местную школу производства: одна скидка 25% на промышленное исследование.','Preserve local skills: one 25% industry research bonus.','add_tech_bonus = { name = FSP_local_tools bonus = 0.25 uses = 1 category = industry }'),
        ('state','Казённые станочные заказы','State Machine-Tool Orders','Сосредоточить закупки: +40 политической власти и +5 опыта армии.','Coordinate procurement: +40 political power and +5 army XP.','add_political_power = 40 army_experience = 5')]),
      ('diplomatic_policy','JSM_council','JSM_ocean',[
        ('markets','Сначала торговые гарантии','Trade Guarantees First','Подготовить переговорные сметы: +45 политической власти. Протекторат требует отдельного ответа другой страны.','Prepare negotiating accounts: +45 political power. Protectorates still require the other country to respond.','add_political_power = 45'),
        ('squadrons','Демонстрация морской готовности','Demonstrate Naval Readiness','Подготовить штаб эскадры: +10 опыта флота и +5% поддержки войны.','Prepare the squadron staff: +10 naval XP and +5% war support.','navy_experience = 10 add_war_support = 0.05')])]
    for prefix,parent,join,rr in rows:
        keys=pair(fs,'JSM_'+prefix,parent,rr)
        parents(fs[join],keys)
    # Three protectorate dossiers are parallel options, not a compulsory queue.
    parents(fs['JSM_north'],('JSM_council',));parents(fs['JSM_south'],('JSM_council',))

def compact(fs,baseline,kind):
    depth={};visiting=set()
    def rank(key):
        if key in depth:return depth[key]
        assert key not in visiting,('focus cycle',key);visiting.add(key)
        ps=[x for x in ids(fs[key]) if x in fs]
        depth[key]=1+max(map(rank,ps)) if ps else 0;visiting.remove(key);return depth[key]
    for key in fs:rank(key)
    coords={}
    for key,f in fs.items():
        x,y=baseline.get(key,(int(value(f,'x')),int(value(f,'y'))))
        coords[key]=[round(x*.75),depth[key]]
    # Compact rows without overlapping focus captions (two grid units minimum).
    rows=defaultdict(list)
    for key,(x,y) in coords.items():rows[y].append(key)
    for y,keys in rows.items():
        keys.sort(key=lambda key:(coords[key][0],baseline.get(key,[0,0])[0],key))
        for previous,key in zip(keys,keys[1:]):coords[key][0]=max(coords[key][0],coords[previous][0]+2)
    if kind=='chamber':
        for suffix in ('public','delegated'):
            key=next(k for k in fs if k.endswith('_focus_mandate_'+suffix))
            parent=ids(fs[key])[0];coords[key][0]=coords[parent][0]+(-2 if suffix=='public' else 2)
        if 'WTN_common_registry' in fs:
            for key in fs:
                if key in baseline and key not in ('WTN_annual_report','WTN_common_registry'):coords[key][0]=round(baseline[key][0]/6)*8+2
            coords['WTN_annual_report'][0]=18;coords['WTN_common_registry'][0]=18
            for suffix in ('public','delegated'):coords['WTN_focus_mandate_'+suffix][0]=16 if suffix=='public' else 20
            for left,right in [('WTN_gold_reserves','WTN_arbitration'),('WTN_silver_convoy','WTN_insured_ports'),('WTN_cable_survey','WTN_malta_correspondence'),('WTN_cable_watch','WTN_strait_wardens')]:
                coords[left][0]-=2;coords[right][0]+=2
        elif 'WTN_RUS_programme_1' in fs:
            centre=coords['WTN_RUS_programme_1'][0];coords['WTN_RUS_programme_2'][0]=centre-2;coords['WTN_RUS_programme_3'][0]=centre+2
    if kind=='british':
        # Branch centres. Paired leaves form diamonds inside each panel.
        centres={'economy':2,'credit':10,'government':20,'colonies':30,'navy':38,'army':46,'east':54,'science':62,'arctic':72,'return':78}
        groups={
          'economy':'rationing bermuda_workshops coal_depots machine_tools ordnance nz_industry cable_school island_economy',
          'credit':'credit_audit chamber_desk independent_accounts lambert_compact insurance revoke_cover service_contracts debt_settlement',
          'government':'leviathan audit hamilton commission admiralty constitution crown naval_cabinet merit strategic_reserve naval_state imperial_budget rights delegates maritime_commonwealth royal_secretariat crown_guard loyal_governors imperial_prerogative budget_subscriptions budget_advance crowns_council',
          'colonies':'station_census australian_dossier dominion_charters nz_ports pacific_stations colonial_red_line australia_sovereignty reconquest',
          'navy':'fleet_register bermuda_dock engine_rooms battle_line cruiser_routes naval_staff convoy_service singapore_docks fleet_logistics yards_state yards_contracts',
          'army':'garrison_audit rotation marines field_hospitals colonial_service amphibious_staff airship_service rotation_medical rotation_depots',
          'east':'malacca batavia_oil philippine_mission pacific_deterrent japanese_note war_plans eastern_supply',
          'science':'song_records instruments malta_license ungudja clinical_rules serum_contract ethical_research calibration research_school tesla_patents ship_suppressors letters_open letters_sealed',
          'arctic':'greenland_watch arctic_depots russian_note scientific_cargo polar_mandate archive',
          'return':'remember_home coastal_trials long_range pioneer_station'}
        offsets={'bermuda_workshops':-2,'coal_depots':2,'ordnance':-2,'nz_industry':2,'independent_accounts':-2,'lambert_compact':2,'insurance':-2,'revoke_cover':-2,'service_contracts':2,'admiralty':-3,'naval_cabinet':-3,'merit':-3,'strategic_reserve':-3,'naval_state':-3,'crown':3,'royal_secretariat':3,'crown_guard':3,'loyal_governors':3,'imperial_prerogative':3,'budget_subscriptions':-2,'budget_advance':2,'crowns_council':5,'dominion_charters':2,'australia_sovereignty':2,'colonial_red_line':-2,'reconquest':-2,'battle_line':-2,'cruiser_routes':2,'yards_state':-2,'yards_contracts':2,'rotation_medical':-2,'rotation_depots':2,'serum_contract':-2,'ethical_research':2,'letters_open':-2,'letters_sealed':2,'tesla_patents':3,'ship_suppressors':3,'arctic_depots':-2,'russian_note':2}
        for group,keys in groups.items():
            for suffix in keys.split():
                key='BLV_'+suffix
                if key in coords:coords[key][0]=centres[group]+offsets.get(suffix,0)
        for suffix in ('admiralty','naval_cabinet','merit','strategic_reserve','naval_state'):coords['BLV_'+suffix][0]=16
        for suffix in ('crown','royal_secretariat','crown_guard','loyal_governors','imperial_prerogative'):coords['BLV_'+suffix][0]=24
        # Deterrence forms a second small fan, without changing dated gates.
        for suffix,offset in [('batavia_oil',-2),('philippine_mission',2),('japanese_note',-2),('war_plans',2),('eastern_supply',0)]:coords['BLV_'+suffix][0]=centres['east']+offset
        for suffix in ('tesla_patents','ship_suppressors'):coords['BLV_'+suffix][0]=66
        coords['BLV_crowns_council'][0]=20
        coords['BLV_crowns_council'][1]=max(coords['BLV_'+suffix][1] for suffix in ('naval_state','maritime_commonwealth','imperial_prerogative'))+2
        coords['BLV_debt_settlement'][1]=max(coords['BLV_revoke_cover'][1],coords['BLV_service_contracts'][1])+2
        coords['BLV_nz_ports'][1]=7;coords['BLV_pacific_stations'][1]=8
        coords['BLV_australia_sovereignty'][1]=9;coords['BLV_reconquest'][1]=9
    elif kind=='japan':
        explicit={'steel':(5,0),'workshop_policy_guilds':(3,1),'workshop_policy_state':(7,1),'workshops':(5,2),'shipyards':(5,3),'council':(5,4),'north':(1,5),'south':(5,5),'diplomatic_policy_markets':(9,5),'diplomatic_policy_squadrons':(13,5),'ocean':(11,6)}
        for suffix,pos in explicit.items():coords['JSM_'+suffix]=list(pos)
    elif kind.startswith('australia'):
        tag=kind.split(':')[1];p='AUC_'+tag+'_'
        if tag=='A07':
            explicit={'leagues':(8,0),'opening_parliament':(6,1),'opening_delegates':(10,1),'corowa':(8,2),'convention':(8,3),'senate':(8,4),'terms_AVC':(0,5),'terms_AQL':(4,5),'terms_ASA':(8,5),'terms_AWA':(12,5),'terms_ATA':(16,5),'referendums':(8,6),'charter':(8,7),'commonwealth':(8,8),'parliament':(6,9),'six_states':(10,9),'first_ministry':(8,10),'customs':(22,1),'arsenal':(20,2),'chamber':(26,1),'accounts':(26,2),'research':(23,3),'staff':(34,1),'defence_territorial':(32,2),'defence_maritime':(36,2),'coast':(32,3),'yards':(36,3),'convoys':(34,4),'japan':(34,5),'partners':(32,6),'deter':(36,6),'japan_goal':(34,9),'sovereignty':(18,8),'own_flag':(16,10),'break_crown':(20,10),'british_routes':(18,11)}
        else:
            root=next(k for k,f in fs.items() if not ids(f));economic,second,last=list(fs)[1:4]
            explicit={root.removeprefix(p):(8,0),'opening_parliament':(6,1),'opening_delegates':(10,1),'demand':(8,2),'federal':(6,3),'separate':(10,3),'mandate':(6,4),economic.removeprefix(p):(0,1),second.removeprefix(p):(4,1),last.removeprefix(p):(2,2),'rifles':(16,1),'harbour':(14,2),'school':(18,2),'credit':(22,1),'services':(20,3)}
        for suffix,pos in explicit.items():coords[p+suffix]=list(pos)
        if tag=='A07':
            for suffix in 'customs arsenal chamber accounts research staff defence_territorial defence_maritime coast yards convoys japan partners deter japan_goal'.split():coords[p+suffix][0]-=4
            for n,t in enumerate(('AVC','AQL','ASA','AWA','ATA')):coords[p+'terms_'+t][0]=4*n
        else:
            for suffix in (economic.removeprefix(p),second.removeprefix(p),last.removeprefix(p)):coords[p+suffix][0]-=2
            coords[p+'services'][0]=22
    for key,(x,y) in coords.items():setv(fs[key],'x',x);setv(fs[key],'y',y)

def philippines(fs):
    """Five distinct panels; a full empty focus slot separates their envelopes."""
    import ast
    src=ast.parse((ROOT/'tools/inspect_coords.py').read_text(encoding='utf-8-sig'))
    maps={n.targets[0].id:ast.literal_eval(n.value) for n in src.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('wtp_map','conf_map','econ_map','mil_map','coup_map','root_postwar_map')}
    war=set(maps['mil_map'])|{'A10D_mountain_infantry','A10D_signal_corps','A10D_war_fleet'}
    econ={k for k in fs if k.startswith('A10D_') and k not in war}
    post={'A10R_war_accounts','A10R_veterans_land','A10_federal_reconstruction','A10R_peace_generation'}
    republican=set(maps['conf_map'])
    groups=[set(k for k in fs if k.startswith('A10W_')),republican,set(k for k in fs if k.startswith('A10M_')),econ,war,post]
    groups=[g&set(fs) for g in groups]
    assert set(fs)==set.union(*groups)|{'A10_island_congress','A10R_provincial_rolls','A10R_emergency_council'},set(fs)-set.union(*groups)
    source={k:v for m in maps.values() for k,v in m.items()}
    source.update({'A10D_export_bureau':(24,16),'A10D_island_industry':(22,20),'A10D_mountain_infantry':(28,12),'A10D_signal_corps':(28,16),'A10D_war_fleet':(28,23)})
    # Depth is calculated from actual gates; every arrow still points down.
    depth={}
    def rank(key):
        if key not in depth:depth[key]=max([rank(x)+1 for x in ids(fs[key])]+[0])
        return depth[key]
    for key in fs:rank(key)
    xcursor=0;panels=[]
    for number,group in enumerate(groups):
        local={k:[source[k][0]*2,rank(k)+1] for k in group}
        if number==0:
            remap={1:0,2:2,3:4,5:6,7:8,8:10,9:12}
            for key in group:local[key][0]=remap[source[key][0]]
        elif number==1:
            remap={11:0,12:2,13:4,15:6,16:8,17:10,18:12}
            for key in group:local[key][0]=remap[source[key][0]]
        elif number==2:
            remap={34:0,36:4,38:6,40:8,42:12}
            for key in group:local[key][0]=remap[source[key][0]]
            for suffix in ('directorate','service_council','audited_budget','professional_army','fixed_term'):local['A10M_'+suffix][0]=8
        elif number==5:
            for key,x,y in [('A10R_war_accounts',2,3),('A10R_veterans_land',0,4),('A10_federal_reconstruction',4,4),('A10R_peace_generation',2,5)]:local[key]=[x,y]
        # Stretch only crowded rows inside a panel; never move another panel into it.
        rows=defaultdict(list)
        for key,(x,y) in local.items():rows[y].append(key)
        for y,keys in rows.items():
            keys.sort(key=lambda k:(local[k][0],k))
            for a,b in zip(keys,keys[1:]):local[b][0]=max(local[b][0],local[a][0]+4)
        low=min(x for x,y in local.values());width=max(x for x,y in local.values())-low
        for key,(x,y) in local.items():setv(fs[key],'x',xcursor+x-low);setv(fs[key],'y',y)
        panels.append((xcursor,xcursor+width));xcursor+=width+4
    centre=(panels[1][0]+panels[1][1])//2
    for key,x,y in [('A10_island_congress',centre,0),('A10R_provincial_rolls',centre-2,1),('A10R_emergency_council',centre+2,1)]:setv(fs[key],'x',x);setv(fs[key],'y',y)
    return panels

def sync_manifests(allrows):
    def rows(path):return allrows.get(path,[])
    for name,key in [('british_campaign_manifest.json','focuses')]:
        path=ROOT/'tools'/name;data=json.loads(path.read_text(encoding='utf-8-sig'));data[key]=rows('BLV_campaign.txt');path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    path=ROOT/'tools/australian_campaign_manifest.json';data=json.loads(path.read_text(encoding='utf-8-sig'))
    for tag in data:data[tag]=rows(f'AUC_campaign_{tag}.txt')
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    path=ROOT/'tools/minor_campaign_manifest.json';data=json.loads(path.read_text(encoding='utf-8-sig'))
    for tag in data:data[tag]['focuses']=rows(f'MNR_{tag}.txt')
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    path=ROOT/'tools/chamber_network_manifest.json';data=json.loads(path.read_text(encoding='utf-8-sig'))
    for name,tree in data.items():
        if rows(name+'_focus.txt'):tree['focuses']=rows(name+'_focus.txt')
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def apply():
    from minor_campaign_profiles import PROFILES
    basepath=ROOT/'tools/focus_layout_baseline.json'
    baseline=json.loads(basepath.read_text(encoding='utf-8-sig')) if basepath.exists() else {}
    allrows={};report={}
    for path in sorted((ROOT/'common/national_focus').glob('*.txt')):
        if path.name=='a01_focus.txt':continue  # The user explicitly keeps the Netherlands as an unchanged reference.
        tree=nodes(path.read_text(encoding='utf-8-sig'));ft=value(tree,'focus_tree',[])
        if not ft or not any(k=='tag' for k,o,v in walk(value(ft,'country',[]))):continue
        fs={value(v,'id'):v for k,o,v in ft if k=='focus'}
        if not fs:continue
        original=list(fs);b=baseline.setdefault(path.name,{})
        added_pattern=r'_(?:common_programme|economy_local|economy_contracts|defence_garrison|defence_mobile|opening_parliament|opening_delegates|defence_territorial|defence_maritime)$|_focus_mandate_|^BLV_(?:budget_subscriptions|budget_advance|yards_state|yards_contracts|rotation_medical|rotation_depots|letters_open|letters_sealed)$|^JSM_(?:workshop_policy|diplomatic_policy)_'
        for key in list(b):
            if re.search(added_pattern,key):del b[key]
        for key,f in fs.items():
            if key not in b and not re.search(added_pattern,key):b[key]=[int(value(f,'x')),int(value(f,'y'))]
        before=[max(v[0] for v in b.values())-min(v[0] for v in b.values()),max(v[1] for v in b.values())]
        kind='generic';treeid=value(ft,'id')
        if path.name.startswith('MNR_'):
            tag=path.stem[4:];minor(fs,tag,PROFILES[tag]);kind='minor'
        elif path.name=='BLV_campaign.txt':british(fs);kind='british'
        elif path.name.startswith('AUC_campaign_'):
            tag=path.stem.removeprefix('AUC_campaign_');australian(fs,tag);kind='australia:'+tag
        elif path.name.startswith('WTN_'):chamber(fs,treeid);kind='chamber'
        elif path.name=='a03_focus.txt' and 'JSM_steel' in fs:japan(fs);kind='japan'
        if path.name=='a10_focus.txt':philippines(fs);kind='philippines'
        elif kind!='minor':compact(fs,b,kind)
        if kind.startswith('australia:') and tag != 'A07':
            from australian_prc_structure import apply as prc_structure
            prc_structure(fs,tag,add,parents,setv)
        # Explicit hard bounds: no duplicate locations, upward edges or caption overlaps.
        pos={key:(int(value(f,'x')),int(value(f,'y'))) for key,f in fs.items()}
        conflicts={p:[k for k,v in pos.items() if v==p] for p in pos.values() if list(pos.values()).count(p)>1}
        assert not conflicts,(path,'overlap',conflicts)
        for key,f in fs.items():
            for parent in ids(f):assert parent not in pos or pos[parent][1]<pos[key][1],(path,key,parent)
        ft[:]=[e for e in ft if e[0]!='focus'];ft.extend(('focus','=',f) for f in fs.values())
        path.write_text(emit(tree)+'\n',encoding='utf-8')
        allrows[path.name]=[dict(id=key,x=pos[key][0],y=pos[key][1],parents=ids(f)) for key,f in fs.items()]
        report[path.name]=dict(before=before,after=[max(x for x,y in pos.values())-min(x for x,y in pos.values()),max(y for x,y in pos.values())],focuses=len(fs),added=[k for k in fs if k not in b])
    basepath.write_text(json.dumps(baseline,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for language,n in [('russian',0),('english',1)]:
        lines=['l_'+language+':']+[f' {key}:0 "{texts[n]}"' for key,texts in LABELS.items()]
        lines.append(' FSP_local_tools:0 "'+('Местная техническая школа' if n==0 else 'Local Technical School')+'"')
        (ROOT/f'localisation/{language}/FSP_focus_shapes_l_{language}.yml').write_text('\n'.join(lines)+'\n',encoding='utf-8-sig')
    sync_manifests(allrows)
    history=ROOT/'history/countries/A07 - Placeholder.txt';text=history.read_text(encoding='utf-8-sig')
    if 'recruit_character = AUC_edmund_barton' not in text:
        text=text.replace('recruit_character = A07_canon_leader','recruit_character = AUC_edmund_barton\nrecruit_character = A07_canon_leader\npromote_character = { character = A07_canon_leader ideology = conservatism }',1)
        history.write_text(text,encoding='utf-8')
    (ROOT/'common/on_actions/FSP_ministry.txt').write_text('# Barton is attached in country history and promoted by the ministry focus.\n',encoding='utf-8')
    (ROOT/'tools/focus_shapes_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Shaped {len(report)} trees, {sum(p["focuses"] for p in report.values())} focuses, {sum(len(p["added"]) for p in report.values())} new focus choices/joins.')
    return allrows

if __name__=='__main__':apply()
