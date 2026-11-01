"""Shared outcomes for British focuses and the author's dated chronicle.

Calendar dates stay in the chronicle. Focuses prepare or acknowledge those events;
late follow-ups use the same guarded outcomes and cannot pay the reward twice.
"""
from pathlib import Path
from datetime import datetime,timedelta
import re,json
from validate_philippines_rework import parse,value

ROOT=Path(__file__).resolve().parents[1]

def emit(nodes,indent=0):
    out=[];pad=' '*indent
    for k,o,v in nodes:
        if o is None:out.append(pad+k)
        elif isinstance(v,list):out.extend([pad+f'{k} {o} {{',emit(v,indent+1),pad+'}'])
        else:out.append(pad+f'{k} {o} {v}')
    return '\n'.join(out)

def nodes(text):return parse(text)

def configure(b):
    """Extend the source builder before it emits files."""
    replacements={
      'BLV_malacca':('BLV_request_passage_policy = yes','date > 1893.11.27','BLV_passage_decided'),
      'BLV_ungudja':('BLV_review_ungudja = yes','date > 1893.4.11','BLV_ungudja_file'),
      'BLV_serum_contract':('BLV_apply_serum_contract = yes','date > 1893.6.27',None),
      'BLV_ethical_research':('BLV_apply_ethical_research = yes','date > 1893.6.27',None),
      'BLV_calibration':('BLV_apply_calibration = yes','date > 1894.7.19 BLV_tesla_access = yes', 'BLV_calibrated'),
      'BLV_polar_mandate':('BLV_request_polar_policy = yes','date > 1896.8.4','BLV_polar_decided'),
    }
    for row in b.FOCUSES:
        if row['id'] not in replacements:continue
        reward,gate,bypass=replacements[row['id']]
        tree=nodes(row['script']);node=value(tree,'focus')
        node[:]=[e for e in node if e[0] not in ('completion_reward','available','bypass')]
        node.append(('available','=',nodes(gate)))
        node.append(('completion_reward','=',nodes(reward+' BLV_refresh = yes')))
        if bypass:node.append(('bypass','=',nodes('has_country_flag = '+bypass)))
        row['script']=emit(tree)
    edits={
      'BLV_malacca':('Порядок судоходства в Малакке','Navigation Rules in Malacca'),
      'BLV_malacca_desc':('Оформить решение о судоходстве, принятое на совещании 28 ноября 1893 года. Капитаны должны получить единый порядок прохода через пролив.','Formalise the navigation settlement of 28 November 1893 and issue consistent passage orders to the captains.'),
      'BLV_ethical_research_desc':('Пересмотреть июньские решения о Фонде Дюбуа и запретить принудительный сбор крови. В дальнейшем поставки Палаты не смогут отменить этот запрет.','Review the June Dubois policy and prohibit coerced blood collection. Later Chamber deliveries cannot overrule the ban.'),
      'BLV_serum_contract_desc':('Утвердить лицензированный контракт или пересмотреть прежний отказ. Казна сверит условия поставок, а врачебный надзор установит порядок применения сыворотки.','Ratify a licensed contract or revise the earlier refusal, with treasury oversight of deliveries and medical supervision of serum use.'),
      'BLV_calibration_desc':('Завершить ранний опыт, назначенный на 20 июля 1894 года. При отсутствии доступа к Тесле работа откладывается. Это глушитель отдельного объекта, а не дальний прототип 1900 года.','Complete the early trial scheduled for 20 July 1894. Without Tesla access it is deferred. This protects a single site, unlike the long-range prototype of 1900.'),
      'BLV_polar_mandate_desc':('Исполнить мандат совещания 5 августа 1896 года: подготовить закрытую экспедицию или согласовать участие иностранных наблюдателей. Раскопки начнутся отдельно с 1898 года.','Implement the expedition mandate of 5 August 1896, arranging a private voyage or foreign observers. Excavation is a separate operation from 1898.'),
      'BLV_arctic_tt':('Мандат и событие 5 августа 1896 года имеют общий исход. Раскопки доступны с 1898 года при контроле Гренландии.','The mandate shares its outcome with the event of 5 August 1896. Excavation opens in 1898 while Greenland is controlled.'),
    }
    for k,(ru,en) in edits.items():b.LOC['russian'][k]=ru;b.LOC['english'][k]=en
    additions=[
      ('tesla_patents','Патенты раннего глушителя','Early Suppressor Patents','Рассмотреть порядок хранения или лицензирования ранних чертежей после 25 октября 1894 года. Палата сама решает, покупать ли лицензию.','Set early-patent policy after 25 October 1894. The Chamber must consent to any purchase.',74,18,'calibration','BLV_request_patent_policy = yes','date > 1894.10.24 has_country_flag = BLV_calibrated','BLV_patents_decided'),
      ('ship_suppressors','Глушители для кораблей и баз','Suppressors for Ships and Bases','После опыта 20 мая 1895 года выбрать корабельную установку малого радиуса или стационарную башню. Это не дальний глушитель.','After 20 May 1895, select a short-range ship installation or a stationary tower, distinct from a long-range suppressor.',74,20,'calibration','BLV_request_installation_policy = yes','date > 1895.5.19 has_country_flag = BLV_calibrated BLV_tesla_access = yes','BLV_installation_decided'),
      ('airship_service','Адмиралтейская служба дирижаблей','Admiralty Airship Service','Исполнить решения совещания 20 мая 1896 года: подготовить экипажи и имущество для разведывательной или ударной программы дирижаблей.','Implement the airship conference settlement of 20 May 1896 by preparing crews and stores for reconnaissance or strike duties.',58,20,'naval_staff','BLV_request_airship_policy = yes','date > 1896.5.19','BLV_airships_decided'),
      ('crowns_council','Совет корон в изгнании','A Council of Exiled Crowns','С 10 декабря 1896 года определить правовое положение Совета корон. Это политическое объединение, которое не заменяет кабинет и не объявляет войну России.','From 10 December 1896, settle the legal status of a political Council of Crowns without replacing cabinets or declaring war on Russia.',34,20,'hamilton','BLV_request_crowns_policy = yes','date > 1896.12.9','BLV_crowns_decided'),
    ]
    for key,ru,en,rd,ed,x,y,parent,reward,gate,bypass in additions:
        b.focus(key,ru,en,rd,ed,x,y,parents=(parent,),reward=reward,gate=gate,icon='GFX_goal_generic_scientific_exchange' if key!='crowns_council' else 'GFX_goal_generic_neutrality_focus')
        tree=nodes(b.FOCUSES[-1]['script']);value(tree,'focus').append(('bypass','=',nodes('has_country_flag = '+bypass)));b.FOCUSES[-1]['script']=emit(tree)
    # The visible chain follows the preparation actually described in the story.
    parents={'BLV_calibration':'BLV_clinical_rules','BLV_ship_suppressors':'BLV_tesla_patents','BLV_airship_service':'BLV_amphibious_staff','BLV_debt_settlement':'BLV_chamber_desk'}
    for row in b.FOCUSES:
        if row['id'] not in parents:continue
        parent=parents[row['id']];tree=nodes(row['script']);node=value(tree,'focus')
        node[:]=[e for e in node if e[0]!='prerequisite']+[('prerequisite','=',nodes('focus = '+parent))]
        row['parents']=[parent];row['script']=emit(tree)
    # The private Unguja report can be delivered once; no public chronicle gets it.
    event_tree=nodes(b.EVENTS[next(i for i,s in enumerate(b.EVENTS) if 'id = blv_campaign.10 ' in s)])
    report=value(event_tree,'country_event')
    opt=value(report,'option');opt[:]=[e for e in opt if e[0] in ('name','ai_chance')]+nodes('BLV_receive_ungudja_file = yes')
    report[:]=[e for e in report if e[0]!='trigger']+[('trigger','=',nodes('tag = A02 date > 1893.4.11 NOT = { has_country_flag = BLV_ungudja_file }'))]
    index=next(i for i,s in enumerate(b.EVENTS) if 'id = blv_campaign.10 ' in s);b.EVENTS[index]=emit(event_tree)


