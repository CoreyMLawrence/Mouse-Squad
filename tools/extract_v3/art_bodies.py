"""Mouse Squad — body transplant.
Bodies: Corey's pose references (swinging arms, leaning torso, trailing tail, cheer jump),
sampled back onto the sprite grid.  Heads: the hand-finished heads from art_mice.py
(continuous glasses, bow, headband, rebuilt ear rims).  Run art_mice.py first."""
import sys, numpy as np
from PIL import Image
from collections import Counter, deque
sys.path.insert(0,'/tmp/ms/ref'); sys.path.insert(0,'/sessions/sharp-brave-hypatia/mnt/outputs/work/ms')
from sample import sample
A='/tmp/ms/x/art/'
FR=['idle','w1','w2','w3','w4','jump']
N4=((1,0),(-1,0),(0,1),(0,-1)); N8=N4+((1,1),(1,-1),(-1,1),(-1,-1))
def load(n): return np.asarray(Image.open(A+n+'.png').convert('RGBA')).astype(np.int32).copy()
def save(q,n): Image.fromarray(np.clip(q,0,255).astype(np.uint8)).save(A+n+'.png')
def shade(c,k): return tuple(int(v*k) for v in c)

MICE={
  #        fur            light            white            black       neck  head source frame
  'pink':  dict(fur=(133,)*3, light=(237,)*3, white=(255,)*3, blk=(26,)*3, neck=57, ref='pink'),
  'cyan':  dict(fur=(105,)*3, light=(223,)*3, white=(247,)*3, blk=(26,)*3, neck=67, ref='cyan'),
  'yellow':dict(fur=(85,)*3,  light=(218,)*3, white=(218,)*3, blk=(27,)*3, neck=52, ref='cyan'),
}
REFCACHE={}
def ref_frames(m):
    if m not in REFCACHE: REFCACHE[m]=sample(m)
    return REFCACHE[m]

def body_mask(arr, bg):
    r,g,b=arr[...,0],arr[...,1],arr[...,2]
    return ~bg
def levels(arr, fg):
    """calibrate this sheet's grey levels: fur peak and the darker far-leg peak"""
    lum=arr.mean(2)[fg]; neutral=lum[(lum>60)&(lum<180)]
    hist=np.bincount(neutral.astype(int),minlength=256)
    sm=np.convolve(hist,np.ones(7)/7,'same')
    fur=int(np.argmax(sm))
    lo=sm.copy(); lo[fur-14:]=0
    far=int(np.argmax(lo)) if lo.max()>sm[fur]*0.06 else fur-25
    return fur,far
def quantize_body(arr, fg, P):
    """snap the reference body to this mouse's palette (no ear/bow/glasses colours in a body)"""
    fur=np.array(P['fur'],float); far=np.array(shade(P['fur'],0.78),float)
    pal=[fur, far, np.array(shade(P['fur'],0.62),float), np.array(P['light'],float), np.array(P['white'],float), np.array(P['blk'],float)]
    # measure the reference's own fur / light levels and map them proportionally onto this mouse
    H,W=fg.shape; q=np.zeros((H,W,4),np.int32)
    lum=arr.mean(2)
    fl,fa=LV                                     # calibrated fur / far-leg levels for this sheet
    t_far=(fl+fa)/2; t_sole=fa-(fl-fa)*0.6
    for j in range(H):
        for i in range(W):
            if not fg[j,i]: continue
            L=lum[j,i]
            # reference levels (pink sheet): fur~128, far leg~100, sole~80, light~235, white~250, black~30
            if   L<min(55,t_sole-8): c=P['blk']
            elif L<t_sole: c=shade(P['fur'],0.62)
            elif L<t_far:  c=shade(P['fur'],0.78)
            elif L<185:    c=P['fur']
            elif L<243: c=P['light']
            else:       c=P['white']
            q[j,i,:3]=c; q[j,i,3]=255
    return q

