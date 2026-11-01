"""Final integration hooks, historical AI priorities and authored canon notes."""
from extend_japan_story import read,write,edit_focus,R
import json,re
def main():
 # These are engine triggers, not the similarly named dynamic variables.
 for folder in ['common/decisions','events']:
  for p in (R/folder).glob('*.txt'):
   if p.name.startswith(('JPF','JPN','JPL','WTC')):
    s=read(p.relative_to(R));s=re.sub(r'\bpolitical_power\s*>','has_political_power >',s);s=re.sub(r'\bmanpower\s*>','has_manpower >',s);write(p.relative_to(R),s)
 p='common/scripted_effects/JPF_finance.txt';s=read(p)
 if 'JPF_defeat_restructuring_effect = {' not in s:s+='''
JPF_defeat_restructuring_effect = {
 if = { limit = { has_country_flag = A03_borneo_defeat NOT = { has_country_flag = JPF_defeat_restructured } }
  set_country_flag = JPF_defeat_restructured
  add_to_variable = { JPF_debt_pressure = -20 }
  add_to_variable = { JPF_budget_confidence = 5 }
  add_stability = -0.04
  add_timed_idea = { idea = JPF_civilian_retrenchment days = 180 }
  JPF_refresh_effect = yes
 }
}
'''
 s=s.replace('remove_ideas = JPF_treasury_ledger','remove_ideas = JPC_bad_loans remove_ideas = JPC_guarantees\n remove_ideas = JPF_treasury_ledger') if 'remove_ideas = JPC_bad_loans remove_ideas = JPC_guarantees' not in s else s
 write(p,s)
 p='common/decisions/JPF_finance.txt';s=read(p).replace('has_country_flag = JPF_guarantee_settled has_idea = JPC_monopoly','OR = { AND = { has_country_flag = JPF_guarantee_settled has_idea = JPC_monopoly } has_country_flag = JPF_defeat_restructured }');write(p,s)
 p='common/national_focus/a03_focus.txt';s=read(p);s=edit_focus(s,'JPC_defeat_inquest','JPF_defeat_restructuring_effect = yes')
 s=s.replace('completion_reward = { JPF_reform_accounts_effect = yes add_political_power = 60','completion_reward = { JPF_audit_savings_effect = yes add_political_power = 60')
 write(p,s)
 p='common/ideas/JPC_canonical.txt';s=read(p).replace('cancel = { NOT = { has_war_with = A01 } } modifier = { navy_org_factor = -0.08','cancel = { OR = { NOT = { has_war_with = A01 } NOT = { has_war_with = A10 } } } modifier = { navy_org_factor = -0.08');write(p,s)
 p='common/decisions/WTC_credit.txt';s=read(p)
 # AI does not draw credit while at peace or while it has sufficient transport reserves.
 a=s.index('WTC_borrow =');b=s.index('\nWTC_repay =');part=s[a:b].replace('ai_will_do = { base = 1 }','ai_will_do = { base = 1 modifier = { factor = 0 has_war = no } modifier = { factor = 0 has_equipment = { convoy_1 > 39 } } modifier = { factor = 0 check_variable = { WTC_debt > 59 } } }');s=s[:a]+part+s[b:];write(p,s)
 p='events/WTC_credit.txt';s=read(p)
 for num in [1,2,3]:
  a=s.index(f'country_event = {{ id = wtc_credit.{num} ');b=s.find('\ncountry_event =',a+1);b=len(s) if b<0 else b
  part=s[a:b].replace('trigger = { country_exists = A04','trigger = { NOT = { has_war_with = A04 } country_exists = A04',1).replace('trigger = { check_variable = { WTC_debt > 90 } country_exists = A04','trigger = { NOT = { has_war_with = A04 } check_variable = { WTC_debt > 90 } country_exists = A04',1)
  s=s[:a]+part+s[b:]
 write(p,s)
 p='common/ai_strategy_plans/A01_canonical.txt';s=read(p);pos=s.index('A03_southern_canonical_plan = {')
 order=['A03_imperial_council','JPC_state_guarantees','JPC_osaka_orders','JPC_iwasaki_accounts','JPF_bond_register','JPF_public_accounts','JPC_northern_protocol','JPC_honshu_depots','JPC_manila_priority','JPC_garrison_accounts','JPC_batavia_demands','JPC_one_war_cabinet','JPN_north_supply_register','JPN_north_civilian_holds','JPN_north_emergency_calendar','JPC_pledged_yards','JPC_borneo_bridgehead','JPL_port_and_mountains','JPL_convoy_timetable','JPL_names_and_units','JPF_delivery_calendar','JPC_convoy_budget','JPC_casualty_returns','JPC_hospital_ships','JPL_medical_rotation','JPL_municipal_buyers','JPL_supply_board','JPL_payroll_inquiry','JPL_quartermaster_school','JPN_north_inspection_channel','JPN_north_tokyo_auditors','JPN_north_admiralty_hearing','JPC_regional_dispatches','JPC_wtc_mission','JPC_honolulu_letters','JPC_australian_assurances','JPC_nz_watch','JPF_coal_not_glory','JPF_excise_bargain','JPC_war_workshops','JPC_no_short_war','JPC_replace_losses','JPC_imperial_inspection','JPC_sulu_escorts','JPL_limited_mandate','JPN_north_imperial_arbitration','JPC_1895_accounts','JPC_hold_until_talks','JPC_count_the_cost','JPC_oil_promise','JPF_royalty_register','JPC_defeat_inquest','JPF_return_small_savings','JPC_rebuild_ports','JPC_partial_demobilisation','JPC_three_heads_again','JPN_north_postwar_audience','JPN_north_permanent_protocol','JPN_north_keep_distance','JPF_civil_budget','JPL_borneo_is_not_luzon']
 write(p,s[:pos]+'A03_southern_canonical_plan = { name = "Three Heads: the Canonical Campaign" desc = "Oil guarantees, audited accounts, northern supply and the cost of Manila." allowed = { original_tag = A03 } enable = { always = yes } ai_national_focuses = { '+' '.join(order)+' } }\n')
 # Preserve generated focus text while adding the outcome-specific financial remedy.
 L={
 'JPC_defeat_inquest_desc':['Разобрать причины поражения и признать невозможность расплатиться борнейской нефтью. Реструктуризация уменьшит долговое давление на 20, доверие вырастет на 5, но стабильность упадёт на 4%, а гражданские заказы сократятся на 180 дней. После мира и выплат станет возможно закрыть чрезвычайную книгу.','Investigate defeat and admit that Borneo oil cannot pay the debt. Restructuring cuts pressure by 20 and raises confidence by 5, at a 4% stability loss and 180 days of civilian retrenchment. Peace and repayment can then close the emergency ledger.'],
 'JPF_close_ledger_desc':['Закрыть внутренний финансовый кризис после всех войн и выплаты чрезвычайного кредита ВТП: давление ниже 20, доверие от 65. Требуется нефтяной расчёт при победе либо реструктуризация после поражения.','Close the domestic crisis after all wars and repayment of emergency Chamber credit: pressure below 20, confidence at 65. Requires oil settlement after victory or restructuring after defeat.']}
 for lang,i in [('russian',0),('english',1)]:write(f'localisation/{lang}/zzzzzzzz_JPS_integration_l_{lang}.yml','l_'+lang+':\n'+'\n'.join(f' {k}:0 "{v[i]}"' for k,v in L.items())+'\n',True)
 write('docs/WTC_CANON.md','''# Всемирная торговая палата: канон и игровая система

## Текст для сюжетного промпта

ВТП (Всемирная Торговая Палата) — Мадейра. Директор Ламберт (личность неизвестна). Теневое мировое правительство, контролирующее кредиты, страховку, связь. Рычаги: долговая удавка, монополия на страхование, чёрный список, контроль кабелей. Слабости: зависимость от британского флота и разведки, отсутствие армии, страх перед возвращением на континент. Внутренние фракции: «Старая гвардия» (банкиры), «Молодые технократы» (союз с Теслой), «Тайный департамент» (разведка и ликвидация).

Ламберт — общая подпись закрытого директората; не установлено, подписывает ли её один человек, преемники или совет. Не раскрывать эту загадку авторским всеведением. Старая гвардия защищает страховую монополию «Серебряный Конвой». Технократы готовы оплачивать исследования Теслы, опасаясь, что независимая энергия разрушит кредитный порядок. Тайный департамент ведёт разведку, операции ликвидации и тайные договоры с пиратами. Стражи Проливов — наёмная охрана, а не регулярная армия. Палата не способна непосредственно управлять территориями: ей нужны местные кабинеты, концессии и британское морское прикрытие. Возвращение на континент вне её кредитной сети — экзистенциальная угроза.

## Долговая книга

Каждая существующая страна, кроме самой A04, получает собственную переменную WTC_debt (0–100), видимую в решениях. Начальные значения — балансировочные допущения: Нидерланды 35, Британия 55, Япония 30, Австралия 15, Осака 65, Конфедерация Филиппин 20, остальные 10. Внутренние обязательства Мицубиси JPF_debt_pressure считаются отдельно.

При ненулевом долге обслуживание стоит 2 политической власти ежемесячно. Война при долге от 30 добавляет 1 в месяц; действующий шестимесячный кредит — ещё 1. Мир сам по себе не списывает основной долг. Долг выше 70 вызывает требования обеспечения с полугодовым интервалом. Выше 90 задерживаются кабельные сообщения; при британском прикрытии действует чёрный список. При 100 через семь дней наступает долговой переворот: местный кабинет сменяется долговой администрацией, долг реструктурируется до 70. Можно избежать переворота чрезвычайной выплатой 200 политической власти и потерей стабильности. Прямой аннексии Палатой нет: это противоречило бы её ограничениям.

Без британского прикрытия чёрный список снимается, а попытка переворота проваливается с реструктуризацией до 90. Прикрытие потеряно, если Британии нет, она капитулировала или воюет с ВТП. Во время прямой войны должника с ВТП её кредитное принуждение приостанавливается.

Снизить долг можно выплатой (75 политической власти за −12), уступкой портовых сборов (−15 сразу, ещё −1 ежемесячно восемь месяцев, штрафы к гражданским ресурсам и строительству) и военной услугой Британии (10 транспортов и 500 винтовок за −12, только во время британской войны). Долговую администрацию можно выкупить после войны при долге не выше 20; прежний политический строй автоматически не возвращается.

## Рычаги и директорат

Морской кредит даёт 25 транспортов за +20 долга. Страхование улучшает сопровождение ценой гражданских ресурсов; кабельный приоритет даёт связь и координацию за +3 долга. ВТП выбирает приоритет групп: влияние поддержанной +10, остальных −5. Приоритет банкиров удорожает новые страховые договоры на 3 долга; технократы добавляют лабораторный контракт; тайный департамент открывает пиратские коридоры с потерей репутации. Это договорные бонусы, а не неуязвимость конвоев. Ликвидации и поиск континента пока заданы каноном, отдельной системы убийств или экспедиций здесь нет.

## Голландские входы

На уровне «Пути одинокого волка» слева стоит «Объединение европейской демократии», справа — «Усиление Всемирной торговой палаты». Три фокуса взаимоисключающие. Первый посылает Британии проект будущего объединения; Британия может принять делегацию или ограничиться перепиской. Второй поддерживает демократию торговых советов, даёт страхование и связь за новый долг. Реализованы начальные фокусы и первые события; последующие альтернативные деревья ещё не написаны. Исторический ИИ выбирает прежний канонический путь. Майский японский ультиматум не отменяется.

## Проверки

validate_story_systems.py исполняет реальные эффекты порогов 70/71, 90/91, 100, переворота и провала без Британии, займов и выплат. Это ограниченная модель скриптов: экономический баланс, дипломатический ИИ и полный игровой прогон требуют движка.
''')
 p='docs/WORLD_CANON.md';s=read(p);needle='**Противоречия:** Зависимость от британского флота и разведки. Конкуренция с голландцами и японцами. Растущее влияние биокорпораций.'
 replacement=needle+'\n**Рычаги:** долг 0–100, страховая монополия «Серебряный Конвой», подводные кабели, чёрный список, тайные пиратские договоры. Выше 70 — концессии, выше 90 — санкции, при 100 — местный долговой переворот.\n**Ограничения:** нет регулярной армии; Стражи Проливов — наёмники. Нет прямого территориального управления. Без британского флота и разведки морское принуждение срывается. Возвращение на континент вне сети ВТП угрожает её власти.\n**Директорат:** Старая гвардия (банкиры), Молодые технократы (сотрудничество с Теслой), Тайный департамент (разведка и ликвидация). Ламберт — неизвестная личность за общей подписью директората. Полный текст для промпта и правила: [WTC_CANON.md](WTC_CANON.md).'
 if '**Рычаги:** долг 0–100' not in s:s=s.replace(needle,replacement)
 write(p,s)
 p='docs/JAPAN_CANONICAL_CAMPAIGN.md';s=read(p).replace('33 фокуса образуют','84 фокуса образуют').replace('Альтернативные гражданское/военно-морское правительства и мирная японская ветка удалены.','Начальная кампания имеет только канонический политический путь. Существующие авторские послевоенные фокусы сохранены ниже её развязки.')
 s=s.replace('Сохраняется прежняя независимая подготовка с 19 марта, но её видимый срок теперь 43 дня. Военные задания имеют запасной срок 1006 дней; календарная проверка завершает активную кампанию с наступлением февраля 1896-го.','Видимый общий отсчёт начинается 1 января: 120 дней до ультиматума 1 мая. Мобилизация всё ещё начинается 19 марта и не перезапускает таймер. После начала войны обе страны видят срок до 1 февраля 1896 года. Однократное восстановление миссий по текущей дате возвращает правильный остаток в существующих партиях; ежедневные проверки не перезапускают часы.')
 s=s.replace('15 новых национальных духов отражают','43 национальных духа сюжетных модулей отражают').replace('Три оригинала созданы','Пять оригиналов созданы')
 s=s.replace('- `gfx/interface/jpc_sources/council.png` — тайный совет в Токио.','- `gfx/interface/jpc_sources/council.png` — тайный совет в Токио;\n- `gfx/interface/jpc_sources/north.png` — телеграф, северный протокол и припасы;\n- `gfx/interface/jpc_sources/luzon.png` — госпитальное судно и тропический гарнизон.')
 s+='''
## Внутренние системы: расширение 12 октября

Добавлены 30 фокусов, 18 событий с выбором, 26 решений и 28 духов поверх исходного канонического ядра. Все новые ответвления начинаются от политических договорённостей; отдельных корней армии или промышленности нет. Все 84 фокуса имеют зарегистрированную иллюстрацию и RU/EN-ключи; тематические эмблемы переиспользуются, это не 84 уникальных рисунка.

Мицубиси: давление 0–100, доверие 0–100, месячное обслуживание 3/5/8 политической власти. Война, гарантии и новые поставки увеличивают давление. Независимый аудит, календарь платежей, акцизы и выкуп облигаций дают разные способы управления. Кассовый кризис требует выбрать между авансом Осаки, заморозкой заказов и отсрочкой выплат семьям. Победитель исполняет нефтяную монополию и распределяет роялти; проигравший может реструктурировать обязательства без нефти. Финансовый кризис можно окончательно закрыть после войн и расчётов. Долг ВТП существует отдельно.

Север: доверие Сайго, раздражение флота и запас месяцев снабжения. 250 реальных винтовок и 4 транспорта передаются A08 и покрывают три месяца. Без поставок доверие падает; отсрочки ограничены двумя, хлебные караваны тремя. Инспекция даёт выбор границ вмешательства. После войны постоянный компакт при достаточном доверии заменяет кризисы постоянной гражданской ценой. Хоккайдо сохраняет власть, территорию, дивизии и нейтралитет.

Лусон: нагрузка и усталость гарнизона растут независимо от Борнео. Эскорты, продовольствие, медицина и ротации стоят ресурсов и увеличивают обязательства Мицубиси. Расследование ложных ведомостей, муниципальные закупки и интенданты сдерживают рост, не выдают победу над Конфедерацией. После отдельного мира театральные штрафы снимаются. Дух двух фронтов действует только при одновременной войне с A01 и A10.

ИИ получает ранние приоритеты аудита, снабжения, конвойного графика и ротаций. У ВТП займы ИИ ограничены военным дефицитом транспортов, чтобы мирные страны не брали их бесконечно. Проверки сценариев и ресурсов: tools/japan_story_validation.json. Канон и механика ВТП: WTC_CANON.md.

Генераторы: extend_japan_story.py → restore_pacific_clocks.py → build_wtc_credit.py → finish_story_integration.py. build_story_localisation.py готовит авторские тексты; исходный build_japan_canonical.py защищён от стирания расширенного дерева. Не запускать генераторы одновременно с ручным редактированием тех же файлов.
'''
 if '## Внутренние системы: расширение' not in read(p):write(p,s)
 p='docs/AUTHOR_DECISIONS.md';s=read(p)
 if '### Видимый календарь и кредитная ВТП' not in s:s+='\n### Видимый календарь и кредитная ВТП — 12 октября 2026\n\nУточнение автора: вернуть таймер обеим сторонам с начала игры, первые два голландских альтернативных входа рядом с Одиноким волком, мировую шкалу долга и ограничения ВТП. Отсчёт 120 дней с января заменяет прежнюю скрытую фазу 77 + видимую 43; майский ультиматум и февральская конференция сохраняются. При долге 100 реализован местный переворот вместо прямой аннексии Палатой, поскольку автор отдельно запретил ей прямое территориальное управление. Подробнее WTC_CANON.md и JAPAN_CANONICAL_CAMPAIGN.md.\n'
 write(p,s)
 print('Finished historical AI, defeat recovery, two-front cleanup and canon documentation.')
if __name__=='__main__':main()
