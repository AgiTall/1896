"""Shared dated-event emitter; scenario effects remain in year-specific builders."""
from datetime import datetime,timedelta
import json,re
from build_chronicle_1893 import ROOT,write

def build(year,tags,effects,helpers,ideas,gates=None,prelude='',extra_loc=None,ai=None):
    prefix=f'ch{str(year)[2:]}'; upper=prefix.upper(); gates=gates or {}; ai=ai or {}
    source=ROOT/f'docs/chronicle_{year}_source.txt'
    blocks=re.split(r'\*\*(\d+)\. (.*?)\*\*',source.read_text(encoding='utf-8-sig'))
    events=[f'add_namespace = {prefix}\n'];loc=['l_russian:'];manifest=[]
    schedule=[f'{upper}_tick = {{',f' if = {{ limit = {{ date > {year-1}.12.31 date < {year+1}.1.1 }}',prelude]
    def l(k,v):loc.append(f' {k}:0 "{v.replace(chr(34),chr(39))}"')
    for pos in range(1,len(blocks),3):
        n,title,body=int(blocks[pos]),blocks[pos+1],blocks[pos+2]
        date=re.search(r'\*\*Дата:\*\* (\d+\.\d+\.\d+)',body)[1]
        dt=datetime.strptime(date,'%d.%m.%Y');prev=dt-timedelta(days=1)
        choices=re.findall(r'\*\*Вариант [12]:\*\* «(.*?)» \((.*?)\)\.',body)
        canon=re.search(r'\*\*Канон:\*\* (.*?)\.',body)[1].split(' (')[0]
        ci=next(i for i,c in enumerate(choices) if c[0]==canon)
        assert len(choices)==2 and dt.year==year
        # The clerical opposition survives its leader, who died in earlier years.
        if year==1896 and n==21:choices[1]=(choices[1][0],'Церковные консерваторы отказываются от иностранной помощи')
        key,tag=f'{prefix}.{n}',tags[n-1]
        schedule.append(f'  if = {{ limit = {{ date > {prev.year}.{prev.month}.{prev.day} NOT = {{ has_global_flag = {prefix}_queued_{n} }} }} set_global_flag = {prefix}_queued_{n} if = {{ limit = {{ country_exists = {tag} }} {tag} = {{ country_event = {{ id = {key} }} }} }} else = {{ set_global_flag = {prefix}_{n}_skipped every_country = {{ limit = {{ is_ai = no }} country_event = {{ id = {prefix}.{200+n} }} }} }} }}')
        l(key+'.t',title);l(key+'.d',date+'. '+' '.join(c[1]+'.' for c in choices))
        events.append(f'country_event = {{\n id = {key}\n title = {key}.t\n desc = {key}.d\n picture = GFX_1896_event_talks\n is_triggered_only = yes\n fire_only_once = yes\n timeout_days = 3')
        for i,(label,desc) in enumerate(choices):
            letter='ab'[i];l(key+'.'+letter,label);l(key+'.news_'+letter,f'{date}. Решение: «{label}». {desc}.')
            effect=effects[n][i]
            if n in gates:effect=f'if = {{ limit = {{ {gates[n]} }} {effect} }} else = {{ set_global_flag = {prefix}_{n}_inactive }}'
            weight=ai.get((n,i),f'factor = {100 if i==ci else 0}')
            events.append(f' option = {{ name = {key}.{letter} ai_chance = {{ {weight} }} set_global_flag = {prefix}_{n}_{letter}\n {effect}\n hidden_effect = {{ every_country = {{ limit = {{ is_ai = no NOT = {{ tag = ROOT }} }} country_event = {{ id = {prefix}.{100+n} }} }} }}\n }}')
        events.append('}\n')
        l(key+'.inactive',date+'. Изменение обстановки сделало этот план неосуществимым. Решение не было исполнено.')
        l(key+'.absent',date+'. Участник эпизода больше не существует как отдельная держава. Историческая развилка утратила актуальность.')
        events.append(f'country_event = {{ id = {prefix}.{100+n} title = {key}.t desc = {{ text = {key}.inactive trigger = {{ has_global_flag = {prefix}_{n}_inactive }} }} desc = {{ text = {key}.news_a trigger = {{ has_global_flag = {prefix}_{n}_a NOT = {{ has_global_flag = {prefix}_{n}_inactive }} }} }} desc = {{ text = {key}.news_b trigger = {{ has_global_flag = {prefix}_{n}_b NOT = {{ has_global_flag = {prefix}_{n}_inactive }} }} }} picture = GFX_1896_event_talks is_triggered_only = yes option = {{ name = {prefix}.read }} }}')
        events.append(f'country_event = {{ id = {prefix}.{200+n} title = {key}.t desc = {key}.absent picture = GFX_1896_event_talks is_triggered_only = yes option = {{ name = {prefix}.read }} }}')
        manifest.append(dict(id=n,date=date,title=title,tag=tag,canonical=ci+1))
    schedule+=[' }','}'];l(prefix+'.read','Мир меняется.')
    for k,v in (extra_loc or {}).items():l(k,v)
    idea_rows=['ideas = { country = {']
    for key,(name,desc,modifier) in ideas.items():
        l(upper+'_'+key,name);l(upper+'_'+key+'_desc',desc)
        idea_rows.append(f' {upper}_{key} = {{ picture = jpc_credit modifier = {{ {modifier} }} }}')
    idea_rows.append('} }')
    write(f'events/chronicle_{year}.txt','\n'.join(events)+'\n')
    write(f'common/scripted_effects/chronicle_{year}.txt','\n'.join(schedule)+'\n'+helpers)
    write(f'common/on_actions/chronicle_{year}.txt',f'on_actions = {{ on_startup = {{ effect = {{ {upper}_tick = yes }} }} on_daily = {{ effect = {{ {upper}_tick = yes }} }} }}\n')
    write(f'common/ideas/chronicle_{year}.txt','\n'.join(idea_rows)+'\n')
    write(f'localisation/russian/chronicle_{year}_l_russian.yml','\n'.join(loc)+'\n',True)
    write(f'tools/chronicle_{year}_manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(f'Built {len(manifest)} choices and {len(manifest)*2} reports for {year}.')
