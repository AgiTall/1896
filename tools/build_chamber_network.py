"""Source for the Chamber and island-country expansion; never invokes old migrations."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
LOC = {"russian": {}, "english": {}}
TREES = {}
IDEAS = {}


def write(path, text, bom=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.rstrip() + "\n", encoding="utf-8-sig" if bom else "utf-8")


def loc(key, ru, en):
    for language, text in (("russian", ru), ("english", en)):
        assert key not in LOC[language], key
        LOC[language][key] = text


def idea(key, ru, en, ru_desc, en_desc, modifiers, picture="jpc_credit"):
    loc(key, ru, en)
    loc(key + "_desc", ru_desc, en_desc)
    IDEAS[key] = f" {key} = {{ picture = {picture} removal_cost = -1 modifier = {{ {modifiers} }} }}"


def focus(tree, suffix, ru, en, ru_desc, en_desc, x, y, parents=(), reward="add_political_power = 35", excludes=(), icon="GFX_goal_generic_national_unity", cost=5):
    key = tree + "_" + suffix
    if icon == "GFX_goal_generic_national_unity":
        if any(word in suffix for word in ("account", "credit", "reserve", "registry", "arbitration", "settlement")):
            icon = "GFX_goal_generic_political_pressure"
        elif any(word in suffix for word in ("tech", "cable", "malta", "measurement", "patent", "observers")):
            icon = "GFX_goal_generic_scientific_exchange"
        elif any(word in suffix for word in ("secret", "pirate", "wardens")):
            icon = "GFX_goal_generic_intelligence_exchange"
        elif "programme" in suffix or any(word in suffix for word in ("convoy", "ports", "routes", "foreign", "admiralty")):
            icon = "GFX_goal_generic_navy_doctrines_tactics"
    loc(key, ru, en)
    loc(key + "_desc", ru_desc, en_desc)
    parent_text = " ".join(f"prerequisite = {{ focus = {tree}_{parent} }}" for parent in parents)
    exclude_text = " ".join(f"mutually_exclusive = {{ focus = {tree}_{other} }}" for other in excludes)
    TREES[tree]["focuses"].append(dict(id=key, x=x, y=y, parents=[tree + "_" + p for p in parents]))
    TREES[tree]["scripts"].append(f" focus = {{ id = {key} icon = {icon} x = {x} y = {y} cost = {cost} {parent_text} {exclude_text} ai_will_do = {{ factor = 5 }} completion_reward = {{ {reward} }} }}")


def tree(name, tags):
    TREES[name] = dict(tags=tags, focuses=[], scripts=[])


def open_desk():
    return "set_country_flag = WTN_compact_desk_open custom_effect_tooltip = WTN_open_compact_tt"


def relations():
    return "set_country_flag = WTN_relations_open custom_effect_tooltip = WTN_open_relations_tt"


def repay(amount):
    return f"WTC_initialize_effect = yes add_to_variable = {{ WTC_debt = -{amount} }} WTC_refresh_effect = yes"


def timed(idea_id, days=180):
    return f"add_timed_idea = {{ idea = {idea_id} days = {days} }}"


def chamber():
    t = "WTN"
    tree(t, ["A04"])
    focus(t, "annual_report", "Годовой отчёт Ламберта", "Lambert's Annual Report", "Сведения о потерянных рейсах и долгах сойдутся под одной подписью. Директорат должен увидеть, на чём держится торговый порядок.", "Reports of lost voyages and unpaid accounts must meet beneath one signature. The directorate needs to know what sustains the trading order.", 12, 0, reward="WTN_initialize_effect = yes WTN_update_ledger_effect = yes add_political_power = 50")
    focus(t, "common_registry", "Единый реестр обязательств", "Common Register of Obligations", "Отделения Палаты обмениваются выписками, чтобы одна и та же выручка не служила залогом нескольким кредиторам. В Фуншале оборудуют мастерские для общих конторских и портовых служб.", "The Chamber's offices will exchange statements so the same receipts cannot secure several creditors. Funchal will equip workshops for common office and harbour services.", 12, 2, ["annual_report"], "WTN_update_ledger_effect = yes add_to_variable = { WTN_reputation = 5 } WTN_clamp_treasury_effect = yes WTN_local_workshops_effect = yes")
    finance = [
        ("credit_committee", "Кредитный комитет", "Credit Committee", "Новые займы пройдут через общий комитет. Каждому обещанию должна соответствовать запись о доступном резерве.", "New loans will pass through a common committee. Every promise must be backed by an available reserve.", "custom_effect_tooltip = WTN_credit_committee_tt"),
        ("gold_reserves", "Неприкосновенный резерв", "Protected Reserve", "Часть поступлений останется в Фуншале для покрытия задержек и непредвиденных убытков.", "Part of each settlement will remain in Funchal to cover delays and unexpected losses.", "add_to_variable = { WTN_liquidity = 15 } WTN_clamp_treasury_effect = yes"),
        ("arbitration", "Арбитраж долговых палат", "Debt Arbitration", "Долг, который нельзя взыскать, опаснее уступки. Арбитры получат право договариваться о частичном списании.", "An uncollectible debt is more dangerous than a concession. Arbitrators will be authorised to negotiate partial write-offs.", "custom_effect_tooltip = WTN_arbitration_tt"),
        ("reserve_audit", "Ревизия отделений", "Audit the Branch Offices", "Проверим выданные гарантии и отделим действительные залоги от обещаний местных посредников.", "We will inspect outstanding guarantees and separate real collateral from local agents' promises.", "add_to_variable = { WTN_reputation = 8 } WTN_clamp_treasury_effect = yes"),
        ("mutual_settlement", "Взаимный зачёт", "Mutual Settlement", "Встречные платежи можно сводить в Фуншале, освобождая суда от перевозки одних и тех же расписок.", "Reciprocal payments can be cleared in Funchal, sparing ships the carriage of the same bills in both directions.", "add_to_variable = { WTN_liquidity = 10 } WTN_clamp_treasury_effect = yes"),
        ("solvent_chamber", "Палата исполняет обязательства", "The Chamber Honours Its Obligations", "Отделения должны знать: директорат отвечает за собственную подпись так же, как требует ответа от должников. Постоянные мастерские получат дополнительные заказы для общей сети.", "Every branch must know that the directorate answers for its own signature as firmly as it holds debtors to theirs. Permanent workshops will receive additional orders for the common network.", "add_ideas = WTN_solvent_accounts WTN_local_workshops_effect = yes"),
    ]
    for i, (key, ru, en, rd, ed, reward) in enumerate(finance):
        focus(t, key, ru, en, rd, ed, 0, 4 + i * 2, ["common_registry" if i == 0 else finance[i-1][0]], reward)
    paths = [
        (6, "guard_charter", "Устав Старой гвардии", "Old Guard Charter", "Страховые дома предлагают укрепить привычный порядок: залоги, премии и ответственность капитанов.", "The insurance houses propose strengthening the established order of collateral, premiums and captains' liability.", "set_global_flag = WTC_guard_priority clr_global_flag = WTC_tech_priority clr_global_flag = WTC_secret_priority add_to_variable = { WTC_old_guard = 10 }", [
            ("silver_convoy", "Книги «Серебряного Конвоя»", "Silver Convoy Books", "Страховщики сведут сведения о потерях и перестанут назначать премии по слухам с пристаней.", "Insurers will consolidate loss records and stop pricing premiums from dockside rumours.", timed("WTN_insurance_office", 360)),
            ("insured_ports", "Смотрители застрахованных портов", "Inspectors of Insured Ports", "Смотрители проверят склады и порядок погрузки прежде, чем Палата примет риск на себя.", "Inspectors will check warehouses and loading practices before the Chamber accepts the risk.", "add_to_variable = { WTN_reputation = 5 } WTN_clamp_treasury_effect = yes"),
            ("market_rules", "Общие правила премий", "Common Premium Rules", "Отделениям запретят скрывать скидки и перекладывать убытки на соседние страховые дома.", "Branch offices will no longer conceal discounts or pass their losses to neighbouring insurance houses.", "add_political_power = 60"),
            ("guard_settlement_charter", "Порядок обеспеченных обязательств", "Order of Secured Obligations", "Кредиторы сохранят право на залог, но спор о нём будет решаться по общему уставу.", "Creditors will retain their claims to collateral, with disputes settled under a common charter.", "add_ideas = WTN_guard_settlement"),
        ]),
        (12, "tech_charter", "Мандат молодых технократов", "Technocrats' Mandate", "Инженеры предлагают вкладывать средства в связь и измерения, пока новые открытия не оставили Палату позади.", "Engineers propose investing in communications and measurement before new discoveries leave the Chamber behind.", "set_global_flag = WTC_tech_priority clr_global_flag = WTC_guard_priority clr_global_flag = WTC_secret_priority add_to_variable = { WTC_technocrats = 10 }", [
            ("cable_survey", "Обследовать кабельную сеть", "Survey the Cable Network", "Ремонтные суда сверят повреждённые линии, а станции договорятся о передаче срочных сообщений.", "Repair ships will survey damaged lines while cable stations agree on urgent-message handling.", timed("WTN_cable_office", 360)),
            ("malta_correspondence", "Переписка с Мальтой", "Correspondence with Malta", "Лабораториям нужны приборы и свободная переписка. Палата предложит оплату поставок без права присваивать чужие открытия.", "Laboratories need instruments and open correspondence. The Chamber will offer supply funding without claiming ownership of others' discoveries.", relations()),
            ("measurement_fund", "Фонд измерительных станций", "Measurement Station Fund", "Разрозненные наблюдения Песни станут полезнее, если приборы и журналы будут сопоставимы.", "Scattered observations of the Song will become more useful when instruments and records can be compared.", timed("WTN_research_contract", 360)),
            ("open_patents", "Договор о научной переписке", "Scientific Correspondence Charter", "Обмен сведениями даст Палате место за столом исследователей, сохраняя самостоятельность лабораторий.", "Exchanging reports will give the Chamber a seat among researchers while preserving laboratory independence.", "add_ideas = WTN_technical_directorate"),
        ]),
        (18, "secret_charter", "Полномочия Тайного департамента", "Secret Department Mandate", "Директорат поручит особому отделу проверять посредников и узнавать о закрытых сделках до их подписания.", "The directorate will task a special department with checking agents and learning of secret agreements before they are signed.", "set_global_flag = WTC_secret_priority clr_global_flag = WTC_guard_priority clr_global_flag = WTC_tech_priority add_to_variable = { WTC_secret_department = 10 }", [
            ("cable_watch", "Закрытые кабельные сводки", "Confidential Cable Summaries", "Кабельные служащие будут отделять коммерческие слухи от сведений, требующих внимания директората.", "Cable clerks will separate commercial gossip from reports requiring the directorate's attention.", timed("WTN_cable_office", 360)),
            ("strait_wardens", "Договоры со Стражами Проливов", "Strait Warden Contracts", "Наёмной охране поручат склады и причалы. Условия найма должны исключать самостоятельные походы от имени Палаты.", "Hired guards will protect warehouses and wharves. Their contracts must forbid independent campaigns in the Chamber's name.", timed("WTN_warden_contract", 360)),
            ("pirate_contacts", "Посредники в вольных гаванях", "Agents in Free Harbours", "Непризнанные капитаны знают обходные пути. Их услуги сохранят связь ценой доверия открытых торговых домов.", "Unrecognised captains know alternate routes. Their services will preserve links at the cost of established merchants' trust.", "add_to_variable = { WTN_reputation = -8 } WTN_clamp_treasury_effect = yes " + timed("WTC_pirate_channels", 360)),
            ("secret_accounts_control", "Отчётность закрытого отдела", "Confidential Department Accounts", "Даже тайные расходы должны иметь предел. Директорат потребует отчёта о людях, договорах и утраченных средствах.", "Even secret expenditure needs limits. The directorate will demand accounts of agents, contracts and lost funds.", "add_ideas = WTN_secret_accounts"),
        ]),
    ]
    heads = [p[1] for p in paths]
    for x, head, ru, en, rd, ed, reward, rows in paths:
        focus(t, head, ru, en, rd, ed, x, 4, ["common_registry"], reward + " WTN_clamp_directorate_effect = yes", [h for h in heads if h != head])
        parent = head
        for i, (key, ru, en, rd, ed, reward) in enumerate(rows):
            focus(t, key, ru, en, rd, ed, x, 6 + i * 2, [parent], reward)
            parent = key
    diplomacy = [
        ("foreign_offices", "Отделения островного мира", "Offices of the Island World", "Фуншал должен слышать не только крупнейших должников, но и небольшие гавани, через которые проходит торговля.", "Funchal must hear not only its largest debtors but also the small harbours through which trade passes.", relations()),
        ("british_understanding", "Соглашение с Левиафаном", "Understanding with the Leviathan", "Британский флот охраняет пути Палаты, но его адмиралы ждут признания собственных расходов и интересов.", "The British fleet protects the Chamber's routes, but its admirals expect their own costs and interests to be recognised.", "add_political_power = 50"),
        ("pacific_accounts", "Тихоокеанские счета", "Pacific Accounts", "Батавия, Токио и Осака связаны торговлей даже тогда, когда их штабы готовятся к столкновению.", "Batavia, Tokyo and Osaka remain bound by trade even when their staffs prepare for conflict.", "add_to_variable = { WTN_liquidity = 8 } WTN_clamp_treasury_effect = yes"),
        ("colonial_desks", "Шесть австралийских отделений", "Six Australian Desks", "Каждая колония ведёт собственные счета. Общий представитель не вправе подписывать обязательства за соседей.", "Each colony keeps its own accounts. A common representative cannot sign obligations on behalf of its neighbours.", "add_to_variable = { WTN_reputation = 5 } WTN_clamp_treasury_effect = yes"),
        ("caribbean_routes", "Карибские маршруты", "Caribbean Routes", "Гаванские посредники готовы обсуждать проводку судов, но не признают за Палатой права распоряжаться их берегами.", "Havana's agents will discuss ship routing but will not recognise a Chamber right to dispose of their shores.", timed("WTN_caribbean_contract", 360)),
        ("northern_observers", "Наблюдатели северных морей", "Observers in the Northern Seas", "Записи исландских и мальтийских учёных помогут оценить слухи о переменах на покинутых берегах.", "Icelandic and Maltese scientific reports will help assess rumours of changes along abandoned shores.", timed("WTN_research_contract", 180)),
        ("island_congress_protocol", "Конгресс торговых представителей", "Congress of Trade Delegates", "Островные правительства получат общий порядок переговоров с Палатой, сохраняя право отвергать её условия.", "Island governments will receive a common negotiating procedure with the Chamber while retaining the right to reject its terms.", "add_ideas = WTN_island_congress"),
    ]
    for i, (key, ru, en, rd, ed, reward) in enumerate(diplomacy):
        focus(t, key, ru, en, rd, ed, 24, 4 + i * 2, ["common_registry" if i == 0 else diplomacy[i-1][0]], reward)


def country_tree(code, tags, opening, economy, independence, cooperation, local_rows):
    """Common readable topology; each country's policy and text are authored below."""
    tree(code, tags)
    ru, en, rd, ed = opening
    focus(code, "council", ru, en, rd, ed, 6, 0, reward="WTC_initialize_effect = yes add_political_power = 45")
    ru, en, rd, ed = economy
    focus(code, "accounts", ru, en, rd, ed, 6, 2, ["council"], repay(5))
    ru, en, rd, ed = independence
    independent_id = "independent_admiralty" if code == "WTN_BRI" else "own_resources"
    focus(code, independent_id, ru, en, rd, ed, 2, 4, ["accounts"], repay(10) + " add_stability = -0.02 " + timed("WTN_domestic_workshops", 240), ["chamber_channel"])
    ru, en, rd, ed = cooperation
    focus(code, "chamber_channel", ru, en, rd, ed, 10, 4, ["accounts"], open_desk(), [independent_id])
    # Both policy choices lead to the same practical programme without requiring both.
    ru, en, rd, ed, reward = local_rows[0]
    focus(code, "local_service", ru, en, rd, ed, 6, 6, reward=reward + " WTN_local_workshops_effect = yes", icon="GFX_goal_generic_construct_civ_factory")
    TREES[code]["scripts"][-1] = TREES[code]["scripts"][-1].replace("ai_will_do", f"prerequisite = {{ focus = {code}_{independent_id} focus = {code}_chamber_channel }} ai_will_do")
    TREES[code]["focuses"][-1]["parents"] = [code + "_" + independent_id, code + "_chamber_channel"]
    for i, (ru, en, rd, ed, reward) in enumerate(local_rows[1:]):
        suffix = f"programme_{i+1}"
        parent = "local_service" if i == 0 else f"programme_{i}"
        if i == len(local_rows) - 2:
            reward += " WTN_local_workshops_effect = yes"
        focus(code, suffix, ru, en, rd, ed, 6, 8 + i * 2, [parent], reward)


