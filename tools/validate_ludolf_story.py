from pathlib import Path
import re,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
GAME=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
errors=[];checks=[]
def clean(t):return re.sub(r'"(?:\\.|[^"\\])*"|#[^\n]*','',t)
def read(p):return p.read_text(encoding='utf-8-sig',errors='replace')
def blocks(t,key):
 for m in re.finditer(r'\b'+re.escape(key)+r'\s*=\s*\{',t):
  depth=1;i=m.end();start=i
  while i<len(t) and depth:depth+=(t[i]=='{')-(t[i]=='}');i+=1
  yield t[start:i-1]
def check(ok,msg):
 if not ok:errors.append(msg)
def topblocks(t):
 pos=0
 while True:
  m=re.search(r'(\w+)\s*=\s*\{',t[pos:])
  if not m:break
  start=pos+m.end();depth=1;i=start
  while i<len(t) and depth:depth+=(t[i]=='{')-(t[i]=='}');i+=1
  yield m.group(1),t[start:i-1]
  pos=i
files=[ROOT/'common/bop/A01_ludolf.txt',ROOT/'common/scripted_effects/A01_ludolf_effects.txt',ROOT/'common/decisions/A01_ludolf_story.txt',ROOT/'common/on_actions/A01_borneo_story.txt',ROOT/'events/A01_ludolf_story.txt',ROOT/'common/characters/A01_admirals.txt',ROOT/'common/characters/A03.txt',ROOT/'common/ai_strategy_plans/A01_canonical.txt']
for p in files:
 depth=0
 for c in clean(read(p)):
  depth+=(c=='{')-(c=='}')
  if depth<0:break
 check(depth==0,f'{p.name}: unbalanced script')
checks.append('Balanced syntax in all new gameplay scripts')
events=read(ROOT/'events/A01_ludolf_story.txt')
eventids=set(re.findall(r'\bid\s*=\s*(ludolf\.\d+)\s',events))
allnew='\n'.join(read(p) for p in files)+read(ROOT/'common/national_focus/a01_focus.txt')
refs=set(re.findall(r'country_event\s*=\s*\{\s*id\s*=\s*(ludolf\.\d+)',allnew))
check(refs<=eventids,'Undefined story event references: '+str(refs-eventids))
focus_flat = ' '.join(read(ROOT/'common/national_focus/a01_focus.txt').split())
for n in ['1','2']:
 check(f'id = ludolf.{n} days = 1' in focus_flat,f'WTC event {n} not sent by focus')
check('A04 = { country_event = { id = ludolf.2' in focus_flat,'Second focus must target A04')
checks.append('Story event references and second-focus A01/A04 recipients')
categorytext='\n'.join(read(p) for p in (ROOT/'common/decisions/categories').glob('*.txt'))
categoryids={key for key,_ in topblocks(categorytext)}
for filename in ['A01_ludolf_story.txt','A01_batavian_congress.txt']:
 t=read(ROOT/'common/decisions'/filename)
 for key,body in topblocks(t):
  check(key in categoryids,f'Missing native decision category {key}')
  first=re.search(r'(\w+)\s*=',body)
  check(first is not None and first.group(1) not in ['icon','allowed','visible'],f'{key}: category metadata is incorrectly inside decision file')
checks.append('Native decision categories are separately declared')
for lang in ['russian','english']:
 texts='\n'.join(read(p) for p in (ROOT/'localisation'/lang).glob('*.yml'))
 keys=set(re.findall(r'^\s+(\S+):(?:\d+)?\s',texts,re.M))
 for token in re.findall(r'\b(?:title|desc|name)\s*=\s*(ludolf\.\w+(?:\.\w+)?)',events):check(token in keys,f'{lang}: missing {token}')
 for token in re.findall(r'\bid\s*=\s*(A01_\w+)',read(ROOT/'common/bop/A01_ludolf.txt')):check(token in keys,f'{lang}: missing BOP label {token}')
