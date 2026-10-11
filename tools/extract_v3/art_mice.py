"""Mouse Squad — hand-finished gameplay mice.
Source: the crisp select-screen art at its true grid (1 art px = 6.146 screen px).
Every edit below is a deliberate pixel decision; re-run to rebuild the frames."""
import numpy as np
from PIL import Image
from collections import Counter
A='/tmp/ms/x/art/'
def load(n): return np.asarray(Image.open(A+n+'.png').convert('RGBA')).astype(np.int32).copy()
def save(q,n): Image.fromarray(np.clip(q,0,255).astype(np.uint8)).save(A+n+'.png')
N4=((1,0),(-1,0),(0,1),(0,-1)); N8=N4+((1,1),(1,-1),(-1,1),(-1,-1))
def op(q,i,j): return 0<=j<q.shape[0] and 0<=i<q.shape[1] and q[j,i,3]>0
def col(q,i,j): return tuple(q[j,i,:3])
def setp(q,i,j,c): q[j,i,:3]=c; q[j,i,3]=255
def clear(q,i,j): q[j,i,3]=0

def despeck(q, keep=(), thin_ok=False):
    """isolated pixels -> neighbour majority; edge specks -> removed"""
    H,W=q.shape[:2]; out=q.copy()
    for j in range(H):
        for i in range(W):
            if not op(q,i,j): continue
            c=col(q,i,j)
            if c in keep: continue
            nb=[col(q,i+a,j+b) for a,b in N4 if op(q,i+a,j+b)]
            n8=sum(op(q,i+a,j+b) for a,b in N8)
            if n8<=(0 if thin_ok else 2): clear(out,i,j); continue
            if c not in nb and len(nb)>=3:
                m,k=Counter(nb).most_common(1)[0]
                if k>=2: out[j,i,:3]=m
                elif len(nb)<4 and not thin_ok: clear(out,i,j)
    return out
def edge_black_specks(q, black):
    H,W=q.shape[:2]; out=q.copy()
    for j in range(H):
        for i in range(W):
            if op(q,i,j) and col(q,i,j)==black:
                edge=any(not op(q,i+a,j+b) for a,b in N4)
                same=sum(op(q,i+a,j+b) and col(q,i+a,j+b)==black for a,b in N8)
                if edge and same<=2: clear(out,i,j)
    return out
def ear_rims(q, ear, rim):
    """the source ears have a 1px fur-coloured rim; rebuild it where it was lost"""
    H,W=q.shape[:2]; add=[]
    for j in range(H):
        for i in range(W):
            if op(q,i,j) and col(q,i,j)==ear:
                for a,b in N8:
                    x,y=i+a,j+b
                    if 0<=x<W and 0<=y<H and not op(q,x,y): add.append((x,y))
    for x,y in add: setp(q,x,y,rim)
    return q
def erase_path(q, pts, r=1.6, guard=None):
    H,W=q.shape[:2]
    for j in range(H):
        for i in range(W):
            if not op(q,i,j) or (guard and guard(i,j)): continue
            for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
                dx,dy=x1-x0,y1-y0; t=max(0,min(1,((i-x0)*dx+(j-y0)*dy)/max(dx*dx+dy*dy,1e-9)))
                if (x0+t*dx-i)**2+(y0+t*dy-j)**2<=r*r: clear(q,i,j); break
    return q
def keep_main(q, minfrac=0.03):
    """drop floating fragments (tail remnants, specks) not attached to the body"""
    from collections import deque
    H,W=q.shape[:2]; lab=np.zeros((H,W),int); k=0; sizes={}
    for j in range(H):
        for i in range(W):
            if op(q,i,j) and not lab[j,i]:
                k+=1; dq=deque([(i,j)]); lab[j,i]=k; n=0
                while dq:
                    a,b=dq.popleft(); n+=1
                    for da,db in N8:
                        x,y=a+da,b+db
                        if 0<=x<W and 0<=y<H and op(q,x,y) and not lab[y,x]: lab[y,x]=k; dq.append((x,y))
                sizes[k]=n
    big=max(sizes,key=sizes.get)
    for j in range(H):
        for i in range(W):
            if lab[j,i] and sizes[lab[j,i]]<sizes[big]*minfrac: clear(q,i,j)
    return q
