"""Validate real industrial routes and prevent the screenshot's layout regressions."""
from pathlib import Path
from itertools import product
import json
from add_canon_countries import parse,value
R=Path(__file__).resolve().parents[1]
tree=value(parse((R/'common/national_focus/a03_focus.txt').read_text()),'focus_tree')
fs={value(n,'id'):n for k,o,n in tree if k=='focus'}
def get(n,k,d=None):return next((v for a,o,v in n if a==k),d)
def parents(fid):return [{v for k,o,v in n if k=='focus'} for k,o,n in fs[fid] if k=='prerequisite']
def excludes(fid):return {v for k,o,n in fs[fid] if k=='mutually_exclusive' for a,b,v in n}
def test(n,flags):
 for k,o,v in n:
  if k=='has_country_flag':r=v in flags
  elif k=='NOT':r=not test(v,flags)
  elif k=='OR':r=any(test([x],flags) for x in v)
  else:raise AssertionError(k)
  if not r:return False
 return True
coords={fid:(int(value(n,'x')),int(value(n,'y'))) for fid,n in fs.items()}
assert max(x for x,y in coords.values())-min(x for x,y in coords.values())<=22
assert max(y for x,y in coords.values())<=25
assert {y for x,y in coords.values()}==set(range(26)),'empty row'
for fid in fs:
 for group in parents(fid):
  for p in group:assert 1<=coords[fid][1]-coords[p][1]<=5,(p,fid,'long or backward wire')
for a,b in [('JPI_electrical_bureau','JPI_fleet_workshops'),('JPI_portable_prototype','JPI_ship_generators'),('JPL_medical_rotation','JPL_forward_workshops')]:
 assert b in excludes(a) and a in excludes(b)
assert 'JPI_raw_register' not in fs and 'JPI_unsigned_contracts' not in fs
assert all(p!='JPR_defence_budget' for fid in fs if not fid.startswith('JPI_') for g in parents(fid) for p in g),'budget wire to late military branch'
routes=[]
for resource,yard,organisation,power in product(['JPI_kyushu_coal','JPI_oil_hunger','JPI_proxy_machines','JPI_copied_samples'],['JPI_kure_yards','JPI_airship_hangars'],['JPI_electrical_bureau','JPI_fleet_workshops'],['JPI_portable_prototype','JPI_ship_generators']):
 policy='JPI_closed_ports' if resource in ['JPI_kyushu_coal','JPI_oil_hunger'] else 'JPI_japanese_terms'
 trial='JPI_quiet_coast' if power=='JPI_portable_prototype' else 'JPI_coastal_trials'
 route=[policy,resource,'JPI_standard_node',yard,organisation,power,trial,'JPI_scarlet_sails','JPI_southern_push']
 done={'JPR_defence_budget'};flags=set()
 for fid in route:
  assert all(g & done for g in parents(fid)),(fid,done)
  assert not (excludes(fid)&done),(fid,done)
  assert test(get(fs[fid],'available',[]),flags),(fid,flags)
  flags.update(v for k,o,v in value(fs[fid],'completion_reward') if k=='set_country_flag' and isinstance(v,str))
  done.add(fid)
 assert {'JPI_tesla_design','JPI_tesla_prototype','JPI_tesla_tested','JPI_tesla_ready','JPI_southern_ready'}<=flags,(route,flags)
 assert ('JPI_portable_towers' in [v for k,o,v in value(fs[trial],'completion_reward') if k=='add_ideas'])==(power=='JPI_portable_prototype')
 routes.append(route)
assert len(routes)==32
for choice in ['JPL_medical_rotation','JPL_forward_workshops']:
 assert parents('JPD_professional_logistics')==[{'JPL_medical_rotation','JPL_forward_workshops'}]
 assert any(choice in g for g in parents('JPD_professional_logistics'))
plan=(R/'common/ai_strategy_plans/A01_canonical.txt').read_text()
japanese=next(n for k,o,n in parse(plan) if k=='A03_southern_canonical_plan')
for fid,o,v in value(japanese,'ai_national_focuses'):assert fid in fs,fid
report={'focuses':len(fs),'width':22,'last_row':25,'empty_rows':0,'maximum_direct_edge_rows':5,'industrial_routes':len(routes),'industrial_focuses_per_route':9,'checks':['all 32 industrial routes reach both readiness flags','reciprocal exclusive choices','both logistics alternatives unlock professional logistics','no late budget wires or redundant full-height links','AI references existing focuses'],'limitations':['Schematic and script checks; current revision not loaded in the game engine']}
(R/'tools/japan_compact_choices_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
