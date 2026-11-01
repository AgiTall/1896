"""Pack generated ink into the water-only sampler and install a matte water shader."""
from pathlib import Path
import sys,shutil,struct,json,hashlib,re
from PIL import Image,ImageOps,ImageChops,ImageFilter
R=Path(__file__).resolve().parents[1]
B=R/'tools/backups/water_before_chinese_paper'
OUT=R/'tools/water_style'
def backup(relative):
    src=R/relative;dest=B/relative;dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():shutil.copy2(src,dest)
    return dest
def dds_mips(image,path):
    levels=[];im=image.convert('RGBA')
    while True:
        levels.append(im)
        if im.size==(1,1):break
        im=im.resize((max(1,im.width//2),max(1,im.height//2)),Image.Resampling.LANCZOS)
    header=[124,0x2100f,image.height,image.width,image.width*4,0,len(levels)]+[0]*11
    header += [32,0x41,0,32,0xff,0xff00,0xff0000,0xff000000,0x401008,0,0,0,0]
    assert len(header)==31
    path.write_bytes(b'DDS '+struct.pack('<31I',*header)+b''.join(im.tobytes() for im in levels))
    return len(levels)
MAIN='''
		float4 main( VS_OUTPUT_WATER Input ) : PDX_COLOR
		{
			// Chinese chart water: fixed ink on paper, not moving reflective water.
			float waterHeight = MultiSampleTexX( HeightTexture, Input.uv ) / ( 95.7f / 255.0f );
			float waterShore = saturate( ( waterHeight - 0.954f ) * 25.0f );
			float3 normal = float3( 0.0f, 1.0f, 0.0f );
			// Flat aged-paper ground. Never sample the screen-space seabed:
			// that texture carries depth shading, dents and a cold colour cast.
			float3 paperColor = float3( 0.36f, 0.33f, 0.25f );
			// Existing engine-bound water-only slot 6. RGB retains the old ice normals;
			// alpha stores our ink. No new engine texture binding is required.
			float tileSize = MAP_SIZE_X / 8.0f;
			float2 paperUV = float2( Input.pos.x, -Input.pos.z ) / tileSize;
			float ink = 1.0f - tex2D( IceDiffuse, paperUV ).a;
			float distanceFade = lerp( 1.0f, 0.20f, cam_distance( 600.0f, 1900.0f ) );
			paperColor *= 1.0f - ink * 0.28f * distanceFade;
			// Preserve visibility and night darkening as brightness only, so fog
			// cannot turn the parchment blue or purple. Apply overlays afterwards.
			float paperLuma = max( dot( paperColor, float3( 0.299f, 0.587f, 0.114f ) ), 0.001f );
			float3 fogColor = ApplyFOW( paperColor, ShadowMap, Input.vScreenCoord );
			float3 nightColor = DayNightWithBlend( fogColor, CalcGlobeNormal( Input.pos.xz ), 1.0f );
			float visibility = clamp( dot( nightColor, float3( 0.299f, 0.587f, 0.114f ) ) / paperLuma, 0.62f, 1.0f );
			float3 vOut = paperColor * visibility;
			float vBloomAlpha = 0.0f;
			gradient_border_apply( vOut, normal, Input.uv,
				GradientBorderChannel1, GradientBorderChannel2, 0.0f,
				vGBCamDistOverride_GBOutlineCutoff.zw * GB_OUTLINE_CUTOFF_SEA,
				vGBCamDistOverride_GBOutlineCutoff.xy, vBloomAlpha );
			secondary_color_mask( vOut, normal, Input.uv, ProvinceSecondaryColorMap, vBloomAlpha );
			return float4( vOut, 1.0f - waterShore );
		}
'''
def main():
    source=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True)
    art=R/'gfx/map/chinese_paper_water';art.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,art/'generated_waves.png')
    original_texture=backup('map/terrain/ice_diffuse.dds')
    original_shader=backup('gfx/FX/pdxwater.shader')
    # Isolate the printed strokes from the generated paper ground. Mirror the
    # repeat in both axes to guarantee matching edge values without a hard seam.
    gray=ImageOps.grayscale(Image.open(source)).resize((512,512),Image.Resampling.LANCZOS)
    local=gray.filter(ImageFilter.GaussianBlur(8))
    ink=ImageChops.subtract(local,gray).point(lambda v:max(0,min(255,(v-3)*5)))
    repeat=Image.new('L',(1024,1024));repeat.paste(ink,(0,0));repeat.paste(ImageOps.mirror(ink),(512,0))
    repeat.paste(ImageOps.flip(ink),(0,512));repeat.paste(ImageOps.flip(ImageOps.mirror(ink)),(512,512))
    alpha=ImageOps.invert(repeat.resize((512,512),Image.Resampling.LANCZOS))
    with Image.open(original_texture) as original:packed=original.convert('RGBA')
    assert packed.size==(512,512)
    packed.putalpha(alpha)
    mip_count=dds_mips(packed,R/'map/terrain/ice_diffuse.dds')
    alpha.save(art/'wave_mask.png')
    shader=original_shader.read_text(encoding='utf-8-sig')
    marker='float4 main( VS_OUTPUT_WATER Input ) : PDX_COLOR'
    start=shader.index(marker);end=shader.index('\n\t]]',start)
    shader=shader[:start]+MAIN.strip('\n\t')+shader[end:]
    (R/'gfx/FX/pdxwater.shader').write_text(shader,encoding='utf-8')
    # Local material preview, not a screenshot of the game.
    paper=Image.new('RGB',(1024,1024),(179,172,148))
    fullalpha=alpha.resize(paper.size,Image.Resampling.LANCZOS)
    strength=ImageOps.invert(fullalpha).point(lambda v:round(v*0.28))
    preview=Image.composite(Image.new('RGB',paper.size,(0,0,0)),paper,strength)
    preview.save(OUT/'paper_water_material_preview.png')
    manifest={'generated_source':str(source),'asset':'gfx/map/chinese_paper_water/generated_waves.png','texture':'map/terrain/ice_diffuse.dds','sampler':'IceDiffuse, index 6, alpha only','shader':'gfx/FX/pdxwater.shader','mip_levels':mip_count,'tile_period_world_units':704,'ink_strength':0.28,'backup':str(B),'engine_tested':False}
    (OUT/'chinese_water_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
