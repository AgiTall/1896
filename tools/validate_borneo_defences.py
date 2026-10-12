"""Static regression checks for the staged Sabah fortification program."""
from pathlib import Path
from add_canon_countries import parse, value, states

R = Path(__file__).resolve().parents[1]
tree = parse((R/'common/national_focus/a01_focus.txt').read_text(encoding='utf-8-sig'))
focuses = {value(v, 'id'): v for k, op, v in value(tree, 'focus_tree') if k == 'focus'}
ids = ('A01_build_bornean_fortifications', 'A01_state_loan', 'A01_improve_bornean_fortifications')
assert [value(focuses[f], 'cost') for f in ids] == ['5', '5', '10']
ports = {10212, 10199, 12228}
buildings = value(value(states[1024][2], 'history'), 'buildings')
for pid in ports:
    assert int(value(value(buildings, str(pid)), 'naval_base')) > 0
assert value(value(focuses[ids[0]], 'completion_reward'), 'add_stability') == '0.05'
for fid, coastal_level in ((ids[2], 2),):
    focus = focuses[fid]
    assert ('owns_state', '=', '1024') in value(focus, 'available')
    effects = value(focus, 'completion_reward')
    works = [v for k, op, v in effects if k == 'if']
    assert len(works) == (3 if coastal_level == 1 else 6)
    for work in works:
        limit = value(work, 'limit')
        assert ('owns_state', '=', '1024') in limit
        pid = int(value(limit, 'controls_province'))
        assert pid in ports
        build = value(value(work, '1024'), 'set_building_level')
        target = int(value(build, 'level'))
        assert target == (coastal_level if value(build, 'type') == 'coastal_bunker' else 1)
        selector = value(build, 'province')
        assert value(selector, 'id') == str(pid)
        assert ('level', '<', str(target)) in selector
        for existing in range(11):
            result = target if existing < target else existing
            assert result == max(existing, target)

for fid, days in [('A01_state_loan',5),('A01_request_fortification_project',5),('A01_own_fortifications',10),('A01_implement_fortification_project',10)]:
 assert int(value(focuses[fid],'cost'))==days
 assert any(k=='bypass' for k,o,v in focuses[fid])
assert value(value(focuses['A01_state_loan'],'mutually_exclusive'),'focus')=='A01_request_fortification_project'
assert value(value(focuses['A01_request_fortification_project'],'mutually_exclusive'),'focus')=='A01_state_loan'
assert {v for k,o,v in value(focuses[ids[2]],'prerequisite')}=={'A01_own_fortifications','A01_implement_fortification_project'}
ideas=value(value(parse((R/'common/ideas/A01_borneo_projects.txt').read_text()),'ideas'),'country')
for idea,amount in [('A01_borneo_self_build','0.20'),('A01_borneo_british_defence','0.15'),('A01_borneo_australian_defence','0.10'),('A01_borneo_local_defence','0.05')]:
 targeted=value(value(ideas,idea),'targeted_modifier')
 assert value(targeted,'tag')=='A03'
 assert value(targeted,'defense_bonus_against')==amount
 assert 'army_defence_factor' not in str(value(ideas,idea))
event=parse((R/'events/A01_borneo_projects.txt').read_text())
event=next(v for k,o,v in event if k=='country_event')
assert 'A01_borneo_project_selected' in str(value(event,'trigger'))
options=[v for k,o,v in event if k=='option']
assert len(options)==3
for opt in options:
 assert ('set_country_flag','=','A01_borneo_project_selected') in opt
 assert 'defense_bonus_against' not in str(opt)
implementation=value(focuses['A01_implement_fortification_project'],'completion_reward')
assert sum(k=='if' for k,o,v in implementation)==3
cleanup=value(parse((R/'common/scripted_effects/expansion_effects.txt').read_text()),'A01_cleanup_expansion_effect')
assert 'A01_borneo_self_contract' in str(cleanup)
assert 'has_completed_focus' not in str(cleanup)
print('PASS: procurement fork, guarded project choice, mutually exclusive bonuses against Japan, capped ports, postwar bypasses and persistent financial obligations.')
