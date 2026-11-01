"""Give the maritime campaign distinct reform chains and earned end states."""
from pathlib import Path
import re
import shutil
from clarify_japan_branches import blocks

R = Path(__file__).resolve().parents[1]
B = R/'tools/backups/japan_development_20261019'

ROWS = {
0: {32:'A03_imperial_council'},
2: {-14:'JPX_land',-8:'JPX_trade',32:'JPX_sea',82:'JPX_kami',88:'JPX_throne'},
3: {-14:'JPX_land_institution',-8:'JPX_trade_institution',82:'JPX_kami_institution',88:'JPX_throne_institution'},
4: {4:'JPC_osaka_orders',12:'JPC_state_guarantees',24:'JPC_northern_protocol'},
5: {10:'JPF_public_accounts',14:'JPF_small_subscription',22:'JPN_north_civilian_holds',26:'JPN_north_emergency_calendar',44:'JPC_manila_priority'},
6: {2:'JPC_war_workshops',6:'JPC_pledged_yards',24:'JPC_honshu_depots',34:'JPR_defence_budget',42:'JPL_convoy_timetable',46:'JPL_names_and_units'},
7: {2:'JPC_replace_losses',6:'JPC_convoy_budget',12:'JPC_iwasaki_accounts',24:'JPN_north_supply_register',44:'JPC_garrison_accounts',54:'JPC_batavia_demands',58:'JPX_sea_institution'},
8: {12:'JPF_bond_register',22:'JPN_north_inspection_channel',26:'JPN_north_admiralty_hearing',44:'JPL_port_and_mountains',54:'JPC_one_war_cabinet'},
9: {4:'JPD_standard_orders',10:'JPF_excise_bargain',16:'JPF_delivery_calendar',22:'JPN_north_tokyo_auditors',42:'JPL_municipal_buyers',46:'JPL_payroll_inquiry',54:'JPC_borneo_bridgehead',66:'JPC_regional_dispatches'},
10:{10:'JPF_coal_not_glory',16:'JPF_madeira_table',24:'JPN_north_imperial_arbitration',42:'JPL_supply_board',46:'JPL_quartermaster_school',54:'JPC_casualty_returns',62:'JPC_wtc_mission',66:'JPC_honolulu_letters',70:'JPC_australian_assurances'},
11:{4:'JPD_engineering_schools',46:'JPC_hospital_ships',54:'JPC_no_short_war'},
12:{42:'JPL_limited_mandate',46:'JPL_medical_rotation',54:'JPC_imperial_inspection',58:'JPC_sulu_escorts',70:'JPC_nz_watch'},
13:{44:'JPD_professional_logistics',54:'JPC_1895_accounts'},
14:{54:'JPC_hold_until_talks'},
15:{58:'JPD_ocean_fleet'},
17:{32:'JPC_count_the_cost'},
18:{4:'JPC_oil_promise',16:'JPC_defeat_inquest',44:'JPL_borneo_is_not_luzon'},
19:{4:'JPC_rebuild_ports',12:'JPF_return_small_savings',32:'JPC_partial_demobilisation'},
20:{8:'JPF_royalty_register',32:'JPC_three_heads_again'},
21:{12:'JPF_civil_budget',24:'JPN_north_postwar_audience',52:'JPD_integrated_staff'},
22:{18:'A03_manage_triple_split',24:'JPN_north_permanent_protocol',34:'A03_constitutional_debate',44:'A03_two_faced_colonialism'},
23:{12:'JPD_sustainable_credit',16:'A03_naval_zaibatsu_compromise',20:'A03_placate_continental_army',24:'JPN_north_keep_distance',32:'A03_prime_minister_filter',36:'A03_direct_imperial_rule',42:'A03_asian_liberation_crusade',46:'A03_kempeitai_iron_fist'},
24:{4:'JPD_industrial_power',16:'A03_pacific_resource_lifeline',20:'A03_continental_ambitions',32:'A03_sacred_shield_monarch',36:'A03_divine_sovereignty',42:'A03_showcase_of_prosperity',46:'A03_total_resource_drain'},
25:{18:'A03_grand_southern_mandate',32:'A03_privy_council_arbiters',42:'A03_pan_asian_brotherhood',46:'A03_labor_battalions'},
26:{32:'A03_cabinet_dissolution'},
27:{28:'JPD_settle_three_heads',44:'A03_imperial_predator'},
29:{32:'JPD_reformed_empire'},
}
POSITIONS = {fid:(x,y) for y,row in ROWS.items() for x,fid in row.items()}

