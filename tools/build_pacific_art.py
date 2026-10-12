from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import shutil, json
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('C:/Users/AgiTall/.codex/generated_images/01a12514-d2e9-7811-b9a8-8f599dd9e8fe')
files={'batavia':'exec-5869f30d-2b0c-4f3c-b160-33a403e41667.png','japan':'exec-0cd63d91-55cf-4e69-b30b-17654fa78f1d.png','industry':'exec-e2cbe299-b090-41b4-bf87-0270411b2746.png','army':'exec-d65fd567-19d9-4898-88a9-53c02c53deb1.png'}
gfx='spriteTypes = {\n'
preview=Image.new('RGB',(640,220),(37,42,40)); draw=ImageDraw.Draw(preview)
for i,(key,file) in enumerate(files.items()):
    dest=ROOT/'gfx/interface/pacific_sources'/f'{key}.png';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SOURCE/file,dest)
    im=Image.open(dest).convert('RGBA'); assert im.getextrema()[3][0]==0,'Expected transparent background'
    im=im.crop(im.getbbox())
    for folder,size,prefix in [('goals',(95,85),'focus'),('ideas',(60,68),'idea')]:
        thumb=ImageOps.contain(im,(size[0]-6,size[1]-6),Image.Resampling.LANCZOS)
        canvas=Image.new('RGBA',size);canvas.alpha_composite(thumb,((size[0]-thumb.width)//2,(size[1]-thumb.height)//2))
        path=ROOT/f'gfx/interface/{folder}/{prefix}_pacific_{key}.dds';canvas.save(path)
        name=f'GFX_{"goal" if folder=="goals" else "idea"}_pacific_{key}'
        gfx+=f'spriteType = {{ name = "{name}" texturefile = "gfx/interface/{folder}/{path.name}" }}\n'
        if folder=='goals':
            gfx+=f'''spriteType = {{ name = "{name}_shine" texturefile = "gfx/interface/{folder}/{path.name}" effectFile = "gfx/FX/buttonstate.lua"
 animation = {{ animationmaskfile = "gfx/interface/{folder}/{path.name}" animationtexturefile = "gfx/interface/goals/shine_overlay.dds" animationrotation = -90 animationlooping = no animationtime = 0.75 animationdelay = 0 animationblendmode = "add" animationtype = "scrolling" animationrotationoffset = {{ x = 0 y = 0 }} animationtexturescale = {{ x = 1 y = 1 }} }}
 legacy_lazy_load = no }}\n'''
            preview.paste(canvas,(i*160+32,40),canvas)
        else: preview.paste(canvas,(i*160+50,135),canvas)
    draw.text((i*160+36,15),key,fill='white')
(ROOT/'interface/pacific_icons.gfx').write_text(gfx+'}\n',encoding='utf-8')
preview.save(ROOT/'gfx/interface/pacific_sources/icon_preview.png')
(ROOT/'gfx/interface/pacific_sources/prompts.json').write_text(json.dumps({'tool':'built-in image_gen','style':'Single standalone HOI4 national focus / national spirit emblem, hand-painted worn bronze and steel relief, readable small silhouette, transparent background, no text.','subjects':{'batavia':'Dutch East Indies bronze anchor, teal shield and rubber leaves','japan':'gold chrysanthemum, steel cog, crimson enamel and anchors','industry':'steel cog, bronze steam locomotive wheel and laurel','army':'coastal fortress, crossed period rifles and bronze shield'}},indent=2),encoding='utf-8')
print('4 generated originals, 8 DDS icons and focus shine definitions written.')
