"""Idempotent, narrowly scoped integration into legacy Philippine/Japanese sources."""
from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
def edit(name,fn):
 p=R/name;s=p.read_text(encoding='utf-8-sig');new=fn(s)
 if new!=s:p.write_text(new,encoding='utf-8',newline='\n')

def fix_japan(s):
 lines=s.splitlines()
 for i,line in enumerate(lines):
  if 'id = japan_canon.4 ' in line:
   if 'A10 = { is_subject = no }' not in line:
    line=line.replace('country_exists = A10 NOT = { has_war_with = A10 }','country_exists = A10 A10 = { is_subject = no } NOT = { has_war_with = A10 }')
   if 'A10R_defensive_armistice' not in line:
    line=line.replace('A10 = { declare_war_on', 'A10 = { declare_war_on')
    line=line.replace('NOT = { A10 = { has_country_flag = A10_archipelago_peace_signed } }', 'NOT = { A10 = { has_country_flag = A10_archipelago_peace_signed } } NOT = { A10 = { has_country_flag = A10R_defensive_armistice } }')
   lines[i]=line
 return '\n'.join(lines)+'\n'
edit('events/JPC_canonical.txt',fix_japan)

members=[(624,'PVI'),(625,'PSM'),(627,'PMD'),(1026,'PNM'),(628,'PCB'),(1085,'PPN'),(623,'PNL'),(327,'PML'),(1027,'PBT')]
def gate_integration(s):
 for state,tag in members:
  marker=f'A10_integrate_{state} = {{'
  start=s.index(marker);end=s.index('complete_effect',start)
  block=s[start:end]
  if 'A10R_equal_rights' not in block:
   block=block.replace('available = {','available = { has_country_flag = A10R_equal_rights has_country_flag = A10R_consent_'+tag+' ',1)
   s=s[:start]+block+s[end:]
 return s
edit('common/decisions/A10_philippines.txt',gate_integration)
edit('common/decisions/categories/A10_philippines.txt',lambda s:s.replace('icon = generic_political_discourse','icon = generic_political_actions'))

cosmetics={'A10_FED':(52,126,166),'A10W_COLONY':(154,129,72),'A10W_METRO':(33,118,116),'A10W_PACIFIC':(52,137,130),'A10M_MILITARY':(114,56,53)}
def add_cosmetics(s):
 for tag,(r,g,b) in cosmetics.items():
  if not re.search(r'^'+tag+r'\s*=',s,re.M):s+=f'\n{tag} = {{ color = rgb {{ {r} {g} {b} }} color_ui = rgb {{ {r} {g} {b} }} }}\n'
 return s
edit('common/countries/cosmetic.txt',add_cosmetics)
print('Integrated subject/peace guards, consent gates, category icons and Philippine cosmetic colours.')
