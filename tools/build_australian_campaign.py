"""Six Australian campaigns, constitutional federation and Pacific sovereignty.

Writes only AUC_campaign files; colonial borders, histories and WTN content stay
owned by their existing builders. Higher tree selection weight selects these trees.
"""
from pathlib import Path
import json,re,shutil

ROOT=Path(__file__).resolve().parents[1]
COLONIES=json.loads((ROOT/'tools/australia_1893_manifest.json').read_text(encoding='utf-8'))
MINORS=[t for t in COLONIES if t!='A07']
LOC={'russian':{},'english':{}};TREES={};EFFECTS=[];EVENTS=['add_namespace = auc_campaign'];IDEAS=[];IDEA_IDS={}

def write(path,text,bom=False):
    for original,actual in IDEA_IDS.items():
        text=re.sub(r'((?:add_ideas|remove_ideas|idea) = )'+re.escape(original)+r'\b',lambda m:m[1]+actual,text)
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text.rstrip()+'\n',encoding='utf-8-sig' if bom else 'utf-8')

def loc(key,ru,en):
    for lang,text in [('russian',ru),('english',en)]:
        assert key not in LOC[lang],key
        LOC[lang][key]=text

def focus(tag,suffix,ru,en,desc,en_desc,x,y,parents=(),reward='add_political_power = 35',available='',excludes=(),cost=5,icon='GFX_goal_generic_national_unity',ai=5):
    key=f'AUC_{tag}_{suffix}'
    loc(key,ru,en);loc(key+'_desc',desc,en_desc)
    req=' '.join(f'prerequisite = {{ focus = AUC_{tag}_{p} }}' for p in parents)
    excl=' '.join(f'mutually_exclusive = {{ focus = AUC_{tag}_{p} }}' for p in excludes)
    avail=f'available = {{ {available} }}' if available else ''
    TREES.setdefault(tag,[]).append(dict(id=key,x=x,y=y,parents=[f'AUC_{tag}_{p}' for p in parents],script=f' focus = {{ id = {key} icon = {icon} x = {x} y = {y} cost = {cost} {req} {excl} {avail} cancel_if_invalid = yes ai_will_do = {{ factor = {ai} }} completion_reward = {{ {reward} }} }}'))

def spirit(key,ru,en,desc,en_desc,mods):
    IDEA_IDS[key]=key+'_spirit'
    key += '_spirit'
    loc(key,ru,en);loc(key+'_desc',desc,en_desc)
    IDEAS.append(f' {key} = {{ picture = generic_pp_unity_bonus removal_cost = -1 modifier = {{ {mods} }} }}')

def event(n,title,en_title,desc,en_desc,options,trigger=''):
    key=f'auc_campaign.{n}'
    loc(key+'.t',title,en_title);loc(key+'.d',desc,en_desc)
    rows=[f'country_event = {{ id = {key} title = {key}.t desc = {key}.d picture = GFX_1896_event_talks is_triggered_only = yes timeout_days = 15']
    if trigger:rows.append(f'trigger = {{ {trigger} }}')
    for i,(ru,en,effect,chance) in enumerate(options):
        # British policy changes AI preferences; a British player keeps both answers.
        policy={
          (1,0): ' modifier = { factor = 0 has_country_flag = BLV_hard_empire } modifier = { factor = 2 has_country_flag = BLV_dominion_policy }',
          (1,1): ' modifier = { factor = 5 has_country_flag = BLV_hard_empire } modifier = { factor = 0 has_country_flag = BLV_dominion_policy }',
          (3,0): ' modifier = { factor = 0.2 has_country_flag = BLV_hard_empire } modifier = { factor = 3 has_country_flag = BLV_dominion_policy }',
          (3,1): ' modifier = { factor = 2 has_country_flag = BLV_hard_empire } modifier = { factor = 0.3 has_country_flag = BLV_dominion_policy }',
          (5,0): ' modifier = { factor = 0.3 has_country_flag = BLV_hard_empire } modifier = { factor = 2 has_country_flag = BLV_dominion_policy }',
        }
        chance+=policy.get((n,i),'')
        k=key+'.'+'abc'[i];loc(k,ru,en)
        rows.append(f' option = {{ name = {k} ai_chance = {{ {chance} }} {effect} }}')
    rows.append('}');EVENTS.append('\n'.join(rows))

def building(kind):
    return 'capital_scope = { if = { limit = { is_owned_by = ROOT is_controlled_by = ROOT } add_extra_state_shared_building_slots = 1 add_building_construction = { type = '+kind+' level = 1 instant_build = yes } } }'

def tech(category='industry',bonus='0.5'):
    return f'add_tech_bonus = {{ name = AUC_research bonus = {bonus} uses = 1 category = {category} }}'

