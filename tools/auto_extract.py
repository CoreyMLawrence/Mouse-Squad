import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from png import read_png, write_png

def find_components(px, min_size=5):
    h = len(px)
    w = len(px[0])
    visited = set()
    components = []
    
    for y in range(h):
        for x in range(w):
            if (x, y) not in visited and px[y][x][3] > 0:
                # new component
                comp = []
                q = [(x, y)]
                visited.add((x, y))
                
                min_x, max_x = x, x
                min_y, max_y = y, y
                
                while q:
                    cx, cy = q.pop(0)
                    comp.append((cx, cy))
                    min_x = min(min_x, cx)
                    max_x = max(max_x, cx)
                    min_y = min(min_y, cy)
                    max_y = max(max_y, cy)
                    
                    for dx, dy in [(0,1),(1,0),(0,-1),(-1,0), (1,1), (-1,-1), (1,-1), (-1,1)]:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited and px[ny][nx][3] > 0:
                            visited.add((nx, ny))
                            q.append((nx, ny))
                            
                if len(comp) >= min_size:
                    components.append({
                        'pixels': comp,
                        'box': (min_x, min_y, max_x+1, max_y+1)
                    })
    return components

def auto_extract(infile, out_prefix):
    w, h, px = read_png(infile)
    comps = find_components(px)
    
    print(f"Found {len(comps)} components in {infile}")
    
    for i, c in enumerate(comps):
        x0, y0, x1, y1 = c['box']
        cw = x1 - x0
        ch = y1 - y0
        
        out_px = [[(0,0,0,0)] * cw for _ in range(ch)]
        for px_x, px_y in c['pixels']:
            out_px[px_y - y0][px_x - x0] = px[px_y][px_x]
            
        write_png(f"{out_prefix}_{i}.png", out_px)

if __name__ == '__main__':
    auto_extract(sys.argv[1], sys.argv[2])
