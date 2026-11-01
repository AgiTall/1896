"""Bounded execution of the actual military scripts, not a replacement game engine.

Models political variables, timed flags/ideas, decision costs and cooldowns,
scheduled event options, focus gates, characters and guarded subject recall.
Combat, AI scheduling, economic modifiers and engine presentation are excluded.
"""
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
import json
from validate_philippines_rework import parse, value

R = Path(__file__).resolve().parents[1]


def read(path):
    return parse((R / path).read_text(encoding="utf-8-sig"))


EFFECTS = {k: v for k, _, v in read("common/scripted_effects/A10M_military.txt")}
TRIGGERS = {k: v for k, _, v in read("common/scripted_triggers/A10M_military.txt")}
EVENTS = {value(v, "id"): v for k, _, v in read("events/A10M_military.txt") if k == "country_event"}
DECISIONS = {k: v for k, _, v in value(read("common/decisions/A10M_military.txt"), "A10M_state_of_siege")}
FOCUSES = {value(v, "id"): v for k, _, v in value(read("common/national_focus/a10_focus.txt"), "focus_tree") if k == "focus" and value(v, "id").startswith("A10M_")}
MONTHLY = value(value(read("common/on_actions/A10M_military.txt"), "on_actions"), "on_monthly")
OP, REP, STRAIN = "A10M_opposition", "A10M_repression", "A10M_strain"