def local_campaigns():
    data={
    'AVC':[
      ('melbourne','Мельбурнский кабинет','Melbourne Cabinet','Соперничество с Сиднеем не должно разрушить торговлю Виктории. Кабинет защищает местный парламент и готовит переговоры о федерации.','Victoria protects its parliament while preparing federal negotiations.'),
      ('foundries','Литейные Мельбурна','Melbourne Foundries','Разместить военные заказы на местных предприятиях и сократить зависимость от импортных винтовок.','Place arms orders with local factories.',building('arms_factory')),
      ('tariffs','Защитить местную промышленность','Protect Local Industry','Общий рынок должен сохранить рабочие места. Тарифный компромисс станет нашим условием вступления в федерацию.','A tariff compromise is Victoria\'s condition for joining the federation.','add_ideas = AUC_AVC_tariffs_spirit'),
      ('dockyards','Доковые мастерские Уильямстауна','Williamstown Workshops','Расширить ремонтные мощности для конвоев и будущего австралийского флота.','Expand repair yards for convoys and an Australian navy.',building('dockyard')),
      ('rifles','Викторианские стрелки','Victorian Rifles','Создать обученный территориальный резерв для обороны Мельбурна.','Train territorial infantry to defend Melbourne.'),
      ('harbour','Береговые батареи Порт Филлипа','Port Phillip Batteries','Укрепить порт и подготовить оборону побережья.','Prepare coastal defence and protect Port Phillip.'),
      ('school','Школа федеральных офицеров','Federal Officers School','Штабная подготовка превращает местное ополчение в основу общей армии.','Staff training prepares the militia for a federal army.'),
      ('demand','Тарифный компромисс','Tariff Compromise','Требовать защиты местных предприятий и представительства Виктории в федеральном правительстве.','Secure industrial protections and federal representation.')],
    'AQL':[
      ('brisbane','Брисбен и северные округа','Brisbane and the North','Удалённые округа требуют дорог, снабжения и защиты. Сначала нужно связать их с колониальным правительством.','Connect remote northern districts to the colonial government.'),
      ('ports','Северные перевалочные порты','Northern Supply Ports','Переработка сельскохозяйственных грузов и портовые склады дадут средства на оборону севера.','Cargo processing and warehouses fund northern defence.',building('industrial_complex')),
      ('labour','Договор с северными округами','Northern District Compact','Урегулировать трудовые споры и обеспечить представительство удалённых поселений.','Settle labour disputes and represent distant settlements.','add_ideas = AUC_AQL_districts_spirit'),
      ('workshops','Брисбенские оружейники','Brisbane Armourers','Собственный ремонт оружия уменьшит зависимость от морских поставок.','Local arms production reduces dependence on shipping.',building('arms_factory')),
      ('rifles','Квинслендская конная пехота','Queensland Mounted Infantry','Подготовить территориальную пехоту для мобильной обороны северных дорог.','Train territorial infantry for northern defence.'),
      ('harbour','Наблюдатели Торресова пролива','Torres Strait Watch','Сеть береговых постов предупреждает о появлении японских десантных сил.','Coastal watchers warn of Japanese landing forces.'),
      ('school','Северный военный округ','Northern Military District','Объединить снабжение разрозненных гарнизонов.','Coordinate supplies for scattered northern garrisons.'),
      ('demand','Гарантия северной обороны','Northern Defence Guarantee','Потребовать федерального бюджета для северных портов и равного голоса в Сенате.','Demand a northern defence budget and an equal Senate voice.')],
    'ASA':[
      ('adelaide','Аделаидский кабинет','Adelaide Cabinet','Северная территория управляется из Аделаиды. Без дорог и связи это обязательство останется тяжёлым бременем.','Adelaide must connect and supply the Northern Territory.'),
      ('telegraph','Вдоль телеграфной линии','Along the Telegraph','Снабжать поселения вдоль существующей линии связи через внутренние районы.','Support settlements along the inland telegraph corridor.',building('industrial_complex')),
      ('inland','Снабжение внутренних районов','Inland Supply Service','Перевалочные склады и согласованные маршруты уменьшают издержки удалённых гарнизонов.','Warehouses and coordinated routes supply distant garrisons.','add_ideas = AUC_ASA_inland_spirit'),
      ('arsenal','Аделаидский арсенал','Adelaide Arsenal','Развернуть производство и ремонт оружия для северных постов.','Produce and repair rifles for northern outposts.',building('arms_factory')),
      ('rifles','Территориальные патрули','Territorial Patrols','Небольшие пехотные части защищают дороги и линии связи.','Small infantry units protect roads and communications.'),
      ('harbour','Оборона северных подходов','Defend the Northern Approaches','Организовать оборону побережья и наблюдение за морскими маршрутами.','Organise coastal defence and watch northern sea routes.'),
      ('school','Служба дальней связи','Long Distance Signals','Обучить штабистов координации войск на больших расстояниях.','Train staff officers for operations across long distances.'),
      ('demand','Федеральный бюджет Севера','Federal Northern Budget','Содружество должно взять на себя часть расходов Северной территории.','The Commonwealth must share the cost of the Northern Territory.')],
    'AWA':[
      ('perth','Перт и золотые прииски','Perth and the Goldfields','Западная Австралия богата золотом, но отделена от восточных колоний огромными расстояниями.','Gold wealth cannot remove Western Australia\'s isolation.'),
      ('gold','Доходы золотых приисков','Goldfield Revenues','Направить часть доходов приисков на мастерские и переработку сырья.','Invest goldfield revenues in local workshops.',building('industrial_complex')),
      ('railway','Требование дороги на восток','The Eastern Railway Demand','Трансконтинентальная дорога станет условием вступления. Пока речь идёт о гарантии и изысканиях, а не о готовой линии.','Demand a transcontinental railway commitment; surveys do not instantly build a railway.','add_ideas = AUC_AWA_surveys_spirit'),
      ('fremantle','Верфи Фримантла','Fremantle Yards','Расширить ремонт и строительство судов на западном побережье.','Expand ship construction and repair on the west coast.',building('dockyard')),
      ('rifles','Стрелки западных округов','Western District Rifles','Обучить пехотный резерв для обороны Перта и приисков.','Train infantry to defend Perth and the goldfields.'),
      ('harbour','Индийский океан под наблюдением','Indian Ocean Watch','Западные порты должны пережить перерыв британского снабжения.','Prepare western ports for a break in British supply.'),
      ('school','Самостоятельное снабжение','Independent Supply Service','Местные ремонтные службы поддерживают войска вдали от восточных арсеналов.','Local repair services sustain forces far from eastern arsenals.'),
      ('demand','Западноавстралийская оговорка','Western Australian Clause','Закрепить железнодорожную гарантию и переходный срок для местных пошлин.','Secure a railway pledge and transitional customs arrangements.')],
    'ATA':[
      ('hobart','Хобартский кабинет','Hobart Cabinet','Остров нуждается в устойчивой торговле через Бассов пролив и защите права голоса малого штата.','Tasmania needs Bass Strait trade and a small state\'s political voice.'),
      ('commerce','Торговля через Бассов пролив','Bass Strait Commerce','Поддержать островные предприятия и склады.','Support island workshops and warehouses.',building('industrial_complex')),
      ('shipping','Расписание каботажных рейсов','Coastal Shipping Schedule','Общий график поставок снижает уязвимость острова к морской блокаде.','Coordinated coastal shipping reduces the island\'s vulnerability.','add_ideas = AUC_ATA_shipping_spirit'),
      ('yards','Ремонтные доки Хобарта','Hobart Repair Docks','Расширить базу ремонта торговых и сторожевых судов.','Expand repair facilities for merchant and patrol vessels.',building('dockyard')),
      ('rifles','Тасманийские добровольцы','Tasmanian Volunteers','Подготовить местную пехоту для обороны островных портов.','Train local infantry to defend island harbours.'),
      ('harbour','Охрана Бассового пролива','Guard Bass Strait','Береговые посты и сопровождение конвоев прикрывают связь с материком.','Watch stations and escorts protect the mainland connection.'),
      ('school','Островная служба конвоев','Island Convoy Service','Подготовить специалистов сопровождения и пополнить торговый флот.','Train escort specialists and expand the merchant fleet.'),
      ('demand','Голос малого штата','A Small State\'s Voice','Равное представительство в Сенате защитит остров от господства материковых столиц.','Equal Senate representation protects Tasmania from mainland domination.')],
    }
    for tag,rows in data.items():
        root=rows[0]
        focus(tag,*root,8,0,reward='add_political_power = 40 add_stability = 0.02')
        for idx,(suffix,ru,en,desc,eng,reward) in enumerate(rows[1:4]):
            focus(tag,suffix,ru,en,desc,eng,2,2+idx*2,parents=(root[0] if idx==0 else rows[idx][0],),reward=reward,icon='GFX_goal_generic_construct_civ_factory')
        for idx,row in enumerate(rows[4:7]):
            suffix,ru,en,desc,eng=row
            reward=(f'AUC_raise_{tag}_militia = yes' if idx==0 else 'add_ideas = AUC_coastal_watch navy_experience = 10' if idx==1 else 'add_ideas = AUC_territorial_staff army_experience = 15')
            if tag=='ATA' and idx==2:reward='add_equipment_to_stockpile = { type = convoy_1 amount = 8 } navy_experience = 15'
            focus(tag,suffix,ru,en,desc,eng,8,2+idx*2,parents=(root[0] if idx==0 else rows[3+idx][0],),reward=reward,icon='GFX_goal_generic_army_doctrines')
        suffix,ru,en,desc,eng=rows[7]
        focus(tag,suffix,ru,en,desc,eng,14,2,parents=(root[0],),reward=f'set_country_flag = AUC_local_terms A07 = {{ set_country_flag = AUC_terms_{tag} }} add_political_power = 25')
        focus(tag,'federal', 'За договорную федерацию','A Negotiated Federation','Поддержать объединение с Сиднеем при сохранении прав штата. Решение о вступлении принимается отдельно: игрок сможет подтвердить передачу управления федерации.','Support a federation with state guarantees. Joining requires a separate explicit vote.',12,4,parents=('demand',),excludes=('separate',),reward='set_country_flag = AUC_federal_campaign add_stability = 0.03')
        focus(tag,'separate','Сохранить отдельный кабинет','Keep Our Own Cabinet','Сохранить самостоятельное колониальное правительство и отказаться от автоматического присоединения.','Keep a separate colonial government and oppose federal annexation.',16,4,parents=('demand',),excludes=('federal',),reward=f'set_country_flag = AUC_separate_cabinet clr_country_flag = AUC_join_authorized A07 = {{ clr_country_flag = AUC_vote_{tag} }} add_ideas = AUC_local_parliament',ai=1)
        focus(tag,'mandate','Местный референдум','Local Referendum','Когда федеральный конвент откроет голосование, подтвердить вступление на согласованных условиях. Отказ оставляет страну под вашим управлением.','When the federal convention opens voting, hold a local referendum. Refusal preserves your country.',12,6,parents=('federal',),available='country_exists = A07 A07 = { has_country_flag = AUC_referendums_open } AUC_can_negotiate = yes NOT = { has_country_flag = AUC_join_authorized }',reward=f'country_event = {{ id = auc_campaign.{10+MINORS.index(tag)} days = 1 }}')
        focus(tag,'credit','Собственный стол Палаты','A Local Chamber Desk','Открыть доступ к кредитным соглашениям ВТП и межгосударственным переговорам.','Open Chamber credit compacts and interstate talks.',20,2,parents=(root[0],),reward='WTC_initialize_effect = yes set_country_flag = WTN_compact_desk_open set_country_flag = WTN_relations_open custom_effect_tooltip = WTN_open_compact_tt')
        focus(tag,'services','Местные договоры снабжения','Local Supply Contracts','Заключить ограниченные договоры снабжения без отказа от контроля местного кабинета.','Arrange supply contracts while preserving the local cabinet.',20,4,parents=('credit',),reward='add_timed_idea = { idea = WTN_colonial_contract days = 240 } add_political_power = 25')

