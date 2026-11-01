"""Condense the maritime campaign into substantial, mostly sequential reforms."""
from pathlib import Path
import re, shutil, json
from clarify_japan_branches import blocks

R=Path(__file__).resolve().parents[1]
B=R/'tools/backups/japan_compaction_20261019'
GROUPS={
'JPC_replace_losses':['JPD_standard_orders','JPD_engineering_schools'],
'JPD_industrial_power':['JPD_sustainable_credit'],
'JPF_public_accounts':['JPC_iwasaki_accounts','JPF_bond_register'],
'JPF_delivery_calendar':['JPF_excise_bargain','JPF_coal_not_glory'],
'JPF_civil_budget':['JPF_return_small_savings'],
'JPC_honshu_depots':['JPN_north_civilian_holds','JPN_north_supply_register'],
'JPN_north_imperial_arbitration':['JPN_north_inspection_channel','JPN_north_tokyo_auditors','JPN_north_admiralty_hearing'],
'JPN_north_postwar_audience':['JPN_north_permanent_protocol','JPN_north_keep_distance'],
'JPC_garrison_accounts':['JPL_convoy_timetable'],
'JPL_supply_board':['JPL_municipal_buyers','JPL_payroll_inquiry','JPL_quartermaster_school'],
'JPL_medical_rotation':['JPC_casualty_returns','JPC_hospital_ships'],
'JPD_professional_logistics':['JPL_port_and_mountains','JPL_limited_mandate'],
'JPC_hold_until_talks':['JPC_no_short_war','JPC_imperial_inspection','JPC_1895_accounts','JPC_sulu_escorts'],
'JPD_ocean_fleet':['JPC_nz_watch'],
'JPD_integrated_staff':['JPL_borneo_is_not_luzon'],
'JPC_regional_dispatches':['JPC_honolulu_letters','JPC_australian_assurances'],
'A03_grand_southern_mandate':['A03_placate_continental_army','A03_continental_ambitions','A03_naval_zaibatsu_compromise','A03_pacific_resource_lifeline'],
'A03_prime_minister_filter':['A03_sacred_shield_monarch','A03_privy_council_arbiters','A03_cabinet_dissolution'],
'A03_direct_imperial_rule':['A03_divine_sovereignty'],
'A03_two_faced_colonialism':['A03_asian_liberation_crusade','A03_kempeitai_iron_fist'],
'A03_imperial_predator':['A03_showcase_of_prosperity','A03_pan_asian_brotherhood','A03_total_resource_drain','A03_labor_battalions'],
}
# The main campaign now uses one policy: audited credit, regular northern supply,
# and protected Manila convoys. Decisions/events still carry the narrative choices.
DISCARDED={'JPF_small_subscription':'JPF_public_accounts',
           'JPN_north_emergency_calendar':'JPC_honshu_depots',
           'JPL_names_and_units':'JPC_garrison_accounts'}
