"""Authored country identities. Dormant tags receive content, not new territory."""
PROFILES={}
def profile(tag,ru,en,capital,kind,partners,threat,opening,opening_en,civic,civic_en,command,command_en,economy,economy_en,defence,defence_en,project,project_en,crisis,crisis_en,goal,goal_en,objective='stock'):
    PROFILES[tag]=dict(tag=tag,ru=ru,en=en,capital=capital,kind=kind,partners=partners.split(),threat=threat,opening=opening,opening_en=opening_en,civic=civic,civic_en=civic_en,command=command,command_en=command_en,economy=economy.split('|'),economy_en=economy_en.split('|'),defence=defence.split('|'),defence_en=defence_en.split('|'),project=project,project_en=project_en,crisis=crisis,crisis_en=crisis_en,goal=goal,goal_en=goal_en,objective=objective)

profile('A05','Железный Союз','Iron Union',315,'convoy','PHW PCF','PAZ',
 'Гавана кормит американских изгнанников, но эскадры требуют угля, а верфи — рабочих рук. Морская республика и постоянное адмиральское правление предлагают разную цену единства.',
 'Havana feeds American exiles while its squadrons need coal and its yards need workers. A naval republic and permanent admiral rule offer different forms of unity.',
 'Конгресс гаванских общин','Congress of Havana Communities','Мандат адмирала Грейвса','Admiral Graves\' Mandate',
 'Ведомости Гаванского порта|Мастерские беженцев|Контракты американских капитанов','Havana Port Ledgers|Refugee Workshops|American Captains\' Contracts',
 'Гаванские добровольцы|Охрана Пуэрто-Рико|Снабжение Карибской эскадры','Havana Volunteers|Guard Puerto Rico|Caribbean Squadron Supply',
 'Провести карибский конвой','Run a Caribbean Convoy',
 'Капитаны требуют уголь, а городские делегаты — продовольствие. Приоритет флоту сохранит боевую готовность ценой доверия гавани.',
 'Captains demand coal while city delegates demand food. Prioritising the fleet will cost the harbour\'s confidence.',
 'Карибская морская республика','A Caribbean Maritime Republic','caribbean')
profile('PCF','Рыцари Конфедерации','Confederate Knights',1082,'relief','A05 PAZ','A05',
 'Плантационные семьи удерживают центральную Кубу, но зависимые работники и бедные поселенцы требуют земли и оплаты. Старые сословия можно сохранить или заменить договором свободных хозяйств.',
 'Plantation families control central Cuba while dependent workers and poor settlers demand land and wages. Preserve estates or negotiate a compact of free farms.',
 'Договор свободных хозяйств','A Compact of Free Farms','Совет плантационных домов','Council of Plantation Houses',
 'Урожайные ведомости|Сельские кооперативы|Оплачиваемая переработка тростника','Harvest Ledgers|Rural Cooperatives|Paid Cane Processing',
 'Окружная милиция|Дороги Санта-Клары|Арсенал центральной Кубы','District Militia|Santa Clara Roads|Central Cuban Arsenal',
 'Доставить урожай в общины','Deliver the Harvest to Communities',
 'Работники остановили вывоз урожая. Переговоры требуют средств, а принудительный порядок усилит зависимость кабинета от вооружённых владельцев.',
 'Workers have halted harvest shipments. Negotiations cost resources; coercion deepens reliance on armed estate owners.',
 'Устойчивое хозяйство центральной Кубы','A Sustainable Central Cuban Economy','mandate')
profile('PAZ','Ацтекское Возрождение','Aztec Revival',1083,'survey','PCF PHR','A05',
 'Мексиканские изгнанники расселились между Сьерра-Маэстрой и Санто-Доминго. Генералы хотят снабжать поселения, а Пророк Пятого Солнца — подчинить их единому священному закону.',
 'Mexican exiles are scattered between the Sierra Maestra and Santo Domingo. Officers favour settlement supply while the Prophet seeks a single sacred law.',
 'Съезд мексиканских поселений','Congress of Mexican Settlements','Закон Пятого Солнца','Law of the Fifth Sun',
 'Землемеры Сьерра-Маэстры|Мастерские переселенцев|Межостровные ведомости','Sierra Maestra Surveyors|Settler Workshops|Inter-Island Ledgers',
 'Горные ополчения|Перевалы и прибрежные склады|Военные мастерские изгнанников','Mountain Militias|Passes and Coastal Depots|Exiles\' Military Workshops',
 'Обследовать пути между поселениями','Survey Settlement Routes',
 'Священные смотрители спорят с землемерами о распределении припасов. От этого решения зависит доверие разобщённых поселений.',
 'Sacred overseers dispute supplies with surveyors. The settlement determines the scattered communities\' trust.',
 'Связать два берега изгнания','Connect the Two Shores of Exile','two_shores')
