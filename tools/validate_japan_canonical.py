"""Reference validation and a bounded interpreter of the actual canonical timeline.

Models dates, event queues, country flags, bilateral wars and treaty ownership.
Does not simulate combat, AI focus selection, modifier balance or the game engine.
"""
from pathlib import Path
from datetime import date,timedelta
import re,json,copy
from PIL import Image
R=Path(__file__).resolve().parents[1]
G=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
def read(p):return (R/p).read_text(encoding='utf-8-sig')
def parse(text):
 tokens=re.findall(r'"(?:\\.|[^"\\])*"|[{}=<>]|[^\s{}=<>]+',re.sub(r'#[^\n]*','',text));pos=0
 def block(nested=False):
  nonlocal pos
  out=[]
  while pos<len(tokens) and tokens[pos]!='}':
   key=tokens[pos].strip('"');pos+=1
   if pos<len(tokens) and tokens[pos] in ('=','<','>'):
    op=tokens[pos];pos+=1
    if tokens[pos]=='{':pos+=1;v=block(True)
    else:v=tokens[pos].strip('"');pos+=1
    out.append((key,op,v))
   else:out.append((key,None,None))
  if nested:assert pos<len(tokens) and tokens[pos]=='}';pos+=1
  return out
 out=block();assert pos==len(tokens);return out
def val(n,k,d=None):return next((v for key,op,v in n if key==k),d)
def walk(n):
 for k,o,v in n:
  yield k,o,v
  if isinstance(v,list):yield from walk(v)
files=[p for folder in ['common','events','interface'] for p in (R/folder).rglob('*') if p.suffix in ('.txt','.gfx') and ('JPC' in p.name or p.name in ['a03_focus.txt','A01_canonical.txt','expansion_effects.txt','borneo_war_effects.txt','A01_inevitable_conflict.txt','A03_japanese_expansion.txt','A03_southern_preparations.txt','A03_wartime_operations.txt','pacific_diplomacy.txt'])]
for p in files:parse(p.read_text(encoding='utf-8-sig'))
tree=val(parse(read('common/national_focus/a03_focus.txt')),'focus_tree')
focuses={val(v,'id'):v for k,o,v in tree if k=='focus'}
roots=[k for k,v in focuses.items() if val(v,'prerequisite') is None]
assert set(roots)=={'A03_imperial_council'},roots
coords=set()
for k,n in focuses.items():
 xy=(val(n,'x'),val(n,'y'));assert xy not in coords;coords.add(xy)
 for key,o,v in n:
  if key=='prerequisite':assert val(v,'focus') in focuses
 def ancestors(fid,path=()):
  assert fid not in path,'Focus cycle'
  prs=[val(v,'focus') for k,o,v in focuses[fid] if k=='prerequisite']
  return {fid}|set().union(*(ancestors(p,path+(fid,)) for p in prs))
 assert 'A03_imperial_council' in ancestors(k)
 # Existing postwar constitutional choices remain; the 1893 opening is canonical.
 if val(n,'mutually_exclusive'):
  for key,op,other in val(n,'mutually_exclusive'):
   if key=='focus':assert any(v==k for kk,oo,v in val(focuses[other],'mutually_exclusive',[]))
plans=parse(read('common/ai_strategy_plans/A01_canonical.txt'))
for fid,o,v in val(val(plans,'A03_southern_canonical_plan'),'ai_national_focuses'):assert fid in focuses,fid
locs={}
for lang in ['russian','english']:
 raw=(R/f'localisation/{lang}/1896_main_l_{lang}.yml').read_bytes();assert raw.startswith(b'\xef\xbb\xbf')
 locs[lang]=set().union(*(set(re.findall(r'^\s+([^ :]+):\d+',p.read_text(encoding='utf-8-sig'),re.M)) for p in (R/f'localisation/{lang}').rglob('*.yml')))
# Unrelated legacy language files need not contain identical key sets.
events={val(v,'id'):v for k,o,v in parse(read('events/JPC_canonical.txt')) if k=='country_event'}
assert len(events)==22
for n in events.values():
 for field in ['title','desc']:assert val(n,field) in locs['russian']
 for k,o,v in n:
  if k=='option':assert val(v,'name') in locs['russian']
