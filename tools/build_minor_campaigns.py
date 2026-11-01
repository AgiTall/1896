"""Source builder for the playable small-state campaigns (no map/history changes)."""
from pathlib import Path
import json,re
from minor_campaign_profiles import PROFILES

ROOT=Path(__file__).resolve().parents[1]
LOC={'russian':{},'english':{}}
FX=[];TR=[];IDEAS=[];DEC=[];EVENTS=['add_namespace = mnr_campaign'];MANIFEST={}

def write(path,text,bom=False):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text.rstrip()+'\n',encoding='utf-8-sig' if bom else 'utf-8')

def loc(key,ru,en):
    assert key not in LOC['russian'],key
    LOC['russian'][key]=ru;LOC['english'][key]=en

def fx(key,body):FX.append(f'{key} = {{\n{body}\n}}')
def tr(key,body):TR.append(f'{key} = {{ {body} }}')
def idea(key,ru,en,mods):
    loc(key,ru,en);loc(key+'_desc',ru+'.',en+'.')
    IDEAS.append(f'{key} = {{ picture = generic_pp_unity_bonus removal_cost = -1 modifier = {{ {mods} }} }}')

def event(eid,ru,en,rd,ed,opts,gate):
    loc(eid+'.t',ru,en);loc(eid+'.d',rd,ed)
    body=[]
    for key,r,e,fxbody,trigger,ai in opts:
        lk=eid+'.'+key;loc(lk,r,e)
        body.append(f'option = {{ name = {lk} '+(f'trigger = {{ {trigger} }} ' if trigger else '')+f'ai_chance = {{ factor = {ai} }} {fxbody} }}')
    EVENTS.append(f'country_event = {{ id = {eid} title = {eid}.t desc = {eid}.d picture = GFX_1896_event_talks is_triggered_only = yes timeout_days = 20 trigger = {{ {gate} }} '+'\n'.join(body)+'\n}')

def decision(key,ru,en,rd,ed,visible,available,effect,cost=35,days=0,finish='',cancel='',cancel_effect='clr_country_flag = MNR_project_active'):
    loc(key,ru,en);loc(key+'_desc',rd,ed)
    timed=(f'days_remove = {days} cancel_if_not_visible = yes cancel_trigger = {{ {cancel} }} remove_effect = {{ {finish} MNR_refresh = yes }} cancel_effect = {{ {cancel_effect} }}' if days else '')
    DEC.append(f'{key} = {{ icon = generic_prepare_civil_war visible = {{ {visible} }} available = {{ {available} }} cost = {cost} fire_only_once = no ai_will_do = {{ factor = 1 }} complete_effect = {{ {effect} MNR_refresh = yes }} {timed} }}')

def building(kind):
    return f'capital_scope = {{ if = {{ limit = {{ is_owned_by = ROOT is_controlled_by = ROOT }} add_extra_state_shared_building_slots = 1 add_building_construction = {{ type = {kind} level = 1 instant_build = yes }} }} }}'

