"""Author the 1893–1902 narrative and its persistent world state. No old migrations."""
from pathlib import Path
import json
import re
from validate_philippines_rework import parse

ROOT = Path(__file__).resolve().parents[1]
FILES = {}
LOC = {'russian': {}, 'english': {}}
EFFECTS, TRIGGERS, EVENTS, IDEAS = [], [], ['add_namespace = sen_campaign'], []


def loc(key, ru, en):
    for lang, text in (('russian', ru), ('english', en)):
        assert key not in LOC[lang], key
        LOC[lang][key] = text


def effect(key, body):
    EFFECTS.append(f'{key} = {{ {body} }}')


def trigger(key, body):
    TRIGGERS.append(f'{key} = {{ {body} }}')


def idea(key, ru, en, rd, ed, modifiers):
    loc(key, ru, en)
    loc(key + '_desc', rd, ed)
    IDEAS.append(f'{key} = {{ picture = jpc_credit removal_cost = -1 modifier = {{ {modifiers} }} }}')


def event(number, ru, en, rd, ed, guard, options, picture='GFX_1896_event_trade'):
    key = f'sen_campaign.{number}'
    loc(key + '.t', ru, en)
    loc(key + '.d', rd, ed)
    rendered = []
    for index, option in enumerate(options):
        r, e, body, *extra = option
        loc(key + f'.o{index}', r, e)
        gate = f'trigger = {{ {extra[0]} }}' if extra and extra[0] else ''
        rendered.append(f'option = {{ name = {key}.o{index} {gate} ai_chance = {{ factor = {70 if index == 0 else 30} }} {body} }}')
    EVENTS.append(f'country_event = {{ id = {key} title = {key}.t desc = {key}.d picture = {picture} is_triggered_only = yes timeout_days = 20 trigger = {{ {guard} }} ' + ' '.join(rendered) + ' }')


def hidden(number, guard, body):
    EVENTS.append(f'country_event = {{ id = sen_campaign.{number} hidden = yes is_triggered_only = yes trigger = {{ {guard} }} immediate = {{ {body} }} }}')


def guarded(guard, body):
    return f'if = {{ limit = {{ {guard} }} {body} }}'


def core():
    trigger('SEN_is_country', 'exists = yes NOT = { tag = ZZZ } has_capitulated = no')
    trigger('SEN_has_artifact_access', 'NOT = { has_global_flag = SEN_artifact_destroyed } has_global_flag = SEN_artifact_found OR = { has_country_flag = SEN_artifact_holder has_global_flag = SEN_open_spectrum }')
    trigger('SEN_has_tesla_access', 'has_global_flag = SEN_tesla_alive OR = { has_country_flag = SEN_tesla_host has_country_flag = SEN_research_license } any_country = { has_country_flag = SEN_tesla_host NOT = { has_war_with = ROOT } has_capitulated = no }')
    effect('SEN_country_initialize_effect', guarded('SEN_is_country = yes NOT = { has_country_flag = SEN_initialized }', 'set_country_flag = SEN_initialized set_variable = { SEN_science = 0 } set_variable = { SEN_readiness = 0 } set_variable = { SEN_security = 20 } set_variable = { SEN_exposure = 0 }'))
    effect('SEN_clamp_effect', 'hidden_effect = { ' + ' '.join(f'clamp_variable = {{ var = SEN_{name} min = 0 max = 100 }}' for name in ('science', 'readiness', 'security', 'exposure')) + ' }')
    effect('SEN_world_initialize_effect', guarded('NOT = { has_global_flag = SEN_world_initialized }', '''
      set_global_flag = SEN_world_initialized
      set_global_flag = SEN_tesla_alive
      if = { limit = { country_exists = MLT } MLT = { set_country_flag = SEN_tesla_host } 116 = { set_state_flag = SEN_tesla_site } }
      else_if = { limit = { country_exists = A02 } A02 = { set_country_flag = SEN_tesla_host capital_scope = { set_state_flag = SEN_tesla_site } } }
      else = { set_country_flag = SEN_tesla_host capital_scope = { set_state_flag = SEN_tesla_site } }
    '''))
    # THIS is the new custodian. Neither the object nor Tesla is copied.
    effect('SEN_claim_artifact_effect', guarded('SEN_is_country = yes NOT = { has_global_flag = SEN_artifact_destroyed }', '''
      every_country = { limit = { has_country_flag = SEN_artifact_holder } clr_country_flag = SEN_artifact_holder }
      set_country_flag = SEN_artifact_holder set_global_flag = SEN_artifact_found
    '''))
    effect('SEN_secure_artifact_effect', guarded('SEN_is_country = yes NOT = { has_global_flag = SEN_artifact_destroyed }', '''
      SEN_claim_artifact_effect = yes
      every_state = { limit = { has_state_flag = SEN_artifact_site } clr_state_flag = SEN_artifact_site }
      capital_scope = { set_state_flag = SEN_artifact_site }
    '''))
    effect('SEN_destroy_artifact_effect', guarded('SEN_is_country = yes has_country_flag = SEN_artifact_holder NOT = { has_global_flag = SEN_artifact_destroyed }', '''
      set_global_flag = SEN_artifact_destroyed clr_global_flag = SEN_open_spectrum
      every_country = { clr_country_flag = SEN_artifact_holder }
      every_state = { limit = { has_state_flag = SEN_artifact_site } clr_state_flag = SEN_artifact_site }
      country_event = { id = sen_campaign.22 days = 1 }
    '''))
    effect('SEN_refresh_custody_effect', '''
      if = { limit = { has_global_flag = SEN_artifact_found NOT = { has_global_flag = SEN_artifact_destroyed } }
       every_state = { limit = { has_state_flag = SEN_artifact_site }
        controller = { if = { limit = { SEN_is_country = yes NOT = { has_country_flag = SEN_artifact_holder } } SEN_claim_artifact_effect = yes } }
       }
      }
      if = { limit = { has_global_flag = SEN_tesla_alive }
       every_state = { limit = { has_state_flag = SEN_tesla_site }
        controller = { if = { limit = { SEN_is_country = yes NOT = { has_country_flag = SEN_tesla_host } }
         every_country = { clr_country_flag = SEN_tesla_host }
         set_country_flag = SEN_tesla_host
        } }
       }
      }
    ''')
    effect('SEN_monthly_country_effect', '''
      SEN_country_initialize_effect = yes
      if = { limit = { OR = { has_country_flag = SEN_expedition_active has_country_flag = SEN_return_active } }
       if = { limit = { has_idea = SEN_serum } add_to_variable = { SEN_exposure = 2 } }
       else = { add_to_variable = { SEN_exposure = 5 } }
      }
      if = { limit = { check_variable = { SEN_exposure > 60 } } add_ideas = SEN_field_exhaustion }
      else = { remove_ideas = SEN_field_exhaustion }
      SEN_clamp_effect = yes
    ''')
    trigger('SEN_can_request_license', 'SEN_is_country = yes has_country_flag = SEN_laboratory_done has_global_flag = SEN_tesla_alive NOT = { has_country_flag = SEN_research_license } NOT = { has_country_flag = SEN_license_pending } NOT = { has_country_flag = SEN_license_cooldown } NOT = { has_country_flag = SEN_tesla_host } any_country = { has_country_flag = SEN_tesla_host NOT = { has_war_with = ROOT } has_capitulated = no }')
    trigger('SEN_can_grant_license', 'SEN_is_country = yes has_country_flag = SEN_tesla_host has_global_flag = SEN_tesla_alive FROM = { SEN_is_country = yes has_country_flag = SEN_license_pending NOT = { has_country_flag = SEN_research_license } NOT = { has_war_with = ROOT } }')
    effect('SEN_request_license_effect', guarded('SEN_can_request_license = yes', 'set_country_flag = { flag = SEN_license_pending days = 30 } set_country_flag = { flag = SEN_license_cooldown days = 180 } any_country_dummy = no'))
    EFFECTS[-1] = EFFECTS[-1].replace('any_country_dummy = no', 'every_country = { limit = { has_country_flag = SEN_tesla_host } country_event = { id = sen_campaign.25 days = 2 } }')
    effect('SEN_approve_license_effect', guarded('SEN_can_grant_license = yes', 'FROM = { clr_country_flag = SEN_license_pending set_country_flag = SEN_research_license country_event = { id = sen_campaign.26 days = 1 } }'))
    effect('SEN_refuse_license_effect', guarded('SEN_can_grant_license = yes', 'FROM = { clr_country_flag = SEN_license_pending country_event = { id = sen_campaign.27 days = 1 } }'))


