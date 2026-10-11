#!/usr/bin/env python3
"""
tools/fix_cyan_jump.py

Fills the transparent pixels in the chest/torso area of cyan_jump.
Updates:
- art/sprites_v3/cyan_jump.png
- art/sprites_v3/assets.json
- index.html
"""

import json, base64, os
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

def main():
    assets_path = 'art/sprites_v3/assets.json'
    with open(assets_path, 'r') as f:
        assets = json.load(f)

    w, h, pal, grid = decode_asset(assets['cyan_jump'])

    # Fill chest/torso transparent gap in cyan_jump
    # pal[0]: [105, 105, 105] (fur gray)
    # pal[2]: [223, 223, 223] (cream belly)
    grid[85][53] = 0
    grid[85][54] = 0
    for x in range(55, 77):
        grid[85][x] = 2

    grid[86][55] = 0
    for x in range(61, 77):
        grid[86][x] = 2

    for x in range(61, 77):
        grid[87][x] = 2

    for x in range(61, 76):
        grid[88][x] = 2

    for x in range(61, 76):
        grid[89][x] = 2

    # Update asset
    assets['cyan_jump']['r'] = encode_rle(grid, w, h)
    write_png('art/sprites_v3/cyan_jump.png', grid_to_rgba(grid, pal, w, h))
    print("Repaired cyan_jump")

    # Save assets.json
    with open(assets_path, 'w') as f:
        json.dump(assets, f, separators=(',', ':'))
    print("Saved updated assets.json")

    # Update index.html
    with open('index.html', 'r') as f:
        html = f.read()

    new_assets_js = 'const ASSETS = ' + json.dumps(assets, separators=(',', ':')) + ';'
    lines = html.splitlines()
    replaced = False
    for i, line in enumerate(lines):
        if line.startswith('const ASSETS = '):
            lines[i] = new_assets_js
            replaced = True
            break
    assert replaced, "Could not find const ASSETS = in index.html"

    with open('index.html', 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print("Updated const ASSETS in index.html")

if __name__ == '__main__':
    main()
