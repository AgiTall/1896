"""Strict bounded interpreter for the installed Chamber scripts, not a game emulator."""
from collections import defaultdict
from pathlib import Path
import re
from validate_philippines_rework import parse, value

ROOT = Path(__file__).resolve().parents[1]


def definitions(folder):
    return {key: node for path in (ROOT / folder).glob('*.txt')
            for key, _, node in parse(path.read_text(encoding='utf-8-sig'))}


EFFECTS = definitions('common/scripted_effects')
TRIGGERS = definitions('common/scripted_triggers')
EVENTS = {value(node, 'id'): node for path in (ROOT / 'events').glob('*.txt')
          for key, _, node in parse(path.read_text(encoding='utf-8-sig')) if key == 'country_event'}
TAGS = {tag for path in (ROOT / 'common/country_tags').glob('*.txt')
        for tag in re.findall(r'^\s*([A-Z0-9]{3})\s*=', path.read_text(encoding='utf-8-sig'), re.M)}


def compare(a, operator, b):
    return {'=': a == b, '>': a > b, '<': a < b, '>=': a >= b, '<=': a <= b}[operator]


class World:
    def __init__(self):
        self.tags = set(TAGS)
        self.day = 0
        self.vars = defaultdict(lambda: defaultdict(float))
        self.flags = defaultdict(set)
        self.flag_expiry = {}
        self.global_flags = {'WTC_british_cover'}
        self.ideas = defaultdict(set)
        self.idea_expiry = {}
        self.stock = defaultdict(lambda: defaultdict(float))
        self.pp = defaultdict(lambda: 500.0)
        self.stability = defaultdict(lambda: 0.5)
        self.capitulated = set()
        self.wars = set()
        self.focuses = defaultdict(set)
        self.government = {}
        self.queue = []
        self.inbox = []
        self.states = {697: dict(owner='A04', controller='A04', industry=0, slots=0)}
        self.capitals = {'A04': 697}
        self.effect('WTN_initialize_effect', 'A04')
        for tag in sorted(self.tags):
            self.effect('WTC_initialize_effect', tag)

    def number(self, token, current, previous=None, root=None, source=None):
        try:
            return float(token)
        except (ValueError, TypeError):
            if '.' in token:
                scope, name = token.split('.', 1)
                scope = {'PREV': previous, 'ROOT': root, 'FROM': source, 'THIS': current}.get(scope, scope)
                return self.vars[scope].get(name, 0)
            return self.vars[current].get(token, 0)

    def test(self, nodes, current, root=None, source=None, previous=None):
        root = current if root is None else root
        results = []
        for key, operator, node in nodes:
            scope = {'ROOT': root, 'THIS': current, 'FROM': source, 'PREV': previous}.get(key, key)
            if key in TAGS or key in ('ROOT', 'THIS', 'FROM', 'PREV'):
                result = scope in self.tags and self.test(node, scope, root, source, current)
            elif key in TRIGGERS:
                result = self.test(TRIGGERS[key], current, root, source, previous) == (node == 'yes')
            elif key in ('AND', 'hidden_trigger'):
                result = self.test(node, current, root, source, previous)
            elif key == 'OR':
                result = any(self.test([part], current, root, source, previous) for part in node)
            elif key == 'NOT':
                result = not self.test(node, current, root, source, previous)
            elif key == 'tag' or key == 'original_tag':
                result = current == node
            elif key == 'exists':
                result = (current in self.tags) == (node == 'yes')
            elif key == 'country_exists':
                result = node in self.tags
            elif key == 'has_capitulated':
                result = (current in self.capitulated) == (node == 'yes')
            elif key == 'has_war_with':
                result = frozenset((current, node)) in self.wars
            elif key == 'has_war':
                result = any(current in war for war in self.wars) == (node == 'yes')
            elif key == 'has_country_flag':
                result = node in self.flags[current]
            elif key == 'has_global_flag':
                result = node in self.global_flags
            elif key == 'has_completed_focus':
                result = node in self.focuses[current]
            elif key == 'has_idea':
                result = node in self.ideas[current]
            elif key == 'has_political_power':
                result = compare(self.pp[current], operator, float(node))
            elif key == 'check_variable':
                name, op, number = node[0]
                result = compare(self.vars[current][name], op, self.number(number, current, previous, root, source))
            elif key == 'has_equipment':
                result = all(compare(self.inventory(current, name), op, float(amount)) for name, op, amount in node)
            elif key in ('is_owned_by', 'is_controlled_by'):
                owner = {'ROOT': root, 'FROM': source, 'PREV': previous}.get(node, node)
                result = self.states[current]['owner' if key == 'is_owned_by' else 'controller'] == owner
            elif key == 'always':
                result = node == 'yes'
            else:
                raise AssertionError(('Unmodelled Chamber condition', key, node))
            results.append(result)
        return all(results)

    def inventory(self, tag, equipment):
        return sum(amount for name, amount in self.stock[tag].items()
                   if name == equipment or name.startswith(equipment + '_'))

    def run(self, nodes, current, root=None, source=None, previous=None):
        root = current if root is None else root
        condition = False
        for key, _, node in nodes:
            scope = {'ROOT': root, 'THIS': current, 'FROM': source, 'PREV': previous}.get(key, key)
            if key == 'if':
                condition = self.test(value(node, 'limit', []), current, root, source, previous)
                if condition:
                    self.run([n for n in node if n[0] != 'limit'], current, root, source, previous)
            elif key == 'else_if':
                if not condition:
                    condition = self.test(value(node, 'limit', []), current, root, source, previous)
                    if condition:
                        self.run([n for n in node if n[0] != 'limit'], current, root, source, previous)
            elif key == 'else':
                if not condition:
                    self.run(node, current, root, source, previous)
            elif key in TAGS or key in ('ROOT', 'THIS', 'FROM', 'PREV'):
                if scope in self.tags:
                    self.run(node, scope, root, source, current)
            elif key in EFFECTS:
                assert node == 'yes'
                self.run(EFFECTS[key], current, root, source, previous)
            elif key in ('hidden_effect', 'immediate'):
                self.run(node, current, root, source, previous)
            elif key == 'every_country':
                for tag in sorted(self.tags):
                    if self.test(value(node, 'limit', []), tag, root, source, current):
                        self.run([n for n in node if n[0] != 'limit'], tag, root, source, current)
            elif key == 'capital_scope':
                if current in self.capitals:
                    self.run(node, self.capitals[current], root, source, current)
            elif key in ('set_variable', 'add_to_variable'):
                name, _, amount = node[0]
                number = self.number(amount, current, previous, root, source)
                self.vars[current][name] = number + (self.vars[current][name] if key == 'add_to_variable' else 0)
            elif key == 'clamp_variable':
                name = value(node, 'var')
                self.vars[current][name] = min(float(value(node, 'max')), max(float(value(node, 'min')), self.vars[current][name]))
            elif key == 'set_country_flag':
                flag = value(node, 'flag') if isinstance(node, list) else node
                self.flags[current].add(flag)
                self.flag_expiry.pop((current, flag), None)
                if isinstance(node, list):
                    self.flag_expiry[current, flag] = self.day + int(value(node, 'days'))
            elif key == 'clr_country_flag':
                self.flags[current].discard(node)
                self.flag_expiry.pop((current, node), None)
            elif key == 'set_global_flag':
                self.global_flags.add(node)
            elif key == 'clr_global_flag':
                self.global_flags.discard(node)
            elif key in ('add_ideas', 'add_timed_idea'):
                idea = node if isinstance(node, str) else value(node, 'idea')
                self.ideas[current].add(idea)
                if isinstance(node, list):
                    self.idea_expiry[current, idea] = self.day + int(value(node, 'days'))
            elif key == 'remove_ideas':
                self.ideas[current].discard(node)
                self.idea_expiry.pop((current, node), None)
            elif key == 'add_equipment_to_stockpile':
                equipment = value(node, 'type')
                amount = float(value(node, 'amount'))
                if amount >= 0:
                    self.stock[current][equipment] += amount
                else:
                    # Base-equipment removals consume actual models, as in the engine.
                    remaining = -amount
                    for name in list(self.stock[current]):
                        if name == equipment or name.startswith(equipment + '_'):
                            take = min(remaining, self.stock[current][name])
                            self.stock[current][name] -= take
                            remaining -= take
                    assert remaining == 0, (current, 'negative equipment', equipment)
            elif key == 'add_political_power':
                self.pp[current] += float(node)
            elif key == 'add_stability':
                self.stability[current] += float(node)
            elif key == 'country_event':
                self.queue.append((self.day + int(value(node, 'days', 0)), value(node, 'id'), current, root))
            elif key == 'set_politics':
                self.government[current] = value(node, 'ruling_party')
            elif key == 'add_extra_state_shared_building_slots':
                self.states[current]['slots'] += int(node)
            elif key == 'add_building_construction':
                assert value(node, 'type') in ('industrial_complex', 'arms_factory') and value(node, 'instant_build') == 'yes'
                name = 'industry' if value(node, 'type') == 'industrial_complex' else 'arms'
                self.states[current][name] = self.states[current].get(name, 0) + int(value(node, 'level'))
            elif key in ('name', 'trigger', 'ai_chance', 'custom_effect_tooltip', 'create_country_leader', 'add_popularity', 'add_war_support'):
                pass  # Presentation, character identity and political support are outside this model.
            else:
                raise AssertionError(('Unmodelled Chamber effect', key, node))

    def effect(self, name, current='A04', source=None):
        self.run(EFFECTS[name], current, source=source)

    def answer(self, event_id, option_name, current, source=None):
        # Deliberately permit a stale displayed event; its effect must recheck eligibility.
        event = EVENTS[event_id]
        option = next(n for k, _, n in event if k == 'option' and value(n, 'name') == option_name)
        self.run(option, current, source=source)

    def advance(self, days, deliver=True):
        for _ in range(days):
            self.day += 1
            for (tag, flag), expiry in list(self.flag_expiry.items()):
                if expiry <= self.day:
                    self.flags[tag].discard(flag)
                    del self.flag_expiry[tag, flag]
            for (tag, idea), expiry in list(self.idea_expiry.items()):
                if expiry <= self.day:
                    self.ideas[tag].discard(idea)
                    del self.idea_expiry[tag, idea]
            for tag in sorted(self.tags):
                self.effect('WTN_customer_cleanup_effect', tag)
                if any(flag.startswith('WTN_link_') for flag in self.flags[tag]) or 'WTN_island_cooperation' in self.ideas[tag]:
                    self.effect('WTN_refresh_links_effect', tag)
            if 'A04' in self.tags:
                self.effect('WTN_cleanup_orphan_reserves_effect')
            if deliver:
                ready = [item for item in self.queue if item[0] <= self.day]
                self.queue = [item for item in self.queue if item[0] > self.day]
                for _, event_id, tag, source in ready:
                    event = EVENTS[event_id]
                    if tag in self.tags and self.test(value(event, 'trigger', []), tag, source=source):
                        if value(event, 'hidden') == 'yes':
                            self.run(value(event, 'immediate', []), tag, source=source)
                        else:
                            self.inbox.append((self.day + int(value(event, 'timeout_days', 13)), event_id, tag, source))
                for item in list(self.inbox):
                    deadline, event_id, tag, source = item
                    if deadline <= self.day:
                        first = next(n for k, _, n in EVENTS[event_id] if k == 'option')
                        self.run(first, tag, source=source)
                        self.inbox.remove(item)

    def assets(self):
        return ({k: dict(v) for k, v in self.vars.items()}, {k: dict(v) for k, v in self.stock.items()},
                {k: set(v) for k, v in self.ideas.items()}, dict(self.pp), dict(self.government), set(self.wars))
