"""Shipped-definition checks and bounded execution of minor campaign lifecycles."""
from pathlib import Path
from collections import Counter,defaultdict
from copy import deepcopy
import hashlib,json,re
from validate_philippines_rework import parse,value,walk
from minor_campaign_profiles import PROFILES

ROOT=Path(__file__).resolve().parents[1]
GAME=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
def read(path):return path.read_text(encoding='utf-8-sig')
def load(path):return parse(read(ROOT/path))
FX={k:v for file in ('MNR_campaign','MNR_story') for k,o,v in load('common/scripted_effects/'+file+'.txt')}
TR={k:v for k,o,v in load('common/scripted_triggers/MNR_campaign.txt')}
DEC=dict((k,v) for k,o,v in value(load('common/decisions/MNR_campaign.txt'),'MNR_campaign_category'))
EVENTS={value(v,'id'):v for k,o,v in load('events/MNR_campaign.txt') if k=='country_event'}
TAGS=set(PROFILES)|{'A01','A02','A03','A04','A06','A07','A10','ZZZ'}

class World:
    def __init__(self):
        self.tags=set(TAGS);self.flags=defaultdict(set);self.vars=defaultdict(lambda:defaultdict(float))
        self.ideas=defaultdict(set);self.equipment=defaultdict(lambda:defaultdict(float));self.pp=defaultdict(lambda:1000)
        self.capitals={t:p['capital'] for t,p in PROFILES.items()};self.owner={n:t for t,n in self.capitals.items()};self.owner.update({686:'A05',319:'PAZ'})
        self.controller=dict(self.owner);self.wars=set();self.capitulated=set();self.subjects=set();self.factions={}
        self.loaded=[];self.events=[];self.built=[];self.leaders=defaultdict(list);self.retired=Counter();self.politics={};self.slots=Counter();self.goals=[]
        self.date=(1901,1,1)
        self.completed=set();self.mtg=True;self.designs=[]
    def test(self,node,tag,root=None):
        root=root or tag;out=[]
        for k,o,v in node:
            if k in TR:r=self.test(TR[k],tag,root)==(v=='yes')
            elif k=='AND':r=self.test(v,tag,root)
            elif k=='OR':r=any(self.test([e],tag,root) for e in v)
            elif k=='NOT':r=not self.test(v,tag,root)
            elif k in TAGS:r=k in self.tags and self.test(v,k,root)
            elif k=='capital_scope':r=self.test(v,self.capitals[tag],root)
            elif k.isdigit():r=self.test(v,int(k),root)
            elif k=='tag':r=tag==v
            elif k=='exists':r=(tag in self.tags)==(v=='yes')
            elif k=='country_exists':r=v in self.tags
            elif k=='has_country_flag':r=v in self.flags[tag]
            elif k=='has_capitulated':r=(tag in self.capitulated)==(v=='yes')
            elif k=='is_subject':r=(tag in self.subjects)==(v=='yes')
            elif k=='has_war':r=any(tag in w for w in self.wars)==(v=='yes')
            elif k=='has_war_with':r=frozenset((tag,v)) in self.wars
            elif k=='is_in_faction_with':r=tag in self.factions and self.factions[tag]==self.factions.get(v)
            elif k=='is_owned_by':r=self.owner.get(tag)==(root if v=='ROOT' else v)
            elif k=='is_controlled_by':r=self.controller.get(tag)==(root if v=='ROOT' else v)
            elif k=='has_idea':r=v in self.ideas[tag]
            elif k=='has_completed_focus':r=v in self.completed
            elif k=='has_dlc':r=self.mtg
            elif k=='check_variable':
                key,op,num=v[0];n=self.vars[tag][key];r=n>float(num) if op=='>' else n<float(num) if op=='<' else n==float(num)
            elif k=='has_political_power':r=self.pp[tag]>float(v) if o=='>' else self.pp[tag]<float(v)
            elif k=='has_equipment':
                key,op,num=v[0];n=self.equipment[tag][key];r=n>float(num) if op=='>' else n<float(num)
            elif k=='date':r=self.date>tuple(map(int,v.split('.'))) if o=='>' else self.date<tuple(map(int,v.split('.')))
            elif k=='has_character':r=self.retired[v]==0
            else:raise AssertionError(('unmodelled trigger',k))
            out.append(r)
        return all(out)
    def run(self,node,tag,root=None):
        root=root or tag;previous=None
        for k,o,v in node:
            if k in ('limit','trigger','name','ai_chance'):continue
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
            elif k in TAGS:
                if k in self.tags:self.run(v,k,root)
            elif k.isdigit():self.run(v,int(k),root)
            elif k=='capital_scope':self.run(v,self.capitals[tag],root)
            elif k=='hidden_effect':self.run(v,tag,root)
            elif k=='WTC_initialize_effect':
                if 'WTC_ledger_open' not in self.flags[tag]:
                    self.flags[tag].add('WTC_ledger_open');self.vars[tag]['WTC_debt']=65 if tag=='A09' else 10
            elif k=='set_country_flag':self.flags[tag].add(v if isinstance(v,str) else value(v,'flag'))
            elif k=='clr_country_flag':self.flags[tag].discard(v)
            elif k in ('set_variable','add_to_variable','subtract_from_variable'):
                key,_,num=v[0];num=float(num)
                if k=='set_variable':self.vars[tag][key]=num
                else:self.vars[tag][key]+=num if k=='add_to_variable' else -num
            elif k=='clamp_variable':
                key=value(v,'var');self.vars[tag][key]=max(float(value(v,'min')),min(float(value(v,'max')),self.vars[tag][key]))
            elif k in ('add_ideas','remove_ideas'):(self.ideas[tag].add if k=='add_ideas' else self.ideas[tag].discard)(v)
            elif k=='add_timed_idea':self.ideas[tag].add(value(v,'idea'))
            elif k=='load_oob':self.loaded.append((tag,v))
            elif k=='add_political_power':self.pp[tag]+=float(v)
            elif k=='add_equipment_to_stockpile':
                typ=value(v,'type');typ={'infantry_equipment_0':'infantry_equipment','support_equipment_1':'support_equipment'}.get(typ,typ)
                self.equipment[tag][typ]+=float(value(v,'amount'))
            elif k=='country_event':self.events.append((tag,value(v,'id')))
            elif k=='add_building_construction':self.built.append((tag,value(v,'type')))
            elif k=='create_country_leader':self.leaders[tag].append(value(v,'name'))
            elif k=='retire_character':self.retired[v]+=1
            elif k=='set_politics':self.politics[tag]=value(v,'ruling_party')
            elif k=='add_research_slot':self.slots[tag]+=int(v)
            elif k=='create_wargoal':self.goals.append((tag,value(v,'target')))
            elif k=='create_equipment_variant':self.designs.append(value(v,'name'))
            elif k in ('add_stability','add_war_support','army_experience','navy_experience','add_tech_bonus','add_extra_state_shared_building_slots','set_popularities','drop_cosmetic_tag','set_cosmetic_tag','give_military_access','set_technology'):pass
            else:raise AssertionError(('unmodelled effect',k))
    def start(self,key,tag):
        d=DEC[key];assert self.test(value(d,'visible'),tag) and self.test(value(d,'available'),tag),key
        self.pp[tag]-=float(value(d,'cost'));self.run(value(d,'complete_effect'),tag)
    def finish(self,key,tag):
        d=DEC[key]
        self.run(value(d,'cancel_effect') if self.test(value(d,'cancel_trigger'),tag) else value(d,'remove_effect'),tag)