def countries():
    country_tree("WTN_BRI", ["A02"],
        ("Совет уцелевшего Адмиралтейства", "Council of the Surviving Admiralty", "Разбросанные базы требуют общих приказов, а правительство на Бермудах — отчёта об их исполнении.", "Scattered bases need common orders, and the government in Bermuda requires an account of their execution."),
        ("Счета имперских стоянок", "Accounts of the Imperial Stations", "Адмиралы сверят долги стоянок и расходы на суда, прежде чем обещать новые походы.", "The admirals will reconcile station debts and ship expenses before promising new campaigns."),
        ("Самостоятельное Адмиралтейство", "Independent Admiralty", "Собственные сборы помогут сократить зависимость от Фуншала. Флот получит право пересмотреть охрану путей Палаты.", "Our own revenues will reduce dependence on Funchal. The fleet will be authorised to reconsider its protection of Chamber routes."),
        ("Цена морского прикрытия", "The Price of Naval Cover", "Палата пользуется британской охраной. Обсудим зачёт части долга в обмен на обслуживание её морских путей.", "The Chamber benefits from British protection. We shall discuss a debt credit in return for servicing its sea routes."), [
        ("Диспетчеры океанских станций", "Ocean Station Dispatchers", "Станции согласуют сроки переходов и перестанут требовать одни и те же суда одновременно.", "Stations will coordinate sailing dates and stop demanding the same ships at the same time.", timed("WTN_british_contract", 240)),
        ("Переговоры о нефти Батавии", "Talks over Batavian Oil", "Без топлива не удержать океан. Торговым представителям поручат прямую переписку с Батавией.", "The ocean cannot be held without fuel. Trade delegates will open direct correspondence with Batavia.", relations()),
        ("Колониальные представители", "Colonial Delegates", "Австралийские кабинеты должны обсуждать снабжение своими голосами, а не получать единый счёт из Гамильтона.", "Australian cabinets must discuss supplies in their own voices rather than receive a single bill from Hamilton.", "add_stability = 0.04 add_political_power = 40"),
        ("Мальтийские приборы", "Instruments for Malta", "Доставим лабораториям измерительное оборудование и защитим научную переписку морской почтой.", "We will deliver measuring equipment to the laboratories and protect scientific correspondence by sea mail.", timed("WTN_research_contract", 240)),
        ("Ремонт между переходами", "Repairs between Voyages", "Списки запасных деталей будут сопровождать корабли от одной стоянки к другой.", "Spare-parts lists will accompany ships from one station to the next.", timed("WTN_warden_contract", 240)),
        ("Левиафан держит пути", "The Leviathan Holds the Routes", "Разбросанные гавани смогут полагаться на согласованное расписание и общие морские службы.", "Scattered harbours will be able to rely on coordinated timetables and common naval services.", "add_ideas = WTN_british_stations"),
    ])
    country_tree("WTN_RUS", ["A06"],
        ("Двор и канцелярия в Рейкьявике", "Court and Chancellery in Reykjavik", "Императорский двор и церковная канцелярия должны разобраться, кто отвечает за повседневную жизнь изгнания.", "The imperial court and church chancellery must establish who answers for the daily business of exile."),
        ("Перепись северных запасов", "Inventory of Northern Stores", "Зимние запасы и долги купцам сведут в общие ведомости, открытые ответственным чиновникам.", "Winter stores and merchant debts will be entered in common records accessible to responsible officials."),
        ("Сборы общин изгнания", "Levies of the Exile Communities", "Общины помогут оплатить снабжение своими средствами, хотя новые сборы вызовут недовольство.", "The communities will help finance supplies themselves, although new levies will cause resentment."),
        ("Кредит северным лабораториям", "Credit for Northern Laboratories", "Учёные предлагают принимать целевые поставки приборов через Палату и сохранять собственные журналы наблюдений.", "Scientists propose accepting designated instrument deliveries through the Chamber while retaining their own observation journals."), [
        ("Портовые службы Рейкьявика", "Reykjavik Harbour Services", "Общие склады помогут зимующим судам пережить задержку очередного рейса.", "Common stores will help wintering ships withstand delays to the next voyage.", timed("WTN_northern_contract", 240)),
        ("Письма мальтийским учёным", "Letters to Maltese Scientists", "Обменяемся измерениями с Мальтой, не передавая ей ни лаборатории, ни право говорить от имени двора.", "We will exchange measurements with Malta without transferring our laboratories or the right to speak for the court.", relations()),
        ("Правила береговых наблюдений", "Rules for Coastal Observations", "Наблюдатели будут сверять записи, чтобы слух о тишине не стал приказом к неподготовленному возвращению.", "Observers will compare records so that a rumour of silence does not become an order for an unprepared return.", timed("WTN_research_contract", 240)),
        ("Ответственность северных чиновников", "Accountable Northern Officials", "Портовым чиновникам придётся отвечать за утраченные грузы перед общинами и двором.", "Harbour officials will answer to the communities and court for missing cargo.", "add_stability = 0.04 add_political_power = 35"),
        ("Северные журналы", "Northern Journals", "Сохраним сведения о побережьях для будущих экспедиций, не обещая безопасной дороги через Песнь.", "We will preserve coastal reports for future expeditions without promising a safe passage through the Song.", "add_ideas = WTN_northern_observatory"),
    ])
    country_tree("WTN_OSA", ["A09"],
        ("Совет осакских торговых домов", "Council of Osaka Trading Houses", "Ивасаки соберёт дома, чьи расписки поддерживают мастерские и связывают их с кредиторами.", "Iwasaki will convene the houses whose bills sustain the workshops and bind them to creditors."),
        ("Свести векселя Мицубиси", "Reconcile Mitsubishi Bills", "Отделим обязательства торговых домов от обещаний императорским подрядчикам.", "We will separate trading-house obligations from promises made to imperial contractors."),
        ("Сократить незакрытые заказы", "Reduce Unsettled Orders", "Откажемся от части обещанных поставок, чтобы рассчитаться по старым обязательствам собственными средствами.", "We will abandon some promised deliveries to settle older obligations with our own funds."),
        ("Осакская расчётная палата", "Osaka Clearing Office", "Через Фуншал можно сводить внешние платежи, сохраняя за домами право выбирать своих заказчиков.", "Foreign payments can be cleared through Funchal while the houses retain the right to choose their customers."), [
        ("Мастерские по общим ведомостям", "Workshops under Common Ledgers", "Мастера получат согласованные списки деталей вместо противоречивых требований нескольких домов.", "Craftsmen will receive agreed parts lists instead of conflicting demands from several houses.", timed("WTN_osaka_contract", 240)),
        ("Заказы Токио и Хакодате", "Orders from Tokyo and Hakodate", "Торговые представители смогут обсуждать поставки с обоими японскими правительствами без обещания политического подчинения.", "Trade delegates will discuss supplies with both Japanese governments without promising political submission.", relations()),
        ("Общие условия приёмки", "Common Acceptance Standards", "Единая проверка качества уменьшит споры между заказчиками и мастерами.", "A common quality inspection will reduce disputes between customers and craftsmen.", "add_political_power = 50 add_stability = 0.02"),
        ("Запасы для паровых мастерских", "Stores for Steam Workshops", "Мастерские подготовят материалы и инструменты к перебоям в морской доставке.", "Workshops will prepare materials and tools against interruptions to sea deliveries.", timed("WTN_domestic_workshops", 240)),
        ("Торговля собственной подписью", "Trade under Our Own Signature", "Осакские дома будут отвечать по своим счетам, сохраняя самостоятельное место среди островных правительств.", "Osaka's houses will answer for their own accounts while retaining an independent place among island governments.", "add_ideas = WTN_osaka_accounts"),
    ])
    country_tree("WTN_NOR", ["A08"],
        ("Северный совет Сайго", "Saigo's Northern Council", "Гарнизоны Хоккайдо должны договориться о снабжении, не отдавая свою судьбу южным штабам.", "Hokkaido's garrisons must agree on supplies without placing their fate in southern staffs' hands."),
        ("Пересчитать зимние склады", "Count the Winter Stores", "Проверим, сколько зерна, одежды и запасных частей действительно дошло до северных гарнизонов.", "We will establish how much grain, clothing and spare equipment actually reached the northern garrisons."),
        ("Северные общинные заказы", "Northern Community Orders", "Общины возьмут часть снабжения на себя, сокращая необходимость новых займов.", "Local communities will take on part of the supply burden, reducing the need for fresh loans."),
        ("Гарантии северных поставок", "Guarantees for Northern Supplies", "Палате предложат обеспечить морскую доставку без права вмешиваться в командование армии.", "The Chamber will be asked to secure sea deliveries without a right to interfere in army command."), [
        ("Интенданты зимнего перехода", "Quartermasters of the Winter Crossing", "Интенданты подготовят единые ведомости для складов и гарнизонов.", "Quartermasters will prepare common records for stores and garrisons.", timed("WTN_northern_contract", 240)),
        ("Самостоятельные переговоры с югом", "Independent Talks with the South", "Встречи с Токио и Осакой должны решать вопросы торговли, сохраняя отдельный северный кабинет.", "Meetings with Tokyo and Osaka must address trade while preserving a separate northern government.", relations()),
        ("Береговые ремонтные артели", "Coastal Repair Cooperatives", "Местные мастерские смогут чинить походное имущество и готовить стрелковое вооружение, не ожидая каждого груза из южных портов.", "Local workshops will repair field equipment and prepare small arms without awaiting every shipment from southern ports.", timed("WTN_domestic_workshops", 240) + " WTN_armourer_workshops_effect = yes"),
        ("Нейтралитет с обеспечением", "Provisioned Neutrality", "Собственные склады дадут северному командованию больше свободы при ответе на чужие требования.", "Our own stores will give northern command greater freedom when answering outside demands.", "add_ideas = WTN_northern_stores"),
    ])
    country_tree("WTN_IRN", ["A05"],
        ("Гаванский совет Грейвса", "Graves's Havana Council", "Военные капитаны и портовые общины должны найти средства для жизни среди враждующих берегов.", "Naval captains and harbour communities must find the means to survive among hostile shores."),
        ("Счета гаванских пристаней", "Accounts of Havana's Wharves", "Запишем портовые сборы и обязательства посредникам, отделив их от неподтверждённых военных обещаний.", "We will record harbour dues and agents' claims separately from unverified wartime promises."),
        ("Собственные портовые сборы", "Our Own Harbour Dues", "Доходы причалов пойдут на погашение обязательств, даже если торговым домам придётся ждать новых заказов.", "Wharf revenues will settle obligations even if trading houses must wait for fresh orders."),
        ("Страхование гаванских рейсов", "Insurance for Havana Voyages", "Обсудим с Фуншалом покрытие торговых рейсов, сохраняя контроль над собственными пристанями.", "We will discuss cover for merchant voyages with Funchal while retaining control of our wharves."), [
        ("Лоцманы западной Кубы", "Pilots of Western Cuba", "Капитаны сведут записи об отмелях и местах сбора торговых судов.", "Captains will consolidate records of shoals and merchant rendezvous.", timed("WTN_caribbean_contract", 240)),
        ("Переписка с океанскими державами", "Correspondence with Ocean Powers", "Гавана предложит Британии и Батавии торговые соглашения без передачи островных владений.", "Havana will propose commercial agreements to Britain and Batavia without transferring island possessions.", relations()),
        ("Доковые ремонтные команды", "Dock Repair Teams", "Сохранившиеся станки и опыт механиков послужат регулярному ремонту торговых судов.", "Surviving machinery and engineers' experience will support regular repairs to merchant ships.", timed("WTN_warden_contract", 240)),
        ("Ответственность портовых командиров", "Accountable Harbour Commanders", "Командиры будут отчитываться перед советом о задержанных грузах и расходах на охрану.", "Commanders will report detained cargo and security expenditure to the council.", "add_stability = 0.04 add_political_power = 35"),
        ("Гавана сохраняет торговый выход", "Havana Keeps Its Trading Outlet", "Устойчивое морское сообщение позволит общинам меньше зависеть от исхода каждого отдельного рейса.", "Reliable sea links will make communities less dependent on the outcome of each individual voyage.", "add_ideas = WTN_havana_routes"),
    ])
    country_tree("WTN_AUS", ["A07", "AVC", "AQL", "ASA", "AWA", "ATA"],
        ("Кабинет самоуправляющейся колонии", "Cabinet of the Self-Governing Colony", "Местный парламент будет отвечать за свои расходы и говорить с соседями от имени собственной колонии.", "The local parliament will answer for its own expenditure and speak to neighbours on its colony's behalf."),
        ("Колониальные бюджетные ведомости", "Colonial Budget Statements", "Доходы гаваней и расходы на снабжение должны быть понятны избранным представителям.", "Harbour revenues and supply expenditure must be clear to elected representatives."),
        ("Местные сбережения", "Local Savings", "Колония оплатит часть обязательств собственными средствами, отложив наиболее дорогие заказы.", "The colony will settle part of its obligations from its own resources, postponing its most expensive orders."),
        ("Собственное отделение Палаты", "Our Own Chamber Office", "Фуншал получит предложение отдельного соглашения с нашим кабинетом, не связывающего соседние колонии.", "Funchal will receive a proposal for a separate agreement with our cabinet, placing no obligation on neighbouring colonies."), [
        ("Складские службы колонии", "Colonial Warehouse Services", "Портовые команды согласуют хранение грузов и снабжение внутренних поселений.", "Harbour crews will coordinate cargo storage and the supply of inland settlements.", timed("WTN_colonial_contract", 240)),
        ("Межколониальная переписка", "Intercolonial Correspondence", "Кабинеты смогут договариваться о поставках, сохраняя отдельные парламенты и собственные счета.", "Cabinets will negotiate supplies while retaining separate parliaments and accounts.", relations()),
        ("Признание торговых ведомостей", "Recognise Trading Documents", "Согласуем форму накладных, чтобы груз не задерживался у каждого соседнего причала.", "We will agree on manifests so cargo is not delayed at every neighbouring wharf.", "add_political_power = 45 add_stability = 0.02"),
        ("Ремонт местного транспорта", "Repair Local Transport", "Мастерские займутся оборудованием, связывающим порт с поселениями колонии.", "Workshops will maintain the equipment linking the harbour to the colony's settlements.", timed("WTN_domestic_workshops", 240)),
        ("Совещание равноправных кабинетов", "Conference of Equal Cabinets", "Общие торговые правила можно обсуждать без передачи власти над колониями единому правительству.", "Common trading rules can be discussed without transferring authority over the colonies to a single government.", "add_ideas = WTN_colonial_council"),
    ])
    country_tree("WTN_SUL", ["A11", "A12", "A13", "A14"],
        ("Совет двора и гавани", "Council of Court and Harbour", "Двор выслушает купцов и общины, чьи суда поддерживают связь султаната с соседними островами.", "The court will hear the merchants and communities whose ships connect the sultanate with neighbouring islands."),
        ("Реестр портовых обязательств", "Register of Harbour Obligations", "Проверим обещания посредникам, прежде чем они станут основанием для новых требований к двору.", "We will inspect agents' claims before they become grounds for fresh demands upon the court."),
        ("Сборы под надзором двора", "Dues under Court Supervision", "Местные сборы помогут расплатиться по старым счетам, сохраняя их учёт в руках двора.", "Local dues will settle older accounts while their records remain in the court's hands."),
        ("Посредник в Фуншале", "An Agent in Funchal", "Представитель султаната обсудит страхование и расчёты с Палатой от имени собственного двора.", "The sultanate's representative will discuss insurance and settlement with the Chamber on the court's own behalf."), [
        ("Смотрители прибрежных складов", "Keepers of Coastal Stores", "Общины подготовят склады к перебоям морского сообщения.", "Communities will prepare stores against interruptions to sea traffic.", timed("WTN_island_contract", 240)),
        ("Переговоры с соседними державами", "Talks with Neighbouring Powers", "Посланники смогут обсуждать торговлю с Батавией, Токио и Филиппинами без обещания уступить власть султана.", "Envoys will discuss trade with Batavia, Tokyo and the Philippines without promising to surrender the sultan's authority.", relations()),
        ("Порядок местного ремонта", "Local Repair Arrangements", "Мастера разделят работы по содержанию причалов и торговых судов.", "Craftsmen will share the work of maintaining wharves and merchant ships.", timed("WTN_domestic_workshops", 240)),
        ("Договоры от имени султаната", "Treaties in the Sultanate's Name", "Двор сохранит собственную подпись под торговыми обязательствами и право отвечать на чужие предложения.", "The court will retain its own signature on trade obligations and the right to answer outside proposals.", "add_ideas = WTN_harbour_court"),
    ])


