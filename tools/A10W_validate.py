"""Validate the real WTP branch and execute its diplomatic guards in a bounded model.

This does not emulate combat, autonomy AI, localization layout, or the game engine.
"""
from pathlib import Path
from collections import defaultdict
import json
import re
from add_canon_countries import parse

ROOT = Path(__file__).resolve().parents[1]
GAME = Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')


def read(path):
    return path.read_text(encoding='utf-8-sig')


def value(node, key, default=None):
    return next((v for k, _, v in node if k == key), default)


def walk(node):
    for k, op, v in node:
        yield k, op, v
        if isinstance(v, list):
            yield from walk(v)


effects = dict((k, v) for stem in ('A10W_paths', 'WTC_credit')
               for k, _, v in parse(read(ROOT / f'common/scripted_effects/{stem}.txt')))
triggers = dict((k, v) for k, _, v in parse(read(ROOT / 'common/scripted_triggers/A10W_paths.txt')))
events = dict((value(v, 'id'), v) for k, _, v in parse(read(ROOT / 'events/A10W_paths.txt')) if k == 'country_event')


class World:
    def __init__(self):
        self.tags = {'A10', 'A04', 'A02', 'PVI'}
        self.flags = defaultdict(set)
        self.variables = defaultdict(dict)
        self.ideas = defaultdict(set)
        self.subject = {}
        self.faction = {}
        self.faction_leaders = {}
        self.wars = set()
        self.capitulated = set()
        self.queue = []
        self.audit = []
        self.territory = {'A10': {1084, 624}, 'A04': {697}}
        self.capital = {'A10': 1084, 'A04': 697}

    def faction_members(self, tag):
        return {t for t, f in self.faction.items() if f == self.faction.get(tag)} if tag in self.faction else set()

    def check(self, node, tag='A10'):
        answers = []
        for key, op, v in node:
            if key in ('A10', 'A04', 'A02', 'PVI'):
                answer = key in self.tags and self.check(v, key)
            elif key in triggers:
                answer = self.check(triggers[key], tag) == (v == 'yes')
            elif key in ('AND', 'hidden_trigger'):
                answer = self.check(v, tag)
            elif key == 'OR':
                answer = any(self.check([n], tag) for n in v)
            elif key == 'NOT':
                answer = not self.check(v, tag)
            elif key == 'always':
                answer = v == 'yes'
            elif key == 'tag':
                answer = tag == v
            elif key == 'country_exists':
                answer = v in self.tags
            elif key == 'exists':
                answer = (tag in self.tags) == (v == 'yes')
            elif key == 'has_country_flag':
                answer = v in self.flags[tag]
            elif key == 'has_global_flag':
                answer = False
            elif key == 'has_idea':
                answer = v in self.ideas[tag]
            elif key == 'has_capitulated':
                answer = (tag in self.capitulated) == (v == 'yes')
            elif key == 'is_subject':
                answer = (tag in self.subject) == (v == 'yes')
            elif key == 'is_subject_of':
                answer = self.subject.get(tag) == v
            elif key == 'has_war_with':
                answer = frozenset((tag, v)) in self.wars
            elif key == 'has_war':
                answer = any(tag in w for w in self.wars) == (v == 'yes')
            elif key == 'is_in_faction':
                answer = (tag in self.faction) == (v == 'yes')
            elif key == 'is_faction_leader':
                answer = (self.faction_leaders.get(self.faction.get(tag)) == tag) == (v == 'yes')
            elif key == 'is_in_faction_with':
                answer = tag in self.faction and self.faction[tag] == self.faction.get(v)
            elif key == 'num_faction_members':
                answer = len(self.faction_members(tag)) < int(v) if op == '<' else len(self.faction_members(tag)) > int(v)
            elif key == 'any_subject_country':
                answer = any(self.check(v, child) for child, master in self.subject.items() if master == tag)
            elif key in ('owns_state', 'controls_state'):
                answer = int(v) in self.territory[tag]
            elif key == 'check_variable':
                vk, vo, vv = v[0]
                amount = self.variables[tag].get(vk, 0)
                answer = {'<': amount < float(vv), '>': amount > float(vv), '=': amount == float(vv)}[vo]
            else:
                raise AssertionError(('unmodeled trigger', key))
            answers.append(answer)
        return all(answers)

    def run(self, node, tag='A10'):
        previous = False
        for key, _, v in node:
            if key == 'if':
                previous = self.check(value(v, 'limit', []), tag)
                if previous:
                    self.run([n for n in v if n[0] != 'limit'], tag)
            elif key == 'else':
                if not previous:
                    self.run(v, tag)
            elif key in ('A10', 'A04', 'A02', 'PVI'):
                if key in self.tags:
                    self.run(v, key)
            elif key in effects:
                self.run(effects[key], tag)
            elif key == 'set_country_flag':
                self.flags[tag].add(value(v, 'flag') if isinstance(v, list) else v)
            elif key == 'clr_country_flag':
                self.flags[tag].discard(v)
            elif key == 'set_variable':
                vk, _, amount = v[0]
                self.variables[tag][vk] = float(amount)
            elif key == 'add_to_variable':
                vk, _, amount = v[0]
                self.variables[tag][vk] = self.variables[tag].get(vk, 0) + float(amount)
            elif key == 'clamp_variable':
                var = value(v, 'var')
                self.variables[tag][var] = max(float(value(v, 'min')), min(float(value(v, 'max')), self.variables[tag].get(var, 0)))
            elif key == 'add_ideas':
                self.ideas[tag].add(v)
            elif key == 'remove_ideas':
                self.ideas[tag].discard(v)
            elif key == 'add_timed_idea':
                self.ideas[tag].add(value(v, 'idea'))
            elif key == 'country_event':
                self.queue.append((tag, value(v, 'id')))
            elif key == 'set_autonomy':
                assert tag != value(v, 'target')
                self.subject[value(v, 'target')] = tag
                self.audit.append((key, tag, value(v, 'target')))
            elif key == 'dismantle_faction':
                members = self.faction_members(tag)
                assert members == {tag}, ('attempted to dissolve nonempty faction', members)
                self.faction_leaders.pop(self.faction.pop(tag))
                self.audit.append((key, tag))
            elif key == 'add_to_faction':
                assert tag in self.faction
                self.faction[v] = self.faction[tag]
            elif key == 'set_capital':
                state = int(value(v, 'state'))
                assert state in self.territory[tag]
                self.capital[tag] = state
            elif key in ('add_stability', 'add_war_support', 'add_political_power', 'create_country_leader',
                         'set_politics', 'set_cosmetic_tag', 'custom_effect_tooltip', 'name', 'ai_chance', 'trigger'):
                pass
            else:
                raise AssertionError(('unmodeled effect', key))

    def effect(self, name, tag='A10'):
        self.run(effects[name], tag)

    def choose(self, event_id, suffix, tag='A04'):
        event = events[event_id]
        assert self.check(value(event, 'trigger', []), tag)
        option = next(v for k, _, v in event if k == 'option' and value(v, 'name') == event_id + '.' + suffix)
        assert self.check(value(option, 'trigger', []), tag)
        self.run(option, tag)


