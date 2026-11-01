"""Author the nine separate ratifications and the republican narrative."""
from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
L={'ru':{},'en':{}}
def loc(key,ru,en):L['ru'][key]=ru;L['en'][key]=en
def write(path,s):
 p=R/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')

members=[('PVI',624,'Висайской республики','Visayan Republic'),('PSM',625,'Самарской республики','Samar Republic'),
 ('PCB',628,'республики Себу','Republic of Cebu'),('PPN',1085,'республики Панай','Republic of Panay'),
 ('PMD',627,'Южного Минданао','Southern Mindanao'),('PNM',1026,'Северного Минданао','Northern Mindanao'),
 ('PNL',623,'Северного Лусона','Northern Luzon'),('PML',327,'Манильской республики','Manila Republic'),('PBT',1027,'Батаанской республики','Bataan Republic')]

events=['add_namespace = A10R_congress\n']
def event(n,title_ru,title_en,desc_ru,desc_en,options,trigger='tag = A10',immediate=''):
 key=f'A10R_congress.{n}'
 loc(key+'.t',title_ru,title_en);loc(key+'.d',desc_ru,desc_en)
 lines=[f'country_event = {{ id = {key} title = {key}.t desc = {key}.d picture = GFX_1896_event_talks is_triggered_only = yes',f' trigger = {{ {trigger} }}']
 if immediate:lines.append(' immediate = { '+immediate+' }')
 for i,(ru,en,effect,chance) in enumerate(options):
  ok=f'{key}.o{i}';loc(ok,ru,en)
  lines.append(f' option = {{ name = {ok} ai_chance = {{ factor = {chance} }} {effect} }}')
 lines.append('}');events.append('\n'.join(lines)+'\n')

event(1,'Столы под навесом','Tables beneath the Awning',
 'В Кавите не хватает зала для всех делегатов. Заседание продолжается под парусиновым навесом: одни требуют оружия для Лусона, другие — письменного обещания не отнимать у островов свободу. Председатель просит сначала выслушать тех, кто добирался сюда через японские патрули.',
 'Cavite has no hall large enough for the delegates. Beneath a canvas awning, some demand weapons for Luzon while others demand written guarantees of island liberty. The chairman asks them first to hear those who crossed the Japanese patrol lines.',
 [('Сначала скрепим обещания.','First make our promises binding.','add_to_variable = { A10R_cohesion = 8 } A10R_refresh = yes',65),
  ('Сначала откроем склады.','Open the depots first.','add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 250 producer = A10 } add_war_support = 0.03',35)])
event(2,'Печати Минданао','The Seals of Mindanao',
 'Посланники Минданао привезли две разные печати и общий список требований. Они готовы защищать острова, но не принимать чужих судей и сборщиков налогов. Военные торопят переговоры; переводчики просят дать старейшинам договорить.',
 'The Mindanao envoys bring two different seals and one list of demands. They will defend the islands, but refuse imposed judges and tax collectors. Officers urge haste; the interpreters ask that the elders be allowed to finish.',
 [('Подтвердить местное право.','Confirm local law.','add_to_variable = { A10R_cohesion = 10 } add_political_power = -25 A10R_refresh = yes',75),
  ('Общая оборона требует общего сбора.','Common defence requires common contributions.','add_political_power = 45 add_to_variable = { A10R_cohesion = -6 } A10R_refresh = yes',25)])
event(3,'Долговые расписки землевладельцев','The Landowners’ Promissory Notes',
 'В конгресс доставили тетрадь арендатора: долг за семена пережил два урожая и смену власти. Землевладелец требует уважать собственность, сельские делегаты — прекратить бесконечные взыскания. Решение станет известным далеко за пределами одной деревни.',
 'Congress receives a tenant’s notebook: a seed debt has survived two harvests and a change of government. The landowner demands respect for property; village delegates demand an end to endless collections. The decision will travel far beyond this village.',
 [('Проверить долги в открытом суде.','Review the debts in open court.','add_to_variable = { A10R_cohesion = 8 } add_political_power = -30 A10R_refresh = yes',75),
  ('Выкупить спорные обязательства из казны.','Redeem the disputed obligations.','add_political_power = -50 add_stability = 0.04 add_to_variable = { A10R_cohesion = 5 } A10R_refresh = yes',25)])
