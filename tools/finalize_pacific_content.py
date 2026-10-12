from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
for folder in ['common/national_focus','common/decisions','history/countries']:
    for p in (ROOT/folder).glob('*.txt'):
        if not (p.name.startswith(('a01','a03','A01','A03','pacific'))):continue
        t=p.read_text(encoding='utf-8-sig')
        for a,b in [('add_army_experience','army_experience'),('add_navy_experience','navy_experience'),('basic_medium_battery = 1','')]:t=t.replace(a,b)
        p.write_text(t,encoding='utf-8')

# Upgrade the original dynamic-spirit artwork to the generated family.
p=ROOT/'interface/A01_ideas.gfx';t=p.read_text(encoding='utf-8-sig')
for a,b in [('A01_racial_divide.dds','idea_pacific_army.dds'),('A01_oil_dependence.dds','idea_pacific_industry.dds'),('A01_admirals_council.dds','idea_pacific_batavia.dds')]:t=t.replace(a,b)
p.write_text(t,encoding='utf-8')
p=ROOT/'common/ideas/A01_ideas.txt';t=p.read_text();t=t.replace('A01_sultans_council_stability = {\n\t\t\tpicture = A01_wilhelmina','A01_sultans_council_stability = {\n\t\t\tpicture = pacific_batavia');p.write_text(t,encoding='utf-8')

old={
'constitution':('Amend the 1854 Constitution','Constitutional amendments temporarily suspend the Admirals Council restrictions. For two weeks, mobilisation, economic and trade laws may be changed without political cost.'),
'wtc_oil_and_rubber_offer':('The World Trade Chamber Offer','Guaranteed oil and rubber exports will attract investment, finance a factory and establish formal contact with the World Trade Chamber.'),
'lone_wolf_path':('The Lone Wolf Course','Batavia will pursue an independent course. Existing faction commitments will end, and future alliances will be ruled out.'),
'strengthen_ludolfs_power':('Strengthen Ludolf\u2019s Authority','Ludolf Sloot van de Beele will retain civilian control, supported by engineers, industrialists and pragmatic officials.'),
'invest_in_mass_consumer_goods':('Invest in Consumer Industries','Rubber can supply growing civilian markets as well as the armed forces. Two new factories will expand local consumer production.'),
'last_chance_to_negotiate':('One Last Negotiation','Offer Japan guaranteed resource deliveries in exchange for mutual non-aggression. The imperial council will decide whether commerce outweighs conquest.'),
'admirals_council_coup':('The Admirals Council Coup','The admirals will remove Ludolf and place Batavia under direct naval leadership. Dockyard construction and war support will receive priority.'),
'direct_naval_rule':('Direct Naval Rule','The civilian parliament will give way to naval administration. Mobilisation will accelerate and the state will pursue a firmer security policy.'),
'build_bornean_fortifications':('Fortify Northern Borneo','A permanent defensive position at Jesselton will protect the northern Bornean port against a surprise landing.'),
'prepare_bornean_logistics':('Prepare Bornean Logistics','A railway linking Jesselton, Sandakan and Tawau will carry supplies and reinforcements across Sabah.'),
'improve_bornean_fortifications':('Expand the Bornean Defences','Strengthen Jesselton and build additional coastal positions to cover the approaches to the port.'),
'open_papuan_road':('Open the Papuan Road','A road through southern New Guinea will improve overland communications. A consignment of rifles will reinforce the frontier garrisons.'),
'fortify_australian_frontier':('Fortify the Australian Frontier','Permanent positions at Merauke and Lae will protect the southern flank of our New Guinea possessions.')}
p=ROOT/'localisation/english/pacific_content_l_english.yml';t=p.read_text(encoding='utf-8-sig')
for key,(title,desc) in old.items():
    t=re.sub(r'^ A01_'+key+r'(?:_desc)?:0 .*\n','',t,flags=re.M)
    t+=f' A01_{key}:0 {json.dumps(title)}\n A01_{key}_desc:0 {json.dumps(desc)}\n'
