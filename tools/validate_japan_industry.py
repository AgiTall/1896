"""Validate all eight authored routes, integration gates and render a focus preview.

Static checks only: this does not claim an in-engine test.
"""
from pathlib import Path
from itertools import product
import re
import json
from add_canon_countries import parse, value
from PIL import Image, ImageDraw, ImageFont

R=Path(__file__).resolve().parents[1]
def read(p): return (R/p).read_text(encoding='utf-8-sig')
def get(n,k,default=None): return next((v for key,op,v in n if key==k),default)
def walk(n):
    for k,o,v in n:
        yield k,o,v
        if isinstance(v,list): yield from walk(v)
def fs(text): return {value(n,'id'):n for k,o,n in value(parse(text),'focus_tree') if k=='focus'}
focus=fs(read('common/national_focus/a03_focus.txt'))
assert len(focus)==68
old=fs(read('tools/backups/japan_scarlet_20261019/common/national_focus/a03_focus.txt'))
removed={'JPC_osaka_orders','JPC_war_workshops','JPC_pledged_yards','JPC_convoy_budget','JPC_replace_losses'}
assert set(focus)==(set(old)-removed)|{k for k in focus if k.startswith('JPI_')}
for fid in set(old)-removed:
    assert get(focus[fid],'completion_reward')==get(old[fid],'completion_reward'),fid
coords={k:(int(value(n,'x')),int(value(n,'y'))) for k,n in focus.items()}
def parents(fid): return [{v for k,o,v in n if k=='focus'} for k,o,n in focus[fid] if k=='prerequisite']
for fid,n in focus.items():
    for group in parents(fid):
        for p in group:
            assert p in focus,(fid,p)
            assert coords[p][1]<coords[fid][1],(p,fid,'upward edge')
    for other in focus:
        if other!=fid and coords[other][1]==coords[fid][1]: assert abs(coords[other][0]-coords[fid][0])>=2,(fid,other)
    for k,o,other in get(n,'mutually_exclusive',[]):
        assert ('focus','=',fid) in get(focus[other],'mutually_exclusive',[]),(fid,other)
    for k,o,v in walk(n):
        if k in {'focus','has_completed_focus'}: assert v in focus,(fid,v)

routes=[]
for material,fleet,gov,outcome in product(['kyushu_coal','oil_hunger','proxy_machines','copied_samples'],['kure_yards','airship_hangars'],['prime_minister_filter','direct_imperial_rule'],['victory','defeat']):
    trade=material in {'proxy_machines','copied_samples'}
    route={'JPI_'+x for x in [material,fleet,'japanese_terms' if trade else 'closed_ports','unsigned_contracts' if trade else 'raw_register','standard_node','electrical_bureau','portable_prototype','coastal_trials','quiet_coast','scarlet_sails','southern_push']}
    blocked={x for x in focus if x.startswith('JPI_') and x not in route}
    blocked|={'JPX_land','JPX_trade','JPX_kami','JPX_throne'}
    blocked.add('A03_direct_imperial_rule' if gov=='prime_minister_filter' else 'A03_prime_minister_filter')
    blocked|={'JPC_defeat_inquest'} if outcome=='victory' else {'JPC_oil_promise','JPC_rebuild_ports','JPF_royalty_register'}
    if not trade: blocked|={'JPC_wtc_mission','JPF_madeira_table'}
    done=set()
    for _ in focus:
        for fid in focus:
            if fid not in blocked and all(group&done for group in parents(fid)): done.add(fid)
    assert route<=done,(material,fleet)
    assert 'JPD_reformed_empire' in done,(material,fleet,gov,outcome)
    # Blocking the mandatory towers must block the entire invasion branch.
    done=set()
    for _ in focus:
        for fid in focus:
            if fid not in blocked|{'JPI_quiet_coast'} and all(group&done for group in parents(fid)): done.add(fid)
    assert not {'JPI_scarlet_sails','JPI_southern_push','JPC_batavia_demands'}&done
    routes.append((material,fleet,gov,outcome))

