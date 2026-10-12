"""Story revision. Uses frozen pre-revision copies; no import-side-effect builds."""
from pathlib import Path
import re, json, shutil
ROOT=Path(__file__).resolve().parents[1]
BACK=ROOT/'tools/backups/ludolf_before'
L={}
def write(path,text,bom=False):
 p=ROOT/path
 if p.exists() and not (BACK/path).exists():
  (BACK/path).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,BACK/path)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8-sig' if bom else 'utf-8')
def original(path):
 p=BACK/path
 return (p if p.exists() else ROOT/path).read_text(encoding='utf-8-sig')
def loc(key,ru,en,dr=None,de=None):
 L[key]=(ru,en)
 if dr: L[key+'_desc']=(dr,de)
def bop(value):return f'add_power_balance_value = {{ id = A01_ludolf_admirals_balance value = {value} }}'
def respect(value):return f'add_to_variable = {{ A01_admirals_respect = {value} }} clamp_variable = {{ var = A01_admirals_respect min = 0 max = 100 }}'

loc('A01_ludolf_admirals_balance','Власть в Батавии','Power in Batavia')
loc('A01_admirals_side','Совет адмиралов','Admirals Council')
loc('A01_ludolf_side','Людольф Слут ван де Беле','Ludolf Sloot van de Beele')
loc('A01_balance_compromise','Неустойчивое равновесие','Uneasy Equilibrium')
loc('A01_council_influence','Влияние морского ведомства','Naval Ministry Influence')
loc('A01_council_pressure','Совет диктует условия','The Council Dictates Terms')
loc('A01_council_supremacy','Господство адмиралов','Admiralty Supremacy')
loc('A01_ludolf_influence','Гражданское руководство','Civilian Leadership')
loc('A01_ludolf_authority','Авторитет губернатора','The Governor\u2019s Authority')
loc('A01_ludolf_supremacy','Устойчивое правительство','A Stable Government')
write('common/bop/A01_ludolf.txt','''A01_ludolf_admirals_balance = {
 initial_value = 0.15
 left_side = A01_admirals_side
 right_side = A01_ludolf_side
 decision_category = A01_council_relations
 range = { id = A01_balance_compromise min = -0.1 max = 0.1 modifier = { } }
 side = {
  id = A01_admirals_side icon = GFX_idea_story_admirals
  range = { id = A01_council_influence min = -0.4 max = -0.1 modifier = { production_speed_dockyard_factor = 0.05 } }
  range = { id = A01_council_pressure min = -0.7 max = -0.4 modifier = { production_speed_dockyard_factor = 0.10 political_power_gain = -0.10 } }
  range = { id = A01_council_supremacy min = -1 max = -0.7 modifier = { production_speed_dockyard_factor = 0.15 stability_factor = -0.05 }
   on_activate = { if = { limit = { has_country_flag = A01_borneo_treaty NOT = { has_country_flag = A01_ludolf_crisis_resolved } } country_event = { id = ludolf.34 days = 1 } } }
  }
 }
 side = {
  id = A01_ludolf_side icon = GFX_idea_story_ludolf
  range = { id = A01_ludolf_influence min = 0.1 max = 0.4 modifier = { political_power_gain = 0.05 } }
  range = { id = A01_ludolf_authority min = 0.4 max = 0.7 modifier = { political_power_gain = 0.10 stability_factor = 0.03 } }
  range = { id = A01_ludolf_supremacy min = 0.7 max = 1 modifier = { political_power_gain = 0.15 stability_factor = 0.05 } }
 }
}
''')

effects='''A01_initialize_balance_effect = {
 if = {
  limit = { NOT = { has_country_flag = A01_balance_initialized } }
  set_country_flag = A01_balance_initialized
  set_variable = { A01_admirals_respect = 30 }
  set_power_balance = { id = A01_ludolf_admirals_balance left_side = A01_admirals_side right_side = A01_ludolf_side set_default = yes set_value = 0.15 }
  country_event = { id = ludolf.10 days = 1 }
 }
}
A01_borneo_resource_rights_effect = {
'''
# Oil/rubber only, not steel/coal and not a cosmetic modifier.
BORNEO=[333,334,1022,1023,1024,1055]
for sid in BORNEO:
 effects+=f'{sid} = {{ owner = {{ if = {{ limit = {{ NOT = {{ tag = A03 }} }} give_resource_rights = {{ receiver = A03 state = {sid} resources = {{ oil rubber }} }} }} }} }}\n'
effects+='}\n'
effects+='''A01_borneo_treaty_effect = {
 if = {
  limit = { NOT = { has_country_flag = A01_borneo_treaty } country_exists = A03 }
  A03 = { white_peace = { tag = A01 } }
  A03 = { transfer_state = 1024 transfer_state = 1023 }
  transfer_state = 333
  transfer_state = 1022
  set_country_flag = A01_borneo_treaty
  set_country_flag = A01_japanese_invasion_begun
  clr_country_flag = A01_refused_japanese_ultimatum
  remove_ideas = A01_war_production
  add_ideas = A01_borneo_humiliation
  add_ideas = A01_revanchism_simmering
  add_stability = -0.10
  A01_initialize_balance_effect = yes
  add_power_balance_value = { id = A01_ludolf_admirals_balance value = -0.35 }
  add_to_variable = { A01_admirals_respect = -15 }
  clamp_variable = { var = A01_admirals_respect min = 0 max = 100 }
  A01_borneo_resource_rights_effect = yes
  A03 = { set_country_flag = A03_borneo_victory diplomatic_relation = { country = A01 relation = non_aggression_pact } country_event = { id = ludolf.21 days = 1 } }
  country_event = { id = ludolf.30 days = 14 }
  country_event = { id = ludolf.33 days = 60 }
 }
}
A01_admirals_remove_ludolf_effect = {
 if = {
  limit = { NOT = { has_country_flag = A01_ludolf_crisis_resolved } }
  set_country_flag = A01_ludolf_crisis_resolved
  set_country_flag = A01_admirals_seized_power
  recruit_character = A01_council_of_admirals
  promote_character = { character = A01_council_of_admirals ideology = despotism }
  retire_character = A01_ludolf_sloot_van_de_beele
  set_power_balance = { id = A01_ludolf_admirals_balance set_value = -0.85 }
  add_ideas = A01_reconstruction_cabinet
  add_stability = 0.05
 }
}
'''
write('common/scripted_effects/A01_ludolf_effects.txt',effects)