def story_effects():
    effects={}
    def effect(name,body):effects['BLV_'+name]=nodes(body)
    def once(flag,body,gate='BLV_is_britain = yes'):
        return f'if = {{ limit = {{ {gate} NOT = {{ has_country_flag = {flag} }} }} set_country_flag = {flag} {body} BLV_refresh = yes }}'
    effect('apply_serum_contract','''if = { limit = { BLV_is_britain = yes date > 1893.6.27 }
      clr_country_flag = BLV_ethical_research set_country_flag = BLV_serum_contract remove_ideas = BLV_medical_commission_spirit
    '''+once('BLV_serum_policy_paid','add_to_variable = { BLV_cohesion = -8 } add_to_variable = { SEN_science = 10 }')+' }')
    effect('apply_ethical_research','''if = { limit = { BLV_is_britain = yes date > 1893.6.27 }
      clr_country_flag = BLV_serum_contract set_country_flag = BLV_ethical_research remove_ideas = BLV_serum_spirit add_ideas = BLV_medical_commission_spirit
    '''+once('BLV_ethical_policy_paid','add_to_variable = { BLV_cohesion = 8 }')+' }')
    effect('review_ungudja',once('BLV_ungudja_pending','country_event = { id = blv_campaign.10 days = 1 }','BLV_is_britain = yes date > 1893.4.11 NOT = { has_country_flag = BLV_ungudja_file }'))
    effect('receive_ungudja_file',once('BLV_ungudja_file','clr_country_flag = BLV_ungudja_pending add_to_variable = { SEN_science = 5 }','BLV_is_britain = yes date > 1893.4.11'))
    effect('apply_calibration',once('BLV_calibrated','set_country_flag = CH94_tesla_prototype clr_country_flag = CH94_tesla_accident add_to_variable = { SEN_science = 15 } add_tech_bonus = { name = CH94_research bonus = 0.5 uses = 1 category = industry } add_timed_idea = { idea = CH94_tesla days = 180 }','BLV_is_britain = yes date > 1894.7.19 has_country_flag = SEN_laboratory_done BLV_tesla_access = yes'))
    policies={
      'passage_open':('BLV_passage_decided','set_country_flag = BLV_open_passage add_to_variable = { BLV_reserve = 5 } add_political_power = 25','date > 1893.11.27'),
      'passage_blockade':('BLV_passage_decided','set_country_flag = BLV_passage_blockade add_fuel = -5000 if = { limit = { country_exists = A03 } A03 = { add_timed_idea = { idea = CH93_blockade days = 90 } } }','date > 1893.11.27'),
      'patents_private':('BLV_patents_decided','set_country_flag = BLV_patents_private','date > 1894.10.24 has_country_flag = BLV_calibrated BLV_tesla_access = yes'),
      'patents_offer':('BLV_patents_decided','set_country_flag = BLV_patents_offered set_country_flag = { flag = BLV_patent_offer_pending days = 45 } A04 = { country_event = { id = blv_story.3 days = 1 } }','date > 1894.10.24 has_country_flag = BLV_calibrated BLV_tesla_access = yes country_exists = A04 NOT = { has_war_with = A04 }'),
      'mobile_installation':('BLV_installation_decided','set_country_flag = CH95_tesla_mobile clr_country_flag = CH95_tesla_stationary remove_ideas = CH95_tesla_tower add_ideas = CH95_tesla_mobile add_political_power = -40','date > 1895.5.19 has_country_flag = BLV_calibrated BLV_tesla_access = yes'),
      'tower_installation':('BLV_installation_decided','set_country_flag = CH95_tesla_stationary clr_country_flag = CH95_tesla_mobile remove_ideas = CH95_tesla_mobile add_ideas = CH95_tesla_tower add_political_power = -35','date > 1895.5.19 has_country_flag = BLV_calibrated BLV_tesla_access = yes'),
      'airship_scouts':('BLV_airships_decided','set_country_flag = BLV_airship_scouts add_political_power = -35 add_timed_idea = { idea = CH96_airship_scouts days = 365 } air_experience = 15','date > 1896.5.19'),
      'airship_strike':('BLV_airships_decided','set_country_flag = BLV_airship_strike add_political_power = -50 add_timed_idea = { idea = CH96_airship_bombers days = 365 } air_experience = 25','date > 1896.5.19'),
      'polar_private':('BLV_polar_decided','set_country_flag = BLV_arctic_open set_country_flag = CH96_secret_greenland add_to_variable = { SEN_readiness = 15 } add_political_power = -40 add_fuel = -4000 add_timed_idea = { idea = CH96_expedition days = 180 }','date > 1896.8.4 101 = { is_owned_by = A02 is_controlled_by = A02 }'),
      'polar_joint':('BLV_polar_decided','set_country_flag = BLV_arctic_open set_country_flag = BLV_joint_polar_offer add_to_variable = { SEN_readiness = 15 } add_political_power = -20 add_timed_idea = { idea = CH96_expedition days = 180 } BLV_invite_polar_partners = yes','date > 1896.8.4 101 = { is_owned_by = A02 is_controlled_by = A02 }'),
      'crowns_legal':('BLV_crowns_decided','set_country_flag = BLV_crowns_association set_global_flag = CH96_united_crowns add_ideas = CH96_crowns BLV_invite_crowns = yes','date > 1896.12.9'),
      'crowns_separate':('BLV_crowns_decided','set_country_flag = BLV_separate_courts add_political_power = 20','date > 1896.12.9'),
    }
    for name,(flag,body,gate) in policies.items():effect('apply_'+name,once(flag,body,'BLV_is_britain = yes '+gate))
    requests=[('passage','BLV_passage_decided',1,'date > 1893.11.27'),('patent','BLV_patents_decided',2,'date > 1894.10.24 has_country_flag = BLV_calibrated BLV_tesla_access = yes'),('installation','BLV_installation_decided',4,'date > 1895.5.19 has_country_flag = BLV_calibrated BLV_tesla_access = yes'),('airship','BLV_airships_decided',5,'date > 1896.5.19'),('polar','BLV_polar_decided',6,'date > 1896.8.4 101 = { is_owned_by = A02 is_controlled_by = A02 }'),('crowns','BLV_crowns_decided',8,'date > 1896.12.9')]
    for name,flag,n,gate in requests:
        effect('request_'+name+'_policy',f'if = {{ limit = {{ BLV_is_britain = yes {gate} NOT = {{ has_country_flag = {flag} }} NOT = {{ has_country_flag = BLV_{name}_question_pending }} }} set_country_flag = {{ flag = BLV_{name}_question_pending days = 45 }} country_event = {{ id = blv_story.{n} days = 1 }} }}')
    effect('invite_polar_partners',' '.join(f'if = {{ limit = {{ country_exists = {tag} NOT = {{ has_war_with = {tag} }} }} {tag} = {{ set_country_flag = {{ flag = BLV_polar_invited days = 45 }} country_event = {{ id = blv_story.7 days = 1 }} }} }}' for tag in ('A03','A04')))
    effect('invite_crowns',' '.join(f'if = {{ limit = {{ country_exists = {tag} NOT = {{ has_war_with = {tag} }} }} {tag} = {{ set_country_flag = {{ flag = BLV_crowns_invited days = 45 }} country_event = {{ id = blv_story.9 days = 1 }} }} }}' for tag in ('A06','MLT')))
    return [(k,'=',v) for k,v in effects.items()]


