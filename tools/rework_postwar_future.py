"""One-time migration of the shared war clock and the postwar political contest."""
from pathlib import Path
import re, shutil

R=Path(__file__).resolve().parents[1]
B=R/'tools/backups/postwar_future_before'
def read(p): return (R/p).read_text(encoding='utf-8-sig')
def write(p,s):
    path=R/p; backup=B/p
    if path.exists() and not backup.exists():
        backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,backup)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(s,encoding='utf-8-sig' if '/localisation/' in '/'+p else 'utf-8')
def span(s,key,identity):
    for m in re.finditer(r'(?m)^\s*'+key+r'\s*=\s*\{',s):
        i=m.end();depth=1
        while depth: depth+=(s[i]=='{')-(s[i]=='}');i+=1
        if re.search(r'\bid\s*=\s*'+re.escape(identity)+r'\b',s[m.end():i]):return m.start(),i
    raise ValueError(identity)
def replace_block(s,key,identity,new):
    a,b=span(s,key,identity);return s[:a]+'\n'+new+'\n'+s[b:]

if 'A01_future_of_netherlands' in read('common/national_focus/a01_focus.txt'):
    raise SystemExit('Migration already applied; edit the generated files directly.')

# Remove the focus and its AI reference; preserve the military development branch.
p='common/national_focus/a03_focus.txt';s=read(p)
s=replace_block(s,'focus','A03_batavia_ultimatum','')
s=s.replace('focus = A03_batavia_ultimatum','focus = A03_resource_commission')
s=s.replace('x = 16\n  y = 5','x = 16\n  y = 4').replace('x = 14\n  y = 6','x = 14\n  y = 5').replace('x = 14\n  y = 7','x = 14\n  y = 6')
write(p,s)
p='common/ai_strategy_plans/A01_canonical.txt';s=read(p).replace('A03_batavia_ultimatum ','')
s=s.replace('A01_reconstruction_commission A01_autonomous_sultanates','A01_future_of_netherlands A01_reconstruction_commission A01_autonomous_sultanates')
s=s.replace('A01_ludolf_survives A01_negotiated_resignation A01_review_borneo_convention','A01_ludolf_survives A01_equal_citizenship A01_elected_civil_service A01_democratic_federation A01_review_borneo_convention')
write(p,s)
# A queued ultimatum from an old save must never bypass the common countdown.
p='events/pacific_diplomacy.txt';s=read(p);a,b=span(s,'country_event','pacific.4');block=s[a:b]
block=block.replace('trigger = {','trigger = {\n  always = no # Retired focus event; the shared opening clock owns escalation.',1)
block=block.replace('A03_start_southern_war_effect = yes','A03_prepare_southern_war_effect = yes')
s=s[:a]+block+s[b:];write(p,s)
p='common/scripted_effects/expansion_effects.txt';s=read(p)
s=s.replace('set_country_flag = A01_island_defence_started\n  activate_mission', '''set_country_flag = A01_island_defence_started
  set_country_flag = A01_refused_japanese_ultimatum
  country_event = { id = A01_future.1 days = 1 }
  country_event = { id = A01_japan.2 days = 14 random_days = 16 }
  activate_mission''',1)
write(p,s)

# Supremacy increases pressure, but cannot silently replace the government.
p='common/bop/A01_ludolf.txt';s=read(p)
s=re.sub(r'\s*on_activate = \{[^\n]+\n','\n',s)
write(p,s)
p='common/on_actions/A01_borneo_story.txt';s=read(p)
s=s.replace('limit = { has_country_flag = A01_borneo_treaty NOT = { has_country_flag = A01_ludolf_crisis_resolved }', 'limit = { has_country_flag = A01_dismissal_debate_active NOT = { has_country_flag = A01_ludolf_crisis_resolved }')
write(p,s)
p='common/scripted_effects/A01_ludolf_effects.txt';s=read(p)
s=s.replace('set_country_flag = A01_borneo_treaty','set_country_flag = A01_borneo_treaty\n  country_event = { id = A01_future.2 days = 7 }',1)
a=s.index('A01_admirals_remove_ludolf_effect = {')
s=s[:a]+'''# All postwar transfers of power go through the explicit political contest.
A01_admirals_remove_ludolf_effect = { A01_establish_military_rule_effect = yes }
'''
write(p,s)