events='add_namespace = ludolf\n'
def event(n,ru,en,dr,de,opts,trigger='',immediate='',picture='GFX_report_event_A01_japan_rejects_dutch_offer'):
 global events
 key=f'ludolf.{n}';loc(key+'.t',ru,en);loc(key+'.d',dr,de)
 events+=f'country_event = {{\n id = {key}\n title = {key}.t\n desc = {key}.d\n picture = {picture}\n is_triggered_only = yes\n'
 if trigger:events+=f' trigger = {{ {trigger} }}\n'
 if immediate:events+=f' immediate = {{ {immediate} }}\n'
 for s,r,e,eff,weight,available in opts:
  loc(key+'.'+s,r,e);events+=f' option = {{ name = {key}.{s} ai_chance = {{ factor = {weight} }} '+(f'trigger = {{ {available} }} ' if available else '')+eff+' }\n'
 events+='}\n'
event(1,'Нефть, каучук и гарантии','Oil, Rubber and Guarantees','Представительство Всемирной Торговой Палаты получило предложение Батавии. Предстоит согласовать закупки каучука и нефти, страхование рейсов и строительство складов. Губернатор рассчитывает получить внешний капитал, не отдавая Палате управление колонией.','The World Trade Chamber has received Batavia\u2019s proposal. Rubber and oil purchases, shipping insurance and warehouses must be agreed. The governor wants foreign capital without surrendering colonial administration.',[
 ('a','Направить торговую делегацию.','Dispatch a trade delegation.','add_political_power = 25 set_country_flag = A01_wtc_offer_announced',100,'')],trigger='tag = A01')
event(2,'Батавский ресурсный контракт','The Batavia Resource Contract','Ост-Индия предлагает Палате долгосрочные поставки нефти и каучука. Наши представители приглашены обсудить цены, портовые сборы и страховые гарантии. Это возможность закрепиться в торговле архипелага без прямого вмешательства в его управление.','The East Indies offers the Chamber long-term oil and rubber deliveries. Our representatives are invited to discuss prices, port fees and insurance. This is an opportunity to expand commerce without assuming direct administration.',[
 ('a','Принять приглашение Батавии.','Accept Batavia\u2019s invitation.','add_political_power = 25 set_country_flag = A04_batavia_trade_contacts',100,'')],trigger='tag = A04')
event(10,'Губернатор и морское ведомство','The Governor and the Naval Ministry','Отказ от внешних союзов оставляет Батавию один на один с морскими угрозами. Адмиралы требуют участия в распределении бюджета. Людольф сохраняет гражданские полномочия, но ему придётся заслужить уважение офицеров делами.\n\nБаланс сил показывает политический контроль; уважение Совета определяет готовность адмиралов сотрудничать с губернатором.','Rejecting outside alliances leaves Batavia alone against maritime threats. The admirals demand a voice in the budget. Ludolf retains civilian authority but must earn the officers\u2019 respect through action.\n\nThe balance measures political control; Council respect determines its willingness to cooperate.',[
 ('a','Власть придётся подкрепить доверием.','Authority must be backed by trust.','',100,'')],trigger='tag = A01')
event(20,'Условия мира на Борнео','The Borneo Peace Terms','Морская война истощила казну и обнажила слабость обороны северного Борнео. Япония предлагает прекратить боевые действия: Сабах (1024) и Бруней (1023) переходят империи; Саравак (333) и внутреннее Борнео (1022) закрепляются за Батавией. Япония получает права на нефть и каучук всего Борнео.\n\nСовет адмиралов возложит ответственность за унизительный договор на Людольфа.','The naval war has drained the treasury and exposed northern Borneo. Japan offers peace: Sabah (1024) and Brunei (1023) pass to the empire; Sarawak (333) and Interior Borneo (1022) are secured for Batavia. Japan receives oil and rubber rights throughout Borneo.\n\nThe Admirals Council will blame Ludolf for the humiliating treaty.',[
 ('a','Подписать договор. Мы не выдержим новой кампании.','Sign. We cannot sustain another campaign.','A01_borneo_treaty_effect = yes',100,''),
 ('b','Продолжать войну вопреки Совету.','Continue the war despite the Council.',bop(-0.15)+respect(-10)+'add_stability = -0.05 set_country_flag = A01_rejected_borneo_peace',0,'has_capitulated = no')],trigger='tag = A01 has_war_with = A03 NOT = { has_country_flag = A01_borneo_treaty }')
event(21,'Борнейская конвенция','The Borneo Convention','Батавия подписала договор. Империя получает Сабах и Бруней, а также исключительные права на нефтяные и каучуковые ресурсы Борнео. Саравак и внутренние районы острова остаются в сфере управления Ост-Индии.','Batavia has signed. The empire gains Sabah and Brunei, together with exclusive oil and rubber rights across Borneo. Sarawak and the interior remain under East Indian administration.',[
 ('a','Ресурсный вопрос решён.','The resource question is settled.','add_war_support = 0.05 add_political_power = 75',100,'')],trigger='tag = A03')