def base():
    for key,ru,en in [
      ('MNR_reserve','Местные запасы','Local Reserves'),('MNR_mandate','Доверие общин','Community Confidence'),('MNR_progress','Завершённые национальные проекты','Completed National Projects'),
      ('MNR_civic','Принят гражданский порядок','Civil Administration Chosen'),('MNR_command','Принят командный порядок','Command Administration Chosen'),('MNR_contacts','Открыты внешние переговоры','External Talks Open'),
      ('MNR_project_active','Национальный проект в работе','National Project Underway'),('MNR_yard_active','Заказ эскортов в работе','Escort Order Underway'),('MNR_escorts_delivered','Эскорты уже переданы','Escorts Already Delivered'),
      ('MNR_insured','Учреждено местное страхование','Local Insurance Established'),('MNR_replenish_cooldown','Недавняя закупка запасов','Recent Reserve Purchase'),('MNR_hearing_cooldown','Недавние слушания общин','Recent Community Hearings'),
      ('MNR_hawaii_succession','Завершена гавайская преемственность','Hawaiian Succession Settled')]:loc(key,ru,en)
    tr('MNR_is_minor','OR = { '+' '.join(f'tag = {t}' for t in PROFILES)+' }')
    tr('MNR_home_secure','exists = yes has_capitulated = no capital_scope = { is_owned_by = ROOT is_controlled_by = ROOT }')
    tr('MNR_has_route','OR = { has_country_flag = MNR_civic has_country_flag = MNR_command }')
    fx('MNR_initialize','''if = { limit = { MNR_is_minor = yes NOT = { has_country_flag = MNR_initialized } }
 set_country_flag = MNR_initialized set_variable = { MNR_reserve = 40 } set_variable = { MNR_mandate = 45 } set_variable = { MNR_progress = 0 }
 WTC_initialize_effect = yes
 if = { limit = { tag = MLT NOT = { has_country_flag = SEN_initialized } } set_country_flag = SEN_initialized set_variable = { SEN_science = 0 } set_variable = { SEN_readiness = 0 } set_variable = { SEN_security = 20 } set_variable = { SEN_exposure = 0 } }
}''')
    fx('MNR_refresh','''if = { limit = { MNR_is_minor = yes has_country_flag = MNR_initialized }
 clamp_variable = { var = MNR_reserve min = 0 max = 100 } clamp_variable = { var = MNR_mandate min = 0 max = 100 } clamp_variable = { var = MNR_progress min = 0 max = 3 }
 if = { limit = { check_variable = { MNR_reserve < 25 } } add_ideas = MNR_shortages } else = { remove_ideas = MNR_shortages }
 if = { limit = { check_variable = { MNR_mandate < 25 } } add_ideas = MNR_discontent } else = { remove_ideas = MNR_discontent }
}''')
    fx('MNR_monthly','''MNR_initialize = yes
if = { limit = { has_war = yes } subtract_from_variable = { MNR_reserve = 1 } }
if = { limit = { has_idea = MNR_civic_service has_war = no } add_to_variable = { MNR_mandate = 1 } }
MNR_refresh = yes''')
    idea('MNR_shortages','Истощённые местные запасы','Depleted Local Reserves','supply_consumption_factor = 0.08 production_factory_efficiency_gain_factor = -0.05')
    idea('MNR_discontent','Недоверие общин','Community Distrust','political_power_gain = -0.15 stability_factor = -0.05')
    idea('MNR_civic_service','Подотчётное местное правление','Accountable Local Administration','stability_factor = 0.05 production_speed_industrial_complex_factor = 0.08')
    idea('MNR_command_service','Система территориального командования','Territorial Command System','army_defence_factor = 0.05 training_time_factor = -0.08')
    idea('MNR_network_service','Согласованное портовое обслуживание','Agreed Harbour Services','supply_consumption_factor = -0.03')
    idea('MNR_emergency','Чрезвычайные караулы','Emergency Watch','army_defence_factor = 0.04 stability_factor = -0.03')
    idea('MNR_repair_service','Восстановительные бригады','Restoration Crews','industry_repair_factor = 0.15')
    idea('MNR_self_insurance','Местный страховой резерв','Local Insurance Reserve','convoy_escort_efficiency = 0.04')
    loc('MNR_campaign_category','Местное правительство и национальные проекты','Local Government and National Projects')
    loc('MNR_campaign_category_desc','Запасы: [?MNR_reserve|0] / 100. Доверие общин: [?MNR_mandate|0] / 100. Завершённые проекты: [?MNR_progress|0] / 3.\nКаждый военный месяц расходует 1 единицу запасов. При показателе ниже 25 страна получает штраф. Проект оплачивается при запуске и прерывается без награды при потере контроля над столицей. Договоры требуют согласия партнёра и действуют два года.','Reserves: [?MNR_reserve|0] / 100. Community confidence: [?MNR_mandate|0] / 100. Completed projects: [?MNR_progress|0] / 3.\nEach month of war consumes 1 reserve. Values below 25 cause penalties. Projects are paid for at launch and cancel without reward if the capital is lost. Agreements require consent and last two years.')
    decision('MNR_replenish','Закупить местные запасы','Purchase Local Reserves','35 политической власти: +20 запасов. Повторно через 90 дней.','35 political power: +20 reserves. Repeat after 90 days.','MNR_is_minor = yes has_country_flag = MNR_initialized','MNR_home_secure = yes check_variable = { MNR_reserve < 81 } NOT = { has_country_flag = MNR_replenish_cooldown }','add_to_variable = { MNR_reserve = 20 } set_country_flag = { flag = MNR_replenish_cooldown days = 90 }')
    decision('MNR_local_hearing','Провести слушания общин','Hold Community Hearings','25 политической власти и 5 запасов: +8 доверия. Повторно через 60 дней.','25 political power and 5 reserves: +8 confidence. Repeat after 60 days.','MNR_is_minor = yes has_country_flag = MNR_initialized','MNR_home_secure = yes check_variable = { MNR_reserve > 4 } check_variable = { MNR_mandate < 93 } NOT = { has_country_flag = MNR_hearing_cooldown }','subtract_from_variable = { MNR_reserve = 5 } add_to_variable = { MNR_mandate = 8 } set_country_flag = { flag = MNR_hearing_cooldown days = 60 }',cost=25)
    decision('MNR_insure','Учредить местное страхование','Establish Local Insurance','При отсутствии внешнего договора можно вложить 75 политической власти и 15 запасов в собственное страхование перевозок.','Without an external agreement, invest 75 political power and 15 reserves in local transport insurance.','MNR_is_minor = yes has_country_flag = MNR_contacts','MNR_home_secure = yes check_variable = { MNR_reserve > 14 } NOT = { has_country_flag = MNR_insured }','subtract_from_variable = { MNR_reserve = 15 } set_country_flag = MNR_insured add_ideas = MNR_self_insurance',cost=75)

