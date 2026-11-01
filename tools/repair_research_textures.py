"""Resolve missing TGWR sprite textures through existing matching artwork."""
from pathlib import Path
import difflib
import json
import re
import shutil
from integrate_great_war_research import ROOT, blocks, read, backup

SOURCE = Path('D:/SteamLibrary/steamapps/workshop/content/394360/3365515312')
GAME = Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')
mp = ROOT / 'tools/great_war_research_manifest.json'
m = json.loads(read(mp))
files = set(m['files'])
valid = {}
for base in (GAME, SOURCE, ROOT):
    for p in (base / 'interface').rglob('*.gfx'):
        text = read(p)
        try:
            entries = blocks(text, 1)
        except ValueError:
            continue
        for key,s,o,e in entries:
            body = text[s:e]
            name = re.search(r'\bname\s*=\s*"?([^"\s{}]+)', body)
            texture = re.search(r'\btexturefile\s*=\s*"([^"]+)"', body, re.I)
            if name and texture and (base / texture[1]).is_file():
                valid[name[1]] = (base, texture[1])
assets = {}
for base in (GAME, SOURCE):
    for p in (base / 'gfx/interface').rglob('*'):
        if p.is_file() and p.suffix.lower() in ('.png','.dds','.tga'):
            assets.setdefault(p.stem.lower(), []).append((base,p.relative_to(base).as_posix()))
repairs = []
for rel in sorted(files):
    p = ROOT / rel
    if p.suffix != '.gfx':
        continue
    text = read(p)
    original = text
    for key,s,o,e in reversed(blocks(text, 1)):
        body = text[s:e]
        texture = re.search(r'\btexturefile\s*=\s*"([^"]+)"', body, re.I)
        name = re.search(r'\bname\s*=\s*"?([^"\s{}]+)', body)
        if not texture or not name:
            continue
        path = texture[1]
        if (ROOT / path).exists() or (GAME / path).exists():
            continue
        candidates = []
        if name[1] in valid:
            candidates.append(valid[name[1]])
        stem = Path(path).stem.lower()
        normalized = re.sub(r'^[a-z]{3}_', '', stem)
        normalized = normalized.replace('ww1_', '').replace('foreign_', '')
        normalized = normalized.replace('self_propelled_', '')
        for option in (stem, normalized, normalized.replace('medium_tank', 'medium_tank_chassis'), normalized.replace('heavy_tank', 'heavy_tank_chassis')):
            candidates.extend(assets.get(option, []))
        generic = re.sub(r'^GFX_[A-Z]{3}_', 'GFX_', name[1])
        for option in (generic, generic.replace('ww1_', '')):
            if option in valid:
                candidates.append(valid[option])
        if not candidates:
            # Match within the same icon family, rather than substituting a
            # generic unrelated technology picture.
            family = 'techtree' if '/techtree/' in path else ('counters' if '/counters/' in path else 'technologies')
            pool = {k:v for k,v in assets.items() if any('/' + family + '/' in pp for bb,pp in v)}
            matches = difflib.get_close_matches(normalized, pool, n=1, cutoff=0.35)
            assert matches, path
            candidates.extend(pool[matches[0]])
        base,newpath = candidates[0]
        assert (base / newpath).is_file(), newpath
        if base == SOURCE:
            target = ROOT / newpath
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(base / newpath, target)
            files.add(newpath)
        body = body.replace(path, newpath)
        text = text[:s] + body + text[e:]
        repairs.append(dict(sprite=name[1], missing=path, replacement=newpath))
    if text != original:
        backup(p)
        p.write_text(text,encoding='utf-8')
m['files'] = sorted(files)
m['texture_repairs'] = m.get('texture_repairs', []) + repairs
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Repaired {len(repairs)} missing source textures with existing artwork.')
