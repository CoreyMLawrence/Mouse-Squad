import numpy as np
from PIL import Image
from collections import deque
CI="/sessions/sharp-brave-hypatia/mnt/mouse-squad/art/Concept Images/"
_cache={}
def load(n):
    if n not in _cache: _cache[n]=np.asarray(Image.open(CI+f'IMG_{n}.PNG').convert('RGB')).astype(float)
    return _cache[n]
def fit1(sig,lo=5.95,hi=6.35):
    best=None;n=len(sig)
    for s in np.arange(lo,hi,0.004):
        for ph in np.arange(0,s,0.1):
            L=np.arange(ph,n-1,s);i=L.astype(int);f=L-i
            v=(sig[i]*(1-f)+sig[np.minimum(i+1,n-1)]*f).mean()
            if best is None or v>best[0]: best=(v,s,ph)
    return best
def grid(n,box):
    im=load(n);x0,y0,x1,y1=box
    c=im[y0:y1,x0:x1].sum(2)
    gx=np.abs(np.diff(c,axis=1)).sum(0);gy=np.abs(np.diff(c,axis=0)).sum(1)
    _,sx,ox=fit1(gx/gx.mean());_,sy,oy=fit1(gy/gy.mean())
    return sx,sy,x0+ox+1,y0+oy+1
