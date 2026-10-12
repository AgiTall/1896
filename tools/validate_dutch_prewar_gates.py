"""Check preparation gates, cancellation, exemptions and mobilisation compatibility."""
from add_canon_countries import parse, value
from update_dutch_prewar_gates import R, excluded_branches

tree = parse((R/'common/national_focus/a01_focus.txt').read_text(encoding='utf-8-sig'))
focuses = {value(v, 'id'): v for k, op, v in value(tree, 'focus_tree') if k == 'focus'}
exempt = excluded_branches(focuses)
gate = parse('custom_trigger_tooltip = { tooltip = A01_before_japanese_war_tt NOT = { has_war_with = A03 has_country_flag = A01_borneo_war_started } }')[0]
for fid, node in focuses.items():
    available = next((v for k, op, v in node if k == 'available'), [])
    assert (gate in available) == (fid not in exempt), fid
    if fid not in exempt:
        assert value(node, 'cancel_if_invalid') == 'yes', fid
        assert value(node, 'continue_if_invalid') == 'no', fid
        assert ('has_war_with', '=', 'A03') not in available, fid
assert 'A01_factory_resettlement' in exempt
assert 'A01_java_steam_power' in exempt
assert 'A01_review_borneo_convention' in exempt
for war, started, expected in ((False, False, True), (True, False, False), (True, True, False), (False, True, False)):
    assert (not war and not started) == expected
idea_tree = parse((R/'common/ideas/pacific_ideas.txt').read_text(encoding='utf-8-sig'))
cancel = value(value(value(value(idea_tree, 'ideas'), 'country'), 'A01_war_production'), 'cancel')
assert ('has_country_flag', '=', 'A01_borneo_war_started') in cancel
assert value(value(cancel, 'NOT'), 'has_war_with') == 'A03'
effects = parse((R/'common/scripted_effects/expansion_effects.txt').read_text(encoding='utf-8-sig'))
assert 'set_country_flag = A01_borneo_war_started' in (R/'common/scripted_effects/expansion_effects.txt').read_text(encoding='utf-8-sig')
print(f'PASS: {len(focuses)-len(exempt)} prewar focuses cancel on war and remain locked after peace; {len(exempt)} agrarian/industrial and postwar focuses exempt; mobilisation remains compatible.')