HEADCACHE={}
# which select-screen heads face the viewer's left (need turning to face the walk direction)
MIRROR={'pink':True,'cyan':True,'yellow':False}
def head_of(m, neck):
    """the finished head, cut at the chin, cleaned, and turned to face the walking direction (right)"""
    if m in HEADCACHE: return HEADCACHE[m].copy()
    h=load(m+'_idle')
    h[neck:,:,3]=0
    P=MICE[m]; fur=np.array(P['fur']); light=np.array(P['light'])
    H,W=h.shape[:2]
    # the select pose rests a hand on the chin: fur pixels in the lower face that are not hair
    # (not connected to fur above the eyes) become face colour, or vanish if on the outline
    isfur=lambda j,i: h[j,i,3] and np.abs(h[j,i,:3]-fur).sum()<12
    top=neck-14
    hair=np.zeros((H,W),bool); dq=deque((i,j) for j in range(top) for i in range(W) if isfur(j,i))
    for i,j in dq: hair[j,i]=True
    while dq:
        a,b=dq.popleft()
        for da,db in N4:
            x,y=a+da,b+db
            if 0<=x<W and 0<=y<neck and not hair[y,x] and isfur(y,x): hair[y,x]=True; dq.append((x,y))
    for j in range(top,neck):
        for i in range(W):
            if isfur(j,i) and not hair[j,i]:
                edge=any(not(0<=i+a<W and 0<=j+b<H) or not h[j+b,i+a,3] for a,b in N4)
                if edge: h[j,i,3]=0
                else: h[j,i,:3]=light
    # crop columns, then mirror so the face looks the way the body walks
    xs=np.where(h[...,3].any(0))[0]; h=h[:,xs.min():xs.max()+1]
    if MIRROR[m]: h=h[:, ::-1]          # only heads drawn facing left get turned
    h=h.copy()
    HEADCACHE[m]=h
    return h.copy()

def align(head, refq, neck):
    """best (dx,dy) placing my head over the reference's head (luminance agreement)"""
    Hh,Wh=head.shape[:2]; H,W=refq.shape[:2]
    hl=head[...,:3].mean(2); ha=head[...,3]>0
    best=None
    for dy in range(-9,10):
        for dx in range(-14,15):
            err=0; n=0
            for j in range(0,min(Hh,neck+4),2):
                y=j+dy
                if not(0<=y<H): continue
                for i in range(0,Wh,2):
                    x=i+dx
                    if not(0<=x<W): continue
                    a=ha[j,i]; b=refq[y,x,3]>0
                    if not a and not b: continue
                    n+=1
                    err+= 120 if a!=b else abs(hl[j,i]-refq[y,x,:3].mean())
            if n and (best is None or err/n<best[0]): best=(err/n,dx,dy)
    return best[1],best[2]

def fill_small_holes(q,maxsz=10):
    H,W=q.shape[:2]; out=np.zeros((H,W),bool); dq=deque()
    for j in range(H):
        for i in range(W):
            if (i in(0,W-1) or j in(0,H-1)) and q[j,i,3]==0: out[j,i]=True; dq.append((i,j))
    while dq:
        a,b=dq.popleft()
        for da,db in N4:
            x,y=a+da,b+db
            if 0<=x<W and 0<=y<H and not out[y,x] and q[y,x,3]==0: out[y,x]=True; dq.append((x,y))
    seen=set()
    for j in range(H):
        for i in range(W):
            if q[j,i,3]==0 and not out[j,i] and (i,j) not in seen:
                comp=[(i,j)]; seen.add((i,j)); dq2=deque([(i,j)])
                while dq2:
                    a,b=dq2.popleft()
                    for da,db in N4:
                        x,y=a+da,b+db
                        if 0<=x<W and 0<=y<H and q[y,x,3]==0 and not out[y,x] and (x,y) not in seen: seen.add((x,y)); comp.append((x,y)); dq2.append((x,y))
                if len(comp)<=maxsz:
                    for _ in range(4):
                        for (a,b) in comp:
                            if q[b,a,3]: continue
                            nb=[tuple(q[b+db,a+da,:3]) for da,db in N8 if 0<=a+da<W and 0<=b+db<H and q[b+db,a+da,3]]
                            if nb: q[b,a,:3]=Counter(nb).most_common(1)[0][0]; q[b,a,3]=255
    return q
def despeck(q):
    H,W=q.shape[:2]; out=q.copy()
    for j in range(H):
        for i in range(W):
            if q[j,i,3]==0: continue
            n8=sum(1 for a,b in N8 if 0<=i+a<W and 0<=j+b<H and q[j+b,i+a,3])
            if n8<=1: out[j,i,3]=0; continue
            c=tuple(q[j,i,:3]); nb=[tuple(q[j+b,i+a,:3]) for a,b in N4 if 0<=i+a<W and 0<=j+b<H and q[j+b,i+a,3]]
            if len(nb)>=3 and c not in nb:
                m_,k=Counter(nb).most_common(1)[0]
                if k>=3: out[j,i,:3]=m_
    return out