event(4,'Договор или конституция','Compact or Constitution',
 'Вопрос о будущем союза расколол даже старых товарищей. Одни видят в общем правительстве защиту от нового завоевателя, другие вспоминают, как столицы превращали временные полномочия в вечные. На столе лежат два проекта, и оба обещают свободу.',
 'The future of the union divides old comrades. Some see a common government as protection against another conqueror; others remember how capitals made temporary powers permanent. Two drafts lie on the table, and both promise liberty.',
 [('Обсудим оба проекта на островах.','Debate both drafts on the islands.','add_to_variable = { A10R_cohesion = 6 } A10R_refresh = yes',100)])
event(5,'Ни одной молчаливой ратификации','No Silent Ratifications',
 'Конвент направляет республикам проект федерального закона. Представители требуют записать: отсутствие ответа не означает согласия, а военная необходимость не отменяет местного голосования. Секретарь оставляет в книге отдельную страницу для каждой печати.',
 'The convention sends its draft federal law to the republics. Delegates insist that silence shall not mean consent and military necessity shall not annul local votes. The secretary leaves a separate page for every seal.',
 [('Разослать проект собраниям республик.','Send the draft to the republican assemblies.','custom_effect_tooltip = A10R_ratification_tt',100)])
event(6,'Федерация, которую ещё предстоит собрать','A Federation Still to Be Joined',
 'Федеральная конституция провозглашена. Делегаты, одобрившие её, остаются у стола, остальные возвращаются к своим избирателям. Теперь задача правительства — исполнить гарантии и заключить соглашение с каждой республикой, а не объявить все острова подчинёнными одной печати.',
 'The federal constitution is proclaimed. Delegates who approved it remain at the table; the others return to their voters. The government must now honour its guarantees and conclude each accession, rather than declare all islands subordinate to one seal.',
 [('Один закон, добровольное присоединение.','One law, voluntary accession.','add_to_variable = { A10R_cohesion = 5 } A10R_refresh = yes',100)])
event(7,'Имена в приходских книгах','Names in the Parish Registers',
 'Комиссия восстановления сравнивает армейские списки с приходскими книгами. Там, где штаб насчитал потерянные винтовки, деревни называют погибших кормильцев. В общей ведомости найдётся место и разрушенным мастерским, и семьям, которым некуда возвращаться.',
 'The reconstruction commission compares army rolls with parish registers. Where the staff counted lost rifles, villages name lost breadwinners. The common ledger must include ruined workshops and families with no home to return to.',
 [('Начать с семей погибших.','Begin with bereaved families.','add_political_power = -35 add_stability = 0.06',65),
  ('Сначала вернуть людям работу.','Restore livelihoods first.','add_political_power = 30 add_to_variable = { A10D_supply = 8 } A10D_refresh_supply = yes',35)])
event(8,'Девять мест под солнцем','Nine Places beneath the Sun',
 'Над местом заседания поднят союзный флаг. Республика, приславшая всего одного делегата, голосует рядом с многолюдными портами. Председатель читает договор: общая оборона, открытые гавани и обязательство решать споры словами прежде, чем брать оружие.',
 'The union flag rises above the assembly. A republic represented by one delegate votes beside the populous ports. The chairman reads the covenant: mutual defence, open harbours and a duty to attempt words before taking up arms.',
 [('Республики держат данное слово.','The republics keep their word.','add_political_power = 50',100)])
event(9,'Правительство перед палатами','The Cabinet before the Chambers',
 'Министры заняли скамьи перед двумя палатами. Среди депутатов — бывшие связные, учителя и владельцы прибрежных мастерских. Военные представители присутствуют как приглашённые: впервые после падения Манилы вопрос о бюджете решают без приказа штаба.',
 'The ministers take their seats before both chambers. Former couriers, teachers and coastal workshop owners sit among the deputies. Officers attend as guests: for the first time since Manila fell, the budget is decided without a staff order.',
 [('Открыть первое заседание.','Open the first sitting.','add_political_power = 75',100)])
event(10,'Пустующие места делегатов','The Delegates’ Empty Seats',
 'Несколько островных делегаций покинули заседание. Они обвиняют казну в сокрытии сборов, а штаб — в предпочтении одних портов другим. Союз не распадётся от одного спора, но молчание сделает следующий раскол гораздо глубже.',
 'Several island delegations have walked out. They accuse the treasury of hiding contributions and the staff of favouring certain ports. One dispute will not dissolve the union, but silence will deepen the next rupture.',
 [('Оплатить согласительную комиссию.','Fund a conciliation commission.','add_political_power = -60 add_to_variable = { A10R_cohesion = 18 } A10R_refresh = yes',60),
  ('Вернуть островам часть сборов.','Return part of the contributions.','add_timed_idea = { idea = A10R_emergency_concessions days = 150 } add_to_variable = { A10R_cohesion = 14 } A10R_refresh = yes',40)])

