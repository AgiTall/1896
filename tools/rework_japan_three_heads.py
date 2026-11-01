"""Apply the authored Three Heads revision once; never run old tree generators afterwards."""
from pathlib import Path
import re, shutil
from add_canon_countries import parse, value, dump
R=Path(__file__).resolve().parents[1]
B=R/'tools/backups/japan_three_heads_20261019'
def write(p,s,bom=False):
 p=R/p
 if p.exists():
  b=B/p.relative_to(R); b.parent.mkdir(parents=True,exist_ok=True)
  if not b.exists(): shutil.copy2(p,b)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8-sig' if bom else 'utf-8')
tree=parse((R/'common/national_focus/a03_focus.txt').read_text(encoding='utf-8-sig'))
t=value(tree,'focus_tree')
fs={value(n,'id'):n for k,o,n in t if k=='focus'}
if 'JPT_treasury_debts' in fs:
 raise SystemExit('Three Heads revision already applied; edit the current source files in place.')
def setv(fid,k,v):
 n=fs[fid];n[:]=[(a,o,b) for a,o,b in n if a!=k];n.append((k,'=',v))
def block(fid,k,s): setv(fid,k,value(parse(k+' = { '+s+' }'),k))
def parents(fid,*groups):
 fs[fid][:]=[(k,o,v) for k,o,v in fs[fid] if k!='prerequisite']
 for g in groups: fs[fid].append(('prerequisite','=',[('focus','=',p) for p in g.split()]))
def pos(fid,x,y): setv(fid,'x',str(x));setv(fid,'y',str(y))
def add(fid,x,y,parent,reward,available='',icon='GFX_goal_unique_A03_imperial_council',cost=3):
 n=value(parse(f'focus = {{ id = {fid} icon = {icon} x = {x} y = {y} cost = {cost} ai_will_do = {{ factor = 5 }} cancel_if_invalid = yes completion_reward = {{ {reward} }} }}'),'focus')
 fs[fid]=n;t.append(('focus','=',n));parents(fid,parent)
 if available:block(fid,'available',available)

# The imperial appointment is the single root; obsolete ideology prologues are replaced.
removed={k for k in fs if k.startswith('JPX_') and k!='JPX_sea_institution'}
t[:]=[(k,o,n) for k,o,n in t if not(k=='focus' and value(n,'id') in removed)]
for k in removed: del fs[k]
for n in fs.values():
 for i,(k,o,v) in enumerate(n):
  if k=='prerequisite':n[i]=(k,o,[(a,b,'A03_imperial_council' if c=='JPX_sea' else c) for a,b,c in v])
root=fs['A03_imperial_council']
reward=value(root,'completion_reward');reward.extend(parse('set_country_flag = JPX_sea_chosen set_country_flag = JPT_ito_premier JPT_initialize_effect = yes add_ideas = JPX_sea_mandate'))
pos('A03_imperial_council',22,0)
pos('JPC_state_guarantees',14,2);setv('JPC_state_guarantees','cost','3')
block('JPC_state_guarantees','completion_reward','set_country_flag = JPT_loans_guaranteed set_country_flag = JPC_guarantees_signed remove_ideas = JPC_bad_loans add_ideas = JPC_guarantees add_ideas = JPT_iwasaki_dependence add_to_variable = { JPF_budget_confidence = 10 } JPF_refresh_effect = yes')
add('JPT_treasury_debts',18,2,'A03_imperial_council','set_country_flag = JPT_treasury_control add_ideas = JPT_osaka_distrust add_stability = -0.04 add_to_variable = { JPF_debt_pressure = 10 } JPF_refresh_effect = yes',icon='GFX_goal_unique_A01_constitution')
block('JPC_state_guarantees','mutually_exclusive','focus = JPT_treasury_debts');block('JPT_treasury_debts','mutually_exclusive','focus = JPC_state_guarantees')
parents('JPF_public_accounts','JPC_state_guarantees JPT_treasury_debts');pos('JPF_public_accounts',16,3)
value(fs['JPF_public_accounts'],'completion_reward').extend(parse('set_country_flag = JPT_loans_reformed'))
pos('JPF_delivery_calendar',16,4)
block('JPF_delivery_calendar','available','NOT = { has_country_flag = JPT_mitsubishi_crashed }')
value(fs['JPF_delivery_calendar'],'completion_reward').extend(parse('set_country_flag = JPT_military_supplies_paid'))
pos('JPC_northern_protocol',22,2);setv('JPC_northern_protocol','cost','3')
block('JPC_northern_protocol','mutually_exclusive','focus = JPT_north_rebellion')
add('JPT_north_rebellion',26,2,'A03_imperial_council','JPT_north_war_effect = yes','country_exists = A08 NOT = { has_war_with = A08 }')
block('JPT_north_rebellion','mutually_exclusive','focus = JPC_northern_protocol')
pos('JPC_honshu_depots',22,3)
add('JPT_north_front_supply',26,3,'JPT_north_rebellion','add_to_variable = { JPF_debt_pressure = 8 } add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 500 producer = A03 } army_experience = 15 JPF_refresh_effect = yes')
parents('JPN_north_imperial_arbitration','JPC_honshu_depots JPT_north_front_supply');pos('JPN_north_imperial_arbitration',24,4)
block('JPN_north_imperial_arbitration','completion_reward','if = { limit = { has_country_flag = JPT_north_rebel } add_command_power = 20 add_war_support = 0.03 } else = { set_country_flag = { flag = JPN_north_arbitration_grace days = 180 } add_to_variable = { JPN_north_trust = 8 } add_to_variable = { JPN_north_fleet_irritation = -8 } set_country_flag = JPN_north_inspection_channel JPN_north_refresh_effect = yes } set_country_flag = JPT_north_supplies_settled')
pos('JPC_manila_priority',30,2);pos('JPC_garrison_accounts',30,3)
parents('JPR_defence_budget','JPF_delivery_calendar','JPN_north_imperial_arbitration','JPC_garrison_accounts');pos('JPR_defence_budget',22,5)
block('JPR_defence_budget','available','NOT = { has_country_flag = JPT_mitsubishi_crashed }')
value(fs['JPR_defence_budget'],'completion_reward').extend(parse('set_country_flag = JPT_budget_approved'))
# Industry follows the political budget, while its authored choices stay intact.
for fid in list(fs):
 if fid.startswith('JPI_'):pos(fid,int(value(fs[fid],'x')),int(value(fs[fid],'y'))+4)
