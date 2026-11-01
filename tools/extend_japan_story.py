"""Idempotent story extension. Preserves other authors' focus additions."""
from pathlib import Path
import re,json,shutil
from PIL import Image,ImageOps
from add_canon_countries import parse,value
R=Path(__file__).resolve().parents[1]
def read(p): return (R/p).read_text(encoding='utf-8-sig')
def write(p,s,bom=False):
 p=R/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8-sig' if bom else 'utf-8',newline='\n')
def span(s,ident,kind='focus'):
 for m in re.finditer(r'\b'+kind+r'\s*=\s*\{',s):
  start=m.start();i=m.end();depth=1;quoted=False
  while depth:
   if s[i]=='"' and s[i-1]!='\\':quoted=not quoted
   if not quoted:depth+=(s[i]=='{')-(s[i]=='}')
   i+=1
  if re.search(r'\bid\s*=\s*'+re.escape(ident)+r'\b',s[m.end():i]):return start,i
 raise ValueError(ident)
def edit_focus(s,ident,hook=None,xy=None):
 a,b=span(s,ident);part=s[a:b]
 if hook and hook not in part:part=re.sub(r'completion_reward\s*=\s*\{','completion_reward = { '+hook,part,count=1)
 if xy:
  for k,v in zip(('x','y'),xy):part=re.sub(r'\b'+k+r'\s*=\s*\d+',f'{k} = {v}',part,count=1)
 return s[:a]+part+s[b:]
LOC={}
def loc(k,ru,en):LOC[k]=(ru,en)
FS=[]
def focus(fid,parent,x,y,ru,en,desc,eng,effect,icon='credit',available=''):
 FS.append(dict(id=fid,parent=parent,x=x,y=y,ru=ru,en=en,desc=desc,eng=eng,effect=effect,icon=icon,available=available))
 loc(fid,ru,en);loc(fid+'_desc',desc,eng)

