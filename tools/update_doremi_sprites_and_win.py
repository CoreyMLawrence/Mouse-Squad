#!/usr/bin/env python3
"""
tools/update_doremi_sprites_and_win.py

1. Swaps Do Re Mi (Yellow)'s body with 1 2 3 (Pink)'s body across all gameplay frames:
   - yellow_idle, yellow_w1, yellow_w2, yellow_w3, yellow_w4, yellow_jump
   - Sizes her down from (84, 109) to (86, 88) - the exact same size as 1 2 3
   - Recolors Pink's body to match Do Re Mi's darker gray fur palette
   - Mounts Do Re Mi's head (with ears, eyes, purple headband, and blue music note) on top seamlessly
2. Restores the light blue music note hair clip in Do Re Mi's hair on the victory screen (win_group):
   - Restores the 169 pixels of the music note shape at x=459..479, y=72..95 to light blue [22, 204, 201] (pal index 8)
3. Updates art/sprites_v3/ PNG files, art/sprites_v3/assets.json, and index.html
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

    # =========================================================================
    # PART 1: Restoring Do Re Mi's Music Note in Victory Screen (win_group)
    # =========================================================================
    # From index.html.bak-level1, we have the exact 169 music note pixels in Do Re Mi's hair
    with open('index.html.bak-level1', 'r') as f:
        bak_html = f.read()
    bak_m = re.search(r'const ASSETS = ({.*?});', bak_html)
    bak_assets = json.loads(bak_m.group(1))
    _, _, _, bak_win_grid = decode_asset(bak_assets['win_group'])

    w_win, h_win, pal_win, cur_win_grid = decode_asset(assets['win_group'])

    # Find the 169 note pixels (palette index 8 in bak_win_grid at x=459..479, y=72..95)
    restored_note_pixels = 0
    for y in range(72, 96):
        for x in range(459, 480):
            if bak_win_grid[y][x] == 8:
                cur_win_grid[y][x] = 8
                restored_note_pixels += 1

    print(f"Restored {restored_note_pixels} music note pixels in win_group with color {pal_win[8]}")
    assert restored_note_pixels == 169, f"Expected 169 note pixels restored, got {restored_note_pixels}"

    assets['win_group']['r'] = encode_rle(cur_win_grid, w_win, h_win)
    win_png = grid_to_rgba(cur_win_grid, pal_win, w_win, h_win)
    win_png.save('art/sprites_v3/win_group.png')
    print("Saved updated art/sprites_v3/win_group.png")

    # =========================================================================
    # PART 2: Swapping Do Re Mi's Body with 1 2 3 (Pink)'s Body
    # =========================================================================
    # Yellow palette in assets.json:
    # 0: [68, 68, 68]   (darker shadow fur)
    # 1: [85, 85, 85]   (main darker gray fur)
    # 2: [255, 191, 196] (inner ears pink)
    # 3: [12, 205, 205]  (music note light blue/cyan)
    # 4: [27, 27, 27]   (black outline/eyes)
    # 5: [216, 69, 184] (purple headband)
    # 6: [218, 218, 218] (off-white belly/chest)
    # 7: [66, 66, 66]   (dark shadow fur)

    # Extract Do Re Mi's finished head from yellow_idle
    w_yi, h_yi, pal_y, g_y_idle = decode_asset(assets['yellow_idle'])
    y_idle_img = Image.open('art/sprites_v3/yellow_idle.png')
    y_idle_arr = np.array(y_idle_img)

    # Head is rows 0..52 in yellow_idle (chin at row 52)
    y_head_raw = y_idle_arr[:53, :, :]
    h_bbox = Image.fromarray(y_head_raw).getbbox()
    head = y_head_raw[h_bbox[1]:h_bbox[3], h_bbox[0]:h_bbox[2], :]
    Hh, Wh = head.shape[:2]
    print(f"Do Re Mi head shape: {Wh}x{Hh} (bbox {h_bbox})")

    # Color mapping from Pink body to Yellow body
    # Pink fur:
    # (133, 133, 133) -> (85, 85, 85)   [pal 1]
    # (103, 103, 103) -> (68, 68, 68)   [pal 0]
    # (243, 243, 243) -> (218, 218, 218) [pal 6]
    # (237, 237, 237) -> (218, 218, 218) [pal 6]
    # (255, 255, 255) -> (218, 218, 218) [pal 6]
    # (26, 26, 26)    -> (27, 27, 27)   [pal 4]
    def recolor_pixel_to_pal_idx(rgb):
        r, g, b = rgb
        if (r, g, b) == (133, 133, 133): return 1
        if (r, g, b) == (103, 103, 103): return 0
        if (r, g, b) in [(243, 243, 243), (237, 237, 237), (255, 255, 255)]: return 6
        if (r, g, b) == (26, 26, 26): return 4
        # Default fallback to main fur or shadow
        if (r + g + b) / 3 > 180: return 6
        elif (r + g + b) / 3 > 90: return 1
        else: return 0

    head_positions = {
        'idle': (3, 3),
        'w1':   (2, 3),
        'w2':   (4, 2),
        'w3':   (2, 3),
        'w4':   (5, 3),
        'jump': (14, 7),
    }

    body_cutoffs = {
        'idle': 51,
        'w1':   51,
        'w2':   50,
        'w3':   51,
        'w4':   51,
        'jump': 54,
    }

    # Map head RGBA colors to yellow pal indices
    def head_rgba_to_idx(rgba):
        r, g, b, a = rgba
        if a == 0: return 255
        rgb = (r, g, b)
        for idx, col in enumerate(pal_y):
            if tuple(col) == rgb:
                return idx
        # Nearest match
        dists = [sum(abs(c1 - c2) for c1, c2 in zip(col, rgb)) for col in pal_y]
        return int(np.argmin(dists))

    head_grid = [[head_rgba_to_idx(head[r, c]) for c in range(Wh)] for r in range(Hh)]

    # Update all 6 frames
    W_NEW, H_NEW = 86, 88
    for fr in ['idle', 'w1', 'w2', 'w3', 'w4', 'jump']:
        key = f'yellow_{fr}'
        pink_key = f'pink_{fr}'
        pink_img = Image.open(f'art/sprites_v3/{pink_key}.png')
        p_arr = np.array(pink_img)

        new_grid = [[255]*W_NEW for _ in range(H_NEW)]
        cutoff = body_cutoffs[fr]
        hx, hy = head_positions[fr]

        # 1. Transfer & recolor Pink's body below cutoff
        for r in range(cutoff, H_NEW):
            for c in range(W_NEW):
                if p_arr[r, c, 3] > 0:
                    new_grid[r][c] = recolor_pixel_to_pal_idx(tuple(p_arr[r, c, :3]))

        # 2. Transfer tail pixels above cutoff
        if fr == 'idle':
            for r in range(48, cutoff):
                for c in range(69, W_NEW):
                    if p_arr[r, c, 3] > 0:
                        new_grid[r][c] = recolor_pixel_to_pal_idx(tuple(p_arr[r, c, :3]))
        elif fr == 'w2':
            for r in range(48, cutoff):
                for c in range(0, 12):
                    if p_arr[r, c, 3] > 0:
                        new_grid[r][c] = recolor_pixel_to_pal_idx(tuple(p_arr[r, c, :3]))

        # 3. Mount Do Re Mi's head on top
        for r in range(Hh):
            for c in range(Wh):
                v = head_grid[r][c]
                if v != 255:
                    new_grid[hy + r][hx + c] = v

        # 4. Save to assets dictionary
        assets[key]['w'] = W_NEW
        assets[key]['h'] = H_NEW
        assets[key]['pal'] = pal_y
        assets[key]['r'] = encode_rle(new_grid, W_NEW, H_NEW)

        # 5. Save PNG
        out_png = grid_to_rgba(new_grid, pal_y, W_NEW, H_NEW)
        out_png.save(f'art/sprites_v3/{key}.png')
        print(f"Updated {key}: canvas=({W_NEW}, {H_NEW}), bbox={out_png.getbbox()}")

    # Update _meta for yellow tail to match pink
    if '_meta' in assets and 'yellow' in assets['_meta']:
        assets['_meta']['yellow'] = {"tailX": 25, "tailY": 73}

    # Save assets.json
    with open(assets_path, 'w') as f:
        json.dump(assets, f, separators=(',', ':'))
    print("Saved updated art/sprites_v3/assets.json")

    # =========================================================================
    # PART 3: Update index.html const ASSETS
    # =========================================================================
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