# Each nested list is an OR group; separate groups are AND requirements.
NEW = {
'JPD_standard_orders': ('GFX_goal_unique_A03_industrial_power',5,
 [['JPC_replace_losses'],['JPC_convoy_budget']],
 'add_ideas = JPD_standardized_industry', ''),
'JPD_engineering_schools': ('GFX_goal_unique_A03_industrial_power',5,
 [['JPD_standard_orders']],
 'add_tech_bonus = { name = JPD_engineering_schools bonus = 0.5 uses = 2 category = industry }', ''),
'JPD_sustainable_credit': ('GFX_goal_unique_A01_governors_secretariat',5,
 [['JPF_civil_budget'],['JPF_excise_bargain','JPF_madeira_table'],['JPF_coal_not_glory']],
 'add_ideas = JPD_sustainable_finance add_political_power = 50',
 'custom_trigger_tooltip = { tooltip = JPD_finance_resolved_tt has_country_flag = JPF_finance_closed }'),
'JPD_industrial_power': ('GFX_goal_unique_A03_industrial_power',7,
 [['JPD_engineering_schools'],['JPD_sustainable_credit']],
 'remove_ideas = JPD_standardized_industry add_ideas = JPD_industrial_economy add_research_slot = 1 set_country_flag = JPD_industry_reformed', ''),
'JPD_professional_logistics': ('GFX_goal_unique_A03_expeditionary_staff',5,
 [['JPL_limited_mandate'],['JPL_medical_rotation']],
 'add_ideas = JPD_professional_supply army_experience = 25', ''),
'JPD_ocean_fleet': ('GFX_goal_unique_A03_combined_operations',7,
 [['JPX_sea_institution'],['JPC_hold_until_talks'],['JPC_sulu_escorts'],['JPC_nz_watch']],
 'add_ideas = JPD_oceanic_service navy_experience = 35', ''),
'JPD_integrated_staff': ('GFX_goal_unique_A03_expeditionary_staff',7,
 [['JPD_professional_logistics'],['JPD_ocean_fleet'],['JPC_partial_demobilisation'],['JPL_borneo_is_not_luzon']],
 'remove_ideas = JPC_joint_staff add_ideas = JPD_permanent_staff set_country_flag = JPD_military_reformed', ''),
'JPD_settle_three_heads': ('GFX_goal_unique_A03_imperial_council',7,
 [['A03_grand_southern_mandate'],['A03_cabinet_dissolution','A03_divine_sovereignty'],['JPN_north_keep_distance']],
 'remove_ideas = JPC_three_heads remove_ideas = JPC_returned_split remove_ideas = A03_triple_split_balance add_ideas = JPD_settled_government set_country_flag = JPD_politics_reformed',
 'custom_trigger_tooltip = { tooltip = JPD_north_settled_tt has_country_flag = JPN_north_compact_signed }'),
'JPD_reformed_empire': ('GFX_goal_unique_A03_imperial_council',7,
 [['JPD_industrial_power'],['JPD_integrated_staff'],['JPD_settle_three_heads'],['A03_imperial_predator']],
 'add_stability = 0.05 add_political_power = 100 set_country_flag = JPD_reformed_empire', ''),
}

