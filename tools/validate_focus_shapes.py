"""Layout spacing, all alternative routes, reference integrity and repeatability."""
from pathlib import Path
from collections import defaultdict,Counter
from itertools import product
import json,hashlib,re
from validate_philippines_rework import parse,value,walk

ROOT=Path(__file__).resolve().parents[1]
def load(path):return parse((ROOT/path).read_text(encoding='utf-8-sig'))

def reachable(fs,blocked):
    taken=set()
    while True:
        before=set(taken)
        for key,f in fs.items():
            if key in blocked:continue
            groups=[{v for k,o,v in group if k=='focus'} for k,o,group in f if k=='prerequisite']
            excluded={v for k,o,group in f if k=='mutually_exclusive' for a,b,v in group}
            if not excluded&taken and all(g&taken for g in groups):taken.add(key)
        if taken==before:return taken

def main():
    report=json.loads((ROOT/'tools/focus_shapes_manifest.json').read_text(encoding='utf-8'))
    assert 'a01_focus.txt' not in report and len(report)==36
    saved=json.loads((ROOT/'tools/dutch_reference_layout.json').read_text(encoding='utf-8'))
    assert hashlib.sha256((ROOT/saved['file']).read_bytes()).hexdigest()==saved['sha256'],'Dutch reference changed'
    keys={}
    for language in ('russian','english'):
        path=ROOT/f'localisation/{language}/FSP_focus_shapes_l_{language}.yml';assert path.read_bytes().startswith(b'\xef\xbb\xbf')
        entries=re.findall(r'^\s+([^ :]+):0',path.read_text(encoding='utf-8-sig'),re.M);assert len(entries)==len(set(entries));keys[language]=set(entries)
    assert keys['russian']==keys['english']
    allfs={};cases=0
    for name,rec in report.items():
        fs={value(v,'id'):v for k,o,v in value(load('common/national_focus/'+name),'focus_tree') if k=='focus'}
        assert len(fs)==rec['focuses'];allfs.update(fs)
        pos={k:(int(value(f,'x')),int(value(f,'y'))) for k,f in fs.items()};assert len(set(pos.values()))==len(pos)
        rows=defaultdict(list)
        for key,(x,y) in pos.items():rows[y].append((x,key))
        for row in rows.values():
            row.sort()
            for a,b in zip(row,row[1:]):assert b[0]-a[0]>=4,(name,a,b,'missing empty focus slot')
        for key,f in fs.items():
            for k,o,g in f:
                if k in ('prerequisite','mutually_exclusive'):
                    for a,b,target in g:
                        assert target in fs,(key,target)
                        if k=='prerequisite':assert pos[target][1]<pos[key][1],(key,target)
                        else:assert any(k=='mutually_exclusive' and any(v==key for a,b,v in ns) for k,o,ns in fs[target]),(key,target)
        if name.startswith('AUC_campaign_') and name!='AUC_campaign_A07.txt':
            tag=name.removeprefix('AUC_campaign_').removesuffix('.txt');p='AUC_'+tag+'_'
            total=set()
            for opening,economy,federal in product((True,False),repeat=3):
                blocked={p+('opening_delegates' if opening else 'opening_parliament'),
                         p+('merchant_orders' if economy else 'public_works'),
                         p+('separate' if federal else 'federal')}
                taken=reachable(fs,blocked)
                assert p+'development_programme' in taken and p+'prepared_colony' in taken,(tag,blocked)
                total|=taken
            assert total==set(fs),(tag,'unreachable colonial focus',set(fs)-total)
        if name.startswith('MNR_'):
            tag=name[4:7];p='MNR_'+tag+'_';total=set()
            for civic,local,garrison in product((True,False),repeat=3):
                blocked={p+('command' if civic else 'civic'),p+('economy_contracts' if local else 'economy_local'),p+('defence_mobile' if garrison else 'defence_garrison')}
                taken=reachable(fs,blocked);assert p+'goal' in taken,(tag,blocked,'blocked final goal')
                assert p+'common_programme' in taken and p+'specialists' in taken;total|=taken;cases+=1
            assert total==set(fs),(tag,'unreachable content',set(fs)-total)
    # New policy forks grant different outcomes and never impose foreign sovereignty.
    forbidden={'annex_country','transfer_state','set_autonomy','declare_war_on','add_to_faction','retire_character'}
    for key in keys['russian']:
        if key not in allfs:continue
        f=allfs[key];assert key+'_desc' in keys['russian']
        reward=value(f,'completion_reward');assert not {k for k,o,v in walk(reward)}&forbidden,key
        for k,o,ns in f:
            if k=='mutually_exclusive':
                for a,b,target in ns:assert reward!=value(allfs[target],'completion_reward'),key
    # Barton is recruited once from history, without replacing the starting leader.
    hist=(ROOT/'history/countries/A07 - Placeholder.txt').read_text(encoding='utf-8-sig')
    assert hist.count('recruit_character = AUC_edmund_barton')==1
    assert hist.index('recruit_character = AUC_edmund_barton')<hist.index('recruit_character = A07_canon_leader')
    assert 'recruit_character' not in str(value(allfs['AUC_A07_first_ministry'],'completion_reward'))
    assert value(value(allfs['AUC_A07_first_ministry'],'completion_reward'),'promote_character') is not None
    # References in decisions/events survive new geometry, including paid escort orders.
    ids=set(allfs)|set(saved['positions'])
    for folder in ('common/decisions','events','common/scripted_effects'):
        for path in (ROOT/folder).glob('*.txt'):
            if not path.name.startswith(('MNR_','AUC_','BLV_','JSM_')):continue
            for k,o,v in walk(parse(path.read_text(encoding='utf-8-sig'))):
                if k=='has_completed_focus':assert v in ids,(path,v)
    paths=[ROOT/'common/national_focus'/name for name in report]+[ROOT/saved['file'],ROOT/'tools/focus_layout_baseline.json']
    paths+=list((ROOT/'localisation').rglob('FSP_focus_shapes*.yml'))
    hashes={p:hashlib.sha256(p.read_bytes()).digest() for p in paths}
    from focus_shapes import apply
    apply();assert all(hashlib.sha256(p.read_bytes()).digest()==h for p,h in hashes.items()),'Layout generator drifted'
    result=dict(trees=len(report),focuses=len(allfs),new_nodes=sum(len(r['added']) for r in report.values()),minor_route_cases=cases,minimum_horizontal_grid_gap=4,dutch_reference_preserved=True,limitations=['Schematic rendering and script checks; no new in-game screenshot.'])
    (ROOT/'tools/focus_shapes_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {len(report)} trees, {len(allfs)} focuses, {cases} minor route combinations; empty focus slots, DAGs, symmetric choices, distinct rewards, unchanged Dutch reference and repeatable generation.')

if __name__=='__main__':main()
