"""Regression checks for the two Dutch courses and independent Japanese ultimatum."""
from add_canon_countries import parse, value
from update_pacific_rivalry import R, read, event, option
tree=parse(read('common/national_focus/a01_focus.txt'))
fs={value(v,'id'):v for k,o,v in value(tree,'focus_tree') if k=='focus'}
courses={'A01_last_chance_to_negotiate','A01_direct_rivalry'}
for fid,stability,balance in [('A01_last_chance_to_negotiate','0.05','-0.10'),('A01_direct_rivalry','-0.05','0.10')]:
 n=fs[fid];reward=value(n,'completion_reward')
 assert value(reward,'add_stability')==stability
 assert value(value(reward,'add_power_balance_value'),'value')==balance
 assert value(value(n,'mutually_exclusive'),'focus') in courses-{fid}
assert {v for k,o,v in value(fs['A01_direct_rivalry'],'prerequisite')}=={'A01_strengthen_ludolfs_power','A01_admirals_council_coup'}
naval_requirements=[{v for k,o,v in body if k=='focus'} for key,op,body in fs['A01_direct_naval_rule'] if key=='prerequisite']
assert {'A01_admirals_council_coup'} in naval_requirements
assert {'A01_direct_rivalry'} in naval_requirements
assert int(value(fs['A01_direct_naval_rule'],'y')) > int(value(fs['A01_direct_rivalry'],'y'))
for fid in ['A01_dutch_literacy','A01_knil_reform','A01_build_bornean_fortifications','A01_pacific_settlement']:
 assert {v for k,o,v in value(fs[fid],'prerequisite')}==courses, fid
 requirements=[{v for k,o,v in body if k=='focus'} for key,op,body in fs[fid] if key=='prerequisite']
 assert {'A01_strengthen_ludolfs_power'} in requirements, fid
assert value(value(fs['A01_wtc_oil_and_rubber_offer'],'prerequisite'),'focus') == 'A01_java_steam_power'
assert value(value(fs['A01_lone_wolf_path'],'prerequisite'),'focus') == 'A01_constitution'
decisions=value(parse(read('common/decisions/A01_inevitable_conflict.txt')),'A01_inevitable_conflict_category')
assert not any(k=='A01_begin_island_defence' for k,o,v in decisions)
events=parse(read('events/pacific_diplomacy.txt'))
for ident,name in [('pacific.1','pacific.1.b'),('pacific.5','pacific.5.a')]:
 response=option(event(events,ident),name)
 assert 'A01_begin_expansion_preparations_effect' not in str(response)
canonical=parse(read('events/JPC_canonical.txt'))
refusal=option(event(canonical,'japan_canon.5'),'japan_canon.5.o0')
assert 'A03_start_southern_war_effect' in str(refusal)
assert 'A01_begin_expansion_preparations_effect' not in str(refusal)
assert 'A01_island_defence_started' in str(refusal)
ult=value(parse(read('common/national_focus/a03_focus.txt')),'focus_tree')
ult=next(v for k,o,v in ult if k=='focus' and value(v,'id')=='JPC_batavia_demands')
assert 'has_completed_focus' not in str(value(ult,'available'))
print('PASS: mutually exclusive courses, opposite rewards, coup access, shared OR prerequisites, independent preparation, no manual decision, independent immediate-war ultimatum.')
