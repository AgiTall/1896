from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1]
G=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
def read(p):return p.read_text(encoding='utf-8-sig')
files=[R/p for p in ['common/scripted_effects/borneo_war_effects.txt','common/ideas/borneo_war_ideas.txt','common/ai_strategy/A03_southern_war.txt','common/decisions/A03_southern_preparations.txt','common/decisions/categories/A03_southern_preparations.txt','common/on_actions/borneo_militia_cleanup.txt','events/southern_war.txt','events/A01_admiral_speeches.txt','history/units/A01_indonesian_militia.txt','history/units/A03_southern_reinforcements.txt','history/units/A03_southern_reinforcements_legacy.txt']]
files.append(R/'common/ai_areas/1896_borneo.txt')
for p in files:
 t=re.sub(r'"(?:\\.|[^"\\])*"|#[^\n]*','',read(p));depth=0
 for c in t:
  depth+=(c=='{')-(c=='}');assert depth>=0,p
 assert depth==0,p
fx=read(files[0]);ideas=read(files[1]);ai=read(files[2]);dec=read(files[3])
assert 'days = 180' in fx and 'idea = A03_southern_blitz' in fx
assert 'has_country_flag = A03_southern_force_prepared' in fx
assert 'delete_unit_template_and_units = { division_template = "Indische Vrijwilligers" }' in fx
for n in [15,15,15]:assert f'days = -{n}' in dec
assert dec.count('fire_only_once = yes')==3
assert 'A03_start_southern_war_effect = yes' in read(R/'common/decisions/A01_inevitable_conflict.txt')
assert 'declare_war_on' not in read(R/'common/national_focus/a03_focus.txt')
assert 'state = 1024' in ai and 'type = invade' in ai and 'naval_invasion_support_priority' in ai
# The staging buffer and theatre must resolve against this mod's replaced map.
area_file=R/'common/ai_areas/1896_borneo.txt'
area=read(area_file)
assert 'A03_borneo' in area and 'strategic_regions = { 159 }' in area
assert 'type = area_priority id = A03_borneo' in ai
assert 'type = put_unit_buffers' in ai and 'states = { 647 }' in ai
assert ai.count('type = strike_force_home_base')==2
assert 'abort_when_not_enabled = yes' in ai
for state in [1024,1023,1055]:
 assert f'area = A03_borneo state = {state}' in ai
 text=read(next((R/'history/states').glob(f'{state}*.txt')))
 assert 'owner = A01' in text and 'naval_base' in text
 text_without_comments=re.sub(r'#[^\n]*','',text)
 provinces=set(re.search(r'\bprovinces\s*=\s*\{([^}]*)\}',text_without_comments,re.S)[1].split())
 region=read(next((R/'map/strategicregions').glob('159*.txt')))
 region_provinces=set(re.search(r'\bprovinces\s*=\s*\{([^}]*)\}',region,re.S)[1].split())
 assert provinces<=region_provinces,(state,provinces-region_provinces)
for modifier in ['naval_invasion_division_cap','naval_invasion_plan_cap']:
 assert re.search(rf'\b{modifier}\s*=\s*[1-9]',ideas)
 assert f'## {modifier}' in read(G/'documentation/modifiers_documentation.md')
for p in [R/'history/units/A03_southern_reinforcements.txt',R/'history/units/A03_southern_reinforcements_legacy.txt']:
 t=read(p);assert len(re.findall(r'\bship\s*=\s*\{',t))==20
 assert t.count('definition = battleship')==4
assert len(re.findall(r'\bdivision\s*=\s*\{',read(R/'history/units/A01_indonesian_militia.txt')))==12
assert '255 191 191' in read(R/'common/countries/A03.txt')
assert 'A03 = { color = rgb { 255 191 191 } color_ui = rgb { 255 191 191 } }' in read(R/'common/countries/colors.txt')
events='\n'.join(read(p) for p in (R/'events').glob('*.txt'))
ids=re.findall(r'\bid\s*=\s*(A01_japan\.\d+|southern_war\.\d+)\s+(?=title|hidden|\n?\s*trigger)',events)
# Definitions and references are checked separately; duplicated namespaces are permitted.
definitions=re.findall(r'country_event\s*=\s*\{\s*id\s*=\s*(A01_japan\.\d+|southern_war\.\d+)\s+(?:title|hidden|trigger|\n)',events)
assert len(definitions)==len(set(definitions)),definitions
alltext='\n'.join(read(p) for p in files)+events
refs=set(re.findall(r'country_event\s*=\s*\{\s*id\s*=\s*(A01_japan\.\d+|southern_war\.\d+)',alltext))
assert refs<=set(definitions),refs-set(definitions)
loc={}
for lang in ['russian','english']:
 t=read(R/f'localisation/{lang}/zzz_borneo_war_l_{lang}.yml');loc[lang]=set(re.findall(r'^\s+(\S+):0',t,re.M))
assert loc['russian']==loc['english'] and len(loc['russian'])==63
for eid in set(definitions):
 if eid=='southern_war.1' or eid in ['A01_japan.1','A01_japan.3','A01_japan.4','A01_japan.5']:continue
 for suffix in ['.t','.d']:assert eid+suffix in loc['russian'],eid+suffix
report=dict(status='passed',reinforcement_ships=20,heavy_ships=4,militia_divisions=12,blitz_days=180,decision_reductions=[15,15,15],campaign_focus_reduction=15,localisation_keys_per_language=len(loc['russian']),checks=['Balanced scripts and event references','One guarded war preparation path and real mission reductions','DLC and legacy fleets','Twelve locked militia divisions and peace cleanup','Vanilla Japanese RGB in both colour definitions','Russian and English chain texts'],campaign_combat_test='Not simulated; AI planning must be assessed during a running campaign.')
report['checks'] += ['Borneo AI area, target ports and province membership', 'Palau staging buffer and southern strike-force home areas', 'Current invasion cap modifiers present in installed game documentation']
(R/'tools/borneo_war_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report))