TEXT = '''
JPD_standard_orders|Единые промышленные заказы|Военные заводы и верфи уже расширены. Объединим требования к деталям, приёмке и срокам поставок, чтобы каждый новый заказ укреплял общую производственную систему. Это начало перехода от отдельных подрядов к постоянной промышленной базе.|Standardize Industrial Orders|Coordinate factory and dockyard specifications, acceptance and delivery schedules. Separate contracts become a permanent industrial system.
JPD_engineering_schools|Подготовить японских инженеров|Заводы должны уметь совершенствовать производство собственными силами. Откроем инженерные школы при предприятиях и передадим им опыт военных заказов. Подготовленные специалисты ускорят следующие промышленные исследования.|Train Japanese Engineers|Establish engineering schools alongside factories. Local specialists will accelerate the next industrial research programmes.
JPD_sustainable_credit|Заменить чрезвычайные займы бюджетом|Военная долговая книга закрыта, порядок оплаты поставок установлен. Переведём заказы на устойчивое финансирование. Казна сможет планировать расходы без ежемесячного спасения очередного военного займа; действующие нефтяные обязательства сохраняются.|Establish Sustainable Public Finance|With the wartime ledger closed and supplier payments organized, replace emergency borrowing with predictable financing. Existing oil obligations remain in force.
JPD_industrial_power|Самостоятельная промышленная держава|Собственные инженеры, стандартизированные предприятия и устойчивое финансирование позволяют Японии развиваться после войны. Завершим промышленную реформу: улучшим выпуск и освоение продукции, расширим постоянную исследовательскую базу. Зависимость от отдельных срочных заказов уступит место развитию национальной промышленности.|An Independent Industrial Power|Local engineers, standardized production and sustainable finance complete the industrial reform. Improve output and production efficiency and establish an additional permanent research slot.
JPD_professional_logistics|Постоянная служба армейского снабжения|Совет снабжения или подготовленные интенданты уже упорядочили работу гарнизона, а ротация дала опыт сбережения людей. Распространим эти правила на всю армию: учёт, доставка и смена частей станут постоянной службой, снижающей расход припасов и укрепляющей организацию войск.|A Professional Army Supply Service|Turn the garrison supply and rotation reforms into a permanent army service. Better accounting and delivery reduce supply consumption and improve organization.
JPD_ocean_fleet|Флот дальнего действия|Корпус морских самураев, караваны Сулу и наблюдение за британскими базами дали опыт длительной морской кампании. Закрепим его в постоянных правилах службы, снабжения и взаимодействия эскадр. Флот сможет действовать вдали от японских портов с меньшими затратами снабжения.|An Ocean-Going Fleet|Combine marine training, Sulu convoy experience and intelligence on British bases into permanent fleet procedures. Improve fleet organization and reduce naval supply costs.
JPD_integrated_staff|Постоянный объединённый штаб|После демобилизации сохраним опыт сухопутной и морской служб. Временный военный кабинет уступит место постоянному штабу, согласующему операции и снабжение. Борнейская кампания и опыт Манилы станут основой общей военной системы.|A Permanent Joint Staff|After demobilization, replace the temporary wartime arrangement with a permanent staff coordinating land and naval operations. Preserve the lessons of Borneo and Manila.
JPD_settle_three_heads|Завершить раскол трёх сил|Армия и флот приняли общий курс, полномочия Мэйдзи закреплены, а постоянный договор с Сайго действительно подписан. Устраним чрезвычайное соперничество ведомств и закрепим новый порядок управления. Хоккайдо сохранит самостоятельность, а уступки промышленникам останутся ценой достигнутого соглашения.|Settle the Three-Headed Crisis|With military interests reconciled, imperial powers settled and Saigo's permanent compact signed, end the emergency rivalry between factions. Hokkaido remains autonomous and industrial concessions remain binding.
JPD_reformed_empire|Империя после реформ|Япония прошла путь от временного союза трёх сил к промышленной державе с устойчивым управлением и постоянным объединённым штабом. Подведём итог реформам и закрепим новый государственный курс. Нефтяные договоры и ответственность за колониальную политику остаются частью этого будущего.|The Reformed Empire|Industrial reform, a settled government and permanent military institutions have transformed the provisional coalition. Consolidate the new state without erasing its oil obligations or colonial responsibilities.
JPD_standardized_industry|Единые производственные стандарты|Общие требования к заводам и верфям сокращают потери между заказом и готовой продукцией.|Standardized Production|Common factory and dockyard standards improve production.
JPD_sustainable_finance|Устойчивые государственные финансы|После урегулирования военных долгов казна планирует расходы на постоянной основе.|Sustainable Public Finance|With the wartime ledger settled, the treasury can plan continuing expenditure.
JPD_industrial_economy|Развитая национальная промышленность|Инженерная база и устойчивое финансирование поддерживают рост производства и исследований.|A Developed Industrial Economy|Local engineering and sustainable finance support production and research.
JPD_professional_supply|Профессиональная служба снабжения|Постоянные интенданты и общие правила доставки укрепляют армию.|Professional Supply Service|Permanent quartermasters and delivery procedures strengthen the army.
JPD_oceanic_service|Океанская служба флота|Согласованные правила службы и снабжения позволяют эскадрам действовать вдали от метрополии.|Oceanic Fleet Service|Coordinated fleet procedures sustain operations far from home.
JPD_permanent_staff|Объединённый генеральный штаб|Армия и флот согласуют планы через постоянное командование.|Permanent Joint General Staff|The army and navy coordinate through permanent joint command.
JPD_settled_government|Урегулированный императорский кабинет|Полномочия двора и ведомств определены; чрезвычайный раскол трёх сил завершён.|A Settled Imperial Government|The court and ministries have defined powers; emergency factional rivalry has ended.
'''