profile('PHR','Дети Урагана','Children of the Hurricane',318,'relief','PAZ PSL','A05',
 'Общины Гаити объединяет сопротивление внешнему господству. Но ополчение, лечебницы и сельские советы спорят о том, кому распоряжаться скудными припасами.',
 'Resistance to foreign domination unites Haiti\'s communities, but militias, clinics and village councils dispute scarce supplies.',
 'Собрание гаитянских общин','Assembly of Haitian Communities','Союз боевых братств','League of Fighting Brotherhoods',
 'Общие рисовые склады|Мастерские Порт-о-Пренса|Сельские лечебницы','Common Rice Stores|Port-au-Prince Workshops|Village Clinics',
 'Ополчения лесных троп|Наблюдатели у побережья|Ремонт трофейного оружия','Forest-Trail Militias|Coastal Watchers|Captured Arms Repair',
 'Провести продовольственный обоз','Run a Food Convoy',
 'Боевая дружина забрала рис у соседней общины. Возмещение укрепит союз, а отказ усилит военных и недоверие деревень.',
 'A war band seized a neighbouring village\'s rice. Restitution strengthens the compact; refusal empowers commanders and distrust.',
 'Сохранить свободные общины Гаити','Preserve Haiti\'s Free Communities','mandate')
profile('PHW','Гавайский рубеж','Hawaiian Frontier',629,'convoy','A07 A02','A03',
 'Королевство живёт перевалкой грузов и страхом перед большим флотом. Сохранённая корона или морское правительство должны подготовить острова к грядущей смене власти.',
 'Shipping sustains the kingdom under the shadow of larger fleets. A preserved Crown or naval government must prepare for the approaching succession.',
 'Конституционная гавайская корона','A Constitutional Hawaiian Crown','Правительство морского рубежа','Government of the Maritime Frontier',
 'Гонолульские грузовые ведомости|Островные ремонтные мастерские|Запасные рейсы через Тихий океан','Honolulu Cargo Ledgers|Island Repair Workshops|Reserve Pacific Voyages',
 'Островная территориальная стража|Охрана гавайских гаваней|Доковая служба Гонолулу','Island Territorial Guard|Protect Hawaiian Harbours|Honolulu Dock Service',
 'Провести тихоокеанский торговый рейс','Run a Pacific Trading Voyage',
 'Судовладельцы требуют подчинить островные сборы эскадре. Двор и муниципалитеты настаивают на гражданской смете.',
 'Shipowners demand that the squadron control island levies. The Court and municipalities insist on civilian estimates.',
 'Гавайи после смены власти','Hawaii After the Succession','hawaii')
profile('MLT','Мальта','Malta',116,'science','A02 A06','',
 'Мальта принимает изгнанные дворы и лабораторию Теслы, оставаясь отдельным государством. Местный совет должен извлекать пользу из посредничества, не отдавая остров покровителю.',
 'Malta hosts exiled courts and Tesla\'s laboratory as a separate state. Its council must benefit from mediation without surrendering the island.',
 'Гражданская хартия Валлетты','Valletta Civic Charter','Совет дворов в изгнании','Council of Exiled Courts',
 'Портовые ведомости Валлетты|Мастерские Святого Ангела|Приборная школа Мальты','Valletta Harbour Ledgers|Saint Angelo Workshops|Malta Instrument School',
 'Мальтийская береговая стража|Нейтральные причалы Валлетты|Арсенал островной обороны','Maltese Coast Guard|Valletta\'s Neutral Quays|Island Defence Arsenal',
 'Провести приборную исследовательскую сессию','Run an Instrument Research Session',
 'Дворы требуют закрыть научную переписку, а инженеры — сохранить связи с иностранными лабораториями. Тесла не становится собственностью ни одной делегации.',
 'The courts demand closed correspondence while engineers seek foreign contacts. Tesla does not become any delegation\'s property.',
 'Независимый остров переговоров','An Independent Island of Negotiation','science')
