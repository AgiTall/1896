"""Validate preserved focus artwork and the expanded royal asset references."""
from pathlib import Path
from PIL import Image
import json,re,hashlib
from add_canon_countries import parse,value
R=Path(__file__).resolve().parents[1]
S=R/'gfx/interface/focus_unique_sources'
M=json.loads((S/'manifest.json').read_text(encoding='utf-8'))
royal=json.loads((R/'tools/royal_story_manifest.json').read_text(encoding='utf-8'))['focus_art']
gfx='\n'.join(p.read_text(encoding='utf-8-sig') for p in (R/'interface').glob('*.gfx'))
sprites=dict(re.findall(r'name\s*=\s*"([^"]+)"\s+texturefile\s*=\s*"([^"]+)"',gfx))
hashes=[]
for asset in M:
 name=asset['sprite'];assert name in sprites and name+'_shine' in sprites,name
 im=Image.open(R/sprites[name]).convert('RGBA')
 assert im.size==(95,85) and im.getextrema()[3]==(0,255),asset['id']
 assert sprites[name]==sprites[name+'_shine']
 hashes.append(hashlib.sha256(im.tobytes()).hexdigest())
assert len(hashes)==len(set(hashes))==84
counts={}
for tag in ('A01','A03'):
 path=f'common/national_focus/{tag.lower()}_focus.txt'
 fs={value(n,'id'):n for k,o,n in value(parse((R/path).read_text(encoding='utf-8-sig')),'focus_tree') if k=='focus'}
 counts[tag]=len(fs)
 for fid,n in fs.items():
  name=value(n,'icon');assert name in sprites,fid
  if fid in royal:
   assert name=='GFX_'+fid and name+'_shine' in sprites,fid
   im=Image.open(R/sprites[name]).convert('RGBA');assert im.size==(95,85) and im.getextrema()[3]==(0,255)
 if tag=='A01':
  before=R/'tools/backups/royal_story'/path
  old={value(n,'id'):n for k,o,n in value(parse(before.read_text(encoding='utf-8-sig')),'focus_tree') if k=='focus'}
  for fid,n in old.items():
   if fid not in royal:assert fs[fid]==n,('Unrelated focus changed',fid)
bop=(R/'common/bop/A01_ludolf.txt').read_text(encoding='utf-8-sig')
for key in ('bop_ludolf','bop_admirals'):
 name='GFX_'+key+'_steel';assert name in bop
 im=Image.open(R/sprites[name]).convert('RGBA');assert im.size==(72,88) and im.getextrema()[3][0]==0
 pixels=[(r,g,b) for r,g,b,a in im.get_flattened_data() if a>200]
 assert sum(max(p)-min(p)>12 for p in pixels)/len(pixels)<0.001
report={'status':'passed','focus_counts':counts,'preserved_unique_textures':len(set(hashes)),'royal_focus_sprites':len(royal),'royal_art_subjects':len(set(royal.values())),'checks':['All 84 earlier generated textures retain DDS alpha and shine sprites','Every current focus sprite resolves','Non-royal focus gameplay and layout preserved against task backup','Royal emblems have transparent native-size DDS and shine effects','Original grayscale balance emblems preserved'],'runtime':'In-game focus rendering not inspected.'}
(R/'tools/focus_art_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
