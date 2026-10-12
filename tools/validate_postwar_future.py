"""Execute the new political branches in a strict script model, plus reference audits.

This checks scripted behaviour, not rendering or a running HOI4 campaign.
"""
from pathlib import Path
from datetime import date
import copy, json, re
from add_canon_countries import parse
def value(node,key,default=None):return next((v for k,o,v in node if k==key),default)
R=Path(__file__).resolve().parents[1]
G=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
def read(p):return (R/p).read_text(encoding='utf-8-sig')
def filetree(p):return parse(read(p))
effects={k:v for p in ['common/scripted_effects/A01_future_effects.txt','common/scripted_effects/A01_ludolf_effects.txt','common/scripted_effects/A01_federal_recovery.txt','common/scripted_effects/A01_crown_struggle.txt'] for k,o,v in filetree(p)}
focuses={value(b,'id'):b for k,o,b in value(filetree('common/national_focus/a01_focus.txt'),'focus_tree') if k=='focus'}
events={value(b,'id'):b for p in (R/'events').glob('*.txt') for k,o,b in parse(p.read_text(encoding='utf-8-sig')) if k=='country_event'}
decisions={k:b for cat,o,body in filetree('common/decisions/A01_future_contest.txt') for k,o,b in body}
decisions.update({k:b for cat,o,body in filetree('common/decisions/A01_royal_story.txt') for k,o,b in body})
checks=[]

class Model:
 def __init__(self):
  self.flags={t:set() for t in ['A01','A03','A04','A11','A12','A13','A14']}
  self.flags['A01'].add('A01_borneo_treaty')
  self.exists={'A01','A03'}
  self.owners={1055:'A01',334:'A01',1022:'A01',1023:'A03',1024:'A03',1059:'A03',333:'A03'}
  self.subjects={};self.cores=set();self.rights=set();self.missions={}
  self.leader='A01_ludolf_sloot_van_de_beele';self.retired=set();self.recruited=set()
  self.ideas=set();self.dynamic={'A01_racial_divide','A01_admirals_council'}
  self.notifications=[];self.completed=set();self.bop=-.2;self.today=date(1895,1,1)
  self.politics={'ruling_party':'neutrality','elections_allowed':'no'};self.cosmetic=None;self.layout=False
 def cond(self,node,tag='A01',state=None):
  values=[]
  for k,o,v in node:
   if k in self.flags:ok=self.cond(v,k,state)
   elif k in ['AND','hidden_trigger']:ok=self.cond(v,tag,state)
   elif k=='OR':ok=any(self.cond([entry],tag,state) for entry in v)
   elif k=='NOT':ok=not self.cond(v,tag,state)
   elif k=='always':ok=v=='yes'
   elif k=='tag':ok=tag==v
   elif k=='has_country_flag':ok=v in self.flags[tag]
   elif k=='country_exists':ok=v in self.exists
   elif k=='owns_state':ok=self.owners.get(int(v))==tag
   elif k=='is_subject_of':ok=self.subjects.get(tag)==v
   elif k=='has_completed_focus':ok=v in self.completed
   elif k=='has_active_mission':ok=v in self.missions
   elif k=='has_war_with':ok=False
   elif k=='power_balance_value':
    _,comparison,threshold=next(e for e in v if e[0]=='value')
    ok=self.bop<float(threshold) if comparison=='<' else self.bop>float(threshold)
   elif k=='date':ok=self.today>date(*map(int,v.split('.')))
   else:raise AssertionError(('Unmodelled condition',k))
   values.append(ok)
  return all(values)
 def run(self,node,tag='A01',state=None):
  for k,o,v in node:
   if k=='if':
    if self.cond(value(v,'limit'),tag,state):self.run([e for e in v if e[0]!='limit'],tag,state)
   elif k in effects:self.run(effects[k],tag,state)
   elif k=='hidden_effect':self.run(v,tag,state)
   elif k in self.flags:self.run(v,k,state)
   elif k.isdigit():self.run(v,tag,int(k))
   elif k=='owner':self.run(v,self.owners[state],state)
   elif k=='set_country_flag':self.flags[tag].add(value(v,'flag') if isinstance(v,list) else v)
   elif k=='clr_country_flag':self.flags[tag].discard(v)
   elif k=='activate_mission':self.missions[v]=int(value(decisions[v],'days_mission_timeout'))
   elif k=='remove_mission':self.missions.pop(v,None)
   elif k=='add_days_mission_timeout':self.missions[value(v,'mission')]+=int(value(v,'days'))
   elif k=='transfer_state':self.owners[int(v)]=tag;self.exists.add(tag)
   elif k=='add_core_of':self.cores.add((state,v))
   elif k=='set_autonomy':self.subjects[value(v,'target')]=tag
   elif k=='give_resource_rights':self.rights.add((int(value(v,'state')),value(v,'receiver')))
   elif k=='set_power_balance':self.bop=float(value(v,'set_value'))
   elif k=='add_power_balance_value':self.bop+=float(value(v,'value'))
   elif k=='country_event':self.notifications.append(value(v,'id'))
   elif k=='add_ideas':self.ideas.add(v)
   elif k=='remove_ideas':self.ideas.discard(v)
   elif k=='remove_dynamic_modifier':self.dynamic.discard(value(v,'modifier'))
   # Category arithmetic is exercised separately by validate_crown_rework.py.
   elif k=='A01_update_spirit_categories':pass
   elif k=='remove_power_balance':self.bop=0
   elif k=='retire_character':self.retired.add(v)
   elif k=='recruit_character':self.recruited.add(v)
   elif k=='promote_character':self.leader=value(v,'character')
   elif k=='add_country_leader_role':self.leader=value(v,'character')
   elif k=='set_politics':self.politics.update({a:c for a,b,c in v})
   elif k=='mark_focus_tree_layout_dirty':self.layout=True
   elif k=='set_cosmetic_tag':self.cosmetic=v
   elif k=='every_subject_country':
    for subject,overlord in list(self.subjects.items()):
     if overlord==tag and self.cond(value(v,'limit'),subject):
      for a,b,effect in v:
       if a=='A01':
        for effectkey,op,annex in effect:
         assert effectkey=='annex_country' and value(annex,'target')=='PREV'
         self.owners={sid:tag if owner==subject else owner for sid,owner in self.owners.items()}
         self.subjects.pop(subject);self.exists.discard(subject)
   elif k in ['name','ai_chance','trigger','set_popularities','set_party_name','add_political_power','add_stability','add_war_support','add_to_variable','clamp_variable','army_experience','navy_experience','set_variable','force_update_dynamic_modifier','add_extra_state_shared_building_slots','add_building_construction']:pass
   else:raise AssertionError(('Unmodelled effect',k))
 def focus(self,fid):
  assert self.cond(value(focuses[fid],'available',[])),fid
  self.completed.add(fid);self.run(value(focuses[fid],'completion_reward'))

