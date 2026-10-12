"""Playable follow-through decisions for the three national doctrines."""
from pathlib import Path
from add_canon_countries import parse,value,dump
R=Path(__file__).resolve().parents[1]
def read(p):return (R/p).read_text(encoding='utf-8-sig')
def save(p,s):(R/p).write_text(s,encoding='utf-8-sig' if p.endswith('.yml') else 'utf-8')
p='common/decisions/A01_royal_story.txt';t=parse(read(p));cat=value(t,'A01_royal_institutions')
if any(k=='A01_open_seas_convention' for k,o,v in cat):raise SystemExit('Already applied.')
subjects='every_subject_country = { limit = { OR = { tag = A11 tag = A12 tag = A13 tag = A14 } } '
new=[
('A01_open_seas_convention','Конвенция общего торгового моря','Common Trading Sea Convention',
'Согласовать портовые правила султанатов и короны. Вклады в гражданские предприятия дадут одну фабрику в столице и политическую поддержку автономных партнёров. Доступно один раз.','Coordinate Crown and sultanate port rules. Civilian investment builds a capital factory and strengthens autonomous partners. Available once.',75,'has_completed_focus = A01_open_seas_kingdom',
'capital_scope = { add_extra_state_shared_building_slots = 1 add_building_construction = { type = industrial_complex level = 1 instant_build = yes } } '+subjects+'add_stability = 0.03 add_political_power = 25 }'),
('A01_exile_volunteer_register','Открыть реестр добровольцев изгнания','Open the Exile Volunteer Register',
'Архивы беженцев помогут найти подготовленных добровольцев. Государство получит 6000 людских ресурсов и 20 армейского опыта; эта программа проводится один раз.','Refugee records help recruit trained volunteers. Gain 6,000 manpower and 20 army experience. Available once.',60,'has_completed_focus = A01_homeland_in_exile','add_manpower = 6000 army_experience = 20'),
('A01_archipelago_naval_exercises','Общие манёвры архипелага','Joint Archipelago Manoeuvres',
'Штаб короны и султанские командиры отработают защиту проливов. Мы получим 20 морского опыта, каждый автономный султанат — 10. Доступно один раз.','Crown and sultanate staffs practise strait defence. Gain 20 navy experience; autonomous sultanates gain 10 each. Available once.',50,'has_completed_focus = A01_archipelago_great_power','navy_experience = 20 '+subjects+'navy_experience = 10 }'),
('A01_review_charter_courts','Совместная ревизия островных судов','Joint Review of Island Courts',
'Проверить исполнение хартий гражданскими и княжескими судьями. Устранение произвольных поборов укрепит стабильность страны и автономных султанатов. Доступно один раз.','Civic and princely judges review charter enforcement and arbitrary taxation. Improve Crown and autonomous sultanate stability. Available once.',45,'has_country_flag = A01_island_settlement','add_stability = 0.02 '+subjects+'add_stability = 0.03 }'),
]
for key,ru,en,desc,eng,cost,gate,eff in new:
    cat.extend(parse(f'{key} = {{ icon = generic_political_discourse cost = {cost} fire_only_once = yes visible = {{ {gate} }} available = {{ {gate} }} complete_effect = {{ {eff} }} ai_will_do = {{ factor = 1 }} }}'))
save(p,dump(t)+'\n')
for lang,i in [('russian',0),('english',1)]:
    p=f'localisation/{lang}/zzzzzzzzzz_royal_story_l_{lang}.yml';s=read(p)
    for key,ru,en,desc,eng,*_ in new:s+=f' {key}:0 "{(ru,en)[i]}"\n {key}_desc:0 "{(desc,eng)[i]}"\n'
    save(p,s)
print('Added national-course follow-through and charter enforcement decisions.')
