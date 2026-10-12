from pathlib import Path
import re,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
GAME=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
errors=[];counts={}
def clean(t): return re.sub(r'"(?:\\.|[^"\\])*"|#[^\n]*','',t)
def blocks(t,key):
    for m in re.finditer(r'\b'+re.escape(key)+r'\s*=\s*\{',t):
        depth=1;i=m.end();start=i
        while i<len(t) and depth:
            depth+=(t[i]=='{')-(t[i]=='}');i+=1
        yield t[start:i-1]
def texts(folder,ext):
    return '\n'.join(p.read_text(encoding='utf-8-sig',errors='replace') for p in folder.rglob('*'+ext))
gfx=texts(GAME/'interface','.gfx')+'\n'+texts(ROOT/'interface','.gfx')
sprite=set(re.findall(r'name\s*=\s*"(GFX_[^"]+)"',gfx))
loc={lang:set(re.findall(r'^\s+([^\s:#]+):',texts(ROOT/'localisation'/lang,'.yml'),re.M)) for lang in ['russian','english']}
for tag in ['A01','A03']:
    p=ROOT/f'common/national_focus/{tag.lower()}_focus.txt';t=p.read_text(encoding='utf-8-sig')
    focuses=list(blocks(t,'focus')); ids=[];coords=set();graph={}
    for b in focuses:
        ident=re.search(r'\bid\s*=\s*(\w+)',b).group(1);ids.append(ident)
        icon=re.search(r'\bicon\s*=\s*(\w+)',b).group(1)
        if icon not in sprite: errors.append(f'{ident}: missing icon {icon}')
        for lang in ['russian','english']:
            if ident not in loc[lang] or ident+'_desc' not in loc[lang]:errors.append(f'{ident}: missing {lang} localisation')
        pos=tuple(int(re.search(r'\b'+axis+r'\s*=\s*(\d+)',b).group(1)) for axis in ['x','y'])
        if pos in coords:errors.append(f'{tag}: overlapping focus at {pos}')
        coords.add(pos)
        graph[ident]=re.findall(r'\bfocus\s*=\s*(A\d+_\w+)',b)
    if len(ids)!=len(set(ids)):errors.append(f'{tag}: duplicate focus id')
    for ident,refs in graph.items():
        for ref in refs:
            if ref not in ids:errors.append(f'{ident}: missing prerequisite {ref}')
    def visit(ident,path):
        if ident in path: errors.append(f'{ident}: prerequisite cycle');return
        # Mutual exclusions are not prerequisite edges.
        b=focuses[ids.index(ident)]
        for pr in blocks(b,'prerequisite'):
            ref=re.search(r'focus\s*=\s*(\w+)',pr).group(1)
            if ref in ids:visit(ref,path+[ident])
    for ident in ids:visit(ident,[])
    counts[tag+'_focuses']=len(ids)

states={}; provinces={};ports={}
for p in (ROOT/'history/states').glob('*.txt'):
    t=p.read_text(encoding='utf-8-sig');idmatch=re.search(r'\bid\s*=\s*(\d+)',t)
    if not idmatch:continue
    sid=int(idmatch.group(1)); owner=re.search(r'\bowner\s*=\s*(\w+)',t)
    if owner:states[sid]=owner.group(1)
    for b in blocks(t,'provinces'):
        for prov in re.findall(r'\d+',b):provinces[int(prov)]=sid
    for m in re.finditer(r'(\d+)\s*=\s*\{\s*naval_base\s*=\s*(\d+)',t):ports[int(m.group(1))]=int(m.group(2))
for p in (ROOT/'history/units').glob('A0[13]*.txt'):
    tag=p.name[:3];t=p.read_text(encoding='utf-8-sig')
    for prov in re.findall(r'\blocation\s*=\s*(\d+)',t):
        sid=provinces.get(int(prov))
        if states.get(sid)!=tag:errors.append(f'{p.name}: location {prov} is not owned by {tag}')
    for prov in re.findall(r'\bnaval_base\s*=\s*(\d+)',t):
        if int(prov) not in ports:errors.append(f'{p.name}: missing naval base {prov}')

tech=texts(GAME/'common/technologies','.txt')+'\n'+texts(ROOT/'common/technologies','.txt')
techids=set(re.findall(r'\b(\w+)\s*=\s*\{',tech))
for p in (ROOT/'history/countries').glob('A0[13]*.txt'):
    for b in blocks(p.read_text(encoding='utf-8-sig'),'set_technology'):
        for key in re.findall(r'\b(\w+)\s*=\s*1',b):
            if key not in techids:errors.append(f'{p.name}: invalid technology {key}')
for p in [ROOT/'common/national_focus/a01_focus.txt',ROOT/'common/national_focus/a03_focus.txt',ROOT/'common/ideas/pacific_ideas.txt',ROOT/'events/pacific_diplomacy.txt',ROOT/'events/A01_japan_events.txt',ROOT/'common/decisions/A01_inevitable_conflict.txt']:
    depth=0
    for c in clean(p.read_text(encoding='utf-8-sig')):
        depth+=(c=='{')-(c=='}')
        if depth<0:break
    if depth:errors.append(f'{p.name}: unbalanced braces')
for p in (ROOT/'gfx/interface').glob('*/**/*pacific*.dds'):
    im=Image.open(p)
    if im.mode!='RGBA':errors.append(f'{p.name}: missing alpha')
    if im.getextrema()[3][0]!=0:errors.append(f'{p.name}: no transparent pixels')
report={'checks':['focus IDs, references, cycles, coordinates, RU/EN localisation, sprite definitions','unit location ownership and naval ports','starting technologies against installed game','script braces and DDS alpha'],'counts':counts,'errors':errors,'runtime_test':'Not run; static validation does not replace an in-game campaign.'}
(ROOT/'tools/pacific_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
