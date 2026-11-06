# H _new [_E]: every known head x one new token x every known 1-3 token tail (or none), ids peeled. numpy.
import pickle,sys,collections,numpy as np
d=pickle.load(open(sys.argv[1],'rb')); V=[l.strip() for l in open(sys.argv[2]) if l.strip()]
POOL=sys.argv[4] if len(sys.argv)>4 else 'xmodel'
OFF,PR,M=0xCBF29CE484222325,0x100000001B3,(1<<64)-1; PINV=pow(PR,-1,1<<64)
named=set(d['named'][POOL].values()); ids=sorted(d['pools'][POOL]-set(d['named'][POOL]))
heads=collections.Counter(); tails=collections.Counter()
for n in named:
    t=n.split('_')
    for i in range(1,len(t)): heads['_'.join(t[:i])]+=1
    for i in range(1,min(4,len(t))): tails['_'.join(t[-i:])]+=1
H=list(heads); E=['']+[k for k,_ in tails.most_common(int(sys.argv[5]) if len(sys.argv)>5 else 20000)]
def st(h,s):
    for c in s.encode(): h=((h^c)*PR)&M
    return h
def un(h,s):
    for c in reversed(s.encode()): h=((h*PINV)&M)^c
    return h
idn=np.array(ids,dtype=np.uint64); idn=np.concatenate([idn,idn|np.uint64(1<<63)])
PI=np.uint64(PINV); parts=[]
with np.errstate(over='ignore'):
    for e in E:
        h=idn.copy()
        for c in reversed(('_'+e).encode() if e else b''): h=(h*PI)^np.uint64(c)
        parts.append(h)
keys=np.unique(np.concatenate(parts)); del parts
Hh=np.array([st(OFF,h) for h in H],dtype=np.uint64)
idset=set(ids)
print('H',len(H),'V',len(V),'E',len(E),'chance %.3f'%(len(H)*len(V)*len(keys)/2**64),file=sys.stderr)
out=open(sys.argv[3],'w');n=0
with np.errstate(over='ignore'):
    for w in V:
        h=Hh.copy()
        for c in ('_'+w).encode(): h=(h^np.uint64(c))*np.uint64(PR)
        pos=np.searchsorted(keys,h); pos[pos>=len(keys)]=0
        for j in np.nonzero(keys[pos]==h)[0]:
            for e in E:
                nm=H[j]+'_'+w+('_'+e if e else ''); x=st(OFF,nm)&((1<<63)-1)
                if x in idset: out.write('%s,%x\n'%(nm,x)); n+=1
print('hits',n,file=sys.stderr)
