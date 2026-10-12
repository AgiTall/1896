from pathlib import Path
from PIL import Image,ImageOps
import json
R=Path(__file__).resolve().parents[1]
mapping={'A03_southern_blitz':('borneo_blitz','A03_southern_campaign'),'A01_coerced_service':('borneo_coerced_service','A01_admirals_council_coup'),'A01_service_compromise':('borneo_service_compromise','A01_equal_service'),'A01_indonesian_volunteers':('borneo_volunteers','A01_island_garrisons')}
gfx=['spriteTypes = {'];p=R/'common/ideas/borneo_war_ideas.txt';t=p.read_text()
for idea,(key,source) in mapping.items():
 im=Image.open(R/f'gfx/interface/focus_unique_sources/{source}.png').convert('RGBA');im=ImageOps.contain(im.crop(im.getbbox()),(56,64),Image.Resampling.LANCZOS)
 canvas=Image.new('RGBA',(60,68));canvas.alpha_composite(im,((60-im.width)//2,(68-im.height)//2));assert canvas.getextrema()[3][0]==0
 path=f'gfx/interface/ideas/idea_{key}.dds';canvas.save(R/path)
 gfx.append(f'spriteType = {{ name = "GFX_idea_{key}" texturefile = "{path}" legacy_lazy_load = no }}')
 import re
 t,n=re.subn(r'('+idea+r'\s*=\s*\{\s*picture\s*=\s*)\w+',lambda m:m[1]+key,t);assert n==1,idea
p.write_text(t,encoding='utf-8');(R/'interface/borneo_war_icons.gfx').write_text('\n'.join(gfx)+'\n}\n',encoding='utf-8')
(R/'gfx/interface/focus_unique_sources/borneo_idea_mapping.json').write_text(json.dumps(mapping,indent=2),encoding='utf-8')
print('4 matching national-spirit icons exported from existing generated focus art, 60x68 transparent DDS.')
