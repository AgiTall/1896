"""1896 peace settlements and the start of the Greenland rivalry."""
from datetime import datetime,timedelta
from chronicle_writer import build
from build_chronicle_1893 import ROOT

TAGS='A03 A10 A01 A01 A03 A10 PHW A03 A04 A02 A04 A07 A05 A01 A02 A08 A04 A10 PHW A10 A06 A06 A02 A04'.split()
LUDOLF='has_country_leader = { character = A01_ludolf_sloot_van_de_beele ruling_only = yes }'
E={
1:('set_global_flag = CH96_japan_rejected_talks add_war_support = 0.05','set_global_flag = CH96_japan_accepted_talks add_war_support = -0.05'),
2:('set_country_flag = CH96_visayas_ultimatum add_war_support = 0.05','set_country_flag = CH96_japanese_sphere add_political_power = 25 add_stability = 0.03'),
3:('CH96_hard_peace = yes','CH96_batavia_compromise = yes'),
4:('CH96_ludolf_cabinet = yes','CH96_admiral_coup = yes'),
5:('CH96_manila_protocol = yes','CH96_visayas_war = yes'),
6:('set_country_flag = A10_federal_path clr_country_flag = A10_confederal_path A10_federal_progress = yes add_to_variable = { A10R_cohesion = -5 } A10R_refresh = yes add_political_power = 40','set_country_flag = A10_confederal_path clr_country_flag = A10_federal_path A10_release_PVI = yes A10_release_PSM = yes add_to_variable = { A10R_cohesion = 10 } A10R_refresh = yes add_stability = 0.03'),
7:('remove_ideas = CH95_legion_raids add_timed_idea = { idea = CH96_escorts days = 180 } set_country_flag = CH96_legion_base','add_timed_idea = { idea = CH96_legion_raids days = 120 } add_fuel = -3000 navy_experience = 15'),
8:('CH94_ito_emergency = yes add_timed_idea = { idea = CH96_naval_empire days = 365 }','add_stability = -0.08 A08 = { add_manpower = 2000 add_war_support = 0.06 }'),
9:('CH96_reconstruction_credit = yes','CH96_default = yes'),
10:('add_political_power = -35 add_timed_idea = { idea = CH96_airship_scouts days = 365 } air_experience = 15','add_political_power = -50 add_timed_idea = { idea = CH96_airship_bombers days = 365 } air_experience = 25'),
11:('add_political_power = -40 add_to_variable = { WTN_liquidity = -5 } WTN_update_ledger_effect = yes add_manpower = 1000','add_political_power = -35 add_war_support = 0.04 set_country_flag = CH96_madagascar_concessions'),
12:('set_country_flag = CH96_australian_trade add_political_power = 25 add_equipment_to_stockpile = { type = convoy_1 amount = 10 }','add_timed_idea = { idea = CH96_quarantine days = 365 } add_stability = 0.03 add_equipment_to_stockpile = { type = convoy_1 amount = -5 }'),
13:('if = { limit = { country_exists = PHR NOT = { has_war_with = PHR } } declare_war_on = { target = PHR type = annex_everything } }','CH96_haiti_truce = yes'),
14:('CH96_equal_citizenship = yes','add_stability = -0.06 add_timed_idea = { idea = CH96_racial_divide days = 365 }'),
15:('set_country_flag = CH96_secret_greenland add_political_power = -40 add_fuel = -4000 add_timed_idea = { idea = CH96_expedition days = 180 }','set_global_flag = CH96_joint_greenland add_political_power = -20 A04 = { add_political_power = -20 add_timed_idea = { idea = CH96_expedition days = 180 } } A03 = { add_political_power = -20 add_timed_idea = { idea = CH96_expedition days = 180 } } add_timed_idea = { idea = CH96_expedition days = 180 }'),
16:('CH96_hokkaido_dominion = yes','CH96_hokkaido_independence = yes'),
17:('every_country = { add_timed_idea = { idea = CH96_escorts days = 90 } }','add_political_power = -30 add_tech_bonus = { name = CH96_research bonus = 0.25 uses = 1 category = industry }'),
18:('CH96_sulu_treaty = yes','if = { limit = { country_exists = PSL NOT = { has_war_with = PSL } } declare_war_on = { target = PSL type = annex_everything } }'),
19:('add_timed_idea = { idea = CH96_legion_raids days = 120 } add_equipment_to_stockpile = { type = convoy_1 amount = -5 }','set_country_flag = CH96_legion_base remove_ideas = CH96_legion_raids add_timed_idea = { idea = CH96_escorts days = 180 }'),
20:('set_country_flag = A10_federal_path clr_country_flag = A10_confederal_path set_country_flag = CH96_federal_attempt A10_federal_progress = yes add_to_variable = { A10R_cohesion = -10 } A10R_refresh = yes add_stability = -0.04','CH96_confederation_breakup = yes'),
21:('A02 = { add_political_power = -35 } add_stability = 0.05 add_manpower = 1000','add_stability = -0.07 add_manpower = -750 add_political_power = 20'),
22:('add_political_power = -40 navy_experience = 20 add_timed_idea = { idea = CH96_arctic_fleet days = 365 } add_equipment_to_stockpile = { type = convoy_1 amount = 10 }','add_political_power = -45 navy_experience = 25 add_timed_idea = { idea = CH96_submarine_program days = 365 }'),
23:('CH96_united_crowns = yes','if = { limit = { country_exists = A06 NOT = { has_war_with = A06 } } declare_war_on = { target = A06 type = annex_everything } }'),
24:('set_global_flag = CH96_greenland_cold_war every_country = { limit = { OR = { tag = A02 tag = A03 tag = A06 } } add_war_support = 0.03 }','CH96_borneo_rematch = yes'),
}
HELPERS='''
CH96_finish_borneo_war = {
 set_country_flag = A01_expansion_resolved
 set_country_flag = A01_borneo_treaty
 set_global_flag = CH96_batavia_signed
 A01_cleanup_expansion_effect = yes
 A01_disband_war_militia_effect = yes
 if = { limit = { has_war_with = A03 } white_peace = { tag = A03 } }
 A01_initialize_postwar_accounts_effect = yes
}
CH96_batavia_compromise = {
 if = { limit = { country_exists = A03 has_war_with = A03 NOT = { has_global_flag = CH96_batavia_signed } }
  CH96_finish_borneo_war = yes
  CH96_transfer_north = yes
  set_variable = { CH96_reparations_millions = 2 }
  WTC_initialize_effect = yes add_to_variable = { WTC_debt = 2 } WTC_refresh_effect = yes
  A03 = { set_variable = { CH96_reparations_millions = 5 } WTC_initialize_effect = yes add_to_variable = { WTC_debt = 5 } WTC_refresh_effect = yes }
  A04 = { WTN_initialize_effect = yes add_to_variable = { WTN_liquidity = 7 } WTN_update_ledger_effect = yes }
  add_stability = -0.04
 }
 else = { set_global_flag = ch96_3_inactive }
}
CH96_hard_peace = {
 if = { limit = { country_exists = A03 has_war_with = A03 NOT = { has_global_flag = CH96_batavia_signed } }
  CH96_finish_borneo_war = yes
  CH96_transfer_north = yes
  CH96_transfer_south = yes
  set_variable = { CH96_reparations_millions = 15 }
  WTC_initialize_effect = yes add_to_variable = { WTC_debt = 15 } WTC_refresh_effect = yes
  A04 = { WTN_initialize_effect = yes add_to_variable = { WTN_liquidity = 15 } WTN_update_ledger_effect = yes }
  add_stability = -0.10
 }
 else = { set_global_flag = ch96_3_inactive }
}
CH96_ludolf_cabinet = {
 if = { limit = { has_character = A01_ludolf_sloot_van_de_beele }
  A01_end_dismissal_debate_effect = yes
  clr_country_flag = A01_admirals_seized_power
  set_country_flag = A01_ludolf_survived
  set_country_flag = A01_ludolf_reform_path
  promote_character = { character = A01_ludolf_sloot_van_de_beele ideology = oligarchism }
  add_stability = 0.04
 }
 else = { set_global_flag = ch96_4_inactive }
}
CH96_admiral_coup = {
 if = { limit = { has_character = A01_council_of_admirals }
  A01_end_dismissal_debate_effect = yes
  set_country_flag = A01_admirals_seized_power
  set_country_flag = A01_ludolf_imprisoned
  promote_character = { character = A01_council_of_admirals ideology = despotism }
  if = { limit = { has_character = A01_ludolf_sloot_van_de_beele } retire_character = A01_ludolf_sloot_van_de_beele }
  add_ideas = A01_military_directorate add_stability = -0.05
 }
 else = { set_global_flag = ch96_4_inactive }
}
CH96_manila_protocol = {
 if = { limit = { country_exists = A10 }
  if = { limit = { A10 = { is_subject_of = A03 } } set_autonomy = { target = A10 autonomy_state = autonomy_free } }
  A10 = { if = { limit = { has_war_with = A03 } white_peace = { tag = A03 } } every_subject_country = { if = { limit = { has_war_with = A03 } white_peace = { tag = A03 } } } set_country_flag = A10_archipelago_peace_signed add_stability = 0.06 }
  set_global_flag = CH96_manila_signed
  CH96_transfer_visayas = yes
 }
 else = { set_global_flag = ch96_5_inactive }
}
CH96_visayas_war = {
 if = { limit = { country_exists = A10 NOT = { has_war_with = A10 } is_subject = no } declare_war_on = { target = A10 type = annex_everything } }
}
CH96_reconstruction_credit = {
 WTN_initialize_effect = yes
 if = { limit = { check_variable = { WTN_liquidity > 19 } }
  add_to_variable = { WTN_liquidity = -20 } WTN_update_ledger_effect = yes
  every_country = { limit = { OR = { tag = A01 tag = A03 } } WTC_initialize_effect = yes add_to_variable = { WTC_debt = 10 } WTC_refresh_effect = yes add_political_power = 30 add_timed_idea = { idea = CH96_reconstruction days = 180 } }
 }
 else = { set_global_flag = ch96_9_inactive }
}
CH96_default = {
 every_country = { limit = { OR = { tag = A01 tag = A03 } }
  WTC_initialize_effect = yes set_variable = { WTC_debt = 100 } WTC_refresh_effect = yes add_stability = -0.04
 }
}
CH96_haiti_truce = {
 if = { limit = { country_exists = PHR }
  if = { limit = { has_war_with = PHR } white_peace = { tag = PHR } }
  319 = { if = { limit = { is_owned_by = A05 } PHR = { transfer_state = 319 } } }
  diplomatic_relation = { country = PHR relation = non_aggression_pact }
 }
}
CH96_equal_citizenship = {
 if = { limit = { has_country_leader = { character = A01_ludolf_sloot_van_de_beele ruling_only = yes } }
  set_country_flag = A01_equal_citizenship_established remove_ideas = CH96_racial_divide
  add_ideas = CH96_citizenship add_stability = 0.04
 }
 else = { set_global_flag = ch96_14_inactive }
}
CH96_hokkaido_dominion = {
 if = { limit = { country_exists = A03 OR = { is_subject = no is_subject_of = A03 } }
  if = { limit = { has_war_with = A03 } white_peace = { tag = A03 } }
  A03 = { set_autonomy = { target = A08 autonomy_state = autonomy_dominion freedom_level = 0.75 } }
  set_country_flag = CH96_hokkaido_dominion add_stability = 0.04
 }
 else = { set_global_flag = ch96_16_inactive }
}
CH96_hokkaido_independence = {
 if = { limit = { is_subject_of = A03 } A03 = { set_autonomy = { target = A08 autonomy_state = autonomy_free end_wars = no } } }
 if = { limit = { country_exists = A03 NOT = { has_war_with = A03 } is_subject = no } declare_war_on = { target = A03 type = annex_everything } }
}
CH96_sulu_treaty = {
 if = { limit = { country_exists = PSL }
  if = { limit = { has_war_with = PSL } white_peace = { tag = PSL } }
  if = { limit = { PSL = { is_subject_of = A10 } } set_autonomy = { target = PSL autonomy_state = autonomy_free } }
  diplomatic_relation = { country = PSL relation = non_aggression_pact }
 }
}
CH96_confederation_breakup = {
 A10_release_PVI = yes A10_release_PSM = yes A10_release_PCB = yes A10_release_PPN = yes
 every_subject_country = { limit = { OR = { tag = PVI tag = PSM tag = PCB tag = PPN tag = PMD tag = PNM tag = PML tag = PBT } }
  save_event_target_as = CH96_leaving_member
  A10 = { set_autonomy = { target = event_target:CH96_leaving_member autonomy_state = autonomy_free end_wars = no } }
 }
 add_to_variable = { A10R_cohesion = -30 } A10R_refresh = yes add_stability = -0.08
}
CH96_united_crowns = {
 if = { limit = { country_exists = A06 NOT = { has_war_with = A06 } }
  set_global_flag = CH96_united_crowns
  create_country_leader = { name = CH96_joint_cabinet ideology = despotism expire = "1965.1.1.1" traits = { } }
  A06 = { create_country_leader = { name = CH96_joint_cabinet ideology = despotism expire = "1965.1.1.1" traits = { } } }
  add_ideas = CH96_crowns A06 = { add_ideas = CH96_crowns }
  give_military_access = A06 A06 = { give_military_access = A02 }
  if = { limit = { NOT = { is_in_faction = yes } A06 = { NOT = { is_in_faction = yes } is_subject = no } is_subject = no }
   create_faction_from_template = CH96_crowns_template add_to_faction = A06
  }
 }
 else = { set_global_flag = ch96_23_inactive }
}
CH96_borneo_rematch = {
 if = { limit = { country_exists = A01 country_exists = A03 A03 = { NOT = { has_war_with = A01 } is_subject = no } }
  A03 = { diplomatic_relation = { country = A01 relation = non_aggression_pact active = no } declare_war_on = { target = A01 type = take_state_focus generator = { 1023 1024 } } }
  set_global_flag = CH96_borneo_rematch
 }
}
'''
IDEAS={
'escorts':('Усиленные морские патрули','Флот охраняет морские пути.','convoy_escort_efficiency = 0.10'),
'legion_raids':('Бои у Мидуэя','Набеги Легиона нарушают снабжение Гавайев.','supply_consumption_factor = 0.10'),
'naval_empire':('Морская Империя','Адмирал Ито укрепляет морскую мощь.','navy_org_factor = 0.05'),
'airship_scouts':('Разведывательные дирижабли','Воздушная разведка поддерживает морские операции.','naval_detection = 0.05'),
'airship_bombers':('Программа боевых дирижаблей','Развитие военной аэронавтики.','air_mission_efficiency = 0.03'),
'reconstruction':('Кредиты на восстановление','Палата финансирует восстановление промышленности.','production_speed_industrial_complex_factor = 0.05'),
'quarantine':('Тотальный карантин','Порты ограничивают торговлю и морские перевозки.','industrial_capacity_factory = -0.05 convoy_escort_efficiency = 0.05'),
'citizenship':('Равное гражданство','Индонезийцы получают гражданские права.','stability_factor = 0.04 recruitable_population_factor = 0.05'),
'racial_divide':('Политика превосходства','Неравенство усиливает напряжение.','stability_factor = -0.05'),
'expedition':('Подготовка Гренландской экспедиции','Экспедиционные работы требуют снабжения и исследований.','research_speed_factor = 0.02 supply_consumption_factor = 0.03'),
'arctic_fleet':('Арктический флот','Ледокольная программа поддерживает полярные экспедиции.','navy_org_factor = 0.04'),
'submarine_program':('Программа подводного флота','Развитие подводных операций.','naval_coordination = 0.04'),
'crowns':('Единый Престол','Совместный совет координирует политику корон.','political_power_gain = 0.10 stability_factor = -0.02'),
}

