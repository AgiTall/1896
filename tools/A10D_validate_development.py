"""Reference audit and bounded execution of actual Philippine supply/state scripts.

This does not simulate combat, AI scheduling or a complete HOI4 campaign.
"""
from pathlib import Path
import json
import re

R = Path(__file__).resolve().parents[1]
G = Path("D:/SteamLibrary/steamapps/common/Hearts of Iron IV")


def read(path):
    return path.read_text(encoding="utf-8-sig")


def parse(text):
    text = re.sub(r'#[^\n]*', '', text)
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[{}=<>]|[^\s{}=<>]+', text)
    pos = 0

    def block(nested=False):
        nonlocal pos
        out = []
        while pos < len(tokens) and tokens[pos] != "}":
            key = tokens[pos]
            pos += 1
            assert pos < len(tokens) and tokens[pos] in ("=", ">", "<"), (key, tokens[pos:pos+5])
            op = tokens[pos]
            pos += 1
            if tokens[pos] == "{":
                pos += 1
                val = block(True)
            else:
                val = tokens[pos]
                pos += 1
            out.append((key, op, val))
        if nested:
            assert pos < len(tokens) and tokens[pos] == "}", "unclosed block"
            pos += 1
        return out

    tree = block()
    assert pos == len(tokens), "unexpected closing brace"
    return tree


def value(node, key, default=None):
    return next((v for k, o, v in node if k == key), default)


def walk(node):
    for k, o, v in node:
        yield k, o, v
        if isinstance(v, list):
            yield from walk(v)


# Audit the playable tree. The earlier generator JSON omits five new focuses
# and still contains the retired gunboat school, so it is not the active schema.
economy_ids = {"A10D_" + name for name in (
    "island_census", "municipal_roads", "mail_ferries", "abaca_cooperatives",
    "sugar_inspectors", "timber_and_slipways", "provincial_workshops",
    "rice_granaries", "district_clinics", "normal_schools", "cable_cooperatives",
    "sanitary_commission", "island_polytechnic", "export_bureau",
    "national_market", "island_industry",
)}
military_ids = {"A10_coastal_arsenals", "A10_landing_plans"} | {
    "A10D_" + name for name in (
        "rifle_inspections", "coastal_boatyards", "common_calibres",
        "field_batteries", "harbour_defences", "sappers_and_pack_trains",
        "mountain_infantry", "chart_the_straits", "staff_college",
        "merchant_reserve", "ammunition_toolrooms", "signal_corps",
        "patrol_flotillas", "war_fleet",
    )
}
assert len(economy_ids) == len(military_ids) == 16
assert economy_ids.isdisjoint(military_ids)
all_focuses = [node for key, _, node in value(parse(read(R / "common/national_focus/a10_focus.txt")), "focus_tree") if key == "focus"]
development_nodes = [node for node in all_focuses if value(node, "id").startswith("A10D_") or value(node, "id") in {"A10_coastal_arsenals", "A10_landing_plans"}]
focuses = [{
    "id": value(node, "id"), "x": int(value(node, "x")),
    "y": int(value(node, "y")), "icon": value(node, "icon"),
    "prerequisites": [[parent for key, _, parent in group if key == "focus"]
                      for key, _, group in node if key == "prerequisite"],
    "mutually_exclusive": [other for key, _, group in node if key == "mutually_exclusive"
                           for child_key, _, other in group if child_key == "focus"],
    "reward": value(node, "completion_reward", []),
} for node in development_nodes]
fs = {f["id"]: f for f in focuses}
assert len(focuses) == len(fs) == 32
assert set(fs) == economy_ids | military_ids
assert len({(f["x"], f["y"]) for f in focuses}) == len(fs)
assert "A10_strike_japan" not in fs
openers = {"A10_confederation", "A10W_oath", "A10M_coup"}
for entry in ("A10D_island_census", "A10_coastal_arsenals"):
    assert len(fs[entry]["prerequisites"]) == 1
    assert set(fs[entry]["prerequisites"][0]) == openers
for f in focuses:
    assert not f["mutually_exclusive"]
    assert 4 <= f["y"] <= 21
    assert all(p in fs or p in openers for group in f["prerequisites"] for p in group)
    for group in f["prerequisites"]:
        for parent in group:
            if parent in fs:
                assert fs[parent]["y"] < f["y"], (f["id"], "parent not above", parent)
for seed in ("A10_island_congress", *sorted(openers)):
    reachable = {seed}
    while True:
        before = set(reachable)
        for f in focuses:
            if all(set(group) & reachable for group in f["prerequisites"]):
                reachable.add(f["id"])
        if reachable == before:
            break
    expected = {seed} if seed == "A10_island_congress" else set(fs) | {seed}
    assert reachable == expected, (seed, reachable ^ expected)

