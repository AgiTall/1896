"""Cross-check focus/calendar order, delayed answers, canonical dates and rebuilds."""
from pathlib import Path
from copy import deepcopy
import hashlib,json
from validate_british_campaign import World,FX,ROOT,load,value,walk,read
from british_story_links import sync,LINKS

def events(year):return {value(v,'id'):v for k,o,v in load(f'events/chronicle_{year}.txt') if k=='country_event'}
CH={y:events(y) for y in range(1893,1897)}
STORY={value(v,'id'):v for k,o,v in load('events/BLV_story.txt') if k=='country_event'}
def option(year,n,i=0):return [v for k,o,v in CH[year][f'ch{str(year)[2:]}.{n}'] if k=='option'][i]
def snapshot(w):return deepcopy((w.vars,w.pp,w.fuel,w.equipment,w.ideas,w.events,w.politics,w.overlord,w.manpower))
def fixture():
    w=World();w.run(FX['BLV_initialize']);w.flags['A02']|={'SEN_laboratory_done','SEN_research_license'}
    w.owner[326]='A02';w.controller[326]='A02';return w

def run():
    manifest=json.loads(read(ROOT/'tools/british_story_links_manifest.json'));assert len(manifest)==21
    focuses={value(v,'id'):v for k,o,v in value(load('common/national_focus/BLV_campaign.txt'),'focus_tree') if k=='focus'}
    for fid,flag in [('BLV_malacca','BLV_passage_decided'),('BLV_calibration','BLV_calibrated'),('BLV_tesla_patents','BLV_patents_decided'),('BLV_ship_suppressors','BLV_installation_decided'),('BLV_airship_service','BLV_airships_decided'),('BLV_polar_mandate','BLV_polar_decided'),('BLV_crowns_council','BLV_crowns_decided')]:
        assert value(value(focuses[fid],'bypass'),'has_country_flag')==flag
    # No focus can grant these dated policies early, even through its actual reward.
    for fid,date in [('BLV_malacca',(1893,11,28)),('BLV_ungudja',(1893,4,12)),('BLV_calibration',(1894,7,20)),('BLV_tesla_patents',(1894,10,25)),('BLV_ship_suppressors',(1895,5,20)),('BLV_airship_service',(1896,5,20)),('BLV_polar_mandate',(1896,8,5)),('BLV_crowns_council',(1896,12,10))]:
        w=fixture();w.flags['A02'].add('BLV_calibrated');w.date=(1892,1,1)
        assert not w.test(value(focuses[fid],'available'))
        before=snapshot(w);w.run(value(focuses[fid],'completion_reward'));assert snapshot(w)==before,fid
        w.date=date;assert w.test(value(focuses[fid],'available')),fid
    # One common outcome in both orders, including payment and invitation queues.
    pairs=[(1893,18,0,'BLV_apply_serum_contract'),(1893,18,1,'BLV_apply_ethical_research'),(1893,33,0,'BLV_apply_passage_open'),(1893,33,1,'BLV_apply_passage_blockade'),(1894,20,0,'BLV_apply_calibration'),(1894,30,0,'BLV_apply_patents_private'),(1894,30,1,'BLV_apply_patents_offer'),(1895,10,0,'BLV_apply_mobile_installation'),(1895,10,1,'BLV_apply_tower_installation'),(1896,10,0,'BLV_apply_airship_scouts'),(1896,10,1,'BLV_apply_airship_strike'),(1896,15,0,'BLV_apply_polar_private'),(1896,15,1,'BLV_apply_polar_joint'),(1896,23,0,'BLV_apply_crowns_legal'),(1896,23,1,'BLV_apply_crowns_separate')]
    expected=['BLV_serum_contract','BLV_ethical_research','BLV_open_passage','BLV_passage_blockade','BLV_calibrated','BLV_patents_private','BLV_patents_offered','CH95_tesla_mobile','CH95_tesla_stationary','BLV_airship_scouts','BLV_airship_strike','CH96_secret_greenland','BLV_joint_polar_offer','BLV_crowns_association','BLV_separate_courts']
    expected=dict(zip((p[3] for p in pairs),expected))
    for y,n,i,effect in pairs:
        for focus_first in (False,True):
            w=fixture()
            if (y,n) in ((1894,30),(1895,10)):w.flags['A02'].add('BLV_calibrated')
            if focus_first:
                w.run(FX[effect]);assert expected[effect] in w.flags['A02'],effect
                assert w.test(value(option(y,n,i),'trigger',[])),(effect,'chosen option unavailable')
                before=snapshot(w);w.run(option(y,n,i));assert snapshot(w)==before,(y,n,i,'focus first')
            else:
                w.run(option(y,n,i));assert expected[effect] in w.flags['A02'],effect
                before=snapshot(w);w.run(FX[effect]);assert snapshot(w)==before,(y,n,i,'event first')
    # All linked event branches are single-use and cannot pay anything before date.
    for row in manifest:
        y,n=row['year'],row['id'];owner=next(r['tag'] for r in json.loads(read(ROOT/f'tools/chronicle_{y}_manifest.json')) if r['id']==n)
        for i in (0,1):
            w=fixture();w.flags['A02']|={'BLV_calibrated','BLV_serum_contract'};w.gflags.add('CH93_crowns_plot_exposed')
            w.run(option(y,n,i),owner,owner);before=snapshot(w);w.run(option(y,n,i),owner,owner);assert snapshot(w)==before,(y,n,i)
            w=fixture();w.date=(1892,1,1);before=snapshot(w);w.run(option(y,n,i),owner,owner);assert snapshot(w)==before,(y,n,i,'early')
    # A focus may explicitly repeal a prior licence. Later foreign supply cannot.
    w=fixture();w.run(option(1893,18,0));assert 'BLV_serum_contract' in w.flags['A02']
    w.run(value(focuses['BLV_ethical_research'],'completion_reward'));assert 'BLV_serum_contract' not in w.flags['A02'] and 'BLV_ethical_research' in w.flags['A02']
    before=snapshot(w);w.run(option(1894,9,0),'A04','A04');assert snapshot(w)==before
    assert 'ch94_9_inactive' in w.gflags
    # Tesla absent/hostile => no imaginary British success; late focus can recover.
    w=fixture();w.flags['A02'].discard('SEN_research_license');before=snapshot(w);w.run(option(1894,20));assert snapshot(w)==before and 'BLV_calibrated' not in w.flags['A02']
    w.flags['A02'].add('SEN_research_license');w.run(value(focuses['BLV_calibration'],'completion_reward'));assert 'BLV_calibrated' in w.flags['A02'] and 'SEN_advanced_knowledge' not in w.flags['A02']
    # Neither patents nor a joint expedition charge another player without consent.
    w=fixture();w.flags['A02'].add('BLV_calibrated');before=w.pp['A04'];w.run(FX['BLV_apply_patents_offer']);assert w.pp['A04']==before and 'BLV_patent_sale_paid' not in w.flags['A02']
    accept=next(v for k,o,v in STORY['blv_story.3'] if k=='option');w.run(accept,'A04','A04');assert w.pp['A04']==before-75 and 'BLV_patent_sale_paid' in w.flags['A02']
    before=snapshot(w);w.run(accept,'A04','A04');assert snapshot(w)==before
    # An open calendar question always retains an acknowledgement after the
    # completed work loses its teacher or the offer loses its counterparty.
    w=fixture();w.flags['A02'].add('BLV_calibrated');w.gflags.discard('SEN_tesla_alive')
    assert w.test(value(option(1894,20,0),'trigger'))
    w=fixture();w.flags['A02']|={'BLV_calibrated','BLV_patents_offered','BLV_patents_decided'};w.tags.remove('A04')
    assert w.test(value(option(1894,30,1),'trigger'))
    w=fixture();before=w.pp['A04'];w.run(FX['BLV_apply_polar_joint']);assert w.pp['A04']==before and 'CH96_joint_greenland' not in w.gflags
    # The Council of Crowns is a political body; constitutions and foreign leaders
    # survive both the December choice and the historical helper alias.
    w=fixture();w.politics={'A02':{'ruling_party':'democratic','elections_allowed':'yes'},'A06':{'ruling_party':'neutrality'}};before=deepcopy((w.politics,w.overlord,w.wars,w.faction))
    w.run(option(1896,23,0));assert (w.politics,w.overlord,w.wars,w.faction)==before
    w=fixture();before=deepcopy(w.wars);w.run(option(1896,23,1));assert w.wars==before
    alias=value(load('common/scripted_effects/chronicle_1896.txt'),'CH96_united_crowns');assert value(alias,'BLV_apply_crowns_legal')=='yes'
    forbidden={'create_country_leader','set_politics','set_autonomy','declare_war_on','create_faction_from_template','add_to_faction'}
    assert not {k for k,o,v in walk(FX['BLV_apply_crowns_legal'])}&forbidden
    # A successful 1893 plot does not lead to the failed-plot expulsion in November.
    w=fixture();w.gflags.add('CH93_crowns_plot_succeeded');w.run(option(1893,40,0),'A06','A06');assert 'CH93_emperor_returned' not in w.flags['A06']
    # Port stories must not punish Britain or seize a port after ownership changes.
    for y,n,sid in ((1894,11,1021),(1894,33,326),(1895,8,1021),(1896,15,101)):
        w=fixture();w.owner[sid]='A03';w.controller[sid]='A03';before=snapshot(w);w.run(option(y,n));assert snapshot(w)==before
    # Every story callback and both language versions exist; no duplicate loc keys.
    keys={lang:set() for lang in ('russian','english')}
    import re
    for lang in keys:
        for p in (ROOT/f'localisation/{lang}').rglob('*.yml'):
            found=re.findall(r'^\s+([\w.]+):\d+',read(p),re.M)
            for k in found:
                if k.startswith('blv_story.'):assert k not in keys[lang],(lang,k)
                keys[lang].add(k)
    for event in STORY.values():
        for k,o,v in walk(event):
            if k in ('title','desc','name') and isinstance(v,str) and v.startswith('blv_story.'):
                assert all(v in entries for entries in keys.values()),v
    paths=[ROOT/f'events/chronicle_{y}.txt' for y in range(1893,1897)]+[ROOT/f'common/scripted_effects/chronicle_{y}.txt' for y in range(1893,1897)]+[ROOT/f'localisation/russian/chronicle_{y}_l_russian.yml' for y in range(1893,1897)]+[ROOT/'events/BLV_story.txt',ROOT/'common/scripted_effects/BLV_story.txt']
    hashes={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths};sync();assert all(hashlib.sha256(p.read_bytes()).hexdigest()==v for p,v in hashes.items())
    print('PASS: 21 dated stories; 30 focus/event order cases; replay, date, policy repeal, missing Tesla, consent, foreign sovereignty, port ownership, multilingual callbacks and repeatable generation.')

if __name__=='__main__':run()
