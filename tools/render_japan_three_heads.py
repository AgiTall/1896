"""Render a readable schematic of the political branch from its actual coordinates."""
from pathlib import Path
import re,textwrap
from PIL import Image,ImageDraw,ImageFont
from add_canon_countries import parse,value
R=Path(__file__).resolve().parents[1]
t=value(parse((R/'common/national_focus/a03_focus.txt').read_text()),'focus_tree')
fs={value(n,'id'):n for k,o,n in t if k=='focus' and int(value(n,'y'))<=5}
loc={}
for p in (R/'localisation/russian').glob('*.yml'):
 loc.update(re.findall(r'^\s*(\w+):\d+\s*"(.*)"',p.read_text(encoding='utf-8-sig'),re.M))
im=Image.new('RGB',(1460,1040),'#101b29');d=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
bold=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',27)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
def pt(fid):return (130+(int(value(fs[fid],'x'))-14)*74,160+int(value(fs[fid],'y'))*130)
d.text((38,22),'ЯПОНИЯ — ТРИ ГОЛОВЫ ДРАКОНА',font=bold,fill='#f0e2bf')
for x,label in [(175,'МИЦУБИСИ / ДЕНЬГИ'),(760,'САЙГО / СЕВЕР'),(1280,'ИТО / ЮГ')]:
 d.text((x,265),label,font=small,fill='#ceb77d',anchor='mm')
for fid,n in fs.items():
 x,y=pt(fid)
 for k,o,v in n:
  if k=='prerequisite':
   for a,b,p in v:
    if p in fs:
     xx,yy=pt(p);d.line([(xx,yy+40),(xx,(yy+y)//2),(x,(yy+y)//2),(x,y-40)],fill='#71879b',width=3)
for fid,n in fs.items():
 x,y=pt(fid);w=238 if fid in ['JPR_defence_budget','A03_imperial_council'] else 216
 d.rounded_rectangle((x-w//2,y-43,x+w//2,y+43),radius=10,fill='#20384b',outline='#c3a660',width=2)
 title=loc[fid]
 lines=textwrap.wrap(title,20)
 for j,line in enumerate(lines):d.text((x,y+(j-(len(lines)-1)/2)*24),line,font=font,fill='#f4ead7',anchor='mm')
 # Red line marks the two exclusive choices on each side.
for a,b in [('JPC_state_guarantees','JPT_treasury_debts'),('JPC_northern_protocol','JPT_north_rebellion')]:
 x,y=pt(a);xx,yy=pt(b);d.text(((x+xx)//2,y),'×',font=bold,fill='#ff8f79',anchor='mm')
d.text((710,900),'↓  Промышленность «Алые паруса»  →  Южный рывок  →  Борнео',font=bold,fill='#f0e2bf',anchor='mm')
d.text((710,969),'Займы: 180 дней   •   Экспедиция Сайго: начало 1894 года',font=font,fill='#a8bdcc',anchor='mm')
d.text((710,1004),'Схема связей из игровых файлов; это не скриншот из игры.',font=small,fill='#a8bdcc',anchor='mm')
im.save(R/'tools/japan_three_heads_preview.png')
print('Saved tools/japan_three_heads_preview.png')
