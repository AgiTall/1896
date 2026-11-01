"""Check the colonial partition without launching HOI4."""
from pathlib import Path
import re,json
from PIL import Image
from split_localisation import entries
R=Path(__file__).resolve().parents[1]
data=json.loads((R/'tools/australia_1893_manifest.json').read_text(encoding='utf-8'))
states={int(re.search(r'\bid\s*=\s*(\d+)',p.read_text(encoding='utf-8-sig'))[1]):p for p in (R/'history/states').glob('*.txt')}
tags='\n'.join(p.read_text(encoding='utf-8-sig') for p in (R/'common/country_tags').glob('*.txt'))
hooks=(R/'common/on_actions/AUC_colonies.txt').read_text()
all_states=[]
for tag,c in data.items():
    assert len(re.findall(rf'^\s*{tag}\s*=',tags,re.M))==1,tag
    histories=list((R/'history/countries').glob(tag+' - *.txt'));assert len(histories)==1
    history=histories[0].read_text(encoding='utf-8-sig')
    assert f'capital = {c["capital"]}' in history
    assert c['capital'] in c['states']
    assert f'target = {tag} autonomy_state = AUC_self_governing_colony' in hooks
    for sid in c['states']:
        text=states[sid].read_text(encoding='utf-8-sig')
        assert re.search(rf'\bowner\s*=\s*{tag}\b',text),(sid,tag)
        assert re.search(rf'\badd_core_of\s*=\s*{tag}\b',text),(sid,tag)
        if tag!='A07':assert not re.search(r'\badd_core_of\s*=\s*A07\b',text)
        backup=R/'tools/backups/australia_before_split_1893'/states[sid].relative_to(R)
        original=backup.read_text(encoding='utf-8-sig')
        for pattern in (r'\bmanpower\s*=\s*\d+',r'\b(?:industrial_complex|arms_factory|dockyard)\s*=\s*\d+'):
            assert re.findall(pattern,text)==re.findall(pattern,original),(sid,'economy changed')
        all_states.append(sid)
    for folder,size in [('',(82,52)),('medium',(41,26)),('small',(10,7))]:
        for suffix in ('','_democratic','_neutrality'):
            with Image.open(R/'gfx/flags'/folder/(tag+suffix+'.tga')) as im:assert im.size==size
assert len(all_states)==len(set(all_states))==14
assert 'owner = A02' in states[523].read_text()
assert 'add_core_of = A07' not in states[523].read_text()
for lang in ('russian','english'):
    loc=entries(sorted((R/'localisation'/lang).glob('*.yml')))
    for tag in data:assert tag in loc and tag+'_democratic' in loc
    assert 'AUC_self_governing_colony' in loc
for folder in ('common/on_actions','common/autonomous_states','common/characters','common/countries','history/countries'):
    for p in (R/folder).glob('*.txt'):
        if p.stem.startswith(('AUC','AVC','AQL','ASA','AWA','ATA')):
            text=p.read_text(encoding='utf-8-sig');assert text.count('{')==text.count('}'),p
print('PASS: 6 colonies, 14 regions, capitals, sovereignty, 54 flags, localisation and economy preservation')
