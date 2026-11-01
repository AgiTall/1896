"""Exercise political outcomes, election changes and foreign ownership boundaries."""
from pathlib import Path
import re,json,copy
from PIL import Image
from add_canon_countries import parse,value
R=Path(__file__).resolve().parents[1]
G=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
def read(p):return (R/p).read_text(encoding='utf-8-sig')
def val(n,k,default=None):return next((v for a,o,v in n if a==k),default)
focuses={value(n,'id'):n for k,o,n in value(parse(read('common/national_focus/a01_focus.txt')),'focus_tree') if k=='focus'}
effects={k:n for k,o,n in parse(read('common/scripted_effects/A01_royal_story.txt'))}
events={value(n,'id'):n for k,o,n in parse(read('events/A01_royal_story.txt')) if k=='country_event'}
decisions={k:n for cat,o,nodes in parse(read('common/decisions/A01_royal_story.txt')) for k,o,n in nodes}
manifest=json.loads(read('tools/royal_story_manifest.json'))
class Model:
    def __init__(self):
        self.flags=set();self.variables={};self.ideas=set();self.missions=set();self.retired=set();self.bop=0
        self.owners={1055:'A01',334:'A01',1022:'A01',1050:'A01',1023:'A03',1024:'A03'}
        self.exists={'A01','A03'};self.subjects={};self.events=[];self.pp=300;self.stability=0.6;self.completed=set()
    def cond(self,n,scope='A01'):
        def cmp(a,op,b):return {'greater_than':a>b,'greater_than_or_equals':a>=b,'less_than':a<b,'less_than_or_equals':a<=b,'equals':a==b,'not_equals':a!=b}[op]
        results=[]
        for k,o,v in n:
            if k in ('A11','A12','A13','A14'):r=self.cond(v,k)
            elif k=='has_country_flag':r=v in self.flags
            elif k=='has_completed_focus':r=v in self.completed
            elif k=='has_political_power':r=self.pp>float(v)
            elif k=='owns_state':r=self.owners[int(v)]==scope
            elif k=='country_exists':r=v in self.exists
            elif k=='is_subject_of':r=self.subjects.get(scope)==v
            elif k=='has_idea':r=v in self.ideas
            elif k=='OR':r=any(self.cond([x],scope) for x in v)
            elif k=='NOT':r=not self.cond(v,scope)
            elif k=='check_variable':
                if val(v,'var'):
                    a=self.variables.get(val(v,'var'),0);target=val(v,'value');b=self.variables.get(target,0) if not re.match(r'^-?[\d.]+$',target) else float(target)
                    r=cmp(a,val(v,'compare','equals'),b)
                else:
                    key,operator,target=v[0];a=self.variables.get(key,0);b=float(target)
                    r=a>b if operator=='>' else a<b if operator=='<' else a==b
            else:raise AssertionError(('Unknown condition',k))
            results.append(r)
        return all(results)
    def run(self,n,scope='A01'):
        branch=False
        for k,o,v in n:
            if k=='if':
                branch=self.cond(val(v,'limit'),scope)
                if branch:self.run([t for t in v if t[0]!='limit'],scope)
            elif k=='else_if':
                if not branch and self.cond(val(v,'limit'),scope):branch=True;self.run([t for t in v if t[0]!='limit'],scope)
            elif k=='else':
                if not branch:self.run(v,scope)
            elif k in effects:self.run(effects[k],scope)
            elif k in ('set_country_flag','clr_country_flag'):
                self.flags.add(v) if k=='set_country_flag' else self.flags.discard(v)
            elif k in ('add_ideas','remove_ideas'):
                self.ideas.add(v) if k=='add_ideas' else self.ideas.discard(v)
            elif k=='add_timed_idea':self.ideas.add(val(v,'idea'))
            elif k in ('set_variable','add_to_variable'):
                if val(v,'var'):
                    key=val(v,'var');amount=val(v,'value');amount=self.variables.get(amount,0) if not re.match(r'^-?[\d.]+$',amount) else float(amount)
                else:key,_,amount=v[0];amount=float(amount)
                self.variables[key]=(self.variables.get(key,0) if k=='add_to_variable' else 0)+amount
            elif k in ('activate_mission','remove_mission'):
                self.missions.add(v) if k=='activate_mission' else self.missions.discard(v)
            elif k=='retire_character':self.retired.add(v)
            elif k=='add_political_power':self.pp+=float(v)
            elif k=='add_stability':self.stability+=float(v)
            elif k=='set_power_balance':self.bop=float(val(v,'set_value'))
            elif k=='add_power_balance_value':self.bop+=float(val(v,'value'))
            elif k=='country_event':self.events.append(val(v,'id'))
            elif k in ('A11','A12','A13','A14'):self.run(v,k)
            elif k.isdigit():pass
            elif k=='transfer_state':self.owners[int(v)]=scope;self.exists.add(scope)
            elif k=='set_autonomy':self.subjects[val(v,'target')]='A01'
            elif k in ('remove_dynamic_modifier','set_politics','navy_experience','army_experience','add_war_support','add_tech_bonus','hidden_effect','name','ai_chance','load_oob'):pass
            else:raise AssertionError(('Unknown effect',k))
    def focus(self,fid):
        assert self.cond(val(focuses[fid],'available',[])),('Focus gated',fid)
        for k,o,n in focuses[fid]:
            if k=='mutually_exclusive':assert not any(v in self.completed for a,o,v in n)
        self.run(val(focuses[fid],'completion_reward',[]));self.completed.add(fid)
    def choice(self,eid,index=0):self.run([n for k,o,n in events[eid] if k=='option'][index])
