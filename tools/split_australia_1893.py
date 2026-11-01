"""Six Australian colonies on 1 January 1893, using existing map regions."""
from pathlib import Path
import re, shutil, json
from fix_1893_start import repair_country_start, technology_data
R=Path(__file__).resolve().parents[1]
B=R/'tools/backups/australia_before_split_1893'
COLONIES={
 'A07':dict(en='New South Wales',ru='Новый Южный Уэльс',adj='Новоюжноуэльск.',capital=285,city='Sydney',states=[285],leader='George Dibbs',leader_ru='Джордж Диббс',color=(40,108,111)),
 'AVC':dict(en='Victoria',ru='Виктория',adj='Викторианск.',capital=517,city='Melbourne',states=[517],leader='William Shiels',leader_ru='Уильям Шилс',color=(58,76,145)),
 'AQL':dict(en='Queensland',ru='Квинсленд',adj='Квинслендск.',capital=521,city='Brisbane',states=[521,872,873,1075],leader='Samuel Griffith',leader_ru='Сэмюэл Гриффит',color=(148,48,69)),
 'ASA':dict(en='South Australia',ru='Южная Австралия',adj='Южноавстралийск.',capital=519,city='Adelaide',states=[519,520,674],leader='John Downer',leader_ru='Джон Даунер',color=(185,142,66)),
 'AWA':dict(en='Western Australia',ru='Западная Австралия',adj='Западноавстралийск.',capital=522,city='Perth',states=[522,870,871,1074],leader='John Forrest',leader_ru='Джон Форрест',color=(86,128,70)),
 'ATA':dict(en='Tasmania',ru='Тасмания',adj='Тасманийск.',capital=518,city='Hobart',states=[518],leader='Henry Dobson',leader_ru='Генри Добсон',color=(139,92,153)),
}
def write(relative,text,bom=False):
    p=R/relative
    if p.exists():
        dest=B/relative;dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():shutil.copy2(p,dest)
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8-sig' if bom else 'utf-8')
def main():
    tech = technology_data()
    files={int(re.search(r'\bid\s*=\s*(\d+)',p.read_text(encoding='utf-8-sig'))[1]):p for p in (R/'history/states').glob('*.txt')}
    for tag,c in COLONIES.items():
        for sid in c['states']:
            p=files[sid];text=p.read_text(encoding='utf-8-sig').replace('owner = A07',f'owner = {tag}').replace('add_core_of = A07',f'add_core_of = {tag}')
            write(str(p.relative_to(R)),text)
        if tag!='A07':
            color=' '.join(map(str,c['color']))
            write(f'common/countries/{tag}.txt',f'graphical_culture = western_european_gfx\ngraphical_culture_2d = western_european_2d\ncolor = rgb {{ {color} }}\n')
            write(f'common/characters/{tag}.txt',f'characters = {{ {tag}_premier = {{ name = {tag}_premier_name country_leader = {{ ideology = conservatism expire = "1965.1.1.1" traits = {{ }} }} }} }}\n')
            history=f'''# Self-governing British colony, 1 January 1893.
capital = {c['capital']}
recruit_character = {tag}_premier
set_politics = {{ ruling_party = democratic elections_allowed = yes }}
set_popularities = {{ democratic = 100 }}
set_research_slots = 2
set_stability = 0.55
set_war_support = 0.20
set_convoys = 5
set_technology = {{ infantry_weapons = 1 construction0 = 1 early_machine_tools = 1 mechanical_engineering = 1 basic_railways = 1 basic_train = 1 }}
add_ideas = volunteer_only
add_ideas = civilian_economy
add_ideas = limited_exports
'''
            history, _ = repair_country_start(history, tag, tech)
            write(f'history/countries/{tag} - {c["en"]}.txt',history,True)
    write('common/country_tags/04_australian_colonies.txt',''.join(f'{tag} = "countries/{tag}.txt"\n' for tag in COLONIES if tag!='A07'))
    # British New Guinea was not territory of a federated Australian state in 1893.
    p=files[523];text=p.read_text(encoding='utf-8-sig').replace('owner = A07','owner = A02').replace('  add_core_of = A07\n','')
    write(str(p.relative_to(R)),text)
    p=R/'history/countries/A07 - Placeholder.txt';text=p.read_text(encoding='utf-8-sig').replace('ruling_party = neutrality elections_allowed = no','ruling_party = democratic elections_allowed = yes').replace('set_popularities = { neutrality = 100 }','set_popularities = { democratic = 100 }')
    write(str(p.relative_to(R)),text)
    p=files[285];text=p.read_text(encoding='utf-8-sig')
    text=re.sub(r'(victory_points\s*=\s*\{\s*7859\s+)30',r'\g<1>5',text)
    text=re.sub(r'(victory_points\s*=\s*\{\s*12406\s+)20',r'\g<1>30',text)
    write(str(p.relative_to(R)),text)
    p=R/'history/units/A07_1893.txt';write(str(p.relative_to(R)),p.read_text(encoding='utf-8-sig').replace('location = 7859','location = 12406'))
    p=R/'common/characters/A07_canon.txt'
    candidates=[p for p in (R/'common/characters').glob('A07*.txt') if 'A07_canon_leader = ' in p.read_text(encoding='utf-8-sig')]
    assert len(candidates)==1
    p=candidates[0];write(str(p.relative_to(R)),p.read_text(encoding='utf-8-sig').replace('ideology = despotism','ideology = conservatism'))
    write('common/autonomous_states/AUC_colony.txt','''autonomy_state = {
 id = AUC_self_governing_colony
 is_puppet = yes
 use_overlord_color = no
 min_freedom_level = 0.5
 rule = { desc = AUC_self_governing_colony_desc can_not_declare_war = yes can_decline_call_to_war = yes units_deployed_to_overlord = no can_create_collaboration_government = no }
 allowed = { OVERLORD = { tag = A02 } }
 can_take_level = { always = no }
 can_lose_level = { always = no }
 ai_subject_wants_higher = { factor = 0 }
 ai_overlord_wants_lower = { factor = 0 }
 ai_overlord_wants_garrison = { always = no }
}
''')
    effects='on_actions = { on_startup = { effect = { A02 = { if = { limit = { NOT = { has_country_flag = AUC_colonies_initialized } } set_country_flag = AUC_colonies_initialized\n'
    for tag in COLONIES:effects+=f' if = {{ limit = {{ country_exists = {tag} {tag} = {{ is_subject = no }} }} set_autonomy = {{ target = {tag} autonomy_state = AUC_self_governing_colony freedom_level = 0.5 }} }}\n'
    write('common/on_actions/AUC_colonies.txt',effects+'} } } } }\n')
    colors=R/'common/countries/colors.txt';text=colors.read_text(encoding='utf-8-sig')
    for tag,c in COLONIES.items():
        if tag=='A07':continue
        color=' '.join(map(str,c['color']));text+=f'\n{tag} = {{ color = rgb {{ {color} }} color_ui = rgb {{ {color} }} }}\n'
    write(str(colors.relative_to(R)),text)
    for lang in ('russian','english'):
        folder=R/'localisation'/lang
        p=folder/f'1896_countries_l_{lang}.yml';text=p.read_text(encoding='utf-8-sig')
        c=COLONIES['A07'];name=c['ru'] if lang=='russian' else c['en'];adj=c['adj'] if lang=='russian' else 'New South Welsh'
        for key,value in {'A07':name,'A07_DEF':name,'A07_ADJ':adj,'A07_neutrality':name,'A07_neutrality_DEF':name,'A07_neutrality_ADJ':adj,'A07_democratic':name,'A07_democratic_DEF':name,'A07_democratic_ADJ':adj}.items():
            line=f' {key}:0 "{value}"'
            if re.search(rf'^\s*{key}:',text,re.M):text=re.sub(rf'^\s*{key}:.*$',lambda m:line,text,flags=re.M)
            else:text+='\n'+line+'\n'
        write(str(p.relative_to(R)),text,True)
        p=folder/f'1896_characters_l_{lang}.yml';text=p.read_text(encoding='utf-8-sig');name=c['leader_ru'] if lang=='russian' else c['leader']
        text=re.sub(r'^\s*A07_canon_leader_name:.*$',lambda m:f' A07_canon_leader_name:0 "{name}"',text,flags=re.M)
        write(str(p.relative_to(R)),text,True)
        lines=['l_'+lang+':']
        for tag,c in COLONIES.items():
            if tag=='A07':continue
            name=c['ru'] if lang=='russian' else c['en'];adj=c['adj'] if lang=='russian' else c['en']
            for suffix in ('','_DEF','_neutrality','_neutrality_DEF','_democratic','_democratic_DEF'):lines.append(f' {tag}{suffix}:0 "{name}"')
            for suffix in ('_ADJ','_neutrality_ADJ','_democratic_ADJ'):lines.append(f' {tag}{suffix}:0 "{adj}"')
        write(f'localisation/{lang}/AUC_countries_l_{lang}.yml','\n'.join(lines)+'\n',True)
        lines=['l_'+lang+':']
        for tag,c in COLONIES.items():
            if tag!='A07':lines.append(f' {tag}_premier_name:0 "{c["leader_ru"] if lang=="russian" else c["leader"]}"')
        lines+=[' AUC_self_governing_colony:0 "'+('Самоуправляющаяся колония' if lang=='russian' else 'Self-governing colony')+'"',' AUC_self_governing_colony_desc:0 "'+('Собственное колониальное правительство под верховной властью британской короны.' if lang=='russian' else 'A local colonial government under the sovereignty of the British Crown.')+'"']
        write(f'localisation/{lang}/AUC_governments_l_{lang}.yml','\n'.join(lines)+'\n',True)
        p=folder/f'1896_misc_l_{lang}.yml';text=p.read_text(encoding='utf-8-sig')
        desc=('§YНовый Южный Уэльс§!\\n\\nНа 1 января 1893 года Австралия состоит из шести самоуправляющихся британских колоний. Правительство Джорджа Диббса заседает в Сиднее. Южная Австралия управляет Северной территорией; общего австралийского государства ещё нет.' if lang=='russian' else '§YNew South Wales§!\\n\\nOn 1 January 1893 Australia consists of six self-governing British colonies. George Dibbs leads the government in Sydney. South Australia administers the Northern Territory; no Australian federation exists yet.')
        text=re.sub(r'^\s*A07_CANON_START_DESC:.*$',lambda m:f' A07_CANON_START_DESC:0 "{desc}"',text,flags=re.M)
        write(str(p.relative_to(R)),text,True)
    p=R/'common/bookmarks/the_gathering_storm.txt';text=p.read_text(encoding='utf-8-sig')
    new=''.join(f' "{tag}" = {{ minor = yes ideology = democratic ideas = {{ }} focuses = {{ }} }}\n' for tag in COLONIES if tag!='A07')
    text=text.replace('"A07" = { history = "A07_CANON_START_DESC" ideology = neutrality','"A07" = { history = "A07_CANON_START_DESC" ideology = democratic')
    text=text.replace(' "---" =',new+' "---" =')
    write(str(p.relative_to(R)),text)
    (R/'tools/australia_1893_manifest.json').write_text(json.dumps(COLONIES,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Installed 6 colonies; Northern Territory assigned to South Australia; British New Guinea to A02.')
if __name__=='__main__':main()
