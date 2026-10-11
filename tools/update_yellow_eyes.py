#!/usr/bin/env python3
"""
tools/update_yellow_eyes.py

Makes Yellow's eyes the exact same size as one another, and perfectly oval shaped.
Applies across:
- yellow_idle, yellow_w1, yellow_w2, yellow_w3, yellow_w4, yellow_jump
- sel_yellow
Updates assets.json and index.html.
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

    # 1. Gameplay frames (1x)
    # Both eyes: Height 8 rows, Width 6 columns
    # Width progression: 2 -> 4 -> 6 -> 6 -> 6 -> 6 -> 4 -> 2
    # Left eye:  x in 34..39 (center 36.5)
    # Right eye: x in 50..55 (center 52.5)
    shape_1x = [2, 4, 6, 6, 6, 6, 4, 2]

    frames_1x = {
        'yellow_idle': (0, 0),
        'yellow_w1':   (1, 10),
        'yellow_w2':   (6, 9),
        'yellow_w3':   (0, 7),
        'yellow_w4':   (1, 6),
        'yellow_jump': (18, 13),
    }

    for key, (dy, dx) in frames_1x.items():
        w, h, pal, g = decode_asset(assets[key])
        # Clear ONLY eye regions (preserving snout at row 42, col 45..47 and mouth at row 44..46)
        for y in range(32 + dy, 42 + dy):
            for x in range(32 + dx, 43 + dx):
                if 0 <= y < h and 0 <= x < w and g[y][x] == 4:
                    g[y][x] = 6
            for x in range(48 + dx, 58 + dx):
                if 0 <= y < h and 0 <= x < w and g[y][x] == 4:
                    g[y][x] = 6

        # Draw identical 8x6 ovals for both eyes
        for i, width in enumerate(shape_1x):
            y = 33 + dy + i
            pad = (6 - width) // 2
            for x in range(34 + dx + pad, 34 + dx + pad + width):
                g[y][x] = 4
            for x in range(50 + dx + pad, 50 + dx + pad + width):
                g[y][x] = 4

        # Validate exact match
        left_pts = [(y, x) for y in range(32 + dy, 42 + dy) for x in range(32 + dx, 43 + dx) if g[y][x] == 4]
        right_pts = [(y, x) for y in range(32 + dy, 42 + dy) for x in range(48 + dx, 58 + dx) if g[y][x] == 4]
        assert len(left_pts) == len(right_pts) == 36, f"Mismatch in {key}: {len(left_pts)} vs {len(right_pts)}"

        assets[key]['r'] = encode_rle(g, w, h)
        write_png(f'art/sprites_v3/{key}.png', grid_to_rgba(g, pal, w, h))
        print(f"Updated {key}: Left={len(left_pts)}px, Right={len(right_pts)}px (perfect matching 8x6 ovals)")

    # 2. Selection frame (2x)
    # Both eyes: Height 16 rows, Width 12 columns
    # Left eye:  x in 79..90
    # Right eye: x in 111..122
    # Rows: 60..75
    shape_2x = [4, 4, 8, 8, 12, 12, 12, 12, 12, 12, 12, 12, 8, 8, 4, 4]

    w, h, pal, g = decode_asset(assets['sel_yellow'])
    # Clear both eye regions
    for y in range(56, 80):
        for x in range(74, 96):
            if g[y][x] == 4: g[y][x] = 6
        for x in range(104, 126):
            if g[y][x] == 4: g[y][x] = 6

    for dy, width in enumerate(shape_2x):
        y = 60 + dy
        pad = (12 - width) // 2
        for x in range(79 + pad, 79 + pad + width):
            g[y][x] = 4
        for x in range(111 + pad, 111 + pad + width):
            g[y][x] = 4

    left_pts = [(y, x) for y in range(56, 80) for x in range(74, 96) if g[y][x] == 4]
    right_pts = [(y, x) for y in range(56, 80) for x in range(104, 126) if g[y][x] == 4]
    assert len(left_pts) == len(right_pts) == 144, f"Mismatch in sel_yellow: {len(left_pts)} vs {len(right_pts)}"

    assets['sel_yellow']['r'] = encode_rle(g, w, h)
    write_png('art/sprites_v3/sel_yellow.png', grid_to_rgba(g, pal, w, h))
    print(f"Updated sel_yellow: Left={len(left_pts)}px, Right={len(right_pts)}px (perfect matching 16x12 ovals)")

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