def redraw_glasses(q, purple, white, face, bridge_x, ytop, ybot):
    global LENS
    """replace aliased dashed rims with continuous 1px ellipses fitted to each lens"""
    H,W=q.shape[:2]
    pts=[(i,j) for j in range(ytop,ybot) for i in range(W) if op(q,i,j) and col(q,i,j)==purple]
    lens=LENS
    inside=lambda i,j:any(((i+.5-cx)/rx)**2+((j+.5-cy)/ry)**2<1 for cx,cy,rx,ry in lens)
    # 1) wipe old rim pixels (keep temple tips beyond the lenses)
    for (i,j) in pts:
        if any(abs(((i+.5-cx)/rx)**2+((j+.5-cy)/ry)**2-1)<0.6 for cx,cy,rx,ry in lens) or inside(i,j):
            q[j,i,:3]=white if inside(i,j) else face
    # 2) draw continuous rims
    for cx,cy,rx,ry in lens:
        for j in range(int(cy-ry-2),int(cy+ry+3)):
            for i in range(int(cx-rx-2),int(cx+rx+3)):
                if not(0<=i<W and 0<=j<H): continue
                d=((i+.5-cx)/rx)**2+((j+.5-cy)/ry)**2
                # pixel-perfect ring: inside the outer edge, outside the inner edge
                if d<=1 and ((i+.5-cx)/max(rx-1,1))**2+((j+.5-cy)/max(ry-1,1))**2>1 and op(q,i,j):
                    if col(q,i,j)!=(26,26,26): q[j,i,:3]=purple
    # 3) bridge between the lenses at eye height
    by=int(round((lens[0][1]+lens[1][1])/2))
    for i in range(int(lens[0][0]+lens[0][2])-1,int(lens[1][0]-lens[1][2])+2):
        for j in (by-1,by):
            if op(q,i,j): q[j,i,:3]=purple
    return lens
def near(c,d,tol=14): return sum(abs(int(a)-int(b)) for a,b in zip(c,d))<=tol
def recolor(q, frm, to, region=lambda i,j:True):
    H,W=q.shape[:2]
    for j in range(H):
        for i in range(W):
            if op(q,i,j) and near(col(q,i,j),frm) and region(i,j): q[j,i,:3]=to
    return q

# ---------- leg painter ----------
def seg_fill(c, pts, r, color):
    H,W=c.shape[:2]
    for j in range(H):
        for i in range(W):
            for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
                dx,dy=x1-x0,y1-y0; t=max(0,min(1,((i+.5-x0)*dx+(j+.5-y0)*dy)/max(dx*dx+dy*dy,1e-9)))
                if (x0+t*dx-i-.5)**2+(y0+t*dy-j-.5)**2<=r*r: setp(c,i,j,color); break
def foot(c, x, y, L, h, color, sole, tilt=0):
    """rounded mouse foot pointing right (+x); (x,y)=heel bottom"""
    H,W=c.shape[:2]
    cx,cy=x+L/2-1, y-h/2
    for j in range(H):
        for i in range(W):
            u=(i+.5-cx)/(L/2); v=(j+.5-cy+ (i+.5-x)*tilt)/(h/2)
            if u*u+v*v<=1: setp(c,i,j, sole if (j+.5)>cy+h*0.22 and u>-0.6 else color)
def leg(c, hip, knee, ankle, r, color, sole, L, h, tilt=0):
    seg_fill(c,[hip,knee,ankle] if knee else [hip,ankle],r,color)
    foot(c,ankle[0]-r*0.6,ankle[1]+r*0.6,L,h,color,sole,tilt)

def shade(c,k): return tuple(max(0,int(v*k)) for v in c)

