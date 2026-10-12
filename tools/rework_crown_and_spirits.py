"""Rework the secret crown route and group related national spirits."""
from pathlib import Path
import json
import re
from add_canon_countries import parse, value, dump

R = Path(__file__).resolve().parents[1]
def read(p): return (R/p).read_text(encoding='utf-8-sig')
if 'id = A01_settle_crown_crisis' in read('common/national_focus/a01_focus.txt'):
 raise SystemExit('Crown/category rework is already applied; use validation scripts to check it.')
def save(p, text):
 path=R/p; path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(text, encoding='utf-8-sig' if path.suffix=='.yml' else 'utf-8')
def setv(n,k,v): n[:]=[t for t in n if t[0]!=k]+[(k,'=',v)]
def append(n,s): n.extend(parse(s))
loc={}
def label(k,ru,en): loc[k]=(ru,en)

# Substantial upgrades are later folded into one evolving Crown spirit.
buffs={
 'A01_royal_guard_loyalty':'army_org_factor = 0.10 army_defence_factor = 0.05 training_time_army_factor = -0.10',
 'A01_royal_naval_loyalty':'navy_org_factor = 0.10 production_speed_dockyard_factor = 0.15',
 'A01_royal_absolutism':'political_power_gain = 0.25 war_support_factor = 0.15 mobilization_speed = 0.20 stability_factor = -0.05',
 'A01_direct_royal_rule':'production_speed_buildings_factor = 0.15 industrial_capacity_factory = 0.10',
 'A01_crown_secret_police':'resistance_target = -0.15 resistance_growth_on_our_occupied_states = -0.20 stability_factor = 0.05',
 'A01_royal_militarism':'army_attack_factor = 0.10 production_speed_dockyard_factor = 0.15 industrial_capacity_factory = 0.10 consumer_goods_expected_value = 0.05',
 'A01_crown_parliament_idea':'political_power_gain = 0.20 research_speed_factor = 0.10 stability_factor = 0.05',
 'A01_crown_commonwealth_idea':'recruitable_population_factor = 0.15 production_factory_max_efficiency_factor = 0.15 consumer_goods_expected_value = -0.10',
}
manifest_path=R/'tools/spirit_categories_manifest.json'
prior=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
groups={
 'A01_defeat_legacy':['A01_borneo_humiliation','A01_revanchism_simmering','A01_revanchism_organised','A01_demands_for_freedom','A01_postwar_destruction','A01_unpaid_families','A01_postwar_budget_burden','A01_reconstruction_cabinet'],
 'A01_army_development':['A01_knil_training','A01_island_defence','A01_jungle_supply','A01_naval_staff','A01_army_transition','A01_joint_officer_corps','A01_federal_defence_command_idea','A01_restored_port_network'],
 'A01_civic_development':['A01_colonial_administration','A01_sultanate_federation','A01_civilian_naval_compact','A01_civilian_reform_mandate','A01_island_representation_idea','A01_federal_constitution_idea','A01_accountable_civil_service','A01_recovery_investment_idea'],
 'A01_crown_order':['A01_royal_arbitration','A01_constitutional_crown','A01_island_charter']+list(buffs)+['A01_emmas_caution','A01_young_queens_resolve','A01_crown_dialogue','A01_crown_resolve'],
}
all_ids={i for ids in groups.values() for i in ids}
data={}
for path in (R/'common/ideas').glob('*.txt'):
 text=path.read_text(encoding='utf-8-sig')
 if not any(re.search(r'\b'+re.escape(i)+r'\s*=',text) for i in all_ids): continue
 tree=parse(text); ideas=value(tree,'ideas')
 hidden=next((v for k,o,v in ideas if k=='hidden_ideas'),None)
 if hidden is None: hidden=[]; ideas.append(('hidden_ideas','=',hidden))
 for k,o,body in list(ideas):
  if k!='country': continue
  for ident,op,n in list(body):
   if ident not in all_ids: continue
   modifiers=value(n,'modifier')
   if ident in buffs: modifiers=parse(buffs[ident])
   data[ident]={m:float(v) for m,op,v in modifiers}
   setv(n,'modifier',[])
   body.remove((ident,op,n)); hidden.append((ident,op,n))
 for ident,op,n in hidden:
  if ident in all_ids and ident not in data:
   data[ident]={m:float(v) for m,op,v in parse(buffs[ident])} if ident in buffs else prior[ident]
 save(str(path.relative_to(R)),dump(tree)+'\n')