def remaining_countries():
    rows = [
        ("WTN_MLT", ["MLT"],
         ("Совет мальтийского двора", "Council of the Maltese Court", "Русский двор на Мальте должен согласовать расходы с общинами и британскими морскими властями.", "The Russian court in Malta must agree its expenditure with the communities and British naval authorities."),
         ("Ведомости лабораторных поставок", "Laboratory Supply Statements", "Приборы, реактивы и корабельные накладные сведут в проверяемые записи.", "Instruments, reagents and shipping manifests will be entered in verifiable records."),
         ("Подписка общин на приборы", "Community Subscription for Instruments", "Общины оплатят самые необходимые поставки, отложив дорогие заказы кредитных посредников.", "The communities will fund essential supplies while postponing expensive orders from credit agents."),
         ("Договор о научных поставках", "Scientific Supply Agreement", "Посреднику в Фуншале предложат оплачивать поставки, сохраняя независимость мальтийских лабораторий.", "Our agent in Funchal will propose funding deliveries while preserving the Maltese laboratories' independence."),
         ("Склад приборов у гавани", "Instrument Store by the Harbour", "Портовые мастера оборудуют склад и мастерские для ремонта доставленных приборов.", "Harbour craftsmen will equip a store and workshops to repair imported instruments."),
         ("Переписка с Исландией и Бермудами", "Correspondence with Iceland and Bermuda", "Посланники будут договариваться о доставке и научной почте с северным двором и британским Адмиралтейством.", "Envoys will negotiate delivery and scientific mail with the northern court and British Admiralty."),
         ("Сопоставимые лабораторные журналы", "Comparable Laboratory Journals", "Учёные сохранят записи в едином порядке, чтобы различать наблюдение и неподтверждённую догадку.", "Scientists will maintain consistent records to distinguish observations from unconfirmed conjecture."), "WTN_research_contract"),
        ("WTN_PCF", ["PCF"],
         ("Совет центральнокубинских поместий", "Council of the Central Cuban Estates", "Плантаторы Борегара обсуждают снабжение и долги поместий, сохраняющих старый принудительный порядок.", "Beauregard's planters debate supplies and debts across estates that preserve the old coercive order."),
         ("Обязательства плантационных домов", "Plantation House Obligations", "Отделим действительные торговые счета от обещаний, выданных военными посредниками.", "We will separate genuine trading accounts from promises issued by wartime agents."),
         ("Оплатить счета урожаем", "Settle Accounts from the Harvest", "Доходы поместий пойдут на погашение обязательств вместо новых дорогих заказов.", "Estate revenues will settle obligations instead of funding expensive new orders."),
         ("Страховщики центральной Кубы", "Insurers for Central Cuba", "Представители поместий предложат Палате отдельные условия вывоза грузов.", "Estate delegates will propose separate terms for cargo shipments to the Chamber."),
         ("Складские дворы Санта-Клары", "Santa Clara Storeyards", "Местные мастерские и склады приведут в порядок партии товаров перед отправкой к морю.", "Local workshops and stores will prepare consignments before their journey to the sea."),
         ("Прямые торговые посланники", "Direct Trade Envoys", "Посланники обсудят торговые рейсы с Британией и Батавией без признания чужой власти над поместьями.", "Envoys will discuss voyages with Britain and Batavia without recognising foreign authority over the estates."),
         ("Оружейные мастерские поместий", "Estate Armourer Workshops", "Плантационные дома сведут заказы оружейникам и подготовят места для ремонта и изготовления стрелкового вооружения.", "The plantation houses will consolidate armourers' orders and prepare facilities for repairing and producing small arms."), "WTN_caribbean_contract"),
        ("WTN_PAZ", ["PAZ"],
         ("Военный совет Сьерра-Маэстры", "Military Council of the Sierra Maestra", "Штабы Эрнандеса и служители Пророка должны разделить ответственность за снабжение удерживаемых берегов.", "Hernandez's staffs and the Prophet's servants must share responsibility for supplying the coasts they hold."),
         ("Пересчитать береговые запасы", "Count the Coastal Stores", "Проверим, какие грузы дошли до поселений, а какие остались обещаниями посредников.", "We will establish which consignments reached the settlements and which remained agents' promises."),
         ("Сборы подвластных общин", "Levies of the Subject Communities", "Местные сборы сократят обязательства перед заморскими кредиторами ценой отложенных заказов.", "Local levies will reduce obligations to overseas creditors at the cost of postponed orders."),
         ("Посланники к страховым домам", "Envoys to the Insurance Houses", "Представители обсудят ограниченное соглашение морских служб с Фуншалом.", "Delegates will discuss a limited voyage-services agreement with Funchal."),
         ("Береговые мастерские восточной Кубы", "Eastern Cuban Coastal Workshops", "Мастерские займутся ремонтом имущества и хранением припасов для поселений.", "Workshops will repair equipment and store provisions for the settlements."),
         ("Переговоры за пределами Карибов", "Talks beyond the Caribbean", "Торговые представители смогут обсуждать поставки с внешними державами отдельно от военных требований.", "Trade delegates will discuss supplies with outside powers separately from military demands."),
         ("Общие записи снабжения", "Common Supply Records", "Штабы и береговые старосты будут сверять ведомости полученных грузов.", "Staffs and coastal headmen will reconcile records of delivered cargo."), "WTN_northern_contract"),
        ("WTN_PHR", ["PHR"],
         ("Совет общин Урагана", "Council of the Hurricane Communities", "Общины Мамы Бриджит должны договориться, кто отвечает за гавани и распределение привезённых припасов.", "Maman Brigitte's communities must agree who answers for the harbours and distribution of imported provisions."),
         ("Общинные книги поставок", "Community Supply Books", "Сведём записи о доставленном продовольствии и обещаниях торговых капитанов.", "We will compile records of delivered food and merchant captains' promises."),
         ("Рассчитаться без чужих управляющих", "Settle without Foreign Receivers", "Общины соберут средства на старые обязательства и отложат дорогие новые закупки.", "The communities will raise funds for old obligations and postpone expensive new purchases."),
         ("Страхование без уступки гавани", "Insurance without Surrendering the Harbour", "Посланники предложат Палате торговое соглашение, сохраняющее общинный контроль над причалами.", "Envoys will propose a Chamber agreement preserving community control of the wharves."),
         ("Общинные склады у моря", "Community Stores by the Sea", "Мастера подготовят склады и ремонтные дворы для судов, снабжающих поселения.", "Craftsmen will prepare stores and repair yards for ships supplying the settlements."),
         ("Посланники свободных общин", "Envoys of the Free Communities", "Представители будут говорить с Британией и Батавией от имени своих общин.", "Delegates will speak to Britain and Batavia on their communities' behalf."),
         ("Согласовать прибрежные рейсы", "Coordinate Coastal Voyages", "Капитаны сверят места встречи судов и порядок передачи припасов.", "Captains will agree ship rendezvous and the handling of provisions."), "WTN_caribbean_contract"),
        ("WTN_HAW", ["PHW"],
         ("Королевский совет Гонолулу", "Royal Council of Honolulu", "Королевский совет обсудит, как сохранить нейтральную гавань среди соперничающих морских держав.", "The royal council will discuss preserving a neutral harbour among rival sea powers."),
         ("Счета нейтральной гавани", "Accounts of the Neutral Harbour", "Казна сверит сборы и расходы, прежде чем принимать новые обязательства иностранных посредников.", "The treasury will reconcile dues and expenditure before accepting fresh obligations to foreign agents."),
         ("Собственные королевские сборы", "Our Own Royal Revenues", "Доходы гавани помогут рассчитаться с кредиторами, сохраняя самостоятельный выбор внешней торговли.", "Harbour revenues will help settle with creditors while preserving our own choice of foreign trade."),
         ("Гавайское страховое представительство", "Hawaiian Insurance Delegation", "Королевский представитель обсудит с Фуншалом обслуживание торговых рейсов без исключительных политических прав.", "The royal delegate will discuss merchant voyage services with Funchal without granting exclusive political rights."),
         ("Мастерские Гонолулу", "Honolulu Workshops", "Портовые мастера подготовят склады и ремонтные места для судов дальнего плавания.", "Harbour craftsmen will prepare stores and repair facilities for ocean-going ships."),
         ("Приём иностранных капитанов", "Receive Foreign Captains", "Гонолулу предложит равные правила морских служб Британии, Японии и торговым домам Палаты.", "Honolulu will propose equal voyage-services rules to Britain, Japan and Chamber trading houses."),
         ("Правила нейтрального причала", "Rules of the Neutral Wharf", "Смотрители будут применять согласованный порядок к торговым судам разных флагов.", "Harbour keepers will apply agreed procedures to merchant ships of different flags."), "WTN_island_contract"),
        ("WTN_SEA", ["PSY", "PTG", "PKR", "PPM", "PZN", "PPE"],
         ("Совет островного порта", "Island Harbour Council", "Местная власть и портовые представители должны договориться о снабжении и расходах морской связи.", "Local authorities and harbour delegates must agree on supplies and the cost of sea links."),
         ("Проверить обязательства посредникам", "Review Agents' Claims", "Проверим, какие обещания даны от имени нашей гавани и чем они обеспечены.", "We will check which promises were made in our harbour's name and how they are secured."),
         ("Расплатиться местными средствами", "Settle from Local Resources", "Доходы гавани пойдут на погашение старых счетов, сокращая зависимость от очередного рейса кредитора.", "Harbour revenues will settle old accounts, reducing dependence on the creditor's next voyage."),
         ("Соглашение с Фуншалом", "Agreement with Funchal", "Наш представитель обсудит ограниченное обслуживание рейсов, не уступая управление местной власти.", "Our delegate will discuss limited voyage services without surrendering local authority."),
         ("Мастерские и береговые склады", "Workshops and Coastal Stores", "Мастера подготовят ремонтные места и защищённые склады для морских поставок.", "Craftsmen will prepare repair facilities and sheltered stores for sea deliveries."),
         ("Соседские морские службы", "Neighbouring Voyage Services", "Посланники предложат подходящим соседям согласовать места встречи судов и торговую переписку.", "Envoys will propose coordinating ship rendezvous and trading correspondence with suitable neighbours."),
         ("Общие записи портовых команд", "Common Harbour Crew Records", "Приёмщики и капитаны смогут сверять грузовые ведомости по одинаковым правилам.", "Receivers and captains will compare cargo manifests under common rules."), "WTN_island_contract"),
        ("WTN_PHI", ["PLS", "PSL", "PCB", "PPN", "PVI", "PSM", "PMD", "PNM", "PNL", "PML", "PBT"],
         ("Совет островного правительства", "Council of the Island Government", "Представители местной власти обсудят снабжение острова и отношения с другими филиппинскими правительствами.", "Local representatives will discuss island supplies and relations with other Philippine governments."),
         ("Местные счета и общие обещания", "Local Accounts and Common Promises", "Отделим собственные обязательства от обещаний, которые другие делегации дали от нашего имени.", "We will separate our own obligations from promises other delegations made on our behalf."),
         ("Снабжение силами острова", "Supply from Island Resources", "Местные средства помогут погасить счета, сохраняя самостоятельное решение о новых закупках.", "Local resources will settle accounts while preserving our own choice over new purchases."),
         ("Собственная делегация в Палату", "Our Own Delegation to the Chamber", "Наши представители предложат Фуншалу торговое соглашение, которое не связывает другие филиппинские кабинеты.", "Our delegates will propose a Funchal agreement placing no obligation on other Philippine cabinets."),
         ("Ремонтные дворы острова", "Island Repair Yards", "Местные мастера подготовят склады и ремонтное оборудование для снабжающих остров судов.", "Local craftsmen will prepare stores and repair equipment for ships supplying the island."),
         ("Самостоятельная торговая переписка", "Independent Trading Correspondence", "Посланники смогут договариваться о морских службах, сохраняя собственную власть и действующие союзы.", "Envoys will negotiate voyage services while retaining their own authority and existing alliances."),
         ("Согласовать приёмку припасов", "Coordinate Supply Acceptance", "Портовые команды и местные власти сверят ведомости прибывающих грузов.", "Harbour crews and local authorities will reconcile manifests of arriving supplies."), "WTN_island_contract"),
    ]
    for code, tags, opening, accounts, own, pact, local, relation, administration, spirit in rows:
        administrative_reward = "add_stability = 0.03 add_political_power = 40"
        if code == "WTN_PCF":
            administrative_reward += " WTN_armourer_workshops_effect = yes"
        country_tree(code, tags, opening, accounts, own, pact, [
            (*local, timed(spirit, 240)),
            (*relation, relations()),
            (*administration, administrative_reward),
            ("Устойчивые островные службы", "Reliable Island Services", "Согласованные склады, ремонт и переписка помогут местной власти поддерживать связь с внешним миром.", "Coordinated stores, repair work and correspondence will help local authorities maintain links with the wider world.", "add_ideas = WTN_local_services"),
        ])


