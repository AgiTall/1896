from pathlib import Path
import re,shutil
R=Path(__file__).resolve().parents[1]
B=R/'tools/backups/borneo_war_before'
def write(rel,text):
 p=R/rel
 if p.exists() and not (B/rel).exists():
  (B/rel).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,B/rel)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8-sig' if rel.startswith('localisation/') else 'utf-8')
def edit(rel,old,new):
 t=(R/rel).read_text(encoding='utf-8-sig');assert old in t,(rel,old);write(rel,t.replace(old,new))
edit('common/countries/A03.txt','45 135 74','255 191 191')
edit('common/countries/colors.txt','A03 = { color = rgb { 45 135 74 } color_ui = rgb { 59 176 96 } }','A03 = { color = rgb { 255 191 191 } color_ui = rgb { 255 191 191 } }')
edit('common/scripted_effects/A01_ludolf_effects.txt','transfer_state = 1024 transfer_state = 1023','transfer_state = 1024 transfer_state = 1023 transfer_state = 1059')
edit('common/scripted_effects/A01_ludolf_effects.txt','  remove_ideas = A01_war_production','  A01_disband_war_militia_effect = yes\n  remove_ideas = A01_war_production')
edit('common/on_actions/A01_borneo_story.txt','id = ludolf.20 days = 120','id = ludolf.20 days = 180')
edit('common/on_actions/A01_borneo_story.txt','    A01 = {\n     if','    A01 = {\n     set_country_flag = A01_borneo_war_started\n     if')
edit('common/scripted_effects/A01_ludolf_effects.txt','A01_borneo_resource_rights_effect = {','A01_borneo_resource_rights_effect = {\n1059 = { owner = { if = { limit = { NOT = { tag = A03 } } give_resource_rights = { receiver = A03 state = 1059 resources = { oil rubber } } } } }')
# One preparation/start path for the mission and national focus; repeat-safe OOB.
effects='''A03_prepare_southern_war_effect = {
 if = { limit = { NOT = { has_country_flag = A03_southern_force_prepared } }
  set_country_flag = A03_southern_force_prepared
  set_technology = { infantry_weapons = 1 tech_support = 1 marines = 1 }
  if = { limit = { has_dlc = "Man the Guns" }
   set_technology = { mtg_transport = 1 early_ship_hull_heavy = 1 basic_heavy_battery = 1 }
   create_equipment_variant = { name = "Pacific Ironclad" type = ship_hull_heavy_1 parent_version = 0
    modules = { fixed_ship_battery_slot = ship_heavy_battery_1 fixed_ship_anti_air_slot = empty fixed_ship_fire_control_system_slot = ship_fire_control_system_0 fixed_ship_radar_slot = empty fixed_ship_engine_slot = heavy_ship_engine_1 fixed_ship_armor_slot = ship_armor_bb_1 front_1_custom_slot = ship_heavy_battery_1 mid_1_custom_slot = empty mid_2_custom_slot = empty rear_1_custom_slot = ship_heavy_battery_1 }
   }
   load_oob = "A03_southern_reinforcements"
   else = { set_technology = { transport = 1 early_battleship = 1 } load_oob = "A03_southern_reinforcements_legacy" }
  }
  load_oob = "A03_borneo_invasion"
  add_equipment_to_stockpile = { type = convoy_1 amount = 150 producer = A03 }
  add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 4000 producer = A03 }
  add_fuel = 100000
  if = { limit = { owns_state = 647 } 647 = { add_building_construction = { type = naval_base level = 3 province = 4357 instant_build = yes } } }
 }
}
A03_start_southern_war_effect = {
 if = { limit = { country_exists = A01 NOT = { has_war_with = A01 } NOT = { has_country_flag = pacific_trade_accord } NOT = { has_country_flag = A03_borneo_victory } }
  A03_prepare_southern_war_effect = yes
  add_timed_idea = { idea = A03_southern_blitz days = 180 }
  add_fuel = 100000
  declare_war_on = { target = A01 type = take_state_focus generator = { 1023 1024 } }
  A01 = { set_country_flag = A01_japanese_invasion_begun country_event = { id = A01_japan.5 hours = 1 } }
  country_event = { id = southern_war.1 days = 30 }
 }
}
A01_disband_war_militia_effect = {
 if = { limit = { has_country_flag = A01_war_militia_raised }
  delete_unit_template_and_units = { division_template = "Indonesian Volunteer Militia" }
  clr_country_flag = A01_war_militia_raised
  remove_ideas = A01_indonesian_volunteers
  country_event = { id = A01_japan.40 days = 1 }
 }
}
'''
write('common/scripted_effects/borneo_war_effects.txt',effects)
# The focus advances the real 180-day mission; it no longer bypasses the timer.
p='common/national_focus/a03_focus.txt';t=(R/p).read_text()
old='completion_reward = { load_oob = "A03_borneo_invasion" declare_war_on = { target = A01 type = take_state_focus generator = { 334 1022 1024 1055 } } A01 = { set_country_flag = A01_japanese_invasion_begun } }'
assert old in t
t=t.replace(old,'completion_reward = { A03_prepare_southern_war_effect = yes A01 = { if = { limit = { has_active_mission = A01_japanese_invasion_countdown } add_days_mission_timeout = { mission = A01_japanese_invasion_countdown days = -30 } } } }')
t=t.replace('available = { owns_state = 1055 NOT = { has_war_with = A01 } }','available = { has_country_flag = A03_borneo_victory NOT = { has_war_with = A01 } }')
t=t.replace('if = { limit = { owns_state = 1055 } 1055 = { add_extra_state_shared_building_slots = 1 add_building_construction = { type = industrial_complex level = 1 instant_build = yes } } }add_stability = 0.05','if = { limit = { owns_state = 1024 } 1024 = { add_extra_state_shared_building_slots = 1 add_building_construction = { type = industrial_complex level = 1 instant_build = yes } } }add_stability = 0.05')
write(p,t)
p='common/decisions/A01_inevitable_conflict.txt';t=(R/p).read_text();start=t.index('\t\ttimeout_effect =');t=t[:start]+'''        timeout_effect = { A03 = { A03_start_southern_war_effect = yes } }
    }
}
''';write(p,t)
# Begin preparing before war; later speeches cannot instantly erase refusal.
p='events/A01_japan_events.txt';t=(R/p).read_text();a=t.index('country_event = {\n\tid = A01_japan.2');b=t.index('country_event = {\n\tid = A01_japan.3',a)
t=t[:a]+'''country_event = {
 id = A01_japan.2 title = A01_japan.2.t desc = A01_japan.2.d is_triggered_only = yes
 trigger = { tag = A01 has_country_flag = A01_refused_japanese_ultimatum NOT = { has_country_flag = A01_admiral_speech_chosen } }
 immediate = { add_ideas = A01_indonesian_refusal }
 option = { name = A01_japan.2.hard ai_chance = { factor = 25 } set_country_flag = A01_admiral_speech_chosen country_event = { id = A01_japan.10 days = 5 } }
 option = { name = A01_japan.2.balance ai_chance = { factor = 50 } set_country_flag = A01_admiral_speech_chosen country_event = { id = A01_japan.11 days = 5 } }
 option = { name = A01_japan.2.support ai_chance = { factor = 25 } set_country_flag = A01_admiral_speech_chosen country_event = { id = A01_japan.12 days = 5 } }
}

'''+t[b:]
t=t.replace('activate_mission = A01_japanese_invasion_countdown','activate_mission = A01_japanese_invasion_countdown\n        A03 = { A03_prepare_southern_war_effect = yes }')
write(p,t)
write('common/ideas/borneo_war_ideas.txt','''ideas = { country = {
 A03_southern_blitz = { picture = pacific_japan allowed = { original_tag = A03 } removal_cost = -1
  modifier = { shore_bombardment_bonus = 0.50 army_attack_factor = 0.15 naval_damage_factor = 0.15 naval_invasion_prep_speed = 0.75 amphibious_invasion = 0.30 naval_invasion_capacity = 12 }
  equipment_bonus = { screen_ship = { naval_range = 1.00 } capital_ship = { naval_range = 1.00 } }
 }
 A01_indonesian_refusal = { picture = story_defeat removal_cost = -1 modifier = { recruitable_population_factor = -0.30 army_org_factor = -0.10 stability_factor = -0.05 } }
 A01_coerced_service = { picture = story_admirals removal_cost = -1 modifier = { recruitable_population_factor = -0.15 army_org_factor = -0.05 stability_factor = -0.10 war_support_factor = 0.05 } }
 A01_service_compromise = { picture = story_constitution removal_cost = -1 modifier = { recruitable_population_factor = -0.10 stability_factor = 0.03 } }
 A01_indonesian_volunteers = { picture = story_sultans removal_cost = -1 modifier = { recruitable_population_factor = -0.05 stability_factor = 0.05 } }
} }
''')
write('common/ai_strategy/A03_southern_war.txt','''A03_borneo_operations = {
 allowed = { original_tag = A03 }
 enable = { has_country_flag = A03_southern_force_prepared NOT = { has_country_flag = A03_borneo_victory } }
 abort = { OR = { has_country_flag = A03_borneo_victory has_country_flag = pacific_trade_accord } }
 ai_strategy = { type = conquer id = A01 value = 300 }
 ai_strategy = { type = invade id = A01 value = 400 }
 ai_strategy = { type = naval_invasion_focus value = 500 }
 ai_strategy = { type = invasion_unit_request state = 1024 value = 250 }
 ai_strategy = { type = invasion_unit_request state = 1023 value = 200 }
 ai_strategy = { type = invasion_unit_request state = 1055 value = 100 }
 ai_strategy = { type = naval_invasion_support_priority id = 75 value = 300 }
 ai_strategy = { type = naval_invasion_support_priority id = 78 value = 300 }
 ai_strategy = { type = naval_invasion_support_priority id = 80 value = 300 }
}
''')
write('common/decisions/categories/A03_southern_preparations.txt','''A03_southern_preparations = { icon = generic_naval allowed = { original_tag = A03 } visible = { country_exists = A01 A01 = { has_active_mission = A01_japanese_invasion_countdown } NOT = { has_war_with = A01 } } }
''')
dec='A03_southern_preparations = {\n'
for key,cost,days in [('charter_transports',35,15),('advance_coaling',50,20),('final_sailing_orders',75,30)]:
 dec+=f''' A03_{key} = {{ icon = generic_naval cost = {cost} fire_only_once = yes
  visible = {{ A01 = {{ has_active_mission = A01_japanese_invasion_countdown }} NOT = {{ has_war_with = A01 }} }}
  available = {{ A01 = {{ has_active_mission = A01_japanese_invasion_countdown }} }}
  complete_effect = {{ A01 = {{ add_days_mission_timeout = {{ mission = A01_japanese_invasion_countdown days = -{days} }} country_event = {{ id = southern_war.2 days = 1 }} }} }}
  ai_will_do = {{ base = 10 }}
 }}\n'''
