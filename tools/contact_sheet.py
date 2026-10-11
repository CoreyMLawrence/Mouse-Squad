import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from png import read_png, write_png

def make_contact_sheet(infiles, outfile):
    images = [read_png(f) for f in infiles]
    
    max_w = max(img[0] for img in images)
    max_h = max(img[1] for img in images)
    
    # 2 columns
    cols = 2
    rows = (len(images) + 1) // 2
    
    # padding
    pad = 10
    
    out_w = (max_w + pad) * cols + pad
    out_h = (max_h + pad) * rows + pad
    out_px = [[(0,0,0,0)] * out_w for _ in range(out_h)]
    
    for idx, (iw, ih, px) in enumerate(images):
        cx = idx % cols
        cy = idx // cols
        
        start_x = pad + cx * (max_w + pad)
        start_y = pad + cy * (max_h + pad)
        
        for y in range(ih):
            for x in range(iw):
                out_px[start_y + y][start_x + x] = px[y][x]
                
    write_png(outfile, out_px)
    print(f"Wrote contact sheet to {outfile}")

if __name__ == '__main__':
    infiles = sys.argv[1:-1]
    outfile = sys.argv[-1]
    make_contact_sheet(infiles, outfile)