profile('PSL','Султанат Сулу','Sultanate of Sulu',1025,'customs','A10 PHR','A03',
 'Султану нужны пошлины и верные гавани, а дато хотят сохранять собственные суда и вооружённых людей. Выбор договора или морской мобилизации определит судьбу султаната.',
 'The Sultan needs customs income and loyal harbours while the datu defend their own ships and armed followers. Choose a negotiated compact or maritime mobilisation.',
 'Договор султана и дато','A Compact of Sultan and Datu','Морской сбор под знамёнами султана','The Sultan\'s Maritime Muster',
 'Таможенные книги Холо|Мастерские местных верфей|Пошлины вместо случайной дани','Jolo Customs Books|Local Yard Workshops|Customs Instead of Arbitrary Tribute',
 'Береговые дружины дато|Посты в проливах Сулу|Оружейники султанской гавани','Datu Coastal Companies|Sulu Strait Posts|The Sultan\'s Harbour Armourers',
 'Провести таможенный сезон','Complete a Customs Season',
 'Один из дато удержал пошлины и требует признать его права. Договор ограничит произвол, а силовой ответ потребует расходов на верные дружины.',
 'A datu withheld customs dues and demands recognised rights. A compact limits arbitrary rule; coercion costs loyal troops and supplies.',
 'Султанат, способный держать проливы','A Sultanate Able to Hold the Straits','stock')
profile('PSY','Султанат Сейшелы','Seychelles Sultanate',709,'convoy','A02 MLT','',
 'Двор в изгнании зависит от маленькой гавани Маэ и беженцев. Корона может заключить договор с островными общинами или управлять через закрытый придворный совет.',
 'An exiled court depends on Mahe\'s small harbour and refugees. Negotiate with island communities or govern through a closed royal council.',
 'Хартия общин Маэ','Charter of Mahe Communities','Двор султана в изгнании','The Sultan\'s Exiled Court',
 'Книги Викторийской гавани|Островные мастерские|Служба воды и снабжения','Victoria Harbour Books|Island Workshops|Water and Supply Service',
 'Стража убежища|Прибрежные сигнальные посты|Ремонт гарнизонного оружия','Refuge Guard|Coastal Signal Posts|Garrison Arms Repair',
 'Доставить грузы на Маэ','Deliver Supplies to Mahe',
 'Новый транспорт с беженцами пришёл в гавань без продовольственного запаса. Придворные и островные старейшины спорят о цене гостеприимства.',
 'A refugee transport reached the harbour without food reserves. Courtiers and elders dispute the cost of shelter.',
 'Островное королевство убежища','An Island Kingdom of Refuge','trade')
profile('A08','Северная армия','Northern Army',536,'defence','A03 A09','A03',
 'Хакодатское перемирие сохранило армию Сайго, но не решило вопроса о будущем Хоккайдо. Поселенческий договор и мобилизационная армия предлагают разные отношения с Токио.',
 'The Hakodate armistice preserved Saigo\'s army without settling Hokkaido\'s future. A settlement compact and permanent mobilisation offer different relations with Tokyo.',
 'Северный поселенческий договор','Northern Settler Compact','Мобилизационный приказ Сайго','Saigo\'s Mobilisation Order',
 'Склады Хакодате|Мастерские северных поселений|Паёк между гарнизоном и деревней','Hakodate Depots|Northern Settlement Workshops|Share Rations with the Villages',
 'Северные стрелковые части|Зимние линии снабжения|Хоккайдский арсенал','Northern Rifle Units|Winter Supply Lines|Hokkaido Arsenal',
 'Провести зимние гарнизонные учения','Complete Winter Garrison Exercises',
 'Офицеры требуют очередного набора, пока поселенцы не собрали урожай. Соглашение сохранит доверие деревень, но отложит усиление армии.',
 'Officers demand recruits before the harvest. A compact preserves village confidence but delays army expansion.',
 'Север, способный выбирать свою судьбу','A North Able to Choose Its Future','north')
