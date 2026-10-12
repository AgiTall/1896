"""Apply the revised cabinet fork, event-only petition, militia and KNIL copy."""
from pathlib import Path
import re, shutil
R=Path(__file__).resolve().parents[1]
B=R/'tools/backups/cabinet_fork_before'
def read(p):return (R/p).read_text(encoding='utf-8-sig')
def write(p,s):
 path=R/p;backup=B/p
 if path.exists() and not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,backup)
 path.write_text(s,encoding='utf-8-sig' if p.startswith('localisation/') else 'utf-8')
def bounds(s,key,fid):
 for m in re.finditer(r'(?m)^\s*'+key+r'\s*=\s*\{',s):
  i=m.end();depth=1
  while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
  if re.search(r'\bid\s*=\s*'+re.escape(fid)+r'\b',s[m.end():i]):return m.start(),i
 raise ValueError(fid)
def change(s,key,fid,fn):
 a,b=bounds(s,key,fid);return s[:a]+fn(s[a:b])+s[b:]
def node(fid,icon,x,y,reward,available,exclusive='',hidden=False):
 return f'''
 focus = {{
  id = {fid}
  icon = {icon}
  x = {x}
  y = {y}
  cost = 3
  prerequisite = {{ focus = A01_pacific_settlement }}
  {('mutually_exclusive = { focus = '+exclusive+' }') if exclusive else ''}
  {('allow_branch = { has_country_flag = A01_royal_path_revealed }') if hidden else ''}
  available = {{ {available} }}
  cancel_if_invalid = yes
  ai_will_do = {{ factor = 1 }}
  search_filters = {{ FOCUS_FILTER_POLITICAL }}
  completion_reward = {{ {reward} }}
 }}
'''
p='common/national_focus/a01_focus.txt';s=read(p)
if 'id = A01_future_of_netherlands' not in s:raise SystemExit('Correction already applied.')
for fid in ['A01_future_of_netherlands','A01_federal_defence_compact']:
 s=change(s,'focus',fid,lambda b:'\n')
s=change(s,'focus','A01_pacific_settlement',lambda b:b.replace('A01_begin_dismissal_debate_effect = yes','A01_begin_dismissal_debate_effect = yes\n   set_country_flag = A01_future_debate_open\n   country_event = { id = A01_future.4 days = 7 }'))
s=change(s,'focus','A01_ludolf_survives',lambda b:node('A01_ludolf_survives','GFX_goal_unique_A01_ludolf_survives',12,14,
 'set_country_flag = A01_political_path_chosen set_country_flag = A01_ludolf_reform_path country_event = { id = A01_future.17 days = 1 }',
 'OR = { NOT = { has_country_flag = A01_political_path_chosen } has_country_flag = A01_ludolf_reform_path } NOT = { has_country_flag = A01_admirals_seized_power }',exclusive='A01_negotiated_resignation'))
s=change(s,'focus','A01_negotiated_resignation',lambda b:node('A01_negotiated_resignation','GFX_goal_unique_A01_negotiated_resignation',18,14,
 'A01_establish_military_rule_effect = yes',
 'OR = { NOT = { has_country_flag = A01_political_path_chosen } has_country_flag = A01_admirals_seized_power }',exclusive='A01_ludolf_survives'))
s=change(s,'focus','A01_crown_above_factions',lambda b:node('A01_crown_above_factions','GFX_goal_generic_neutrality_focus',24,14,
 'A01_establish_regency_effect = yes add_political_power = 75 add_stability = 0.05',
 'has_country_flag = A01_royal_path_revealed NOT = { has_country_flag = A01_political_path_chosen } NOT = { power_balance_value = { id = A01_ludolf_admirals_balance value < -0.1 } } NOT = { power_balance_value = { id = A01_ludolf_admirals_balance value > 0.1 } }',hidden=True))
updates={
 'A01_reconstruction_commission':('A01_ludolf_survives',15),
 'A01_autonomous_sultanates':('A01_reconstruction_commission',16),
 'A01_equal_citizenship':('A01_autonomous_sultanates',17),
 'A01_elected_civil_service':('A01_equal_citizenship',18),
 'A01_democratic_federation':('A01_elected_civil_service',19),
 'A01_purge_civil_service':('A01_negotiated_resignation',15),
 'A01_purge_officer_corps':('A01_purge_civil_service',16),
 'A01_military_state':('A01_purge_officer_corps',17),
 'A01_northern_memory':('A01_negotiated_resignation',18),
 'A01_fleet_of_recovery':('A01_northern_memory',19),
 'A01_royal_island_charter':('A01_crown_above_factions',15),
 'A01_wilhelmina_comes_of_age':('A01_royal_island_charter',16),
 'A01_royal_constitution':('A01_wilhelmina_comes_of_age',17),
}
for fid,(parent,y) in updates.items():
 def transform(b,parent=parent,y=y):
  b=re.sub(r'prerequisite = \{[^}]+\}',f'prerequisite = {{ focus = {parent} }}',b,count=1)
  return re.sub(r'\by = \d+',f'y = {y}',b,count=1)
 s=change(s,'focus',fid,transform)
