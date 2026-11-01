"""Visible, shared calendar missions; safe to restore once in existing campaigns."""
from datetime import date,timedelta
from extend_japan_story import read,write,span
import re
def clock_alignment(name,start,end,mission_a,mission_b,base):
 rows=[name+' = {']
 day=start
 while day<end:
  delta=(end-day).days-base
  if delta:
   before=day-timedelta(days=1);after=day+timedelta(days=1)
   fmt=lambda d:f'{d.year}.{d.month}.{d.day}'
   rows.append(f' if = {{ limit = {{ date > {fmt(before)} date < {fmt(after)} }} add_days_mission_timeout = {{ mission = {mission_a} days = {delta} }} A03 = {{ add_days_mission_timeout = {{ mission = {mission_b} days = {delta} }} }} }}')
  day+=timedelta(days=1)
 return '\n'.join(rows)+'\n}\n'
def main():
 # Calendar prelude is invisible. 77 days is the uninterrupted Dutch focus chain.
 text = """# A01 scope. One-time migration; ongoing missions retain Japanese acceleration.
JPS_restore_clocks_effect = {
 if = { limit = { country_exists = A03 NOT = { has_country_flag = JPS_opening_clock_v3 } NOT = { has_country_flag = A01_expansion_resolved } NOT = { has_country_flag = pacific_trade_accord } NOT = { has_war_with = A03 } }
  if = { limit = { NOT = { has_country_flag = JPS_prelude_initialized } }
   set_country_flag = JPS_prelude_initialized
   remove_mission = A01_japanese_invasion_countdown
   A03 = { remove_mission = A03_japanese_invasion_countdown }
  }
  if = { limit = { OR = { has_completed_focus = A01_last_chance_to_negotiate date > 1893.3.18 } }
   JPS_begin_visible_countdown_effect = yes
  }
 }
 if = { limit = { has_war_with = A03 date < 1896.2.1 NOT = { has_country_flag = JPS_war_clock_v2 } NOT = { has_country_flag = A01_expansion_resolved } }
  set_country_flag = JPS_war_clock_v2
  remove_mission = A01_japanese_expansion activate_mission = A01_japanese_expansion
  A03 = { remove_mission = A03_japanese_expansion activate_mission = A03_japanese_expansion }
  JPS_align_war_clocks_effect = yes
 }
}
JPS_begin_visible_countdown_effect = {
 if = { limit = { country_exists = A03 NOT = { has_country_flag = JPS_opening_clock_v3 } NOT = { has_country_flag = A01_expansion_resolved } NOT = { has_country_flag = pacific_trade_accord } NOT = { has_war_with = A03 } }
  set_country_flag = JPS_opening_clock_v3
  set_country_flag = A01_island_defence_started
  A01_begin_expansion_preparations_effect = yes
  if = { limit = { date < 1894.1.1 }
   remove_mission = A01_japanese_invasion_countdown activate_mission = A01_japanese_invasion_countdown
   A03 = { remove_mission = A03_japanese_invasion_countdown activate_mission = A03_japanese_invasion_countdown }
   JPS_align_opening_clocks_effect = yes
  }
  else = { A03 = { JPC_issue_ultimatum = yes } }
 }
}
# A03 scope: both countries lose the same 15 days; once-only decisions call this.
JPS_accelerate_invasion_effect = {
 if = { limit = { has_active_mission = A03_japanese_invasion_countdown A01 = { has_active_mission = A01_japanese_invasion_countdown } }
  add_days_mission_timeout = { mission = A03_japanese_invasion_countdown days = -15 }
  A01 = { add_days_mission_timeout = { mission = A01_japanese_invasion_countdown days = -15 } }
 }
}
"""
 text+=clock_alignment('JPS_align_opening_clocks_effect',date(1893,1,1),date(1894,1,1),'A01_japanese_invasion_countdown','A03_japanese_invasion_countdown',365)
 text+=clock_alignment('JPS_align_war_clocks_effect',date(1893,1,1),date(1896,2,1),'A01_japanese_expansion','A03_japanese_expansion',1006)
 write('common/scripted_effects/JPS_calendar_clocks.txt',text)
 print('Generated hidden prelude, January 1894 invasion deadline and shared acceleration.')
if __name__=='__main__':main()
