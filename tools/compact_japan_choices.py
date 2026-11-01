"""One-time layout and industrial-choice repair after in-game screenshot review."""
from pathlib import Path
import re,shutil
from add_canon_countries import parse,value,dump
R=Path(__file__).resolve().parents[1];B=R/'tools/backups/japan_compact_choices_20261019'
def save(p,s,bom=False):
 p=R/p
 if p.exists():
  b=B/p.relative_to(R);b.parent.mkdir(parents=True,exist_ok=True)
  if not b.exists():shutil.copy2(p,b)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8-sig' if bom else 'utf-8')
t=parse((R/'common/national_focus/a03_focus.txt').read_text());tree=value(t,'focus_tree')
fs={value(n,'id'):n for k,o,n in tree if k=='focus'}
if 'JPI_fleet_workshops' in fs:raise SystemExit('Already applied; edit current sources in place.')
def put(fid,k,v):
 fs[fid][:]=[(a,o,b) for a,o,b in fs[fid] if a!=k]+[(k,'=',v)]
def block(fid,k,s):put(fid,k,value(parse(k+' = { '+s+' }'),k))
def parents(fid,*groups):
 fs[fid][:]=[(k,o,v) for k,o,v in fs[fid] if k!='prerequisite']
 for g in groups:fs[fid].append(('prerequisite','=',[('focus','=',p) for p in g.split()]))
def pos(fid,x,y):put(fid,'x',str(x));put(fid,'y',str(y))
def new(fid,x,y,parent,reward,icon):
 n=value(parse(f'focus = {{ id = {fid} icon = {icon} cost = 2 cancel_if_invalid = yes ai_will_do = {{ factor = 10 }} search_filters = {{ FOCUS_FILTER_INDUSTRY FOCUS_FILTER_NAVY }} completion_reward = {{ {reward} }} }}'),'focus')
 fs[fid]=n;tree.append(('focus','=',n));pos(fid,x,y);parents(fid,parent)
def pair(a,b):block(a,'mutually_exclusive','focus = '+b);block(b,'mutually_exclusive','focus = '+a)
# Fold two clerical steps into the actual industrial policy choice.
for old,target in [('JPI_raw_register','JPI_closed_ports'),('JPI_unsigned_contracts','JPI_japanese_terms')]:
 value(fs[target],'completion_reward').extend(value(fs[old],'completion_reward'))
 tree[:]=[(k,o,n) for k,o,n in tree if not(k=='focus' and value(n,'id')==old)];del fs[old]
