"""Consolidate root localisation, preserving the current sorted override order.

The replace directory keeps its separate engine priority. Run again after using
legacy content generators that still emit their own localisation files.
"""
from pathlib import Path
from collections import defaultdict
import re,json,shutil,hashlib
R=Path(__file__).resolve().parents[1]
B=R/'tools/backups/localisation_before_compaction_20261013'
ENTRY=re.compile(r'^\s*([^\s:]+):\d*\s+".*"\s*(?:#.*)?$')
def load(paths,language):
 entries={};count=0
 for p in paths:
  for number,line in enumerate(p.read_text(encoding='utf-8-sig').splitlines(),1):
   if not line.strip() or line.lstrip().startswith('#'):continue
   if line.strip() in ('l_'+language+':','цl_'+language+':'):continue
   m=ENTRY.fullmatch(line)
   if not m:raise ValueError((p,number,line))
   entries[m[1]]=line.strip();count+=1
 return entries,count
def section(key):
 if key.startswith(('A03_','JPC_','JPF_','JPN_','JPL_','JPA_','JPS_','JPX_','japan_','japan.')):return 'Japan'
 if key.startswith(('A01_','A01.','ludolf','royal','crown','borneo','sabah')):return 'Netherlands and Borneo'
 if key.startswith(('WTC_','wtc_','wtc.')):return 'Trade Chamber'
 if key.startswith(('A10_','A10.','philipp','luzon')):return 'Philippines'
 if key.startswith(('STATE_','STRATEGICREGION_')):return 'Geography'
 return 'World and shared content'
report={};names=set()
for lang in ('russian','english'):
 folder=R/'localisation'/lang;paths=sorted(folder.glob('*.yml'))
 before,count=load(paths,lang);groups=defaultdict(list)
 for key in before:groups[section(key)].append(key)
 text='l_'+lang+':\n'
 for title in sorted(groups):
  text+='\n # '+title+'\n'+''.join(' '+before[k]+'\n' for k in sorted(groups[title]))
 target=folder/f'1896_main_l_{lang}.yml'
 # Validate the prepared result before removing any old files.
 for p in paths:
  backup=B/p.relative_to(R)
  if not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
 target.write_text(text,encoding='utf-8-sig',newline='\n')
 after,_=load([target],lang);assert after==before
 for p in paths:
  names.add(p.name)
  if p!=target:p.unlink()
 report[lang]={'files_before':len(paths),'files_after':1,'unique_keys':len(before),'duplicate_definitions_removed':count-len(before),'values_preserved':True,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
# Existing validators should inspect the consolidated source.
# Legacy one-time generators are retained; rerun this tool after using them.
for p in (R/'tools').glob('validate*.py'):
 old=p.read_text(encoding='utf-8-sig');new=old
 for name in names:
  lang='russian' if name.endswith('_russian.yml') else 'english'
  new=new.replace(name,'1896_main_l_'+lang+'.yml')
  stem=name.removesuffix('_l_'+lang+'.yml')
  new=new.replace(stem+'_l_{lang}.yml','1896_main_l_{lang}.yml')
 if new!=old:
  backup=B/p.relative_to(R)
  if not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
  p.write_text(new,encoding='utf-8')
(R/'tools/localisation_compaction.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