profile('A09','Осака','Osaka',531,'finance','A03 A04','',
 'Торговые дома удерживают Осаку между государственными заказами и долгами. Поддержка Токио может спасти текущий сезон, но лишить купцов свободы решений.',
 'Osaka\'s houses balance state orders against debt. Tokyo\'s contracts may save the season while costing commercial independence.',
 'Союз самостоятельных торговых домов','League of Independent Houses','Казённые заказы для Осаки','State Orders for Osaka',
 'Сверить осакские обязательства|Мастерские торговых домов|Расчёты без двойного залога','Audit Osaka Liabilities|Trading-House Workshops|Accounts Without Double Collateral',
 'Охрана купеческих складов|Пристанская таможенная стража|Оружейные заказы для охраны','Protect Merchant Depots|Harbour Customs Guard|Arms Orders for the Guard',
 'Провести расчётный сезон','Complete a Settlement Season',
 'Кредиторы требуют нового залога, а государственный заказчик — скидки. Кабинету предстоит выбрать, кому уступить в текущем сезоне.',
 'Creditors demand more collateral while the state customer demands discounts. The cabinet must decide whom to accommodate.',
 'Платёжеспособная Золотая середина','A Solvent Golden Mean','debt')

def released(tag,ru,en,cap,kind,partners,opening,opening_en,civic,civic_en,command,command_en,econ,econ_en,defence,defence_en,project,project_en,goal,goal_en):
    profile(tag,ru,en,cap,kind,partners,'A03' if tag.startswith('P') else '',opening,opening_en,civic,civic_en,command,command_en,econ,econ_en,defence,defence_en,project,project_en,
      'Местный совет требует отчёта о припасах и правах общин. Договор с делегатами укрепит доверие, а чрезвычайный порядок передаст больше власти гарнизону.',
      'The local council demands accounts of supplies and community rights. A compact strengthens trust; emergency rule empowers the garrison.',goal,goal_en,'charter')

released('A11','Кутай','Kutai',1055,'customs','A01 A04','Речные пристани Махаками должны кормить двор и платить по действующим обязательствам. Местная хартия не отменяет чужие ресурсные права.','Mahakam river landings must support the court and honour existing obligations; a charter does not erase foreign resource rights.',
 'Договор речных общин','River Community Compact','Султанская речная стража','Sultan\'s River Guard','Книги пристаней Махаками|Мастерские Кутая|Проверенные права на ренту','Mahakam Landing Books|Kutai Workshops|Audited Rent Rights','Речные дружины|Стража переправ|Кутайские оружейники','River Companies|Crossing Guards|Kutai Armourers','Провести речной таможенный сезон','Run a River Customs Season','Хартия речного султаната','A Charter for the River Sultanate')
released('A12','Понтианак','Pontianak',334,'convoy','A01 A04','Гавань на Капуасе зависит от устойчивой торговли и переговоров с покровителем. Военная охрана должна защищать порт, а не разорять его поборами.','The Kapuas harbour needs regular trade and negotiations with its patron; guards must protect commerce rather than live on arbitrary levies.',
 'Купеческо-султанский договор','Merchant-Sultan Compact','Пристанская власть дворца','Palace Harbour Authority','Пошлины Капуаса|Понтианакские мастерские|Распорядок торговой гавани','Kapuas Customs|Pontianak Workshops|Commercial Harbour Rules','Городская стража Понтианака|Посты у речного устья|Портовый оружейный двор','Pontianak Town Guard|River-Mouth Posts|Harbour Armoury','Доставить грузы через устье Капуаса','Deliver Cargo Through the Kapuas Mouth','Гавань с признанными правилами','A Harbour with Recognised Rules')
released('A13','Банджар','Banjar',1022,'defence','A01 A11','Разрозненные речные поселения требуют защиты от произвольных сборов. Гарнизон хочет единого командования, а старейшины — права голоса.','Scattered river settlements seek protection from arbitrary dues; garrisons want unified command and elders representation.',
 'Совет речных старейшин','River Elders Council','Банджарский оборонный сбор','Banjar Defence Muster','Перепись речных хозяйств|Мастерские Банджармасина|Общий речной склад','River Farm Census|Banjarmasin Workshops|Common River Depot','Стража речных троп|Посты заболоченных переходов|Банджарские ремонтные команды','River-Trail Guard|Marsh-Crossing Posts|Banjar Repair Teams','Подготовить стражу речных переходов','Train the River-Crossing Guard','Защищённые речные общины','Protected River Communities')
released('A14','Ачех','Aceh',1050,'defence','A01 PSL','Ачехские старейшины и улемы хотят сохранить местный закон. Условия покровительства можно уточнять переговорами, а силовое отделение не возникает от одного фокуса.','Acehnese elders and scholars seek to preserve local law; patronage is negotiated and no focus instantly causes secession.',
 'Соглашение старейшин и улемов','Compact of Elders and Scholars','Ачехский военный совет','Acehnese Military Council','Книги северосуматранских портов|Ачехские мастерские|Снабжение горных общин','Northern Sumatran Port Books|Acehnese Workshops|Mountain Community Supply','Добровольцы местных общин|Горные наблюдательные посты|Ачехская оружейная служба','Community Volunteers|Mountain Watch Posts|Acehnese Arms Service','Провести учения горных дружин','Drill the Mountain Companies','Ачехская местная хартия','An Acehnese Local Charter')