def federal_campaign():
    t='A07'
    focus(t,'leagues','Лиги австралийской федерации','Australian Federation Leagues','Сидней станет центром переговоров шести колоний. Объединение требует согласия местных парламентов и британской хартии либо собственного суверенитета.','Sydney organises six colonial governments. Union needs local consent and either a British charter or sovereignty.',10,0,reward='add_political_power = 50')
    focus(t,'corowa','План Корова','The Corowa Plan','Избираемый конвент подготовит проект конституции, который затем вынесут на голосование. Историческая отправная точка — конференция 1893 года.','An elected convention will draft a constitution for popular ratification, following the 1893 Corowa plan.',10,2,parents=('leagues',),reward='set_country_flag = AUC_corowa_plan add_stability = 0.03',available='date > 1893.7.30')
    focus(t,'convention','Избираемый федеральный конвент','An Elected Federal Convention','Поручить делегатам согласование общей конституции, не передавая Сиднею власть над соседями заранее.','Delegates negotiate a common constitution without annexing neighbouring colonies.',10,4,parents=('corowa',),reward='add_political_power = 35',cost=7)
    focus(t,'senate','Сенат равных штатов','A Senate of Equal States','Защитить малые колонии равным представительством в верхней палате и закрепить ответственность федерального кабинета.','Protect small colonies through equal representation in the upper house.',10,6,parents=('convention',),reward='set_country_flag = AUC_equal_senate add_stability = 0.03')
    pacts=[('AVC','Тарифный компромисс с Мельбурном','Melbourne Tariff Compromise'),('AQL','Гарантия обороны Квинсленда','Queensland Defence Guarantee'),('ASA','Разделить расходы Севера','Share the Northern Burden'),('AWA','Обещать дорогу на запад','Promise a Western Railway'),('ATA','Гарантировать голос Тасмании','Guarantee Tasmania a Voice')]
    for i,(tag,ru,en) in enumerate(pacts):
        focus(t,'terms_'+tag,ru,en,'Закрепить условие вступления этой колонии. Гарантия стоит 25 политического влияния и повышает вероятность согласия на референдуме. Само присоединение требует отдельного решения.','Pay 25 political power to guarantee this colony\'s terms and strengthen support in its referendum. Joining requires a separate vote.',2+i*4,8,parents=('senate',),available='has_political_power > 24',reward=f'add_political_power = -25 set_country_flag = AUC_terms_{tag}')
    focus(t,'referendums','Колониальные референдумы','Colonial Referendums','Пригласить пять правительств провести голосование. Согласившиеся колонии разрешают последующее присоединение; отказавшиеся сохраняют самостоятельность.','Invite five colonial governments to vote. Approval authorises later annexation; rejection preserves their independence.',10,10,parents=('senate',),reward='AUC_open_referendums = yes custom_effect_tooltip = AUC_referendum_tt',cost=7)
    focus(t,'charter','Хартия федерации','A Federal Charter','Передать британскому правительству проект федерации. Хартия разрешает объединение под короной, но не даёт независимости. Требуется согласие хотя бы двух колоний.','Request a British charter for federation under the Crown. It does not grant independence. At least two colonial approvals are required.',10,12,parents=('referendums',),available='AUC_two_approvals = yes OR = { is_subject = no is_subject_of = A02 }',reward='AUC_request_charter = yes custom_effect_tooltip = AUC_charter_tt')
    focus(t,'commonwealth','Провозгласить Содружество','Proclaim the Commonwealth','Учредить федерацию из согласившихся колоний. Передача территорий и войск происходит только после их согласия и при действующей хартии либо независимости Сиднея. Другие колонии могут вступить позже.','Form a federation from consenting colonies after a valid charter or independence. Other colonies may join later.',10,14,parents=('charter',),available='AUC_can_form_federation = yes has_war = no',reward='AUC_found_commonwealth = yes custom_effect_tooltip = AUC_federate_tt',cost=7)
    focus(t,'parliament','Временный парламент в Мельбурне','An Interim Parliament in Melbourne','Мельбурн примет общий парламент. Сидней сохранит политический вес, а постоянную столицу предстоит выбрать позднее.','Melbourne hosts the federal parliament while the permanent capital remains a future decision.',6,16,parents=('commonwealth',),available='517 = { is_owned_by = ROOT is_controlled_by = ROOT }',reward='set_capital = { state = 517 } add_stability = 0.04')
    focus(t,'six_states','Шесть штатов одного Содружества','Six States in One Commonwealth','Завершить объединение всех четырнадцати австралийских регионов мода и утвердить общий бюджет.','Complete the union of all fourteen Australian map regions and approve a common budget.',14,16,parents=('commonwealth',),available='AUC_owns_australia = yes',reward='add_ideas = AUC_common_market add_political_power = 75')
    focus(t,'first_ministry','Первый федеральный кабинет','The First Federal Ministry','Передать управление Содружеством кабинету Эдмунда Бартона. Конституционный путь сохраняет парламентскую форму правления.','Appoint Edmund Barton to lead the Commonwealth while retaining parliamentary government.',10,18,parents=('commonwealth',),available='has_government = democratic',reward='recruit_character = AUC_edmund_barton promote_character = { character = AUC_edmund_barton ideology = conservatism } add_political_power = 50')
    # Local economy and a Chamber branch remain available during the convention.
    focus(t,'customs','Торговля через границы колоний','Trade Across Colonial Borders','Начать унификацию торговых правил и поддержать предприятия Нового Южного Уэльса.','Coordinate trade rules and support New South Wales workshops.',24,2,parents=('leagues',),reward=building('industrial_complex'),icon='GFX_goal_generic_construct_civ_factory')
    focus(t,'arsenal','Сиднейский арсенал','Sydney Arsenal','Заказать местное производство винтовок до появления единой федеральной армии.','Establish local rifle production before a federal army exists.',24,4,parents=('customs',),reward=building('arms_factory'),icon='GFX_goal_generic_construct_mil_factory')
    focus(t,'research','Межколониальный технический совет','Intercolonial Technical Board','Обмен техническими решениями сократит стоимость военных и промышленных исследований.','Share industrial and military research.',24,6,parents=('arsenal',),reward=tech())
    focus(t,'chamber','Палата при федеральной казне','A Chamber Desk at the Treasury','Сохранить доступ к соглашениям ВТП и внешним торговым связям.','Keep access to Chamber compacts and external trade talks.',28,2,parents=('leagues',),reward='WTC_initialize_effect = yes set_country_flag = WTN_compact_desk_open set_country_flag = WTN_relations_open custom_effect_tooltip = WTN_open_compact_tt')
    focus(t,'accounts','Не закладывать будущую федерацию','Do Not Mortgage the Federation','Уменьшить существующую задолженность, прежде чем финансировать общие ведомства новыми займами.','Reduce existing debt before borrowing for federal institutions.',28,4,parents=('chamber',),reward='WTC_initialize_effect = yes add_to_variable = { WTC_debt = -5 } WTC_refresh_effect = yes')
    # Pacific defence can develop alongside the constitutional campaign.
    defence=[
     ('staff','Общий оборонный комитет','Joint Defence Committee','Колониальные штабы согласуют планы обороны и подготовку резервов.','Colonial staffs coordinate defence plans and reserves.','add_ideas = AUC_territorial_staff army_experience = 15'),
     ('coast','Береговая дозорная сеть','Coastal Watch Network','Береговые наблюдатели и связь предупреждают гарнизоны о высадках.','Coastwatchers and signals warn garrisons of landings.','add_ideas = AUC_coastal_watch navy_experience = 15'),
     ('yards','Федеральная программа верфей','Federal Dockyard Programme','Расширить строительство и ремонт судов. Крупный флот придётся построить за счёт собственной промышленности.','Expand shipyards; a major fleet must still be built by Australian industry.',building('dockyard')),
     ('convoys','Торговые суда под охраной','Escort the Merchant Fleet','Выделить новые транспорты и обучить конвойные службы.','Commission merchant transports and train escort services.','add_equipment_to_stockpile = { type = convoy_1 amount = 15 } add_ideas = AUC_escorts'),
     ('japan','Тихоокеанская угроза','The Pacific Threat','Японское продвижение к Филиппинам требует готовности северных гарнизонов. Австралия начнёт подготовку, сохраняя выбор момента войны.','Japanese advances in the Philippines require prepared northern garrisons without forcing an immediate war.','add_war_support = 0.05 '+tech('land_doctrine','0.25')),
     ('partners','Связи с Батавией и Филиппинами','Links with Batavia and the Philippines','Предложить невоюющим с нами правительствам взаимный военный доступ. Союз и участие в их войнах не возникают автоматически.','Arrange mutual military access with peaceful partners; this does not enter their wars.','AUC_pacific_partners = yes'),
     ('deter','Австралийский тихоокеанский рубеж','An Australian Pacific Line','Единый штаб повышает готовность флота. После создания Содружества Австралия сможет сама определить свою политику на море.','A federal naval staff improves readiness and supports an independent Pacific policy.','add_ideas = AUC_pacific_line navy_experience = 20')]
    for i,(suffix,ru,en,desc,eng,reward) in enumerate(defence):
        focus(t,suffix,ru,en,desc,eng,34,2+i*2,parents=('leagues' if i==0 else defence[i-1][0],),reward=reward,icon='GFX_goal_generic_navy_doctrines_tactics')
    focus(t,'japan_goal','Потребовать японского отхода','Demand a Japanese Withdrawal','Независимая Австралия получает повод к войне за Манилу, если Япония по-прежнему владеет ею. Это подготовка конфликта: войну объявляет игрок.','An independent Australia gains a war goal for Manila while Japan still owns it. The player chooses whether to declare war.',34,16,parents=('deter','commonwealth'),available='is_subject = no country_exists = A03 NOT = { is_in_faction_with = A03 } NOT = { has_war_with = A03 } 327 = { is_owned_by = A03 }',reward='create_wargoal = { type = take_state_focus target = A03 generator = { 327 } }',cost=7)
    # Britain: negotiated sovereignty or an explicit independence war.
    focus(t,'sovereignty','Ответственное австралийское правительство','Responsible Australian Government','После учреждения Содружества или отказа в хартии потребовать контроля внешней политики. Британское правительство может согласиться или отвергнуть требование.','After federation or a refused charter, demand control of foreign policy. Britain can accept or refuse.',22,14,parents=('charter',),available='is_subject_of = A02 OR = { has_country_flag = AUC_commonwealth_proclaimed has_country_flag = AUC_charter_refused } NOT = { has_country_flag = AUC_sovereignty_pending }',reward='set_country_flag = { flag = AUC_sovereignty_pending days = 45 } A02 = { country_event = { id = auc_campaign.3 days = 1 } } custom_effect_tooltip = AUC_sovereignty_tt')
    focus(t,'own_flag','Внешняя политика под своим флагом','Foreign Policy Under Our Own Flag','Закрепить независимость и право самостоятельно выбирать союзников.','Consolidate independence and the right to choose allies.',20,18,parents=('commonwealth',),available='is_subject = no',excludes=('break_crown',),reward='add_ideas = AUC_sovereign_policy add_stability = 0.03')
    focus(t,'break_crown','Разрыв с британской короной','Break with the British Crown','После отказа в суверенитете открыть войну за независимость. Этот фокус освобождает Австралию от британского подчинения и немедленно начинает войну с Британией.','After Britain refuses sovereignty, break colonial rule and immediately begin an independence war.',24,18,parents=('sovereignty',),available='country_exists = A02 is_subject_of = A02 has_country_flag = AUC_sovereignty_refused NOT = { has_war_with = A02 } has_war_support > 0.34',excludes=('own_flag',),reward='AUC_independence_war = yes custom_effect_tooltip = AUC_independence_war_tt',cost=7,ai=1)
    focus(t,'british_routes','Снабжение без британских портов','Supply Without British Ports','Расширить самостоятельную логистику перед длительным противостоянием с метрополией.','Build independent logistics for prolonged confrontation with the former metropole.',24,20,parents=('commonwealth',),available='is_subject = no',reward='add_ideas = AUC_independent_logistics add_equipment_to_stockpile = { type = convoy_1 amount = 10 }')

