"""Validate revised dates, IDs, AI canon, helper effects and repeatability."""
from datetime import datetime,timedelta
import json,re,hashlib
from apply_chronicle_revision import ROOT,read,main
from validate_philippines_rework import parse,value,walk

def run():
    paths=[];total=0
    for year,count in ((1893,40),(1894,39),(1895,24),(1896,24)):
        prefix=f'ch{str(year)[2:]}';rows=json.loads(read(f'tools/chronicle_{year}_manifest.json'))
        assert len(rows)==count
        byid={r['id']:r for r in rows};assert len(byid)==count
        events=parse(read(f'events/chronicle_{year}.txt'))
        eventlist=[v for k,o,v in events if k=='country_event']
        definitions={value(v,'id'):v for v in eventlist}
        assert len(definitions)==len(eventlist)
        loc=set(re.findall(r'^\s+([\w.]+):0',read(f'localisation/russian/chronicle_{year}_l_russian.yml'),re.M))
        for row in rows:
            event=definitions[f'{prefix}.{row["id"]}']
            opts=[v for k,o,v in event if k=='option'];assert len(opts)==2
            # 1896 has conditional AI weights; the revised years use fixed canon.
            if year in (1893,1894):
                assert [int(value(value(v,'ai_chance'),'factor')) for v in opts]==[100 if i+1==row['canonical'] else 0 for i in range(2)]
        for k,o,v in walk(events):
            if k in ('title','desc','text','name') and isinstance(v,str) and v.startswith((prefix+'.',prefix.upper()+'_')):assert v in loc,(year,v)
            if k=='country_event' and isinstance(v,list):assert value(v,'id') in definitions
        script=read(f'common/scripted_effects/chronicle_{year}.txt');parse(script)
        # Read the emitted schedule, rather than simulating the manifest alone.
        schedule=value(parse(script),prefix.upper()+'_tick')
        outer=value(schedule,'if')
        actual=[]
        for k,o,v in outer:
            if k!='if' or not isinstance(v,list):continue
            flag=value(v,'set_global_flag')
            if isinstance(flag,str) and flag.startswith(prefix+'_queued_'):
                actual.append((value(value(v,'limit'),'date'),flag.rsplit('_',1)[1]))
        assert len(actual)==count
        for date,n in actual:
            assert datetime.strptime(date,'%Y.%m.%d')+timedelta(days=1)==datetime.strptime(byid[int(n)]['date'],'%d.%m.%Y')
        for start in (datetime(year,1,1),datetime(year,7,1)):
            flags=set();fired=[];day=start
            while day.year==year:
                for pulse in range(2):
                    for date,n in actual:
                        if day>datetime.strptime(date,'%Y.%m.%d') and n not in flags:flags.add(n);fired.append(n)
                day+=timedelta(days=1)
            assert len(fired)==count
        total+=count
        for folder,suffix in (('events','.txt'),('common/scripted_effects','.txt'),('localisation/russian','_l_russian.yml'),('tools','_manifest.json')):paths.append(ROOT/f'{folder}/chronicle_{year}{suffix}')
    for year in (1894,1895):
        s=read(f'common/scripted_effects/chronicle_{year}.txt')
        assert 'retire_character = A06_pobedonostsev' not in s
        assert 'set_country_flag = CH94_pobedonostsev_dead' not in s
    from apply_chronicle_revision import block
    s=read('common/scripted_effects/chronicle_1896.txt');a,b=block(s,'CH96_batavia_compromise = {');peace=s[a:b]
    assert 'CH96_restore_borneo = yes' in peace and 'CH96_transfer_north = yes' not in peace
    assert 'CH96_ludolf_cabinet = yes' in peace
    a,b=block(s,'CH96_restore_borneo = {');restoration=s[a:b]
    restoration_tree=parse(restoration)
    assert any(k=='is_owned_by' and v=='A03' for k,o,v in walk(restoration_tree))
    assert any(k=='A01' and isinstance(v,list) and value(v,'transfer_state') is not None for k,o,v in walk(restoration_tree))
    assert '327' not in restoration
    before={p:hashlib.sha256(p.read_bytes()).digest() for p in paths}
    main()
    assert all(hashlib.sha256(p.read_bytes()).digest()==h for p,h in before.items()),'Revision must be idempotent'
    print(f'PASS: {total} dated choices, parsed scripts, unique IDs, localization, canonical AI, repeat calendar pulses, survival and peace regression checks; idempotent rebuild. No game launch.')

if __name__=='__main__':run()
