#!/usr/bin/env python3
"""
tools/fix_doremi_chin_and_sprites.py

Fixes Do Re Mi (Yellow)'s sprites by completely removing the extraneous chin and mouth
pixels brought over from 1 2 3 (Pink)'s body:
- Takes 1 2 3's body ONLY from the neck row down:
    idle: row 58 down
    w1:   row 58 down
    w2:   row 57 down
    w3:   row 58 down
    w4:   row 58 down
    jump: row 62 down
- Above the neck row, preserves only the curling tail pixels on the far edge,
  strictly omitting any face/chin/mouth pixels from 1 2 3.
- Mounts Do Re Mi's head seamlessly so her chin meets the neck directly:
    idle: hy = 8  (chin at 57, neck at 58)
    w1:   hy = 8  (chin at 57, neck at 58)
    w2:   hy = 7  (chin at 56, neck at 57)
    w3:   hy = 8  (chin at 57, neck at 58)
    w4:   hy = 8  (chin at 57, neck at 58)
    jump: hy = 12 (chin at 61, neck at 62)
- Updates art/sprites_v3/ PNGs, art/sprites_v3/assets.json, and index.html.
"""

import json, base64, re, os
import numpy as np
from PIL import Image

def decode_asset(a):
    w, h, pal = a['w'], a['h'], a['pal']
    raw = base64.b64decode(a['r'])
    grid = [[255]*w for _ in range(h)]
    x, y = 0, 0
    for i in range(0, len(raw), 2):
        v, cnt = raw[i], raw[i+1]
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
    img = Image.new('RGBA', (w, h))
    pix = img.load()
    for y in range(h):
        for x in range(w):
            v = grid[y][x]
            if v == 255:
                pix[x, y] = (0, 0, 0, 0)
            else:
                pix[x, y] = tuple(pal[v]) + (255,)
    return img