event(30,'Правительство после поражения','Government After Defeat','В Батавии обсуждают, кто заплатит за Борнейскую конвенцию. Адмиралы требуют следствия и нового кабинета; местные правители добиваются автономии. Людольф предлагает перестройку управления, которая сохранит общую оборону и даст султанам собственные правительства.','Batavia debates who will pay for the Borneo Convention. The admirals demand an inquiry and a new cabinet; local rulers demand autonomy. Ludolf proposes a reorganisation preserving common defence while giving the sultans their own governments.',[
 ('a','Сначала расследование и открытые счета.','Begin with an inquiry and open accounts.',respect(10)+'add_political_power = -50 set_country_flag = A01_reconstruction_started',80,''),
 ('b','Сохранить кабинет и закрыть обсуждение.','Keep the cabinet and close the debate.',bop(0.10)+respect(-15)+'add_stability = -0.05 set_country_flag = A01_reconstruction_started',20,'')],trigger='tag = A01 has_country_flag = A01_borneo_treaty')
event(31,'Хартии автономных султанатов','Charters of the Autonomous Sultanates','Подписаны основы нового порядка. Кутай, Понтианак и Банджар смогут получить отдельные администрации под верховенством Батавии. Оборона и внешняя политика останутся общими, а японские ресурсные концессии сохранят силу и на автономных территориях.','The new order is taking shape. Kutai, Pontianak and Banjar may form separate administrations under Batavia\u2019s sovereignty. Defence and foreign policy remain common, and Japanese resource concessions remain valid in autonomous territories.',[
 ('a','Готовить отдельные хартии.','Prepare the individual charters.','set_country_flag = A01_sultanate_charters_unlocked',100,'')],trigger='tag = A01 has_country_flag = A01_borneo_treaty')
event(32,'Память о потерянном севере','The Lost North Remembered','В офицерских клубах и портовых кварталах говорят о возвращении Сабаха и Брунея. Одни требуют немедленной мести, другие призывают сначала восстановить флот. Людольф видит шанс объединить страну вокруг долгой программы восстановления.','Officer clubs and port districts speak of recovering Sabah and Brunei. Some demand immediate revenge; others want the fleet rebuilt first. Ludolf sees a chance to unite the country around a long reconstruction programme.',[
 ('a','Реванш начинается с восстановления.','Recovery comes before revenge.','remove_ideas = A01_revanchism_simmering add_ideas = A01_revanchism_organised add_war_support = 0.05',80,''),
 ('b','Поддержать горячие головы.','Support the firebrands.','add_war_support = 0.15 add_stability = -0.10 '+respect(-5),20,'')],trigger='tag = A01 has_country_flag = A01_borneo_treaty')
event(33,'Адмиралы требуют ответа','The Admirals Demand an Answer','Совет снова ставит вопрос об ответственности губернатора. Офицеры сравнивают его обещания с ремонтом кораблей, жалованьем экипажей и ходом восстановления. Уважение к Людольфу сейчас: [?A01_admirals_respect|0]/100.','The Council again questions the governor\u2019s responsibility. Officers compare his promises with ship repairs, crew pay and reconstruction. Current respect for Ludolf: [?A01_admirals_respect|0]/100.',[
 ('a','Представить результаты и сохранить кабинет.','Present results and keep the cabinet.',bop(0.10)+'add_stability = 0.02 country_event = { id = ludolf.33 days = 90 }',90,'check_variable = { A01_admirals_respect > 59 }'),
 ('b','Пойти на новые уступки морскому ведомству.','Make further concessions to the navy.',bop(-0.10)+respect(10)+'add_political_power = -35 country_event = { id = ludolf.33 days = 90 }',70,''),
 ('c','Отвергнуть требования Совета.','Reject the Council\u2019s demands.',bop(-0.15)+respect(-10)+'add_stability = -0.03 country_event = { id = ludolf.33 days = 60 }',10,''),
 ('d','Согласиться на передачу власти.','Agree to hand over power.','A01_admirals_remove_ludolf_effect = yes country_event = { id = ludolf.35 days = 1 }',10,'')],trigger='tag = A01 has_country_flag = A01_borneo_treaty NOT = { has_country_flag = A01_ludolf_crisis_resolved }')
event(34,'Вотум недоверия губернатору','A Vote of No Confidence','Совет контролирует ключевые назначения и больше не считает Людольфа способным руководить страной. Адмиралы предъявили требование об отставке. Только накопленное уважение офицеров позволяет губернатору просить последнее время на завершение реформ.','The Council controls key appointments and no longer accepts Ludolf\u2019s leadership. It demands his resignation. Only the officers\u2019 accumulated respect can secure one last opportunity to complete the reforms.',[
 ('a','Принять отставку.','Accept resignation.','A01_admirals_remove_ludolf_effect = yes country_event = { id = ludolf.35 days = 1 }',80,''),
 ('b','Использовать поддержку офицеров для компромисса.','Use officer support to secure a compromise.','set_power_balance = { id = A01_ludolf_admirals_balance set_value = -0.40 } '+respect(-25)+'add_political_power = -75',20,'check_variable = { A01_admirals_respect > 59 }')],trigger='tag = A01 has_country_flag = A01_borneo_treaty NOT = { has_country_flag = A01_ludolf_crisis_resolved } power_balance_value = { id = A01_ludolf_admirals_balance value < -0.69 }')
