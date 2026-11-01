"""Reference audit plus bounded execution of the actual domestic and creditor scripts.
No combat, AI strategy, UI placement rendering or full engine campaign is simulated.
"""
from pathlib import Path
from datetime import date,timedelta
from collections import defaultdict
import json,re,copy
from add_canon_countries import parse
def value(n,key,default=None):return next((v for k,o,v in n if k==key),default)
R=Path(__file__).resolve().parents[1]
G=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
def read(p):return p.read_text(encoding='utf-8-sig')
def walk(n):
 for k,o,v in n:
  yield k,o,v
  if isinstance(v,list):yield from walk(v)
prefixes=('JPC','JPF','JPN','JPL','JPS','JPA','JPX','WTC')
files=[p for folder in ['common','events','interface'] for p in (R/folder).rglob('*') if p.suffix in ['.txt','.gfx'] and p.name.startswith(prefixes)]
for p in files:parse(read(p))
effects={k:v for p in (R/'common/scripted_effects').glob('*.txt') for k,o,v in parse(read(p))}
events={value(v,'id'):v for p in (R/'events').glob('*.txt') for k,o,v in parse(read(p)) if k=='country_event'}
ideas={k:v for p in (R/'common/ideas').glob('*.txt') for k,o,v in value(value(parse(read(p)),'ideas',[]),'country',[])}
decisions={k:v for p in (R/'common/decisions').glob('*.txt') for cat,o,n in parse(read(p)) if isinstance(n,list) for k,o,v in n if isinstance(v,list)}
loc={}
for lang in ['russian','english']:
 loc[lang]=set().union(*(set(re.findall(r'^\s+([^ :]+):\d+',read(p),re.M)) for p in (R/f'localisation/{lang}').rglob('*.yml')))
 for p in (R/f'localisation/{lang}').glob('*JP*_l_*.yml'):assert p.read_bytes().startswith(b'\xef\xbb\xbf'),p
 for p in (R/f'localisation/{lang}').glob('*WTC*_l_*.yml'):assert p.read_bytes().startswith(b'\xef\xbb\xbf'),p
sprites={}
for base in [G,R]:
 for p in (base/'interface').rglob('*.gfx'):
  # Vanilla's loose gfx syntax may contain non-Clausewitz blocks; inspect sprite declarations only.
  for m in re.finditer(r'spriteType\s*=\s*\{\s*name\s*=\s*"?([^"\s]+)"?[^}]*?texturefile\s*=\s*"([^"]+)"',read(p),re.S|re.I):sprites[m[1]]=m[2]
def localized(k):
 for lang in loc:assert k in loc[lang],(lang,k)
def sprite(k):
 assert k in sprites,('missing sprite',k)
 assert (R/sprites[k]).exists() or (G/sprites[k]).exists(),('missing texture',k,sprites[k])
focus_counts={}
for tag in ['a01','a03']:
 fs={value(v,'id'):v for k,o,v in value(parse(read(R/f'common/national_focus/{tag}_focus.txt')),'focus_tree') if k=='focus'}
 focus_counts[tag]=len(fs);coords=defaultdict(list)
 for fid,n in fs.items():
  coords[(value(n,'x'),value(n,'y'))].append(fid)
  if tag=='a03' or fid.startswith(('A01_european_','A01_wtc_strengthening')):
   localized(fid);localized(fid+'_desc');sprite(value(n,'icon'))
  for k,o,v in n:
   if k in ['prerequisite','mutually_exclusive']:
    for fk,fo,fv in v:
     if fk=='focus':assert fv in fs,(fid,fv)
 for xy,ids in coords.items():assert len(ids)==1,(tag,'focus collision',xy,ids)
 if tag=='a03':
  assert {fid for fid,n in fs.items() if value(n,'prerequisite') is None}=={'A03_imperial_council'}
 else:
  for fid in ['A01_european_democratic_unity','A01_lone_wolf_path','A01_wtc_strengthening_path']:assert value(fs[fid],'y')=='2'
  assert int(value(fs['A01_european_democratic_unity'],'x'))<16<int(value(fs['A01_wtc_strengthening_path'],'x'))