def ideas():
    rows = [
        ("british_contract", "Оплаченные океанские стоянки", "Funded Ocean Stations", "Согласованные расчёты помогают морским станциям поддерживать ремонт и снабжение.", "Agreed settlements help naval stations sustain repair and supply services.", "industrial_capacity_dockyard = 0.03 naval_supply_consumption_factor = -0.03"),
        ("osaka_contract", "Осакские расчётные ведомости", "Osaka Clearing Statements", "Торговые дома согласуют платежи и очередность промышленных заказов.", "Trading houses coordinate settlements and the order of industrial work.", "production_factory_efficiency_gain_factor = 0.04"),
        ("northern_contract", "Сверенные северные запасы", "Verified Northern Stores", "Интенданты знают, какие грузы находятся в складах и какие ещё идут морем.", "Quartermasters know which supplies are in store and which are still at sea.", "supply_consumption_factor = -0.03"),
        ("research_contract", "Обмен научной перепиской", "Scientific Correspondence Exchange", "Учёные получают приборы и сопоставимые журналы наблюдений, сохраняя самостоятельность своих лабораторий.", "Scientists receive instruments and comparable observation journals while retaining their laboratories' independence.", "research_speed_factor = 0.02"),
        ("caribbean_contract", "Согласованные карибские рейсы", "Coordinated Caribbean Voyages", "Капитаны и посредники согласуют места встречи и передачи грузов.", "Captains and agents agree on rendezvous and cargo handovers.", "convoy_escort_efficiency = 0.04"),
        ("colonial_contract", "Колониальные торговые ведомости", "Colonial Trading Statements", "Склады и мастерские получают согласованные сведения о поступлении материалов.", "Warehouses and workshops receive coordinated reports of incoming materials.", "production_speed_buildings_factor = 0.03"),
        ("island_contract", "Островные складские соглашения", "Island Warehouse Agreements", "Посредники и портовые команды работают по согласованным правилам хранения и расчёта.", "Agents and harbour crews follow agreed storage and settlement rules.", "production_speed_buildings_factor = 0.02 naval_coordination = 0.02"),
        ("domestic_workshops", "Заказы собственным мастерским", "Orders for Domestic Workshops", "Местные мастера согласуют работу, чтобы реже ожидать срочных морских поставок.", "Local craftsmen coordinate their work to reduce dependence on urgent sea deliveries.", "production_factory_efficiency_gain_factor = 0.03"),
        ("insurance_office", "Сверенные страховые книги", "Reconciled Insurance Books", "Палата оценивает потери по проверенным сведениям своих отделений.", "The Chamber assesses losses from verified branch reports.", "political_power_gain = 0.05"),
        ("cable_office", "Согласованная кабельная служба", "Coordinated Cable Service", "Станции передают срочные сообщения по согласованной очереди.", "Stations transmit urgent messages in an agreed order.", "naval_coordination = 0.03"),
        ("warden_contract", "Договоры охраны и ремонта", "Security and Repair Contracts", "Наёмная охрана отвечает за причалы, а мастерские — за готовность судов к рейсу.", "Hired guards answer for wharf security while workshops prepare ships for their voyages.", "industrial_capacity_dockyard = 0.03"),
        ("solvent_accounts", "Обеспеченные счета Палаты", "Solvent Chamber Accounts", "Отделения сверяют обязательства с доступными средствами, поддерживая доверие к общей подписи.", "Branch offices reconcile obligations against available funds, sustaining confidence in their common signature.", "stability_factor = 0.03"),
        ("guard_settlement", "Устав обеспеченных обязательств", "Secured Obligations Charter", "Страховые дома соблюдают общий порядок рассмотрения залоговых споров.", "Insurance houses observe a common procedure for collateral disputes.", "political_power_gain = 0.08"),
        ("technical_directorate", "Технический директорат", "Technical Directorate", "Инженеры участвуют в решениях о связи, снабжении приборов и научной переписке.", "Engineers participate in decisions on communications, instrument supplies and scientific correspondence.", "research_speed_factor = 0.03"),
        ("secret_accounts", "Подотчётный Тайный департамент", "Accountable Secret Department", "Закрытый отдел обязан объяснять расходы директорату, даже когда имена посредников остаются в запечатанных делах.", "The confidential department must explain expenditure to the directorate even when agents' names remain sealed.", "political_power_gain = 0.05 naval_coordination = 0.02"),
        ("island_congress", "Конгресс торговых представителей", "Congress of Trade Delegates", "Островные представители пользуются общим порядком переговоров с Палатой.", "Island delegates follow a common negotiating procedure with the Chamber.", "stability_factor = 0.03 political_power_gain = 0.03"),
        ("british_stations", "Сеть британских стоянок", "British Station Network", "Адмиралтейские станции обмениваются расписаниями и сведениями о ремонте.", "Admiralty stations exchange timetables and repair reports.", "naval_coordination = 0.03"),
        ("northern_observatory", "Северные наблюдательные журналы", "Northern Observation Journals", "Наблюдения сведены в сопоставимые записи и сохранены для дальнейших исследований.", "Observations have been compiled into comparable records and preserved for further research.", "research_speed_factor = 0.02"),
        ("osaka_accounts", "Ответственные торговые дома", "Accountable Trading Houses", "Торговые дома отвечают по своим счетам и поддерживают общий порядок приёмки заказов.", "Trading houses answer for their accounts and sustain common acceptance standards.", "production_factory_efficiency_gain_factor = 0.03"),
        ("northern_stores", "Северное складское хозяйство", "Northern Storekeeping", "Собственные склады помогают гарнизонам выдерживать перебои связи с югом.", "Our own stores help garrisons withstand interruptions to southern links.", "supply_consumption_factor = -0.02"),
        ("havana_routes", "Торговый выход Гаваны", "Havana Trading Outlet", "Гаванские посредники поддерживают устойчивую связь с внешними торговыми домами.", "Havana's agents maintain reliable links with foreign trading houses.", "convoy_escort_efficiency = 0.03"),
        ("colonial_council", "Совещания колониальных кабинетов", "Colonial Cabinet Conferences", "Отдельные кабинеты обсуждают общие торговые дела, сохраняя самостоятельные парламенты.", "Separate cabinets discuss common trade affairs while retaining their own parliaments.", "stability_factor = 0.03"),
        ("harbour_court", "Двор и торговые представители", "Court and Trade Delegates", "Представители двора отвечают за переговоры, а портовые общины — за исполнение местных договоров.", "Court delegates answer for negotiations while harbour communities fulfil local agreements.", "stability_factor = 0.03"),
        ("island_cooperation", "Договор островных служб", "Island Services Agreement", "Оба правительства согласовали обмен морскими ведомостями и порядок обслуживания торговых рейсов.", "Both governments have agreed to exchange maritime records and coordinate merchant voyage services.", "naval_coordination = 0.02"),
        ("local_services", "Устойчивые местные службы", "Reliable Local Services", "Местная власть согласовала работу складов, ремонтных дворов и торговых представителей.", "Local authorities have coordinated warehouses, repair yards and trade delegates.", "stability_factor = 0.02"),
        ("link_research_services", "Совместные наблюдательные журналы", "Joint Observation Journals", "Исландские и мальтийские исследователи обмениваются записями через согласованные морские службы.", "Icelandic and Maltese researchers exchange records through coordinated maritime services.", "research_speed_factor = 0.02"),
        ("link_workshop_services", "Осакско-токийские производственные ведомости", "Osaka–Tokyo Production Records", "Заказчики и мастерские сверяют сведения о деталях и очередности поставок.", "Customers and workshops reconcile parts records and delivery priorities.", "production_factory_efficiency_gain_factor = 0.02"),
        ("link_northern_services", "Северный порядок поставок", "Northern Delivery Arrangements", "Северные и южные представители согласуют приёмку грузов, сохраняя отдельные правительства.", "Northern and southern delegates coordinate cargo acceptance while retaining separate governments.", "supply_consumption_factor = -0.02"),
        ("link_fuel_services", "Сопровождение батавских грузов", "Escort for Batavian Cargo", "Британские и батавские портовые службы согласуют морские рейсы, обслуживающие торговлю топливом.", "British and Batavian harbour services coordinate voyages serving the fuel trade.", "naval_supply_consumption_factor = -0.03"),
        ("link_colonial_services", "Межколониальная грузовая служба", "Intercolonial Cargo Service", "Кабинеты согласовали приёмку строительных грузов, не объединяя колониальные казначейства.", "Cabinets have coordinated construction cargo acceptance without merging colonial treasuries.", "production_speed_buildings_factor = 0.02"),
        ("link_caribbean_services", "Согласованные карибские эскорты", "Coordinated Caribbean Escorts", "Карибские и внешние капитаны согласуют места встречи торговых судов с охранением.", "Caribbean and foreign captains coordinate merchant rendezvous with their escorts.", "convoy_escort_efficiency = 0.02"),
    ]
    for key, ru, en, rd, ed, modifiers in rows:
        idea("WTN_" + key, ru, en, rd, ed, modifiers)
    # Treaty services have their own IDs: cancellation must preserve domestic focus rewards.
    for key, ru, en, rd, ed, modifiers in rows:
        if key in ("british_contract", "osaka_contract", "northern_contract", "research_contract", "caribbean_contract", "colonial_contract", "island_contract"):
            idea("WTN_pact_" + key.removesuffix("_contract") + "_services", "Палата: " + ru, "Chamber: " + en, rd, ed, modifiers)