def diplomacy():
    # Target-side consent is never supplied by a Sydney focus alone.
    for i,tag in enumerate(MINORS):
        c=COLONIES[tag];ru=c['ru'];en=c['en']
        accept=f'''if = {{ limit = {{ AUC_can_negotiate = yes A07 = {{ has_country_flag = AUC_referendums_open }} }}
         set_country_flag = AUC_join_authorized clr_country_flag = AUC_join_refused
         A07 = {{ set_country_flag = AUC_vote_{tag} country_event = {{ id = auc_campaign.40 days = 1 }} }}
        }}'''
        event(10+i,'Референдум о федерации','Referendum on Federation',f'{ru} решает, вступать ли в Содружество. Голос «за» разрешит Сиднею присоединить нашу страну после хартии: территории, войска и управление перейдут федерации. Голос «против» сохраняет отдельное государство.',f'{en} votes on federation. Approval authorises Sydney to annex this country after the charter: territory, forces and control pass to the federation. Rejection preserves a separate country.',[
         ('За федерацию и передачу управления','Approve federation and transfer control',accept,f'factor = 35 modifier = {{ factor = 4 A07 = {{ has_country_flag = AUC_terms_{tag} }} }} modifier = {{ factor = 2 has_country_flag = AUC_federal_campaign }} modifier = {{ factor = 0 has_country_flag = AUC_separate_cabinet }}'),
         ('Сохранить отдельное правительство','Keep a separate government',f'clr_country_flag = AUC_join_authorized set_country_flag = AUC_join_refused A07 = {{ clr_country_flag = AUC_vote_{tag} }} add_stability = 0.02','factor = 25')],trigger=f'tag = {tag} AUC_can_negotiate = yes A07 = {{ has_country_flag = AUC_referendums_open }} NOT = {{ has_country_flag = AUC_join_authorized }}')
    event(1,'Британская хартия Австралии','A British Charter for Australia','Сидней просит разрешить объединение согласившихся колоний под короной. Хартия сохраняет британскую верховную власть, но создаёт единое австралийское правительство.','Sydney requests permission to unite consenting colonies under the Crown, retaining British sovereignty.',[
     ('Разрешить договорную федерацию','Approve a negotiated federation','A07 = { clr_country_flag = AUC_charter_pending set_country_flag = AUC_british_charter country_event = { id = auc_campaign.2 days = 1 } }','factor = 90'),
     ('Сохранить раздельные колонии','Preserve separate colonies','A07 = { clr_country_flag = AUC_charter_pending set_country_flag = AUC_charter_refused country_event = { id = auc_campaign.2 days = 1 } }','factor = 10')],trigger='tag = A02 country_exists = A07 A07 = { OR = { is_subject_of = A02 is_subject = no } NOT = { has_war_with = A02 } has_country_flag = AUC_charter_pending }')
    event(2,'Ответ на проект федерации','Reply to the Federation Bill','Результат переговоров отображается в решениях федерации. При отказе можно повторить переговоры через полгода или добиваться суверенитета.','Federation decisions show the result. After refusal, retry in six months or seek sovereignty.',[('Продолжить работу','Continue','add_political_power = 10','factor = 100')])
    event(3,'Австралия требует суверенитета','Australia Requests Sovereignty','Содружество требует самостоятельной внешней политики. Отказ сохранит колониальный статус и откроет путь австралийской войне за независимость.','The Commonwealth demands an independent foreign policy. Refusal preserves colonial status and opens an independence war path.',[
     ('Признать австралийский суверенитет','Recognise Australian sovereignty','AUC_release_federation = yes A07 = { clr_country_flag = AUC_sovereignty_pending set_country_flag = AUC_sovereignty_recognized country_event = { id = auc_campaign.4 days = 1 } }','factor = 40'),
     ('Отклонить требование','Reject the demand','A07 = { clr_country_flag = AUC_sovereignty_pending set_country_flag = AUC_sovereignty_refused add_war_support = 0.10 country_event = { id = auc_campaign.4 days = 1 } }','factor = 60')],trigger='tag = A02 country_exists = A07 A07 = { is_subject_of = A02 has_country_flag = AUC_sovereignty_pending }')
    event(4,'Наши полномочия и корона','Our Powers and the Crown','Правительство получило британский ответ. Признание даёт независимость; отказ оставляет выбор между новыми переговорами и подготовкой вооружённого разрыва.','The British reply determines whether Australia is free or must choose renewed talks or an armed break.',[('Доложить парламенту','Report to Parliament','add_political_power = 15','factor = 100')])
    event(40,'Итоги колониального голосования','A Colonial Vote Returns','Одна из колоний разрешила вступление. Текущее число согласившихся правительств и условия ратификации доступны в решениях федерации.','A colony has authorised joining. Federation decisions show current approvals and ratification requirements.',[('Принять протокол','Receive the protocol','add_political_power = 5','factor = 100')])
    event(5,'Австралийское предложение о перемирии','An Australian Armistice Proposal','Австралийцы удерживают свои владения после шести месяцев борьбы и предлагают признать независимость. Согласие прекратит войну с Австралией и разрешит договорное объединение согласившихся колоний.','Australia has held its territory for six months and proposes recognition of independence. Acceptance ends the war and permits the negotiated union of consenting colonies.',[
      ('Признать самостоятельную Австралию','Recognise an independent Australia','if = { limit = { A07 = { has_war_with = A02 AUC_holds_owned_states = yes } } white_peace = { tag = A07 } A07 = { set_country_flag = AUC_british_charter set_country_flag = AUC_sovereignty_recognized country_event = { id = auc_campaign.6 days = 1 } } }','factor = 60'),
      ('Продолжить войну','Continue the war','A07 = { add_war_support = 0.03 }','factor = 40')],trigger='tag = A02 country_exists = A07 A07 = { has_war_with = A02 has_country_flag = AUC_independence_war_started NOT = { has_country_flag = AUC_independence_opening } AUC_holds_owned_states = yes }')
    event(6,'Британское признание независимости','Britain Recognises Independence','Перемирие подтверждает австралийскую самостоятельность. Британская сторона также разрешила включение колоний, которые отдельно согласятся на федерацию.','The armistice recognises Australian independence and permits the admission of colonies that separately approve federation.',[('Утвердить мир','Ratify peace','add_stability = 0.05','factor = 100')])