# Runtime guards are applied both before and after an event stays open.
RESEARCH='A02 = { has_country_flag = SEN_laboratory_done BLV_tesla_access = yes }'
EARLY='A02 = { has_country_flag = BLV_calibrated BLV_tesla_access = yes }'
LINKS={
 (1893,4):('country_exists = A06 NOT = { has_war_with = A06 }',None,('set_country_flag = BLV_valletta_cooperation A06 = { give_military_access = A02 } give_military_access = A06','set_country_flag = BLV_valletta_neutrality add_political_power = 15')),
 (1893,11):('country_exists = A02',None,('set_global_flag = BLV_ungudja_public_study add_political_power = -35 add_tech_bonus = { name = CH93_research bonus = 0.25 uses = 1 category = industry }','set_global_flag = BLV_ungudja_quarantine A02 = { add_timed_idea = { idea = CH93_patrols days = 180 } add_fuel = -3000 }')),
 (1893,15):('BLV_is_britain = yes',None,('set_country_flag = BLV_danish_protectorate add_timed_idea = { idea = CH93_patrols days = 240 } add_political_power = -25','set_country_flag = BLV_danish_volunteers add_political_power = 25')),
 (1893,18):('BLV_is_britain = yes date > 1893.6.27','serum',('BLV_apply_serum_contract = yes','BLV_apply_ethical_research = yes')),
 (1893,24):('BLV_is_britain = yes BLV_tesla_access = yes',None,('set_country_flag = BLV_andean_observations add_political_power = -40 add_to_variable = { SEN_science = 5 }','add_timed_idea = { idea = CH93_patrols days = 90 }')),
 (1893,33):('BLV_is_britain = yes','passage',('BLV_apply_passage_open = yes','BLV_apply_passage_blockade = yes')),
 (1893,39):('country_exists = A06 NOT = { has_war_with = A06 }',None,('set_global_flag = CH93_crowns_plot_exposed add_political_power = 40 A06 = { add_political_power = -40 }','set_global_flag = CH93_crowns_plot_succeeded add_stability = -0.05 A06 = { add_political_power = 40 }')),
 (1893,40):('has_global_flag = CH93_crowns_plot_exposed',None,('set_country_flag = CH93_emperor_returned add_political_power = -20 add_stability = 0.03','set_country_flag = CH93_emperor_detained add_stability = -0.05')),
 (1894,7):('country_exists = A01 country_exists = A03 NOT = { has_war_with = A01 } A01 = { has_war_with = A03 }',None,('set_country_flag = BLV_borneo_corridors A01 = { remove_ideas = CH93_blockade add_timed_idea = { idea = CH94_corridors days = 90 } } add_political_power = -25','set_country_flag = BLV_borneo_pressure add_political_power = 25 A01 = { add_stability = -0.02 }')),
 (1894,9):('country_exists = A02 NOT = { has_war_with = A02 } A02 = { has_capitulated = no has_country_flag = BLV_serum_contract NOT = { has_country_flag = BLV_ethical_research } }',None,('add_political_power = -50 A02 = { add_to_variable = { BLV_reserve = 5 } add_stability = 0.02 }','add_political_power = -15')),
 (1894,11):('1021 = { is_owned_by = A02 is_controlled_by = A02 }',None,('set_country_flag = BLV_singapore_accord clr_country_flag = BLV_singapore_curfew add_political_power = 35 add_stability = -0.02 add_timed_idea = { idea = CH94_singapore_market days = 180 }','set_country_flag = BLV_singapore_curfew clr_country_flag = BLV_singapore_accord add_stability = -0.06 add_manpower = -500 navy_experience = 10')),
 (1894,20):('OR = { has_country_flag = BLV_calibrated '+RESEARCH+' }','calibration',('BLV_apply_calibration = yes','set_country_flag = CH94_tesla_accident add_political_power = -50 add_stability = -0.03')),
 (1894,30):(EARLY,'patent',('BLV_apply_patents_private = yes','BLV_apply_patents_offer = yes')),
 (1894,33):('326 = { is_owned_by = A02 is_controlled_by = A02 }',None,('set_country_flag = BLV_hongkong_charter clr_country_flag = BLV_hongkong_curfew add_political_power = -30 add_stability = 0.04 add_equipment_to_stockpile = { type = convoy_1 amount = 5 }','set_country_flag = BLV_hongkong_curfew clr_country_flag = BLV_hongkong_charter add_political_power = 15 add_timed_idea = { idea = CH94_blockade days = 60 } add_stability = -0.03')),
 (1895,8):('1021 = { is_owned_by = A02 is_controlled_by = A02 }',None,('set_country_flag = BLV_singapore_renewed set_country_flag = BLV_singapore_accord clr_country_flag = BLV_singapore_curfew add_political_power = 30 add_stability = -0.02 add_timed_idea = { idea = CH95_port_market days = 180 }','set_country_flag = BLV_singapore_curfew clr_country_flag = BLV_singapore_accord add_manpower = -400 add_stability = -0.05 navy_experience = 10')),
 (1895,10):(EARLY,'installation',('BLV_apply_mobile_installation = yes','BLV_apply_tower_installation = yes')),
 (1895,15):('BLV_is_britain = yes',None,('set_country_flag = CH95_ceylon_relief add_political_power = -35 add_to_variable = { BLV_reserve = -5 } add_manpower = 1000 add_stability = 0.03','add_stability = -0.04 add_timed_idea = { idea = CH95_refugees days = 90 }')),
 (1896,10):('BLV_is_britain = yes','airship',('BLV_apply_airship_scouts = yes','BLV_apply_airship_strike = yes')),
 (1896,12):('tag = A07',None,('set_country_flag = CH96_australian_trade add_political_power = 25 add_equipment_to_stockpile = { type = convoy_1 amount = 10 }','add_timed_idea = { idea = CH96_quarantine days = 365 } add_stability = 0.03 add_equipment_to_stockpile = { type = convoy_1 amount = -5 }')),
 (1896,15):('101 = { is_owned_by = A02 is_controlled_by = A02 }','polar',('BLV_apply_polar_private = yes','BLV_apply_polar_joint = yes')),
 (1896,23):('BLV_is_britain = yes','crowns',('BLV_apply_crowns_legal = yes','BLV_apply_crowns_separate = yes')),
}

