"""Check the shipped tree and execute live campaign guards in a bounded model."""
from pathlib import Path
from collections import defaultdict,Counter
from copy import deepcopy
import json,re
from validate_philippines_rework import parse,value,walk

ROOT=Path(__file__).resolve().parents[1]
GAME=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
def read(p):return p.read_text(encoding='utf-8-sig')
def load(path):return parse(read(ROOT/path))
FX={k:v for k,o,v in load('common/scripted_effects/BLV_campaign.txt')}
FX.update({k:v for k,o,v in load('common/scripted_effects/BLV_story.txt')})
TR={k:v for k,o,v in load('common/scripted_triggers/BLV_campaign.txt')}
EVENTS={value(v,'id'):v for k,o,v in load('events/BLV_campaign.txt') if k=='country_event'}
DEC={k:v for k,o,v in value(load('common/decisions/BLV_campaign.txt'),'BLV_imperial_government')}
TAGS={'A01','A02','A03','A04','A06','A07','A10','MLT','AVC','AQL','ASA','AWA','ATA','ZZZ'}

class World:
    def __init__(self,mtg=True):
        self.tags=set(TAGS);self.flags=defaultdict(set);self.gflags=set();self.vars=defaultdict(lambda:defaultdict(float))
        self.owner={696:'A02',101:'A02',1021:'A02',116:'MLT',334:'A01',284:'A02'};self.controller=dict(self.owner);self.sf=defaultdict(set)
        self.overlord={'A07':'A02'};self.faction={};self.wars=set();self.capitulated=set();self.ideas=defaultdict(set)
        self.equipment=defaultdict(lambda:defaultdict(float));self.pp=defaultdict(lambda:500);self.fuel=defaultdict(float)
        self.completed={'BLV_song_records'};self.date=(1901,2,1);self.mtg=mtg;self.loaded=[];self.events=[];self.constructed=[];self.designs=[]
        self.politics={};self.popularities={}
        self.manpower=defaultdict(float)
    def test(self,node,tag='A02',root='A02'):
        results=[]
        for k,o,v in node:
            if k in TR:r=self.test(TR[k],tag,root)==(v=='yes')
            elif k=='AND':r=self.test(v,tag,root)
            elif k=='OR':r=any(self.test([entry],tag,root) for entry in v)
            elif k=='NOT':r=not self.test(v,tag,root)
            elif k in TAGS:r=k in self.tags and self.test(v,k,root)
            elif k=='ROOT':r=self.test(v,root,root)
            elif k=='any_country':r=any(self.test(v,t,root) for t in self.tags)
            elif k=='any_state':r=any(self.test(v,s,root) for s in self.owner)
            elif k.isdigit():r=self.test(v,int(k),root)
            elif k=='tag':r=tag==v
            elif k=='exists':r=(tag in self.tags)==(v=='yes')
            elif k=='country_exists':r=v in self.tags
            elif k=='has_capitulated':r=(tag in self.capitulated)==(v=='yes')
            elif k=='has_country_flag':r=v in self.flags[tag]
            elif k=='has_global_flag':r=v in self.gflags
            elif k=='has_state_flag':r=v in self.sf[tag]
            elif k=='has_idea':r=v in self.ideas[tag]
            elif k=='has_war':r=any(tag in w for w in self.wars)==(v=='yes')
            elif k=='has_war_with':r=frozenset((tag,v)) in self.wars
            elif k=='is_subject':r=(tag in self.overlord)==(v=='yes')
            elif k=='is_subject_of':r=self.overlord.get(tag)==v
            elif k=='is_in_faction_with':r=tag in self.faction and self.faction.get(tag)==self.faction.get(v)
            elif k=='is_owned_by':r=self.owner.get(tag)==(root if v=='ROOT' else v)
            elif k=='is_controlled_by':r=self.controller.get(tag)==(root if v=='ROOT' else v)
            elif k=='check_variable':
                key,op,num=v[0];actual=self.vars[tag][key];r=actual>float(num) if op=='>' else actual<float(num) if op=='<' else actual==float(num)
            elif k=='has_political_power':r=self.pp[tag]>float(v) if o=='>' else self.pp[tag]<float(v)
            elif k=='has_completed_focus':r=v in self.completed
            elif k=='has_character':r=v=='A02_canon_leader'
            elif k=='has_dlc':r=self.mtg
            elif k=='is_ai':r=v=='yes'
            elif k=='has_equipment':
                key,op,num=v[0];actual=self.equipment[tag][key];r=actual>float(num) if op=='>' else actual<float(num)
            elif k=='date':r=self.date>tuple(map(int,v.split('.'))) if o=='>' else self.date<tuple(map(int,v.split('.')))
            else:raise AssertionError(('unmodelled condition',k))
            results.append(r)
        return all(results)
    def run(self,node,tag='A02',root='A02'):
        previous=None
        for k,o,v in node:
            if k in ('limit','name','ai_chance','trigger'):continue
            if k=='if':
                previous=self.test(value(v,'limit'),tag,root)
                if previous:self.run(v,tag,root)
            elif k=='else_if':
                if previous is False:
                    previous=self.test(value(v,'limit'),tag,root)
                    if previous:self.run(v,tag,root)
            elif k=='else':
                if previous is False:self.run(v,tag,root)
            elif k in FX:self.run(FX[k],tag,root)
            elif k in ('WTC_initialize_effect','WTC_refresh_effect','WTC_check_cover_effect'):
                if k=='WTC_initialize_effect' and 'WTC_ledger_open' not in self.flags[tag]:self.flags[tag].add('WTC_ledger_open');self.vars[tag]['WTC_debt']=55
            elif k=='hidden_effect':self.run(v,tag,root)
            elif k in TAGS:
                if k in self.tags:self.run(v,k,root)
            elif k.isdigit():self.run(v,int(k),root)
            elif k in ('every_country','every_state'):
                for scope in list(self.tags if k=='every_country' else self.owner):
                    if value(v,'limit') is None or self.test(value(v,'limit'),scope,root):self.run(v,scope,root)
            elif k=='capital_scope':self.run(v,696,root)
            elif k=='controller':self.run(v,self.controller[tag],root)
            elif k=='set_country_flag':self.flags[tag].add(v if isinstance(v,str) else value(v,'flag'))
            elif k=='clr_country_flag':self.flags[tag].discard(v)
            elif k=='set_global_flag':self.gflags.add(v)
            elif k=='clr_global_flag':self.gflags.discard(v)
            elif k=='set_state_flag':self.sf[tag].add(v)
            elif k=='clr_state_flag':self.sf[tag].discard(v)
            elif k in ('set_variable','add_to_variable'):
                key,_,num=v[0]
                if k=='set_variable':self.vars[tag][key]=float(num)
                else:self.vars[tag][key]+=float(num)
            elif k=='clamp_variable':
                key=value(v,'var');self.vars[tag][key]=max(float(value(v,'min')),min(float(value(v,'max')),self.vars[tag][key]))
            elif k in ('add_ideas','remove_ideas'):
                (self.ideas[tag].add if k=='add_ideas' else self.ideas[tag].discard)(v)
            elif k=='add_timed_idea':self.ideas[tag].add(value(v,'idea'))
            elif k=='set_autonomy':
                target=value(v,'target');assert self.overlord.get(target)==tag;self.overlord.pop(target)
            elif k=='leave_faction':self.faction.pop(tag,None)
            elif k=='load_oob':self.loaded.append(v)
            elif k=='create_equipment_variant':self.designs.append(value(v,'name'))
            elif k=='country_event':self.events.append((tag,value(v,'id'),value(v,'days')))
            elif k=='add_political_power':self.pp[tag]+=float(v)
            elif k=='add_fuel':self.fuel[tag]+=float(v)
            elif k=='add_manpower':self.manpower[tag]+=float(v)
            elif k=='add_equipment_to_stockpile':self.equipment[tag][value(v,'type')]+=float(value(v,'amount'))
            elif k=='add_building_construction':self.constructed.append((tag,value(v,'type')))
            elif k=='set_politics':self.politics[tag]={a:b for a,o,b in v}
            elif k=='set_popularities':
                self.popularities[tag]={a:float(b) for a,o,b in v};assert sum(self.popularities[tag].values())==100
            elif k in ('add_stability','add_war_support','army_experience','navy_experience','air_experience','set_technology','add_extra_state_shared_building_slots','give_military_access','add_country_leader_role','add_tech_bonus'):pass
            else:raise AssertionError(('unmodelled effect',k))