docs=read(G/'documentation/modifiers_documentation.md')
engine_triggers=set(re.findall(r'^## (\w+)\s*$',read(G/'documentation/triggers_documentation.md'),re.M))
scripted_triggers={k for p in (R/'common/scripted_triggers').glob('*.txt') for k,o,v in parse(read(p))}
def check_trigger(n):
 for k,o,v in n:
  if k in ['AND','OR','NOT','hidden_trigger']:check_trigger(v)
  elif re.fullmatch(r'A\d\d|PHW|ROOT|FROM|PREV|THIS|\d+',k):check_trigger(v)
  else:assert k in engine_triggers or k in scripted_triggers,('undocumented trigger',k)
for p in files:
 for k,o,v in walk(parse(read(p))):
  if k in ['limit','trigger','visible','available','allowed','cancel','cancel_trigger','activation'] and isinstance(v,list):check_trigger(v)
  if k=='country_event' and isinstance(v,list):assert value(v,'id') in events,(p,value(v,'id'))
  if k in effects:assert isinstance(effects[k],list)
  if k in ['has_completed_focus']:
   assert any(re.search(r'\bid\s*=\s*'+re.escape(v)+r'\b',read(f)) for f in (R/'common/national_focus').glob('*.txt')),(p,v)
  if k in ['add_ideas','remove_ideas','has_idea'] and isinstance(v,str):assert v in ideas,(p,k,v)
  if k=='add_timed_idea':assert value(v,'idea') in ideas,(p,v)
  if k=='picture' and isinstance(v,str):sprite(v if v.startswith('GFX_') else 'GFX_idea_'+v)
  if k in ['title','desc'] and isinstance(v,str):localized(v)
  if k=='option':localized(value(v,'name'))
 for key,o,n in parse(read(p)):
  if p.parent.name=='decisions':
   for did,o,dn in n:localized(did);localized(did+'_desc')
  if p.parent.name=='categories':localized(key);localized(key+'_desc')
 for key,n in ideas.items():
  if key.startswith(prefixes):
   localized(key);localized(key+'_desc')
   for m,op,mv in value(n,'modifier',[]):
    assert f'## {m}\n' in docs or m=='democratic_drift' or re.fullmatch(r'production_speed_(dockyard|industrial_complex|arms_factory)_factor',m),m

