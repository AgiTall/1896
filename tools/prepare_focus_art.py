from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1]
subjects='''
A01_constitution|An open constitutional parchment with red wax seal and bronze quill
A01_wtc_oil_and_rubber_offer|Merchant balance scales weighing an oil barrel against raw rubber bales
A01_lone_wolf_path|A lone silver wolf head over a maritime compass
A01_strengthen_ludolfs_power|Governor's engraved signet ring, fountain pen and orange ceremonial sash
A01_invest_in_mass_consumer_goods|Nineteenth century rubber boots and rubber household goods beside a small workshop cog
A01_last_chance_to_negotiate|Two diplomatic hands clasped above a sealed nonaggression pact, tiny rubber branch
A01_admirals_council_coup|Naval officer's gauntlet seizing a governor's broken ceremonial staff, anchor behind
A01_direct_naval_rule|Admiral's bicorne above a naval anchor and a closed parliamentary ledger
A01_build_bornean_fortifications|A low nineteenth century stone coastal battery with a single cannon and palm frond
A01_prepare_bornean_logistics|Steam locomotive pulling supply crates over a tropical railway bridge
A01_improve_bornean_fortifications|Three tiered coastal stone gun batteries with reinforced earthworks
A01_open_papuan_road|Surveyor's machete and wooden road sign above a jungle trail carrying rifle crates
A01_fortify_australian_frontier|A frontier palisade and two guard towers above a parchment outline of New Guinea
A01_java_development|A Javanese brick textile mill with tall chimney and woven cloth spool
A01_archipelago_shipping|A small coastal sailing steamer linking three island silhouettes with dotted sea routes
A01_sumatran_railways|A brass steam locomotive wheel with railway tracks and a Sumatran palm leaf
A01_surabaya_arsenal|An arsenal workbench with brass ammunition cartridges, gun barrel and hammer
A01_batavia_docks|A steam warship sitting in a stone dry dock with dock gates visibly open
A01_rubber_processing|Rubber tapping cup on a tree trunk beside a mechanical roller press and rubber sheet
A01_local_rifles|Two nineteenth century bolt action rifles and a machinist's caliper over wooden gunstock
A01_technical_college|An engineer's open drafting book with brass dividers, small bridge drawing and gear
A01_knil_reform|A colonial infantry kepi above crossed period rifles and a drill manual
A01_island_garrisons|Three island forts linked by a central stack of reserve rifles
A01_marine_brigades|A naval infantry cap with crossed rifle and boarding cutlass, short blue ribbon
A01_jungle_supply|A woven supply basket with ammunition crates and tropical trail guide's staff
A01_coastal_watch|Brass spyglass above a coastal signal mast and small lighthouse
A01_equal_service|Two uniform sleeves, one European hand and one Indonesian hand, holding identical pay coins
A01_colonial_hierarchy|A tall governor's administrative seal on top of three descending ledgers
A01_sultans_compact|A Malay royal headdress with crescent and rolled diplomatic treaty
A01_colonial_charter|An unfolded island charter with three colored wax seals beneath a balanced justice scale
A01_admiralty_shipyards|A wooden ship hull under construction on a slipway, shipwright hammer and ribs visible
A01_naval_general_staff|An admiral's plotting table with brass compass and two miniature squadron markers
A01_military_industry|A weapons factory chimney with crossed machining tools and a shell casing
A01_defence_in_depth|Three staggered earthwork lines with a reserve infantry helmet behind them
A01_archipelago_command|A land officer's baton and naval telescope crossed above connected island shields
A01_wartime_industry|A steel factory gear surrounding stacked ammunition shells and a shift clock
A01_secure_sea_lanes|A convoy of merchant steamers guarded by one escort beneath a protective shield
A01_pacific_settlement|A cracked naval anchor, lowered Dutch ribbon and armistice document
A01_admiralty_diplomacy|A nineteenth century gunboat's forward cannon overlooking a diplomatic scroll
A01_governors_secretariat|A secretary's ornate writing desk with stacked official files and governor's ink stamp
A01_officers_audience|Two naval epaulettes and a report folder facing a small governor's ceremonial chair
A01_civilian_procurement|An open procurement ledger with a magnifying glass, verified invoice and civilian pen
A01_naval_budget_compromise|A balance scale with a miniature anchor on one pan and treasury coins on the other
A01_reconstruction_commission|A round committee table with engineer's ruler, civilian papers and naval officer cap
A01_autonomous_sultanates|Three different Malay sultan crowns resting above three autonomy charters
A01_northern_memory|A stone memorial obelisk with a laurel wreath, lowered Dutch pennant and Borneo outline
A01_federal_defence_compact|Three crescent shields joined around a central coastal cannon and anchor
A01_fleet_of_recovery|A repaired nineteenth century steam frigate rising above shipwright tools and a broken chain
A01_ludolf_survives|A governor's ceremonial chair standing firmly above a civil seal and an intact orange ribbon
A01_negotiated_resignation|A hand laying down a ceremonial governor's key beside a sealed transfer of office
A01_review_borneo_convention|A gloved hand with a sabre cutting a broken chain over a parchment Borneo treaty
A03_imperial_council|A gold Japanese chrysanthemum crest over a red enamel roundel with a gear and anchor
A03_civil_government|A Japanese civilian minister's formal top hat and cabinet portfolio with small chrysanthemum seal
A03_naval_government|A Japanese nineteenth century naval peaked cap over an anchor and ministerial portfolio
A03_prefectural_reform|Three Japanese prefectural administrative seals connected to a central tax ledger
A03_commercial_diplomacy|A Japanese merchant fan, brass globe and pair of diplomatic trade scrolls
A03_batavia_convention|A treaty scroll tied with Japanese red-white and Dutch orange ribbons, a small rubber leaf
A03_pacific_prosperity|A merchant steamer, rising factory chimneys and spilling gold coins within a laurel half wreath
A03_southern_strategy|A brass naval compass over a sea chart with an arrow pointing south to tropical islands
A03_resource_commission|An oil barrel, rubber bale and brass abacus arranged on an imperial inventory ledger
A03_batavia_ultimatum|A sealed Japanese ultimatum pierced by a diplomatic dagger above an oil barrel
A03_southern_bases|A tropical naval coaling station with stacked coal, mooring bollard and palm tree
A03_southern_campaign|A nineteenth century Japanese steam warship and rowing landing boat approaching a palm shore
A03_southern_reconstruction|An oil derrick being repaired with a crane, carpenter tools and tropical foliage
A03_osaka_industry|A Japanese brick industrial mill with smokestacks, merchant warehouse roof and machine flywheel
A03_kansai_railways|A Japanese nineteenth century steam locomotive emerging between two railway station roofs
A03_hiroshima_arsenal|A crossed rifle barrel and ammunition mould above a Japanese arsenal gate
A03_steel_contracts|Three steel ingots on a signed commercial contract with a bronze handshake seal
A03_standard_rifles|One nineteenth century bolt action rifle above identical cartridge rows and engineering blueprint
A03_imperial_university|A Japanese university gate with an open engineering textbook and brass drafting triangle
A03_electrical_workshops|A nineteenth century electrical dynamo with copper coils and a telegraph key
A03_industrial_power|A large steel factory gear framing three tall smoking industrial chimneys and a small chrysanthemum
A03_naval_programme|A steam ironclad ship blueprint beneath a Japanese imperial chrysanthemum and shipwright dividers
A03_kure_yards|A Japanese steam warship in a large dry dock framed by two dockside cranes
A03_merchant_marine|A nineteenth century cargo steamer with stacked timber crates and Japanese merchant flag pennant
A03_naval_academy|A naval cadet's cap above an open navigation textbook, sextant and brass anchor
A03_island_supply|Two merchant steamships beside a barrel and crate, a dotted route connecting island silhouettes
A03_fleet_exercises|Three nineteenth century steam warship silhouettes maneuvering around brass tactical arrows
A03_army_reorganisation|A Japanese infantry officer kepi and crossed swords above orderly regimental roster cards
A03_conscription_register|An open military registration ledger with orderly rows of stamps and a recruit's period cap
A03_landing_forces|A wooden landing boat carrying period rifles beneath a Japanese naval infantry cap
A03_field_artillery|A nineteenth century field cannon with wooden spoked wheels and three brass shells
A03_expeditionary_staff|A rolled expedition map with officer's binoculars, campaign compass and red route pins
A03_combined_operations|A crossed army sword and naval anchor above interlocking land and sea tactical arrows
'''
S=dict(line.split('|',1) for line in subjects.strip().splitlines())
loc={}
for p in sorted((R/'localisation/russian').glob('*.yml')):
 for k,v in re.findall(r'^\s*(A0[13]_\w+):(?:\d+)?\s*"(.*)"',p.read_text(encoding='utf-8-sig'),re.M):loc[k]=v