released('PCB','Республика Себу','Cebu Republic',628,'customs','A10 PSL','Себуанские торговые дома контролируют склады, но рабочие гавани требуют представительства. Общие связи с конфедерацией должны приносить пользу городу.','Cebu houses control the depots while dockworkers demand representation; confederal ties must benefit the city.',
 'Муниципальная торговая хартия','Municipal Trade Charter','Совет крупнейших торговых домов','Council of the Largest Houses','Себуанские торговые книги|Гаванские мастерские Себу|Портовые расчётные правила','Cebu Trade Books|Cebu Harbour Workshops|Port Settlement Rules','Муниципальная портовая стража|Сигналы пролива Себу|Арсенал торговой республики','Municipal Harbour Guard|Cebu Strait Signals|Trading Republic Arsenal','Завершить себуанский портовый сезон','Complete a Cebu Port Season','Республика работающих гаваней','A Republic of Working Harbours')
released('PPN','Конфедерация Панай','Panay Confederation',1085,'relief','A10 PCB','Касики Панай согласуют рисовые поставки между общинами. Земельный договор может дать им доверие крестьян или закрепить власть старых семейств.','Panay\'s chiefs coordinate rice supplies; a land compact may earn farmers\' trust or entrench the old families.',
 'Союз крестьянских общин','League of Farming Communities','Старший совет касиков','Senior Council of Chiefs','Рисовые амбары Илоило|Общинные мастерские Панай|Согласованные земельные ведомости','Iloilo Rice Granaries|Panay Community Workshops|Agreed Land Ledgers','Общинная островная стража|Наблюдатели рисовых дорог|Ремонт оружия для Панай','Community Island Guard|Rice-Road Watchers|Panay Arms Repair','Доставить рис между общинами','Deliver Rice Between Communities','Панай без голодных деревень','Panay Without Hungry Villages')
released('PVI','Висайская республика','Visayan Republic',624,'convoy','A10 PCB','Разные островные советы требуют равного доступа к паромам и общему бюджету. Централизация охраны не должна лишить малые гавани права голоса.','Island councils seek equal ferry access and budget representation; centralised guards must not silence small harbours.',
 'Съезд висайских городов','Congress of Visayan Towns','Единая островная комендатура','Unified Island Command','Паромные ведомости Висайев|Висайские мастерские|Общий график межостровных рейсов','Visayan Ferry Ledgers|Visayan Workshops|Common Inter-Island Timetables','Стража паромных линий|Наблюдательные посты Висайев|Ремонтное управление республики','Ferry-Line Guard|Visayan Watch Posts|Republic Repair Administration','Провести межостровной паромный сезон','Run an Inter-Island Ferry Season','Связанные гаванями Висайи','Harbours Connecting the Visayas')
released('PSM','Республика Самар','Samar Republic',625,'repair','A10 PVI','Самар нуждается в надёжных лодках и защите лесных дорог. Шторм способен отрезать гарнизоны раньше, чем придёт неприятель.','Samar needs reliable boats and forest roads; storms may isolate its garrisons before an enemy arrives.',
 'Советы лесных и прибрежных общин','Forest and Coastal Councils','Самарское береговое командование','Samar Coastal Command','Ведомости штормовых повреждений|Самарские лодочные мастерские|Запасные склады Самар','Storm Damage Ledgers|Samar Boat Workshops|Samar Reserve Depots','Лесная территориальная стража|Смотровые посты Самар|Ремонт гарнизонных винтовок','Forest Territorial Guard|Samar Lookout Posts|Garrison Rifle Repair','Восстановить самарские пути снабжения','Restore Samar Supply Routes','Остров, переживший штормовой сезон','An Island Surviving the Storm Season')