def sync():
    """Deterministic overlay, also called after rebuilding the author revision."""
    if not (ROOT/'common/national_focus/BLV_campaign.txt').exists():return
    effects=story_effects()
    write('common/scripted_effects/BLV_story.txt',emit(effects))
    loc={'russian':{},'english':{}};events=[]
    def text(k,ru,en):loc['russian'][k]=ru;loc['english'][k]=en
    def popup(n,title,en_title,desc,en_desc,choices,gate):
        key=f'blv_story.{n}';text(key+'.t',title,en_title);text(key+'.d',desc,en_desc)
        node=nodes(f'id = {key} title = {key}.t desc = {key}.d picture = GFX_1896_event_talks is_triggered_only = yes timeout_days = 20 trigger = {{ {gate} }}')
        for i,(ru,en,body,condition) in enumerate(choices):
            k=key+'.'+'ab'[i];text(k,ru,en)
            weights=(80,20) if n in (3,7,9) else (100,1)
            node.append(('option','=',nodes(f'name = {k} ai_chance = {{ factor = {weights[i]} }} '+(f'trigger = {{ {condition} }} ' if condition else '')+body)))
        events.append(('country_event','=',node))
    definitions=[
      (1,'Порядок прохода через Малакку','Passage Through Malacca','Подтвердить свободу прохода или распорядиться о блокаде. После утверждения приказ поступит капитанам и портовым службам.','Choose free passage or a blockade and issue the approved order to captains and harbour services.','passage_open','passage_blockade','Свободный проход','Free passage','Блокада','Blockade','date > 1893.11.27 NOT = { has_country_flag = BLV_passage_decided }'),
      (2,'Патенты раннего глушителя','Early Suppressor Patents','Чертежи ранней установки можно оставить закрытыми или предложить Палате ограниченную лицензию. Дальний глушитель сюда не входит.','Retain early designs or offer the Chamber a limited licence; this does not include the long-range suppressor.','patents_private','patents_offer','Закрытый архив','Private archive','Предложить лицензию','Offer a licence','date > 1894.10.24 has_country_flag = BLV_calibrated BLV_tesla_access = yes NOT = { has_country_flag = BLV_patents_decided }'),
      (4,'Ранние установки для флота','Early Naval Suppressors','Выбрать корабельную установку малого радиуса или стационарную башню. Технология 1895 года не заменяет дальний опыт 1900 года.','Choose a short-range ship unit or a stationary tower. The 1895 design does not replace the 1900 long-range trial.','mobile_installation','tower_installation','Корабельная установка','Ship installation','Стационарная башня','Stationary tower','date > 1895.5.19 has_country_flag = BLV_calibrated BLV_tesla_access = yes NOT = { has_country_flag = BLV_installation_decided }'),
      (5,'Программа дирижаблей','The Airship Programme','Назначить разведывательную или ударную роль программе. От решения зависят подготовка экипажей и распределение средств.','Choose reconnaissance or strike duties to determine crew training and the allocation of funds.','airship_scouts','airship_strike','Разведывательная служба','Reconnaissance service','Ударная программа','Strike programme','date > 1896.5.19 NOT = { has_country_flag = BLV_airships_decided }'),
      (6,'Мандат северной экспедиции','The Northern Expedition Mandate','Подготовить закрытый поход или пригласить партнёров. Их участие потребует согласия, а раскопки начнутся отдельно с 1898 года.','Prepare a private voyage or invite partners. Participation needs their consent; excavation is a separate project from 1898.','polar_private','polar_joint','Закрытая экспедиция','Private expedition','Пригласить партнёров','Invite partners','date > 1896.8.4 101 = { is_owned_by = A02 is_controlled_by = A02 } NOT = { has_country_flag = BLV_polar_decided }'),
      (8,'Правовое положение Совета корон','The Legal Status of the Council of Crowns','Совет может стать легальным политическим объединением изгнанных дворов. Он не заменяет действующий кабинет и не получает чужие государства.','The Council may become a legal political association of exiled courts. It replaces no cabinet and acquires no foreign state.','crowns_legal','crowns_separate','Легальное объединение','A legal association','Раздельные дворы','Separate courts','date > 1896.12.9 NOT = { has_country_flag = BLV_crowns_decided }')]
    for n,ru,en,rd,ed,a,b,ar,ae,br,be,gate in definitions:
        choices=[(ar,ae,f'BLV_apply_{a} = yes',''),(br,be,f'BLV_apply_{b} = yes','country_exists = A04 NOT = { has_war_with = A04 }' if n==2 else '')]
        popup(n,ru,en,rd,ed,choices,'BLV_is_britain = yes '+gate)
    popup(3,'Лицензия британского Адмиралтейства','An Admiralty Licence','Британия предлагает ранние чертежи за 75 политического влияния. Покупка не передаёт Теслу и не даёт артефакт.','Britain offers early drawings for 75 political power, without Tesla or the artifact.',[
      ('Приобрести лицензию','Purchase the licence','if = { limit = { has_political_power > 74 NOT = { has_war_with = A02 } A02 = { has_country_flag = BLV_patent_offer_pending NOT = { has_country_flag = BLV_patent_sale_paid } has_country_flag = BLV_calibrated BLV_tesla_access = yes } } add_political_power = -75 add_ideas = CH94_tesla A02 = { clr_country_flag = BLV_patent_offer_pending set_country_flag = BLV_patent_sale_paid set_country_flag = BLV_patents_licensed add_political_power = 75 } }','has_political_power > 74'),
      ('Отказаться','Decline','A02 = { clr_country_flag = BLV_patent_offer_pending set_country_flag = BLV_patent_offer_refused }','')],
      'tag = A04 country_exists = A02 NOT = { has_war_with = A02 } A02 = { has_country_flag = BLV_patent_offer_pending }')
    popup(7,'Приглашение в северную экспедицию','An Invitation to the Northern Expedition','Британия приглашает наблюдателей. Согласие не передаёт артефакт и не списывает средства без нашего решения.','Britain invites observers; neither artifact custody nor funds are transferred without consent.',[
      ('Направить наблюдателей','Send observers','if = { limit = { has_country_flag = BLV_polar_invited NOT = { has_war_with = A02 } A02 = { has_country_flag = BLV_joint_polar_offer } } clr_country_flag = BLV_polar_invited set_country_flag = BLV_joint_polar_member set_global_flag = CH96_joint_greenland }',''),
      ('Не участвовать','Do not participate','clr_country_flag = BLV_polar_invited','')],
      'OR = { tag = A03 tag = A04 } country_exists = A02 has_country_flag = BLV_polar_invited NOT = { has_war_with = A02 }')
    popup(9,'Объединение изгнанных корон','An Association of Exiled Crowns','Предлагается участие в политическом Совете корон. Наше правительство, правящий строй и суверенитет сохраняются.','Join a political association while preserving our government, constitution and sovereignty.',[
      ('Присоединить делегацию','Send a delegation','if = { limit = { has_country_flag = BLV_crowns_invited NOT = { has_war_with = A02 } A02 = { has_country_flag = BLV_crowns_association } } clr_country_flag = BLV_crowns_invited set_country_flag = BLV_crowns_member }',''),
      ('Сохранить отдельный двор','Keep a separate court','clr_country_flag = BLV_crowns_invited','')],
      'OR = { tag = A06 tag = MLT } country_exists = A02 has_country_flag = BLV_crowns_invited NOT = { has_war_with = A02 }')
    write('events/BLV_story.txt','add_namespace = blv_story\n'+emit(events))
    manifest=[]
    for year in range(1893,1897):
        ep=ROOT/f'events/chronicle_{year}.txt';tree=parse(ep.read_text(encoding='utf-8-sig'))
        ev={value(v,'id'):v for k,o,v in tree if k=='country_event'}
        manifests=json.loads((ROOT/f'tools/chronicle_{year}_manifest.json').read_text(encoding='utf-8'))
        for (y,n),(gate,policy,outcomes) in LINKS.items():
            if y!=year:continue
            key=f'ch{str(y)[2:]}.{n}';prefix=f'ch{str(y)[2:]}';current=ev[key]
            canonical=next(r['canonical'] for r in manifests if r['id']==n)
            owner=next(r['tag'] for r in manifests if r['id']==n)
            if owner=='A02' and not gate.startswith('BLV_is_britain'):gate='BLV_is_britain = yes '+gate
            when=datetime.strptime(next(r['date'] for r in manifests if r['id']==n),'%d.%m.%Y')-timedelta(days=1)
            gate=f'date > {when.year}.{when.month}.{when.day} '+gate
            manifest.append(dict(year=y,id=n,guard=gate,policy=policy))
            current[:]=[e for e in current if e[0] not in ('option','immediate')]
            for i,body in enumerate(outcomes):
                letter='ab'[i];weight=f'factor = {100 if i+1==canonical else 0}'
                if i+1==canonical:weight+=f' modifier = {{ factor = 0 NOT = {{ {gate} }} }}'
                else:weight+=f' modifier = {{ add = 100 NOT = {{ {gate} }} }}'
                optgate=''
                if policy=='serum':
                    opposite='BLV_ethical_research' if i==0 else 'BLV_serum_contract'
                    optgate=f'trigger = {{ NOT = {{ has_country_flag = {opposite} }} }}'
                    if i==1:weight+=' modifier = { add = 100 has_country_flag = BLV_ethical_research }'
                elif policy in ('passage','patent','installation','airship','polar','crowns'):
                    flags={'passage':('BLV_open_passage','BLV_passage_blockade'),'patent':('BLV_patents_private','BLV_patents_offered'),'installation':('CH95_tesla_mobile','CH95_tesla_stationary'),'airship':('BLV_airship_scouts','BLV_airship_strike'),'polar':('CH96_secret_greenland','BLV_joint_polar_offer'),'crowns':('BLV_crowns_association','BLV_separate_courts')}
                    forbidden=flags[policy][1-i]
                    optgate=f'trigger = {{ NOT = {{ has_country_flag = {forbidden} }} }}'
                    weight+=f' modifier = {{ add = 100 has_country_flag = {flags[policy][i]} }}'
                if policy=='patent' and i==1:optgate='trigger = { OR = { has_country_flag = BLV_patents_offered AND = { country_exists = A04 NOT = { has_war_with = A04 } NOT = { has_country_flag = BLV_patents_private } } } }'
                if policy=='calibration' and i==1:optgate='trigger = { NOT = { has_country_flag = BLV_calibrated } }'
                if policy=='calibration' and i==0:
                    optgate=f'trigger = {{ OR = {{ has_country_flag = BLV_calibrated AND = {{ {gate} }} }} }}'
                    weight+=' modifier = { add = 100 has_country_flag = BLV_calibrated }'
                if (y,n)==(1894,9) and i==0:optgate=f'trigger = {{ {gate} }}'
                # The already queued date cannot change after focus completion;
                # all effects are checked against the live situation at selection.
                wrapped=f'''name = {key}.{letter} {optgate} ai_chance = {{ {weight} }}
 if = {{ limit = {{ NOT = {{ has_global_flag = BLV_{prefix}_{n}_processed }} }}
  set_global_flag = BLV_{prefix}_{n}_processed set_global_flag = {prefix}_{n}_{letter}
  if = {{ limit = {{ {gate} }} {body} }} else = {{ set_global_flag = {prefix}_{n}_inactive }}
  A02 = {{ BLV_refresh = yes }}
  hidden_effect = {{ every_country = {{ limit = {{ is_ai = no NOT = {{ tag = ROOT }} }} country_event = {{ id = {prefix}.{100+n} }} }} }}
 }}'''
                current.append(('option','=',nodes(wrapped)))
            report=ev[f'{prefix}.{100+n}'];report[:]=[e for e in report if e[0]!='desc']
            report.extend(nodes(f'desc = {{ text = {key}.inactive trigger = {{ has_global_flag = {prefix}_{n}_inactive }} }} desc = {{ text = {key}.news_a trigger = {{ has_global_flag = {prefix}_{n}_a NOT = {{ has_global_flag = {prefix}_{n}_inactive }} }} }} desc = {{ text = {key}.news_b trigger = {{ has_global_flag = {prefix}_{n}_b NOT = {{ has_global_flag = {prefix}_{n}_inactive }} }} }}'))
            text(key+'.inactive','Обстановка изменилась: прежний план не исполнен. Действующие решения кабинета сохраняются.','Circumstances changed; the old plan was not carried out. Current cabinet policy is preserved.')
        write(str(ep.relative_to(ROOT)),emit(tree))
    # Legacy entry points must call the same result, rather than creating a second
    # prototype, replacing cabinets, or forming a faction behind the player's back.
    for year,aliases in {1894:{'CH94_tesla_secret':'BLV_apply_patents_private','CH94_tesla_sale':'BLV_apply_patents_offer'},1895:{'CH95_mobile_tesla':'BLV_apply_mobile_installation','CH95_tesla_tower':'BLV_apply_tower_installation'},1896:{'CH96_united_crowns':'BLV_apply_crowns_legal'}}.items():
        p=ROOT/f'common/scripted_effects/chronicle_{year}.txt';tree=parse(p.read_text(encoding='utf-8-sig'))
        tree=[(k,o,nodes(aliases[k]+' = yes') if k in aliases else v) for k,o,v in tree];write(str(p.relative_to(ROOT)),emit(tree))
    locale_fixes(text)
    for lang,entries in loc.items():
        write(f'localisation/{lang}/BLV_story_l_{lang}.yml','l_'+lang+':\n'+'\n'.join(f' {k}:0 "{v.replace(chr(34),chr(39))}"' for k,v in entries.items()),True)
    # Put the RU corrections into the original localization instead of relying on
    # file load order for duplicate keys. EN keys are new in this mod.
    ru=loc['russian'];own={k:v for k,v in ru.items() if not k.startswith(('ch93.','ch94.','ch95.','ch96.'))}
    write('localisation/russian/BLV_story_l_russian.yml','l_russian:\n'+'\n'.join(f' {k}:0 "{v.replace(chr(34),chr(39))}"' for k,v in own.items()),True)
    for year in range(1893,1897):
        p=ROOT/f'localisation/russian/chronicle_{year}_l_russian.yml';s=p.read_text(encoding='utf-8-sig');prefix=f'ch{str(year)[2:]}.'
        for k,v in ru.items():
            if not k.startswith(prefix):continue
            line=f' {k}:0 "{v.replace(chr(34),chr(39))}"';pat=r'^\s*'+re.escape(k)+r':0[^\n]*'
            if re.search(pat,s,re.M):s=re.sub(pat,lambda m:line,s,flags=re.M)
            else:s+='\n'+line
        write(str(p.relative_to(ROOT)),s,True)
    write('tools/british_story_links_manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
    print(f'Synchronised {len(LINKS)} chronicle events with British campaign outcomes.')

def locale_fixes(text):
    updates={
      'ch93.40.inactive':('Исход заговора не привёл к прежнему порядку изгнания. Возвращение или арест императора этим планом не навязываются.','The plot did not produce the conditions for the old expulsion plan; neither return nor arrest is imposed.'),
      'ch94.9.inactive':('Британский контракт отсутствует либо медицинская комиссия запретила поставки. Палата не оплачивает запрещённую закупку.','The British contract is absent or deliveries are banned. The Chamber does not fund a prohibited purchase.'),
      'ch94.20.inactive':('Британская приборная служба или доступ к Тесле ещё не подготовлены. Опыт отложен до восстановления необходимых условий.','Britain lacks instruments or Tesla access. The trial is deferred until its requirements are restored.'),
      'ch94.30.inactive':('Ранний глушитель не испытан либо доступ к лаборатории утрачен. Готовые чертежи пока не предлагаются к продаже.','The early suppressor is untested or laboratory access is lost. Finished drawings cannot yet be offered for sale.'),
      'ch95.10.inactive':('Для установки ещё нет испытанного раннего глушителя или доступа к Тесле. Программа ждёт подготовки лаборатории.','The installation lacks a tested early suppressor or Tesla access. The programme awaits laboratory preparation.'),
      'ch96.15.inactive':('Британия не владеет Гренландией и не контролирует место подготовки. Прежний мандат экспедиции не исполняется.','Britain lacks ownership or control of Greenland. The old expedition mandate cannot be carried out.'),
      'ch93.18.d':('28.06.1893. Рассмотреть лицензию Фонда Дюбуа или пресечь деятельность ферм. Если медицинская политика уже выбрана фокусом, она сохраняется.','28 June 1893. Consider a Dubois licence or close the blood farms. A policy already chosen by focus is preserved.'),
      'ch93.18.news_a':('Британия разрешила лицензированный контракт Фонда Дюбуа.','Britain authorised a licensed Dubois contract.'),
      'ch93.18.b':('Закрыть фермы крови','Close the blood farms'),
      'ch93.18.news_b':('Британская комиссия запретила принудительный сбор крови.','A British commission banned coerced blood collection.'),
      'ch94.9.news_a':('Палата оплачивает поставки по действующему британскому контракту.','The Chamber funds deliveries under the current British contract.'),
      'ch94.7.a':('Гуманитарные коридоры','Humanitarian corridors'),
      'ch94.7.news_a':('Британия добилась коридоров снабжения. Борнейская война этим решением не прекращается.','Britain secured supply corridors. This decision does not end the Borneo war.'),
      'ch94.20.d':('20.07.1894. Проверить ранний глушитель отдельного объекта. Участие Британии требует приборной службы и доступа к Тесле; без них опыт откладывается.','20 July 1894. Test an early site suppressor. British participation requires instruments and Tesla access; otherwise the trial is deferred.'),
      'ch94.20.news_a':('Проверен ранний глушитель отдельного объекта. Это не дальний прототип и не разрешение заселять материки.','An early site suppressor has been tested; it is neither a long-range prototype nor permission to resettle continents.'),
      'ch94.20.b':('Отложить или остановить опыт','Defer or stop the trial'),
      'ch94.20.news_b':('Ранний опыт приостановлен; дальнейшая работа потребует подготовки и доступа к лаборатории.','The early trial was suspended; further work requires preparation and laboratory access.'),
      'ch94.30.news_a':('Ранние чертежи оставлены в закрытом архиве.','The early drawings were retained in a private archive.'),
      'ch94.30.t':('Патенты раннего глушителя','Early Suppressor Patents'),
      'ch94.30.d':('25.10.1894. Сохранить ранние чертежи в архиве или предложить Палате ограниченную лицензию. Продажа требует её согласия.','25 October 1894. Retain early drawings or offer the Chamber a limited licence, subject to its consent.'),
      'ch94.30.b':('Предложить лицензию','Offer a licence'),
      'ch94.30.news_b':('Британия предложила Палате лицензию на ранние чертежи. Покупка ещё требует согласия Палаты.','Britain offered early designs to the Chamber. The purchase still requires Chamber consent.'),
      'ch95.8.t':('Исполнение Сингапурского договора','Implementing the Singapore Settlement'),
      'ch95.8.d':('22.04.1895. Пересмотреть портовые договорённости 1894 года: продлить соглашение или ввести силовой контроль. Речь идёт о порядке в порту, а не передаче его территории.','22 April 1895. Renew or replace the 1894 port settlement without transferring Singapore\'s territory.'),
      'ch95.8.news_a':('Продлены договорённости о торговле и портовом надзоре в Сингапуре.','Singapore\'s trade and port-supervision arrangements were renewed.'),
      'ch95.10.t':('Ранние глушители для кораблей и баз','Early Suppressors for Ships and Bases'),
      'ch95.10.d':('20.05.1895. Выбрать установку малого радиуса для корабля или стационарную башню. Участие требует раннего прототипа и доступа к Тесле.','20 May 1895. Select a short-range ship unit or stationary tower, requiring an early prototype and Tesla access.'),
      'ch95.10.news_a':('Для ранней программы выбрана корабельная установка малого радиуса.','The early programme selected a short-range ship installation.'),
      'ch95.10.news_b':('Для ранней программы выбрана стационарная башня.','The early programme selected a stationary tower.'),
      'ch96.10.d':('20.05.1896. Утвердить разведывательную или ударную программу дирижаблей. Фокус службы и календарное решение используют один результат.','20 May 1896. Approve a reconnaissance or strike airship programme; the focus and dated event share one result.'),
      'ch96.10.news_a':('Учреждена разведывательная программа дирижаблей.','A reconnaissance airship programme was established.'),
      'ch96.10.news_b':('Учреждена ударная программа дирижаблей.','A strike airship programme was established.'),
      'ch96.12.d':('28.06.1896. Правительство [A07.GetName] определяет режим торговли. Это решение не подразумевает объединения остальных австралийских колоний.','28 June 1896. [A07.GetName] sets its trade policy without implying union with the other Australian colonies.'),
      'ch96.12.news_a':('Правительство [A07.GetName] открыло торговые рейсы.','The government of [A07.GetName] opened commercial voyages.'),
      'ch96.12.news_b':('Правительство [A07.GetName] ограничило заход иностранных судов.','The government of [A07.GetName] restricted foreign shipping.'),
      'ch96.15.d':('05.08.1896. Выбрать закрытую рекогносцировку или пригласить иностранных наблюдателей. Участие партнёров требует согласия; артефакт этим решением не выдаётся.','5 August 1896. Choose private reconnaissance or invite foreign observers. Partners must consent; no artifact is awarded.'),
      'ch96.15.news_a':('Британия усиливает снабжение северных станций. Подробности похода не раскрываются.','Britain is reinforcing northern stations; voyage details remain undisclosed.'),
      'ch96.15.news_b':('Британия направила приглашения иностранным наблюдателям северной экспедиции.','Britain invited foreign observers to its northern expedition.'),
      'ch96.23.d':('10.12.1896. Определить правовое положение Совета корон как политического объединения. Действующие кабинеты, строй и суверенитет стран сохраняются.','10 December 1896. Settle the Council of Crowns\' legal status as a political association without replacing governments or changing sovereignty.'),
      'ch96.23.a':('Легальный Совет корон','A legal Council of Crowns'),
      'ch96.23.b':('Раздельные дворы','Separate courts'),
      'ch96.23.news_a':('В Британии разрешено политическое объединение Совета корон. Иностранные дворы получают приглашения, а не новое правительство.','Britain authorised a political Council of Crowns. Foreign courts receive invitations, not replacement governments.'),
      'ch96.23.news_b':('Дворы сохранили отдельные политические представительства. Война этим решением не объявляется.','The courts retain separate political representation. This decision declares no war.'),
    }
    for k,(ru,en) in updates.items():text(k,ru,en)

def write(path,text,bom=False):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.rstrip()+'\n',encoding='utf-8-sig' if bom else 'utf-8')

if __name__=='__main__':sync()