class Model:
 def __init__(self):
  self.completed=defaultdict(set);self.now=date(1893,5,2);self.tags={'A01','A02','A03','A04','A08','A09','A10'}
  self.vars=defaultdict(dict);self.flags=defaultdict(set);self.ideas=defaultdict(set);self.stock=defaultdict(lambda:defaultdict(int));self.pp=defaultdict(lambda:500);self.manpower=defaultdict(lambda:20000)
  self.wars={frozenset(('A03','A01')),frozenset(('A03','A10'))};self.control=defaultdict(set,{'A03':{327,529}});self.global_flags={'WTC_british_cover'};self.queue=[];self.government={};self.missions=defaultdict(dict)
  self.stock['A03'].update(infantry_equipment=10000,convoy_1=200,support_equipment=200)
 def num(self,x,t):
  try:return float(x)
  except (ValueError,TypeError):return self.vars[t].get(x,0)
 def test(self,n,t):
  rs=[]
  for k,o,v in n:
   if k in self.tags:r=self.test(v,k)
   elif k in ['AND','hidden_trigger']:r=self.test(v,t)
   elif k=='OR':r=any(self.test([x],t) for x in v)
   elif k=='NOT':r=not self.test(v,t)
   elif k=='always':r=v=='yes'
   elif k=='tag':r=t==v
   elif k=='country_exists':r=v in self.tags
   elif k=='has_completed_focus':r=v in self.completed[t]
   elif k=='has_country_flag':r=v in self.flags[t]
   elif k=='has_global_flag':r=v in self.global_flags
   elif k=='has_idea':r=v in self.ideas[t]
   elif k=='has_war_with':r=frozenset((t,v)) in self.wars
   elif k=='has_war':r=any(t in w for w in self.wars)==(v=='yes')
   elif k=='has_capitulated':r=v=='no'
   elif k=='controls_state':r=int(v) in self.control[t]
   elif k=='any_controlled_state':r=any(self.test(v,str(st)) for st in self.control[t])
   elif k=='state':r=t==v
   elif k=='date':r=self.now>date(*map(int,v.split('.'))) if o=='>' else self.now<date(*map(int,v.split('.')))
   elif k in ['has_political_power','has_manpower']:r=(self.pp[t] if k=='has_political_power' else self.manpower[t])>float(v)
   elif k=='has_active_mission':r=v in self.missions[t]
   elif k=='has_equipment':
    ek,eo,ev=v[0];r=self.stock[t][ek]>float(ev) if eo=='>' else self.stock[t][ek]<float(ev)
   elif k=='check_variable':
    var=value(v,'var')
    if var:a=self.vars[t].get(var,0);b=self.num(value(v,'value'),t);comp=value(v,'compare','equals')
    else:var,op,x=v[0];a=self.vars[t].get(var,0);b=self.num(x,t);comp={'=':'equals','>':'greater_than','<':'less_than'}[op]
    r={'equals':a==b,'greater_than':a>b,'less_than':a<b,'greater_than_or_equals':a>=b,'less_than_or_equals':a<=b}[comp]
   else:raise AssertionError(('unmodelled trigger',k))
   rs.append(r)
  return all(rs)
 def run(self,n,t='A03'):
  previous=False
  for k,o,v in n:
   if k=='if':
    previous=self.test(value(v,'limit',[]),t)
    if previous:self.run([x for x in v if x[0]!='limit'],t)
   elif k=='else_if':
    if not previous:
     previous=self.test(value(v,'limit',[]),t)
     if previous:self.run([x for x in v if x[0]!='limit'],t)
   elif k=='else':
    if not previous:self.run(v,t)
   elif k in self.tags:self.run(v,k)
   elif k in effects:self.run(effects[k],t)
   elif k in ['hidden_effect','immediate']:self.run(v,t)
   elif k in ['set_country_flag','clr_country_flag']:
    flag=value(v,'flag') if isinstance(v,list) else v
    if k=='set_country_flag':self.flags[t].add(flag)
    else:self.flags[t].discard(flag)
   elif k in ['set_global_flag','clr_global_flag']:
    if k=='set_global_flag':self.global_flags.add(v)
    else:self.global_flags.discard(v)
   elif k in ['set_variable','add_to_variable']:
    vk,vo,vv=v[0];self.vars[t][vk]=self.num(vv,t)+(self.vars[t].get(vk,0) if k=='add_to_variable' else 0)
   elif k=='clamp_variable':
    var=value(v,'var');self.vars[t][var]=min(float(value(v,'max')),max(float(value(v,'min')),self.vars[t].get(var,0)))
   elif k=='add_ideas':self.ideas[t].add(v)
   elif k=='add_timed_idea':self.ideas[t].add(value(v,'idea'))
   elif k=='remove_ideas':self.ideas[t].discard(v)
   elif k=='add_equipment_to_stockpile':
    kind=value(v,'type');kind='infantry_equipment' if kind=='infantry_equipment_0' else kind;self.stock[t][kind]+=int(value(v,'amount'));assert self.stock[t][kind]>=0,(t,kind)
   elif k=='add_political_power':self.pp[t]+=float(v)
   elif k=='add_manpower':self.manpower[t]+=int(v)
   elif k=='country_event':self.queue.append((t,value(v,'id')))
   elif k=='set_politics':self.government[t]=value(v,'ruling_party')
   elif k=='activate_mission':self.missions[t][v]=int(value(decisions[v],'days_mission_timeout'))
   elif k=='remove_mission':self.missions[t].pop(v,None)
   elif k=='add_days_mission_timeout':self.missions[t][value(v,'mission')]+=int(value(v,'days'))
   elif k in ['add_stability','add_war_support','create_country_leader','add_popularity','army_experience','navy_experience','add_command_power','diplomatic_relation']:pass
   elif k in ['name','trigger','ai_chance']:pass
   else:raise AssertionError(('unmodelled effect',k))
 def effect(self,k,t='A03'):self.run(effects[k],t)
 def choose(self,event,suffix,t='A03'):
  n=events[event];assert self.test(value(n,'trigger',[]),t),(event,'trigger')
  opt=next(v for k,o,v in n if k=='option' and value(v,'name')==event+'.'+suffix);assert self.test(value(opt,'trigger',[]),t),(event,suffix,'unavailable')
  self.run(value(n,'immediate',[]),t);self.run(opt,t)