checks=[]
# Three distinct resolutions remain gated until their actual political prerequisites are met.
for route in ('trial','purge','pension'):
    m=Model();m.flags.update({'A01_wilhelmina_reigns','A01_royal_guard_established'})
    fid={'trial':'A01_admirals_on_trial','purge':'A01_purge_the_admiralty','pension':'A01_admirals_retirement'}[route]
    if route!='pension':assert not m.cond(val(focuses[fid],'available'))
    m.focus('A01_summon_grand_council');m.focus('A01_royal_commission');m.choice('A01_royal_story.4',0)
    assert m.variables['A01_admiralty_evidence']==2
    m.run(val(decisions['A01_audit_naval_contracts'],'complete_effect'));m.focus('A01_win_the_captains')
    m.focus(fid)
    assert 'A01_admiralty_defeated' in m.flags and 'A01_admiralty_deadline' not in m.missions
    assert 'A01_admiralty_obstruction' not in m.ideas
    assert ('A01_purged_fleet' in m.ideas)==(route=='purge')
    assert ('A01_casembroot' in m.retired)==(route=='purge')
    assert ('A01_admiralty_pensions' in m.ideas)==(route=='pension')
    if route=='pension':m.run(val(focuses['A01_reform_procurement'],'completion_reward'));assert 'A01_admiralty_pensions' not in m.ideas
    m.flags.add('A01_island_settlement');m.focus('A01_civilian_admiralty');m.focus('A01_settle_crown_crisis')
    for index,balance in ((0,0),(1,.65)):
        t=copy.deepcopy(m);t.choice('A01_royal_story.7',index);assert t.bop==balance
checks.append('All three Council resolutions; proof/loyalty gates; purge removes a commander; pension reform; both constitutional outcomes')
# A missed deadline costs time/resources but cannot make the branch impossible.
m=Model();m.choice('A01_royal_story.15',0);assert m.pp==225 and 'A01_admiralty_deadline' in m.missions
checks.append('Deadline failure offers a recoverable political setback')
law=value(parse(read('common/scripted_triggers/A01_law_triggers.txt')),'A01_can_change_locked_laws')
for flags,expected in [(set(),False),({'A01_constitutional_amendments_active'},True),({'A01_admirals_council_abolished'},True)]:
    m=Model();m.flags=flags;assert m.cond(law)==expected
checks.append('Council defeat permanently unlocks its law veto after temporary amendments expire')
# Foreign-owned or independently existing sultanates must never be annexed or stolen.
for owners,exists in [({1055:'A03'},set()),({1055:'A11'},{'A11'}),({},set())]:
    m=Model();m.owners.update(owners);m.exists.update(exists);m.run(effects['A01_charter_crown_sultanates'])
    if owners:assert m.owners[1055]==owners[1055] and 'A11' not in m.subjects
    else:assert m.subjects.get('A11')=='A01'
    assert m.owners[1023]=='A03' and m.owners[1024]=='A03'
checks.append('Autonomous charters release only held land and preserve existing independent countries and Japanese holdings')
# Both social approaches reach the treaty; postponing civic representation changes election support.
for option in (0,1):
    m=Model();m.choice('A01_royal_story.1',option);m.choice('A01_royal_story.2',option)
    m.focus('A01_princely_guarantees');m.focus('A01_equal_subjects');assert m.cond(val(focuses['A01_island_compact'],'available'))
    m.focus('A01_island_compact');m.choice('A01_royal_story.3',0);assert 'A01_island_settlement' in m.flags
