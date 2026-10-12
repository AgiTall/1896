"""One-time migration of the 1893 country foundation. Backups are never overwritten.

Flags are provisional geometric designs, not author-approved heraldry.
No external portraits are downloaded: new leaders use labelled generic art.
"""
from pathlib import Path
import copy
import json
import re
import shutil
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parents[1]
G = Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
B = R / 'tools/backups/canon_countries_1893'
MANIFEST = R / 'tools/canon_countries_manifest.json'

def write(relative, text, bom=False):
    p = R / relative
    if p.exists():
        backup = B / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists(): shutil.copy2(p, backup)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8-sig' if bom else 'utf-8')

def parse(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[{}=<>]|[^\s{}=<>]+', re.sub(r'#[^\n]*', '', text))
    pos = 0
    def block(nested=False):
        nonlocal pos
        result = []
        while pos < len(tokens) and tokens[pos] != '}':
            key = tokens[pos]; pos += 1
            if pos < len(tokens) and tokens[pos] in ['=', '<', '>']:
                op = tokens[pos]; pos += 1
                if tokens[pos] == '{':
                    pos += 1; v = block(True)
                else: v = tokens[pos]; pos += 1
                result.append((key, op, v))
            else: result.append((key, None, None))
        if nested:
            assert tokens[pos] == '}'
            pos += 1
        return result
    result = block()
    assert pos == len(tokens)
    return result

def value(node, key): return next(v for k, op, v in node if k == key)
def put(node, key, v):
    node[:] = [(k, op, old) for k, op, old in node if k != key] + [(key, '=', str(v))]
def dump(node, depth=0):
    out = []
    for k, op, v in node:
        prefix = ' ' * depth + k
        if op is None: out.append(prefix)
        elif isinstance(v, list): out.extend([prefix + ' ' + op + ' {', dump(v, depth+1), ' '*depth+'}'])
        else: out.append(prefix+' '+op+' '+v)
    return '\n'.join(out)

states = {}
for p in (R/'history/states').glob('*.txt'):
    tree = parse(p.read_text(encoding='utf-8-sig'))
    body = value(tree, 'state'); sid = int(value(body, 'id'))
    states[sid] = [p, tree, body]
changed = set()

def assign(sid, tag, core=True):
    body = states[sid][2]; hist = value(body, 'history')
    put(hist, 'owner', tag)
    hist[:] = [entry for entry in hist if not (entry[0] == 'add_core_of' and entry[2] == 'ZZZ')]
    if core and not any(k == 'add_core_of' and v == tag for k, op, v in hist): hist.append(('add_core_of', '=', tag))
    changed.add(sid)

splits = []
def split(source, sid, slug, provinces, population, tag, capital_province):
    body = states[source][2]
    original = {int(k) for k, op, v in value(body, 'provinces')}
    assert set(provinces) <= original
    body[:] = [(k, op, [(str(p), None, None) for p in sorted(original-set(provinces))] if k == 'provinces' else v) for k, op, v in body]
    put(body, 'manpower', int(value(body, 'manpower'))-population)
    hist = value(body, 'history')
    # Remove province-specific buildings and VPs that have moved to the new state.
    def filter_moved(node):
        result = []
        for k, op, v in node:
            if k.isdigit() and int(k) in provinces: continue
            if k == 'victory_points' and int(v[0][0]) in provinces: continue
            result.append((k, op, filter_moved(v) if isinstance(v, list) else v))
        return result
    hist[:] = filter_moved(hist)
    new_text = f'''state = {{
 id = {sid}
 name = "STATE_{sid}"
 manpower = {population}
 state_category = rural
 history = {{
  owner = {tag}
  add_core_of = {tag}
  buildings = {{ infrastructure = 2 {capital_province} = {{ naval_base = 1 }} }}
  victory_points = {{ {capital_province} 3 }}
 }}
 provinces = {{ {' '.join(map(str, provinces))} }}
 local_supplies = 0.0
}}'''
    tree = parse(new_text); newbody = value(tree, 'state')
    states[sid] = [R/f'history/states/{sid} - {slug}.txt', tree, newbody]
    changed.update([source, sid]); splits.append({'source':source,'new_state':sid,'provinces':provinces})

# ru, en, ru leader, en leader, capital, colour, emblem, active
COUNTRIES = {
 'A02':('Британский Левиафан','British Leviathan','Королева Виктория','Queen Victoria',116,(38,65,120),'union',True),
 'A04':('Всемирная торговая палата','World Trade Chamber','Директор Ламберт','Director Lambert',697,(174,135,45),'compass',True),
 'A05':('Железный Союз','Iron Union','Адмирал Грейвс','Admiral Graves',315,(47,72,105),'star',True),
 'A06':('Российская империя в изгнании','Russian Empire in Exile','Александр III','Alexander III',100,(110,72,145),'tricolor',True),
 'A07':('Австралийский Доминион','Australian Dominion','Сэр Генри Паркс','Sir Henry Parkes',285,(40,108,111),'stars',True),
 'A08':('Северная Армия Чистой Земли','Northern Army of the Pure Land','Сайго Такамори','Saigo Takamori',536,(93,104,53),'sun',True),
 'A09':('Партия Золотой Середины','Golden Mean Party','Ивасаки Яносукэ','Iwasaki Yanosuke',531,(179,133,47),'diamond',True),
 'A10':('Конфедерация Филиппинских Островов','Confederation of the Philippine Islands','Правительство в изгнании','Government in Exile',1084,(54,116,139),'sunstar',True),
 'PCF':('Рыцари Конфедерации','Knights of the Confederacy','Сенатор Борегар','Senator Beauregard',1082,(147,76,70),'cross',True),
 'PAZ':('Ацтекское Возрождение','Aztec Revival','Генералиссимус Эрнандес','Generalissimo Hernandez',1083,(96,125,64),'sun',True),
 'PHR':('Дети Урагана','Children of the Hurricane','Маман Бриджит','Maman Brigitte',318,(117,67,132),'spiral',True),
 'PLS':('Католическая Республика Лусон','Catholic Republic of Luzon','Эмилио Агинальдо','Emilio Aguinaldo',623,(177,160,92),'cross',True),
 'PSL':('Султанат Сулу','Sultanate of Sulu','Джамалул Кирам II','Jamalul Kiram II',1025,(39,122,92),'crescent',True),
 'PHW':('Королевство Гавайи','Kingdom of Hawaii','Дэвид Калакауа','David Kalakaua',629,(155,64,79),'hawaii',True),
 'PSY':('Султанат Сейшелы','Sultanate of Seychelles','Наследник Баргаша','Heir of Barghash',709,(90,145,130),'crescent',True),
 'PCB':('Республика Себу','Republic of Cebu','Совет торговых домов','Council of Trading Houses',628,(57,145,170),'compass',True),
 'PPN':('Конфедерация Панай','Panay Confederation','Совет касиков','Council of Caciques',1085,(143,115,66),'stars',True),
 'PTG':('Королевство Тонга','Kingdom of Tonga','Джордж Тупоу II','George Tupou II',None,(167,51,59),'cross',False),
 'PKR':('Курильский рубеж','Kuril Frontier','Адмирал Старик','Admiral Starik',None,(68,113,143),'anchor',False),
 'PPM':('Поморская вольница','Pomor Free Community','Совет капитанов','Council of Captains',None,(69,133,147),'anchor',False),
 'PZN':('Занзибарские Молчаливые','Silent Ones of Zanzibar','Старейшины жестового языка','Sign Language Elders',None,(133,119,68),'circle',False),
 'PPE':('Пираты Пембы','Pirates of Pemba','Капитан Чёрный Ахмед','Captain Black Ahmed',None,(62,68,72),'crossbones',False),
}

def generate():
    if MANIFEST.exists(): raise SystemExit('Migration already applied. Edit final files; do not regenerate over manual work.')
    # Three Cuban governments; population is split without duplicating the island total.
    split(315,1082,'Central Cuba',[7451,10374,4476],1200000,'PCF',10374)
    split(315,1083,'Eastern Cuba',[7546,1550,7590,12347],1400000,'PAZ',7590)
    # Cavite/Batangas is represented at province scale, not a newly painted city polygon.
    split(327,1084,'Cavite and Southern Luzon',[1221,4288,10272,12236],700000,'A10',1221)
    split(628,1085,'Panay',[1368,7423,10302],550000,'PPN',7423)
    ownership = {
     'A02':[116,118,284,1079,1080,1081,299,326,636,634,696,703,704,707,1021,639,689,690,691,692,693,101],
     'A01':[333,695], 'A04':[697,710], 'A06':[100],
     'A07':[285,517,518,519,520,521,522,674,870,871,872,873,1074,1075,523],
     'A08':[536], 'A09':[531], 'A03':[282,526,633,645,327,1027],
     'A10':[624,625,627,1026], 'PLS':[623], 'PSL':[1025],
     'PHW':[629], 'PSY':[709], 'PCB':[628], 'PHR':[318], 'PAZ':[319],
    }
    for tag, ids in ownership.items():
        for sid in ids: assign(sid,tag)
    # Old VTP holdings contradict the supplied canon. Panama/Aden/Socotra remain
    # outside this state-foundation batch; no invented replacement state is used.
    for sid in [685,906,992]: assign(sid,'ZZZ')
    # Manila is occupied Japanese territory; the confederation retains a claim/core.
    value(states[327][2],'history').append(('add_core_of','=','A10'))
    # Danish formal rights in Greenland are represented by a claim, not an invented
    # independent Danish administration with additional land.
    value(states[101][2],'history').append(('add_claim_by','=','DEN'))
    for sid in sorted(changed):
        p, tree, body = states[sid]
        write(p.relative_to(R),dump(tree)+'\n')

    tags=[]; colours=[]; ru=['l_russian:']; en=['l_english:']
    armies={}; roster=[]
    for tag,(name,english,leader,english_leader,capital,colour,emblem,active) in COUNTRIES.items():
        if tag not in ['A02','A04','A05','A06','A07','A08','A09','A10']:
            tags.append(f'{tag} = "countries/{tag}.txt"')
        culture = 'asian_gfx' if tag in ['A08','A09','A10','PLS','PSL','PCB','PPN'] else 'western_european_gfx'
        write(f'common/countries/{tag}.txt',f'graphical_culture = {culture}\ngraphical_culture_2d = western_european_2d\ncolor = rgb {{ {" ".join(map(str,colour))} }}\n')
        colours.append(f'{tag} = {{ color = rgb {{ {" ".join(map(str,colour))} }} color_ui = rgb {{ {" ".join(map(str,colour))} }} }}')
        subtype='oligarchism' if tag in ['A04','A09','PCB','PPN'] else 'despotism'
        character=f'{tag}_canon_leader'
        portrait='gfx/leaders/Asia/Portrait_Asia_Generic_1.dds' if culture=='asian_gfx' else 'gfx/leaders/Europe/Portrait_Europe_Generic_1.dds'
        assert (G/portrait).exists(),portrait
        write(f'common/characters/{tag}_canon.txt',f'characters = {{ {character} = {{ name = {character}_name portraits = {{ civilian = {{ large = "{portrait}" }} }} country_leader = {{ ideology = {subtype} expire = "1965.1.1.1" traits = {{ }} }} }} }}\n')
        history=f'# Canon 1893. Generic portrait; historical likeness not supplied.\n'
        if capital is not None: history+=f'capital = {capital}\n'
        history+=f'recruit_character = {character}\nset_politics = {{ ruling_party = neutrality elections_allowed = no }}\nset_popularities = {{ neutrality = 100 }}\nset_research_slots = 2\nset_stability = 0.50\nset_war_support = 0.30\nset_convoys = {50 if tag in ["A02","A04","A07"] else 10 if active else 0}\n'
        history+='set_technology = { infantry_weapons = 1 }\nadd_ideas = volunteer_only\nadd_ideas = civilian_economy\nadd_ideas = limited_exports\n'
        if active:
            provinces=[int(k) for k,op,v in value(states[capital][2],'provinces')]
            hist=value(states[capital][2],'history')
            vp=next((int(v[0][0]) for k,op,v in hist if k=='victory_points'),provinces[0])
            count=3 if tag in ['A02','A05','A06','A07','A08','PCF','PAZ'] else 1
            template='Island Garrison'
            unittext=f'division_template = {{ name = "{template}" regiments = {{ infantry = {{ x = 0 y = 0 }} infantry = {{ x = 0 y = 1 }} infantry = {{ x = 0 y = 2 }} }} }}\nunits = {{\n'
            for n in range(count): unittext+=f' division = {{ name = "{tag} {n+1}" location = {vp} division_template = "{template}" start_experience_factor = 0.1 start_equipment_factor = 0.7 }}\n'
            unittext+='}\n'; write(f'history/units/{tag}_1893.txt',unittext)
            history+=f'oob = "{tag}_1893"\n'; armies[tag]=count
        existing=next((R/'history/countries').glob(f'{tag} - *.txt'),None)
        write(existing.relative_to(R) if existing else f'history/countries/{tag} - Canon.txt',history)
        for group,label,lname in [(ru,name,leader),(en,english,english_leader)]:
            for suffix in ['', '_DEF','_ADJ','_neutrality','_neutrality_DEF','_neutrality_ADJ']:
                group.append(f' {tag}{suffix}:0 "{label}"')
            group.append(f' {character}_name:0 "{lname}"')
        roster.append({'tag':tag,'name':name,'leader':leader,'capital':capital,'active':active,'flag':'provisional geometric design','portrait':'generic, not historical'})
        flag(tag,colour,emblem)
    write('common/country_tags/02_canon_1893.txt','\n'.join(tags)+'\n')
    # Update existing colour entries without duplicating tags across colour files.
    old=(R/'common/countries/colors.txt').read_text(encoding='utf-8-sig')
    old='\n'.join(line for line in old.splitlines() if not re.match(r'('+'|'.join(COUNTRIES)+r')\s*=',line))
    write('common/countries/colors.txt',old+'\n'+'\n'.join(colours)+'\n')
    write('localisation/russian/zzzzz_canon_countries_l_russian.yml','\n'.join(ru)+'\n',True)
    write('localisation/english/zzzzz_canon_countries_l_english.yml','\n'.join(en)+'\n',True)
    # Japan now governs from Tokyo; old Osaka-based formations move to Japanese ports.
    p=R/'history/countries/A03 - Placeholder.txt'
    write(p.relative_to(R),p.read_text(encoding='utf-8-sig').replace('capital = 531','capital = 282'))
    for p in (R/'history/units').glob('A03*.txt'):
        t=p.read_text(encoding='utf-8-sig')
        for province in [7072,11960,4142,1136]:
            t=re.sub(r'(\b(?:location|naval_base)\s*=\s*)'+str(province)+r'\b',r'\g<1>9998',t)
        if t!=p.read_text(encoding='utf-8-sig'): write(p.relative_to(R),t)
    diplomacy()
    preview()
    report={'countries':roster,'changed_states':sorted(changed),'state_splits':splits,'starter_divisions':armies,
     'limits':['Generic portraits, provisional flags and starter garrison balance','Tonga, Kurils, Svalbard, Zanzibar and Pemba are registered but inactive until map representation is supplied','Russian Maltese court and nomadic fleets are not given invented territory','Western Hispaniola assigned to Hurricane per detailed geographic register; older east-Hispaniola entry conflicts','Cavite/Batangas uses existing province-scale geography','VTP retains Madeira as technical host for existing A04 events; organisational migration is pending','No engine campaign test']}
    write('tools/canon_countries_manifest.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n')

def flag(tag,colour,emblem):
    im=Image.new('RGB',(328,208),colour); d=ImageDraw.Draw(im); gold=(239,211,130); white=(241,236,218); red=(172,49,57)
    if emblem=='union':
        d.line((0,0,328,208),fill=white,width=27);d.line((328,0,0,208),fill=white,width=27)
        d.rectangle((136,0,192,208),fill=white);d.rectangle((0,76,328,132),fill=white)
        d.rectangle((148,0,180,208),fill=red);d.rectangle((0,88,328,120),fill=red)
    elif emblem=='tricolor':
        d.rectangle((0,0,328,69),fill=white);d.rectangle((0,70,328,139),fill=(46,81,144));d.rectangle((0,140,328,208),fill=red)
    elif emblem=='hawaii':
        for n in range(8): d.rectangle((0,n*26,328,(n+1)*26),fill=[white,red,(40,65,125)][n%3])
        d.rectangle((0,0,145,104),fill=(40,65,125));d.line((0,0,145,104),fill=white,width=14);d.line((145,0,0,104),fill=white,width=14);d.line((72,0,72,104),fill=red,width=16);d.line((0,52,145,52),fill=red,width=16)
    elif emblem=='cross':
        d.rectangle((145,38,183,170),fill=white);d.rectangle((109,76,219,110),fill=white)
    elif emblem=='crescent':
        d.ellipse((112,45,220,163),fill=gold);d.ellipse((142,35,232,145),fill=colour)
    elif emblem in ['sun','sunstar']:
        import math
        for n in range(12):
            a=n*math.pi/6;d.line((164+42*math.cos(a),104+42*math.sin(a),164+72*math.cos(a),104+72*math.sin(a)),fill=gold,width=8)
        d.ellipse((123,63,205,145),fill=gold)
    elif emblem=='diamond': d.polygon([(164,37),(235,104),(164,171),(93,104)],fill=gold);d.polygon([(164,64),(205,104),(164,144),(123,104)],fill=colour)
    elif emblem=='spiral':
        import math
        pts=[(164+(7+i*.2)*math.cos(i*.05),104+(7+i*.2)*math.sin(i*.05)) for i in range(260)]
        d.line(pts,fill=white,width=12)
    elif emblem=='anchor':
        d.ellipse((146,35,182,71),outline=white,width=8);d.line((164,65,164,157),fill=white,width=10);d.line((124,91,204,91),fill=white,width=10);d.arc((109,84,219,168),0,180,fill=white,width=10)
    elif emblem=='crossbones':
        d.line((114,63,214,145),fill=white,width=13);d.line((214,63,114,145),fill=white,width=13)
    elif emblem=='circle': d.ellipse((112,52,216,156),outline=white,width=12)
    else:
        import math
        count=5 if emblem=='stars' else 1
        for n in range(count):
            cx=164 if count==1 else 164+60*math.cos(n*math.tau/count);cy=104 if count==1 else 104+60*math.sin(n*math.tau/count)
            radius=48 if count==1 else 18
            pts=[(cx+(radius if j%2==0 else radius*.4)*math.cos(-math.pi/2+j*math.pi/5),cy+(radius if j%2==0 else radius*.4)*math.sin(-math.pi/2+j*math.pi/5)) for j in range(10)]
            d.polygon(pts,fill=gold)
    for folder,size in [('',(82,52)),('medium',(41,26)),('small',(10,7))]:
        relative=Path('gfx/flags')/folder/f'{tag}.tga';p=R/relative
        if p.exists():
            backup=B/relative;backup.parent.mkdir(parents=True,exist_ok=True)
            if not backup.exists():shutil.copy2(p,backup)
        p.parent.mkdir(parents=True,exist_ok=True)
        im.resize(size,Image.Resampling.LANCZOS).convert('RGBA').save(p)

def diplomacy():
    pairs=[('A02','A04','pz_commercial_partner'),('A02','A06','pz_exile_solidarity'),('A02','A07','pz_common_heritage'),('A01','A02','pz_commercial_partner'),('A01','A04','pz_debt_dependence'),('A03','A04','pz_commercial_partner'),('A03','A01','pz_oil_rivalry'),('A03','A08','pz_japanese_schism'),('A03','A09','pz_japanese_schism'),('A08','A09','pz_japanese_schism'),('A03','A10','pz_occupation'),('A03','PLS','pz_occupation'),('A03','PSL','pz_occupation'),('A10','PLS','pz_resistance'),('A10','PCB','pz_federal_dispute'),('A10','PPN','pz_federal_dispute'),('A10','PSL','pz_mutual_suspicion'),('A03','A07','pz_pacific_rivalry'),('A01','A07','pz_papua_dispute'),('A05','PCF','pz_caribbean_conflict'),('A05','PAZ','pz_caribbean_conflict'),('PCF','PAZ','pz_caribbean_conflict'),('PHR','PAZ','pz_caribbean_conflict')]
    mods={'pz_commercial_partner':25,'pz_exile_solidarity':35,'pz_common_heritage':40,'pz_debt_dependence':-15,'pz_oil_rivalry':-60,'pz_japanese_schism':-40,'pz_occupation':-80,'pz_resistance':35,'pz_federal_dispute':-15,'pz_mutual_suspicion':-20,'pz_pacific_rivalry':-35,'pz_papua_dispute':-25,'pz_caribbean_conflict':-80}
    write('common/opinion_modifiers/pz_canon_1893.txt','opinion_modifiers = {\n'+''.join(f' {key} = {{ value = {v} }}\n' for key,v in mods.items())+'}\n')
    effect='PZ_initialize_canon_relations_effect = {\n if = {\n  limit = { NOT = { has_global_flag = PZ_canon_relations_initialized } }\n  set_global_flag = PZ_canon_relations_initialized\n'
    for a,b,mod in pairs:
        effect+=f'  if = {{ limit = {{ country_exists = {a} country_exists = {b} }} {a} = {{ add_opinion_modifier = {{ target = {b} modifier = {mod} }} }} {b} = {{ add_opinion_modifier = {{ target = {a} modifier = {mod} }} }} }}\n'
    # Political sympathies are not automatic wars or military alliances.
    effect+=' }\n}\n'
    write('common/scripted_effects/pz_canon_relations.txt',effect)
    write('common/on_actions/pz_canon_relations.txt','on_actions = { on_startup = { effect = { PZ_initialize_canon_relations_effect = yes } } }\n')
    names={'pz_commercial_partner':('Торговые связи','Commercial ties'),'pz_exile_solidarity':('Солидарность изгнанников','Solidarity in exile'),'pz_common_heritage':('Общее наследие','Common heritage'),'pz_debt_dependence':('Долговая зависимость','Debt dependence'),'pz_oil_rivalry':('Борьба за нефть','Oil rivalry'),'pz_japanese_schism':('Японский раскол','Japanese schism'),'pz_occupation':('Оккупация и сопротивление','Occupation and resistance'),'pz_resistance':('Общее сопротивление','Shared resistance'),'pz_federal_dispute':('Спор о федерации','Federal dispute'),'pz_mutual_suspicion':('Взаимное недоверие','Mutual suspicion'),'pz_pacific_rivalry':('Тихоокеанское соперничество','Pacific rivalry'),'pz_papua_dispute':('Спор о Новой Гвинее','New Guinea dispute'),'pz_caribbean_conflict':('Карибская вражда','Caribbean hostility')}
    for lang,index in [('russian',0),('english',1)]:
        write(f'localisation/{lang}/pz_relations_l_{lang}.yml',f'l_{lang}:\n'+''.join(f' {k}:0 "{v[index]}"\n' for k,v in names.items()),True)

def preview():
    sheet=Image.new('RGB',(720,((len(COUNTRIES)+3)//4)*105),(25,29,36));d=ImageDraw.Draw(sheet)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
    for n,(tag,data) in enumerate(COUNTRIES.items()):
        x=(n%4)*180;y=(n//4)*105
        sheet.paste(Image.open(R/f'gfx/flags/{tag}.tga').resize((123,78)),(x+10,y+3))
        d.text((x+10,y+83),tag+' — '+data[1][:17],font=font,fill=(240,235,220))
    sheet.save(R/'tools/canon_flags_preview.png')

if __name__=='__main__': generate()