def sample(n,box,g=None,core=0.3):
    im=load(n);x0,y0,x1,y1=box
    sx,sy,ax,ay=g or grid(n,box)
    ni=int((x1-ax)//sx);nj=int((y1-ay)//sy)
    out=np.zeros((nj,ni,3))
    for j in range(nj):
        for i in range(ni):
            cx=ax+(i+0.5)*sx;cy=ay+(j+0.5)*sy
            r=max(1,int(sx*core))
            p=im[int(cy)-r:int(cy)+r+1,int(cx)-r:int(cx)+r+1].reshape(-1,3)
            out[j,i]=np.median(p,0)
    return out,(sx,sy,ax,ay)
def matte(arr,isbg,seedall=True):
    H,W,_=arr.shape;bg=np.zeros((H,W),bool);q=deque()
    for j in range(H):
        for i in range(W):
            if (i in(0,W-1) or j in(0,H-1)) and isbg(arr[j,i]): bg[j,i]=1;q.append((i,j))
    while q:
        i,j=q.popleft()
        for di,dj in((1,0),(-1,0),(0,1),(0,-1)):
            a,b=i+di,j+dj
            if 0<=a<W and 0<=b<H and not bg[b,a] and isbg(arr[b,a]): bg[b,a]=1;q.append((a,b))
    fg=~bg
    # keep largest component
    lab=np.zeros((H,W),int);k=0;sizes={}
    for j in range(H):
        for i in range(W):
            if fg[j,i] and not lab[j,i]:
                k+=1;q=deque([(i,j)]);lab[j,i]=k;c=0
                while q:
                    a,b=q.popleft();c+=1
                    for di,dj in((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
                        x,y=a+di,b+dj
                        if 0<=x<W and 0<=y<H and fg[y,x] and not lab[y,x]: lab[y,x]=k;q.append((x,y))
                sizes[k]=c
    if not sizes: return fg
    big=max(sizes,key=sizes.get)
    keep=[kk for kk,v in sizes.items() if v>=max(6,sizes[big]*0.02)] if not seedall else [big]
    return np.isin(lab,keep)
def kmeans(cols,k=14,minsep=30,it=30):
    rng=np.random.RandomState(1);k=min(k,len(cols))
    C=cols[rng.choice(len(cols),k,replace=False)]
    for _ in range(it):
        lab=((cols[:,None]-C[None])**2).sum(2).argmin(1)
        C=np.array([cols[lab==i].mean(0) if (lab==i).any() else C[i] for i in range(len(C))])
    m=True
    while m:
        m=False
        for i in range(len(C)):
            for j in range(i+1,len(C)):
                if np.linalg.norm(C[i]-C[j])<minsep:
                    C=np.vstack([C[:j],C[j+1:]]);m=True;break
            if m:break
    return C
def quant(arr,fg,k=14,minsep=30,pal=None):
    cols=arr[fg]
    C=pal if pal is not None else kmeans(cols,k,minsep)
    out=np.zeros(arr.shape[:2]+(4,),np.uint8)
    lab=((arr[:,:,None,:]-C[None,None])**2).sum(3).argmin(2)
    q=C[lab]
    out[...,:3]=np.clip(q,0,255);out[...,3]=fg*255
    return out,C
def crop_alpha(rgba):
    a=rgba[...,3]>0;ys,xs=np.where(a)
    return rgba[ys.min():ys.max()+1,xs.min():xs.max()+1]
def save(rgba,name,d='/tmp/ms/x/'):
    Image.fromarray(rgba).save(d+name+'.png')

def palette(cols,k=16,minsep=22):
    C=kmeans(cols,k,minsep)
    lab=((cols[:,None]-C[None])**2).sum(2).argmin(1)
    out=[]
    for i in range(len(C)):
        m=cols[lab==i]
        if len(m)==0: continue
        c=np.median(m,0)
        if c.max()-c.min()<16: c=np.full(3,c.mean())   # neutral greys stay neutral
        out.append(c)
    return np.array(out)
def despeckle(rgba):
    a=rgba.copy();H,W=a.shape[:2]
    for j in range(1,H-1):
        for i in range(1,W-1):
            if a[j,i,3]==0: continue
            c=tuple(rgba[j,i,:3]); nb=[tuple(rgba[j+dj,i+di,:3]) for di,dj in((1,0),(-1,0),(0,1),(0,-1)) if rgba[j+dj,i+di,3]]
            if len(nb)==4 and c not in nb:
                from collections import Counter
                m,cnt=Counter(nb).most_common(1)[0]
                if cnt>=3 and sum(c)>40: a[j,i,:3]=m   # never erase dark detail
    return a
def extract(n,box,isbg,k=16,minsep=22,despk=True,pal=None):
    arr,g=sample(n,box)
    fg=matte(arr,isbg)
    C=pal if pal is not None else palette(arr[fg],k,minsep)
    q,_=quant(arr,fg,pal=C)
    if despk: q=despeckle(q)
    return crop_alpha(q),C,g

def prune(cols,C,minfrac=0.025,tol=26,anchors=()):
    lab=((cols[:,None]-C[None])**2).sum(2).argmin(1)
    cnt=np.bincount(lab,minlength=len(C))/len(cols)
    big=[i for i in range(len(C)) if cnt[i]>=minfrac or C[i].max()<40]
    keep=list(big)
    P=[C[i] for i in big]+[np.array(a,float) for a in anchors]
    for i in range(len(C)):
        if i in big: continue
        c=C[i]; dmin=1e9
        if c.max()-c.min()>110 and cnt[i]>0.003: keep.append(i); continue   # saturated accent
        for a in range(len(P)):
            for b in range(len(P)):
                if a>=b: continue
                A,B=P[a],P[b]; ab=B-A; t=np.clip(np.dot(c-A,ab)/max(np.dot(ab,ab),1e-6),0,1)
                dmin=min(dmin,np.linalg.norm(A+t*ab-c))
        if dmin>tol: keep.append(i)   # distinct accent colour, not an edge blend
    return C[keep]
def extract(n,box,isbg,k=16,minsep=22,despk=True,pal=None,pr=True,anchors=()):
    arr,g=sample(n,box)
    fg=matte(arr,isbg)
    C=pal if pal is not None else palette(arr[fg],k,minsep)
    if pr and pal is None: C=prune(arr[fg],C,anchors=anchors)
    q,_=quant(arr,fg,pal=C)
    if despk: q=despeckle(q.astype(np.int32)).astype(np.uint8)
    return crop_alpha(q),C,g

P0=2360/384
def fitph(sig,s=None):
    s=s or P0
    best=None;n=len(sig)
    for ph in np.arange(0,s,0.05):
        L=np.arange(ph,n-1,s);i=L.astype(int);f=L-i
        v=(sig[i]*(1-f)+sig[np.minimum(i+1,n-1)]*f).mean()
        if best is None or v>best[0]: best=(v,ph)
    return best[1]
def gridfixed(n,box,P=None):
    P=P or P0
    im=load(n);x0,y0,x1,y1=box
    c=im[y0:y1,x0:x1].sum(2)
    gx=np.abs(np.diff(c,axis=1)).sum(0);gy=np.abs(np.diff(c,axis=0)).sum(1)
    return P,P,x0+fitph(gx,P)+1,y0+fitph(gy,P)+1
def extractF(n,box,isbg,**kw):
    arr,g=sample(n,box,g=gridfixed(n,box,kw.pop('P',None)),core=kw.pop('core',0.3))
    fg=matte(arr,isbg,seedall=kw.pop('single',True))
    h=kw.pop("holes",False)
    if h: fg=strip_lines(arr,clear_holes(arr,fg,thr=16,minsize=(120 if h is True else h)))
    pal=kw.get('pal');anchors=kw.get('anchors',())
    C=pal if pal is not None else palette(arr[fg],kw.get('k',16),kw.get('minsep',22))
    if pal is None: C=prune(arr[fg],C,anchors=anchors)
    q,_=quant(arr,fg,pal=C)
    q=despeckle(q.astype(np.int32)).astype(np.uint8)
    return crop_alpha(q),C,g

def clear_holes(arr,fg,thr=16,minsize=20):
    """enclosed pockets of pure background black -> transparent (eyes are ~26+)"""
    H,W=fg.shape; cand=fg&(arr.max(2)<thr); seen=np.zeros_like(cand)
    for j in range(H):
        for i in range(W):
            if cand[j,i] and not seen[j,i]:
                q=deque([(i,j)]);seen[j,i]=1;pts=[]
                while q:
                    a,b=q.popleft();pts.append((a,b))
                    for di,dj in((1,0),(-1,0),(0,1),(0,-1)):
                        x,y=a+di,b+dj
                        if 0<=x<W and 0<=y<H and cand[y,x] and not seen[y,x]: seen[y,x]=1;q.append((x,y))
                if len(pts)>=minsize:
                    S=set(pts); nb=[]
                    for a,b in pts:
                        for di,dj in((1,0),(-1,0),(0,1),(0,-1)):
                            x,y=a+di,b+dj
                            if 0<=x<W and 0<=y<H and (x,y) not in S: nb.append(arr[y,x].max() if fg[y,x] else 0)
                    light=sum(1 for v in nb if v>170)/max(1,len(nb))
                    if light<0.5:                       # bordered by light fur => it's a nose/pupil
                        for a,b in pts: fg[b,a]=False
    return fg

def strip_lines(arr,fg,thr=62,it=4):
    H,W=fg.shape
    for _ in range(it):
        rm=[]
        for j in range(H):
            for i in range(W):
                if fg[j,i] and arr[j,i].max()<thr:
                    t=sum(1 for di,dj in((1,0),(-1,0),(0,1),(0,-1)) if not(0<=i+di<W and 0<=j+dj<H) or not fg[j+dj,i+di])
                    if t>=2: rm.append((i,j))
        if not rm: break
        for i,j in rm: fg[j,i]=False
    return fg