paths = [p for folder in ("common/scripted_effects", "common/scripted_triggers", "common/ideas", "common/decisions", "common/decisions/categories", "events") for p in (R / folder).glob("A10D*.txt")]
trees = {p.relative_to(R).as_posix(): parse(read(p)) for p in paths}
effects = dict((k, v) for k, o, v in trees["common/scripted_effects/A10D_development.txt"])
triggers = dict((k, v) for k, o, v in trees["common/scripted_triggers/A10D_development.txt"])
ideas = dict((k, v) for k, o, v in value(value(trees["common/ideas/A10D_development.txt"], "ideas"), "country"))
decisions = dict((k, v) for k, o, v in value(trees["common/decisions/A10D_development.txt"], "A10D_development"))
events = {value(v, "id"): v for k, o, v in trees["events/A10D_development.txt"] if k == "country_event"}
assert len(decisions) == 11 and len(events) == 6 and len(ideas) == 28
assert set(decisions).isdisjoint(fs)

# Locale keys remain separate from the root tree's focus localisations.
locs = {}
for lang in ("russian", "english"):
    p = R / f"localisation/{lang}/A10D_development_l_{lang}.yml"
    assert p.read_bytes().startswith(b"\xef\xbb\xbf")
    entries = re.findall(r'^ ([^ :]+):0 "(.*)"$', read(p), re.M)
    locs[lang] = dict(entries)
    assert len(entries) == len(locs[lang]), "duplicate locale key"
    assert all('"' not in text for key, text in entries)
assert set(locs["russian"]) == set(locs["english"])
for lang in locs:
    focus_locs = {
        key: text
        for path in (R / "localisation" / lang).rglob("*.yml")
        for key, text in re.findall(r'^\s+([^ :]+):\d+\s+"(.*)"\s*$', read(path), re.M)
    }
    for fid in fs:
        assert fid in focus_locs and fid + "_desc" in focus_locs, (lang, fid)
        assert len(focus_locs[fid + "_desc"]) > 60, (lang, fid, "short description")
for key in set(ideas) | set(decisions) | {"A10D_development"}:
    for lang in locs:
        assert key in locs[lang] and key + "_desc" in locs[lang], key

# Engine documentation and sprite files, rather than guessed modern identifiers.
engine_effects = set(re.findall(r'^## (\w+)\s*$', read(G / "documentation/effects_documentation.md"), re.M))
engine_triggers = set(re.findall(r'^## (\w+)\s*$', read(G / "documentation/triggers_documentation.md"), re.M))
engine_modifiers = set(re.findall(r'^## (\w+)\s*$', read(G / "documentation/modifiers_documentation.md"), re.M))
sprites = {}
for base in (G, R):
    for p in (base / "interface").rglob("*.gfx"):
        for m in re.finditer(r'spriteType\s*=\s*\{\s*name\s*=\s*"?([^"\s]+)"?[^}]*?texturefile\s*=\s*"([^"]+)"', read(p), re.S | re.I):
            sprites[m[1]] = m[2]


def sprite(name):
    assert name in sprites, ("missing sprite", name)
    assert any((base / sprites[name]).exists() for base in (R, G)), ("missing sprite texture", name)


techs = "\n".join(read(p) for p in (R / "common/technologies").glob("*.txt"))
equipment = "\n".join(read(p) for p in (R / "common/units/equipment").glob("*.txt"))
for f in focuses:
    sprite(f["icon"])
for node in [*trees.values(), *(f["reward"] for f in focuses)]:
    for k, o, v in walk(node):
        if k == "set_technology":
            for tech, _, amount in v:
                assert re.search(r'\b' + re.escape(tech) + r'\s*=\s*\{', techs), tech
        if k == "add_equipment_to_stockpile":
            typ = value(v, "type")
            assert re.search(r'\b' + re.escape(typ) + r'\s*=\s*\{', equipment), typ
        if k in ("add_ideas", "remove_ideas", "has_idea"):
            assert v in ideas, v
        if k == "add_timed_idea":
            assert value(v, "idea") in ideas
        if k in ("title", "desc") and isinstance(v, str):
            assert v in locs["russian"], v
        if k == "option":
            assert value(v, "name") in locs["russian"]
        if k == "picture":
            sprite(v if v.startswith("GFX_") else "GFX_idea_" + v)
        if k == "country_event" and isinstance(v, list):
            assert value(v, "id") in events
        if k in ("limit", "trigger", "available", "visible", "allowed"):
            for key, op, val in walk(v):
                if isinstance(val, list) and key in ("check_variable", "has_equipment"):
                    continue
                if key in ("A10D_supply", "convoy_1", "infantry_equipment") or key.isdigit():
                    continue
                assert key in engine_triggers or key in triggers or key in ("A10R_member_trigger", "A10R_archipelago_state_trigger", "AND", "OR", "NOT", "owner", "infrastructure"), ("unknown trigger", key)
        if k.startswith("A10D_") and v == "yes":
            assert k in effects or k in triggers, k
