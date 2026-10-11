from PIL import Image, ImageDraw
import numpy as np, sys
def view(names, out, Z=8, bgc=(255,214,240), label=True):
    ims=[Image.open(f'art/{n}.png') for n in names]
    H=max(i.height for i in ims)*Z; W=sum(i.width*Z+16 for i in ims)
    s=Image.new('RGB',(W,H+14),(40,40,40)); x=0; d=ImageDraw.Draw(s)
    for n,im in zip(names,ims):
        bg=Image.new('RGBA',im.size,bgc+(255,)); bg.alpha_composite(im)
        z=bg.resize((im.width*Z,im.height*Z),Image.NEAREST).convert('RGB'); dz=ImageDraw.Draw(z)
        for gx in range(0,im.width,5): dz.line([(gx*Z,0),(gx*Z,im.height*Z)],fill=(230,190,215) if gx%10 else (200,120,170))
        for gy in range(0,im.height,5): dz.line([(0,gy*Z),(im.width*Z,gy*Z)],fill=(230,190,215) if gy%10 else (200,120,170))
        s.paste(z,(x,14)); d.text((x+2,1),n,fill=(255,255,0)); x+=im.width*Z+16
    s.save(out); return s.size
if __name__=='__main__':
    print(view(sys.argv[2:],sys.argv[1]))
