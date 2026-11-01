"""Apply the author's corrected timeline; stable IDs preserve existing references.

Run after the legacy year builders. The checked-in source JSON is extracted from
the supplied DOCX, never executed as instructions. Later years retain their events
except for explicit contradictions addressed by this revision.
"""
from pathlib import Path
from datetime import datetime, timedelta
import json, re

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return (ROOT/path).read_text(encoding='utf-8-sig')

def write(path, text):
    (ROOT/path).write_text(text, encoding='utf-8-sig' if str(path).endswith('.yml') else 'utf-8')

def block(text, marker):
    start = text.index(marker)
    opening = text.index('{', start)
    depth = 1
    end = opening+1
    while depth:
        depth += (text[end]=='{')-(text[end]=='}')
        end += 1
    return start, end

def replace_block(text, marker, replacement):
    a,b = block(text, marker)
    return text[:a]+replacement+text[b:]

def localization(year, values):
    p=f'localisation/russian/chronicle_{year}_l_russian.yml'
    text=read(p)
    for key,value in values.items():
        line=f' {key}:0 "{value.replace(chr(34), chr(39))}"'
        pattern=r'^ '+re.escape(key)+r':0 .*?$'
        if re.search(pattern,text,re.M):
            text=re.sub(pattern,lambda m:line,text,flags=re.M)
        else:text+='\n'+line
    write(p,text.rstrip()+'\n')

NEW = {
 (1893,'08.01'): (37,'A03',('set_global_flag = CH93_hakodate_armistice A08 = { add_stability = 0.05 } add_stability = 0.03','add_war_support = 0.05 A08 = { add_stability = -0.05 }')),
 (1893,'20.03'): (38,'A01',('WTC_initialize_effect = yes add_to_variable = { WTC_debt = 3 } WTC_refresh_effect = yes set_country_flag = CH93_farmer_guarantee add_stability = 0.04','add_political_power = -50 add_stability = 0.03')),
 (1893,'12.10'): (39,'A02',('set_global_flag = CH93_crowns_plot_exposed add_political_power = 40 A06 = { add_political_power = -40 }','set_global_flag = CH93_crowns_plot_succeeded add_stability = -0.05 A06 = { add_political_power = 40 }')),
 (1893,'20.11'): (40,'A06',('set_country_flag = CH93_emperor_returned add_political_power = -20 add_stability = 0.03','set_country_flag = CH93_emperor_detained add_stability = -0.05')),
 (1894,'20.03'): (37,'A08',('set_country_flag = CH94_saigo_expedition add_political_power = -40 add_tech_bonus = { name = CH94_research bonus = 0.25 uses = 1 category = industry }','add_political_power = 20')),
 (1894,'02.04'): (38,'A06',('set_global_flag = CH94_spitsbergen_settlement add_stability = 0.04','add_war_support = 0.04 add_stability = -0.02')),
 (1894,'18.04'): (39,'A04',('set_global_flag = CH94_japan_dossier_shared A02 = { add_political_power = 25 }','set_country_flag = CH94_japan_dossier_reserved add_political_power = 25')),
}

def revise_year(year, entries):
    prefix=f'ch{str(year)[2:]}'; upper=prefix.upper()
    mp=f'tools/chronicle_{year}_manifest.json'
    rows=json.loads(read(mp)); bydate={r['date'][:5]:r for r in rows}
    ep=f'events/chronicle_{year}.txt'; events=read(ep); loc={}
    for entry in entries:
        date=entry['date']; ndate=date[:5]
        new=NEW.get((year,ndate))
        if new:
            n,tag,effects=new
            row=next((r for r in rows if r['id']==n),None)
            if row is None:
                row=dict(id=n,tag=tag);rows.append(row)
        else:
            row=bydate[ndate];n=row['id'];tag=row['tag'];effects=None
        row.update(date=date,title=entry['title'],canonical=entry['canonical'])
        if year==1893 and ndate=='22.02':
            tag='A06';row['tag']=tag
        key=f'{prefix}.{n}'
        if new and not re.search(r'\bid = '+re.escape(key)+r'\s',events):
            events+=f'\ncountry_event = {{\n id = {key}\n title = {key}.t\n desc = {key}.d\n picture = GFX_1896_event_talks\n is_triggered_only = yes\n fire_only_once = yes\n timeout_days = 3\n'
            for i in range(2):
                letter='ab'[i]
                events+=f' option = {{ name = {key}.{letter} ai_chance = {{ factor = {100 if i+1==entry["canonical"] else 0} }} set_global_flag = {prefix}_{n}_{letter} {effects[i]} hidden_effect = {{ every_country = {{ limit = {{ is_ai = no NOT = {{ tag = ROOT }} }} country_event = {{ id = {prefix}.{100+n} }} }} }} }}\n'
            events+='}\n'
            events+=f'country_event = {{ id = {prefix}.{100+n} title = {key}.t desc = {{ text = {key}.news_a trigger = {{ has_global_flag = {prefix}_{n}_a }} }} desc = {{ text = {key}.news_b trigger = {{ has_global_flag = {prefix}_{n}_b }} }} is_triggered_only = yes option = {{ name = {prefix}.read }} }}\n'
        else:
            a,b=block(events,f'country_event = {{\n id = {key}\n')
            piece=events[a:b]
            for i,letter in enumerate('ab'):
                piece=re.sub(r'(name = '+re.escape(key+'.'+letter)+r' ai_chance = \{ factor = )\d+',lambda m:m[1]+str(100 if i+1==entry['canonical'] else 0),piece)
            events=events[:a]+piece+events[b:]
        note=entry['note']
        details=' '.join(f'«{choice}» {detail}.' for choice,detail in zip(entry['choices'],entry.get('details',['',''])))
        loc[key+'.t']=entry['title'];loc[key+'.d']=f'{date}. {details} {note}'.strip()
        for i,letter in enumerate('ab'):
            loc[key+'.'+letter]=entry['choices'][i]
            loc[key+'.news_'+letter]=f'{date}. {entry["title"]}. Решение: «{entry["choices"][i]}».'+(f' {note}' if i+1==entry['canonical'] else '')
        loc[key+'.absent']=f'{date}. Участник события больше не существует как отдельная держава.'
    rows.sort(key=lambda r:datetime.strptime(r['date'],'%d.%m.%Y'))
    schedule=[f'{upper}_tick = {{',f' if = {{ limit = {{ date > {year-1}.12.31 date < {year+1}.1.1 }}']
    for row in rows:
        n=row['id'];tag=row['tag'];prev=datetime.strptime(row['date'],'%d.%m.%Y')-timedelta(days=1)
        schedule.append(f' if = {{ limit = {{ date > {prev.year}.{prev.month}.{prev.day} NOT = {{ has_global_flag = {prefix}_queued_{n} }} }} set_global_flag = {prefix}_queued_{n} if = {{ limit = {{ country_exists = {tag} }} {tag} = {{ country_event = {{ id = {prefix}.{n} }} }} }} else = {{ set_global_flag = {prefix}_{n}_skipped }} }}')
    schedule+=[' }','}']
    sp=f'common/scripted_effects/chronicle_{year}.txt';s=read(sp)
    s=replace_block(s,f'{upper}_tick = {{','\n'.join(schedule))
    write(sp,s);write(ep,events);write(mp,json.dumps(rows,ensure_ascii=False,indent=2)+'\n');localization(year,loc)

