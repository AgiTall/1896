"""Readable layout proof sheets, not screenshots of the running game."""
from pathlib import Path
import json,re,textwrap
from PIL import Image,ImageDraw,ImageFont
from validate_philippines_rework import parse,value

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tools/previews/focus_shapes';OUT.mkdir(parents=True,exist_ok=True)
loc={}
for path in (ROOT/'localisation/russian').rglob('*.yml'):loc.update(re.findall(r'^\s+([^ :]+):\d+ "(.*)"',path.read_text(encoding='utf-8-sig'),re.M))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13);titlefont=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',23)
manifest=json.loads((ROOT/'tools/focus_shapes_manifest.json').read_text(encoding='utf-8'))

def render(name,subset=None,suffix='',title=None):
    tree=value(parse((ROOT/'common/national_focus'/name).read_text(encoding='utf-8-sig')),'focus_tree')
    fs={value(v,'id'):v for k,o,v in tree if k=='focus' and (subset is None or value(v,'id') in subset)}
    xmin=min(int(value(f,'x')) for f in fs.values());xmax=max(int(value(f,'x')) for f in fs.values());ymin=min(int(value(f,'y')) for f in fs.values());ymax=max(int(value(f,'y')) for f in fs.values())
    im=Image.new('RGB',((xmax-xmin)*52+180,(ymax-ymin)*100+160),'#14212d');draw=ImageDraw.Draw(im)
    draw.text((20,16),title or name,font=titlefont,fill='#f3d79b')
    draw.text((20,47),'Схема расположения • игровой интерфейс проверяется отдельно',font=font,fill='#a1adb7')
    pos={key:((int(value(f,'x'))-xmin)*52+22,(int(value(f,'y'))-ymin)*100+88) for key,f in fs.items()}
    for key,f in fs.items():
        x,y=pos[key]
        for k,o,g in f:
            if k=='prerequisite':
                for a,b,parent in g:
                    if parent not in pos:continue
                    px,py=pos[parent];mid=py+78
                    draw.line((px+64,py+59,px+64,mid,x+64,mid,x+64,y),fill='#637f91',width=2)
            elif k=='mutually_exclusive':
                for a,b,target in g:
                    if target in pos and target>key and pos[target][1]==y:
                        tx,ty=pos[target];draw.line((x+130,y+29,tx,y+29),fill='#a66458',width=2)
    for key,f in fs.items():
        x,y=pos[key];colour='#28434b' if key.startswith('A10D_') else '#3a3546' if key.startswith('A10M_') else '#35412f' if key.startswith('A10W_') else '#293d50'
        draw.rounded_rectangle((x,y,x+128,y+60),radius=6,fill=colour,outline='#b5a078')
        lines=textwrap.wrap(loc.get(key,key),width=18,break_long_words=False)
        label_font=font
        if any(draw.textbbox((0,0),line,font=font)[2]>120 for line in lines):label_font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',11)
        for i,line in enumerate(lines[:3]):
            box=draw.textbbox((0,0),line,font=label_font);draw.text((x+(128-box[2]+box[0])/2,y+5+i*16),line,font=label_font,fill='#f4eedc')
    path=OUT/(Path(name).stem+suffix+'.png');im.save(path);return str(path)

for name in manifest:render(name)
phil={value(f,'id') for k,o,f in value(parse((ROOT/'common/national_focus/a10_focus.txt').read_text(encoding='utf-8-sig')),'focus_tree') if k=='focus'}
for prefix,title in [('A10W_','Филиппины — Палата и два протектората'),('A10M_','Филиппины — переворот и два военных режима')]:render('a10_focus.txt',{key for key in phil if key.startswith(prefix)},'_'+prefix.rstrip('_'),title)
render('MNR_A05.txt',title='Железный Союз — три выбора и национальный проект')
print(f'Rendered {len(manifest)+2} review sheets in {OUT}.')