# Cabinet mandate must open hearings without touching the incumbent, even at -1.
for balance in [-1,0,1]:
 m=Model();m.bop=balance;m.focus('A01_pacific_settlement')
 assert m.leader=='A01_ludolf_sloot_van_de_beele' and not m.retired
 assert 'A01_postwar.1' in m.notifications and not m.missions
 m.missions['A01_motion_to_dismiss_ludolf']=100
 m.run(effects['A01_begin_dismissal_debate_effect'])
 assert m.missions['A01_motion_to_dismiss_ludolf']==100
 for eid in ['ludolf.33','ludolf.34']:
  for k,o,option in events[eid]:
   if k=='option':
    trial=copy.deepcopy(m);trial.run(option)
    assert trial.leader==m.leader and not trial.retired
checks.append('Cabinet schedules the political contest; extreme balance and queued legacy options cannot dismiss Ludolf')

m=Model();m.focus('A01_pacific_settlement');m.run(effects['A01_establish_federal_mandate_effect']);m.focus('A01_ludolf_survives')
assert not m.cond(value(focuses['A01_negotiated_resignation'],'available'))
assert 'A01_federal_mandate' in m.flags['A01'] and m.leader=='A01_ludolf_sloot_van_de_beele'
m.run(effects['A01_create_autonomous_sultanates_effect'])
assert m.subjects=={'A11':'A01','A12':'A01','A13':'A01'}
assert all(m.owners[s]==t for t,s in [('A11',1055),('A12',334),('A13',1022)])
assert {(1055,'A03'),(334,'A03'),(1022,'A03')}<=m.rights
assert 'A01_sultanates_back_ludolf' in m.flags['A01']
trial=Model();trial.owners[1055]='A03';trial.run(effects['A01_create_autonomous_sultanates_effect'])
assert trial.owners[1055]=='A03' and 'A11' not in trial.subjects
checks.append('Focus releases three real subjects automatically, retains concessions and never transfers foreign-owned land')

