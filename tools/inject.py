import sys, re

def inject():
    with open('index.html', 'r') as f:
        html = f.read()
        
    with open('assets.js', 'r') as f:
        assets_js = f.read()
        
    # Replace ASSETS
    html = re.sub(r'const ASSETS = \{.*?\n\};\n', assets_js, html, flags=re.DOTALL)
    
    # Replace decode function
    new_decode = """function decode(s){
  const c = document.createElement('canvas');
  c.width = s.w; c.height = s.h;
  const g = c.getContext('2d');
  const img = g.createImageData(s.w, s.h);
  
  if (s.rle) {
    const raw = atob(s.rle);
    let i = 0, px = 0;
    while(i < raw.length) {
      const val = raw.charCodeAt(i++);
      const count = raw.charCodeAt(i++);
      for(let k=0; k<count; k++) {
        if(val !== 255) {
          const o = px * 4;
          const p = s.pal[val];
          img.data[o]=p[0]; img.data[o+1]=p[1]; img.data[o+2]=p[2]; img.data[o+3]=255;
        }
        px++;
      }
    }
  } else {
    // Old format fallback
    for(let y=0;y<s.h;y++)for(let x=0;x<s.w;x++){
      const k = s.px[y][x];
      if(k<0) continue;
      const o = (y*s.w+x)*4, p = s.pal[k];
      img.data[o]=p[0]; img.data[o+1]=p[1]; img.data[o+2]=p[2]; img.data[o+3]=255;
    }
  }
  g.putImageData(img,0,0);
  return c;
}

const flip = (c) => {
  const fc = document.createElement('canvas');
  fc.width = c.width; fc.height = c.height;
  const fg = fc.getContext('2d');
  fg.translate(c.width, 0); fg.scale(-1, 1);
  fg.drawImage(c, 0, 0);
  return fc;
};

const SPR = {};
for(const k in ASSETS) {
  SPR[k] = decode(ASSETS[k]);
  SPR[k+'_flip'] = flip(SPR[k]);
}
"""
    html = re.sub(r'function decode\(s\)\{.*?const SPR = \{.*?\n\};\n', new_decode, html, flags=re.DOTALL)
    
    # Modify fixed width and height
    html = html.replace('let NI=MAZE[0].length, NJ=MAZE.length;', 'let NI=384, NJ=216;')
    html = html.replace('let WNAT=NI*T, HNAT=NJ*T;', 'let WNAT=384, HNAT=216;')
    
    with open('index.html', 'w') as f:
        f.write(html)
        
    print("Injected assets and decoding logic.")

if __name__ == '__main__':
    inject()