all_events='\n'.join(p.read_text(encoding='utf-8-sig') for p in (R/'events').glob('*.txt'))
all_defs=set(re.findall(r'country_event\s*=\s*\{\s*id\s*=\s*(\w+\.\d+)\s+(?:title|hidden|trigger)',all_events))
legacy_missing_events=set()
for p in files:
 for k,o,v in walk(parse(p.read_text(encoding='utf-8-sig'))):
  if k=='country_event' and isinstance(v,list) and val(v,'id') not in all_defs:
   if p.name=='a03_focus.txt' and val(v,'id').startswith('A03_imperial.'):legacy_missing_events.add(val(v,'id'))
   else:raise AssertionError((p,val(v,'id')))
ideas=val(val(parse(read('common/ideas/JPC_canonical.txt')),'ideas'),'country')
documented=(G/'documentation/modifiers_documentation.md').read_text(encoding='utf-8-sig')
for k,o,n in ideas:
 assert k in locs['russian'] and k+'_desc' in locs['russian']
 for m,op,v in val(n,'modifier'):
  assert f'## {m}\n' in documented or re.fullmatch(r'production_speed_(dockyard|industrial_complex|arms_factory)_factor',m),m
for p in (R/'gfx/interface').glob('*/jpc_*.dds'):
 im=Image.open(p);assert im.mode=='RGBA' and im.getextrema()[3][0]==0
assert Image.open(R/'gfx/event_pictures/jpc_council.dds').size==(430,230)
for p in ['common/decisions/A01_inevitable_conflict.txt','common/decisions/A03_japanese_expansion.txt']:
 s=read(p);assert 'days_mission_timeout = 365' in s and 'days_mission_timeout = 1006' in s
for p in ['common/decisions/A03_wartime_operations.txt','common/decisions/A03_southern_preparations.txt','common/decisions/A01_inevitable_conflict.txt']:
 assert 'add_days_mission_timeout' not in read(p)

decisions={k:v for p in (R/'common/decisions').glob('*.txt') for cat,o,n in parse(p.read_text(encoding='utf-8-sig')) if isinstance(n,list) for k,o,v in n if isinstance(v,list)}
effects={}
for p in (R/'common/scripted_effects').glob('*.txt'):
 for k,o,v in parse(p.read_text(encoding='utf-8-sig')):effects[k]=v
actions=[]
for p in ['common/on_actions/JPC_canonical.txt','common/on_actions/A01_independent_preparations.txt','common/on_actions/JPI_industry.txt']:
 hooks=val(parse(read(p)),'on_actions');actions.append(val(val(hooks,'on_daily',val(hooks,'on_daily_A03')),'effect'))
