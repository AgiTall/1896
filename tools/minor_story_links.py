"""Idempotent chronology overlays for Hawaiian institutions and Sulu consent."""
from pathlib import Path
import json,re
from british_story_links import emit,nodes
from validate_philippines_rework import value

ROOT=Path(__file__).resolve().parents[1]

def write(path,text,bom=False):
    (ROOT/path).write_text(text.rstrip()+'\n',encoding='utf-8-sig' if bom else 'utf-8')

def sync():
    if not (ROOT/'common/national_focus/MNR_PHW.txt').exists():return
    script='''MNR_hawaii_apply_route = {
 if = { limit = { tag = PHW has_country_flag = MNR_hawaii_succession }
  if = { limit = { has_country_flag = MNR_civic NOT = { has_country_flag = MNR_hawaii_civic_installed } }
   set_country_flag = MNR_hawaii_civic_installed
   create_country_leader = { name = MNR_hawaii_crown_council ideology = despotism expire = "1965.1.1" traits = {} }
   set_popularities = { neutrality = 70 democratic = 30 } set_politics = { ruling_party = neutrality elections_allowed = yes } drop_cosmetic_tag = yes
  }
  else_if = { limit = { OR = { has_country_flag = MNR_command has_country_flag = MNR_hawaii_naval_policy } NOT = { has_country_flag = MNR_civic } NOT = { has_country_flag = MNR_hawaii_command_installed } }
   set_country_flag = MNR_hawaii_command_installed
   create_country_leader = { name = MNR_hawaii_naval_council ideology = despotism expire = "1965.1.1" traits = {} }
   set_popularities = { neutrality = 70 democratic = 30 } set_politics = { ruling_party = neutrality elections_allowed = no } drop_cosmetic_tag = yes
  }
 }
}
MNR_hawaii_succession = {
 if = { limit = { tag = PHW date > 1894.4.29 NOT = { has_country_flag = MNR_hawaii_succession } }
  set_country_flag = MNR_hawaii_succession
  if = { limit = { has_character = PHW_canon_leader } retire_character = PHW_canon_leader }
  if = { limit = { NOT = { MNR_has_route = yes } NOT = { has_country_flag = MNR_hawaii_naval_policy } }
   create_country_leader = { name = CH94_hawaii_council ideology = liberalism expire = "1965.1.1" traits = {} }
   set_popularities = { democratic = 70 neutrality = 30 } set_politics = { ruling_party = democratic elections_allowed = yes } set_cosmetic_tag = PHW_REPUBLIC
  }
  add_stability = 0.05
 }
 MNR_hawaii_apply_route = yes
}
MNR_hawaii_naval_succession = {
 if = { limit = { NOT = { has_country_flag = MNR_civic } NOT = { has_country_flag = MNR_hawaii_succession } } set_country_flag = MNR_hawaii_naval_policy }
 MNR_hawaii_succession = yes
}
MNR_hawaii_constitutional_review = {
 if = { limit = { tag = PHW date > 1895.2.19 NOT = { has_country_flag = CH95_hawaii_settled } }
  MNR_hawaii_succession = yes set_country_flag = CH95_hawaii_settled add_stability = 0.03 add_political_power = 20
 }
}
'''
    write('common/scripted_effects/MNR_story.txt',script)
    aliases={1894:{'CH94_hawaiian_republic':'MNR_hawaii_succession = yes','CH94_hawaiian_succession':'MNR_hawaii_naval_succession = yes',
      'CH94_sulu_cooperation':'''if = { limit = { country_exists = A10 } give_military_access = A10 A10 = { give_military_access = PSL } }
 if = { limit = { has_country_flag = MNR_command is_subject = no country_exists = A03 country_exists = A10 A10 = { has_war_with = A03 } NOT = { has_war_with = A03 } NOT = { is_in_faction_with = A03 } }
 create_wargoal = { type = puppet_wargoal_focus target = A03 } }
 add_war_support = 0.05'''},
      1895:{'CH95_hawaii_republic':'MNR_hawaii_constitutional_review = yes','CH95_hawaii_regency':'MNR_hawaii_constitutional_review = yes'}}
    for year,replacements in aliases.items():
        path=f'common/scripted_effects/chronicle_{year}.txt';tree=nodes((ROOT/path).read_text(encoding='utf-8-sig'))
        for k,o,v in tree:
            if k in replacements:v[:]=nodes(replacements[k])
        write(path,emit(tree))
    path='events/chronicle_1894.txt';tree=nodes((ROOT/path).read_text(encoding='utf-8-sig'))
    event=next(v for k,o,v in tree if k=='country_event' and value(v,'id')=='ch94.12')
    opts=[v for k,o,v in event if k=='option']
    for n,opt in enumerate(opts):
        opt[:]=[e for e in opt if e[0] not in ('trigger','add_stability','add_war_support','add_timed_idea')]
        opt.append(('trigger','=',nodes('NOT = { has_country_flag = MNR_'+('command' if n==0 else 'civic')+' }')))
    # Canon remains the republic unless a focus has committed to naval government.
    ai=value(opts[1],'ai_chance');ai[:]=nodes('factor = 0 modifier = { add = 100 has_country_flag = MNR_command }')
    write(path,emit(tree))
    from apply_chronicle_revision import localization
    localization(1894,{
      'ch94.12.d':'30 апреля 1894 года умер Калакауа. Выбранные ранее учреждения определяют преемственность: конституционная корона сохраняется при совете, морское правительство передаёт власть капитанам. Без принятого курса возможно провозглашение республики.',
      'ch94.12.a':'Подтвердить гражданскую преемственность', 'ch94.12.b':'Передать преемственность морскому совету',
      'ch94.12.news_a':'После смерти Калакауа на Гавайях подтверждён гражданский порядок. Конституционная корона сохраняется, если её хартия принята; иначе действует республиканский совет.',
      'ch94.12.news_b':'После смерти Калакауа власть на Гавайях принимает морской совет. Положение легионеров не меняет суверенитет архипелага.',
      'ch94.26.a':'Сотрудничать с Конфедерацией без автоматического вступления в войну',
      'ch94.26.d':'Султан Сулу рассматривает сотрудничество с Филиппинской конфедерацией. Обмен доступом не означает вступления в её войны. При выбранном вооружённом курсе можно подготовить цель войны против Японии; объявление войны требует отдельного решения.'})
    localization(1895,{
      'ch95.4.t':'Гавайский конституционный пересмотр','ch95.4.continued_t':'Гавайский конституционный пересмотр',
      'ch95.4.d':'Правительство Гавайев проверяет порядок преемственности после смерти Калакауа в апреле 1894 года. Пересмотр укрепляет действующие учреждения и не заменяет выбранную власть.',
      'ch95.4.continued_d':'После прошлогодней преемственности Гавайи уточняют полномочия совета и бюджетные правила. Принятый политический путь сохраняется.',
      'ch95.4.a':'Подтвердить действующую конституцию','ch95.4.b':'Уточнить полномочия действующего совета',
      'ch95.4.news_a':'Гавайское правительство завершило конституционный пересмотр, сохранив избранный порядок власти.',
      'ch95.4.news_b':'На Гавайях уточнены полномочия действующего совета без новой смены режима.'})
    path='tools/chronicle_1895_manifest.json';rows=json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
    next(p for p in rows if p['id']==4)['title']='Гавайский конституционный пересмотр'
    write(path,json.dumps(rows,ensure_ascii=False,indent=2))
    for language,labels in {'russian':{'MNR_hawaii_crown_council':'Совет гавайской короны','MNR_hawaii_naval_council':'Гавайский морской совет','MNR_route_survey':'Обследование местных маршрутов','SEN_science':'Научная готовность'},'english':{'MNR_hawaii_crown_council':'Council of the Hawaiian Crown','MNR_hawaii_naval_council':'Hawaiian Maritime Council','MNR_route_survey':'Local Route Survey','SEN_science':'Scientific Readiness'}}.items():
        write(f'localisation/{language}/MNR_story_l_{language}.yml','l_'+language+':\n'+'\n'.join(f' {k}:0 "{v}"' for k,v in labels.items()),True)

if __name__=='__main__':sync()