def main():
    helpers=HELPERS
    for name,states,target,owner in [('north',[1024,1023,1059,333],'A03','A01'),('south',[334,1022,1055],'A03','A01'),('visayas',[624,625,627,628,1026,1085],'A10','A03')]:
        helpers+=f'\nCH96_transfer_{name} = {{\n'+''.join(f' {s} = {{ if = {{ limit = {{ is_owned_by = {owner} }} {target} = {{ transfer_state = {s} }} }} }}\n' for s in states)+'}\n'
    # Reset only the still-running mission once, aligning old saves to Feb 15.
    timer=['CH96_align_borneo_timer = {',' if = { limit = { date < 1896.2.15 A01 = { has_war_with = A03 NOT = { has_country_flag = CH96_timer_aligned } } }',' A01 = { set_country_flag = CH96_timer_aligned set_country_flag = JPS_war_clock_v2 remove_mission = A01_japanese_expansion activate_mission = A01_japanese_expansion }',' A03 = { remove_mission = A03_japanese_expansion activate_mission = A03_japanese_expansion }']
    day=datetime(1896,1,1);end=datetime(1896,2,15)
    while day<end:
        prev,nxt=day-timedelta(days=1),day+timedelta(days=1);delta=(end-day).days-1006
        fmt=lambda d:f'{d.year}.{d.month}.{d.day}'
        timer.append(f' if = {{ limit = {{ date > {fmt(prev)} date < {fmt(nxt)} }} A01 = {{ add_days_mission_timeout = {{ mission = A01_japanese_expansion days = {delta} }} }} A03 = {{ add_days_mission_timeout = {{ mission = A03_japanese_expansion days = {delta} }} }} }}')
        day+=timedelta(days=1)
    timer+=[' }','}'];helpers+='\n'+'\n'.join(timer)+'\n'
    # The treaty decision owns the deadline; the old automatic outcome must not
    # resolve before a human has answered the February 15 event.
    prelude='CH96_align_borneo_timer = yes\n if = { limit = { date > 1896.2.13 NOT = { has_global_flag = CH96_batavia_signed } } A01 = { remove_mission = A01_japanese_expansion } A03 = { remove_mission = A03_japanese_expansion } }'
    ai={(14,0):f'factor = 100 modifier = {{ factor = 0 NOT = {{ {LUDOLF} }} }}',(14,1):f'factor = 0 modifier = {{ add = 100 NOT = {{ {LUDOLF} }} }}'}
    build(1896,TAGS,E,helpers,IDEAS,gates={14:LUDOLF},prelude=prelude,extra_loc={'CH96_research':'Исследования Чёрного Хора','CH96_crowns_faction':'Совет Корон','CH96_joint_cabinet':'Совет Единого Престола'},ai=ai)
    from build_chronicle_1893 import write
    write('common/factions/templates/chronicle_1896.txt','CH96_crowns_template = { name = CH96_crowns_faction icon = GFX_A10_confederation_sun manifest = faction_manifest_strength_in_unity default_rules = { change_leader_rule_manpower } }\n')

def finalize_current_revision():
    main()
    if (ROOT / 'docs/chronicle_revision_source.json').exists() and (ROOT / 'common/national_focus/BLV_campaign.txt').exists():
        from apply_chronicle_revision import main as apply_revision
        apply_revision()

if __name__=='__main__':finalize_current_revision()
