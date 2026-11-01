"""Validate Japanese maritime scripts and execute bounded lifecycle scenarios.

The model executes the actual parsed guards/effects and rejects unknown syntax.
It models eligibility, political power, equipment, flags, ideas, XP, project
durations, cooldowns and delayed choices. It does not simulate combat or AI.
"""
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
import re

from validate_philippines_rework import parse, value, walk

ROOT = Path(__file__).resolve().parents[1]
GAME = Path("D:/SteamLibrary/steamapps/common/Hearts of Iron IV")
KINDS = ("register", "repairs", "coaling", "drills", "conference", "reserves")
DONE = {kind: "JMC_" + kind + "_done" for kind in KINDS[:4]}
DONE["conference"] = "JMC_programme_complete"
EXPECTED_COSTS = dict(zip(KINDS, (35, 50, 60, 40, 50, 45)))
EXPECTED_DURATIONS = dict(zip(KINDS, (21, 35, 35, 21, 14, 30)))
REQUIRED_FILES = (
    "common/decisions/JMC_maritime.txt",
    "common/decisions/categories/JMC_maritime.txt",
    "common/scripted_effects/JMC_maritime.txt",
    "common/scripted_triggers/JMC_maritime.txt",
    "common/ideas/JMC_maritime.txt",
    "events/JMC_maritime.txt",
)


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8-sig")


def compare(actual, operator, expected):
    return {"=": actual == expected, ">": actual > expected,
            "<": actual < expected, ">=": actual >= expected,
            "<=": actual <= expected}[operator]


