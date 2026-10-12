from pathlib import Path
import re,shutil
ROOT=Path(__file__).resolve().parents[1]
BACK=ROOT/'tools/backups/ludolf_before'
def write(path,t):
 p=ROOT/path
 if p.exists() and not (BACK/path).exists():(BACK/path).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,BACK/path)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf-8')
def endblock(t,start):
 depth=1;i=start+1;quote=False;escape=False
 while depth:
  c=t[i]
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='{':depth+=1
  elif c=='}':depth-=1
  i+=1
 return i
def entries(t):
 pos=0
 while pos<len(t):
  m=re.search(r'(\w+)\s*=\s*',t[pos:])
  if not m:break
  start=pos+m.start();value=pos+m.end();key=m.group(1)
  if t[value]=='{':end=endblock(t,value)
  elif t[value]=='"':end=t.index('"',value+1)+1
  else:
   q=re.match(r'[^\s}]+',t[value:]);end=value+len(q.group(0))
  yield key,t[start:end],value-start
  pos=end

# Country history uses an else inside the if, unlike ordinary effect scripts.
for tag in ['A01','A03']:
 path=f'history/countries/{tag} - Placeholder.txt';t=(ROOT/path).read_text(encoding='utf-8-sig')
 while True:
  matched=False
  for m in re.finditer(r'(?m)^if\s*=\s*\{',t):
   close=endblock(t,t.index('{',m.start()));nextm=re.match(r'\s*else\s*=\s*\{',t[close:])
   if nextm:
    estart=close+nextm.start();brace=close+nextm.end()-1;eend=endblock(t,brace)
    t=t[:close-1]+t[estart:eend]+'\n}'+t[eend:];matched=True;break
  if not matched:break
 if tag=='A01':
  if 'recruit_character = A01_council_of_admirals' not in t:t+='\nrecruit_character = A01_council_of_admirals\n'
  if 'promote_character = A01_ludolf_sloot_van_de_beele' not in t:t+='promote_character = A01_ludolf_sloot_van_de_beele\n'
 write(path,t)

# Native category definitions belong in common/decisions/categories.
categories=[]
for name in ['A01_ludolf_story.txt','pacific_preparations.txt','A01_batavian_congress.txt']:
 path='common/decisions/'+name;t=(ROOT/path).read_text(encoding='utf-8-sig');result=''
 for category,whole,valuepos in entries(t):
  if whole[valuepos]!='{':raise ValueError(category)
  content=whole[valuepos+1:-1];headers=[];decisions=[]
  for key,item,_ in entries(content):
   if key in ['icon','allowed','visible','available','priority','picture','on_map_area','on_map_mode']:headers.append(item)
   else:decisions.append(item)
  if headers:categories.append(category+' = {\n'+'\n'.join(headers)+'\n}\n')
  result+=category+' = {\n'+'\n'.join(decisions)+'\n}\n'
 write(path,result)
# Preserve extracted definitions if this fixer is run again after extraction.
if categories:
 path='common/decisions/categories/A01_story_categories.txt';p=ROOT/path
 merged={key:item for key,item,_ in entries(p.read_text())} if p.exists() else {}
 for category in categories:
  for key,item,_ in entries(category):merged[key]=item
 write(path,'\n\n'.join(merged.values())+'\n')

for path in ['common/national_focus/a01_focus.txt','common/scripted_effects/A01_ludolf_effects.txt']:
 t=(ROOT/path).read_text(encoding='utf-8-sig');t=re.sub(r'\s*recruit_character = A01_council_of_admirals\s*','\n',t);t=t.replace(' set_default = yes','');write(path,t)
path='common/dynamic_modifiers/A01_dynamic_modifiers.txt';t=(ROOT/path).read_text(encoding='utf-8-sig')
t=re.sub(r'hidden_modifier\s*=\s*\{\s*(mobilization_laws_cost_factor\s*=\s*A01_admirals_mobilization_law_cost\s*economy_cost_factor\s*=\s*A01_admirals_economy_law_cost\s*trade_laws_cost_factor\s*=\s*A01_admirals_trade_law_cost)\s*\}',r'\1',t)
write(path,t)
# Legacy congress conditions use the engine's global tension trigger.
path='common/decisions/A01_batavian_congress.txt';write(path,(ROOT/path).read_text().replace('has_world_tension','threat').replace('global_threat','threat'))
path='interface/A01_ideas.gfx';t=(ROOT/path).read_text(encoding='utf-8-sig').replace('idea_pacific_batavia.dds','idea_story_admirals.dds').replace('idea_pacific_industry.dds','idea_story_trade.dds');write(path,t)
# The atlas expects 32bpp TGA flags.
from PIL import Image
for p in (ROOT/'gfx/flags').rglob('A1[123].tga'):Image.open(p).convert('RGBA').save(p)
print('Native decision category files, history conditional syntax, Council recruitment, BOP setup, dynamic laws and 32bpp flags repaired.')