def diplomacy():
    edges=[(tag,partner) for tag,p in PROFILES.items() for partner in p['partners']]
    directed=set(edges)|{(b,a) for a,b in edges}
    cases=[]
    for a,b in sorted(directed):
        cases.append(f'AND = {{ tag = {a} country_exists = {b} has_country_flag = MNR_pact_{b} NOT = {{ has_war_with = {b} }} {b} = {{ has_capitulated = no has_country_flag = MNR_pact_{a} }} }}')
    for tag in sorted({b for a,b in directed}):
        loc('MNR_pact_'+tag,f'Действует договор: [{tag}.GetName]',f'Active Agreement: [{tag}.GetName]')
        loc('MNR_pending_'+tag,f'Ожидается ответ: [{tag}.GetName]',f'Awaiting Reply: [{tag}.GetName]')
        loc('MNR_cooldown_'+tag,f'Недавнее предложение: [{tag}.GetName]',f'Recent Offer: [{tag}.GetName]')
    tr('MNR_has_live_partner','has_capitulated = no OR = { '+' '.join(cases)+' }')
    cleanup=[]
    for a,b in sorted(directed):
        cleanup.append(f'''if = {{ limit = {{ tag = {a} has_country_flag = MNR_pact_{b} OR = {{ has_capitulated = yes NOT = {{ country_exists = {b} }} has_war_with = {b} {b} = {{ OR = {{ has_capitulated = yes NOT = {{ has_country_flag = MNR_pact_{a} }} }} }} }} }}
 clr_country_flag = MNR_pact_{b} if = {{ limit = {{ country_exists = {b} }} {b} = {{ clr_country_flag = MNR_pact_{a} }} }} }}''')
    cleanup.append('if = { limit = { MNR_has_live_partner = yes } add_ideas = MNR_network_service } else = { remove_ideas = MNR_network_service }')
    fx('MNR_refresh_network','\n'.join(cleanup))
    for n,(a,b) in enumerate(edges,1):
        eid=f'mnr_campaign.{100+n}';key=f'MNR_{a}_offer_{b}'
        guard=f'country_exists = {a} country_exists = {b} {a} = {{ has_capitulated = no has_country_flag = MNR_pending_{b} NOT = {{ has_war_with = {b} }} NOT = {{ has_country_flag = MNR_pact_{b} }} }} has_capitulated = no NOT = {{ has_country_flag = MNR_pact_{a} }}'
        accept=f'''if = {{ limit = {{ {guard} }}
 set_country_flag = {{ flag = MNR_pact_{a} days = 730 }}
 {a} = {{ clr_country_flag = MNR_pending_{b} set_country_flag = {{ flag = MNR_pact_{b} days = 730 }}
 if = {{ limit = {{ NOT = {{ has_country_flag = MNR_rewarded_{b} }} }} set_country_flag = MNR_rewarded_{b} add_to_variable = {{ MNR_mandate = 5 }} }} MNR_refresh = yes MNR_refresh_network = yes country_event = {{ id = mnr_campaign.2 }} }}
 MNR_refresh_network = yes }}'''
        event(eid,'Предложение: портовое обслуживание','Offer: Harbour Services',f'Правительство [${a}.GetName] предлагает на два года согласовать снабжение и обслуживание портов. Обе стороны получат снижение расхода припасов на 3%. Договор не меняет суверенитет и прекратится в случае войны между участниками.',f'The government of [${a}.GetName] proposes two years of harbour and supply cooperation. Both sides gain 3% lower supply use. The agreement ends if the participants go to war.'.replace('[$','['),[
            ('a','Принять договор','Accept the Agreement',accept,guard,65),
            ('b','Отклонить предложение','Decline',f'{a} = {{ clr_country_flag = MNR_pending_{b} }}','',35)],f'tag = {b}')
        # Localisation scopes use literal country tags, not shell-style dollar prefixes.
        for lang in LOC:LOC[lang][eid+'.d']=LOC[lang][eid+'.d'].replace('[$','[')
        decision(key,f'Предложить обслуживание: [{b}.GetName]',f'Offer Harbour Services: [{b}.GetName]',f'Направить предложение стране [{b}.GetName]. Стоимость — 25 политической власти; партнёр вправе отказаться. Новое предложение через 180 дней.',f'Send an offer to [{b}.GetName]. Costs 25 political power; the recipient may decline. Repeat after 180 days.',f'tag = {a} has_country_flag = MNR_contacts',f'MNR_home_secure = yes country_exists = {b} {b} = {{ has_capitulated = no }} NOT = {{ has_war_with = {b} }} NOT = {{ has_country_flag = MNR_pact_{b} }} NOT = {{ has_country_flag = MNR_pending_{b} }} NOT = {{ has_country_flag = MNR_cooldown_{b} }}',f'set_country_flag = {{ flag = MNR_pending_{b} days = 45 }} set_country_flag = {{ flag = MNR_cooldown_{b} days = 180 }} {b} = {{ country_event = {{ id = {eid} }} }}',cost=25)
    event('mnr_campaign.2','Договор вступил в силу','Agreement in Force','Партнёр принял предложение. Условия обслуживания действуют два года, пока оба правительства существуют и не воюют друг с другом.','The partner accepted. Services last two years while both governments exist and remain at peace with each other.',[('a','Передать условия капитанам','Notify the Captains','','',100)],'MNR_is_minor = yes')

