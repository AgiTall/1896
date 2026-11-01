"""Parse shipped content and execute consent/annexation guards in a bounded model."""
from pathlib import Path
from collections import defaultdict
from copy import deepcopy
import json,re
from validate_philippines_rework import parse,value,walk
ROOT=Path(__file__).resolve().parents[1]
def read(p):return (ROOT/p).read_text(encoding='utf-8-sig')
TRIGGERS=dict((k,v) for k,o,v in parse(read('common/scripted_triggers/AUC_campaign.txt')))
EFFECTS=dict((k,v) for k,o,v in parse(read('common/scripted_effects/AUC_campaign.txt')))
COLONIES=json.loads(read('tools/australia_1893_manifest.json'))
TAGS=set(COLONIES)|{'A02','A03','A01','A10','ZZZ'}

class World:
    def __init__(self):
        self.exists=set(TAGS);self.overlord={t:'A02' for t in COLONIES}
        self.flags=defaultdict(set);self.wars=set();self.factions={};self.capitulated=set()
        self.owner={s:t for t,c in COLONIES.items() for s in c['states']};self.controller=dict(self.owner)
        self.cores=defaultdict(set);self.annexed=[];self.calls=[];self.queue=[]
    def test(self,node,tag,root='A07'):
        results=[]
        for k,o,v in node:
            if k in TRIGGERS:r=self.test(TRIGGERS[k],tag,root)==(v=='yes')
            elif k=='AND':r=self.test(v,tag,root)
            elif k=='OR':r=any(self.test([entry],tag,root) for entry in v)
            elif k=='NOT':r=not self.test(v,tag,root)
            elif k=='count_triggers':
                amount=next(entry for entry in v if entry[0]=='amount');count=sum(self.test([entry],tag,root) for entry in v if entry[0]!='amount')
                r=count>int(amount[2]) if amount[1]=='>' else count==int(amount[2])
            elif k in TAGS:r=k in self.exists and self.test(v,k,root)
            elif k.isdigit():r=self.test(v,int(k),root)
            elif k=='tag':r=tag==v
            elif k=='country_exists':r=v in self.exists
            elif k=='has_country_flag':r=v in self.flags[tag]
            elif k=='has_war':r=any(tag in w for w in self.wars)==(v=='yes')
            elif k=='has_war_with':r=frozenset((tag,v)) in self.wars
            elif k=='has_capitulated':r=(tag in self.capitulated)==(v=='yes')
            elif k=='is_subject':r=(tag in self.overlord)==(v=='yes')
            elif k=='is_subject_of':r=self.overlord.get(tag)==v
            elif k=='is_in_faction':r=(tag in self.factions)==(v=='yes')
            elif k=='is_in_faction_with':r=tag in self.factions and self.factions.get(tag)==self.factions.get(v)
            elif k=='is_owned_by':r=self.owner.get(tag)==(root if v=='ROOT' else v)
            elif k=='is_controlled_by':r=self.controller.get(tag)==(root if v=='ROOT' else v)
            elif k=='owns_state':r=self.owner.get(int(v))==tag
            elif k=='all_owned_state':r=all(self.test(v,s,root) for s,owner in self.owner.items() if owner==tag)
            else:raise AssertionError(('unsupported test condition',k))
            results.append(r)
        return all(results)
    def run(self,node,tag='A07',root='A07'):
        previous=None
        for k,o,v in node:
            if k=='limit':continue
            if k=='if':
                previous=self.test(value(v,'limit'),tag,root)
                if previous:self.run(v,tag,root)
            elif k=='else':
                if previous is False:self.run(v,tag,root)
            elif k in EFFECTS:self.run(EFFECTS[k],tag,root)
            elif k in TAGS:
                if k in self.exists:self.run(v,k,root)
            elif k.isdigit():self.run(v,int(k),root)
            elif k=='set_country_flag':self.flags[tag].add(v if isinstance(v,str) else value(v,'flag'))
            elif k=='clr_country_flag':self.flags[tag].discard(v)
            elif k=='set_autonomy':
                assert tag=='A02' and value(v,'autonomy_state')=='autonomy_free'
                self.overlord.pop(value(v,'target'),None)
            elif k=='annex_country':
                target=value(v,'target');assert target in self.exists and target not in self.overlord
                assert value(v,'transfer_troops')=='yes';self.annexed.append(target);self.exists.remove(target)
                for s,owner in list(self.owner.items()):
                    if owner==target:self.owner[s]=tag;self.controller[s]=tag
            elif k=='add_core_of':self.cores[tag].add(root if v=='ROOT' else v)
            elif k=='leave_faction':self.factions.pop(tag,None)
            elif k=='declare_war_on':self.wars.add(frozenset((tag,value(v,'target'))))
            elif k=='white_peace':self.wars.discard(frozenset((tag,value(v,'tag'))))
            elif k=='country_event':self.queue.append((tag,value(v,'id')))
            elif k in ('set_cosmetic_tag','add_ideas','give_military_access'):self.calls.append((tag,k,v))
            else:raise AssertionError(('unsupported test effect',k))