focus('JPF_bond_register','JPC_iwasaki_accounts',2,4,'Реестр обещаний','Register of Promises','За каждым новым корпусом стоит чужая расписка. Разделить государственный долг и обязательства Мицубиси — первый шаг к выплатам. Открывает обслуживание облигаций.','Every hull has a creditor. Separate public bonds from Mitsubishi liabilities and open regular repayments.','set_country_flag = JPF_bond_register JPF_audit_savings_effect = yes')
focus('JPF_public_accounts','JPF_bond_register',2,5,'Книги для императора','Books for the Emperor','Ивасаки согласен показать книги, но не простит публичного унижения. Независимая проверка снизит долговое давление и вернёт доверие вкладчиков; публикация отчётов станет постоянной мерой.','Iwasaki will open his books, but will resent humiliation. Independent audits reduce pressure and unlock published accounts.','JPF_reform_accounts_effect = yes')
focus('JPF_small_subscription','JPF_bond_register',5,5,'Сбережения нации','The Nation’s Savings','Мелкие вкладчики могут профинансировать транспорты. Подписка добровольна лишь пока казначейству верят; после войны деньги придётся вернуть.','Small savers can finance transports while confidence lasts. Their money must eventually be returned.','set_country_flag = JPF_subscription_open add_to_variable = { JPF_budget_confidence = 5 } JPF_refresh_effect = yes')
focus('JPF_excise_bargain','JPF_public_accounts',2,6,'Цена акцизного мира','The Excise Bargain','Новые акцизы дадут деньги без кредита, но переложат расходы на города. Разрешить сбор: меньше долга ценой доверия, стабильности и строительства.','Excises pay creditors without new borrowing, at the cost of confidence, stability and construction.','set_country_flag = JPF_excise_open add_political_power = 20')
focus('JPF_delivery_calendar','JPF_public_accounts',5,7,'Календарь платежей','Calendar of Payments','Осакские верфи, угольщики и флот предъявляют одни и те же счета по три раза. Единый график сокращает ежемесячный рост долга, но требует признать все обязательства.','A single delivery calendar cuts monthly debt growth, while acknowledging outstanding invoices.','set_country_flag = JPF_delivery_schedule JPF_audit_savings_effect = yes JPF_fleet_invoice_effect = yes')
focus('JPF_coal_not_glory','JPF_delivery_calendar',2,8,'Уголь прежде славы','Coal Before Glory','Сократить парадные рейсы и закрепить угольные контракты за действующими эскадрами. Экономия снабжения потребует ещё одного военного расхода сейчас.','Reserve coal for active squadrons. Lower fleet supply consumption requires another expenditure now.','add_ideas = JPF_coal_contracts JPF_add_war_expense_effect = yes','fleet')
focus('JPF_madeira_table','JPF_delivery_calendar',5,9,'Стол переговоров на Мадейре','The Madeira Table','Палата предлагает мостовой кредит под страховку Серебряного Конвоя. Переговоры открывают выбор: новые транспорты и два долговых счёта либо сокращение гражданских заказов.','The Chamber offers bridge credit under Silver Convoy insurance: transports and two debt ledgers, or civilian retrenchment.','set_country_flag = JPF_credit_table_open JPF_credit_table_effect = yes',available='country_exists = A04 NOT = { has_war_with = A04 }')
focus('JPF_royalty_register','JPC_oil_promise',2,15,'Роялти вместо обещаний','Royalties, Not Promises','Нефть Борнео заложена заранее. Реестр роялти направит часть доходов на долг; обещанная Мицубиси монополия останется ценой победы.','Borneo oil was pledged in advance. Royalties service the debt; Mitsubishi retains its promised monopoly.','set_country_flag = JPF_royalty_office JPF_oil_settlement_effect = yes',available='has_country_flag = A03_borneo_victory')
focus('JPF_return_small_savings','JPC_count_the_cost',5,16,'Вернуть мелкие вклады','Return Small Deposits','Большие кредиторы переждут, семьи погибших — нет. Открыть выкуп мелких облигаций, когда долговое давление позволит это сделать.','Families cannot wait as long as banks. Open redemption of small deposits once debt pressure permits.','set_country_flag = JPF_small_savers add_to_variable = { JPF_budget_confidence = 5 } JPF_refresh_effect = yes')
focus('JPF_civil_budget','JPF_return_small_savings',5,18,'Бюджет после войны','A Budget After War','Закрыть чрезвычайную книгу можно после всех войн, выполнения нефтяных гарантий, выплаты долга Палате и восстановления доверия. Это решение ликвидирует финансовый кризис, но не раскол империи.','Close the emergency ledger after all wars, oil settlement, Chamber repayment and restored confidence. Solvency does not reunite the empire.','set_country_flag = JPF_civil_budget add_political_power = 30')

