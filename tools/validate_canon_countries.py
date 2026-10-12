"""Validate the country foundation against actual states, units and assets."""
from pathlib import Path
import json
import re
from PIL import Image
from add_canon_countries import parse, value
from validate_canon_map_buildings import validate as validate_map_buildings

validate_map_buildings()

R=Path(__file__).resolve().parents[1]
G=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
m=json.loads((R/'tools/canon_countries_manifest.json').read_text(encoding='utf-8'))
errors=[]
def check(condition,message):
    if not condition: errors.append(message)

states={}; province_owner={}; province_state={}
for p in (R/'history/states').glob('*.txt'):
    try:
        body=value(parse(p.read_text(encoding='utf-8-sig')),'state')
        sid=int(value(body,'id')); hist=value(body,'history'); owner=value(hist,'owner')
        check(sid not in states,f'Duplicate state {sid}')
        states[sid]=(owner,body)
        for province,op,v in value(body,'provinces'):
            province=int(province)
            check(province not in province_state,f'Province {province} appears in two states')
            province_state[province]=sid;province_owner[province]=owner
    except (ValueError,StopIteration,AssertionError) as e: errors.append(f'{p.name}: {e}')

mod_tags={}
for p in (R/'common/country_tags').glob('*.txt'):
    for tag,op,file in parse(p.read_text(encoding='utf-8-sig')):
        check(tag not in mod_tags,f'Duplicate mod tag {tag}')
        mod_tags[tag]=file.strip('"')

loc={}
for lang in ['russian','english']:
    p=R/f'localisation/{lang}/zzzzz_canon_countries_l_{lang}.yml'
    check(p.read_bytes().startswith(b'\xef\xbb\xbf'),f'No BOM: {p.name}')
    loc[lang]=set(re.findall(r'^\s+(\S+):',p.read_text(encoding='utf-8-sig'),re.M))

for country in m['countries']:
    tag=country['tag'];capital=country['capital']
    check(tag in mod_tags,f'Missing tag: {tag}')
    check((R/'common'/mod_tags[tag]).exists(),f'Missing definition: {tag}')
    paths=list((R/'history/countries').glob(f'{tag} - *.txt'))
    check(len(paths)==1,f'Expected one history: {tag}')
    if not paths: continue
    tree=parse(paths[0].read_text(encoding='utf-8-sig'))
    character=value(tree,'recruit_character')
    char_path=R/f'common/characters/{tag}_canon.txt'
    characters=value(parse(char_path.read_text(encoding='utf-8-sig')),'characters')
    check(any(k==character for k,op,v in characters),f'Undefined character: {tag}')
    for portrait in re.findall(r'large\s*=\s*"([^"]+)"',char_path.read_text()):
        check((G/portrait).exists() or (R/portrait).exists(),f'Missing portrait {portrait}')
    for lang in loc:
        for suffix in ['', '_DEF','_ADJ','_neutrality','_neutrality_DEF','_neutrality_ADJ']:
            check(tag+suffix in loc[lang],f'Missing label {lang}: {tag+suffix}')
        check(character+'_name' in loc[lang],f'Missing leader name {tag}')
    for folder,size in [('',(82,52)),('medium',(41,26)),('small',(10,7))]:
        p=R/'gfx/flags'/folder/(tag+'.tga')
        check(p.exists() and Image.open(p).size==size,f'Flag size: {tag}/{folder}')
        check(Image.open(p).mode=='RGBA',f'Expected 32-bit flag: {tag}/{folder}')
    if country['active']:
        check(capital in states and states[capital][0]==tag,f'Capital not owned: {tag}/{capital}')
        oob=value(tree,'oob').strip('"')
        units=(R/f'history/units/{oob}.txt').read_text()
        for province in re.findall(r'location\s*=\s*(\d+)',units):
            check(province_owner.get(int(province))==tag,f'Unit outside home territory: {tag}/{province}')

# The migration must not lose or duplicate provinces or population in a split.
for split in m['state_splits']:
    source=split['source']; new=split['new_state']
    old=list((R/'tools/backups/canon_countries_1893/history/states').glob(f'{source}*.txt'))[0]
    oldbody=value(parse(old.read_text(encoding='utf-8-sig')),'state')
    orig={int(k) for k,op,v in value(oldbody,'provinces')}
    now={int(k) for sid in [source,new] for k,op,v in value(states[sid][1],'provinces')}
    # Cuba was split twice, so both new regions must be included in the comparison.
    if source==315:
        now={int(k) for sid in [315,1082,1083] for k,op,v in value(states[sid][1],'provinces')}
        total=sum(int(value(states[sid][1],'manpower')) for sid in [315,1082,1083])
    else: total=sum(int(value(states[sid][1],'manpower')) for sid in [source,new])
    check(orig==now,f'Province conservation failed: {source}')
    check(total==int(value(oldbody,'manpower')),f'Population conservation failed: {source}')