def mechanics():
    allstates=[s for c in COLONIES.values() for s in c['states']]
    conditions=[]
    for tag in MINORS:
        # Admission requires both a persistent vote in Sydney and live local consent.
        conditions.append(f'AUC_approval_{tag} = {{ country_exists = {tag} has_country_flag = AUC_vote_{tag} {tag} = {{ has_country_flag = AUC_join_authorized AUC_can_negotiate = yes }} }}')
    triggers='\n'.join(conditions)+'''
AUC_can_negotiate = {
 country_exists = A07 has_war = no has_capitulated = no
 NOT = { has_war_with = A07 }
 OR = { is_subject = no is_subject_of = A02 }
 A07 = { has_war = no has_capitulated = no OR = { is_subject = no is_subject_of = A02 } }
 OR = { is_in_faction = no is_in_faction_with = A07 AND = { is_subject_of = A02 is_in_faction_with = A02 A07 = { has_country_flag = AUC_british_charter } } }
}
AUC_two_approvals = { count_triggers = { amount > 1
'''+''.join(f'AUC_approval_{t} = yes\n' for t in MINORS)+'''} }
AUC_owns_australia = { '''+' '.join(f'{s} = {{ is_owned_by = ROOT is_controlled_by = ROOT }}' for s in allstates)+' }\n'
    triggers+='\nAUC_holds_owned_states = { tag = A07 all_owned_state = { is_controlled_by = A07 } owns_state = 285 }\n'
    triggers+='\nAUC_can_form_federation = { AUC_two_approvals = yes OR = { AND = { has_country_flag = AUC_british_charter OR = { is_subject = no is_subject_of = A02 } } AND = { is_subject = no count_triggers = { amount > 1 '+''.join(f'AND = {{ AUC_approval_{t} = yes {t} = {{ is_subject = no }} }} ' for t in MINORS)+'} } } }\n'
    write('common/scripted_triggers/AUC_campaign.txt',triggers)
    effects=['''AUC_open_referendums = {
 set_country_flag = AUC_referendums_open
'''+''.join(f' if = {{ limit = {{ country_exists = {tag} {tag} = {{ AUC_can_negotiate = yes NOT = {{ has_country_flag = AUC_join_authorized }} }} }} {tag} = {{ country_event = {{ id = auc_campaign.{10+i} days = 1 }} }} }}\n' for i,tag in enumerate(MINORS))+'}\n',
    '''AUC_request_charter = {
 if = { limit = { country_exists = A02 OR = { is_subject_of = A02 is_subject = no } NOT = { has_war_with = A02 } NOT = { has_country_flag = AUC_charter_pending } }
  set_country_flag = { flag = AUC_charter_pending days = 45 } set_country_flag = { flag = AUC_charter_cooldown days = 180 }
  A02 = { country_event = { id = auc_campaign.1 days = 1 } }
 }
}
AUC_release_federation = {
 if = { limit = { tag = A02 country_exists = A07 A07 = { is_subject_of = A02 } }
  set_autonomy = { target = A07 autonomy_state = autonomy_free end_wars = no end_civil_wars = no }
  A07 = { if = { limit = { is_in_faction_with = A02 } leave_faction = yes } }
 }
}
AUC_independence_war = {
 if = { limit = { tag = A07 is_subject_of = A02 has_country_flag = AUC_sovereignty_refused NOT = { has_war_with = A02 } }
  A02 = { AUC_release_federation = yes }
  if = { limit = { is_subject = no NOT = { is_in_faction_with = A02 } }
   declare_war_on = { target = A02 type = annex_everything }
   set_country_flag = AUC_independence_war_started
   set_country_flag = { flag = AUC_independence_opening days = 180 }
  }
 }
}
AUC_found_commonwealth = {
 if = { limit = { tag = A07 AUC_can_form_federation = yes has_war = no }
  set_country_flag = AUC_commonwealth_proclaimed
  set_cosmetic_tag = AUC_COMMONWEALTH
  add_ideas = AUC_federal_compact
'''+''.join(f'  AUC_integrate_{tag} = yes\n' for tag in MINORS)+''' }
}
AUC_pacific_partners = {
'''+''.join(f' if = {{ limit = {{ country_exists = {tag} NOT = {{ has_war_with = {tag} }} }} give_military_access = {tag} {tag} = {{ give_military_access = ROOT }} }}\n' for tag in ('A01','A10'))+'}\n']
    for tag in MINORS:
        effects.append(f'''AUC_integrate_{tag} = {{
 if = {{ limit = {{ tag = A07 has_country_flag = AUC_commonwealth_proclaimed AUC_approval_{tag} = yes
  OR = {{ {tag} = {{ is_subject = no }} AND = {{ has_country_flag = AUC_british_charter {tag} = {{ is_subject_of = A02 }} }} }}
  OR = {{ is_subject = no AND = {{ is_subject_of = A02 has_country_flag = AUC_british_charter }} }}
 }}
  if = {{ limit = {{ {tag} = {{ is_subject_of = A02 }} }} A02 = {{ set_autonomy = {{ target = {tag} autonomy_state = autonomy_free end_wars = no end_civil_wars = no }} }} }}
  {tag} = {{ if = {{ limit = {{ is_in_faction_with = A02 }} leave_faction = yes }} }}
  if = {{ limit = {{ {tag} = {{ is_subject = no }} }}
   annex_country = {{ target = {tag} transfer_troops = yes }}
'''+''.join(f'   {s} = {{ if = {{ limit = {{ is_owned_by = ROOT }} add_core_of = ROOT }} }}\n' for s in COLONIES[tag]['states'])+f'''   clr_country_flag = AUC_vote_{tag} set_country_flag = AUC_integrated_{tag}
  }}
 }}
}}
''')
        c=COLONIES[tag]
        path=next(p for p in (ROOT/'history/states').glob('*.txt') if re.search(r'\bid\s*=\s*'+str(c['capital'])+r'\b',p.read_text(encoding='utf-8-sig')))
        points=re.findall(r'victory_points\s*=\s*\{\s*(\d+)\s+(\d+)',path.read_text(encoding='utf-8-sig'))
        province=max(points,key=lambda x:int(x[1]))[0]
        template=f'{tag} Territorial Infantry'
        write(f'history/units/AUC_campaign_{tag}.txt',f'division_template = {{ name = "{template}" regiments = {{ infantry = {{ x = 0 y = 0 }} infantry = {{ x = 0 y = 1 }} infantry = {{ x = 0 y = 2 }} }} }}\nunits = {{ division = {{ name = "{c["en"]} Territorial Guard" location = {province} division_template = "{template}" start_experience_factor = 0.10 start_equipment_factor = 0.60 }} }}')
        effects.append(f'''AUC_raise_{tag}_militia = {{
 if = {{ limit = {{ tag = {tag} NOT = {{ has_country_flag = AUC_militia_raised }} {c['capital']} = {{ is_owned_by = ROOT is_controlled_by = ROOT }} }}
  set_country_flag = AUC_militia_raised load_oob = AUC_campaign_{tag}
  add_equipment_to_stockpile = {{ type = infantry_equipment_0 amount = 200 }}
  army_experience = 10
 }}
}}''')
    write('common/scripted_effects/AUC_campaign.txt','\n'.join(effects))