class Model:
    """A deliberately small interpreter for the maritime contract."""

    def __init__(self, content):
        self.content = content
        self.day = 0
        self.countries = {"A03", "A01"}
        self.subjects = set()
        self.capitulated = set()
        self.states = {"282": dict(owner="A03", controller="A03", coastal=True),
                       "531": dict(owner="A03", controller="A03", coastal=False)}
        self.focuses = {"JSM_steel", "JSM_workshops", "JSM_shipyards", "JSM_council"}
        self.flags = set()
        self.ideas = set()
        self.idea_expiry = {}
        self.pp = 1000.0
        self.stock = defaultdict(float, support_equipment_1=1000, convoy_1=0)
        self.xp = defaultdict(float)
        self.queue = []
        self.active = {}
        self.cooldowns = {}

    def inventory(self, name):
        return sum(amount for equipment, amount in self.stock.items()
                   if equipment == name or equipment.startswith(name + "_"))

    def test(self, node, scope="A03", root="A03"):
        outcomes = []
        for key, operator, val in node:
            if key in self.content["triggers"]:
                result = self.test(self.content["triggers"][key], scope, root) == (val == "yes")
            elif key in ("AND", "hidden_trigger"):
                result = self.test(val, scope, root)
            elif key == "OR":
                result = any(self.test([entry], scope, root) for entry in val)
            elif key == "NOT":
                result = not self.test(val, scope, root)
            elif key in self.countries or re.fullmatch(r"[A-Z][A-Z0-9]{2}", key):
                result = self.test(val, key, root)
            elif key == "tag":
                result = scope == val
            elif key == "exists":
                result = (scope in self.countries) == (val == "yes")
            elif key == "country_exists":
                result = val in self.countries
            elif key == "always":
                result = val == "yes"
            elif key == "is_subject":
                result = (scope in self.subjects) == (val == "yes")
            elif key == "has_capitulated":
                result = (scope in self.capitulated) == (val == "yes")
            elif key == "has_completed_focus":
                result = val in self.focuses
            elif key == "has_country_flag":
                result = val in self.flags
            elif key == "has_idea":
                result = val in self.ideas
            elif key == "has_equipment":
                result = all(compare(self.inventory(name), op, float(amount))
                             for name, op, amount in val)
            elif key == "has_political_power":
                result = compare(self.pp, operator, float(val))
            elif key == "any_owned_state":
                result = any(self.test(val, sid, root) for sid, state in self.states.items()
                             if state["owner"] == scope)
            elif key in ("is_owned_by", "is_controlled_by"):
                country = root if val == "ROOT" else val
                field = "owner" if key == "is_owned_by" else "controller"
                result = self.states[scope][field] == country
            elif key == "is_coastal":
                result = self.states[scope]["coastal"] == (val == "yes")
            else:
                raise AssertionError(("Unmodelled maritime trigger", key, val))
            outcomes.append(result)
        return all(outcomes)

    def run(self, node, scope="A03", root="A03"):
        previous = False
        for key, _, val in node:
            if key == "if":
                previous = self.test(value(val, "limit", []), scope, root)
                if previous:
                    self.run([part for part in val if part[0] != "limit"], scope, root)
            elif key == "else_if":
                if not previous:
                    previous = self.test(value(val, "limit", []), scope, root)
                    if previous:
                        self.run([part for part in val if part[0] != "limit"], scope, root)
            elif key == "else":
                if not previous:
                    self.run(val, scope, root)
            elif key in self.content["effects"]:
                assert val == "yes", (key, "scripted effect arguments not modelled")
                self.run(self.content["effects"][key], scope, root)
            elif key == "hidden_effect":
                self.run(val, scope, root)
            elif key == "set_country_flag":
                self.flags.add(val)
            elif key == "clr_country_flag":
                self.flags.discard(val)
            elif key == "add_ideas":
                self.ideas.add(val)
                self.idea_expiry.pop(val, None)
            elif key == "remove_ideas":
                self.ideas.discard(val)
                self.idea_expiry.pop(val, None)
            elif key == "add_timed_idea":
                idea = value(val, "idea")
                self.ideas.add(idea)
                self.idea_expiry[idea] = self.day + int(value(val, "days"))
            elif key == "add_equipment_to_stockpile":
                self.stock[value(val, "type")] += float(value(val, "amount"))
            elif key == "add_political_power":
                self.pp += float(val)
            elif key in ("army_experience", "navy_experience", "air_experience"):
                self.xp[key] += float(val)
            elif key == "country_event":
                self.queue.append((self.day + int(value(val, "days", 0)), value(val, "id")))
            elif key in ("name", "ai_chance", "custom_effect_tooltip", "log"):
                pass  # Presentation or AI weights carry no modelled reward.
            else:
                raise AssertionError(("Unmodelled maritime effect", key, val))

    def visible(self, kind):
        return self.test(value(self.content["decisions"][kind], "visible", []))

    def can_start(self, kind):
        decision = self.content["decisions"][kind]
        return (kind not in self.active and self.day >= self.cooldowns.get(kind, 0)
                and self.pp >= float(value(decision, "cost", 0))
                and self.visible(kind) and self.test(value(decision, "available", [])))

    def start(self, kind):
        assert self.can_start(kind), (kind, "cannot start")
        decision = self.content["decisions"][kind]
        self.pp -= float(value(decision, "cost", 0))
        self.run(value(decision, "complete_effect", []))
        self.active[kind] = self.day + int(value(decision, "days_remove"))

    def advance(self, days):
        for _ in range(days):
            self.day += 1
            for idea, expiry in list(self.idea_expiry.items()):
                if expiry <= self.day:
                    self.ideas.discard(idea)
                    del self.idea_expiry[idea]
            for kind, deadline in list(self.active.items()):
                decision = self.content["decisions"][kind]
                cancelled = self.test(value(decision, "cancel_trigger", [("always", "=", "no")]))
                cancelled |= value(decision, "cancel_if_not_visible") == "yes" and not self.visible(kind)
                if cancelled:
                    self.run(value(decision, "cancel_effect", []))
                    del self.active[kind]
                elif deadline <= self.day:
                    self.run(value(decision, "remove_effect", []))
                    del self.active[kind]
                    self.cooldowns[kind] = self.day + int(value(decision, "days_re_enable", 0))

    def answer(self, event_id, index=0):
        options = [node for key, _, node in self.content["events"][event_id] if key == "option"]
        option = options[index]
        assert self.test(value(option, "trigger", [])), (event_id, "option unavailable", index)
        self.run(option)

    def assets(self):
        return (self.pp, dict(self.stock), dict(self.xp), set(self.ideas),
                dict(self.idea_expiry), set(self.flags), list(self.queue))


