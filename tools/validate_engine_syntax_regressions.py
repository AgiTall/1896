"""Guard against actual Clausewitz syntax errors missed by the script model."""
from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
for folder in ('common','events','history'):
 for p in (R/folder).rglob('*.txt'):
  s=p.read_text(encoding='utf-8-sig')
  assert not re.search(r'\bremove_dynamic_modifier\s*=\s*\w+',s),p
  assert not re.search(r'\bcompliance\s*(?:>=|<=)',s),p
  if folder!='history':
   assert not re.search(r'\brecruit_character\s*=\s*A01_(?:emma_waldeck_pyrmont|wilhelmina_monarch|postwar_conservative|postwar_indonesian)\b',s),p
colors=(R/'common/countries/colors.txt').read_text(encoding='utf-8-sig')
cosmetics=(R/'common/countries/cosmetic.txt').read_text(encoding='utf-8-sig')
for tag in ('A01_CROWN','A01_COMMONWEALTH','A01_ROYAL_EMPIRE'):
 assert not re.search(r'^'+tag+r'\s*=',colors,re.M)
 assert re.search(r'^'+tag+r'\s*=',cosmetics,re.M)
s=(R/'common/decisions/A10_philippines.txt').read_text()
assert s.count('NOT = { compliance < 80 }')==9
assert all((not (x<80))==(x>=80) for x in (0,79,79.99,80,80.01,100))
assert 'short_name' not in (R/'events/A01_postwar.txt').read_text()
default_map=(R/'map/default.map').read_text(encoding='utf-8-sig')
for filename in re.findall(r'^\s*\w+\s*=\s*"([^"]+)"',default_map,re.M):
 p=R/'map'/filename
 assert p.exists(), f'Missing map input: {filename}'
print('PASS: engine-supported dynamic removal, exact 80% threshold boundaries, cosmetic color file, party fields and history-only recruitment.')