# Parse every edited script, including effects/decisions inherited from earlier work.
backup=R/'tools/backups/japan_scarlet_20261019'
paths={p.relative_to(backup) for p in backup.rglob('*.txt')}
paths|={p.relative_to(R) for folder in ['common','events'] for p in (R/folder).rglob('JPI*.txt')}
for p in paths: parse(read(p))
effects=parse(read('common/scripted_effects/borneo_war_effects.txt'))
for name in ['A03_prepare_southern_war_effect','A03_start_southern_war_effect']:
    limit=value(value(value(effects,name),'if'),'limit')
    assert ('has_country_flag','=','JPI_tesla_ready') in limit,name
ult=value(parse(read('common/scripted_effects/JPC_canonical.txt')),'JPC_issue_ultimatum')
assert ('set_country_flag','=','JPI_ultimatum_due') in ult
limit=value(value(ult,'if'),'limit')
for flag in ['JPI_tesla_ready','JPI_southern_ready']: assert ('has_country_flag','=',flag) in limit
prepare=value(value(value(effects,'A03_prepare_southern_war_effect'),'if'),'limit')
heavy=[n for k,o,n in walk(value(effects,'A03_prepare_southern_war_effect')) if k=='if' and ('has_completed_focus','=','JPI_kure_yards') in get(n,'limit',[])]
assert len(heavy)==1
assert {v.strip('"') for k,o,v in walk(heavy[0]) if k=='load_oob'}=={'A03_southern_reinforcements','A03_southern_reinforcements_legacy'}
naval_dlc=value(heavy[0],'if')
assert get(heavy[0],'else') is not None and get(naval_dlc,'else') is None,'DLC fallback must be a sibling'
wtc=value(parse(read('common/decisions/WTC_credit.txt')),'WTC_debt_ledger')
for fid in ['WTC_borrow','WTC_concede','WTC_naval_service','WTC_insure','WTC_cables']:
    assert [('has_country_flag','=','JPI_autarky')] in [n for k,o,n in value(value(wtc,fid),'available') if k=='NOT']
assert 'JPI_autarky' not in str(value(value(wtc,'WTC_repay'),'available'))
ai=value(value(parse(read('common/ai_strategy_plans/A01_canonical.txt')),'A03_southern_canonical_plan'),'ai_national_focuses')
assert all(fid in focus for fid,o,v in ai)
assert [fid for fid,o,v in ai].index('JPI_southern_push')<[fid for fid,o,v in ai].index('JPC_one_war_cabinet')

locs={}
for lang in ['russian','english']:
    path=R/f'localisation/{lang}/1896_main_l_{lang}.yml'
    assert path.read_bytes().startswith(b'\xef\xbb\xbf')
    pairs=re.findall(r'^\s+([^ :]+):\d*\s*"(.*)"',path.read_text(encoding='utf-8-sig'),re.M)
    keys=[k for k,v in pairs]; locs[lang]=dict(pairs)
    assert len(keys)==len(set(keys)),'Duplicate localisation keys'
    for fid in focus: assert fid in keys and fid+'_desc' in keys,(lang,fid)
    for p in paths:
        for k,o,v in walk(parse(read(p))):
            if k in {'title','text','custom_effect_tooltip','name'} and isinstance(v,str) and (v.startswith('JPI_') or v.startswith('japan_industry.')): assert v in keys,(lang,v)
# Verify actual symbol definitions rather than inventing equipment or focus sprites.
gfx='\n'.join(p.read_text(encoding='utf-8-sig') for p in (R/'interface').rglob('*.gfx'))
for fid,n in focus.items():
    if fid.startswith('JPI_'): assert re.search(r'name\s*=\s*"?'+re.escape(value(n,'icon'))+r'\b',gfx),fid
