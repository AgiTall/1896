"""Validate the new Dutch army and the start of industrialisation."""
from pathlib import Path
import re
import sys
from add_canon_countries import parse, value

R = Path(__file__).resolve().parents[1]
def read(path): return (R/path).read_text(encoding="utf-8-sig")
def children(body,key): return [v for k,o,v in body if k==key]

army = parse(read("history/units/A01_1877.txt"))
assert len(children(army,"units")) == 1
units = children(value(army,"units"),"division")
assert len(units)==13
names = [value(u,"name").strip('"') for u in units]
assert len(names)==len(set(names))
assert all(not re.search(r"[А-Яа-я]", n) for n in names)
templates={value(t,"name").strip('"'):t for t in children(army,"division_template")}
expected = {
 "Batavische Mariniers": ("marine", 16, 3, 38),
 "KNIL-Infanterie": ("infantry", 16, 4, 40),
 "Koloniale Landstorm": ("infantry", 12, 2, 28),
}
for name, (unit, men, guns, width) in expected.items():
 regiments = value(templates[name], "regiments")
 assert len(children(regiments, unit)) == men, name
 assert len(children(regiments, "field_gun_brigade")) == guns, name
 assert len(regiments) == men + guns, name
 positions = [(value(body, "x"), value(body, "y")) for key, op, body in regiments]
 assert len(set(positions)) == len(positions), f"Overlapping battalions: {name}"
 assert all(0 <= int(x) < 5 and 0 <= int(y) < 5 for x, y in positions), name
 field_gun = value(value(parse(read("common/units/artillery_brigade.txt")), "sub_units"), "field_gun_brigade")
 assert men * 2 + guns * float(value(field_gun, "combat_width")) == width, name
assert "early_artillery = 1" in read("history/countries/A01 - Placeholder.txt")
assert all(value(u,"division_template").strip('"') in templates for u in units)
assert sum(value(u,"division_template").strip('"')=="Koloniale Landstorm" for u in units)==6
militia=parse(read("history/units/A01_indonesian_militia.txt"))
war_units=children(value(militia,"units"),"division")
assert len(war_units)==12
war_template=value(value(militia,"division_template"),"name").strip('"')
assert war_template not in templates, "Peace cleanup must not delete the starting garrisons"
assert f'division_template = "{war_template}"' in read("common/scripted_effects/borneo_war_effects.txt")
assert all(value(u,"division_template").strip('"')==war_template for u in war_units)
assert value(value(militia,"division_template"),"is_locked")=="yes"

focuses=children(value(parse(read("common/national_focus/a01_focus.txt")),"focus_tree"),"focus")
by_id={value(f,"id"):f for f in focuses}
chain=["A01_dutch_literacy","A01_rural_labour_duty","A01_factory_resettlement"]
assert [int(value(by_id[n],"cost"))*7 for n in chain] == [35,35,70]
for index,ident in enumerate(chain):
 expected = "A01_last_chance_to_negotiate" if index==0 else chain[index-1]
 assert {value(p,"focus") for p in children(by_id[ident],"prerequisite")} == ({expected, "A01_strengthen_ludolfs_power"} if index == 0 else {expected})
assert value(value(by_id[chain[1]],"completion_reward"),"add_stability") == "-0.05"
assert value(value(by_id[chain[-1]],"completion_reward"),"add_stability") == "-0.05"
# Execute the actual idea changes in order: the final step must remove every agrarian spirit.
active={"A01_agrarian_society"}
for ident in chain:
 for key,op,body in value(by_id[ident],"completion_reward"):
  if key=="swap_ideas":
   old=value(body,"remove_idea"); assert old in active
   active.remove(old);active.add(value(body,"add_idea"))
  elif key=="remove_ideas":
   assert body in active;active.remove(body)
  elif key=="add_ideas":active.add(body)
