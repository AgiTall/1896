"""Exercise editor writes in a temporary mod."""
import sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import country_editor as ed
from PIL import Image
from unittest.mock import patch
with tempfile.TemporaryDirectory() as temp:
    ed.ROOT=Path(temp)
    fixtures={'common/country_tags/test.txt':'A03 = "countries/Japan.txt"',
      'common/characters/test.txt':'characters = { A03_emperor = { name = emperor portraits = { civilian = { large = GFX_old small = GFX_small } } country_leader = { ideology = despotism } } }',
      'history/countries/A03 - Japan.txt':'recruit_character = A03_emperor\nset_politics = { ruling_party = neutrality }',
      'interface/test.gfx':'spriteTypes = { spriteType = { name = "GFX_old" texturefile = "gfx/leaders/old.dds" } }',
      'localisation/russian/test_l_russian.yml':'l_russian:\n A03:0 "Япония"\n'}
    for name,text in fixtures.items():
        p=ed.ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8-sig')
    root=ed.tk.Tk();root.withdraw();app=ed.Editor(root);app.list.selection_set(0);app.leaders();app.stamp='smoke'
    assert all(p is None for p in app.preview_paths.values())
    old=ed.ROOT/'gfx/leaders/old.dds';old.parent.mkdir(parents=True,exist_ok=True)
    Image.new('RGBA',(156,210),'blue').save(old)
    app.refresh_previews();assert app.preview_paths['portrait']==old
    variant=ed.ROOT/'gfx/flags/A03_neutrality.tga';variant.parent.mkdir(parents=True,exist_ok=True)
    Image.new('RGBA',(82,52),'green').save(variant)
    app.refresh_previews();assert app.preview_paths['flag']==variant
    app.png=lambda:Image.new('RGBA',(2400,1600),(255,0,0,255))
    app.flag();app.portrait();app.name.set('Тестовый генерал');app.extra.set('trickster');app.general()
    for folder,size in [('',(82,52)),('medium',(41,26)),('small',(10,7))]:
        with Image.open(ed.ROOT/'gfx/flags'/folder/'A03.tga') as im:assert im.size==size
    chars=list((ed.ROOT/'common/characters').glob('A03_editor*'));assert len(chars)==1
    assert 'trickster' in chars[0].read_text(encoding='utf-8')
    assert 'A03_editor_' in (ed.ROOT/'history/countries/A03 - Japan.txt').read_text(encoding='utf-8-sig')
    assert 'GFX_old' not in (ed.ROOT/'common/characters/test.txt').read_text(encoding='utf-8')
    assert list((ed.ROOT/'tools/backups').rglob('*.txt'))
    assert all(p is not None for p in app.preview_paths.values())
    assert all(key in app.preview_images for key in ('flag','medium','small','portrait'))
    # Exercise each paste action without touching the user's real clipboard.
    with patch.object(ed.ImageGrab,'grabclipboard',return_value=Image.new('RGB',(1800,1200),'yellow')):
        app.flag(clipboard=True);app.portrait(clipboard=True)
        app.name.set('Генерал из буфера');app.general(clipboard=True)
    assert len(list((ed.ROOT/'common/characters').glob('A03_editor*')))==2
    with Image.open(variant) as im:assert im.convert('RGB').getpixel((0,0))==(255,255,0)
    with patch.object(ed.ImageGrab,'grabclipboard',return_value=[str(old)]):
        assert app.clipboard_image().size==(156,210)
    with patch.object(ed.ImageGrab,'grabclipboard',return_value=None):
        try:app.clipboard_image()
        except ValueError as e:assert 'нет изображения' in str(e)
        else:raise AssertionError('Empty clipboard should report an error')
    app.search.set('не существует');assert all(p is None for p in app.preview_paths.values())
    root.destroy()
print('PASS: previews, large images, 3 flag sizes, generals, backups, clipboard images/files and empty clipboard')
