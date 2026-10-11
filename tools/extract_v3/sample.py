import numpy as np
from PIL import Image
U='/sessions/sharp-brave-hypatia/mnt/uploads/'
FR=['idle','w1','w2','w3','w4','jump']
SHEETS={
 'pink':{'file':'yellow.jpeg','W':74,'H':93,'y0':31,
         'panels':[(0,724),(762,1488),(1525,2251),(2288,3014),(3051,3775),(3812,4602)],'uniform':True},
 'cyan':{'file':'cyan.jpeg','W':89,'H':118,'y0':30,
         'panels':[(0,726),(758,1482),(1515,2227),(2256,2935),(2960,3680),(3696,4408)],'uniform':False},
}
BG=[(255,214,240),(230,190,215),(200,120,170),(245,200,228),(220,170,200)]
def sample(m):
    S=SHEETS[m]; im=np.asarray(Image.open(U+S['file']).convert('RGB')).astype(float)
    Himg=im.shape[0]; ph=(Himg-S['y0'])/S['H']
    base=(S['panels'][0][1]-S['panels'][0][0])/S['W']
    out={}
    for f,(x0,x1) in zip(FR,S['panels']):
        pw=base if S['uniform'] else (x1-x0)/S['W']
        cols=int(round((x1-x0)/pw))
        arr=np.zeros((S['H'],cols,3)); bg=np.zeros((S['H'],cols),bool)
        for j in range(S['H']):
            for i in range(cols):
                cx=x0+(i+.5)*pw; cy=S['y0']+(j+.5)*ph
                r=max(1,int(min(pw,ph)*0.22))
                p=im[int(cy)-r:int(cy)+r+1,int(cx)-r:int(cx)+r+1].reshape(-1,3)
                c=np.median(p,0); arr[j,i]=c
                r_,g_,b_=c
                bg[j,i]=((r_-g_>22 and b_-g_>12 and g_>158) or               # pink sheet background / light grid
                         sum(abs(c-np.array((200,120,170))))<40)            # dark grid line
        out[f]=(arr,bg)
    return out
if __name__=='__main__':
    for m in SHEETS:
        o=sample(m)
        for f,(arr,bg) in o.items():
            q=np.zeros(arr.shape[:2]+(4,),np.uint8); q[...,:3]=np.clip(arr,0,255); q[...,3]=(~bg)*255
            Image.fromarray(q).save(f'/tmp/ms/ref/{m}_{f}_raw.png')
        print(m,{f:o[f][0].shape[:2] for f in o})