def mission(p):
    t=p['tag'];k=p['kind'];key=f'MNR_{t}_project'
    costs={'convoy':(45,6,35,'has_equipment = { convoy_1 > 2 }','add_equipment_to_stockpile = { type = convoy_1 amount = -1 }',15,5),
      'relief':(45,12,35,'','',4,10),
      'defence':(45,6,35,'has_equipment = { infantry_equipment > 99 }','add_equipment_to_stockpile = { type = infantry_equipment amount = -100 }',0,6),
      'survey':(60,6,35,'has_equipment = { support_equipment > 24 }','add_equipment_to_stockpile = { type = support_equipment amount = -25 }',0,5),
      'repair':(60,10,35,'','',0,6),
      'finance':(60,5,55,'','',0,5),
      'science':(60,10,35,'has_equipment = { support_equipment > 24 }','add_equipment_to_stockpile = { type = support_equipment amount = -25 }',0,5),
      'customs':(45,8,35,'','',12,4)}
    days,reserve,pp,gate,paid,back,mandate=costs[k]
    bonus={'convoy':'navy_experience = 3','defence':'army_experience = 5','survey':'add_tech_bonus = { name = MNR_route_survey bonus = 0.25 uses = 1 category = industry }','repair':'add_timed_idea = { idea = MNR_repair_service days = 180 }','finance':'subtract_from_variable = { WTC_debt = 8 } clamp_variable = { var = WTC_debt min = 0 max = 200 }','science':'add_to_variable = { SEN_science = 5 }','relief':'add_stability = 0.01','customs':'navy_experience = 2'}[k]
    r=f'{days} дней; {pp} политической власти, {reserve} запасов'
    e=f'{days} days; {pp} political power, {reserve} reserves'
    if k=='convoy':r+=', 1 транспорт';e+=', 1 convoy'
    if k=='defence':r+=', 100 винтовок';e+=', 100 rifles'
    if k in ('survey','science'):r+=', 25 единиц дополнительного оснащения';e+=', 25 support equipment'
    payoff={'convoy':('3 опыта флота','3 naval XP'),'defence':('5 опыта армии','5 army XP'),'survey':('одна скидка 25% на промышленное исследование','one 25% industry research bonus'),'repair':('ускорение ремонта на 180 дней','180 days of faster repair'),'finance':('долг Палате уменьшается на 8','Chamber debt decreases by 8'),'science':('5 очков общей научной готовности','5 shared science points'),'relief':('1% стабильности','1% stability'),'customs':('2 опыта флота','2 naval XP')}[k]
    r+=f'. Награда: {back} запасов, {mandate} доверия, 1 завершённый проект; {payoff[0]}. Требуется собственная контролируемая столица. Всего три проекта.'
    e+=f'. Reward: {back} reserves, {mandate} confidence, 1 completed project; {payoff[1]}. Requires an owned, controlled capital. Maximum three projects.'
    finish=f'''if = {{ limit = {{ MNR_home_secure = yes has_country_flag = MNR_project_active check_variable = {{ MNR_progress < 3 }} }}
 clr_country_flag = MNR_project_active add_to_variable = {{ MNR_progress = 1 }} add_to_variable = {{ MNR_reserve = {back} }} add_to_variable = {{ MNR_mandate = {mandate} }} {bonus}
 if = {{ limit = {{ NOT = {{ has_country_flag = MNR_project_reported }} }} set_country_flag = MNR_project_reported country_event = {{ id = mnr_campaign.{300+list(PROFILES).index(t)} }} }} }}'''
    decision(key,p['project'],p['project_en'],r,e,f'tag = {t} has_country_flag = MNR_projects_open',f'MNR_home_secure = yes NOT = {{ has_country_flag = MNR_project_active }} check_variable = {{ MNR_progress < 3 }} check_variable = {{ MNR_reserve > {reserve-1} }} {gate}',f'set_country_flag = MNR_project_active subtract_from_variable = {{ MNR_reserve = {reserve} }} {paid}',cost=pp,days=days,finish=finish,cancel='NOT = { MNR_home_secure = yes }')

def goal(p):
    obj=p['objective'];t=p['tag'];extra='';res=35;mandate=65
    owned=lambda n:f'{n} = {{ is_owned_by = ROOT is_controlled_by = ROOT }}'
    if obj=='caribbean':extra=owned(315)+' '+owned(686)+' OR = { MNR_has_live_partner = yes has_country_flag = MNR_insured }'
    elif obj=='two_shores':extra=owned(1083)+' '+owned(319)
    elif obj=='hawaii':extra='has_country_flag = MNR_hawaii_succession '+owned(629)
    elif obj=='science':extra='check_variable = { SEN_science > 14 } '+owned(116)
    elif obj=='north':res=60;mandate=70;extra=owned(536)
    elif obj=='debt':extra='check_variable = { WTC_debt < 51 }'
    elif obj=='trade':extra='OR = { MNR_has_live_partner = yes has_country_flag = MNR_insured }'
    return f'MNR_home_secure = yes check_variable = {{ MNR_progress > 2 }} check_variable = {{ MNR_reserve > {res-1} }} check_variable = {{ MNR_mandate > {mandate-1} }} MNR_has_route = yes {extra}'

