import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from png import read_png, write_png

def priority(color):
    r, g, b, a = color
    if a == 0: return 0
    # Black outline/eye
    if r < 30 and g < 30 and b < 30: return 3
    # Accessories (pink, purple, cyan, yellow)
    if (r > 200 and g < 100) or (r < 100 and b > 200) or (r > 200 and g > 200) or (g > 200 and b > 200):
        return 2
    # Fur / other
    return 1

def downsample(infile, outfile):
    w, h, px = read_png(infile)
    out_w = w // 2
    out_h = h // 2
    out_px = [[(0,0,0,0)] * out_w for _ in range(out_h)]
    
    for y in range(out_h):
        for x in range(out_w):
            c0 = px[y*2][x*2]
            c1 = px[y*2][x*2+1] if x*2+1 < w else (0,0,0,0)
            c2 = px[y*2+1][x*2] if y*2+1 < h else (0,0,0,0)
            c3 = px[y*2+1][x*2+1] if x*2+1 < w and y*2+1 < h else (0,0,0,0)
            
            blocks = [c0, c1, c2, c3]
            scores = {}
            for i, c in enumerate(blocks):
                if c[3] == 0: continue
                # We group by color
                col = tuple(c[:3])
                if col not in scores: scores[col] = 0
                scores[col] += priority(c)
                
            if not scores:
                continue
                
            # Tie breaking goes to the one that appeared first (c0 -> c1 -> c2 -> c3)
            best_col = None
            best_score = -1
            for c in blocks:
                if c[3] == 0: continue
                col = tuple(c[:3])
                s = scores[col]
                if s > best_score:
                    best_score = s
                    best_col = col
                    
            if best_col:
                out_px[y][x] = best_col + (255,)
                
    write_png(outfile, out_px)

if __name__ == '__main__':
    downsample(sys.argv[1], sys.argv[2])