def validate_files():
    paths=[p for folder in ('common/national_focus','common/scripted_effects','common/scripted_triggers','common/ideas','common/decisions','common/decisions/categories','common/characters','events','history/units') for p in (ROOT/folder).glob('AUC_campaign*txt')]
    trees={p:parse(p.read_text(encoding='utf-8-sig')) for p in paths}
    locales={}
    for lang in ('russian','english'):
        p=ROOT/f'localisation/{lang}/AUC_campaign_l_{lang}.yml';assert p.read_bytes().startswith(b'\xef\xbb\xbf')
        entries=re.findall(r'^\s+(\w[\w.]*):0',p.read_text(encoding='utf-8-sig'),re.M)
        assert len(entries)==len(set(entries));locales[lang]=set(entries)
        locales[lang].update(re.findall(r'^\s+(\w[\w.]*):0',(ROOT/f'localisation/{lang}/FSP_focus_shapes_l_{lang}.yml').read_text(encoding='utf-8-sig'),re.M))
    assert locales['russian']==locales['english'];keys=locales['russian']
    allfocus={};total=0
    for tag in COLONIES:
        tree=value(trees[ROOT/f'common/national_focus/AUC_campaign_{tag}.txt'],'focus_tree')
        sel=value(value(tree,'country'),'modifier');assert value(sel,'tag')==tag and value(sel,'add')=='200'
        focuses={value(v,'id'):v for k,o,v in tree if k=='focus'};xy=set()
        assert len(focuses)==(36 if tag=='A07' else 27)
        for fid,node in focuses.items():
            assert fid not in allfocus;allfocus[fid]=node
            assert fid in keys and fid+'_desc' in keys
            pos=(value(node,'x'),value(node,'y'));assert pos not in xy,(tag,pos);xy.add(pos)
            for k,o,v in node:
                if k in ('prerequisite','mutually_exclusive'):
                    for _,_,parent in v:
                        assert parent in focuses,(fid,parent)
                        if k=='prerequisite':assert int(value(focuses[parent],'y'))<int(value(node,'y'))
                        else:assert fid in [p for a,b,x in focuses[parent] if a=='mutually_exclusive' for _,_,p in x]
        total+=len(focuses)
    eventnodes=[v for k,o,v in trees[ROOT/'events/AUC_campaign.txt'] if k=='country_event']
    events={value(v,'id'):v for v in eventnodes};assert len(events)==len(eventnodes)==12
    idea_nodes=value(value(trees[ROOT/'common/ideas/AUC_campaign.txt'],'ideas'),'country')
    ideas={k for k,o,v in idea_nodes};assert len(ideas)==14
    doc=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md')
    mods=set(re.findall(r'^## (\w+)\s*$',doc.read_text(encoding='utf-8-sig'),re.M))
    for k,o,node in idea_nodes:
        assert k in keys and k+'_desc' in keys
        for name,_,_ in value(node,'modifier'):assert name in mods or name.startswith('production_speed_'),name
    for tree in trees.values():
        for k,o,v in walk(tree):
            if k in ('title','desc','text','name','custom_effect_tooltip') and isinstance(v,str) and v.startswith(('auc_campaign.','AUC_')):assert v in keys,v
            if k in ('add_ideas','remove_ideas','idea') and isinstance(v,str) and v.startswith('AUC_'):assert v in ideas,v
            if k.startswith('AUC_') and v=='yes':assert k in EFFECTS or k in TRIGGERS,k
            if k=='country_event' and isinstance(v,list):assert value(v,'id') in events
    # Generated IDs must be globally unique, including the older WTN trees.
    allids=[]
    for p in (ROOT/'common/national_focus').glob('*.txt'):
        for k,o,v in walk(parse(p.read_text(encoding='utf-8-sig'))):
            if k=='focus' and isinstance(v,list):
                fid=value(v,'id')
                if fid:allids.append(fid)
    assert all(allids.count(k)==1 for k in allfocus)
    return events,total

