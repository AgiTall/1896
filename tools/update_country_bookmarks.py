"""Describe new countries and use compact single-paragraph country descriptions."""
from pathlib import Path
import re,shutil
R=Path(__file__).resolve().parents[1]
B=R/'tools/backups/bookmarks_before_short_descriptions'
def write(p,text,bom=False):
    if p.exists():
        b=B/p.relative_to(R);b.parent.mkdir(parents=True,exist_ok=True)
        if not b.exists():shutil.copy2(p,b)
    p.write_text(text,encoding='utf-8-sig' if bom else 'utf-8')
DESCS={
'MLT':('Мальта обрела самостоятельность после переноса британского двора на Бермуды. Государственный совет управляет островом из Валлетты, опираясь на гавань и морскую торговлю. Малому государству предстоит сохранить независимость среди соперничающих морских держав.','Malta has gained independence after the British court moved to Bermuda. The State Council governs from Valletta, relying on its harbour and maritime trade. The island must protect its independence among rival naval powers.'),
'AVC':('Из Мельбурна Уильям Шилс управляет одной из самых развитых австралийских колоний. Промышленность и оживлённый порт дают Виктории вес среди соседей, но торговое соперничество мешает сближению. Колонии предстоит укрепить хозяйство и определить своё место в будущем Австралии.','From Melbourne, William Shiels governs one of the most developed Australian colonies. Industry and a busy port give Victoria influence, but commercial rivalry divides its neighbours. The colony must strengthen its economy and find its place in Australia’s future.'),
'AQL':('Правительство Сэмюэла Гриффита управляет Квинслендом из Брисбена. Прибрежные поселения отделены большими расстояниями, а развитие севера требует дорог, портов и рабочих рук. Британская защита сохраняет морские связи, но будущее колонии зависит от собственного хозяйства.','Samuel Griffith’s government administers Queensland from Brisbane. Great distances separate its coastal settlements, while the north needs roads, ports and labour. British protection maintains maritime links, but the colony’s future rests on its own economy.'),
'ASA':('Джон Даунер управляет Южной Австралией из Аделаиды. Власть колонии простирается до Северной территории, содержание которой ложится тяжёлым бременем на казну. Торговля и развитие путей сообщения должны связать далёкие поселения и укрепить положение колонии среди соседей.','John Downer governs South Australia from Adelaide. The colony also administers the Northern Territory, whose upkeep burdens its treasury. Trade and better transport must connect distant settlements and strengthen its position among the neighbouring colonies.'),
'AWA':('Правительство Джона Форреста управляет Западной Австралией из Перта. Огромные расстояния отделяют колонию от восточных соседей, а новые поселения нуждаются в снабжении и сообщении. Разработка месторождений обещает рост, если удастся связать побережье с внутренними районами.','John Forrest’s government rules Western Australia from Perth. Vast distances separate it from the eastern colonies, and new settlements need supplies and transport. Mining promises growth if the coast can be connected to the interior.'),
'ATA':('Генри Добсон возглавляет правительство Тасмании в Хобарте. Островная колония живёт морской торговлей, сельским хозяйством и связями с материком. Ограниченные средства заставляют беречь казну, а споры о сближении австралийских колоний требуют осторожного выбора.','Henry Dobson leads Tasmania’s government in Hobart. The island colony depends on maritime trade, farming and links with the mainland. Limited funds demand careful spending, while debate over closer ties between the Australian colonies calls for a cautious choice.'),
'A07':('Правительство Джорджа Диббса управляет Новым Южным Уэльсом из Сиднея. Порты, промышленность и торговля дают колонии вес среди австралийских соседей. Британская корона сохраняет верховную власть, но споры о пошлинах и будущем объединении требуют собственного политического курса.','George Dibbs governs New South Wales from Sydney. Ports, industry and trade give the colony influence among its Australian neighbours. The British Crown retains sovereignty, but disputes over tariffs and future federation demand a policy of its own.'),
'A03':('Императорский двор Мэйдзи стремится укрепить Японию среди соперничающих морских держав. Новые заводы и верфи должны стать опорой внешней политики. На севере сохраняется власть армии Сайго, на Филиппинах продолжается сопротивление, а нефть южных морей привлекает всё больше внимания Токио.','Meiji’s court seeks to strengthen Japan among rival maritime powers. New factories and shipyards must underpin its foreign policy. Saigo’s army retains power in the north, resistance continues in the Philippines, and Tokyo increasingly looks towards the oil of the southern seas.')}
def main():
    p=R/'common/bookmarks/the_gathering_storm.txt';text=p.read_text(encoding='utf-8-sig')
    for tag in ('AVC','AQL','ASA','AWA','ATA'):
        text=re.sub(rf'"{tag}"\s*=\s*\{{\s*minor = yes ideology = democratic ideas = \{{ \}} focuses = \{{ \}} \}}',f'"{tag}" = {{ minor = yes history = "{tag}_CANON_START_DESC" ideology = democratic ideas = {{ }} focuses = {{ }} }}',text)
    if '"MLT" = ' not in text:text=text.replace(' "---" =',' "MLT" = { minor = yes history = "MLT_CANON_START_DESC" ideology = neutrality ideas = { } focuses = { } }\n "---" =')
    text=text.replace('focuses = { A03_imperial_council JPC_state_guarantees JPC_batavia_demands }','focuses = { JSM_steel JSM_workshops JSM_shipyards }')
    write(p,text)
    keys=set(re.findall(r'history\s*=\s*"([^"]+)"',text))
    for lang,index in [('russian',0),('english',1)]:
        folder=R/'localisation'/lang
        # Normalize all existing country cards, including the minor countries.
        for p in folder.glob('*.yml'):
            text=p.read_text(encoding='utf-8-sig');original=text
            for key in keys:
                match=re.search(rf'^\s*{re.escape(key)}:\d*\s+"(.*)"\s*$',text,re.M)
                if not match:continue
                value=match[1];parts=value.split('\\n\\n')
                if len(parts)>1:value=parts[1]
                value=re.sub(r'§.','',value).replace('\\n',' ').strip()
                if key in ('A03_PACIFIC_START_DESC','A07_CANON_START_DESC'):value=DESCS['A03' if key.startswith('A03') else 'A07'][index]
                text=text[:match.start()]+f' {key}:0 "{value}"'+text[match.end():]
            if text!=original:write(p,text,True)
        lines=['l_'+lang+':']
        for tag in ('MLT','AVC','AQL','ASA','AWA','ATA'):lines.append(f' {tag}_CANON_START_DESC:0 "{DESCS[tag][index]}"')
        write(folder/f'1896_bookmarks_l_{lang}.yml','\n'.join(lines)+'\n',True)
    print('Updated country descriptions. Preserve compact minor-country placement for the new countries.')
if __name__=='__main__':main()