def static_checks():
    folders=('common/national_focus','common/ideas','common/scripted_effects','common/scripted_triggers','common/on_actions','common/decisions','common/decisions/categories','events','history/units')
    paths=[p for d in folders for p in (ROOT/d).glob('BLV_campaign*.txt')];trees={p:parse(read(p)) for p in paths}
    locs={}
    for lang in ('russian','english'):
        p=ROOT/f'localisation/{lang}/BLV_campaign_l_{lang}.yml';assert p.read_bytes().startswith(b'\xef\xbb\xbf')
        entries=re.findall(r'^\s+(\w[\w.]*):0',read(p),re.M);assert len(entries)==len(set(entries));locs[lang]=set(entries)
        locs[lang].update(re.findall(r'^\s+(\w[\w.]*):0',read(ROOT/f'localisation/{lang}/FSP_focus_shapes_l_{lang}.yml'),re.M))
    assert locs['russian']==locs['english'];keys=locs['russian']
    ft=value(trees[ROOT/'common/national_focus/BLV_campaign.txt'],'focus_tree')
    focuses={value(v,'id'):v for k,o,v in ft if k=='focus'};assert len(focuses)==96
    positions={fid:(int(value(v,'x')),int(value(v,'y'))) for fid,v in focuses.items()};assert len(set(positions.values()))==len(positions)
    for fid,v in focuses.items():
        assert fid in keys and fid+'_desc' in keys
        for k,o,group in v:
            if k in ('prerequisite','mutually_exclusive'):
                for _,_,parent in group:
                    assert parent in focuses
                    if k=='prerequisite':assert positions[parent][1]<positions[fid][1],(fid,parent)
                    else:assert fid in [p for a,b,n in focuses[parent] if a=='mutually_exclusive' for _,_,p in n]
    all_loc=set();all_effects=set();all_triggers=set();all_ideas=set();all_events=[]
    for lang in ('russian',):
        for p in (ROOT/f'localisation/{lang}').rglob('*.yml'):all_loc.update(re.findall(r'^\s+(\w[\w.]*):\d+',read(p),re.M))
    for p in (ROOT/'common/scripted_effects').glob('*.txt'):all_effects.update(k for k,o,v in parse(read(p)))
    for p in (ROOT/'common/scripted_triggers').glob('*.txt'):all_triggers.update(k for k,o,v in parse(read(p)))
    for p in (ROOT/'common/ideas').glob('*.txt'):all_ideas.update(k for k,o,v in value(value(parse(read(p)),'ideas',[]),'country',[]))
    for p in (ROOT/'events').glob('*.txt'):all_events.extend(value(v,'id') for k,o,v in parse(read(p)) if k=='country_event')
    assert all(all_events.count(e)==1 for e in EVENTS)
    focus_counts=Counter(value(v,'id') for p in (ROOT/'common/national_focus').glob('*.txt') for k,o,v in value(parse(read(p)),'focus_tree',[]) if k=='focus')
    assert all(focus_counts[fid]==1 for fid in focuses)
    for tree in trees.values():
        for k,o,v in walk(tree):
            if k in ('title','desc','text','name','custom_effect_tooltip') and isinstance(v,str) and v.startswith(('BLV_','blv_campaign.')):assert v in keys,v
            if k.startswith('BLV_') and v=='yes':assert k in all_effects or k in all_triggers,k
            if k in ('add_ideas','remove_ideas','idea') and isinstance(v,str):assert v in all_ideas,v
            if k=='country_event' and isinstance(v,list):assert value(v,'id') in all_events
            if k=='load_oob':assert (ROOT/f'history/units/{v.strip(chr(34))}.txt').exists(),v
    docs=set(re.findall(r'^## (\w+)\s*$',read(GAME/'documentation/modifiers_documentation.md'),re.M))
    ideas=value(value(trees[ROOT/'common/ideas/BLV_campaign.txt'],'ideas'),'country')
    for key,o,node in ideas:
        for mod,_,_ in value(node,'modifier'):assert mod in docs or mod.startswith('production_speed_'),mod
    # Match every installed hull slot and module; 1890s hulls differ from vanilla.
    eq={};modules=set()
    for base in (GAME,ROOT):
        for p in (base/'common/units/equipment').glob('*.txt'):
            for k,o,v in value(parse(read(p)),'equipments',[]):eq[k]=v
        for p in (base/'common/units/equipment/modules').glob('*.txt'):
            for k,o,v in value(parse(read(p)),'equipment_modules',[]):modules.add(k)
    def slots(typ):
        node=eq[typ];parent=value(node,'parent');out=slots(parent) if parent in eq else {}
        current=value(node,'module_slots',[])
        if isinstance(current,list):out.update((k,v) for k,o,v in current)
        return out
    for k,o,v in walk(load('common/scripted_effects/BLV_campaign.txt')):
        if k=='create_equipment_variant':
            typ=value(v,'type');allowed=slots(typ)
            for slot,_,module in value(v,'modules'):assert slot in allowed and (module=='empty' or module in modules),(typ,slot,module)
    for suffix in ('','_legacy'):
        ships=[]
        for fleet in ('atlantic','eastern'):
            tree=load(f'history/units/BLV_campaign_{fleet}{suffix}.txt');ships.extend(v for k,o,v in walk(tree) if k=='ship')
        assert len(ships)==28
        assert len({value(s,'name') for s in ships})==28
    # A secret report is local to Britain; no broadcast of the Unguja finding.
    report=EVENTS['blv_campaign.10'];assert value(value(report,'trigger'),'tag')=='A02'
    assert 'every_country' not in str(report)
    for key in ('excavation','decode','prototype','station'):
        assert 'NOT' not in [k for k,o,v in value(DEC['BLV_'+key],'visible')],key
    sprites={}
    for base in (GAME,ROOT):
        for p in (base/'interface').rglob('*.gfx'):
            for m in re.finditer(r'spriteType\s*=\s*\{\s*name\s*=\s*"?([^"\s]+)"?[^}]*?texturefile\s*=\s*"([^"]+)"',read(p),re.S|re.I):sprites[m[1]]=m[2]
    for focus in focuses.values():
        icon=value(focus,'icon');assert icon in sprites,icon
        assert any((base/sprites[icon]).exists() for base in (ROOT,GAME))
    return focuses