def decisions():
    loc('AUC_federation_category','Австралийская федерация','Australian Federation')
    loc('AUC_federation_category_desc','Федерация строится на согласии колоний. После хартии или получения независимости Сидней может объединить согласившиеся правительства. Отказавшиеся колонии сохраняют свой путь.','Federation requires colonial consent. After a charter or independence, Sydney may integrate consenting governments.')
    loc('AUC_defence_category','Австралийская самостоятельность','Australian Self Government')
    rows=['AUC_federation_category = {']
    rows.append(''' AUC_retry_charter = { icon = generic_political_discourse cost = 50 days_re_enable = 180 visible = { has_country_flag = AUC_charter_refused NOT = { has_country_flag = AUC_british_charter } } available = { country_exists = A02 OR = { is_subject_of = A02 is_subject = no } NOT = { has_war_with = A02 } AUC_two_approvals = yes NOT = { has_country_flag = AUC_charter_pending } NOT = { has_country_flag = AUC_charter_cooldown } } complete_effect = { AUC_request_charter = yes } ai_will_do = { factor = 1 } }''')
    loc('AUC_retry_charter','Повторить переговоры о хартии','Renew Charter Negotiations');loc('AUC_retry_charter_desc','Через полгода после обращения можно снова запросить британскую хартию.','After six months, request the British charter again.')
    for i,tag in enumerate(MINORS):
        c=COLONIES[tag]
        key='AUC_vote_status_'+tag
        loc(key,'Согласие на вступление: '+c['ru'],'Approval to Join: '+c['en']);loc(key+'_desc','Правительство разрешило вступление. Присоединение потребует основания федерации и действующих условий хартии.','This government has authorised joining. Integration requires federation and valid charter conditions.')
        rows.append(f' {key} = {{ icon = generic_political_discourse cost = 0 visible = {{ AUC_approval_{tag} = yes }} available = {{ always = no }} complete_effect = {{ }} }}')
        key='AUC_reinvite_'+tag
        loc(key,'Новое приглашение: '+c['ru'],'Renew Invitation: '+c['en']);loc(key+'_desc','Повторить предложение о референдуме через полгода после предыдущего приглашения.','Renew the referendum invitation after six months.')
        rows.append(f' {key} = {{ icon = generic_political_discourse cost = 35 days_re_enable = 180 visible = {{ country_exists = {tag} has_country_flag = AUC_referendums_open NOT = {{ AUC_approval_{tag} = yes }} }} available = {{ {tag} = {{ AUC_can_negotiate = yes }} }} complete_effect = {{ {tag} = {{ country_event = {{ id = auc_campaign.{10+i} days = 1 }} }} }} ai_will_do = {{ factor = 1 }} }}')
        key='AUC_admit_'+tag
        loc(key,'Ратифицировать вступление: '+c['ru'],'Ratify Admission: '+c['en']);loc(key+'_desc','Присоединить согласившуюся колонию. Игрок за неё утратит отдельное государство после ранее подтверждённого согласия.','Annex a consenting colony. Its player gives up separate control after previously approving federation.')
        rows.append(f' {key} = {{ icon = generic_political_discourse cost = 25 visible = {{ has_country_flag = AUC_commonwealth_proclaimed country_exists = {tag} }} available = {{ AUC_approval_{tag} = yes OR = {{ {tag} = {{ is_subject = no }} has_country_flag = AUC_british_charter }} OR = {{ is_subject = no AND = {{ is_subject_of = A02 has_country_flag = AUC_british_charter }} }} }} complete_effect = {{ AUC_integrate_{tag} = yes }} ai_will_do = {{ factor = 5 }} }}')
    rows.append('}')
    rows.append('''AUC_defence_category = {
 AUC_seek_recognition = { icon = generic_political_discourse cost = 75 days_re_enable = 180
  visible = { tag = A07 has_country_flag = AUC_independence_war_started has_war_with = A02 }
  available = { is_subject = no NOT = { has_country_flag = AUC_independence_opening } AUC_holds_owned_states = yes }
  complete_effect = { A02 = { country_event = { id = auc_campaign.5 days = 1 } } }
  ai_will_do = { factor = 3 }
 }
 AUC_retry_sovereignty = { icon = generic_political_discourse cost = 75 days_re_enable = 180
  visible = { tag = A07 has_country_flag = AUC_sovereignty_refused }
  available = { is_subject_of = A02 NOT = { has_country_flag = AUC_sovereignty_pending } }
  complete_effect = { set_country_flag = { flag = AUC_sovereignty_pending days = 45 } A02 = { country_event = { id = auc_campaign.3 days = 1 } } }
  ai_will_do = { factor = 1 }
 }
}''')
    loc('AUC_retry_sovereignty','Возобновить переговоры о суверенитете','Renew Sovereignty Talks');loc('AUC_retry_sovereignty_desc','Попытаться получить независимость дипломатическим путём после отказа.','Seek negotiated independence after an earlier refusal.')
    loc('AUC_seek_recognition','Добиться признания независимости','Seek Recognition of Independence');loc('AUC_seek_recognition_desc','После 180 дней войны, удерживая Новый Южный Уэльс и все свои владения, предложить Британии перемирие. Британский игрок может отказать.','After 180 days of war, retain New South Wales and control all owned territory to propose an armistice. Britain may refuse.')
    write('common/decisions/AUC_campaign.txt','\n'.join(rows))
    write('common/decisions/categories/AUC_campaign.txt','AUC_federation_category = { icon = generic_political_discourse visible = { tag = A07 has_completed_focus = AUC_A07_leagues } }\nAUC_defence_category = { icon = generic_political_discourse visible = { tag = A07 OR = { has_country_flag = AUC_commonwealth_proclaimed has_country_flag = AUC_independence_war_started } } }')

