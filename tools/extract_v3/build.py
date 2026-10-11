from lib import *
import json, base64
from PIL import Image
OUT={}
def bg_sel(c):
    mx,mn=max(c),min(c); return mx<60 or (mx-mn>150)
def bg_play(c):
    r,g,b=c; mx,mn=max(c),min(c)
    if b-r>100 and g>200: return True
    if g>r+40 and g>b+15: return True
    if b-r>12 and g-r>8 and mx<175: return True
    return False
def bg_dark(c): return max(c)<70 or (c[1]>200 and c[0]<120 and c[2]<60)   # black + HUD green
def cleanup(q):
    q=q.copy(); H,W=q.shape[:2]; a=q[...,3]>0
    for _ in range(2):
        rm=[]
        for j in range(H):
            for i in range(W):
                if not a[j,i]: continue
                n8=sum(1 for di in(-1,0,1) for dj in(-1,0,1) if (di or dj) and 0<=i+di<W and 0<=j+dj<H and a[j+dj,i+di])
                if n8<=1: rm.append((i,j)); continue
                # light 1px fringe on the silhouette that matches none of its neighbours
                c=tuple(q[j,i,:3]); edge=any(not(0<=i+di<W and 0<=j+dj<H) or not a[j+dj,i+di] for di,dj in((1,0),(-1,0),(0,1),(0,-1)))
                if edge and sum(c)>560:
                    same=sum(1 for di,dj in((1,0),(-1,0),(0,1),(0,-1)) if 0<=i+di<W and 0<=j+dj<H and a[j+dj,i+di] and tuple(q[j+dj,i+di,:3])==c)
                    if same==0: rm.append((i,j))
        for i,j in rm: a[j,i]=False
    q[...,3]=a*255
    return crop_alpha(q)
def deteal(q):
    q=q.copy(); H,W=q.shape[:2]
    for _ in range(3):
        a=q[...,3]>0; rm=[]
        for j in range(H):
            for i in range(W):
                if not a[j,i]: continue
                r,g,b_=[int(v) for v in q[j,i,:3]]
                if not(b_-r>40 and g-r>40): continue
                edge=any(not(0<=i+di<W and 0<=j+dj<H) or not a[j+dj,i+di] for di,dj in((1,0),(-1,0),(0,1),(0,-1)))
                if edge or j>H*0.45: rm.append((i,j))
        for i,j in rm:
            # interior speck -> take the most common opaque non-teal neighbour; edge -> transparent
            nb=[tuple(q[j+dj,i+di,:3]) for di in(-1,0,1) for dj in(-1,0,1) if (di or dj) and 0<=i+di<W and 0<=j+dj<H and q[j+dj,i+di,3] and not(int(q[j+dj,i+di,2])-int(q[j+dj,i+di,0])>40)]
            edge=any(not(0<=i+di<W and 0<=j+dj<H) or not a[j+dj,i+di] for di,dj in((1,0),(-1,0),(0,1),(0,-1)))
            if edge or not nb: q[j,i,3]=0
            else:
                from collections import Counter; q[j,i,:3]=Counter(nb).most_common(1)[0][0]
    return q
def put(name,q):
    q=np.asarray(q); OUT[name]=q; save(q,name,'/tmp/ms/x/final/')
import os; os.makedirs('/tmp/ms/x/final',exist_ok=True)
P=P0/2
# --- select-screen mice (crisp grid art, shared 3.073 grid) ---
for k,(b,d) in {'pink':((300,690,800,1330),(252,3,165)),'cyan':((930,480,1540,1310),(3,249,252)),'yellow':((1560,690,2110,1330),(249,252,57))}.items():
    q,C,g=extractF(1093,b,bg_sel,anchors=[(0,0,0),d],P=P,core=0.25,holes=6)
    put('sel_'+k,cleanup(q))
# --- gameplay walkers + alternate stride ---
def stride(q):
    H,W=q.shape[:2]; a=q[...,3]>0
    # legs zone = below the widest part of the white belly
    light=(q[...,:3].sum(2)>600)&a
    rows=[j for j in range(H) if light[j].sum()>2]
    top=int(H*0.72) if not rows else max(int(H*0.70),min(rows[-1]-2,int(H*0.82)))
    zone=q[top:].copy(); za=zone[...,3]>0
    xs=np.where(za.any(0))[0]; x0,x1=xs.min(),xs.max()
    out=q.copy(); out[top:]=0
    seg=zone[:,x0:x1+1][:,::-1]
    out[top:,x0:x1+1]=seg
    # body bob: shift everything above the legs up 1px
    b=np.zeros_like(out); b[:-1]=out[1:]; b[top-1:]=out[top-1:]
    return b
for k,b in {'pink':(1379,920,1652,1290),'cyan':(1689,950,1912,1275),'yellow':(1065,960,1345,1260)}.items():
    q,C,g=extractF(1107,b,bg_play,anchors=[(105,237,252),(3,183,51),(69,99,105)],k=14,P=P,core=0.25)
    q=deteal(q); q=cleanup(q); put(k+'_a',q); put(k+'_b',stride(q))
# --- boss (built by boss.py) ---
for n in('boss_angry','boss_sad'): put(n,cleanup(np.asarray(Image.open(n+'.png'))))
# --- win group ---
put('win_group',cleanup(np.asarray(Image.open('win_group.png'))))
# --- HUD trophy, party icons, big trophy ---
q,C,g=extractF(1122,(130,365,235,480),bg_dark,k=6,P=P,core=0.25,holes=2); put('trophy',q)
for k,b in {'party_p':(1040,1365,1130,1440),'party_c':(1135,1365,1225,1440),'party_y':(1225,1365,1315,1440)}.items():
    q,C,g=extractF(1122,b,bg_dark,k=3,P=P,core=0.25); put(k,q)
q,C,g=extractF(1123,(405,570,920,1105),bg_dark,k=6,P=P,core=0.25,holes=6); put('trophy_big',q)
# --- pack: palette + base64 index bytes (255 = transparent) ---
assets={}
for n,q in OUT.items():
    H,W=q.shape[:2]; pal=[]; idx=bytearray()
    lut={}
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
    print(n,W,'x',H,len(pal),'cols')
json.dump(assets,open('/tmp/ms/x/final/assets.json','w'),separators=(',',':'))
print('bytes',len(json.dumps(assets)))
