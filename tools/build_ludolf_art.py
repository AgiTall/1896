from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import json,shutil
ROOT=Path(__file__).resolve().parents[1]
SRC=Path('C:/Users/AgiTall/.codex/generated_images/01a12514-d2e9-7811-b9a8-8f599dd9e8fe')
files={
'constitution':'exec-06db97ed-2065-46fb-9145-f0e06d15b050.png','trade':'exec-e99ede5b-04aa-4d86-82eb-c2b31a01c2dc.png','wolf':'exec-90c41037-34d7-461d-817b-3855c0f883d8.png','ludolf':'exec-84795e57-f337-4193-adc1-251fd0c82e81.png','admirals':'exec-4762a6f4-2599-4223-aad2-65551b5ad77a.png','sultans':'exec-31add499-3130-4671-8f1f-c9a4e465fc72.png','defeat':'exec-9fb4bcf4-ad38-4774-b118-ecac43a04b98.png','revanchism':'exec-0d62c4b6-135f-43b9-9113-71d328242fd6.png'}
out=ROOT/'gfx/interface/ludolf_sources';out.mkdir(parents=True,exist_ok=True)
preview=Image.new('RGB',(800,300),(35,40,40));draw=ImageDraw.Draw(preview)
gfx='spriteTypes = {\n'
def sprite(name,path,shine=False):
 global gfx
 gfx+=f'spriteType = {{ name = "{name}" texturefile = "{path}" legacy_lazy_load = no }}\n'
 if shine:
  gfx+=f'''spriteType = {{ name = "{name}_shine" texturefile = "{path}" effectFile = "gfx/FX/buttonstate.lua" legacy_lazy_load = no
 animation = {{ animationmaskfile = "{path}" animationtexturefile = "gfx/interface/goals/shine_overlay.dds" animationrotation = -90 animationlooping = no animationtime = 0.75 animationdelay = 0 animationblendmode = "add" animationtype = "scrolling" animationrotationoffset = {{ x = 0 y = 0 }} animationtexturescale = {{ x = 1 y = 1 }} }} }}\n'''
for i,(key,file) in enumerate(files.items()):
 shutil.copy2(SRC/file,out/(key+'.png'));im=Image.open(out/(key+'.png')).convert('RGBA');assert im.getextrema()[3][0]==0
 im=im.crop(im.getbbox())
 for folder,size,prefix in [('goals',(95,85),'focus'),('ideas',(60,68),'idea')]:
  thumb=ImageOps.contain(im,(size[0]-4,size[1]-4),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',size);canvas.alpha_composite(thumb,((size[0]-thumb.width)//2,(size[1]-thumb.height)//2))
  path=f'gfx/interface/{folder}/{prefix}_story_{key}.dds';canvas.save(ROOT/path)
  sprite(f'GFX_{"goal" if folder=="goals" else "idea"}_story_{key}',path,folder=='goals')
  if folder=='goals':
   x=(i%4)*200+52;y=(i//4)*150+35;preview.paste(canvas,(x,y),canvas);draw.text((x-15,y-23),key,fill='white')
for key,asset in json.loads((ROOT/'tools/ludolf_icon_mapping.json').read_text()).items():
 path=f'gfx/interface/goals/{asset}.dds';assert (ROOT/path).exists() or (Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')/path).exists(),path;sprite('GFX_goal_A01_subject_'+key,path,True)
(ROOT/'interface/A01_story_icons.gfx').write_text(gfx+'}\n',encoding='utf-8');preview.save(out/'preview.png')
# Stylised heraldic flags for the three new autonomous administrations.
for tag,col in [('A11',(37,108,61)),('A12',(172,132,32)),('A13',(35,74,115))]:
 flag=Image.new('RGB',(82,52),col);d=ImageDraw.Draw(flag);d.rectangle((0,0,81,7),fill=(228,194,97));d.rectangle((0,44,81,51),fill=(228,194,97));d.ellipse((30,13,52,36),fill=(239,219,152));d.ellipse((36,10,55,33),fill=col)
 for folder,size in [('',(82,52)),('medium',(41,26)),('small',(10,7))]:
  p=ROOT/'gfx/flags'/folder/(tag+'.tga');p.parent.mkdir(parents=True,exist_ok=True);flag.resize(size,Image.Resampling.LANCZOS).save(p)
prompts={'tool':'built-in image_gen','style':'Single HOI4 focus emblem, hand-painted antique metal and enamel, unique subject silhouette, readable 95x85, transparent background, no words.','subjects':{'constitution':'parchment, red seal, bronze quill','trade':'oil barrels, raw rubber, merchant scales','wolf':'lone silver wolf and maritime compass','ludolf':'civilian signet, pen, orange sash','admirals':'bicorne hats, anchor, baton','sultans':'Malay royal headdress, crescent, treaty scrolls','defeat':'cracked anchor, lowered Dutch ribbon, armistice document','revanchism':'gloved sabre, orange ribbon, broken chain'}}
(out/'prompts.json').write_text(json.dumps(prompts,ensure_ascii=False,indent=2),encoding='utf-8')
print('8 unique story emblems, 16 DDS exports, shine sprites, thematic vanilla assets and 3 sultanate flags built.')
