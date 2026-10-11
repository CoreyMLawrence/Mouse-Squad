import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from png import read_png, write_png

def extract_sprite(px, box):
    x0, y0, x1, y1 = box
    out = []
    for y in range(y0, y1):
        row = []
        for x in range(x0, x1):
            if y < len(px) and x < len(px[0]):
                row.append(px[y][x])
            else:
                row.append((0,0,0,0))
        out.append(row)
    return out

def process_sprites(recipe_file):
    with open(recipe_file, 'r') as f:
        config = json.load(f)
        
    cache = {}
    def get_frame(f):
        if f not in cache:
            # Load quantized version
            w, h, px = read_png(f"art/native/{f}_quantized.png")
            cache[f] = px
        return cache[f]
        
    for name, sp in config.items():
        base_px = get_frame(sp['base_frame'])
        
        # Scale box from screen space to native space
        box_screen = sp['box']
        # Native conversion: x_nat = int((x_scr - 2.0) / (8/3))
        # Wait! The gridlock step already did: cols = int((w - PX)/P).
        # And playfield is at Y=25 to 240 natively.
        # It's better to just write the box directly in native coordinates if we know them,
        # or calculate them here.
        P = 8/3
        PX = 2.0
        PY = 0.66
        x0 = int((box_screen[0] - PX) / P)
        y0 = int((box_screen[1] - PY) / P)
        x1 = int((box_screen[2] - PX) / P)
        y1 = int((box_screen[3] - PY) / P)
        
        sprite_px = extract_sprite(base_px, (x0, y0, x1, y1))
        
        # Apply repairs
        repairs = sp.get('repairs', [])
        for rep in repairs:
            if rep['type'] == 'remove_colors':
                # Turn specific colors transparent
                colors = [tuple(int(c.lstrip('#')[i:i+2], 16) for i in (0,2,4)) for c in rep['colors']]
                for y in range(len(sprite_px)):
                    for x in range(len(sprite_px[0])):
                        if sprite_px[y][x][:3] in colors:
                            sprite_px[y][x] = (0, 0, 0, 0)
                            
            elif rep['type'] == 'mirror_fill':
                axis = rep['axis_x'] - x0 # axis relative to sprite
                for y in range(len(sprite_px)):
                    for x in range(len(sprite_px[0])):
                        if sprite_px[y][x][3] == 0:
                            # reflect across axis
                            mir_x = int(axis + (axis - x))
                            if 0 <= mir_x < len(sprite_px[0]) and sprite_px[y][mir_x][3] > 0:
                                sprite_px[y][x] = sprite_px[y][mir_x]
                                
        write_png(f"art/sprites/{name}.png", sprite_px)
        print(f"Extracted and repaired {name}")

if __name__ == '__main__':
    process_sprites(sys.argv[1])
