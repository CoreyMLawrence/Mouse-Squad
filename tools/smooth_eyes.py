#!/usr/bin/env python3
"""
tools/smooth_eyes.py

Smooths the mouse character eyes (Pink, Yellow, Cyan) into clean, rounded ovals.
Updates:
- idle, w1, w2, w3, w4, jump, and sel_* for Pink, Yellow, and Cyan
- assets.json and index.html
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

def apply_mods_to_grid(grid, mods, dy=0, dx=0):
    h = len(grid)
    w = len(grid[0])
    for my, mx, new_val in mods:
        ny = my + dy
        nx = mx + dx
        if 0 <= ny < h and 0 <= nx < w:
            grid[ny][nx] = new_val

def main():
    assets_path = 'art/sprites_v3/assets.json'
    with open(assets_path, 'r') as f:
        assets = json.load(f)

    # =========================================================================
    # 1. PINK EYES
    # =========================================================================
    # Left eye: y=[37..45], x=[38..44]
    # Right eye: y=[37..45], x=[53..58]
    # pal[7] is eye (black)
    # pal[3] is fur, pal[4] is purple ear/fur shadow
    pink_mods = [
        # Left eye: soften 4 corners and bottom corners
        (39, 38, 3), (39, 44, 3),
        (43, 38, 3), (43, 44, 3),
        (45, 39, 3), (45, 43, 3),
        # Right eye: soften 4 corners
        (39, 53, 4), (39, 58, 3),
        (43, 53, 4), (43, 58, 3),
    ]

    pink_frames = {
        'pink_idle': (0, 0),
        'pink_w1':   (0, -1),
        'pink_w2':   (0, 1),
        'pink_w3':   (0, -1),
        'pink_w4':   (0, 2),
        'pink_jump': (3, 11),
    }

    for key, (dy, dx) in pink_frames.items():
        w, h, pal, grid = decode_asset(assets[key])
        apply_mods_to_grid(grid, pink_mods, dy, dx)
        assets[key]['r'] = encode_rle(grid, w, h)
        write_png(f'art/sprites_v3/{key}.png', grid_to_rgba(grid, pal, w, h))
        print(f"Updated {key}")

    # sel_pink
    w, h, pal, grid = decode_asset(assets['sel_pink'])
    # left eye corners
    for y in (76, 77, 84, 85):
        for x in (32, 33, 42, 43): grid[y][x] = 3
    for y in (88, 89):
        for x in (34, 35, 40, 41): grid[y][x] = 3
    # right eye corners
    for y in (76, 77, 84, 85):
        for x in (60, 61, 72, 73): grid[y][x] = 3
    for y in (88, 89):
        for x in (60, 61, 62, 63, 70, 71, 72, 73): grid[y][x] = 3
    assets['sel_pink']['r'] = encode_rle(grid, w, h)
    write_png('art/sprites_v3/sel_pink.png', grid_to_rgba(grid, pal, w, h))
    print("Updated sel_pink")

    # =========================================================================
    # 2. YELLOW EYES
    # =========================================================================
    # Left eye: y=[33..39], x=[34..40]
    # Right eye: y=[33..41], x=[49..55]
    # pal[4] is eye (black), pal[6] is fur
    yellow_mods = [
        # Left eye: round top, left wall, and bottom
        (33, 34, 6), (33, 38, 6),
        (34, 34, 6), (34, 40, 6),
        (35, 40, 6),
        (38, 34, 6), (38, 39, 4),
        (39, 34, 6), (39, 38, 6),
        # Right eye: smooth top, remove spike at (37, 49), smooth bottom
        (33, 53, 4), (33, 54, 4),
        (37, 49, 6),
        (38, 49, 6), (38, 55, 4),
        (39, 49, 6), (39, 55, 6),
    ]

    yellow_frames = {
        'yellow_idle': (0, 0),
        'yellow_w1':   (1, 10),
        'yellow_w2':   (6, 9),
        'yellow_w3':   (0, 7),
        'yellow_w4':   (1, 6),
        'yellow_jump': (18, 13),
    }

    for key, (dy, dx) in yellow_frames.items():
        w, h, pal, grid = decode_asset(assets[key])
        apply_mods_to_grid(grid, yellow_mods, dy, dx)
        assets[key]['r'] = encode_rle(grid, w, h)
        write_png(f'art/sprites_v3/{key}.png', grid_to_rgba(grid, pal, w, h))
        print(f"Updated {key}")

    # sel_yellow
    w, h, pal, grid = decode_asset(assets['sel_yellow'])
    for y in (58, 59):
        for x in (80, 81, 88, 89): grid[y][x] = 6
    for y in (60, 61):
        for x in (78, 79): grid[y][x] = 6
    for y in (62, 63):
        for x in (90, 91): grid[y][x] = 6
    for y in (68, 69):
        for x in (78, 79): grid[y][x] = 6
    for y in (70, 71):
        for x in (78, 79, 86, 87): grid[y][x] = 6
    for y in range(68, 72):
        for x in (108, 109): grid[y][x] = 6
    assets['sel_yellow']['r'] = encode_rle(grid, w, h)
    write_png('art/sprites_v3/sel_yellow.png', grid_to_rgba(grid, pal, w, h))
    print("Updated sel_yellow")

    # =========================================================================
    # 3. CYAN EYES
    # =========================================================================
    # Left eye: y=[42..52], x=[50..58]
    # Right eye: y=[39..48], x=[68..74]
    # pal[3] is eye (black), pal[2] is cream fur
    cyan_mods = [
        # Left eye: soften corners
        (43, 51, 2),
        (45, 50, 2),
        (48, 58, 2),
        (49, 50, 2),
        # Right eye: soften corners
        (39, 69, 2),
        (40, 68, 2),
        (45, 74, 2),
        (46, 74, 2),
        (47, 69, 2),
    ]

    cyan_frames = {
        'cyan_idle': (0, 0),
        'cyan_w1':   (3, 5),
        'cyan_w2':   (3, 6),
        'cyan_w3':   (3, 2),
        'cyan_w4':   (3, 1),
        'cyan_jump': (15, 9),
    }

    for key, (dy, dx) in cyan_frames.items():
        w, h, pal, grid = decode_asset(assets[key])
        apply_mods_to_grid(grid, cyan_mods, dy, dx)
        assets[key]['r'] = encode_rle(grid, w, h)
        write_png(f'art/sprites_v3/{key}.png', grid_to_rgba(grid, pal, w, h))
        print(f"Updated {key}")

    # sel_cyan
    w, h, pal, grid = decode_asset(assets['sel_cyan'])
    for y in (84, 85, 92, 93):
        for x in (28, 29): grid[y][x] = 2
    for y in (86, 87):
        for x in (64, 65): grid[y][x] = 2
    for y in (94, 95, 96, 97):
        for x in (76, 77): grid[y][x] = 2
    assets['sel_cyan']['r'] = encode_rle(grid, w, h)
    write_png('art/sprites_v3/sel_cyan.png', grid_to_rgba(grid, pal, w, h))
    print("Updated sel_cyan")

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
