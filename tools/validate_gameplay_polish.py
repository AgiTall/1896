"""Execute Japanese protectorate offers across delayed diplomacy changes.

This bounded model checks the actual script guards and effects. It does not
simulate AI acceptance, diplomacy modifiers or a running game campaign.
"""
from copy import deepcopy
from pathlib import Path

from validate_philippines_rework import parse, value

ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return parse((ROOT / relative).read_text(encoding="utf-8-sig"))


TRIGGERS = dict((key, node) for key, _, node in read("common/scripted_triggers/JSM_story.txt"))
DECISIONS = dict((key, node) for key, _, node in value(read("common/decisions/JSM_story.txt"), "JSM_subordination"))
EVENT = next(node for key, _, node in read("events/JSM_story.txt") if key == "country_event")
OPTIONS = [node for key, _, node in EVENT if key == "option"]


class Model:
    def __init__(self):
        self.countries = {"A03", "A08", "A10", "A01", "XYZ"}
        self.overlords = {}
        self.wars = set()
        self.queue = []
        self.goals = []

    def test(self, node, tag):
        results = []
        for key, _, val in node:
            if key in TRIGGERS:
                result = self.test(TRIGGERS[key], tag) == (val == "yes")
            elif key in {"A03", "A08", "A10", "A01", "XYZ"}:
                result = self.test(val, key)
            elif key == "NOT":
                result = not self.test(val, tag)
            elif key == "tag":
                result = tag == val
            elif key == "country_exists":
                result = val in self.countries
            elif key == "exists":
                result = (tag in self.countries) == (val == "yes")
            elif key == "is_subject":
                result = (tag in self.overlords) == (val == "yes")
            elif key == "has_war":
                result = any(tag in war for war in self.wars) == (val == "yes")
            else:
                raise AssertionError(("Unmodelled trigger", key))
            results.append(result)
        return all(results)

    def run(self, node, tag, root=None):
        root = root or tag
        for key, _, val in node:
            if key == "if":
                if self.test(value(val, "limit"), tag):
                    self.run([entry for entry in val if entry[0] != "limit"], tag, root)
            elif key in {"A03", "A08", "A10", "A01"}:
                self.run(val, key, root)
            elif key == "country_event":
                self.queue.append((tag, value(val, "id")))
            elif key == "puppet":
                assert val == "ROOT"
                self.overlords[root] = tag
            elif key == "create_wargoal":
                assert value(val, "target") == "ROOT"
                self.goals.append((tag, root, value(val, "type")))
            elif key not in {"name", "ai_chance"}:
                raise AssertionError(("Unmodelled effect", key))


def invalidate(model, target, scenario):
    if scenario == "target_annexed":
        model.countries.remove(target)
    elif scenario == "japan_annexed":
        model.countries.remove("A03")
    elif scenario == "target_subject":
        model.overlords[target] = "XYZ"
    elif scenario == "japan_subject":
        model.overlords["A03"] = "XYZ"
    elif scenario == "target_war":
        model.wars.add(frozenset((target, "XYZ")))
    elif scenario == "japan_war":
        model.wars.add(frozenset(("A03", "XYZ")))
    else:
        raise AssertionError(scenario)


def validate():
    scenarios = ("target_annexed", "japan_annexed", "target_subject", "japan_subject", "target_war", "japan_war")
    cases = 0
    for target in ("A08", "A10", "A01"):
        decision = DECISIONS["JSM_offer_" + target]
        model = Model()
        assert model.test(value(decision, "available"), "A03")
        assert not model.test(value(decision, "cancel_trigger"), "A03")
        model.run(value(decision, "remove_effect"), "A03")
        assert model.queue == [(target, "jsm_story.1")]
        assert model.test(value(EVENT, "trigger"), target)
        accepted = deepcopy(model)
        accepted.run(OPTIONS[0], target)
        assert accepted.overlords[target] == "A03"
        refused = deepcopy(model)
        refused.run(OPTIONS[1], target)
        assert refused.goals == [("A03", target, "puppet_wargoal_focus")]
        cases += 2

        for scenario in scenarios:
            changed = Model()
            invalidate(changed, target, scenario)
            assert not changed.test(value(decision, "available"), "A03"), (target, scenario)
            assert changed.test(value(decision, "cancel_trigger"), "A03"), (target, scenario)
            changed.run(value(decision, "remove_effect"), "A03")
            assert not changed.queue, (target, scenario, "invalid negotiation queued an event")
            assert not changed.test(value(EVENT, "trigger"), target), (target, scenario)
            # Also cover a response already displayed when diplomacy changes.
            for option in OPTIONS:
                stale = deepcopy(changed)
                original_overlords = dict(stale.overlords)
                stale.run(option, target)
                assert stale.overlords == original_overlords and not stale.goals, (target, scenario)
                cases += 1
    print(f"PASS: {cases} protectorate response scenarios; delayed offers respect existence, sovereignty and peace.")


if __name__ == "__main__":
    validate()
