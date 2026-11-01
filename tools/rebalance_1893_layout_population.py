"""Apply the October 2026 layout/population revision; no political effects changed."""
from pathlib import Path
from collections import defaultdict
import re, json, shutil
from add_canon_countries import parse, value

R = Path(__file__).resolve().parents[1]
B = R / 'tools/backups/layout_population_20261013'

def write(p, text):
    backup = B / p.relative_to(R)
    if not backup.exists():
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, backup)
    raw=backup.read_bytes()
    encoding='utf-8-sig' if p.suffix=='.yml' or raw.startswith(b'\xef\xbb\xbf') else 'utf-8'
    newline='\r\n' if b'\r\n' in raw else '\n'
    p.write_text(text, encoding=encoding, newline=newline)

def layout(tag, positions):
    p = R / f'common/national_focus/{tag}_focus.txt'
    s = p.read_text(encoding='utf-8-sig')
    # Focus blocks are balanced; edit coordinates only, preserving script and comments.
    spans = []
    for m in re.finditer(r'\bfocus\s*=\s*\{', s):
        i = m.end(); depth = 1
        while depth:
            depth += (s[i] == '{') - (s[i] == '}'); i += 1
        block = s[m.start():i]
        fid = re.search(r'\bid\s*=\s*(\w+)', block)[1]
        if fid in positions:
            for key, n in zip(('x', 'y'), positions[fid]):
                block = re.sub(r'\b' + key + r'\s*=\s*-?\d+', f'{key} = {n}', block, count=1)
            spans.append((m.start(), i, block))
    for a, b, block in reversed(spans): s = s[:a] + block + s[b:]
    write(p, s)

def apply_layout():
    from refine_japan_presentation import positions
    layout('a03', positions())
    nl = {}
    p=R/'common/national_focus/a01_focus.txt'
    fs={value(f,'id'):f for k,o,f in value(parse(p.read_text(encoding='utf-8-sig')),'focus_tree') if k=='focus'}
    # The royal alternative has its own broad area, separated from the republic.
    royal=set()
    for fid,f in fs.items():
        if any(k=='allow_branch' and 'A01_royal_path_revealed' in str(v) for k,o,v in f): royal.add(fid)
    royal.add('A01_crown_above_factions')
    # Derive coordinates from the saved original to keep re-runs idempotent.
    original=B/'common/national_focus/a01_focus.txt'
    source=original if original.exists() else p
    before={value(f,'id'):f for k,o,f in value(parse(source.read_text(encoding='utf-8-sig')),'focus_tree') if k=='focus'}
    for fid in royal: nl[fid]=(int(value(before[fid],'x'))+26,int(value(before[fid],'y'))+2)
    rows={
      2:{'european_democratic_unity':-8,'wtc_strengthening_path':48},
      15:{'ludolf_survives':13,'negotiated_resignation':32},
      16:{'wtc_oil_and_rubber_offer':3,'purge_civil_service':30,'purge_officer_corps':34},
      17:{'reconstruction_commission':3,'demobilise_colonial_army':10,'blame_the_military':14,'autonomous_sultanates':20},
      18:{'repair_ports':1,'families_compensation':5,'joint_officer_schools':8,'civilian_defence_ministry':12,'island_representation':20,'british_raj_model':24},
      19:{'public_recovery_fund':1,'wtc_recovery_agreement':5,'golden_bridges':12,'equal_citizenship':20,'sultanates_language_guarantees':24,'military_state':32},
      20:{'federal_defence_command':8,'northern_memory':30,'postwar_admiralty_shipyards':34},
      21:{'domestic_debt_redemption':1,'wtc_settlement':5,'town_hall_crisis':10},
      22:{'fleet_of_recovery':32},
      23:{'recovery_investment':3,'general_amnesty':8,'ludolf_retirement_navy':12},
      24:{'abolish_admirals_council':16},
      26:{'federal_constitution':20},27:{'elected_civil_service':20},28:{'democratic_federation':20},
      30:{'electoral_commission':18,'legalise_federal_parties':22},31:{'first_federal_election':20},
      33:{'liberal_victory':16,'conservative_victory':20,'peoples_party_victory':24},
      32:{'reform_procurement':64},
      38:{'review_borneo_convention':32},
    }
    for y,cols in rows.items():
        for fid,x in cols.items(): nl['A01_'+fid]=(x,y)
    layout('a01',nl)

def population():
    groups=defaultdict(list)
    philippines={327,623,624,625,626,627,628,1025,1026,1027,1084,1085}
    caribbean={315,318,319,686,689,690,691,692,693,695,696,1082,1083}
    nz={284,723,1079,1080,1081}
    japan={282,526,528,529,530,531,532,533,534,535,536,645,1018,1019,1020}
    for p in (R/'history/states').glob('*.txt'):
        s=p.read_text(encoding='utf-8-sig'); n=value(parse(s),'state'); sid=int(value(n,'id'))
        owner=next((v for k,o,v in value(n,'history') if k=='owner'),'ZZZ')
        group=('Japan' if sid in japan else 'Philippines' if sid in philippines else
            'Caribbean' if sid in caribbean else 'New Zealand' if sid in nz else
            'Ceylon' if sid==422 else 'Madagascar' if sid==543 else
            'Dutch East Indies' if owner=='A01' else 'Australia' if owner=='A07' and sid!=523 else
            'British Leviathan' if owner=='A02' else 'Other' if owner!='ZZZ' else None)
        if group: groups[group].append((sid,p,s,int(value(n,'manpower'))))
    targets={'Japan':48000000,'Dutch East Indies':42000000,'Philippines':8000000,'Caribbean':8000000,
        'Australia':6000000,'British Leviathan':4000000,'New Zealand':1500000,'Ceylon':1500000,
        'Madagascar':2000000,'Other':15000000}
    report={}
    for group,states in groups.items():
        states.sort();total=sum(s[3] for s in states);target=targets[group]
        counts=[s[3]*target//total for s in states]
        order=sorted(range(len(states)),key=lambda i:(states[i][3]*target%total,-states[i][0]),reverse=True)
        for i in order[:target-sum(counts)]:counts[i]+=1
        report[group]={'total':target,'states':{}}
        for (sid,p,s,old),new in zip(states,counts):
            write(p,re.sub(r'(\bmanpower\s*=\s*)\d+',lambda m:m[1]+str(new),s,count=1))
            report[group]['states'][sid]=new
    assert sum(x['total'] for x in report.values())==136000000
    (R/'tools/population_1893.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__=='__main__':
    apply_layout(); population()
    print('Repositioned focus trees; balanced 10 geographic population groups to 136,000,000.')