def ideas():
    spirit('AUC_AVC_tariffs','Викторианский тарифный компромисс','Victorian Tariff Compromise','Поддержка местных предприятий повышает промышленную эффективность.','Support for local firms improves efficiency.','production_factory_efficiency_gain_factor = 0.05')
    spirit('AUC_AQL_districts','Соглашение северных округов','Northern District Compact','Представительство округов укрепляет поддержку кабинета.','District representation strengthens the cabinet.','stability_factor = 0.04 recruitable_population_factor = 0.05')
    spirit('AUC_ASA_inland','Снабжение внутренних районов','Inland Supply Service','Организованные поставки сокращают расход снабжения.','Organised deliveries reduce supply consumption.','supply_consumption_factor = -0.05')
    spirit('AUC_AWA_surveys','Изыскания западной дороги','Western Railway Surveys','Подготовленные проекты облегчают строительство инфраструктуры.','Prepared plans improve infrastructure construction.','production_speed_infrastructure_factor = 0.10')
    spirit('AUC_ATA_shipping','Тасманийское каботажное сообщение','Tasmanian Coastal Shipping','Каботажные службы улучшают защиту транспортов.','Coastal shipping services improve convoy protection.','convoy_escort_efficiency = 0.08')
    spirit('AUC_local_parliament','Самостоятельный колониальный кабинет','Separate Colonial Cabinet','Парламент сохраняет контроль над местной политикой.','Parliament retains control of local affairs.','political_power_gain = 0.10 stability_factor = 0.03')
    spirit('AUC_territorial_staff','Территориальные штабы','Territorial Staffs','Обученные штабисты поддерживают оборону.','Trained staff officers support territorial defence.','army_defence_factor = 0.04')
    spirit('AUC_coastal_watch','Береговая дозорная сеть','Coastal Watch Network','Наблюдение и связь помогают гарнизонам готовиться к высадкам.','Watchers and signals help garrisons prepare for landings.','army_defence_factor = 0.03 convoy_escort_efficiency = 0.03')
    spirit('AUC_escorts','Австралийская конвойная служба','Australian Convoy Service','Регулярное сопровождение поддерживает морские поставки.','Regular escorts sustain maritime supplies.','convoy_escort_efficiency = 0.10')
    spirit('AUC_pacific_line','Тихоокеанский оборонный рубеж','Pacific Defence Line','Согласованная работа штаба повышает готовность флота.','Staff coordination improves naval readiness.','navy_org_factor = 0.05 naval_coordination = 0.05')
    spirit('AUC_federal_compact','Федеральный договор','Federal Compact','Конституция согласует общую власть с правами штатов.','The constitution balances federal authority and state rights.','political_power_gain = 0.10 stability_factor = 0.04')
    spirit('AUC_common_market','Общий австралийский рынок','Australian Common Market','Унифицированные правила поддерживают строительство предприятий.','Common rules support industrial construction.','production_speed_industrial_complex_factor = 0.07')
    spirit('AUC_sovereign_policy','Суверенная внешняя политика','Sovereign Foreign Policy','Кабинет самостоятельно определяет курс федерации.','The cabinet determines the federation\'s own course.','political_power_gain = 0.10')
    spirit('AUC_independent_logistics','Независимая морская логистика','Independent Maritime Logistics','Собственные маршруты уменьшают зависимость от метрополии.','Domestic routes reduce dependence on the former metropole.','supply_consumption_factor = -0.05 convoy_escort_efficiency = 0.05')

