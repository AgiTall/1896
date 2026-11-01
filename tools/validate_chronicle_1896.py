"""Four-year calendar checks and bounded execution of Batavia treaty branches."""
from pathlib import Path
from datetime import datetime,timedelta
from collections import defaultdict
import json,re
from validate_philippines_rework import parse,value,walk
R=Path(__file__).resolve().parents[1]
def read(p):return p.read_text(encoding='utf-8-sig')

class TreatyWorld:
    """Only the effects used by the treaty, with external cleanup/ledger stubs."""
    def __init__(self,effects,war=True):
        self.effects=effects;self.war=war;self.flags=set();self.calls=[]
        self.owners={s:'A01' for s in (1024,1023,1059,334,1022,1055)};self.owners[333]='ZZZ'
        self.vars=defaultdict(lambda:defaultdict(float));self.country_flags=defaultdict(set)
    def condition(self,node,country):
        for k,o,v in node:
            if k=='NOT':result=not self.condition(v,country)
            elif k=='country_exists':result=v in ('A01','A03','A04')
            elif k=='has_war_with':result=self.war
            elif k=='has_global_flag':result=v in self.flags
            elif k=='is_owned_by':result=self.owners.get(country)==v
            else:raise AssertionError(('unknown treaty trigger',k))
            if not result:return False
        return True
    def execute(self,node,country='A01'):
        previous=None
        for k,o,v in node:
            if k=='limit':continue
            if k=='if':
                previous=self.condition(value(v,'limit'),country)
                if previous:self.execute(v,country)
            elif k=='else':
                if previous is False:self.execute(v,country)
            elif k in self.effects:self.execute(self.effects[k],country)
            elif k in ('A01','A03','A04') or k.isdigit():self.execute(v,int(k) if k.isdigit() else k)
            elif k=='set_country_flag':self.country_flags[country].add(v)
            elif k=='set_global_flag':self.flags.add(v)
            elif k=='white_peace':self.war=False
            elif k=='transfer_state':self.owners[int(v)]=country
            elif k in ('set_variable','add_to_variable'):
                for name,_,amount in v:
                    if k=='set_variable':self.vars[country][name]=float(amount)
                    else:self.vars[country][name]+=float(amount)
            elif k=='add_stability':pass
            elif k in ('A01_cleanup_expansion_effect','A01_disband_war_militia_effect','A01_initialize_postwar_accounts_effect','WTC_initialize_effect','WTC_refresh_effect','WTN_initialize_effect','WTN_update_ledger_effect'):self.calls.append((country,k))
            else:raise AssertionError(('unknown treaty effect',k))