def maritime_contracts():
    """Small, paid escort orders; no free fleets on country initialization."""
    ports={'A05':7622,'PHW':4180,'MLT':12003,'PSL':1421,'PSY':2188,'A12':1316,'PCB':12118,'PVI':1261}
    # Resolve the actual naval base from the state history for released countries.
    from validate_philippines_rework import parse,value
    coast={int(row.split(';')[0]) for row in (ROOT/'map/definition.csv').read_text(encoding='utf-8-sig').splitlines() if len(row.split(';'))>5 and row.split(';')[5]=='true'}
    for tag,port in ports.items():
        state=PROFILES[tag]['capital']
        paths=list((ROOT/'history/states').glob(str(state)+'-*'))+list((ROOT/'history/states').glob(str(state)+' -*'))
        assert len(paths)==1,(tag,paths)
        state_node=value(parse(paths[0].read_text(encoding='utf-8-sig')),'state');hist=value(state_node,'history')
        bases=[int(k) for k,o,v in value(hist,'buildings') if k.isdigit() and isinstance(v,list) and value(v,'naval_base')]
        missing_port=not bases
        if missing_port:bases=[int(k) for k,o,v in value(state_node,'provinces') if int(k) in coast]
        assert bases,(tag,'missing coast');port=bases[0]
        port_work=f'add_building_construction = {{ type = naval_base province = {port} level = 1 instant_build = yes }}' if missing_port else ''
        version='Local Escort '+tag
        modules='fixed_ship_battery_slot = ship_light_battery_1 fixed_ship_radar_slot = empty fixed_ship_engine_slot = light_ship_engine_1 fixed_ship_torpedo_slot = ship_torpedo_1 mid_1_custom_slot = empty rear_1_custom_slot = empty'
        for legacy in (False,True):
            typ='destroyer_1' if legacy else 'ship_hull_light_1';suffix='_legacy' if legacy else ''
            variant='' if legacy else f'version_name = "{version}"'
            ships='\n'.join(f'ship = {{ name = "{tag} Coastal Escort {i+1}" definition = destroyer start_experience_factor = 0.1 equipment = {{ {typ} = {{ amount = 1 owner = {tag} {variant} }} }} }}' for i in range(2))
            write(f'history/units/MNR_{tag}_escorts{suffix}.txt',f'units = {{ fleet = {{ name = "{tag} Coastal Service" naval_base = {port} task_force = {{ name = "{tag} Local Escort Division" location = {port} {ships} }} }} }}')
        secure=f'MNR_home_secure = yes {state} = {{ is_owned_by = ROOT is_controlled_by = ROOT }}'
        fx(f'MNR_{tag}_commission_escorts',f'''if = {{ limit = {{ {secure} has_country_flag = MNR_yard_active NOT = {{ has_country_flag = MNR_escorts_delivered }} }}
 clr_country_flag = MNR_yard_active set_country_flag = MNR_escorts_delivered
 {state} = {{ add_extra_state_shared_building_slots = 1 add_building_construction = {{ type = dockyard level = 1 instant_build = yes }} {port_work} }}
 if = {{ limit = {{ has_dlc = "Man the Guns" }}
  set_technology = {{ early_ship_hull_light = 1 }}
  create_equipment_variant = {{ name = "{version}" type = ship_hull_light_1 parent_version = 0 modules = {{ {modules} }} }} load_oob = MNR_{tag}_escorts
 }} else = {{ set_technology = {{ early_destroyer = 1 }} load_oob = MNR_{tag}_escorts_legacy }}
}}''')
        decision(f'MNR_{tag}_escort_order','Заказать два прибрежных эскорта','Order Two Coastal Escorts','После первого национального проекта и оружейных мастерских можно вложить 75 политической власти, 25 запасов и 50 единиц дополнительного оснащения в морскую службу. Через 90 дней: два малых эскорта и одна верфь в исходной столице. Один заказ за кампанию; потеря столичного порта отменяет заказ без награды.','After the first national project and arms workshops, spend 75 political power, 25 reserves and 50 support equipment on a coastal service. After 90 days: two light escorts and a dockyard in the original capital. Once per campaign; losing the harbour cancels the order without reward.',f'tag = {tag} has_completed_focus = MNR_{tag}_defence2 check_variable = {{ MNR_progress > 0 }}',f'{secure} NOT = {{ has_country_flag = MNR_yard_active }} NOT = {{ has_country_flag = MNR_escorts_delivered }} check_variable = {{ MNR_reserve > 24 }} has_equipment = {{ support_equipment > 49 }}','set_country_flag = MNR_yard_active subtract_from_variable = { MNR_reserve = 25 } add_equipment_to_stockpile = { type = support_equipment amount = -50 }',cost=75,days=90,finish=f'MNR_{tag}_commission_escorts = yes',cancel=f'NOT = {{ {secure} }}',cancel_effect='clr_country_flag = MNR_yard_active')
        MANIFEST[tag]['escort_port']=port