effects='''A01_begin_dismissal_debate_effect = {
 if = { limit = { has_country_flag = A01_borneo_treaty NOT = { has_country_flag = A01_ludolf_crisis_resolved } NOT = { has_country_flag = A01_dismissal_debate_started } }
  set_country_flag = A01_dismissal_debate_started
  set_country_flag = A01_dismissal_debate_active
  activate_mission = A01_motion_to_dismiss_ludolf
  country_event = { id = A01_future.3 days = 1 }
 }
}
A01_end_dismissal_debate_effect = {
 set_country_flag = A01_ludolf_crisis_resolved
 clr_country_flag = A01_dismissal_debate_active
 remove_mission = A01_motion_to_dismiss_ludolf
 remove_ideas = A01_demands_for_freedom
 remove_ideas = A01_reconstruction_cabinet
}
A01_establish_federal_mandate_effect = {
 if = { limit = { NOT = { has_country_flag = A01_ludolf_crisis_resolved } }
  A01_end_dismissal_debate_effect = yes
  set_country_flag = A01_ludolf_survived
  set_country_flag = A01_federal_mandate
  set_power_balance = { id = A01_ludolf_admirals_balance set_value = 0.35 }
  remove_ideas = A01_borneo_humiliation
  add_ideas = A01_federal_transition
  country_event = { id = ludolf.36 days = 1 }
 }
}
A01_establish_military_rule_effect = {
 if = { limit = { has_country_flag = A01_borneo_treaty has_country_flag = A01_dismissal_debate_started NOT = { has_country_flag = A01_ludolf_crisis_resolved } }
  A01_end_dismissal_debate_effect = yes
  set_country_flag = A01_admirals_seized_power
  set_country_flag = A01_ludolf_imprisoned
  set_politics = { ruling_party = neutrality elections_allowed = no }
  set_popularities = { neutrality = 85 democratic = 10 communism = 5 fascism = 0 }
  promote_character = { character = A01_council_of_admirals ideology = despotism }
  retire_character = A01_ludolf_sloot_van_de_beele
  set_power_balance = { id = A01_ludolf_admirals_balance set_value = -0.85 }
  add_ideas = A01_military_directorate
  remove_ideas = A01_wilhelmina
  country_event = { id = ludolf.35 days = 1 }
 }
}
A01_establish_regency_effect = {
 if = { limit = { NOT = { has_country_flag = A01_ludolf_crisis_resolved } }
  A01_end_dismissal_debate_effect = yes
  set_country_flag = A01_royal_path_revealed
  set_country_flag = A01_emma_regency
  recruit_character = A01_emma_waldeck_pyrmont
  promote_character = { character = A01_emma_waldeck_pyrmont ideology = despotism }
  retire_character = A01_ludolf_sloot_van_de_beele
  set_politics = { ruling_party = neutrality elections_allowed = no }
  set_power_balance = { id = A01_ludolf_admirals_balance set_value = 0 }
  add_ideas = A01_royal_arbitration
  mark_focus_tree_layout_dirty = yes
  country_event = { id = A01_future.11 days = 1 }
 }
}
A01_create_autonomous_sultanates_effect = {
'''
for tag,sid in [('A11',1055),('A12',334),('A13',1022)]:
    effects+=f''' if = {{ limit = {{ owns_state = {sid} NOT = {{ country_exists = {tag} }} }}
  {sid} = {{ add_core_of = {tag} }}
  {tag} = {{ transfer_state = {sid} set_politics = {{ ruling_party = neutrality elections_allowed = no }} set_popularities = {{ neutrality = 100 }} }}
  set_autonomy = {{ target = {tag} autonomy_state = autonomy_puppet freedom_level = 0.25 }}
 }}
'''
effects+=''' A01_borneo_resource_rights_effect = yes
 if = { limit = { OR = { A11 = { is_subject_of = A01 } A12 = { is_subject_of = A01 } A13 = { is_subject_of = A01 } } }
  set_country_flag = A01_sultanates_back_ludolf
  add_power_balance_value = { id = A01_ludolf_admirals_balance value = 0.15 }
 }
 country_event = { id = ludolf.31 days = 1 }
}
'''
write('common/scripted_effects/A01_future_effects.txt',effects)
# Remove the three manual release decisions.
p='common/decisions/A01_ludolf_story.txt';s=read(p)
s=re.sub(r'^A01_charter_A1[123] = .*\n','',s,flags=re.M);write(p,s)
for tag,c in [('A11','170 49 59'),('A12','178 57 67'),('A13','186 65 75')]:
    p=f'common/countries/{tag}.txt';s=re.sub(r'color = rgb \{[^}]+\}',f'color = rgb {{ {c} }}',read(p));write(p,s)