PROJECTS = [
    ('survey', 'Сверить береговые наблюдения', 'Reconcile Coastal Observations', 'Капитаны и землемеры сопоставят сведения о тихих бухтах и опасных переходах.', 'Captains and surveyors will compare records of quiet bays and dangerous crossings.', 35, 30, 20, 0, '', 'add_to_variable = { SEN_readiness = 30 } set_country_flag = SEN_survey_done', True),
    ('laboratory', 'Снарядить измерительную лабораторию', 'Equip a Measurement Laboratory', 'Приборы и одинаковые журналы позволят отличать изменение Песни от ошибки наблюдателя.', 'Instruments and consistent journals will distinguish changes in the Song from observers\' errors.', 50, 60, 30, 0, 'has_country_flag = SEN_survey_done', 'set_country_flag = SEN_laboratory_done add_to_variable = { SEN_science = 15 } if = { limit = { SEN_has_artifact_access = yes } add_to_variable = { SEN_science = 15 } }', True),
    ('expedition', 'Подготовить северную экспедицию', 'Prepare a Northern Expedition', 'Зимняя одежда, уголь и съёмочное имущество должны прибыть к причалам до выхода экспедиционных судов.', 'Winter clothing, coal and surveying equipment must reach the wharves before the expedition ships sail.', 75, 60, 75, 5, 'date > 1897.11.30 has_country_flag = SEN_survey_done', 'set_country_flag = SEN_expedition_done add_to_variable = { SEN_readiness = 40 }', True),
    ('excavation', 'Вскрыть гренландское хранилище', 'Open the Greenland Chamber', 'Под ледяным сводом найдены обработанные поверхности. Экспедиция подготовит безопасный проход к ним.', 'Worked surfaces have been found beneath the ice. The expedition will prepare a safe passage to them.', 60, 60, 75, 5, 'date > 1898.1.31 has_country_flag = SEN_expedition_done controls_state = 101 NOT = { has_global_flag = SEN_artifact_found } NOT = { has_global_flag = SEN_artifact_destroyed }', 'SEN_claim_artifact_effect = yes 101 = { set_state_flag = SEN_artifact_site } country_event = { id = sen_campaign.20 days = 1 }', False),
    ('security', 'Проверить охрану научных грузов', 'Inspect Scientific Cargo Security', 'Смотрители сверят пропуска и опечатают ящики с приборами, не прерывая работу учёных.', 'Keepers will check passes and seal instrument crates without interrupting scientific work.', 40, 30, 25, 0, 'has_country_flag = SEN_laboratory_done', 'add_to_variable = { SEN_security = 25 }', True),
    ('theft', 'Подготовить вывоз чужого артефакта', 'Prepare to Seize the Foreign Artifact', 'Посредники обещают провести людей к хранилищу и вывести груз на ожидающий транспорт.', 'Agents promise to guide a party to the store and bring its cargo to a waiting transport.', 100, 60, 100, 10, 'date > 1898.12.31 has_country_flag = SEN_expedition_done NOT = { check_variable = { SEN_readiness < 70 } } has_global_flag = SEN_artifact_found NOT = { has_global_flag = SEN_artifact_destroyed } NOT = { has_country_flag = SEN_artifact_holder } any_country = { has_country_flag = SEN_artifact_holder check_variable = { SEN_security < 60 } }', 'SEN_secure_artifact_effect = yes country_event = { id = sen_campaign.20 days = 1 }', True),
    ('prototype', 'Собрать глушитель дальнего действия', 'Assemble a Long-Range Suppressor', 'Спектральные записи позволяют проверить новую катушку и питание. Испытания должны подтвердить защиту отдельного берегового узла.', 'Spectral records allow a new coil and power supply to be tested. Trials must confirm protection of a single coastal site.', 100, 90, 100, 0, 'date > 1899.12.31 has_country_flag = SEN_laboratory_done SEN_has_artifact_access = yes SEN_has_tesla_access = yes NOT = { check_variable = { SEN_science < 60 } }', 'set_country_flag = SEN_advanced_knowledge add_ideas = SEN_advanced_suppressor country_event = { id = sen_campaign.30 days = 1 }', False),
    ('manufacture', 'Наладить выпуск глушителей', 'Organise Suppressor Manufacture', 'Мастерские получат проверенные чертежи, порядок испытаний и отдельный запас проводников и изоляторов.', 'Workshops will receive verified drawings, test procedures and a dedicated stock of conductors and insulators.', 100, 90, 150, 0, 'date > 1900.12.31 has_country_flag = SEN_advanced_knowledge', 'set_country_flag = SEN_production_done add_ideas = SEN_suppressor_workshops', False),
    ('return', 'Оборудовать опытную береговую станцию', 'Equip an Experimental Coastal Station', 'Экспедиция подготовит небольшой узел с непрерывным питанием и сменными командами. Дальнейший путь потребует новых измерений.', 'The expedition will prepare a small site with continuous power and rotating crews. Any advance beyond it requires further measurements.', 100, 90, 200, 10, 'date > 1900.12.31 has_country_flag = SEN_production_done has_country_flag = SEN_advanced_knowledge check_variable = { SEN_exposure < 91 }', 'set_country_flag = SEN_return_done add_ideas = SEN_coastal_station country_event = { id = sen_campaign.31 days = 1 }', False),
    ('rotation', 'Сменить экспедиционные команды', 'Rotate Expedition Crews', 'Свежие команды заменят людей, слишком долго работавших у опасного берега. Отстранённые вернутся под врачебное наблюдение.', 'Fresh crews will replace those who have spent too long on the dangerous coast. Relieved personnel will return to medical supervision.', 40, 30, 25, 0, 'has_country_flag = SEN_expedition_done check_variable = { SEN_exposure > 0 }', 'add_to_variable = { SEN_exposure = -30 }', True),
]


