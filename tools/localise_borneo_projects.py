from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
ru={
'A01_build_bornean_fortifications':('Инспекция укреплений','Проверка береговых позиций укрепит доверие к правительству. Стабильность +5%. После инспекции выберем государственное строительство или проект внешних специалистов.'),
'A01_state_loan':('Государственный заём','Заём у ВТП увеличит долговые обязательства на 20 пунктов. Прирост политической власти снизится на 10%. Средства позволят начать собственное строительство.'),
'A01_own_fortifications':('Собственные укрепления','Собственная программа даёт +20% защиты против Японии. На стройку направляются дополнительные 5% потребительских фабрик; выплаты требуют 0,10 политической власти в день. Британия теряет 10 пунктов отношения к нам. Будет построена железная дорога между портами Сабаха.'),
'A01_request_fortification_project':('Запросить проект','Правительство рассмотрит британское и австралийское предложения, а также план индонезийских общин. Выбрать можно только один проект. Бонус защиты начнёт действовать после реализации.'),
'A01_implement_fortification_project':('Реализация проекта','Выполним выбранный план и свяжем порты Сабаха железной дорогой. Защита против Японии: британский проект +15%, австралийский +10%, местный +5%.'),
'A01_improve_bornean_fortifications':('Борнейский оборонительный пояс','После собственного строительства или реализации выбранного проекта завершим оборону Джесселтона, Сандакана и Тавау: береговые форты уровня 2 и сухопутные уровня 1. Более сильные укрепления сохраняются. Работы требуют принадлежности Сабаха и контроля соответствующего порта.'),
'A01_borneo_state_loan':('Заём ВТП на оборону','Заём увеличил долговую нагрузку ВТП на 20 пунктов. Обслуживание обязательств снижает прирост политической власти на 10%.\nТекущий долг: [?A01_wtc_debt|0] пунктов.'),
'A01_borneo_self_build':('Государственная программа укреплений','Собственные укрепления повышают защиту против Японии на 20%. Строительство и долг отвлекают фабрики и политические ресурсы. Военный бонус снимается после окончания кампании, выплаты сохраняются.'),
'A01_borneo_debt_service':('Обслуживание оборонного займа','После окончания войны сохраняются выплаты по займу и обязательства перед подрядчиками.'),
'A01_borneo_british_commitments':('Британская инженерная миссия','Британское влияние выросло на 15 пунктов, потеря суверенитета — на 10. Согласование с иностранными советниками снижает прирост политической власти на 10%.\nВлияние Британии: [?A01_british_influence|0]. Потеря суверенитета: [?A01_sovereignty_loss|0].'),
'A01_borneo_british_defence':('Британский проект обороны','Современные бетонные позиции дают +15% защиты против Японии до окончания кампании.'),
'A01_borneo_australian_commitments':('Гарантии по Новой Гвинее','Австралийское участие улучшает отношения на 10 пунктов. Мы обязуемся не укреплять направленный против Австралии рубеж: соответствующий фокус недоступен.'),
'A01_borneo_australian_defence':('Австралийский проект обороны','Материалы и специалисты Австралии дают +10% защиты против Японии до окончания кампании.'),
'A01_borneo_local_commitments':('Сотрудничество с индонезийскими общинами','Общины обеспечивают +15% рекрутируемого населения. Расовый раскол смягчён на 10 пунктов стабильности, но уважение адмиралов к губернатору снижено на 5 пунктов.'),
'A01_borneo_local_defence':('Местная система обороны','Земляные позиции, препятствия и скрытые тропы дают +5% защиты против Японии до окончания кампании.'),
}
en={
'A01_build_bornean_fortifications':('Inspect the Fortifications','Inspect coastal positions and gain 5% stability. Choose state construction or an outside project.'),
'A01_state_loan':('State Loan','Increase WTC debt by 20 points and reduce political power gain by 10%. Unlock domestic construction.'),
'A01_own_fortifications':('Our Own Fortifications','Gain 20% defence against Japan. Commit an additional 5% of factories to consumer goods and pay 0.10 political power daily. British opinion falls by 10 points. Build the Sabah port railway.'),
'A01_request_fortification_project':('Request a Project','Choose one British, Australian or Indonesian community proposal. Its defence bonus begins upon implementation.'),
'A01_implement_fortification_project':('Implement the Project','Complete the selected project and Sabah port railway. Defence against Japan: British 15%, Australian 10%, local 5%.'),
'A01_improve_bornean_fortifications':('Bornean Defensive Belt','After domestic construction or project implementation, raise coastal forts to level 2 and land forts to level 1 in Jesselton, Sandakan and Tawau. Stronger forts are preserved. Works require ownership of Sabah and control of each port.'),
'A01_borneo_state_loan':('WTC Defence Loan','WTC debt increased by 20 points. Political power gain falls by 10%.\nCurrent debt: [?A01_wtc_debt|0] points.'),
'A01_borneo_self_build':('State Fortification Program','Gain 20% defence against Japan. Construction and debt consume civilian and political resources. Defence expires after the campaign; debt commitments remain.'),
'A01_borneo_debt_service':('Defence Debt Service','Loan repayments and contractor obligations continue after the war.'),
'A01_borneo_british_commitments':('British Engineering Mission','British influence rises by 15 points and sovereignty loss by 10. Foreign supervision reduces political power gain by 10%.\nBritish influence: [?A01_british_influence|0]. Sovereignty loss: [?A01_sovereignty_loss|0].'),
'A01_borneo_british_defence':('British Defence Project','Concrete positions grant 15% defence against Japan until the campaign ends.'),
'A01_borneo_australian_commitments':('New Guinea Guarantees','Australian opinion improves by 10 points. Our commitment prevents taking the focus to fortify the Australian frontier.'),
'A01_borneo_australian_defence':('Australian Defence Project','Australian materials and specialists grant 10% defence against Japan until the campaign ends.'),
'A01_borneo_local_commitments':('Indonesian Community Cooperation','Gain 15% recruitable population factor. Racial tensions improve by 10 stability points, but admiral respect falls by 5 points.'),
'A01_borneo_local_defence':('Local Defence Network','Earthworks, obstacles and hidden paths grant 5% defence against Japan until the campaign ends.'),
}
extra_ru={
'borneo_project.1.t':'Три проекта обороны Борнео',
'borneo_project.1.d':'Инспекция выявила слабость береговых позиций. Британия предлагает бетон и инженеров; Австралия — материалы и специалистов в обмен на гарантии по Новой Гвинее. Индонезийские общины готовы строить земляные валы, препятствия и скрытые тропы. Каждый проект имеет свою цену. Защитный бонус появится после завершения фокуса «Реализация проекта».',
'borneo_project.1.a':'Британские инженеры и бетон.',
'borneo_project.1.b':'Австралийские материалы и специалисты.',
'borneo_project.1.c':'Довериться местным общинам.',
'A01_wtc_debt_20_tt':'Долг перед ВТП увеличится на §R20 пунктов§! по шкале процентов долговой нагрузки.',
'A01_own_fortifications_tt':'Защита против Японии: §G+20%§!. Британия: §R−10§! отношения. Долговые обязательства сохраняются после войны.',
'A01_project_selected_tt':'Выбран один из трёх проектов обороны.',
'A01_project_implementation_tt':'Будет введён в действие бонус защиты выбранного проекта против Японии.',
'A01_british_project_tt':'Потеря суверенитета: §R+10§! пунктов. Влияние Британии: §R+15§! пунктов. После реализации: §G+15%§! защиты против Японии.',
'A01_australian_project_tt':'Австралия: §G+10§! отношения. Принимаются гарантии по Новой Гвинее; «Укрепить австралийский рубеж» станет недоступен. После реализации: §G+10%§! защиты против Японии.',
'A01_local_project_tt':'Рекрутируемое население: §G+15%§!. Стабильность расового раскола: §G+10%§!. Уважение адмиралов: §R−5§! пунктов. После реализации: §G+5%§! защиты против Японии.',
'A01_no_australian_guarantees_tt':'Нет обязательства перед Австралией не укреплять рубеж Новой Гвинеи.',
'A01_borneo_british_exclusion':'Британия исключена из оборонного проекта',
'A01_borneo_australian_cooperation':'Совместный оборонный проект',
}
extra_en={
'borneo_project.1.t':'Three Projects for Borneo',
'borneo_project.1.d':'Inspectors report weak coastal positions. Britain offers concrete and engineers; Australia offers materials and specialists in exchange for New Guinea guarantees. Indonesian communities propose earthworks, obstacles and hidden paths. The defence bonus begins only after project implementation.',
'borneo_project.1.a':'British engineers and concrete.',
'borneo_project.1.b':'Australian materials and specialists.',
'borneo_project.1.c':'Trust the local communities.',
'A01_wtc_debt_20_tt':'WTC debt increases by §R20 percentage points§!.',
'A01_own_fortifications_tt':'Defence against Japan: §G+20%§!. British opinion: §R−10§!. Debt commitments survive the war.',
'A01_project_selected_tt':'One of the three defence projects has been selected.',
'A01_project_implementation_tt':'Activate the selected project’s defence bonus against Japan.',
'A01_british_project_tt':'Sovereignty loss: §R+10§! points. British influence: §R+15§! points. After implementation: §G+15%§! defence against Japan.',
'A01_australian_project_tt':'Australian opinion: §G+10§!. New Guinea guarantees block the Australian frontier fortification focus. After implementation: §G+10%§! defence against Japan.',
'A01_local_project_tt':'Recruitable population factor: §G+15%§!. Racial stability: §G+10%§!. Admiral respect: §R−5§! points. After implementation: §G+5%§! defence against Japan.',
'A01_no_australian_guarantees_tt':'No commitment to Australia prohibiting New Guinea frontier fortifications.',
'A01_borneo_british_exclusion':'Britain Excluded from the Defence Project',
'A01_borneo_australian_cooperation':'Joint Defence Project',
}
for lang,entries,extra in [('russian',ru,extra_ru),('english',en,extra_en)]:
 labels=dict(extra)
 for key,(name,desc) in entries.items():labels[key]=name;labels[key+'_desc']=desc.replace('\n','\\n')
 remaining=dict(labels)
 for p in (R/'localisation'/lang).glob('*.yml'):
  t=p.read_text(encoding='utf-8-sig');changed=False
  for key,label in labels.items():
   t,n=re.subn(r'^\s*'+re.escape(key)+r':\d* .*$',lambda m:f' {key}:0 "{label}"',t,flags=re.M)
   if n:changed=True;remaining.pop(key,None)
  if changed:p.write_text(t,encoding='utf-8-sig')
 p=R/f'localisation/{lang}/pacific_content_l_{lang}.yml'
 p.write_text(p.read_text(encoding='utf-8-sig')+'\n'+''.join(f' {k}:0 "{v}"\n' for k,v in remaining.items()),encoding='utf-8-sig')
