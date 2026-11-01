"""Build the first research module. Never writes to the reference mod.

Uses installed game definitions for equipment/focus compatibility; progression
is informed by the inspected Great War Redux industry tree and our world canon.
"""
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def block_end(text, opening):
    depth = 0
    quoted = False
    comment = False
    for i in range(opening, len(text)):
        c = text[i]
        if c == '\n':
            comment = False
        if comment:
            continue
        if c == '"':
            quoted = not quoted
        if not quoted:
            if c == '#':
                comment = True
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return i + 1
    raise ValueError('Unbalanced script block')


def build(game):
    records = {}

    def add(key, year, ru, en, desc_ru, desc_en):
        records[key] = dict(year=year, ru=ru, en=en, desc_ru=desc_ru, desc_en=desc_en)

    groups = [
        (['basic_machine_tools', 'improved_machine_tools', 'advanced_machine_tools', 'assembly_line_production'],
         [1890, 1894, 1898, 1902],
         ['Восстановление станочного парка', 'Взаимозаменяемые детали', 'Точные станки', 'Серийная сборка'],
         ['Restored Machine Shops', 'Interchangeable Parts', 'Precision Machine Tools', 'Serial Assembly'],
         'Стандартизация деталей и оснащения мастерских повышает устойчивость военного производства после разрыва прежних цепочек поставок.',
         'Standardized parts and better workshops restore reliable military production after the collapse of old supply chains.'),
        (['concentrated_industry' + (str(i) if i > 1 else '') for i in range(1, 6)],
         [1890, 1894, 1898, 1902, 1906],
         ['Портовые мануфактуры', 'Фабричные кварталы', 'Электрификация фабрик', 'Промышленные комплексы', 'Интегрированные комбинаты'],
         ['Port Manufactories', 'Factory Districts', 'Factory Electrification', 'Industrial Complexes', 'Integrated Works'],
         'Сосредоточение мастерских у портов упрощает доставку сырья и увеличивает выпуск. Выбор исключает развитие распределённой промышленности.',
         'Concentrating workshops near ports improves output and access to imported materials. This excludes the distributed industry path.'),
        (['dispersed_industry' + (str(i) if i > 1 else '') for i in range(1, 6)],
         [1890, 1894, 1898, 1902, 1906],
         ['Островные мастерские', 'Региональные арсеналы', 'Местные электростанции', 'Сеть запасных производств', 'Автономные промышленные округа'],
         ['Island Workshops', 'Regional Arsenals', 'Local Power Stations', 'Reserve Production Networks', 'Autonomous Industrial Districts'],
         'Распределённые мастерские уменьшают зависимость от одного порта и сохраняют навыки при смене заказов. Выбор исключает концентрацию промышленности.',
         'Distributed workshops reduce dependence on a single port and retain skills when orders change. This excludes concentrated industry.'),
        (['construction' + str(i) for i in range(1, 6)], [1890, 1894, 1898, 1902, 1906],
         ['Строительные артели', 'Паровые строительные машины', 'Стальные конструкции', 'Стандартизация строительства', 'Крупные инженерные работы'],
         ['Construction Guilds', 'Steam Construction Machinery', 'Structural Steel', 'Standardized Construction', 'Large Engineering Works'],
         'Подготовка инженеров, механизация работ и стандартные проекты ускоряют строительство и восстановление островной инфраструктуры.',
         'Trained engineers, mechanical equipment and standard plans accelerate construction and repairs across the islands.'),
        (['excavation' + str(i) for i in range(1, 6)], [1890, 1894, 1898, 1902, 1906],
         ['Геологические экспедиции', 'Паровые шахтные насосы', 'Механизация рудников', 'Обогащение руды', 'Глубокие шахты'],
         ['Geological Expeditions', 'Steam Mine Pumps', 'Mechanized Mines', 'Ore Beneficiation', 'Deep Mining'],
         'Разведка месторождений, откачка воды и переработка руды увеличивают доступные запасы стратегического сырья.',
         'Prospecting, drainage and ore processing increase the supply of strategic raw materials.'),
        (['fuel_refining' + (str(i) if i > 1 else '') for i in range(1, 6)], [1890, 1894, 1898, 1902, 1906],
         ['Перегонка нефти', 'Очистка нефтяных фракций', 'Промышленный мазут', 'Термическая переработка нефти', 'Нефтеперерабатывающие комплексы'],
         ['Petroleum Distillation', 'Petroleum Purification', 'Industrial Fuel Oil', 'Thermal Oil Processing', 'Refining Complexes'],
         'Улучшенная переработка нефти обеспечивает флот топливом. Она не заменяет отдельную разработку корабельных двигателей.',
         'Improved petroleum processing supplies the fleet with fuel. Ship engines remain a separate research problem.'),
        (['oil_processing', 'improved_oil_processing', 'advanced_oil_processing', 'modern_oil_processing'], [1902, 1906, 1910, 1914],
         ['Опытные химические заводы', 'Переработка угольных смол', 'Каталитические процессы', 'Комплексная нефтехимия'],
         ['Experimental Chemical Works', 'Coal Tar Processing', 'Catalytic Processes', 'Integrated Petrochemistry'],
         'Развитие экспериментальной химической промышленности увеличивает выход топлива из переработанного сырья.',
         'Experimental chemical industry improves fuel yields from processed raw materials.'),
        (['rubber_processing', 'improved_rubber_processing', 'advanced_rubber_processing', 'modern_rubber_processing'], [1906, 1910, 1914, 1918],
         ['Опыты с эластомерами', 'Лабораторный искусственный каучук', 'Промышленный искусственный каучук', 'Специализированные эластомеры'],
         ['Elastomer Experiments', 'Laboratory Artificial Rubber', 'Industrial Artificial Rubber', 'Specialized Elastomers'],
         'Искусственные эластомеры — дорогая поздняя альтернатива природному каучуку. Плантации остаются стратегическим преимуществом архипелага.',
         'Artificial elastomers are a costly late alternative to natural rubber. Plantations remain a strategic advantage of the archipelago.'),
    ]
    for keys, years, rus, ens, dr, de in groups:
        for key, year, ru, en in zip(keys, years, rus, ens):
            add(key, year, ru, en, dr, de)
    for row in [
        ('flexible_line', 1906, 'Универсальные сборочные мастерские', 'Flexible Assembly Workshops'),
        ('streamlined_line', 1906, 'Специализированные сборочные линии', 'Specialized Assembly Lines'),
        ('improved_equipment_conversion', 1898, 'Арсенальная переделка вооружения', 'Arsenal Equipment Conversion'),
        ('advanced_equipment_conversion', 1902, 'Стандартизированная переделка вооружения', 'Standardized Equipment Conversion'),
        ('fuel_silos', 1890, 'Нефтяные резервуары', 'Petroleum Storage Tanks'),
        ('synth_oil_experiments', 1898, 'Углехимические лаборатории', 'Coal Chemistry Laboratories'),
    ]:
        add(*row, 'Инженерные методы адаптированы к ограниченным ресурсам островного мира. Эффекты исследования указаны ниже.',
            'Engineering methods adapted to the limited resources of the island world. Research effects are listed below.')

    text = (game / 'common/technologies/industry.txt').read_text(encoding='utf-8-sig')
    matches = list(re.finditer(r'^\t([a-z_0-9]+) = \{', text, re.M))
    assert {m[1] for m in matches} == set(records), 'Game industry IDs changed; review before generating'
    for m in reversed(matches):
        end = block_end(text, text.index('{', m.start()))
        body = text[m.start():end]
        year = records[m[1]]['year']
        if not re.search(r'start_year\s*=', body):
            body = body[:body.index('{') + 1] + f'\n\t\tstart_year = {year}' + body[body.index('{') + 1:]
        body = re.sub(r'(start_year\s*=\s*)\d+', lambda x: x[1] + str(year), body)
        body = re.sub(r'(date\s*>\s*"?)19\d{2}(\.\d+\.\d+)', lambda x: x[1] + str(year) + x[2], body)
        # Smaller cumulative bonuses for a fragmented economy. Keep unlocks,
        # resource mechanics, XOR and all IDs compatible with existing content.
        for modifier in ('production_factory_max_efficiency_factor', 'industrial_capacity_factory',
                         'industrial_capacity_dockyard', 'production_speed_buildings_factor', 'local_resources_factor'):
            body = re.sub(r'(' + modifier + r'\s*=\s*)(0\.1[05]?)\b', lambda x: x[1] + '0.05', body)
        text = text[:m.start()] + body + text[end:]
    target = ROOT / 'common/technologies/industry.txt'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('# 1893 industry module; see docs/RESEARCH_INDUSTRY.md\n' + text, encoding='utf-8')
    for lang, field in [('russian', 'ru'), ('english', 'en')]:
        lines = ['l_' + lang + ':']
        for key, rec in records.items():
            lines += [f' {key}:0 "{rec[field]}"', f' {key}_desc:0 "{rec["desc_" + field]}"']
        (ROOT / f'localisation/{lang}/zzzzzzzzzz_research_industry_l_{lang}.yml').write_text('\n'.join(lines) + '\n', encoding='utf-8-sig')
    # Change only the industry's printed years; other tabs remain vanilla.
    gui = (game / 'interface/countrytechtreeview.gui').read_text(encoding='utf-8-sig')
    pos = gui.index('name = "industry_folder"')
    start = gui.rfind('containerWindowType', 0, pos)
    opening = gui.index('{', start)
    end = block_end(gui, opening)
    body = gui[start:end]
    year_map = {'1936': '1890', '1937': '1894', '1939': '1898', '1941': '1902', '1943': '1906', '1945': '1910'}
    body = re.sub(r'(text\s*=\s*")(19\d{2})(")', lambda m: m[1] + year_map.get(m[2], m[2]) + m[3], body)
    (ROOT / 'interface/countrytechtreeview.gui').write_text(gui[:start] + body + gui[end:], encoding='utf-8')
    (ROOT / 'tools/industry_research_manifest.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Built {len(records)} industry technologies and RU/EN localisation.')


if __name__ == '__main__':
    if (ROOT / 'tools/great_war_research_manifest.json').exists():
        raise SystemExit('Retired: the full Great War research integration supersedes this first industry module. See docs/RESEARCH_AND_WARFARE.md.')
    parser = argparse.ArgumentParser()
    parser.add_argument('--game', type=Path, required=True)
    build(parser.parse_args().game)
