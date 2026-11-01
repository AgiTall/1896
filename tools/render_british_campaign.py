"""Reviewable local layout diagrams; these are not engine screenshots."""
from pathlib import Path
import json,re,textwrap
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'tools/british_campaign_manifest.json').read_text(encoding='utf-8'))['focuses']
loc=dict(re.findall(r'^\s+(\w+):0 "(.*)"',(ROOT/'localisation/russian/BLV_campaign_l_russian.yml').read_text(encoding='utf-8-sig'),re.M))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13);titlefont=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',25)
out=ROOT/'tools/previews/british_campaign';out.mkdir(parents=True,exist_ok=True)
def render(name,title,minimum,maximum):
    rows=[r for r in data if minimum<=r['x']<=maximum]
    width=(maximum-minimum)*40+190;height=max(r['y'] for r in rows)*46+170
    im=Image.new('RGB',(width,height),'#152533');draw=ImageDraw.Draw(im)
    draw.text((24,18),title,font=titlefont,fill='#ebd6a7')
    pos={r['id']:((r['x']-minimum)*40+25,r['y']*46+80) for r in rows}
    for row in rows:
        x,y=pos[row['id']]
        for parent in row['parents']:
            if parent in pos:
                px,py=pos[parent]
                if px==x:draw.line((px+70,py+54,x+70,y),fill='#638295',width=2)
                else:draw.line((px+70,py+54,px+70,py+73,x+70,py+73,x+70,y),fill='#638295',width=2)
    for row in rows:
        x,y=pos[row['id']]
        colour='#38443f' if row['x']>=66 else '#2c3b50' if row['x']<34 else '#263e49'
        draw.rounded_rectangle((x,y,x+140,y+54),radius=5,fill=colour,outline='#a58e60')
        lines=textwrap.wrap(loc[row['id']],width=21,break_long_words=False)
        assert len(lines)<=3,(row['id'],lines)
        for i,line in enumerate(lines):
            box=draw.textbbox((0,0),line,font=font);draw.text((x+(140-(box[2]-box[0]))/2,y+4+i*16),line,font=font,fill='#f1ebdf')
    im.save(out/(name+'.png'))
render('overview','Британский Левиафан — дерево кампании',2,88)
render('government','Казна, Адмиралтейство и корона',2,33)
render('maritime','Имперские станции, флот и Тихий океан',34,64)
render('science','Тесла, Гренландия и возвращение',66,88)
print('Rendered the overview and three branch diagrams.')