p='common/countries/colors.txt';s=read(p)
for tag,c in [('A11','170 49 59'),('A12','178 57 67'),('A13','186 65 75')]:
    s=re.sub(r'^'+tag+r'\s*=.*\n','',s,flags=re.M)
    s+=f'{tag} = {{ color = rgb {{ {c} }} color_ui = rgb {{ {c} }} }}\n'
write(p,s)

# A fixed public layout, with the royal branch absent until its event is accepted.
def focus(fid,x,y,prereqs,reward,available='',exclusive='',cost=3,icon='GFX_goal_generic_political_pressure',hidden=False):
    s=f''' focus = {{
  id = {fid}
  icon = {icon}
  x = {x}
  y = {y}
  cost = {cost}
'''
    for group in prereqs: s+='  prerequisite = { '+ ' '.join('focus = '+p for p in group.split())+' }\n'
    if exclusive:s+='  mutually_exclusive = { focus = '+exclusive+' }\n'
    if hidden:s+='  allow_branch = { has_country_flag = A01_royal_path_revealed }\n'
    if available:s+='  available = { '+available+' }\n  cancel_if_invalid = yes\n'
    s+='  ai_will_do = { factor = 1 }\n  search_filters = { FOCUS_FILTER_POLITICAL }\n'
    s+='  completion_reward = { '+reward+' }\n }'
    return s