s=change(s,'focus','A01_review_borneo_convention',lambda b:re.sub(r'prerequisite = \{[^}]+\}','prerequisite = { focus = A01_democratic_federation focus = A01_fleet_of_recovery }',b,count=1).replace('y = 23','y = 20'))
write(p,s)
p='common/ai_strategy_plans/A01_canonical.txt';s=read(p)
s=s.replace('A01_future_of_netherlands ','').replace('A01_federal_defence_compact ','')
s=s.replace('A01_reconstruction_commission A01_autonomous_sultanates','A01_ludolf_survives A01_reconstruction_commission A01_autonomous_sultanates')
s=s.replace('A01_northern_memory A01_fleet_of_recovery\n  A01_ludolf_survives ','')
write(p,s)
# Petition resolves the remaining dismissal question as an event, not a focus.
p='events/A01_ludolf_story.txt';s=read(p)
s=change(s,'country_event','ludolf.31',lambda b:b.replace('option = { name = ludolf.31.a }','option = { name = ludolf.31.a A01_establish_federal_mandate_effect = yes add_ideas = A01_sultanate_federation }'))
write(p,s)
p='common/scripted_effects/A01_future_effects.txt';s=read(p)
s=s.replace('A01_end_dismissal_debate_effect = {','A01_end_dismissal_debate_effect = {\n set_country_flag = A01_political_path_chosen')
s=s.replace('set_country_flag = A01_federal_mandate','set_country_flag = A01_federal_mandate\n  set_country_flag = A01_ludolf_reform_path')
write(p,s)
p='common/on_actions/A01_future_on_actions.txt';s=read(p)
s=s.replace('   has_completed_focus = A01_autonomous_sultanates\n','   NOT = { has_country_flag = A01_political_path_chosen }\n')
s=s.replace('power_balance_value = { id = A01_ludolf_admirals_balance value > -0.1 }','NOT = { power_balance_value = { id = A01_ludolf_admirals_balance value < -0.1 } }')
s=s.replace('power_balance_value = { id = A01_ludolf_admirals_balance value < 0.1 }','NOT = { power_balance_value = { id = A01_ludolf_admirals_balance value > 0.1 } }')
write(p,s)
p='events/A01_future_events.txt';s=read(p)
s=change(s,'country_event','A01_future.16',lambda b:b.replace('power_balance_value = { id = A01_ludolf_admirals_balance value > -0.1 }','NOT = { power_balance_value = { id = A01_ludolf_admirals_balance value < -0.1 } }').replace('power_balance_value = { id = A01_ludolf_admirals_balance value < 0.1 }','NOT = { power_balance_value = { id = A01_ludolf_admirals_balance value > 0.1 } }').replace('trigger = { tag = A01','trigger = { tag = A01 NOT = { has_country_flag = A01_political_path_chosen }').replace('A01_establish_regency_effect = yes','set_country_flag = A01_royal_path_revealed mark_focus_tree_layout_dirty = yes'))
s+='''
country_event = {
 id = A01_future.17
 title = A01_future.17.t
 desc = A01_future.17.d
 picture = GFX_1896_event_council
 is_triggered_only = yes
 trigger = { tag = A01 has_country_flag = A01_ludolf_reform_path NOT = { has_country_flag = A01_ludolf_crisis_resolved } }
 option = { name = A01_future.17.a }
}
'''
write(p,s)

# Vanilla militia battalions, enabled before loading the existing twelve units.
p='history/units/A01_indonesian_militia.txt';s=read(p).replace('regiments = { infantry =','regiments = { militia =').replace(' } infantry =',' } militia =');write(p,s)
p='events/A01_admiral_speeches.txt';s=read(p)
s=s.replace('load_oob = "A01_indonesian_militia"','set_technology = { militia_tech = 1 } load_oob = "A01_indonesian_militia"')
s=s.replace('name = A01_japan.32.a remove_ideas','name = A01_japan.32.a custom_effect_tooltip = A01_real_militia_tt remove_ideas')
write(p,s)