event(35,'Людольф покидает резиденцию','Ludolf Leaves the Residence','Людольф передал полномочия Совету адмиралов. Новому правительству достались японские концессии, автономные администрации и общество, ожидающее возвращения потерянных земель. Смена главы государства не снимает этих противоречий.','Ludolf has transferred authority to the Admirals Council. The new government inherits Japanese concessions, autonomous administrations and a public expecting the lost territories to return. A change of leadership has not resolved these tensions.',[
 ('a','Восстановление продолжается.','Reconstruction continues.','',100,'')],trigger='tag = A01 has_country_flag = A01_admirals_seized_power')
event(36,'Гражданский кабинет устоял','The Civilian Cabinet Endures','Восстановление флота, соглашения с султанами и регулярные консультации лишили противников Людольфа главных аргументов. Совет признал его полномочия. Правительство продолжит подготовку к пересмотру Борнейской конвенции, опираясь на общий план восстановления.','Fleet repairs, agreements with the sultans and regular consultations have weakened Ludolf\u2019s opponents. The Council has recognised his authority. The cabinet will continue preparing to revise the Borneo Convention through a common reconstruction programme.',[
 ('a','Власть сохранена — обязательства остаются.','Authority is preserved; obligations remain.','add_stability = 0.05',100,'')],trigger='tag = A01 has_country_flag = A01_ludolf_survived')
write('events/A01_ludolf_story.txt',events)

write('common/on_actions/A01_borneo_story.txt','''on_actions = {
 on_war_relation_added = {
  effect = {
   if = {
    limit = { OR = { AND = { ROOT = { tag = A03 } FROM = { tag = A01 } } AND = { ROOT = { tag = A01 } FROM = { tag = A03 } } } }
    A01 = {
     if = { limit = { NOT = { has_country_flag = A01_borneo_peace_scheduled } NOT = { has_country_flag = A01_borneo_treaty } }
      set_country_flag = A01_borneo_peace_scheduled
      country_event = { id = ludolf.20 days = 120 }
     }
    }
   }
  }
 }
 on_capitulation_immediate = {
  effect = {
   if = { limit = { ROOT = { tag = A01 has_war_with = A03 NOT = { has_country_flag = A01_borneo_treaty } } FROM = { tag = A03 } }
    A01 = { A01_borneo_treaty_effect = yes }
   }
  }
 }
}
''')

# Decisions in the native balance panel and a separate reconstruction category.
category='A01_council_relations'
loc(category,'Губернатор и Совет адмиралов','Governor and Admirals Council','§YУважение Совета: [?A01_admirals_respect|0]/100§!\n\nУступки передают полномочия адмиралам, но повышают их готовность сотрудничать. Манёвры, открытые счета и выполнение обещаний укрепляют уважение без отказа от гражданской власти. После поражения низкий баланс может привести к отставке Людольфа.','§YCouncil respect: [?A01_admirals_respect|0]/100§!\n\nConcessions transfer authority to the admirals but improve cooperation. Exercises, open accounts and fulfilled promises build respect. After defeat, a low balance can force Ludolf\u2019s resignation.')
dec=f'{category} = {{ icon = generic_political_actions allowed = {{ original_tag = A01 }} visible = {{ has_country_flag = A01_balance_initialized NOT = {{ has_country_flag = A01_ludolf_crisis_resolved }} }}\n'
def decision(key,ru,en,dr,de,cost,days,cooldown,effect,available='',visible='',icon='generic_prepare_civil_war',ai=1):
 loc(key,ru,en,dr,de)
 return f'{key} = {{ icon = {icon} cost = {cost} days_remove = {days} days_re_enable = {cooldown} '+(f'visible = {{ {visible} }} ' if visible else '')+f'available = {{ has_capitulated = no {available} }} remove_effect = {{ {effect} }} ai_will_do = {{ factor = {ai} }} }}\n'
