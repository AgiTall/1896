from pathlib import Path
R=Path(__file__).resolve().parents[1]
ru={
'A01_surya_wirata_name':'Раден Сурья Вирата',
'A01_japan.2.t':'Индонезийцы отказываются воевать',
'A01_japan.2.d':'В портах обсуждают будущую войну, но призывные списки остаются пустыми. Индонезийские матросы и рабочие спрашивают, почему они должны защищать правительство, отказывающее им в равных правах. Одна прокламация не вернёт доверия. Совет предлагает поручить публичное выступление одному из трёх адмиралов; затем предстоит ответить на возражения его коллег и утвердить конкретные меры.',
'A01_japan.2.hard':'Касемброот: дисциплина прежде уступок.',
'A01_japan.2.balance':'Фабиус: обязанности в обмен на гарантии.',
'A01_japan.2.support':'Сурья Вирата: вооружить местных добровольцев.',
'A01_japan.10.t':'Касемброот требует повиновения',
'A01_japan.10.d':'«Пока неприятель готовит корабли, обсуждать приказ поздно», — заявляет Касемброот. Он требует полицейского сопровождения призыва и наказания дезертиров. Часть офицеров приветствует решительность, но в казармах слова адмирала воспринимают как обещание новых облав.',
'A01_japan.11.t':'Фабиус предлагает договор о службе',
'A01_japan.11.d':'«Флоту нужны надёжные экипажи, а не запуганные люди», — говорит Фабиус. Он предлагает прозрачное жалованье, помощь семьям и расследование злоупотреблений, сохранив обязательную службу. Обе стороны ждут, превратятся ли обещания в распоряжения.',
'A01_japan.12.t':'Сурья Вирата обращается к островам',
'A01_japan.12.d':'«Наша земля принадлежит и тем, кто на ней родился», — заявляет Сурья Вирата. Он предлагает добровольческие части с местными командирами и гарантирует их роспуск после войны. В портах появляются желающие защищать свои дома, но европейские офицеры опасаются самостоятельных вооружённых отрядов.',
'A01_japan.20.t':'Адмиралы спорят о принуждении',
'A01_japan.20.d':'Фабиус предупреждает Касемброота: принудительный призыв даст людей сегодня и ненадёжные части завтра. Сурья Вирата сообщает о бегстве семей из портовых кварталов. Жёсткий курс улучшит мобилизацию лишь частично и усилит недоверие; потребуются полиция и дальнейшие разбирательства.',
'A01_japan.21.t':'Компромисс под перекрёстным огнём',
'A01_japan.21.d':'Касемброот считает уступки Фабиуса наградой за неповиновение. Сурья Вирата отвечает, что равного жалованья недостаточно без местных командиров. Фабиус настаивает на проверяемых гарантиях и отказывается обещать мгновенное примирение.',
'A01_japan.22.t':'Кто будет командовать добровольцами?',
'A01_japan.22.d':'Касемброот требует разоружить будущие отряды сразу после мира. Фабиус предлагает включить их снабжение в общую систему. Сурья Вирата принимает единый оборонный план, но требует местных командиров и письменного обязательства распустить ополчение после окончания войны.',
'A01_japan.30.t':'Служба под принуждением',
'A01_japan.30.d':'Правительство утверждает полицейский призыв. Часть уклонистов возвращается, однако доверие не восстановлено: сохраняются нехватка новобранцев и проблемы с организацией частей. Жёсткий курс снижает стабильность и может вызвать новое партизанское выступление.',
'A01_japan.31.t':'Гарантии Фабиуса утверждены',
'A01_japan.31.d':'Проверка жалованья и защита семей становятся обязательными. Султаны смогут направлять жалобы в постоянный совет. Уклонение сокращается, но часть населения по-прежнему не желает служить колониальной администрации. Компромисс требует денег и постоянного исполнения обещаний.',
'A01_japan.32.t':'Островное добровольческое ополчение',
'A01_japan.32.d':'На Яве формируются три дивизии местного добровольческого ополчения. Они получают оружие и подчиняются общему оборонному плану. Их мандат ограничен войной с Японией: после мира отряды будут распущены. Добровольцы укрепляют доверие, но не устраняют все причины отказа от службы.',
'A01_japan.40.t':'Ополчение возвращается домой',
'A01_japan.40.d':'Военный кризис с Японией завершён. В соответствии с обещанием правительства добровольческие дивизии расформированы, их временный военный мандат прекращён. Вопрос о постоянном участии индонезийцев в управлении остаётся открытым.',
'A01_indonesian_refusal':'Массовый отказ от службы',
'A01_indonesian_refusal_desc':'До завершения переговоров и выступлений призывные участки пустуют, а доверие в частях падает.',
'A01_coerced_service':'Принудительная мобилизация',
'A01_coerced_service_desc':'Полиция вернула часть призывников, но принуждение не восстановило доверия. Сохраняются уклонение, организационные проблемы и политическая напряжённость.',
'A01_service_compromise':'Договор о колониальной службе',
'A01_service_compromise_desc':'Гарантии жалованья и помощи семьям смягчили конфликт. Уклонение уменьшилось, однако полного согласия ещё нет.',
'A01_indonesian_volunteers':'Индонезийские добровольцы',
'A01_indonesian_volunteers_desc':'Три временные дивизии защищают острова под местным командованием. Они будут распущены после войны с Японией.',
'A03_southern_blitz':'Стремительная южная кампания',
'A03_southern_blitz_desc':'На 180 дней флот и десантные силы получают приоритет снабжения: усиленный обстрел берега, повышенные атака и дальность флота, ускоренные подготовка и проведение высадок. После полугода программа прекращается.',
'A03_southern_preparations':'Последние приготовления к южной войне',
'A03_charter_transports':'Зафрахтовать дополнительные транспорты',
'A03_charter_transports_desc':'Сокращает активный таймер вторжения в Ост-Индию на 15 дней. Решение доступно один раз.',
'A03_advance_coaling':'Перенести вперёд сроки снабжения',
'A03_advance_coaling_desc':'Сокращает активный таймер вторжения на 20 дней. Решение доступно один раз.',
'A03_final_sailing_orders':'Отдать окончательные приказы эскадре',
'A03_final_sailing_orders_desc':'Сокращает активный таймер вторжения на 30 дней. Решение доступно один раз.',
'southern_war.2.t':'Япония ускоряет приготовления',
'southern_war.2.d':'Разведка сообщает о переносе сроков японских морских приготовлений. Наш активный таймер вторжения сокращён. До начала войны остаётся меньше времени, чем рассчитывал кабинет.',
'southern_war.2.a':'Проверить новый срок мобилизации.',
'A03_southern_campaign_desc':'Подготовим десантные части, тяжёлые корабли и запасы для Борнео. Завершение программы сокращает активный таймер вторжения ещё на 30 дней. Война начнётся по окончании этого таймера.',
'A03_southern_reconstruction_desc':'По Борнейской конвенции Япония получила северные районы и Лимбанг. Восстановим промышленность Сабаха и закрепим новые владения.',
'ludolf.20.d':'Японское морское давление заставило Батавию согласиться на переговоры. Конвенция передаёт Японии Сабах, Бруней и Лимбанг (1024, 1023 и 1059); Ост-Индия получает Саравак и западный Калимантан (333 и 1022). За Японией закрепляются права на нефть и каучук Борнео. Военное ополчение будет распущено, а правительству предстоит пережить последствия поражения.',
'ludolf.21.d':'Борнейская конвенция закрепляет за Японией районы 1024, 1023 и 1059. Батавия получает 333 и 1022, признав японские права на нефть и каучук Борнео. Морская кампания завершена; начинается восстановление новых владений.'
}
for n in [10,11,12,20,21,22,30,31,32]:ru[f'A01_japan.{n}.a']='Продолжить обсуждение.' if n<30 else 'Утвердить этот порядок.'
ru['A01_japan.40.a']='Выполнить обещание добровольцам.'
en={
'A01_surya_wirata_name':'Raden Surya Wirata',
'A01_japan.2.t':'Indonesians Refuse to Serve',
'A01_japan.2.d':'Empty recruiting offices reveal a conflict that one proclamation cannot settle. Choose an admiral to address the population, hear the other officers, and enact a policy.',
'A01_japan.2.hard':'Casembroot: discipline before concessions.',
'A01_japan.2.balance':'Fabius: duties in exchange for guarantees.',
'A01_japan.2.support':'Surya Wirata: arm local volunteers.',
'A01_indonesian_refusal':'Widespread Refusal to Serve','A01_indonesian_refusal_desc':'Recruitment and unit cohesion suffer while the government debates its response.',
'A01_coerced_service':'Coerced Recruitment','A01_coerced_service_desc':'Police measures recover some recruits, but distrust, organisational problems and instability persist.',
'A01_service_compromise':'Colonial Service Compact','A01_service_compromise_desc':'Pay and family guarantees reduce refusal without removing its deeper causes.',
'A01_indonesian_volunteers':'Indonesian Volunteers','A01_indonesian_volunteers_desc':'Three temporary militia divisions defend the islands. They disband when the war with Japan ends.',
'A03_southern_blitz':'Swift Southern Campaign','A03_southern_blitz_desc':'For 180 days: stronger shore bombardment, increased attack and naval range, faster invasion preparation and landings, and additional invasion capacity.',
'A03_southern_preparations':'Final Southern Preparations',
'A03_charter_transports':'Charter Additional Transports','A03_charter_transports_desc':'Shortens the active invasion countdown by 15 days. Once only.',
'A03_advance_coaling':'Advance the Supply Schedule','A03_advance_coaling_desc':'Shortens the active invasion countdown by 20 days. Once only.',
'A03_final_sailing_orders':'Issue Final Sailing Orders','A03_final_sailing_orders_desc':'Shortens the active invasion countdown by 30 days. Once only.',
'southern_war.2.t':'Japan Accelerates Preparations','southern_war.2.d':'Intelligence reports an earlier Japanese sailing schedule. The active invasion countdown has been shortened.','southern_war.2.a':'Review the revised deadline.',
'A03_southern_campaign_desc':'Prepare marines, heavy ships and supplies. Completing the programme shortens the active invasion countdown by another 30 days; war begins when that countdown expires.',
'A03_southern_reconstruction_desc':'The Borneo Convention awarded Japan the northern territories and Limbang. Restore industry in Sabah and consolidate the settlement.',
'ludolf.20.d':'The Convention transfers states 1024, 1023 and 1059 to Japan; the East Indies receive 333 and 1022. Japan receives Borneo oil and rubber rights. Temporary militia will disband and the government must face the defeat.',
'ludolf.21.d':'Japan receives 1024, 1023 and 1059 under the Convention. Batavia receives 333 and 1022 and recognises Japanese oil and rubber rights across Borneo.',
'A01_japan.40.t':'The Militia Goes Home','A01_japan.40.d':'The military crisis with Japan has ended. In accordance with the government pledge, the volunteer divisions have been disbanded. The wider question of Indonesian political participation remains unresolved.','A01_japan.40.a':'Honour the promise.'}
titles=['Casembroot Demands Obedience','Fabius Offers a Service Compact','Surya Wirata Appeals to the Islands','Admirals Debate Coercion','The Compromise Under Fire','Who Commands the Volunteers?','Service Under Compulsion','Fabius Guarantees Enacted','Island Volunteer Militia']
descs=[
'Casembroot demands police-backed conscription and punishment for deserters. Other officers warn that obedience obtained through fear will not create reliable formations.',
'Fabius proposes transparent pay, family support and investigations of abuse while retaining compulsory service. The population demands enforceable guarantees.',
'Surya Wirata calls for local volunteers led by local officers, with a written promise to disband after the war. European officers fear autonomous armed formations.',
'Fabius warns of unreliable conscripts. Surya Wirata reports families fleeing port districts. Coercion restores only part of recruitment and risks renewed unrest.',
'Casembroot calls concessions a reward for disobedience; Surya Wirata demands local commanders. Fabius insists on practical, enforceable guarantees.',
'Casembroot demands disarmament after peace. Fabius proposes common supply arrangements. Surya Wirata accepts joint defence with local commanders and a limited wartime mandate.',
'Police conscription restores some manpower, but recruitment and organisation penalties remain. Stability falls and another partisan outbreak may follow.',
'Pay inspections and family protections become binding. A council of sultans can hear complaints. Refusal decreases, but some communities still oppose colonial service.',
'Three equipped volunteer militia divisions assemble on Java under local commanders. They will disband when the war with Japan ends; volunteering does not erase every grievance.'
]
for n,title,desc in zip([10,11,12,20,21,22,30,31,32],titles,descs):en[f'A01_japan.{n}.t']=title;en[f'A01_japan.{n}.d']=desc;en[f'A01_japan.{n}.a']='Continue the debate.' if n<30 else 'Enact this policy.'
assert ru.keys()==en.keys(),(ru.keys()-en.keys(),en.keys()-ru.keys())
for lang,data in [('russian',ru),('english',en)]:
 p=R/f'localisation/{lang}/zzz_borneo_war_l_{lang}.yml'
 p.write_text('l_'+lang+':\n'+''.join(f' {k}:0 "{v}"\n' for k,v in data.items()),encoding='utf-8-sig')
print(len(ru),'RU/EN localisation keys')
