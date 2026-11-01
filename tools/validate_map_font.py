"""Check the map font and render sample labels from its actual bitmap atlas."""
from pathlib import Path
import re,struct
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
directory=R/'gfx/fonts'
text=(directory/'hoi_mapfont4.fnt').read_text(encoding='utf-8')
assert 'face="Miranda script"' in text
glyphs={};kernings={}
for line in text.splitlines():
    values={k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',line)}
    if line.startswith('char id='):glyphs[values['id']]=values
    elif line.startswith('kerning first='):kernings[values['first'],values['second']]=values['amount']
with Image.open(directory/'hoi_mapfont4.dds') as img:atlas=img.convert('RGBA')
assert atlas.size==(2048,1024)
header=struct.unpack('<31I',(directory/'hoi_mapfont4.dds').read_bytes()[4:128]);assert header[6]==4
for g in glyphs.values():
    assert g['x']>=0 and g['y']>=0
    assert g['x']+g['width']<=atlas.width and g['y']+g['height']<=atlas.height
source=ImageFont.truetype(directory/'mirandascript.ttf',78)
assert source.getname()[0]=='Miranda script'
missing=source.getmask(chr(0x10ffff));missing=(missing.size,bytes(missing))
for code in list(range(1040,1104))+[1025,1105]:
    mask=source.getmask(chr(code));assert (mask.size,bytes(mask))!=missing
    assert code in glyphs
samples=['ЯПОНИЯ','БРИТАНСКИЙ ЛЕВИАФАН','МАЛЬТА','НОВЫЙ ЮЖНЫЙ УЭЛЬС','ЗАПАДНАЯ АВСТРАЛИЯ','New South Wales']
canvas=Image.new('RGBA',(1500,850),(218,199,153,255));draw=ImageDraw.Draw(canvas)
draw.text((40,20),'Miranda Script — country labels / atlas preview',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25),fill=(65,48,25))
for row,sample in enumerate(samples):
    x=40;y=75+row*120;previous=None
    for char in sample:
        code=ord(char);g=glyphs[code]
        if previous is not None:x+=kernings.get((previous,code),0)
        tile=atlas.crop((g['x'],g['y'],g['x']+g['width'],g['y']+g['height']))
        assert x+g['xoffset']+g['width']<canvas.width,sample
        canvas.alpha_composite(tile,(x+g['xoffset'],y+g['yoffset']))
        x+=g['xadvance'];previous=code
out=R/'tools/miranda_map_font_preview.png';canvas.convert('RGB').save(out)
print(f'PASS: {len(glyphs)} glyphs, full Russian alphabet, atlas bounds, 4 mipmaps, {len(kernings)} kernings')
print(out)
