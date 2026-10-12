from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import json,shutil,re
ROOT=Path(__file__).resolve().parents[1]
BACK=ROOT/'tools/backups/ludolf_before'
SOURCE=Path('C:/Users/AgiTall/.codex/generated_images/01a12514-d2e9-7811-b9a8-8f599dd9e8fe')
def original(path):return ((BACK/path) if (BACK/path).exists() else ROOT/path).read_text(encoding='utf-8-sig')
def write(path,text,bom=False):
 p=ROOT/path
 if p.exists() and not (BACK/path).exists():
  (BACK/path).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,BACK/path)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8-sig' if bom else 'utf-8')
art={'meiji':'exec-158aada6-bf21-4d3b-a5d9-c2b4a0a58138.png','casembroot':'exec-c125cd8e-46a0-4491-9204-5985c817597a.png','fabius':'exec-c5e26780-0845-4284-8e82-f97f6065213b.png'}
gfx='spriteTypes = {\n';preview=Image.new('RGB',(510,250),(35,40,40));draw=ImageDraw.Draw(preview)
for i,(key,file) in enumerate(art.items()):
 dest=ROOT/'gfx/leaders/period_sources'/(key+'_painted.png');shutil.copy2(SOURCE/file,dest)
 im=Image.open(dest).convert('RGBA');thumb=ImageOps.fit(im,(156,210),Image.Resampling.LANCZOS)
 path=f'gfx/leaders/{"A03" if key=="meiji" else "A01"}/Portrait_{key}.dds';(ROOT/path).parent.mkdir(parents=True,exist_ok=True);thumb.save(ROOT/path)
 gfx+=f'spriteType = {{ name = "GFX_portrait_period_{key}" texturefile = "{path}" }}\n'
 small=ImageOps.fit(im,(65,67),Image.Resampling.LANCZOS,centering=(0.5,0.25));path=f'gfx/interface/ideas/Portrait_{key}_small.dds';small.save(ROOT/path)
 gfx+=f'spriteType = {{ name = "GFX_portrait_period_{key}_small" texturefile = "{path}" }}\n'
 preview.paste(thumb,(i*170+7,30));draw.text((i*170+10,8),key,fill='white')
write('interface/period_characters.gfx',gfx+'}\n');preview.save(ROOT/'gfx/leaders/period_sources/preview.png')

path='common/characters/A03.txt';t=original(path)
t=re.sub(r'A03_imperial_council = \{.*?\n', '''A03_emperor_meiji = {
 name = A03_emperor_meiji_name
 portraits = { civilian = { large = GFX_portrait_period_meiji small = GFX_portrait_period_meiji_small } }
 country_leader = { ideology = despotism expire = "1912.7.30.1" traits = { A03_imperial_authority } }
 }
''',t,count=1)
write(path,t)
path='history/countries/A03 - Placeholder.txt';write(path,original(path).replace('recruit_character = A03_imperial_council','recruit_character = A03_emperor_meiji'))
write('common/country_leader/A03_meiji.txt','leader_traits = { A03_imperial_authority = { random = no stability_factor = 0.05 } }\n')

chars='characters = {\n'
for key,name,skill,attack,defence,maneuver,coord,traits in [('fabius','A01_gerhardus_fabius_name',4,3,4,2,4,'old_guard navy_career_officer'),('casembroot','A01_francois_de_casembroot_name',3,4,2,3,3,'bold superior_tactician')]:
 chars+=f'''A01_{key} = {{
 name = {name}
 portraits = {{ army = {{ large = GFX_portrait_period_{key} small = GFX_portrait_period_{key}_small }} navy = {{ large = GFX_portrait_period_{key} small = GFX_portrait_period_{key}_small }} }}
 navy_leader = {{ skill = {skill} attack_skill = {attack} defense_skill = {defence} maneuvering_skill = {maneuver} coordination_skill = {coord} traits = {{ {traits} }} }}
}}
'''
write('common/characters/A01_admirals.txt',chars+'}\n')
path='history/countries/A01 - Placeholder.txt';t=original(path)
t+='\nrecruit_character = A01_fabius\nrecruit_character = A01_casembroot\n';write(path,t)
texts={
'A03_emperor_meiji_name':('Мэйдзи','Emperor Meiji'),
'A03_imperial_authority':('Императорский авторитет','Imperial Authority'),
'A03_imperial_authority_desc':('Императорская власть объединяет кабинет и военное командование.','Imperial authority unites the cabinet and military command.'),
'A01_gerhardus_fabius_name':('Герардус Фабиус','Gerhardus Fabius'),
'A01_francois_de_casembroot_name':('Франсуа де Каземброт','François de Casembroot')}
for lang,i in [('russian',0),('english',1)]:write(f'localisation/{lang}/period_characters_l_{lang}.yml','l_'+lang+':\n'+''.join(f' {k}:0 {json.dumps(v[i],ensure_ascii=False)}\n' for k,v in texts.items()),True)
print('Meiji is the Japanese leader; Fabius and de Casembroot are recruited A01 admirals, with painted historical portraits.')
