"""Connect social support, named premiers and lasting cabinet programmes."""
from pathlib import Path
import json,re
from add_canon_countries import parse,value,dump
R=Path(__file__).resolve().parents[1]
def read(p):return (R/p).read_text(encoding='utf-8-sig')
def save(p,s):(R/p).write_text(s,encoding='utf-8-sig' if p.endswith('.yml') else 'utf-8')
tree=parse(read('common/national_focus/a01_focus.txt'));body=value(tree,'focus_tree')
fs={value(n,'id'):n for k,o,n in body if k=='focus'}
if 'A01_cabinet_open_budget' in fs:raise SystemExit('Already refined.')
value(fs['A01_island_compact'],'available') if any(k=='available' for k,o,v in fs['A01_island_compact']) else fs['A01_island_compact'].append(('available','=',[]))
value(fs['A01_island_compact'],'available').extend(parse('check_variable = { A01_sultan_confidence > 2 }'))
value(fs['A01_purge_the_admiralty'],'completion_reward').extend(parse('retire_character = A01_casembroot'))
p='common/scripted_effects/A01_royal_story.txt';s=read(p)
s=s.replace('set_variable = { A01_vote_indonesian = 3 }','set_variable = { A01_vote_indonesian = 3 }\n  add_to_variable = { var = A01_vote_indonesian value = A01_civic_support }')
save(p,s)
programmes=[
('A01_cabinet_open_budget','A01_pm_constitutional_winner','Открытый бюджет ван Рейна','Van Rijn’s Open Budget','Государственные расходы станут предметом открытого парламентского отчёта. Кабинет направит средства в гражданские предприятия и королевские инженерные школы.','Public parliamentary accounts direct investment towards civilian enterprises and the royal engineering schools.',26,'academy','add_political_power = 50 add_tech_bonus = { name = A01_cabinet_open_budget bonus = 0.5 uses = 1 category = industry }'),
('A01_cabinet_princely_budget','A01_pm_order_winner','Морской бюджет ван дер Велде','Van der Velde’s Naval Budget','Партия порядка сочетает гарантии султанским дворам с заказами верфям. Капитаны получат средства, но политическое вето Совета не вернётся.','The Order Party combines princely guarantees with shipyard orders while keeping the Council’s political veto abolished.',30,'navy','navy_experience = 25 add_tech_bonus = { name = A01_cabinet_princely_budget bonus = 0.5 uses = 1 category = naval_equipment }'),
('A01_cabinet_island_schools','A01_pm_indonesian_winner','Островные училища Радена Сурьи','Raden Surya’s Island Schools','Коалиция направит средства на подготовку учителей и инженеров. Королевские и султанские земли получат общую школьную программу при сохранении местных языков.','The coalition trains teachers and engineers through a shared curriculum on Crown and sultanate lands, preserving local languages.',34,'citizenship','army_experience = 15 add_stability = 0.03 add_tech_bonus = { name = A01_cabinet_island_schools bonus = 0.5 uses = 1 category = industry }')]
manifest=json.loads(read('tools/royal_story_manifest.json'));locs={}
ids=[p[0] for p in programmes]
for fid,flag,ru,en,desc,eng,x,art,reward in programmes:
    body.extend(parse(f'''focus = {{ id = {fid} icon = GFX_{fid} x = {x} y = 30 cost = 5
      prerequisite = {{ focus = A01_responsible_cabinet }} allow_branch = {{ has_country_flag = A01_royal_path_revealed }}
      mutually_exclusive = {{ {' '.join('focus = '+p for p in ids if p!=fid)} }}
      available = {{ has_country_flag = {flag} }} ai_will_do = {{ factor = 1 }}
      completion_reward = {{ {reward} }} }}'''))
    manifest['new_focuses'].append(fid);manifest['focus_art'][fid]=art
    locs[fid]=(ru,en);locs[fid+'_desc']=(desc,eng)
