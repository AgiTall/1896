"""Validate actual tree, political gates and authored crisis outcomes; no combat simulation."""
from pathlib import Path
from itertools import product
import re,json
from add_canon_countries import parse,value
R=Path(__file__).resolve().parents[1]
def read(p):return (R/p).read_text(encoding='utf-8-sig')
def get(n,k,d=None):return next((v for a,o,v in n if a==k),d)
def walk(n):
 for k,o,v in n:
  yield k,o,v
  if isinstance(v,list):yield from walk(v)
t=value(parse(read('common/national_focus/a03_focus.txt')),'focus_tree')
fs={value(n,'id'):n for k,o,n in t if k=='focus'}
def parents(fid):return [{v for k,o,v in n if k=='focus'} for k,o,n in fs[fid] if k=='prerequisite']
coords={k:(int(value(n,'x')),int(value(n,'y'))) for k,n in fs.items()}
roots=[k for k in fs if not parents(k)]
assert roots==['A03_imperial_council'],roots
for fid,n in fs.items():
 for group in parents(fid):
  for p in group:assert p in fs and coords[p][1]<coords[fid][1],(p,fid)
 for other in fs:
  if fid!=other and coords[fid][1]==coords[other][1]:assert abs(coords[fid][0]-coords[other][0])>=2,(fid,other)
 for k,o,v in n:
  if k=='mutually_exclusive':
   for a,b,p in v:assert any(fid==x for key,op,ls in fs[p] if key=='mutually_exclusive' for q,z,x in ls),(fid,p)
assert parents('JPR_defence_budget')==[{'JPF_delivery_calendar'},{'JPN_north_imperial_arbitration'},{'JPC_garrison_accounts'}]
assert parents('JPI_closed_ports')==parents('JPI_japanese_terms')==[{'JPR_defence_budget'}]
assert parents('JPF_public_accounts')==[{'JPC_state_guarantees','JPT_treasury_debts'}]
assert parents('JPN_north_imperial_arbitration')==[{'JPC_honshu_depots','JPT_north_front_supply'}]
loc={}
for lang in ['russian','english']:
 loc[lang]={}
 for p in (R/f'localisation/{lang}').glob('*.yml'):
  for k,v in re.findall(r'^\s*(\w+(?:\.\w+)*):\d+\s*"(.*)"',p.read_text(encoding='utf-8-sig'),re.M):loc[lang][k]=v
 for fid in fs:assert fid in loc[lang] and fid+'_desc' in loc[lang],(lang,fid)
gfx='\n'.join(p.read_text(encoding='utf-8-sig') for p in (R/'interface').glob('*.gfx'))
for n in fs.values():assert '"'+value(n,'icon')+'"' in gfx,value(n,'icon')
paths=['common/scripted_effects/JPT_three_heads.txt','common/on_actions/JPT_three_heads.txt','common/ideas/JPT_three_heads.txt','common/decisions/JPT_three_heads.txt','common/decisions/categories/JPT_three_heads.txt','events/JPT_three_heads.txt']
for p in paths:parse(read(p))
events={value(n,'id'):n for k,o,n in parse(read('events/JPT_three_heads.txt')) if k=='country_event'}
for n in events.values():
 for k,o,v in n:
  if k in ['title','desc']:assert all(v in loc[l] for l in loc)
  if k=='option':assert all(value(v,'name') in loc[l] for l in loc)
effects=dict((k,n) for k,o,n in parse(read('common/scripted_effects/JPT_three_heads.txt')))
mission=value(parse(read('common/decisions/JPT_three_heads.txt')),'JPT_three_heads')
deadline=value(mission,'JPT_mitsubishi_deadline')
assert value(deadline,'days_mission_timeout')=='180'
def test(n,flags=set(),done=set()):
 out=[]
 for k,o,v in n:
  if k=='OR':r=any(test([x],flags,done) for x in v)
  elif k=='AND':r=test(v,flags,done)
  elif k=='NOT':r=not test(v,flags,done)
  elif k=='has_country_flag':r=v in flags
  elif k=='has_completed_focus':r=v in done
  elif k=='always':r=v=='yes'
  else:raise AssertionError(k)
  out.append(r)
 return all(out)