def interface_text():
    texts = [
        ("WTC_debt", "Долг Палате", "Chamber Debt"),
        ("WTC_old_guard", "Влияние Старой гвардии", "Old Guard Influence"),
        ("WTC_technocrats", "Влияние технократов", "Technocrat Influence"),
        ("WTC_secret_department", "Влияние Тайного департамента", "Secret Department Influence"),
        ("WTN_liquidity", "Кредитный резерв", "Credit Reserve"),
        ("WTN_reputation", "Репутация Палаты", "Chamber Reputation"),
        ("WTN_principal", "Суммарный индекс обязательств", "Aggregate Obligation Index"),
        ("WTN_accounts", "Долговые счета", "Debtor Accounts"),
        ("WTN_distressed", "Счета под угрозой", "Distressed Accounts"),
        ("WTN_partners", "Соглашения Палаты", "Chamber Agreements"),
        ("WTN_suspend_credit", "Приостановить новые кредитные линии", "Suspend New Credit Lines"),
        ("WTN_suspend_credit_desc", "Прекратить открытие новых стандартных кредитов и целевых поставок. Предложения, под которые резерв уже выделен, сохраняют силу до ответа или истечения срока.", "Stop opening new standard credits and supply offers. Existing offers backed by reserved funds remain valid until answered or expired."),
        ("WTN_resume_credit", "Возобновить кредитные линии", "Resume Credit Lines"),
        ("WTN_resume_credit_desc", "Вновь разрешить новые кредитные предложения в пределах доступного резерва.", "Allow new credit offers again within the available reserve."),
        ("WTN_world_accounts", "Мировая долговая книга", "World Debt Ledger"),
        ("WTN_world_accounts_desc", "Резерв Палаты: §Y[?WTN_liquidity|0]/100§!\\nРепутация: §Y[?WTN_reputation|0]/100§!\\nОбязательства: §Y[?WTN_principal|0]§!\\nСчета с долгом: §Y[?WTN_accounts|0]§!; под угрозой: §R[?WTN_distressed|0]§!\\nДействующие соглашения: §Y[?WTN_partners|0]§!\\nСводка обновляется ежемесячно и при проверке счёта. Кредитное предложение резервирует 10 единиц до ответа; непринятое возвращает резерв.", "Chamber reserve: §Y[?WTN_liquidity|0]/100§!\\nReputation: §Y[?WTN_reputation|0]/100§!\\nOutstanding principal: §Y[?WTN_principal|0]§!\\nDebtor accounts: §Y[?WTN_accounts|0]§!; distressed: §R[?WTN_distressed|0]§!\\nActive agreements: §Y[?WTN_partners|0]§!\\nTotals refresh monthly and on account review. A credit offer reserves 10 points until answered; unaccepted offers return the reserve."),
        ("WTN_foreign_desks", "Торговые представительства", "Trade Delegations"),
        ("WTN_foreign_desks_desc", "Наш долг Палате: §Y[?WTC_debt|0]/100§!\\nКредитный резерв Фуншала: §Y[?A04.WTN_liquidity|0]/100§!\\nПоставки, страхование и расчёты требуют отдельных соглашений. Отправленное предложение не связывает вторую сторону до её ответа.", "Our Chamber debt: §Y[?WTC_debt|0]/100§!\\nFunchal credit reserve: §Y[?A04.WTN_liquidity|0]/100§!\\nDeliveries, insurance and clearing require separate agreements. A proposal does not bind the other government until it responds."),
        ("WTN_offer_credit", "Предложить кредит: [FROM.GetName]", "Offer Credit: [FROM.GetName]"),
        ("WTN_offer_credit_desc", "Зарезервируем средства для поставки транспортов и оснащения. Получатель решит, принимать ли обязательство.", "Reserve funds for transport and equipment deliveries. The recipient decides whether to accept the obligation."),
        ("WTN_review_account", "Счёт [FROM.GetName]: [?FROM.WTC_debt|0]", "[FROM.GetName] Account: [?FROM.WTC_debt|0]"),
        ("WTN_review_account_desc", "Сверить счёт и обновить мировую сводку обязательств.", "Reconcile this account and update the world debt summary."),
        ("WTN_account_report_tt", "Долг [FROM.GetName]: §Y[?FROM.WTC_debt|0]/100§!.", "[FROM.GetName] debt: §Y[?FROM.WTC_debt|0]/100§!."),
        ("WTN_relieve_account", "Списать часть долга: [FROM.GetName]", "Partial Debt Relief: [FROM.GetName]"),
        ("WTN_relieve_account_desc", "Сократить долг на 12 за 8 единиц резерва. Повторное списание этому кабинету — не ранее чем через 360 дней.", "Reduce debt by 12 at a cost of 8 reserve points. Further relief for this government is possible after 360 days."),
        ("WTN_recapitalise", "Собрать чрезвычайные взносы", "Raise Emergency Contributions"),
        ("WTN_recapitalise_desc", "Добавить 20 единиц резерва ценой 3 единиц репутации. Новые взносы можно собирать раз в 180 дней.", "Gain 20 reserve points at a cost of 3 reputation. Contributions may be raised every 180 days."),
        ("WTN_request_credit", "Запросить целевую поставку Палаты", "Request a Chamber Supply Credit"),
        ("WTN_request_credit_desc", "При согласии: 15 транспортов и 75 вспомогательного оснащения за 15 долга; дополнительные проценты начисляются шесть месяцев. Средства резервируются до ответа, срок ответа — 30 дней.", "On acceptance: 15 convoys and 75 support equipment for 15 debt; additional interest accrues for six months. Funds are reserved pending a response, which must arrive within 30 days."),
        ("WTN_request_compact", "Предложить соглашение торговых служб", "Propose a Trade Services Agreement"),
        ("WTN_request_compact_desc", "Предложить Палате годовое соглашение. При согласии долг увеличится на 5; британские морские услуги вместо этого сокращают его на 5. Услуги соответствуют нуждам нашей страны.", "Propose a one-year agreement to the Chamber. Acceptance adds 5 debt; British naval services instead reduce it by 5. Services reflect our country's needs."),
        ("WTN_terminate_compact", "Расторгнуть соглашение с Палатой", "Terminate the Chamber Agreement"),
        ("WTN_terminate_compact_desc", "Прекратить услуги по соглашению. Ранее принятый долг сохраняется; срыв поставок вызывает недовольство.", "End the services covered by the agreement. Previously accepted debt remains, and interrupted deliveries cause discontent."),
        ("WTN_revoke_cover", "Отозвать британское прикрытие Палаты", "Withdraw British Cover from the Chamber"),
        ("WTN_revoke_cover_desc", "Отозвать флотское обеспечение кредитного принуждения. Без него Палата не сможет поддерживать чёрный список и навязывать долговые кабинеты.", "Withdraw naval support for credit enforcement. Without it, the Chamber cannot sustain its blacklist or impose receivership governments."),
        ("WTN_restore_cover", "Возобновить британское прикрытие", "Restore British Naval Cover"),
        ("WTN_restore_cover_desc", "Вновь поручить флоту охрану путей Палаты при сохранении мира с Фуншалом.", "Resume naval protection of Chamber routes while peace with Funchal lasts."),
        ("WTN_open_compact_tt", "Открывает предложение соглашения в торговых представительствах. Палата вправе отказать.", "Unlocks a trade-services proposal in Trade Delegations. The Chamber may refuse."),
        ("WTN_open_relations_tt", "Открывает предложения взаимного обслуживания морских рейсов подходящим партнёрам. Вторая сторона вправе отказать.", "Unlocks proposals for reciprocal voyage services with eligible partners. The other government may refuse."),
        ("WTN_credit_committee_tt", "Открывает адресные кредитные предложения в мировой долговой книге.", "Unlocks targeted credit offers in the World Debt Ledger."),
        ("WTN_arbitration_tt", "Открывает адресное списание части долга за средства Палаты.", "Unlocks targeted debt relief funded from the Chamber's reserve."),
        ("wtn_network.1.t", "Предложение из Фуншала", "An Offer from Funchal"),
        ("wtn_network.1.d", "Представитель Палаты предлагает оплатить фрахт транспортов и доставку оснащения. Взамен казна признает новое обязательство; его обслуживание войдёт в общие расчёты с Фуншалом. Подписи нашего кабинета под договором пока нет.", "The Chamber's agent offers to fund transport charters and equipment deliveries. In return, our treasury must recognise a new obligation, serviced through our accounts in Funchal. Our cabinet has yet to sign."),
        ("wtn_network.1.a", "Подписать условия поставки", "Sign the delivery terms"),
        ("wtn_network.1.b", "Отказаться от нового обязательства", "Decline the new obligation"),
        ("wtn_network.3.t", "Торговое представительство [FROM.GetName]", "A Trade Delegation from [FROM.GetName]"),
        ("wtn_network.3.d", "Представительство предлагает согласовать обслуживание рейсов и расчёты с Палатой. Делегаты подчёркивают: их кабинет сохраняет самостоятельность, а соглашение касается только оговорённых торговых служб.", "The delegation proposes coordinating voyage services and settlements with the Chamber. Its delegates insist that their cabinet remains independent and that the agreement covers only the specified trade services."),
        ("wtn_network.3.a", "Согласовать условия с представителями", "Agree terms with the delegates"),
        ("wtn_network.3.b", "Отложить заключение соглашения", "Decline to conclude an agreement"),
        ("wtn_network.4.t", "Палата подтвердила соглашение", "The Chamber Confirms the Agreement"),
        ("wtn_network.4.d", "Из Фуншала поступили подписанные ведомости. Представители Палаты согласовали обслуживание рейсов и порядок расчётов; наши портовые службы получили условия работы на предстоящий сезон.", "Signed statements have arrived from Funchal. Chamber delegates have agreed voyage services and settlement procedures; our harbour services have received the arrangements for the coming season."),
        ("wtn_network.5.t", "Переговоры остались без соглашения", "Talks End without an Agreement"),
        ("wtn_network.5.d", "Посланники завершили переписку с Фуншалом без подтверждённых условий. Кабинету предстоит опираться на собственные морские службы и вновь оценить предложения посредников.", "Our envoys have closed their correspondence with Funchal without confirmed terms. The cabinet must rely on its own maritime services and reassess the agents' proposals."),
        ("wtn_network.ack", "Принять донесение к сведению", "Acknowledge the report"),
    ]
    for key, ru, en in texts:
        loc(key, ru, en)


