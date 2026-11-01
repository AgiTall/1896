"""Validate packed DDS, mipmaps, repeats and preserved game overlay hooks."""
from pathlib import Path
import struct,json
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[1]
B=R/'tools/backups/water_before_chinese_paper'
p=R/'map/terrain/ice_diffuse.dds';raw=p.read_bytes()
header=struct.unpack('<31I',raw[4:128]);assert raw[:4]==b'DDS '
assert header[0]==124 and header[6]==10
size=512;expected=128
for _ in range(10):expected+=size*size*4;size=max(1,size//2)
assert len(raw)==expected
with Image.open(p) as current,Image.open(B/'map/terrain/ice_diffuse.dds') as original:
    assert current.size==original.size==(512,512)
    assert ImageChops.difference(current.convert('RGB'),original.convert('RGB')).getbbox() is None
    alpha=current.getchannel('A');assert alpha.getextrema()[0]<150 and alpha.getextrema()[1]==255
    # Edge continuity must survive downsampling of the mirrored periodic tile.
    for a,b in [(alpha.crop((0,0,1,512)),alpha.crop((511,0,512,512))), (alpha.crop((0,0,512,1)),alpha.crop((0,511,512,512)))]:
        assert ImageChops.difference(a,b).getextrema()[1]<=5
shader=(R/'gfx/FX/pdxwater.shader').read_text(encoding='utf-8-sig')
assert shader.count('{')==shader.count('}')
assert shader.count('[[')==shader.count(']]')
main=shader.split('float4 main( VS_OUTPUT_WATER Input ) : PDX_COLOR')[1].split(']]')[0]
assert 'vTime_HalfPixelOffset.x' not in main
assert 'SampleWater(' not in main and 'texCUBE(' not in main
assert 'tex2D( WaterRefraction' not in main
assert 'float3( 0.36f, 0.33f, 0.25f )' in main
assert main.index('DayNightWithBlend(')<main.index('gradient_border_apply(')
for text in ('gradient_border_apply(','secondary_color_mask(','ApplyFOW(','DayNightWithBlend(','1.0f - waterShore','cam_distance( 600.0f, 1900.0f )'):
    assert text in main,text
for effect in ('water_low_gfx','water_no_refractions','water'):assert 'Effect '+effect in shader
assert 'tex2D( IceDiffuse, paperUV ).a' in main
print('PASS: DDS 512x512, 10 mip levels, original RGB, seamless edges, fixed waves and overlay hooks')