def projects():
    tags = sorted({tag for p in (ROOT / 'common/country_tags').glob('*.txt') for tag in re.findall(r'^\s*([A-Z0-9]{3})\s*=', p.read_text(encoding='utf-8-sig'), re.M)} - {'ZZZ'})
    target_checks, target_mark, target_clear = [], [], []
    for tag in tags:
        target_checks.append(f'AND = {{ has_country_flag = SEN_target_{tag} country_exists = {tag} {tag} = {{ has_country_flag = SEN_artifact_holder check_variable = {{ SEN_security < 60 }} }} }}')
        target_mark.append(f'if = {{ limit = {{ {tag} = {{ has_country_flag = SEN_artifact_holder }} }} set_country_flag = SEN_target_{tag} }}')
        target_clear.append(f'clr_country_flag = SEN_target_{tag}')
    trigger('SEN_same_theft_target', 'OR = { ' + ' '.join(target_checks) + ' }')
    effect('SEN_mark_theft_target_effect', ' '.join(target_clear + target_mark))
    effect('SEN_clear_theft_target_effect', ' '.join(target_clear))
    decisions = []
    for key, ru, en, rd, ed, pp, duration, equipment, convoys, required, reward, repeat in PROJECTS:
        one_off = f'NOT = {{ has_country_flag = SEN_{key}_done }}' if not repeat else ''
        if key == 'prototype': one_off += ' NOT = { has_country_flag = SEN_advanced_knowledge }'
        trigger(f'SEN_{key}_requirements', f'SEN_is_country = yes {required} {one_off}')
        trigger(f'SEN_can_start_{key}', f'SEN_{key}_requirements = yes NOT = {{ has_country_flag = SEN_{key}_active }} NOT = {{ has_equipment = {{ support_equipment < {equipment} }} }} NOT = {{ has_equipment = {{ convoy_1 < {convoys} }} }}')
        ongoing = ' SEN_same_theft_target = yes' if key == 'theft' else ''
        start_extra = 'SEN_mark_theft_target_effect = yes' if key == 'theft' else ''
        cleanup = ' SEN_clear_theft_target_effect = yes' if key == 'theft' else ''
        effect(f'SEN_finish_{key}_effect', guarded(f'SEN_{key}_requirements = yes has_country_flag = SEN_{key}_active {ongoing}', reward + f' set_country_flag = SEN_{key}_done SEN_clamp_effect = yes') + f' clr_country_flag = SEN_{key}_active {cleanup}')
        loc('SEN_' + key, ru, en)
        loc('SEN_' + key + '_desc', rd, ed)
        decisions.append(f'''SEN_{key} = {{ icon = generic_naval cost = {pp} days_remove = {duration} days_re_enable = {180 if repeat else 0} fire_only_once = no
          visible = {{ SEN_is_country = yes {one_off} }} available = {{ SEN_can_start_{key} = yes }}
          cancel_trigger = {{ NOT = {{ SEN_{key}_requirements = yes {ongoing} }} }} cancel_if_not_visible = yes
          complete_effect = {{ if = {{ limit = {{ SEN_can_start_{key} = yes }} set_country_flag = SEN_{key}_active {start_extra}
            add_equipment_to_stockpile = {{ type = support_equipment amount = -{equipment} }}
            add_equipment_to_stockpile = {{ type = convoy_1 amount = -{convoys} }} }} }}
          cancel_effect = {{ clr_country_flag = SEN_{key}_active {cleanup} }} remove_effect = {{ SEN_finish_{key}_effect = yes }}
          ai_will_do = {{ base = {0 if key == 'theft' else 2} }} }}''')
    FILES['common/decisions/SEN_projects.txt'] = 'SEN_scientific_programme = {\n' + '\n'.join(decisions) + '\n}'