IDEAS = '''ideas = { country = {
JPD_standardized_industry = { picture = jpc_credit removal_cost = -1 modifier = { industrial_capacity_factory = 0.05 production_speed_dockyard_factor = 0.05 } }
JPD_sustainable_finance = { picture = jpc_credit removal_cost = -1 modifier = { consumer_goods_factor = -0.03 } }
JPD_industrial_economy = { picture = jpc_credit removal_cost = -1 modifier = { industrial_capacity_factory = 0.08 production_factory_max_efficiency_factor = 0.05 research_speed_factor = 0.03 } }
JPD_professional_supply = { picture = jpc_fleet removal_cost = -1 modifier = { supply_consumption_factor = -0.05 army_org_factor = 0.05 } }
JPD_oceanic_service = { picture = jpc_fleet removal_cost = -1 modifier = { naval_supply_consumption_factor = -0.08 navy_org_factor = 0.05 } }
JPD_permanent_staff = { picture = jpc_fleet removal_cost = -1 modifier = { supply_consumption_factor = -0.05 naval_coordination = 0.08 } }
JPD_settled_government = { picture = jpc_fleet removal_cost = -1 modifier = { political_power_gain = 0.10 stability_factor = 0.05 } }
} }
'''

def write(p, text):
    backup = B/p.relative_to(R)
    if p.exists() and not backup.exists():
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p,backup)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8-sig' if p.suffix=='.yml' else 'utf-8', newline='\n')