# Update keys in place; never rely on duplicate localisation priority.
updates_ru={
'A01_pacific_settlement_desc':'Поражение ставит вопрос о том, кому принадлежит власть. Этот фокус открывает главную послевоенную развилку: сохранить гражданский кабинет Людольфа и начать реформы или передать государство Совету адмиралов. Начинаются слушания о смещении губернатора; выбор ветви определит дальнейшие преобразования.',
'A01_ludolf_survives':'Курс Людольфа',
'A01_ludolf_survives_desc':'Сохранить Людольфа во главе гражданского кабинета и дать ему время ответить на требования свободы. Открытая комиссия и автономия султанатов должны стать началом демократической федерации. Поддержка новых автономий будет выражена отдельным обращением к Совету.',
'A01_negotiated_resignation':'Приход Совета адмиралов',
'A01_negotiated_resignation_desc':'Передать власть Совету сразу после формирования послевоенного кабинета. Адмиралы сместят и арестуют Людольфа за поражение, начнут чистки и подчинят государственные учреждения военной элите.',
'A01_motion_to_dismiss_ludolf_desc':'Совет рассматривает ответственность Людольфа за поражение. «Кабинет после поражения» открывает выбор политического курса. На пути Людольфа автономия султанатов приведёт к событию с просьбой дать ему ещё один шанс. Если слушания затянутся на 240 дней, состоится решающее заседание.',
'A01_crown_above_factions_desc':'Предложение королевы-матери открывает третий выход из послевоенного кризиса. При равновесии гражданского кабинета и адмиралов Эмма примет регентство. Завершение этого фокуса передаст ей власть.',
'A01_future.16.a':'Рассмотреть монархический выход из кризиса.',
'A01_knil_reform':'Реформа КНИЛ — колониальной армии',
'A01_knil_reform_desc':'КНИЛ (KNIL, Koninklijk Nederlands-Indisch Leger) — Королевская нидерландская ост-индская армия, сухопутные войска Нидерландов в Индонезии. В моде это регулярные гарнизоны и полевые части архипелага под управлением Батавии.\n\nРеформа вводит общую подготовку и создаёт национальный дух КНИЛ. Последующие армейские фокусы улучшают его организацию, оборону, обучение и снабжение. Добровольческое индонезийское ополчение — отдельные временные части для войны с Японией.',
'A01_knil_training':'Подготовка колониальной армии (КНИЛ)',
'A01_knil_training_desc':'КНИЛ — Королевская нидерландская ост-индская армия (KNIL), регулярные сухопутные войска архипелага. Общие программы подготовки делают гарнизоны и полевые части более организованными. Это кадровая армия; временное добровольческое ополчение формируется отдельно.',
'A01_knil_field_training':'КНИЛ: островные гарнизоны',
'A01_knil_field_training_desc':'КНИЛ — Королевская нидерландская ост-индская армия, регулярные сухопутные войска колонии. Общая подготовка и гарнизонная служба повышают организацию и оборону этих частей.',
'A01_knil_reformed':'КНИЛ: полевые реформы',
'A01_knil_reformed_desc':'Полевые наставления и единое снабжение регулярной колониальной армии повышают организацию, ускоряют подготовку и снижают расход припасов.',
'A01_knil_professional':'КНИЛ: подготовленный командный состав',
'A01_knil_professional_desc':'КНИЛ — регулярная ост-индская армия. Местные сержанты обеспечивают связь между командирами и солдатами и закрепляют результаты реформ.',
'A01_local_nco_schools_desc':'Подготовить местных сержантов для КНИЛ — Королевской нидерландской ост-индской армии. Это регулярные сухопутные части архипелага. Армейский дух будет улучшен, а инспекция колониальной армии станет доступна в качестве начальника армии.',
'A01_knil_inspectorate_name':'Инспекция колониальной армии (КНИЛ)',
'A01_knil_inspectorate':'Инспекция колониальной армии (КНИЛ)',
'A01_army_advisor_unlocked_tt':'Станет доступен начальник армии §YИнспекция колониальной армии (КНИЛ)§! с бонусом к обороне. КНИЛ — регулярные сухопутные войска Нидерландов в Индонезии. Назначение стоит 100 политической власти.',
'A01_island_garrisons_desc':'Введём единый порядок подготовки островных гарнизонов КНИЛ — регулярной колониальной армии. Её национальный дух получит дополнительный бонус к обороне.',
'A01_jungle_supply_desc':'Полевые инструкции и общее снабжение улучшат дух КНИЛ — регулярной ост-индской армии: организация возрастёт, подготовка ускорится, расход припасов снизится.',
}
updates_en={
'A01_pacific_settlement_desc':'The key postwar fork: preserve Ludolfs civilian government and pursue reform, or bring the Admirals Council to power. Dismissal hearings begin, but there is no automatic removal.',
'A01_ludolf_survives':'Ludolfs Course','A01_ludolf_survives_desc':'Keep Ludolf in office and pursue civilian reform. Reconstruction and autonomous sultanates lead towards federation. The sultans request for another chance is delivered through an event.',
'A01_negotiated_resignation':'The Admirals Council Takes Power','A01_negotiated_resignation_desc':'Transfer power to the council directly from the postwar cabinet. Ludolf is dismissed and imprisoned; purges and military control follow.',
'A01_motion_to_dismiss_ludolf_desc':'The postwar cabinet opens the political fork. On Ludolfs route the autonomous sultanates petition the council through an event. Hearings expire after 240 days.',
'A01_crown_above_factions_desc':'Complete this focus to bring Emma to power while the balance lies between -10% and +10%. The private royal proposal reveals this otherwise hidden branch.',
'A01_future.16.a':'Consider a monarchical settlement.',
'A01_knil_reform':'Reform the KNIL — Colonial Army',
'A01_knil_reform_desc':'KNIL stands for Koninklijk Nederlands-Indisch Leger, the Royal Netherlands East Indies Army. In the mod it is the regular land army of the archipelago, governed from Batavia.\n\nArmy focuses improve its national spirit: organisation, defence, training and supply. Indonesian volunteer militia are separate temporary formations for the war with Japan.',
'A01_knil_training_desc':'The KNIL is the Royal Netherlands East Indies Army: the regular land forces of the archipelago. It is distinct from the temporary Indonesian volunteer militia.',
'A01_knil_field_training_desc':'The KNIL is the regular Royal Netherlands East Indies Army. Common training strengthens the organisation and defence of its island garrisons.',
'A01_knil_professional_desc':'Local NCOs improve the command structure of the KNIL, the regular colonial land army.',
'A01_local_nco_schools_desc':'Train local NCOs for the KNIL, the Royal Netherlands East Indies Army. The army spirit improves and the colonial army inspectorate becomes available as an army chief.',
'A01_knil_inspectorate_name':'Colonial Army Inspectorate (KNIL)','A01_knil_inspectorate':'Colonial Army Inspectorate (KNIL)',
}
for lang,changes in [('russian',updates_ru),('english',updates_en)]:
 for key,val in changes.items():
  found=0
  for p in (R/'localisation'/lang).glob('*.yml'):
   s=p.read_text(encoding='utf-8-sig');s,n=re.subn(r'^ '+re.escape(key)+r':(?:\d+)? .*$',lambda m:f' {key}:0 "{val.replace(chr(10),r"\n")}"',s,flags=re.M)
   if n:write(str(p.relative_to(R)).replace('\\','/'),s);found+=n
  assert found,key
 new={
 'A01_real_militia_tt':('Будут сформированы §Y12 дивизий индонезийского ополчения§!, каждая из §Y3 батальонов ополчения§! ванильного типа. Это временные части: после окончания кризиса с Японией они будут распущены.' if lang=='russian' else 'Raise 12 Indonesian militia divisions, each with 3 vanilla militia battalions. These temporary units disband after the Japanese crisis.'),
 'A01_future.17.t':('Людольф получает время на реформы' if lang=='russian' else 'Ludolf Receives Time for Reform'),
 'A01_future.17.d':('Послевоенный кабинет сохраняет гражданский курс. Людольф остаётся на посту, но не получает прощения за поражение. Совет требует результатов, а делегаты островов — ответа на требования свободы.\n\nФабиус предлагает начать с открытой комиссии. Вирата настаивает, что жители должны увидеть перемены за пределами Батавии. Людольф поручает готовить автономные хартии. Когда султанаты появятся, именно их представители смогут обратиться к Совету с просьбой дать губернатору второй шанс.' if lang=='russian' else 'The cabinet preserves civilian rule, but Ludolf has not been absolved. Open reconstruction and autonomous charters must answer the demands for freedom. Once the sultanates exist, their delegates can petition the council to give him another chance.'),
 'A01_future.17.a':('Приступить к гражданским реформам.' if lang=='russian' else 'Begin civilian reforms.'),
 }
 p=f'localisation/{lang}/zzzz_postwar_future_l_{lang}.yml';s=read(p)
 for key,val in new.items():s+=f' {key}:0 "{val.replace(chr(10),r"\n")}"\n'
 write(p,s)
print('Cabinet now branches directly; petition is event-only; twelve divisions use vanilla militia; KNIL explained.')