def prepared(path):
    world = World()
    world.effect('A10W_initialize_effect')
    world.flags['A10'].update(('A10W_oath_accepted', 'A10W_' + path + '_selected'))
    return world


def validate():
    checks = []
    w = World()
    w.effect('A10W_request_oath_effect')
    assert 'A10W_oath_pending' in w.flags['A10']
    w.choose('A10W_path.1', 'a')
    assert 'A10W_oath_accepted' in w.flags['A10'] and 'A10W_oath_pending' not in w.flags['A10']
    assert not w.subject
    checks.append('Recognized oath preserves sovereignty and clears pending state')
    w = World()
    w.effect('A10W_request_oath_effect')
    w.choose('A10W_path.1', 'b')
    assert 'A10W_oath_refused' in w.flags['A10'] and not w.subject
    checks.append('Explicit oath refusal leaves a playable sovereign council')
    for cause in ('absent', 'war', 'capitulated'):
        w = World()
        if cause == 'absent':
            w.tags.discard('A04')
        elif cause == 'war':
            w.wars.add(frozenset(('A10', 'A04')))
        else:
            w.capitulated.add('A04')
        w.effect('A10W_request_oath_effect')
        assert 'A10W_oath_refused' in w.flags['A10'] and 'A10W_oath_pending' not in w.flags['A10']
        checks.append('Oath fallback with Chamber ' + cause)
    w = World()
    w.effect('A10W_request_oath_effect')
    w.run(value(events['A10W_path.4'], 'immediate'))
    assert 'A10W_oath_refused' in w.flags['A10']
    checks.append('Unanswered oath timeout resolves pending state')
    for solo in (False, True):
        w = prepared('colonial')
        if solo:
            w.faction['A10'] = 'islands'
            w.faction_leaders['islands'] = 'A10'
        before = {k: set(v) for k, v in w.territory.items()}
        w.effect('A10W_request_colony_effect')
        w.choose('A10W_path.10', 'a')
        assert w.subject == {'A10': 'A04'} and w.territory == before
        assert 'A10W_colony_ratified' in w.flags['A10']
        assert ('A10' not in w.faction) if solo else True
        checks.append('Voluntary colony, empty faction=' + str(solo))
    for obstacle in ('own_subject', 'own_overlord', 'chamber_overlord', 'own_war', 'chamber_war', 'full_faction'):
        w = prepared('colonial')
        if obstacle == 'own_subject':
            w.subject['PVI'] = 'A10'
        elif obstacle == 'own_overlord':
            w.subject['A10'] = 'A02'
        elif obstacle == 'chamber_overlord':
            w.subject['A04'] = 'A02'
        elif obstacle.endswith('war'):
            w.wars.add(frozenset(('A10' if obstacle == 'own_war' else 'A04', 'A02')))
        else:
            w.faction.update(A10='islands', PVI='islands')
            w.faction_leaders['islands'] = 'A10'
        before = dict(w.subject)
        assert not w.check(triggers['A10W_colony_eligible'])
        w.effect('A10W_establish_colony_effect')
        assert w.subject == before and not w.audit
        checks.append('Colony transition safely blocked by ' + obstacle)
    w = prepared('colonial')
    w.effect('A10W_request_colony_effect')
    w.choose('A10W_path.10', 'b')
    assert not w.subject and 'A10W_colony_refused' in w.flags['A10']
    checks.append('Colonial treaty refusal preserves sovereignty')
    for shared in (False, True):
        w = prepared('metropolitan')
        if shared:
            w.faction.update(A10='islands', A04='islands')
            w.faction_leaders['islands'] = 'A10'
        before = {k: set(v) for k, v in w.territory.items()}
        w.effect('A10W_request_metropole_effect')
        w.choose('A10W_path.20', 'a')
        assert w.subject == {'A04': 'A10'} and w.territory == before
        assert 'A10W_temporary_exchange' in w.flags['A10']
        assert 'A10W_metropole_ratified' in w.flags['A10']
        checks.append('Voluntary Atlantic office with shared faction=' + str(shared))
    w = prepared('metropolitan')
    w.effect('A10W_establish_metropole_effect')
    assert not w.subject
    checks.append('Metropole cannot subordinate Chamber without explicit consent')
    w = prepared('metropolitan')
    w.effect('A10W_request_metropole_effect')
    w.choose('A10W_path.20', 'b')
    assert not w.subject and 'A10W_metropole_refused' in w.flags['A10']
    checks.append('Metropolitan refusal preserves the provisional exchange')
    w = prepared('metropolitan')
    w.effect('A10W_request_metropole_effect')
    w.wars.add(frozenset(('A10', 'A02')))
    assert not w.check(value(next(v for k, _, v in events['A10W_path.20'] if k == 'option'), 'trigger'))
    w.flags['A04'].add('A10W_voluntary_office')
    w.effect('A10W_establish_metropole_effect')
    assert not w.subject
    checks.append('State change during seven-day diplomatic delay is rechecked')
    w = prepared('metropolitan')
    w.territory['A10'].add(327)
    w.flags['A04'].add('A10W_voluntary_office')
    w.effect('A10W_establish_metropole_effect')
    assert w.capital['A10'] == 327 and 'A10W_manila_exchange' in w.flags['A10']
    checks.append('Manila capital requires existing island ownership and control')
    w = prepared('metropolitan')
    w.variables['A10']['A10W_charter_tension'] = 59
    w.effect('A10W_refresh_effect')
    assert 'A10W_charter_strikes' not in w.ideas['A10']
    w.variables['A10']['A10W_charter_tension'] = 60
    w.effect('A10W_refresh_effect')
    assert 'A10W_charter_strikes' in w.ideas['A10']
    w.variables['A10']['A10W_charter_tension'] = 90
    w.effect('A10W_refresh_effect')
    assert ('A10', 'A10W_path.30') in w.queue
    checks.append('Real tension thresholds at 59, 60 and 90')
    scripts = [p for folder in ('common', 'events') for p in (ROOT / folder).rglob('A10W*.txt')]
    for path in scripts:
        parse(read(path))
    fs = json.loads(read(ROOT / 'tools/a10w_focuses.json'))
    assert len(fs) == len({f['id'] for f in fs}) == 24
    assert all(f['available'] == 'always = yes' for f in fs)
    assert all(not re.search(r'\b(transfer_state|annex_country|declare_war_on)\s*=', read(p)) for p in scripts)
    checks.append('24 focus specifications; no sovereignty-dependent focus locks or territory seizure')
    return checks


if __name__ == '__main__':
    results = validate()
    print(json.dumps({'status': 'passed', 'checks': results,
                      'limitation': 'Bounded execution of actual scripts; full autonomy and faction integration require the game engine.'},
                     ensure_ascii=False, indent=2))
