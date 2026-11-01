"""Bounded scenarios executing the actual republican scripts and decision gates.

The interpreter models cohesion, sovereignty, consent, cores and the monthly
dispatcher. It does not model combat, AI timing, economy or every engine feature.
"""
from pathlib import Path
from collections import defaultdict
from copy import deepcopy
import json
from validate_philippines_rework import parse, value, walk

R = Path(__file__).resolve().parents[1]
MEMBERS = dict(PVI=624, PSM=625, PCB=628, PPN=1085, PMD=627, PNM=1026, PNL=623, PML=327, PBT=1027)


def read(path):
    return parse((R / path).read_text(encoding="utf-8-sig"))


EFFECTS = {k: v for k, o, v in read("common/scripted_effects/A10R_republics.txt")}
TRIGGERS = {k: v for k, o, v in read("common/scripted_triggers/A10R_republics.txt")}
EVENTS = {value(v, "id"): v for k, o, v in read("events/A10R_republics.txt") if k == "country_event"}
DECISIONS = {k: v for k, o, v in value(read("common/decisions/A10R_ratification.txt"), "A10R_federal_ratification")}
LEGACY = {k: v for k, o, v in value(read("common/decisions/A10_philippines.txt"), "A10_integration")}
FOCUSES = {value(v, "id"): v for k, o, v in value(read("common/national_focus/a10_focus.txt"), "focus_tree") if k == "focus"}
MONTHLY = value(value(read("common/on_actions/A10R_republics.txt"), "on_actions"), "on_monthly")