def story_events():
    trigger('SEN_can_manage_artifact', 'SEN_is_country = yes has_country_flag = SEN_artifact_holder NOT = { has_global_flag = SEN_artifact_destroyed } any_state = { has_state_flag = SEN_artifact_site is_controlled_by = ROOT }')
    effect('SEN_publish_spectrum_effect', guarded('SEN_can_manage_artifact = yes has_country_flag = SEN_custody_pending', '''
      clr_country_flag = SEN_custody_pending set_global_flag = SEN_open_spectrum
      every_country = { limit = { NOT = { tag = ZZZ } } set_country_flag = SEN_spectral_copy }
      add_stability = 0.03
      if = { limit = { tag = A04 } add_to_variable = { WTN_reputation = 10 } WTN_clamp_treasury_effect = yes }
    '''))
    effect('SEN_private_custody_effect', guarded('SEN_can_manage_artifact = yes has_country_flag = SEN_custody_pending', 'clr_country_flag = SEN_custody_pending set_country_flag = SEN_private_archive add_to_variable = { SEN_security = 10 } SEN_clamp_effect = yes'))
    event(20, 'Ящик из-подо льда', 'The Crate from beneath the Ice',
          'В ящике лежит устройство, чьё назначение не объясняют известные чертежи. Между обработанными поверхностями мерцает кристалл. Учёные просят время для измерений; посланники других держав уже предлагают охрану и сотрудничество.',
          'The crate contains a device unlike anything in known drawings. A crystal glimmers between worked surfaces. Scientists ask for time to measure it; foreign envoys are already offering protection and cooperation.',
          'SEN_can_manage_artifact = yes has_country_flag = SEN_custody_pending', [
              ('Опечатать хранилище', 'Seal the store', 'SEN_private_custody_effect = yes'),
              ('Разослать проверенные спектральные записи', 'Distribute verified spectral records', 'SEN_publish_spectrum_effect = yes')])
    event(21, 'Последняя печать', 'The Final Seal',
          'Охрана ждёт окончательного приказа у закрытого хранилища. Разрушение устройства оборвёт новые измерения. Копии записей останутся в лабораториях, но изготовить второй кристалл пока не сумел никто.',
          'The guards await a final order outside the sealed store. Destroying the device will end new measurements. Copies of its records will remain in laboratories, but no one has manufactured a second crystal.',
          'SEN_can_manage_artifact = yes has_country_flag = SEN_destruction_pending', [
              ('Сохранить устройство', 'Preserve the device', 'clr_country_flag = SEN_destruction_pending'),
              ('Отдать приказ об уничтожении', 'Order its destruction', guarded('SEN_can_manage_artifact = yes has_country_flag = SEN_destruction_pending', 'clr_country_flag = SEN_destruction_pending SEN_destroy_artifact_effect = yes'))])
    event(22, 'Пустое место кристалла', 'Where the Crystal Used to Be',
          'В опечатанном помещении больше нечего измерять. Сохранённые журналы вынесены в архив, исправные приборы возвращены учёным. Предстоит искать ответы в оставшихся записях и в новых наблюдениях Песни.',
          'There is nothing left to measure in the sealed room. Surviving journals have gone to the archive and intact instruments back to the scientists. Answers must now be sought in the remaining records and fresh observations of the Song.',
          'has_global_flag = SEN_artifact_destroyed', [('Сохранить всё, что удалось узнать', 'Preserve everything we learned', '')])
    event(25, 'Запрос к лаборатории Теслы', 'A Request to Tesla\'s Laboratory',
          'Представители [FROM.GetName] предлагают присылать приборы и сверенные наблюдения. Взамен они просят научную переписку и проверенные чертежи опытных катушек. Сотрудники лаборатории ждут решения о допуске.',
          'Delegates from [FROM.GetName] offer instruments and verified observations. In return, they request scientific correspondence and tested drawings for experimental coils. The laboratory staff await an access decision.',
          'SEN_can_grant_license = yes', [
              ('Сохранить закрытый порядок', 'Keep the laboratory closed', 'SEN_refuse_license_effect = yes'),
              ('Разрешить научную переписку', 'Authorise scientific correspondence', 'SEN_approve_license_effect = yes')])
    event(26, 'Мальтийские чертежи', 'Drawings from the Laboratory',
          'С научной почтой пришли проверенные схемы и замечания к нашим наблюдениям. Учёные смогут сверять работу своих приборов с опытами Теслы, сохраняя собственные лаборатории.',
          'Scientific mail has brought verified drawings and comments on our observations. Our scientists can compare their instruments with Tesla\'s experiments while retaining their own laboratories.',
          'has_country_flag = SEN_research_license', [('Передать пакет инженерам', 'Pass the packet to the engineers', '')])
    event(27, 'Запечатанное письмо', 'A Sealed Reply',
          'Лаборатория отказалась расширить переписку. Наши наблюдатели продолжат собственную работу; сведения о Песни придётся проверять без доступа к закрытым опытам.',
          'The laboratory has declined to extend its correspondence. Our observers will continue their own work, checking reports of the Song without access to the confidential experiments.',
          'SEN_is_country = yes', [('Продолжить наблюдения', 'Continue the observations', '')])
    event(30, 'Тихий круг у башни', 'A Quiet Circle around the Tower',
          'Измерительные команды прошли границу защищённого круга и вернулись к башне. Новый прибор держит противофазу дальше прежнего, но за отмеченными столбами Песнь снова различима. Инженеры требуют непрерывного питания и сменных расчётов.',
          'The measuring teams crossed the protected circle and returned to the tower. The new device maintains counterphase farther than its predecessor, but the Song can still be heard beyond the marked posts. Engineers require continuous power and rotating crews.',
          'has_country_flag = SEN_advanced_knowledge', [('Записать подтверждённые пределы', 'Record the verified limits', '')])
    event(31, 'Огонь береговой станции', 'The Coastal Station\'s Light',
          'На опытном берегу зажглись фонари. Команда проверила генератор, закрыла ведомость смены и передала первый связный отчёт. За пределами небольшого узла по-прежнему опасно; дальнейший путь начинается с новых измерений.',
          'Lamps have been lit on the experimental shore. The crew checked its generator, completed the rotation ledger and transmitted its first coherent report. The ground beyond the small site remains dangerous; any advance begins with fresh measurements.',
          'has_country_flag = SEN_return_done', [('Сохранить станцию и людей', 'Preserve the station and its people', '')])
    raid_guard = 'SEN_is_country = yes has_country_flag = SEN_tesla_host has_global_flag = SEN_tesla_alive has_country_flag = SEN_raid_pending'
    dead = 'clr_global_flag = SEN_tesla_alive every_country = { clr_country_flag = SEN_tesla_host } every_state = { limit = { has_state_flag = SEN_tesla_site } clr_state_flag = SEN_tesla_site } set_global_flag = SEN_tesla_lost'
    defend = guarded(raid_guard, 'clr_country_flag = SEN_raid_pending if = { limit = { NOT = { check_variable = { SEN_security < 50 } } } add_to_variable = { SEN_science = 5 } } else = { ' + dead + ' } SEN_clamp_effect = yes')
    evacuate = guarded(raid_guard + ' NOT = { has_political_power < 50 }', 'clr_country_flag = SEN_raid_pending add_political_power = -50 add_to_variable = { SEN_science = -15 } every_state = { limit = { has_state_flag = SEN_tesla_site } clr_state_flag = SEN_tesla_site } capital_scope = { set_state_flag = SEN_tesla_site } SEN_clamp_effect = yes')
    event(40, 'Ночные люди у лаборатории', 'Figures outside the Laboratory',
          'Часовой заметил людей, двигавшихся к служебному входу без огней. У задержанного нашли знаки Безмолвного Хора. Охрана предлагает держать входы; ассистенты просят немедленно вывезти Теслу и журналы в запасное помещение.',
          'A sentry spotted figures approaching the service entrance without lights. Signs of the Silent Choir were found on a detainee. The guards propose holding the entrances; the assistants ask to move Tesla and the journals to reserve quarters immediately.',
          raid_guard, [('Удерживать входы', 'Hold the entrances', defend + ' custom_effect_tooltip = SEN_raid_risk_tt'), ('Вывести учёных под охраной', 'Evacuate the scientists under guard', evacuate, 'NOT = { has_political_power < 50 }')])
    congress_guard = 'SEN_is_country = yes has_country_flag = SEN_congress_pending NOT = { has_country_flag = SEN_congress_answered }'
    event(50, 'Предложение Совета по Песни', 'A Proposed Council on the Song',
          'В письме предлагается постоянный обмен измерениями и общие правила научных экспедиций. Делегаты сохранят самостоятельность своих правительств. Спор идёт о том, кто сможет закрывать доступ к наблюдениям и назначать условия будущих походов.',
          'The letter proposes a permanent exchange of measurements and common rules for scientific expeditions. Delegates will preserve their governments\' independence. The dispute concerns who may restrict observations and dictate terms for future voyages.',
          congress_guard, [
              ('Оставить наблюдения в собственном архиве', 'Retain our observations in our own archive', guarded(congress_guard, 'clr_country_flag = SEN_congress_pending set_country_flag = SEN_congress_answered set_country_flag = SEN_separate_science')),
              ('Отправить научную делегацию', 'Send a scientific delegation', guarded(congress_guard, 'clr_country_flag = SEN_congress_pending set_country_flag = SEN_congress_answered set_country_flag = SEN_congress_member 101 = { add_to_variable = { SEN_congress_votes = 1 } if = { limit = { check_variable = { SEN_congress_votes > 2 } } set_global_flag = SEN_congress_established } } add_timed_idea = { idea = SEN_scientific_council days = 730 }'))])