def build(name, torso, cx, hip, LL, R, FL, FH, fur, tail_anchor, extra=None):
    """torso: cleaned art with legs removed. returns dict of frames"""
    H0,W0=torso.shape[:2]
    G=hip+LL                              # ground (sole) row
    W=max(W0,cx+int(0.5*LL)+FL+2); H=G+1
    near=fur; far=shade(fur,0.78); sole=shade(fur,0.72); fsole=shade(fur,0.6)
    s=LL; GA=G-R*0.6                   # ankle height for a planted foot
    P={  # (near:(knee,ankle,tilt), far:(...), bob)
     'idle': (((None),(cx+3,GA)),((None),(cx-3,GA)),0,(0,0)),
     'w1':   ((None,(cx+0.42*s,GA)),(None,(cx-0.42*s,GA-1)),0,(0,0.12)),
     'w2':   (((cx+0.30*s,hip+0.50*s),(cx+0.08*s,GA-0.30*s)),(None,(cx-1,GA)),-1,(0.08,0)),
     'w3':   ((None,(cx-0.42*s,GA-1)),(None,(cx+0.42*s,GA)),0,(0.12,0)),
     'w4':   ((None,(cx+1,GA)),((cx+0.26*s,hip+0.50*s),(cx+0.02*s,GA-0.30*s)),-1,(0,0.08)),
     'jump': (((cx+0.42*s,hip+0.38*s),(cx+0.12*s,hip+0.70*s)),((cx-0.05*s,hip+0.45*s),(cx-0.32*s,hip+0.78*s)),0,(0.1,0.1)),
    }
    out={}
    for k,(nl,fl,bob,(tn,tf)) in P.items():
        c=np.zeros((H,W,4),np.int32)
        hn=(cx+R*0.9,hip-2); hf=(cx-R*0.9,hip-2)
        def L1(spec,h0,color,sl,tilt):
            if spec[0] is None or spec[0]==(None): kn=None
            else: kn=spec[0]
            leg(c,h0,kn,spec[1],R,color,sl,FL,FH,tilt)
        L1(fl if isinstance(fl,tuple) and len(fl)==2 else (None,fl),hf,far,fsole,tf)
        L1(nl if isinstance(nl,tuple) and len(nl)==2 else (None,nl),hn,near,sole,tn)
        # torso over the hips (with bob)
        for j in range(H0):
            for i in range(W0):
                if torso[j,i,3]>0:
                    y=j+bob
                    if 0<=y<H: c[y,i]=torso[j,i]
        if extra: extra(c,k,bob)
        out[k]=c
    return out

def crop_all(frames):
    """common crop so every frame shares one anchor (feet = bottom row)"""
    al=np.zeros(next(iter(frames.values())).shape[:2],bool)
    for f in frames.values(): al|=f[...,3]>0
    ys,xs=np.where(al); x0,x1=xs.min(),xs.max()+1
    return {k:f[:,x0:x1] for k,f in frames.items()}, x0

TAILS={}
def fill_holes(q):
    """transparent pockets fully enclosed by the sprite get the surrounding colour"""
    from collections import deque
    H,W=q.shape[:2]; out=np.zeros((H,W),bool); dq=deque()
    for j in range(H):
        for i in range(W):
            if (i in(0,W-1) or j in(0,H-1)) and not op(q,i,j): out[j,i]=True; dq.append((i,j))
    while dq:
        a,b=dq.popleft()
        for da,db in N4:
            x,y=a+da,b+db
            if 0<=x<W and 0<=y<H and not out[y,x] and not op(q,x,y): out[y,x]=True; dq.append((x,y))
    cand=set((i,j) for j in range(H) for i in range(W) if not op(q,i,j) and not out[j,i])
    holes=[]; seen=set()
    for st in list(cand):                    # only small pockets are flaws; big ones are real gaps
        if st in seen: continue
        comp=[st]; seen.add(st); dq2=deque([st])
        while dq2:
            a,b=dq2.popleft()
            for da,db in N4:
                n=(a+da,b+db)
                if n in cand and n not in seen: seen.add(n); comp.append(n); dq2.append(n)
        if len(comp)<=14: holes+=comp
    for _ in range(6):
        left=[]
        for (i,j) in holes:
            nb=[col(q,i+a,j+b) for a,b in N8 if op(q,i+a,j+b)]
            if nb: q[j,i,:3]=Counter(nb).most_common(1)[0][0]; q[j,i,3]=255
            else: left.append((i,j))
        holes=left
        if not holes: break
    return q
def finish(q,ear,rim,keep,thin_ok=False):
    q=fill_holes(q)
    q=keep_main(q,0.002 if thin_ok else 0.03); q=ear_rims(q,ear,rim); return despeck(q,keep=keep,thin_ok=thin_ok)
SEL={}
# ======================= PINK (glasses + bow) =======================
BLK=(26,26,26); FUR=(133,133,133); EAR=(255,183,177); LIGHT=(237,237,237); PUR=(111,52,149)
def pink_fix(p):
    p=edge_black_specks(p,BLK)
    recolor(p,PUR,FUR,lambda i,j:j>52)                       # purple specks on shoulder / hand
    recolor(p,EAR,LIGHT,lambda i,j:j>50 and 15<i<40)         # pink 'collar' line under the chin
    redraw_glasses(p,PUR,(255,255,255),LIGHT,22,28,52)
    return p