dec+=decision('A01_concede_naval_budget','Уступить Совету часть бюджета','Concede a Share of the Budget','Морское ведомство получит больше контроля над заказами. Уважение Совета +15; баланс на 10% в пользу адмиралов.','The navy gains control over orders. Council respect +15; balance shifts 10% toward the admirals.',50,14,90,respect(15)+bop(-0.10))
dec+=decision('A01_honour_naval_officers','Отметить заслуги офицеров','Recognise Naval Service','Губернатор лично вручит награды отличившимся экипажам. Уважение +10; баланс на 5% в пользу Людольфа.','The governor will personally honour distinguished crews. Respect +10; balance shifts 5% toward Ludolf.',50,7,90,respect(10)+bop(0.05))
dec+=decision('A01_joint_naval_exercises','Провести совместные манёвры','Hold Joint Naval Exercises','Совместная инспекция и учения подтвердят серьёзность оборонной программы. Уважение +10; баланс на 10% в пользу Людольфа.','A joint inspection and exercises demonstrate commitment to defence. Respect +10; balance shifts 10% toward Ludolf.',75,30,120,respect(10)+bop(0.10)+'navy_experience = 10')
dec+=decision('A01_open_admiralty_accounts','Открыть счета Адмиралтейства','Open the Admiralty Accounts','Прозрачные закупки уменьшат взаимные подозрения. Уважение +8; небольшое укрепление гражданского контроля.','Transparent procurement reduces mutual suspicion. Respect +8; a small gain in civilian control.',40,14,90,respect(8)+bop(0.05))
dec+=decision('A01_accept_naval_appointments','Принять назначения Совета','Accept Council Appointments','Адмиралы займут новые административные посты. Уважение +20; баланс на 15% в пользу Совета.','Admirals gain administrative posts. Respect +20; balance shifts 15% toward the Council.',35,7,120,respect(20)+bop(-0.15))
dec+='}\n'
loc('A01_postwar_reconstruction','Перестройка Ост-Индии','Reorganising the East Indies','Борнейская конвенция изменила границы, но не сняла противоречий между губернатором, флотом и местными правителями. Автономные султанаты сохранят подчинение Батавии и японские ресурсные права.','The Borneo Convention changed borders without resolving tensions between governor, navy and local rulers. Autonomous sultanates remain under Batavia and retain Japanese resource concessions.')
dec+='A01_postwar_reconstruction = { icon = generic_political_actions allowed = { original_tag = A01 } visible = { has_country_flag = A01_borneo_treaty }\n'
for tag,sid,ru,en in [('A11',1055,'Кутай','Kutai'),('A12',334,'Понтианак','Pontianak'),('A13',1022,'Банджар','Banjar')]:
 effect=f'{sid} = {{ add_core_of = {tag} }} {tag} = {{ transfer_state = {sid} set_politics = {{ ruling_party = neutrality elections_allowed = no }} set_popularities = {{ neutrality = 100 }} give_resource_rights = {{ receiver = A03 state = {sid} resources = {{ oil rubber }} }} }} set_autonomy = {{ target = {tag} autonomy_state = autonomy_puppet freedom_level = 0.25 }} add_stability = 0.03 '+bop(-0.05)
 ident='A01_charter_'+tag
 dec+=decision(ident,'Предоставить хартию: '+ru,'Grant a Charter: '+en,'Султанат получит собственную администрацию и армию, оставаясь зависимым от Батавии. Японские права на нефть и каучук сохраняются.','The sultanate receives its own administration and army while remaining subordinate to Batavia. Japanese oil and rubber rights remain in force.',60,30,0,effect,available=f'owns_state = {sid} NOT = {{ country_exists = {tag} }}',visible=f'has_country_flag = A01_sultanate_charters_unlocked NOT = {{ country_exists = {tag} }}')
 # Make release decisions truly one-use, not repeatable 0-day cooldown.
 dec=dec.replace(f'{ident} = {{ icon',f'{ident} = {{ fire_only_once = yes icon')
dec+=decision('A01_fund_widows','Помощь семьям погибших','Support Bereaved Families','Выплаты семьям моряков уменьшат ожесточение в портах. Уважение +5, стабильность +3%.','Payments to sailors\u2019 families ease bitterness in the ports. Respect +5, stability +3%.',50,30,120,respect(5)+'add_stability = 0.03')
dec+='}\n'
write('common/decisions/A01_ludolf_story.txt',dec)

ideas='ideas = { country = {\n'
for key,ru,en,icon,mod,dr,de in [
 ('A01_borneo_humiliation','Борнейское унижение','The Borneo Humiliation','defeat','stability_factor = -0.05 political_power_gain = -0.10','Утрата северного Борнео и японские концессии подрывают доверие к Батавии.','The loss of northern Borneo and Japanese concessions undermine confidence in Batavia.'),
 ('A01_revanchism_simmering','Зреющий реваншизм','Simmering Revanchism','revanchism','war_support_factor = 0.05 stability_factor = -0.03','Общество требует вернуть потерянные земли, но общей программы восстановления пока нет.','The public demands the lost territories back, but there is no common reconstruction programme.'),
 ('A01_revanchism_organised','Программа национального восстановления','National Reconstruction Programme','revanchism','war_support_factor = 0.10 production_speed_dockyard_factor = 0.10','Реваншистские настроения направлены на восстановление флота и оборонной промышленности.','Revanchist sentiment is channelled into rebuilding the fleet and defence industry.'),
 ('A01_reconstruction_cabinet','Кабинет восстановления','Reconstruction Cabinet','ludolf','political_power_gain = 0.10 stability_factor = 0.03','Новый кабинет согласует восстановление портов и отношения с автономными правителями.','The new cabinet coordinates port reconstruction and relations with autonomous rulers.'),
 ('A01_sultanate_federation','Договор с султанатами','The Sultanate Compact','sultans','stability_factor = 0.05 recruitable_population_factor = 0.05','Автономные администрации сохраняют общий оборонный договор с Батавией.','Autonomous administrations retain a common defence compact with Batavia.'),
 ('A01_civilian_naval_compact','Гражданско-морской компромисс','Civilian-Naval Compact','admirals','navy_org_factor = 0.05 political_power_gain = 0.05','Совет признал гражданское руководство в обмен на выполнение согласованной морской программы.','The Council recognises civilian leadership in exchange for an agreed naval programme.')]:
 loc(key,ru,en,dr,de);ideas+=f'{key} = {{ picture = story_{icon} allowed = {{ original_tag = A01 }} allowed_civil_war = {{ always = yes }} removal_cost = -1 modifier = {{ {mod} }} }}\n'
write('common/ideas/A01_ludolf_story.txt',ideas+'} }\n')

# Amend existing focuses without replaying the first build.
fp='common/national_focus/a01_focus.txt';t=original(fp)
def edit_focus(text,ident,fn):
 m=re.search(r'\bfocus\s*=\s*\{\s*id\s*=\s*'+re.escape(ident)+r'\b',text)
 if not m:raise ValueError(ident)
 start=m.start();i=text.index('{',m.start())+1;depth=1
 while depth:
  depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[:start]+fn(text[start:i])+text[i:]