class Model:
    def __init__(self):
        self.tags = {"A10", "A03", *MEMBERS}
        self.vars = defaultdict(dict)
        self.vars["A10"].update(A10R_cohesion=60, A10R_federal_votes=0)
        self.flags = defaultdict(set)
        self.flags["A10"].add("A10_confederal_path")
        self.flag_expiry = {}
        self.ideas = defaultdict(set)
        self.completed = defaultdict(set)
        self.overlords = {tag: "A10" for tag in MEMBERS}
        self.states = {str(s): dict(owner=t, controller=t, cores={t}, compliance=10) for t, s in MEMBERS.items()}
        self.states["1084"] = dict(owner="A10", controller="A10", cores={"A10"}, compliance=100)
        self.wars = set()
        self.capitulated = set()
        self.queue = []
        self.calls = defaultdict(int)
        self.pp = defaultdict(lambda: 1000)
        self.day = 0
        self.annexations = []

    def compare(self, left, op, right):
        return {"=": left == right, "<": left < right, ">": left > right, "<=": left <= right, ">=": left >= right}[op]

    def test(self, node, scope="A10"):
        out = []
        for k, op, v in node:
            if k in ("AND", "hidden_trigger"):
                result = self.test(v, scope)
            elif k == "OR":
                result = any(self.test([part], scope) for part in v)
            elif k == "NOT":
                result = not self.test(v, scope)
            elif k in self.tags or k in self.states:
                result = self.test(v, k)
            elif k in MEMBERS or k == "A03":
                result = False  # A scoped country that has ceased to exist.
            elif k in TRIGGERS:
                result = self.test(TRIGGERS[k], scope)
            elif k == "tag":
                result = scope == v
            elif k == "state":
                result = scope == v
            elif k == "exists":
                result = (scope in self.tags) == (v == "yes")
            elif k == "country_exists":
                result = v in self.tags
            elif k == "has_country_flag":
                result = v in self.flags[scope]
            elif k == "has_idea":
                result = v in self.ideas[scope]
            elif k == "has_completed_focus":
                result = v in self.completed[scope]
            elif k == "check_variable":
                name, comp, amount = v[0]
                result = self.compare(self.vars[scope].get(name, 0), comp, float(amount))
            elif k == "has_war":
                result = any(scope in war for war in self.wars) == (v == "yes")
            elif k == "has_capitulated":
                result = (scope in self.capitulated) == (v == "yes")
            elif k == "is_subject_of":
                result = self.overlords.get(scope) == v
            elif k == "any_subject_country":
                result = any(self.test(v, country) for country, lord in self.overlords.items() if lord == scope and country in self.tags)
            elif k == "any_owned_state":
                result = any(self.test(v, state) for state, data in self.states.items() if data["owner"] == scope)
            elif k in ("owns_state", "controls_state"):
                result = self.states[v]["owner" if k == "owns_state" else "controller"] == scope
            elif k in ("is_owned_by", "is_controlled_by"):
                result = self.states[scope]["owner" if k == "is_owned_by" else "controller"] == v
            elif k == "is_core_of":
                result = v in self.states[scope]["cores"]
            elif k == "compliance":
                result = self.compare(self.states[scope]["compliance"], op, float(v))
            elif k == "has_political_power":
                result = self.compare(self.pp[scope], op, float(v))
            else:
                raise AssertionError(("Unmodelled trigger", scope, k))
            out.append(result)
        return all(out)

    def run(self, node, scope="A10"):
        previous = False
        for k, op, v in node:
            if k == "if":
                previous = self.test(value(v, "limit", []), scope)
                if previous:
                    self.run([part for part in v if part[0] != "limit"], scope)
            elif k == "else_if":
                if not previous:
                    previous = self.test(value(v, "limit", []), scope)
                    if previous:
                        self.run([part for part in v if part[0] != "limit"], scope)
            elif k == "else":
                if not previous:
                    self.run(v, scope)
            elif k in self.tags or k in self.states:
                self.run(v, k)
            elif k in EFFECTS:
                self.calls[k] += 1
                self.run(EFFECTS[k], scope)
            elif k == "add_to_variable":
                name, comp, amount = v[0]
                self.vars[scope][name] = self.vars[scope].get(name, 0) + float(amount)
            elif k == "clamp_variable":
                name = value(v, "var")
                self.vars[scope][name] = min(float(value(v, "max")), max(float(value(v, "min")), self.vars[scope][name]))
            elif k == "set_country_flag":
                name = value(v, "flag") if isinstance(v, list) else v
                self.flags[scope].add(name)
                if isinstance(v, list):
                    self.flag_expiry[scope, name] = self.day + int(value(v, "days"))
            elif k == "clr_country_flag":
                self.flags[scope].discard(v)
            elif k == "add_ideas":
                self.ideas[scope].add(v)
            elif k == "remove_ideas":
                self.ideas[scope].discard(v)
            elif k == "country_event":
                self.queue.append((scope, value(v, "id")))
            elif k == "add_core_of":
                self.states[scope]["cores"].add(v)
            elif k == "every_owned_state":
                for state, data in self.states.items():
                    if data["owner"] == scope and self.test(value(v, "limit", []), state):
                        self.run([part for part in v if part[0] != "limit"], state)
            elif k == "annex_country":
                target = value(v, "target")
                assert target in self.tags and self.overlords.get(target) == scope
                self.annexations.append((scope, target))
                for data in self.states.values():
                    if data["owner"] == target:
                        data["owner"] = scope
                        if data["controller"] == target:
                            data["controller"] = scope
                self.tags.remove(target)
                self.overlords.pop(target)
            elif k == "add_political_power":
                self.pp[scope] += float(v)
            elif k in ("add_stability", "add_timed_idea"):
                pass  # Neither is included in this model's claims.
            else:
                raise AssertionError(("Unmodelled effect", scope, k))

    def advance(self, days):
        self.day += days
        for (tag, flag), expiry in list(self.flag_expiry.items()):
            if expiry <= self.day:
                self.flags[tag].discard(flag)
                del self.flag_expiry[tag, flag]

    def decide(self, key, legacy=False):
        node = (LEGACY if legacy else DECISIONS)[key]
        if not self.test(value(node, "visible", [])) or not self.test(value(node, "available", [])):
            return False
        self.pp["A10"] -= float(value(node, "cost", 0))
        self.run(value(node, "complete_effect", []))
        return True

    def fire(self, event, choice, country):
        node = EVENTS[event]
        if not self.test(value(node, "trigger", []), country):
            return False
        options = [v for k, o, v in node if k == "option"]
        option = options[choice]
        if not self.test(value(option, "trigger", []), country):
            return False
        self.run([part for part in option if part[0] not in ("name", "ai_chance", "trigger")], country)
        return True