parents('JPI_kyushu_coal','JPI_closed_ports');parents('JPI_oil_hunger','JPI_closed_ports')
parents('JPI_proxy_machines','JPI_japanese_terms');parents('JPI_copied_samples','JPI_japanese_terms')
for fid,x,y in [('JPI_closed_ports',12,6),('JPI_japanese_terms',20,6),('JPI_kyushu_coal',10,7),('JPI_oil_hunger',14,7),('JPI_proxy_machines',18,7),('JPI_copied_samples',22,7),('JPI_standard_node',16,8),('JPI_kure_yards',14,9),('JPI_airship_hangars',18,9),('JPI_electrical_bureau',14,10),('JPI_portable_prototype',14,11),('JPI_quiet_coast',14,12),('JPI_coastal_trials',18,12),('JPI_scarlet_sails',16,13),('JPI_southern_push',16,14)]:pos(fid,x,y)
new('JPI_fleet_workshops',18,10,'JPI_kure_yards JPI_airship_hangars','set_country_flag = JPI_tesla_design navy_experience = 15 add_to_variable = { JPF_debt_pressure = 5 } JPF_refresh_effect = yes add_ideas = JPI_workshop_network','GFX_goal_unique_A03_expeditionary_staff')
pair('JPI_electrical_bureau','JPI_fleet_workshops')
new('JPI_ship_generators',18,11,'JPI_electrical_bureau JPI_fleet_workshops','set_country_flag = JPI_tesla_prototype add_political_power = -15 add_fuel = 5000','GFX_goal_unique_A03_merchant_marine')
parents('JPI_portable_prototype','JPI_electrical_bureau JPI_fleet_workshops');pair('JPI_portable_prototype','JPI_ship_generators')
parents('JPI_quiet_coast','JPI_portable_prototype');parents('JPI_coastal_trials','JPI_ship_generators')
# Either completed technical programme gives actual sailing readiness.
fs['JPI_quiet_coast'][:]=[(k,o,v) for k,o,v in fs['JPI_quiet_coast'] if k!='available']
value(fs['JPI_quiet_coast'],'completion_reward').extend(parse('set_country_flag = JPI_tesla_tested'))
block('JPI_coastal_trials','completion_reward','set_country_flag = JPI_tesla_tested set_country_flag = JPI_tesla_ready add_ideas = JPI_shipboard_power navy_experience = 15 add_equipment_to_stockpile = { type = convoy_1 amount = 10 producer = A03 }')
parents('JPI_scarlet_sails','JPI_quiet_coast JPI_coastal_trials')
# No budget-to-war empty columns: the fleet/logistics steps now begin at sailing readiness.
parents('JPC_batavia_demands','JPI_southern_push');parents('JPL_supply_board','JPI_southern_push')
parents('JPX_sea_institution','JPC_one_war_cabinet');parents('JPF_madeira_table','JPI_japanese_terms')
for fid,x,y in [('JPF_madeira_table',26,7),('JPL_supply_board',28,15),('JPL_medical_rotation',26,16),('JPD_professional_logistics',28,17),('JPC_batavia_demands',22,15),('JPC_one_war_cabinet',22,16),('JPC_borneo_bridgehead',20,17),('JPC_regional_dispatches',24,17),('JPX_sea_institution',32,17),('JPC_hold_until_talks',20,18),('JPC_wtc_mission',24,18),('JPD_ocean_fleet',20,19),('JPC_count_the_cost',22,20),('JPC_oil_promise',12,21),('JPC_defeat_inquest',16,21),('JPC_partial_demobilisation',22,21),('JPC_rebuild_ports',10,22),('JPF_royalty_register',14,22),('JPC_three_heads_again',22,22),('JPD_integrated_staff',28,22),('JPF_civil_budget',16,23),('JPN_north_postwar_audience',20,23),('A03_manage_triple_split',24,23),('A03_constitutional_debate',28,23),('A03_two_faced_colonialism',32,23),('JPD_industrial_power',16,24),('A03_grand_southern_mandate',24,24),('A03_prime_minister_filter',26,24),('A03_direct_imperial_rule',30,24),('A03_imperial_predator',32,24),('JPD_settle_three_heads',22,25),('JPD_reformed_empire',22,26)]:pos(fid,x,y)
new('JPL_forward_workshops',30,16,'JPL_supply_board','add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 500 producer = A03 } add_to_variable = { JPL_garrison_fatigue = 5 } JPL_refresh_effect = yes add_to_variable = { JPF_debt_pressure = 5 } JPF_refresh_effect = yes add_ideas = JPL_repair_network','GFX_goal_unique_A03_standard_rifles')
pair('JPL_medical_rotation','JPL_forward_workshops');parents('JPD_professional_logistics','JPL_medical_rotation JPL_forward_workshops')
# These prerequisites are already guaranteed through the campaign; drawing them
# again creates full-height wires down otherwise empty columns.
parents('JPD_industrial_power','JPF_civil_budget')
parents('JPN_north_postwar_audience','JPC_three_heads_again')
# Remove the unused blank row under the root. Every occupied tier follows the previous one.
for fid,n in fs.items():
 y=int(value(n,'y'))
 if y>0:put(fid,'y',str(y-1))
save('common/national_focus/a03_focus.txt','# Compact Japanese choices: screenshot correction 2026-10-19\n'+dump(t)+'\n')
p='common/ai_strategy_plans/A01_canonical.txt';s=(R/p).read_text();s=s.replace(' JPI_raw_register','').replace(' JPI_unsigned_contracts','');s=s.replace(' JPI_portable_prototype JPI_coastal_trials JPI_quiet_coast',' JPI_portable_prototype JPI_quiet_coast');save(p,s)
print('Applied compact layout and four meaningful choice pairs:',len(fs),'focuses')