def can_focus(fid,flags,done):return all(g & done for g in parents(fid)) and test(get(fs[fid],'available',[]),flags,done)
scenarios=[]
for guaranteed,reformed in product([False,True],repeat=2):
 flags=set()
 if guaranteed:flags.add('JPT_loans_guaranteed')
 if reformed:flags.add('JPT_loans_reformed')
 assert test(value(deadline,'cancel_trigger'),flags)==(guaranteed or reformed)
 branch=value(value(deadline,'timeout_effect'),'if')
 assert test(value(branch,'limit'),flags)==(not guaranteed and not reformed)
scenarios.append('180-day deadline: guarantees or reform avert collapse; treasury assumption alone does not')
for money,north in product(['JPC_state_guarantees','JPT_treasury_debts'],['JPC_northern_protocol','JPT_north_rebellion']):
 done={'A03_imperial_council',money,north}
 assert can_focus('JPF_public_accounts',set(),done)
 done.update({'JPF_public_accounts','JPF_delivery_calendar','JPC_manila_priority','JPC_garrison_accounts','JPN_north_imperial_arbitration'})
 assert can_focus('JPR_defence_budget',set(),done)
 assert not can_focus('JPR_defence_budget',{'JPT_mitsubishi_crashed'},done)
 for gate in ['JPF_delivery_calendar','JPN_north_imperial_arbitration','JPC_garrison_accounts']:
  assert not can_focus('JPR_defence_budget',set(),done-{gate}),gate
 scenarios.append(money+' / '+north+': budget opens only with all three completed columns')
assert not can_focus('JPF_delivery_calendar',{'JPT_mitsubishi_crashed'},{'JPF_public_accounts'})
recovery=value(mission,'JPT_restructure_after_crash')
assert value(recovery,'cost')=='100' and value(recovery,'days_remove')=='60'
assert ('clr_country_flag','=','JPT_mitsubishi_crashed') in value(recovery,'remove_effect')
assert ('remove_ideas','=','JPT_mitsubishi_collapse') in value(recovery,'remove_effect')
war=effects['JPT_north_war_effect'];assert any(k=='declare_war_on' for k,o,v in walk(war))
daily=effects['JPT_daily_effect'];assert ('has_country_flag','=','JPT_expedition_checked') in list(walk(daily))
assert ('set_country_flag','=','JPT_expedition_checked') in list(walk(daily))
assert ('date','>','1893.12.31') in list(walk(daily))
assert [k for k,o,v in walk(daily) if k in ['70','30']]==['70','30']
assert len([1 for k,o,v in events['japan_dragon.2'] if k=='option'])==2
assert any(k=='declare_war_on' for k,o,v in walk(events['japan_dragon.5']))
for p in ['common/scripted_effects/JPC_canonical.txt','common/scripted_effects/borneo_war_effects.txt']:
 assert 'has_completed_focus = JPR_defence_budget has_completed_focus = JPC_garrison_accounts' in read(p)
doc=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md')
if doc.exists():
 documented=doc.read_text(encoding='utf-8-sig')
 for k,o,n in walk(parse(read('common/ideas/JPT_three_heads.txt'))):
  if k=='modifier':
   for m,op,v in n:assert f'## {m}\n' in documented or m.startswith('production_speed_'),m
report={'focuses':len(fs),'roots':roots,'scenarios':scenarios,'checks':['prerequisites, reciprocal exclusions, no overlaps or backward edges','RU/EN focus/event localisation and registered icons','debt deadline and recovery','four political combinations and three mandatory budget columns','one-shot 1894 expedition, two outcomes and optional British escalation','both Borneo entry effects gated'],'limitations':['Static checks and bounded predicate evaluation; no engine or combat test']}
(R/'tools/japan_three_heads_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
