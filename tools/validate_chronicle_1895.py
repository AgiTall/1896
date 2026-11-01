"""Validate the installed three-year calendar and 1895 continuation guards."""
from pathlib import Path
from datetime import datetime,timedelta
import json,re
from validate_philippines_rework import parse,value,walk
R=Path(__file__).resolve().parents[1]

def read(p):return p.read_text(encoding='utf-8-sig')

def run():
    rows=json.loads(read(R/'tools/chronicle_1895_manifest.json'))
    assert len(rows)==24 and rows[0]['canonical']==2 and rows[13]['canonical']==2
    paths=[R/f for f in ('events/chronicle_1895.txt','common/scripted_effects/chronicle_1895.txt','common/on_actions/chronicle_1895.txt','common/ideas/chronicle_1895.txt')]
    trees={p:parse(read(p)) for p in paths}
    event_nodes=[v for k,o,v in trees[paths[0]] if k=='country_event']
    events={value(v,'id'):v for v in event_nodes}
    assert len(event_nodes)==len(events)==72
    locpath=R/'localisation/russian/chronicle_1895_l_russian.yml'
    assert locpath.read_bytes().startswith(b'\xef\xbb\xbf')
    keys=re.findall(r'^\s+(\w[\w.]*):0',read(locpath),re.M)
    assert len(keys)==len(set(keys))
    for n in range(1,25):
        options=[v for k,o,v in events[f'ch95.{n}'] if k=='option']
        assert len(options)==2
        weights=[int(value(value(o,'ai_chance'),'factor')) for o in options]
        assert weights[rows[n-1]['canonical']-1]==100 and sum(weights)==100
    all_ids=[]
    for p in (R/'events').glob('*.txt'):
        all_ids.extend(value(v,'id') for k,o,v in parse(read(p)) if k=='country_event')
    for eid in events:assert all_ids.count(eid)==1,eid
    definitions={k for p in (R/'common/scripted_effects').glob('*.txt') for k,o,v in parse(read(p))}
    idea_defs={k for p in (R/'common/ideas').glob('*.txt') for a,b,node in parse(read(p)) if a=='ideas' for group,_,items in node if isinstance(items,list) for k,_,v in items}
    for tree in trees.values():
        for k,o,v in walk(tree):
            if k in ('title','desc','text','name') and isinstance(v,str) and v.startswith(('ch95.','CH95_')):assert v in keys,(k,v)
            if k=='country_event' and isinstance(v,list):assert value(v,'id') in events
            if k.startswith(('CH94_','CH95_','WTC_','WTN_')) and v=='yes':assert k in definitions,k
            if k=='add_ideas':assert v in idea_defs,v
            if k=='add_timed_idea':assert value(v,'idea') in idea_defs,value(v,'idea')
    # Exercise the actual parsed tick blocks over all three years, with duplicate
    # daily pulses, old saves and 1896 boundary calls.
    schedules={y:dict((k,v) for k,o,v in parse(read(R/f'common/scripted_effects/chronicle_{y}.txt')))[f'CH{str(y)[2:]}_tick'] for y in (1893,1894,1895)}
    def eligible(node,day,flags):
        for k,op,v in node:
            if k=='date':
                date=datetime.strptime(v,'%Y.%m.%d')
                if not (day>date if op=='>' else day<date):return False
            elif k=='has_global_flag':
                if v not in flags:return False
            elif k=='NOT':
                if eligible(v,day,flags):return False
            else:raise AssertionError(k)
        return True
    for start in (datetime(1893,1,1),datetime(1895,1,1),datetime(1895,8,1),datetime(1896,1,1)):
        flags=set();fired=[];day=start
        while day<=datetime(1896,1,2):
            for pulse in range(2):
                for year,schedule in schedules.items():
                    outer=value(schedule,'if')
                    if eligible(value(outer,'limit'),day,flags):
                        for k,o,node in outer:
                            if k=='if' and eligible(value(node,'limit'),day,flags):
                                flag=value(node,'set_global_flag');flags.add(flag);fired.append((year,int(flag.rsplit('_',1)[1]),day))
            day+=timedelta(days=1)
        assert len(fired)==(96 if start.year==1893 else 24 if start.year==1895 else 0)
        if start==datetime(1893,1,1):
            for year,n,day in fired:
                manifest=json.loads(read(R/f'tools/chronicle_{year}_manifest.json'))
                assert day==datetime.strptime(manifest[n-1]['date'],'%d.%m.%Y')
    effects=dict((k,v) for k,o,v in trees[paths[1]])
    assert 'has_government' in str(value(value(effects['CH95_hawaii_republic'],'if'),'if'))
    assert not any(k in ('recruit_character','create_country_leader') for k,o,v in walk(effects['CH95_pobedonostsev_legacy']))
    assert 'has_character' in str(effects['CH95_pobedonostsev_legacy'])
    assert 'CH94_pobedonostsev_dead' in str(events['ch95.17'])
    assert 'is_controlled_by' in str(value(value(effects['CH95_brunei_retreat'],'if'),'limit'))
    loans=value(effects['CH95_war_loans'],'if')
    assert value(value(value(loans,'limit'),'check_variable'),'WTN_liquidity')=='19'
    assert 'WTC_debt' in str(effects['CH95_war_loans'])
    assert not any(k=='white_peace' for k,o,v in walk(effects['CH95_peace_conference']))
    game=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV/documentation')
    if game.exists():
        modifiers=set(re.findall(r'^## (\w+)\s*$',read(game/'modifiers_documentation.md'),re.M))
        for k,o,v in walk(trees[paths[3]]):
            if k=='modifier':
                for name,_,_ in v:assert name in modifiers or re.fullmatch(r'production_speed_\w+_factor',name),name
        effects_doc=read(game/'effects_documentation.md')
        for name in ('drop_cosmetic_tag','set_state_controller','create_country_leader','retire_character','add_to_variable'):
            assert f'## {name}\n' in effects_doc,name
    print('PASS: 24 choices/72 events, references, canonical AI, 96 dates across 1893–1895, duplicate pulses, save catch-up, debt integration, continuity guards and documented modifiers.')

if __name__=='__main__':run()