for key, node in ideas.items():
    for mod, op, val in value(node, "modifier"):
        assert mod in engine_modifiers or re.fullmatch(r'production_speed_(dockyard|industrial_complex)_factor', mod), mod
sprite("GFX_decision_category_generic_naval")
sprite("GFX_decision_generic_political_discourse")


class Model:
    """Run only the documented effects used by the supply and guarded state tests."""
    def __init__(self):
        self.vars = {"A10D_supply": 35}
        self.flags = set()
        self.ideas = set()
        self.states = {
            "1084": dict(owner="A10", controller="A10", coastal=True, infrastructure=2),
            "624": dict(owner="PVI", controller="PVI", coastal=True, infrastructure=2),
            "628": dict(owner="A03", controller="A03", coastal=True, infrastructure=2),
            "625": dict(owner="PSM", controller="A03", coastal=True, infrastructure=2),
            "327": dict(owner="A03", controller="A10", coastal=True, infrastructure=2),
            "647": dict(owner="A10", controller="A10", coastal=True, infrastructure=2),
        }
        self.subjects = {"PVI", "PSM"}
        self.buildings = []
        self.queue = []

    def test(self, node, scope="A10"):
        results = []
        for k, o, v in node:
            if k == "OR":
                ok = any(self.test([entry], scope) for entry in v)
            elif k == "NOT":
                ok = not self.test(v, scope)
            elif k == "AND":
                ok = self.test(v, scope)
            elif k in self.states:
                ok = self.test(v, k)
            elif k == "owner":
                ok = self.test(v, self.states[scope]["owner"])
            elif k == "tag":
                ok = scope == v
            elif k == "has_country_flag":
                ok = v in self.flags
            elif k == "check_variable":
                name, comp, amount = v[0]
                actual = self.vars.get(name, 0)
                ok = actual < float(amount) if comp == "<" else actual > float(amount) if comp == ">" else actual == float(amount)
            elif k == "is_owned_by":
                ok = self.states[scope]["owner"] == v
            elif k == "is_controlled_by":
                country = self.states[scope]["owner"] if v == "OWNER" else v
                ok = self.states[scope]["controller"] == country
            elif k == "is_subject_of":
                ok = v == "A10" and scope in self.subjects
            elif k == "is_coastal":
                ok = self.states[scope]["coastal"] == (v == "yes")
            elif k == "infrastructure":
                ok = self.states[scope]["infrastructure"] < int(v) if o == "<" else self.states[scope]["infrastructure"] > int(v)
            elif k == "A10R_member_trigger":
                ok = scope in {"PVI", "PSM", "PMD", "PNM", "PCB", "PPN", "PNL", "PML", "PBT"}
            elif k == "A10R_archipelago_state_trigger":
                ok = scope in {"1084", "624", "625", "627", "1026", "628", "1085", "623", "327", "1027", "626", "1025"}
            elif k in triggers:
                ok = self.test(triggers[k], scope)
            elif k == "has_capitulated":
                ok = v == "no"
            else:
                raise AssertionError(("unmodelled trigger", k))
            results.append(ok)
        return all(results)

    def run(self, node, scope="A10"):
        previous = False
        for k, o, v in node:
            if k == "if":
                previous = self.test(value(v, "limit", []), scope)
                if previous:
                    self.run([entry for entry in v if entry[0] != "limit"], scope)
            elif k == "else_if":
                if not previous:
                    previous = self.test(value(v, "limit", []), scope)
                    if previous:
                        self.run([entry for entry in v if entry[0] != "limit"], scope)
            elif k == "else":
                if not previous:
                    self.run(v, scope)
            elif k in effects:
                self.run(effects[k], scope)
            elif k == "set_variable":
                self.vars[v[0][0]] = float(v[0][2])
            elif k in ("add_to_variable", "subtract_from_variable"):
                self.vars[v[0][0]] += float(v[0][2]) * (-1 if k.startswith("subtract") else 1)
            elif k == "clamp_variable":
                name = value(v, "var")
                self.vars[name] = max(float(value(v, "min")), min(float(value(v, "max")), self.vars[name]))
            elif k == "set_country_flag":
                self.flags.add(v)
            elif k == "add_ideas":
                self.ideas.add(v)
            elif k == "remove_ideas":
                self.ideas.discard(v)
            elif k == "country_event":
                self.queue.append(value(v, "id"))
            elif k in self.states:
                self.run(v, k)
            elif k == "random_state":
                for state in self.states:
                    if self.test(value(v, "limit", []), state):
                        self.run([entry for entry in v if entry[0] != "limit"], state)
                        break
            elif k == "add_extra_state_shared_building_slots":
                pass
            elif k == "add_building_construction":
                typ = value(v, "type")
                self.buildings.append((scope, typ, int(value(v, "level"))))
                if typ == "infrastructure":
                    self.states[scope]["infrastructure"] += int(value(v, "level"))
            elif k in ("navy_experience", "army_experience", "add_stability", "add_political_power", "add_equipment_to_stockpile", "add_timed_idea", "add_war_support"):
                pass  # Not claimed as modelled by the bounded supply/state checks.
            else:
                raise AssertionError(("unmodelled effect", k))