def regression(events):
    # Local vote plus metropolitan permission; approvals of 3–5 also pass.
    for count in (0,1,2,3,5):
        w=World();w.flags['A07'].add('AUC_british_charter')
        for t in list(COLONIES)[1:1+count]:w.flags[t].add('AUC_join_authorized');w.flags['A07'].add('AUC_vote_'+t)
        w.run(EFFECTS['AUC_found_commonwealth'])
        assert len(w.annexed)==(count if count>=2 else 0),(count,w.annexed)
        if count>=2:
            prior=list(w.annexed);w.run(EFFECTS['AUC_found_commonwealth']);assert w.annexed==prior
    base=World();base.flags['A07']|={'AUC_commonwealth_proclaimed','AUC_british_charter','AUC_vote_AVC'};base.flags['AVC'].add('AUC_join_authorized')
    good=deepcopy(base);good.run(EFFECTS['AUC_integrate_AVC']);assert good.annexed==['AVC'] and good.owner[517]=='A07'
    for scenario in ('refused','new_overlord','colony_war','sydney_war','capitulation','foreign_faction','extinct','no_charter','no_local_consent','third_party_state'):
        w=deepcopy(base)
        if scenario=='refused':w.flags['A07'].discard('AUC_vote_AVC')
        elif scenario=='new_overlord':w.overlord['AVC']='A03'
        elif scenario=='colony_war':w.wars.add(frozenset(('AVC','A03')))
        elif scenario=='sydney_war':w.wars.add(frozenset(('A07','A03')))
        elif scenario=='capitulation':w.capitulated.add('AVC')
        elif scenario=='foreign_faction':w.factions['AVC']='foreign'
        elif scenario=='extinct':w.exists.remove('AVC')
        elif scenario=='no_charter':w.overlord.pop('A07');w.flags['A07'].discard('AUC_british_charter')
        elif scenario=='no_local_consent':w.flags['AVC'].clear()
        elif scenario=='third_party_state':w.owner[517]='ZZZ';w.controller[517]='ZZZ'
        w.run(EFFECTS['AUC_integrate_AVC'])
        if scenario=='third_party_state':assert w.owner[517]=='ZZZ' and 'A07' not in w.cores[517]
        else:assert not w.annexed,scenario
    # Independent participants can federate; British subjects need a charter.
    w=World();w.overlord.clear()
    for t in ('AVC','ATA'):w.flags['A07'].add('AUC_vote_'+t);w.flags[t].add('AUC_join_authorized')
    w.run(EFFECTS['AUC_found_commonwealth']);assert set(w.annexed)=={'AVC','ATA'}
    w=deepcopy(base);w.overlord.pop('A07');w.factions={'A02':'british','AVC':'british'}
    w.run(EFFECTS['AUC_integrate_AVC']);assert w.annexed==['AVC'] and 'AVC' not in w.factions
    # Refused independence causes a genuine war only after a deliberate break.
    w=World();w.flags['A07'].add('AUC_sovereignty_refused');w.factions={'A07':'british','A02':'british'}
    w.run(EFFECTS['AUC_independence_war']);assert 'A07' not in w.overlord and 'A07' not in w.factions and frozenset(('A07','A02')) in w.wars
    for hostile in ('A03',None):
        w=World();w.flags['A07'].add('AUC_sovereignty_refused')
        if hostile:w.overlord['A07']=hostile
        else:w.overlord.pop('A07')
        w.run(EFFECTS['AUC_independence_war']);assert not w.wars
    # A queued local vote cannot authorise annexation after subjugation by Japan.
    option=next(v for k,o,v in events['auc_campaign.10'] if k=='option')
    w=World();w.flags['A07'].add('AUC_referendums_open');w.overlord['AVC']='A03'
    w.run([e for e in option if e[0] not in ('name','ai_chance')],'AVC')
    assert 'AUC_join_authorized' not in w.flags['AVC']
    # The armistice requires real survival time and control of owned territory.
    w=World();w.overlord.pop('A07');w.wars.add(frozenset(('A07','A02')));w.flags['A07'].add('AUC_independence_war_started')
    trigger=value(events['auc_campaign.5'],'trigger')
    assert w.test(trigger,'A02',root='A02')
    w.flags['A07'].add('AUC_independence_opening');assert not w.test(trigger,'A02',root='A02');w.flags['A07'].clear();w.flags['A07'].add('AUC_independence_war_started')
    w.controller[285]='A02';assert not w.test(trigger,'A02',root='A02');w.controller[285]='A07'
    option=next(v for k,o,v in events['auc_campaign.5'] if k=='option')
    w.run([e for e in option if e[0] not in ('name','ai_chance')],'A02',root='A02')
    assert not w.wars and 'AUC_british_charter' in w.flags['A07']

if __name__=='__main__':
    events,total=validate_files();regression(events)
    print(f'PASS: six trees, {total} focuses, 12 events, 14 spirits, graph/layout/reference checks, documented modifiers and consent/sovereignty/armistice regression scenarios. No engine playthrough.')