class Model:
    def __init__(self, opposition=35, repression=35, strain=25):
        self.tags = {"A10", "A03", "PVI", "PSM", "PCB", "PBT", "XYZ"}
        self.vars = defaultdict(lambda: defaultdict(float))
        self.vars["A10"].update({OP: opposition, REP: repression, STRAIN: strain})
        self.flags = defaultdict(set)
        self.flags["A10"].update({"A10M_initialized", "A10M_active"})
        self.flag_expiry, self.idea_expiry, self.decision_expiry = {}, {}, {}
        self.ideas, self.completed, self.characters = defaultdict(set), defaultdict(set), defaultdict(set)
        self.completed["A10"].add("A10_island_congress")
        self.characters["A10"].update({"A10_canon_leader", "A10M_mateo_sandoval"})
        self.overlords = {}
        self.war, self.capitulated = set(), set()
        self.stats = defaultdict(lambda: defaultdict(float))
        self.stats["A10"]["political_power"] = 1000
        self.stats["A10"]["manpower"] = 10000
        self.stats["A10"]["stability"] = 0.5
        self.queue, self.annexed, self.calls = [], [], defaultdict(int)
        self.day = 0
        self.leaders, self.cosmetic, self.fired_decisions = {}, {}, set()

    @staticmethod
    def compare(left, compare, right):
        return {"=": left == right, "<": left < right, ">": left > right,
                "equals": left == right, "not_equals": left != right,
                "less_than": left < right, "less_than_or_equals": left <= right,
                "greater_than": left > right, "greater_than_or_equals": left >= right}[compare]

    def variable(self, node):
        if value(node, "var") is not None:
            return value(node, "var"), value(node, "compare", "="), float(value(node, "value", 0))
        key, op, number = node[0]
        return key, op, float(number)

    def test(self, node, scope="A10"):
        results = []
        for key, op, v in node:
            if key in ("AND", "hidden_trigger"):
                result = self.test(v, scope)
            elif key == "OR":
                result = any(self.test([part], scope) for part in v)
            elif key == "NOT":
                result = not self.test(v, scope)
            elif key in self.tags:
                result = self.test(v, key)
            elif key in TRIGGERS:
                result = self.test(TRIGGERS[key], scope)
            elif key == "check_variable":
                name, comp, number = self.variable(v)
                result = self.compare(self.vars[scope][name], comp, number)
            elif key in ("has_country_flag", "has_idea", "has_completed_focus", "has_character"):
                source = {"has_country_flag": self.flags, "has_idea": self.ideas,
                          "has_completed_focus": self.completed, "has_character": self.characters}[key]
                result = v in source[scope]
            elif key == "tag":
                result = scope == v
            elif key == "always":
                result = v == "yes"
            elif key == "has_war":
                result = (scope in self.war) == (v == "yes")
            elif key == "has_capitulated":
                result = (scope in self.capitulated) == (v == "yes")
            elif key == "is_subject":
                result = (scope in self.overlords) == (v == "yes")
            else:
                raise AssertionError(("Unmodelled trigger", key))
            results.append(result)
        return all(results)

    def run(self, node, scope="A10", previous_scope=None):
        branch = False
        for key, _, v in node:
            if key == "if":
                branch = self.test(value(v, "limit", []), scope)
                if branch:
                    self.run([p for p in v if p[0] != "limit"], scope, previous_scope)
            elif key == "else":
                if not branch:
                    self.run(v, scope, previous_scope)
            elif key in EFFECTS:
                self.calls[key] += 1
                self.run(EFFECTS[key], scope, previous_scope)
            elif key in self.tags:
                self.run(v, key, scope)
            elif key in ("set_variable", "add_to_variable", "subtract_from_variable"):
                name, _, number = self.variable(v)
                if key == "set_variable": self.vars[scope][name] = number
                else: self.vars[scope][name] += number * (-1 if key == "subtract_from_variable" else 1)
            elif key == "clamp_variable":
                name = value(v, "var")
                self.vars[scope][name] = min(float(value(v, "max")), max(float(value(v, "min")), self.vars[scope][name]))
            elif key == "set_country_flag":
                name = value(v, "flag") if isinstance(v, list) else v
                self.flags[scope].add(name)
                if isinstance(v, list): self.flag_expiry[scope, name] = self.day + int(value(v, "days"))
            elif key == "clr_country_flag":
                self.flags[scope].discard(v)
                self.flag_expiry.pop((scope, v), None)
            elif key in ("add_ideas", "remove_ideas"):
                if key == "add_ideas": self.ideas[scope].add(v)
                else:
                    self.ideas[scope].discard(v)
                    self.idea_expiry.pop((scope, v), None)
            elif key == "add_timed_idea":
                idea = value(v, "idea")
                self.ideas[scope].add(idea)
                self.idea_expiry[scope, idea] = self.day + int(value(v, "days"))
            elif key == "country_event":
                self.queue.append((self.day + int(value(v, "days", 0)), scope, value(v, "id")))
            elif key in ("add_political_power", "add_stability", "add_war_support", "add_manpower", "add_command_power"):
                self.stats[scope][key[4:]] += float(v)
            elif key in ("army_experience", "navy_experience"):
                self.stats[scope][key] += float(v)
            elif key == "add_equipment_to_stockpile":
                self.stats[scope][value(v, "type")] += float(value(v, "amount"))
            elif key == "add_country_leader_role":
                character = value(v, "character")
                assert character in self.characters[scope]
                assert value(v, "promote_leader") == "yes"
                self.leaders[scope] = character
            elif key == "create_country_leader":
                self.leaders[scope] = value(v, "name")
            elif key == "retire_character":
                self.characters[scope].discard(v)
            elif key == "set_cosmetic_tag":
                self.cosmetic[scope] = v
            elif key == "every_subject_country":
                for target, lord in list(self.overlords.items()):
                    if lord == scope and self.test(value(v, "limit", []), target):
                        self.run([p for p in v if p[0] != "limit"], target, scope)
            elif key == "annex_country":
                target = previous_scope if value(v, "target") == "PREV" else value(v, "target")
                assert self.overlords.get(target) == scope
                assert value(v, "transfer_troops") == "yes"
                self.annexed.append(target)
                self.overlords.pop(target)
                self.tags.remove(target)
            elif key in ("custom_effect_tooltip", "set_politics"):
                pass  # Presentation and party composition are outside the numeric model.
            else:
                raise AssertionError(("Unmodelled effect", key))

    def effect(self, key):
        self.run([(key, "=", "yes")])

    def option(self, event, letter="a", scope="A10"):
        definition = EVENTS[event]
        if not self.test(value(definition, "trigger", []), scope): return False
        option = next(v for k, _, v in definition if k == "option" and value(v, "name") == event + "." + letter)
        if not self.test(value(option, "trigger", []), scope): return False
        self.run([p for p in option if p[0] not in ("name", "ai_chance", "trigger")], scope)
        return True

    def advance(self, days, choices=None):
        self.day += days
        for expiries, source in ((self.flag_expiry, self.flags), (self.idea_expiry, self.ideas)):
            for (scope, key), end in list(expiries.items()):
                if end <= self.day:
                    source[scope].discard(key)
                    del expiries[scope, key]
        ready = sorted(item for item in self.queue if item[0] <= self.day)
        self.queue = [item for item in self.queue if item[0] > self.day]
        for _, scope, event in ready: self.option(event, (choices or {}).get(event, "a"), scope)

    def decide(self, key):
        definition = DECISIONS[key]
        if not self.test(value(definition, "visible", [])): return False
        if not self.test(value(definition, "available", [])): return False
        if self.day < self.decision_expiry.get(key, 0) or key in self.fired_decisions: return False
        cost = float(value(definition, "cost", 0))
        if self.stats["A10"]["political_power"] < cost: return False
        self.stats["A10"]["political_power"] -= cost
        self.run(value(definition, "complete_effect", []))
        self.decision_expiry[key] = self.day + int(value(definition, "days_re_enable", 0))
        if value(definition, "fire_only_once") == "yes": self.fired_decisions.add(key)
        return True

    def focus(self, key):
        definition = FOCUSES[key]
        groups = [[p for _, _, p in v] for k, _, v in definition if k == "prerequisite"]
        exclusive = [p for k, _, v in definition if k == "mutually_exclusive" for _, _, p in v]
        if key in self.completed["A10"] or not all(set(g) & self.completed["A10"] for g in groups): return False
        if set(exclusive) & self.completed["A10"] or not self.test(value(definition, "available", [])): return False
        self.run(value(definition, "completion_reward", []))
        self.completed["A10"].add(key)
        return True

    def dispatch_month(self):
        for tag in list(self.tags): self.run(value(MONTHLY, "effect", []), tag)