def country(p,index):
    tag=p['tag'];prefix='MNR_'+tag+'_';focuses=[];rows=[]
    def focus(key,ru,en,rd,ed,x,y,parents=(),reward='',gate='',exclude=None,cost=5,icon='GFX_goal_generic_national_unity'):
        fid=prefix+key;loc(fid,ru,en);loc(fid+'_desc',rd,ed)
        pre=' '.join(f'prerequisite = {{ focus = {prefix}{parent} }}' for parent in parents)
        exc=f'mutually_exclusive = {{ focus = {prefix}{exclude} }}' if exclude else ''
        focuses.append(f'focus = {{ id = {fid} icon = {icon} x = {x} y = {y} cost = {cost} {pre} {exc} available = {{ MNR_home_secure = yes {gate} }} cancel_if_invalid = yes ai_will_do = {{ factor = 5 }} completion_reward = {{ {reward} MNR_refresh = yes }} }}')
        rows.append(dict(id=fid,x=x,y=y,parents=[prefix+x for x in parents]))
    start=f'''MNR_initialize = yes add_political_power = 40
 if = {{ limit = {{ NOT = {{ has_country_flag = MNR_crisis_queued }} }} set_country_flag = MNR_crisis_queued country_event = {{ id = mnr_campaign.{200+index} days = 240 random_days = 30 }} }}'''
    focus('root',p['ru']+': собственный путь',p['en']+': Our Own Course',p['opening'],p['opening_en'],10,0,reward=start)
    econmod={'convoy':'convoy_escort_efficiency = 0.08','relief':'consumer_goods_factor = -0.03','survey':'production_speed_infrastructure_factor = 0.12','defence':'supply_consumption_factor = -0.04','science':'research_speed_factor = 0.03','customs':'political_power_gain = 0.10','finance':'production_factory_efficiency_gain_factor = 0.08','repair':'industry_repair_factor = 0.15'}[p['kind']]
    idea(prefix+'economy_spirit',p['economy'][2],p['economy_en'][2],econmod)
    for n in range(3):
        rewards=['add_to_variable = { MNR_reserve = 8 }',building('industrial_complex'),'add_ideas = '+prefix+'economy_spirit']
        focus('economy'+str(n),p['economy'][n],p['economy_en'][n],['Сверить местные запасы: +8 запасов.','Расширить мастерские столицы: одна гражданская фабрика.','Закрепить местную хозяйственную специализацию национальным духом.'][n],['Audit local stores: +8 reserves.','Expand capital workshops: one civilian factory.','Secure local economic specialisation through a national spirit.'][n],2,2+n*2,parents=('root' if n==0 else 'economy'+str(n-1),),reward=rewards[n],cost=10 if n==1 else 5,icon='GFX_goal_generic_construct_civ_factory')
    template=f'''if = {{ limit = {{ NOT = {{ has_country_flag = MNR_template_ready }} }} set_country_flag = MNR_template_ready load_oob = MNR_{tag}_template }} add_equipment_to_stockpile = {{ type = infantry_equipment_0 amount = 200 producer = ROOT }} army_experience = 5'''
    for n in range(3):
        rewards=[template,'subtract_from_variable = { MNR_reserve = 5 } add_timed_idea = { idea = MNR_emergency days = 365 }',building('arms_factory')]
        focus('defence'+str(n),p['defence'][n],p['defence_en'][n],['Открыть лёгкий шаблон из двух пехотных батальонов, получить 200 винтовок и 5 опыта армии. Новые дивизии набираются обычным порядком.','За 5 запасов организовать местные караулы на один год.','Оборудовать оружейное предприятие в собственной контролируемой столице.'][n],['Unlock a two-battalion infantry template, 200 rifles and 5 army XP. Recruit divisions normally.','Spend 5 reserves on a year of local defence watches.','Build an arms workshop in the owned and controlled capital.'][n],10,2+n*2,parents=('root' if n==0 else 'defence'+str(n-1),),reward=rewards[n],gate='check_variable = { MNR_reserve > 4 }' if n==1 else '',cost=10 if n==2 else 5,icon='GFX_goal_generic_defence')
    focus('contacts','Переговоры с соседями','Talks with Our Neighbours','Открыть два двусторонних предложения. Партнёр вправе отказаться; для итоговой цели существует местное страхование.','Open two bilateral proposals. Partners may decline; local insurance offers an alternative for the final objective.',18,2,parents=('root',),reward='set_country_flag = MNR_contacts add_political_power = 25',icon='GFX_goal_generic_improve_relations')
    focus('chamber','Собственный стол Палаты','Our Own Chamber Desk','Открыть действующую систему контрактов Палаты. Прежний долг и договоры сохраняются.','Open the existing Chamber contract network, preserving previous debt and agreements.',18,4,parents=('contacts',),reward='WTC_initialize_effect = yes set_country_flag = WTN_compact_desk_open set_country_flag = WTN_relations_open',icon='GFX_goal_generic_trade')
    for civic,x in [(True,6),(False,14)]:
        route='civic' if civic else 'command';other='command' if civic else 'civic'
        effect=f'set_country_flag = MNR_{route} add_ideas = MNR_{route}_service add_to_variable = {{ MNR_mandate = {8 if civic else -4} }}'
        if tag=='PHW':effect+=' MNR_hawaii_apply_route = yes'
        focus(route,p[route],p[route+'_en'],('Подотчётность общинам даёт стабильность и рост доверия в мирное время.' if civic else 'Территориальное командование ускоряет подготовку войск, но вызывает недовольство общин.'),('Accountability improves stability and builds confidence during peace.' if civic else 'Territorial command improves troop training but costs community confidence.'),x,8,parents=('economy0','defence0'),reward=effect,exclude=other,icon='GFX_goal_generic_neutrality_focus')
        focus(route+'_law','Открытые местные сметы' if civic else 'Ведомости территориальных сил','Public Local Accounts' if civic else 'Territorial Muster Rolls','Укрепить выбранный порядок: +6 доверия и +30 политической власти.' if civic else 'Сверить мобилизационные списки: +8 опыта армии и +5% поддержки войны.','Strengthen the chosen system: +6 confidence and +30 political power.' if civic else 'Audit muster rolls: +8 army XP and +5% war support.',x,10,parents=(route,),reward='add_to_variable = { MNR_mandate = 6 } add_political_power = 30' if civic else 'army_experience = 8 add_war_support = 0.05')
        threat=p['threat']
        war=f'if = {{ limit = {{ is_subject = no country_exists = {threat} NOT = {{ has_war_with = {threat} }} NOT = {{ is_in_faction_with = {threat} }} }} create_wargoal = {{ type = puppet_wargoal_focus target = {threat} }} }}' if threat else 'add_to_variable = { MNR_reserve = 10 }'
        focus(route+'_settlement','Хартия устойчивого правления' if civic else 'Мандат вооружённой готовности','Charter of Stable Government' if civic else 'Armed Readiness Mandate','Принять местную хартию: +5% стабильности и +10 запасов.' if civic else ('Получить цель войны против соперничающего правительства, если мы независимы и не состоим с ним в одной фракции. Объявление войны остаётся решением игрока.' if threat else 'Создать дополнительные оборонные запасы: +10 запасов и +5 опыта армии.'),'Ratify a local charter: +5% stability and +10 reserves.' if civic else ('Gain a war goal against the rival government if independent and outside its faction. Declaring war remains a separate choice.' if threat else 'Prepare additional defensive stores: +10 reserves and +5 army XP.'),x,12,parents=(route+'_law',),reward='add_stability = 0.05 add_to_variable = { MNR_reserve = 10 }' if civic else war+' army_experience = 5',gate='check_variable = { MNR_mandate > 34 }')
    focus('projects','План национального проекта','National Project Plan',p['project']+'. Решение открывает оплачиваемый проект; время и ресурсы указаны в его описании.',p['project_en']+'. Unlock the paid project decision, with its duration and costs listed there.',24,2,parents=('root',),reward='set_country_flag = MNR_projects_open add_political_power = 25',icon='GFX_goal_generic_production')
    focus('specialists','Подготовить местных специалистов','Train Local Specialists','Освоить выпуск дополнительного оснащения и получить 50 комплектов для землемеров, лабораторий и служб снабжения. Для повторных проектов оснащение производится самостоятельно.','Unlock support equipment production and receive 50 sets for surveyors, laboratories and supply services. Manufacture further equipment for repeated projects.',24,4,parents=('projects',),reward='set_technology = { tech_support = 1 } add_equipment_to_stockpile = { type = support_equipment_1 amount = 50 producer = ROOT }',icon='GFX_goal_generic_scientific_exchange')
    gate=goal(p)
    focus('goal',p['goal'],p['goal_en'],'Завершить три национальных проекта, укрепить доверие и запасы, принять политический путь и выполнить дополнительные условия, показанные в требованиях фокуса. Награда: 100 политической власти, 5% стабильности, дополнительная ячейка исследований.','Complete three national projects, secure confidence and reserves, choose a political route, and meet the additional conditions shown below. Reward: 100 political power, 5% stability and a research slot.',24,14,parents=('economy2','defence2','specialists','chamber'),reward=f'if = {{ limit = {{ NOT = {{ has_country_flag = MNR_goal_complete }} }} set_country_flag = MNR_goal_complete add_political_power = 100 add_stability = 0.05 add_research_slot = 1 country_event = {{ id = mnr_campaign.{400+index} }} }}',gate=gate,cost=10,icon='GFX_goal_generic_scientific_exchange')
    write(f'common/national_focus/MNR_{tag}.txt',f'focus_tree = {{ id = MNR_{tag}_tree country = {{ factor = 0 modifier = {{ add = 200 tag = {tag} }} }} default = no continuous_focus_position = {{ x = 50 y = 1800 }}\n'+'\n'.join(focuses)+'\n}')
    write(f'history/units/MNR_{tag}_template.txt','division_template = { name = "'+p['en']+' Territorial Companies" regiments = { infantry = { x = 0 y = 0 } infantry = { x = 0 y = 1 } } }')
    mission(p)
    event(f'mnr_campaign.{200+index}','Спор о местных приоритетах','A Dispute over Local Priorities',p['crisis'],p['crisis_en'],[
        ('a','Оплатить согласованное решение','Fund an Agreed Settlement','add_political_power = -35 subtract_from_variable = { MNR_reserve = 5 } add_to_variable = { MNR_mandate = 8 } MNR_refresh = yes','has_political_power > 34 check_variable = { MNR_reserve > 4 }',70),
        ('b','Ввести чрезвычайный порядок','Issue Emergency Orders','subtract_from_variable = { MNR_mandate = 6 } add_timed_idea = { idea = MNR_emergency days = 180 } army_experience = 3 MNR_refresh = yes','',30)],f'tag = {tag} MNR_home_secure = yes')
    event(f'mnr_campaign.{300+index}',p['project']+': итог',p['project_en']+': Report','Первый проект завершён. Следующие два потребуют новых ресурсов. Местные специалисты могут воспроизвести результат, но сооружения не появляются бесплатно при каждом повторении.','The first project is complete. Two more require fresh resources. Repeating projects does not create free buildings.',[('a','Продолжить работу','Continue the Work','','',100)],f'tag = {tag}')
    event(f'mnr_campaign.{400+index}',p['goal'],p['goal_en'],p['opening']+' Теперь правительство располагает подготовленными службами, запасами и тремя завершёнными проектами. Дальнейшая внешняя политика остаётся вашим выбором.',p['opening_en']+' The government now has trained services, reserves and three completed projects. Its further foreign policy remains your choice.',[('a','Начинается следующая глава','The Next Chapter Begins','','',100)],f'tag = {tag}')
    MANIFEST[tag]={**p,'focuses':rows,'goal_trigger':gate,'project':f'MNR_{tag}_project'}