parents('JPI_closed_ports','JPR_defence_budget');parents('JPI_japanese_terms','JPR_defence_budget')
# Leave room below the longer industrial sequence for the existing war and aftermath.
for fid,n in fs.items():
 if not fid.startswith('JPI_') and int(value(n,'y'))>=14:pos(fid,int(value(n,'x')),int(value(n,'y'))+4)
parents('JPD_settle_three_heads','A03_grand_southern_mandate','A03_prime_minister_filter A03_direct_imperial_rule','JPN_north_postwar_audience')
block('JPD_settle_three_heads','available','custom_trigger_tooltip = { tooltip = JPT_north_settled_tt OR = { has_country_flag = JPN_north_compact_signed AND = { has_country_flag = JPT_north_rebel NOT = { country_exists = A08 } } } }')
write('common/national_focus/a03_focus.txt','# Three Heads of the Dragon: political revision 2026-10-19\n'+dump(tree)+'\n')
p='common/ai_strategy_plans/A01_canonical.txt';s=(R/p).read_text(encoding='utf-8-sig')
s=s.replace('A03_imperial_council JPX_sea JPI_closed_ports','A03_imperial_council JPC_state_guarantees JPF_public_accounts JPF_delivery_calendar JPC_northern_protocol JPC_honshu_depots JPN_north_imperial_arbitration JPC_manila_priority JPC_garrison_accounts JPR_defence_budget JPI_closed_ports')
# Deduplicate only the Japanese focus list, preserving its authored order.
def dedup(m):return 'ai_national_focuses = { '+' '.join(dict.fromkeys(m.group(1).split()))+' }'
start=s.index('A03_southern_canonical_plan');s=s[:start]+re.sub(r'ai_national_focuses\s*=\s*\{([^}]+)\}',dedup,s[start:])
write(p,s)
# Both the ultimatum and actual war require the completed political settlement.
for p,needle in [('common/scripted_effects/JPC_canonical.txt','has_country_flag = JPI_tesla_ready has_country_flag = JPI_southern_ready'),('common/scripted_effects/borneo_war_effects.txt','has_country_flag = JPC_ultimatum_sent has_country_flag = JPI_tesla_ready')]:
 s=(R/p).read_text(encoding='utf-8-sig');s=s.replace(needle,'has_completed_focus = JPR_defence_budget has_completed_focus = JPC_garrison_accounts '+needle);write(p,s)
# Emergency fallback must not undo the player's northern war or debt nationalisation.
p='common/scripted_effects/JPA_agency.txt';s=(R/p).read_text();s=s.replace('NOT = { has_country_flag = JPC_guarantees_signed }','NOT = { has_country_flag = JPC_guarantees_signed } NOT = { has_country_flag = JPT_treasury_control }').replace('NOT = { has_country_flag = JPC_north_signed }','NOT = { has_country_flag = JPC_north_signed } NOT = { has_country_flag = JPT_north_rebel }');write(p,s)
print('Three Heads tree and integration applied:',len(fs),'focuses')