assert set(data)==all_ids, all_ids-set(data)
save('tools/spirit_categories_manifest.json',json.dumps(data,indent=2))
icons={'A01_defeat_legacy':'GFX_idea_story_defeat','A01_army_development':'GFX_idea_pacific_army','A01_civic_development':'GFX_idea_pacific_industry','A01_crown_order':'GFX_idea_A01_wilhelmina'}
dynamic=''; effects='A01_update_spirit_categories = {\n'
for group,ids in groups.items():
 mods=sorted({m for i in ids for m in data[i]})
 dynamic+=f'{group} = {{ enable = {{ always = yes }} icon = {icons[group]}\n'
 for m in mods:
  var=f'{group}_{m}'
  dynamic+=f' {m} = {var}\n';effects+=f' set_variable = {{ {var} = 0 }}\n'
 for i in ids:
  effects+=f' if = {{ limit = {{ has_idea = {i} }}\n'
  for m,v in data[i].items(): effects+=f' add_to_variable = {{ {group}_{m} = {v:g} }}\n'
  effects+=' }\n'
 effects+=' if = { limit = { OR = { '+' '.join(f'has_idea = {i}' for i in ids)+' } }\n'
 effects+=f'  if = {{ limit = {{ NOT = {{ has_dynamic_modifier = {group} }} }} add_dynamic_modifier = {{ modifier = {group} }} }}\n force_update_dynamic_modifier = yes\n }}\n'
 effects+=f' else = {{ remove_dynamic_modifier = {{ modifier = {group} }} }}\n'
 dynamic+='}\n'
effects+='}\n'
save('common/dynamic_modifiers/A01_spirit_categories.txt',dynamic)
save('common/scripted_effects/A01_spirit_categories.txt',effects)

tree=parse(read('common/national_focus/a01_focus.txt')); body=value(tree,'focus_tree')
fs={value(n,'id'):n for k,o,n in body if k=='focus'}
rewards={
 'A01_crown_above_factions':'add_political_power = 100 add_stability = 0.05',
 'A01_crown_island_council':'add_political_power = 75 add_stability = 0.05 add_power_balance_value = { id = A01_crown_council_balance value = -0.15 }',
 'A01_crown_legal_guarantees':'add_stability = 0.05 add_power_balance_value = { id = A01_crown_council_balance value = -0.10 } add_tech_bonus = { name = A01_crown_legal_guarantees bonus = 0.5 uses = 1 category = industry }',
}
for fid,s in rewards.items():setv(fs[fid],'completion_reward',parse(s))
append(value(fs['A01_royal_guard_corps'],'completion_reward'),'add_manpower = 10000 add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 3000 producer = A01 } add_power_balance_value = { id = A01_crown_council_balance value = 0.15 }')
append(value(fs['A01_royal_naval_advisors'],'completion_reward'),'add_power_balance_value = { id = A01_crown_council_balance value = 0.15 } add_tech_bonus = { name = A01_royal_naval_advisors bonus = 0.75 uses = 2 category = naval_equipment }')
append(value(fs['A01_wilhelmina_comes_of_age'],'completion_reward'),'A01_initialize_crown_struggle = yes')
for fid in ('A01_royal_constitution','A01_royal_dictatorship'):
 fs[fid].append(('prerequisite','=',parse('focus = A01_settle_crown_crisis')))
 avail=value(fs[fid],'available')
 append(avail,'has_country_flag = A01_crown_crisis_settled')
 if fid.endswith('constitution'):
  append(avail,'NOT = { power_balance_value = { id = A01_crown_council_balance value < -0.40 } } NOT = { power_balance_value = { id = A01_crown_council_balance value > 0.40 } }')
  append(value(fs[fid],'completion_reward'),'set_country_flag = A01_constitutional_monarchy_path add_political_power = 150')
 else:
  append(avail,'power_balance_value = { id = A01_crown_council_balance value > 0.59 }')
  append(value(fs[fid],'completion_reward'),'add_political_power = 150')
for fid,x,y in [('A01_royal_constitution',24,22),('A01_royal_dictatorship',28,22),('A01_crown_parliament',24,23),('A01_crown_absolute_rule',28,23),('A01_royal_secret_police',30,23),('A01_crown_commonwealth',24,24),('A01_crown_militarism',28,24)]:
 setv(fs[fid],'x',str(x));setv(fs[fid],'y',str(y))
append(value(fs['A01_crown_commonwealth'],'completion_reward'),'capital_scope = { add_extra_state_shared_building_slots = 2 add_building_construction = { type = industrial_complex level = 2 instant_build = yes } } add_research_slot = 1')
append(value(fs['A01_crown_militarism'],'completion_reward'),'capital_scope = { add_extra_state_shared_building_slots = 3 add_building_construction = { type = arms_factory level = 2 instant_build = yes } add_building_construction = { type = dockyard level = 1 instant_build = yes } } add_tech_bonus = { name = A01_crown_militarism bonus = 1 uses = 2 category = artillery }')
for fid,y,parent,reward in [
 ('A01_summon_grand_council',20,'A01_wilhelmina_comes_of_age','country_event = { id = A01_crown.1 days = 1 }'),
 ('A01_settle_crown_crisis',21,'A01_summon_grand_council','set_country_flag = A01_crown_crisis_settled add_stability = 0.10 add_political_power = 100')]:
 body.extend(parse(f'focus = {{ id = {fid} icon = GFX_goal_unique_A01_archipelago_command cost = 5 x = 26 y = {y} prerequisite = {{ focus = {parent} }} allow_branch = {{ has_country_flag = A01_royal_path_revealed }} available = {{ has_country_flag = A01_wilhelmina_reigns }} completion_reward = {{ {reward} }} ai_will_do = {{ factor = 1 }} }}'))
