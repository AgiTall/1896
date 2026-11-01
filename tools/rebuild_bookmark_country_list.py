"""Keep seven featured countries above the complete, unfiltered minor list."""
from pathlib import Path
import re,shutil
R=Path(__file__).resolve().parents[1]
MAJORS=['A01','A03','A02','A06','A07','A04','PHW']
def main():
    tags=[]
    for p in sorted((R/'common/country_tags').glob('*.txt')):
        tags+=re.findall(r'^\s*([A-Z0-9]{3})\s*=\s*"',p.read_text(encoding='utf-8-sig'),re.M)
    tags=list(dict.fromkeys(t for t in tags if t!='ZZZ'))
    minors=[t for t in tags if t not in MAJORS]
    old=R/'common/bookmarks/the_gathering_storm.txt'
    dest=R/'tools/backups/bookmarks_before_all_countries/the_gathering_storm.txt';dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():shutil.copy2(old,dest)
    text='''bookmarks = {
 bookmark = {
  name = "SONG_EARTH_1893_NAME"
  desc = "SONG_EARTH_1893_DESC"
  date = 1893.1.1.12
  picture = "GFX_select_date_1936"
  default_country = "A01"
  default = yes
  sort_unplayed_first = no
  filters = { }
  include_majors_in_minor_list = no
  scrollable_country_list = yes

  # Seven featured countries plus Other: eight stock 150px slots.
'''
    keys={}
    for t in MAJORS+['---']+minors:
        if t=='---':text+='  "---" = { history = "PZ_OTHER_COUNTRIES_DESC" }\n\n  # All other mod countries, without region filters.\n';continue
        key=t+('_PACIFIC_START_DESC' if t in ('A01','A03') else '_CANON_START_DESC');keys[t]=key
        histories=list((R/'history/countries').glob(t+' - *.txt'));assert len(histories)==1,t
        history=histories[0].read_text(encoding='utf-8-sig')
        match=re.search(r'ruling_party\s*=\s*(\w+)',history);ideology=match[1] if match else 'neutrality'
        text+=f'  "{t}" = {{\n'
        if t in minors:text+='   minor = yes\n'
        text+=f'   history = "{key}"\n   ideology = {ideology}\n   version = base_game\n   ideas = {{'+(' A01_wilhelmina ' if t=='A01' else ' ')+'}\n'
        focus={'A01':'A01_constitution A01_java_development A01_knil_reform','A03':'JSM_steel JSM_workshops JSM_shipyards'}.get(t,'')
        text+=f'   focuses = {{ {focus} }}\n  }}\n'
    text+='  effect = { randomize_weather = 22345 }\n }\n}\n'
    old.write_text(text,encoding='utf-8')
    import sys
    sys.path.insert(0,str(R/'tools'))
    from split_localisation import entries
    for lang in ('russian','english'):
        folder=R/'localisation'/lang;loc=entries(sorted(folder.glob('*.yml')))
        additions=[]
        for t,key in keys.items():
            if key in loc:continue
            name_line=loc.get(t,loc.get(t+'_neutrality',f'{t}:0 "{t}"'))
            name=re.search(r'"(.*)"',name_line)[1]
            desc=(f'{name} сохраняет местную власть и собственные интересы в раздробленном мире. Морская торговля и отношения с соседями определят будущее государства.' if lang=='russian' else f'{name} maintains its own government and interests in a divided world. Maritime trade and relations with its neighbours will shape its future.')
            additions.append(f' {key}:0 "{desc}"')
        p=folder/f'1896_bookmarks_l_{lang}.yml';data=p.read_text(encoding='utf-8-sig')
        data=re.sub(r'^\s*PZ_SELECT_\w+:.*\n?', '',data,flags=re.M)
        if additions:data+='\n'+'\n'.join(additions)+'\n'
        p.write_text(data,encoding='utf-8-sig')
    assert len(MAJORS)+1==8 and (len(MAJORS)+1)*150<=1200
    assert len(minors)<=46
    assert set(MAJORS)|set(minors)==set(tags)
    assert set(MAJORS).isdisjoint(minors)
    assert text.count('{')==text.count('}')
    print(f'PASS: {len(MAJORS)} featured countries including Hawaii; {len(minors)} other countries below; no filters, duplicates or missing mod tags.')
if __name__=='__main__':main()
