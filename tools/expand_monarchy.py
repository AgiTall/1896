from pathlib import Path
import re, shutil
R=Path.cwd()
source=Path(r'C:/Users/AgiTall/.codex/attachments/a4b73a8d-0678-48a6-9f23-eb62c0dbd225/Вставленный текст.txt').read_text(encoding='utf-8-sig')
ns={"__file__":str(R/"tools/add_canon_countries.py")}; exec((R/'tools/add_canon_countries.py').read_text(encoding='utf-8').split('states = {}')[0],ns)
parse,value,dump=ns['parse'],ns['value'],ns['dump']
def save(path,text):
 p=R/path
 if p.exists():
  b=R/'tools/backups/monarchy_expansion'/path;b.parent.mkdir(parents=True,exist_ok=True)
  if not b.exists():shutil.copy2(p,b)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8-sig' if p.suffix=='.yml' else 'utf-8')
def setv(n,k,v):n[:]=[t for t in n if t[0]!=k]+[(k,'=',v)]
p='common/national_focus/a01_focus.txt'; tree=parse((R/p).read_text(encoding='utf-8-sig')); body=value(tree,'focus_tree')
new=parse(re.findall(r'```hoi4\s*(.*?)```',source,re.S)[0])
fs={value(v,'id'):v for k,o,v in body if k=='focus'}
# Royal branch occupies columns 22--30, clear of Council and federal focuses.
positions={'A01_crown_above_factions':(26,14),'A01_royal_island_charter':(26,15),'A01_crown_island_council':(22,16),'A01_crown_legal_guarantees':(26,16),'A01_island_delegation':(22,17),'A01_emma_and_daughter':(26,17),'A01_wilhelmina_comes_of_age':(26,19),'A01_royal_guard_corps':(30,16),'A01_royal_naval_advisors':(30,17),'A01_royal_constitution':(24,20),'A01_crown_parliament':(24,21),'A01_crown_commonwealth':(24,22),'A01_royal_dictatorship':(28,20),'A01_crown_absolute_rule':(28,21),'A01_royal_secret_police':(30,21),'A01_crown_militarism':(28,22)}
for k,o,n in new:
 fid=value(n,'id');fs[fid]=n;body.append((k,o,n))
for fid,(x,y) in positions.items():setv(fs[fid],'x',str(x));setv(fs[fid],'y',str(y))
for fid in positions:
 n=fs[fid];setv(n,'allow_branch',parse('has_country_flag = A01_royal_path_revealed'))
 # Use guaranteed existing sprite identifiers.
 setv(n,'icon','GFX_goal_generic_neutrality_focus' if 'guard' not in fid and 'naval' not in fid and 'militarism' not in fid else 'GFX_goal_unique_A01_archipelago_command')
for fid in ('A01_crown_absolute_rule','A01_royal_secret_police','A01_crown_militarism','A01_crown_parliament','A01_crown_commonwealth'):setv(fs[fid],'available',parse('has_country_flag = A01_wilhelmina_reigns'))
n=fs['A01_wilhelmina_comes_of_age'];setv(n,'prerequisite',parse('focus = A01_emma_and_daughter'));setv(n,'available',parse('has_country_flag = A01_emma_regency OR = { date > 1898.8.30 has_country_flag = A01_early_royal_accession }'))
n=fs['A01_royal_constitution'];setv(n,'mutually_exclusive',parse('focus = A01_royal_dictatorship'));setv(n,'available',parse('has_country_flag = A01_wilhelmina_reigns'))
# Parliament cannot precede island representation, and officers must back an absolute crown.
fs['A01_crown_parliament'].append(('prerequisite','=',parse('focus = A01_island_delegation')))
fs['A01_royal_dictatorship'].append(('prerequisite','=',parse('focus = A01_royal_naval_advisors')))
# Plain ideas carry effects; do not overwrite the unrelated government-course variables.
for fid in positions:
 reward=value(fs[fid],'completion_reward')
 reward[:]=[t for t in reward if t[0] not in ('set_variable','force_update_dynamic_modifier','custom_effect_tooltip')]
 if fid=='A01_royal_guard_corps':reward.append(('set_country_flag','=','A01_royal_guard_established'))
 if fid=='A01_royal_dictatorship':reward.extend(parse('remove_ideas = A01_royal_arbitration remove_ideas = A01_constitutional_crown remove_dynamic_modifier = A01_admirals_council set_country_flag = A01_admirals_council_abolished'))
 if fid=='A01_crown_commonwealth':reward.extend(parse('set_country_flag = A01_equal_citizenship_established set_country_flag = A01_crown_commonwealth_established'))
