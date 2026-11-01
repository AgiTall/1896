"""Build the shared Philippine development content; never edits legacy files."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
LOCS = {"russian": {}, "english": {}}
FOCUSES = []


def write(path, value, bom=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value.strip() + "\n", encoding="utf-8-sig" if bom else "utf-8")


def loc(key, ru, en, ru_desc=None, en_desc=None):
    LOCS["russian"][key] = ru
    LOCS["english"][key] = en
    if ru_desc is not None:
        LOCS["russian"][key + "_desc"] = ru_desc
        LOCS["english"][key + "_desc"] = en_desc


def focus(id, ru, en, x, y, prereqs, reward, ru_desc, en_desc, icon="production", cost=5, available="", ai=2):
    FOCUSES.append(dict(id=id, name_ru=ru, name_en=en, desc_ru=ru_desc, desc_en=en_desc,
                        icon="GFX_goal_generic_" + icon, x=x, y=y+3, cost=cost,
                        prerequisites=[[p] if isinstance(p, str) else p for p in prereqs], mutually_exclusive=[],
                        available=available, reward=reward, ai=ai))


ELIGIBLE = "any_state = { A10D_eligible_state_trigger = yes }"

# Economy: fourteen focuses, independently useful to every constitutional path.
focus("A10D_island_census", "Перепись островных хозяйств", "The Island Household Census", -10, 1,
      [["A10_confederation", "A10W_oath", "A10M_coup"]], "add_political_power = 35 add_to_variable = { A10D_supply = 5 } A10D_refresh_supply = yes country_event = { id = A10D_development.3 days = 3 }",
      "Сборщики пошлин знают число тюков, но не число голодных семей. Перепись лодок, колодцев и посевов покажет, какие провинции действительно способны кормить соседей.",
      "Customs collectors can count bales, but not hungry households. A census of boats, wells and cultivated land will show which provinces can actually feed their neighbours.", "national_unity")
focus("A10D_municipal_roads", "Муниципальные дороги", "Municipal Roads", -14, 3,
      ["A10D_island_census"], "A10D_build_roads = yes add_to_variable = { A10D_supply = 5 } A10D_refresh_supply = yes",
      "Дорога от поля до пристани важнее обещаний о большой железной дороге. Общины получат инструменты и оплату за мощёные участки, мосты и дренажные канавы.",
      "The road from a field to its landing stage matters more than promises of a grand railway. Communities will receive tools and wages for paving, bridges and drainage ditches.", "construction", cost=10, available=ELIGIBLE)
focus("A10D_mail_ferries", "Почтовые паромы", "The Mail Ferries", -6, 3,
      ["A10D_island_census"], "add_equipment_to_stockpile = { type = convoy_1 amount = 8 producer = A10 } add_to_variable = { A10D_supply = 10 } A10D_refresh_supply = yes",
      "Между островами ходят парусники с несовместимыми расписаниями. Договор с капитанами соединит почтовую службу, перевозку врачей и доставку зерна в одну сеть.",
      "Sailing vessels connect the islands on incompatible timetables. Agreements with their captains will unite mail, visiting doctors and grain deliveries in one service.", "navy_doctrines_tactics", cost=10)
focus("A10D_abaca_cooperatives", "Кооперативы абаки", "Abaca Cooperatives", -14, 5,
      ["A10D_municipal_roads"], "add_ideas = A10D_abaca_exports add_political_power = 35",
      "Корабли всего мира нуждаются в манильском пеньковом канате. Совместные склады и единый вес тюка позволят мелким производителям договариваться с купцами без разорительных авансов.",
      "The world's ships need Manila hemp rope. Shared warehouses and a standard bale weight will let small growers bargain with merchants without ruinous advances.", "trade")
focus("A10D_sugar_inspectors", "Весы сахарных пристаней", "Scales on the Sugar Quays", -10, 5,
      ["A10D_municipal_roads"], "add_ideas = A10D_sugar_standards add_to_variable = { A10D_supply = 5 } A10D_refresh_supply = yes",
      "Провинциальные инспекторы проверят вес и качество сахара, а договоры сохранят участки под рис. Экспорт не должен оставлять семьи без хлеба в сезон штормов.",
      "Provincial inspectors will verify sugar weights and grades, while contracts preserve land for rice. Export earnings must not leave families hungry during the storm season.", "trade")
focus("A10D_timber_and_slipways", "Лесопилки у проливов", "Sawmills on the Straits", -6, 5,
      ["A10D_mail_ferries"], "A10D_build_cebu_workshops = yes add_to_variable = { A10D_supply = 5 } A10D_refresh_supply = yes",
      "Сушильные навесы, пилорамы и учёт рубок обеспечат досками лодочников и строителей. Заказы пойдут в Себу, если остров остаётся в нашем круге, иначе — в доступные союзные мастерские.",
      "Seasoning sheds, sawmills and managed cutting will supply boatbuilders and carpenters. Cebu will receive the contracts if it remains within our association; otherwise accessible member workshops will take them.", "construct_civ_factory", cost=10, available=ELIGIBLE)
focus("A10D_provincial_workshops", "Провинциальные мастерские", "Provincial Workshops", -14, 7,
      ["A10D_abaca_cooperatives"], "A10D_build_visayan_factory = yes remove_ideas = A10D_workshop_islands add_ideas = A10D_workshop_network set_technology = { early_machine_tools = 1 }",
      "Провинции не обязаны отдавать свои станки столице. Общие чертежи и закупка приводных ремней соединят небольшие мастерские в сеть взаимных заказов.",
      "The provinces need not surrender their lathes to the capital. Shared drawings and purchases of drive belts will link small workshops through mutual orders.", "construct_civ_factory", cost=10, available=ELIGIBLE)
focus("A10D_rice_granaries", "Рисовые амбары общин", "Communal Rice Granaries", -10, 7,
      ["A10D_sugar_inspectors"], "add_ideas = A10D_granary_network add_to_variable = { A10D_supply = 15 } A10D_refresh_supply = yes",
      "Каждая община оставит часть урожая в сухом общественном амбаре. Запас будут учитывать избранные хранители, чтобы тайфун не превращал нехватку пароходов в голод.",
      "Every community will reserve part of its harvest in a dry public granary. Elected custodians will keep the accounts so that a typhoon cannot turn a steamer shortage into famine.", "production")
focus("A10D_district_clinics", "Уездные лечебницы", "District Clinics", -6, 7,
      ["A10D_timber_and_slipways"], "add_ideas = A10D_district_medicine set_technology = { tech_support = 1 } add_equipment_to_stockpile = { type = support_equipment_1 amount = 100 producer = A10 } country_event = { id = A10D_development.4 days = 2 }",
      "Кипячёная вода, перевязочный материал и акушерка спасают больше жизней, чем пышные столичные больницы. Лечебницы станут одновременно местом обучения санитаров для островных гарнизонов.",
      "Boiled water, clean dressings and a trained midwife save more lives than magnificent hospitals in the capital. District clinics will also train orderlies for the island garrisons.", "scientific_exchange", cost=10)
focus("A10D_normal_schools", "Учительские семинарии", "Teacher Training Colleges", -14, 10,
      ["A10D_provincial_workshops"], "add_ideas = A10D_teacher_colleges add_political_power = 30",
      "Учитель должен уметь объяснить счёт, устройство насоса и содержание государственного письма на языке своей общины. Семинарии подготовят таких наставников для прибрежных городков и горных селений.",
      "A teacher must explain arithmetic, a pump and an official letter in the language of the community. New colleges will prepare such teachers for coastal towns and upland villages.", "scientific_exchange")
focus("A10D_cable_cooperatives", "Кабельные артели", "Cable Cooperatives", -10, 10,
      ["A10D_rice_granaries", "A10D_mail_ferries"], "add_ideas = A10D_island_telegraph add_to_variable = { A10D_supply = 10 } A10D_refresh_supply = yes",
      "Местный телеграф не заменит океанских кабелей Палаты, зато позволит сообщать о штормах и ценах без недельного ожидания. Рыбацкие артели дадут береговые команды, мастерские — изоляторы и провод.",
      "A local telegraph cannot replace the Chamber's ocean cables, but it can carry storm warnings and market prices without a week's delay. Fishing cooperatives will provide shore crews, and workshops the wire and insulators.", "intelligence_exchange", cost=10)
focus("A10D_sanitary_commission", "Санитарная комиссия островов", "The Islands Sanitary Commission", -6, 10,
      ["A10D_district_clinics"], "swap_ideas = { remove_idea = A10D_district_medicine add_idea = A10D_public_health } add_stability = 0.03 add_to_variable = { A10D_supply = 5 } A10D_refresh_supply = yes",
      "Карантин должен останавливать лихорадку, а не торговлю. Врачи согласуют правила для портов, устроят чистые водозаборы и научат паромные команды распознавать первые признаки болезни.",
      "Quarantine should stop fever rather than commerce. Doctors will agree on port regulations, establish clean water intakes and teach ferry crews to recognise the first signs of disease.", "scientific_exchange")
focus("A10D_island_polytechnic", "Островной политехникум", "The Island Polytechnic", -14, 13,
      ["A10D_normal_schools", "A10D_cable_cooperatives"], "add_research_slot = 1 add_ideas = A10D_polytechnic",
      "Машинисты, землемеры и химики нуждаются в собственном училище. Политехникум объединит преподавателей из провинций и беженцев со старого материка вокруг практических задач островной жизни.",
      "Engine drivers, surveyors and chemists need a college of their own. The polytechnic will bring provincial teachers and refugees from the old continents together around the practical problems of island life.", "scientific_exchange", cost=10)
focus("A10D_national_market", "Рынок тысячи пристаней", "The Market of a Thousand Quays", -10, 16,
      ["A10D_island_polytechnic", "A10D_sanitary_commission"], "A10D_build_market_factory = yes add_ideas = A10D_common_market add_to_variable = { A10D_supply = 10 } A10D_refresh_supply = yes country_event = { id = A10D_development.6 days = 2 }",
      "Расписания паромов, проверенные весы, ремесленные школы и здоровые портовые города наконец складываются в одно хозяйство. Каждый остров сохранит своё лицо, а его товары найдут дорогу к соседям.",
      "Ferry timetables, honest scales, trade schools and healthy ports are finally becoming one economy. Each island will keep its character while its goods find a reliable passage to its neighbours.", "trade", cost=10, available=ELIGIBLE)

# Military: fourteen focuses; the declaration of war is owned by the root tree.
focus("A10_coastal_arsenals", "Береговые арсеналы", "Coastal Arsenals", -28, 1,
      [["A10_confederation", "A10W_oath", "A10M_coup"]], "A10D_build_arsenal = yes add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 1500 producer = A10 }",
      "Защита островов начинается с сухого склада, исправного затвора и собственного оружейника. Береговые мастерские получат станки и запас винтовок для будущих гарнизонов.",
      "Island defence begins with a dry store, a working bolt and a gunsmith of our own. Coastal workshops will receive machine tools and a reserve of rifles for future garrisons.", "construct_mil_factory", cost=10, available=ELIGIBLE, ai=4)
focus("A10D_rifle_inspections", "Осмотр полковых винтовок", "The Regimental Rifle Inspection", -32, 3,
      ["A10_coastal_arsenals"], "army_experience = 10 add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 500 producer = A10 } add_tech_bonus = { name = A10D_rifle_studies bonus = 0.5 uses = 1 category = infantry_weapons }",
      "На соседних островах одинаковое слово «патрон» означает разный калибр. Оружейники перепишут системы, отделят опасные стволы и вернут в строй исправные винтовки.",
      "On neighbouring islands the same word for cartridge can mean different calibres. Gunsmiths will catalogue each system, condemn unsafe barrels and return serviceable rifles to the ranks.", "production")
focus("A10D_coastal_boatyards", "Лодочные верфи", "Coastal Boatyards", -24, 3,
      ["A10_coastal_arsenals"], "A10D_build_boatyard = yes add_equipment_to_stockpile = { type = convoy_1 amount = 10 producer = A10 } add_to_variable = { A10D_supply = 5 } A10D_refresh_supply = yes",
      "Малой стране нужны ремонтные стапели раньше океанских броненосцев. Лодочники и котельщики начнут строить простые грузовые суда и обслуживать прибрежные пароходы.",
      "A small country needs repair slips before ocean-going battleships. Boatbuilders and boiler makers will begin with simple cargo vessels and the maintenance of coastal steamers.", "navy_doctrines_tactics", cost=10, available=ELIGIBLE)
focus("A10D_common_calibres", "Общий калибр снабжения", "One Calibre for the Supply Columns", -32, 5,
      ["A10D_rifle_inspections"], "remove_ideas = A10D_separate_quartermasters add_ideas = A10D_standard_stores add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 500 producer = A10 } add_to_variable = { A10D_supply = 5 } A10D_refresh_supply = yes",
      "Не требуется немедленно перевооружать каждого солдата. Достаточно разделить склады по системам, ввести одинаковые ящики и перестать посылать части патроны, которыми она не может стрелять.",
      "We need not rearm every soldier at once. Separate stores by rifle system, standardise the ammunition boxes and stop sending units cartridges they cannot fire.", "production")
focus("A10D_chart_the_straits", "Промеры проливов", "Sound the Straits", -24, 5,
      ["A10D_coastal_boatyards"], "navy_experience = 15 add_ideas = A10D_pilot_stations add_to_variable = { A10D_supply = 5 } A10D_refresh_supply = yes",
      "Рыбаки знают рифы, которые отсутствуют на адмиральских картах. Гидрографы запишут их знания, поставят сигнальные огни и соберут службу лоцманов для тёмных и штормовых проходов.",
      "Fishermen know reefs missing from the admirals' charts. Hydrographers will record that knowledge, establish signal lights and organise pilots for passages in darkness and storms.", "navy_doctrines_tactics")
focus("A10D_field_batteries", "Полевые батареи", "Field Batteries", -32, 7,
      ["A10D_common_calibres"], "set_technology = { early_artillery = 1 } add_equipment_to_stockpile = { type = field_gun_equipment_0 amount = 48 producer = A10 } add_equipment_to_stockpile = { type = howitzer_equipment_0 amount = 12 producer = A10 } army_experience = 10",
      "Пехоте нужны лёгкие полевые пушки и несколько старых гаубиц, которые можно разобрать для вьючной перевозки. Расчёты обучатся выбирать позиции в джунглях и экономить привозные снаряды.",
      "Infantry needs light field guns and a few old howitzers that can be broken down for pack transport. Their crews will learn to choose jungle positions and conserve imported shells.", "army_artillery", cost=10)
focus("A10D_harbour_defences", "Батареи у гаваней", "Harbour Batteries", -24, 7,
      ["A10D_chart_the_straits"], "A10D_fortify_harbours = yes add_ideas = A10D_coastal_defence",
      "Старое морское орудие на береговом станке всё ещё опасно для десантной баржи. Укрытые склады и наблюдательные посты помогут защищать гавани без разорительного состязания с японскими броненосцами.",
      "An old naval gun on a shore mounting can still threaten a landing barge. Sheltered magazines and observation posts will help defend the harbours without an unaffordable race against Japanese battleships.", "fortify_city", cost=10, available="OR = { 1084 = { A10D_eligible_state_trigger = yes } 628 = { A10D_eligible_state_trigger = yes } }")
focus("A10D_sappers_and_pack_trains", "Сапёры и вьючные колонны", "Sappers and Pack Trains", -32, 9,
      ["A10D_field_batteries"], "set_technology = { tech_support = 1 tech_engineers = 1 } add_equipment_to_stockpile = { type = support_equipment_1 amount = 150 producer = A10 } add_ideas = A10D_pack_columns",
      "Мулы, плоты и переносные мостки доставят боеприпасы туда, где не пройдёт повозка. Сапёры научатся готовить тропы до подхода колонн, а не после первых потерь от голода.",
      "Mules, rafts and portable footbridges can carry ammunition where wagons fail. Sappers will prepare trails before the supply columns arrive, rather than after the first losses to hunger.", "army_doctrines", cost=10)
focus("A10D_merchant_reserve", "Резерв торговых судов", "The Merchant Shipping Reserve", -24, 9,
      ["A10D_harbour_defences"], "add_equipment_to_stockpile = { type = convoy_1 amount = 15 producer = A10 } add_to_variable = { A10D_supply = 10 } A10D_refresh_supply = yes country_event = { id = A10D_development.5 days = 2 }",
      "Судовладельцы заранее узнают условия найма, а армия — грузоподъёмность каждого судна. Резервные команды не позволят мобилизации сразу остановить рисовые перевозки.",
      "Shipowners will know the charter terms in advance, and the army the capacity of every vessel. Reserve crews will keep mobilisation from bringing the rice trade to an immediate halt.", "navy_doctrines_tactics", cost=10)
focus("A10D_staff_college", "Штабная школа островов", "The Islands Staff College", -32, 11,
      ["A10D_sappers_and_pack_trains"], "add_ideas = A10D_staff_school army_experience = 15 add_command_power = 20",
      "Штаб должен рассчитывать прилив так же уверенно, как численность батальона. В школе сведут полевых офицеров, лоцманов и интендантов за одним картографическим столом.",
      "A staff must calculate the tide as confidently as a battalion's strength. The college will put field officers, pilots and quartermasters around the same map table.", "army_doctrines", cost=10)
focus("A10D_gunboat_school", "Школа канонерских команд", "The Gunboat Crews School", -24, 11,
      ["A10D_merchant_reserve"], "if = { limit = { has_dlc = \"Man the Guns\" } set_technology = { torpedo_boat_ship_hull_light = 1 gunboat_ship_hull_light = 1 } } else = { set_technology = { early_destroyer = 1 } } navy_experience = 20 add_tech_bonus = { name = A10D_light_vessels bonus = 0.5 uses = 1 category = naval_equipment }",
      "Будущим командирам предстоит служить на канонерках, миноносцах и вооружённых пароходах. Они начнут с котельного дела, стрельбы по щитам и сопровождения тихоходных транспортов.",
      "Future commanders will serve in gunboats, torpedo craft and armed steamers. They will begin with boiler practice, gunnery targets and the escort of slow transports.", "navy_cruiser", cost=10)
focus("A10D_ammunition_toolrooms", "Инструментальные цеха арсеналов", "Arsenal Toolrooms", -32, 13,
      ["A10D_staff_college"], "A10D_build_toolroom = yes add_ideas = A10D_ammunition_contracts add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 800 producer = A10 }",
      "Новые цеха будут делать гильзы, пружины и запасные части по общим допускам. Заказ мал, но его можно выполнять круглый год, не ожидая очередного застрахованного каравана.",
      "New toolrooms will make cartridge cases, springs and spare parts to shared tolerances. The order is modest, but it can be filled all year without waiting for another insured convoy.", "construct_mil_factory", cost=10, available=ELIGIBLE)
focus("A10D_patrol_flotillas", "Дозорные флотилии", "Patrol Flotillas", -24, 13,
      ["A10D_gunboat_school"], "A10D_build_second_boatyard = yes add_ideas = A10D_escort_service navy_experience = 10",
      "Небольшие дозоры прикроют подходы к паромным линиям и передадут предупреждение гарнизонам. Их задача — сохранить перевозки и уйти от превосходящих сил, пока береговые батареи готовятся к бою.",
      "Small patrols will cover the ferry approaches and warn the garrisons. Their task is to preserve shipping and withdraw from superior forces while the harbour batteries prepare for action.", "navy_doctrines_tactics", cost=10, available=ELIGIBLE)
focus("A10_landing_plans", "Планы островных высадок", "Plans for Island Landings", -28, 16,
      ["A10D_ammunition_toolrooms", "A10D_patrol_flotillas"], "if = { limit = { has_dlc = \"Man the Guns\" } set_technology = { mtg_transport = 1 } } else = { set_technology = { transport = 1 } } add_ideas = A10D_landing_staff add_command_power = 25 add_war_support = 0.08 navy_experience = 10",
      "Высадка начинается с пресной воды, приливной таблицы и лодки для разгрузки, а не с приказа наступать. Армия и флот отработают ограниченные операции, оставив решение о войне гражданской или военной власти.",
      "A landing begins with fresh water, a tide table and an unloading boat, rather than an order to advance. The army and fleet will rehearse limited operations, leaving the decision for war to the country's government.", "amphibious_assault", cost=10)

write("tools/a10d_focuses.json", json.dumps(FOCUSES, ensure_ascii=False, indent=2))

write("common/scripted_triggers/A10D_development.txt", '''
A10D_eligible_state_trigger = {
 A10R_archipelago_state_trigger = yes
 OR = {
  AND = { is_owned_by = A10 is_controlled_by = A10 }
  AND = { owner = { A10R_member_trigger = yes is_subject_of = A10 } is_controlled_by = OWNER }
 }
}
''')

# A preferred local province is always checked, with a safe member-state fallback.
def state_build(preferred, kind, slots=1, level=1):
    body = f"add_extra_state_shared_building_slots = {slots} add_building_construction = {{ type = {kind} level = {level} instant_build = yes }}"
    return f'''if = {{ limit = {{ {preferred} = {{ A10D_eligible_state_trigger = yes }} }}
  {preferred} = {{ {body} }}
 }} else = {{ random_state = {{ limit = {{ A10D_eligible_state_trigger = yes }} {body} }} }}'''


effects = '''
A10D_initialize = {
 if = { limit = { tag = A10 NOT = { has_country_flag = A10D_initialized } }
  set_country_flag = A10D_initialized
  set_variable = { A10D_supply = 35 }
  add_ideas = A10D_workshop_islands
  add_ideas = A10D_separate_quartermasters
  A10D_refresh_supply = yes
  country_event = { id = A10D_development.1 days = 21 }
  country_event = { id = A10D_development.2 days = 240 random_days = 45 }
 }
}
A10D_refresh_supply = {
 clamp_variable = { var = A10D_supply min = 0 max = 100 }
 remove_ideas = A10D_shipping_shortage
 remove_ideas = A10D_strained_shipping
 remove_ideas = A10D_reliable_shipping
 if = { limit = { check_variable = { A10D_supply < 20 } } add_ideas = A10D_shipping_shortage }
 else_if = { limit = { check_variable = { A10D_supply < 50 } } add_ideas = A10D_strained_shipping }
 else_if = { limit = { NOT = { check_variable = { A10D_supply < 80 } } } add_ideas = A10D_reliable_shipping }
}
A10D_build_roads = {
 random_state = { limit = { A10D_eligible_state_trigger = yes NOT = { has_country_flag = A10D_unused } infrastructure < 5 }
  add_building_construction = { type = infrastructure level = 1 instant_build = yes }
 }
 random_state = { limit = { A10D_eligible_state_trigger = yes infrastructure < 5 }
  add_building_construction = { type = infrastructure level = 1 instant_build = yes }
 }
}
'''
for name, state, kind in [
    ("A10D_build_cebu_workshops", 628, "industrial_complex"),
    ("A10D_build_visayan_factory", 624, "industrial_complex"),
    ("A10D_build_market_factory", 1084, "industrial_complex"),
    ("A10D_build_arsenal", 1084, "arms_factory"),
    ("A10D_build_toolroom", 624, "arms_factory"),
    ("A10D_build_boatyard", 1084, "dockyard"),
    ("A10D_build_second_boatyard", 628, "dockyard"),
]:
    # Only coastal states can host a dockyard; all preferred states are coastal.
    value = state_build(state, kind)
    if kind == "dockyard":
        value = value.replace("limit = { A10D_eligible_state_trigger = yes }", "limit = { A10D_eligible_state_trigger = yes is_coastal = yes }")
    effects += f"{name} = {{\n {value}\n}}\n"
effects += '''
A10D_fortify_harbours = {
 1084 = { if = { limit = { A10D_eligible_state_trigger = yes }
  add_building_construction = { type = coastal_bunker level = 2 province = 1221 instant_build = yes }
  add_building_construction = { type = naval_base level = 1 province = 1221 instant_build = yes }
 } }
 628 = { if = { limit = { A10D_eligible_state_trigger = yes }
  add_building_construction = { type = coastal_bunker level = 1 province = 12118 instant_build = yes }
 } }
}
'''
# State limit uses a state building level, not a country flag.
effects = effects.replace("NOT = { has_country_flag = A10D_unused } ", "")
write("common/scripted_effects/A10D_development.txt", effects)

IDEAS = [
 ("A10D_workshop_islands", "Островки ремесла", "Islands of Craft", "industrial_capacity_factory = -0.08 production_speed_buildings_factor = -0.08", "Малые мастерские спасли ремёсла после Исхода, но общих чертежей, запасных частей и устойчивых заказов пока нет.", "Small workshops preserved the trades after the Exodus, but shared drawings, spare parts and reliable orders are still lacking."),
 ("A10D_separate_quartermasters", "Провинциальные интенданты", "Separate Provincial Quartermasters", "army_org_factor = -0.08 supply_consumption_factor = 0.08", "Местные склады снабжают свои гарнизоны. Соседний полк часто получает чужой калибр и не знает расписания судов.", "Local stores provision their own garrisons. A neighbouring regiment too often receives the wrong cartridges and no sailing timetable."),
 ("A10D_shipping_shortage", "Перебои островного снабжения", "Island Provisioning Shortage", "supply_consumption_factor = 0.10 industrial_capacity_factory = -0.05 stability_factor = -0.05", "Резерв перевозок ниже 20. Недостаток сухих складов, лодок и рисовых запасов задерживает военные и гражданские грузы. Почтовые паромы, амбары и решения о доставке риса восстановят сообщение.", "The provisioning reserve is below 20. Too few dry stores, boats and grain reserves delay military and civilian cargo. Mail ferries, granaries and rice delivery programmes can restore the service."),
 ("A10D_strained_shipping", "Перегруженные паромные линии", "Overburdened Ferry Lines", "supply_consumption_factor = 0.05 stability_factor = -0.02", "Резерв перевозок от 20 до 49. Любая поломка парохода задерживает рис, почту и армейские грузы. При резерве 50 задержки прекратятся.", "The provisioning reserve is between 20 and 49. Every steamer breakdown delays grain, mail and military cargo. A reserve of 50 will clear the bottleneck."),
 ("A10D_reliable_shipping", "Надёжное островное сообщение", "Reliable Island Shipping", "naval_supply_consumption_factor = -0.03 stability_factor = 0.03", "При резерве не ниже 80 острова располагают запасными командами, сухими складами и судами на случай шторма.", "With a provisioning reserve of at least 80, the islands have reserve crews, dry warehouses and vessels for the storm season."),
 ("A10D_workshop_network", "Сеть провинциальных мастерских", "The Provincial Workshop Network", "industrial_capacity_factory = 0.05 production_factory_efficiency_gain_factor = 0.05", "Чертежи и взаимные заказы соединяют провинциальные мастерские, сохраняя местное ремесло.", "Shared drawings and mutual orders connect provincial workshops while preserving local craftsmanship."),
 ("A10D_abaca_exports", "Канат для океанских флотов", "Rope for the Ocean Fleets", "production_speed_dockyard_factor = 0.05 consumer_goods_factor = -0.02", "Кооперативы абаки обеспечивают канатные дворы сырьём и получают устойчивую долю экспортного дохода.", "Abaca cooperatives supply the ropewalks and receive a reliable share of export earnings."),
 ("A10D_sugar_standards", "Честные сахарные весы", "Honest Sugar Scales", "local_resources_factor = 0.05 stability_factor = 0.02", "Единый вес и проверенное качество облегчают торговлю, а сохранённые рисовые поля защищают общины от неурожая.", "Common weights and inspected grades support commerce, while preserved rice fields protect communities from harvest failure."),
 ("A10D_granary_network", "Общественные рисовые амбары", "Public Rice Granaries", "consumer_goods_factor = -0.02 supply_consumption_factor = -0.03", "Сухие общественные амбары позволяют пережить задержку судов без немедленного голода.", "Dry communal granaries allow households to survive shipping delays without immediate hunger."),
 ("A10D_district_medicine", "Уездная медицина", "District Medicine", "casualty_trickleback = 0.03 experience_loss_factor = -0.03", "Небольшие лечебницы готовят санитаров и возвращают раненых в строй.", "Small clinics train orderlies and return wounded soldiers to service."),
 ("A10D_public_health", "Чистая вода островов", "Clean Water for the Islands", "casualty_trickleback = 0.06 experience_loss_factor = -0.05 monthly_population = 0.03", "Водозаборы, карантины и обученные санитары уменьшают потери от болезней в семьях и гарнизонах.", "Clean water intakes, quarantine rules and trained orderlies reduce sickness in households and garrisons."),
 ("A10D_teacher_colleges", "Провинциальные учительские семинарии", "Provincial Teacher Colleges", "research_speed_factor = 0.03 stability_factor = 0.02", "Учителя объясняют счёт и грамоту на языках общин и готовят учеников к техническому образованию.", "Teachers explain arithmetic and literacy in community languages and prepare pupils for technical study."),
 ("A10D_island_telegraph", "Телеграф между пристанями", "The Quayside Telegraph", "planning_speed = 0.05 production_factory_efficiency_gain_factor = 0.03", "Сигнальные посты и местные кабели быстро передают распоряжения, цены и предупреждения о штормах.", "Signal stations and local cables quickly carry orders, prices and storm warnings."),
 ("A10D_polytechnic", "Островной политехникум", "The Island Polytechnic", "research_speed_factor = 0.03", "Училище готовит мастеров, химиков и землемеров для самостоятельного островного хозяйства.", "The college trains foremen, chemists and surveyors for a self-sustaining island economy."),
 ("A10D_common_market", "Рынок тысячи пристаней", "The Market of a Thousand Quays", "production_speed_industrial_complex_factor = 0.05 consumer_goods_factor = -0.02", "Надёжное сообщение и общие меры связывают местные рынки, не уничтожая их многообразия.", "Reliable shipping and common measures connect local markets without erasing their diversity."),
 ("A10D_standard_stores", "Упорядоченные полковые склады", "Standardised Regimental Stores", "supply_consumption_factor = -0.03 production_factory_max_efficiency_factor = 0.03", "Общие ведомости и разделённые по системам винтовок склады уменьшают потери боеприпасов.", "Common manifests and stores separated by rifle system reduce wasted ammunition."),
 ("A10D_pilot_stations", "Лоцманские станции проливов", "Straits Pilot Stations", "naval_coordination = 0.03 navy_org_factor = 0.03", "Знание течений и сигнальные огни помогают кораблям держать строй у родных берегов.", "Local current charts and signal lights help ships keep station near their own coasts."),
 ("A10D_coastal_defence", "Укрытые береговые батареи", "Sheltered Shore Batteries", "army_defence_factor = 0.03", "Береговые расчёты держат под наблюдением подходы к важнейшим пристаням.", "Shore gun crews keep watch over the approaches to the principal landing stages."),
 ("A10D_pack_columns", "Вьючные колонны гарнизонов", "Garrison Pack Columns", "supply_consumption_factor = -0.05 attrition = -0.05", "Подготовленные тропы, мулы и лодки доставляют грузы через горы и мангровые заросли.", "Prepared trails, mules and boats carry stores through mountains and mangroves."),
 ("A10D_staff_school", "Штабная школа островов", "The Islands Staff College", "army_org_factor = 0.05 planning_speed = 0.05 training_time_army_factor = -0.05", "Офицеры учатся согласовывать марш, приливы и разгрузку запасов.", "Officers learn to coordinate marches, tides and the unloading of supplies."),
 ("A10D_ammunition_contracts", "Круглогодичные оружейные заказы", "Year-Round Arsenal Orders", "industrial_capacity_factory = 0.04 production_factory_efficiency_gain_factor = 0.04", "Мастерские выполняют постоянные заказы на патроны и запасные части вместо лихорадочных закупок перед каждой тревогой.", "Workshops fulfil steady orders for cartridges and spare parts instead of emergency purchases at every alarm."),
 ("A10D_escort_service", "Служба прибрежных конвоев", "Coastal Escort Service", "convoy_escort_efficiency = 0.08 naval_coordination = 0.03", "Дозорные флотилии прикрывают паромные линии и вовремя предупреждают о появлении крупных сил.", "Patrol flotillas cover the ferry routes and give early warning of major enemy forces."),
 ("A10D_landing_staff", "Штаб островных высадок", "The Island Landing Staff", "naval_invasion_prep_speed = 0.10 naval_invasion_division_cap = 2", "Совместные учения научили штаб рассчитывать ограниченную высадку и снабжение первого эшелона.", "Joint exercises have taught the staff to plan limited landings and supply their first wave."),
 ("A10D_monsoon_damage", "Повреждённые тайфуном пристани", "Typhoon-Damaged Quays", "production_speed_buildings_factor = -0.05 supply_consumption_factor = 0.05", "Шторм повредил склады и причалы. Срочная починка пристаней сократит перебои, а обычные работы завершат восстановление за сезон.", "The storm has damaged stores and quays. Emergency repairs can shorten the disruption; ordinary works will finish restoration within the season."),
 ("A10D_evening_classes", "Вечерние занятия при мастерских", "Workshop Evening Classes", "research_speed_factor = 0.03", "Учителя и мастера ведут временные вечерние курсы для учеников, занятых днём на производстве.", "Teachers and foremen run temporary evening courses for apprentices who work during the day."),
 ("A10D_tools_programme", "Провинциальная закупка инструментов", "Provincial Tool Purchasing", "production_factory_efficiency_gain_factor = 0.05", "Оплаченная партия инструментов помогает мастерским освоить новые заказы.", "A paid consignment of tools helps workshops master their new orders."),
 ("A10D_volunteer_orderlies", "Добровольные санитарные дружины", "Volunteer Medical Detachments", "casualty_trickleback = 0.04 experience_loss_factor = -0.03", "Общины оплатили материалы и подготовку добровольных санитаров на ближайший сезон.", "Communities have paid for dressings and the training of volunteer orderlies for the coming season."),
 ("A10D_war_collections", "Общинные военные сборы", "Communal War Collections", "consumer_goods_factor = 0.02", "Сборы для семей призванных укрепляют поддержку войны, но требуют части гражданского выпуска.", "Collections for conscripts' families strengthen support for the war but absorb some civilian output."),
]
idea_text = "ideas = { country = {\n"
for key, ru, en, modifiers, ru_desc, en_desc in IDEAS:
    icon = "generic_army_war_college" if key in {"A10D_separate_quartermasters", "A10D_standard_stores", "A10D_pack_columns", "A10D_staff_school", "A10D_landing_staff"} else "generic_production_bonus"
    idea_text += f" {key} = {{ picture = {icon} removal_cost = -1 modifier = {{ {modifiers} }} }}\n"
    loc(key, ru, en, ru_desc, en_desc)
write("common/ideas/A10D_development.txt", idea_text + "} }")

loc("A10D_development", "Хозяйство и оборона архипелага", "Economy and Defence of the Archipelago",
    "Резерв островных перевозок: §Y[?A10D_supply|0]/100§!.\\nНиже §Y20§! — тяжёлые перебои; §Y20–49§! — перегруженные линии; §Y50–79§! — обычное сообщение; от §Y80§! — надёжные резервные маршруты.\\nРезерв учитывает лодки, сухие склады, экипажи и рис для рейсов. Работы, закупки и учения меняют его отдельно от государственного долга перед ВТП.",
    "Island provisioning reserve: §Y[?A10D_supply|0]/100§!.\\nBelow §Y20§!: serious shortages; §Y20–49§!: strained routes; §Y50–79§!: normal service; §Y80§! and above: reliable reserve routes.\\nThe reserve represents boats, dry warehouses, crews and grain for the voyages. Construction, purchases and exercises affect it independently of the state debt to the WTC.")
write("common/decisions/categories/A10D_development.txt", '''
A10D_development = {
 icon = generic_naval
 allowed = { tag = A10 }
 visible = { has_country_flag = A10D_initialized has_completed_focus = A10_island_congress }
}
''')

DECISIONS = []
def decision(key, ru, en, cost, days, cooldown, available, complete, remove, ru_desc, en_desc, visible="", ai=1, modifier=""):
    loc(key, ru, en, ru_desc, en_desc)
    text = f''' {key} = {{
  icon = generic_political_discourse cost = {cost} days_remove = {days} days_re_enable = {cooldown}
  available = {{ has_capitulated = no {available} }}
'''
    if visible:
        text += f"  visible = {{ {visible} }}\n"
    if modifier:
        text += f"  modifier = {{ {modifier} }}\n"
    if complete:
        text += f"  complete_effect = {{ {complete} }}\n"
    text += f"  remove_effect = {{ if = {{ limit = {{ has_capitulated = no }} {remove} }} }}\n"
    text += f"  ai_will_do = {{ factor = {ai} }}\n }}\n"
    DECISIONS.append(text)


decision("A10D_hire_coastal_boats", "Нанять прибрежные лодки", "Charter Coastal Boats", 40, 21, 60,
         "check_variable = { A10D_supply < 89 }", "", "add_to_variable = { A10D_supply = 12 } A10D_refresh_supply = yes navy_experience = 2",
         "Трёхнедельный договор с рыбаками и лодочниками восстановит малые рейсы. После завершения работ резерв перевозок вырастет на 12.",
         "A three-week contract with fishermen and boatbuilders will restore short routes. When the programme ends, the provisioning reserve rises by 12.", ai=2)
decision("A10D_buy_reserve_rice", "Закупить рис для паромных линий", "Purchase Rice for the Ferry Routes", 35, 21, 90,
         "check_variable = { A10D_supply < 89 }", "", "add_to_variable = { A10D_supply = 12 } A10D_refresh_supply = yes",
         "Оплатим продовольствие для команд и складов, временно отвлекая часть гражданских товаров. Через 21 день резерв перевозок вырастет на 12.",
         "Pay for grain for crews and warehouses, temporarily diverting some civilian goods. After 21 days the provisioning reserve rises by 12.", ai=2, modifier="consumer_goods_factor = 0.02")
decision("A10D_repair_typhoon_quays", "Восстановить штормовые пристани", "Repair the Storm-Damaged Quays", 60, 35, 180,
         "has_idea = A10D_monsoon_damage", "", "remove_ideas = A10D_monsoon_damage add_to_variable = { A10D_supply = 20 } A10D_refresh_supply = yes",
         "Направим плотников и плавучие краны в пострадавшие гавани. Через 35 дней повреждённые пристани вернутся в строй, а резерв перевозок вырастет на 20.",
         "Send carpenters and floating lifting crews to the damaged harbours. After 35 days the damaged quays return to service and the provisioning reserve rises by 20.", visible="has_idea = A10D_monsoon_damage", ai=5)
decision("A10D_export_rope_contract", "Выполнить канатный контракт", "Fulfil a Rope Contract", 30, 30, 120,
         "has_completed_focus = A10D_abaca_cooperatives check_variable = { A10D_supply > 24 }",
         "subtract_from_variable = { A10D_supply = 10 } A10D_refresh_supply = yes", "add_political_power = 65",
         "Кооперативы займут часть перевозок экспортным грузом: резерв сразу снизится на 10. Через месяц выручка в 65 политической власти пополнит общественные кассы.",
         "The cooperatives will reserve shipping for an export cargo, immediately consuming 10 reserve. After a month, export receipts provide 65 political power for public funds.", visible="has_completed_focus = A10D_abaca_cooperatives")
decision("A10D_purchase_provincial_tools", "Оплатить инструменты провинциям", "Purchase Tools for the Provinces", 65, 45, 180,
         "has_completed_focus = A10D_provincial_workshops check_variable = { A10D_supply > 24 }",
         "subtract_from_variable = { A10D_supply = 10 } A10D_refresh_supply = yes", "add_timed_idea = { idea = A10D_tools_programme days = 120 }",
         "Закупка и доставка потребуют 10 резерва перевозок. Через 45 дней мастерские получат инструменты и на 120 дней ускорят освоение производства.",
         "Purchasing and delivery require 10 provisioning reserve. After 45 days the workshops receive tools and improve production efficiency growth for 120 days.", visible="has_completed_focus = A10D_provincial_workshops")
decision("A10D_evening_literacy", "Провести вечерние занятия", "Organise Evening Classes", 40, 35, 150,
         "has_completed_focus = A10D_normal_schools check_variable = { A10D_supply > 14 }",
         "subtract_from_variable = { A10D_supply = 5 } A10D_refresh_supply = yes", "add_timed_idea = { idea = A10D_evening_classes days = 120 } add_stability = 0.01",
         "Учителя выедут в портовые мастерские. Доставка пособий потребует 5 резерва; через 35 дней начнутся курсы, помогающие исследованиям в течение 120 дней.",
         "Teachers will visit the harbour workshops. Transporting the books costs 5 reserve; after 35 days the classes improve research for 120 days.", visible="has_completed_focus = A10D_normal_schools")
decision("A10D_garrison_field_drills", "Провести гарнизонные учения", "Hold Garrison Field Exercises", 35, 21, 90,
         "has_completed_focus = A10D_common_calibres has_equipment = { infantry_equipment > 149 } check_variable = { A10D_supply > 19 }",
         "add_equipment_to_stockpile = { type = infantry_equipment amount = -150 } subtract_from_variable = { A10D_supply = 5 } A10D_refresh_supply = yes",
         "army_experience = 8",
         "Учебные стрельбы израсходуют 150 винтовок и 5 резерва перевозок на износ оружия и снабжение. Через 21 день офицеры принесут 8 опыта армии.",
         "Weapons wear and exercise supply consume 150 rifles and 5 provisioning reserve. After 21 days the officers return with 8 army experience.", visible="has_completed_focus = A10D_common_calibres")
decision("A10D_train_volunteer_orderlies", "Подготовить санитарные дружины", "Train Volunteer Orderlies", 45, 30, 180,
         "has_completed_focus = A10D_district_clinics check_variable = { A10D_supply > 14 }",
         "subtract_from_variable = { A10D_supply = 5 } A10D_refresh_supply = yes", "add_timed_idea = { idea = A10D_volunteer_orderlies days = 120 }",
         "Материалы и поездки потребуют 5 резерва. Через месяц санитарные дружины будут помогать возвращать раненых в строй в течение 120 дней.",
         "Dressings and travel cost 5 reserve. After a month the trained medical detachments will aid the recovery of wounded soldiers for 120 days.", visible="has_completed_focus = A10D_district_clinics")
decision("A10D_collect_for_soldiers_families", "Организовать сбор для семей солдат", "Collect for Soldiers' Families", 50, 35, 150,
         "has_war = yes has_war_support < 0.85 check_variable = { A10D_supply > 24 }",
         "subtract_from_variable = { A10D_supply = 10 } A10D_refresh_supply = yes add_timed_idea = { idea = A10D_war_collections days = 90 }",
         "add_war_support = 0.04",
         "Помощь семьям призванных требует 10 резерва и на 90 дней отвлекает гражданские товары. Через 35 дней поддержка войны вырастет на 4 процентных пункта.",
         "Support for conscripts' families consumes 10 reserve and diverts civilian goods for 90 days. After 35 days war support rises by 4 percentage points.", visible="has_war = yes", ai=2)
decision("A10D_emergency_shipping_levy", "Объявить чрезвычайный найм судов", "Charter Emergency Shipping", 60, 30, 180,
         "has_war = yes check_variable = { A10D_supply < 71 }",
         "add_stability = -0.02", "add_equipment_to_stockpile = { type = convoy_1 amount = 8 producer = A10 } add_to_variable = { A10D_supply = 20 } A10D_refresh_supply = yes",
         "Срочный наём частных судов вызовет недовольство торговцев: стабильность сразу снизится на 2 процентных пункта. Через месяц флот получит 8 транспортов, а резерв вырастет на 20.",
         "Emergency chartering of private vessels angers merchants, immediately reducing stability by 2 percentage points. After a month the fleet receives 8 convoys and the reserve rises by 20.", visible="has_war = yes", ai=3)
decision("A10D_restore_peacetime_routes", "Вернуть мирные расписания", "Restore Peacetime Timetables", 45, 45, 120,
         "has_war = no has_completed_focus = A10D_mail_ferries check_variable = { A10D_supply < 86 }", "",
         "add_to_variable = { A10D_supply = 15 } A10D_refresh_supply = yes add_stability = 0.01",
         "Вернём почтовые паромы к гражданским рейсам, проверим склады и отремонтируем лодки. Через 45 дней резерв вырастет на 15, стабильность — на 1 процентный пункт.",
         "Return mail ferries to civilian routes, inspect warehouses and repair the boats. After 45 days the reserve rises by 15 and stability by 1 percentage point.", visible="has_war = no has_completed_focus = A10D_mail_ferries", ai=2)
write("common/decisions/A10D_development.txt", "A10D_development = {\n" + "".join(DECISIONS) + "}")

EVENTS = []
def event(num, ru, en, ru_desc, en_desc, immediate, options, trigger="", picture="GFX_report_event_generic_parliament"):
    key = f"A10D_development.{num}"
    loc(key + ".t", ru, en)
    loc(key + ".d", ru_desc, en_desc)
    value = f"country_event = {{\n id = {key}\n title = {key}.t\n desc = {key}.d\n picture = {picture}\n is_triggered_only = yes\n"
    if trigger:
        value += f" trigger = {{ {trigger} }}\n"
    if immediate:
        value += f" immediate = {{ {immediate} }}\n"
    for letter, rname, ename, effect, req, chance in options:
        loc(key + "." + letter, rname, ename)
        value += f" option = {{ name = {key}.{letter} ai_chance = {{ factor = {chance} }} "
        if req:
            value += f"trigger = {{ {req} }} "
        value += effect + " }\n"
    EVENTS.append(value + "}\n")


event(1, "Сколько лодок между островами?", "How Many Boats Link the Islands?",
      "На стол съезда легли три несовпадающие ведомости судов. В одной считают только пароходы, в другой — лодки сборщиков пошлин, в третьей — всё, что когда-либо вышло из гавани. За каждой ошибкой стоят недоставленный мешок риса и гарнизон, напрасно ждущий патроны. Капитаны предлагают начать с оплаченной проверки рейсов.",
      "Three incompatible shipping registers lie before the congress. One counts only steamers, another the customs boats, the third everything that ever left a harbour. Behind each error is an undelivered sack of rice and a garrison waiting in vain for cartridges. The captains propose a paid inspection of the routes.", "",
      [("a", "Оплатить проверку рейсов", "Pay for a route inspection", "add_political_power = -25 add_to_variable = { A10D_supply = 8 } A10D_refresh_supply = yes", "has_political_power > 24", 70),
       ("b", "Пусть общины сверят списки", "Let the communities compare their lists", "add_political_power = 15 navy_experience = 3", "", 30)], trigger="tag = A10 has_capitulated = no")
event(2, "Тайфун над паромными линиями", "A Typhoon over the Ferry Routes",
      "Утренние донесения принесли вести о сорванных кровлях, затопленных рисовых складах и нескольких выброшенных на берег лодках. Самые важные пристани уцелели, но почтовые рейсы отменены. Провинциальные плотники просят прислать инструменты до следующего прилива.",
      "The morning dispatches report torn roofs, flooded rice stores and several boats driven ashore. The principal quays have survived, but mail sailings are suspended. Provincial carpenters ask for tools before the next tide.",
      "subtract_from_variable = { A10D_supply = 15 } A10D_refresh_supply = yes add_timed_idea = { idea = A10D_monsoon_damage days = 90 }",
      [("a", "Выделить средства плотникам", "Release funds to the carpenters", "add_political_power = -40 add_to_variable = { A10D_supply = 8 } A10D_refresh_supply = yes", "has_political_power > 39", 75),
       ("b", "Ввести временные рисовые пайки", "Introduce temporary rice rations", "add_stability = -0.02 add_to_variable = { A10D_supply = 4 } A10D_refresh_supply = yes", "", 25)], trigger="tag = A10 has_capitulated = no", picture="GFX_report_event_generic_construction_site")
event(3, "Ведомость трёх пристаней", "The Register of Three Quays",
      "Переписчики вернулись с неожиданным выводом: одни и те же лодки записаны на трёх разных пристанях, зато целые рыбацкие поселения отсутствуют в ведомостях. Теперь у съезда есть основа для расписаний и перечень общин, которым первой понадобится помощь при шторме.",
      "The enumerators have returned with an unexpected finding: the same boats appear in three different harbour registers, while entire fishing villages appear nowhere. The congress now has the foundation of a timetable and a list of communities that will need help first when storms arrive.", "",
      [("a", "Начать с рисовых складов", "Begin with the rice stores", "add_to_variable = { A10D_supply = 5 } A10D_refresh_supply = yes", "", 60),
       ("b", "Обнародовать полную ведомость", "Publish the full register", "add_stability = 0.02 add_political_power = 10", "", 40)], trigger="tag = A10 has_capitulated = no")
event(4, "Санитар с соседнего острова", "An Orderly from the Next Island",
      "Первая лечебница прислала благодарность паромной команде: санитар успел к началу лихорадки, а не после похорон. В небольших палатах ещё не хватает коек, но лекари уже договариваются о курсах для добровольцев и единых карантинных свидетельствах.",
      "The first district clinic has sent its thanks to a ferry crew: its orderly arrived at the beginning of the fever, rather than after the funeral. The little wards still lack beds, but the physicians are already discussing volunteer courses and common quarantine certificates.", "",
      [("a", "Поддержать добровольные курсы", "Support the volunteer courses", "add_political_power = -25 add_timed_idea = { idea = A10D_volunteer_orderlies days = 120 }", "has_political_power > 24", 65),
       ("b", "Сначала обеспечить чистую воду", "Provide clean water first", "add_stability = 0.02", "", 35)], trigger="tag = A10 has_capitulated = no", picture="GFX_report_event_generic_construction_site")
event(5, "Капитаны просят письменный договор", "The Captains Ask for Written Terms",
      "Список судов резерва готов. Капитаны согласны перевозить солдат и припасы, но напоминают: на тех же судах острова получают рис. Они просят заранее определить вознаграждение и оставить часть расписания гражданским рейсам.",
      "The reserve shipping register is complete. The captains agree to carry soldiers and stores, but remind the government that the same vessels carry the islands' rice. They ask for agreed compensation and a share of the timetable reserved for civilian sailings.", "",
      [("a", "Закрепить гражданские рейсы в договоре", "Protect civilian sailings in the contract", "add_to_variable = { A10D_supply = 8 } A10D_refresh_supply = yes add_stability = 0.01", "", 75),
       ("b", "Оплатить дополнительные учебные рейсы", "Pay for additional training voyages", "add_political_power = -35 navy_experience = 15", "has_political_power > 34", 25)], trigger="tag = A10 has_capitulated = no")
event(6, "Первый общий торговый сезон", "The First Common Trading Season",
      "Сахар и абака дошли до покупателей без прежних недельных задержек. В портовых лавках появились инструменты из соседних провинций, а школьные тетради привезли тем же рейсом, что и запасные части для мельницы. Местные газеты впервые пишут об общем хозяйстве островов как о повседневном деле.",
      "Sugar and abaca have reached their buyers without the old week-long delays. Harbour shops stock tools made in neighbouring provinces, while school copybooks arrived on the same sailing as spare parts for the mill. For the first time, local newspapers describe a common island economy as an everyday reality.", "",
      [("a", "Укрепить общественные запасы", "Strengthen the public reserves", "add_to_variable = { A10D_supply = 10 } A10D_refresh_supply = yes add_stability = 0.02", "", 70),
       ("b", "Оплатить новые производственные заказы", "Finance new workshop orders", "add_political_power = 50 add_timed_idea = { idea = A10D_tools_programme days = 180 }", "", 30)], trigger="tag = A10 has_capitulated = no")
write("events/A10D_development.txt", "add_namespace = A10D_development\n\n" + "\n".join(EVENTS))

loc("A10D_rifle_studies", "Полковые оружейные ведомости", "Regimental Rifle Registers")
loc("A10D_light_vessels", "Опыт канонерских команд", "Gunboat Crew Experience")
for language, values in LOCS.items():
    lines = [f"l_{language}:"]
    for key, value in values.items():
        lines.append(f' {key}:0 "{value.replace(chr(34), chr(39))}"')
    write(f"localisation/{language}/A10D_development_l_{language}.yml", "\n".join(lines), bom=True)

write("docs/PHILIPPINES_DEVELOPMENT.md", '''
# Общая проработка Филиппин: хозяйство, снабжение и оборона

28 фокусов: 14 хозяйственных и 14 армейских/морских. Данные для основного дерева хранятся в `tools/a10d_focuses.json`; генератор `tools/A10D_build_development.py` изменяет только собственные файлы. Их русские и английские названия/описания находятся в JSON для единой интеграции корневым генератором дерева. Тексты остальных систем находятся в двух локализациях A10D с UTF-8 BOM.

## Начало и общий цикл

`A10D_initialize = yes` однократно вызывается из общей инициализации A10R. Начальный резерв перевозок A10D_supply = 35. Начальные проблемы: разрозненные мастерские, несовместимое полковое снабжение, перегруженные паромные линии. Общая хозяйственная и военная ветви открываются только после выбора политического пути: договора республик, присяги ВТП либо военного переворота. Один островной съезд их не открывает. Оба входа имеют одну OR-группу требований A10_confederation/A10W_oath/A10M_coup; все 28 фокусов смещены на три ряда вниз, с первого ряда y=4 до завершающего y=19.

Резерв 0–100 отражает лодки, экипажи, сухие склады и рис, не государственный долг. Ниже 20: +10% расхода припасов, −5% выпуска военных заводов, −5 п.п. стабильности; 20–49: +5% расхода припасов, −2 п.п. стабильности; 50–79: без дополнительного духа; 80–100: −3% морского расхода припасов, +3 п.п. стабильности. Эффект обновляется сразу после каждого изменения и ограничивает значение диапазоном. Ежемесячного списания нет; долговая книга WTC не изменяется.

11 решений с оплатой, сроками и повторными интервалами: найм лодок; закупка риса; восстановление после тайфуна; экспортный канатный контракт; закупка инструментов; вечернее обучение; гарнизонные учения с расходом винтовок; подготовка санитаров; помощь семьям солдат; чрезвычайный найм транспортов; возврат мирных расписаний. Даже при истощении резерва доступны рис и лодки, а после войны — мирное восстановление. Учебные и хозяйственные усиления временные; повторные решения не выдают заводов, исследовательских ячеек или постоянных боевых духов.

Шесть событий: проверка судовых ведомостей; один тайфун через 240–285 дней (последствия на 90 дней, можно ускорить ремонт); результаты переписи; открытие лечебниц; договор с капитанами; первый общий торговый сезон. Платные варианты скрыты при нехватке политической власти, бесплатная развилка всегда остаётся. Не используются современные самолёты, танки, грузовые автопарки или бесплатные броненосцы.

## Хозяйственные награды

Три гражданские фабрики, два военных завода, две верфи распределены по семи отдельным 70-дневным фокусам. Дополнительная исследовательская ячейка одна, в политехникуме после учительских и кабельных программ. Все промышленные награды проверяют местные территории, владение и контроль A10 либо её филиппинского субъекта. Выпуск республик из конфедерации не отключает общие проекты. Независимые иностранные владельцы, японская оккупация и субъекты чужих держав исключены. Если предпочтительная область недоступна, выбирается подходящая контролируемая область архипелага; верфи требуют побережья. Береговые укрепления и база создаются только в проверенных Кавите и Себу, с корректными провинциями 1221 и 12118.

## Вооружение и общая подготовка

Сохранены идентификаторы A10_coastal_arsenals и A10_landing_plans. Арсеналы дают 1500 винтовок и завод; полный общий путь добавляет ограниченные партии винтовок, 48 старых полевых орудий, 12 старых гаубиц и 250 единиц вспомогательного оснащения. Используются реально существующие infantry_equipment_0, field_gun_equipment_0, howitzer_equipment_0, support_equipment_1 и convoy_1. Технологии: early_artillery, tech_support, tech_engineers, early_machine_tools. Морская школа открывает старые торпедные катера/канонерки с Man the Guns или early_destroyer без него. Планы высадок открывают mtg_transport либо transport соответственно.

Политическая готовность и решение об объявлении японской войны принадлежат основному дереву. Завершение общих планов само по себе не начинает войну. Высадки по-прежнему требуют транспортов и реального морского обеспечения.

## Проверка

`tools/A10D_validate_development.py` проверяет схему 28 фокусов, уникальность идентификаторов/координат, связи, доступность всех общих фокусов после каждого политического выбора и их блокировку до него, баланс скобок и строк, локализацию, наличие технологий/снаряжения/иконок, диапазон резерва, пороги, повторное восстановление, охрану владельцев территорий и отсутствие изменения долговой книги. Проверка движком и кампания в HOI4 остаются необходимы для окончательного морского баланса.
''')

print(f"Built {len(FOCUSES)} focuses, {len(IDEAS)} ideas, {len(DECISIONS)} decisions, {len(EVENTS)} events.")
