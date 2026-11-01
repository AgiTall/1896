import re
from pathlib import Path
from inspect_coords import conf_map, root_postwar_map, mil_map

R = Path(__file__).resolve().parent
rework_path = R / 'build_philippines_rework.py'
text = rework_path.read_text(encoding='utf-8')

mapping = {**conf_map, **root_postwar_map, 'A10_strike_japan': mil_map['A10_strike_japan']}

for fid, (nx, ny) in mapping.items():
    # Find focus('fid',
    pos = text.find(f"focus('{fid}'")
    if pos == -1:
        print(f"ERROR: {fid} not found")
        continue
    # From pos, find the commas outside quotes:
    # arg 0: id
    # arg 1: ru
    # arg 2: en
    # arg 3: x
    # arg 4: y
    i = pos
    arg_indices = []
    in_quote = False
    quote_char = ''
    while len(arg_indices) < 5 and i < len(text):
        c = text[i]
        if in_quote:
            if c == '\\':
                i += 2
                continue
            elif c == quote_char:
                in_quote = False
        else:
            if c in ("'", '"'):
                in_quote = True
                quote_char = c
            elif c == ',' or c == '(':
                arg_indices.append(i)
        i += 1
    # arg_indices[0] is '('
    # arg_indices[1] is comma after id
    # arg_indices[2] is comma after ru
    # arg_indices[3] is comma after en -> then x starts!
    # arg_indices[4] is comma after x -> then y starts!
    # find comma after y:
    c_after_y = text.find(',', arg_indices[4] + 1)
    
    prefix = text[:arg_indices[3] + 1]
    suffix = text[c_after_y:]
    text = f"{prefix}{nx},{ny}{suffix}"
    print(f"Replaced {fid} with ({nx}, {ny})")

rework_path.write_text(text, encoding='utf-8')
print("Successfully updated build_philippines_rework.py!")