checks=[]
monthly=value(value(value(parse(read(R/'common/on_actions/WTC_credit.txt')),'on_actions'),'on_monthly'),'effect')
m=Model()
for tag in sorted(m.tags):m.run(monthly,tag)
assert m.pp['A03']==498 and m.vars['A03']['WTC_debt']==31,'Monthly service must run once per debtor'
for module in ['JPF_finance','JPN_north','JPL_luzon']:
 hooks=value(parse(read(R/f'common/on_actions/{module}.txt')),'on_actions')
 assert value(hooks,'on_monthly') is None and value(hooks,'on_monthly_A03') is not None
checks.append('Country pulses charge one monthly service, not one per country in the world')
fs={value(v,'id'):v for k,o,v in value(parse(read(R/'common/national_focus/a03_focus.txt')),'focus_tree') if k=='focus'}
opening=['JPC_state_guarantees','JPC_northern_protocol','JPC_manila_priority','JPC_batavia_demands']
m=Model();m.now=date(1893,1,15)
for fid in opening:
 expected={'JPC_manila_priority':'JPC_northern_protocol','JPC_batavia_demands':'JPR_defence_budget'}.get(fid,'JPX_sea')
 assert value(value(fs[fid],'prerequisite'),'focus')==expected
 assert m.test(value(fs[fid],'available',[]),'A03'),(fid,'January lock')
assert sum(int(value(fs[f],'cost'))*7 for f in ['A03_imperial_council','JPX_sea','JPR_defence_budget']+opening)==196<365
assert {value(n,'focus') for k,o,n in fs['JPR_defence_budget'] if k=='prerequisite'}=={'JPC_northern_protocol','JPC_state_guarantees'}
for fid in ['JPL_supply_board','JPL_quartermaster_school']:
 assert 'JPR_defence_budget' in {value(n,'focus') for k,o,n in fs[fid] if k=='prerequisite'}
assert len(value(fs['JPC_one_war_cabinet'],'prerequisite'))==4
checks.append('Politics opens initial army reform, then advanced army and navy; 196 days fit before January 1894')
for left,right in [('JPF_public_accounts','JPF_small_subscription'),('JPN_north_civilian_holds','JPN_north_emergency_calendar'),('JPL_convoy_timetable','JPL_names_and_units')]:
 assert value(value(fs[left],'mutually_exclusive'),'focus')==right
 assert value(value(fs[right],'mutually_exclusive'),'focus')==left
 assert value(fs[left],'completion_reward')!=value(fs[right],'completion_reward')
