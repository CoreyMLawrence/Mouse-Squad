import sys, os, json, random
sys.path.insert(0, os.path.dirname(__file__))
from png import read_png, write_png

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f"#{r:02X}{g:02X}{b:02X}"

def color_dist(c1, c2):
    rmean = (c1[0] + c2[0]) / 2
    dr = c1[0] - c2[0]
    dg = c1[1] - c2[1]
    db = c1[2] - c2[2]
    return (2 + rmean/256)*dr**2 + 4*dg**2 + (2 + (255-rmean)/256)*db**2

def kmeans(colors, weights, k, iters=10):
    if len(colors) <= k: return colors
    centroids = random.sample(colors, k)
    for _ in range(iters):
        clusters = [[] for _ in range(k)]
        cluster_weights = [0] * k
        for i, c in enumerate(colors):
            best_d = float('inf')
            best_idx = 0
            for j, cent in enumerate(centroids):
                d = color_dist(c, cent)
                if d < best_d:
                    best_d = d
                    best_idx = j
            clusters[best_idx].append(c)
            cluster_weights[best_idx] += weights[i]
            
        new_centroids = []
        for i in range(k):
            if not clusters[i]:
                new_centroids.append(centroids[i])
            else:
                r, g, b = 0, 0, 0
                for c in clusters[i]:
                    w = weights[colors.index(c)] # slightly inefficient but colors list is small
                    r += c[0] * w
                    g += c[1] * w
                    b += c[2] * w
                cw = cluster_weights[i]
                new_centroids.append((int(r/cw), int(g/cw), int(b/cw)))
        centroids = new_centroids
    return centroids

def quantize(infile, outfile, recipe_file):
    with open(recipe_file, 'r') as f:
        recipe = json.load(f)
        
    w, h, px = read_png(infile)
    
    # Extract unique colors and frequencies
    color_counts = {}
    for y in range(h):
        for x in range(w):
            p = px[y][x]
            if len(p) > 3 and p[3] == 0: continue
            c = tuple(p[:3])
            color_counts[c] = color_counts.get(c, 0) + 1
            
    unique_colors = list(color_counts.keys())
    weights = list(color_counts.values())
    
    # 1. K-means to find natural palette
    k = recipe.get('k', 16)
    clusters = kmeans(unique_colors, weights, k)
    
    # 2. Snap to canonical palette
    canonical = [hex_to_rgb(h) for h in recipe.get('palette', [])]
    if not canonical:
        canonical = clusters
        
    final_palette = []
    for c in clusters:
        best_d = float('inf')
        best_can = c
        for can in canonical:
            d = color_dist(c, can)
            if d < best_d:
                best_d = d
                best_can = can
        # If distance is small enough, snap, else keep new color
        # Redmean distance of 1500 is roughly deltaE of 8
        if best_d < 3000:
            final_palette.append(best_can)
        else:
            final_palette.append(c)
            print(f"Adding new color: {rgb_to_hex(*c)}")
            
    # 3. Map pixels
    out_px = []
    for y in range(h):
        row = []
        for x in range(w):
            p = px[y][x]
            if len(p) > 3 and p[3] == 0:
                row.append((0, 0, 0, 0))
                continue
            
            c = tuple(p[:3])
            best_d = float('inf')
            best_idx = 0
            for i, pal in enumerate(final_palette):
                d = color_dist(c, pal)
                if d < best_d:
                    best_d = d
                    best_idx = i
            row.append(final_palette[best_idx] + (255,))
        out_px.append(row)
        
    # 4. Despeckle (simple majority filter)
    despeckled = []
    for y in range(h):
        row = []
        for x in range(w):
            p = out_px[y][x]
            if p[3] == 0:
                row.append(p)
                continue
                
            neighbors = []
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0: continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        np = out_px[ny][nx]
                        if np[3] > 0:
                            neighbors.append(np)
                            
            # Check if all neighbors differ from current
            differ_count = sum(1 for np in neighbors if np[:3] != p[:3])
            if differ_count == len(neighbors) and len(neighbors) > 0:
                # Take majority
                counts = {}
                for np in neighbors: counts[np[:3]] = counts.get(np[:3], 0) + 1
                best_n = max(counts.keys(), key=lambda k: counts[k])
                row.append(best_n + (255,))
            else:
                row.append(p)
        despeckled.append(row)
        
    print(f"Quantized {infile} to {len(final_palette)} colors")
    write_png(outfile, despeckled)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: quantize.py <infile> <outfile> <recipe.json>")
        sys.exit(1)
    quantize(sys.argv[1], sys.argv[2], sys.argv[3])
