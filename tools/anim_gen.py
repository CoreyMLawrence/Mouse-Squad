import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from png import read_png, write_png

def squash(px, amount=2):
    h = len(px)
    w = len(px[0])
    out = [[(0,0,0,0)] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            # map y to slightly squashed y
            if px[y][x][3] > 0:
                new_y = y + int((y / h) * amount)
                if new_y < h:
                    out[new_y][x] = px[y][x]
                    
    # Fill holes
    for y in range(1, h):
        for x in range(w):
            if out[y][x][3] == 0 and out[y-1][x][3] > 0 and px[y][x][3] > 0:
                out[y][x] = out[y-1][x]
                
    return out

def stretch(px, amount=2):
    h = len(px)
    w = len(px[0])
    out = [[(0,0,0,0)] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if px[y][x][3] > 0:
                new_y = y - int(((h - y) / h) * amount)
                if new_y >= 0:
                    out[new_y][x] = px[y][x]
                    
    for y in range(h-2, -1, -1):
        for x in range(w):
            if out[y][x][3] == 0 and out[y+1][x][3] > 0 and px[y][x][3] > 0:
                out[y][x] = out[y+1][x]
    return out

def gen_anims(name):
    w, h, px = read_png(f"art/sprites/{name}_select_2x.png")
    
    # Idle
    write_png(f"art/sprites/{name}_idle.png", px)
    
    # Walk1 (same as idle)
    write_png(f"art/sprites/{name}_walk1.png", px)
    
    # Walk2 (squashed)
    write_png(f"art/sprites/{name}_walk2.png", squash(px, 2))
    
    # Jump (stretched)
    write_png(f"art/sprites/{name}_jump.png", stretch(px, 2))
    
    print(f"Generated animations for {name}")

if __name__ == '__main__':
    for name in ['cyan', 'pink', 'yellow']:
        gen_anims(name)