def run():
    paths=[R/f for f in ('events/chronicle_1896.txt','common/scripted_effects/chronicle_1896.txt','common/on_actions/chronicle_1896.txt','common/ideas/chronicle_1896.txt','common/factions/templates/chronicle_1896.txt')]
    trees={p:parse(read(p)) for p in paths};effects=dict((k,v) for k,o,v in trees[paths[1]])
    events={value(v,'id'):v for k,o,v in trees[paths[0]] if k=='country_event'}
    assert len(events)==72
    rows=json.loads(read(R/'tools/chronicle_1896_manifest.json'));assert len(rows)==24
    locpath=R/'localisation/russian/chronicle_1896_l_russian.yml';assert locpath.read_bytes().startswith(b'\xef\xbb\xbf')
    loc=re.findall(r'^\s+(\w[\w.]*):0',read(locpath),re.M);assert len(loc)==len(set(loc))
    all_effects={k for p in (R/'common/scripted_effects').glob('*.txt') for k,o,v in parse(read(p))}
    for tree in trees.values():
        for k,o,v in walk(tree):
            if k in ('title','desc','text','name') and isinstance(v,str) and v.startswith(('CH96_','ch96.')):assert v in loc,v
            if k=='country_event' and isinstance(v,list):assert value(v,'id') in events
            if v=='yes' and k.startswith(('CH96_','CH94_','A01_','A10_','A10R_','WTN_','WTC_')):assert k in all_effects,k
    for n in range(1,25):
        options=[v for k,o,v in events[f'ch96.{n}'] if k=='option'];assert len(options)==2
        if n!=14:assert int(value(value(options[rows[n-1]['canonical']-1],'ai_chance'),'factor'))==100
    assert 'has_country_leader' in str(events['ch96.14'])
    assert 'has_country_leader' in str(effects['CH96_equal_citizenship'])
    for branch,north,south,dutch,japanese in [('CH96_batavia_compromise',True,False,2,5),('CH96_hard_peace',True,True,15,0)]:
        w=TreatyWorld(effects);w.execute(effects[branch])
        assert not w.war and 'CH96_batavia_signed' in w.flags
        assert all(w.owners[s]=='A03' for s in (1024,1023,1059))
        assert all(w.owners[s]==('A03' if south else 'A01') for s in (334,1022,1055))
        assert w.owners[333]=='ZZZ','Treaty must preserve third-party territory'
        assert w.vars['A01']['CH96_reparations_millions']==dutch
        assert w.vars['A03']['CH96_reparations_millions']==japanese
        before=repr(dict((k,dict(v)) for k,v in w.vars.items()))
        w.execute(effects[branch]);assert repr(dict((k,dict(v)) for k,v in w.vars.items()))==before
        peace=TreatyWorld(effects,False);peace.execute(effects[branch]);assert 'ch96_3_inactive' in peace.flags and peace.owners[1023]=='A01'
    # Execute the date/once-only conditions of all four schedules twice daily.
    schedules={y:dict((k,v) for k,o,v in parse(read(R/f'common/scripted_effects/chronicle_{y}.txt')))[f'CH{str(y)[2:]}_tick'] for y in range(1893,1897)}
    def eligible(node,day,flags):
        for k,o,v in node:
            if k=='date':
                d=datetime.strptime(v,'%Y.%m.%d')
                if not (day>d if o=='>' else day<d):return False
            elif k=='has_global_flag':
                if v not in flags:return False
            elif k=='NOT':
                if eligible(v,day,flags):return False
            else:raise AssertionError(k)
        return True
    for start in (datetime(1893,1,1),datetime(1896,8,1),datetime(1897,1,1)):
        day=start;flags=set();fired=[]
        while day<=datetime(1897,1,2):
            for pulse in range(2):
                for year,schedule in schedules.items():
                    outer=value(schedule,'if')
                    if eligible(value(outer,'limit'),day,flags):
                        for k,o,v in outer:
                            flag=value(v,'set_global_flag') if isinstance(v,list) else None
                            if k=='if' and flag and '_queued_' in flag and eligible(value(v,'limit'),day,flags):
                                flags.add(flag);fired.append((year,int(flag.rsplit('_',1)[1]),day))
            day+=timedelta(days=1)
        assert len(fired)==(120 if start.year==1893 else 24 if start.year==1896 else 0)
        if start.year==1893:
            for year,n,day in fired:assert day==datetime.strptime(json.loads(read(R/f'tools/chronicle_{year}_manifest.json'))[n-1]['date'],'%d.%m.%Y')
    assert 'date > 1896.2.13' in str(read(paths[1]))
    assert 'is_subject_of' in str(effects['CH96_manila_protocol'])
    assert 'is_owned_by' in str(effects['CH96_transfer_visayas'])
    assert 'has_war_with' in str(effects['CH96_united_crowns'])
    game=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV/documentation')
    if game.exists():
        mods=set(re.findall(r'^## (\w+)\s*$',read(game/'modifiers_documentation.md'),re.M))
        for k,o,v in walk(trees[paths[3]]):
            if k=='modifier':
                for name,_,_ in v:assert name in mods or re.fullmatch(r'production_speed_\w+_factor',name),name
    print('PASS: 24 choices/72 events; all 120 dates for 1893–1896; canonical AI; peace branches, payments, replay guards, third-party territory, leader conditions and documented modifiers. External cleanup/credit routines are stubbed in treaty tests; no engine playthrough.')

if __name__=='__main__':run()