m.run(next(v for k,o,v in events['ludolf.31'] if k=='option'))
for fid in ['A01_equal_citizenship','A01_abolish_admirals_council','A01_elected_civil_service','A01_democratic_federation']:m.focus(fid)
assert m.politics['elections_allowed']=='no'
m.run(value(events['A01_postwar.3'],'immediate'))
m.run(next(v for k,o,v in events['A01_postwar.3'] if k=='option'))
assert m.leader=='A01_ludolf_sloot_van_de_beele'
assert m.politics['ruling_party']=='democratic' and m.politics['elections_allowed']=='yes'
assert not m.dynamic and not m.missions and m.cosmetic=='A01_FEDERAL'
before=copy.deepcopy(m.__dict__);m.run(effects['A01_establish_military_rule_effect']);assert before==m.__dict__
checks.append('Federal route preserves Ludolf, removes racial restrictions, enables democracy and blocks subsequent military takeover')

m=Model();m.focus('A01_pacific_settlement');m.run(effects['A01_establish_military_rule_effect']);m.focus('A01_negotiated_resignation')
assert m.leader=='A01_council_of_admirals' and 'A01_ludolf_imprisoned' in m.flags['A01']
for fid in ['A01_purge_civil_service','A01_purge_officer_corps','A01_military_state']:m.focus(fid)
assert {'A01_industrial_advisory_council','A01_surya_wirata','A01_knil_inspectorate'}<=m.retired
assert m.politics['elections_allowed']=='no' and 'A01_total_military_state' in m.ideas
before=copy.deepcopy(m.__dict__);m.run(effects['A01_establish_federal_mandate_effect']);m.run(effects['A01_establish_regency_effect']);assert before==m.__dict__
checks.append('Council arrests Ludolf; purges remove actual advisers and a commander; the dictatorship cannot be overwritten')

royal=[fid for fid in focuses if fid in ['A01_crown_above_factions','A01_royal_island_charter','A01_wilhelmina_comes_of_age','A01_royal_constitution']]
assert len(royal)==4
for balance,eligible in [(-.101,False),(-.1,True),(-.099,True),(0,True),(.099,True),(.1,True),(.101,False),(.8,False)]:
 m=Model();m.bop=balance;m.focus('A01_pacific_settlement');m.flags['A01'].add('A01_dismissal_debate_active')
 assert all(not m.cond(value(focuses[fid],'allow_branch')) for fid in royal)
 assert m.cond(value(events['A01_future.16'],'trigger'))==eligible
checks.append('All four secret focuses remain absent; event boundaries match the unstable equilibrium range')
m=Model();m.focus('A01_pacific_settlement');m.bop=0;m.flags['A01'].add('A01_dismissal_debate_active')
m.run(next(v for k,o,v in events['A01_future.16'] if k=='option'))
assert m.leader=='A01_ludolf_sloot_van_de_beele' and m.layout
m.run(effects['A01_establish_regency_effect']);m.focus('A01_crown_above_factions')
assert m.leader=='A01_emma_waldeck_pyrmont' and m.layout
assert all(m.cond(value(focuses[fid],'allow_branch')) for fid in royal)
m.today=date(1898,8,30);assert not m.cond(value(focuses['A01_wilhelmina_comes_of_age'],'available'))
m.today=date(1898,8,31);m.focus('A01_wilhelmina_comes_of_age');m.focus('A01_summon_grand_council')
# The expanded political struggle is exercised through all three resolutions by
# validate_royal_story.py; this older test concerns succession and path isolation.
m.flags['A01'].update({'A01_admiralty_defeated','A01_island_settlement'})
m.focus('A01_settle_crown_crisis');m.focus('A01_royal_constitution')
assert m.leader=='A01_wilhelmina_monarch' and 'A01_emma_waldeck_pyrmont' in m.retired
checks.append('Accepted secret offer reveals the branch; succession is blocked until 31 August 1898 and replaces Emma correctly')

assert 'A01_future_of_netherlands' not in focuses
assert 'A01_federal_defence_compact' not in focuses
for fid in ['A01_ludolf_survives','A01_negotiated_resignation','A01_crown_above_factions']:
 assert value(value(focuses[fid],'prerequisite'),'focus')=='A01_pacific_settlement'
m=Model();m.focus('A01_pacific_settlement');m.run(effects['A01_establish_federal_mandate_effect']);m.focus('A01_ludolf_survives')
assert not m.cond(value(events['ludolf.31'],'trigger'))
assert not m.cond(value(focuses['A01_negotiated_resignation'],'available'))
assert m.leader=='A01_ludolf_sloot_van_de_beele'
checks.append('Cabinet directly precedes all three political roots; the sultan petition and debate are not focus requirements')

