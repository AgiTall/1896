from pathlib import Path
import re
from validate_philippines_rework import parse,value
from split_localisation import entries
R=Path(__file__).resolve().parents[1]
focus=(R/'common/national_focus/a03_focus.txt').read_text()
fs={value(v,'id'):v for k,o,v in value(parse(focus),'focus_tree') if k=='focus'}
assert len(fs)==11
assert [value(fs['JSM_'+suffix],'cost') for suffix in ('steel','workshops','shipyards','council','north','south','ocean')]==['20','20','15','5','5','5','5']
gfx='\n'.join(p.read_text(encoding='utf-8-sig') for base in (R,Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')) for p in (base/'interface').rglob('*.gfx'))
for icon in re.findall(r'icon = (\w+)',focus):assert '"'+icon+'"' in gfx,icon
for lang in ('russian','english'):
    loc=entries(sorted((R/'localisation'/lang).glob('*.yml')))
    for key in re.findall(r'\bid = (JSM_\w+)',focus):assert key in loc and key+'_desc' in loc
for name in ('common/national_focus/a03_focus.txt','common/decisions/JSM_story.txt','common/decisions/categories/JSM_story.txt','events/JSM_story.txt'):
    text=(R/name).read_text(); assert text.count('{')==text.count('}'),name
print('PASS: 11 focuses, original timing, icons, both languages and balanced scripts')