released('PMD','Республика Минданао','Mindanao Republic',627,'relief','A10 PSL','Муниципалитеты и сельские общины ищут общий порядок снабжения. Религиозные и местные различия делают договор важнее приказа из столицы.','Towns and villages seek common supply arrangements; religious and local differences make agreement essential.',
 'Межобщинный договор Минданао','Mindanao Intercommunity Compact','Южное территориальное командование','Southern Territorial Command','Книги сельских поставок|Муниципальные мастерские Минданао|Общие лечебницы и амбары','Rural Supply Books|Mindanao Municipal Workshops|Shared Clinics and Granaries','Стража общинных дорог|Береговые дозоры Минданао|Ремонтные мастерские гарнизона','Community Road Guard|Mindanao Coastal Patrols|Garrison Repair Workshops','Доставить помощь отдалённым общинам','Deliver Aid to Remote Communities','Минданао по общему договору','Mindanao Under a Shared Compact')
released('PNM','Северный Минданао','Northern Mindanao',1026,'survey','A10 PMD','Северные гавани и внутренние поселения плохо связаны. Землемеры и охрана дорог могут превратить формальное правительство в работающий союз.','Northern harbours and inland settlements lack connections; surveyors and road guards can make the government effective.',
 'Совет северных поселений','Council of Northern Settlements','Североминданайская комендатура','Northern Mindanao Command','Карты внутренних дорог|Мастерские северных гаваней|Обследование складских маршрутов','Inland Road Maps|Northern Harbour Workshops|Depot Route Surveys','Дорожные территориальные части|Наблюдатели перевалов|Северные оружейные мастерские','Road Territorial Units|Pass Watchers|Northern Arms Workshops','Обследовать маршрут к внутренним поселениям','Survey the Inland Settlement Route','Соединить северные гавани с глубинкой','Connect Northern Harbours to the Interior')
released('PNL','Северный Лусон','Northern Luzon',623,'defence','A10 PBT','После освобождения горные муниципалитеты должны восстановить хозяйство и подготовить оборону. Республика не обязана возвращаться к прежней теократической форме.','After liberation, mountain municipalities must rebuild and defend themselves without automatically restoring the former theocratic state.',
 'Союз горных муниципалитетов','League of Mountain Municipalities','Лусонский оборонный комитет','Luzon Defence Committee','Перепись освобождённых хозяйств|Горные мастерские Лусона|Продовольственные пути к побережью','Liberated Farm Census|Luzon Mountain Workshops|Food Routes to the Coast','Горные стрелковые дружины|Посты лусонских перевалов|Арсенал освобождённого Севера','Mountain Rifle Companies|Luzon Pass Posts|Liberated North Arsenal','Подготовить оборону горных дорог','Prepare Mountain Road Defences','Северный Лусон после освобождения','Northern Luzon After Liberation')
released('PML','Республика Манила','Manila Republic',327,'repair','A10 PCB','Освобождённая Манила должна восстановить склады и вернуть доверие жителей. Торговые дома и муниципальные делегаты спорят о порядке реконструкции.','Liberated Manila must restore depots and public trust while merchant houses and municipal delegates dispute reconstruction.',
 'Выборная городская дума','An Elected City Council','Портовая чрезвычайная администрация','Emergency Port Administration','Перепись разрушенных складов|Манильские восстановительные мастерские|Прозрачные сметы реконструкции','Damaged Depot Census|Manila Reconstruction Workshops|Public Reconstruction Estimates','Городская стража освобождения|Охрана манильских причалов|Манильский ремонтный арсенал','Liberation City Guard|Protect Manila Quays|Manila Repair Arsenal','Восстановить манильский портовый квартал','Restore Manila\'s Harbour Quarter','Манила, вернувшаяся к мирной работе','Manila Returned to Civilian Work')
released('PBT','Республика Батаан','Bataan Republic',1027,'defence','A10 PNL','Батаан прикрывает подходы к Маниле, но его жители не хотят жить одним гарнизоном. Оборону полуострова нужно совместить с местным хозяйством.','Bataan guards Manila\'s approaches, but its residents need more than a garrison; defence must coexist with local livelihoods.',
 'Хартия муниципалитетов Батаана','Bataan Municipal Charter','Командование полуостровной обороны','Peninsula Defence Command','Сметы полуостровных хозяйств|Батаанские мастерские|Резерв продовольствия полуострова','Peninsula Farm Estimates|Bataan Workshops|Peninsula Food Reserve','Батаанские территориальные части|Наблюдатели манильских подходов|Арсенал полуострова','Bataan Territorial Units|Manila Approach Watchers|Peninsula Arsenal','Провести полуостровные оборонные учения','Drill the Peninsula Defence Force','Батаан с собственной хартией','Bataan with Its Own Charter')