def main():
    assets_path = 'art/sprites_v3/assets.json'
    with open(assets_path, 'r') as f:
        assets = json.load(f)

    # 1. Load original Do Re Mi head from index.html.bak-level1
    with open('index.html.bak-level1', 'r') as f:
        bak_html = f.read()
    bak_m = re.search(r'const ASSETS = ({.*?});', bak_html)
    bak_assets = json.loads(bak_m.group(1))

    _, _, pal_y, orig_y_grid = decode_asset(bak_assets['yellow_idle'])
    orig_y_arr = np.array(orig_y_grid)

    # Head is rows 4..53 in original yellow_idle
    head_raw = orig_y_arr[4:54, :] # 50 rows
    h_mask = (head_raw != 255)
    c_min, c_max = np.where(h_mask.any(axis=0))[0][[0, -1]]
    head_cropped = head_raw[:, c_min:c_max+1]
    Hh, Wh = head_cropped.shape
    print(f"Extracted Do Re Mi head: {Wh}x{Hh} (cols {c_min}..{c_max})")

    # Recolor function from Pink body to Yellow palette
    def recolor_pixel_to_yellow(rgb):
        r, g, b = rgb[:3]
        if (r, g, b) == (133, 133, 133): return 1 # main darker gray fur
        if (r, g, b) == (103, 103, 103): return 0 # shadow fur
        if (r, g, b) in [(243, 243, 243), (237, 237, 237), (255, 255, 255)]: return 6 # light gray belly/tummy
        if (r, g, b) == (26, 26, 26): return 4   # black outline
        # Fallback
        lum = (int(r) + int(g) + int(b)) / 3
        if lum > 180: return 6
        elif lum > 90: return 1
        else: return 0

    neck_rows = {
        'idle': 58,
        'w1':   58,
        'w2':   57,
        'w3':   58,
        'w4':   58,
        'jump': 62
    }

    head_positions = {
        'idle': (5, 8),
        'w1':   (4, 8),
        'w2':   (6, 7),
        'w3':   (4, 8),
        'w4':   (7, 8),
        'jump': (15, 12)
    }

    W_NEW, H_NEW = 86, 88
    for fr in ['idle', 'w1', 'w2', 'w3', 'w4', 'jump']:
        key = f'yellow_{fr}'
        pink_key = f'pink_{fr}'
        pink_img = Image.open(f'art/sprites_v3/{pink_key}.png')
        p_arr = np.array(pink_img)

        new_grid = [[255]*W_NEW for _ in range(H_NEW)]
        neck_r = neck_rows[fr]
        hx, hy = head_positions[fr]

        # 1. Transfer Pink's body ONLY from neck_r down
        for r in range(neck_r, H_NEW):
            for c in range(W_NEW):
                if p_arr[r, c, 3] > 0:
                    new_grid[r][c] = recolor_pixel_to_yellow(p_arr[r, c])

        # 2. Transfer Pink's tail pixels above neck_r (ONLY gray fur, NEVER white/chin)
        if fr == 'idle':
            for r in range(48, neck_r):
                for c in range(65, W_NEW):
                    if p_arr[r, c, 3] > 0 and p_arr[r, c, 0] < 200:
                        new_grid[r][c] = recolor_pixel_to_yellow(p_arr[r, c])
        elif fr in ['w1', 'w3']:
            for r in range(50, neck_r):
                for c in range(20, 29):
                    if p_arr[r, c, 3] > 0 and p_arr[r, c, 0] < 200:
                        new_grid[r][c] = recolor_pixel_to_yellow(p_arr[r, c])
        elif fr == 'w2':
            for r in range(48, neck_r):
                for c in range(0, 15):
                    if p_arr[r, c, 3] > 0 and p_arr[r, c, 0] < 200:
                        new_grid[r][c] = recolor_pixel_to_yellow(p_arr[r, c])
        elif fr == 'w4':
            for r in range(50, neck_r):
                for c in range(20, 30):
                    if p_arr[r, c, 3] > 0 and p_arr[r, c, 0] < 200:
                        new_grid[r][c] = recolor_pixel_to_yellow(p_arr[r, c])
        elif fr == 'jump':
            for r in range(54, neck_r):
                for c in range(18, 29):
                    if p_arr[r, c, 3] > 0 and p_arr[r, c, 0] < 200:
                        new_grid[r][c] = recolor_pixel_to_yellow(p_arr[r, c])

        # 3. Mount Do Re Mi's head cleanly on top
        for r in range(Hh):
            for c in range(Wh):
                v = head_cropped[r, c]
                if v != 255:
                    new_grid[hy + r][hx + c] = v

        # Verify no disconnected rows
        arr_check = np.array(new_grid)
        non_empty = [r for r in range(H_NEW) if np.any(arr_check[r] != 255)]
        assert (non_empty[-1] - non_empty[0] + 1) == len(non_empty), f"{key} has a disconnected row gap!"

        # Verify that row neck_r - 1 (chin) meets row neck_r (neck) directly
        chin_cols = np.where(arr_check[neck_r - 1] != 255)[0]
        neck_cols = np.where(arr_check[neck_r] != 255)[0]
        overlap = set(chin_cols).intersection(set(neck_cols))
        assert len(overlap) > 10, f"{key} chin does not overlap neck sufficiently ({len(overlap)} px)"

        # 4. Save to assets dictionary
        assets[key]['w'] = W_NEW
        assets[key]['h'] = H_NEW
        assets[key]['pal'] = pal_y
        assets[key]['r'] = encode_rle(new_grid, W_NEW, H_NEW)

        # 5. Save PNG
        out_png = grid_to_rgba(new_grid, pal_y, W_NEW, H_NEW)
        out_png.save(f'art/sprites_v3/{key}.png')
        print(f"Updated {key}: canvas=({W_NEW}, {H_NEW}), bbox={out_png.getbbox()}, chin_y={hy+Hh-1}, neck_y={neck_r}")

    # Save assets.json
    with open(assets_path, 'w') as f:
        json.dump(assets, f, separators=(',', ':'))
    print("Saved updated art/sprites_v3/assets.json")

    # Update index.html const ASSETS
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
    print("Successfully updated const ASSETS in index.html!")

if __name__ == '__main__':
    main()
