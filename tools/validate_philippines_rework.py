"""Static reference, graph and bounded script checks for the Philippine campaign.

This validator imports no legacy migration scripts and changes no game sources.
"""
from pathlib import Path
from collections import Counter, defaultdict
import json, re

R=Path(__file__).resolve().parents[1]
G=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
PFX=('A10','a10')
def read(p):return p.read_text(encoding='utf-8-sig')
def parse(s):
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|#[^\n]*|>=|<=|[{}=<>]|[^\s{}=<>]+',s)
    tokens=[t for t in tokens if not t.startswith('#')]
    pos=0
    def block(nested=False):
        nonlocal pos
        out=[]
        while pos<len(tokens) and tokens[pos]!='}':
            k=tokens[pos];pos+=1
            if pos<len(tokens) and tokens[pos] in ('=','<','>','<=','>='):
                op=tokens[pos];pos+=1
                assert pos<len(tokens),(k,'missing value')
                if tokens[pos]=='{':pos+=1;v=block(True)
                else:v=tokens[pos];pos+=1
                out.append((k,op,v))
            else:out.append((k,None,None))
        if nested:
            assert pos<len(tokens) and tokens[pos]=='}','unclosed block'
            pos+=1
        return out
    out=block();assert pos==len(tokens),'unmatched closing brace';return out
def value(n,k,d=None):return next((v for key,o,v in n if key==k),d)
def walk(n):
    for k,o,v in n:
        yield k,o,v
        if isinstance(v,list):yield from walk(v)
def definitions(folder):
    return {k:v for p in (R/folder).glob('*.txt') for k,o,v in parse(read(p))}

