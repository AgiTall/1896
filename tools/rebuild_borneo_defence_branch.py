"""One-time rebuild of the Dutch defence procurement branch."""
from pathlib import Path
import copy, shutil
from add_canon_countries import parse,value,dump
R=Path(__file__).resolve().parents[1]
def save(p,t,bom=False):
 path=R/p
 if path.exists():
  b=R/'tools/backups/borneo_procurement'/p;b.parent.mkdir(parents=True,exist_ok=True)
  if not b.exists():shutil.copy2(path,b)
 path.write_text(t,encoding='utf-8-sig' if bom else 'utf-8')
def setv(n,k,v):n[:]=[e for e in n if e[0]!=k]+[(k,'=',v)]
def prereq(*ids):return [('focus','=',i) for i in ids]
if __name__=='__main__':
 p='common/national_focus/a01_focus.txt';t=parse((R/p).read_text(encoding='utf-8-sig'));body=value(t,'focus_tree')
 fs={value(n,'id'):n for k,o,n in body if k=='focus'}
 inspection=fs['A01_build_bornean_fortifications']
 setv(inspection,'completion_reward',parse('add_stability = 0.05'))
 setv(inspection,'x','15')
 oldlog=fs['A01_prepare_bornean_logistics']
 rail=copy.deepcopy(value(oldlog,'completion_reward'))
 rail=[e for e in rail if e[0]!='log']
 body[:]=[e for e in body if not(e[0]=='focus' and value(e[2],'id')=='A01_prepare_bornean_logistics')]
 def focus(fid,icon,x,y,cost,parents,reward):
  n=copy.deepcopy(inspection)
  for k,v in [('id',fid),('icon',icon),('x',str(x)),('y',str(y)),('cost',str(cost)),('completion_reward',parse(reward))]:setv(n,k,v)
  n[:]=[e for e in n if e[0] not in ['prerequisite','mutually_exclusive']]
  n.append(('prerequisite','=',prereq(*parents)))
  body.append(('focus','=',n));return n
 loan=focus('A01_state_loan','GFX_goal_unique_A01_wtc_oil_and_rubber_offer',13,7,5,['A01_build_bornean_fortifications'],'''add_to_variable = { A01_wtc_debt = 20 } add_ideas = A01_borneo_state_loan custom_effect_tooltip = A01_wtc_debt_20_tt''')
 request=focus('A01_request_fortification_project','GFX_goal_unique_A01_last_chance_to_negotiate',17,7,5,['A01_build_bornean_fortifications'],'country_event = { id = borneo_project.1 days = 1 }')
 loan.append(('mutually_exclusive','=',prereq('A01_request_fortification_project')))
 request.append(('mutually_exclusive','=',prereq('A01_state_loan')))
 own=focus('A01_own_fortifications','GFX_goal_unique_A01_build_bornean_fortifications',13,8,10,['A01_state_loan'],'''add_ideas = A01_borneo_self_build
 if = { limit = { country_exists = A02 } A02 = { add_opinion_modifier = { target = A01 modifier = A01_borneo_british_exclusion } } }
 custom_effect_tooltip = A01_own_fortifications_tt''')
 value(own,'completion_reward').extend(copy.deepcopy(rail))
 implementation=focus('A01_implement_fortification_project','GFX_goal_unique_A01_prepare_bornean_logistics',17,8,10,['A01_request_fortification_project'],'''if = { limit = { has_country_flag = A01_borneo_british_project } add_ideas = A01_borneo_british_defence }
 if = { limit = { has_country_flag = A01_borneo_australian_project } add_ideas = A01_borneo_australian_defence }
 if = { limit = { has_country_flag = A01_borneo_local_project } add_ideas = A01_borneo_local_defence }
 custom_effect_tooltip = A01_project_implementation_tt''')
 value(implementation,'available').append(('custom_trigger_tooltip','=',parse('tooltip = A01_project_selected_tt OR = { has_country_flag = A01_borneo_british_project has_country_flag = A01_borneo_australian_project has_country_flag = A01_borneo_local_project }')))
 value(implementation,'completion_reward').extend(copy.deepcopy(rail))
 belt=fs['A01_improve_bornean_fortifications']
 setv(belt,'prerequisite',prereq('A01_own_fortifications','A01_implement_fortification_project'))
 setv(belt,'y','9')
 for fid in ['A01_open_papuan_road','A01_fortify_australian_frontier','A01_wartime_industry']:
  n=fs[fid];setv(n,'y',str(int(value(n,'y'))+2))
 frontier=fs['A01_fortify_australian_frontier']
 value(frontier,'available').append(('custom_trigger_tooltip','=',parse('tooltip = A01_no_australian_guarantees_tt NOT = { has_country_flag = A01_new_guinea_guarantees }')))
 # Keep the postwar branch below the new defence rows.
 post={'A01_pacific_settlement'}
 while True:
  added={fid for fid,n in fs.items() if any(v in post for k,o,b in n if k=='prerequisite' for a,c,v in b if a=='focus')}
  if added<=post:break
  post|=added
 for fid in post:
  n=fs[fid];setv(n,'y',str(int(value(n,'y'))+2))
 save(p,dump(t)+'\n')
 save('common/ideas/A01_borneo_projects.txt','''ideas = { country = {
 A01_borneo_state_loan = { picture = pacific_industry allowed = { original_tag = A01 } removal_cost = -1 modifier = { political_power_factor = -0.10 } }
 A01_borneo_self_build = {
  picture = pacific_army allowed = { original_tag = A01 } removal_cost = -1
  modifier = { consumer_goods_expected_value = 0.05 political_power_gain = -0.10 }
  targeted_modifier = { tag = A03 defense_bonus_against = 0.20 }
 }
 A01_borneo_british_commitments = { picture = pacific_industry allowed = { original_tag = A01 } removal_cost = -1 modifier = { political_power_factor = -0.10 } }
 A01_borneo_british_defence = { picture = pacific_army allowed = { original_tag = A01 } removal_cost = -1 targeted_modifier = { tag = A03 defense_bonus_against = 0.15 } }
 A01_borneo_australian_commitments = { picture = pacific_industry allowed = { original_tag = A01 } removal_cost = -1 modifier = { } }
 A01_borneo_australian_defence = { picture = pacific_army allowed = { original_tag = A01 } removal_cost = -1 targeted_modifier = { tag = A03 defense_bonus_against = 0.10 } }
 A01_borneo_local_commitments = { picture = pacific_army allowed = { original_tag = A01 } removal_cost = -1 modifier = { recruitable_population_factor = 0.15 } }
 A01_borneo_local_defence = { picture = pacific_army allowed = { original_tag = A01 } removal_cost = -1 targeted_modifier = { tag = A03 defense_bonus_against = 0.05 } }
} }
''')
 save('common/opinion_modifiers/A01_borneo_projects.txt','''opinion_modifiers = {
 A01_borneo_british_exclusion = { value = -10 }
 A01_borneo_australian_cooperation = { value = 10 }
}
''')
 save('events/A01_borneo_projects.txt','''add_namespace = borneo_project
country_event = {
 id = borneo_project.1 title = borneo_project.1.t desc = borneo_project.1.d
 picture = GFX_A01_japanese_preparations is_triggered_only = yes
 trigger = { tag = A01 NOT = { has_country_flag = A01_borneo_project_selected } NOT = { has_country_flag = A01_borneo_treaty } }
 option = {
  name = borneo_project.1.a trigger = { country_exists = A02 } ai_chance = { factor = 50 }
  set_country_flag = A01_borneo_project_selected set_country_flag = A01_borneo_british_project
  add_to_variable = { A01_british_influence = 15 } add_to_variable = { A01_sovereignty_loss = 10 }
  add_ideas = A01_borneo_british_commitments
  custom_effect_tooltip = A01_british_project_tt
 }
 option = {
  name = borneo_project.1.b trigger = { country_exists = A07 } ai_chance = { factor = 25 }
  set_country_flag = A01_borneo_project_selected set_country_flag = A01_borneo_australian_project set_country_flag = A01_new_guinea_guarantees
  add_ideas = A01_borneo_australian_commitments
  A07 = { add_opinion_modifier = { target = A01 modifier = A01_borneo_australian_cooperation } }
  custom_effect_tooltip = A01_australian_project_tt
 }
 option = {
  name = borneo_project.1.c ai_chance = { factor = 25 }
  set_country_flag = A01_borneo_project_selected set_country_flag = A01_borneo_local_project
  add_ideas = A01_borneo_local_commitments
  add_to_variable = { A01_racial_stability = 0.10 }
  add_to_variable = { A01_admirals_respect = -5 }
  clamp_variable = { var = A01_admirals_respect min = 0 max = 100 }
  force_update_dynamic_modifier = yes
  custom_effect_tooltip = A01_local_project_tt
 }
}
''')
 # Defence bonuses cease after the Borneo campaign; financial commitments survive it.
 p='common/scripted_effects/expansion_effects.txt';t=parse((R/p).read_text(encoding='utf-8-sig'))
 cleanup=value(t,'A01_cleanup_expansion_effect')
 for idea in ['A01_borneo_self_build','A01_borneo_british_defence','A01_borneo_australian_defence','A01_borneo_local_defence']:
  cleanup.append(('remove_ideas','=',idea))
 # Self-build debt service and civilian burden must remain after defensive bonus ends.
 cleanup.append(('if','=',parse('limit = { has_completed_focus = A01_own_fortifications } add_ideas = A01_borneo_debt_service')))
 save(p,dump(t)+'\n')
 p='common/ideas/A01_borneo_projects.txt';s=(R/p).read_text();s=s.replace('ideas = { country = {','ideas = { country = {\n A01_borneo_debt_service = { picture = pacific_industry allowed = { original_tag = A01 } removal_cost = -1 modifier = { consumer_goods_expected_value = 0.05 political_power_gain = -0.10 } }',1);save(p,s)
