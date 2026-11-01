"""Render the real Chamber graph as a review diagram, not an in-game screenshot."""
from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont
from validate_philippines_rework import parse, value

ROOT = Path(__file__).resolve().parents[1]


def main():
    tree = value(parse((ROOT / 'common/national_focus/WTN_focus.txt').read_text(encoding='utf-8')), 'focus_tree')
    focuses = {value(node, 'id'): node for key, _, node in tree if key == 'focus'}
    loc = dict(re.findall(r'^\s+([^ :]+):\d+\s+"(.*)"$', (ROOT / 'localisation/russian/WTN_network_l_russian.yml').read_text(encoding='utf-8-sig'), re.M))
    image = Image.new('RGB', (1772, 1175), '#101c28')
    draw = ImageDraw.Draw(image)
    regular = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 19)
    small = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 17)
    bold = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 23)
    title = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 34)
    draw.text((42, 25), 'Всемирная торговая палата', font=title, fill='#efe5d2')
    draw.text((44, 73), 'Резерв, страхование, связь и переговоры островного мира · 30 фокусов', font=regular, fill='#a6b7c8')
    colours = {0: '#c5b37d', 6: '#c79b67', 12: '#73b6c6', 18: '#b597c6', 24: '#88b68e'}
    positions = {fid: (190 + 58 * int(value(node, 'x')), 140 + 56 * int(value(node, 'y'))) for fid, node in focuses.items()}
    for fid, node in focuses.items():
        x, y = positions[fid]
        for key, _, parents in node:
            if key == 'prerequisite':
                for _, _, parent in parents:
                    px, py = positions[parent]
                    draw.line([(px, py + 35), (x, y - 35)], fill='#697c8b', width=3)
    heads = ['WTN_guard_charter', 'WTN_tech_charter', 'WTN_secret_charter']
    for left, right in zip(heads, heads[1:]):
        lx, ly = positions[left]
        rx, _ = positions[right]
        for x in range(lx + 130, rx - 130, 12):
            draw.line([(x, ly), (min(x + 7, rx - 130), ly)], fill='#db8c82', width=3)
    labels = {0: 'Резервы и арбитраж', 6: 'Старая гвардия', 12: 'Технократы', 18: 'Тайный департамент', 24: 'Торговая сеть'}
    for x, label in labels.items():
        cx = 190 + x * 58
        draw.rounded_rectangle((cx - 155, 304, cx + 155, 329), 6, fill='#101c28')
        draw.text((cx, 316), label, font=bold, fill=colours[x], anchor='mm')

    for fid, node in focuses.items():
        x, y = positions[fid]
        colour = colours.get(int(value(node, 'x')), '#c5b37d')
        draw.rounded_rectangle((x - 130, y - 35, x + 130, y + 35), radius=11, fill='#203241', outline=colour, width=2)
        lines, line = [], ''
        for word in loc[fid].split():
            candidate = (line + ' ' + word).strip()
            if draw.textlength(candidate, font=regular) > 236 and line:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
        assert len(lines) <= 3, (fid, lines)
        for i, text in enumerate(lines):
            draw.text((x, y + (i - (len(lines)-1)/2) * 22), text, anchor='mm', font=regular, fill='#f0f0ec')
    draw.line((44, 1104, 1728, 1104), fill='#43576a')
    draw.text((44, 1120), 'Серые линии — зависимости. Красный пунктир — выбор одного из трёх уставов.', font=small, fill='#a6b7c8')
    draw.text((44, 1146), 'Схема по действующим файлам мода; внешний вид интерфейса игры проверяется отдельно.', font=small, fill='#a6b7c8')
    target = ROOT / 'tools/previews/chamber_focus_tree.png'
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)
    print(target)


if __name__ == '__main__':
    main()
