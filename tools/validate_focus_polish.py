"""Check focus paths and research rewards against the active technology set.

The path check models prerequisites and exclusions, not campaign availability,
timers, ownership changes or AI scheduling. No game files are changed.
"""
from collections import Counter
from functools import lru_cache
from itertools import product
from pathlib import Path

from validate_philippines_rework import parse, value, walk

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return parse(path.read_text(encoding="utf-8-sig"))


def validate():
    technologies = {}
    category_members = Counter()
    for path in (ROOT / "common/technologies").glob("*.txt"):
        for tech_id, _, node in value(read(path), "technologies", []):
            if not isinstance(node, list):
                continue  # Script constants share the technology container.
            technologies[tech_id] = node
            for key, _, categories in node:
                if key == "categories":
                    category_members.update(name for name, _, _ in categories)

    declared_categories = {
        category
        for path in (ROOT / "common/technology_tags").glob("*.txt")
        for category, _, _ in value(read(path), "technology_categories", [])
    }
    total_focuses = 0
    total_bonuses = 0
    all_ids = set()
    for path in sorted((ROOT / "common/national_focus").glob("*.txt")):
        tree = value(read(path), "focus_tree")
        nodes = [node for key, _, node in tree if key == "focus"]
        focuses = {value(node, "id"): node for node in nodes}
        assert len(focuses) == len(nodes), (path.name, "duplicate focus ID")
        assert not (all_ids & focuses.keys()), (path.name, "cross-tree duplicate focus ID")
        all_ids.update(focuses)
        prerequisites = {
            fid: [{parent for key, _, parent in group if key == "focus"}
                  for key, _, group in node if key == "prerequisite"]
            for fid, node in focuses.items()
        }
        exclusions = {
            fid: {other for key, _, group in node if key == "mutually_exclusive"
                  for child_key, _, other in group if child_key == "focus"}
            for fid, node in focuses.items()
        }
        for fid in focuses:
            for group in prerequisites[fid]:
                assert group, (fid, "empty prerequisite group")
                assert group <= focuses.keys(), (fid, "missing prerequisite", group - focuses.keys())
            for other in exclusions[fid]:
                assert other in focuses, (fid, "missing excluded focus", other)
                assert fid in exclusions[other], (fid, "asymmetric exclusion", other)

        visiting = set()

        @lru_cache(None)
        def paths_to(fid):
            assert fid not in visiting, (fid, "prerequisite cycle")
            visiting.add(fid)
            alternatives = [
                [path for parent in group for path in paths_to(parent)]
                for group in prerequisites[fid]
            ]
            valid = []
            for combination in product(*alternatives):
                completed = frozenset({fid}.union(*combination))
                if any(exclusions[done] & completed for done in completed):
                    continue
                # Supersets cannot rescue an already incompatible prerequisite route.
                if any(path <= completed for path in valid):
                    continue
                valid = [path for path in valid if not completed < path]
                valid.append(completed)
            visiting.remove(fid)
            return tuple(valid)

        for fid, node in focuses.items():
            assert paths_to(fid), (fid, "all prerequisite routes exclude this focus")
            for key, _, bonus in walk(value(node, "completion_reward", [])):
                if key != "add_tech_bonus":
                    continue
                total_bonuses += 1
                for target, _, name in bonus:
                    if target == "category":
                        assert name in declared_categories, (fid, "undeclared research category", name)
                        assert category_members[name], (fid, "research category has no technologies", name)
                    elif target == "technology":
                        assert name in technologies, (fid, "missing bonus technology", name)
        total_focuses += len(focuses)

    print(f"PASS: {total_focuses} focuses have reachable prerequisite routes and reciprocal exclusions; "
          f"{total_bonuses} research rewards match active technologies.")


if __name__ == "__main__":
    validate()
