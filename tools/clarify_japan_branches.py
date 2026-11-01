"""Apply the author's politics -> military stages, with independent industry.

Run after older Japan generators. Preserves route prologues and existing rewards.
"""
from pathlib import Path
import re

R = Path(__file__).resolve().parents[1]
INDUSTRY = {'JPC_osaka_orders', 'JPC_war_workshops', 'JPC_pledged_yards',
            'JPC_convoy_budget', 'JPC_replace_losses'}
POSITIONS = {
    'JPC_osaka_orders': (2, 0), 'JPC_war_workshops': (2, 2),
    'JPC_pledged_yards': (6, 2), 'JPC_convoy_budget': (6, 3),
    'JPC_replace_losses': (2, 3),
    'JPC_manila_priority': (30, 3), 'JPL_convoy_timetable': (28, 4),
    'JPL_names_and_units': (32, 4), 'JPC_garrison_accounts': (30, 5),
    'JPL_port_and_mountains': (30, 6), 'JPL_municipal_buyers': (28, 7),
    'JPL_payroll_inquiry': (32, 7), 'JPL_supply_board': (28, 8),
    'JPL_quartermaster_school': (32, 8),
    'JPC_batavia_demands': (38, 5), 'JPX_sea_institution': (42, 5),
    'JPR_defence_budget': (24, 4),
}

def blocks(s):
    for m in re.finditer(r'\bfocus\s*=\s*\{', s):
        start = m.start(); end = m.end(); depth = 1
        while depth:
            depth += (s[end] == '{') - (s[end] == '}'); end += 1
        yield start, end, s[start:end]

def save(p, s):
    raw = p.read_bytes() if p.exists() else b''
    p.write_text(s, encoding='utf-8-sig' if p.suffix == '.yml' else 'utf-8',
                 newline='\r\n' if b'\r\n' in raw else '\n')