def test_cohesion_and_dispatch():
    for cohesion in (-20, 0, 24, 34, 35, 74, 75, 100, 120):
        m = Model()
        m.vars["A10"]["A10R_cohesion"] = cohesion
        m.run(EFFECTS["A10R_refresh"])
        bounded = max(0, min(100, cohesion))
        assert m.vars["A10"]["A10R_cohesion"] == bounded
        assert ("A10R_fractured_council" in m.ideas["A10"]) == (bounded < 35)
        assert ("A10R_trusted_council" in m.ideas["A10"]) == (bounded >= 75)
    for war in (False, True):
        for treasury in (False, True):
            for transition in (False, True):
                for parliament in (False, True):
                    m = Model()
                    if war:
                        m.wars.add(frozenset(("A10", "A03")))
                    if treasury:
                        m.ideas["A10"].add("A10R_common_treasury_spirit")
                    if transition:
                        m.flags["A10"].add("A10R_federal_transition")
                    if parliament:
                        m.completed["A10"].add("A10R_federal_parliament")
                    for tag in sorted(m.tags):
                        m.run(value(MONTHLY, "effect"), tag)
                    expected = 60 + (-2 if war else 1) + int(treasury) - int(transition and not parliament)
                    assert m.vars["A10"]["A10R_cohesion"] == expected, (war, treasury, transition, parliament)
                    assert m.calls["A10R_monthly"] == 1, "Country loop must call A10 exactly once"
    for alternate in ("A10M_active", "A10W_oath_accepted"):
        m = Model()
        m.flags["A10"].add(alternate)
        m.ideas["A10"].update(("A10R_fractured_council", "A10R_trusted_council"))
        m.run(EFFECTS["A10R_monthly"])
        assert m.vars["A10"]["A10R_cohesion"] == 60
        assert not {"A10R_fractured_council", "A10R_trusted_council"} & m.ideas["A10"]
    m = Model()
    m.vars["A10"]["A10R_cohesion"] = 20
    m.run(EFFECTS["A10R_monthly"])
    m.run(EFFECTS["A10R_monthly"])
    assert m.queue.count(("A10", "A10R_congress.10")) == 1
    m.advance(120)
    m.run(EFFECTS["A10R_monthly"])
    assert m.queue.count(("A10", "A10R_congress.10")) == 2


def test_ratifications():
    for i, (tag, state) in enumerate(MEMBERS.items(), 20):
        m = Model()
        m.flags["A10"].update(("A10R_federal_transition", "A10R_federal_guarantees"))
        before = deepcopy(m.states)
        assert m.decide("A10R_request_" + tag)
        assert (tag, f"A10R_congress.{i}") in m.queue
        assert m.fire(f"A10R_congress.{i}", 0, tag)
        assert m.states == before, "A vote is not an annexation"
        assert m.vars["A10"]["A10R_federal_votes"] == 1
        assert m.test(TRIGGERS["A10R_republic_has_consented"], tag)
        assert all(not m.test(TRIGGERS["A10R_republic_has_consented"], other) for other in MEMBERS if other != tag)
        assert m.fire(f"A10R_congress.{i}", 0, tag)
        assert m.vars["A10"]["A10R_federal_votes"] == 1, "Duplicate answers must not create extra votes"
        m.flags["A10"].update(("A10_federal_path", "A10R_equal_rights"))
        assert m.decide("A10R_accession_" + tag)
        assert tag not in m.tags and m.states[str(state)]["owner"] == "A10"
        assert "A10" in m.states[str(state)]["cores"]
        for other, data in before.items():
            if other != str(state):
                assert m.states[other] == data, "Accession modified a different republic"
        m = Model()
        m.flags["A10"].update(("A10R_federal_transition", "A10R_federal_guarantees"))
        before = deepcopy(m.states)
        assert m.fire(f"A10R_congress.{i}", 1, tag)
        assert not m.test(TRIGGERS["A10R_republic_has_consented"], tag)
        assert m.states == before and tag in m.tags and m.vars["A10"]["A10R_federal_votes"] == 0
        assert not m.decide("A10R_request_" + tag), "Refusal cooldown must prevent immediate re-petition"
        m.advance(150)
        assert m.decide("A10R_request_" + tag)
        m.overlords.pop(tag)
        assert not m.fire(f"A10R_congress.{i}", 0, tag), "Foreign independent country received a ratification"
        assert not m.decide("A10R_accession_" + tag)
        assert m.states == before
    for reason in ("occupied", "foreign_overlord", "no_consent", "war"):
        m = Model()
        m.flags["A10"].update(("A10R_federal_transition", "A10R_equal_rights", "A10_federal_path", "A10R_consent_PVI"))
        if reason == "occupied":
            m.states["624"]["controller"] = "A03"
        elif reason == "foreign_overlord":
            m.overlords["PVI"] = "A03"
        elif reason == "no_consent":
            m.flags["A10"].discard("A10R_consent_PVI")
        else:
            m.wars.add(frozenset(("A10", "A03")))
        before = deepcopy(m.states)
        assert not m.decide("A10R_accession_PVI"), reason
        assert m.states == before and not m.annexations