militia=parse(read('history/units/A01_indonesian_militia.txt'))
template=value(militia,'division_template')
regiments=value(template,'regiments')
assert len(regiments)==3 and all(k=='militia' for k,o,v in regiments)
assert value(template,'is_locked')=='yes'
assert sum(k=='division' for k,o,v in value(militia,'units'))==12
units=parse((G/'common/units/infantry.txt').read_text(encoding='utf-8-sig'))
assert value(value(units,'sub_units'),'militia') is not None
tech=parse((G/'common/technologies/infantry.txt').read_text(encoding='utf-8-sig'))
assert ('militia',None,None) in value(value(value(tech,'technologies'),'militia_tech'),'enable_subunits')
volunteer=next(v for k,o,v in events['A01_japan.32'] if k=='option')
spawn=value(volunteer,'if')
keys=[k for k,o,v in spawn]
assert keys.index('set_technology')<keys.index('load_oob')
assert value(value(spawn,'set_technology'),'militia_tech')=='1'
assert value(spawn,'load_oob').strip('"')=='A01_indonesian_militia'
cleanup=read('common/scripted_effects/borneo_war_effects.txt')
assert 'delete_unit_template_and_units = { division_template = "Indische Vrijwilligers" }' in cleanup
checks.append('Volunteer outcome unlocks vanilla militia before spawning twelve locked three-battalion divisions; peace cleanup remains attached')

# Full reference audit for all focus definitions, new events and assets.
all_focuses={}
for p in (R/'common/national_focus').glob('*.txt'):
 for k,o,tree in parse(p.read_text(encoding='utf-8-sig')):
  if k=='focus_tree':
   for key,op,body in tree:
    if key=='focus':
     fid=value(body,'id');assert fid not in all_focuses,fid;all_focuses[fid]=body
assert 'A03_batavia_ultimatum' not in all_focuses
assert 'A03_batavia_ultimatum' not in read('common/ai_strategy_plans/A01_canonical.txt')
for fid,body in all_focuses.items():
 for k,o,v in body:
  if k in ['prerequisite','mutually_exclusive']:
   for _,_,reference in v:assert reference in all_focuses,(fid,reference)
newfocuses=[fid for fid in focuses if fid in royal or fid.startswith('A01_purge_') or fid in ['A01_equal_citizenship','A01_elected_civil_service','A01_democratic_federation','A01_military_state']]
sprite_text='\n'.join(p.read_text(encoding='utf-8-sig',errors='replace') for root in [R/'interface',G/'interface'] for p in root.glob('*.gfx'))
for fid in newfocuses:
 assert re.search(r'name\s*=\s*"'+re.escape(value(focuses[fid],'icon'))+'"',sprite_text),(fid,'missing focus icon')
assert not any(k=='on_activate' for k,o,v in filetree('common/bop/A01_ludolf.txt'))
assert ('always','=','no') in value(events['pacific.4'],'trigger')
for eid in [5,16]:
 assert not Model().cond(value(events[f'A01_future.{eid}'],'trigger'))
new_scripts='\n'.join(read(p) for p in ['common/scripted_effects/A01_future_effects.txt','common/on_actions/A01_future_on_actions.txt','events/A01_future_events.txt','common/decisions/A01_future_contest.txt'])+read('common/national_focus/a01_focus.txt')
for ref in re.findall(r'country_event\s*=\s*\{\s*id\s*=\s*([\w.]+)',new_scripts):assert ref in events,ref
for lang in ['russian','english']:
 loc='\n'.join(p.read_text(encoding='utf-8-sig') for p in (R/'localisation'/lang).glob('*.yml'))
 keys=re.findall(r'^\s+(\S+):(?:\d+)?\s',loc,re.M)
 for fid in ['A01_equal_citizenship','A01_elected_civil_service','A01_democratic_federation','A01_purge_civil_service','A01_purge_officer_corps','A01_military_state']+royal:
  assert keys.count(fid)>=1,(lang,fid,keys.count(fid))
  duplicate_values=re.findall(r'^\s*'+re.escape(fid)+r':\d*\s+"(.*)"',loc,re.M)
  assert len(set(duplicate_values))==1,(lang,fid,'conflicting overrides')
  assert keys.count(fid+'_desc')>=1,(lang,fid)
 for eid in range(1,18):
  for suffix in ['t','d','a']:assert keys.count(f'A01_future.{eid}.{suffix}')==1,(lang,eid,suffix)
 gfx='\n'.join(p.read_text(encoding='utf-8-sig',errors='replace') for p in (R/'interface').glob('*.gfx'))
 for picture in re.findall(r'picture = (GFX_\w+)',read('events/A01_future_events.txt')):assert f'name = "{picture}"' in gfx,picture
checks.append('Focus prerequisites, retired ultimatum, event references, RU/EN localisation uniqueness and event illustrations')
report=dict(status='passed',checks=checks,engine_campaign_test='Not run; this model does not validate engine rendering or combat.')
(R/'tools/postwar_future_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
