"""Check reachable reform outcomes, real settlement gates and permanent rewards."""
from itertools import product
from pathlib import Path
import re
from validate_story_systems import Model, value, parse, fs, ideas, walk
from develop_japan_branches import NEW, POSITIONS, B, R

assert set(fs)==set(POSITIONS)
assert len(fs)==104
baseline={value(n,'id'):n for k,o,n in value(parse((B/'common/national_focus/a03_focus.txt').read_text(encoding='utf-8-sig')),'focus_tree') if k=='focus'}
for fid,node in baseline.items():
    # Preserve every old reward, duration, availability gate and exclusive choice.
    for key in ['completion_reward','cost','available','mutually_exclusive']:
        assert value(node,key)==value(fs[fid],key),(fid,key)

pairs=[('JPF_public_accounts','JPF_small_subscription'),
       ('JPN_north_civilian_holds','JPN_north_emergency_calendar'),
       ('JPL_convoy_timetable','JPL_names_and_units'),
       ('A03_prime_minister_filter','A03_direct_imperial_rule')]
for picks in product((0,1),repeat=4):
    excluded={pair[1-pick] for pair,pick in zip(pairs,picks)}
    excluded.update({'JPX_land','JPX_trade','JPX_kami','JPX_throne'})
    for result in ['victory','defeat']:
        blocked=excluded|({'JPC_defeat_inquest'} if result=='victory' else {'JPC_oil_promise','JPC_rebuild_ports','JPF_royalty_register'})
        done=set()
        for _ in range(len(fs)):
            for fid,n in fs.items():
                if fid in blocked:continue
                groups=[{v for k,o,v in group if k=='focus'} for k,o,group in n if k=='prerequisite']
                if all(group&done for group in groups):done.add(fid)
        assert set(NEW)<=done,(picks,result,set(NEW)-done)

def gate(fid):
    return [x for x in value(value(fs[fid],'available'),'custom_trigger_tooltip') if x[0]!='tooltip']
m=Model()
assert not m.test(gate('JPD_sustainable_credit'),'A03')
m.flags['A03'].add('JPF_civil_budget')
assert not m.test(gate('JPD_sustainable_credit'),'A03'),'Focus alone must not fake debt settlement'
m.effect('JPF_close_ledger_effect')
assert m.test(gate('JPD_sustainable_credit'),'A03')
assert not m.test(gate('JPD_settle_three_heads'),'A03')
m.flags['A03'].update({'JPN_north_compact_ready','JPC_north_signed'})
assert not m.test(gate('JPD_settle_three_heads'),'A03'),'A draft compact is not a signed compact'
m.wars.clear()
m.vars['A03'].update(JPN_north_trust=70,JPN_north_fleet_irritation=20)
m.effect('JPN_north_sign_compact_effect')
assert m.test(gate('JPD_settle_three_heads'),'A03')

m.ideas['A03'].update({'JPC_three_heads','JPC_returned_split','A03_triple_split_balance','JPC_monopoly','JPN_north_limited_compact'})
m.run(value(fs['JPD_settle_three_heads'],'completion_reward'))
assert not {'JPC_three_heads','JPC_returned_split','A03_triple_split_balance'}&m.ideas['A03']
assert {'JPD_settled_government','JPC_monopoly','JPN_north_limited_compact'}<=m.ideas['A03']
assert 'A08' in m.tags and 'JPD_politics_reformed' in m.flags['A03']
m.ideas['A03'].add('JPD_standardized_industry')
reward=value(fs['JPD_industrial_power'],'completion_reward')
assert value(reward,'add_research_slot')=='1'
m.run([x for x in reward if x[0]!='add_research_slot'])
assert 'JPD_industrial_economy' in m.ideas['A03'] and 'JPD_standardized_industry' not in m.ideas['A03']
m.ideas['A03'].add('JPC_joint_staff')
m.run(value(fs['JPD_integrated_staff'],'completion_reward'))
assert 'JPD_permanent_staff' in m.ideas['A03'] and 'JPC_joint_staff' not in m.ideas['A03']

docs=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md').read_text(encoding='utf-8-sig')
for fid,n in ideas.items():
    if fid.startswith('JPD_'):
        for key,op,v in value(n,'modifier',[]):
            assert '## '+key+'\n' in docs or (key=='production_speed_dockyard_factor' and 'production_speed_<Building>_factor' in docs),key
print('PASS: prerequisite reachability for all nine milestones in 32 policy/war-result combinations; real debt/north settlement gates; reform rewards replace crisis spirits while preserving concessions and northern autonomy; modifiers documented. No combat or full campaign simulation.')
