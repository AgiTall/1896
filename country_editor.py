"""Local HOI4 country editor. Requires Python 3 and Pillow: pip install Pillow."""
from pathlib import Path
import re, shutil, uuid, datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageOps, ImageTk, ImageGrab

ROOT=Path(__file__).resolve().parent
class Editor:
    def __init__(self, window):
        self.window=window; window.title('1896 — редактор стран'); window.geometry('820x850')
        self.preview_images={}; self.preview_paths={}; self.preview_boxes={}
        self.sprites={}
        for p in sorted((ROOT/'interface').rglob('*.gfx')):
            for block in re.findall(r'spriteType\s*=\s*\{([^{}]*)\}',p.read_text(encoding='utf-8-sig'),re.S):
                name=re.search(r'\bname\s*=\s*"([^"]+)"',block)
                path=re.search(r'\btexturefile\s*=\s*"([^"]+)"',block,re.I)
                if name and path:self.sprites[name[1]]=path[1]
        self.countries={}; self.names={}
        for p in sorted((ROOT/'common/country_tags').glob('*.txt')):
            for tag,path in re.findall(r'^\s*([A-Z0-9]{3})\s*=\s*"([^"]+)"',p.read_text(encoding='utf-8-sig'),re.M): self.countries[tag]=path
        for p in sorted((ROOT/'localisation/russian').rglob('*.yml')):
            for key,value in re.findall(r'^\s*([^\s:]+):\d*\s+"(.*)"',p.read_text(encoding='utf-8-sig'),re.M): self.names[key]=value
        ttk.Label(window,text='Найти страну: тег или название').pack(anchor='w',padx=15,pady=6)
        self.search=tk.StringVar(); self.search.trace_add('write',lambda *_:self.filter())
        ttk.Entry(window,textvariable=self.search).pack(fill='x',padx=15)
        self.list=tk.Listbox(window,height=6,exportselection=False); self.list.pack(fill='x',padx=15,pady=6); self.filter()
        previews=ttk.Frame(window); previews.pack(fill='x',padx=15,pady=6)
        for key,title in [('flag','Флаг · 82×52'),('medium','Флаг · 41×26'),('small','Флаг · 10×7'),('portrait','Правитель')]:
            card=ttk.Frame(previews); card.pack(side='left',expand=True)
            ttk.Label(card,text=title).pack()
            canvas=tk.Canvas(card,width=120,height=120,bg='#e4e4e4',highlightthickness=1,highlightbackground='#aaaaaa')
            canvas.pack(pady=4); self.preview_boxes[key]=canvas
        self.image_actions(window,'Загрузить PNG флага → TGA (3 размера)',self.flag)
        self.leader=ttk.Combobox(window,state='readonly'); self.leader.pack(fill='x',padx=15)
        self.leader.bind('<<ComboboxSelected>>',lambda _:self.refresh_previews())
        self.list.bind('<<ListboxSelect>>',lambda _:self.leaders())
        self.image_actions(window,'Загрузить PNG портрета правителя → DDS',self.portrait)
        ttk.Label(window,text='Новый генерал: имя').pack(anchor='w',padx=15)
        self.name=tk.StringVar(); ttk.Entry(window,textvariable=self.name).pack(fill='x',padx=15)
        ttk.Label(window,text='Черты (Ctrl — несколько; также можно вписать ID через пробел)').pack(anchor='w',padx=15)
        self.traits=tk.Listbox(window,selectmode='extended',height=5,exportselection=False); self.traits.pack(fill='x',padx=15)
        traits=set()
        for folder in ('common/unit_leader','common/unit_leader_traits'):
            for p in (ROOT/folder).glob('*.txt'):
                traits.update(re.findall(r'^\s*([\w]+)\s*=\s*\{',p.read_text(encoding='utf-8-sig'),re.M))
        traits-=set('leader_traits gain_xp ai_will_do modifier equipment_bonus shared_modifier corps_commander field_marshal navy_leader'.split())
        if not traits: traits.update('logistics_wizard defensive_doctrine offensive_doctrine trickster engineer infantry_leader cavalry_leader panzer_leader commando'.split())
        for t in sorted(traits): self.traits.insert('end',t)
        self.extra=tk.StringVar(); ttk.Entry(window,textvariable=self.extra).pack(fill='x',padx=15,pady=3)
        self.image_actions(window,'Выбрать PNG и добавить генерала (навык 1)',self.general)
        ttk.Label(window,text='Изменения видны в новой игре. Копии: tools/backups/country_editor.\nФлаг заменяется для базового тега и существующих идеологий.').pack(padx=15,pady=8)
    def image_actions(self,parent,label,action):
        row=ttk.Frame(parent); row.pack(fill='x',padx=15,pady=4)
        ttk.Button(row,text=label,command=lambda:self.run(action)).pack(side='left',fill='x',expand=True)
        ttk.Button(row,text='Вставить из буфера',command=lambda:self.run(lambda:action(clipboard=True))).pack(side='left',padx=(6,0))
    def filter(self):
        self.list.delete(0,'end')
        for tag in sorted(self.countries):
            name=self.names.get(tag,self.names.get(tag+'_neutrality',Path(self.countries[tag]).stem))
            label=f'{tag} — {name}'
            if self.search.get().casefold() in label.casefold(): self.list.insert('end',label)
        if hasattr(self,'leader'):self.leader.set(''); self.leader['values']=()
        for key in self.preview_boxes:self.show_preview(key,None)
    def tag(self):
        if not self.list.curselection(): raise ValueError('Выберите страну из списка.')
        return self.list.get(self.list.curselection()[0]).split(' — ')[0]
    def history(self,tag):
        files=list((ROOT/'history/countries').glob(tag+' - *.txt'))
        if len(files)!=1: raise ValueError(f'Для {tag} найдено файлов истории: {len(files)}. Нужен ровно один.')
        return files[0]
    def blocks(self,tag):
        # Balanced scanner: nested character blocks and braces inside strings are handled.
        result=[]
        for p in (ROOT/'common/characters').glob('*.txt'):
            text=p.read_text(encoding='utf-8-sig')
            for m in re.finditer(r'\b('+re.escape(tag)+r'_\w+)\s*=\s*\{',text):
                start=m.end(); depth=1; quote=False; comment=False; i=start
                while i<len(text) and depth:
                    c=text[i]
                    if c=='\n': comment=False
                    if not quote and c=='#': comment=True
                    if not comment:
                        if c=='"' and (i==0 or text[i-1]!='\\'): quote=not quote
                        if not quote:
                            depth+=(c=='{')-(c=='}')
                    i+=1
                if 'country_leader' in text[start:i]: result.append((m[1],p,start,i-1,text))
        return result
    def leaders(self):
        if not self.list.curselection():return
        self.leader['values']=[b[0] for b in self.blocks(self.tag())]
        if self.leader['values']: self.leader.current(0)
        else: self.leader.set('')
        self.refresh_previews()
    def show_preview(self,key,path):
        canvas=self.preview_boxes[key]; canvas.delete('all')
        self.preview_images.pop(key,None); self.preview_paths[key]=None
        if path is None or not path.is_file():return
        try:
            with Image.open(path) as source:
                img=source.convert('RGBA')
                img.thumbnail((112,112),Image.Resampling.NEAREST if key=='small' else Image.Resampling.LANCZOS)
            photo=ImageTk.PhotoImage(img,master=self.window)
            self.preview_images[key]=photo; self.preview_paths[key]=path
            canvas.create_image(60,60,image=photo)
        except (OSError,ValueError):pass
    def refresh_previews(self):
        if not self.list.curselection():return
        tag=self.tag(); ideology=None
        try:
            m=re.search(r'\bruling_party\s*=\s*(\w+)',self.history(tag).read_text(encoding='utf-8-sig'))
            if m:ideology=m[1]
        except ValueError:pass
        for key,folder in [('flag',''),('medium','medium'),('small','small')]:
            base=ROOT/'gfx/flags'/folder
            candidates=([base/f'{tag}_{ideology}.tga'] if ideology else [])+[base/f'{tag}.tga']
            self.show_preview(key,next((p for p in candidates if p.is_file()),None))
        path=None
        for ident,p,start,end,text in self.blocks(tag):
            if ident!=self.leader.get():continue
            match=re.search(r'civilian\s*=\s*\{[^}]*?\blarge\s*=\s*("[^"]+"|[\w]+)',text[start:end])
            if match:
                token=match[1].strip('"'); texture=self.sprites.get(token,token)
                path=ROOT/texture.replace('\\','/')
        self.show_preview('portrait',path)
    def backup(self,p):
        if p.exists():
            b=ROOT/'tools/backups/country_editor'/self.stamp/p.relative_to(ROOT); b.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,b)
    def save(self,p,text,bom=False):
        self.backup(p); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding='utf-8-sig' if bom else 'utf-8')
    def png(self):
        p=filedialog.askopenfilename(filetypes=[('PNG','*.png')])
        if not p: return None
        with Image.open(p) as img: return ImageOps.exif_transpose(img).convert('RGBA')
    def clipboard_image(self):
        try: content=ImageGrab.grabclipboard()
        except OSError as e:raise ValueError('Не удалось прочитать буфер обмена. Скопируйте изображение ещё раз.') from e
        if isinstance(content,Image.Image):return ImageOps.exif_transpose(content).convert('RGBA')
        if isinstance(content,list):
            for name in content:
                try:
                    with Image.open(name) as img:return ImageOps.exif_transpose(img).convert('RGBA')
                except (OSError,ValueError):continue
        raise ValueError('В буфере нет изображения. Скопируйте картинку, сделайте снимок экрана или скопируйте файл изображения в Проводнике.')
    def texture(self,img,p,size,fit=False):
        self.backup(p); p.parent.mkdir(parents=True,exist_ok=True)
        output=img.resize(size,Image.Resampling.LANCZOS) if fit else ImageOps.fit(img,size,method=Image.Resampling.LANCZOS)
        output.save(p)
    def flag(self,clipboard=False):
        tag=self.tag(); img=self.clipboard_image() if clipboard else self.png()
        if img is None:return
        for folder,size in [('',(82,52)),('medium',(41,26)),('small',(10,7))]:
            base=ROOT/'gfx/flags'/folder
            paths={base/(tag+'.tga'),*base.glob(tag+'_*.tga')}
            for p in paths:self.texture(img,p,size,fit=True)
        self.refresh_previews()
    def portrait(self,clipboard=False):
        tag=self.tag(); matches=[b for b in self.blocks(tag) if b[0]==self.leader.get()]
        if not matches:raise ValueError('Выберите правителя; для страны без персонажа-правителя эта операция недоступна.')
        key,p,start,end,text=matches[0]; body=text[start:end]
        m=re.search(r'civilian\s*=\s*\{\s*large\s*=\s*("[^"]+"|[\w]+)',body)
        img=self.clipboard_image() if clipboard else self.png()
        if img is None:return
        path=f'gfx/leaders/{tag}/{key}_editor.dds'; self.texture(img,ROOT/path,(156,210))
        if m:body=body[:m.start(1)]+'"'+path+'"'+body[m.end(1):]
        else:
            civilian=re.search(r'civilian\s*=\s*\{',body)
            portraits=re.search(r'portraits\s*=\s*\{',body)
            if civilian:body=body[:civilian.end()]+f' large = "{path}" '+body[civilian.end():]
            elif portraits:body=body[:portraits.end()]+f' civilian = {{ large = "{path}" }} '+body[portraits.end():]
            else:body=f' portraits = {{ civilian = {{ large = "{path}" }} }} '+body
        small=re.search(r'civilian\s*=\s*\{[^}]*\bsmall\s*=\s*("[^"]+"|[\w]+)',body)
        if small:
            sp=f'gfx/leaders/{tag}/{key}_editor_small.dds'; self.texture(img,ROOT/sp,(65,67))
            body=body[:small.start(1)]+'"'+sp+'"'+body[small.end(1):]
        self.save(p,text[:start]+body+text[end:])
        self.refresh_previews()
    def general(self,clipboard=False):
        tag=self.tag(); hist=self.history(tag); name=self.name.get().strip()
        if not name or any(c in name for c in '\n\r"\\'):raise ValueError('Введите имя без кавычек, обратной косой черты и переноса строки.')
        traits=[self.traits.get(i) for i in self.traits.curselection()]+self.extra.get().split()
        if any(not re.fullmatch(r'[A-Za-z0-9_]+',t) for t in traits):raise ValueError('Черты должны быть ID из букв, цифр и подчёркиваний.')
        img=self.clipboard_image() if clipboard else self.png()
        if img is None:return
        key=f'{tag}_editor_{uuid.uuid4().hex[:12]}'; path=f'gfx/leaders/{tag}/{key}.dds'
        self.texture(img,ROOT/path,(156,210))
        self.save(ROOT/f'common/characters/{key}.txt',f'characters = {{ {key} = {{ name = {key}_name portraits = {{ army = {{ large = "{path}" }} }} corps_commander = {{ skill = 1 attack_skill = 1 defense_skill = 1 planning_skill = 1 logistics_skill = 1 traits = {{ {" ".join(traits)} }} }} }} }}\n')
        self.save(hist,hist.read_text(encoding='utf-8-sig')+f'\nrecruit_character = {key}\n')
        for lang in ('russian','english'):
            self.save(ROOT/f'localisation/{lang}/{key}_l_{lang}.yml',f'l_{lang}:\n {key}_name:0 "{name}"\n',True)
    def run(self,fn):
        self.stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        try:
            fn(); messagebox.showinfo('1896','Операция завершена. Если выбран файл, изменения сохранены.')
        except Exception as e:messagebox.showerror('1896',str(e))
if __name__=='__main__':
    app=tk.Tk(); Editor(app); app.mainloop()