check('A01_initialize_balance_effect = yes' in read(ROOT/'common/national_focus/a01_focus.txt'),'Missing focus balance initialisation')
boptext=read(ROOT/'common/bop/A01_ludolf.txt')
ranges=[]
for b in blocks(boptext,'range'):
 lo=re.search(r'\bmin\s*=\s*(-?[\d.]+)',b);hi=re.search(r'\bmax\s*=\s*(-?[\d.]+)',b)
 if lo and hi:ranges.append((float(lo.group(1)),float(hi.group(1))))
ranges.sort();check(ranges[0][0]==-1 and ranges[-1][1]==1,'BOP does not span -1 to 1')
for a,b in zip(ranges,ranges[1:]):check(a[1]==b[0],f'BOP gap or overlap: {a} {b}')
checks.append('RU/EN event and BOP labels, contiguous BOP ranges')
effects=read(ROOT/'common/scripted_effects/A01_ludolf_effects.txt')
check('A03 = { transfer_state = 1024 transfer_state = 1023 transfer_state = 1059 transfer_state = 333 }' in effects,'Wrong Japanese territory settlement')
check('\n  transfer_state = 1022' in effects,'Wrong Indies territory settlement')
rights=list(blocks(effects,'give_resource_rights'))
check(len(rights)==7,'Resource rights must cover seven Borneo states including Limbang')
check(all('resources = { oil rubber }' in b and 'receiver = A03' in b for b in rights),'Resource rights must be oil/rubber only for A03')
checks.append('Japanese Sabah/Brunei/Limbang/Sarawak, Dutch interior and seven-state oil/rubber rights')
decisions=read(ROOT/'common/decisions/A01_ludolf_story.txt')
release_effects=read(ROOT/'common/scripted_effects/A01_future_effects.txt')
for tag,sid in [('A11',1055),('A12',334),('A13',1022)]:
 check(bool(re.search(r'target\s*=\s*'+tag+r'\s+autonomy_state\s*=\s*autonomy_puppet',release_effects)),f'{tag}: missing automatic puppet creation')
 check(f'state = {sid} resources = {{ oil rubber }}' in effects and 'A01_borneo_resource_rights_effect = yes' in release_effects,f'{tag}: missing retained resource rights')
 check(f'A01_charter_{tag}' not in decisions,f'{tag}: obsolete manual release decision')
 for folder,size in [('',(82,52)),('medium',(41,26)),('small',(10,7))]:
  p=ROOT/'gfx/flags'/folder/(tag+'.tga');check(p.exists() and Image.open(p).size==size,f'{tag}: missing flag {folder}')
checks.append('Three real subject countries, resource concessions and all flag sizes')
for p in [ROOT/'interface/A01_story_icons.gfx',ROOT/'interface/period_characters.gfx']:
 for tex in re.findall(r'texturefile = "([^"]+)"',read(p)):check((ROOT/tex).exists() or (GAME/tex).exists(),f'Missing texture {tex}')
for key in ['constitution','trade','wolf','ludolf','admirals','sultans','defeat','revanchism']:
 for folder,prefix,size in [('goals','focus',(95,85)),('ideas','idea',(60,68))]:
  im=Image.open(ROOT/f'gfx/interface/{folder}/{prefix}_story_{key}.dds');check(im.size==size and im.mode=='RGBA' and im.getextrema()[3][0]==0,f'{key}: invalid DDS format')
checks.append('All sprite textures, 16 DDS dimensions and alpha')
for tag,characters in [('A01',['fabius','casembroot','surya_wirata']),('A03',['emperor_meiji'])]:
 hist=read(ROOT/f'history/countries/{tag} - Placeholder.txt')
 for char in characters:check(f'recruit_character = {tag}_{char}' in hist,f'{tag}: character {char} not recruited')
check('recruit_character = A03_imperial_council' not in read(ROOT/'history/countries/A03 - Placeholder.txt'),'Japan still starts with placeholder leader')
checks.append('Named Japanese leader and three recruited A01 admirals')
report={'checks':checks,'story_events':len(eventids),'bop_ranges':len(ranges),'errors':errors,'campaign_simulation':'Not yet run; this is static validation.'}
(ROOT/'tools/ludolf_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(bool(errors))
