from lib import *
import lib
from PIL import Image
PAL=np.array([[252,240,155],[115,190,72],[245,174,40],[204,71,106],[177,224,240],[149,19,55],[166,59,92],[190,51,90],[31,3,9],[1,1,1],[96,110,214],[203,173,178],[250,250,250],[179,26,68],[138,189,208],[209,46,92]],float)
def bg_boss(c):
    r,g,b=c; mx,mn=max(c),min(c)
    if b-r>100 and g>200: return True
    if g>r+40 and g>b+15 and r<120: return True
    if b-r>12 and g-r>8 and mx<150: return True
    if r>200 and g>200 and b<110: return True
    return False
def base():
    a=load(1103).copy();b=load(1102)
    a[1000:1400,1680:1920]=b[1000:1400,1680:1920]
    star=(a[...,0]>200)&(a[...,1]>200)&(a[...,2]<100); a[star]=b[star]
    return a
BOX=(1070,620,1915,1335)
def build(a,name):
    lib._cache[name]=a
    arr,g=sample(name,BOX,g=gridfixed(1103,BOX,P0/2),core=0.25)
    fg=matte(arr,bg_boss)
    q,_=quant(arr,fg,pal=PAL); q=despeckle(q.astype(np.int32)).astype(np.uint8)
    # NOTE: no crop -> both variants share identical frame/anchor
    return q
angry=build(base(),'b_angry')
S=1.55
a=base(); src=load(1105)
X0,Y0,X1,Y1=900,860,1420,1100
patch=np.asarray(Image.fromarray(src[Y0:Y1,X0:X1].astype(np.uint8)).resize((int((X1-X0)/S),int((Y1-Y0)/S)),Image.NEAREST)).astype(float)
tx=int(round(1525+(X0-1296)/S)); ty=int(round(693+(Y0-722)/S))
sky=(patch[...,2]-patch[...,0]>100)
reg=a[ty:ty+patch.shape[0],tx:tx+patch.shape[1]]; reg[~sky]=patch[~sky]
sad=build(a,'b_sad')
# common crop
al=(angry[...,3]>0)|(sad[...,3]>0); ys,xs=np.where(al)
for q,n in((angry,'boss_angry'),(sad,'boss_sad')):
    save(q[ys.min():ys.max()+1,xs.min():xs.max()+1],n)
print('ok')
