import json, base64, numpy as np
from PIL import Image
names={}
for m in ('pink','cyan','yellow'):
    for f in ('idle','w1','w2','w3','w4','jump'): names[f'{m}_{f}']=f'art/{m}_{f}.png'
    names[f'sel_{m}']=f'art/sel_{m}.png'
for n in ('boss_angry','boss_sad','win_group','trophy','party_p','party_c','party_y','trophy_big'): names[n]=f'final/{n}.png'
assets={}
for n,path in names.items():
    q=np.asarray(Image.open(path).convert('RGBA')); H,W=q.shape[:2]; pal=[]; lut={}; idx=bytearray()
    for j in range(H):
        for i in range(W):
            if q[j,i,3]==0: idx.append(255); continue
            c=tuple(int(v) for v in q[j,i,:3])
            if c not in lut: lut[c]=len(pal); pal.append(list(c))
            idx.append(lut[c])
    rle=bytearray(); k=0
    while k<len(idx):
        v=idx[k]; c=1
        while k+c<len(idx) and idx[k+c]==v and c<255: c+=1
        rle+=bytes([v,c]); k+=c
    assets[n]={'w':W,'h':H,'pal':pal,'r':base64.b64encode(bytes(rle)).decode()}
meta=json.load(open('art/mice_meta.json'))
assets['_meta']=meta
json.dump(assets,open('final/assets2.json','w'),separators=(',',':'))
print(len(assets),'sprites', len(json.dumps(assets)),'bytes'); print({k:(v['w'],v['h']) for k,v in assets.items() if k.endswith('idle')}, meta)