opinion_text=(R/'common/opinion_modifiers/pz_canon_1893.txt').read_text()
modifiers={k for k,op,v in value(parse(opinion_text),'opinion_modifiers')}
relations=(R/'common/scripted_effects/pz_canon_relations.txt').read_text()
parse(relations)
for target in re.findall(r'country_exists\s*=\s*(\w+)',relations):check(target in mod_tags,f'Unknown relation participant {target}')
for modifier in re.findall(r'modifier\s*=\s*(\w+)',relations):check(modifier in modifiers,f'Undefined opinion modifier {modifier}')
check('has_global_flag = PZ_canon_relations_initialized' in relations,'Relations lack repeat protection')
check(relations.count('declare_war_on')==6,'Six Caribbean starting conflicts expected')
for target in re.findall(r'declare_war_on\s*=\s*\{\s*target\s*=\s*(\w+)',relations):
    check(target in mod_tags and any(owner==target for owner,body in states.values()),f'War target has no territory: {target}')
# Province-level ports must belong to their state and be coastal.
definitions={int(a[0]):a for a in [line.split(';') for line in (R/'map/definition.csv').read_text().splitlines()]}
for split in m['state_splits']:
    sid=split['new_state'];hist=value(states[sid][1],'history')
    for province,op,body in value(hist,'buildings'):
        if province.isdigit():
            check(province_state.get(int(province))==sid,f'New building outside state: {sid}/{province}')
            if any(k=='naval_base' for k,op,v in body):
                check(definitions[int(province)][5]=='true',f'Inland port: {sid}/{province}')
for p in [R/'common/characters/pz_canon_councils.txt',R/'common/ideas/pz_canon_governments.txt',R/'common/bookmarks/the_gathering_storm.txt']:
    parse(p.read_text(encoding='utf-8-sig'))
for lang in ['russian','english']:
    loc_text=(R/f'localisation/{lang}/zzzzz_canon_countries_l_{lang}.yml').read_text(encoding='utf-8-sig')
    all_labels=set(re.findall(r'^\s+(\S+):',loc_text,re.M))
    for key in ['A02_fisher_name','A06_pobedonostsev_name','PAZ_prophet_name']:
        check(key in all_labels,f'Missing secondary leader label: {lang}/{key}')
check(states[282][0]=='A03' and states[531][0]=='A09' and states[536][0]=='A08','Japanese split incorrect')
check(states[116][0]=='A02' and states[100][0]=='A06','Exile capitals incorrect')
check(all(states[sid][0]=='A03' for sid in [282,528,529,530,532,533,534,535,1019,1020]),'Japanese home islands contain an unintended wasteland')
check(all(states[sid][0]=='A02' for sid in [284,723,1081]),'New Zealand is not fully British')
check(states[327][0]=='A03' and states[623][0]=='PLS','Philippine occupation incorrect')

# Existing Japanese formations must survive Osaka changing hands.
for p in (R/'history/units').glob('A03*.txt'):
    if 'legacy' in p.name or 'reinforcements' in p.name: pass
    for province in re.findall(r'(?:location|naval_base)\s*=\s*(\d+)',p.read_text(encoding='utf-8-sig')):
        check(province_owner.get(int(province))=='A03',f'Japanese OOB in foreign province: {p.name}/{province}')

report={'status':'passed' if not errors else 'failed','active_countries_added_or_completed':sum(c['active'] for c in m['countries']), 'registered_dormant_countries':sum(not c['active'] for c in m['countries']), 'checks':['Unique states and province membership','Capital ownership, leaders, portrait paths and RU/EN labels','All three flag sizes','Conserved split provinces and population','Starter armies and existing Japanese deployment ownership','Diplomatic participants, modifiers and repeat protection','Japanese and Philippine political geography'], 'errors':errors,'engine_test':'Not run; static validation does not establish campaign balance.'}
(R/'tools/canon_countries_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(bool(errors))
