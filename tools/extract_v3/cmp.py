import sys
from PIL import Image
from lib import load
import numpy as np
def cmp(items,out,Z=5):
    # items: (name, n, box)
    tiles=[]
    for name,n,box in items:
        o=Image.fromarray(load(n)[box[1]:box[3],box[0]:box[2]].astype(np.uint8))
        e=Image.open(f'/tmp/ms/x/{name}.png')
        eb=Image.new('RGBA',e.size,(255,0,255,255)); eb.alpha_composite(e)
        eb=eb.resize((e.width*Z,e.height*Z),Image.NEAREST).convert('RGB')
        o=o.resize((int(o.width*eb.height/o.height),eb.height))
        t=Image.new('RGB',(o.width+eb.width+10,eb.height),(30,30,30));t.paste(o,(0,0));t.paste(eb,(o.width+10,0))
        tiles.append(t)
    W=max(t.width for t in tiles);H=sum(t.height+10 for t in tiles)
    s=Image.new('RGB',(W,H),(30,30,30));y=0
    for t in tiles: s.paste(t,(0,y));y+=t.height+10
    s.thumbnail((1600,2400));s.save(out)