save('common/national_focus/a01_focus.txt',dump(tree)+'\n')
save('tools/royal_story_manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
s='defined_text = { name = GetA01RoyalPremier\n'
for suffix,key in [('constitutional','A01_premier_van_rijn'),('order','A01_premier_van_der_velde'),('indonesian','A01_premier_raden_surya')]:
    s+=f'text = {{ trigger = {{ has_country_flag = A01_pm_{suffix}_winner }} localization_key = {key} }}\n'
s+='text = { localization_key = A01_premier_pending }\n}\n'
save('common/scripted_localisation/A01_royal_story.txt',s)
locs.update({'A01_premier_van_rijn':('Маттейс ван Рейн','Matthijs van Rijn'),'A01_premier_van_der_velde':('Хендрик ван дер Велде','Hendrik van der Velde'),'A01_premier_raden_surya':('Раден Сурья','Raden Surya'),'A01_premier_pending':('Кабинет ещё не избран','Cabinet not yet elected')})
for lang,i in [('russian',0),('english',1)]:
    p=f'localisation/{lang}/zzzzzzzzzz_royal_story_l_{lang}.yml';s=read(p)
    # The existing parliament event now honours the constitutional division of powers.
    old=f'localisation/{lang}/zzzzzzz_monarchy_l_{lang}.yml';z=read(old)
    if i==0:
        replacements={
          'A01_monarchy.3.d':'Вильгельмина открывает первое заседание парламента Нидерландов и Индонезии. Голландские купцы, гражданские делегаты островов и представители султанских дворов спорят о бюджете и избирательном законе. Совет адмиралов больше не имеет права вето. Королева обещает назначить премьер-министра, способного получить доверие палаты.',
          'A01_monarchy.3.b':'Корона гарантирует соблюдение конституции.',
          'A01_monarchy.5.d':'После устранения Совета Вильгельмина закрепляет личную власть. Гвардия присягает короне, министры отвечают перед ней, а парламентский кабинет не создаётся. Островные хартии сохраняют силу: победа над адмиралами не отменяет договоров с султанатами.'}
        # Name the incumbent in the ballot category and in the election result.
        s=s.replace('Председатель палаты приносит результаты выборов.','Премьер-министр — §Y[Root.GetA01RoyalPremier]§!. Председатель палаты приносит результаты выборов.')
        s=s.replace('Поддержка блоков:', 'Действующий премьер-министр: §Y[Root.GetA01RoyalPremier]§!.\\nПоддержка блоков:')
        s=s.replace('Премьер-министр: Конституционный союз','Маттейс ван Рейн — Конституционный союз').replace('Премьер-министр: Партия порядка','Хендрик ван дер Велде — Партия порядка').replace('Премьер-министр: Индонезийская коалиция','Раден Сурья — Индонезийская коалиция')
        s=s.replace('Доверие дворов снижает цену земельного договора.','Островной договор требует не менее 3 доверия дворов.')
    else:
        replacements={
          'A01_monarchy.3.d':'Wilhelmina opens the first parliament of the Netherlands and Indonesia. Merchants, island civic delegates and princely envoys debate the budget and electoral law. The Admiralty Council no longer holds a veto. The Queen promises to appoint a premier who commands the chamber’s confidence.',
          'A01_monarchy.3.b':'The Crown guarantees the constitution.',
          'A01_monarchy.5.d':'After defeating the Council, Wilhelmina establishes personal rule. The Guard swears allegiance to the Crown and ministers answer to her. No parliamentary cabinet is formed. Island charters remain binding: victory over the admirals does not cancel treaties with the sultanates.'}
        s=s.replace('The speaker delivers the results.','The prime minister is §Y[Root.GetA01RoyalPremier]§!. The speaker delivers the results.')
        s=s.replace('Bloc support:', 'Incumbent prime minister: §Y[Root.GetA01RoyalPremier]§!.\\nBloc support:')
        s=s.replace('Prime Minister: Constitutional Union','Matthijs van Rijn — Constitutional Union').replace('Prime Minister: Order Party','Hendrik van der Velde — Order Party').replace('Prime Minister: Indonesian Coalition','Raden Surya — Indonesian Coalition')
        s=s.replace('Court confidence helps sustain the settlement.','The island compact requires at least 3 court confidence.')
    for key,v in replacements.items():z=re.sub(r'(?m)^\s*'+re.escape(key)+r':\d*\s+".*"$',f' {key}:0 "{v}"',z)
    save(old,z)
    s+=''.join(f' {k}:0 "{v[i]}"\n' for k,v in locs.items());save(p,s)
print('Added three named premiers, cabinet programmes and meaningful court/civic support.')