write('common/decisions/A03_southern_preparations.txt',dec+'}\n')
write('events/southern_war.txt','''add_namespace = southern_war
country_event = { id = southern_war.1 hidden = yes is_triggered_only = yes trigger = { tag = A03 has_war_with = A01 has_idea = A03_southern_blitz } immediate = { add_fuel = 15000 country_event = { id = southern_war.1 days = 30 } } }
country_event = { id = southern_war.2 title = southern_war.2.t desc = southern_war.2.d is_triggered_only = yes trigger = { tag = A01 NOT = { has_war_with = A03 } } option = { name = southern_war.2.a } }
''')
# Existing naval variants are kept; the prewar reinforcement has heavy guns for shore fire.
def ship(name,kind,legacy=False):
 eq,var,definition={'heavy':('ship_hull_heavy_1','Pacific Ironclad','battleship'),'cruiser':('ship_hull_cruiser_1','Pacific Cruiser','light_cruiser'),'escort':('ship_hull_light_1','Pacific Escort','destroyer')}[kind]
 if legacy:eq={'heavy':'battleship_1','cruiser':'light_cruiser_1','escort':'destroyer_1'}[kind]
 version='' if legacy else f'version_name = "{var}"'
 return f'ship = {{ name = "{name}" definition = {definition} start_experience_factor = 0.30 equipment = {{ {eq} = {{ amount = 1 owner = A03 {version} }} }} }}\n'