def main():
    ideas()
    chamber()
    countries()
    remaining_countries()
    interface_text()
    for name, data in TREES.items():
        selectors = " ".join(f"modifier = {{ add = 100 tag = {tag} }}" for tag in data["tags"])
        if (ROOT / "tools/minor_campaign_manifest.json").exists():
            from minor_campaign_profiles import PROFILES
            selectors = " ".join(f"modifier = {{ add = 100 tag = {tag} }}" for tag in data["tags"] if tag not in PROFILES)
        if name == "WTN_AUS" and (ROOT / "common/national_focus/AUC_campaign_A07.txt").exists():
            selectors = ""  # The six Australian campaign trees own these countries.
        if name == "WTN_BRI" and (ROOT / "common/national_focus/BLV_campaign.txt").exists():
            selectors = ""  # Britain has a dedicated campaign and its own Chamber branch.
        write(f"common/national_focus/{name}_focus.txt", f"focus_tree = {{ id = {name}_focus country = {{ factor = 0 {selectors} }} default = no continuous_focus_position = {{ x = 100 y = 1900 }}\n" + "\n".join(data["scripts"]) + "\n}")
    write("common/ideas/WTN_network.txt", "ideas = { country = {\n" + "\n".join(IDEAS.values()) + "\n} }")
    for language, entries in LOC.items():
        write(f"localisation/{language}/WTN_network_l_{language}.yml", "l_" + language + ":\n" + "\n".join(f' {key}:0 "{text}"' for key, text in entries.items()), bom=True)
    write("tools/chamber_network_manifest.json", json.dumps({name: {k: v for k, v in data.items() if k != "scripts"} for name, data in TREES.items()}, ensure_ascii=False, indent=2))
    from focus_shapes import apply as apply_shapes
    apply_shapes()
    print(f"Built {len(TREES)} base trees with compact campaign layouts.")


if __name__ == "__main__":
    main()