PROFILES = [
    ('DUT', ['A01'], 'Батавские ведомости', 'Batavian Ledgers', 'Батавия сводит требования двора, совета и островных общин. Военные планы требуют ресурсов, а торговые представители — надёжной подписи.', 'Batavia must reconcile the court, council and island communities. War plans require resources, while trade delegates demand a reliable signature.', 'Гражданские договоры', 'Civil Agreements', 'Общий порядок переговоров даёт общинам голос при распределении поставок.', 'Common negotiating procedures give communities a voice in allocating supplies.', 'Военный порядок', 'Military Administration', 'Штабы получают преимущество при распределении грузов и требуют единой отчётности.' , 'Staffs receive priority in cargo allocation and demand common accounting.'),
    ('BRI', ['A02'], 'Приказы из Гамильтона', 'Orders from Hamilton', 'Далёкие стоянки просят корабли и уголь. На Бермудах спорят, служит ли уцелевший флот будущему возвращению или постоянной жизни среди островов.', 'Distant stations ask for ships and coal. Bermuda debates whether the surviving fleet serves a future return or permanent life among the islands.', 'Обязательство перед родиной', 'Commitment to the Homeland', 'Адмиралтейство сохраняет береговые наблюдения ради будущего возвращения.', 'The Admiralty preserves coastal observations in preparation for a future return.', 'Океанский союз стоянок', 'Oceanic Station Compact', 'Опорой державы становятся уцелевшие гавани и согласованные службы между ними.', 'The state rests upon surviving harbours and the coordinated services between them.'),
    ('JAP', ['A03'], 'Императорские морские ведомости', 'Imperial Maritime Ledgers', 'Токио получает противоречивые донесения с островов. Флот, армейские интенданты и торговые дома требуют собственного места в общем плане.', 'Tokyo receives conflicting island reports. The fleet, army quartermasters and trading houses each demand a place in the common plan.', 'Согласованные островные кабинеты', 'Coordinated Island Cabinets', 'Переговоры с соседними правительствами получают собственных уполномоченных.', 'Negotiations with neighbouring governments receive dedicated delegates.', 'Приоритет экспедиционных штабов', 'Priority for Expedition Staffs', 'Штабы согласуют дальние выходы и порядок снабжения гарнизонов.', 'Staffs coordinate distant voyages and garrison supplies.'),
    ('WTP', ['A04'], 'Под общей подписью', 'Beneath a Common Signature', 'Ламберт остаётся подписью на закрытых письмах. Директорат спорит о цене научного прогресса: открытые измерения могут изменить всю систему обязательств.', 'Lambert remains a signature on sealed letters. The directorate debates the price of scientific progress: open measurements could transform the entire system of obligations.', 'Отчётность торговых представителей', 'Accountable Trade Delegates', 'Представители обязаны объяснять условия договоров и стоимость принятого риска.', 'Delegates must explain treaty terms and the cost of accepted risks.', 'Закрытый надзор директората', 'Confidential Directorate Oversight', 'Закрытые отделы сверяют сведения о грузах и посредниках перед решениями директората.', 'Confidential offices check cargo and agents before directorate decisions.'),
    ('IRN', ['A05'], 'Голос гаванских капитанов', 'The Voice of Havana\'s Captains', 'Грейвс выслушивает портовые советы и командиров. Судьбу уцелевших общин определяют не только орудия, но и порядок распределения прибывающих грузов.', 'Graves hears harbour councils and commanders. The surviving communities\' fate depends on cargo distribution as well as guns.', 'Представительство портовых общин', 'Harbour Community Representation', 'Общины участвуют в разборе снабжения и ответственности командиров.', 'Communities help review supplies and commanders\' responsibility.', 'Единое морское командование', 'Unified Naval Command', 'Капитаны передают учёт поставок общему командованию.', 'Captains place supply records under a common command.'),
    ('RUS', ['A06'], 'Письма двора и канцелярии', 'Letters from Court and Chancellery', 'Александр III получает северные наблюдения; канцелярия Победоносцева требует ограничить переписку с мальтийскими учёными. Спор выходит за стены двора.', 'Alexander III receives northern observations; Pobedonostsev\'s chancellery demands restrictions on correspondence with Maltese scientists. The dispute is spreading beyond the court.', 'Императорская научная переписка', 'Imperial Scientific Correspondence', 'Двор поддерживает проверку наблюдений и связь с внешними лабораториями.', 'The court supports verified observations and links with outside laboratories.', 'Попечительство духовной канцелярии', 'Guardianship of the Church Chancellery', 'Канцелярия требует надзора над общественными собраниями и научной перепиской.', 'The chancellery demands oversight of public assemblies and scientific correspondence.'),
    ('AUS', ['A07','AVC','AQL','ASA','AWA','ATA'], 'Колониальные представительства', 'Colonial Delegations', 'Парламенты обсуждают общие накладные и будущую связь колоний. Каждый кабинет настаивает на праве отвечать за собственные обязательства.', 'Parliaments debate common manifests and the colonies\' future relationship. Each cabinet insists on answering for its own obligations.', 'Согласование между кабинетами', 'Agreement between Cabinets', 'Парламентские делегации договариваются о признании общих правил.', 'Parliamentary delegations negotiate recognition of common rules.', 'Приоритет местного казначейства', 'Priority for the Local Treasury', 'Казначейство сохраняет отдельный порядок распределения средств.', 'The treasury retains its own allocation procedures.'),
    ('NOR', ['A08'], 'Зимние письма Хакодате', 'Winter Letters from Hakodate', 'Сайго получает жалобы на южных посредников и сведения о северных складах. Гарнизоны просят определить границу между торговлей и подчинением.', 'Saigo receives complaints about southern agents and reports on northern stores. Garrisons ask for a clear boundary between trade and submission.', 'Договоры северных общин', 'Northern Community Agreements', 'Общины участвуют в согласовании поставок с внешними представителями.', 'Communities help coordinate supplies with foreign delegates.', 'Складской приказ командования', 'Command Store Directive', 'Командование отвечает за приёмку и распределение запасов.', 'Command answers for the acceptance and distribution of stores.'),
    ('OSA', ['A09'], 'Расписки торговых домов', 'Trading House Bills', 'Ивасаки собирает спорные расписки. За каждым обещанием стоит мастерская, корабельная партия или требование кредитора.', 'Iwasaki gathers disputed bills. Behind each promise stands a workshop, a shipload or a creditor\'s demand.', 'Открытые расчётные книги', 'Open Clearing Books', 'Дома сверяют счета и признают общий порядок разбора претензий.', 'The houses reconcile accounts and recognise a common claims procedure.', 'Закрытый совет домов', 'Confidential House Council', 'Совет распределяет заказы и ограничивает доступ к торговым сведениям.', 'The council allocates orders and restricts access to commercial records.'),
    ('PHI', ['A10'], 'Письма с островных собраний', 'Letters from Island Assemblies', 'В Кавите приходят делегации островных правительств. Они готовы обсуждать снабжение, но требуют признания своих голосов и подписей.', 'Delegations from the island governments arrive in Cavite. They will discuss supplies but demand recognition of their own voices and signatures.', 'Согласие островных делегаций', 'Consent of Island Delegations', 'Делегации участвуют в общих решениях о поставках и переговорах.', 'Delegations participate in common decisions on supplies and negotiations.', 'Чрезвычайное снабжение центра', 'Emergency Central Supply', 'Центр получает преимущество при распределении военных грузов.', 'The centre receives priority in allocating military cargo.'),
    ('PCF', ['PCF'], 'Спор в совете поместий', 'Dispute in the Estate Council', 'Борегар слышит требования плантаторов и донесения с прибрежных дорог. Принудительный труд удерживает старый порядок, но обостряет внутренний раскол.', 'Beauregard hears planters\' demands and reports from the coastal roads. Forced labour sustains the old order while deepening internal divisions.', 'Договорный труд и местные собрания', 'Contract Labour and Local Assemblies', 'Поместья переходят к договорному найму под надзором местных собраний.', 'Estates shift to contractual employment under local assemblies\' supervision.', 'Совет старых поместий', 'Council of the Old Estates', 'Плантационные дома сохраняют прежнее распределение власти и обязанностей.', 'The plantation houses preserve the existing distribution of authority and obligations.'),
    ('PAZ', ['PAZ'], 'Штаб и святилище', 'Staff and Sanctuary', 'Эрнандес требует точных ведомостей снабжения. Служители Пророка утверждают, что решения штаба должны подтверждаться священным советом.', 'Hernandez demands accurate supply records. The Prophet\'s servants insist that staff decisions must be confirmed by a sacred council.', 'Ответственность военных служб', 'Accountable Military Services', 'Службы отвечают за приказы и снабжение перед общим советом.', 'The services answer to a common council for orders and supplies.', 'Попечительство Пророка', 'The Prophet\'s Guardianship', 'Священный совет утверждает решения о службе и распределении припасов.', 'The sacred council approves service decisions and the distribution of provisions.'),
    ('PHR', ['PHR'], 'Собрание у прибрежного огня', 'An Assembly by the Coastal Fire', 'Мама Бриджит созывает представителей общин. Прибывшие беженцы нуждаются в крове, а смотрители складов боятся истощить последние запасы.', 'Maman Brigitte convenes community delegates. Arriving refugees need shelter, while storekeepers fear exhausting the last reserves.', 'Приют общин', 'Community Sanctuary', 'Общины распределяют приём новых семей и совместное снабжение.', 'Communities share responsibility for new families and common supplies.', 'Закрытые береговые дозоры', 'Closed Coastal Watches', 'Дозоры усиливают надзор за высадками и местными складами.', 'Watches tighten supervision over landings and local stores.'),
    ('HAW', ['PHW'], 'Королевские гости в Гонолулу', 'Royal Guests in Honolulu', 'Иностранные капитаны предлагают исключительные права у причалов. Королевский совет обсуждает цену таких обещаний и доверие островных общин.', 'Foreign captains offer exclusive wharf arrangements. The royal council debates their price and the confidence of island communities.', 'Равные правила нейтральной гавани', 'Equal Rules for a Neutral Harbour', 'Портовые службы применяют общий порядок к торговым судам разных флагов.', 'Harbour services apply common procedures to merchant ships of different flags.', 'Королевское портовое управление', 'Royal Harbour Administration', 'Королевские уполномоченные надзирают за отдельными торговыми договорами.', 'Royal commissioners oversee individual trading agreements.'),
    ('MLT', ['MLT'], 'За стенами Святого Ангела', 'Behind Saint Angelo\'s Walls', 'Валлетта принимает закрытые научные грузы и письма изгнанных дворов. Местный совет спорит о пределах британской охраны и самостоятельности лабораторий.', 'Valletta receives confidential scientific cargo and letters from exiled courts. Its council debates the limits of British protection and laboratory independence.', 'Свободная научная переписка', 'Open Scientific Correspondence', 'Совет защищает проверяемый обмен сведениями между лабораториями.', 'The council protects verifiable exchanges between laboratories.', 'Особый порядок научной охраны', 'Special Scientific Security', 'Научные грузы и посетители проходят дополнительную проверку.', 'Scientific cargo and visitors undergo additional checks.'),
    ('SUL', ['A11','A12','A13','A14'], 'Слово двора и портовых общин', 'The Court and Harbour Communities', 'Посланники соседних держав предлагают договоры. Двору предстоит решить, кто вправе обещать сборы и обслуживание местных причалов.', 'Envoys from neighbouring powers propose treaties. The court must decide who may promise dues and services at local wharves.', 'Совет общин при дворе', 'Community Council at Court', 'Портовые общины участвуют в принятии торговых обязательств.', 'Harbour communities participate in accepting trade obligations.', 'Личная канцелярия султана', 'The Sultan\'s Chancellery', 'Двор сосредоточивает договоры и распределение сборов в своей канцелярии.', 'The court concentrates treaties and allocation of dues in its chancellery.'),
    ('SEA', ['PSY','PTG','PKR','PPM','PZN','PPE'], 'Письма малого порта', 'Letters from a Small Harbour', 'Гавань получает несовместимые предложения торговых посредников. Местной власти придётся выбрать порядок работы с внешними обещаниями.', 'The harbour receives incompatible offers from trading agents. Its authorities must choose how to handle outside promises.', 'Собрание портовых представителей', 'Assembly of Harbour Delegates', 'Представители разбирают торговые обещания перед общим собранием.', 'Delegates review trading promises before a common assembly.', 'Единая портовая канцелярия', 'Unified Harbour Office', 'Управление причалов получает общий порядок хранения договоров.', 'The wharf administration adopts common treaty records.'),
    ('ISL', ['PLS','PSL','PCB','PPN','PVI','PSM','PMD','PNM','PNL','PML','PBT'], 'Собственная островная подпись', 'Our Own Island Signature', 'Посланники предлагают общие договоры от имени соседей. Местные представители требуют сначала определить полномочия своего кабинета.', 'Envoys propose common treaties on their neighbours\' behalf. Local delegates demand that their own cabinet\'s authority be settled first.', 'Согласие местных собраний', 'Consent of Local Assemblies', 'Местные собрания подтверждают договоры, заключённые от их имени.', 'Local assemblies confirm treaties concluded in their name.', 'Чрезвычайные полномочия кабинета', 'Emergency Cabinet Powers', 'Кабинет получает особый порядок исполнения снабженческих договоров.', 'The cabinet receives special authority to carry out supply agreements.'),
]


