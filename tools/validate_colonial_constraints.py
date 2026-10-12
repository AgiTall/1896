"""Validate actual colonial-pressure scripts using the existing script model."""
import json
import re
import validate_expansion as v

R = v.R
G = R.__class__('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
new_effects = dict((key, body) for key, op, body in v.parse(v.read('common/scripted_effects/A01_colonial_constraints.txt')))
v.effects.update(new_effects)

class ColonialModel(v.Model):
    def __init__(self):
        super().__init__()
        self.state = None
        self.state_flags = {state: set() for state in self.owner}
        self.controller = self.owner.copy()
        self.characters = {val for key, op, val in v.parse(v.read('history/countries/A01 - Placeholder.txt')) if key == 'recruit_character'}
        self.recruited = []
        self.ideas = set()
        self.flags['A01'].add('A01_balance_initialized')
    def condition(self, node, tag):
        results = []
        for key, op, val in node:
            if key == 'is_controlled_by': ok = self.controller[self.state] == val
            elif key == 'has_state_flag': ok = val in self.state_flags[self.state]
            elif key == 'state': ok = self.state == int(val)
            elif key == 'has_character': ok = val in self.characters
            else: ok = super().condition([(key, op, val)], tag)
            results.append(ok)
        return all(results)
    def run(self, node, tag='A01'):
        # Delegate conditionals as complete blocks so the base interpreter
        # preserves the if/else relationship.
        pending = []
        def flush():
            if pending:
                super(ColonialModel, self).run(pending[:], tag)
                pending.clear()
        for key, op, val in node:
            if key in ['every_owned_state', 'set_state_flag', 'recruit_character', 'add_ideas']:
                flush()
                if key == 'every_owned_state':
                    previous = self.state
                    for state, owner in self.owner.items():
                        if owner != tag: continue
                        self.state = state
                        if self.condition(v.value(val, 'limit'), tag):
                            self.run([entry for entry in val if entry[0] != 'limit'], tag)
                    self.state = previous
                elif key == 'set_state_flag': self.state_flags[self.state].add(val)
                elif key == 'recruit_character': self.characters.add(val); self.recruited.append(val)
                else: self.ideas.add(val)
            else: pending.append((key, op, val))
        flush()

m = ColonialModel()
m.run(new_effects['A01_initialize_colonial_constraints_effect'])
m.run(new_effects['A01_initialize_colonial_constraints_effect'])
assert not m.recruited, 'Runtime character recruitment is forbidden by the engine'
assert {'A01_fabius', 'A01_casembroot', 'A01_surya_wirata'} <= m.characters
assert m.ideas == {'A01_agrarian_society'}

m.war = True
m.controller[1024] = 'A03'
m.run(new_effects['A01_japanese_occupation_pressure_effect'])
assert abs(m.bop - (-.05)) < 1e-8
for _ in range(30): m.run(new_effects['A01_japanese_occupation_pressure_effect'])
assert abs(m.bop - (-.05)) < 1e-8, 'Daily occupation drain repeated'
m.controller[1024] = 'A01'; m.run(new_effects['A01_japanese_occupation_pressure_effect'])
m.controller[1024] = 'A03'; m.run(new_effects['A01_japanese_occupation_pressure_effect'])
assert abs(m.bop - (-.05)) < 1e-8, 'Repeated capture charged twice'
m.controller[1055] = 'A03'; m.run(new_effects['A01_japanese_occupation_pressure_effect'])
assert abs(m.bop - (-.15)) < 1e-8
m.owner[1023] = 'A03'; m.controller[1023] = 'A03'
m.run(new_effects['A01_japanese_occupation_pressure_effect'])
assert abs(m.bop - (-.15)) < 1e-8, 'Lease incorrectly charged'
m.owner[1058] = 'A01'; m.controller[1058] = 'A03'; m.state_flags[1058] = set()
m.run(new_effects['A01_japanese_occupation_pressure_effect'])
assert abs(m.bop - (-.4)) < 1e-8

for gate in ['peace', 'resolved', 'admirals']:
    m = ColonialModel(); m.controller[1024] = 'A03'; m.war = gate != 'peace'
    if gate == 'resolved': m.flags['A01'].add('A01_expansion_resolved')
    if gate == 'admirals': m.flags['A01'].add('A01_admirals_seized_power')
    m.run(new_effects['A01_japanese_occupation_pressure_effect'])
    assert m.bop == .15

characters = v.value(v.parse(v.read('common/characters/A01_admirals.txt')), 'characters')
for token in ['A01_fabius', 'A01_casembroot', 'A01_surya_wirata']:
    character = v.value(characters, token)
    assert v.value(character, 'navy_leader') is not None
    assert v.value(v.value(character, 'portraits'), 'army') is not None
    assert 'recruit_character = '+token in v.read('history/countries/A01 - Placeholder.txt')
for key, op, option in v.events['A01_japan.2']:
    if key != 'option': continue
    assert v.value(option, 'hidden_effect') is not None
    assert v.value(option, 'country_event') is None
    assert v.value(option, 'custom_effect_tooltip') is None

idea_tree = v.parse(v.read('common/ideas/A01_colonial_constraints.txt'))
idea = v.value(v.value(v.value(idea_tree, 'ideas'), 'country'), 'A01_agrarian_society')
modifiers = {k: float(val) for k, op, val in v.value(idea, 'modifier')}
docs = (G/'documentation/modifiers_documentation.md').read_text(encoding='utf-8-sig')
vanilla_ideas = '\n'.join(p.read_text(encoding='utf-8-sig', errors='replace') for p in (G/'common/ideas').glob('*.txt'))
for modifier in modifiers:
    # Building-specific speed modifiers are generated from building IDs and
    # omitted from the generic modifier reference; verify vanilla usage too.
    assert '## '+modifier+'\n' in docs or re.search(r'\b'+modifier+r'\s*=', vanilla_ideas), modifier
assert modifiers['production_speed_buildings_factor'] == -.45
assert modifiers['recruitable_population_factor'] == -.35
assert modifiers['recruitable_population'] == -.01
assert .015 + modifiers['recruitable_population'] > 0
assert 1 + modifiers['recruitable_population_factor'] - .30 - .30 > 0, 'Stacked modifiers eliminate all manpower'
assert not (R/'common/decisions/pacific_preparations.txt').exists(), 'Obsolete preparation decisions returned'
for lang in ['russian', 'english']:
    texts = '\n'.join(p.read_text(encoding='utf-8-sig') for p in (R/'localisation'/lang).glob('*.yml'))
    keys = set(re.findall(r'^\s+([^\s:#]+):', texts, re.M))
    assert {'A01_agrarian_society', 'A01_agrarian_society_desc', 'A01_occupation_balance_tt'} <= keys
for path in ['common/ideas/A01_colonial_constraints.txt', 'common/scripted_effects/A01_colonial_constraints.txt', 'common/on_actions/A01_colonial_constraints.txt', 'events/sabah_war.txt']:
    v.parse(v.read(path))
report = {'status': 'passed', 'checks': ['Three naval roles, valid portrait slots and history-only recruitment', 'Speech choices expose no event or policy effect tooltip', 'Agrarian modifiers exist in installed game documentation', 'Stacked manpower penalties remain below 100 percent under volunteer law', 'Obsolete preparation decisions removed', 'Occupation penalty for ordinary states, Sabah and Batavia', 'No daily or repeated-capture penalty farming', 'No penalty for lease, peace, resolved war or Admirals government', 'RU/EN labels and balanced changed scripts'], 'engine_campaign_test': 'Not run; these are static checks and execution in a script model.'}
(R/'tools/colonial_constraints_validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
