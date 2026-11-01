"""Static references plus execution of the actual scripted outcome branches.

The small interpreter models flags, scopes, mission clocks and state transfers;
it does not model HOI4 combat or replace an engine campaign test.
"""
from pathlib import Path
import copy
import json
import re
from datetime import date

R = Path(__file__).resolve().parents[1]

def read(path):
    return (R / path).read_text(encoding='utf-8-sig')

def parse(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[{}=<>]|[^\s{}=<>]+', re.sub(r'#[^\n]*', '', text))
    pos = 0
    def block(nested=False):
        nonlocal pos
        result = []
        while pos < len(tokens) and tokens[pos] != '}':
            key = tokens[pos].strip('"'); pos += 1
            if pos < len(tokens) and tokens[pos] in ['=', '<', '>']:
                op = tokens[pos]; pos += 1
                if tokens[pos] == '{':
                    pos += 1; value = block(True)
                else:
                    value = tokens[pos].strip('"'); pos += 1
                result.append((key, op, value))
            else:
                result.append((key, None, None))
        if nested:
            assert pos < len(tokens) and tokens[pos] == '}', 'Unbalanced script'
            pos += 1
        return result
    result = block()
    assert pos == len(tokens), 'Unexpected closing brace'
    return result

def value(node, name, default=None):
    return next((v for k, op, v in node if k == name), default)

paths = [
    'common/scripted_effects/expansion_effects.txt',
    'common/scripted_effects/borneo_war_effects.txt',
    'common/scripted_effects/A01_ludolf_effects.txt',
    'common/decisions/A01_inevitable_conflict.txt',
    'common/decisions/A03_japanese_expansion.txt',
    'common/decisions/A03_southern_preparations.txt',
    'common/on_actions/A01_borneo_story.txt',
    'events/japanese_expansion.txt',
    'events/A01_japan_events.txt',
    'events/A01_ludolf_story.txt',
]
trees = {p: parse(read(p)) for p in paths}
effects = {k: v for p in paths[:3] for k, op, v in trees[p]}
effects.update({k: v for k, op, v in parse(read('common/scripted_effects/A01_federal_recovery.txt'))})
effects.update({k: v for k, op, v in parse(read('common/scripted_effects/JPS_calendar_clocks.txt'))})
borneo_trigger = dict((k, v) for k, op, v in parse(read('common/scripted_triggers/A03_borneo_triggers.txt')))['A03_controls_borneo_province']
borneo_provinces = {int(v) for k, op, v in value(borneo_trigger, 'OR') if k == 'controls_province'}
expected_borneo = set()
for state in [333, 334, 1022, 1023, 1024, 1055, 1059]:
    state_path = next((R / 'history/states').glob(f'{state}*.txt'))
    state_tree = value(parse(state_path.read_text(encoding='utf-8-sig')), 'state')
    expected_borneo.update(int(k) for k, op, v in value(state_tree, 'provinces'))
assert borneo_provinces == expected_borneo, 'Victory trigger must cover every Borneo province and no others'
decisions = {k: v for p in paths[3:6] for category, op, body in trees[p] for k, op, v in body}
events = {value(body, 'id'): body for p in paths[7:] for k, op, body in trees[p] if k == 'country_event'}

class Model:
    def __init__(self):
        self.now = date(1893,1,1)
        self.flags = {tag: set() for tag in ['A01', 'A03']}
        self.missions = {tag: {} for tag in self.flags}
        self.bop = .15
        self.war = False
        self.controlled_provinces = set()
        self.owner = {1023: 'A01', 1024: 'A01', 1055: 'A01', 647: 'A03'}
        self.notifications = []
        self.rights = set()
    def condition(self, node, tag):
        result = []
        for key, op, val in node:
            if key in self.flags: ok = self.condition(val, key)
            elif key == 'OR': ok = any(self.condition([entry], tag) for entry in val)
            elif key in ['AND', 'hidden_trigger']: ok = self.condition(val, tag)
            elif key == 'NOT': ok = not self.condition(val, tag)
            elif key == 'always': ok = val == 'yes'
            elif key == 'has_country_flag': ok = val in self.flags[tag]
            elif key == 'country_exists': ok = val in self.flags
            elif key == 'has_war_with': ok = self.war
            elif key == 'has_active_mission': ok = val in self.missions[tag]
            elif key == 'A03_controls_borneo_province': ok = self.condition(borneo_trigger, tag)
            elif key == 'controls_province': ok = tag == 'A03' and int(val) in self.controlled_provinces
            elif key == 'owns_state': ok = self.owner.get(int(val)) == tag
            elif key == 'has_dlc': ok = False
            elif key == 'power_balance_value':
                _, comparison, threshold = next(entry for entry in val if entry[0] == 'value')
                ok = self.bop < float(threshold) if comparison == '<' else self.bop > float(threshold)
            elif key == 'tag': ok = tag == val
            elif key == 'date':
                d=date(*map(int,val.split('.')));ok=self.now>d if op=='>' else self.now<d
            else: raise AssertionError(('Unmodelled condition', key))
            result.append(ok)
        return all(result)
    def run(self, node, tag='A01'):
        previous_if = None
        for key, op, val in node:
            if key == 'if':
                previous_if = self.condition(value(val, 'limit'), tag)
                if previous_if: self.run([entry for entry in val if entry[0] != 'limit'], tag)
            elif key == 'else':
                assert previous_if is not None
                if not previous_if: self.run(val, tag)
            elif key in self.flags: self.run(val, key)
            elif key in effects: self.run(effects[key], tag)
            elif key == 'set_country_flag': self.flags[tag].add(value(val, 'flag') if isinstance(val, list) else val)
            elif key == 'clr_country_flag': self.flags[tag].discard(val)
            elif key == 'activate_mission': self.missions[tag][val] = int(value(decisions[val], 'days_mission_timeout'))
            elif key == 'remove_mission': self.missions[tag].pop(val, None)
            elif key == 'add_days_mission_timeout':
                mission = value(val, 'mission')
                assert mission in self.missions[tag], ('Missing peer mission', tag, mission)
                self.missions[tag][mission] = max(0, self.missions[tag][mission] + int(value(val, 'days')))
            elif key == 'white_peace': self.war = False
            elif key == 'transfer_state': self.owner[int(val)] = tag
            elif key == 'add_power_balance_value': self.bop += float(value(val, 'value'))
            elif key == 'country_event': self.notifications.append((tag, value(val, 'id')))
            elif key == 'give_resource_rights': self.rights.add(int(value(val, 'state')))
            elif key == 'remove_resource_rights': self.rights.discard(int(val))
            elif key.isdigit(): pass  # Borneo Convention resource-rights scopes are checked separately.
            elif key in ['navy_experience', 'add_command_power']: pass
            elif key in ['set_technology', 'load_oob', 'create_equipment_variant', 'add_equipment_to_stockpile', 'add_fuel', 'add_timed_idea', 'remove_ideas', 'add_ideas', 'add_stability', 'add_war_support', 'add_political_power', 'add_to_variable', 'clamp_variable', 'diplomatic_relation', 'set_variable', 'set_power_balance', 'delete_unit_template_and_units']: pass
            else: raise AssertionError(('Unmodelled effect', key))

def preparation():
    m = Model()
    m.flags['A01'].update(['A01_balance_initialized', 'A01_refused_japanese_ultimatum'])
    m.run(effects['JPS_restore_clocks_effect'])
    m.run(effects['A01_begin_expansion_preparations_effect'])
    return m

def assert_clocks(m, days):
    assert m.missions['A01']['A01_japanese_invasion_countdown'] == days
    assert m.missions['A03']['A03_japanese_invasion_countdown'] == days

refusal = next(v for k,o,v in events['A01_japan.1'] if k == 'option')
assert ('A01_begin_expansion_preparations_effect', '=', 'yes') not in refusal
m = Model(); m.run([e for e in refusal if e[0] != 'name']); assert not m.missions['A01']
m = preparation(); assert_clocks(m, 120)
m.run(effects['A01_begin_expansion_preparations_effect']); assert_clocks(m, 120)
for decision, days in [('A03_charter_transports', 120), ('A03_advance_coaling', 120), ('A03_final_sailing_orders', 120)]:
    m.run(value(decisions[decision], 'complete_effect'), 'A03'); assert_clocks(m, days)
# The narrative focus cannot alter the canonical calendar.
focuses = parse(read('common/national_focus/a03_focus.txt'))
tree = value(focuses, 'focus_tree')
campaign_focus = next(body for key, op, body in tree if key == 'focus' and value(body, 'id') == 'JPC_batavia_demands')
m.run(value(campaign_focus, 'completion_reward'), 'A03'); assert_clocks(m, 120)
m = preparation()
for decision in ['A03_charter_transports', 'A03_advance_coaling', 'A03_final_sailing_orders']:
    m.run(value(decisions[decision], 'complete_effect'), 'A03')
for decision, days in [('A01_lease_brunei', 120), ('A01_rubber_concession', 120), ('A01_supply_concession', 120)]:
    m.run(value(decisions[decision], 'complete_effect')); assert_clocks(m, days)
assert m.owner[1023] == 'A03'
m.run(value(events['expansion.13'], 'immediate'))
assert m.owner[1023] == 'A01' and 'A01_brunei_lease_active' not in m.flags['A01']
m.run(value(events['expansion.12'], 'immediate')); assert 1055 not in m.rights

# An early war defers the lease return; a later treaty must preserve its
# permanent transfer and permanent resource concessions.
m = preparation(); m.run(value(decisions['A01_lease_brunei'], 'complete_effect'))
m.war = True; m.run(value(events['expansion.13'], 'immediate'))
assert m.owner[1023] == 'A03' and 'A01_brunei_lease_active' in m.flags['A01']
m.war = False; m.flags['A01'].add('A01_borneo_treaty')
m.run(value(events['expansion.13'], 'immediate'))
assert m.owner[1023] == 'A03' and 'A01_brunei_lease_active' not in m.flags['A01']
m.rights.add(1055); m.run(value(events['expansion.12'], 'immediate'))
assert 1055 in m.rights

outcomes = []
for controlled in [set(), {1}] + [{province} for province in sorted(borneo_provinces)] + [borneo_provinces]:
    occupied = bool(controlled & borneo_provinces)
    m = preparation(); m.war = True; m.controlled_provinces = set(controlled)
    m.run(effects['A01_start_expansion_campaign_effect'])
    assert m.missions == {'A01': {'A01_japanese_expansion': 1006}, 'A03': {'A03_japanese_expansion': 1006}}
    m.run(value(decisions['A01_japanese_expansion'], 'timeout_effect'))
    first = copy.deepcopy(m.__dict__)
    m.run(value(decisions['A03_japanese_expansion'], 'timeout_effect'), 'A03')
    assert first == m.__dict__, 'Second peer callback applied the outcome twice'
    assert not m.war and all(not missions for missions in m.missions.values())
    if occupied:
        assert 'A01_borneo_treaty' in m.flags['A01'] and m.owner[1024] == 'A03'
        assert all(m.owner[state] == 'A03' for state in [1023, 1059, 333])
        assert m.owner[1022] == 'A01'
        assert 'A03_borneo_defeat' not in m.flags['A03']
    else:
        assert 'A01_defended_sabah' in m.flags['A01'] and 'A03_borneo_defeat' in m.flags['A03']
        assert 'A01_borneo_treaty' not in m.flags['A01'] and m.owner[1024] == 'A01'
        assert m.bop > .15
    outcomes.append('Japanese victory' if occupied else 'Dutch victory (no Borneo foothold)')

# Losing the last foothold before the deadline restores a Dutch victory.
m = preparation(); m.war = True; m.controlled_provinces = {min(borneo_provinces)}
m.run(effects['A01_start_expansion_campaign_effect'])
m.controlled_provinces.clear()
m.run(value(decisions['A01_japanese_expansion'], 'timeout_effect'))
assert 'A03_borneo_defeat' in m.flags['A03']

# Author confirmed that a surviving Brunei lease counts as control, even
# without any battle. The model records the province controller explicitly.
brunei_state = value(parse(next((R / 'history/states').glob('1023*.txt')).read_text(encoding='utf-8-sig')), 'state')
brunei_province = int(value(brunei_state, 'provinces')[0][0])
m = preparation()
m.run(value(decisions['A01_lease_brunei'], 'complete_effect'))
m.controlled_provinces = {brunei_province}
m.war = True
m.run(effects['A01_start_expansion_campaign_effect'])
m.run(value(decisions['A01_japanese_expansion'], 'timeout_effect'))
assert 'A01_borneo_treaty' in m.flags['A01']
assert m.owner[1023] == 'A03' and 'A03_borneo_defeat' not in m.flags['A03']
outcomes = sorted(set(outcomes))

# Pressure is possible only during the explicit dismissal hearings.
for balance, resolved, expected in [(.8, False, False), (.15, False, False), (0, False, False), (-.2, False, True), (-.8, True, False)]:
    m = Model(); m.bop = balance; m.flags['A01'].add('A01_borneo_treaty')
    m.flags['A01'].add('A01_dismissal_debate_active')
    if resolved: m.flags['A01'].add('A01_ludolf_crisis_resolved')
    assert m.condition(value(events['ludolf.33'], 'trigger'), 'A01') == expected
assert value(events['ludolf.20'], 'trigger') == [('always', '=', 'no')]
assert not any(value(opt, 'name') == 'ludolf.33.d' for key, op, opt in events['ludolf.33'] if key == 'option')

all_scripts = '\n'.join(read(p) for p in paths)
expansion_ids = {value(body, 'id') for key, op, body in trees['events/japanese_expansion.txt'] if key == 'country_event'}
references = set(re.findall(r'country_event\s*=\s*\{\s*id\s*=\s*(expansion\.\d+)', all_scripts))
assert references <= expansion_ids, ('Undefined expansion event', references-expansion_ids)
for mission in re.findall(r'(?:activate_mission|remove_mission)\s*=\s*(\w+)', all_scripts):
    assert mission in decisions, ('Undefined mission', mission)
all_loc = {}
for lang in ['russian', 'english']:
    loc = '\n'.join(p.read_text(encoding='utf-8-sig') for p in (R/'localisation'/lang).glob('*.yml'))
    all_loc[lang] = set(re.findall(r'^\s+([^\s:#]+):', loc, re.M))
    for event in events.values():
        ident = value(event, 'id')
        if not ident.startswith('expansion.'): continue
        for key in ['title', 'desc']:
            if value(event, key): assert value(event, key) in all_loc[lang]
    for ident in decisions:
        assert ident in all_loc[lang] and ident+'_desc' in all_loc[lang], (lang, ident)

report = {'status': 'passed', 'checks': ['Balanced changed scripts and mission references', 'Diplomatic refusal does not start or reset independent preparation', 'Both preparation clocks start once and stay synchronised across all concessions and naval decisions', 'Lease return and temporary resource-rights expiry', 'Both wartime missions start together', 'Deadline outcomes and duplicate callback protection', 'Queued pressure suppressed at neutral or strong Ludolf balance', 'Old unconditional peace offer disabled', 'Russian and English mission, decision and event labels'], 'outcomes': outcomes, 'engine_campaign_test': 'Not run; script model is not the HOI4 engine.'}
(R/'tools/expansion_validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))

