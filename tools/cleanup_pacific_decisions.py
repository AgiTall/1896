"""Remove the obsolete generic Pacific preparation menu, retaining a backup."""
from pathlib import Path
import re,shutil
from add_canon_countries import parse,dump
R=Path(__file__).resolve().parents[1]
removed={f'{tag}_pacific_{suffix}' for tag in ('A01','A03') for suffix in ('preparations','training','convoys','reserves')}
def backup(p):
    b=R/'tools/backups/pacific_decision_cleanup'/p.relative_to(R)
    b.parent.mkdir(parents=True,exist_ok=True)
    if not b.exists():shutil.copy2(p,b)
p=R/'common/decisions/pacific_preparations.txt'
if p.exists():backup(p);p.unlink()
p=R/'common/decisions/categories/A01_story_categories.txt';backup(p)
t=parse(p.read_text(encoding='utf-8-sig'));t=[n for n in t if n[0] not in removed]
p.write_text(dump(t)+'\n',encoding='utf-8')
for lang in ('russian','english'):
    for p in (R/f'localisation/{lang}').glob('*.yml'):
        s=p.read_text(encoding='utf-8-sig')
        new=''.join(line for line in s.splitlines(keepends=True) if not any(re.match(r'^\s*'+re.escape(k)+r'(?:_desc)?:',line) for k in removed))
        if new!=s:backup(p);p.write_text(new,encoding='utf-8-sig')
for filename in ('validate_pacific.py','validate_ludolf_story.py'):
    p=R/'tools'/filename;backup(p);s=p.read_text(encoding='utf-8-sig')
    s=s.replace("ROOT/'common/decisions/pacific_preparations.txt',",'').replace("'pacific_preparations.txt',",'')
    p.write_text(s,encoding='utf-8')
p=R/'tools/validate_colonial_constraints.py';backup(p);s=p.read_text(encoding='utf-8-sig')
start=s.index("decisions = v.parse(v.read('common/decisions/pacific_preparations.txt'))")
end=s.index("for lang in ['russian', 'english']:",start)
s=s[:start]+"assert not (R/'common/decisions/pacific_preparations.txt').exists(), 'Obsolete preparation decisions returned'\n"+s[end:]
s=s.replace('One-time reserve recruitment','Obsolete preparation decisions removed')
p.write_text(s,encoding='utf-8')
scripts='\n'.join(p.read_text(encoding='utf-8-sig') for folder in ('common','events') for p in (R/folder).rglob('*.txt'))
assert not any(re.search(r'\b'+re.escape(k)+r'\b',scripts) for k in removed)
print('Removed six decisions, two categories and RU/EN localisation; no live script references remain.')