p='common/national_focus/a01_focus.txt';s=read(p)
a,b=span(s,'focus','A01_pacific_settlement');block=s[a:b]
block=block.replace('set_country_flag = A01_postwar_cabinet_mandate','set_country_flag = A01_postwar_cabinet_mandate\n   A01_begin_dismissal_debate_effect = yes')
block=block.replace('add_ideas = A01_reconstruction_cabinet','add_ideas = A01_reconstruction_cabinet')
s=s[:a]+block+s[b:]
replacements={
'A01_reconstruction_commission':focus('A01_reconstruction_commission',12,15,['A01_future_of_netherlands'],'add_political_power = 35 add_stability = 0.03',icon='GFX_goal_unique_A01_reconstruction_commission'),
'A01_autonomous_sultanates':focus('A01_autonomous_sultanates',12,16,['A01_reconstruction_commission'],'A01_create_autonomous_sultanates_effect = yes',available='NOT = { has_country_flag = A01_admirals_seized_power }',icon='GFX_goal_unique_A01_autonomous_sultanates'),
'A01_northern_memory':focus('A01_northern_memory',18,15,['A01_future_of_netherlands'],'country_event = { id = ludolf.32 days = 1 }',icon='GFX_goal_unique_A01_northern_memory'),
'A01_federal_defence_compact':focus('A01_federal_defence_compact',12,17,['A01_autonomous_sultanates'],'add_ideas = A01_sultanate_federation add_stability = 0.03',available='has_country_flag = A01_sultanates_back_ludolf',icon='GFX_goal_unique_A01_federal_defence_compact'),
'A01_fleet_of_recovery':focus('A01_fleet_of_recovery',18,16,['A01_northern_memory'],'if = { limit = { owns_state = 1058 } 1058 = { add_extra_state_shared_building_slots = 2 add_building_construction = { type = dockyard level = 2 instant_build = yes } } } navy_experience = 15',icon='GFX_goal_unique_A01_fleet_of_recovery'),
'A01_ludolf_survives':focus('A01_ludolf_survives',12,18,['A01_federal_defence_compact'],'A01_establish_federal_mandate_effect = yes',available='has_country_flag = A01_sultanates_back_ludolf OR = { NOT = { has_country_flag = A01_ludolf_crisis_resolved } has_country_flag = A01_federal_mandate }',exclusive='A01_negotiated_resignation',icon='GFX_goal_unique_A01_ludolf_survives'),
'A01_negotiated_resignation':focus('A01_negotiated_resignation',18,18,['A01_fleet_of_recovery'],'A01_establish_military_rule_effect = yes',available='OR = { NOT = { has_country_flag = A01_ludolf_crisis_resolved } has_country_flag = A01_admirals_seized_power }',exclusive='A01_ludolf_survives',icon='GFX_goal_unique_A01_negotiated_resignation'),
'A01_review_borneo_convention':focus('A01_review_borneo_convention',15,23,['A01_northern_memory'],'add_war_support = 0.05 add_political_power = 100 set_country_flag = A01_borneo_revisionism',available='has_country_flag = A01_ludolf_crisis_resolved',icon='GFX_goal_unique_A01_review_borneo_convention'),
}
for fid,block in replacements.items():s=replace_block(s,'focus',fid,block)
new=[focus('A01_future_of_netherlands',15,14,['A01_pacific_settlement'],'set_country_flag = A01_future_debate_open country_event = { id = A01_future.4 days = 1 }'),
focus('A01_equal_citizenship',12,19,['A01_ludolf_survives'],'remove_dynamic_modifier = A01_racial_divide add_stability = 0.03 country_event = { id = A01_future.6 days = 1 }',available='has_country_flag = A01_federal_mandate'),
focus('A01_elected_civil_service',12,20,['A01_equal_citizenship'],'add_political_power = 75 country_event = { id = A01_future.7 days = 1 }',available='has_country_flag = A01_federal_mandate'),
focus('A01_democratic_federation',12,21,['A01_elected_civil_service'],'''add_country_leader_role = { character = A01_ludolf_sloot_van_de_beele promote_leader = yes country_leader = { ideology = liberalism expire = "1965.1.1.1" traits = { } } }
   set_politics = { ruling_party = democratic elections_allowed = yes election_frequency = 48 }
   set_popularities = { democratic = 70 neutrality = 25 communism = 5 fascism = 0 }
   set_party_name = { ideology = democratic long_name = A01_federal_party short_name = A01_federal_party_short }
   remove_ideas = A01_federal_transition add_ideas = A01_democratic_federation_idea
   remove_dynamic_modifier = A01_admirals_council
   set_cosmetic_tag = A01_FEDERAL
   country_event = { id = A01_future.8 days = 1 }''',available='has_country_flag = A01_federal_mandate',cost=5),
focus('A01_purge_civil_service',18,19,['A01_negotiated_resignation'],'add_ideas = A01_purged_administration add_stability = -0.04 add_political_power = 75 country_event = { id = A01_future.9 days = 1 }',available='has_country_flag = A01_admirals_seized_power'),
focus('A01_purge_officer_corps',18,20,['A01_purge_civil_service'],'add_ideas = A01_purged_officers army_experience = -20 navy_experience = -20 add_stability = -0.03 country_event = { id = A01_future.10 days = 1 }',available='has_country_flag = A01_admirals_seized_power'),
focus('A01_military_state',18,21,['A01_purge_officer_corps'],'remove_ideas = A01_purged_administration remove_ideas = A01_purged_officers add_ideas = A01_total_military_state set_cosmetic_tag = A01_DIRECTORATE country_event = { id = A01_future.15 days = 1 }',available='has_country_flag = A01_admirals_seized_power',cost=5),
focus('A01_crown_above_factions',24,18,[],'add_political_power = 75 add_stability = 0.05',available='has_country_flag = A01_emma_regency',hidden=True),
focus('A01_royal_island_charter',24,19,['A01_crown_above_factions'],'add_stability = 0.04 add_ideas = A01_island_charter country_event = { id = A01_future.12 days = 1 }',hidden=True),
focus('A01_wilhelmina_comes_of_age',24,20,['A01_royal_island_charter'],'''recruit_character = A01_wilhelmina_monarch
   promote_character = { character = A01_wilhelmina_monarch ideology = despotism }
   retire_character = A01_emma_waldeck_pyrmont
   clr_country_flag = A01_emma_regency set_country_flag = A01_wilhelmina_reigns
   country_event = { id = A01_future.13 days = 1 }''',available='date > 1898.8.30 has_country_flag = A01_emma_regency',hidden=True),
focus('A01_royal_constitution',24,21,['A01_wilhelmina_comes_of_age'],'remove_ideas = A01_royal_arbitration add_ideas = A01_constitutional_crown set_cosmetic_tag = A01_CROWN remove_dynamic_modifier = A01_admirals_council country_event = { id = A01_future.14 days = 1 }',hidden=True,cost=5)
]
s=s.rstrip();assert s.endswith('}');s=s[:-1]+'\n'+'\n'.join(new)+'\n}\n';write(p,s)

write('common/characters/A01_royal_family.txt','''characters = {
 A01_emma_waldeck_pyrmont = {
  name = A01_emma_name
  gender = female
  country_leader = { ideology = despotism expire = "1965.1.1.1" traits = { popular_figurehead } }
 }
 A01_wilhelmina_monarch = {
  name = A01_wilhelmina_name
  gender = female
  country_leader = { ideology = despotism expire = "1965.1.1.1" traits = { popular_figurehead } }
 }
}
''')