ALIASES={old:new for new,olds in GROUPS.items() for old in olds}|DISCARDED
ROWS={
0:{14:'A03_imperial_council'},
1:{-6:'JPX_land',-2:'JPX_trade',14:'JPX_sea',32:'JPX_kami',36:'JPX_throne'},
2:{-6:'JPX_land_institution',-2:'JPX_trade_institution',32:'JPX_kami_institution',36:'JPX_throne_institution'},
3:{2:'JPC_osaka_orders',8:'JPC_state_guarantees',14:'JPC_northern_protocol',20:'JPC_manila_priority'},
4:{0:'JPC_war_workshops',4:'JPC_pledged_yards',8:'JPF_public_accounts',14:'JPC_honshu_depots',20:'JPC_garrison_accounts'},
5:{0:'JPC_replace_losses',4:'JPC_convoy_budget',8:'JPF_delivery_calendar',14:'JPN_north_imperial_arbitration',18:'JPR_defence_budget'},
6:{8:'JPF_madeira_table',20:'JPL_supply_board',24:'JPC_batavia_demands'},
7:{22:'JPX_sea_institution',26:'JPC_one_war_cabinet'},
8:{20:'JPL_medical_rotation',24:'JPC_borneo_bridgehead',28:'JPC_regional_dispatches'},
9:{20:'JPD_professional_logistics',24:'JPC_hold_until_talks',28:'JPC_wtc_mission'},
10:{24:'JPD_ocean_fleet'},
11:{14:'JPC_count_the_cost'},
12:{4:'JPC_oil_promise',8:'JPC_defeat_inquest',14:'JPC_partial_demobilisation'},
13:{4:'JPC_rebuild_ports',6:'JPF_royalty_register',14:'JPC_three_heads_again',22:'JPD_integrated_staff'},
14:{8:'JPF_civil_budget',12:'JPN_north_postwar_audience',16:'A03_manage_triple_split',20:'A03_constitutional_debate',26:'A03_two_faced_colonialism'},
15:{16:'A03_grand_southern_mandate',18:'A03_prime_minister_filter',22:'A03_direct_imperial_rule'},
16:{4:'JPD_industrial_power',14:'JPD_settle_three_heads',26:'A03_imperial_predator'},
17:{14:'JPD_reformed_empire'},
}
POSITIONS={fid:(x,y) for y,row in ROWS.items() for x,fid in row.items()}
PARENTS={
'JPC_manila_priority':[['JPX_sea']],
'JPF_public_accounts':[['JPC_state_guarantees']],
'JPF_delivery_calendar':[['JPF_public_accounts']],
'JPF_madeira_table':[['JPF_delivery_calendar']],
'JPC_honshu_depots':[['JPC_northern_protocol']],
'JPN_north_imperial_arbitration':[['JPC_honshu_depots']],
'JPR_defence_budget':[['JPC_state_guarantees'],['JPC_northern_protocol']],
'JPC_garrison_accounts':[['JPC_manila_priority']],
'JPL_supply_board':[['JPC_garrison_accounts'],['JPR_defence_budget']],
'JPL_medical_rotation':[['JPL_supply_board']],
'JPD_professional_logistics':[['JPL_medical_rotation']],
'JPC_one_war_cabinet':[['JPC_batavia_demands']],
'JPC_hold_until_talks':[['JPC_borneo_bridgehead']],
'JPD_ocean_fleet':[['JPC_hold_until_talks'],['JPX_sea_institution']],
'JPF_civil_budget':[['JPC_count_the_cost']],
'JPN_north_postwar_audience':[['JPC_three_heads_again'],['JPN_north_imperial_arbitration']],
'A03_grand_southern_mandate':[['A03_manage_triple_split']],
'A03_prime_minister_filter':[['A03_constitutional_debate']],
'A03_direct_imperial_rule':[['A03_constitutional_debate']],
'A03_imperial_predator':[['A03_two_faced_colonialism']],
'JPD_integrated_staff':[['JPD_professional_logistics'],['JPD_ocean_fleet'],['JPC_partial_demobilisation']],
'JPD_settle_three_heads':[['A03_grand_southern_mandate'],['A03_prime_minister_filter','A03_direct_imperial_rule'],['JPN_north_postwar_audience']],
'JPD_industrial_power':[['JPC_replace_losses'],['JPC_convoy_budget'],['JPF_civil_budget']],
}
TEXT={
'JPC_replace_losses':('Промышленная и инженерная база','Объединим расширение военных заводов с едиными стандартами заказов и подготовкой инженеров. Следующий этап — самостоятельная промышленная держава после урегулирования военных долгов.'),
'JPF_public_accounts':('Реформа государственных займов','Проверим счета Мицубиси, введём открытые ведомости и единый реестр обязательств. Вместо нескольких отдельных ревизий казна получит постоянный порядок управления долгом.'),
'JPF_delivery_calendar':('Оплатить военные поставки','Согласуем график расчётов, разрешим акцизный сбор и заключим угольные контракты. Эти меры поддержат снабжение и откроют решения для обслуживания долга.'),
'JPC_honshu_depots':('Постоянные поставки на Север','Склады Хонсю, гражданские караваны и учёт запасов станут единой системой снабжения Хоккайдо. Сайго получит подтверждение договора делом; северные войска сохранят самостоятельность.'),
'JPN_north_imperial_arbitration':('Урегулировать северные поставки','Совместная проверка складов, ревизия отправителей и посредничество Мэйдзи снизят напряжение между Сайго и флотом. После войны этот порядок позволит перейти к постоянному договору.'),
'JPC_garrison_accounts':('Перевооружить и снабдить Манилу','Направим гарнизону вооружение и закрепим охранение за манильскими караванами. Это единый этап снабжения, после которого можно реформировать работу интендантов.'),
'JPL_supply_board':('Реформа гарнизонного снабжения','Объединим местные закупки, расследование растрат, совет поставок и обучение интендантов. Решения расследования сохранятся в событиях; каждый административный шаг больше не требует отдельного фокуса.'),
'JPL_medical_rotation':('Помощь солдатам и ротация','Сведём потери, организуем госпитальные рейсы и смену уставших частей. Опыт заботы о людях и снабжения станет основой постоянной армейской службы.'),
'JPC_hold_until_talks':('Обеспечить длительную кампанию','Пересмотрим военную смету, проверим фронт и наладим караваны Сулу. Кабинет получит средства для удержания позиций до переговоров. Победу по-прежнему определит фактическое положение на Борнео.'),
'JPC_regional_dispatches':('Соглашения в южных морях','Обратимся к Австралии и Гавайям, согласуя безопасность соседей и обслуживание судов. Каждая страна самостоятельно ответит на предложение. Отдельная миссия к ВТП позволит запросить кредит.'),
'JPN_north_postwar_audience':('Постоянный договор с Сайго','Проведём послевоенную аудиенцию, подготовим постоянный протокол и гарантируем самостоятельность Севера. Окончательная подпись зависит от доверия и реальных поставок; один фокус не заменяет исполнения договора.'),
'JPF_civil_budget':('Вернуть вклады и закрыть военную смету','Подготовим возврат мелких вкладов и переход к мирному бюджету. После урегулирования нефтяных обязательств и внешних долгов решение казначейства закроет военную книгу. Тогда станет доступно завершение промышленной реформы.'),
'A03_grand_southern_mandate':('Общая программа армии и флота','Согласуем уступки сухопутным командирам и промышленникам, расширим военное производство и морские перевозки. Общий южный курс заменит спор ведомств о каждом заказе.'),
'A03_prime_minister_filter':('Ответственное правительство','Учредим кабинет министров, закрепим положение императора, роль совета Гэнро и право роспуска правительства. Завершённая система управления станет одним из оснований урегулирования раскола трёх сил.'),
'A03_direct_imperial_rule':('Личная власть Мэйдзи','Закрепим непосредственное управление императора и его верховный авторитет. Это альтернативное устройство власти внутри адмиралтейского курса, ведущее к тому же завершению государственного кризиса.'),
'A03_imperial_predator':('Тихоокеанская колониальная система','Объединим гражданские вложения, пропаганду братства, контроль добычи и трудовую мобилизацию. За обещанием освобождения закрепится система имперского управления; её выгоды и ответственность сохранятся после реформ.'),
}