assert not any("agrarian" in n for n in active)
assert {"A01_dutch_primary_schooling","A01_factory_workforce"} <= active
ideas={}
for path in ["common/ideas/A01_colonial_constraints.txt","common/ideas/A01_industrial_transition.txt"]:
 for k,o,v in value(value(parse(read(path)),"ideas"),"country"):
  ideas[k]={mk:float(mv) for mk,mo,mv in value(v,"modifier")}
stages=["A01_agrarian_society","A01_agrarian_schooling","A01_agrarian_labour_transition"]
for key in ["production_speed_buildings_factor","industrial_capacity_factory","production_factory_efficiency_gain_factor"]:
 assert ideas[stages[0]][key] < ideas[stages[1]][key] < ideas[stages[2]][key] < 0
for stage in stages:
 assert .015 + ideas[stage]["recruitable_population"] > 0
 assert 1 + ideas[stage]["recruitable_population_factor"] - .30 - .30 > 0
roots={ident for ident,f in by_id.items() if not children(f,"prerequisite")}
assert roots=={"A01_constitution"}, roots
assert {value(p,"focus") for p in children(by_id["A01_knil_reform"],"prerequisite")}=={"A01_last_chance_to_negotiate", "A01_strengthen_ludolfs_power"}
assert {value(p,"focus") for p in children(by_id["A01_java_development"],"prerequisite")}=={"A01_factory_resettlement"}
assert "A01_archipelago_shipping" not in by_id
# The full tree must remain compact and labels on the same row must have room.
positions=[(int(value(f,"x")),int(value(f,"y"))) for f in focuses]
# The secret royal branch has its own compact block, revealed only after choosing it.
public=[(int(value(f,"x")),int(value(f,"y"))) for f in focuses if "A01_royal_path_revealed" not in str(children(f,"allow_branch"))]
royal=[(int(value(f,"x")),int(value(f,"y"))) for f in focuses if "A01_royal_path_revealed" in str(children(f,"allow_branch"))]
assert max(x for x,y in public)-min(x for x,y in public)<=24
# The approved 46-focus royal expansion occupies a 24-column block.
assert max(x for x,y in royal)-min(x for x,y in royal)<=24
for x,y in positions:
 assert all(abs(x-x2)>=2 for x2,y2 in positions if y2==y and x2!=x)
# Prevent one-month grants of two permanent industrial buildings, and wartime buff retention.
for ident in ["A01_batavia_docks","A01_admiralty_shipyards","A01_military_industry"]:
 assert int(value(by_id[ident],"cost"))*7==70
assert all(not any(k=="repeatable" and v=="yes" for k,o,v in f) for f in focuses)
war_idea=value(value(value(parse(read("common/ideas/pacific_ideas.txt")),"ideas"),"country"),"A01_war_production")
assert value(value(value(war_idea,"cancel"),"NOT"),"has_war_with")=="A03"
# AI references and advisor gates must point to existing focuses.
ai=read("common/ai_strategy_plans/A01_canonical.txt")
plan=value(parse(ai),"A01_ludolf_canonical_plan")
for ident,o,v in value(plan,"ai_national_focuses"):assert ident in by_id,ident
advisors=value(parse(read("common/characters/A01_reform_advisors.txt")),"characters")
history=read("history/countries/A01 - Placeholder.txt")
for ident,o,body in advisors:
 assert history.count("recruit_character = "+ident)==1
 available=value(value(body,"advisor"),"available")
 assert value(available,"has_completed_focus") in by_id
for lang in ["russian","english"]:
 raw=(R/f"localisation/{lang}/1896_main_l_{lang}.yml").read_bytes()
 assert raw.startswith(b"\xef\xbb\xbf")
 keys=set(re.findall(r"^\s+([^\s:]+):",raw.decode("utf-8-sig"),re.M))
 for ident in chain+["A01_production_standardisation","A01_java_steam_power","A01_local_nco_schools"]+list(ideas.keys()-{stages[0]}):
  assert ident in keys and ident+"_desc" in keys,ident
print("PASS: army and militia preserved; 35/35/70-day reform removes agrarian spirits; one political root; compact layout; meaningful army/industry spirit progression; AI references and advisor unlocks; RU/EN labels.")