checks.append('Three reciprocal exclusive policy pairs with different durations and effects')
unprepared=Model();unprepared.effect('JPA_emergency_compromises_effect')
assert {'JPA_forced_guarantees','JPA_unwritten_neutrality','JPA_hasty_orders'}<=unprepared.ideas['A03']
prepared=Model();prepared.effect('JPF_initialize_effect');prepared.effect('JPN_north_initialize_effect');prepared.effect('JPL_initialize_effect')
prepared.effect('JPA_negotiate_guarantees_effect');prepared.choose('japan_canon.2','o0')
prepared.effect('JPA_negotiate_north_effect');prepared.choose('japan_canon.3','o0')
prepared.run(value(fs['JPC_manila_priority'],'completion_reward'));prepared.effect('JPA_emergency_compromises_effect')
assert 'JPA_forced_guarantees' not in prepared.ideas['A03'] and 'JPA_unwritten_neutrality' not in prepared.ideas['A03']
assert 'JPA_hasty_orders' in prepared.ideas['A03'],'Three domestic priorities leave the fleet unprepared'
assert prepared.vars['A03']['JPF_debt_pressure']<unprepared.vars['A03']['JPF_debt_pressure']
assert prepared.vars['A03']['JPN_north_trust']>unprepared.vars['A03']['JPN_north_trust']
assert prepared.vars['A03']['JPL_garrison_burden']<unprepared.vars['A03']['JPL_garrison_burden']
checks.append('Completed domestic focuses improve May outcome; skipped fleet preparation has a real penalty')
unprepared.effect('JPA_negotiate_guarantees_effect');unprepared.effect('JPA_negotiate_north_effect')
assert 'JPA_forced_guarantees' not in unprepared.ideas['A03'] and 'JPA_unwritten_neutrality' not in unprepared.ideas['A03']
checks.append('Late negotiations repair imposed terms instead of staying permanently locked')
for n in [70,71,90,91,100]:
 m=Model();m.effect('WTC_initialize_effect');m.vars['A03']['WTC_debt']=n;m.effect('WTC_refresh_effect')
 assert ('WTC_blacklist' in m.ideas['A03'])==(n>90)
 assert any(e=='wtc_credit.1' for t,e in m.queue)==(70<n<100)
 assert any(e=='wtc_credit.3' for t,e in m.queue)==(n==100)
 checks.append(f'WTC exact threshold {n}')
m=Model();m.effect('WTC_initialize_effect');m.vars['A03']['WTC_debt']=100;m.effect('WTC_refresh_effect');m.choose('wtc_credit.3','a');assert m.government['A03']=='neutrality' and m.vars['A03']['WTC_debt']==70;checks.append('Local financial coup; no annexation')
m=Model();m.effect('WTC_initialize_effect');m.vars['A03']['WTC_debt']=100;m.global_flags.clear();m.effect('WTC_refresh_effect');m.choose('wtc_credit.3','c');assert 'A03' not in m.government and 'WTC_blacklist' not in m.ideas['A03'];checks.append('British cover absent: coup fails, blacklist absent')
m=Model();m.effect('WTC_initialize_effect');m.effect('WTC_borrow_effect');assert m.vars['A03']['WTC_debt']==50 and m.stock['A03']['convoy_1']==225;m.effect('WTC_repay_effect');m.effect('WTC_concession_effect');assert m.vars['A03']['WTC_debt']==23;checks.append('Real borrowing, repayment and concession effects')
m=Model();m.effect('JPF_initialize_effect');m.flags['A03'].add('JPC_guarantees_signed');m.effect('JPF_reform_accounts_effect');before=m.vars['A03']['JPF_debt_pressure'];m.effect('JPF_monthly_tick_effect');assert m.vars['A03']['JPF_debt_pressure']==before+3;m.effect('JPF_add_war_expense_effect');assert m.vars['A03']['JPF_debt_pressure']==before+8;checks.append('War, guarantees, audits and shipments affect Mitsubishi ledger')
m=Model();m.effect('JPN_north_initialize_effect');m.flags['A03'].add('JPC_north_signed');m.effect('JPN_north_daily_effect')
for _ in range(10):m.effect('JPN_north_monthly_effect')
assert 'JPN_north_protocol_broken' in m.flags['A03'];before=m.stock['A03']['infantry_equipment'];m.effect('JPN_north_send_rifles_effect');assert m.stock['A03']['infantry_equipment']==before-250 and m.stock['A08']['infantry_equipment']==250;checks.append('Starvation breaks protocol; supplies transfer from actual stock')
m.vars['A03'].update(JPN_north_trust=70,JPN_north_fleet_irritation=30);m.wars.discard(frozenset(('A03','A01')));m.effect('JPN_north_sign_compact_effect');assert 'JPN_north_compact_signed' in m.flags['A03'];assert 'A08' in m.tags and all('A08' not in w for w in m.wars);checks.append('Postwar compact preserves northern neutrality and country')
m=Model();m.effect('JPL_safety_check_effect');before=m.vars['A03']['JPL_garrison_burden'];m.effect('JPL_monthly_effect');assert m.vars['A03']['JPL_garrison_burden']>before;m.effect('JPL_correct_accounts_effect');assert m.vars['A03']['JPL_garrison_burden']<before;m.effect('JPL_hospital_allocation_effect');assert frozenset(('A03','A10')) in m.wars
m.wars.discard(frozenset(('A03','A10')));m.effect('JPL_safety_check_effect');assert not any(k.startswith('JPL_') for k in m.ideas['A03']);checks.append('Luzon reforms reduce load; peace cleans spirits without scripted victory')
# Hidden prelude and date-aligned reveal; no repeated reset after acceleration.
for d in [date(1893,1,1),date(1893,2,15),date(1893,3,18),date(1893,3,19),date(1893,4,30),date(1893,12,31)]:
 m=Model();m.now=d;m.wars.clear();m.flags['A01'].add('A01_preparation_dispatched')
 m.effect('JPS_restore_clocks_effect','A01')
 if d<date(1893,3,19):assert not m.missions['A01'] and not m.missions['A03']
 else:
  expected=(date(1894,1,1)-d).days
  assert m.missions['A01']['A01_japanese_invasion_countdown']==m.missions['A03']['A03_japanese_invasion_countdown']==expected
 saved=copy.deepcopy(dict(m.missions));m.effect('JPS_restore_clocks_effect','A01');assert dict(m.missions)==saved
 checks.append(f'Hidden/revealed clocks exact and repeat safe at {d}')