p.write_text(t,encoding='utf-8-sig')

# Selectable countries and introductory text for the existing 1877 scenario.
p=ROOT/'common/bookmarks/the_gathering_storm.txt'; original=ROOT/'tools/backups/pacific_before/common/bookmarks/the_gathering_storm.txt'
if original.exists(): t=original.read_text(encoding='utf-8-sig')
else:
    t=p.read_text(encoding='utf-8-sig')
    # The pre-existing bookmark has one ZZZ entry; preserve it on repeat runs.
    t=re.sub(r'"A01" = \{.*?(?="ZZZ" = \{)', '', t, flags=re.S)
    original.parent.mkdir(parents=True,exist_ok=True);original.write_text(t,encoding='utf-8')
t=t.replace('"ZZZ" = {','''"A01" = {
 history = "A01_PACIFIC_START_DESC"
 ideology = neutrality
 ideas = { A01_wilhelmina }
 focuses = { A01_constitution A01_java_development A01_knil_reform }
}
"A03" = {
 history = "A03_PACIFIC_START_DESC"
 ideology = neutrality
 ideas = { }
 focuses = { A03_imperial_council A03_osaka_industry A03_naval_programme }
}
"ZZZ" = {''')
p.write_text(t,encoding='utf-8')
entries={
'A01_PACIFIC_START_DESC':('Батавия управляет богатым, но разобщённым архипелагом. Совет адмиралов ограничивает гражданскую власть, а неравенство подрывает мобилизацию. Людольфу предстоит выбрать между соглашением с местными правителями и сохранением колониального порядка. На севере Япония присматривается к нефти Борнео.','Batavia governs a wealthy but divided archipelago. The Admirals Council constrains civilian authority while inequality undermines recruitment. Ludolf must choose between an agreement with local rulers and the colonial hierarchy. To the north, Japan eyes the oil of Borneo.'),
'A03_PACIFIC_START_DESC':('Императорский двор в Киото опирается на промышленные районы западной Японии и цепь тихоокеанских баз. Кабинету предстоит выбрать торговое сближение с Батавией или южную стратегию морского ведомства. Новые заводы, подготовленная армия и сильный флот определят будущее империи.','The Kyoto imperial court relies on western Japan industry and a chain of Pacific bases. The cabinet must choose commercial cooperation with Batavia or the naval ministry southern strategy. New factories, a trained army and a strong fleet will determine the empire future.'),
'A01':('Голландская Ост-Индия','Dutch East Indies'),'A01_DEF':('Голландская Ост-Индия','the Dutch East Indies'),'A01_ADJ':('Ост-Индск.','East Indian'),
'A03':('Японская империя','Japanese Empire'),'A03_DEF':('Японская империя','the Japanese Empire'),'A03_ADJ':('Японск.','Japanese')}
for lang,i in [('russian',0),('english',1)]:
    p=ROOT/f'localisation/{lang}/pacific_start_l_{lang}.yml'
    p.write_text('l_'+lang+':\n'+''.join(f' {key}:0 {json.dumps(v[i],ensure_ascii=False)}\n' for key,v in entries.items()),encoding='utf-8-sig')
print('Final script syntax, original spirit art, English legacy focus text and bookmark entries updated.')

p=ROOT/'events/pacific_diplomacy.txt';t=p.read_text()
t=re.sub(r'non_aggression_pact = (A0[13])',r'diplomatic_relation = { country = \1 relation = non_aggression_pact }',t)
p.write_text(t,encoding='utf-8')
p=ROOT/'common/national_focus/a03_focus.txt';t=p.read_text()
t=t.replace('completion_reward = { declare_war_on =', 'completion_reward = { load_oob = "A03_borneo_invasion" declare_war_on =')
p.write_text(t,encoding='utf-8')
