"""Check independent opening deadline, agreement cancellation and postwar bypasses."""
from pathlib import Path
from datetime import date
from add_canon_countries import parse, value
R=Path(__file__).resolve().parents[1]
def read(p):return (R/p).read_text(encoding='utf-8-sig')
assert (date(1893,3,19)-date(1893,1,1)).days==77
opening=read('common/on_actions/A01_independent_preparations.txt')
clocks=read('common/scripted_effects/JPS_calendar_clocks.txt')
assert 'date > 1893.3.18' in clocks
assert 'has_completed_focus' not in opening
assert 'A01_begin_expansion_preparations_effect = yes' in clocks
assert 'pacific_trade_accord' in clocks
for p,cat,mission in [('common/decisions/A01_inevitable_conflict.txt','A01_inevitable_conflict_category','A01_japanese_invasion_countdown'),('common/decisions/A03_japanese_expansion.txt','A03_southern_preparations','A03_japanese_invasion_countdown')]:
 assert value(value(value(parse(read(p)),cat),mission),'days_mission_timeout')=='365'
assert 'on_startup' in opening and 'JPS_restore_clocks_effect = yes' in opening
assert 'JPS_align_opening_clocks_effect' in read('common/scripted_effects/JPS_calendar_clocks.txt')
effects=parse(read('common/scripted_effects/expansion_effects.txt'))
cancel=value(effects,'A01_cancel_preparations_for_agreement_effect')
assert value(value(cancel,'A01'),'remove_mission')=='A01_japanese_invasion_countdown'
assert value(value(cancel,'A03'),'remove_mission')=='A03_japanese_invasion_countdown'
def audit(node):
 if ('set_country_flag','=','pacific_trade_accord') in node:
  assert ('A01_cancel_preparations_for_agreement_effect','=','yes') in node
 for k,o,v in node:
  if isinstance(v,list):audit(v)
audit(parse(read('events/pacific_diplomacy.txt')))
focuses={value(n,'id'):n for k,o,n in value(parse(read('common/national_focus/a01_focus.txt')),'focus_tree') if k=='focus'}
count=0
for fid,n in focuses.items():
 available=next((v for k,o,v in n if k=='available'),[])
 if 'A01_before_japanese_war_tt' in str(available):
  bypass=value(n,'bypass')
  assert ('has_country_flag','=','A01_borneo_treaty') in bypass
  assert value(value(bypass,'NOT'),'has_war_with')=='A03'
  count+=1
for fid in ['A01_dutch_literacy','A01_factory_resettlement','A01_java_steam_power','A01_wtc_oil_and_rubber_offer','A01_pacific_settlement']:
 assert not any(k=='bypass' for k,o,v in focuses[fid])
print(f'PASS: hidden 77-day opening; January 1894 deadline; March mobilisation; shared calendar with save repair; agreement cancels clocks; {count} prewar focuses bypassed after defeat.')