def keep_main(q,minfrac=0.02):
    H,W=q.shape[:2]; lab=np.zeros((H,W),int); k=0; sizes={}
    for j in range(H):
        for i in range(W):
            if q[j,i,3] and not lab[j,i]:
                k+=1; dq=deque([(i,j)]); lab[j,i]=k; n=0
                while dq:
                    a,b=dq.popleft(); n+=1
                    for da,db in N8:
                        x,y=a+da,b+db
                        if 0<=x<W and 0<=y<H and q[y,x,3] and not lab[y,x]: lab[y,x]=k; dq.append((x,y))
                sizes[k]=n
    big=max(sizes,key=sizes.get)
    for j in range(H):
        for i in range(W):
            if lab[j,i] and sizes[lab[j,i]]<sizes[big]*minfrac: q[j,i,3]=0
    return q

def build(m):
    P=MICE[m]; neck=P['neck']
    head=head_of(m,neck); Hh,Wh=head.shape[:2]
    refs=ref_frames(P['ref'])
    out={}
    for f in FR:
        arr,bg=refs[f]
        fg=body_mask(arr,bg)
        global LV; LV=levels(arr,fg)
        body=quantize_body(arr,fg,P)
        # samples that landed on the sheet's grid lines (pink hue) get their neighbours' colour
        r_,g_,b_=arr[...,0],arr[...,1],arr[...,2]
        unk=fg&(r_-g_>18)&(b_-g_>8)
        for _ in range(3):
            for j,i in zip(*np.where(unk)):
                nb=[tuple(body[j+b,i+a,:3]) for a,b in N8 if 0<=j+b<body.shape[0] and 0<=i+a<body.shape[1] and body[j+b,i+a,3] and not unk[j+b,i+a]]
                if len(nb)>=3: body[j,i,:3]=Counter(nb).most_common(1)[0][0]; unk[j,i]=False
        body[unk,3]=0
        dx,dy=align(head if P['ref']==m else head_of(P['ref'],MICE[P['ref']]['neck']), body, MICE[P['ref']]['neck'] if P['ref']!=m else neck)
        if P['ref']!=m:          # borrowed body (yellow): seat my head on the donor's neck line
            dn=MICE[P['ref']]['neck']-neck
            dy+=dn
        MG=16
        body=np.pad(body,((0,0),(MG,MG),(0,0))); dx+=MG
        dy=max(-4,min(4,dy))
        hn=MICE[P['ref']]['neck'] if P['ref']!=m else neck
        hrow=np.where(head[...,3].any(1))[0].max()
        chin=[i for j in range(hrow-4,hrow+1) for i in range(head.shape[1]) if head[j,i,3]]
        tor=[i for j in range(hn+dy+3,hn+dy+10) if 0<=j<body.shape[0] for i in range(body.shape[1]) if body[j,i,3]]
        if chin and tor:
            dx=int(round(np.median(tor)-np.median(chin)))
        H,W=body.shape[:2]
        # canvas tall enough for my head above the borrowed body
        top=max(0,-dy); c=np.zeros((H+top,max(W,Wh+abs(dx))+2,4),np.int32)
        c[top:top+H,:W]=body
        hy=dy+top
        # remove the reference's own head: anything above the neck that isn't fur (arms/tail are fur)
        hm=np.zeros(c.shape[:2],bool)
        for j in range(Hh):
            for i in range(Wh):
                if head[j,i,3]:
                    y,x=j+hy,i+dx
                    for a in range(-2,3):
                        for b in range(-2,3):
                            if 0<=y+b<c.shape[0] and 0<=x+a<c.shape[1]: hm[y+b,x+a]=True
        if P['ref']!=m:            # borrowed body: also clear where the DONOR's head sat
            dh=head_of(P['ref'],MICE[P['ref']]['neck']); ddx=dx-int(round((dh.shape[1]-head.shape[1])/2)); ddy=hy-(MICE[P['ref']]['neck']-neck)
            for j in range(dh.shape[0]):
                for i in range(dh.shape[1]):
                    if dh[j,i,3]:
                        y,x=j+ddy,i+ddx
                        for a in range(-3,4):
                            for b in range(-3,4):
                                if 0<=y+b<c.shape[0] and 0<=x+a<c.shape[1]: hm[y+b,x+a]=True
        refneck=top+(MICE[P['ref']]['neck'] if P['ref']!=m else neck)+dy-(MICE[P['ref']]['neck']-neck if P['ref']!=m else 0)
        for j in range(c.shape[0]):
            for i in range(c.shape[1]):
                if c[j,i,3] and (hm[j,i] or (j<refneck+3 and tuple(c[j,i,:3]) not in (P['fur'],shade(P['fur'],0.78),shade(P['fur'],0.62)))):
                    c[j,i,3]=0
        H2,W2=c.shape[:2]; reach=np.zeros((H2,W2),bool); dq=deque()
        for j in range(min(H2,refneck+3),H2):
            for i in range(W2):
                if c[j,i,3]: reach[j,i]=True; dq.append((i,j))
        while dq:
            a,b=dq.popleft()
            for da,db in N8:
                x,y=a+da,b+db
                if 0<=x<W2 and 0<=y<H2 and c[y,x,3] and not reach[y,x]: reach[y,x]=True; dq.append((x,y))
        c[~reach,3]=0
        # smooth mottled body greys (3x3 majority on fur/far pixels only)
        furs=(P['fur'],shade(P['fur'],0.78))
        sm=c.copy()
        for j in range(1,H2-1):
            for i in range(1,W2-1):
                if c[j,i,3] and tuple(c[j,i,:3]) in furs:
                    nb=[tuple(c[j+b,i+a,:3]) for a in(-1,0,1) for b in(-1,0,1) if c[j+b,i+a,3] and tuple(c[j+b,i+a,:3]) in furs]
                    m_,k=Counter(nb).most_common(1)[0]
                    if k>=6: sm[j,i,:3]=m_
        c=sm
        # seat the head: lowest chin row overlaps the torso top by 2 rows (no floating gap)
        ch_rows=np.where(head[...,3].any(1))[0]; chin_y=ch_rows.max()
        chin_cols=[i for i in range(Wh) if head[chin_y,i,3]]
        cx0,cx1=min(chin_cols)+dx,max(chin_cols)+dx
        bt=[j for j in range(c.shape[0]) if c[j,max(0,cx0):cx1+1,3].any() and j>chin_y+hy-12]
        if bt: hy=bt[0]-chin_y+1
        # the donor's chin can leak out beside the neck: clear body light/white just below my chin
        ly=chin_y+hy
        for j in range(max(0,ly-8),min(c.shape[0],ly+6)):
            for i in range(c.shape[1]):
                if c[j,i,3] and tuple(c[j,i,:3]) in (P['light'],P['white']): c[j,i,3]=0
        bt=[j for j in range(c.shape[0]) if c[j,max(0,cx0):cx1+1,3].any() and j>chin_y+hy-12]
        if bt: hy=bt[0]-chin_y+2                       # re-seat on what's left: chin overlaps the torso
        # my head on top
        for j in range(Hh):
            for i in range(Wh):
                if head[j,i,3]:
                    y,x=j+hy,i+dx
                    if 0<=y<c.shape[0] and 0<=x<c.shape[1]: c[y,x]=head[j,i]
        c=keep_main(c); c=fill_small_holes(c); c=despeck(c)
        out[f]=c
    # common canvas: feet on the bottom row for every grounded frame
    CW=max(q.shape[1] for q in out.values()); CH=max(q.shape[0] for q in out.values())
    for f in FR:
        q=out[f]; p=np.zeros((CH,CW,4),np.int32); p[CH-q.shape[0]:,:q.shape[1]]=q; out[f]=p
    ys={f:np.where(out[f][...,3].any(1))[0] for f in FR}
    xs={f:np.where(out[f][...,3].any(0))[0] for f in FR}
    hmax=max(ys[f].max()-ys[f].min()+1 for f in FR)
    x0=min(xs[f].min() for f in FR); x1=max(xs[f].max() for f in FR)+1
    final={}
    for f in FR:
        q=out[f][:,x0:x1]; yb=ys[f].max()
        g=np.zeros((hmax+ (6 if f=='jump' else 0) if False else hmax,x1-x0,4),np.int32)
        hh=g.shape[0]
        src=q[max(0,yb-hh+1):yb+1]
        g[hh-src.shape[0]:]=src
        final[f]=g
    for f,q in final.items(): save(q,f'{m}_{f}')
    return {f:(dx) for f in FR}

if __name__=='__main__':
    for m in MICE: build(m); print(m,'ok')