def add_reward(b,reward):return b.replace('completion_reward = {','completion_reward = {\n'+reward,1)
t=edit_focus(t,'A01_wtc_oil_and_rubber_offer',lambda b:add_reward(b,'country_event = { id = ludolf.1 days = 1 }\n if = { limit = { country_exists = A04 } A04 = { country_event = { id = ludolf.2 days = 1 } } }\n'))
t=edit_focus(t,'A01_lone_wolf_path',lambda b:add_reward(b,'A01_initialize_balance_effect = yes\n'))
t=edit_focus(t,'A01_strengthen_ludolfs_power',lambda b:add_reward(b,bop(0.10)).replace('factor = 1','factor = 10'))
t=edit_focus(t,'A01_admirals_council_coup',lambda b:add_reward(b,'set_country_flag = A01_ludolf_crisis_resolved\nset_power_balance = { id = A01_ludolf_admirals_balance set_value = -0.85 }\n').replace('factor = 1','factor = 0.1'))
# Pre-war charter becomes groundwork; the actual autonomous governments follow defeat.
t=edit_focus(t,'A01_colonial_charter',lambda b:b.replace('completion_reward = {','completion_reward = { set_country_flag = A01_prewar_charter_foundation ',1))
# The postwar narrative must remain reachable after losing Sabah, even if forts
# or wartime industry were never completed.
t=edit_focus(t,'A01_pacific_settlement',lambda b:re.sub(r'prerequisite = \{ focus = A01_wartime_industry \}','prerequisite = { focus = A01_strengthen_ludolfs_power }',b).replace('NOT = { has_war = yes } has_country_flag = A01_japanese_invasion_begun','has_country_flag = A01_borneo_treaty NOT = { has_war_with = A03 }').replace('add_stability = 0.10 add_political_power = 100 remove_ideas = A01_war_production','set_country_flag = A01_postwar_cabinet_mandate add_political_power = 50 add_ideas = A01_reconstruction_cabinet'))

def focus(key,ru,en,dr,de,x,y,parents,reward,icon,cost=5,available='',exclusive=''):
 ident='A01_'+key;loc(ident,ru,en,dr,de)
 return f'focus = {{ id = {ident} icon = GFX_goal_story_{icon} x = {x} y = {y} cost = {cost}\n'+''.join(f'prerequisite = {{ focus = A01_{p} }}\n' for p in parents)+(f'mutually_exclusive = {{ focus = A01_{exclusive} }}\n' if exclusive else '')+(f'available = {{ {available} }} cancel_if_invalid = yes\n' if available else '')+f'ai_will_do = {{ factor = 1 }} completion_reward = {{ {reward} }} }}\n'