focus('JPN_north_supply_register','JPC_honshu_depots',10,4,'Северные накладные','Northern Waybills','Нейтралитет Сайго держится на поставках. Вести запас в месяцах и помнить: ящик, ушедший на Хоккайдо, не попадёт на Борнео.','Saigo’s neutrality rests on deliveries. Every crate sent north is absent from Borneo.','add_to_variable = { JPN_north_supply_months = 1 } JPN_north_refresh_effect = yes','north')
focus('JPN_north_civilian_holds','JPN_north_supply_register',8,5,'Хлеб прежде винтовок','Bread Before Rifles','Три гражданских каравана могут заменить часть оружейных поставок. Они стоят денег и судов, но вызывают меньше раздражения у адмиралтейства.','Three civilian charters can substitute for rifle deliveries, spending money and shipping with less naval resentment.','set_country_flag = JPN_north_civilian_holds add_timed_idea = { idea = JPN_north_civilian_charters days = 180 }','north')
focus('JPN_north_emergency_calendar','JPN_north_supply_register',12,5,'Письменная отсрочка','A Written Postponement','Сайго признаёт нужды действующего флота. Две письменные отсрочки сохранят график, но каждая подорвёт доверие Севера.','Saigo allows two wartime postponements. Each keeps the schedule at the expense of northern trust.','set_country_flag = JPN_north_emergency_schedule add_political_power = 15','north')
focus('JPN_north_inspection_channel','JPN_north_civilian_holds',8,6,'Инспекторы без солдат','Inspectors Without Soldiers','Послать наблюдателей в склады, не превращая проверку в оккупацию. Сайго сам определит границы допуска. Открывает событие о полномочиях комиссии.','Inspect warehouses without an occupation force. Negotiate the commission’s authority with Saigo.','set_country_flag = JPN_north_inspection_channel JPN_north_inspection_queue_effect = yes','north')
focus('JPN_north_tokyo_auditors','JPN_north_inspection_channel',8,7,'Проверить Токио тоже','Audit Tokyo Too','Ошибки бывают по обе стороны пролива. Проверка отправителей снизит раздражение флота каждый месяц и принесёт казначейству ограниченную экономию.','Inspect the senders as well. Monthly naval resentment falls, with a limited treasury saving.','set_country_flag = JPN_north_tokyo_auditors JPF_audit_savings_effect = yes','north')
focus('JPN_north_admiralty_hearing','JPN_north_emergency_calendar',12,7,'Слушание адмиралтейства','The Admiralty Hearing','Ито считает нейтралитет привилегией трусов. Дать его офицерам слово и снизить раздражение, не требуя северных дивизий.','Ito calls neutrality a coward’s privilege. Hear his officers without demanding northern divisions.','add_to_variable = { JPN_north_fleet_irritation = -10 } JPN_north_refresh_effect = yes','fleet')
focus('JPN_north_imperial_arbitration','JPN_north_tokyo_auditors',10,9,'Арбитраж Мэйдзи','Meiji’s Arbitration','Шесть месяцев личного арбитража не дадут сорвать протокол из-за нового спора. Примирение не заменяет поставок.','Six months of imperial arbitration prevent a new dispute from breaking the protocol. Deliveries remain necessary.','set_country_flag = { flag = JPN_north_arbitration_grace days = 180 } add_to_variable = { JPN_north_trust = 8 } add_to_variable = { JPN_north_fleet_irritation = -8 } JPN_north_refresh_effect = yes','north')
focus('JPN_north_postwar_audience','JPC_three_heads_again',10,15,'Вернувшаяся телеграмма','The Telegram Returns','Война кончилась, а Север всё ещё ждёт ответа. Личная аудиенция откроет переговоры о постоянном снабжении, не о подчинении Сайго.','The war is over, and the North still awaits an answer. Discuss permanent supply without Saigo’s submission.','JPN_north_postwar_focus_effect = yes add_to_variable = { JPN_north_trust = 8 } JPN_north_refresh_effect = yes','north')
focus('JPN_north_permanent_protocol','JPN_north_postwar_audience',10,16,'Постоянный северный протокол','Permanent Northern Protocol','Доверие выше 54, раздражение флота ниже 60 и реальные запасы позволят подписать компакт. Хоккайдо сохранит нейтралитет, армию и собственную власть.','Trust above 54, resentment below 60 and real supplies allow a compact. Hokkaido retains neutrality, its army and government.','set_country_flag = JPN_north_compact_ready add_political_power = 30','north')
focus('JPN_north_keep_distance','JPN_north_permanent_protocol',10,18,'Мир на расстоянии','Peace at a Distance','Принять пределы договора: Север не даёт солдат, Токио не командует его складами. Снабжение становится постоянным обязательством вместо повторяющихся ультиматумов.','Accept the compact’s limits: no northern soldiers and no Tokyo command over its stores. Permanent obligations replace recurring ultimatums.','add_stability = 0.03','north',available='has_country_flag = JPN_north_compact_signed')

