"""Restore only A01 coordinates from its saved, authored October layout."""
import ast,json,hashlib
from pathlib import Path
from british_story_links import nodes,emit
from validate_philippines_rework import value

ROOT=Path(__file__).resolve().parents[1]

def restore():
    path=ROOT/'common/national_focus/a01_focus.txt'
    tree=nodes(path.read_text(encoding='utf-8-sig'));ft=value(tree,'focus_tree')
    fs={value(v,'id'):v for k,o,v in ft if k=='focus'}
    old=value(nodes((ROOT/'tools/backups/layout_population_20261013/common/national_focus/a01_focus.txt').read_text(encoding='utf-8-sig')),'focus_tree')
    source={value(v,'id'):v for k,o,v in old if k=='focus'};assert fs.keys()==source.keys()
    positions={k:(int(value(v,'x')),int(value(v,'y'))) for k,v in source.items()}
    royal={k for k,v in fs.items() if any(a=='allow_branch' and 'A01_royal_path_revealed' in str(c) for a,b,c in v)}|{'A01_crown_above_factions'}
    for key in royal:
        x,y=positions[key];positions[key]=(x+26,y+2)
    author=ast.parse((ROOT/'tools/rebalance_1893_layout_population.py').read_text(encoding='utf-8-sig'))
    fn=next(n for n in author.body if isinstance(n,ast.FunctionDef) and n.name=='apply_layout')
    rows=next(ast.literal_eval(n.value) for n in fn.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='rows' for t in n.targets))
    for y,row in rows.items():
        for key,x in row.items():positions['A01_'+key]=(x,y)
    payload=lambda f:[e for e in f if e[0] not in ('x','y')]
    before={k:payload(v) for k,v in fs.items()}
    for key,f in fs.items():
        for axis,n in zip(('x','y'),positions[key]):
            f[:]=[(k,o,str(n) if k==axis else v) for k,o,v in f]
    assert all(payload(f)==before[key] for key,f in fs.items())
    assert positions['A01_constitution']==(16,0) and positions['A01_wtc_oil_and_rubber_offer']==(3,16)
    path.write_text(emit(tree)+'\n',encoding='utf-8')
    record=dict(file='common/national_focus/a01_focus.txt',sha256=hashlib.sha256(path.read_bytes()).hexdigest(),positions=positions,source='Saved 132-focus source plus its authored layout_population_20261013 coordinate revision. No gameplay replacement.')
    (ROOT/'tools/dutch_reference_layout.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Restored all 132 Dutch focus positions; current focus effects, prerequisites and text preserved.')

if __name__=='__main__':restore()