def load():
    for path in REQUIRED_FILES:
        assert (ROOT / path).is_file(), ("Missing maritime file", path)
    trees = {path: parse(read(path)) for path in REQUIRED_FILES}
    effects = dict((key, node) for key, _, node in trees["common/scripted_effects/JMC_maritime.txt"])
    triggers = dict((key, node) for key, _, node in trees["common/scripted_triggers/JMC_maritime.txt"])
    events = {value(node, "id"): node for key, _, node in trees["events/JMC_maritime.txt"] if key == "country_event"}
    ideas = dict((key, node) for key, _, node in value(value(trees["common/ideas/JMC_maritime.txt"], "ideas"), "country"))
    decision_entries = [(key, node) for _, _, category in trees["common/decisions/JMC_maritime.txt"] for key, _, node in category]
    decisions = {}
    decision_ids = {}
    for kind in KINDS:
        matches = [(key, node) for key, node in decision_entries
                   if value(value(node, "available", []), "JMC_can_start_" + kind) == "yes"]
        assert len(matches) == 1, (kind, "decision start trigger contract", [key for key, _ in matches])
        decision_ids[kind], decisions[kind] = matches[0]
    assert len(decision_entries) == len(decisions) == 6
    assert len(events) == 5 and len(ideas) == 6
    return dict(trees=trees, effects=effects, triggers=triggers, events=events,
                ideas=ideas, decisions=decisions, decision_ids=decision_ids)