checks.append('Both princely negotiation options reach settlement with civic rights; no dead end')
# Elections retain the Queen, clear the incumbent programme and can change government repeatedly.
for winner in ('constitutional','order','indonesian'):
    m=Model();m.flags.update({'A01_civic_electoral_law','A01_equal_citizenship_established','A01_princes_guaranteed'})
    m.run(effects['A01_start_royal_election']);assert 'A01_royal_election_campaign' in m.missions
    for _ in range(3):m.run(val(decisions['A01_campaign_'+winner],'complete_effect'))
    m.run(val(decisions['A01_royal_election_campaign'],'timeout_effect'))
    assert m.ideas&{'A01_pm_constitutional','A01_pm_order','A01_pm_indonesian'}=={'A01_pm_'+winner}
    assert 'A01_prime_minister_elected' in m.flags and 'A01_royal_election_term' in m.missions
    previous=winner;winner='order' if winner!='order' else 'constitutional'
    m.run(val(decisions['A01_royal_election_term'],'timeout_effect'))
    for _ in range(4):m.run(val(decisions['A01_campaign_'+winner],'complete_effect'))
    m.run(effects['A01_finish_royal_election'])
    assert 'A01_pm_'+winner in m.ideas and 'A01_pm_'+previous not in m.ideas
    assert not m.retired, 'Elections must not replace the monarch'
m=Model();m.run(effects['A01_start_royal_election']);m.run(effects['A01_finish_royal_election']);assert 'A01_pm_indonesian' in m.ideas
checks.append('All three named premiers can win; repeat elections replace cabinet bonuses; deterministic ties; monarch remains')
# Exact references, localization, modifier names, mutual exclusions and DAG checks.
royal=manifest['focus_art'];locs={}
for lang in ('russian','english'):
    locs[lang]='\n'.join(p.read_text(encoding='utf-8-sig') for p in (R/f'localisation/{lang}').glob('*.yml'))
    keys=set(re.findall(r'^\s*(\S+):\d*\s',locs[lang],re.M))
    required=set()
    for fid in royal:required.update((fid,fid+'_desc'))
    for eid,n in events.items():
        required.update((value(n,'title'),value(n,'desc')))
        required.update(value(o,'name') for k,op,o in n if k=='option')
    for d in decisions:required.update((d,d+'_desc'))
    for i in manifest['ideas']:required.update((i,i+'_desc'))
    assert required<=keys,(lang,required-keys)
    local=(R/f'localisation/{lang}/1896_main_l_{lang}.yml').read_bytes();assert local.startswith(b'\xef\xbb\xbf')
    for line in local.decode('utf-8-sig').splitlines()[1:]:
        if not line.strip() or line.lstrip().startswith('#'): continue
        assert re.match(r'^ \S+:\d* ".*"\s*(?:#.*)?$',line),line
def visit(fid,stack=()):
    assert fid not in stack,('Cycle',fid)
    for k,o,n in focuses[fid]:
        if k=='prerequisite':
            for a,op,ref in n:assert ref in focuses;visit(ref,stack+(fid,))
for fid,n in focuses.items():
    visit(fid)
    for k,o,nodes in n:
        if k=='mutually_exclusive':
            for a,op,ref in nodes:assert any(k=='mutually_exclusive' and ('focus','=',fid) in v for k,o,v in focuses[ref]),(fid,ref)
pos={}
for fid,n in focuses.items():
    xy=(value(n,'x'),value(n,'y'));assert xy not in pos,(fid,pos.get(xy),xy);pos[xy]=fid
mods=(G/'documentation/modifiers_documentation.md').read_text(encoding='utf-8-sig')
for key,o,n in value(value(parse(read('common/ideas/A01_royal_story.txt')),'ideas'),'country'):
    for mod,op,v in value(n,'modifier'):
        assert '## '+mod+'\n' in mods or mod.startswith('production_speed_'),mod
checks.append('All prerequisites, cycles, layout, symmetric exclusions, complete RU/EN localisation and installed-engine modifier names')
gfx='\n'.join(p.read_text(encoding='utf-8-sig') for p in (R/'interface').glob('*.gfx'))
for fid in royal:assert 'name = "GFX_'+fid+'"' in gfx,fid
for art in set(manifest['ideas'].values()):
    assert 'name = "GFX_idea_royal_'+art+'"' in gfx,art
    path=R/f'gfx/interface/ideas/royal_{art}.dds';im=Image.open(path).convert('RGBA');assert im.size==(64,64) and im.getextrema()[3][0]==0
checks.append('Local focus/shine/idea DDS sprites and transparent national spirit textures')
report={'status':'passed','new_focuses':len(manifest['new_focuses']),'royal_focuses':len(royal),'new_events':len(events),'visible_spirits':len(manifest['ideas']),'checks':checks,'in_game_campaign':'Not run; script simulation and asset validation only.'}
(R/'tools/royal_story_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
