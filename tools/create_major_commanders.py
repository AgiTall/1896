"""Create editable commander placeholders once; never overwrite custom work."""
import re
import shutil
from integrate_great_war_research import ROOT, read

TAGS = ('A01', 'A02', 'A03', 'A04', 'A06', 'A07')
GAME = ROOT.__class__('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')


def main():
    targets = [ROOT / f'common/characters/{tag}_commander_placeholders.txt' for tag in TAGS]
    if any(p.exists() for p in targets):
        raise SystemExit('Placeholder files already exist. Edit them directly; regeneration would overwrite your work.')
    locale = {lang: [f'l_{lang}:'] for lang in ('russian', 'english')}
    for tag, target in zip(TAGS, targets):
        lines = ['# Editable placeholders: names are in major_commanders_l_*.yml.', 'characters = {']
        recruits = ['# BEGIN EDITABLE COMMANDER PLACEHOLDERS']
        for i in range(6):
            marshal = i == 0
            role = 'field_marshal' if marshal else 'corps_commander'
            suffix = 'marshal_01' if marshal else f'general_{i:02}'
            identifier = f'{tag}_placeholder_{suffix}'
            portrait = f'gfx/leaders/{tag}/placeholders/{suffix}.dds'
            asset = ROOT / portrait
            asset.parent.mkdir(parents=True, exist_ok=True)
            if not asset.exists():
                shutil.copyfile(GAME / 'gfx/leaders' / ('leader_marshal_unknown.dds' if marshal else 'leader_unknown.dds'), asset)
            lines += [f' {identifier} = {{', f'  name = {identifier}_name',
                      f'  portraits = {{ army = {{ large = "{portrait}" }} }}',
                      f'  {role} = {{', '   skill = 1', '   attack_skill = 1', '   defense_skill = 1',
                      '   planning_skill = 1', '   logistics_skill = 1', '   traits = { }', '  }', ' }']
            recruits.append(f'recruit_character = {identifier}')
            ru = f'{tag} — Фельдмаршал 01' if marshal else f'{tag} — Генерал {i:02}'
            en = f'{tag} — Field Marshal 01' if marshal else f'{tag} — General {i:02}'
            locale['russian'].append(f' {identifier}_name:0 "{ru}"')
            locale['english'].append(f' {identifier}_name:0 "{en}"')
        target.write_text('\n'.join(lines + ['}']) + '\n', encoding='utf-8')
        recruits.append('# END EDITABLE COMMANDER PLACEHOLDERS')
        history = next((ROOT / 'history/countries').glob(f'{tag} - *.txt'))
        text = read(history).rstrip()
        history.write_text(text + '\n\n' + '\n'.join(recruits) + '\n', encoding='utf-8-sig')
    for lang, lines in locale.items():
        p = ROOT / f'localisation/{lang}/major_commanders_l_{lang}.yml'
        p.write_text('\n'.join(lines) + '\n', encoding='utf-8-sig')
    print('Created 36 editable characters: five generals and one field marshal per major.')


if __name__ == '__main__':
    main()
