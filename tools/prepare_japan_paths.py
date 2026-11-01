"""Small political route prologues. No completed regime changes or peace shortcuts."""
from extend_japan_story import R, read, write, span
import json,re

L = {}
def loc(k, ru, en): L[k] = (ru, en)
def named(k, ru, en, rd, ed):
 loc(k, ru, en); loc(k+'_desc', rd, ed)

# Each tuple defines a political bargain, its institution, and the price of funding it.
paths = [
 dict(key='sea', title='Морская империя', en='Maritime Empire', icon='A03_southern_strategy', nexticon='A03_combined_operations',
  next='Устав морских самураев', nexten='Charter of the Sea Samurai', spirit='Пакт трона и адмиралтейства', spiriten='Throne and Admiralty Pact', picture='jpc_fleet',
  mod='navy_org_factor = 0.05 army_org_factor = -0.03',
  desc='Ито предлагает двору соглашение, а не переворот: император сохраняет трон, адмиралтейство получает право определять южный курс. Кредиторы ещё потребуют своего, а северные офицеры запомнят, чьими интересами пожертвовали.',
  descen='Ito offers an agreement, not a coup: the Emperor keeps his throne while the Admiralty sets the southern course. Creditors still expect payment; northern officers remember whose interests were sacrificed.',
  step='Новая морская каста начинается с устава и учебной команды. Отбор людей из сухопутных частей обещает опыт десантных операций, но требует отдельного бюджета. Корпус ещё предстоит создать.',
  stepen='A new naval caste begins with a charter and training cadre. Drawing officers from the army can improve landing operations, but requires its own budget. The corps itself remains a future project.',
  event='Ито кладёт перед императором список инструкторов. В нём офицеры, которых армия не готова отпустить. Адмирал просит оплатить отдельную учебную команду: тогда спор о подчинении можно отложить. Двор вправе ограничиться уставом, однако бумага не научит людей высаживаться под огнём.',
  eventen='Ito presents a list of instructors whom the army is unwilling to release. Funding a separate training cadre could postpone the dispute over command. A charter alone will not teach men to land under fire.',
  a='Оплатить учебную команду', aen='Fund the training cadre', reward='navy_experience = 20 army_experience = 5',
  b='Пока утвердить только устав', ben='Approve only the charter for now', modest='navy_experience = 5'),
 dict(key='land', title='Континентальная империя', en='Continental Empire', icon='A03_standard_rifles', nexticon='A03_expeditionary_staff',
  next='Посланники Чистой Земли', nexten='Envoys of the Pure Land', spirit='Проповедь возвращения', spiriten='Sermon of Return', picture='jpc_north',
  mod='army_org_factor = 0.05 navy_org_factor = -0.03',
  desc='Сайго нужен путь на Хонсю, открытый словом, а не штыком. Его сторонники ищут союз офицеров, крестьян и жрецов вокруг возвращения на континент. Флот воспринимает проповедь как покушение на свой бюджет.',
  descen='Saigo needs a road to Honshu opened by preaching rather than bayonets. Officers, peasants and priests rally around a return to the continent. The fleet sees a challenge to its budget.',
  step='Допустить делегацию северных проповедников и подготовить обращение будущего Ордена Чистой Земли. Ни Хоккайдо, ни его армия не переходят под власть Токио одним росчерком пера.',
  stepen='Receive northern preachers and draft an appeal for a future Order of the Pure Land. Neither Hokkaido nor its army can be brought under Tokyo by a stroke of the pen.',
  event='Посланники привезли рассказы о Песни и просьбу открыть школы для добровольцев. Они обещают дисциплину, но не подчинение морскому министерству. Офицеры флота требуют закрытых слушаний; сторонники Сайго — публичной кафедры.',
  eventen='The envoys bring accounts of the Song and ask for volunteer schools. They promise discipline, but not obedience to the naval ministry. Admirals demand closed hearings; Saigo’s supporters demand a public platform.',
  a='Открыть школы добровольцев', aen='Open volunteer schools', reward='army_experience = 20 add_war_support = 0.03 add_stability = -0.02',
  b='Ограничиться закрытыми слушаниями', ben='Hold closed hearings', modest='army_experience = 5'),
 dict(key='trade', title='Торговая империя', en='Commercial Empire', icon='A03_merchant_marine', nexticon='A01_wtc_oil_and_rubber_offer',
  next='Цена будущего мира', nexten='The Price of a Future Peace', spirit='Кредит доверия Осаке', spiriten='Osaka’s Political Credit', picture='jpc_credit',
  mod='consumer_goods_factor = -0.03 war_support_factor = -0.05',
  desc='Ивасаки просит политический мандат искать договор вместо победы. Директора обещают оживить оборот, военные видят готовность уступить. Перемирия пока нет: сначала нужно выяснить, кто оплатит его цену.',
  descen='Iwasaki seeks a mandate to pursue agreement rather than victory. Directors promise revived trade; officers see a willingness to surrender. There is no truce yet: its price must first be calculated.',
  step='Собрать долговые книги и подготовить условия для будущих переговоров с Батавией. Оплаченная ревизия уменьшит внутреннее долговое давление; проект мира сам по себе не остановит войну и не изменит требования Нидерландов.',
  stepen='Collect debt ledgers and prepare terms for future talks with Batavia. A funded audit reduces domestic debt pressure. A draft peace neither stops the war nor changes Dutch demands.',
  event='В Осаке составляют две сметы: сколько стоит продолжать войну и сколько потребуют за её прекращение. Представитель Палаты интересуется залогом, банкиры — очередностью выплат. Ивасаки предлагает сначала открыть собственные книги, рискуя доверием кредиторов.',
  eventen='Osaka draws up two estimates: the cost of continuing the war and the price of ending it. The Chamber asks about collateral; bankers ask about repayment priority. Iwasaki proposes opening his own ledgers first.',
  a='Оплатить независимую ревизию', aen='Fund an independent audit', reward='add_to_variable = { JPF_debt_pressure = -6 } add_to_variable = { JPF_budget_confidence = 5 } JPF_refresh_effect = yes',
  b='Подготовить закрытую записку', ben='Prepare a confidential memorandum', modest='add_to_variable = { JPF_budget_confidence = 2 } JPF_refresh_effect = yes'),
 dict(key='kami', title='Синтоистская реставрация', en='Shinto Restoration', icon='A01_sultans_compact', nexticon='A01_equal_service',
  next='Первый собор святилищ', nexten='First Assembly of Shrines', spirit='Круг будущего Совета Ками', spiriten='The Future Kami Council', picture='jpc_north',
  mod='war_support_factor = 0.06 consumer_goods_factor = 0.03',
  desc='Священнослужители предлагают освятить решения трона и объединить страну вокруг живого божества. Их круг ещё не стал Советом Ками, но содержание святилищ уже требует средств. Личная власть Мэйдзи и власть жрецов от его имени — разные будущие.',
  descen='Priests offer to unite the country around a living deity. Their circle is not yet a Kami Council, but supporting shrines already costs money. Meiji’s personal rule and priestly rule in his name are different futures.',
  step='Собрать представителей святилищ для обсуждения будущего Божественного Самурайского Ордена. Собор должен решить, начать ли помощь семьям солдат или ограничиться общим воззванием.',
  stepen='Gather shrine representatives to discuss a future Divine Samurai Order. The assembly must decide whether to support soldiers’ families or issue only a joint proclamation.',
  event='Жрецы расходятся в том, с чего начинается очищение. Одни требуют торжественного воззвания, другие указывают на семьи погибших, которым нечем платить за рис. Общий фонд даст собору опору в деревнях, но его придётся организовать за государственный счёт.',
  eventen='The priests disagree about where purification begins. Some demand a proclamation; others point to bereaved families unable to buy rice. A common fund would build support in the villages, but requires state organisation.',
  a='Учредить фонд семей солдат', aen='Establish a soldiers’ family fund', reward='add_stability = 0.04 add_war_support = 0.02',
  b='Обратиться к стране с воззванием', ben='Issue a proclamation', modest='add_war_support = 0.02'),
 dict(key='throne', title='Императорский абсолютизм', en='Imperial Absolutism', icon='A03_imperial_council', nexticon='A01_governors_secretariat',
  next='Канцелярия личного доклада', nexten='Office of Personal Reports', spirit='Личный мандат Мэйдзи', spiriten='Meiji’s Personal Mandate', picture='pacific_japan',
  mod='political_power_gain = 0.10 stability_factor = -0.03',
  desc='Мэйдзи требует прямых докладов, минуя посредников трёх фракций. Это первый шаг к личному правлению, а не передача власти жрецам. Ведомства сопротивляются проверкам; гвардию и новую бюрократию ещё нужно построить.',
  descen='Meiji demands direct reports that bypass the three factions. This is a first step towards personal rule, not priestly government. Ministries resist scrutiny; a guard and loyal bureaucracy still have to be built.',
  step='Сформировать небольшую канцелярию, подотчётную лично императору. Проверка счетов укрепит государственное доверие, но потребует политического капитала. Титул Хранителя Севера ещё не лишает Сайго его армии.',
  stepen='Establish a small office accountable to the Emperor. Inspecting accounts builds confidence but consumes political capital. Calling Saigo Guardian of the North would not by itself deprive him of his army.',
  event='Впервые донесения флота, армии и Осакских банков лежат на одном столе. Числа не сходятся. Чиновники предлагают начать с формы доклада; Мэйдзи может потребовать настоящую сверку и принять на себя недовольство всех ведомств.',
  eventen='Fleet, army and Osaka bank reports lie on the same desk for the first time. Their figures disagree. Officials propose standardising the forms; Meiji can demand a real reconciliation and face every ministry’s resentment.',
  a='Проверить счета всех ведомств', aen='Reconcile every ministry’s accounts', reward='add_to_variable = { JPF_budget_confidence = 8 } JPF_refresh_effect = yes add_stability = 0.02',
  b='Начать с единой формы доклада', ben='Standardise the reports first', modest='add_to_variable = { JPF_budget_confidence = 2 } JPF_refresh_effect = yes'),
]

