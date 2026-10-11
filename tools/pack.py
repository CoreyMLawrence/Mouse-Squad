import sys, os, base64
sys.path.insert(0, os.path.dirname(__file__))
from png import read_png

def pack_sprite(infile):
    w, h, px = read_png(infile)
    
    # Extract palette
    palette = []
    indices = []
    
    for y in range(h):
        for x in range(w):
            c = px[y][x]
            if c[3] == 0:
                indices.append(255)
            else:
                rgb = tuple(c[:3])
                if rgb not in palette:
                    palette.append(rgb)
                indices.append(palette.index(rgb))
                
    # RLE
    rle = []
    if not indices: return ""
    
    curr = indices[0]
    count = 1
    for i in range(1, len(indices)):
        if indices[i] == curr and count < 255:
            count += 1
        else:
            rle.append(curr)
            rle.append(count)
            curr = indices[i]
            count = 1
    rle.append(curr)
    rle.append(count)
    
    # Base64 encode RLE
    b64 = base64.b64encode(bytes(rle)).decode('ascii')
    
    pal_str = "[" + ",".join(f"[{r},{g},{b}]" for r,g,b in palette) + "]"
    
    return f"{{w:{w}, h:{h}, pal:{pal_str}, rle:'{b64}'}}"

def pack_all(sprite_dir, outfile):
    sprites = {}
    for f in os.listdir(sprite_dir):
        if f.endswith('.png'):
            name = f.split('.')[0]
            sprites[name] = pack_sprite(os.path.join(sprite_dir, f))
            
    out_js = "const ASSETS = {\n"
    for name, data in sprites.items():
        out_js += f"  '{name}': {data},\n"
    out_js += "};\n"
    
    with open(outfile, 'w') as f:
        f.write(out_js)
        
    print(f"Packed {len(sprites)} sprites into {outfile}")

if __name__ == '__main__':
    pack_all(sys.argv[1], sys.argv[2])