def validate_references(content):
    """Resolve names against installed game data and both mod localisations."""
    docs = {kind: set(re.findall(r"^## (\w+)\s*$", (GAME / "documentation" / (kind + "_documentation.md")).read_text(encoding="utf-8-sig"), re.M))
            for kind in ("effects", "triggers", "modifiers")}
    sprites = {}
    for base in (GAME, ROOT):
        for path in (base / "interface").rglob("*.gfx"):
            for match in re.finditer(r'spriteType\s*=\s*\{\s*name\s*=\s*"?([^"\s]+)"?[^}]*?texturefile\s*=\s*"([^"]+)"', path.read_text(encoding="utf-8-sig"), re.S | re.I):
                sprites[match[1]] = match[2]

    def sprite(name):
        assert name in sprites, ("Missing maritime sprite", name)
        assert any((base / sprites[name]).exists() for base in (ROOT, GAME)), ("Missing maritime texture", name)

    locs = {}
    for lang in ("russian", "english"):
        entries = defaultdict(list)
        for path in (ROOT / "localisation" / lang).rglob("*.yml"):
            text = path.read_text(encoding="utf-8-sig")
            if path.name.startswith("JMC_"):
                assert path.read_bytes().startswith(b"\xef\xbb\xbf"), (lang, "Missing BOM", path)
                assert text.splitlines()[0] == "l_" + lang + ":"
            for key, text in re.findall(r'^\s+([^ :]+):\d+\s+"(.*)"\s*$', text, re.M):
                entries[key].append(text)
        for key, texts in entries.items():
            if key.startswith(("JMC_", "jmc_maritime.")):
                assert len(texts) == 1, (lang, "Duplicate maritime localisation", key)
        locs[lang] = entries

    def localized(key):
        for lang in locs:
            assert key.strip('"') in locs[lang], (lang, "Missing maritime localisation", key)

    equipment = "\n".join(path.read_text(encoding="utf-8-sig") for path in (ROOT / "common/units/equipment").glob("*.txt"))
    scopes = {"ROOT", "FROM", "PREV", "THIS", "owner", "controller", "capital_scope"}

    def check_trigger(node):
        for key, _, val in node:
            if key in ("AND", "OR", "NOT", "hidden_trigger") or key in scopes:
                check_trigger(val)
            else:
                assert key in docs["triggers"] or key in content["triggers"], ("Unknown maritime trigger", key)
                if key == "any_owned_state":
                    check_trigger(val)

    def check_effect(node):
        for key, _, val in node:
            assert key in docs["effects"] or key in content["effects"] or key in scopes or key in ("if", "else_if", "else", "hidden_effect"), ("Unknown maritime effect", key)
            if key in ("if", "else_if", "else", "hidden_effect") or key in scopes:
                for child, op, nested in val:
                    if child == "limit":
                        check_trigger(nested)
                    else:
                        check_effect([(child, op, nested)])
    for node in content["triggers"].values():
        check_trigger(node)
    for node in content["effects"].values():
        check_effect(node)
    for path, tree in content["trees"].items():
        for key, _, val in walk(tree):
            if key in ("available", "visible", "allowed", "trigger", "limit", "cancel_trigger") and isinstance(val, list):
                check_trigger(val)
            if key in ("complete_effect", "remove_effect", "cancel_effect", "immediate"):
                check_effect(val)
            if key == "option":
                localized(value(val, "name"))
                check_effect([entry for entry in val if entry[0] not in ("name", "ai_chance", "trigger")])
            if key in ("title", "desc", "custom_effect_tooltip") and isinstance(val, str):
                localized(val)
            if key == "country_event" and isinstance(val, list):
                assert value(val, "id") in content["events"], (path, "Missing maritime event", value(val, "id"))
            if key in ("add_ideas", "remove_ideas", "has_idea"):
                assert val in content["ideas"], (path, "Missing maritime idea", val)
            if key == "add_timed_idea":
                assert value(val, "idea") in content["ideas"]
            if key == "picture" and isinstance(val, str) and val.startswith("GFX_"):
                sprite(val)
            if key == "add_equipment_to_stockpile":
                typ = value(val, "type")
                assert re.search(r"\b" + re.escape(typ) + r"\s*=\s*\{", equipment), ("Missing maritime equipment", typ)
            if key.startswith("JMC_") and val == "yes":
                assert key in content["effects"] or key in content["triggers"], ("Missing maritime scripted call", key)
    for idea_id, idea in content["ideas"].items():
        localized(idea_id)
        localized(idea_id + "_desc")
        sprite("GFX_idea_" + value(idea, "picture"))
        for modifier, _, _ in value(idea, "modifier", []):
            assert modifier in docs["modifiers"], (idea_id, "Unknown maritime modifier", modifier)
    for kind, decision in content["decisions"].items():
        decision_id = content["decision_ids"][kind]
        localized(decision_id)
        localized(decision_id + "_desc")
        icon = value(decision, "icon")
        sprite(icon if icon.startswith("GFX_") else "GFX_decision_" + icon)
    for category_id, _, category in content["trees"]["common/decisions/categories/JMC_maritime.txt"]:
        localized(category_id)
        localized(category_id + "_desc")
        icon = value(category, "icon")
        sprite(icon if icon.startswith("GFX_") else "GFX_decision_category_" + icon)


def invalidate(model, scenario):
    if scenario == "annexed":
        model.countries.remove("A03")
    elif scenario == "subject":
        model.subjects.add("A03")
    elif scenario == "capitulated":
        model.capitulated.add("A03")
    elif scenario == "coast_lost":
        model.states["282"]["owner"] = "A01"
    elif scenario == "coast_occupied":
        model.states["282"]["controller"] = "A01"
    elif scenario == "inland_only":
        model.states["282"]["coastal"] = False
    else:
        raise AssertionError(scenario)


def restore_eligibility(model):
    model.countries.add("A03")
    model.subjects.discard("A03")
    model.capitulated.discard("A03")
    model.states["282"] = dict(owner="A03", controller="A03", coastal=True)


def expect_no_reward(before, after, kind):
    """An invalid finish may clear its active marker, but may not issue assets."""
    expected = deepcopy(before)
    expected.flags.discard("JMC_" + kind + "_in_progress")
    assert after.assets() == expected.assets(), (kind, "invalid finish issued a reward")


