"""Replace optional defence activation with diplomacy-driven preparation."""
from pathlib import Path
import copy, re, shutil
from add_canon_countries import parse, value, dump
R = Path(__file__).resolve().parents[1]
def read(p): return (R/p).read_text(encoding='utf-8-sig')
def save(p,t,bom=False):
 b=R/'tools/backups/pacific_rivalry'/p;b.parent.mkdir(parents=True,exist_ok=True)
 if not b.exists():shutil.copy2(R/p,b)
 (R/p).write_text(t,encoding='utf-8-sig' if bom else 'utf-8')
def setv(n,k,v):
 n[:]=[e for e in n if e[0]!=k]+[(k,'=',v)]
def event(t,ident):return next(v for k,o,v in t if k=='country_event' and value(v,'id')==ident)
def option(n,name):return next(v for k,o,v in n if k=='option' and value(v,'name')==name)

if __name__=='__main__':
 p='common/national_focus/a01_focus.txt';t=parse(read(p));body=value(t,'focus_tree')
 fs={value(v,'id'):v for k,o,v in body if k=='focus'}
 negotiate=fs['A01_last_chance_to_negotiate']
 setv(negotiate,'x','15')
 value(negotiate,'completion_reward').extend(parse('A01_initialize_balance_effect = yes add_stability = 0.05 add_power_balance_value = { id = A01_ludolf_admirals_balance value = -0.10 }'))
 negotiate.append(('mutually_exclusive','=',parse('focus = A01_direct_rivalry')))
 rivalry=copy.deepcopy(negotiate)
 setv(rivalry,'id','A01_direct_rivalry');setv(rivalry,'x','17')
 setv(rivalry,'mutually_exclusive',parse('focus = A01_last_chance_to_negotiate'))
 setv(rivalry,'prerequisite',parse('focus = A01_strengthen_ludolfs_power focus = A01_admirals_council_coup'))
 setv(rivalry,'completion_reward',parse('A01_initialize_balance_effect = yes add_stability = -0.05 add_power_balance_value = { id = A01_ludolf_admirals_balance value = 0.10 } set_country_flag = A01_direct_rivalry_declared A03 = { country_event = { id = pacific.5 days = 2 } }'))
 body.append(('focus','=',rivalry))
 for fid,n in fs.items():
  for k,o,v in n:
   if k=='prerequisite' and ('focus','=','A01_last_chance_to_negotiate') in v:
    v.append(('focus','=','A01_direct_rivalry'))
 save(p,dump(t)+'\n')
 p='common/decisions/A01_inevitable_conflict.txt';t=parse(read(p));v=value(t,'A01_inevitable_conflict_category');v[:]=[e for e in v if e[0]!='A01_begin_island_defence'];save(p,dump(t)+'\n')
 p='events/pacific_diplomacy.txt';t=parse(read(p))
 option(event(t,'pacific.1'),'pacific.1.b').append(('A01','=',parse('A01_begin_expansion_preparations_effect = yes')))
 # An ultimatum is a separate, immediate-war path, even if the Dutch ignore their focuses.
 setv(option(event(t,'pacific.4'),'pacific.4.b'),'if',parse('limit = { NOT = { has_country_flag = A01_expansion_resolved } } set_country_flag = A01_refused_japanese_ultimatum set_country_flag = A01_island_defence_started A03 = { A03_start_southern_war_effect = yes }'))
 t.extend(parse('''country_event = {
 id = pacific.5 title = pacific.5.t desc = pacific.5.d
 picture = GFX_report_event_A01_japan_rejects_dutch_offer is_triggered_only = yes
 trigger = { tag = A03 country_exists = A01 NOT = { has_war_with = A01 } NOT = { has_country_flag = pacific_trade_accord } A01 = { NOT = { has_country_flag = A01_expansion_resolved } } }
 option = { name = pacific.5.a ai_chance = { factor = 100 }
  A01 = { A01_begin_expansion_preparations_effect = yes country_event = { id = pacific.6 days = 1 } }
 }
}
country_event = {
 id = pacific.6 title = pacific.6.t desc = pacific.6.d
 picture = GFX_report_event_A01_japan_rejects_dutch_offer is_triggered_only = yes
 trigger = { tag = A01 NOT = { has_war_with = A03 } NOT = { has_country_flag = A01_expansion_resolved } }
 option = { name = A01_japan.1.a set_country_flag = A01_refused_japanese_ultimatum country_event = { id = A01_japan.2 days = 14 random_days = 16 } }
}'''))
 save(p,dump(t)+'\n')
 p='events/A01_japan_events.txt';t=parse(read(p));option(event(t,'A01_japan.1'),'A01_japan.1.a').append(('A01_begin_expansion_preparations_effect','=','yes'));save(p,dump(t)+'\n')
 p='common/decisions/categories/A01_inevitable_conflict_categories.txt';t=parse(read(p));visible=value(value(t,'A01_inevitable_conflict_category'),'visible');visible[:]=[e for e in visible if e[0]!='has_country_flag' or e[2]!='A01_refused_japanese_ultimatum'];visible.append(('OR','=',parse('has_country_flag = A01_refused_japanese_ultimatum has_country_flag = A01_island_defence_started')));save(p,dump(t)+'\n')
 entries={
 'russian':{
 'A01_direct_rivalry':'Прямое соперничество',
 'A01_direct_rivalry_desc':'Батавия открыто оспорит японское господство на южных морях. Решительность укрепит авторитет Людольфа на 10 пунктов, но тревога перед конфликтом снизит стабильность на 5%. После ответа Токио автоматически начнётся отсчёт подготовки к вторжению.',
 'A01_last_chance_to_negotiate_desc':'Предложим Японии соглашение ради мира. Переговоры повышают стабильность на 5%, но уступчивая позиция снижает авторитет Людольфа на 10 пунктов. Отказ Токио автоматически запускает общий отсчёт подготовки к вторжению.',
 'pacific.1.b':'Они сами еле на ногах держатся.',
 'pacific.5.t':'Батавия бросает вызов',
 'pacific.5.d':'Нидерландское правительство объявило курс на прямое соперничество с Японией. Морское ведомство предлагает ответить подготовкой экспедиции на Борнео.',
 'pacific.5.a':'Они сами еле на ногах держатся.',
 'pacific.4.d':'Япония требует привилегированного доступа к сырью Борнео. Согласие сохранит мир ценой экономических уступок. Отказ означает немедленное объявление войны.',
 'pacific.4.b':'Отвергнуть ультиматум. Мы будем защищаться.',
 'A01_inevitable_conflict_category_desc':'Отказ Японии от соглашения или её ответ на объявленное соперничество автоматически запускает общий отсчёт подготовки к вторжению. Уступки могут отложить войну. Отказ от японского ультиматума означает немедленную войну. Для победы к концу кампании на Борнео не должно остаться ни одной провинции под контролем Японии.',
 'A03_batavia_ultimatum_desc':'Потребуем доступа к сырью Борнео независимо от курса Батавии. Отказ Нидерландов означает немедленную войну.'},
 'english':{
 'A01_direct_rivalry':'Direct Rivalry',
 'A01_direct_rivalry_desc':'Challenge Japanese dominance openly. Stability falls by 5%, while Ludolf gains 10 points of authority. Tokyo’s response automatically starts the shared invasion preparation countdown.',
 'A01_last_chance_to_negotiate_desc':'Offer Japan an agreement to preserve peace. Gain 5% stability at the cost of 10 points of Ludolf’s authority. Japanese rejection automatically starts the shared invasion preparation countdown.',
 'pacific.1.b':'They can barely stand on their own feet.',
 'pacific.5.t':'Batavia Issues a Challenge',
 'pacific.5.d':'The Dutch government has declared a policy of direct rivalry with Japan. The naval ministry proposes preparing a Borneo expedition in response.',
 'pacific.5.a':'They can barely stand on their own feet.',
 'pacific.4.d':'Japan demands privileged access to Borneo’s resources. Acceptance preserves peace through economic concessions. Rejection means an immediate declaration of war.',
 'pacific.4.b':'Reject the ultimatum. We will defend ourselves.',
 'A01_inevitable_conflict_category_desc':'Japanese rejection of an agreement or its response to declared rivalry automatically starts the shared invasion preparation countdown. Concessions can postpone war. Rejecting the Japanese ultimatum causes immediate war. Victory requires clearing every Japanese foothold on Borneo before the campaign deadline.',
 'A03_batavia_ultimatum_desc':'Demand access to Borneo’s resources regardless of Batavia’s political course. Dutch refusal means immediate war.'}}
 for lang,labels in entries.items():
  remaining=dict(labels)
  for p in (R/'localisation'/lang).glob('*.yml'):
   text=p.read_text(encoding='utf-8-sig');changed=False
   for key,label in labels.items():
    text,n=re.subn(r'^\s*'+re.escape(key)+r':\d* .*$',lambda m:f' {key}:0 "{label}"',text,flags=re.M)
    if n:changed=True;remaining.pop(key,None)
   if changed:save(str(p.relative_to(R)),text,True)
  p=f'localisation/{lang}/pacific_content_l_{lang}.yml'
  save(p,read(p)+'\n'+''.join(f' {k}:0 "{v}"\n' for k,v in remaining.items()),True)
