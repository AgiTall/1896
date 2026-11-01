from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
updates={
'JPI_electrical_bureau':('Бюро Теслы','Tesla Bureau'),
'JPI_electrical_bureau_desc':('Сосредоточить электротехническую программу в едином бюро. Даёт 50% бонус к одному промышленному исследованию. Исключает мастерские флота; после любого из этих путей можно выбрать переносные башни или корабельные генераторы.','Centralise electrical development in one bureau. Grants a 50% bonus to one industrial research. Excludes fleet workshops. Either organisation can develop portable towers or shipboard generators.'),
'JPI_portable_prototype':('Переносные башни','Portable Towers'),
'JPI_portable_prototype_desc':('За 25 политической власти разработать переносной образец башни Теслы. Исключает корабельные генераторы и открывает береговые испытания. Итоговая система усиливает флот в бою и даёт 20 транспортов.','Spend 25 political power developing portable Tesla towers. Excludes shipboard generators and unlocks coastal trials. The completed system improves fleet combat performance and provides 20 convoys.'),
'JPI_quiet_coast':('Испытать башни на берегу','Coastal Tower Trials'),
'JPI_quiet_coast_desc':('Завершить программу переносных башен: боевой дух электротехнического флота, 20 транспортов и техническая готовность к Южному рывку. Это завершение выбранного пути, без отдельного фокуса на бюрократическое утверждение.','Complete the portable tower programme: the existing electrical fleet combat spirit, 20 convoys and technical readiness for the Southern Push.'),
'JPI_coastal_trials':('Морские испытания генераторов','Generator Sea Trials'),
'JPI_coastal_trials_desc':('Завершить корабельную энергетическую программу: −8% морского расхода снабжения, +10% скорости подготовки вторжений, 15 морского опыта и 10 транспортов. Даёт техническую готовность к Южному рывку. Переносные башни этим путём недоступны.','Complete shipboard power: 8% less naval supply consumption, 10% faster invasion preparation, 15 naval experience and 10 convoys. Provides technical readiness for the Southern Push. This route does not grant portable towers.'),
'JPI_scarlet_sails_desc':('Свести выбранные промышленные, корабельные и энергетические решения в единую доктрину. Доступно после береговых испытаний башен или морских испытаний генераторов. Награды зависят от выбранных ресурсов и типа верфей.','Combine the selected industrial, shipbuilding and electrical policies into one doctrine. Requires either tower trials or generator sea trials. Rewards depend on the resource and yard choices.'),
'JPI_closed_ports_desc':('Выбрать собственную промышленную базу: военный завод, бонус к промышленному исследованию и открытие выбора между углём Кюсю и нефтяной программой. Учёт сырья включён в этот фокус.','Choose domestic industry: a military factory, an industrial research bonus and access to the Kyushu coal or oil programme choice. Resource accounting is included in this focus.'),
'JPI_japanese_terms_desc':('Закупать машины на японских условиях: доступ к внешним контрактам, местные вольфрам и хром, затем выбор между посредническими закупками и копированием образцов. Подготовка контрактов включена в этот фокус.','Acquire machinery on Japanese terms: external contracts, local tungsten and chromium, then choose proxy purchases or copied samples. Contract preparation is included in this focus.'),
'JPL_medical_rotation_desc':('Направить ресурсы на госпитальные суда и ротацию гарнизона. Снижает усталость, укрепляет стабильность и даёт опыт, но требует политических расходов. Исключает полевые ремонтные мастерские; оба варианта открывают профессиональную логистику.','Fund hospital ships and garrison rotations. Reduces fatigue, improves stability and grants experience at a political cost. Excludes forward repair workshops; either choice unlocks professional logistics.'),
}
new={
'JPI_fleet_workshops':('Мастерские флота','Fleet Workshops'),
'JPI_fleet_workshops_desc':('Передать разработку электрических систем мастерским флота. Даёт 15 морского опыта и +5% скорости строительства верфей, но увеличивает долговое давление на 5. Исключает единое бюро Теслы; обе организации могут выбрать любой энергетический путь.','Delegate electrical development to fleet workshops. Grants 15 naval experience and 5% dockyard construction speed, but adds 5 debt pressure. Excludes the central Tesla bureau; either organisation can choose either power programme.'),
'JPI_ship_generators':('Корабельные генераторы','Shipboard Generators'),
'JPI_ship_generators_desc':('За 15 политической власти разработать корабельную энергетическую установку и получить 5000 топлива. Исключает переносные башни. Морские испытания дадут экономию снабжения и ускорят подготовку высадок.','Spend 15 political power developing shipboard generators and receive 5,000 fuel. Excludes portable towers. Sea trials will reduce supply consumption and speed invasion preparation.'),
'JPI_workshop_network':('Сеть флотских мастерских','Fleet Workshop Network'),
'JPI_workshop_network_desc':('Распределённые мастерские ускоряют строительство верфей на 5%. Разработка оплачена дополнительными долговыми обязательствами.','Distributed workshops improve dockyard construction speed by 5%. Development was funded through additional debt obligations.'),
'JPI_shipboard_power':('Корабельная электрическая сеть','Shipboard Electrical Network'),
'JPI_shipboard_power_desc':('Генераторы уменьшают морской расход снабжения на 8% и ускоряют подготовку морских вторжений на 10%.','Generators reduce naval supply consumption by 8% and speed naval invasion preparation by 10%.'),
'JPL_forward_workshops':('Полевые ремонтные мастерские','Forward Repair Workshops'),
'JPL_forward_workshops_desc':('Сделать ставку на ремонт и оружейные запасы: 500 винтовок и постоянное снижение расхода снабжения на 5%. Цена — +5 долгового давления и +5 усталости гарнизона, которому придётся отложить ротацию. Исключает медицинскую ротацию.','Prioritise repairs and reserves: 500 rifles and a permanent 5% reduction in supply consumption. Costs 5 debt pressure and 5 garrison fatigue as rotations are postponed. Excludes medical rotation.'),
'JPL_repair_network':('Фронтовая ремонтная сеть','Frontline Repair Network'),
'JPL_repair_network_desc':('Полевой ремонт снижает расход снабжения армии на 5%.','Forward repairs reduce army supply consumption by 5%.'),
}
for i,lang in enumerate(['russian','english']):
 todo=set(updates)
 for p in (R/f'localisation/{lang}').glob('*.yml'):
  s=p.read_text(encoding='utf-8-sig');old=s
  for k in list(todo):
   s,n=re.subn(r'(?m)^\s*'+re.escape(k)+r':\d+\s*".*"\s*$',lambda m:' '+k+':0 "'+updates[k][i]+'"',s)
   if n:todo.remove(k)
  if old!=s:p.write_text(s,encoding='utf-8-sig')
 assert not todo,todo
 (R/f'localisation/{lang}/JPI_compact_choices_l_{lang}.yml').write_text('l_'+lang+':\n'+'\n'.join(' '+k+':0 "'+v[i]+'"' for k,v in new.items())+'\n',encoding='utf-8-sig')
print('Compact choices RU/EN updated')