def apply():
    p = R/'common/national_focus/a03_focus.txt'
    s = p.read_text(encoding='utf-8-sig')
    if 'id = JPR_defence_budget' not in s:
        pos = s.rfind('}')
        s = s[:pos] + ''' focus = {
  id = JPR_defence_budget icon = GFX_goal_unique_A03_imperial_council x = 24 y = 4 cost = 3
  prerequisite = { focus = JPC_northern_protocol }
  prerequisite = { focus = JPC_state_guarantees }
  ai_will_do = { factor = 8 }
  completion_reward = { add_political_power = 25 }
 }
''' + s[pos:]
    parents = {
        'JPC_osaka_orders': '',
        'JPC_war_workshops': 'JPC_osaka_orders',
        'JPC_pledged_yards': 'JPC_osaka_orders',
        'JPC_replace_losses': 'JPC_war_workshops',
        'JPC_iwasaki_accounts': 'JPF_public_accounts focus = JPF_small_subscription',
        'JPC_manila_priority': 'JPC_northern_protocol',
        'JPC_batavia_demands': 'JPR_defence_budget',
        'JPX_sea_institution': 'JPR_defence_budget',
    }
    icons = {
        'JPC_osaka_orders': 'GFX_goal_unique_A03_industrial_power',
        'JPC_war_workshops': 'GFX_goal_unique_A03_standard_rifles',
        'JPC_pledged_yards': 'GFX_goal_unique_A03_merchant_marine',
        'JPC_convoy_budget': 'GFX_goal_unique_A01_archipelago_shipping',
    }
    for start, end, b in reversed(list(blocks(s))):
        fid = re.search(r'\bid\s*=\s*(\w+)', b)[1]
        if fid in parents:
            b = re.sub(r'\s*prerequisite\s*=\s*\{[^{}]*\}', '', b)
            if parents[fid]:
                b = b[:-1] + '\n  prerequisite = { focus = '+parents[fid]+' }\n }'
        if fid in {'JPL_supply_board', 'JPL_quartermaster_school'} and 'focus = JPR_defence_budget' not in b:
            b = b[:-1] + '\n  prerequisite = { focus = JPR_defence_budget }\n }'
        if fid in POSITIONS:
            x, y = POSITIONS[fid]
            b = re.sub(r'\bx\s*=\s*-?\d+', f'x = {x}', b, count=1)
            b = re.sub(r'\by\s*=\s*-?\d+', f'y = {y}', b, count=1)
        if fid in icons:
            b = re.sub(r'\bicon\s*=\s*\w+', 'icon = '+icons[fid], b, count=1)
        s = s[:start] + b + s[end:]
    save(p, s)

    p = R/'common/ai_strategy_plans/A01_canonical.txt'
    s = p.read_text(encoding='utf-8-sig')
    start = s.index('A03_southern_canonical_plan')
    head, tail = s[:start], s[start:]
    def plan(m):
        ids = m[1].split()
        ids = [fid for fid in ids if fid != 'JPR_defence_budget']
        ids.insert(ids.index('JPC_northern_protocol')+1, 'JPR_defence_budget')
        return 'ai_national_focuses = { '+' '.join(ids)+' }'
    tail = re.sub(r'ai_national_focuses\s*=\s*\{([^}]+)\}', plan, tail, count=1)
    save(p, head+tail)

    titles = {
        'A03_imperial_council': ('Политика: кризис трёх голов', 'Politics: Crisis of the Three Heads'),
        'JPC_osaka_orders': ('Промышленность: фабрики Хонсю', 'Industry: Honshu Factories'),
        'JPC_war_workshops': ('Строительство военных заводов', 'Build Armament Factories'),
        'JPC_pledged_yards': ('Расширение японских верфей', 'Expand Japanese Dockyards'),
        'JPC_convoy_budget': ('Строительство транспортов', 'Build Merchant Transports'),
        'JPC_replace_losses': ('Расширение военного производства', 'Expand Armament Production'),
        'JPC_northern_protocol': ('Соглашение с Северной армией', 'Agreement with the Northern Army'),
        'JPC_manila_priority': ('Армия: реформа гарнизонов', 'Army: Garrison Reform'),
        'JPC_garrison_accounts': ('Перевооружение гарнизонов', 'Rearm the Garrisons'),
        'JPC_batavia_demands': ('Флот: план южной кампании', 'Navy: Southern Campaign Plan'),
        'JPR_defence_budget': ('Политика: военный бюджет', 'Politics: Defence Budget'),
    }
    descs = {
        'JPC_osaka_orders': (
            'Развиваем гражданские фабрики в принадлежащей Токио части Хонсю. Это начало независимой промышленной ветки: она доступна с первого дня при любом политическом пути. Дальше можно отдельно строить военные заводы и верфи.',
            'Develop civilian factories in Tokyo-owned Honshu. This independent industry branch is available from day one on every political route. It leads to separate armament and dockyard programmes.'),
        'JPC_war_workshops': ('На базе гражданской промышленности построим военный завод. Политические соглашения и начало войны не требуются.', 'Build an armament factory on our civilian industrial base. No political agreement or war is required.'),
        'JPC_pledged_yards': ('Расширим собственные верфи для будущего флота. Строительство доступно и в мирное время, при любом политическом пути. Военные заказы во время войны могут вызвать отдельный счёт казначейству.', 'Expand our own dockyards for the future fleet. Construction is available in peacetime on every political route. Wartime orders may generate a separate treasury invoice.'),
        'JPC_replace_losses': ('Расширим выпуск вооружений и закажем дополнительные транспорты. Программа доступна после строительства военного завода, независимо от войны и политического курса.', 'Expand armament production and order additional transports. Available after building an armament factory, regardless of war or political route.'),
        'JPR_defence_budget': ('Северный протокол определил отношения с армией, а гарантии промышленникам — финансовую опору правительства. Теперь кабинет утверждает следующий этап военных реформ: подготовку интендантов, управление снабжением и планирование операций флота. Для этого решения не требуется ждать войны.', 'The Northern Protocol settles relations with the army; industrial guarantees underpin government finance. The cabinet can now authorize the next military reform stage: quartermaster training, supply administration and naval planning. War is not required.'),
    }
    for lang, ix in [('russian', 0), ('english', 1)]:
        p = R/f'localisation/{lang}/1896_main_l_{lang}.yml'
        l = p.read_text(encoding='utf-8-sig')
        entries = {k: v[ix] for k, v in titles.items()}
        entries.update({k+'_desc': v[ix] for k, v in descs.items()})
        for fid, label in [('JPC_northern_protocol', ('Политика — первый этап реформ армии.', 'Politics — first army reform stage.')),
                           ('JPC_manila_priority', ('Армия — первичные реформы. Открывается соглашением с Северной армией.', 'Army — initial reforms. Unlocked by the Northern Army agreement.')),
                           ('JPC_batavia_demands', ('Флот — второй этап реформ. Открывается военным бюджетом.', 'Navy — second reform stage. Unlocked by the defence budget.')),
                           ('JPL_supply_board', ('Армия — второй этап реформ. Требуется военный бюджет.', 'Army — second reform stage. Requires the defence budget.')),
                           ('JPL_quartermaster_school', ('Армия — второй этап реформ. Требуется военный бюджет.', 'Army — second reform stage. Requires the defence budget.'))]:
            m = re.search(r'^ '+fid+r'_desc:\d*\s*"(.*)"', l, re.M)
            if m and not m[1].startswith(label[ix]): entries[fid+'_desc'] = label[ix]+'\\n\\n'+m[1]
        for route in ['land', 'trade', 'kami', 'throne']:
            for suffix in ['', '_institution']:
                key = 'JPX_'+route+suffix+'_desc'
                label = ('Альтернативный путь: заготовка из двух фокусов. Продолжение пока не реализовано. Независимая промышленная ветка остаётся доступной.', 'Alternative route: a two-focus prologue. Further content is not implemented yet. The independent industry branch remains available.')[ix]
                m = re.search(r'^ '+key+r':\d*\s*"(.*)"', l, re.M)
                if m and not m[1].startswith(label): entries[key] = label+'\\n\\n'+m[1]
        for key, text in entries.items():
            line = ' '+key+':0 "'+text+'"'
            pattern = r'^ '+re.escape(key)+r':\d*\s*".*"'
            if re.search(pattern, l, re.M): l = re.sub(pattern, lambda m: line, l, flags=re.M)
            else: l = l.rstrip()+'\n'+line+'\n'
        save(p, l)
    print('Japan: independent industry, two political military stages, explicit RU/EN branch labels.')

if __name__ == '__main__':
    apply()