decisions=['A10R_federal_ratification = {']
for i,(tag,state,ru,en) in enumerate(members,20):
 consent=f'A10R_consent_{tag}';pending=f'A10R_vote_pending_{tag}';cool=f'A10R_vote_cooldown_{tag}'
 request=f'A10R_request_{tag}';join=f'A10R_accession_{tag}'
 local_vote=f'A10R_local_vote_{tag}'
 loc(local_vote,'Местное собрание: '+ru,'Local Assembly: '+en)
 loc(local_vote+'_desc','В освобождённой области созовём местных представителей для обсуждения федеральной хартии. Интеграция потребует их согласия, равных гражданских прав и доверия к новой администрации.',
     'Convene local representatives in the liberated territory to debate the federal charter. Integration will require their consent, equal civil rights and trust in the new administration.')
 decisions.append(f''' {local_vote} = {{ icon = generic_political_discourse cost = 35 fire_only_once = yes
  visible = {{ owns_state = {state} controls_state = {state} NOT = {{ has_country_flag = {consent} }} }}
  available = {{ has_country_flag = A10R_federal_guarantees {state} = {{ NOT = {{ compliance < 60 }} }} }}
  complete_effect = {{ if = {{ limit = {{ owns_state = {state} controls_state = {state} NOT = {{ has_country_flag = {consent} }} }}
   set_country_flag = {consent} add_to_variable = {{ A10R_federal_votes = 1 }} add_to_variable = {{ A10R_cohesion = 3 }} A10R_refresh = yes
  }} }}
  ai_will_do = {{ factor = 4 }}
 }}''')
 loc(request,'Ратификация: '+ru,'Ratification: '+en)
 loc(request+'_desc','Передадим проект конституции местному собранию. Республика вправе отказать; после нового обсуждения переговоры можно будет возобновить.',
     'Submit the constitution to the local assembly. The republic may refuse; negotiations can resume after a new round of discussion.')
 loc(join,'Присоединение: '+ru,'Accession: '+en)
 loc(join+'_desc','После согласия республики и принятия единого гражданства её учреждения войдут в федерацию. Голосование не даёт права забирать земли, захваченные чужими войсками.',
     'With republican consent and equal citizenship, its institutions may join the federation. A vote conveys no right to seize territory held by foreign armies.')
 decisions.append(f''' {request} = {{ icon = generic_political_discourse cost = 25 days_re_enable = 90
  visible = {{ {tag} = {{ is_subject_of = A10 }} NOT = {{ has_country_flag = {consent} }} }}
  available = {{ {tag} = {{ is_subject_of = A10 has_capitulated = no }} has_country_flag = A10R_federal_guarantees NOT = {{ has_country_flag = {pending} }} NOT = {{ has_country_flag = {cool} }} }}
  complete_effect = {{ set_country_flag = {{ flag = {pending} days = 30 }} {tag} = {{ country_event = {{ id = A10R_congress.{i} days = 2 }} }} }}
  ai_will_do = {{ factor = 5 }}
 }}
 {join} = {{ icon = generic_political_discourse cost = 60 fire_only_once = yes
  visible = {{ {tag} = {{ is_subject_of = A10 }} has_country_flag = {consent} }}
  available = {{ has_country_flag = A10_federal_path has_country_flag = A10R_equal_rights has_war = no {tag} = {{ is_subject_of = A10 has_war = no NOT = {{ any_owned_state = {{ NOT = {{ is_controlled_by = {tag} }} }} }} }} }}
  complete_effect = {{
   if = {{ limit = {{ has_country_flag = {consent} {tag} = {{ is_subject_of = A10 has_war = no NOT = {{ any_owned_state = {{ NOT = {{ is_controlled_by = {tag} }} }} }} }} }}
    annex_country = {{ target = {tag} transfer_troops = yes }}
    every_owned_state = {{ limit = {{ A10R_archipelago_state_trigger = yes is_core_of = {tag} is_controlled_by = A10 }} add_core_of = A10 }}
    add_to_variable = {{ A10R_cohesion = 3 }} A10R_refresh = yes
   }}
  }}
  ai_will_do = {{ factor = 6 }}
 }}''')
 event(i,'Федеральный проект: '+ru,'Federal Draft: '+en,
       'Посланник Кавите представил проект общей конституции. Он обещает местные советы, равное гражданство и представительство в палате островов. Собрание должно решить, доверяет ли оно этим гарантиям. Отказ сохранит республику в прежнем союзе.',
       'Cavite’s envoy presents a common constitution promising local councils, equal citizenship and island representation. The assembly must decide whether it trusts these guarantees. Refusal will preserve the republic within the existing union.',
       [('Ратифицировать при сохранении местных прав.','Ratify with local rights preserved.',f'''A10 = {{ clr_country_flag = {pending} if = {{ limit = {{ NOT = {{ has_country_flag = {consent} }} }} set_country_flag = {consent} add_to_variable = {{ A10R_federal_votes = 1 }} add_to_variable = {{ A10R_cohesion = 3 }} A10R_refresh = yes }} }} add_stability = 0.03''',
         '65 modifier = { factor = 1.8 A10 = { check_variable = { A10R_cohesion > 64 } } } modifier = { factor = 0.5 A10 = { check_variable = { A10R_cohesion < 40 } } }'),
        ('Сохранить республиканский договор.','Preserve the republican compact.',f'A10 = {{ clr_country_flag = {pending} set_country_flag = {{ flag = {cool} days = 150 }} add_to_variable = {{ A10R_cohesion = -2 }} A10R_refresh = yes }}',35)],
       trigger=f'tag = {tag} is_subject_of = A10 A10 = {{ has_country_flag = A10R_federal_transition }}')