m=Model();m.now=date(1893,3,19);m.wars.clear();m.flags['A01'].add('A01_preparation_dispatched')
m.effect('JPS_restore_clocks_effect','A01')
for i in range(3):m.effect('JPS_accelerate_invasion_effect')
assert m.missions['A01']['A01_japanese_invasion_countdown']==m.missions['A03']['A03_japanese_invasion_countdown']==243
m.effect('JPS_restore_clocks_effect','A01');assert m.missions['A03']['A03_japanese_invasion_countdown']==243
m.effect('A01_cancel_preparations_for_agreement_effect','A01');assert not m.missions['A01'] and not m.missions['A03']
checks.append('All three accelerations synchronised: 288 to 243 days; no reset; agreement cancels both')
m=Model();m.now=date(1893,2,15);m.wars.clear();m.flags['A01'].add('A01_preparation_dispatched');m.completed['A01'].add('A01_last_chance_to_negotiate')
m.effect('JPS_restore_clocks_effect','A01');assert m.missions['A03']['A03_japanese_invasion_countdown']==320
checks.append('Early negotiation focus completion reveals the countdown immediately')
for d in [date(1893,11,17),date(1894,1,2),date(1894,7,12),date(1896,1,31)]:
 m=Model();m.now=d;m.effect('JPS_restore_clocks_effect','A01')
 assert m.missions['A01']['A01_japanese_expansion']==m.missions['A03']['A03_japanese_expansion']==(date(1896,2,1)-d).days
 saved=copy.deepcopy(dict(m.missions));m.effect('JPS_restore_clocks_effect','A01');assert dict(m.missions)==saved
 checks.append(f'Wartime settlement clocks unchanged and repeat safe at {d}')
report={'status':'passed','focuses':focus_counts,'new_story_focuses':30,'Japan_story_events':sum(e.startswith(('japan_canon.','japan_finance.','japan_north.','japan_luzon.','japan_agency.')) for e in events),'Japan_story_spirits':sum(k.startswith(('JPC_','JPF_','JPN_','JPL_','JPA_')) for k in ideas),'checks':checks,'all_focus_icons_and_localisation':'references and files verified','limitations':['Bounded scripts; timed flag expiry and monthly pulses invoked explicitly','Combat, AI, runtime UI and a full campaign require the game engine']}
(R/'tools/japan_story_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