reuse={'A01_constitution':'story_constitution','A01_wtc_oil_and_rubber_offer':'story_trade','A01_lone_wolf_path':'story_wolf','A01_strengthen_ludolfs_power':'story_ludolf','A01_sultans_compact':'story_sultans','A01_pacific_settlement':'story_defeat','A01_review_borneo_convention':'story_revanchism','A03_imperial_council':'pacific_japan'}
style='Use case: stylized-concept. Single isolated national focus icon for Hearts of Iron IV, nineteenth century alternate history. Authentic hand-painted strategy-game emblem, sculpted antique bronze and gunmetal with restrained enamel accents, dramatic readable light and dark planes, crisp dominant silhouette, few large details, professionally finished. Centered compact composition, occupies 85 percent of canvas, readable at 95x85 pixels. Transparent background. No words, letters, numbers, modern weapons, tank, aircraft, rectangular backdrop or UI frame. One emblem only, no contact sheet. Subject: '
out=[]
for tag in ['a01','a03']:
 for fid in re.findall(r'\bfocus\s*=\s*\{\s*id\s*=\s*(A0[13]_\w+)',(R/f'common/national_focus/{tag}_focus.txt').read_text()):
  if fid.endswith("_focus"):continue
  assert fid in S,fid
  title=loc.get(fid,fid);desc=loc.get(fid+'_desc','')
  out.append(dict(id=fid,title=title,description=desc,subject=S[fid],prompt=style+S[fid]+'. Focus meaning: '+title+'. '+desc,reuse=reuse.get(fid)))
idx=0
for x in out:
 if not x['reuse']:
  finish='professionally finished Paradox-style strategy game UI.' if idx<12 else 'professionally finished strategy game UI.'
  prefix='Single isolated HOI4 national focus emblem, nineteenth century. Hand-painted antique bronze and gunmetal, restrained enamel accents, crisp bold silhouette and dramatic highlights, '+finish+' Compact centered design filling canvas, readable at 95x85. Transparent background. No text, numbers, rectangular backdrop, tanks, planes or modern equipment. Subject: '
  x['prompt']=prefix+x['subject']+'. Meaning: '+x['title']+'. '+x['description']
  idx+=1
p=R/'gfx/interface/focus_unique_sources';p.mkdir(parents=True,exist_ok=True)
(p/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(out),'focuses;',sum(not x['reuse'] for x in out),'new emblems')


