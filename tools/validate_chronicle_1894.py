"""Parse installed scripts and exercise calendar/branch eligibility boundaries."""
from pathlib import Path
from datetime import datetime,timedelta
import json,re
from validate_philippines_rework import parse,value,walk
R=Path(__file__).resolve().parents[1]

def run():
    paths=[R/f for f in ('events/chronicle_1894.txt','common/scripted_effects/chronicle_1894.txt','common/on_actions/chronicle_1894.txt','common/ideas/chronicle_1894.txt')]
    trees={p:parse(p.read_text(encoding='utf-8-sig')) for p in paths}
    events={value(v,'id'):v for k,o,v in trees[paths[0]] if k=='country_event'}
    assert len(events)==108
    locpath=R/'localisation/russian/chronicle_1894_l_russian.yml'
    assert locpath.read_bytes().startswith(b'\xef\xbb\xbf')
    loc=set(re.findall(r'^\s+(\w[\w.]*):0',locpath.read_text(encoding='utf-8-sig'),re.M))
    for n in range(1,37):
        options=[v for k,o,v in events[f'ch94.{n}'] if k=='option']
        assert len(options)==2
        assert sorted(int(value(value(o,'ai_chance'),'factor')) for o in options)==[0,100]
    for tree in trees.values():
        for k,o,v in walk(tree):
            if k in ('title','desc','text','name') and isinstance(v,str) and v.startswith(('ch94.','CH94_')):
                assert v in loc,(k,v)
            if k=='country_event' and isinstance(v,list):
                assert value(v,'id') in events
    effects=dict((k,v) for k,o,v in trees[paths[1]])
    # Evaluate the real generated calendar conditions; repeated daily pulses and
    # repeated startup calls must never duplicate a scheduled event.
    def evaluate(node,flags,day):
        for k,op,v in node:
            if k=='date':
                d=datetime.strptime(v,'%Y.%m.%d')
                if not (day>d if op=='>' else day<d):return False
            elif k=='has_global_flag':
                if v not in flags:return False
            elif k=='NOT':
                if evaluate(v,flags,day):return False
            else:raise AssertionError(k)
        return True
    outer=next(v for k,o,v in effects['CH94_tick'] if k=='if')
    rows=json.loads((R/'tools/chronicle_1894_manifest.json').read_text(encoding='utf-8'))
    assert len(rows)==36 and rows[3]['canonical']==2 and rows[25]['canonical']==1
    for start in (datetime(1893,12,31),datetime(1894,1,1),datetime(1894,7,1),datetime(1895,1,1)):
        flags=set(); fired=[]; day=start
        while day<=datetime(1895,1,2):
            for pulse in range(2):
                if evaluate(value(outer,'limit'),flags,day):
                    for k,o,v in outer:
                        if k=='if' and evaluate(value(v,'limit'),flags,day):
                            flag=value(v,'set_global_flag'); flags.add(flag)
                            fired.append((int(flag.rsplit('_',1)[1]),day))
            day+=timedelta(days=1)
        assert len(fired)==(0 if start.year==1895 else 36)
        if start<datetime(1894,7,1):
            assert all(day==datetime.strptime(rows[n-1]['date'],'%d.%m.%Y') for n,day in fired)
    # Major branch safeguards and effects must survive regeneration.
    front=value(effects['CH94_open_second_front'],'if')
    gates=dict((k,v) for k,o,v in value(front,'limit'))
    assert gates['is_subject']=='no' and gates['country_exists']=='A03'
    assert len([v for k,o,v in value(front,'limit') if k=='NOT'])==5
    assert value(value(effects['CH94_hawaiian_republic'],'set_politics'),'ruling_party')=='democratic'
    assert value(effects['CH94_ito_emergency'],'if')
    assert 'CH94_tesla_prototype' in str(value(value(effects['CH94_tesla_sale'],'if'),'limit'))
    assert 'is_controlled_by' in str(value(value(effects['CH94_burn_oil'],'if'),'limit'))
    assert 'CH94_oil_destroyed' in str(effects['CH94_burn_oil'])
    assert 'retire_character' in str(effects['CH94_pobedonostsev_dies'])
    assert 'date > 1894.12.31' in (R/'events/A10_philippines.txt').read_text(encoding='utf-8')
    game=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV/documentation')
    if game.exists():
        modifiers=set(re.findall(r'^## (\w+)\s*$',(game/'modifiers_documentation.md').read_text(encoding='utf-8-sig'),re.M))
        for k,o,v in walk(trees[paths[3]]):
            if k=='modifier':
                for name,_,_ in v:
                    assert name in modifiers or re.fullmatch(r'production_speed_\w+_factor',name), name
        documented=(game/'effects_documentation.md').read_text(encoding='utf-8-sig')
        for name in ('add_country_leader_role','add_resource','create_country_leader','retire_character','set_state_controller'):
            assert f'## {name}\n' in documented,name
    print('PASS: 36 dated choices, 108 event IDs, canonical options, localization, parsed syntax, actual calendar conditions, duplicate pulses, year boundaries and campaign guards.')

if __name__=='__main__':run()
