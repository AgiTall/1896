"""Exercise spirit aggregation and peace eligibility using actual game scripts."""
from pathlib import Path
import json,re
from add_canon_countries import parse,value
R=Path(__file__).resolve().parents[1]
def read(p):return (R/p).read_text(encoding='utf-8-sig')
def tree(p):return parse(read(p))
groups=json.loads(read('tools/spirit_categories_manifest.json'))
hidden={}
for p in (R/'common/ideas').glob('*.txt'):
 for k,o,body in value(parse(p.read_text(encoding='utf-8-sig')),'ideas'):
  if k=='hidden_ideas':hidden.update({i:n for i,o,n in body})
assert set(groups)<=hidden.keys()
assert all(value(hidden[i],'modifier')==[] for i in groups), 'Double-counting hidden modifiers'
effect=value(tree('common/scripted_effects/A01_spirit_categories.txt'),'A01_update_spirit_categories')
def aggregate(active):
 variables={};visible=set()
 def condition(body):
  results=[]
  for k,o,v in body:
   if k=='has_idea':r=v in active
   elif k=='has_dynamic_modifier':r=v in visible
   elif k=='NOT':r=not condition(v)
   elif k=='OR':r=any(condition([x]) for x in v)
   else:raise AssertionError(k)
   results.append(r)
  return all(results)
 def run(body):
  last=False
  for k,o,v in body:
   if k=='if':
    last=condition(value(v,'limit'))
    if last:run([x for x in v if x[0]!='limit'])
   elif k=='else':
    if not last:run(v)
   elif k in ('set_variable','add_to_variable'):
    ident,op,num=v[0];variables[ident]=(variables.get(ident,0) if k=='add_to_variable' else 0)+float(num)
   elif k=='add_dynamic_modifier':visible.add(value(v,'modifier'))
   elif k=='remove_dynamic_modifier':visible.discard(value(v,'modifier'))
   elif k=='force_update_dynamic_modifier':pass
   else:raise AssertionError(k)
 run(effect)
 return variables,visible
def expected(active):
 result={}
 for i in active:
  for k,v in groups[i].items():result[k]=result.get(k,0)+v
 return result
for active in [set(),set(groups),{'A01_borneo_humiliation','A01_postwar_destruction','A01_unpaid_families','A01_postwar_budget_burden'}, {'A01_borneo_humiliation','A01_postwar_budget_burden'}, {'A01_royal_absolutism','A01_direct_royal_rule','A01_royal_militarism'}, {'A01_constitutional_crown','A01_crown_parliament_idea','A01_crown_commonwealth_idea'}]:
 variables,visible=aggregate(active)
 actual={}
 for name in visible:
  for k,o,var in value(tree('common/dynamic_modifiers/A01_spirit_categories.txt'),name):
   if k not in ('enable','icon'):actual[k]=actual.get(k,0)+variables[var]
 for k,v in expected(active).items():assert abs(actual.get(k,0)-v)<1e-8,(k,v,actual)
 assert len(visible)<=4
 if active and all(i.startswith(('A01_borneo_humiliation','A01_postwar','A01_unpaid')) for i in active):assert visible=={'A01_defeat_legacy'}

triggers=dict((k,v) for k,o,v in tree('common/scripted_triggers/A10_peace.txt'))
def eligibility(controllers, owners, trigger):
 def test(body,scope='A10'):
  results=[]
  for k,o,v in body:
   if k=='OR':r=any(test([x],scope) for x in v)
   elif k=='AND':r=test(v,scope)
   elif k=='NOT':r=not test(v,scope)
   elif k in triggers:r=test(triggers[k],scope)
   elif k.isdigit():r=test(v,int(k))
   elif k=='A03':r=test(v,'A03')
   elif k=='is_controlled_by':r=controllers[scope]==v
   elif k=='is_owned_by':r=owners[scope]==v
   elif k=='controller':r=test(v,controllers[scope])
   elif k=='is_subject_of':r=scope in ('PML','PNL','PBT') and v=='A10'
   elif k=='any_controlled_state':r=any(test(v,s) for s,c in controllers.items() if c==scope)
   elif k=='state':r=scope==int(v)
   else:raise AssertionError(k)
   results.append(r)
  return all(results)
 return test(triggers[trigger])
ids=[327,623,624,625,626,627,628,1025,1026,1027,1084,1085]
owners={s:('A03' if s in (327,623,626,1027) else 'A10') for s in ids}
control={s:'A10' for s in ids}
assert eligibility(control,owners,'A10_full_archipelago_liberated')
assert not eligibility(control,owners,'A10_manila_only_liberated')
subject=dict(control);subject.update({327:'PML',623:'PNL',1027:'PBT'})
assert eligibility(subject,owners,'A10_full_archipelago_liberated')
partial=dict(control);partial.update({623:'A03',1027:'A03',626:'A03'})
assert eligibility(partial,owners,'A10_manila_only_liberated')
assert not eligibility(partial,owners,'A10_full_archipelago_liberated')
lost=dict(control);lost[626]='A03'
assert not eligibility(lost,owners,'A10_full_archipelago_liberated')
lost=dict(control);lost[327]='A03'
assert not eligibility(lost,owners,'A10_manila_only_liberated')
peace=tree('common/scripted_effects/A10_peace.txt')
full=value(peace,'A10_conclude_archipelago_peace')
partial_effect=value(peace,'A10_conclude_manila_peace')
assert 'transfer_state' not in str([x for x in partial_effect if x[0] in ('623','1027')]), 'Partial peace must preserve Japanese north'
assert [v for k,o,v in partial_effect if k=='event_target:A10_manila_recipient'] == [parse('transfer_state = 327')]
assert all(f'A10_recipient_{s}' in str(full) for s in ids)
assert 'A01' not in str(peace), 'Philippine peace must not invoke the Dutch settlement'

focuses={value(n,'id'):n for k,o,n in value(tree('common/national_focus/a01_focus.txt'),'focus_tree') if k=='focus'}
assert 'value' in str(value(focuses['A01_royal_constitution'],'available'))
assert '0.59' in str(value(focuses['A01_royal_dictatorship'],'available'))
assert 'add_research_slot' in str(value(focuses['A01_crown_commonwealth'],'completion_reward'))
assert 'arms_factory' in str(value(focuses['A01_crown_militarism'],'completion_reward'))
for p in ['events/A01_crown_struggle.txt','events/A10_peace.txt','common/decisions/A01_crown_struggle.txt','common/decisions/A10_peace.txt','common/bop/A01_crown.txt']:
 t=tree(p)
 if p.startswith('events/'):
  for k,o,n in t:
   if k!='country_event':continue
   keys=[value(n,'title'),value(n,'desc')]+[value(b,'name') for a,o,b in n if a=='option']
   for lang in ('russian','english'):
    loc='\n'.join(f.read_text(encoding='utf-8-sig') for f in (R/f'localisation/{lang}').glob('*.yml'))
    assert all(re.search(r'^\s*'+re.escape(key)+r':',loc,re.M) for key in keys),keys
print('PASS: 39 hidden components aggregate without double bonuses; recovery removes only paid consequences; full/partial/subject/lost-control peace scenarios; royal gates/rewards; event localisation.')