for k,o,n in body:
 if k=='focus': append(value(n,'completion_reward'),'hidden_effect = { A01_update_spirit_categories = yes }')
save('common/national_focus/a01_focus.txt',dump(tree)+'\n')
regency=parse(read('common/scripted_effects/A01_future_effects.txt'))
n=value(value(regency,'A01_establish_regency_effect'),'if')
append(n,'A01_initialize_crown_struggle = yes')
save('common/scripted_effects/A01_future_effects.txt',dump(regency)+'\n')

for key,ru,en in [
 ('A01_defeat_legacy','Наследие поражения','Legacy of Defeat'),
 ('A01_army_development','Военное строительство','Military Development'),
 ('A01_civic_development','Гражданское управление','Civil Administration'),
 ('A01_crown_order','Новый порядок Короны','The Crown’s New Order')]:
 label(key,ru,en)
 label(key+'_desc','Единый изменяемый национальный дух. Его суммарные эффекты обновляются при реформах, снятии последствий и завершении временных мер.','An evolving national spirit. Its combined effects update as reforms progress, consequences are resolved and temporary measures expire.')
label('A01_defeat_legacy_desc','Разрушения, невыплаченные компенсации, бюджетное бремя, унижение, реваншизм и послевоенный кабинет объединены здесь. Каждый восстановительный фокус снимает соответствующую часть последствий.','Destruction, unpaid compensation, budget strain, humiliation, revanchism and the reconstruction cabinet are combined here. Recovery focuses remove their respective effects.')
for key,ru,en in [
 ('A01_crown_council_balance','Королева и Большой совет','The Queen and the Grand Council'),
 ('A01_grand_council_side','Большой совет','Grand Council'),('A01_queen_side','Королева','The Queen'),
 ('A01_crown_equilibrium','Соглашение о полномочиях','Settlement of Powers'),
 ('A01_council_veto','Право вето Совета','Council Veto'),('A01_council_obstruction','Обструкция Совета','Council Obstruction'),
 ('A01_queen_influence','Двор укрепляет позиции','The Court Gains Ground'),('A01_queen_supremacy','Власть Королевы','The Queen’s Supremacy'),
 ('A01_crown_struggle','Борьба за новый порядок','Struggle for a New Order'),
 ('A01_crown_audiences','Открытые аудиенции Королевы','The Queen’s Public Audiences'),
 ('A01_council_concessions','Согласовать бюджет с Советом','Negotiate the Council Budget'),
 ('A01_guard_oaths','Присяга офицеров Королеве','Officers Swear to the Queen'),
 ('A01_crown_compromise','Созвать согласительную комиссию','Convene a Conciliation Commission'),
 ('A01_summon_grand_council','Последний ультиматум Большого совета','The Grand Council’s Last Ultimatum'),
 ('A01_settle_crown_crisis','Установить новый порядок','Establish the New Order'),
 ('A01_royal_dictatorship','Полная власть Королевы','Full Royal Authority')]:label(key,ru,en)
label('A01_summon_grand_council_desc','Совет требует права утверждать назначения и блокировать указы. Королева должна выбрать: уступить, договориться или опереться на гвардию.','The Council demands control of appointments and a veto over decrees. The Queen must concede, negotiate or rely on the Guard.')
label('A01_settle_crown_crisis_desc','Закрепить результат борьбы. Конституция требует баланса от −40% до +40%; полная власть — не менее 60% влияния Королевы. Управляйте влиянием через решения.','Consolidate the outcome. A constitution requires a balance between −40% and +40%; full authority requires at least 60% royal influence. Use decisions to manage influence.')
label('A01_royal_constitution_desc','Королева и Большой совет разделят власть. Парламент даст +10% скорости исследований, а Содружество — дополнительную ячейку исследований, промышленность и равное гражданство.','The Queen and Grand Council share power. Parliament grants +10% research speed; the Commonwealth adds a research slot, industry and equal citizenship.')
label('A01_royal_dictatorship_desc','При поддержке гвардии и флота Королева подчинит Совет. Прямое правление ускорит строительство и военное производство; военная монархия даст наступательные бонусы и новые заводы.','With Guard and fleet support, the Queen subordinates the Council. Direct rule boosts construction and military output; military monarchy adds offensive bonuses and new factories.')
for lang,index in [('russian',0),('english',1)]:
 save(f'localisation/{lang}/zzzzzzzz_crown_rework_l_{lang}.yml',f'l_{lang}:\n'+''.join(f' {k}:0 "{v[index]}"\n' for k,v in loc.items()))
print(f'Grouped {len(data)} national spirits into four evolving categories; upgraded crown branch with council crisis and substantial endings.')