def main():
    source=json.loads(read('docs/chronicle_revision_source.json'))
    for year in (1893,1894):revise_year(year,[e for e in source if e['date'].endswith(str(year))])
    # Names remain as compatibility aliases; neither helper kills the character.
    for year,name in ((1894,'CH94_pobedonostsev_dies'),(1895,'CH95_pobedonostsev_legacy')):
        p=f'common/scripted_effects/chronicle_{year}.txt';s=read(p)
        s=replace_block(s,name+' = {',name+' = { set_country_flag = CH94_pobedonostsev_ill set_country_flag = CH95_generals_council clr_country_flag = CH94_pobedonostsev_dead }')
        write(p,s)
        prefix=f'ch{str(year)[2:]}';n=32 if year==1894 else 17;key=f'{prefix}.{n}'
        localization(year,{key+'.t':'Болезнь Победоносцева',key+'.d':'Победоносцев тяжело болен. Совет генералов забирает управление, Александр III остаётся символом власти.',key+'.a':'Совет генералов',key+'.b':'Власть Синода',key+'.news_a':'Болезнь Победоносцева ускоряет переход власти к совету генералов. Царь остаётся символом.',key+'.news_b':'Синод пытается сохранить влияние больного Победоносцева.',key+'.continued_t':'Совет генералов',key+'.continued_d':'Победоносцев болен. Генералы закрепляют полномочия при номинальном императоре.'})
        mp=f'tools/chronicle_{year}_manifest.json';rows=json.loads(read(mp))
        next(r for r in rows if r['id']==n)['title']='Болезнь Победоносцева'
        write(mp,json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    # Public reports disclose only the quarantine, never the intelligence secret.
    for year in (1893,1894,1895,1896):
        p=f'localisation/russian/chronicle_{year}_l_russian.yml';s=read(p)
        s=s.replace('После смерти Победоносцева','Во время болезни Победоносцева').replace('после смерти Победоносцева','во время болезни Победоносцева')
        write(p,s)
    # Canonical Batavia settlement: Dutch Borneo and Japanese Manila/Luzon.
    p='common/scripted_effects/chronicle_1896.txt';s=read(p)
    body='''CH96_batavia_compromise = {
 if = { limit = { country_exists = A03 NOT = { has_global_flag = CH96_batavia_signed } OR = { has_war_with = A03 has_country_flag = A01_expansion_resolved } }
  CH96_finish_borneo_war = yes
  CH96_restore_borneo = yes
  set_country_flag = CH96_dutch_victory
  A03 = { clr_country_flag = A03_borneo_victory set_country_flag = CH96_japan_withdrawn }
  CH96_ludolf_cabinet = yes
  add_stability = 0.05
 } else = { set_global_flag = ch96_3_inactive }
}'''
    s=replace_block(s,'CH96_batavia_compromise = {',body)
    if 'CH96_restore_borneo = {' not in s:
        s+='\nCH96_restore_borneo = {\n'+''.join(f' {state} = {{ if = {{ limit = {{ is_owned_by = A03 }} A01 = {{ transfer_state = {state} }} }} if = {{ limit = {{ is_owned_by = A01 is_controlled_by = A03 }} set_state_controller = A01 }} }}\n' for state in (333,334,1022,1023,1024,1055,1059))+'}\n'
    write(p,s)
    localization(1896,{'ch96.3.t':'Батавский мир','ch96.3.b':'Япония уходит с Борнео','ch96.3.news_b':'Голландия побеждает. Япония уходит с Борнео, сохраняя Манилу и Лусон. Победа спасает Людольфа от вотума недоверия.','ch96.3.d':'Голландия требует ухода японских войск с Борнео. Умеренный договор сохраняет японские владения на Лусоне и в Маниле.'})
    from british_story_links import sync
    sync()
    from minor_story_links import sync as sync_minors
    sync_minors()
    print('Applied corrected chronology: 40 events in 1893, 39 in 1894; continuity fixes in 1895–1896.')

if __name__=='__main__':main()
