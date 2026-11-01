"""Regression checks for the political gateway and affordable event choices."""
from validate_story_systems import Model, fs, events, value
from clarify_japan_branches import INDUSTRY

routes=['JPX_'+s for s in ['sea','land','trade','kami','throne']]

def ancestors(fid):
 parents=[v for k,o,n in fs[fid] if k=='prerequisite' for key,op,v in n if key=='focus']
 return set(parents).union(*(ancestors(p) for p in parents))
for fid,n in fs.items():
 if fid=='A03_imperial_council':continue
 if not fid.startswith('JPX_'):assert 'JPX_sea' in ancestors(fid),(fid,'bypasses canonical gateway')
 if fid in INDUSTRY:
  assert not value(fs[fid],'available'),(fid,'industry has an unrelated availability gate')
 # Alternatives may only lead to their own prologue institution, never the main campaign.
 for route in ['JPX_land','JPX_trade','JPX_kami','JPX_throne']:
  if route in ancestors(fid):assert fid == route+'_institution',(route,fid,'alternative joins main branch')
for i,fid in enumerate(routes,1):
 assert not value(fs[fid],'mutually_exclusive'),(fid,'horizontal connections between separate routes')
 gate=value(value(value(fs[fid],'available'),'NOT'),'OR')
 assert set(v for k,o,v in gate if k=='has_completed_focus')==set(routes)-{fid}
 for chosen in [None]+routes:
  available=not any(chosen==v for k,o,v in gate)
  assert available==(chosen is None or chosen==fid),(fid,chosen)
 assert ancestors(fid)=={'A03_imperial_council'}
 if fid=='JPX_sea':
  assert 'JPR_defence_budget' in ancestors(fid+'_institution')
 else:assert ancestors(fid+'_institution')=={'A03_imperial_council',fid}
 assert len([v for k,o,v in events[f'japan_paths.{i}'] if k=='option'])==2
 for pp in [0,49,50,100]:
  for option in ['a','b']:
   m=Model();m.effect('JPF_initialize_effect');m.pp['A03']=pp
   event=f'japan_paths.{i}'
   choice=next(n for k,o,n in events[event] if k=='option' and value(n,'name')==event+'.'+option)
   assert m.test(value(choice,'trigger',[]),'A03')==(option=='b' or pp>=50)
   if option=='a' and pp<50:continue
   oldwars=m.wars.copy();oldmissions=dict(m.missions['A03'])
   m.choose(event,option)
   assert m.pp['A03']==pp-(50 if option=='a' else 0)
   assert fid+('_funded' if option=='a' else '_limited') in m.flags['A03']
   assert m.wars==oldwars and dict(m.missions['A03'])==oldmissions
print('PASS: canonical gateway, five exclusive routes, both event options at 0/49/50/100 PP, no scripted peace or clock reset.')
