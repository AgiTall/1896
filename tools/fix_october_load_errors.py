"""Repair syntax rejected by the user's actual HOI4 engine load."""
from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
for directory in ('common','events','history'):
 for p in (R/directory).rglob('*.txt'):
  s=p.read_text(encoding='utf-8-sig')
  t=re.sub(r'\bremove_dynamic_modifier\s*=\s*(\w+)',r'remove_dynamic_modifier = { modifier = \1 }',s)
  t=t.replace('compliance >= 80','NOT = { compliance < 80 }')
  if p.name=='A01_postwar.txt' and directory=='events':
   t=t.replace('short_name =','name =')
  if directory!='history':
   t=re.sub(r'\brecruit_character\s*=\s*A01_(?:emma_waldeck_pyrmont|wilhelmina_monarch|postwar_conservative|postwar_indonesian)\b','',t)
  if t!=s:p.write_text(t,encoding='utf-8')
colors=R/'common/countries/colors.txt'
s=colors.read_text(encoding='utf-8-sig')
cosmetics=re.findall(r'(?m)^A01_(?:CROWN|COMMONWEALTH|ROYAL_EMPIRE)\s*=\s*\{[^\n]+',s)
s=re.sub(r'(?m)^A01_(?:CROWN|COMMONWEALTH|ROYAL_EMPIRE)\s*=\s*\{[^\n]+\n?','',s)
colors.write_text(s,encoding='utf-8')
# Preserve vanilla cosmetic definitions because this file overrides its base-game counterpart.
p=R/'common/countries/cosmetic.txt'
s=p.read_text(encoding='utf-8-sig') if p.exists() else Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV/common/countries/cosmetic.txt').read_text(encoding='utf-8-sig')
for entry in cosmetics:
 if entry.split('=')[0].strip()+' =' not in s:s+='\n'+entry+'\n'
p.write_text(s,encoding='utf-8')
p=R/'history/countries/A01 - Placeholder.txt';s=p.read_text(encoding='utf-8-sig')
for char in ('emma_waldeck_pyrmont','wilhelmina_monarch','postwar_conservative','postwar_indonesian'):
 line=f'recruit_character = A01_{char}'
 if line not in s:s+='\n'+line+'\n'
s+='\npromote_character = A01_ludolf_sloot_van_de_beele\n' if not s.rstrip().endswith('promote_character = A01_ludolf_sloot_van_de_beele') else ''
p.write_text(s,encoding='utf-8')
print('Repaired dynamic removal blocks, exact 80% gate, party names, cosmetic color placement and history-only character recruitment.')