def political_profiles():
    pulse = []
    for index, (code, tags, title_ru, title_en, rd, ed, ar, ae, ard, aed, br, be, brd, bed) in enumerate(PROFILES):
        group = 'OR = { ' + ' '.join('tag = ' + t for t in tags) + ' }'
        trigger('SEN_profile_' + code, 'SEN_is_country = yes ' + group)
        for route, ru, en, desc_ru, desc_en, modifiers in [('civic', ar, ae, ard, aed, 'stability_factor = 0.03 research_speed_factor = 0.01'), ('command', br, be, brd, bed, 'political_power_gain = 0.05 supply_consumption_factor = -0.02')]:
            idea(f'SEN_{code}_{route}', ru, en, desc_ru, desc_en, modifiers)
            other = 'command' if route == 'civic' else 'civic'
            body = f'clr_country_flag = SEN_{code}_{other} remove_ideas = SEN_{code}_{other} set_country_flag = SEN_{code}_{route} add_ideas = SEN_{code}_{route}'
            effect(f'SEN_{code}_{route}_effect', guarded(f'SEN_profile_{code} = yes has_country_flag = SEN_policy_pending NOT = {{ has_country_flag = SEN_policy_set }}', f'clr_country_flag = SEN_policy_pending set_country_flag = SEN_policy_set {body}'))
        number = 100 + index * 3
        event(number, title_ru, title_en, rd, ed, f'SEN_profile_{code} = yes has_country_flag = SEN_policy_pending NOT = {{ has_country_flag = SEN_policy_set }}', [(ar, ae, f'SEN_{code}_civic_effect = yes'), (br, be, f'SEN_{code}_command_effect = yes')])
        crisis_guard = f'SEN_profile_{code} = yes has_country_flag = SEN_crisis_pending NOT = {{ has_country_flag = SEN_crisis_set }}'
        settle = 'clr_country_flag = SEN_crisis_pending set_country_flag = SEN_crisis_set add_stability = 0.03 add_political_power = 25'
        extra = 'country_event = { id = sen_campaign.400 days = 1 }' if code == 'RUS' else ''
        switch = f'''clr_country_flag = SEN_crisis_pending set_country_flag = SEN_crisis_set add_stability = -0.04
          if = {{ limit = {{ has_country_flag = SEN_{code}_civic }} clr_country_flag = SEN_{code}_civic remove_ideas = SEN_{code}_civic set_country_flag = SEN_{code}_command add_ideas = SEN_{code}_command }}
          else = {{ clr_country_flag = SEN_{code}_command remove_ideas = SEN_{code}_command set_country_flag = SEN_{code}_civic add_ideas = SEN_{code}_civic }} {extra}'''
        event(number + 1, title_ru + ': новые требования', title_en + ': New Demands',
              rd + ' Старые решения теперь проверяют спором о новых грузах и расходах. Представители требуют подтвердить принятый порядок или пересмотреть полномочия.',
              ed + ' Earlier decisions now face disputes over new cargo and expenditure. Delegates demand confirmation of the arrangements or a revision of authority.', crisis_guard,
              [('Подтвердить принятый порядок', 'Confirm the arrangements', guarded(crisis_guard, settle + ' ' + extra)), ('Пересмотреть полномочия', 'Revise the allocation of authority', guarded(crisis_guard, switch))])
        end_guard = f'SEN_profile_{code} = yes has_country_flag = SEN_future_pending NOT = {{ has_country_flag = SEN_future_set }}'
        event(number + 2, 'Куда ведут наши морские пути', 'Where Our Sea Routes Lead',
              'На столе лежат новые береговые записи и счета уцелевших гаваней. Одни представители предлагают готовить опасные опытные рейсы; другие хотят направить силы на постоянный дом среди островов. ' + ard,
              'New coastal records and surviving harbours\' accounts lie on the table. Some delegates propose preparing hazardous trial voyages; others would build a permanent island home. ' + aed,
              end_guard, [('Сохранить средства для опытных рейсов', 'Reserve resources for trial voyages', guarded(end_guard, 'clr_country_flag = SEN_future_pending set_country_flag = SEN_future_set set_country_flag = SEN_return_committed add_to_variable = { SEN_readiness = 10 } SEN_clamp_effect = yes')), ('Укреплять островной дом', 'Strengthen our island home', guarded(end_guard, 'clr_country_flag = SEN_future_pending set_country_flag = SEN_future_set set_country_flag = SEN_island_home add_ideas = SEN_island_future'))])
        pulse.append(f'''if = {{ limit = {{ SEN_profile_{code} = yes }}
          if = {{ limit = {{ date > 1893.2.28 NOT = {{ has_country_flag = SEN_policy_dispatched }} }} set_country_flag = SEN_policy_dispatched set_country_flag = SEN_policy_pending country_event = {{ id = sen_campaign.{number} days = 1 }} }}
          if = {{ limit = {{ date > 1897.8.31 has_country_flag = SEN_policy_set NOT = {{ has_country_flag = SEN_crisis_dispatched }} }} set_country_flag = SEN_crisis_dispatched set_country_flag = SEN_crisis_pending country_event = {{ id = sen_campaign.{number+1} days = 1 }} }}
          if = {{ limit = {{ date > 1901.8.31 has_country_flag = SEN_crisis_set NOT = {{ has_country_flag = SEN_future_dispatched }} }} set_country_flag = SEN_future_dispatched set_country_flag = SEN_future_pending country_event = {{ id = sen_campaign.{number+2} days = 1 }} }}
        }}''')
    effect('SEN_profile_pulse_effect', ' '.join(pulse))
    russian_crisis()