for legacy in [False,True]:
 ships=''.join(ship(f'Nankai Ironclad {i+1}','heavy',legacy) for i in range(4))+''.join(ship(f'Nankai Cruiser {i+1}','cruiser',legacy) for i in range(6))+''.join(ship(f'Nankai Escort {i+1}','escort',legacy) for i in range(10))
 write('history/units/A03_southern_reinforcements'+('_legacy' if legacy else '')+'.txt','units = { fleet = { name = "Southern Expedition Fleet" naval_base = 4357 task_force = { name = "Borneo Assault Squadron" location = 4357\n'+ships+'} } }\n')
# Marines assemble in a supplied forward harbour within operational range.
p='history/units/A03_borneo_invasion.txt';t=(R/p).read_text();t=t.replace('location = 1421','location = 4357').replace('location = 4429','location = 4357');write(p,t)
write('history/units/A01_indonesian_militia.txt','''division_template = { name = "Indonesian Volunteer Militia" is_locked = yes regiments = { infantry = { x = 0 y = 0 } infantry = { x = 0 y = 1 } infantry = { x = 1 y = 0 } } }
units = {
 division = { name = "1. Java Volunteer Militia" location = 7381 division_template = "Indonesian Volunteer Militia" start_equipment_factor = 1.0 start_experience_factor = 0.05 }
 division = { name = "2. Java Volunteer Militia" location = 7381 division_template = "Indonesian Volunteer Militia" start_equipment_factor = 1.0 start_experience_factor = 0.05 }
 division = { name = "3. Java Volunteer Militia" location = 7381 division_template = "Indonesian Volunteer Militia" start_equipment_factor = 1.0 start_experience_factor = 0.05 }
}
''')
write('common/on_actions/borneo_militia_cleanup.txt','''on_actions = { on_daily = { effect = { A01 = { if = { limit = { has_country_flag = A01_war_militia_raised has_country_flag = A01_borneo_war_started NOT = { has_war_with = A03 } } A01_disband_war_militia_effect = yes } } } } }
''')
p='common/characters/A01_admirals.txt';t=(R/p).read_text();t=t.rstrip()[:-1]+'''
 # Fictional officer of this alternate-history colonial navy.
 A01_surya_wirata = { name = A01_surya_wirata_name
  portraits = { navy = { large = GFX_portrait_se_asia_generic_navy_1 small = GFX_portrait_se_asia_generic_navy_1_small } }
  navy_leader = { skill = 3 attack_skill = 2 defense_skill = 3 maneuvering_skill = 4 coordination_skill = 3 traits = { navy_career_officer } }
 }
}
''';write(p,t)
p=next((R/'history/countries').glob('A01*'));rel=str(p.relative_to(R)).replace('\\','/');edit(rel,'recruit_character = A01_fabius','recruit_character = A01_fabius\nrecruit_character = A01_surya_wirata')
# Four stages: refusal -> chosen speech -> other admirals' response -> policy.
ev='add_namespace = A01_japan\n'
for idx,path in enumerate(['hard','balance','support']):
 for num,nextnum in [(10+idx,20+idx),(20+idx,30+idx)]:
  ev+=f'country_event = {{ id = A01_japan.{num} title = A01_japan.{num}.t desc = A01_japan.{num}.d is_triggered_only = yes trigger = {{ tag = A01 NOT = {{ has_country_flag = A01_borneo_treaty }} }} option = {{ name = A01_japan.{num}.a country_event = {{ id = A01_japan.{nextnum} days = 7 }} }} }}\n'
 outcomes=[
 'add_ideas = A01_coerced_service set_country_flag = A01_hardline_response_to_indonesians set_country_flag = A01_colonial_police_decision_unlocked add_war_support = 0.05 country_event = { id = A01_japan.3 days = 60 }',
 'add_ideas = A01_service_compromise set_country_flag = A01_council_of_sultans_decision_unlocked add_political_power = -35',
 'add_ideas = A01_indonesian_volunteers set_country_flag = A01_indonesian_integration if = { limit = { NOT = { has_country_flag = A01_war_militia_raised } } load_oob = "A01_indonesian_militia" set_country_flag = A01_war_militia_raised } add_political_power = -50'
 ]
 num=30+idx
 ev+=f'country_event = {{ id = A01_japan.{num} title = A01_japan.{num}.t desc = A01_japan.{num}.d is_triggered_only = yes trigger = {{ tag = A01 NOT = {{ has_country_flag = A01_borneo_treaty }} }} option = {{ name = A01_japan.{num}.a remove_ideas = A01_indonesian_refusal {outcomes[idx]} }} }}\n'
ev+='country_event = { id = A01_japan.40 title = A01_japan.40.t desc = A01_japan.40.d is_triggered_only = yes option = { name = A01_japan.40.a } }\n'
write('events/A01_admiral_speeches.txt',ev)
print('War, countdown, fleet, speech chain and militia scripts written. Localisation follows separately.')
