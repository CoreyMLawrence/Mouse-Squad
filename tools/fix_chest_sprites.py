#!/usr/bin/env python3
"""
tools/fix_chest_sprites.py

Fills empty/transparent pixels in the chest/torso area of the non-yellow mice
(Cyan and Pink) across idle, walk, jump, and select sprites.
Yellow sprites are left completely unchanged.
"""

import os, sys, json, base64, shutil
from png import read_png, write_png

def decode_asset(a):
    w, h, pal = a['w'], a['h'], a['pal']
    raw = base64.b64decode(a['r'])
    grid = [[None]*w for _ in range(h)]
    x = 0; y = 0
    for i in range(0, len(raw), 2):
        v = raw[i]; cnt = raw[i+1]
        for _ in range(cnt):
            grid[y][x] = v
            x += 1
            if x == w: x = 0; y += 1
    return w, h, pal, grid

def encode_rle(grid, w, h):
    flat = []
    for y in range(h):
        for x in range(w):
            flat.append(grid[y][x])
    rle = bytearray()
    curr = flat[0]
    count = 1
    for i in range(1, len(flat)):
        if flat[i] == curr and count < 255:
            count += 1
        else:
            rle.append(curr)
            rle.append(count)
            curr = flat[i]
            count = 1
    rle.append(curr)
    rle.append(count)
    return base64.b64encode(bytes(rle)).decode('ascii')

def grid_to_rgba(grid, pal, w, h):
    px = []
    for y in range(h):
        row = []
        for x in range(w):
            v = grid[y][x]
            if v == 255:
                row.append((0, 0, 0, 0))
            else:
                row.append(tuple(pal[v]) + (255,))
        px.append(row)
    return px

