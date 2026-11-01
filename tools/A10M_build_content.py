"""Rebuild the isolated Philippine military focus payload and bilingual localisation."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
focuses = []
loc = {"russian": {}, "english": {}}

def text(key, ru, en):
    loc["russian"][key] = ru
    loc["english"][key] = en

def focus(key, ru, en, dru, den, x, y, parents, reward, icon="neutrality_focus", mx=(), available="has_country_flag = A10M_active", ai=2, cost=5):
    fid = "A10M_" + key
    focuses.append(dict(id=fid, name_ru=ru, desc_ru=dru, name_en=en, desc_en=den,
                        icon="GFX_goal_generic_" + icon, x=x, y=y, cost=cost,
                        prerequisites=[[p] for p in parents], mutually_exclusive=list(mx),
                        available=available, reward=reward, ai=ai))
    text(fid, ru, en)
    text(fid + "_desc", dru, den)

focus("coup", "Ночь запертых дверей", "The Night of Locked Doors",
      "Караулы перекроют подходы к островному конгрессу. Полковник Матео Сандоваль объявит, что свобода республик стала прикрытием бессилия, и передаст власть чрезвычайному военному командованию. Делегатов отпустят лишь после присяги.",
      "Guards will seal the approaches to the island congress. Colonel Mateo Sandoval will declare the republics' freedom a cover for impotence and place power in an emergency military command. Delegates will leave only after taking its oath.",
      58, 3, ["A10_island_congress"], "A10M_begin_coup = yes", "military_sphere",
      ["A10_confederation", "A10W_oath"], "is_subject = no", ai=1)
focus("martial_law", "Приказ о чрезвычайном положении", "The Emergency Proclamation",
      "Военные коменданты получат контроль над портами, телеграфом и ночным движением. За каждым обещанием порядка останется семья, которой придётся просить разрешение на обычную жизнь.",
      "Military commandants will control ports, telegraphs and movement after dark. Behind every promise of order stands a family forced to request permission for ordinary life.",
      58, 4, ["A10M_coup"], "add_political_power = 50 add_to_variable = { var = A10M_repression value = 10 } add_to_variable = { var = A10M_opposition value = 5 } A10M_update = yes", "major_war")
focus("recall_charters", "Отозвать островные хартии", "Revoke the Island Charters",
      "Коменданты заменят советы там, где власть конгресса ещё признаётся. Подчинённые нам республики вернут войска и учреждения общему командованию; за чужими границами одного приказа недостаточно.",
      "Commandants will replace councils wherever the congress is still obeyed. Republics subordinate to us will return troops and institutions to the common command; an order alone cannot cross foreign frontiers.",
      54, 5, ["A10M_martial_law"], "A10M_recall_members = yes", "national_unity")
focus("censor_cables", "Тишина на проводах", "Silence on the Wires",
      "Частные кабельные сообщения будут проходить через цензора. Режим сможет скрывать передвижения гарнизонов, но вместе с опасными слухами исчезнут сведения, без которых купцы и учёные работают вслепую.",
      "Private cable messages will pass through a censor. The regime can conceal garrison movements, but useful reports will disappear beside dangerous rumours, leaving merchants and scholars to work blind.",
      62, 5, ["A10M_martial_law"], "add_ideas = A10M_censored_society add_to_variable = { var = A10M_repression value = 5 } A10M_update = yes", "propaganda")
focus("officer_tribunal", "Трибунал над старым штабом", "Tribunal of the Old Staff",
      "Офицеры, вчера охранявшие конгресс, сегодня должны ответить за его слабость. Процесс определит, станет ли армия орудием личной верности Сандовалю или сохранит место для профессионального возражения.",
      "Officers who guarded the congress yesterday must answer for its weakness today. Their trial will decide whether the army becomes an instrument of personal loyalty to Sandoval or retains room for professional dissent.",
      58, 6, ["A10M_recall_charters", "A10M_censor_cables"], "set_country_flag = A10R_war_ready army_experience = 15 country_event = { id = A10M.2 days = 1 }", "army_doctrines")
focus("rice_commissions", "Рисовые комиссии", "Rice Commissions",
      "Без риса не удержать ни гарнизон, ни портовый квартал. Комиссии перепишут запасы и семейные наделы, чтобы штаб впервые увидел цену своих заявок на снабжение.",
      "Neither a garrison nor a dockside district can be held without rice. Commissions will register stocks and household plots so that headquarters can finally see the cost of its supply demands.",
      50, 6, ["A10M_recall_charters"], "subtract_from_variable = { var = A10M_strain value = 10 } add_political_power = 25 A10M_update = yes", "construction")
focus("requisition", "Складские книги командования", "The Command's Warehouse Ledgers",
      "Поставки объединят в обязательные квоты. Арсеналы получат более ровный поток сырья, а сельские пристани — наряды, которым всё труднее соответствовать.",
      "Deliveries will be combined into compulsory quotas. Arsenals will receive a steadier flow of material while rural landings receive demands that grow harder to fulfil.",
      54, 7, ["A10M_rice_commissions"], "add_ideas = A10M_requisition_bureaus custom_effect_tooltip = A10M_requisition_tt", "construct_mil_factory")
focus("compensation", "Расписки вместо конфискаций", "Receipts Instead of Confiscations",
      "Военные квитанции должны стать обязательством казны. Выплаты обременят бюджет, зато поставщики смогут снова закупать зерно и не прятать лодки при виде мундира.",
      "Military receipts must become obligations of the treasury. Payments will burden the budget, but suppliers will be able to buy grain again instead of hiding their boats at the sight of a uniform.",
      50, 8, ["A10M_requisition"], "add_ideas = A10M_compensation_bonds subtract_from_variable = { var = A10M_opposition value = 8 } custom_effect_tooltip = A10M_compensation_tt A10M_update = yes", "construction", ["A10M_labour_battalions"])
focus("labour_battalions", "Трудовые батальоны", "Labour Battalions",
      "Радикалы требуют поставить людей на строительство казарм и мастерских по приказу. Работы ускорятся, но семьи лишатся работников, а за проволокой возникнет новая, более непримиримая оппозиция.",
      "Radicals demand that men be ordered into barracks and workshop construction. Work will accelerate, but families will lose their workers and a more implacable opposition will form behind the wire.",
      54, 8, ["A10M_requisition"], "add_ideas = A10M_compulsory_labour add_to_variable = { var = A10M_repression value = 10 } add_to_variable = { var = A10M_opposition value = 10 } custom_effect_tooltip = A10M_labour_tt A10M_update = yes", "construct_mil_factory", ["A10M_compensation"], ai=1)
focus("cadet_schools", "Школы военного сословия", "Schools of the Military Estate",
      "Коменданты отберут способных юношей для ускоренных офицерских курсов. Образование откроет дорогу тем, кого не принимали старые семейные связи, и одновременно привяжет их будущее к режиму.",
      "Commandants will select able youths for accelerated officer courses. Education will open doors once closed by family connections while binding their future to the regime.",
      62, 6, ["A10M_censor_cables"], "add_ideas = A10M_cadet_estate army_experience = 10", "special_forces")
focus("levy_rolls", "Единые призывные списки", "Unified Levy Rolls",
      "Разрозненные островные списки сведут воедино. Штаб получит резерв, но мастерские начнут терять опытные руки; командиры обязаны учитывать, кто ещё способен кормить призванных.",
      "Scattered island registers will be brought together. Headquarters will gain a reserve, but workshops will begin losing skilled hands; commanders must account for who can still feed the conscripts.",
      66, 7, ["A10M_cadet_schools"], "add_ideas = A10M_military_levies add_manpower = 3500 add_to_variable = { var = A10M_strain value = 7 } add_to_variable = { var = A10M_opposition value = 5 } A10M_update = yes", "small_arms")
focus("medical_corps", "Санитарные команды гарнизонов", "Garrison Medical Teams",
      "Полевые лазареты должны остановить потери, которые не видны на карте боёв. На санитарные лодки и лекарства придётся выделить место в каждом снабженческом рейсе.",
      "Field infirmaries must stop losses invisible on battle maps. Medical boats and supplies will need space on every supply voyage.",
      66, 8, ["A10M_levy_rolls"], "add_ideas = A10M_field_hospitals subtract_from_variable = { var = A10M_strain value = 8 } custom_effect_tooltip = A10M_hospitals_tt A10M_update = yes", "special_forces")
focus("quartermasters", "Инспекция интендантов", "Quartermaster Inspectorate",
      "Складской отчёт не должен зависеть от настроения коменданта. Инспекторы проверят потери и распределение лодок, лишив местных начальников части привычного дохода.",
      "Warehouse reports must no longer depend on a commandant's mood. Inspectors will examine losses and boat allocation, depriving local commanders of part of their customary income.",
      58, 9, ["A10M_officer_tribunal", "A10M_requisition", "A10M_medical_corps"], "add_ideas = A10M_supply_inspectorate subtract_from_variable = { var = A10M_strain value = 10 } custom_effect_tooltip = A10M_inspectorate_tt A10M_update = yes", "army_doctrines")
focus("junta", "Власть вечного караула", "Rule of the Perpetual Guard",
      "Радикальные полковники отвергают обещание временной власти. По их уставу мирная жизнь станет продолжением военной службы, а само чрезвычайное положение — основой государства.",
      "Radical colonels reject the promise of temporary rule. Under their charter, civilian life will become an extension of military service and the emergency itself the foundation of the state.",
      54, 10, ["A10M_quartermasters"], "A10M_junta_effect = yes", "military_sphere", ["A10M_directorate"], ai=2)
focus("directorate", "Директорат военных служб", "Directorate of the Services",
      "Начальники служб предлагают управлять коллегией и письменным приказом. Конгресс они не вернут, но снабжение, флот и сухопутные части получат собственный голос за закрытой дверью.",
      "Service chiefs propose rule by a board and written orders. They will not restore the congress, but supply, fleet and land forces will each have a voice behind the closed door.",
      64, 10, ["A10M_quartermasters"], "A10M_directorate_effect = yes", "neutrality_focus", ["A10M_junta"], ai=3)
focus("revolutionary_command", "Командование национального очищения", "Command of National Purification",
      "Новый штаб объявит всякое несогласие продолжением прежнего распада. Офицеры получат больше свободы наступать и меньше свободы обсуждать цену приказов.",
      "The new staff will call every dissent a continuation of the old disintegration. Officers will gain greater freedom to attack and less freedom to discuss the cost of orders.",
      54, 11, ["A10M_junta"], "army_experience = 20 add_to_variable = { var = A10M_repression value = 10 } add_war_support = 0.04 A10M_update = yes", "major_war")
focus("commissars", "Политические надзиратели", "Political Supervisors",
      "Рядом с каждым командиром появится уполномоченный хунты. Он поддержит части, утратившие решимость, и доложит обо всех, кто усомнится в её праве распоряжаться островами.",
      "An envoy of the junta will stand beside every commander. He will stiffen faltering units and report anyone who doubts its right to command the islands.",
      54, 12, ["A10M_revolutionary_command"], "add_ideas = A10M_political_commissars add_to_variable = { var = A10M_repression value = 5 } A10M_update = yes", "propaganda")
focus("islands_barracks", "Архипелаг казарм", "An Archipelago of Barracks",
      "Учебные сборы охватят новые возрастные группы. Каждая пристань будет знать своего военного начальника, каждое хозяйство — день, когда его работник обязан явиться к строю.",
      "Training assemblies will encompass new age groups. Every landing will know its military chief and every household the day its worker must report for duty.",
      54, 13, ["A10M_commissars"], "add_ideas = A10M_barracks_state add_manpower = 2500 add_to_variable = { var = A10M_strain value = 8 } add_to_variable = { var = A10M_opposition value = 5 } A10M_update = yes", "small_arms")
focus("red_seal", "Печать верховного коменданта", "Seal of the Supreme Commandant",
      "Постановление утвердит личную печать Сандоваля выше всех островных хартий. Командование отпразднует окончание переворота, хотя прекращение самой чрезвычайной власти никто уже не обещает.",
      "A decree will place Sandoval's personal seal above every island charter. The command will celebrate the end of the coup, though no one now promises an end to emergency rule itself.",
      54, 14, ["A10M_islands_barracks"], "add_political_power = 50 country_event = { id = A10M.5 days = 1 }", "national_unity")
focus("service_council", "Совет родов службы", "Council of the Services",
      "Моряки, интенданты и сухопутные командиры подпишут порядок разрешения споров. Личная ссора полковников больше не должна останавливать рисовую баржу или переброску гарнизона.",
      "Sailors, quartermasters and army commanders will sign rules for settling disputes. A personal quarrel between colonels must no longer delay a rice barge or a garrison transfer.",
      64, 11, ["A10M_directorate"], "add_command_power = 20 subtract_from_variable = { var = A10M_opposition value = 5 } A10M_update = yes", "army_doctrines")
focus("audited_budget", "Бюджет под подписью", "A Budget Under Signature",
      "Каждая служба представит расходы общему ревизору. Публиковать придётся хотя бы итоговые суммы: без доверия поставщиков власть останется с аккуратными приказами и пустыми складами.",
      "Each service will submit its expenses to a common auditor. At least the totals must be published: without supplier confidence, power will be left with tidy orders and empty warehouses.",
      64, 12, ["A10M_service_council"], "add_ideas = A10M_published_budget subtract_from_variable = { var = A10M_strain value = 8 } custom_effect_tooltip = A10M_budget_tt A10M_update = yes", "construction")
focus("professional_army", "Служба по военному уставу", "Service Under Military Regulations",
      "Профессиональные инструкторы заменят политические проверки проверкой подготовки. Обучение займёт больше времени, зато командир сможет положиться на умение солдата, а не на его подпись под лозунгом.",
      "Professional instructors will replace political examinations with tests of training. Instruction will take longer, but a commander can rely on a soldier's skill rather than his signature beneath a slogan.",
      64, 13, ["A10M_audited_budget"], "add_ideas = A10M_professional_service subtract_from_variable = { var = A10M_repression value = 5 } custom_effect_tooltip = A10M_professional_tt A10M_update = yes", "special_forces")
focus("fixed_term", "Сроки и полномочия комендантов", "Terms and Powers of Commandants",
      "Военная власть сохранит исключительное положение, но полномочия получат срок, а жалобы — путь в служебный суд. Это обещание не вернёт конгресс; оно хотя бы ограничит произвол отдельного гарнизона.",
      "Military rule will retain its exceptional position, but appointments will have terms and complaints a route to a service court. This promise will not restore the congress; it will at least limit a garrison's arbitrary rule.",
      64, 14, ["A10M_professional_army"], "subtract_from_variable = { var = A10M_repression value = 10 } subtract_from_variable = { var = A10M_opposition value = 10 } add_stability = 0.04 A10M_update = yes country_event = { id = A10M.5 days = 1 }", "neutrality_focus")
focus("coastal_observers", "Цепь береговых наблюдателей", "Chain of Coastal Observers",
      "Малые сигнальные посты свяжут гарнизоны с дозорными судами. Рыбацкие лодки получат порядок оповещения, а береговая служба — обязанность отличать угрозу от очередного мирного рейса.",
      "Small signal posts will link garrisons with patrol craft. Fishing boats will receive reporting instructions, and the coastal service a duty to distinguish threats from ordinary voyages.",
      58, 15, [], "add_ideas = A10M_coastal_watch navy_experience = 15", "navy_doctrines_tactics")
focuses[-1]["prerequisites"] = [["A10M_red_seal", "A10M_fixed_term"]]
focus("defence_plans", "Планы обороны проливов", "Plans for Strait Defence",
      "Штаб подготовит маршруты отхода, охрану складов и взаимодействие батарей с флотом. Приказ оборонять остров должен оставлять гарнизону путь к следующей позиции, а не только красивую последнюю телеграмму.",
      "The staff will prepare withdrawal routes, depot security and cooperation between batteries and fleet. An order to defend an island must leave a garrison a route to its next position, as well as a fine final telegram.",
      58, 16, ["A10M_coastal_observers"], "army_experience = 20 add_command_power = 15 add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 500 producer = A10 }", "defence")
focus("veteran_settlement", "Долг перед солдатскими семьями", "The Debt to Soldiers' Families",
      "Семьи убитых и искалеченных будут получать содержание по единому списку. Этот расход нельзя вычеркнуть красивой речью о победе: без него военная власть пожрёт собственную опору.",
      "Families of the dead and maimed will receive support from a common register. A fine victory speech cannot cancel this expense: without it, military rule will consume its own support.",
      55, 17, ["A10M_defence_plans"], "A10M_settlement_effect = yes", "national_unity")
focus("restore_markets", "Открыть рынки после караула", "Open the Markets After the Watch",
      "Пристани и мастерские должны вновь работать без ежедневного вмешательства коменданта. Трудовые батальоны будут распущены, а часть снабженческих полномочий вернётся гражданским распорядителям.",
      "Landings and workshops must function again without a commandant's daily intervention. Labour battalions will be disbanded and some supply powers returned to civilian administrators.",
      61, 17, ["A10M_defence_plans"], "A10M_recovery_effect = yes", "construction")
focus("iron_archipelago", "Железный архипелаг", "The Iron Archipelago",
      "Военный режим пережил первые бунты и научился считать цену собственных приказов. Он сохранит гарнизоны и закрытый конгресс, но его прочность теперь зависит от работающих складов и людей, способных дожить до следующего урожая.",
      "The military regime has weathered its first revolts and learned to count the cost of its orders. It will retain the garrisons and closed congress, but its strength now depends on functioning depots and people able to survive until the next harvest.",
      58, 19, ["A10M_veteran_settlement", "A10M_restore_markets"], "add_ideas = A10M_iron_state add_stability = 0.04 add_political_power = 75 set_country_flag = A10M_consolidated", "national_unity", available="has_country_flag = A10M_active A10M_crisis_contained = yes")

text("A10M_mateo_sandoval_name", "Матео Сандоваль", "Mateo Sandoval")
text("A10M_MILITARY", "Филиппинское военное государство", "Philippine Military State")
text("A10M_MILITARY_DEF", "Филиппинское военное государство", "the Philippine Military State")
text("A10M_MILITARY_ADJ", "Филиппинск.", "Philippine")
for ideology in ("neutrality", "democratic", "fascism", "communism"):
    text("A10M_MILITARY_" + ideology, "Филиппинское военное государство", "Philippine Military State")
    text("A10M_MILITARY_" + ideology + "_DEF", "Филиппинское военное государство", "the Philippine Military State")
    text("A10M_MILITARY_" + ideology + "_ADJ", "Филиппинск.", "Philippine")
text("A10M_opposition", "Оппозиция", "Opposition")
text("A10M_repression", "Репрессии", "Repression")
text("A10M_strain", "Истощение снабжения", "Supply Strain")
text("A10M_state_of_siege", "Государство под караулом", "The State Under Guard")
text("A10M_state_of_siege_desc",
     "Оппозиция: §Y[?A10M_opposition|0]/100§!\\nРепрессии: §Y[?A10M_repression|0]/100§!\\nИстощение снабжения: §Y[?A10M_strain|0]/100§!\\n\\nКаждый месяц оппозиция растёт на §R2§!. Война добавляет §R2§! истощения, мир уменьшает его на §G1§!. При репрессиях от §Y65§! ежемесячно добавляются ещё §R2§! оппозиции и §R2§! истощения. Вне постоянной хунты репрессии уменьшаются на §G1§! в месяц. Учреждения и обязательства изменяют этот итог.\\n\\nОппозиция от §Y65§! вызывает забастовки, истощение от §Y65§! — перебои снабжения. От §Y80§! возможны заговор и продовольственный кризис; каждый из них повторяется не чаще раза в 150 дней. Снижение показателей ниже 65 снимает соответствующие штрафы.",
     "Opposition: §Y[?A10M_opposition|0]/100§!\\nRepression: §Y[?A10M_repression|0]/100§!\\nSupply strain: §Y[?A10M_strain|0]/100§!\\n\\nOpposition rises by §R2§! each month. War adds §R2§! strain; peace removes §G1§!. Repression of §Y65§! or more adds another §R2§! opposition and §R2§! strain monthly. Outside the permanent junta, repression falls by §G1§! monthly. Institutions and obligations alter these totals.\\n\\nOpposition of §Y65§! causes strikes; strain of §Y65§! causes supply shortages. At §Y80§!, conspiracy and food crises can occur, each at most once every 150 days. Lowering a value below 65 removes its penalty.")

ideas = {
"martial_government": ("Чрезвычайное военное правительство", "Emergency Military Government", "Армия удерживает порты и учреждения, но её право управлять признают далеко не все островитяне.", "The army holds the ports and institutions, but many islanders reject its right to rule."),
"censored_society": ("Общество под цензурой", "Society Under Censorship", "Цензор пропускает победные сообщения и задерживает всё, что может смутить командование.", "The censor clears reports of victory and detains anything that may trouble the command."),
"requisition_bureaus": ("Реквизиционные бюро", "Requisition Bureaus", "Квоты поддерживают арсеналы за счёт сельских запасов. Ежемесячно: §R+2§! истощения снабжения.", "Quotas sustain the arsenals at the expense of rural stocks. Monthly: §R+2§! supply strain."),
"compensation_bonds": ("Казначейские расписки поставщикам", "Treasury Receipts for Suppliers", "Казна платит за изъятые запасы. Ежемесячно: §G−2§! истощения снабжения.", "The treasury pays for requisitioned stocks. Monthly: §G−2§! supply strain."),
"compulsory_labour": ("Принудительные трудовые батальоны", "Compulsory Labour Battalions", "Военные стройки забирают работников из семей и мастерских. Ежемесячно: §R+3§! оппозиции и §R+2§! истощения снабжения.", "Military construction takes workers from families and workshops. Monthly: §R+3§! opposition and §R+2§! supply strain."),
"cadet_estate": ("Кадетское сословие", "The Cadet Estate", "Новые офицеры обязаны своим положением военному государству.", "The new officers owe their standing to the military state."),
"military_levies": ("Военные призывные списки", "Military Levy Rolls", "Общие списки расширяют резерв и отвлекают работников от производства.", "Common registers expand the reserve and draw workers away from production."),
"field_hospitals": ("Гарнизонные лазареты", "Garrison Infirmaries", "Медики и санитарные лодки получают постоянное снабжение. Ежемесячно: §G−1§! истощения снабжения.", "Medical staff and ambulance boats receive regular supplies. Monthly: §G−1§! supply strain."),
"supply_inspectorate": ("Интендантская инспекция", "Quartermaster Inspectorate", "Потери на складах больше не исчезают из отчётов. Ежемесячно: §G−1§! истощения снабжения.", "Warehouse losses can no longer vanish from reports. Monthly: §G−1§! supply strain."),
"permanent_junta": ("Постоянная радикальная хунта", "Permanent Radical Junta", "Чрезвычайное положение признано вечным основанием власти. Репрессии больше не уменьшаются сами по себе.", "The emergency has been declared the permanent foundation of power. Repression no longer declines on its own."),
"political_commissars": ("Надзиратели при командирах", "Supervisors Beside Commanders", "Политический надзор поддерживает решимость и связывает инициативу.", "Political supervision stiffens resolve and constrains initiative."),
"barracks_state": ("Казарменное государство", "The Barracks State", "Новые возрастные группы готовятся к строю, пока гражданские стройки ждут работников.", "New age groups prepare for the ranks while civilian construction waits for workers."),
"military_directorate": ("Военный директорат", "Military Directorate", "Начальники служб делят полномочия, сохраняя власть армии над закрытым конгрессом.", "The service chiefs divide powers while preserving army rule over a closed congress."),
"professional_service": ("Профессиональная служба", "Professional Service", "Устав требует подготовки и запрещает месть под видом проверки верности. Ежемесячно: §G−1§! оппозиции.", "Regulations demand training and prohibit vengeance disguised as loyalty checks. Monthly: §G−1§! opposition."),
"published_budget": ("Опубликованные военные расходы", "Published Military Expenditure", "Проверяемая смета возвращает доверие поставщиков. Ежемесячно: §G−1§! истощения снабжения.", "An auditable estimate restores supplier confidence. Monthly: §G−1§! supply strain."),
"veterans_obligations": ("Обязательства перед семьями солдат", "Obligations to Soldiers' Families", "Содержание семей становится постоянной статьёй бюджета. Ежемесячно: §G−1§! оппозиции и §G−2§! истощения снабжения.", "Family support becomes a standing budget obligation. Monthly: §G−1§! opposition and §G−2§! supply strain."),
"civil_recovery": ("Гражданское восстановление", "Civilian Recovery", "Рынки вновь кормят острова, а мастерские получают работников. Ежемесячно: §G−1§! оппозиции и §G−1§! истощения снабжения.", "Markets feed the islands again and workshops regain workers. Monthly: §G−1§! opposition and §G−1§! supply strain."),
"coastal_watch": ("Береговая наблюдательная служба", "Coastal Observation Service", "Сигнальные посты связывают патрули и гарнизоны.", "Signal posts link patrols and garrisons."),
"strikes": ("Забастовки и тайные ячейки", "Strikes and Underground Cells", "При оппозиции от 65 склады и мастерские становятся местом сопротивления. Штраф исчезнет после снижения оппозиции ниже 65.", "At opposition of 65 or more, depots and workshops become centres of resistance. The penalty ends when opposition falls below 65."),
"rationing": ("Срыв продовольственных квот", "Food Quotas Breaking Down", "При истощении от 65 приказов больше, чем риса и исправных лодок. Штраф исчезнет после снижения истощения ниже 65.", "At strain of 65 or more, orders outnumber rice stocks and working boats. The penalty ends when strain falls below 65."),
"shattered_officer_corps": ("Обезглавленные штабы", "Decapitated Staffs", "Устрашение сломило противников, но унёсшиеся с ними знания не заменишь новой присягой.", "Intimidation broke the opposition, but another oath cannot replace the expertise lost with it."),
"iron_state": ("Железный архипелаг", "The Iron Archipelago", "Гарнизоны держат проливы, а государство научилось переживать собственные чрезвычайные меры.", "Garrisons hold the straits, and the state has learned to survive its own emergency measures."),
}
for key, (ru, en, dru, den) in ideas.items():
    text("A10M_" + key, ru, en)
    text("A10M_" + key + "_desc", dru, den)

tips = {
"system": ("Открывает управление §Yоппозицией§!, §Yрепрессиями§! и §Yистощением снабжения§! через решения «Государство под караулом». Показатели ограничены диапазоном 0–100.", "Unlocks management of §Yopposition§!, §Yrepression§! and §Ysupply strain§! through The State Under Guard decisions. Values are bounded between 0 and 100."),
"recall_members": ("Присоединяет только наши собственные подчинённые островные республики и возвращает их войска. Независимые страны и чужие субъекты сохраняют свой статус.", "Annexes only our own subordinate island republics and transfers their troops back. Independent countries and foreign subjects retain their status."),
"junta": ("Репрессии больше не снижаются на 1 каждый месяц. Освобождение задержанных остаётся доступным.", "Repression no longer falls by 1 each month. Releasing detainees remains available."),
"requisition": ("Реквизиционные бюро ежемесячно добавляют §R2§! истощения снабжения. Открывает чрезвычайные реквизиции и их последующую отмену.", "Requisition bureaus add §R2§! supply strain monthly. Unlocks emergency requisitions and the later suspension of the quota system."),
"compensation": ("Расписки ежемесячно уменьшают истощение снабжения на §G2§!.", "Receipts reduce supply strain by §G2§! monthly."),
"labour": ("Трудовые батальоны ежемесячно добавляют §R3§! оппозиции и §R2§! истощения снабжения. Их можно распустить отдельным решением.", "Labour battalions add §R3§! opposition and §R2§! supply strain monthly. They can be disbanded through a separate decision."),
"hospitals": ("Лазареты ежемесячно уменьшают истощение снабжения на §G1§!.", "Infirmaries reduce supply strain by §G1§! monthly."),
"inspectorate": ("Инспекция ежемесячно уменьшает истощение снабжения на §G1§!. Открывает ротацию гарнизонов.", "The inspectorate reduces supply strain by §G1§! monthly. Unlocks garrison rotations."),
"budget": ("Ревизия ежемесячно уменьшает истощение снабжения на §G1§!.", "Auditing reduces supply strain by §G1§! monthly."),
"professional": ("Уставная служба ежемесячно уменьшает оппозицию на §G1§!.", "Regulated service reduces opposition by §G1§! monthly."),
"settlement": ("Выплаты ежемесячно уменьшают оппозицию на §G1§! и истощение снабжения на §G2§!.", "Payments reduce opposition by §G1§! and supply strain by §G2§! monthly."),
"recovery": ("Распускает трудовые батальоны. Восстановление ежемесячно уменьшает оппозицию и истощение снабжения на §G1§!.", "Disbands labour battalions. Recovery reduces opposition and supply strain by §G1§! monthly."),
"suspend_requisitions": ("Обязательные квоты прекращают ежемесячно добавлять 2 истощения снабжения. Разовые чрезвычайные реквизиции остаются доступны.", "Compulsory quotas stop adding 2 supply strain monthly. Individual emergency requisitions remain available."),
}
for key, (ru, en) in tips.items():
    text("A10M_" + key + "_tt", ru, en)

decisions = {
"provincial_hearings": ("Выслушать провинциальных посредников", "Hear Provincial Intermediaries", "Подписанные жалобы дадут островам способ говорить без тайных собраний. Оппозиция: §G−12§!, репрессии: §G−3§!, истощение: §R+3§!.", "Signed petitions will give the islands a way to speak without secret assemblies. Opposition: §G−12§!, repression: §G−3§!, strain: §R+3§!."),
"security_sweep": ("Провести облавы комендатур", "Order Commandant Sweeps", "Аресты разрушат сеть противников, но их семьи запомнят лица караулов. Оппозиция: §G−18§!, репрессии: §R+12§!, истощение: §R+6§!.", "Arrests will disrupt the opposition network, but its families will remember the guards. Opposition: §G−18§!, repression: §R+12§!, strain: §R+6§!."),
"release_detainees": ("Пересмотреть списки задержанных", "Review Detainee Lists", "Освобождение людей без предъявленного обвинения ограничит произвол комендантов. Репрессии: §G−15§!, оппозиция: §G−5§!.", "Releasing people held without charge will curb the commandants' arbitrary power. Repression: §G−15§!, opposition: §G−5§!."),
"purchase_rice": ("Закупить рис для гарнизонов и семей", "Buy Rice for Garrisons and Families", "Казённые закупки пополнят запасы прежде, чем очередная квота разорит пристань. Истощение: §G−18§!, оппозиция: §G−3§!.", "Treasury purchases will replenish stocks before another quota ruins a landing. Strain: §G−18§!, opposition: §G−3§!."),
"emergency_requisition": ("Изъять резервные поставки", "Seize Reserve Deliveries", "Склад получит оружие за счёт запасов, предназначенных для будущих работ. Истощение: §R+12§!, оппозиция: §R+8§!.", "The depot will receive weapons at the expense of reserves intended for future work. Strain: §R+12§!, opposition: §R+8§!."),
"rotate_garrisons": ("Сменить гарнизонные команды", "Rotate Garrison Commands", "Смена начальников ослабит местные поборы и позволит проверить ведомости. Оппозиция: §G−8§!, истощение: §G−8§!.", "A change of commanders will disrupt local extortion and permit an audit. Opposition: §G−8§!, strain: §G−8§!."),
"end_labour_battalions": ("Распустить трудовые батальоны", "Disband the Labour Battalions", "Люди вернутся в семьи, а казна признает обязательства перед поставщиками. Оппозиция: §G−15§!, истощение: §G−10§!.", "Workers will return to their families and the treasury will recognise its obligations to suppliers. Opposition: §G−15§!, strain: §G−10§!."),
"recall_officers": ("Вернуть отстранённых специалистов", "Recall Dismissed Specialists", "Штабам снова нужны опытные люди, даже если их прежние показания неудобны коменданту. Снимает штраф обезглавленных штабов; оппозиция: §R+5§!, репрессии: §G−5§!.", "The staffs need experienced people again, even if their earlier testimony troubles the commandant. Removes the decapitated staffs penalty; opposition: §R+5§!, repression: §G−5§!."),
"suspend_requisitions": ("Отменить обязательные квоты", "Suspend Compulsory Quotas", "Поставки вернутся к закупкам по договору. Истощение: §G−15§!; реквизиционные бюро прекращают работу.", "Deliveries will return to contract purchases. Strain: §G−15§!; requisition bureaus cease operating."),
}
for key, (ru, en, dru, den) in decisions.items():
    text("A10M_" + key, ru, en)
    text("A10M_" + key + "_desc", dru, den)

events = {
1: ("Последний звонок конгресса", "The Congress's Last Bell",
    "На рассвете делегатов вывели между караулами. Полковник Сандоваль принял доклады о занятых причалах и приказал снять с дверей печати конгресса. Радикалы требуют немедленных арестов. Интенданты напоминают, что без прежних служащих порт не сумеет выдать даже суточный паёк.",
    "At dawn the delegates were led out between guards. Colonel Sandoval received reports of occupied landings and ordered the congress seals stripped from the doors. Radicals demand immediate arrests. Quartermasters warn that without the old clerks the port cannot issue even a day's rations.",
    "Закрепить власть показательной чисткой.", "Secure power with an exemplary purge.", "Оставить служащих под офицерским поручительством.", "Keep the clerks under officers' guarantees."),
2: ("Подсудимые в мундирах", "Defendants in Uniform",
    "Трибунал представил два списка. В первом — офицеры, против которых есть подписанные показания. Во втором — всякий начальник, когда-либо возражавший полковнику. Молодые радикалы уже требуют освободившиеся должности; штаб предупреждает, что списки включают лучших организаторов снабжения.",
    "The tribunal has produced two lists. The first contains officers named in signed testimony. The second names every commander who ever contradicted the colonel. Young radicals already demand the vacant posts; the staff warns that the lists include its best supply organisers.",
    "Судить только по предъявленным обвинениям.", "Try only the documented charges.", "Выжечь нелояльность во всём штабе.", "Burn disloyalty out of the entire staff."),
3: ("Пустые мешки под казённой печатью", "Empty Sacks Under Treasury Seals",
    "Коменданты снова отчитались об исполненных квотах, но на пристанях стоят пустые мешки. В деревнях едят посевное зерно, гарнизоны делят недостающие пайки. Казна может срочно закупить продовольствие и сократить требования. Радикалы предлагают забрать остатки хозяйственных запасов ради немедленного снабжения армии.",
    "The commandants have again reported completed quotas, yet empty sacks stand on the landings. Villages are eating seed grain and garrisons dividing short rations. The treasury can buy food urgently and reduce its demands. Radicals propose seizing remaining household reserves to supply the army at once.",
    "Снизить квоты и заплатить за рис.", "Reduce the quotas and pay for rice.", "Забрать остатки. Армия получит своё.", "Seize what remains. The army will have its share."),
4: ("Заговор под складской крышей", "Conspiracy Beneath the Depot Roof",
    "Портовые рабочие, провинциальные посредники и несколько младших офицеров готовили общую остановку погрузки. Охрана захватила переписку, но новые аресты могут поднять соседние гарнизоны. Посредники обещают прекратить выступления в обмен на пересмотр задержаний и обязательств казны.",
    "Dock workers, provincial intermediaries and several junior officers prepared a common loading stoppage. The guards seized their correspondence, but further arrests may turn neighbouring garrisons. Intermediaries promise to halt the action in exchange for a review of detentions and treasury obligations.",
    "Купить перемирие пересмотром обязательств.", "Purchase a truce by revising the obligations.", "Объявить заговорщиков врагами государства.", "Declare the conspirators enemies of the state."),
5: ("Парад и закрытые двери", "The Parade and the Closed Doors",
    "На пристани прошли части нового военного государства. За трибуной остался дом конгресса, куда делегаты так и не вернулись. Командование может превратить день в новую присягу или открыть приём прошений, чтобы услышать семьи тех, кто прошёл перед трибуной.",
    "Units of the new military state marched along the landing. Behind the reviewing stand stood the congress building, to which the delegates have never returned. The command can turn the day into another oath or receive petitions from the families of those marching before it.",
    "Присяга превыше прошений.", "The oath stands above petitions.", "Открыть приём семей и посредников.", "Receive the families and intermediaries."),
6: ("Посредники у комендатуры", "Intermediaries at the Commandant's Office",
    "Отзыв хартий не уничтожил людей, которые ими пользовались. Советы прислали старейшин с просьбой сохранить местных писарей, расписание рынков и привычный порядок водных перевозок. Радикалы видят в этих просьбах попытку переждать переворот; интенданты — единственный способ не остановить жизнь островов.",
    "Revoking the charters has not erased the people who lived by them. Councils have sent elders asking to retain local clerks, market schedules and familiar boat services. Radicals see an attempt to outlast the coup; quartermasters see the only way to keep island life moving.",
    "Сохранить местные службы под надзором.", "Retain local services under supervision.", "Заменить посредников военными командами.", "Replace the intermediaries with military detachments."),
}
for eid, (ru, en, dru, den, aru, aen, bru, ben) in events.items():
    for suffix, r, e in (("t", ru, en), ("d", dru, den), ("a", aru, aen), ("b", bru, ben)):
        text(f"A10M.{eid}.{suffix}", r, e)

(ROOT / "tools/a10m_focuses.json").write_text(json.dumps(focuses, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for lang, entries in loc.items():
    content = "l_" + lang + ":\n" + "\n".join(f' {key}:0 "{value}"' for key, value in entries.items()) + "\n"
    (ROOT / f"localisation/{lang}/A10M_military_l_{lang}.yml").write_text(content, encoding="utf-8-sig")
print(f"Built {len(focuses)} military focuses and {len(loc['russian'])} keys per language.")