save(p,dump(tree)+'\n')
ideas={
'A01_royal_guard_loyalty':('Королевская гвардия','Royal Guard','army_org_factor = 0.05'),
'A01_royal_naval_loyalty':('Флот на службе короны','Navy in Crown Service','navy_org_factor = 0.05'),
'A01_royal_absolutism':('Королевский абсолютизм','Royal Absolutism','stability_factor = -0.05 war_support_factor = 0.15 mobilization_speed = 0.10'),
'A01_direct_royal_rule':('Прямое правление короны','Direct Crown Rule','political_power_gain = 0.10'),
'A01_crown_secret_police':('Тайная полиция короны','Crown Secret Police','resistance_growth_on_our_occupied_states = -0.15 stability_factor = -0.03'),
'A01_royal_militarism':('Военная монархия','Military Monarchy','production_speed_dockyard_factor = 0.20 mobilization_speed = 0.05 consumer_goods_expected_value = 0.05'),
'A01_crown_parliament_idea':('Парламент при короне','Crown Parliament','political_power_gain = 0.05 stability_factor = 0.03'),
'A01_crown_commonwealth_idea':('Королевское содружество','Royal Commonwealth','recruitable_population_factor = 0.05 stability_factor = 0.03')}
save('common/ideas/A01_monarchy.txt','ideas = { country = {\n'+''.join(f'{k} = {{ picture = story_ludolf allowed = {{ original_tag = A01 }} removal_cost = -1 modifier = {{ {v[2]} }} }}\n' for k,v in ideas.items())+'} }\n')
# An additional diary opportunity belongs to the still-unresolved postwar contest.
save('common/decisions/categories/A01_monarchy.txt','A01_monarchy_category = { icon = generic_political_actions allowed = { original_tag = A01 } visible = { has_completed_focus = A01_pacific_settlement NOT = { has_country_flag = A01_ludolf_crisis_resolved } date > 1894.12.31 } }\n')
save('common/decisions/A01_monarchy.txt','''A01_monarchy_category = {
 A01_wilhelminas_diary = {
 icon = generic_political_discourse cost = 0 fire_only_once = yes
 visible = { NOT = { has_country_flag = A01_ludolf_crisis_resolved } date > 1894.12.31 }
 available = { has_completed_focus = A01_pacific_settlement has_stability > 0.40 NOT = { has_country_flag = A01_ludolf_crisis_resolved } }
 complete_effect = { country_event = { id = A01_monarchy.0 days = 1 } }
 ai_will_do = { factor = 0 }
 }
}''')
# Event definitions and complete RU/EN localisation.
loc={}
def label(k,ru,en):loc[k]=(ru,en)
def event(num,title,desc,options,trigger='has_country_flag = A01_royal_path_revealed'):
 eid=f'A01_monarchy.{num}';label(eid+'.t',*title);label(eid+'.d',*desc)
 s=f'country_event = {{ id = {eid} title = {eid}.t desc = {eid}.d picture = GFX_1896_event_council is_triggered_only = yes trigger = {{ tag = A01 {trigger} }}\n'
 for i,(ru,en,effect) in enumerate(options):
  key=eid+'.'+chr(97+i);label(key,ru,en);s+=f'option = {{ name = {key} {effect} }}\n'
 return s+'}\n'