def main():
    ideas();local_campaigns();federal_campaign();diplomacy();mechanics();decisions()
    # Retain the legacy WTN focus IDs for saves, but assign only the six new trees.
    legacy=ROOT/'common/national_focus/WTN_AUS_focus.txt'
    if legacy.exists():
        text=legacy.read_text(encoding='utf-8-sig')
        text=re.sub(r'country = \{ factor = 0(?: modifier = \{ add = 100 tag = [A-Z0-9]+ \})* \}', 'country = { factor = 0 }',text,count=1)
        legacy.write_text(text,encoding='utf-8')
    loc('AUC_research','Австралийские технические исследования','Australian Technical Research')
    for suffix in ('','_DEF','_democratic','_democratic_DEF','_neutrality','_neutrality_DEF'):
        loc('AUC_COMMONWEALTH'+suffix,'Австралийское Содружество','Commonwealth of Australia')
    for suffix in ('_ADJ','_democratic_ADJ','_neutrality_ADJ'):
        loc('AUC_COMMONWEALTH'+suffix,'Австралийск.','Australian')
    for key,ru,en in [
      ('AUC_referendum_tt','Пять колоний получат предложение о вступлении. Их согласие требуется отдельно.','Five colonies receive invitations. Each must approve separately.'),
      ('AUC_charter_tt','Британия решит, разрешить ли федерацию под короной. Независимость не предоставляется.','Britain decides whether to permit a federation under the Crown. Independence is not granted.'),
      ('AUC_federate_tt','Согласившиеся колонии войдут в федерацию вместе с войсками. Отказавшиеся сохранят самостоятельность.','Consenting colonies and their forces join the federation; rejecting colonies remain separate.'),
      ('AUC_sovereignty_tt','Британия может признать независимость или отвергнуть требование.','Britain may recognise independence or reject the demand.'),
      ('AUC_independence_war_tt','Начнётся настоящая война за независимость против Британии.','Immediately begins a real independence war against Britain.')]:loc(key,ru,en)
    for tag,rows in TREES.items():
        text=f'focus_tree = {{ id = AUC_campaign_{tag} country = {{ factor = 0 modifier = {{ add = 200 tag = {tag} }} }} default = no continuous_focus_position = {{ x = 100 y = 2200 }}\n'
        write(f'common/national_focus/AUC_campaign_{tag}.txt',text+'\n'.join(r['script'] for r in rows)+'\n}')
    write('events/AUC_campaign.txt','\n\n'.join(EVENTS))
    write('common/characters/AUC_campaign.txt','characters = { AUC_edmund_barton = { name = AUC_edmund_barton_name country_leader = { ideology = conservatism expire = "1965.1.1.1" traits = { } } } }')
    loc('AUC_edmund_barton_name','Эдмунд Бартон','Edmund Barton')
    write('common/ideas/AUC_campaign.txt','ideas = { country = {\n'+'\n'.join(IDEAS)+'\n} }')
    for lang,entries in LOC.items():write(f'localisation/{lang}/AUC_campaign_l_{lang}.yml','l_'+lang+':\n'+'\n'.join(f' {k}:0 "{v.replace(chr(34),chr(39))}"' for k,v in entries.items()),True)
    manifest={tag:[{k:v for k,v in row.items() if k!='script'} for row in rows] for tag,rows in TREES.items()}
    write('tools/australian_campaign_manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
    # Reuse the installed game's Commonwealth flag, with a local flag fallback.
    game=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
    for size in ('','medium','small'):
        source=game/'gfx/flags'/size/'AST_democratic.tga'
        if not source.exists():source=ROOT/'gfx/flags'/size/'A07_democratic.tga'
        for suffix in ('','_democratic','_neutrality'):
            dest=ROOT/'gfx/flags'/size/f'AUC_COMMONWEALTH{suffix}.tga'
            shutil.copyfile(source,dest)
    from focus_shapes import apply as apply_shapes
    apply_shapes()
    print(f'Built {len(TREES)} Australian base trees, with compact layouts and policy forks.')

if __name__=='__main__':main()
