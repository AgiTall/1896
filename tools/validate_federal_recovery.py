"""Execute financial and election transitions; audit the new constitutional gates."""
from pathlib import Path
import copy,re
from add_canon_countries import parse,value
R=Path(__file__).resolve().parents[1]
def tree(p):return parse((R/p).read_text(encoding='utf-8-sig'))
fs={value(n,'id'):n for k,o,n in value(tree('common/national_focus/a01_focus.txt'),'focus_tree') if k=='focus'}
effects=dict((k,v) for k,o,v in tree('common/scripted_effects/A01_federal_recovery.txt'))
events={value(n,'id'):n for p in (R/'events').glob('*.txt') for k,o,n in parse(p.read_text(encoding='utf-8-sig')) if k=='country_event'}
class Ledger:
 def __init__(self):
  self.flags=set();self.vars={'A01_wtc_debt':20};self.ideas={'A01_borneo_state_loan','A01_borneo_debt_service'};self.party=None;self.leader=None
 def cond(self,n):
  results=[]
  for k,o,v in n:
   if k=='NOT':r=not self.cond(v)
   elif k=='has_country_flag':r=v in self.flags
   else:raise AssertionError(('unmodelled condition',k))
   results.append(r)
  return all(results)
 def run(self,n):
  for k,o,v in n:
   if k in effects:self.run(effects[k])
   elif k=='if':
    if self.cond(value(v,'limit')):self.run([e for e in v if e[0]!='limit'])
   elif k=='set_country_flag':self.flags.add(v)
   elif k=='clr_country_flag':self.flags.discard(v)
   elif k=='set_variable':self.vars.update({a:float(c) for a,b,c in v})
   elif k=='add_ideas':self.ideas.add(v)
   elif k=='remove_ideas':self.ideas.discard(v)
   elif k=='add_country_leader_role':self.leader=value(v,'character')
   elif k=='promote_character':self.leader=value(v,'character')
   elif k=='set_party_name':self.party=value(v,'long_name')
   elif k in ['name','ai_chance','recruit_character','set_politics','set_popularities']:pass
   else:raise AssertionError(('unmodelled effect',k))

initial=Ledger();initial.run(effects['A01_initialize_postwar_accounts_effect'])
assert initial.vars['A01_reconstruction_costs']==40 and initial.vars['A01_family_compensation_costs']==20
assert {'A01_postwar_destruction','A01_unpaid_families','A01_postwar_budget_burden'}<=initial.ideas
initial.vars['A01_reconstruction_costs']=17
initial.run(effects['A01_initialize_postwar_accounts_effect'])
assert initial.vars['A01_reconstruction_costs']==17,'Initialization must not reset existing repayments'
m=copy.deepcopy(initial);m.flags.add('A01_borneo_self_contract');m.run(effects['A01_settle_postwar_accounts_effect'])
assert all(m.vars[k]==0 for k in ['A01_wtc_debt','A01_reconstruction_costs','A01_family_compensation_costs'])
assert not {'A01_postwar_destruction','A01_unpaid_families','A01_postwar_budget_burden','A01_borneo_state_loan','A01_borneo_debt_service'}&m.ideas
assert 'A01_families_compensated' in m.flags and 'A01_borneo_self_contract' not in m.flags
before=copy.deepcopy(m.__dict__);m.run(effects['A01_settle_postwar_accounts_effect']);assert before==m.__dict__
m=copy.deepcopy(initial);m.run(effects['A01_clear_wtc_debt_effect'])
assert m.vars['A01_wtc_debt']==0 and 'A01_postwar_destruction' in m.ideas,'Debt redemption cannot silently repair ports'
wtc=value(fs['A01_wtc_recovery_agreement'],'available')
assert 'A01_wtc_oil_and_rubber_offer' in str(wtc) and 'country_exists' in str(wtc)
for fid in ['A01_repair_ports','A01_families_compensation','A01_public_recovery_fund']:
 assert value(value(fs[fid],'bypass'),'has_country_flag')=='A01_wtc_recovery_financed'
def parents(fid):return [{v for k,o,v in p if k=='focus'} for a,b,p in fs[fid] if a=='prerequisite']
assert {'A01_joint_officer_schools'} in parents('A01_federal_defence_command')
assert {'A01_civilian_defence_ministry'} in parents('A01_federal_defence_command')
assert {'A01_abolish_admirals_council'} in parents('A01_federal_constitution')
assert any(k=='remove_dynamic_modifier' and value(v,'modifier')=='A01_admirals_council' for k,o,v in value(fs['A01_abolish_admirals_council'],'completion_reward'))
assert {'A01_electoral_commission'} in parents('A01_first_federal_election')
assert {'A01_legalise_federal_parties'} in parents('A01_first_federal_election')
federation=effects['A01_create_democratic_federation_effect']
assert value(value(federation,'set_politics'),'elections_allowed')=='no'
subjects=value(federation,'every_subject_country')
assert 'A11' in str(value(subjects,'limit')) and 'A14' in str(value(subjects,'limit'))
assert value(value(value(subjects,'A01'),'annex_country'),'target')=='PREV'
election=events['A01_postwar.3']
assert 'NOT' in str(value(election,'trigger')) and 'A01_first_election_held' in str(value(election,'trigger'))
assert value(value(value(election,'immediate'),'set_politics'),'elections_allowed')=='yes'
victories=['A01_liberal_victory','A01_conservative_victory','A01_peoples_party_victory']
for suffix,party,fid in zip('abc',['liberal','conservative','peoples'],victories):
 m=Ledger();m.run(value(election,'immediate'))
 opt=next(v for k,o,v in election if k=='option' and value(v,'name')=='A01_postwar.3.'+suffix)
 m.run(opt)
 assert {f for f in ['A01_liberal_election_winner','A01_conservative_election_winner','A01_peoples_election_winner'] if f in m.flags}=={f'A01_{party}_election_winner'}
 assert f'A01_{party}_election_winner' in str(value(fs[fid],'available'))
 assert {v for k,o,v in value(fs[fid],'mutually_exclusive')}==set(victories)-{fid}
 for other,n in fs.items():
  assert not any(fid in group for group in parents(other)), 'Only the first party focus was requested'
# Confirm every declared modifier is supported by the installed engine documentation.
docs=(Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md')).read_text(encoding='utf-8-sig')
for k,o,n in value(value(tree('common/ideas/A01_federal_recovery.txt'),'ideas'),'country'):
 for mod,op,amount in value(n,'modifier'):assert '## '+mod+'\n' in docs,mod
print('PASS: guarded postwar accounts, real settlement and domestic alternative, military/civilian gates, subject-only federation, three exclusive election outcomes, valid engine modifiers.')
