import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from png import read_png, write_png

P = 8/3
PX = 2.0
PY = 0.66

def gridlock(infile, outfile, spreadfile=None):
    w, h, px = read_png(infile)
    cols = int((w - PX) / P)
    rows = int((h - PY) / P)
    grid = []
    spreads = []
    for j in range(rows):
        r = []
        rs = []
        for i in range(cols):
            # Sample inner core of the cell (avoid seams)
            xs = [int(PX + i*P + 0.75 + k*0.6) for k in range(3)]
            ys = [int(PY + j*P + 0.75 + k*0.6) for k in range(3)]
            s = [px[y][x] for y in ys for x in xs if x < w and y < h]
            
            med = []
            max_spread = 0
            for ch in range(3):
                vals = sorted(c[ch] for c in s)
                med.append(vals[len(vals)//2])
                max_spread = max(max_spread, vals[-1] - vals[0])
            
            r.append(tuple(med) + (255,)) # RGBA
            rs.append(max_spread)
        grid.append(r)
        spreads.append(rs)
        
    print(f"Grid-locked {infile} to {cols}x{rows}")
    write_png(outfile, grid)
    if spreadfile:
        with open(spreadfile, 'w') as f:
            json.dump(spreads, f)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: gridlock.py <infile> <outfile> [spreadfile]")
        sys.exit(1)
    gridlock(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
