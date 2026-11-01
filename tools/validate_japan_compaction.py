"""Validate the condensed graph and preserved story/reward payloads."""
from pathlib import Path
import runpy
if 'id = JPI_closed_ports' in (Path(__file__).resolve().parents[1]/'common/national_focus/a03_focus.txt').read_text(encoding='utf-8-sig'):
    runpy.run_path(str(Path(__file__).with_name('validate_japan_industry.py')), run_name='__main__')
    raise SystemExit(0)
from itertools import product
import re
from add_canon_countries import parse, value
from compact_japan_campaign import R,B,ALIASES,GROUPS,DISCARDED,POSITIONS,body
from clarify_japan_branches import blocks

def load(text):
    return {value(n,'id'):n for k,o,n in value(parse(text),'focus_tree') if k=='focus'}
current=(R/'common/national_focus/a03_focus.txt').read_text(encoding='utf-8-sig')
original=(B/'common/national_focus/a03_focus.txt').read_text(encoding='utf-8-sig')
fs=load(current);old=load(original)
assert set(fs)==set(POSITIONS) and len(fs)==56
assert len(fs)-10==46
def parents(fid):return [{v for k,o,v in n if k=='focus'} for k,o,n in fs[fid] if k=='prerequisite']
def ancestors(fid,path=()):
    assert fid not in path,('cycle',fid)
    return {fid}|set().union(*(ancestors(p,path+(fid,)) for group in parents(fid) for p in group))
for fid in fs:
    assert 'A03_imperial_council' in ancestors(fid)
    if not fid.startswith('JPX_') and fid!='A03_imperial_council':assert 'JPX_sea' in ancestors(fid),fid
    if fid.startswith('JPX_') and fid not in {'JPX_sea','JPX_sea_institution'}:
        assert not any(fid in ancestors(other) for other in fs if other not in {fid,fid+'_institution'}),(fid,'joined main tree')
    for group in parents(fid):
        for parent in group:assert POSITIONS[parent][1]<POSITIONS[fid][1],(parent,fid)
# All policy and constitutional alternatives can reach the final milestone.
for government in ['A03_prime_minister_filter','A03_direct_imperial_rule']:
    for result in ['victory','defeat']:
        blocked={'JPX_land','JPX_trade','JPX_kami','JPX_throne'}
        blocked.add('A03_direct_imperial_rule' if government=='A03_prime_minister_filter' else 'A03_prime_minister_filter')
        blocked.update({'JPC_defeat_inquest'} if result=='victory' else {'JPC_oil_promise','JPC_rebuild_ports','JPF_royalty_register'})
        done=set()
        for _ in fs:
            for fid in fs:
                if fid not in blocked and all(group&done for group in parents(fid)):done.add(fid)
        assert 'JPD_reformed_empire' in done,(government,result)
# Exactly preserve existing payloads when consolidating; no rewards from rejected
# emergency policies are silently granted alongside the standard policy.
raw_old={re.search(r'\bid\s*=\s*(\w+)',b)[1]:b for _,_,b in blocks(original)}
raw_new={re.search(r'\bid\s*=\s*(\w+)',b)[1]:b for _,_,b in blocks(current)}
for fid in fs:
    reward=parse(body(raw_new[fid],'completion_reward'))
    expected=[]
    for source in [fid]+GROUPS.get(fid,[]):expected+=parse(body(raw_old[source],'completion_reward'))
    assert reward==expected,(fid,'lost or reordered reward')
for p in (R/'common').rglob('*.txt'):
    s=p.read_text(encoding='utf-8-sig')
    for ref in re.findall(r'has_completed_focus\s*=\s*(\w+)',s):assert ref not in ALIASES,(p,ref)
for lang in ['russian','english']:
    s=(R/f'localisation/{lang}/1896_main_l_{lang}.yml').read_text(encoding='utf-8-sig')
    keys=set(re.findall(r'^\s+([^ :]+):',s,re.M))
    for fid in fs:assert fid in keys and fid+'_desc' in keys,(lang,fid)
assert 'has_country_flag = JPF_finance_closed' in raw_new['JPD_industrial_power']
assert 'has_country_flag = JPN_north_compact_signed' in raw_new['JPD_settle_three_heads']
print('PASS: 56 focuses / 46 main stages; no cycles or alternative routes joining the main campaign; both government choices and war outcomes reach the finale in the prerequisite graph; all consolidated rewards/events preserved; no stale focus references; actual finance/north settlement gates retained.')