def field_span(s,key):
    m=re.search(r'\b'+key+r'\s*=\s*\{',s)
    if not m:return None
    end=m.end();depth=1
    while depth:depth+=(s[end]=='{')-(s[end]=='}');end+=1
    return m.start(),m.end(),end

def body(s,key):
    span=field_span(s,key)
    return s[span[1]:span[2]-1] if span else ''

def write(p,text):
    backup=B/p.relative_to(R)
    if p.exists() and not backup.exists():
        backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
    p.write_text(text,encoding='utf-8-sig' if p.suffix=='.yml' else 'utf-8',newline='\n')

def apply():
    p=R/'common/national_focus/a03_focus.txt'
    if 'id = JPI_closed_ports' in p.read_text(encoding='utf-8-sig'):
        raise SystemExit('Historical compaction disabled for the current branching industry.')
    snapshot=B/'common/national_focus/a03_focus.txt'
    if not snapshot.exists():
        snapshot.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,snapshot)
    original=snapshot.read_text(encoding='utf-8-sig')
    allblocks=list(blocks(original))
    source={re.search(r'\bid\s*=\s*(\w+)',b)[1]:b for _,_,b in allblocks}
    assert set(source)-set(ALIASES)==set(POSITIONS),(set(source)-set(ALIASES))-set(POSITIONS)
    text=original
    for start,end,b in reversed(allblocks):
        fid=re.search(r'\bid\s*=\s*(\w+)',b)[1]
        if fid in ALIASES:text=text[:start]+text[end:];continue
        if fid in GROUPS:
            # Preserve earned rewards and story events in one substantial stage.
            merged='\n'.join(body(source[old],'completion_reward') for old in GROUPS[fid])
            span=field_span(b,'completion_reward')
            b=b[:span[2]-1]+'\n'+merged+'\n'+b[span[2]-1:]
            cost=min(7,max(int(re.search(r'\bcost\s*=\s*(\d+)',source[k])[1]) for k in [fid]+GROUPS[fid])+1)
            b=re.sub(r'\bcost\s*=\s*\d+',f'cost = {cost}',b,count=1)
        if fid in {'JPF_public_accounts','JPC_honshu_depots','JPC_garrison_accounts'}:
            b=re.sub(r'\s*mutually_exclusive\s*=\s*\{[^{}]*\}','',b)
        parents=PARENTS.get(fid)
        if parents is None:
            parents=[]
            for m in re.finditer(r'prerequisite\s*=\s*\{([^}]+)\}',b):
                group=list(dict.fromkeys(ALIASES.get(k,k) for k in re.findall(r'focus\s*=\s*(\w+)',m[1])))
                group=[k for k in group if k!=fid]
                if group and group not in parents:parents.append(group)
        b=re.sub(r'\s*prerequisite\s*=\s*\{[^{}]*\}','',b)
        b=b[:-1]+'\n'+''.join(' prerequisite = { '+' '.join('focus = '+parent for parent in group)+' }\n' for group in parents)+' }'
        # Final industry now includes financial reform: real ledger closure required.
        if fid=='JPD_industrial_power':
            b=b[:-1]+'\n available = { custom_trigger_tooltip = { tooltip = JPD_finance_resolved_tt has_country_flag = JPF_finance_closed } }\n cancel_if_invalid = yes\n }'
        x,y=POSITIONS[fid]
        b=re.sub(r'\bx\s*=\s*-?\d+',f'x = {x}',b,count=1)
        b=re.sub(r'\by\s*=\s*-?\d+',f'y = {y}',b,count=1)
        text=text[:start]+b+text[end:]
    write(p,text)
    # Redirect focus references only: identically named flags/ideas retain their meaning.
    changed=[]
    for folder in ['common','events']:
        for target in (R/folder).rglob('*.txt'):
            if target==p:continue
            content=target.read_text(encoding='utf-8-sig');updated=content
            for old,new in ALIASES.items():
                updated=re.sub(r'(has_completed_focus\s*=\s*)'+re.escape(old)+r'\b',lambda m:m[1]+new,updated)
            if target.name=='A01_canonical.txt':
                def plan(m):
                    ids=list(dict.fromkeys(ALIASES.get(k,k) for k in m[1].split()))
                    return 'ai_national_focuses = { '+' '.join(ids)+' }'
                begin=updated.index('A03_southern_canonical_plan')
                updated=updated[:begin]+re.sub(r'ai_national_focuses\s*=\s*\{([^}]+)\}',plan,updated[begin:],count=1)
            if updated!=content:write(target,updated);changed.append(str(target.relative_to(R)))
    for lang in ['russian','english']:
        target=R/f'localisation/{lang}/1896_main_l_{lang}.yml'
        content=target.read_text(encoding='utf-8-sig')
        for fid,(title,desc) in TEXT.items():
            if lang!='russian':continue
            for key,value in [(fid,title),(fid+'_desc',desc)]:
                content,count=re.subn(r'^ '+re.escape(key)+r':\d*\s*".*"',lambda m:' '+key+':0 "'+value+'"',content,flags=re.M)
                assert count==1,key
        write(target,content)
    report={'before':len(source),'after':len(POSITIONS),'merged':GROUPS,'fixed_main_policies':DISCARDED,'redirected_files':changed}
    (R/'tools/japan_compaction_20261019.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Japan compacted: {len(source)} -> {len(POSITIONS)} focuses; {len(POSITIONS)-10} main-campaign stages.')

if __name__=='__main__':
    if 'id = JPI_closed_ports' in (R/'common/national_focus/a03_focus.txt').read_text(encoding='utf-8-sig'):
        raise SystemExit('Historical compaction disabled: the current branching industry is validated by validate_japan_industry.py.')
    apply()
