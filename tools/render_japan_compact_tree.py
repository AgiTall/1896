"""Render all actual focus positions, then a readable upper-tree crop."""
from pathlib import Path
import re,textwrap
from PIL import Image,ImageDraw,ImageFont
from add_canon_countries import parse,value
R=Path(__file__).resolve().parents[1]
t=value(parse((R/'common/national_focus/a03_focus.txt').read_text()),'focus_tree')
fs={value(n,'id'):n for k,o,n in t if k=='focus'}
loc={}
for p in (R/'localisation/russian').glob('*.yml'):loc.update(re.findall(r'^\s*(\w+):\d+\s*"(.*)"',p.read_text(encoding='utf-8-sig'),re.M))
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14)
titlefont=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',25)
def pt(fid):return (115+(int(value(fs[fid],'x'))-10)*77,120+int(value(fs[fid],'y'))*110)
im=Image.new('RGB',(1924,2980),'#101b29');d=ImageDraw.Draw(im)
d.text((35,22),'ЯПОНИЯ — КОМПАКТНОЕ ДЕРЕВО С ВЫБОРАМИ',font=titlefont,fill='#f3e4c0')
for fid,n in fs.items():
 x,y=pt(fid)
 for k,o,v in n:
  if k=='prerequisite':
   for a,b,p in v:
    xx,yy=pt(p);d.line([(xx,yy+37),(xx,(yy+y)//2),(x,(yy+y)//2),(x,y-37)],fill='#60758c',width=2)
for fid,n in fs.items():
 x,y=pt(fid);c='#264838' if fid.startswith('JPI_') else '#20384b'
 d.rounded_rectangle((x-71,y-38,x+71,y+38),radius=8,fill=c,outline='#c4a76b',width=2)
 lines=textwrap.wrap(loc.get(fid,fid),18)
 for j,line in enumerate(lines):d.text((x,y+(j-(len(lines)-1)/2)*16),line,font=font,fill='#f3ead8',anchor='mm')
 for k,o,v in n:
  if k=='mutually_exclusive':
   for a,b,p in v:
    if p>fid:
     xx,yy=pt(p)
     if yy==y:d.text(((x+xx)/2,y),'×',font=titlefont,fill='#ff9179',anchor='mm')
im.save(R/'tools/japan_compact_tree_preview.png')
im.crop((0,0,1924,1640)).save(R/'tools/japan_compact_upper_preview.png')
print('Rendered full tree and upper branch from actual coordinates')
