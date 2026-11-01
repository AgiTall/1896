"""Split root localisation by game system; preserve resolved values and replace priority."""
from pathlib import Path
import re, shutil, json
from collections import defaultdict
R=Path(__file__).resolve().parents[1]
ENTRY=re.compile(r'^\s*([^\s:]+):\d*\s+".*"\s*(?:#.*)?$')
def entries(paths):
    result={}
    for p in paths:
        for line in p.read_text(encoding='utf-8-sig').splitlines():
            if not line.strip() or line.lstrip().startswith('#') or line.strip().startswith('l_'):continue
            m=ENTRY.fullmatch(line)
            if not m:raise ValueError((str(p),line))
            result[m[1]]=line.strip()
    return result
def main():
    types={}
    for folder,kind in [('common/ideas','ideas'),('common/characters','characters'),('common/decisions','decisions'),('common/national_focus','focus'),('events','events'),('common/country_leader','traits'),('common/unit_leader','traits')]:
        for p in (R/folder).rglob('*.txt'):
            text=p.read_text(encoding='utf-8-sig')
            pattern=r'\b(?:id|title|desc|name)\s*=\s*([\w.]+)' if kind in ('focus','events') else r'^\s*([\w.]+)\s*=\s*\{'
            for key in re.findall(pattern,text,re.M):types[key]=kind
            if kind=='characters':
                for key in re.findall(r'\bname\s*=\s*([\w.]+)',text):types[key]='characters'
    report={}
    for lang in ('russian','english'):
        folder=R/'localisation'/lang; paths=sorted(folder.glob('*.yml')); before=entries(paths); groups=defaultdict(dict)
        for key,value in before.items():
            base=key.removesuffix('_desc')
            if key.startswith(('STATE_','STRATEGICREGION_','VICTORY_POINTS_')):kind='state_names'
            elif re.fullmatch(r'[A-Z0-9]{3}(?:_(?:ADJ|DEF|neutrality|democratic|communism|fascism|neutrality_ADJ|neutrality_DEF|democratic_ADJ|democratic_DEF|communism_ADJ|communism_DEF|fascism_ADJ|fascism_DEF))?',key):kind='countries'
            elif 'party' in key:kind='parties'
            elif base in types:kind=types[base]
            elif key.endswith('_name') or 'commander' in key:kind='characters'
            elif re.search(r'\.\d+\.',key):kind='events'
            elif 'bookmark' in key:kind='bookmarks'
            elif 'trait' in key:kind='traits'
            elif 'modifier' in key:kind='modifiers'
            else:kind='misc'
            groups[kind][key]=value
        prepared={}
        for kind,items in groups.items():
            p=folder/f'1896_{kind}_l_{lang}.yml'
            prepared[p]='l_'+lang+':\n'+''.join(' '+items[k]+'\n' for k in sorted(items))
        for p in paths:
            backup=R/'tools/backups/localisation_before_split_20261019'/p.relative_to(R)
            backup.parent.mkdir(parents=True,exist_ok=True)
            if not backup.exists():shutil.copy2(p,backup)
        for p,text in prepared.items():p.write_text(text,encoding='utf-8-sig')
        assert entries(sorted(prepared))==before
        for p in paths:
            if p not in prepared:p.unlink()
        report[lang]={'keys':len(before),'files':{p.name:len(groups[kind]) for kind in groups for p in [folder/f'1896_{kind}_l_{lang}.yml']},'values_preserved':True}
    (R/'tools/localisation_split_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