assert any(re.search(r'\bairship_equipment_1\s*=\s*\{',p.read_text(encoding='utf-8-sig')) for p in (R/'common/units/equipment').rglob('*.txt'))
documented=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md').read_text(encoding='utf-8-sig')
industry_ideas=value(value(parse(read('common/ideas/JPI_industry.txt')),'ideas'),'country')
for fid,o,n in industry_ideas:
    assert fid in locs['russian'] and fid+'_desc' in locs['russian']
    assert fid in locs['english'] and fid+'_desc' in locs['english']
    for modifier,op,v in value(n,'modifier'): assert '## '+modifier+'\n' in documented or re.fullmatch(r'production_speed_(dockyard|arms_factory)_factor',modifier),modifier
finals={k for k,o,n in industry_ideas if k.startswith('JPI_scarlet_')}
assert len(finals)==8
scarlet=value(parse(read('common/scripted_effects/JPI_industry.txt')),'JPI_scarlet_sails_effect')
for material,fleet in product(['kyushu_coal','oil_hunger','proxy_machines','copied_samples'],['kure_yards','airship_hangars']):
    completed={'JPI_'+material,'JPI_'+fleet}
    granted=[]
    for k,o,n in scarlet:
        if k=='if' and all(v in completed for kk,oo,v in get(n,'limit',[]) if kk=='has_completed_focus'):
            granted += [v for kk,oo,v in n if kk=='add_ideas' and v in finals]
    assert len(granted)==1,(material,fleet,granted)
assert parents('JPI_quiet_coast')==[{'JPI_coastal_trials'}]
assert 'JPI_tesla_tested' in str(get(focus['JPI_quiet_coast'],'available'))

# Standalone schematic with the real labels, prerequisites and red exclusion links.
ids=['JPX_sea']+[fid for fid in focus if fid.startswith('JPI_')]
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
im=Image.new('RGB',(1200,1295),(20,26,34));draw=ImageDraw.Draw(im)
def pos(fid):
    x,y=(6,1) if fid=='JPX_sea' else coords[fid]
    return 120+x*80,55+(y-1)*105
for fid in ids:
    for group in parents(fid):
        for parent in group:
            if parent not in ids: continue
            x,y=pos(parent);xx,yy=pos(fid)
            draw.line([(x,y+32),(x,y+50),(xx,y+50),(xx,yy-32)],fill=(125,156,183),width=3)
for fid in ids:
    x,y=pos(fid)
    for k,o,other in get(focus[fid],'mutually_exclusive',[]):
        if other in ids and fid<other:
            xx,yy=pos(other);left,right=sorted([x,xx]);cy=y
            draw.line([(left+108,cy),(right-108,cy)],fill=(235,83,82),width=3)
            draw.polygon([(left+108,cy),(left+116,cy-5),(left+116,cy+5)],fill=(235,83,82))
            draw.polygon([(right-108,cy),(right-116,cy-5),(right-116,cy+5)],fill=(235,83,82))
for fid in ids:
    x,y=pos(fid);w=200 if fid=='JPX_sea' else 108
    draw.rounded_rectangle((x-w,y-32,x+w,y+32),radius=8,fill=(39,50,64),outline=(191,166,104),width=2)
    words=locs['russian'][fid].split();lines=[];line=''
    for word in words:
        candidate=(line+' '+word).strip()
        if draw.textlength(candidate,font=font)>2*w-12 and line: lines.append(line);line=word
        else:line=candidate
    lines.append(line)
    draw.multiline_text((x,y),'\n'.join(lines),font=font,fill='white',anchor='mm',align='center',spacing=0)
im.save(R/'tools/japan_scarlet_industry_preview.png')
report={'status':'passed','focuses':len(focus),'industry_focuses':17,'routes_and_endings':len(routes),'final_spirit_variants':len(finals),'script_files_parsed':len(paths),'engine_tested':False}
(R/'tools/japan_industry_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