def test_quorum():
    gate = value(FOCUSES["A10_federation"], "available")
    for population in (0, 1, 2, 3, 6, 9):
        for votes in range(population + 1):
            m = Model()
            active = list(MEMBERS)[:population]
            m.overlords = {tag: "A10" for tag in active}
            m.flags["A10"].update("A10R_consent_" + tag for tag in active[:votes])
            m.vars["A10"]["A10R_federal_votes"] = votes
            assert m.test(gate) == (votes >= 3 or votes == population), (population, votes)
            m.vars["A10"]["A10R_cohesion"] = 39
            assert not m.test(gate), "Quorum cannot waive the cohesion gate"


def test_local_consultations():
    pending = []
    for tag, state in MEMBERS.items():
        key = "A10R_local_vote_" + tag
        if key not in DECISIONS:
            pending.append(key)
            continue
        m = Model()
        m.tags.remove(tag)
        m.overlords.pop(tag)
        m.states[str(state)].update(owner="A10", controller="A10", compliance=59.99)
        m.flags["A10"].update(("A10R_federal_transition", "A10R_federal_guarantees"))
        assert not m.decide(key), "Local vote below 60 compliance"
        m.states[str(state)]["compliance"] = 60
        assert m.decide(key), (key, "60 percent should permit consultation")
        assert m.vars["A10"]["A10R_federal_votes"] == 1
        assert "A10R_consent_" + tag in m.flags["A10"]
        assert not m.decide(key), "A local vote cannot be repeated"
        for compliance in (79.99, 80):
            m.states[str(state)]["compliance"] = compliance
            assert not m.decide("A10_integrate_" + str(state), legacy=True), "Equal citizenship is required"
            m.flags["A10"].add("A10R_equal_rights")
            allowed = m.decide("A10_integrate_" + str(state), legacy=True)
            assert allowed == (compliance >= 80), "Exact 80 percent integration boundary"
            m.flags["A10"].discard("A10R_equal_rights")
        m = Model()
        m.tags.remove(tag)
        m.overlords.pop(tag)
        m.flags["A10"].update(("A10R_federal_transition", "A10R_federal_guarantees", "A10R_equal_rights"))
        m.states[str(state)].update(owner="A10", controller="A10", compliance=100)
        assert not m.decide("A10_integrate_" + str(state), legacy=True), "No integration without separate consent"
        m.states[str(state)]["controller"] = "A03"
        assert not m.decide(key), "Occupied state cannot vote"
        m.states[str(state)].update(owner="A03", controller="A03")
        assert not m.decide(key), "Foreign state cannot vote"
    return pending


def main():
    test_cohesion_and_dispatch()
    test_ratifications()
    test_quorum()
    pending = test_local_consultations()
    report = dict(monthly_scenarios=16, integer_cohesion_boundaries=9, ratifications=9,
                  guarded_annexation_failures=4, quorum_populations=[0, 1, 2, 3, 6, 9],
                  pending_local_consultations=pending,
                  checks=["country dispatcher calls A10 once", "war/treasury/transition/parliament effects", "crisis cooldown expires", "cohesion bounds and tier spirits", "nine successful and refused votes", "idempotent votes", "separate consent trigger", "foreign sovereignty and occupation preserved", "federation quorum"],
                  engine_campaign_tested=False)
    if not pending:
        report["checks"].extend(("nine local consultations", "60 percent local-vote boundary", "consent and equal rights protect legacy cores", "80 percent integration boundary"))
    (R / "tools/philippines_republics_test_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    assert not pending, ("Local-vote source patch not generated yet", pending)
    print("PASS: actual monthly effects, country dispatcher, cohesion bounds, crisis cooldown, nine consent/refusal/accession scenarios, sovereignty guards, idempotent votes, federation quorum and local consultation/integration gates. No combat or full engine simulation.")


if __name__ == "__main__":
    main()
