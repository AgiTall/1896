"""Check royal succession, mutually exclusive endings, assets and engine modifiers."""
from pathlib import Path
from datetime import date
import re,json
from PIL import Image
from add_canon_countries import parse,value
R=Path(__file__).resolve().parents[1]
def tree(p):return parse((R/p).read_text(encoding='utf-8-sig'))
fs={value(n,'id'):n for k,o,n in value(tree('common/national_focus/a01_focus.txt'),'focus_tree') if k=='focus'}
royal={k:n for k,n in fs.items() if 'A01_royal_path_revealed' in str(n) and any(a=='allow_branch' for a,b,c in n)}
manifest=json.loads((R/'tools/royal_story_manifest.json').read_text(encoding='utf-8'))
assert len(royal)==18+len(manifest['new_focuses'])
assert set(royal)==set(manifest['focus_art'])
assert {'A01_royal_dictatorship'}=={v for k,o,v in value(fs['A01_royal_constitution'],'mutually_exclusive')}
assert {'A01_royal_constitution'}=={v for k,o,v in value(fs['A01_royal_dictatorship'],'mutually_exclusive')}
def parents(fid):return [{v for k,o,v in n if k=='focus'} for a,b,n in fs[fid] if a=='prerequisite']
assert parents('A01_wilhelmina_comes_of_age')==[{'A01_emma_and_daughter'}]
assert {'A01_royal_naval_advisors'} in parents('A01_royal_dictatorship')
assert {'A01_island_delegation'} in parents('A01_crown_parliament')
def cond(n,flags,today):
 vals=[]
 for k,o,v in n:
  if k=='has_country_flag':ok=v in flags
  elif k=='OR':ok=any(cond([t],flags,today) for t in v)
  elif k=='NOT':ok=not any(cond([t],flags,today) for t in v)
  elif k=='date':ok=today>date(*map(int,v.split('.')))
  else:raise AssertionError(k)
  vals.append(ok)
 return all(vals)
gate=value(fs['A01_wilhelmina_comes_of_age'],'available')
flags={'A01_emma_regency'}
assert not cond(gate,flags,date(1895,1,1))
assert not cond(gate,flags,date(1898,8,30))
assert cond(gate,flags,date(1898,8,31))
assert cond(gate,flags|{'A01_early_royal_accession'},date(1895,1,1))
assert not cond(gate,{'A01_early_royal_accession','A01_wilhelmina_reigns'},date(1898,9,1))
events={value(n,'id'):n for k,o,n in tree('events/A01_monarchy.txt') if k=='country_event'}
options=[n for k,o,n in events['A01_monarchy.1'] if k=='option']
assert 'A01_early_royal_accession' not in str(options[0]) and 'A01_early_royal_accession' in str(options[1])
regency=dict((k,v) for k,o,v in tree('common/scripted_effects/A01_future_effects.txt'))['A01_establish_regency_effect']
assert 'A01_ludolf_crisis_resolved' in str(value(value(regency,'if'),'limit'))
assert 'A01_CROWN' in str(regency)
# Succession remains a transition to Wilhelmina, never a route back to Emma.
r=value(fs['A01_wilhelmina_comes_of_age'],'completion_reward')
assert ('clr_country_flag','=','A01_emma_regency') in r and ('set_country_flag','=','A01_wilhelmina_reigns') in r
assert any(k=='remove_dynamic_modifier' and value(v,'modifier')=='A01_admirals_council' for k,o,v in value(fs['A01_royal_dictatorship'],'completion_reward'))
assert any(k=='remove_dynamic_modifier' and value(v,'modifier')=='A01_racial_divide' for k,o,v in value(fs['A01_crown_commonwealth'],'completion_reward'))
assert not any('A01_government_' in str(value(n,'completion_reward')) for n in royal.values())
mods=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md').read_text(encoding='utf-8-sig')
ideas=value(value(tree('common/ideas/A01_monarchy.txt'),'ideas'),'country')
for k,o,n in ideas:
 for mod,op,v in value(n,'modifier'):assert '## '+mod+'\n' in mods or (mod=='production_speed_dockyard_factor' and 'production_speed_<Building>_factor' in mods),mod
for folder,size in [('gfx/flags',(82,52)),('gfx/flags/medium',(41,26)),('gfx/flags/small',(10,7))]:
 for tag in ('A01_CROWN','A01_COMMONWEALTH','A01_ROYAL_EMPIRE'):
  for suffix in ('','_neutrality','_democratic','_fascism','_communism'):
   im=Image.open(R/folder/(tag+suffix+'.tga'));assert im.size==size
colors=(R/'common/countries/cosmetic.txt').read_text()
for tag in ('A01_CROWN','A01_COMMONWEALTH','A01_ROYAL_EMPIRE'):assert tag+' = { color = rgb { 235 135 45 }' in colors
for lang in ('russian','english'):
 s=(R/f'localisation/{lang}/1896_main_l_{lang}.yml').read_text(encoding='utf-8-sig')
 keys=set(re.findall(r'^\s+(\S+):\d',s,re.M))
 for fid in royal.keys()-{'A01_crown_above_factions','A01_royal_island_charter','A01_crown_island_council','A01_crown_legal_guarantees','A01_wilhelmina_comes_of_age','A01_royal_constitution'}:assert fid in keys and fid+'_desc' in keys
 for k in events:
  assert k+'.t' in keys and k+'.d' in keys
  for a,b,n in events[k]:
   if a=='option':assert value(n,'name') in keys
print(f'PASS: {len(royal)} hidden royal focuses; exclusive endings; normal and early succession; guarded diary; real modifier names; RU/EN events; orange colours and all flag sizes.')