write('common/decisions/categories/A01_future_categories.txt','''A01_future_contest = {
 icon = generic_political_actions
 allowed = { original_tag = A01 }
 visible = { has_country_flag = A01_dismissal_debate_active }
}
''')
write('common/decisions/A01_future_contest.txt','''A01_future_contest = {
 A01_motion_to_dismiss_ludolf = {
  icon = generic_political_discourse
  days_mission_timeout = 240
  fire_only_once = yes
  selectable_mission = no
  is_good = no
  activation = { always = no }
  available = { hidden_trigger = { always = no } }
  visible = { has_country_flag = A01_dismissal_debate_active }
  cancel_trigger = { has_country_flag = A01_ludolf_crisis_resolved }
  cancel_if_not_visible = yes
  timeout_effect = { country_event = { id = A01_future.5 days = 1 } }
 }
 A01_hear_island_delegates = {
  icon = generic_political_discourse cost = 40 days_re_enable = 30
  available = { has_country_flag = A01_dismissal_debate_active }
  complete_effect = { add_power_balance_value = { id = A01_ludolf_admirals_balance value = 0.10 } add_stability = 0.01 }
  ai_will_do = { factor = 1 }
 }
 A01_back_admiralty_inquiry = {
  icon = generic_prepare_civil_war cost = 40 days_re_enable = 30
  available = { has_country_flag = A01_dismissal_debate_active }
  complete_effect = { add_power_balance_value = { id = A01_ludolf_admirals_balance value = -0.10 } add_to_variable = { A01_admirals_respect = 5 } clamp_variable = { var = A01_admirals_respect min = 0 max = 100 } }
  ai_will_do = { factor = 1 }
 }
 A01_extend_cabinet_hearings = {
  icon = generic_political_discourse cost = 60 fire_only_once = yes
  available = { has_active_mission = A01_motion_to_dismiss_ludolf }
  complete_effect = { add_days_mission_timeout = { mission = A01_motion_to_dismiss_ludolf days = 60 } add_stability = -0.02 }
  ai_will_do = { factor = 1 }
 }
}
''')

ideas={
'A01_demands_for_freedom':('story_sultans','stability_factor = -0.05 political_power_gain = -0.05'),
'A01_federal_transition':('story_ludolf','political_power_gain = -0.05 stability_factor = 0.03'),
'A01_democratic_federation_idea':('story_sultans','stability_factor = 0.08 political_power_gain = 0.15 recruitable_population_factor = 0.10'),
'A01_military_directorate':('story_admirals','political_power_gain = 0.15 war_support_factor = 0.10'),
'A01_purged_administration':('story_admirals','production_speed_buildings_factor = -0.10 stability_factor = -0.03'),
'A01_purged_officers':('story_admirals','army_org_factor = -0.10 navy_org_factor = -0.10'),
'A01_total_military_state':('story_admirals','industrial_capacity_factory = 0.10 political_power_gain = 0.15 stability_factor = -0.05'),
'A01_royal_arbitration':('A01_wilhelmina','stability_factor = 0.07 political_power_gain = 0.05'),
'A01_island_charter':('story_sultans','stability_factor = 0.03 recruitable_population_factor = 0.05'),
'A01_constitutional_crown':('A01_wilhelmina','stability_factor = 0.10 political_power_gain = 0.10')}
s='ideas = { country = {\n'
for key,(pic,mods) in ideas.items():s+=f' {key} = {{ picture = {pic} allowed = {{ original_tag = A01 }} removal_cost = -1 modifier = {{ {mods} }} }}\n'
write('common/ideas/A01_future_ideas.txt',s+'} }\n')

# One hidden eligibility check. No public focus or decision mentions the crown.
write('common/on_actions/A01_future_on_actions.txt','''on_actions = {
 on_daily = { effect = { A01 = {
  if = { limit = {
   has_country_flag = A01_dismissal_debate_active
   has_country_flag = A01_future_debate_open
   has_completed_focus = A01_autonomous_sultanates
   NOT = { has_country_flag = A01_ludolf_crisis_resolved }
   NOT = { has_country_flag = A01_royal_offer_sent }
   power_balance_value = { id = A01_ludolf_admirals_balance value > -0.1 }
   power_balance_value = { id = A01_ludolf_admirals_balance value < 0.1 }
  }
   set_country_flag = A01_royal_offer_sent
   country_event = { id = A01_future.16 days = 7 }
  }
 } } }
}
''')