def option(event,index=0):return [v for k,o,v in EVENTS[event] if k=='option'][index]

def regressions(focuses):
    for mtg in (False,True):
        for singapore in (False,True):
            w=World(mtg);w.vars['A02']['WTC_debt']=73;w.flags['A02'].add('WTC_ledger_open')
            if not singapore:w.controller[1021]='A03'
            w.run(FX['BLV_initialize']);assert len(w.loaded)==2 and w.vars['A02']['WTC_debt']==73
            assert ('BLV_campaign_eastern'+('' if mtg else '_legacy') in w.loaded)==singapore
            before=deepcopy((w.loaded,w.vars['A02'],w.fuel));w.run(FX['BLV_initialize']);assert (w.loaded,w.vars['A02'],w.fuel)==before
            assert len(w.designs)==(3 if mtg else 0)
    # Crisis effects disappear after a real recovery and variables remain bounded.
    w=World();w.run(FX['BLV_initialize']);w.vars['A02']['BLV_reserve']=-40;w.vars['A02']['BLV_cohesion']=300
    w.run(FX['BLV_refresh']);assert w.vars['A02']['BLV_reserve']==0 and w.vars['A02']['BLV_cohesion']==100 and 'BLV_supply_crisis_spirit' in w.ideas['A02']
    w.vars['A02']['BLV_reserve']=50;w.run(FX['BLV_refresh']);assert 'BLV_supply_crisis_spirit' not in w.ideas['A02']
    for route in ('admiralty','constitution','crown'):
        w=World();w.run(FX['BLV_choose_'+route]);w.run(FX['BLV_choose_'+('crown' if route!='crown' else 'admiralty')]);assert len([f for f in w.flags['A02'] if f.endswith('_path')])==1
        if route=='constitution':assert w.politics['A02']['ruling_party']=='democratic' and w.politics['A02']['elections_allowed']=='yes'
    w=World();w.flags['A02'].add('SEN_initialized');w.gflags|={'SEN_world_initialized','SEN_tesla_lost'};w.vars['A02']['SEN_science']=72
    w.run(FX['BLV_initialize']);assert w.vars['A02']['SEN_science']==72 and 'SEN_tesla_alive' not in w.gflags
    w=World();w.run(FX['BLV_initialize'])
    for _ in range(60):w.run(FX['BLV_monthly'])
    assert w.vars['A02']['BLV_reserve']==0 and 'BLV_supply_crisis_spirit' in w.ideas['A02']
    # Oil supply ends on war, loss of the oil state, or partner disappearance.
    for scenario in ('valid','war','lost_oil','gone'):
        w=World();w.run(FX['BLV_initialize']);w.flags['A02'].add('BLV_oil_signed')
        if scenario=='war':w.wars.add(frozenset(('A01','A02')))
        if scenario=='lost_oil':w.controller[334]='A03'
        if scenario=='gone':w.tags.remove('A01')
        before=w.fuel['A02'];w.run(FX['BLV_monthly']);assert (w.fuel['A02']>before)==(scenario=='valid')
    # Delayed diplomacy must not grant access after a war or a host change.
    for scenario in ('valid','war','host_changed','tesla_dead'):
        w=World();w.run(FX['BLV_initialize']);w.flags['A02'].add('BLV_license_pending')
        if scenario=='war':w.wars.add(frozenset(('A02','MLT')))
        if scenario=='host_changed':w.flags['MLT'].clear()
        if scenario=='tesla_dead':w.gflags.discard('SEN_tesla_alive')
        w.run(option('blv_campaign.9'),'MLT',root='MLT');assert ('SEN_research_license' in w.flags['A02'])==(scenario=='valid')
    # Genuine Australian independence changes only our existing federal subject.
    for scenario in ('valid','independent','other_overlord','no_federation','war'):
        w=World();w.flags['A07'].add('AUC_commonwealth_proclaimed')
        if scenario=='independent':w.overlord.pop('A07')
        if scenario=='other_overlord':w.overlord['A07']='A03'
        if scenario=='no_federation':w.flags['A07'].clear()
        if scenario=='war':w.wars.add(frozenset(('A02','A07')))
        before=deepcopy(w.overlord);w.run(FX['BLV_recognise_australia'])
        if scenario=='valid':assert 'A07' not in w.overlord
        else:assert before==w.overlord
    # Time projects stay visible while active, consume equipment once and cancel
    # without rewards if the physical site or research access is lost.
    w=World();w.run(FX['BLV_initialize']);w.flags['A02'].add('BLV_arctic_open');w.equipment['A02']['support_equipment']=500;w.vars['A02']['SEN_readiness']=50
    d=DEC['BLV_excavation'];assert w.test(value(d,'available'))
    w.run(value(d,'complete_effect'));assert w.test(value(d,'visible')) and not w.test(value(d,'cancel_trigger')) and w.equipment['A02']['support_equipment']==425
    before=deepcopy(w);w.controller[101]='A03';assert w.test(value(d,'cancel_trigger'));w.run(value(d,'remove_effect'));assert 'SEN_artifact_found' not in w.gflags
    w=before;w.run(value(d,'remove_effect'));assert 'SEN_artifact_found' in w.gflags and 'SEN_artifact_holder' in w.flags['A02']
    w.run(FX['BLV_claim_artifact']);assert w.vars['A02']['SEN_science']==10
    # Custody follows the site's controller and does not delete scientific memory.
    w.vars['A02']['SEN_science']=65;w.controller[101]='A06';w.run(FX['BLV_custody']);assert 'SEN_artifact_holder' in w.flags['A06'] and 'SEN_artifact_holder' not in w.flags['A02'] and w.vars['A02']['SEN_science']==65
    w.gflags.add('SEN_artifact_destroyed');w.controller[101]='A02';w.run(FX['BLV_custody']);assert 'SEN_artifact_holder' not in w.flags['A02']
    # A retained prototype is knowledge; destroying the object does not erase it.
    w=World();w.run(FX['BLV_initialize']);w.flags['A02']|={'SEN_artifact_holder','SEN_research_license','BLV_prototype_open','BLV_prototype_active'};w.gflags.add('SEN_artifact_found');w.sf[101].add('SEN_artifact_site');w.vars['A02']['SEN_science']=65;w.vars['A02']['SEN_security']=50
    w.date=(1899,12,31);assert not w.test(TR['BLV_prototype_requirements'])
    w.date=(1900,1,1);w.run(FX['BLV_finish_prototype']);assert 'SEN_advanced_knowledge' in w.flags['A02']
    w.gflags.add('SEN_artifact_destroyed');w.run(FX['BLV_refresh']);assert 'SEN_advanced_knowledge' in w.flags['A02']
    # Westminster policy affects Australian AI answers but removes no player option.
    aus={value(v,'id'):v for k,o,v in load('events/AUC_campaign.txt') if k=='country_event'}
    def weights(node,w):
        output=[]
        for opt in [v for k,o,v in node if k=='option']:
            assert value(opt,'trigger') is None
            chance=value(opt,'ai_chance');score=float(value(chance,'factor'))
            for k,o,mod in chance:
                if k=='modifier' and w.test([e for e in mod if e[0]!='factor']):score*=float(value(mod,'factor'))
            output.append(score)
        return output
    w=World();w.flags['A02'].add('BLV_dominion_policy');a,b=weights(aus['auc_campaign.1'],w);assert a>0 and b==0
    w.flags['A02']={'BLV_hard_empire'};a,b=weights(aus['auc_campaign.1'],w);assert a==0 and b>0

if __name__=='__main__':
    focuses=static_checks();regressions(focuses)
    print('PASS: 96 focuses; graph, references, bilingual text, documented modifiers, hull slots/modules, 28 ships in both DLC modes, budget, cabinet, delayed diplomacy, Australia, science cancellation and unique custody regressions. No engine playthrough.')