def apply():
    if (R/'tools/backups/japan_compaction_20261019/common/national_focus/a03_focus.txt').exists():
        from compact_japan_campaign import apply as compact
        compact()
        return
    p=R/'common/national_focus/a03_focus.txt'
    text=p.read_text(encoding='utf-8-sig')
    for start,end,b in reversed(list(blocks(text))):
        fid=re.search(r'\bid\s*=\s*(\w+)',b)[1]
        assert fid in POSITIONS,fid
        x,y=POSITIONS[fid]
        extra = {'JPF_delivery_calendar': ['JPF_bond_register'],
                 'JPN_north_postwar_audience': ['JPN_north_imperial_arbitration','JPN_north_admiralty_hearing']}.get(fid)
        if extra and not any('focus = '+parent in b for parent in extra):
            b=b[:-1]+'\n prerequisite = { '+' '.join('focus = '+parent for parent in extra)+' }\n }'
        b=re.sub(r'\bx\s*=\s*-?\d+',f'x = {x}',b,count=1)
        b=re.sub(r'\by\s*=\s*-?\d+',f'y = {y}',b,count=1)
        text=text[:start]+b+text[end:]
    for fid,(icon,cost,parents,reward,available) in NEW.items():
        if re.search(r'\bid\s*=\s*'+fid+r'\b',text):continue
        x,y=POSITIONS[fid]
        prereqs='\n'.join(' prerequisite = { '+' '.join('focus = '+p for p in group)+' }' for group in parents)
        b=f' focus = {{\n id = {fid}\n icon = {icon}\n x = {x}\n y = {y}\n cost = {cost}\n{prereqs}\n ai_will_do = {{ factor = 5 }}\n completion_reward = {{ {reward} }}\n'
        if available:b+=' available = { '+available+' }\n cancel_if_invalid = yes\n'
        b+=' }\n'
        text=text[:text.rfind('}')]+b+'}\n'
    assert len(list(blocks(text)))==len(POSITIONS)
    write(p,text)
    write(R/'common/ideas/JPD_development.txt',IDEAS)
    p=R/'common/ai_strategy_plans/A01_canonical.txt'
    ai=p.read_text(encoding='utf-8-sig')
    begin=ai.index('A03_southern_canonical_plan')
    head,tail=ai[:begin],ai[begin:]
    def extend_plan(m):
        ids=m[1].split()
        return 'ai_national_focuses = { '+' '.join(ids+[fid for fid in NEW if fid not in ids])+' }'
    tail,count=re.subn(r'ai_national_focuses\s*=\s*\{([^}]+)\}',extend_plan,tail,count=1)
    assert count==1
    write(p,head+tail)
    for lang,offset in [('russian',1),('english',3)]:
        p=R/f'localisation/{lang}/1896_main_l_{lang}.yml'
        text=p.read_text(encoding='utf-8-sig')
        entries={}
        for line in TEXT.strip().splitlines():
            fields=line.split('|')
            entries[fields[0]]=fields[offset]
            entries[fields[0]+'_desc']=fields[offset+1]
        entries.update({'JPD_finance_resolved_tt': ('Военная долговая книга закрыта через решение казначейства.' if lang=='russian' else 'The wartime ledger has been closed through the treasury decision.'),
                        'JPD_north_settled_tt': ('Постоянное соглашение с Сайго подписано.' if lang=='russian' else 'The permanent compact with Saigo has been signed.')})
        if lang=='russian':
            entries.update({
                'JPC_osaka_orders_desc': 'Адмиралтейский курс требует собственной промышленной базы. Расширение фабрик открывает военные заводы и верфи, затем единые производственные стандарты и инженерные школы. Завершение цепочки превратит военные подряды в самостоятельную промышленную систему с дополнительной исследовательской ячейкой.',
                'JPC_state_guarantees_desc': 'Ивасаки готов дать деньги на южный поход под будущие нефтяные доходы. Согласуем условия займа. Эта цепочка ведёт от срочных гарантий через проверку счетов и возврат вкладов к закрытию военной долговой книги и устойчивому бюджету.',
                'JPC_northern_protocol_desc': 'Договоримся с Сайго о нейтралитете Хоккайдо и поставках Северной армии. Исполнение выбранного порядка поставок создаст основу постоянного соглашения после войны. Подписанный договор позволит завершить раскол трёх сил, сохранив северное командование самостоятельным.',
                'JPC_manila_priority_desc': 'Наладим снабжение Манилы и выдадим гарнизону дополнительное вооружение. Выбор эскортов определит, какие следующие реформы потребуются. Учёт, интенданты и ротация затем сложатся в постоянную службу армейского снабжения, а не останутся мерами одной кампании.',
                'JPC_batavia_demands_desc': 'Согласуем задачи десанта и приказы эскадрам. Борнейская кампания даст опыт морских операций, охранения и длительного снабжения. Закрепление этого опыта позволит создать флот дальнего действия и постоянный объединённый штаб. Высадку и удержание плацдарма предстоит выполнить самим.',
                'JPC_three_heads_again_desc': 'После войны вернёмся к спору Ито, Сайго и Ивасаки. Теперь цель — завершить временный раскол: согласовать интересы армии и флота, определить полномочия Мэйдзи и подписать постоянный договор с Севером. Проведённые реформы позволят заменить соперничество ведомств устойчивым управлением.'})
        for key,value in entries.items():
            line=' '+key+':0 "'+value+'"'
            pattern=r'^ '+re.escape(key)+r':\d*\s*".*"'
            if re.search(pattern,text,re.M):text=re.sub(pattern,lambda m:line,text,flags=re.M)
            else:text=text.rstrip()+'\n'+line+'\n'
        write(p,text)
    print(f'Japan: {len(POSITIONS)} focuses; separate industry/finance, politics and military sectors; nine development milestones.')

if __name__=='__main__':apply()