new=''
new+=focus('governors_secretariat','Секретариат губернатора','The Governor\u2019s Secretariat','Постоянный секретариат сведёт воедино бюджет, назначения и обязательства перед флотом. Людольф получит собственный инструмент контроля за исполнением решений.','A permanent secretariat will coordinate budgets, appointments and promises to the fleet, giving Ludolf a means to enforce government decisions.',10,4,['strengthen_ludolfs_power'],bop(0.10)+'add_political_power = 75','ludolf')
new+=focus('officers_audience','Аудиенция командиров эскадр','An Audience for Squadron Commanders','Регулярные доклады командиров дадут губернатору достоверную картину состояния флота. Уважение офицеров нужно заслужить вниманием к их действительным нуждам.','Regular reports will give the governor a reliable picture of the fleet. Officer respect must be earned by addressing real needs.',8,5,['governors_secretariat'],respect(15)+'navy_experience = 15','admirals')
new+=focus('civilian_procurement','Гражданский контроль над заказами','Civilian Procurement Oversight','Сметы станут открытыми, а сроки поставок — обязательными. Совет потеряет часть влияния на подрядчиков, но получит предсказуемое снабжение.','Published estimates and binding delivery dates will reduce the Council\u2019s influence over contractors while ensuring reliable supplies.',10,5,['governors_secretariat'],bop(0.10)+respect(5),'trade')
new+=focus('naval_budget_compromise','Компромисс по морскому бюджету','The Naval Budget Compromise','Губернатор закрепит согласованные расходы на ремонт и обучение флота. В обмен адмиралы признают его право утверждать общий бюджет.','The governor guarantees agreed spending on naval repair and training. In return, the admirals accept his authority over the general budget.',9,6,['officers_audience','civilian_procurement'],respect(15)+bop(0.05)+'add_ideas = A01_civilian_naval_compact','admirals',cost=7)
new+=focus('reconstruction_commission','Комиссия по восстановлению','The Reconstruction Commission','Поражение требует нового кабинета и проверки прежних решений. Комиссия объединит гражданских специалистов, офицеров и представителей островных правителей.','Defeat requires a new cabinet and an examination of earlier decisions. The commission will unite civilian experts, officers and island rulers.',18,11,['pacific_settlement'],respect(10)+'add_stability = 0.03','constitution')
new+=focus('autonomous_sultanates','Автономные султанаты','Autonomous Sultanates','Кутай, Понтианак и Банджар получат хартии автономии. Их правительства останутся зависимыми от Батавии, а японские ресурсные права будут подтверждены.','Kutai, Pontianak and Banjar will receive charters of autonomy under Batavia. Japanese resource rights will be reaffirmed.',16,12,['reconstruction_commission'],'country_event = { id = ludolf.31 days = 1 }','sultans')
new+=focus('northern_memory','Память о северном Борнео','Remember Northern Borneo','Публичные церемонии дадут горечи поражения общий язык. Правительство должно направить реваншизм на восстановление, прежде чем он станет угрозой самой Батавии.','Public commemorations will give defeat a shared meaning. The government must channel revanchism into reconstruction before it threatens Batavia itself.',20,12,['reconstruction_commission'],'country_event = { id = ludolf.32 days = 1 }','revanchism')
new+=focus('federal_defence_compact','Общая оборона султанатов','A Common Sultanate Defence','Отдельные правительства сохранят общие морские коммуникации и согласованный план обороны. Хартии станут основой единого оборонного договора.','Separate governments will share maritime communications and a coordinated defence plan. The charters will underpin a common defence compact.',16,13,['autonomous_sultanates'],'add_ideas = A01_sultanate_federation add_stability = 0.03','sultans',available='OR = { A11 = { is_subject_of = A01 } A12 = { is_subject_of = A01 } A13 = { is_subject_of = A01 } }')
new+=focus('fleet_of_recovery','Флот восстановления','The Recovery Fleet','Новые доки и ремонтные мастерские позволят восстановить корабельный состав. Реванш требует подготовленных экипажей и исправных судов.','New docks and repair shops will rebuild naval strength. Recovering the lost north requires trained crews and serviceable ships.',20,13,['northern_memory'],'if = { limit = { owns_state = 1058 } 1058 = { add_extra_state_shared_building_slots = 2 add_building_construction = { type = dockyard level = 2 instant_build = yes } } } '+respect(15),'admirals',cost=7)
new+=focus('ludolf_survives','Сохранить власть Людольфа','Preserve Ludolf\u2019s Government','Людольф предъявит Совету результаты восстановления и добьётся признания гражданского кабинета. Для компромисса необходимы уважение офицеров и достаточный политический вес.','Ludolf will present the reconstruction results and secure recognition for his civilian cabinet. This requires officer respect and sufficient political authority.',17,14,['federal_defence_compact','fleet_of_recovery'],'set_country_flag = A01_ludolf_crisis_resolved set_country_flag = A01_ludolf_survived remove_ideas = A01_borneo_humiliation '+bop(0.20)+'country_event = { id = ludolf.36 days = 1 }','ludolf',cost=7,available='NOT = { has_country_flag = A01_admirals_seized_power } check_variable = { A01_admirals_respect > 59 } power_balance_value = { id = A01_ludolf_admirals_balance value > -0.01 }',exclusive='negotiated_resignation')
new+=focus('negotiated_resignation','Уйти ради единства','Resign for Unity','Если сохранить гражданский кабинет невозможно, Людольф согласится на передачу полномочий Совету. Автономные хартии и план восстановления продолжат действовать.','If the civilian cabinet cannot survive, Ludolf will agree to hand authority to the Council. The autonomous charters and reconstruction programme will remain in force.',19,14,['federal_defence_compact','fleet_of_recovery'],'A01_admirals_remove_ludolf_effect = yes country_event = { id = ludolf.35 days = 1 }','admirals',exclusive='ludolf_survives')
new+=focus('review_borneo_convention','Пересмотр Борнейской конвенции','Review the Borneo Convention','Восстановив управление и флот, Батавия сможет сформулировать требования о пересмотре унизительного договора. Утрата земель останется центром внешней политики.','With government and fleet restored, Batavia can formulate demands to revise the humiliating convention. Recovering the lost territories will remain central to foreign policy.',18,15,['northern_memory'],'add_war_support = 0.05 add_political_power = 100 set_country_flag = A01_borneo_revisionism','revanchism',available='has_country_flag = A01_ludolf_crisis_resolved',cost=7)
t=t.rsplit('}',1)[0]+new+'}\n';t=t.replace('x = 1100 y = 1450','x = 1100 y = 1950')
# Replace overly repeated icons by subject. New story icons handle political milestones.
mapping={'constitution':'constitution','wtc_oil_and_rubber_offer':'trade','lone_wolf_path':'wolf','strengthen_ludolfs_power':'ludolf','admirals_council_coup':'admirals','direct_naval_rule':'admirals','last_chance_to_negotiate':'trade','equal_service':'constitution','colonial_hierarchy':'ludolf','sultans_compact':'sultans','colonial_charter':'constitution','naval_general_staff':'admirals','archipelago_command':'admirals','pacific_settlement':'defeat','admiralty_diplomacy':'trade'}
for key,icon in mapping.items():t=edit_focus(t,'A01_'+key,lambda b,icon=icon:re.sub(r'icon = \w+',f'icon = GFX_goal_story_{icon}',b,count=1))
# Reuse shipped subject-specific assets for economic and military branches.
vanilla={'archipelago_shipping':'focus_INS_economic_integration','batavia_docks':'focus_INS_naval_program','rubber_processing':'focus_generic_rubber_plantations','knil_reform':'focus_INS_reform_knil','island_garrisons':'focus_INS_infantry_training_borneo','marine_brigades':'focus_INS_elevate_elite_infantry','jungle_supply':'focus_INS_knil_engineers','coastal_watch':'focus_INS_request_naval_control','admiralty_shipyards':'focus_INS_naval_program','military_industry':'focus_INS_artillerie_inrichtingen','secure_sea_lanes':'focus_INS_request_naval_control'}
for key,asset in vanilla.items():t=edit_focus(t,'A01_'+key,lambda b,key=key:re.sub(r'icon = \w+',f'icon = GFX_goal_A01_subject_{key}',b,count=1))
write(fp,t)
write('tools/ludolf_icon_mapping.json',json.dumps(vanilla,indent=2))
fp='common/national_focus/a03_focus.txt';s=original(fp)
for key,icon in {'civil_government':'constitution','naval_government':'admirals','prefectural_reform':'ludolf','commercial_diplomacy':'trade','batavia_convention':'trade','resource_commission':'trade','batavia_ultimatum':'revanchism','southern_reconstruction':'defeat','naval_academy':'admirals','fleet_exercises':'admirals'}.items():
 s=edit_focus(s,'A03_'+key,lambda b,icon=icon:re.sub(r'icon = \w+',f'icon = GFX_goal_story_{icon}',b,count=1))
