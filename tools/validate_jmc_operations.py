"""Exercise course-specific maritime work using the parsed production scripts."""
from copy import deepcopy
import re

from validate_jmc_maritime import Model, ROOT, load, read, validate_references, invalidate
from validate_philippines_rework import parse, value


PROJECTS = {
    "pilots": ("JMC_organise_pilot_service", "merchant", 40, 20, 30,
               "JMC_pilot_service", "jmc_operations.1"),
    "transports": ("JMC_prepare_transport_service", "expedition", 50, 40, 35,
                   "JMC_transport_service", "jmc_operations.2"),
}


def content_with_operations():
    content = load()
    for folder, target in (("decisions", "decisions"), ("scripted_triggers", "triggers"),
                           ("scripted_effects", "effects"), ("ideas", "ideas")):
        path = f"common/{folder}/JMC_operations.txt"
        tree = parse(read(path))
        content["trees"][path] = tree
        if target == "decisions":
            entries = dict((key, node) for _, _, category in tree for key, _, node in category)
            assert set(entries) == {spec[0] for spec in PROJECTS.values()}
            for kind, spec in PROJECTS.items():
                content[target][kind] = entries[spec[0]]
                content["decision_ids"][kind] = spec[0]
        else:
            if target == "ideas":
                tree = value(value(tree, "ideas"), "country")
            content[target].update((key, node) for key, _, node in tree)
    path = "events/JMC_operations.txt"
    tree = parse(read(path))
    content["trees"][path] = tree
    content["events"].update((value(node, "id"), node) for key, _, node in tree if key == "country_event")
    return content


def prepared(content, course):
    model = Model(content)
    model.flags.update(("JMC_programme_complete", "JMC_course_confirmed", f"JMC_{course}_course"))
    model.ideas.add(f"JMC_{course}_plan")
    return model


def main():
    content = content_with_operations()
    validate_references(content)
    localized = []
    for language in ("russian", "english"):
        path = ROOT / "localisation" / language / f"JMC_operations_l_{language}.yml"
        assert path.read_bytes().startswith(b"\xef\xbb\xbf")
        keys = re.findall(r'^\s+([^ :]+):\d+\s+".*"$', path.read_text(encoding="utf-8-sig"), re.M)
        assert len(keys) == len(set(keys)) == 14
        localized.append(set(keys))
    assert localized[0] == localized[1]
    cases = 0
    for kind, (_, course, cost, equipment, duration, idea, event) in PROJECTS.items():
        decision = content["decisions"][kind]
        assert value(decision, "fire_only_once") == "no"
        assert int(value(decision, "days_re_enable")) == 180
        assert int(value(decision, "days_remove")) == duration
        assert int(value(decision, "cost")) == cost
        base = prepared(content, course)
        assert base.can_start(kind)
        assert not prepared(content, "expedition" if course == "merchant" else "merchant").can_start(kind)
        # The provisional merchant plan must not unlock projects before the choice.
        for missing in ("JMC_programme_complete", "JMC_course_confirmed", f"JMC_{course}_course"):
            blocked = deepcopy(base)
            blocked.flags.remove(missing)
            assert not blocked.can_start(kind)
            cases += 1
        for amount in (0, equipment - 0.01, equipment, equipment + 0.01):
            gate = deepcopy(base)
            gate.stock["support_equipment_1"] = amount
            assert gate.can_start(kind) == (amount >= equipment)
            if amount >= equipment:
                gate.pp = cost
                gate.start(kind)
                assert gate.pp == 0 and abs(gate.inventory("support_equipment") - (amount - equipment)) < 1e-6
                gate.advance(duration)
                assert idea in gate.ideas  # No second equipment charge at completion.
            cases += 1
        poor = deepcopy(base)
        poor.pp = cost - 0.01
        assert not poor.can_start(kind)
        cases += 1

        success = deepcopy(base)
        success.start(kind)
        assert not success.can_start(kind)
        success.advance(duration - 1)
        assert idea not in success.ideas
        success.advance(1)
        assert idea in success.ideas and success.idea_expiry[idea] == success.day + 120
        assert success.queue == [(success.day + 1, event)]
        assert success.pp == base.pp - cost
        assert success.inventory("support_equipment") == 1000 - equipment
        after = success.assets()
        success.run(value(decision, "remove_effect"))
        assert success.assets() == after, (kind, "duplicate completion")
        success.advance(119)
        assert idea in success.ideas
        success.advance(1)
        assert idea not in success.ideas
        success.advance(59)
        assert not success.can_start(kind)
        success.advance(1)
        assert success.can_start(kind)
        success.start(kind)
        success.advance(duration)
        assert success.pp == base.pp - 2 * cost
        assert success.inventory("support_equipment") == 1000 - 2 * equipment
        cases += 4

        for scenario in ("annexed", "subject", "capitulated", "coast_lost", "course_lost", "plan_lost"):
            def disable(model):
                if scenario == "course_lost":
                    model.flags.remove(f"JMC_{course}_course")
                elif scenario == "plan_lost":
                    model.ideas.remove(f"JMC_{course}_plan")
                else:
                    invalidate(model, scenario)

            blocked = deepcopy(base)
            disable(blocked)
            assert not blocked.can_start(kind)
            before = blocked.assets()
            blocked.run(value(decision, "complete_effect"))
            assert blocked.assets() == before

            cancelled = deepcopy(base)
            cancelled.start(kind)
            disable(cancelled)
            before = cancelled.assets()
            cancelled.run(value(decision, "remove_effect"))
            assert idea not in cancelled.ideas and not cancelled.queue
            assert cancelled.pp == before[0] and dict(cancelled.stock) == before[1]
            assert f"JMC_{kind}_in_progress" not in cancelled.flags

            retry = deepcopy(base)
            retry.start(kind)
            disable(retry)
            retry.advance(1)
            assert kind not in retry.active and f"JMC_{kind}_in_progress" not in retry.flags
            retry.countries = set(base.countries)
            retry.subjects.clear()
            retry.capitulated.clear()
            retry.states = deepcopy(base.states)
            retry.flags = set(base.flags)
            retry.ideas = set(base.ideas)
            assert retry.can_start(kind)
            retry.start(kind)
            retry.advance(duration)
            assert idea in retry.ideas
            assert retry.pp == base.pp - 2 * cost
            assert retry.inventory("support_equipment") == 1000 - 2 * equipment

            stale_event = deepcopy(success)
            disable(stale_event)
            assert not stale_event.test(value(content["events"][event], "trigger"))
            cases += 4
        cases += 2
    print(f"PASS: {cases} course-specific maritime scenarios; resources, provisional plans, "
          "course locks, cancellation/retry, repeat rewards, expiry and cooldown; RU/EN and engine references.")


if __name__ == "__main__":
    main()