def validate():
    folders=('common/national_focus','common/ideas','common/scripted_effects','common/scripted_triggers','common/decisions','common/on_actions','common/characters','common/autonomous_states','common/factions/templates','common/ai_strategy_plans','events')
    paths=[p for folder in folders for p in (R/folder).rglob('*.txt') if p.name.startswith(PFX)]
    trees={}
    for p in paths:
        try:trees[p]=parse(read(p))
        except Exception as e:raise AssertionError(f'{p.relative_to(R)}: {e}') from e
    fs={value(v,'id'):v for k,o,v in value(parse(read(R/'common/national_focus/a10_focus.txt')),'focus_tree') if k=='focus'}
    assert len(fs)==117,len(fs)
    coords={}
    for id,n in fs.items():
        xy=(int(value(n,'x')),int(value(n,'y')))
        assert xy not in coords,(id,'overlap',coords.get(xy));coords[xy]=id
        for k,o,v in n:
            if k in ('prerequisite','mutually_exclusive'):
                for _,_,parent in v:
                    assert parent in fs,(id,parent)
                    if k=='prerequisite':assert int(value(fs[parent],'y'))<xy[1],(id,'parent not above',parent)
                    else:assert any(id==p for key,_,node in fs[parent] if key=='mutually_exclusive' for _,_,p in node),(id,'asymmetric exclusion',parent)
    assert [id for id,n in fs.items() if value(n,'prerequisite') is None]==['A10_island_congress']
    political_choices={'A10_confederation','A10W_oath','A10M_coup'}
    for entry in ('A10D_island_census','A10_coastal_arsenals'):
        assert {p for _,_,p in value(fs[entry],'prerequisite')}==political_choices,(entry,'industry must follow political choice')
    scenarios={
        'confederation':{'A10W_oath','A10M_coup','A10R_federal_convention'},
        'federation':{'A10W_oath','A10M_coup','A10R_republics_forever'},
        'colony':{'A10_confederation','A10M_coup','A10W_metropolitan_charter'},
        'metropole':{'A10_confederation','A10M_coup','A10W_colonial_charter'},
        'junta':{'A10_confederation','A10W_oath','A10M_directorate','A10M_compensation'},
        'directorate':{'A10_confederation','A10W_oath','A10M_junta','A10M_labour_battalions'},
    }
    reachable={}
    for scenario,blocked in scenarios.items():
        taken=set()
        while True:
            before=set(taken)
            for id,n in fs.items():
                if id in blocked:continue
                groups=[{p for _,_,p in v} for k,o,v in n if k=='prerequisite']
                excludes={p for k,o,v in n if k=='mutually_exclusive' for _,_,p in v}
                if not(excludes&taken) and all(group&taken for group in groups):taken.add(id)
            if taken==before:break
        reachable[scenario]=taken
    for scenario,end in [('confederation','A10R_republican_compact_end'),('federation','A10R_civilian_commonwealth'),('colony','A10W_colony'),('metropole','A10W_new_metropole'),('junta','A10M_red_seal'),('directorate','A10M_fixed_term')]:
        assert end in reachable[scenario],(scenario,'unreachable',end)
    assert set.union(*reachable.values())==set(fs),('unreachable focuses',set(fs)-set.union(*reachable.values()))

    locs={}
    for lang in ('russian','english'):
        entries=defaultdict(list)
        for p in (R/f'localisation/{lang}').rglob('*.yml'):
            if p.name.startswith(PFX):assert p.read_bytes().startswith(b'\xef\xbb\xbf'),p
            for key in re.findall(r'^\s+([^ :]+):\d+\s+"',read(p),re.M):entries[key].append(p)
        locs[lang]=entries
        for key,files in entries.items():
            if key.startswith(PFX):assert len(files)==1,('duplicate localisation',lang,key,[str(p.relative_to(R)) for p in files])
    def localized(k):
        for lang in locs:assert k in locs[lang],('missing localisation',lang,k)
    for id in fs:localized(id);localized(id+'_desc')
    effects=definitions('common/scripted_effects');triggers=definitions('common/scripted_triggers')
    ideas={k:v for p in (R/'common/ideas').glob('*.txt') for k,o,v in value(value(parse(read(p)),'ideas',[]),'country',[])}
    event_ids={value(v,'id') for p in (R/'events').glob('*.txt') for k,o,v in parse(read(p)) if k=='country_event'}
    focus_ids={value(n,'id') for p in (R/'common/national_focus').glob('*.txt') for k,o,v in parse(read(p)) if k=='focus_tree' for nk,no,n in v if nk=='focus'}
    sprites={}
    for base in (G,R):
        for p in (base/'interface').rglob('*.gfx'):
            for m in re.finditer(r'spriteType\s*=\s*\{\s*name\s*=\s*"?([^"\s]+)"?[^}]*?texturefile\s*=\s*"([^"]+)"',read(p),re.S|re.I):sprites[m[1]]=m[2]
    def sprite(k):
        assert k in sprites,('missing sprite',k)
        assert (R/sprites[k]).exists() or (G/sprites[k]).exists(),('missing texture',k,sprites[k])
    engine_effects=set(re.findall(r'^## (\w+)\s*$',read(G/'documentation/effects_documentation.md'),re.M))
    engine_triggers=set(re.findall(r'^## (\w+)\s*$',read(G/'documentation/triggers_documentation.md'),re.M))
    engine_triggers.update(('infrastructure','industrial_complex','arms_factory','dockyard','naval_base','bunker','coastal_bunker'))
    engine_modifiers=set(re.findall(r'^## (\w+)\s*$',read(G/'documentation/modifiers_documentation.md'),re.M))
    scopes={'ROOT','FROM','PREV','THIS','OVERLORD','owner','controller','capital_scope','overlord','faction_leader'}
    def is_scope(k):return k in scopes or re.fullmatch(r'[A-Z][A-Z0-9]{2}|\d+|event_target:\w+',k)
    def check_trigger(n):
        for k,o,v in n:
            if k in ('AND','OR','NOT','hidden_trigger') or is_scope(k):check_trigger(v)
            else:assert k in engine_triggers or k in triggers,('undocumented trigger',k)
    def check_effect(n):
        for k,o,v in n:
            assert k in engine_effects or k in effects or is_scope(k) or k in ('if','else_if','else','hidden_effect'),('undocumented effect',k)
            if k in ('if','else_if','else','hidden_effect') or is_scope(k):
                for key,op,node in v:
                    if key=='limit':check_trigger(node)
                    else:check_effect([(key,op,node)])
            elif k in ('every_subject_country','every_owned_state','random_state','random_owned_controlled_state'):
                for key,op,node in v:
                    if key=='limit':check_trigger(node)
                    else:check_effect([(key,op,node)])
    checked_modifiers=set()
    for p,n in trees.items():
        for k,o,v in walk(n):
            if k in ('limit','trigger','visible','available','allowed','activation','bypass') and isinstance(v,list):check_trigger(v)
            if k in ('completion_reward','complete_effect','remove_effect','immediate') and isinstance(v,list):check_effect(v)
            if k.startswith(PFX) and v=='yes':assert k in effects or k in triggers,('missing scripted call',p,k)
            if k=='country_event' and isinstance(v,list):assert value(v,'id') in event_ids,(p,'missing event',value(v,'id'))
            if k=='has_completed_focus':assert v in focus_ids,(p,'missing focus',v)
            if k in ('has_idea','add_ideas','remove_ideas') and isinstance(v,str):assert v in ideas,(p,'missing idea',v)
            if k=='add_timed_idea':assert value(v,'idea') in ideas,(p,'missing timed idea',v)
            if k in ('title','custom_effect_tooltip') or (k=='desc' and isinstance(v,str)):localized(v.strip('"'))
            if k=='option':localized(value(v,'name'))
            if k=='picture' and v.startswith('GFX_'):sprite(v)
        if p.parent.name=='ideas':
            for id,_,idea in value(value(n,'ideas'),'country'):
                localized(id);localized(id+'_desc');sprite('GFX_idea_'+value(idea,'picture'))
                for key,_,_ in value(idea,'modifier',[]):
                    assert key in engine_modifiers or re.fullmatch(r'production_speed_\w+_factor',key),(id,'unknown modifier',key)
                    checked_modifiers.add(key)
        if p.parent.name=='scripted_effects':
            for key,_,body in n:check_effect(body)
        if p.parent.name=='ai_strategy_plans':
            for _,_,body in n:
                for key in ('allowed','enable','abort'):check_trigger(value(body,key,[]))
                for fid,_,_ in value(body,'ai_national_focuses',[]):assert fid in focus_ids,('AI focus',fid)
        if p.parent.name in ('decisions','categories'):
            for key,_,body in n:
                if p.parent.name=='categories':localized(key);localized(key+'_desc')
                else:
                    for did,_,_ in body:localized(did);localized(did+'_desc')
    for id,n in fs.items():sprite(value(n,'icon'))
    # Nine ratifications, separate ownership safeguards, exact compliance gate.
    rat=read(R/'common/decisions/A10R_ratification.txt')
    assert rat.count('annex_country =')==9 and rat.count('transfer_troops = yes')==9
    assert len(re.findall(r'A10R_consent_\w+.*?is_subject_of = A10',rat,re.S))>=9
    assert read(R/'common/decisions/A10_philippines.txt').count('NOT = { compliance < 80 }')==9
    assert 'is_subject = no' in read(R/'common/scripted_effects/A10_philippines.txt').split('A10_release_PVI')[0]
    actions=read(R/'common/on_actions/A10R_republics.txt')
    assert 'on_monthly = { effect = { A10 =' not in actions
    report={'date':'2026-10-31','focuses':len(fs),'scripts':len(paths),
      'focus_paths':{k:len(v) for k,v in reachable.items()},'checked_modifier_types':len(checked_modifiers),
      'ideas':sum(k.startswith(PFX) for k in ideas),'events':sum(k.startswith(PFX) for k in event_ids),
      'checks':['balanced parsed scripts','six reachable political outcomes','symmetric exclusions','focus layout and dependency order','bilingual localisation with no A10 duplicates','real sprites and textures','engine effect/trigger/modifier names','reference integrity','nine guarded consent/accessions','legacy 80 percent gates','subject faction guard','country-scoped monthly update'],
      'limitations':['Static graph checks abstract focus availability and AI scheduling','Separate bounded model tests cover supply and sovereignty transitions','No full campaign or combat balance playthrough']}
    (R/'tools/philippines_rework_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':validate()
