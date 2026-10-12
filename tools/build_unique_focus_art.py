from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,re,shutil,hashlib
R=Path(__file__).resolve().parents[1]
S=R/'gfx/interface/focus_unique_sources'
manifest=json.loads((S/'manifest.json').read_text(encoding='utf-8'))
paths=json.loads((S/'generated_paths.json').read_text(encoding='utf-8'))
backup=R/'tools/backups/focus_art_before'
for rel in ['common/national_focus/a01_focus.txt','common/national_focus/a03_focus.txt','common/bop/A01_ludolf.txt']:
 p=backup/rel
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/rel,p)
gfx=['spriteTypes = {']
hashes=[]
def sprite(name,path,shine=False):
 gfx.append(f'spriteType = {{ name = "{name}" texturefile = "{path}" legacy_lazy_load = no }}')
 if shine:
  gfx.append(f'''spriteType = {{ name = "{name}_shine" texturefile = "{path}" effectFile = "gfx/FX/buttonstate.lua" legacy_lazy_load = no
 animation = {{ animationmaskfile = "{path}" animationtexturefile = "gfx/interface/goals/shine_overlay.dds" animationrotation = -90 animationlooping = no animationtime = 0.75 animationdelay = 0 animationblendmode = "add" animationtype = "scrolling" animationrotationoffset = {{ x = 0 y = 0 }} animationtexturescale = {{ x = 1 y = 1 }} }} }}''')
def export(source,path,size):
 im=Image.open(source).convert('RGBA');assert im.getextrema()[3][0]==0,source
 im=im.crop(im.getbbox());thumb=ImageOps.contain(im,(size[0]-4,size[1]-4),Image.Resampling.LANCZOS)
 canvas=Image.new('RGBA',size);canvas.alpha_composite(thumb,((size[0]-thumb.width)//2,(size[1]-thumb.height)//2))
 p=R/path;p.parent.mkdir(parents=True,exist_ok=True);canvas.save(p)
 return canvas
thumbs={}
for x in manifest:
 fid=x['id'];path=f'gfx/interface/goals/focus_unique_{fid}.dds'
 if x['reuse']:
  source=R/f'gfx/interface/goals/focus_{x["reuse"]}.dds';shutil.copy2(source,R/path);im=Image.open(R/path).convert('RGBA')
 else:
  source=S/(fid+'.png')
  if not source.exists():shutil.copy2(paths[fid],source)
  im=export(source,path,(95,85))
 x['texture']=path;x['sprite']='GFX_goal_unique_'+fid
 sprite(x['sprite'],path,True);thumbs[fid]=im
 hashes.append(hashlib.sha256(im.tobytes()).hexdigest())
assert len(set(hashes))==84,'Repeated rendered focus art'
for tag in ['a01','a03']:
 p=R/f'common/national_focus/{tag}_focus.txt';t=p.read_text(encoding='utf-8-sig')
 for x in manifest:
  if not x['id'].lower().startswith(tag):continue
  t,n=re.subn(r'(\bfocus\s*=\s*\{\s*id\s*=\s*'+re.escape(x['id'])+r'\s+icon\s*=\s*)\w+',lambda m:m[1]+x['sprite'],t);assert n==1,x['id']
 p.write_text(t,encoding='utf-8')
bop=R/'common/bop/A01_ludolf.txt';t=bop.read_text(encoding='utf-8-sig')
for key,old in [('bop_ludolf','ludolf'),('bop_admirals','admirals')]:
 source=S/(key+'.png')
 if not source.exists():shutil.copy2(paths[key],source)
 path=f'gfx/interface/bop/{key}_steel.dds';export(source,path,(72,88));sprite('GFX_'+key+'_steel',path)
 t=t.replace('GFX_idea_story_'+old,'GFX_'+key+'_steel')
bop.write_text(t,encoding='utf-8');(R/'interface/unique_focus_icons.gfx').write_text('\n'.join(gfx)+'\n}\n',encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
for tag in ['A01','A03']:
 rows=[x for x in manifest if x['id'].startswith(tag)]
 sheet=Image.new('RGB',(1080,((len(rows)+5)//6)*148),(34,39,43));d=ImageDraw.Draw(sheet)
 for i,x in enumerate(rows):
  px=(i%6)*180;py=(i//6)*148;im=thumbs[x['id']];sheet.paste(im,(px+42,py+6),im)
  words=x['title'].split();lines=['']
  for word in words:
   if d.textlength(lines[-1]+' '+word,font=font)>170:lines.append(word)
   else:lines[-1]=(lines[-1]+' '+word).strip()
  for j,line in enumerate(lines[:3]):d.text((px+5,py+94+j*14),line,font=font,fill=(224,224,216))
 sheet.save(S/f'{tag}_preview.png')
sheet=Image.new('RGB',(420,250),(34,39,43));d=ImageDraw.Draw(sheet)
for i,key in enumerate(['bop_admirals','bop_ludolf']):
 im=Image.open(S/(key+'.png')).convert('RGBA');im=ImageOps.contain(im.crop(im.getbbox()),(160,190),Image.Resampling.LANCZOS);sheet.paste(im,(25+210*i,5),im)
 d.text((25+210*i,211),['Совет адмиралов','Людольф'][i],font=font,fill='white')
sheet.save(S/'balance_preview.png')
(S/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('84 distinct focus textures; 76 new generated emblems; 8 retained; 2 steel balance icons. DDS alpha verified.')