def retire_legacy():
    for path in (ROOT/'common/national_focus').glob('WTN_*_focus.txt'):
        s=path.read_text(encoding='utf-8-sig')
        for tag in PROFILES:s=re.sub(r'modifier\s*=\s*\{\s*add\s*=\s*100\s+tag\s*=\s*'+tag+r'\s*\}','',s)
        write(path,s)

def main():
    base();diplomacy()
    for index,p in enumerate(PROFILES.values()):country(p,index)
    maritime_contracts()
    write('common/scripted_effects/MNR_campaign.txt','\n\n'.join(FX))
    write('common/scripted_triggers/MNR_campaign.txt','\n'.join(TR))
    write('common/ideas/MNR_campaign.txt','ideas = { country = {\n'+'\n'.join(IDEAS)+'\n} }')
    write('events/MNR_campaign.txt','\n\n'.join(EVENTS))
    write('common/decisions/categories/MNR_campaign.txt','MNR_campaign_category = { icon = generic_political_discourse visible = { MNR_is_minor = yes has_country_flag = MNR_initialized } }')
    write('common/decisions/MNR_campaign.txt','MNR_campaign_category = {\n'+'\n'.join(DEC)+'\n}')
    write('common/on_actions/MNR_campaign.txt','''on_actions = {
 on_startup = { effect = { every_country = { limit = { MNR_is_minor = yes } MNR_initialize = yes MNR_refresh = yes } } }
 on_daily = { effect = { if = { limit = { MNR_is_minor = yes } MNR_initialize = yes MNR_refresh = yes } MNR_refresh_network = yes } }
 on_monthly = { effect = { if = { limit = { MNR_is_minor = yes } MNR_monthly = yes } } }
}''')
    for language,entries in LOC.items():
        write(f'localisation/{language}/MNR_campaign_l_{language}.yml','l_'+language+':\n'+'\n'.join(f' {k}:0 "{v.replace(chr(34),chr(39)).replace(chr(10),chr(92)+"n")}"' for k,v in entries.items()),True)
    write('tools/minor_campaign_manifest.json',json.dumps(MANIFEST,ensure_ascii=False,indent=2))
    retire_legacy()
    from minor_story_links import sync
    sync()
    from focus_shapes import apply as apply_shapes
    apply_shapes()
    print(f'Built {len(MANIFEST)} minor trees, {sum(len(p["focuses"]) for p in MANIFEST.values())} focuses, {len(EVENTS)-1} events and {len(DEC)} decisions.')

if __name__=='__main__':main()