focus('JPL_port_and_mountains','JPC_garrison_accounts',28,5,'Порт и горы','The Port and the Mountains','Манильский порт занят; горы принадлежат Агинальдо. Разрешить сокращение периметра снабжения ценой усталости и боевого духа.','Manila’s port is occupied; Aguinaldo holds the mountains. Shorten the supply perimeter at the cost of fatigue and morale.','add_to_variable = { JPL_garrison_burden = -4 } JPL_refresh_effect = yes','luzon')
focus('JPL_convoy_timetable','JPL_port_and_mountains',26,6,'Рейс до Манилы','The Manila Sailing','Каждый эскорт, отправленный к Маниле, ослабляет борнейскую эскадру. Открывает регулярное выделение охранения с временной потерей организации флота.','Escorts for Manila weaken the Borneo fleet. Open regular escort assignments with a temporary organisation cost.','add_to_variable = { JPL_garrison_burden = -4 } JPL_refresh_effect = yes','luzon')
focus('JPL_names_and_units','JPL_port_and_mountains',30,6,'Имена вместо численности','Names, Not Numbers','В донесениях одни батальоны существуют дважды, другие исчезли совсем. Поимённый реестр позволит проводить ротации за счёт реального резерва.','Reports duplicate some battalions and omit others. Named rolls permit rotations using real manpower.','set_country_flag = JPL_rotation_board add_to_variable = { JPL_garrison_fatigue = -4 } JPL_refresh_effect = yes','luzon')
focus('JPL_municipal_buyers','JPL_convoy_timetable',26,7,'Закупщики муниципалитетов','Municipal Purchasing Agents','Покупать продовольствие через местные управы дороже реквизиций, но дешевле ещё одной экспедиции. Открывает местные закупки ценой роста долга Мицубиси.','Local purchases cost more than requisitions and less than another expedition. Municipal contracts increase Mitsubishi debt.','add_political_power = 20','luzon')
focus('JPL_payroll_inquiry','JPL_names_and_units',30,7,'Следствие по ведомостям','The Payroll Inquiry','Пропавшие жалованья связывают чиновников, поставщиков и офицеров. Вскрыть ведомости: снизить нагрузку, но оставить гарнизон без привычной сети посредников.','Missing wages connect officials, suppliers and officers. Expose the books, reducing burden while disrupting the garrison’s patronage.','country_event = { id = japan_luzon.4 days = 1 }','luzon')
focus('JPL_supply_board','JPL_municipal_buyers',26,9,'Совет манильских поставок','Manila Supply Board','Дать порту единый гражданский заказ вместо трёх военных. Совет уменьшит ежемесячный рост нагрузки на один пункт.','Replace competing military orders with a single port contract. Monthly burden growth falls by one.','set_country_flag = JPL_supply_board JPF_audit_savings_effect = yes','luzon')
focus('JPL_quartermaster_school','JPL_payroll_inquiry',30,9,'Школа интендантов','The Quartermasters’ School','Обучить людей считать потери на пристани, а не после боя. Подготовленные интенданты уменьшат ежемесячный рост нагрузки ещё на один пункт.','Count losses at the pier before combat. Trained quartermasters cut monthly burden growth by another point.','set_country_flag = JPL_quartermasters_trained army_experience = 10','luzon')
focus('JPL_medical_rotation','JPC_hospital_ships',28,10,'Не третий срок в тропиках','No Third Tour in the Tropics','Госпитальные суда не помогут тем, кого сразу возвращают в строй. Ротационная комиссия уменьшит рост усталости, но не заменит резервистов и медикаменты.','Hospital ships cannot help men immediately sent back. A rotation board reduces fatigue growth but still needs replacements and medicine.','set_country_flag = JPL_rotation_board add_to_variable = { JPL_garrison_fatigue = -8 } JPL_refresh_effect = yes','luzon')
focus('JPL_limited_mandate','JPL_supply_board',28,12,'Пределы манильского мандата','Limits of the Manila Mandate','Закрепить ответственность управы за закупки и довольствие. Подотчётная оккупация смягчит политическую цену гарнизона; война с Конфедерацией продолжится.','Make the administration accountable for purchasing and pay. This reduces political costs while the Confederation war continues.','set_country_flag = JPL_limited_mandate JPL_refresh_effect = yes','luzon')
focus('JPL_borneo_is_not_luzon','JPC_count_the_cost',28,15,'Борнео — ещё не Лусон','Borneo Is Not Luzon','Нефтяной мир не снимает осаду дорог Манилы. Вернуть часть охранения с Борнео и помочь усталому гарнизону, заплатив по новому счёту.','Oil peace leaves Manila’s roads contested. Return escorts from Borneo at a fresh financial cost.','JPL_escort_allocation_effect = yes add_to_variable = { JPL_garrison_fatigue = -8 } JPL_refresh_effect = yes','luzon',available='has_country_flag = JPL_theater_active')