decisions.append('}')
write('common/decisions/A10R_ratification.txt','\n'.join(decisions)+'\n')

# A costly negotiated way out of a losing war. No territorial transfers.
write('common/decisions/A10R_armistice.txt','''A10_japanese_settlement = {
 A10R_request_defensive_armistice = {
  icon = generic_political_discourse cost = 75 days_re_enable = 180
  visible = { has_war_with = A03 date > 1894.1.1 }
  available = { is_subject = no has_capitulated = no controls_state = 1084 has_war_support < 0.20 NOT = { has_country_flag = A10R_armistice_pending } }
  complete_effect = { set_country_flag = { flag = A10R_armistice_pending days = 30 } A03 = { country_event = { id = A10R_congress.40 days = 2 } } }
  ai_will_do = { factor = 1 }
 }
}
''')
loc('A10R_request_defensive_armistice','Предложить оборонительное перемирие','Propose a Defensive Armistice')
loc('A10R_request_defensive_armistice_desc','Если силы островов иссякли, можно предложить прекращение войны без территориальных уступок. Япония вправе отказаться. Цена согласия — тяжёлый удар по престижу правительства.',
    'If the islands are exhausted, propose an end to hostilities without territorial concessions. Japan may refuse. Acceptance will seriously damage the government’s prestige.')
loc('A10_japanese_settlement_desc','Условия мира зависят от освобождённых гаваней. Полное соглашение требует освобождения японских владений архипелага; Манильский компромисс оставляет северный Лусон и Батаан Японии. Тяжёлое истощение позволяет просить отдельного перемирия.',
    'Peace terms depend on the harbours liberated. A full settlement requires liberation of the Japanese archipelago possessions; a Manila compromise leaves northern Luzon and Bataan to Japan. Severe exhaustion permits a separate armistice request.')
event(40,'Посланник из Кавите','An Envoy from Cavite',
 'Филиппинский посланник предлагает прекратить боевые действия и вернуть войска за прежние границы. Манильские офицеры называют это упущенной победой, казначейство — возможностью сократить расходы. Никаких новых уступок островитяне не предлагают.',
 'A Philippine envoy proposes an end to hostilities and the withdrawal of troops behind the old borders. Manila’s officers call it a lost victory; the treasury calls it an opportunity to reduce expenses. The islanders offer no new concessions.',
 [('Принять прекращение огня.','Accept the ceasefire.','A10 = { clr_country_flag = A10R_armistice_pending white_peace = { tag = A03 } every_subject_country = { if = { limit = { has_war_with = A03 } white_peace = { tag = A03 } } } set_country_flag = A10R_defensive_armistice add_stability = -0.08 add_timed_idea = { idea = A10R_bitter_armistice days = 365 } country_event = { id = A10R_congress.41 days = 1 } }',35),
  ('Продолжать кампанию.','Continue the campaign.','A10 = { clr_country_flag = A10R_armistice_pending add_war_support = 0.03 }',65)],
 trigger='tag = A03 has_war_with = A10 A10 = { is_subject = no }')