def repair_all():
    assets_path = 'art/sprites_v3/assets.json'
    with open(assets_path, 'r') as f:
        assets = json.load(f)

    # 1. CYAN REPAIRS
    # cyan palette:
    # 0: [105, 105, 105] (fur gray)
    # 1: [239, 183, 177] (pink ear/nose)
    # 2: [223, 223, 223] (cream belly)
    # 3: [26, 26, 26] (black outline/eye)
    # 4: [249, 249, 249] (white belly)
    # 5: [81, 81, 81] (dark gray fur)

    # cyan_idle
    w, h, pal, grid = decode_asset(assets['cyan_idle'])
    for x in range(51, 60): grid[70][x] = 2
    for x in range(50, 61): grid[71][x] = 2
    assets['cyan_idle']['r'] = encode_rle(grid, w, h)
    write_png('art/sprites_v3/cyan_idle.png', grid_to_rgba(grid, pal, w, h))
    print("Repaired cyan_idle")

    # cyan_w1
    w, h, pal, grid = decode_asset(assets['cyan_w1'])
    for x in range(63, 67): grid[70][x] = 2
    for x in range(62, 68): grid[71][x] = 2
    for x in range(61, 69): grid[72][x] = 2
    for x in range(61, 69): grid[73][x] = 2
    grid[72][51] = 0
    grid[73][50] = 0
    grid[73][51] = 0
    assets['cyan_w1']['r'] = encode_rle(grid, w, h)
    write_png('art/sprites_v3/cyan_w1.png', grid_to_rgba(grid, pal, w, h))
    print("Repaired cyan_w1")

    # cyan_w3
    w, h, pal, grid = decode_asset(assets['cyan_w3'])
    for x in range(63, 67): grid[70][x] = 2
    for x in range(61, 68): grid[71][x] = 2
    for x in range(60, 69): grid[72][x] = 2
    for x in range(59, 69): grid[73][x] = 2
    assets['cyan_w3']['r'] = encode_rle(grid, w, h)
    write_png('art/sprites_v3/cyan_w3.png', grid_to_rgba(grid, pal, w, h))
    print("Repaired cyan_w3")

    # cyan_w4
    w, h, pal, grid = decode_asset(assets['cyan_w4'])
    for x in range(62, 68): grid[70][x] = 2
    for x in range(62, 69): grid[71][x] = 2
    for x in range(60, 69): grid[72][x] = 2
    for x in range(60, 69): grid[73][x] = 2
    grid[72][50] = 0
    grid[72][51] = 0
    assets['cyan_w4']['r'] = encode_rle(grid, w, h)
    write_png('art/sprites_v3/cyan_w4.png', grid_to_rgba(grid, pal, w, h))
    print("Repaired cyan_w4")

    # 2. PINK REPAIRS
    # pink palette:
    # 0: [133, 133, 133] (fur gray)
    # 1: [249, 108, 141] (magenta)
    # 2: [255, 183, 177] (inner ear peach)
    # 3: [243, 243, 243] (cream belly)
    # 4: [111, 52, 149] (purple glasses)
    # 5: [237, 237, 237] (belly shade)
    # 6: [255, 255, 255] (belly highlight)
    # 7: [26, 26, 26] (black outline/eye)
    # 8: [103, 103, 103] (dark gray fur)

    # pink_idle
    w, h, pal, grid = decode_asset(assets['pink_idle'])
    # upper chest / belly
    for x in range(39, 53): grid[58][x] = 3
    for x in range(39, 53): grid[59][x] = 3
    for x in range(38, 53): grid[60][x] = 3
    for x in range(38, 53): grid[61][x] = 3
    # back fur gaps
    for x in (54, 55, 56): grid[60][x] = 0
    for x in (55, 56): grid[61][x] = 0
    for x in (49, 50, 51): grid[62][x] = 0
    for x in (49, 50, 51, 52): grid[63][x] = 0
    for x in (50, 51, 52, 53): grid[64][x] = 0
    for x in (51, 52): grid[65][x] = 0
    grid[66][51] = 0
    # lower chest / belly border
    grid[67][37] = 3
    for x in range(37, 39): grid[68][x] = 3
    for x in range(36, 39): grid[69][x] = 3
    for x in range(35, 39): grid[70][x] = 3
    for x in range(34, 38): grid[71][x] = 3
    for x in range(34, 37): grid[72][x] = 3
    for x in range(34, 37): grid[73][x] = 3
    assets['pink_idle']['r'] = encode_rle(grid, w, h)
    write_png('art/sprites_v3/pink_idle.png', grid_to_rgba(grid, pal, w, h))
    print("Repaired pink_idle")

    # pink_w1
    w, h, pal, grid = decode_asset(assets['pink_w1'])
    for x in range(49, 54): grid[58][x] = 3
    for x in range(49, 54): grid[59][x] = 3
    for x in range(48, 55): grid[60][x] = 3
    for x in range(48, 55): grid[61][x] = 3
    grid[62][54] = 3
    for x in (41, 42, 43): grid[60][x] = 0
    for x in (41, 42): grid[61][x] = 0
    assets['pink_w1']['r'] = encode_rle(grid, w, h)
    write_png('art/sprites_v3/pink_w1.png', grid_to_rgba(grid, pal, w, h))
    print("Repaired pink_w1")

    # pink_w2
    w, h, pal, grid = decode_asset(assets['pink_w2'])
    for y in range(57, 61):
        grid[y][49] = 0 # fur
        for x in range(50, 56):
            grid[y][x] = 3 # belly
    assets['pink_w2']['r'] = encode_rle(grid, w, h)
    write_png('art/sprites_v3/pink_w2.png', grid_to_rgba(grid, pal, w, h))
    print("Repaired pink_w2")

    # pink_w3
    w, h, pal, grid = decode_asset(assets['pink_w3'])
    for x in range(49, 55): grid[58][x] = 3
    for x in range(49, 55): grid[59][x] = 3
    for x in range(48, 55): grid[60][x] = 3
    for x in range(48, 55): grid[61][x] = 3
    grid[62][49] = 6
    for x in (54, 55): grid[62][x] = 5
    grid[60][42] = 0
    for x in (41, 42): grid[61][x] = 0
    assets['pink_w3']['r'] = encode_rle(grid, w, h)
    write_png('art/sprites_v3/pink_w3.png', grid_to_rgba(grid, pal, w, h))
    print("Repaired pink_w3")

    # pink_w4
    w, h, pal, grid = decode_asset(assets['pink_w4'])
    for x in range(50, 57): grid[58][x] = 3
    for x in range(50, 57): grid[59][x] = 3
    for x in range(49, 58): grid[60][x] = 3
    for x in range(49, 58): grid[61][x] = 3
    assets['pink_w4']['r'] = encode_rle(grid, w, h)
    write_png('art/sprites_v3/pink_w4.png', grid_to_rgba(grid, pal, w, h))
    print("Repaired pink_w4")

    # pink_jump
    w, h, pal, grid = decode_asset(assets['pink_jump'])
    for y in range(62, 66):
        for x in range(57, 68):
            grid[y][x] = 5
    grid[66][65] = 5
    grid[67][65] = 5
    assets['pink_jump']['r'] = encode_rle(grid, w, h)
    write_png('art/sprites_v3/pink_jump.png', grid_to_rgba(grid, pal, w, h))
    print("Repaired pink_jump")

    # sel_pink
    w, h, pal, grid = decode_asset(assets['sel_pink'])
    for y in (126, 127):
        for x in range(68, 74): grid[y][x] = 0
    for y in (128, 129):
        for x in range(70, 76): grid[y][x] = 0
    for y in (130, 131):
        for x in range(70, 78): grid[y][x] = 0
    for y in (132, 133):
        for x in range(72, 80): grid[y][x] = 0
    for y in (134, 135):
        for x in range(74, 78): grid[y][x] = 0
    for y in (136, 137):
        for x in range(74, 76): grid[y][x] = 0
    assets['sel_pink']['r'] = encode_rle(grid, w, h)
    write_png('art/sprites_v3/sel_pink.png', grid_to_rgba(grid, pal, w, h))
    print("Repaired sel_pink")

    # Save updated assets.json
    with open(assets_path, 'w') as f:
        json.dump(assets, f, separators=(',', ':'))
    print(f"Saved updated {assets_path}")

    # Update index.html
    with open('index.html', 'r') as f:
        html = f.read()

    new_assets_js = 'const ASSETS = ' + json.dumps(assets, separators=(',', ':')) + ';'
    
    # Replace line starting with const ASSETS =
    lines = html.splitlines()
    replaced = False
    for i, line in enumerate(lines):
        if line.startswith('const ASSETS = '):
            lines[i] = new_assets_js
            replaced = True
            break
            
    assert replaced, "Could not find const ASSETS = line in index.html"
    
    with open('index.html', 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print("Updated ASSETS in index.html")

if __name__ == '__main__':
    repair_all()