# Supply boundaries, idempotent startup, and repeatable recovery from zero.
tiers = {"A10D_shipping_shortage", "A10D_strained_shipping", "A10D_reliable_shipping"}
for supply in (-100, -1, 0, 19, 19.99, 20, 35, 49.99, 50, 79, 79.99, 80, 100, 101, 1000):
    m = Model()
    m.vars["A10D_supply"] = supply
    m.ideas.update(tiers)
    m.run(effects["A10D_refresh_supply"])
    actual = max(0, min(100, supply))
    assert m.vars["A10D_supply"] == actual
    expected = {"A10D_shipping_shortage"} if actual < 20 else {"A10D_strained_shipping"} if actual < 50 else {"A10D_reliable_shipping"} if actual >= 80 else set()
    assert m.ideas & tiers == expected, (supply, m.ideas)
    m.run(effects["A10D_refresh_supply"])
    assert m.ideas & tiers == expected
m = Model()
m.run(effects["A10D_initialize"])
m.vars["A10D_supply"] = 63
m.run(effects["A10D_initialize"])
assert m.vars["A10D_supply"] == 63 and len(m.queue) == 2
m.vars["A10D_supply"] = 0
for _ in range(5):
    m.run(value(decisions["A10D_hire_coastal_boats"], "remove_effect"))
assert m.vars["A10D_supply"] == 60 and not (m.ideas & tiers)

# Actual territory guards: owned/controlled core and released subject are safe;
# Japanese ownership, occupation, occupied member and non-Philippine state are not.
m = Model()
assert {s for s in m.states if m.test(triggers["A10D_eligible_state_trigger"], s)} == {"1084", "624"}
for name in ("A10D_build_cebu_workshops", "A10D_build_visayan_factory", "A10D_build_market_factory", "A10D_build_arsenal", "A10D_build_toolroom", "A10D_build_boatyard", "A10D_build_second_boatyard", "A10D_build_roads", "A10D_fortify_harbours"):
    m.run(effects[name])
assert {s for s, _, _ in m.buildings} <= {"1084", "624"}
assert any(s == "624" and typ == "industrial_complex" for s, typ, _ in m.buildings)
m.states["1084"]["controller"] = "A03"
m.subjects.clear()
before = len(m.buildings)
for name in ("A10D_build_arsenal", "A10D_build_cebu_workshops", "A10D_fortify_harbours"):
    m.run(effects[name])
assert len(m.buildings) == before, "No factories for foreign or occupied owners"

# Repeatable actions have concrete costs and cooldowns and cannot farm permanent assets.
for key, node in decisions.items():
    assert int(value(node, "cost")) >= 30 and int(value(node, "days_remove")) >= 21
    assert int(value(node, "days_re_enable")) >= 60
    names = {k for k, o, v in walk(node)}
    assert not names & {"add_building_construction", "add_research_slot"}
    assert "WTC_debt" not in str(node)
    assert "add_ideas" not in names, "repeatable permanent spirit"
for event in events.values():
    options = [v for k, o, v in event if k == "option"]
    assert any(value(option, "trigger") is None for option in options), "No affordable fallback"
    for option in options:
        costs = [float(v) for k, o, v in option if k == "add_political_power" and float(v) < 0]
        if costs:
            gate = value(option, "trigger", [])
            assert any(k == "has_political_power" and float(v) >= -min(costs) - 1 for k, o, v in gate)
assert all("WTC_debt" not in read(p) for p in paths)

result = dict(focuses=len(fs), focus_groups={"economy": len(economy_ids), "military": len(military_ids)},
              focus_source="common/national_focus/a10_focus.txt", ideas=28, decisions=11, events=6, localisation_keys=len(locs["russian"]),
              political_openers=sorted(openers), congress_alone_unlocks_development=False,
              supply_boundaries="passed", safe_state_scope="passed", repeated_recovery="passed",
              startup_idempotence="passed", sprites_and_technology="passed", engine_campaign_tested=False)
(R / "tools/A10D_development_validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
print("PASS: 32 active focuses (16 economy, 16 military) reachable from each political opener and none from Congress alone; documented modifiers, real sprites/equipment/technologies; bilingual BOM localisation; supply boundaries and startup idempotence; repeated recovery from zero; owned/controlled state and subject guards; priced cooldown decisions; affordable event fallbacks. No combat or full engine campaign simulation.")