event(41,'Горькая тишина','A Bitter Silence',
 'На пристанях снова разгружают мирные товары, но северные гавани остались под чужим флагом. Правительство говорит о спасённых жизнях. Вернувшиеся солдаты молчат. Впереди восстановление страны и долгий спор о цене мира.',
 'Peaceful cargo returns to the quays, but the northern harbours remain under a foreign flag. The government speaks of lives saved. Returning soldiers remain silent. Reconstruction and a long argument over the price of peace lie ahead.',
 [('Сберечь то, что удалось удержать.','Preserve what we managed to hold.','',100)])
write('events/A10R_republics.txt','\n'.join(events))

spirits=[
 ('provisional_compact','Временный договор республик','Provisional Republican Compact','Общие учреждения ещё слабы, но первые обязательства уже скреплены печатями островов.','Common institutions remain fragile, but the islands have sealed their first mutual obligations.'),
 ('common_treasury_spirit','Открытая союзная казна','An Open Union Treasury','Республики видят, куда идут их взносы, и могут требовать ответа у казначеев.','The republics can see where their contributions go and hold the treasurers accountable.'),
 ('arbitration','Межостровный арбитраж','Inter-Island Arbitration','Споры между советами разбирает общий суд, а не республиканские отряды.','A common court, rather than republican detachments, settles disputes between councils.'),
 ('tenant_rights','Гарантии сельских общин','Village Guarantees','Письменные договоры и проверка долгов защищают сельские семьи от произвола.','Written leases and debt reviews protect village families against arbitrary exactions.'),
 ('confederal_covenant','Союз суверенных республик','Union of Sovereign Republics','Острова связывает постоянный договор, общая оборона и взаимная ответственность.','A permanent compact, common defence and mutual responsibility bind the islands.'),
 ('customs_union_spirit','Общая внешняя таможня','Common External Customs','Внутренние пошлины уступили место открытым гаваням и согласованным внешним сборам.','Open harbours and agreed external duties have replaced internal tariffs.'),
 ('republican_solidarity','Республиканская солидарность','Republican Solidarity','Разные знамёна больше не мешают совместной обороне родных берегов.','Different banners no longer impede the common defence of the islands.'),
 ('bill_of_rights_spirit','Гарантии федеральной хартии','Federal Charter Guarantees','Местные языки, советы и верования защищены общим законом.','Common law protects local languages, councils and faiths.'),
 ('federal_citizenship','Единое островное гражданство','Common Island Citizenship','Место рождения больше не определяет права человека перед федеральным законом.','Birthplace no longer determines a person’s rights before federal law.'),
 ('responsible_cabinet','Правительство перед парламентом','A Cabinet Answerable to Parliament','Министры обязаны обосновывать свои решения перед двумя палатами.','Ministers must justify their decisions before both chambers.'),
 ('fractured_council','Разлад островных советов','Divided Island Councils','Делегаты не доверяют общей казне, а командиры спорят о снабжении.','Delegates distrust the common treasury while commanders dispute their supplies.'),
 ('trusted_council','Доверие островов','Trust of the Islands','Советы исполняют общие решения, потому что участвовали в их принятии.','Councils carry out common decisions because they took part in making them.'),
 ('emergency_concessions','Чрезвычайные уступки республикам','Emergency Republican Concessions','Часть союзных доходов временно оставлена местным советам ради сохранения согласия.','Part of union revenue has temporarily returned to local councils to preserve agreement.'),
 ('reconstruction','Обязательства восстановления','Reconstruction Obligations','Пристани, дороги и семьи погибших требуют помощи из общей казны.','Quays, roads and bereaved families require support from the common treasury.'),
 ('island_recovery','Острова возвращаются к жизни','The Islands Recover','Вновь работают мастерские, возвращаются семьи, открываются школы.','Workshops reopen, families return and schools welcome their pupils.'),
 ('bitter_armistice','Горечь перемирия','A Bitter Armistice','Война остановлена, но обещание вернуть все северные гавани осталось неисполненным.','The war is over, but the promise to recover all northern harbours remains unfulfilled.')]