ev='add_namespace = A01_monarchy\n'
ev+=event(0,('Дневник Вильгельмины',"Wilhelmina's Diary"),('В дневнике юная Вильгельмина пишет, что не хочет быть декорацией. Она видит, как Совет и адмиралы разоряют страну, и хочет взять ответственность за её будущее. Поддержим ли мы корону в послевоенном споре?','Young Wilhelmina writes that she refuses to be an ornament. She sees the Council and admirals ruin the country and wants responsibility for its future. Will we support the Crown in the postwar contest?'),[('Она ещё ребёнок.','She is still a child.',''),('Она — наша надежда.','She is our hope.','A01_establish_regency_effect = yes')],'has_completed_focus = A01_pacific_settlement NOT = { has_country_flag = A01_ludolf_crisis_resolved }')
ev+=event(1,('Разговор с матерью','A Conversation with Mother'),('Эмма Вальдек-Пирмонтская вызывает дочь в кабинет. Мать говорит о долге, осторожности и стране, не готовой к правлению ребёнка. Дочь отвечает, что страна гибнет, пока решения откладывают. Разговор длится всю ночь. К утру обе выходят с красными глазами.','Emma of Waldeck and Pyrmont calls her daughter to her study. The mother speaks of duty, caution and a country unprepared for a child ruler. The daughter argues that delay is ruining the country. Their conversation lasts all night.'),[('Уступить матери.','Yield to Mother.','add_stability = 0.10 add_timed_idea = { idea = A01_emmas_caution days = 180 }'),('Настоять на своём.','Insist on taking the throne.','add_stability = -0.10 add_timed_idea = { idea = A01_young_queens_resolve days = 180 } set_country_flag = A01_early_royal_accession')],'has_country_flag = A01_emma_regency NOT = { has_country_flag = A01_wilhelmina_reigns }')
ev+=event(3,('Парламент при короне','Parliament under the Crown'),('Вильгельмина открывает первое заседание парламента Нидерландов и Индонезии. Голландские купцы, яванские регенты, суматранские султаны и амбонские капитаны не доверяют друг другу. Но теперь они сидят в одном зале. Корона сохраняет власть, а представители островов получают право голоса.','Wilhelmina opens the first parliament of the Netherlands and Indonesia. Dutch merchants, Javanese regents, Sumatran sultans and Ambonese captains distrust one another, but now sit in the same chamber. The Crown retains power while island representatives gain a voice.'),[('Пусть говорят.','Let them speak.','add_stability = 0.05 add_timed_idea = { idea = A01_crown_dialogue days = 180 }'),('Корона слушает, но решает.','The Crown listens, but decides.','add_stability = -0.05 add_timed_idea = { idea = A01_crown_resolve days = 180 }')])
ev+=event(4,('Содружество двух берегов','A Commonwealth of Two Shores'),('Хартия содружества признаёт равные права жителей Нидерландов и Индонезии. Султанаты сохраняют местные законы и представительство; общие дела решаются парламентом при короне. Это союз под одной короной, основанный на договоре.','The Commonwealth Charter recognises equal rights for the people of the Netherlands and Indonesia. Sultanates retain local laws and representation; shared affairs go before the Crown Parliament. One crown unites a partnership founded on agreement.'),[('Одна корона, много народов.','One crown, many peoples.','')])
ev+=event(5,('Королевская диктатура','Royal Dictatorship'),('Вильгельмина распускает Совет директоров. Адмиралы присягают лично ей, а парламент откладывается «до лучших времён». Нидерланды и Индонезия будут управляться королевскими указами. На площадях одни радуются, другие молчат.','Wilhelmina dissolves the governing Council. The admirals swear personal loyalty to her, and parliament is postponed until better times. Royal decrees will govern the Netherlands and Indonesia. In the squares, some cheer while others remain silent.'),[('Так надо.','It must be done.','add_stability = 0.10 add_timed_idea = { idea = A01_crown_dialogue days = 180 }'),('Мы ещё вернёмся к парламенту.','We will return to parliament someday.','add_stability = -0.05 every_other_country = { limit = { has_government = democratic } add_opinion_modifier = { target = ROOT modifier = A01_royal_reassurances } }')])
ev+=event(6,('Власть королевского указа','Rule by Royal Decree'),('Совет адмиралов утрачивает право вмешиваться в гражданские дела. Министры отвечают перед королевой, а армия остаётся на службе государства. Ответственность за каждое решение теперь лежит на короне.','The Admiralty Council loses its right to interfere in civilian affairs. Ministers answer to the Queen while the armed forces remain in state service. The Crown now bears responsibility for every decision.'),[('Корона принимает ответственность.','The Crown accepts responsibility.','')])
ev+=event(7,('Корона и меч','Crown and Sword'),('Верфи и мобилизационные управления переходят на военные приоритеты. Королевский флот становится опорой власти на островах. За это придётся платить: гражданское снабжение уступает место вооружению.','Shipyards and mobilisation offices adopt military priorities. The Royal Navy becomes the foundation of power across the islands. Civilian supply must give way to armaments.'),[('Служить короне.','Serve the Crown.','')])
save('events/A01_monarchy.txt',ev)
extra={'A01_emmas_caution':('Осторожность регентши',"The Regent's Caution",'political_power_factor = -0.10'),'A01_young_queens_resolve':('Решимость юной королевы',"The Young Queen's Resolve",'political_power_factor = 0.15'),'A01_crown_dialogue':('Корона ведёт диалог','Crown Dialogue','political_power_factor = 0.05'),'A01_crown_resolve':('Решающее слово короны','The Crown Has the Final Word','political_power_factor = 0.10')}
ideas.update(extra)
text=(R/'common/ideas/A01_monarchy.txt').read_text();text=text.rsplit('} }',1)[0]+''.join(f'{k} = {{ picture = story_ludolf allowed = {{ original_tag = A01 }} removal_cost = -1 modifier = {{ {v[2]} }} }}\n' for k,v in extra.items())+'} }\n';save('common/ideas/A01_monarchy.txt',text)
save('common/opinion_modifiers/A01_monarchy.txt','opinion_modifiers = { A01_royal_reassurances = { value = 5 } }\n')
focusnames={
'A01_emma_and_daughter':('Эмма и её дочь','Emma and Her Daughter','Решить спор о сроках передачи власти от регентши к королеве.','Resolve the dispute over the transfer of power from the Regent to the Queen.'),
'A01_royal_guard_corps':('Корпус королевской гвардии','Royal Guard Corps','Создать верную короне военную опору, ограничив влияние адмиралов.','Build a military foundation loyal to the Crown and reduce Admiralty influence.'),
'A01_royal_naval_advisors':('Морские советники короны','Royal Naval Advisers','Офицеры флота присягают короне и готовят единые правила морской службы.','Naval officers pledge loyalty to the Crown and develop common service standards.'),
'A01_island_delegation':('Делегация островов','Island Delegation','Представители островов получают постоянное место в обсуждении государственных дел.','Island representatives gain a permanent voice in affairs of state.'),
'A01_royal_dictatorship':('Королевская диктатура','Royal Dictatorship','Опираясь на гвардию и флот, королева отказывается от конституционного ограничения власти.','Backed by the Guard and Navy, the Queen rejects constitutional limits on her power.'),
'A01_crown_parliament':('Парламент при короне','Crown Parliament','Собрать голландских и индонезийских представителей под властью конституционной короны.','Bring Dutch and Indonesian representatives together under a constitutional Crown.'),
'A01_crown_commonwealth':('Королевское содружество','Royal Commonwealth','Закрепить равноправие народов и договорное устройство содружества с Индонезией.','Establish equal rights and a charter-based commonwealth with Indonesia.'),
'A01_crown_absolute_rule':('Абсолютная власть короны','Absolute Crown Rule','Упразднить политическую власть Совета адмиралов и подчинить министров королеве.','End the Admiralty Council\'s political power and make ministers accountable to the Queen.'),
'A01_crown_militarism':('Военная монархия','Military Monarchy','Направить средства на верфи и мобилизацию ценой гражданского снабжения.','Prioritise dockyards and mobilisation at the expense of civilian supply.'),
'A01_royal_secret_police':('Тайная полиция короны','Crown Secret Police','Создать службу надзора. Подавление сопротивления усилится, но общество заплатит за это доверием.','Establish a surveillance service. Resistance will be suppressed at the cost of public trust.')}
for k,(ru,en,rd,ed) in focusnames.items():label(k,ru,en);label(k+'_desc',rd,ed)
for k,(ru,en,mods) in ideas.items():label(k,ru,en);label(k+'_desc',ru+'.',en+'.')
label('A01_monarchy_category','Будущее короны','Future of the Crown');label('A01_wilhelminas_diary','Дневник Вильгельмины',"Wilhelmina's Diary");label('A01_wilhelminas_diary_desc','Прочитать дневник принцессы и решить, поддержать ли корону в споре о послевоенной власти. Доступно с 1895 года, пока политический путь не выбран.','Read the princess\'s diary and decide whether to support the Crown in the unresolved postwar political contest. Available from 1895.');label('A01_royal_reassurances','Обещание вернуться к парламенту','Promise of Parliamentary Government')
for tag,ru,en in [('A01_COMMONWEALTH','Королевское содружество Нидерландов и Индонезии','Royal Commonwealth of the Netherlands and Indonesia'),('A01_ROYAL_EMPIRE','Королевская империя Нидерландов','Royal Empire of the Netherlands')]:
 for ideology in ('neutrality','democratic','fascism','communism'):
  label(tag+'_'+ideology,ru,en);label(tag+'_'+ideology+'_DEF',ru,en);label(tag+'_'+ideology+'_ADJ','Нидерландск.','Dutch')
for lang,col in [('russian',0),('english',1)]:save(f'localisation/{lang}/zzzzzzz_monarchy_l_{lang}.yml','l_'+lang+':\n'+''.join(f' {k}:0 "{v[col].replace(chr(34),chr(39))}"\n' for k,v in loc.items()))
# Cosmetic colours are separate from the republic's base colour.
p='common/countries/cosmetic.txt';text=(R/p).read_text(encoding='utf-8-sig')
for tag in ('A01_CROWN','A01_COMMONWEALTH','A01_ROYAL_EMPIRE'):text+=f'\n{tag} = {{ color = rgb {{ 235 135 45 }} color_ui = rgb {{ 235 135 45 }} }}\n'
save(p,text)
for folder in ('gfx/flags','gfx/flags/medium','gfx/flags/small'):
 for f in (R/folder).glob('A01_CROWN*.tga'):
  for tag in ('A01_COMMONWEALTH','A01_ROYAL_EMPIRE'):shutil.copy2(f,f.with_name(f.name.replace('A01_CROWN',tag)))
print('Added',len(new),'focuses and 7 events; royal cosmetic flags and orange colours ready.')