LENS=[(13.5,40.5,9.5,10.0),(34.5,41.0,12.0,10.0)]   # measured: left lens x4-22, right x22-46, rows 30-50
p=pink_fix(load('pink_raw'))
SEL['pink']=finish(p.copy(),EAR,FUR,{BLK,PUR,(255,255,255)},thin_ok=True)
p=erase_path(p,[(30,85),(40,83),(50,79),(58,75),(66,70),(75,68)],r=1.7,guard=lambda i,j:j<70 and i<45)   # baked tail
for j in range(77,p.shape[0]):
    for i in range(18,37): clear(p,i,j)
p=finish(p,EAR,FUR,{BLK,PUR,(255,255,255)})
fr=build('pink',p,29,77,15,3.0,10,5,FUR,None)
# ======================= CYAN (the boy) =======================
BLK=(26,26,26); FUR=(105,105,105); EAR=(239,183,177); LIGHT=(223,223,223)
c=edge_black_specks(load('cyan_raw'),BLK)
recolor(c,EAR,LIGHT,lambda i,j:(i<14 and 38<j<50) or (14<=i<60 and j>40))   # pink specks on cheek / chin
SEL['cyan']=finish(c.copy(),EAR,FUR,{BLK},thin_ok=True)
c=erase_path(c,[(53,93),(62,91),(70,86),(77,78),(83,71),(88,66),(92,65)],r=1.7)   # baked tail
for j in range(96,c.shape[0]):
    for i in range(12,62): clear(c,i,j)
c=finish(c,EAR,FUR,{BLK})
fc=build('cyan',c,31,96,21,4.0,13,6,FUR,None)
# ======================= YELLOW (headband) =======================
BLK=(27,27,27); FUR=(85,85,85); HAIR=(68,68,68); EAR=(255,191,196); LIGHT=(218,218,218); MAG=(216,68,184)
y=edge_black_specks(load('yellow_raw'),BLK)
recolor(y,MAG,HAIR,lambda i,j:i<26 and (j<4 or j>24))     # headband magenta bleeding into the ear rim
recolor(y,MAG,BLK,lambda i,j:44<=i<=56 and 38<=j<=43)      # magenta in the mouth line -> black
recolor(y,MAG,LIGHT,lambda i,j:j>=24 and i>=30)            # any other magenta on the face
recolor(y,EAR,LIGHT,lambda i,j:30<i<60 and 30<j<50)        # speck by the mouth
for (i,j) in ((46,42),(54,42)): setp(y,i,j,BLK)            # smile corners turn up
recolor(y,HAIR,FUR,lambda i,j:j>=46)                        # one body tone below the hair
SEL['yellow']=finish(y.copy(),EAR,HAIR,{BLK},thin_ok=True)
for j in range(44,y.shape[0]):                              # kicked leg + tail behind her
    for i in range(0,36): clear(y,i,j)
for j in range(68,y.shape[0]):                              # standing leg
    for i in range(30,56): clear(y,i,j)
y=finish(y,EAR,HAIR,{BLK})
def yellow_arm(c,k,bob):
    hand={'idle':(27,60),'w1':(24,58),'w2':(27,61),'w3':(31,61),'w4':(27,61),'jump':(23,52)}[k]
    sh=(36,50+bob); hx,hy=hand[0]+3,hand[1]+bob
    seg_fill(c,[sh,(hx,hy)],2.6,FUR)
    for j in range(c.shape[0]):
        for i in range(c.shape[1]):
            if (i+.5-hx)**2+(j+.5-hy)**2<=2.9**2: setp(c,i,j,FUR)
fy=build('yellow',y,43,68,15,3.2,10,5,FUR,None,extra=yellow_arm)
# select-screen versions: concept pose kept, cleaned, shown at 2x
for k,q in SEL.items():
    al=q[...,3]>0; ys,xs=np.where(al); q=q[ys.min():ys.max()+1,xs.min():xs.max()+1]
    save(np.repeat(np.repeat(q,2,0),2,1),'sel_'+k)

meta={}
for name,frames,hip,cx in (('pink',fr,77,29),('cyan',fc,96,31),('yellow',fy,68,43)):
    frames,x0=crop_all(frames)
    for k,f in frames.items(): save(f,f'{name}_{k}')
    H=next(iter(frames.values())).shape[0]
    meta[name]={'tailX':int(cx-x0-4),'tailY':int(hip-4)}      # tail root: back of the hips
print(meta)
import json; json.dump(meta,open(A+'mice_meta.json','w'))
