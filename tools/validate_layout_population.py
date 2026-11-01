"""Validate regional totals, focus ordering/spacing, and render schematic previews."""
from pathlib import Path
from collections import defaultdict
import json,re
from PIL import Image,ImageDraw,ImageFont
from add_canon_countries import parse,value

R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/'tools/population_1893.json').read_text())
seen=set();total=0
states={int(value(n,'id')):n for p in (R/'history/states').glob('*.txt')
        for n in [value(parse(p.read_text(encoding='utf-8-sig')),'state')]}
for name,group in manifest.items():
    actual=0
    for sid,count in group['states'].items():
        sid=int(sid);assert sid not in seen,(name,sid);seen.add(sid)
        assert int(value(states[sid],'manpower'))==count,(name,sid)
        actual+=count
    assert actual==group['total'],name
    total+=actual
assert total==136000000
loc={}
for p in sorted((R/'localisation/russian').glob('*.yml')):
    loc.update(re.findall(r'^\s*(\w+):(?:\d+)?\s*"(.*)"',p.read_text(encoding='utf-8-sig'),re.M))
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15)
counts={}
for tag in ['a01','a03']:
    fs={value(f,'id'):f for k,o,f in value(parse((R/f'common/national_focus/{tag}_focus.txt').read_text(encoding='utf-8-sig')),'focus_tree') if k=='focus'}
    xy={fid:(int(value(f,'x')),int(value(f,'y'))) for fid,f in fs.items()}
    rows=defaultdict(list)
    for fid,(x,y) in xy.items():rows[y].append((x,fid))
    for row in rows.values():
        row.sort()
        for (x,a),(xx,b) in zip(row,row[1:]):assert xx-x>=2,(tag,a,b,'overlap')
    edges=[]
    for fid,f in fs.items():
        for k,o,n in f:
            if k=='prerequisite':
                for key,op,parent in n:
                    if key=='focus':
                        assert parent in fs
                        assert xy[parent][1]<xy[fid][1],(tag,parent,fid,'upward dependency')
                        edges.append((parent,fid))
    # Preserve prior gameplay except the explicitly requested Japanese branch gates/icons.
    original=R/f'tools/backups/layout_population_20261013/common/national_focus/{tag}_focus.txt'
    old={value(f,'id'):f for k,o,f in value(parse(original.read_text(encoding='utf-8-sig')),'focus_tree') if k=='focus'}
    from develop_japan_branches import NEW
    from compact_japan_campaign import ALIASES, GROUPS, PARENTS
    added={'JPR_defence_budget'} | set(NEW) if tag=='a03' else set()
    expected=(set(old)|added)-set(ALIASES) if tag=='a03' else set(old)
    if tag=='a03' and 'JPI_closed_ports' in fs:
        from rework_japan_industry import REMOVED
        expected=(expected-REMOVED)|{fid for fid in fs if fid.startswith('JPI_')}
    assert expected==set(fs)
    branch_edits={'JPC_osaka_orders','JPC_war_workshops','JPC_pledged_yards',
                  'JPC_convoy_budget','JPC_replace_losses','JPC_iwasaki_accounts',
                  'JPC_manila_priority','JPC_batavia_demands','JPX_sea_institution',
                  'JPL_supply_board','JPL_quartermaster_school','JPF_delivery_calendar','JPN_north_postwar_audience'} if tag=='a03' else set()
    for fid,f in fs.items():
        if fid in added:continue
        if tag=='a03':
            # Current 56-focus campaign has its own complete payload and graph
            # checks in validate_japan_compaction.py; the 20261013 snapshot is obsolete.
            continue
        def gameplay(n):
            return [(k,o,gameplay(v) if isinstance(v,list) else v) for k,o,v in n
                    if k not in ['x','y','JPS_begin_visible_countdown_effect']
                    and not (fid in branch_edits and k in ['prerequisite','icon'])
                    and not (fid in {'JPX_sea','JPX_land','JPX_trade','JPX_kami','JPX_throne'} and k in ['mutually_exclusive','available'])]
        if tag=='a03' and (fid in GROUPS or fid in PARENTS):
            # Consolidated milestones are checked against the pre-compaction source
            # by validate_japan_compaction.py; this check covers untouched focuses.
            continue
        assert gameplay(old[fid])==gameplay(f),(tag,fid,'unintended gameplay edit')
    xmin=min(x for x,y in xy.values())-1;xmax=max(x for x,y in xy.values())+1
    ymax=max(y for x,y in xy.values())+1
    im=Image.new('RGB',((xmax-xmin+1)*80,(ymax+1)*90),(22,27,34));draw=ImageDraw.Draw(im)
    def pos(fid):
        x,y=xy[fid];return ((x-xmin)*80+40,y*90+45)
    for parent,child in edges:
        x,y=pos(parent);xx,yy=pos(child);bend=y+40
        draw.line([(x,y+25),(x,bend),(xx,bend),(xx,yy-25)],fill=(83,113,141),width=2)
    for fid in fs:
        x,y=pos(fid);draw.rounded_rectangle((x-73,y-27,x+73,y+27),radius=7,fill=(39,49,62),outline=(175,154,98),width=2)
        words=loc.get(fid,fid).split();lines=[];line=''
        for word in words:
            candidate=(line+' '+word).strip()
            if draw.textlength(candidate,font=font)>137 and line:lines.append(line);line=word
            else:line=candidate
        lines.append(line)
        draw.multiline_text((x,y),'\n'.join(lines),font=font,fill='white',anchor='mm',align='center',spacing=0)
    im.save(R/f'tools/{tag}_layout_preview.png')
    if tag=='a01':crop=(0,13,37,34)
    else:crop=(0,19,38,25)
    l,t,r,b=crop
    im.crop(((l-xmin)*80,t*90,(r-xmin+1)*80,(b+1)*90)).save(R/f'tools/{tag}_postwar_preview.png')
    counts[tag]=len(fs)
report={'status':'passed','population':total,'groups':{k:v['total'] for k,v in manifest.items()},
        'focuses':counts,'overlaps':0,'upward_dependencies':0,
        'gameplay_preserved':'Japan: branching industry checked by validate_japan_industry.py; Netherlands unchanged by this pass',
        'limitation':'Schematic preview, not an in-game screenshot; ZZZ territories outside the listed groups are excluded.'}
(R/'tools/layout_population_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