class World:
 def __init__(self,foothold=True,choices=None,missing=(),prepared=True):
  self.now=date(1893,1,1);self.tags=set(['A01','A02','A03','A04','A07','A08','A09','A10','PHW'])-set(missing)
  self.flags={t:set() for t in self.tags};self.wars=set();self.queue=[];self.seen=[];self.missions={t:{} for t in self.tags}
  # Fixture: industrial preparation is supplied explicitly; the model does not choose focuses.
  # Political prerequisites are supplied separately from industrial readiness.
  self.completed={'JPR_defence_budget','JPC_garrison_accounts'}
  if prepared:self.flags['A03'].update({'JPI_tesla_ready','JPI_southern_ready'})
  self.owners={327:'A03',1023:'A01',1024:'A01',333:'A01',1059:'A01',1022:'A01'};self.foothold=foothold;self.choices=choices or {};self.war_dates=[]
 def test(self,n,t):
  results=[]
  for k,o,v in n:
   if k in self.tags:r=self.test(v,k)
   elif re.fullmatch(r'A\d\d|PHW',k):r=False
   elif k=='OR':r=any(self.test([x],t) for x in v)
   elif k in ['AND','hidden_trigger']:r=self.test(v,t)
   elif k=='NOT':r=not self.test(v,t)
   elif k=='always':r=v=='yes'
   elif k=='date':r=self.now>date(*map(int,v.split('.'))) if o=='>' else self.now<date(*map(int,v.split('.')))
   elif k=='tag':r=t==v
   elif k=='country_exists':r=v in self.tags
   elif k=='has_completed_focus':r=v in self.completed if t=='A03' else False
   elif k=='has_idea':r=False # Spirit durations are outside this calendar model.
   elif k=='has_country_flag':r=v in self.flags[t]
   elif k=='has_war_with':r=frozenset([t,v]) in self.wars
   elif k=='owns_state':r=self.owners.get(int(v))==t
   elif k=='A03_controls_borneo_province':r=self.foothold
   elif k=='has_active_mission':r=v in self.missions[t]
   elif k=='has_dlc':r=True
   elif k=='power_balance_value':r=False
   else:raise AssertionError(('Unmodelled trigger',k))
   results.append(r)
  return all(results)
 def run(self,n,t):
  branch=False
  for k,o,v in n:
   if k=='if':branch=self.test(val(v,'limit',[]),t);self.run([x for x in v if x[0]!='limit'],t) if branch else None
   elif k=='else':self.run(v,t) if not branch else None
   elif k=='else_if':
    if not branch:branch=self.test(val(v,'limit',[]),t);self.run([x for x in v if x[0]!='limit'],t) if branch else None
   elif k in self.tags:self.run(v,k)
   elif k=='hidden_effect':self.run(v,t)
   # Domestic ledgers are executed in validate_story_systems, not this calendar model.
   elif k.startswith(('JPF_','JPN_','JPL_')) and k in effects:pass
   elif k in effects:self.run(effects[k],t)
   elif k=='set_country_flag':self.flags[t].add(val(v,'flag') if isinstance(v,list) else v)
   elif k=='clr_country_flag':self.flags[t].discard(v)
   elif k=='country_event':self.queue.append((self.now+timedelta(days=int(val(v,'days','0'))),t,val(v,'id')))
   elif k=='activate_mission':self.missions[t][v]=self.now+timedelta(days=int(val(decisions[v],'days_mission_timeout')))
   elif k=='add_days_mission_timeout':self.missions[t][val(v,'mission')]+=timedelta(days=int(val(v,'days')))
   elif k=='remove_mission':self.missions[t].pop(v,None)
   elif k=='declare_war_on':
    enemy=val(v,'target');self.wars.add(frozenset([t,enemy]));self.war_dates.append((t,enemy,str(self.now)))
    if {t,enemy}=={'A01','A03'}:self.run(effects['A01_start_expansion_campaign_effect'],'A01')
   elif k=='white_peace':self.wars.discard(frozenset([t,val(v,'tag')]))
   elif k=='transfer_state':self.owners[int(v)]=t
   # Equipment, politics, buildings and modifiers do not change this model's outcome.
 def advance(self,end):
  while self.now<=end:
   for action in actions:self.run(action,'A03')
   for tag,missions in self.missions.items():
    for mission,deadline in list(missions.items()):
     if mission not in missions:continue
     if self.test(val(decisions[mission],'cancel_trigger',[]),tag):missions.pop(mission,None)
     elif deadline<=self.now:
      missions.pop(mission,None);self.run(val(decisions[mission],'timeout_effect',[]),tag)
   due=[q for q in self.queue if q[0]<=self.now];self.queue=[q for q in self.queue if q[0]>self.now]
   for d,t,e in due:
    if e not in events:continue # External atmosphere events do not drive this timeline.
    n=events[e]
    if self.test(val(n,'trigger',[]),t):
     self.seen.append((e,str(self.now)));self.run(val(n,'immediate',[]),t)
     opts=[v for k,o,v in n if k=='option'];self.run(opts[self.choices.get(e,0)],t)
   self.now+=timedelta(days=1)

