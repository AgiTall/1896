"""Install the small Japan campaign and split localisation without losing values."""
from pathlib import Path
import re, shutil, json
R = Path(__file__).resolve().parents[1]
B = R/'tools/backups/japan_before_mini_20261019'
def backup(p):
    dest = B/p.relative_to(R)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists(): shutil.copy2(p, dest)
def write(name, text):
    p=R/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding='utf-8-sig' if name.endswith('.yml') else 'utf-8')
def install():
    p=R/'common/national_focus/a03_focus.txt'; backup(p)
    # Keep scripted effects for references from other countries; stop legacy daily plots.
    for p in (R/'common/on_actions').glob('JP*.txt'):
        backup(p); p.write_text('# Archived for the mini Japan campaign. See tools/backups/japan_before_mini_20261019.\n',encoding='utf-8')
    for p in (R/'common/decisions/categories').glob('JP*.txt'):
        backup(p)
        text=p.read_text(encoding='utf-8-sig')
        text=re.sub(r'allowed\s*=\s*\{', 'allowed = { has_country_flag = JSM_legacy_campaign_enabled ',text)
        p.write_text(text,encoding='utf-8')
    plan=R/'common/ai_strategy_plans/A01_canonical.txt'; backup(plan)
    text=plan.read_text(encoding='utf-8-sig'); pos=text.find('A03_southern_canonical_plan =')
    if pos>=0: text=text[:pos]
    text+='A03_mini_plan = { name = "Japan: industrial foundations" allowed = { original_tag = A03 } enable = { always = yes } ai_national_focuses = { JSM_steel JSM_workshops JSM_shipyards JSM_council JSM_north JSM_south JSM_ocean } }\n'
    plan.write_text(text,encoding='utf-8')
    focuses=[('steel',20,'generic_construct_civ_factory','', 'add_extra_state_shared_building_slots = 3 add_building_construction = { type = industrial_complex level = 3 instant_build = yes }',282),
      ('workshops',20,'generic_construct_mil_factory','steel','add_extra_state_shared_building_slots = 3 add_building_construction = { type = arms_factory level = 3 instant_build = yes }',531),
      ('shipyards',15,'generic_construct_naval_dockyard','workshops','add_extra_state_shared_building_slots = 2 add_building_construction = { type = dockyard level = 2 instant_build = yes }',528),
      ('council',5,'generic_national_unity','shipyards','add_political_power = 100 add_stability = 0.05',None),
      ('north',5,'generic_national_unity','council','set_country_flag = JSM_north_open',None),
      ('south',5,'generic_navy_doctrines_tactics','north','set_country_flag = JSM_south_open',None),
      ('ocean',5,'generic_navy_doctrines_tactics','south','set_country_flag = JSM_ocean_open add_war_support = 0.05',None)]
    out='focus_tree = { id = A03_focus country = { factor = 0 modifier = { add = 100 tag = A03 } } default = no continuous_focus_position = { x = 400 y = 1200 }\n'
    for y,(key,cost,icon,prev,reward,state) in enumerate(focuses):
        if state: reward=f'{state} = {{ if = {{ limit = {{ is_owned_by = ROOT }} {reward} }} }}'
        out+=f' focus = {{ id = JSM_{key} icon = GFX_goal_{icon} x = 5 y = {y*2} cost = {cost} '+(f'prerequisite = {{ focus = JSM_{prev} }} ' if prev else '')+f'ai_will_do = {{ factor = 10 }} completion_reward = {{ {reward} }} }}\n'
    write('common/national_focus/a03_focus.txt',out+'}\n')
    write('common/decisions/categories/JSM_story.txt','JSM_subordination = { icon = generic_political_discourse allowed = { original_tag = A03 } visible = { has_completed_focus = JSM_council } }\n')
    decisions='JSM_subordination = {\n'
    for target,gate in [('A08','north'),('A10','south'),('A01','ocean')]:
        decisions+=f''' JSM_offer_{target} = {{ icon = generic_political_discourse cost = 100 fire_only_once = yes days_remove = 30
 visible = {{ has_country_flag = JSM_{gate}_open country_exists = {target} {target} = {{ is_subject = no }} }}
 available = {{ has_war = no {target} = {{ has_war = no }} }}
 complete_effect = {{ log = "Japan opens a protectorate negotiation with {target}" }}
 remove_effect = {{ if = {{ limit = {{ country_exists = {target} {target} = {{ is_subject = no has_war = no }} has_war = no }} {target} = {{ country_event = {{ id = jsm_story.1 days = 1 }} }} }} }}
 ai_will_do = {{ base = 1 }} }}\n'''
    write('common/decisions/JSM_story.txt',decisions+'}\n')
    write('events/JSM_story.txt','''add_namespace = jsm_story
country_event = { id = jsm_story.1 title = JSM_offer_title desc = JSM_offer_desc is_triggered_only = yes
 option = { name = JSM_accept ai_chance = { factor = 60 } A03 = { puppet = ROOT } }
 option = { name = JSM_refuse ai_chance = { factor = 40 } A03 = { create_wargoal = { type = puppet_wargoal_focus target = ROOT } } }
}
''')
    ru=[('steel','Сталь для новой Японии','Казённые инвестиции в металлургию дадут три гражданские фабрики в столичной области. 140 дней.'),('workshops','Императорские мастерские','Стандартизация станков и оружейных заказов: три военных завода в Осаке. 140 дней.'),('shipyards','Верфи Нагасаки','Две новые верфи обеспечат морскую опору будущих договоров. 105 дней.'),('council','Совет императорской политики','Промышленная основа готова. Совет определит последовательность предложений о протекторате.'),('north','Северный договор','Открывает переговоры о подчинении северного соседа. Решение стоит 100 политической власти и занимает 30 дней.'),('south','Посольство на Филиппины','Открывает предложение японского протектората Филиппинам.'),('ocean','Порядок южных морей','Открывает переговоры с Нидерландской Индией. Отказ даст цель войны на подчинение.')]
    for lang in ('russian','english'):
        lines=['l_'+lang+':']
        for key,title,desc in ru:
            if lang=='english': title={'steel':'Steel for a new Japan','workshops':'Imperial workshops','shipyards':'Nagasaki shipyards','council':'Imperial policy council','north':'The northern treaty','south':'Embassy to the Philippines','ocean':'Order in the southern seas'}[key]; desc={'steel':'140 days. Adds three civilian factories in the capital region.','workshops':'140 days. Adds three military factories in Osaka.','shipyards':'105 days. Adds two dockyards in Nagasaki.'}.get(key,'Opens protectorate negotiations. Offers cost 100 political power and take 30 days. Refusal grants a puppet war goal.')
            lines.extend([f' JSM_{key}:0 "{title}"',f' JSM_{key}_desc:0 "{desc}"'])
        pairs={'JSM_subordination':('Императорская дипломатия','Imperial diplomacy'),'JSM_offer_title':('Предложение японского протектората','A Japanese protectorate'),'JSM_offer_desc':('Токио предлагает признать японское верховенство. Согласие сохранит местную администрацию под властью Японии; отказ даст Японии цель войны на подчинение.','Tokyo offers a protectorate. Acceptance places our country under Japan. Refusal grants Japan a puppet war goal.'),'JSM_accept':('Принять условия','Accept the terms'),'JSM_refuse':('Отстоять независимость','Defend our independence')}
        for tag,name,en in [('A08','Северный договор','Northern treaty'),('A10','Протекторат над Филиппинами','Philippine protectorate'),('A01','Протекторат над Нидерландской Индией','East Indies protectorate')]:
            pairs['JSM_offer_'+tag]=(name,en); pairs['JSM_offer_'+tag+'_desc']=('Переговоры займут 30 дней. Согласие создаст японскую марионетку; отказ даст цель войны.','Negotiations take 30 days. Acceptance creates a Japanese puppet; refusal grants a war goal.')
        for k,v in pairs.items(): lines.append(f' {k}:0 "{v[lang=="english"]}"')
        write(f'localisation/{lang}/JSM_story_l_{lang}.yml','\n'.join(lines)+'\n')
    from focus_shapes import apply as apply_shapes
    apply_shapes()
if __name__=='__main__': install()