def static():
    paths=[p for folder in ('common','events','history/units') for p in (ROOT/folder).rglob('*.txt') if p.name.startswith('MNR_')]
    trees={p:parse(read(p)) for p in paths}
    docs={k:set(re.findall(r'^## (\w+)\s*$',read(GAME/'documentation'/f'{k}_documentation.md'),re.M)) for k in ('effects','triggers','modifiers')}
    locs={}
    for language in ('russian','english'):
        keys=[]
        for path in list((ROOT/'localisation'/language).glob('MNR_*.yml'))+list((ROOT/'localisation'/language).glob('FSP_*.yml')):
            assert path.read_bytes().startswith(b'\xef\xbb\xbf');keys+=re.findall(r'^\s+([^ :]+):0',read(path),re.M)
        assert len(keys)==len(set(keys));locs[language]=set(keys)
    assert locs['russian']==locs['english'];keys=locs['russian']
    sprites={}
    for base in (GAME,ROOT):
        for path in (base/'interface').rglob('*.gfx'):
            for m in re.finditer(r'spriteType\s*=\s*\{\s*name\s*=\s*"?([^"\s]+)"?[^}]*?texturefile\s*=\s*"([^"]+)"',read(path),re.S|re.I):sprites[m[1]]=m[2]
    def sprite(name):
        assert name in sprites,('sprite',name)
        assert any((base/sprites[name]).exists() for base in (ROOT,GAME)),('texture',name)
    def cond(ns):
        for k,o,v in ns:
            if k in ('AND','OR','NOT','capital_scope') or k in TAGS or k.isdigit():cond(v)
            else:assert k in TR or k in docs['triggers'],('condition',k)
    def effect(ns):
        for k,o,v in ns:
            if k in TAGS or k.isdigit() or k in ('capital_scope','every_country','if','else_if','else','hidden_effect'):
                for a,b,c in v:cond(c) if a=='limit' else effect([(a,b,c)])
            else:assert k in FX or k in docs['effects'] or k=='WTC_initialize_effect',('effect',k)
    assignments=Counter();focuses={}
    for path in (ROOT/'common/national_focus').glob('*.txt'):
        ft=value(parse(read(path)),'focus_tree',[])
        for k,o,v in walk(value(ft,'country',[])):
            if k=='tag' and v in PROFILES:assignments[v]+=1
    assert assignments==Counter({t:1 for t in PROFILES}),assignments
    for tag,p in PROFILES.items():
        ft=value(trees[ROOT/f'common/national_focus/MNR_{tag}.txt'],'focus_tree')
        fs={value(v,'id'):v for k,o,v in ft if k=='focus'};assert len(fs)==23
        focuses.update(fs);pos={k:(int(value(v,'x')),int(value(v,'y'))) for k,v in fs.items()};assert len(set(pos.values()))==23
        for fid,f in fs.items():
            assert fid in keys and fid+'_desc' in keys;sprite(value(f,'icon'));cond(value(f,'available'));effect(value(f,'completion_reward'))
            for k,o,v in f:
                if k in ('prerequisite','mutually_exclusive'):
                    for a,b,target in v:
                        assert target in fs
                        if k=='prerequisite':assert pos[target][1]<pos[fid][1]
                        else:assert any(a=='mutually_exclusive' and value(c,'focus')==fid for a,b,c in fs[target])
        template=trees[ROOT/f'history/units/MNR_{tag}_template.txt'];assert len(template)==1 and template[0][0]=='division_template'
        assert len(value(value(template,'division_template'),'regiments'))==2
    ideas=value(value(trees[ROOT/'common/ideas/MNR_campaign.txt'],'ideas'),'country');ideaids={k for k,o,v in ideas}
    for k,o,v in ideas:
        for mod,o,num in value(v,'modifier'):assert mod in docs['modifiers'] or mod.startswith('production_speed_'),mod
    for tree in trees.values():
        for k,o,v in walk(tree):
            if k in ('title','desc','text','name') and isinstance(v,str) and v.startswith(('MNR_','mnr_campaign.')):assert v in keys,v
            if k.startswith('MNR_') and v=='yes':assert k in FX or k in TR,k
            if k in ('add_ideas','remove_ideas','idea') and isinstance(v,str):assert v in ideaids,v
            if k=='country_event' and isinstance(v,list):assert value(v,'id') in EVENTS,value(v,'id')
            if k=='load_oob':assert (ROOT/f'history/units/{v}.txt').exists(),v
    # Naval orders must match installed hull slots, versions and real coastal provinces.
    eq={};modules=set()
    for base in (GAME,ROOT):
        for path in (base/'common/units/equipment').glob('*.txt'):
            for k,o,v in value(parse(read(path)),'equipments',[]):eq[k]=v
        for path in (base/'common/units/equipment/modules').glob('*.txt'):
            modules.update(k for k,o,v in value(parse(read(path)),'equipment_modules',[]))
    def slots(typ):
        node=eq[typ];parent=value(node,'parent');out=slots(parent) if parent in eq else {}
        current=value(node,'module_slots',[])
        if isinstance(current,list):out.update((k,v) for k,o,v in current)
        return out
    for tree in trees.values():
        for k,o,v in walk(tree):
            if k=='create_equipment_variant':
                allowed=slots(value(v,'type'))
                for slot,o,module in value(v,'modules'):assert slot in allowed and (module=='empty' or module in modules),(slot,module)
    manifest=json.loads(read(ROOT/'tools/minor_campaign_manifest.json'))
    coast={int(row.split(';')[0]) for row in read(ROOT/'map/definition.csv').splitlines() if len(row.split(';'))>5 and row.split(';')[5]=='true'}
    for tag,p in manifest.items():
        if 'escort_port' not in p:continue
        assert p['escort_port'] in coast
        for suffix in ('','_legacy'):
            ns=trees[ROOT/f'history/units/MNR_{tag}_escorts{suffix}.txt'];ships=[v for k,o,v in walk(ns) if k=='ship'];assert len(ships)==2
            assert all(value(v,'definition')=='destroyer' for v in ships)
            if not suffix:assert all(value(value(value(v,'equipment'),'ship_hull_light_1'),'version_name')=='"Local Escort '+tag+'"' for v in ships)
    for k,v in TR.items():cond(v)
    for k,v in FX.items():effect(v)
    for key,d in DEC.items():
        assert key in keys and key+'_desc' in keys;sprite('GFX_decision_'+value(d,'icon'))
        cond(value(d,'available'));cond(value(d,'visible'));effect(value(d,'complete_effect'))
        if value(d,'days_remove'):
            assert value(d,'cancel_if_not_visible')=='yes';cond(value(d,'cancel_trigger'));effect(value(d,'remove_effect'));effect(value(d,'cancel_effect'))
            assert not any(a=='has_country_flag' and c=='MNR_project_active' for a,b,c in walk(value(d,'visible')))
    for eid,e in EVENTS.items():
        cond(value(e,'trigger'))
        options=[v for k,o,v in e if k=='option'];assert any(value(v,'trigger') is None for v in options),eid
        for opt in options:
            cond(value(opt,'trigger',[]));effect([(k,o,v) for k,o,v in opt if k not in ('name','trigger','ai_chance')])
    forbidden={'annex_country','transfer_state','set_autonomy','declare_war_on','add_to_faction','set_state_controller'}
    assert not forbidden & {k for tree in trees.values() for k,o,v in walk(tree)}
    return focuses,len(paths),len(keys)

