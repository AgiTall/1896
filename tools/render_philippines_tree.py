"""A reviewable overview of the actual generated focus positions and links."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parents[1]
fs=json.loads((R/'tools/philippines_focus_manifest.json').read_text(encoding='utf-8'))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',32)
head=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',21)
S=68;Y=92;LEFT=120;TOP=205
def xy(f):return (int(f['x']*S+LEFT),int(f['y']*Y+TOP))
width=3250;height=TOP+25*Y+90
im=Image.new('RGB',(width,height),(16,23,34));d=ImageDraw.Draw(im)
d.text((45,30),'ФИЛИППИНСКИЕ ОСТРОВА · 113 ФОКУСОВ',font=title,fill='#f5e5b2')
d.text((46,80),'1893 · Компактное древовидное расположение · Центр: развитие и армия под Конгрессом',font=head,fill='#aabbd1')
groups=[(1,9,'ПРИСЯГА ВТП','#3c858a'),(10,19,'РЕСПУБЛИКИ И ФЕДЕРАЦИЯ','#9b803d'),(20,24,'ХОЗЯЙСТВО','#377367'),(26,31,'АРМИЯ И ФЛОТ','#405777'),(33,43,'ВОЕННЫЙ ПЕРЕВОРОТ','#935454')]
for lo,hi,label,color in groups:
 x1=lo*S+LEFT-30;x2=hi*S+LEFT+30
 d.rounded_rectangle((x1,140,x2,height-65),radius=18,fill='#1b2637',outline=color,width=2)
 d.text((x1+18,155),label,font=head,fill=color)
byid={f['id']:f for f in fs}
for f in fs:
 x,y=xy(f)
 for group in f.get('prerequisites',[]):
  for p in group:
   px,py=xy(byid[p]);c='#536177' if len(group)==1 else '#7899bd'
   mid=y-48
   d.line([(px,py+34),(px,mid),(x,mid),(x,y-34)],fill=c,width=2)
for f in fs:
 x,y=xy(f);color=next((c for lo,hi,label,c in groups if lo<=f['x']<=hi),'#f5e5b2')
 # The cross-branch congress stays above the republican band.
 d.rounded_rectangle((x-76,y-32,x+76,y+32),radius=9,fill='#26364b',outline=color,width=2)
 words=f['name_ru'].split();lines=[];line=''
 for word in words:
  if d.textlength((line+' '+word).strip(),font=font)>140 and line:lines.append(line);line=word
  else:line=(line+' '+word).strip()
 if line:lines.append(line)
 use=font
 if len(lines)>3:
  use=small;lines=[];line=''
  for word in words:
   if d.textlength((line+' '+word).strip(),font=use)>140 and line:lines.append(line);line=word
   else:line=(line+' '+word).strip()
  if line:lines.append(line)
 step=18 if use==font else 15
 for i,line in enumerate(lines):d.text((x,y-(len(lines)*step)/2+i*step),line,font=use,fill='#eef2f8',anchor='mt')
 d.text((x+70,y+28),str(int(f.get('cost',4)*7))+' д.',font=small,fill='#b5c1d0',anchor='rt')
for f in fs:
 for ex in f.get('mutually_exclusive',[]):
  if ex>f['id'] and byid[ex]['y']==f['y']:
   x,y=xy(f);px,py=xy(byid[ex]);d.line([(min(x,px)+77,y),(max(x,px)-77,y)],fill='#b76666',width=2)
d.text((45,height-43),'Красные связи: взаимоисключение. Светлые связи с несколькими родителями в одной группе: достаточно одного из них. Условия событий и договоров описаны в документации.',font=font,fill='#aabbd1')
out=R/'docs/philippines_focus_tree.png';im.save(out)
print(str(out))