def main():
 loc('A03_imperial_council','Кризис трёх голов','Crisis of the Three Heads')
 loc('A03_imperial_council_desc','Совет занимает 14 дней и открывает пять взаимоисключающих путей. Морская империя — канонический вход в основную ветку: ещё 21 день на соглашение и четыре приоритета по 35 дней. Все приготовления требуют 175 дней при 120 днях до ультиматума. У альтернатив пока есть только первые шаги; таймер войны действует для всех.','The 14-day council opens five mutually exclusive routes. Maritime Empire leads into the main campaign: a 21-day pact and four preparations of 35 days each. Completing all of them takes 175 days against a 120-day ultimatum deadline. Alternatives currently contain only their opening steps; the war clock applies to all routes.')
 p='common/national_focus/a03_focus.txt'; s=read(p)
 for d in paths:
  for suffix in ['', '_institution']:
   fid='JPX_'+d['key']+suffix
   if 'id = '+fid+' ' in s:
    a,b=span(s,fid);s=s[:a]+s[b:]
 if '# JPX canonical gateway' not in s:
  # Make room for the common political choice above the original campaign.
  ids=re.findall(r'\bid\s*=\s*((?:A03|JPC|JPF|JPN|JPL)_\w+)',s)
  for fid in ids:
   if fid in ['A03_focus','A03_imperial_council']:continue
   a,b=span(s,fid);part=s[a:b]
   part=re.sub(r'\by\s*=\s*(\d+)',lambda m:'y = '+str(int(m[1])+1),part,count=1)
   s=s[:a]+part+s[b:]
  s='# JPX canonical gateway\n'+s
 for fid in ['JPC_state_guarantees','JPC_northern_protocol','JPC_manila_priority','JPC_batavia_demands']:
  a,b=span(s,fid);part=s[a:b].replace('focus = A03_imperial_council','focus = JPX_sea');s=s[:a]+part+s[b:]
 blocks=[];ideas=[];events=['add_namespace = japan_paths']
 note='\\n\\n§YНачало альтернативного пути.§! Выбор исключает остальные четыре направления, включая основную морскую ветку. Пока доступен только пролог; смена режима и отдельный исход войны ещё не реализованы. Таймер войны продолжает идти.'
 ennote='\\n\\n§YAlternative route prologue.§! Selecting this route excludes the other four, including the main maritime campaign. Only the prologue is available; regime changes and alternative war settlements are not implemented yet. The war clock continues to run.'
 for i,d in enumerate(paths,1):
  fid='JPX_'+d['key'];follow=fid+'_institution';spirit=fid+'_mandate';eid=f'japan_paths.{i}';x=[20,0,8,32,40][i-1]
  mutex=' '.join('focus = JPX_'+other['key'] for other in paths if other!=d)
  ai='factor = 0' if d['key']!='sea' else 'factor = 100'
  blocks.append(f''' focus = {{ id = {fid} icon = GFX_goal_unique_{d['icon']} x = {x} y = 1 cost = 3
  prerequisite = {{ focus = A03_imperial_council }}
  mutually_exclusive = {{ {mutex} }}
  ai_will_do = {{ {ai} }}
  completion_reward = {{ set_country_flag = {fid}_chosen add_ideas = {spirit} custom_effect_tooltip = JPX_prologue_tt }}
 }}
 focus = {{ id = {follow} icon = GFX_goal_unique_{d['nexticon']} x = {34 if i==1 else x} y = {3 if i==1 else 2} cost = 4
  prerequisite = {{ focus = {fid} }} ai_will_do = {{ factor = 4 }}
  completion_reward = {{ country_event = {{ id = {eid} days = 1 }} }}
 }}''')
  ideas.append(f' {spirit} = {{ picture = {d["picture"]} removal_cost = -1 modifier = {{ {d["mod"]} }} }}')
  events.append(f'''country_event = {{ id = {eid} title = {eid}.t desc = {eid}.d picture = GFX_jpc_council is_triggered_only = yes
 trigger = {{ tag = A03 }}
 option = {{ name = {eid}.a trigger = {{ has_political_power > 49 }} ai_chance = {{ factor = 60 }} add_political_power = -50 {d['reward']} set_country_flag = {fid}_funded }}
 option = {{ name = {eid}.b ai_chance = {{ factor = 40 }} {d['modest']} set_country_flag = {fid}_limited }}
}}''')
  route_note='\\n\\n§YКанонический путь.§! Открывает основную ветку Японии: соглашение с Мицубиси, Северный протокол, Манилу и войну за Борнео. Исключает четыре альтернативных направления.' if i==1 else note
  route_en='\\n\\n§YCanonical route.§! Opens Japan’s main tree: Mitsubishi, the Northern Protocol, Manila and the Borneo war. Excludes the four alternative routes.' if i==1 else ennote
  named(fid,d['title'],d['en'],d['desc']+route_note,d['descen']+route_en)
  named(follow,d['next'],d['nexten'],d['step']+'\\n\\nСобытие предложит полную программу за §Y50 политической власти§! или ограниченный первый шаг.',d['stepen']+'\\n\\nAn event offers a full programme for §Y50 political power§! or a limited first step.')
  named(spirit,d['spirit'],d['spiriten'],d['desc'],d['descen'])
  loc(eid+'.t',d['next'],d['nexten']);loc(eid+'.d',d['event'],d['eventen']);loc(eid+'.a',d['a'],d['aen']);loc(eid+'.b',d['b'],d['ben'])
 loc('JPX_prologue_tt','Выбран политический курс. Это подготовительная часть пути: она не заключает мир, не меняет владельцев территорий и не завершает преобразование государства.','A political course has been chosen. This prologue does not conclude peace, transfer territory or complete a transformation of the state.')
 # Preserve the preparation subtree and its clock behind the canonical gateway.
 s=s.rstrip();assert s.endswith('}');s=s[:-1]+'\n# JPX political prologues: institutions inside political paths.\n'+'\n'.join(blocks)+'\n}\n';write(p,s)
 write('common/ideas/JPX_paths.txt','ideas = { country = {\n'+'\n'.join(ideas)+'\n} }\n')
 write('events/JPX_paths.txt','\n'.join(events)+'\n')
 p='common/ai_strategy_plans/A01_canonical.txt';ai=read(p)
 ai=ai.replace('A03_imperial_council JPC_state_guarantees','A03_imperial_council JPX_sea JPC_state_guarantees');write(p,ai)
 for idx,lang in enumerate(['russian','english']):
  write(f'localisation/{lang}/zzzzzzzzz_JPX_paths_l_{lang}.yml','l_'+lang+':\n'+''.join(f' {k}:0 "{v[idx]}"\n' for k,v in L.items()),True)
 write('tools/japan_paths_manifest.json',json.dumps({'focuses':[f'JPX_{d["key"]}{suffix}' for d in paths for suffix in ['', '_institution']], 'events':[f'japan_paths.{i}' for i in range(1,6)],'scope':'Maritime route opens the main campaign; four alternative prologues; war clock unchanged.'},ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
