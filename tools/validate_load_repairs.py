"""Regression checks for the errors in the 2026-10-11 engine log."""
import json
import re
import validate_expansion as v

R=v.R
tree=v.parse(v.read('common/decisions/A03_wartime_operations.txt'))
categories={k:body for p in (R/'common/decisions/categories').glob('*.txt') for k,op,body in v.parse(p.read_text(encoding='utf-8-sig'))}
decisions={k:body for category,op,body in tree for k,op,body in body}
for category,op,body in tree:
    assert category in categories, ('Unregistered decision category',category)

def no_effects_in_trigger(node):
    for key,op,body in node:
        assert key not in ['add_days_mission_timeout','recruit_character','add_manpower','country_event'],('Effect in trigger',key)
        if isinstance(body,list):no_effects_in_trigger(body)

for body in decisions.values():
    for key in ['available','visible','allowed']:
        no_effects_in_trigger(v.value(body,key,[]))

class WartimeModel(v.Model):
    def run(self,node,tag='A01'):
        # The regression concerns clocks; manpower is unrelated to their timing.
        super().run([entry for entry in node if entry[0]!='add_manpower'],tag)

m=WartimeModel();m.war=True
m.run(v.effects['A01_start_expansion_campaign_effect'])
for ident,days in [('A03_rush_second_wave',225),('A03_mobilize_reserves',255),('A03_imperial_press_campaign',275)]:
    m.run(v.value(decisions[ident],'complete_effect'),'A03')
    assert m.missions['A01']['A01_japanese_expansion']==days
    assert m.missions['A03']['A03_japanese_expansion']==days
available=v.value(decisions['A01_request_japanese_terms'],'available')
assert not m.condition(available,'A01'),'Peace request requires a Japanese foothold'
m.controlled_provinces={min(v.borneo_provinces)}
assert m.condition(available,'A01')
m.flags['A01'].add('A01_peace_terms_requested')
assert not m.condition(available,'A01'),'Pending request must not be repeated'

events=v.parse(v.read('events/a01_peace_request.txt'))
for lang in ['russian','english']:
    text='\n'.join(p.read_text(encoding='utf-8-sig') for p in (R/'localisation'/lang).glob('*.yml'))
    keys=set(re.findall(r'^\s+([^\s:#]+):',text,re.M))
    for category,op,body in tree:
        assert category in keys and category+'_desc' in keys
    for ident in decisions: assert ident in keys and ident+'_desc' in keys
    for key,op,event in events:
        if key!='country_event':continue
        for field in ['title','desc']:assert v.value(event,field) in keys
        for key,op,option in event:
            if key=='option':assert v.value(option,'name') in keys

assert (R/'localisation/russian/1896_main_l_russian.yml').read_bytes().startswith(b'\xef\xbb\xbf')
assert not re.search(r'\brecruit_character\s*=',v.read('common/scripted_effects/A01_colonial_constraints.txt'))
assert not re.search(r'\bstart_resistance\s*=\s*CRO',v.read('history/states/163-Dalmatia.txt'))
report={'status':'passed','checks':['Registered wartime and peace-request categories','No effects in decision conditions','45/30/20-day extensions keep both clocks synchronised','Peace-request conditions and repeat guard','RU/EN decision and peace-event labels','Sabah localisation BOM','History-only admiral recruitment','Removed invalid Croatian resistance'],'engine_reload':'Not performed; the access violation is not proven fixed.'}
(R/'tools/load_repairs_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
