from pathlib import Path
from PIL import Image,ImageOps
import json,shutil
R=Path(__file__).resolve().parents[1]
S=R/'gfx/interface/focus_unique_sources'
src=Path('C:/Users/AgiTall/.codex/generated_images/01a12514-d2e9-7811-b9a8-8f599dd9e8fe')
files={'bop_ludolf':'exec-659b429d-1f49-4357-9a1d-199128729e7e.png','bop_admirals':'exec-e564f422-8c13-4c94-bf52-44f12ce77c9d.png'}
p=R/'common/bop/A01_ludolf.txt';backup=R/'tools/backups/focus_art_before/common/bop/A01_ludolf.txt'
if not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
t=p.read_text(encoding='utf-8-sig');gfx=['spriteTypes = {']
for key,file in files.items():
 shutil.copy2(src/file,S/(key+'.png'));im=Image.open(S/(key+'.png')).convert('RGBA');assert im.getextrema()[3][0]==0
 im=ImageOps.contain(im.crop(im.getbbox()),(68,84),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',(72,88));canvas.alpha_composite(im,((72-im.width)//2,(88-im.height)//2))
 path=f'gfx/interface/bop/{key}_steel.dds';(R/path).parent.mkdir(parents=True,exist_ok=True);canvas.save(R/path)
 gfx.append(f'spriteType = {{ name = "GFX_{key}_steel" texturefile = "{path}" legacy_lazy_load = no }}')
 t=t.replace('GFX_idea_story_'+key.replace('bop_',''),'GFX_'+key+'_steel')
p.write_text(t,encoding='utf-8');(R/'interface/unique_focus_icons.gfx').write_text('\n'.join(gfx)+'\n}\n',encoding='utf-8')
print('Steel bust and tricorn anchor installed at native 72x88.')