def main():
 s=read('common/national_focus/a03_focus.txt')
 if '# JPA player-led preparation' in s:raise SystemExit('Player-led tree is authoritative. Run rework_japan_agency.py; this older expansion would overwrite its choices.')
 # Preserve pre-existing postwar content; relocate it below the canonical settlement.
 tree=value(parse(s),'focus_tree')
 for k,o,n in tree:
  if '# JPS layout normalized' not in s and k=='focus' and value(n,'id').startswith('A03_') and value(n,'id')!='A03_imperial_council':
   s=edit_focus(s,value(n,'id'),xy=(int(value(n,'x'))+6,int(value(n,'y'))+6 if int(value(n,'y'))<20 else int(value(n,'y'))))
 # Stable positions for the 33 canonical focuses, with domestic decisions attached to politics.
 pos={'A03_imperial_council':(20,0),'JPC_state_guarantees':(20,1),'JPC_osaka_orders':(4,2),'JPC_iwasaki_accounts':(4,3),'JPC_northern_protocol':(12,2),'JPC_honshu_depots':(10,3),'JPC_manila_priority':(20,3),'JPC_batavia_demands':(20,4),'JPC_garrison_accounts':(28,4),'JPC_one_war_cabinet':(20,5),'JPC_pledged_yards':(17,6),'JPC_borneo_bridgehead':(20,6),'JPC_regional_dispatches':(36,6),'JPC_convoy_budget':(17,7),'JPC_casualty_returns':(20,7),'JPC_wtc_mission':(34,7),'JPC_honolulu_letters':(38,7),'JPC_australian_assurances':(42,7),'JPC_nz_watch':(42,9),'JPC_war_workshops':(17,8),'JPC_hospital_ships':(22,8),'JPC_no_short_war':(20,9),'JPC_replace_losses':(17,10),'JPC_imperial_inspection':(20,10),'JPC_sulu_escorts':(34,10),'JPC_1895_accounts':(20,11),'JPC_hold_until_talks':(20,12),'JPC_count_the_cost':(20,14),'JPC_oil_promise':(17,15),'JPC_defeat_inquest':(23,15),'JPC_rebuild_ports':(17,16),'JPC_partial_demobilisation':(20,16),'JPC_three_heads_again':(20,17)}
 hooks={'A03_imperial_council':'JPF_initialize_effect = yes JPN_north_initialize_effect = yes JPL_initialize_effect = yes','JPC_state_guarantees':'JPF_state_guarantees_effect = yes','JPC_iwasaki_accounts':'JPF_reform_accounts_effect = yes','JPC_northern_protocol':'JPN_north_protocol_focus_effect = yes','JPC_honshu_depots':'JPN_north_depots_focus_effect = yes','JPC_manila_priority':'JPL_manila_priority_effect = yes','JPC_garrison_accounts':'JPL_garrison_accounts_effect = yes','JPC_pledged_yards':'JPF_fleet_invoice_effect = yes','JPC_hospital_ships':'JPL_hospital_ships_effect = yes','JPC_hold_until_talks':'JPL_hold_until_talks_effect = yes','JPC_oil_promise':'JPF_oil_settlement_effect = yes','JPC_three_heads_again':'JPN_north_postwar_focus_effect = yes'}
 for fid,xy in pos.items():s=edit_focus(s,fid,hooks.get(fid),xy)
 for f in FS:
  if re.search(r'\bid\s*=\s*'+f['id']+r'\b',s):continue
  n=f''' focus = {{ id = {f['id']} icon = GFX_goal_jpc_{f['icon']} x = {f['x']} y = {f['y']} cost = 3
  prerequisite = {{ focus = {f['parent']} }}
  available = {{ {f['available']} }}
  cancel_if_invalid = yes ai_will_do = {{ factor = 5 }}
  search_filters = {{ FOCUS_FILTER_POLITICAL }}
  completion_reward = {{ {f['effect']} }}
 }}\n'''
  s=s.rstrip()[:-1]+n+'}\n'
 s=s.replace('id = JPN_north_postwar_audience icon = GFX_goal_jpc_north x = 10 y = 15','id = JPN_north_postwar_audience icon = GFX_goal_jpc_north x = 10 y = 18').replace('id = JPN_north_permanent_protocol icon = GFX_goal_jpc_north x = 10 y = 16','id = JPN_north_permanent_protocol icon = GFX_goal_jpc_north x = 10 y = 19').replace('id = JPN_north_keep_distance icon = GFX_goal_jpc_north x = 10 y = 18','id = JPN_north_keep_distance icon = GFX_goal_jpc_north x = 10 y = 20').replace('id = JPF_royalty_register icon = GFX_goal_jpc_credit x = 2 y = 15','id = JPF_royalty_register icon = GFX_goal_jpc_credit x = 2 y = 16')
 if '# JPS layout normalized' not in s:s='# JPS layout normalized\n'+s
 write('common/national_focus/a03_focus.txt',s)
 # Actual two-front status follows both wars, including a Philippine peace or lost theatre.
 s=read('events/JPC_canonical.txt').replace('immediate = { add_ideas = JPC_two_fronts }','immediate = { if = { limit = { has_war_with = A10 } add_ideas = JPC_two_fronts } }')
 write('events/JPC_canonical.txt',s)
 write('common/on_actions/JPS_story.txt','''on_actions = {
 on_daily = { effect = { A03 = {
  if = { limit = { has_war_with = A01 has_war_with = A10 } if = { limit = { NOT = { has_idea = JPC_two_fronts } } add_ideas = JPC_two_fronts } }
  else = { remove_ideas = JPC_two_fronts }
 } } }
}
''')
 write('common/on_actions/JPL_luzon.txt','''on_actions = {
 on_startup = { effect = { A03 = { JPL_safety_check_effect = yes } } }
 on_daily = { effect = { A03 = { JPL_safety_check_effect = yes } } }
 on_monthly = { effect = { A03 = { JPL_monthly_effect = yes } } }
}
''')
 # Repeated runs must not move existing extensions a second time.
 # New art is copied before any renderer consumes the DDS assets.
 src=Path('C:/Users/AgiTall/.codex/generated_images/01a13102-7769-7861-8095-eedaf7b2ed52')
 art={'north':'exec-29a18add-b707-4dae-bcb2-b25345d74ae1.png','luzon':'exec-af3803fc-8023-4414-818e-838eb66a047e.png'}
 sprites=[]
 for name,fn in art.items():
  dest=R/f'gfx/interface/jpc_sources/{name}.png';shutil.copy2(src/fn,dest)
  im=Image.open(dest).convert('RGBA');im=im.crop(im.getbbox())
  for folder,size,kind in [('goals',(95,85),'goal'),('ideas',(60,68),'idea')]:
   out=Image.new('RGBA',size);thumb=ImageOps.contain(im,(size[0]-4,size[1]-4),Image.Resampling.LANCZOS);out.alpha_composite(thumb,((size[0]-thumb.width)//2,(size[1]-thumb.height)//2));path=f'gfx/interface/{folder}/jpc_{name}.dds';out.save(R/path)
   sprites.append(f'spriteType = {{ name = "GFX_{kind}_jpc_{name}" texturefile = "{path}" }}')
   if kind=='goal':sprites.append(f'spriteType = {{ name = "GFX_goal_jpc_{name}_shine" texturefile = "{path}" effectFile = "gfx/FX/buttonstate.lua" }}')
 write('interface/JPS_story.gfx','spriteTypes = {\n'+'\n'.join(sprites)+'\n}\n')
 for module,name in [('JPN_north','north'),('JPL_luzon','luzon')]:
  p=f'common/ideas/{module}.txt';write(p,re.sub(r'picture = jpc_(?:fleet|credit)',f'picture = jpc_{name}',read(p)))
 prompts=json.loads(read('gfx/interface/jpc_sources/prompts.json'))
 prompts.update(north='1893 Japanese focus emblem: brass telegraph, sealed neutrality protocol, rice crate and rifles, snowy Hokkaido mountain, crimson bronze laurel. Painted antique metal relief, transparent background, no text.',luzon='1893 tropical garrison hospital emblem: medical steamship, white medicine chest with red cross, lantern and palm silhouette in bronze laurel. Painted antique metal relief, transparent background, no text.')
 write('gfx/interface/jpc_sources/prompts.json',json.dumps(prompts,ensure_ascii=False,indent=2))
 write('tools/japan_story_focuses.json',json.dumps(FS,ensure_ascii=False,indent=2))
 if (R/'tools/japan_story_localisation.json').exists():LOC.update(json.loads(read('tools/japan_story_localisation.json')))
 for lang,i in [('russian',0),('english',1)]:
  write(f'localisation/{lang}/zzzzzzz_JPS_story_l_{lang}.yml','l_'+lang+':\n'+'\n'.join(f' {k}:0 "{v[i].replace(chr(34),chr(39))}"' for k,v in LOC.items())+'\n',True)
 print('Integrated 30 domestic story focuses and two original illustrated emblems.')

if __name__=='__main__':main()