def validate():
    checks = []
    for threshold in (64, 64.999, 65, 65.001, 66):
        m = Model(opposition=threshold, strain=threshold)
        m.effect("A10M_update")
        assert ("A10M_strikes" in m.ideas["A10"]) == (threshold >= 65)
        assert ("A10M_rationing" in m.ideas["A10"]) == (threshold >= 65)
        assert m.test(TRIGGERS["A10M_crisis_contained"]) == (threshold < 65)
        m.vars["A10"].update({OP: 64.999, STRAIN: 64.999})
        m.effect("A10M_update")
        assert not {"A10M_strikes", "A10M_rationing"} & m.ideas["A10"]
    m = Model(-5, 105, 150); m.effect("A10M_update")
    assert dict(m.vars["A10"]) == {OP: 0, REP: 100, STRAIN: 100}
    checks.append("65 threshold: integer/fractional onset, recovery, containment and 0–100 bounds")

    for war in (False, True):
        for rep in (64.999, 65, 65.001):
            for junta in (False, True):
                m = Model(20, rep, 20)
                if war: m.war.add("A10")
                if junta: m.flags["A10"].add("A10M_junta")
                m.effect("A10M_monthly")
                assert m.vars["A10"][OP] == 22 + (2 if rep >= 65 else 0)
                assert m.vars["A10"][STRAIN] == 20 + (2 if war else -1) + (2 if rep >= 65 else 0)
                assert m.vars["A10"][REP] == rep - (0 if junta else 1)
    checks.append("12 monthly war/peace, 65 repression and junta/ordinary decay scenarios")

    deltas = {"requisition_bureaus": (0, 2), "compensation_bonds": (0, -2),
              "compulsory_labour": (3, 2), "field_hospitals": (0, -1),
              "supply_inspectorate": (0, -1), "professional_service": (-1, 0),
              "published_budget": (0, -1), "veterans_obligations": (-1, -2), "civil_recovery": (-1, -1)}
    for idea, (opposition, strain) in deltas.items():
        m = Model(20, 20, 20); m.ideas["A10"].add("A10M_" + idea); m.effect("A10M_monthly")
        assert (m.vars["A10"][OP], m.vars["A10"][STRAIN]) == (22 + opposition, 19 + strain), idea
    checks.append("all nine institution costs/recovery monthly deltas")

    for target, event in ((OP, "A10M.4"), (STRAIN, "A10M.3")):
        for final in (79, 79.999, 80, 80.001, 81):
            m = Model(20, 20, 20); m.war.add("A10"); m.vars["A10"][target] = final - 2
            m.effect("A10M_monthly")
            assert any(e == event for _, _, e in m.queue) == (final >= 80)
    m = Model(90, 20, 90); m.war.add("A10"); m.effect("A10M_monthly")
    assert {e for _, _, e in m.queue} == {"A10M.3", "A10M.4"}
    m.effect("A10M_monthly"); assert len(m.queue) == 2
    m.advance(149); m.vars["A10"].update({OP: 90, STRAIN: 90}); m.effect("A10M_monthly")
    assert not m.queue
    m.advance(1); m.effect("A10M_monthly"); assert len(m.queue) == 2
    checks.append("80 integer/fractional scheduling and independent exact 150-day crisis cooldowns")

    for event in EVENTS:
        for option in ("a", "b"):
            m = Model(90, 40, 90); m.stats["A10"]["political_power"] = -100
            assert m.option(event, option)
            assert all(0 <= n <= 100 for n in m.vars["A10"].values())
            if event in ("A10M.3", "A10M.4") and option == "a":
                assert m.stats["A10"]["political_power"] < -100
            if event in ("A10M.2", "A10M.4") and option == "b":
                assert "A10M_shattered_officer_corps" in m.ideas["A10"]
                m.advance(179); assert "A10M_shattered_officer_corps" in m.ideas["A10"]
                m.advance(1); assert "A10M_shattered_officer_corps" not in m.ideas["A10"]
    m = Model(64.999, 20, 64.999)
    assert not m.option("A10M.3") and not m.option("A10M.4")
    checks.append("all 12 event options, debt-tolerant compromise, conditional delivery and 180-day purge expiry")

    for key, definition in DECISIONS.items():
        m = Model(70, 70, 70)
        m.completed["A10"].update(FOCUSES)
        m.ideas["A10"].update({"A10M_compulsory_labour", "A10M_shattered_officer_corps", "A10M_requisition_bureaus"})
        before = m.stats["A10"]["political_power"]
        assert m.decide(key), key
        assert m.stats["A10"]["political_power"] == before - float(value(definition, "cost"))
        assert not m.decide(key), (key, "same-day repeat")
        if value(definition, "fire_only_once") != "yes":
            m.advance(int(value(definition, "days_re_enable")) - 1)
            assert not m.decide(key), (key, "early repeat")
    m = Model(90, 90, 90); m.ideas["A10"].add("A10M_compulsory_labour")
    assert m.decide("A10M_end_labour_battalions")
    assert "A10M_compulsory_labour" not in m.ideas["A10"] and "A10M_compensation_bonds" in m.ideas["A10"]
    m.advance(1000); m.ideas["A10"].add("A10M_compulsory_labour")
    assert not m.decide("A10M_end_labour_battalions")
    m.stats["A10"]["political_power"] = 0
    assert not m.decide("A10M_purchase_rice")
    checks.append("all nine decision costs, repeat gates, forced-labour reversal and unaffordable decision rejection")

    for character_present in (False, True):
        m = Model(); m.flags["A10"].clear()
        m.ideas["A10"].update({"PZ_philippine_confederation", "A10_separatism"})
        if not character_present: m.characters["A10"].discard("A10M_mateo_sandoval")
        m.effect("A10M_begin_coup")
        assert m.leaders["A10"] == ("A10M_mateo_sandoval" if character_present else "A10M_mateo_sandoval_name")
        assert not {"PZ_philippine_confederation", "A10_separatism"} & m.ideas["A10"]
        before = deepcopy(m.vars["A10"]); m.effect("A10M_initialize"); assert m.vars["A10"] == before
    m = Model(); m.overlords = {"PVI": "A10", "PBT": "A10", "PSM": "A03", "XYZ": "A10"}
    m.effect("A10M_recall_members")
    assert set(m.annexed) == {"PVI", "PBT"} and m.overlords == {"PSM": "A03", "XYZ": "A10"}
    assert "PCB" in m.tags
    checks.append("history character and old-save fallback, coup cleanup, idempotent initialization, own-subject troop recall")

    for route, blocked, end in (("junta", {"A10M_directorate", "A10M_compensation"}, "A10M_red_seal"),
                                ("directorate", {"A10M_junta", "A10M_labour_battalions"}, "A10M_fixed_term")):
        m = Model(); m.flags["A10"].clear(); m.stats["A10"]["political_power"] = 10000
        for _ in range(40):
            moved = False
            for key in FOCUSES:
                if key not in blocked and key not in m.completed["A10"] and m.focus(key):
                    moved = True; m.advance(3)
            if not moved: break
        if "A10M_iron_archipelago" not in m.completed["A10"]:
            # A radical run can finish institutions exactly at the 65 boundary;
            # exercise the real civilian relief decision before the final gate.
            assert m.decide("A10M_provincial_hearings")
            assert m.focus("A10M_iron_archipelago")
        assert end in m.completed["A10"] and "A10M_iron_archipelago" in m.completed["A10"], route
        assert ("A10M_permanent_junta" in m.ideas["A10"]) == (route == "junta")
        assert ("A10M_military_directorate" in m.ideas["A10"]) == (route == "directorate")
        assert "A10M_compulsory_labour" not in m.ideas["A10"]
        assert "A10R_war_ready" in m.flags["A10"]
        m.vars["A10"].update({OP: 20, REP: 20, STRAIN: 20}); m.war.add("A10")
        m.dispatch_month()
        assert m.vars["A10"][OP] <= 20 and m.vars["A10"][STRAIN] < 20
        assert m.calls["A10M_monthly"] == 1, "Monthly processing repeated for foreign countries"
        before = deepcopy(m.vars["A10"]); m.capitulated.add("A10"); m.dispatch_month()
        assert m.vars["A10"] == before
    checks.append("both full focus outcomes and shared finale; sustainable wartime recovery; one monthly dispatch; capitulation pause")

    report = {"date": "2026-10-24", "status": "PASS", "focuses": len(FOCUSES), "event_options": len(EVENTS) * 2,
              "decisions": len(DECISIONS), "scenario_groups": len(checks), "checks": checks,
              "method": "Executes parsed actual A10M effect/trigger/event/decision/focus/on_action bodies with fail-closed unsupported operations",
              "limitations": ["Bounded script model is not the HOI4 engine", "No combat, AI timing, economy modifier recalculation or campaign balance simulation"]}
    (R / "tools/philippines_military_validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    validate()