events='add_namespace = A01_future\n'
def event(eid,options,trigger='',immediate='',picture='talks'):
    global events
    events+=f'''country_event = {{
 id = A01_future.{eid}
 title = A01_future.{eid}.t
 desc = A01_future.{eid}.d
 picture = GFX_1896_event_{picture}
 is_triggered_only = yes
 trigger = {{ tag = A01 {trigger} }}
'''
    if immediate:events+=' immediate = { '+immediate+' }\n'
    events+=options+'\n}\n'
def opt(eid,effect='',suffix='a',extra=''):return f' option = {{ name = A01_future.{eid}.{suffix} {extra} {effect} }}'
event(1,opt(1),trigger='has_active_mission = A01_japanese_invasion_countdown',picture='navy')
event(2,opt(2),trigger='has_country_flag = A01_borneo_treaty NOT = { has_country_flag = A01_ludolf_crisis_resolved }',immediate='add_ideas = A01_demands_for_freedom',picture='protest')
event(3,opt(3),trigger='has_country_flag = A01_dismissal_debate_active',picture='council')
event(4,opt(4),trigger='has_country_flag = A01_dismissal_debate_active',picture='council')
event(5,opt(5,'A01_establish_federal_mandate_effect = yes',extra='trigger = { has_country_flag = A01_sultanates_back_ludolf } ai_chance = { factor = 55 }')+'\n'+opt(5,'A01_establish_military_rule_effect = yes',suffix='b',extra='ai_chance = { factor = 45 }'),trigger='has_country_flag = A01_dismissal_debate_active NOT = { has_country_flag = A01_ludolf_crisis_resolved }',picture='council')
for eid,flag,pic in [(6,'A01_federal_mandate','treaty'),(7,'A01_federal_mandate','council'),(8,'A01_federal_mandate','treaty'),(9,'A01_admirals_seized_power','council'),(10,'A01_admirals_seized_power','navy'),(11,'A01_royal_path_revealed','council'),(12,'A01_royal_path_revealed','treaty'),(13,'A01_wilhelmina_reigns','council'),(14,'A01_wilhelmina_reigns','treaty'),(15,'A01_admirals_seized_power','council')]:
    event(eid,opt(eid),trigger=f'has_country_flag = {flag}',picture=pic)
event(16,opt(16,'A01_establish_regency_effect = yes',extra='ai_chance = { factor = 20 }')+'\n'+opt(16,'add_stability = -0.01',suffix='b',extra='ai_chance = { factor = 80 }'),trigger='has_country_flag = A01_dismissal_debate_active NOT = { has_country_flag = A01_ludolf_crisis_resolved } power_balance_value = { id = A01_ludolf_admirals_balance value > -0.1 } power_balance_value = { id = A01_ludolf_admirals_balance value < 0.1 }',picture='talks')
write('events/A01_future_events.txt',events)

# Replace legacy removal events so queued save-game events cannot end the debate.
p='events/A01_ludolf_story.txt';s=read(p)
s=replace_block(s,'country_event','ludolf.31','''country_event = {
 id = ludolf.31 title = ludolf.31.t desc = ludolf.31.d picture = GFX_1896_event_treaty is_triggered_only = yes
 trigger = { tag = A01 has_country_flag = A01_borneo_treaty }
 option = { name = ludolf.31.a }
}''')
for eid in [33,34]:
    block=f'''country_event = {{
 id = ludolf.{eid} title = ludolf.{eid}.t desc = ludolf.{eid}.d picture = GFX_1896_event_council is_triggered_only = yes
 trigger = {{ tag = A01 has_country_flag = A01_dismissal_debate_active NOT = {{ has_country_flag = A01_ludolf_crisis_resolved }} }}
 option = {{ name = ludolf.{eid}.a add_power_balance_value = {{ id = A01_ludolf_admirals_balance value = -0.05 }} add_political_power = 25 }}
 option = {{ name = ludolf.{eid}.b add_power_balance_value = {{ id = A01_ludolf_admirals_balance value = 0.05 }} add_political_power = -25 }}
}}'''
    s=replace_block(s,'country_event',f'ludolf.{eid}',block)
write(p,s)
print('Shared war clock and postwar gameplay migrated. Localisation is supplied separately.')