def regressions(focuses):
    cases=0
    for t,p in PROFILES.items():
        for route in ('civic','command'):
            w=World();w.flags[t].add('WTC_ledger_open');w.vars[t]['WTC_debt']=73
            w.run(FX['MNR_initialize'],t);w.vars[t]['MNR_reserve']=72;w.vars[t]['MNR_mandate']=69
            w.run(FX['MNR_initialize'],t);assert w.vars[t]['WTC_debt']==73 and w.vars[t]['MNR_reserve']==72
            if t=='MLT':w.vars[t]['SEN_science']=37;w.run(FX['MNR_initialize'],t);assert w.vars[t]['SEN_science']==37
            for fid,f in focuses.items():
                if not fid.startswith('MNR_'+t+'_') or fid.endswith('_goal'):continue
                if any(fid.endswith('_'+s) for s in ('command','command_law','command_settlement') if route=='civic'):continue
                if any(fid.endswith('_'+s) for s in ('civic','civic_law','civic_settlement') if route=='command'):continue
                if route=='civic' and fid.endswith(('_economy_contracts','_defence_mobile')):continue
                if route=='command' and fid.endswith(('_economy_local','_defence_garrison')):continue
                w.run(value(f,'completion_reward'),t)
            assert len(w.built)==2 and len(w.loaded)==1 and w.equipment[t]['infantry_equipment']==200
            for eq in ('infantry_equipment','support_equipment','convoy_1'):w.equipment[t][eq]+=500
            key=f'MNR_{t}_project';reserve=w.vars[t]['MNR_reserve']
            for n in range(3):
                w.start(key,t);assert not w.test(value(DEC[key],'available'),t);assert w.test(value(DEC[key],'visible'),t)
                assert not w.test(value(DEC[key],'cancel_trigger'),t)
                w.finish(key,t);assert w.vars[t]['MNR_progress']==n+1
                progress=w.vars[t]['MNR_progress'];w.run(value(DEC[key],'remove_effect'),t);assert w.vars[t]['MNR_progress']==progress
            assert not w.test(value(DEC[key],'available'),t)
            assert sum(eid==f'mnr_campaign.{300+list(PROFILES).index(t)}' for target,eid in w.events)==1
            w.vars[t]['MNR_reserve']=90;w.vars[t]['MNR_mandate']=90;w.flags[t].add('MNR_insured')
            if t=='A09':w.vars[t]['WTC_debt']=40
            if t=='PHW':w.run(FX['MNR_hawaii_succession'],t)
            f=focuses[f'MNR_{t}_goal'];assert w.test(value(f,'available'),t),(t,route)
            w.run(value(f,'completion_reward'),t);w.run(value(f,'completion_reward'),t);assert w.slots[t]==1
            # Losing the capital cancels a paid operation without its completion reward.
            w.vars[t]['MNR_progress']=0;w.start(key,t);before=deepcopy(dict(w.vars[t]));w.controller[p['capital']]='ZZZ'
            assert w.test(value(DEC[key],'cancel_trigger'),t);w.finish(key,t)
            assert dict(w.vars[t])==before and 'MNR_project_active' not in w.flags[t]
            # Capital regained permits a fresh project; occupation never creates a factory.
            count=len(w.built);w.run(value(focuses[f'MNR_{t}_economy1'],'completion_reward'),t);assert len(w.built)==count
            cases+=1
    for t,p in PROFILES.items():
        for b in p['partners']:
            w=World();w.run(FX['MNR_initialize'],t);w.flags[t].add('MNR_contacts')
            key=f'MNR_{t}_offer_{b}';w.start(key,t)
            eid=next(e for target,e in w.events if target==b);opts=[v for k,o,v in EVENTS[eid] if k=='option']
            assert w.test(value(opts[0],'trigger'),b);m=w.vars[t]['MNR_mandate'];w.run(opts[0],b)
            assert w.test(TR['MNR_has_live_partner'],t) and w.test(TR['MNR_has_live_partner'],b)
            w.run(opts[0],b);assert w.vars[t]['MNR_mandate']==m+5
            # Partner wartime invalidation persists even after peace.
            w.wars.add(frozenset((t,b)));w.run(FX['MNR_refresh_network'],t);w.run(FX['MNR_refresh_network'],b)
            assert 'MNR_network_service' not in w.ideas[t] and 'MNR_pact_'+t not in w.flags[b]
            w.wars.clear();w.run(FX['MNR_refresh_network'],t);assert not w.test(TR['MNR_has_live_partner'],t)
            # Expired offers, disappearance and surrender cannot accept stale promises.
            for mode in ('expired','gone','capitulated','war'):
                z=World();z.run(FX['MNR_initialize'],t);z.flags[t].add('MNR_contacts');z.start(key,t)
                if mode=='expired':z.flags[t].discard('MNR_pending_'+b)
                if mode=='gone':z.tags.discard(t)
                if mode=='capitulated':z.capitulated.add(b)
                if mode=='war':z.wars.add(frozenset((t,b)))
                assert not z.test(value(opts[0],'trigger'),b);z.run(opts[0],b);assert not z.test(TR['MNR_has_live_partner'],b)
                cases+=1
            cases+=1
    for route in ('civic','command',None):
        w=World();w.flags['PHW'].update({'MNR_'+route} if route else set());w.date=(1894,4,29)
        w.run(FX['MNR_hawaii_succession'],'PHW');assert not w.retired
        w.date=(1894,4,30);w.run(FX['MNR_hawaii_succession'],'PHW');leaders=list(w.leaders['PHW']);assert w.retired['PHW_canon_leader']==1
        for n in range(4):w.run(FX['MNR_hawaii_succession'],'PHW');w.run(FX['MNR_hawaii_constitutional_review'],'PHW')
        w.date=(1895,2,20);w.run(FX['MNR_hawaii_constitutional_review'],'PHW');w.run(FX['MNR_hawaii_constitutional_review'],'PHW')
        assert w.leaders['PHW']==leaders and w.retired['PHW_canon_leader']==1
        cases+=1
    # Several live partners retain the service until the last agreement ends.
    w=World();w.run(FX['MNR_initialize'],'A05');w.flags['A05'].update({'MNR_contacts','MNR_pact_PHW','MNR_pact_PCF'});w.flags['PHW'].add('MNR_pact_A05');w.flags['PCF'].add('MNR_pact_A05')
    w.flags['PHW'].clear();w.run(FX['MNR_refresh_network'],'A05');assert 'MNR_network_service' in w.ideas['A05']
    w.tags.discard('PCF');w.run(FX['MNR_refresh_network'],'A05');assert 'MNR_network_service' not in w.ideas['A05']
    cases+=1
    # Reciprocal simultaneous offers and renewals cannot duplicate mandate rewards.
    w=World()
    for tag in ('A05','PCF'):w.run(FX['MNR_initialize'],tag);w.flags[tag].add('MNR_contacts')
    w.start('MNR_A05_offer_PCF','A05');w.start('MNR_PCF_offer_A05','PCF')
    first=w.events[-2][1];second=w.events[-1][1]
    opt=lambda eid:[v for k,o,v in EVENTS[eid] if k=='option'][0]
    w.run(opt(first),'PCF');assert not w.test(value(opt(second),'trigger'),'A05');w.run(opt(second),'A05')
    assert w.vars['A05']['MNR_mandate']==50 and w.vars['PCF']['MNR_mandate']==45
    for tag,other in [('A05','PCF'),('PCF','A05')]:
        w.flags[tag].discard('MNR_pact_'+other);w.flags[tag].discard('MNR_pending_'+other);w.flags[tag].discard('MNR_cooldown_'+other)
    w.start('MNR_A05_offer_PCF','A05');w.run(opt(first),'PCF');assert w.vars['A05']['MNR_mandate']==50
    cases+=1
    # Recovery remains affordable and available after bad crisis choices or long wars.
    for tag in PROFILES:
        w=World();w.run(FX['MNR_initialize'],tag);w.vars[tag]['MNR_reserve']=0;w.vars[tag]['MNR_mandate']=0
        w.run(FX['MNR_refresh'],tag);assert {'MNR_shortages','MNR_discontent'}<=w.ideas[tag]
        w.start('MNR_replenish',tag);w.start('MNR_local_hearing',tag)
        assert w.vars[tag]['MNR_reserve']==15 and w.vars[tag]['MNR_mandate']==8
        assert not w.test(value(DEC['MNR_replenish'],'available'),tag)
        w.wars.add(frozenset((tag,'ZZZ')));w.run(FX['MNR_monthly'],tag);assert w.vars[tag]['MNR_reserve']==14
        w.vars[tag]['MNR_reserve']=-2;w.vars[tag]['MNR_mandate']=200;w.run(FX['MNR_refresh'],tag)
        assert w.vars[tag]['MNR_reserve']==0 and w.vars[tag]['MNR_mandate']==100
        cases+=1
    # Major budgets and the Tesla host/custody state are outside the minor initializer.
    w=World();w.run(FX['MNR_initialize'],'A02');assert not w.vars['A02'] and not w.flags['A02']
    for t in ('A08','PSL'):
        w=World();w.subjects.add(t);w.run(value(focuses[f'MNR_{t}_command_settlement'],'completion_reward'),t);assert not w.goals
    cases+=3
    for tag,p in json.loads(read(ROOT/'tools/minor_campaign_manifest.json')).items():
        if 'escort_port' not in p:continue
        for mtg in (False,True):
            for mode in ('finish','occupied','capitulated','moved_capital'):
                w=World();w.mtg=mtg;w.run(FX['MNR_initialize'],tag);w.vars[tag]['MNR_progress']=1;w.vars[tag]['MNR_reserve']=80
                w.completed.add(f'MNR_{tag}_defence2');w.equipment[tag]['support_equipment']=100
                key=f'MNR_{tag}_escort_order';w.start(key,tag)
                if mode=='occupied':w.controller[p['capital']]='ZZZ'
                if mode=='capitulated':w.capitulated.add(tag)
                if mode=='moved_capital':w.capitals[tag]=686;w.owner[686]=tag;w.controller[686]=tag;w.controller[p['capital']]='ZZZ'
                w.finish(key,tag)
                assert len(w.loaded)==(1 if mode=='finish' else 0)
                assert 'MNR_yard_active' not in w.flags[tag]
                if mode=='finish':
                    before=len(w.built);w.run(FX[f'MNR_{tag}_commission_escorts'],tag);assert len(w.built)==before and len(w.loaded)==1
                    assert w.loaded[0][1]==f'MNR_{tag}_escorts'+('' if mtg else '_legacy')
                cases+=1
    return cases

def main():
    focuses,files,keys=static();cases=regressions(focuses)
    paths=[p for folder in ('common','events','history/units','localisation') for p in (ROOT/folder).rglob('*') if p.is_file() and p.name.startswith('MNR_')]
    hashes={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    from build_minor_campaigns import main as build
    build();assert all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in hashes.items()),'Builder must be idempotent'
    report=dict(countries=len(PROFILES),focuses=len(focuses),events=len(EVENTS),decisions=len(DEC),files=files,bilingual_keys=keys,lifecycle_cases=cases,limitations=['No HOI4 engine launch or balance playthrough.'])
    (ROOT/'tools/minor_campaign_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {len(PROFILES)} countries, {len(focuses)} focuses, {len(EVENTS)} events, {len(DEC)} decisions; {cases} bounded lifecycle cases; native references, bilingual text, unique selection and idempotent rebuild. No game launch.')

if __name__=='__main__':main()