def validate_lifecycles(content):
    cases = 0
    for kind, decision in content["decisions"].items():
        assert int(value(decision, "cost")) == EXPECTED_COSTS[kind], kind
        assert int(value(decision, "days_remove")) == EXPECTED_DURATIONS[kind], kind
        assert value(decision, "fire_only_once", "no") == "no", (kind, "cancellation must allow retry")
        assert float(value(value(decision, "ai_will_do"), "base")) > 0, kind
        assert value(decision, "cancel_if_not_visible") == "yes", kind
        assert value(decision, "cancel_effect"), (kind, "missing cancellation cleanup")
    assert int(value(content["decisions"]["reserves"], "days_re_enable")) == 120

    # Complete the authored sequence, accounting for real costs, project times,
    # delayed notices and both the provisional and confirmed civilian plan.
    model = Model(content)
    prepared = {}
    pending_answers = {}
    for index, kind in enumerate(KINDS[:5], 1):
        prepared[kind] = deepcopy(model)
        assert model.can_start(kind), (kind, "normal route blocked")
        decision = content["decisions"][kind]
        before_pp = model.pp
        model.start(kind)
        assert model.pp == before_pp - EXPECTED_COSTS[kind]
        assert "JMC_" + kind + "_in_progress" in model.flags
        assert not model.can_start(kind), (kind, "active project offered twice")
        before_duplicate_start = model.assets()
        model.run(value(decision, "complete_effect"))
        assert model.assets() == before_duplicate_start, (kind, "duplicate start charged equipment")
        model.advance(EXPECTED_DURATIONS[kind] - 1)
        assert DONE[kind] not in model.flags, (kind, "premature success")
        model.advance(1)
        assert DONE[kind] in model.flags
        assert "JMC_" + kind + "_in_progress" not in model.flags
        assert not model.visible(kind), (kind, "completed project still visible")
        timed_rewards = {"repairs": ("JMC_yard_coordination", 180),
                         "coaling": ("JMC_coaling_network", 180),
                         "drills": ("JMC_escort_training", 120)}
        if kind in timed_rewards:
            idea, duration = timed_rewards[kind]
            assert model.idea_expiry[idea] == model.day + duration, (kind, "wrong bonus duration")
        event_id = "jmc_maritime." + str(index)
        assert model.queue[-1] == (model.day + 1, event_id), (kind, "wrong delayed event")
        if kind == "conference":
            assert "JMC_merchant_plan" in model.ideas
            assert "JMC_expedition_plan" not in model.ideas
            assert "JMC_course_confirmed" not in model.flags
        # All completions are safe to execute twice, including stock and XP.
        rewarded = model.assets()
        model.run(value(decision, "remove_effect"))
        assert model.assets() == rewarded, (kind, "duplicate finish issued assets")
        model.advance(1)
        assert model.test(value(content["events"][event_id], "trigger")), event_id
        pending_answers[event_id] = deepcopy(model)
        model.answer(event_id, 0)
        cases += 1
    assert model.pp == 785, ("full route political power", model.pp)
    assert model.inventory("support_equipment") == 1025
    assert model.xp["navy_experience"] == 18
    assert "JMC_merchant_plan" in model.ideas and "JMC_expedition_plan" not in model.ideas
    assert "JMC_course_confirmed" in model.flags
    assert len(model.queue) == 5
    prepared["reserves"] = deepcopy(model)

    # Ignored notifications cannot hold the economic programme hostage. Both
    # real choices remain optional for progress and grant at most one outcome.
    unanswered = Model(content)
    for kind in KINDS[:5]:
        unanswered.start(kind)
        unanswered.advance(EXPECTED_DURATIONS[kind])
    assert "JMC_register_outcome_chosen" not in unanswered.flags
    assert "JMC_course_confirmed" not in unanswered.flags
    assert "JMC_merchant_plan" in unanswered.ideas
    assert unanswered.can_start("reserves")
    unanswered.advance(30)
    unanswered.answer("jmc_maritime.1", 1)
    unanswered.answer("jmc_maritime.5", 1)
    late_rewarded = unanswered.assets()
    unanswered.advance(1)
    # Advancing one day does not expire any of these ideas.
    unanswered.answer("jmc_maritime.1", 0)
    unanswered.answer("jmc_maritime.5", 0)
    assert unanswered.assets() == late_rewarded, "late opposite answers changed confirmed outcomes"
    assert "JMC_expedition_plan" in unanswered.ideas and "JMC_merchant_plan" not in unanswered.ideas
    premature_answers = Model(content)
    for event_id in ("jmc_maritime.1", "jmc_maritime.5"):
        before = premature_answers.assets()
        premature_answers.answer(event_id, 0)
        assert premature_answers.assets() == before, (event_id, "choice before project completion")
    cases += 4

    # Focus staging and project prerequisites are independently necessary.
    focus_gates = {"register": "JSM_steel", "repairs": "JSM_workshops",
                   "coaling": "JSM_shipyards", "conference": "JSM_council"}
    for kind, focus in focus_gates.items():
        gated = deepcopy(prepared[kind])
        gated.focuses.remove(focus)
        assert not gated.can_start(kind), (kind, "missing focus gate")
        cases += 1
    for kind, prerequisite in (("repairs", "JMC_register_done"),
                               ("coaling", "JMC_register_done"),
                               ("drills", "JMC_repairs_done"),
                               ("drills", "JMC_coaling_done"),
                               ("conference", "JMC_drills_done"),
                               ("reserves", "JMC_programme_complete")):
        gated = deepcopy(prepared[kind])
        gated.flags.remove(prerequisite)
        assert not gated.can_start(kind), (kind, "missing predecessor accepted", prerequisite)
        cases += 1
    for kind in KINDS:
        premature = deepcopy(prepared[kind])
        before = premature.assets()
        premature.run(value(content["decisions"][kind], "remove_effect"))
        assert premature.assets() == before, (kind, "finish without a started project")
        poor = deepcopy(prepared[kind])
        poor.pp = EXPECTED_COSTS[kind] - 0.5
        assert not poor.can_start(kind), (kind, "insufficient political power")
        poor.pp = EXPECTED_COSTS[kind]
        assert poor.can_start(kind), (kind, "exact political power rejected")
        cases += 2

    # Exact stock boundaries include fractional balances. Finishing must not
    # require or charge equipment that was already committed at the start.
    for kind, price in (("coaling", 50), ("reserves", 25)):
        for amount, allowed in ((price - 1, False), (price - 0.5, False),
                                (price, True), (price + 0.5, True)):
            boundary = deepcopy(prepared[kind])
            boundary.stock = defaultdict(float, support_equipment_1=amount)
            assert boundary.can_start(kind) == allowed, (kind, "equipment boundary", amount)
            if allowed:
                boundary.start(kind)
                assert boundary.inventory("support_equipment") == amount - price
                boundary.advance(EXPECTED_DURATIONS[kind])
                assert "JMC_" + kind + "_in_progress" not in boundary.flags
                if kind in DONE:
                    assert DONE[kind] in boundary.flags, (kind, "charged equipment rechecked at finish")
                else:
                    assert boundary.inventory("convoy") == 6
            cases += 1

    invalid_states = ("annexed", "subject", "capitulated", "coast_lost", "coast_occupied", "inland_only")
    for kind in KINDS:
        decision = content["decisions"][kind]
        for scenario in invalid_states:
            blocked = deepcopy(prepared[kind])
            invalidate(blocked, scenario)
            assert not blocked.can_start(kind), (kind, scenario, "invalid start")
            before = blocked.assets()
            blocked.run(value(decision, "complete_effect"))
            assert blocked.assets() == before, (kind, scenario, "unguarded start effects")

            finishing = deepcopy(prepared[kind])
            finishing.start(kind)
            invalidate(finishing, scenario)
            before_finish = deepcopy(finishing)
            finishing.run(value(decision, "remove_effect"))
            expect_no_reward(before_finish, finishing, kind)
            if kind in DONE:
                assert DONE[kind] not in finishing.flags

            retry = deepcopy(prepared[kind])
            retry.start(kind)
            stock_after_start = retry.inventory("support_equipment")
            invalidate(retry, scenario)
            retry.advance(1)
            assert kind not in retry.active
            assert "JMC_" + kind + "_in_progress" not in retry.flags
            assert retry.inventory("support_equipment") == stock_after_start
            restore_eligibility(retry)
            assert retry.can_start(kind), (kind, scenario, "cancelled project cannot be retried")
            retry.start(kind)
            retry.advance(EXPECTED_DURATIONS[kind])
            assert kind not in retry.active
            if kind in DONE:
                assert DONE[kind] in retry.flags
            else:
                assert retry.inventory("convoy") == 6
            cases += 3

    # Choices already displayed are protected again at response time. A later
    # click or duplicate event cannot collect both rewards or both plans.
    for event_id, pending in pending_answers.items():
        options = [node for key, _, node in content["events"][event_id] if key == "option"]
        for index in range(len(options)):
            answered = deepcopy(pending)
            answered.answer(event_id, index)
            rewarded = answered.assets()
            for late_index in range(len(options)):
                answered.answer(event_id, late_index)
                assert answered.assets() == rewarded, (event_id, index, late_index, "repeat answer reward")
            if event_id == "jmc_maritime.1":
                assert answered.pp - pending.pp == (20 if index == 0 else 0)
                assert answered.xp["navy_experience"] - pending.xp["navy_experience"] == (0 if index == 0 else 5)
            if event_id == "jmc_maritime.5":
                assert len(answered.ideas & {"JMC_merchant_plan", "JMC_expedition_plan"}) == 1
                assert len(answered.flags & {"JMC_merchant_course", "JMC_expedition_course"}) == 1
                assert ("JMC_merchant_plan" in answered.ideas) == (index == 0)
            for scenario in invalid_states:
                stale = deepcopy(pending)
                invalidate(stale, scenario)
                before = stale.assets()
                stale.answer(event_id, index)
                assert stale.assets() == before, (event_id, scenario, "stale answer issued assets")
                if event_id in ("jmc_maritime.1", "jmc_maritime.5"):
                    assert not stale.test(value(content["events"][event_id], "trigger"))
                cases += 1
            cases += 1

    reserve = deepcopy(prepared["reserves"])
    reserve.start("reserves")
    reserve.advance(30)
    completed_day = reserve.day
    assert reserve.inventory("convoy") == 6
    assert reserve.pp == prepared["reserves"].pp - 45
    assert reserve.inventory("support_equipment") == 1000
    assert reserve.idea_expiry["JMC_ready_stores"] == completed_day + 90
    after_finish = reserve.assets()
    reserve.run(value(content["decisions"]["reserves"], "remove_effect"))
    assert reserve.assets() == after_finish, "duplicate reserve finish"
    reserve.advance(89)
    assert "JMC_ready_stores" in reserve.ideas
    assert not reserve.can_start("reserves")
    reserve.advance(1)
    assert "JMC_ready_stores" not in reserve.ideas
    reserve.advance(29)
    assert not reserve.can_start("reserves")
    reserve.advance(1)
    assert reserve.can_start("reserves"), "reserve cooldown never releases"
    reserve.start("reserves")
    reserve.advance(30)
    assert reserve.inventory("convoy") == 12
    assert reserve.pp == prepared["reserves"].pp - 90
    assert reserve.inventory("support_equipment") == 975
    cases += 3

    # A different country cannot use the programme even with copied flags/foci.
    assert not model.test(content["triggers"]["JMC_can_manage_programme"], "A01", "A01")
    return cases + 1


def validate():
    content = load()
    validate_references(content)
    cases = validate_lifecycles(content)
    print(f"PASS: {cases} maritime lifecycle scenarios; exact resource gates, project timers, "
          "cancel/retry, repeated finishes and delayed choices; bilingual references, "
          "equipment, sprites and engine names. No full engine campaign simulation.")


if __name__ == "__main__":
    validate()
