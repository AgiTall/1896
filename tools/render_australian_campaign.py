"""Local layout previews for the six generated focus trees."""
from pathlib import Path
import json,re,textwrap
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
data=json.loads((R/'tools/australian_campaign_manifest.json').read_text(encoding='utf-8'))
loc=dict(re.findall(r'^\s+(\w+):0 "(.*)"',(R/'localisation/russian/AUC_campaign_l_russian.yml').read_text(encoding='utf-8-sig'),re.M))
loc.update(dict(re.findall(r'^\s+(\w+):0 "(.*)"',(R/'localisation/russian/FSP_focus_shapes_l_russian.yml').read_text(encoding='utf-8-sig'),re.M)))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
titlefont=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',23)
names={'A07':'Сидней — федерация и внешняя политика','AVC':'Виктория','AQL':'Квинсленд','ASA':'Южная Австралия','AWA':'Западная Австралия','ATA':'Тасмания'}
out=R/'tools/previews/australian_campaign';out.mkdir(parents=True,exist_ok=True)
for tag,rows in data.items():
    w=max(r['x'] for r in rows)*40+180;h=max(r['y'] for r in rows)*64+150
    im=Image.new('RGB',(w,h),'#182330');d=ImageDraw.Draw(im)
    d.text((24,18),names[tag],font=titlefont,fill='#f4e3bb')
    positions={r['id']:(r['x']*40+30,r['y']*64+75) for r in rows}
    for r in rows:
        x,y=positions[r['id']]
        for parent in r['parents']:
            px,py=positions[parent];d.line((px+65,py+44,x+65,y),fill='#64788b',width=2)
    for r in rows:
        x,y=positions[r['id']];d.rounded_rectangle((x,y,x+130,y+48),radius=5,fill='#293d4d',outline='#ae9970',width=1)
        label=loc[r['id']];lines=textwrap.wrap(label,width=19)
        for i,line in enumerate(lines[:3]):
            box=d.textbbox((0,0),line,font=small);d.text((x+(130-(box[2]-box[0]))/2,y+3+i*14),line,font=small,fill='#f5f0e5')
    im.save(out/f'{tag}.png')
print('Rendered six focus tree previews.')