def main():
    core()
    projects()
    story_events()
    political_profiles()
    calendar()
    interface()
    FILES['common/scripted_effects/SEN_campaign.txt'] = '\n'.join(EFFECTS)
    FILES['common/scripted_triggers/SEN_campaign.txt'] = '\n'.join(TRIGGERS)
    FILES['events/SEN_campaign.txt'] = '\n'.join(EVENTS)
    FILES['common/ideas/SEN_campaign.txt'] = 'ideas = { country = {\n' + '\n'.join(IDEAS) + '\n} }'
    for relative, text in FILES.items():
        if relative.endswith('.txt'): parse(text)
    for relative, text in FILES.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.rstrip() + '\n', encoding='utf-8')
    for lang, entries in LOC.items():
        path = ROOT / f'localisation/{lang}/SEN_campaign_l_{lang}.yml'
        path.write_text(f'l_{lang}:\n' + '\n'.join(f' {key}:0 "{text}"' for key, text in entries.items()) + '\n', encoding='utf-8-sig')
    (ROOT / 'tools/song_campaign_manifest.json').write_text(json.dumps(dict(projects=[dict(id=p[0], days=p[6], equipment=p[7], convoys=p[8], repeat=p[11]) for p in PROJECTS], profiles=PROFILES, events=len(EVENTS)-1, ideas=len(IDEAS), localized_keys=len(LOC['russian'])), ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Built {len(EVENTS)-1} campaign events, {len(PROJECTS)} projects, {len(PROFILES)} political profiles and {len(IDEAS)} spirits.')


if __name__ == '__main__':
    main()