scenarios=[]
# A missed deadline must wait for towers AND the sailing order, then resume once.
w=World(prepared=False);w.advance(date(1894,2,1))
assert 'JPI_ultimatum_due' in w.flags['A03']
assert not any(enemy=='A01' for tag,enemy,d in w.war_dates)
w.flags['A03'].add('JPI_tesla_ready');w.advance(date(1894,2,4))
assert not any(enemy=='A01' for tag,enemy,d in w.war_dates)
w.flags['A03'].add('JPI_southern_ready');w.advance(date(1894,2,10))
assert len([x for x in w.war_dates if x[1]=='A01'])==1
scenarios.append({'missing_industry':'deadline deferred; towers alone insufficient; southern order resumes once'})
# Industrial flags or an expired calendar cannot bypass the political columns.
w=World();w.completed.clear();w.advance(date(1894,2,1))
assert not any(enemy=='A01' for tag,enemy,d in w.war_dates)
w.completed.add('JPR_defence_budget');w.advance(date(1894,2,4))
assert not any(enemy=='A01' for tag,enemy,d in w.war_dates)
w.completed.add('JPC_garrison_accounts');w.advance(date(1894,2,10))
assert len([x for x in w.war_dates if x[1]=='A01'])==1
scenarios.append({'missing_politics':'industry cannot bypass budget or Manila; completion resumes once'})
# Oil chosen before the visible mission must apply its acceleration once it exists.
w=World();w.flags['A03'].add('JPI_oil_priority');w.advance(date(1894,1,3))
assert ('A03','A01','1893-12-03') in w.war_dates,w.war_dates
assert 'JPI_oil_clock_applied' in w.flags['A03']
scenarios.append({'oil_before_countdown':'30 days earlier, applied once after mission activation'})
for foothold in [True,False]:
 w=World(foothold);w.advance(date(1896,2,5))
 assert w.war_dates[:2]==[('A10','A03','1893-04-02'),('A03','A01','1894-01-02')],w.war_dates
 assert ('A03_borneo_victory' if foothold else 'A03_borneo_defeat') in w.flags['A03']
 assert frozenset(['A03','A01']) not in w.wars
 assert frozenset(['A03','A10']) in w.wars,'Dutch treaty must not end the Philippine war'
 assert (w.owners[1024]=='A03')==foothold
 assert not any(e=='japan_canon.2' for e,d in w.seen),'Negotiated guarantees must require a completed focus'
 assert 'JPA_finance_forced' in w.flags['A03'],'Ignoring preparations has consequences'
 assert len([e for e,d in w.seen if e=='japan_canon.30'])==(1 if foothold else 0)
 before=dict(w.owners);w.advance(date(1896,3,5));assert before==w.owners
 scenarios.append({'foothold':foothold,'wars_started':w.war_dates,'outcome':'Japanese treaty' if foothold else 'Dutch victory','repeat_safe':True})
w=World();w.advance(date(1893,3,20))
for i in range(3):w.run(effects['JPS_accelerate_invasion_effect'],'A03')
w.advance(date(1894,1,3))
assert ('A03','A01','1893-11-18') in w.war_dates,w.war_dates
assert len([x for x in w.seen if x[0]=='japan_canon.5'])==1
scenarios.append({'three_accelerations':'45 days earlier; war 1893-11-18; ultimatum once'})
w=World();w.advance(date(1893,3,20));w.flags['A01'].add('pacific_trade_accord');w.flags['A03'].add('pacific_trade_accord')
w.run(effects['A01_cancel_preparations_for_agreement_effect'],'A01');w.advance(date(1894,2,1))
assert not any(enemy=='A01' for tag,enemy,d in w.war_dates)
scenarios.append({'trade_accord':'both clocks cancelled; no invasion'})
w=World(True,{'japan_canon.27':1});w.advance(date(1896,2,5))
assert frozenset(['A02','A03']) in w.wars,'British war is independent of Borneo peace'
scenarios.append({'British note':'rejected','British war':'starts; survives Borneo treaty'})
w=World(True,missing=('A02','A07','A08','A09','PHW'));w.advance(date(1896,2,5));assert 'A03_borneo_victory' in w.flags['A03']
w=World();w.flags['A03'].add('JPC_ultimatum_sent');w.flags['A01'].add('A01_island_defence_started')
w.run(effects['A03_start_southern_war_effect'],'A03');assert not w.wars,'Legacy caller must not start a January war'
w=World();w.advance(date(1894,6,1));restored=copy.deepcopy(w)
w.advance(date(1896,2,5));restored.advance(date(1896,2,5));assert w.__dict__==restored.__dict__
scenarios.append({'snapshot_resume':'same events, wars, flags and ownership as uninterrupted model'})
report={'existing_missing_legacy_events':sorted(legacy_missing_events),'focuses':len(focuses),'roots':roots,'spirits':len(ideas),'events':len(events),'scenarios':scenarios,'optional_countries_absent':'passed','limitations':['Bounded script model; no combat or focus AI simulation','Engine loading and a complete campaign are separate checks']}
(R/'tools/japan_canonical_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