for id,ru,en,rd,ed in spirits:loc('A10R_'+id,ru,en);loc('A10R_'+id+'_desc',rd,ed)
loc('A10R_council','Совет республик','Council of the Republics')
loc('A10R_council_desc','Согласие островов: [?A10R_cohesion|0]/100. Военные нужды испытывают союз на прочность; открытая казна и собрания делегатов укрепляют доверие.',
    'Island cohesion: [?A10R_cohesion|0]/100. War tests the union; an open treasury and meetings of delegates build trust.')
loc('A10R_federal_ratification','Федеральные ратификации','Federal Ratifications')
loc('A10R_federal_ratification_desc','Одобрено республиками: [?A10R_federal_votes|0]. Для провозглашения федерации нужны три согласия либо согласие всех оставшихся республик, если их меньше трёх, и согласие островов не ниже 40. Присоединение требует мира, ратификации и единого гражданства; местные национальные земли сохраняются.',
    'Republican approvals: [?A10R_federal_votes|0]. Proclamation requires three approvals, or all remaining republics if fewer than three, and cohesion of at least 40. Accession requires peace, ratification and equal citizenship; local national territories are retained.')
loc('A10R_ratification_tt','Открываются отдельные переговоры о ратификации с республиками — участницами союза. Каждая может согласиться или отказать.',
    'Separate ratification negotiations open with subject republics. Each may accept or refuse.')
for id,ru,en,rd,ed in [
 ('convene_delegates','Созвать островных делегатов','Convene the Island Delegates','Выслушаем жалобы республик и согласуем общий порядок снабжения.','Hear republican grievances and agree a common supply order.'),
 ('emergency_contributions','Попросить чрезвычайные поставки','Request Emergency Contributions','Республики выделят оружие из местных запасов, но такая просьба испытывает их доверие.','The republics can release local rifle stocks, but the request will test their trust.'),
 ('publish_accounts','Опубликовать союзные счета','Publish the Union Accounts','Открытые ведомости покажут советам, что их взносы не исчезают в чужих карманах.','Open ledgers will show councils that their contributions are not disappearing into private pockets.')]:
 loc('A10R_'+id,ru,en);loc('A10R_'+id+'_desc',rd,ed)
loc('A10R_federal_presidency_name','Федеральный гражданский кабинет','Federal Civilian Cabinet')
loc('A10R_federal_presidency_desc','Избранное правительство, ответственное перед палатой населения и палатой островов.','An elected government answerable to the population chamber and the island chamber.')
loc('A10R_confederal_presidency_name','Совет островных республик','Council of Island Republics')
loc('A10R_confederal_presidency_desc','Союзное председательство, ответственное перед делегатами суверенных островных республик.','A union presidency answerable to delegates of the sovereign island republics.')
loc('A10_separatism_desc','Местные советы опасаются, что общее правительство повторит порядки прежних завоевателей. Печать Кавите ещё не заменяет доверия островов.','Local councils fear that a common government will repeat the practices of earlier conquerors. Cavite’s seal has yet to earn island trust.')
loc('A10_federal_administration_desc','Общий устав связывает провинциальные службы с избираемыми советами. Доверие к новым учреждениям растёт медленно и требует соблюдения обещанных прав.','A common statute connects provincial services with elected councils. Trust in the new institutions grows gradually and requires their promised rights to be honoured.')
loc('A10_common_army_desc','Республики содержат собственные отряды, но склады, переправы и распоряжения штаба подчиняются общему порядку.','The republics maintain their own detachments, but depots, crossings and staff orders follow a common arrangement.')
for lang,code in [('russian','ru'),('english','en')]:
 lines=['l_'+lang+':']
 legacy=R/f'localisation/{lang}/1896_ideas_l_{lang}.yml'
 legacy_text=legacy.read_text(encoding='utf-8-sig')
 for k,v in L[code].items():
  entry=' '+k+':0 "'+v.replace('"','\\"').replace('\n','\\n')+'"'
  pattern=r'^ '+re.escape(k)+r':\d+ .*?$'
  if re.search(pattern,legacy_text,re.M):legacy_text=re.sub(pattern,lambda m:entry,legacy_text,flags=re.M)
  else:lines.append(entry)
 legacy.write_text(legacy_text,encoding='utf-8-sig',newline='\n')
 (R/f'localisation/{lang}/A10R_republics_l_{lang}.yml').write_text('\n'.join(lines)+'\n',encoding='utf-8-sig')
print('Generated republican events, nine consent/accession pairs and bilingual localisation.')