write(fp,s)
fp='common/ideas/pacific_ideas.txt';s=original(fp)
for key,icon in {'A01_colonial_administration':'ludolf','A01_naval_staff':'admirals','A03_civil_government':'constitution','A03_naval_government':'admirals','A03_commercial_network':'trade','A03_resource_commission':'trade','A03_naval_academy':'admirals','pacific_trade_accord_idea':'trade'}.items():
 s=re.sub(r'('+key+r' = \{ picture = )\w+',lambda m:m.group(1)+'story_'+icon,s)
write(fp,s)
loc('A01_pacific_settlement','Кабинет после поражения','The Post-defeat Cabinet','Людольф получит мандат на перестройку правительства. Последующие реформы определят, сохранится ли его власть или перейдёт к адмиралам.','Ludolf will seek a mandate to reorganise government. The following reforms will decide whether he remains in office or yields to the admirals.')

# Make the canonical AI route actually choose war rather than the older random pact.
p='events/pacific_diplomacy.txt';s=original(p);s=s.replace('ai_chance = { factor = 40 }','ai_chance = { factor = 0 }',1).replace('ai_chance = { factor = 60 }','ai_chance = { factor = 100 }',1);write(p,s)

# Brunei must belong to A01 before it can be ceded.
for p in (ROOT/'history/states').glob('1023*'):
 s=original(str(p.relative_to(ROOT)));s=s.replace('owner = ZZZ','owner = A01').replace('add_core_of = ZZZ','add_core_of = A01');write(str(p.relative_to(ROOT)),s)

# Autonomous polities are real subject countries, not only cosmetic modifiers.
tags='';colors=[(61,117,65),(170,141,43),(51,95,127)]
for (tag,sid,ru,en),color in zip([('A11',1055,'Султанат Кутай','Sultanate of Kutai'),('A12',334,'Султанат Понтианак','Sultanate of Pontianak'),('A13',1022,'Султанат Банджар','Sultanate of Banjar')],colors):
 tags+=f'{tag} = "countries/{tag}.txt"\n';write(f'common/countries/{tag}.txt','graphical_culture = asian_gfx\ngraphical_culture_2d = asian_2d\ncolor = rgb { '+' '.join(map(str,color))+' }\n')
 write(f'history/countries/{tag} - Sultanate.txt',f'capital = {sid}\nset_research_slots = 2\nset_politics = {{ ruling_party = neutrality elections_allowed = no }}\nset_popularities = {{ neutrality = 100 }}\nset_convoys = 10\nrecruit_character = {tag}_sultans_council\nset_technology = {{ infantry_weapons = 1 }}\n')
 write(f'common/characters/{tag}.txt',f'characters = {{ {tag}_sultans_council = {{ name = {tag}_council_name country_leader = {{ ideology = despotism expire = "1965.1.1.1" traits = {{ }} }} }} }}\n')
 for suffix in ['', '_DEF','_neutrality','_neutrality_DEF']:loc(tag+suffix,ru,en)
 loc(tag+'_ADJ',ru.replace('Султанат ','')+'ск.',en.replace('Sultanate of ',''))
 loc(tag+'_council_name','Двор султана','The Sultan\u2019s Court')
write('common/country_tags/01_borneo_sultanates.txt',tags)

write('common/ai_strategy_plans/A01_canonical.txt','''A01_ludolf_canonical_plan = {
 name = "Ludolf and the Borneo Convention"
 desc = "Civilian rule, defeat in the Borneo war, reconstruction and autonomous sultanates."
 allowed = { original_tag = A01 }
 enable = { is_historical_focus_on = yes }
 abort = { has_country_flag = A01_admirals_seized_power }
 ai_national_focuses = {
  A01_constitution A01_wtc_oil_and_rubber_offer A01_lone_wolf_path
  A01_strengthen_ludolfs_power A01_invest_in_mass_consumer_goods
  A01_governors_secretariat A01_officers_audience A01_civilian_procurement
  A01_naval_budget_compromise A01_last_chance_to_negotiate
  A01_build_bornean_fortifications A01_prepare_bornean_logistics
  A01_improve_bornean_fortifications A01_pacific_settlement
  A01_reconstruction_commission A01_autonomous_sultanates
  A01_northern_memory A01_federal_defence_compact A01_fleet_of_recovery
  A01_ludolf_survives A01_negotiated_resignation A01_review_borneo_convention
 }
}
A03_southern_canonical_plan = {
 name = "Japan Southern Strategy"
 desc = "The naval cabinet pursues the Borneo resource settlement."
 allowed = { original_tag = A03 }
 enable = { is_historical_focus_on = yes }
 ai_national_focuses = {
  A03_imperial_council A03_naval_government A03_southern_strategy
  A03_resource_commission A03_naval_programme A03_kure_yards
  A03_batavia_ultimatum A03_southern_bases A03_southern_campaign
  A03_osaka_industry A03_kansai_railways A03_hiroshima_arsenal
 }
}
''')

for lang,i in [('russian',0),('english',1)]:
 write(f'localisation/{lang}/zz_ludolf_story_l_{lang}.yml','l_'+lang+':\n'+''.join(f' {key}:0 {json.dumps(v[i],ensure_ascii=False)}\n' for key,v in L.items()),True)
write('tools/ludolf_story_manifest.json',json.dumps({'new_focuses':12,'peace_transfer_to_A03':[1024,1023],'peace_transfer_to_A01':[333,1022],'japanese_resource_right_states':BORNEO,'resources':['oil','rubber'],'sultanates':['A11','A12','A13'],'respect_range':[0,100]},indent=2))
print('Ludolf story, balance, decisions, bilateral WTC events, canonical peace and autonomous sultanates written.')
