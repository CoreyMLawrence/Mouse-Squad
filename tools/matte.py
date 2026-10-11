import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from png import read_png, write_png

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def in_class(color, bg_classes):
    r, g, b = color[:3]
    for cls in bg_classes:
        if 'max_val' in cls:
            if r <= cls['max_val'] and g <= cls['max_val'] and b <= cls['max_val']: return True
        elif 'min_val' in cls and 'max_val' in cls:
            pass # Handle ranges if needed
        elif 'color' in cls:
            tr, tg, tb = hex_to_rgb(cls['color'])
            tol = cls.get('tol', 0)
            if abs(r - tr) <= tol and abs(g - tg) <= tol and abs(b - tb) <= tol: return True
        elif 'color_range' in cls:
            c1 = hex_to_rgb(cls['color_range'][0])
            c2 = hex_to_rgb(cls['color_range'][1])
            if c1[0] <= r <= c2[0] and c1[1] <= g <= c2[1] and c1[2] <= b <= c2[2]: return True
    return False

def matte(infile, outfile, recipe_file):
    with open(recipe_file, 'r') as f:
        recipe = json.load(f)
        
    w, h, px = read_png(infile)
    bg_classes = recipe.get('bg_classes', [])
    
    # 4-connected flood fill from the edges
    visited = set()
    queue = []
    
    # Add borders to queue
    for x in range(w):
        queue.append((x, 0))
        queue.append((x, h - 1))
    for y in range(1, h - 1):
        queue.append((0, y))
        queue.append((w - 1, y))
        
    alpha_mask = [[255]*w for _ in range(h)]
    
    while queue:
        x, y = queue.pop(0)
        if (x, y) in visited: continue
        visited.add((x, y))
        
        color = px[y][x]
        if in_class(color, bg_classes):
            alpha_mask[y][x] = 0
            # add neighbors
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                    queue.append((nx, ny))
                    
    # Cloud special rule: cloud is only removed if connected to sky. 
    # Handled by adding cloud colour to bg_classes, so flood fill does it naturally!
    
    out_px = []
    for y in range(h):
        row = []
        for x in range(w):
            r, g, b = px[y][x][:3]
            a = alpha_mask[y][x]
            row.append((r, g, b, a))
        out_px.append(row)
        
    print(f"Matted {infile}")
    write_png(outfile, out_px)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: matte.py <infile> <outfile> <recipe.json>")
        sys.exit(1)
    matte(sys.argv[1], sys.argv[2], sys.argv[3])
