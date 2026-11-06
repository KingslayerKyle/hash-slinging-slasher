# Co-located placements (same origin within 0.5 units): how named pairs relate, and the named partners of unnamed ids.
# usage: py coloc.py PKL "place_*.tsv" OUT.txt   (OUT: "#I hex" blocks of co-located named partners, nbedit format)
import sys,glob,collections,pickle,re
d=pickle.load(open(sys.argv[1],'rb')); pool=d['pools']['xmodel']; named=d['named']['xmodel']
M=(1<<63)-1; M60=(1<<60)-1; m60={i&M60:i for i in pool}
def h(s):
    x=0xCBF29CE484222325
    for c in s.encode(): x=((x^c)*0x100000001B3)&0xFFFFFFFFFFFFFFFF
    return x&M
rel=collections.Counter(); part=collections.defaultdict(collections.Counter); npairs=0
for f in glob.glob(sys.argv[2]):
    cell=collections.defaultdict(set)
    for l in open(f,encoding='utf-8'):
        p=l.rstrip('\n').split('\t')
        try: o=tuple(round(float(x)*2) for x in p[2].split())
        except: continue
        m=p[1]
        x=m60.get(int(m[7:],16)&M60) if m.startswith('xmodel_') else h(m)
        if x is None or x not in pool: continue
        cell[o].add(x)
    for o,xs in cell.items():
        if len(xs)<2 or len(xs)>8: continue
        for a in xs:
            for b in xs:
                if a==b or b not in named: continue
                if a in named:
                    A=named[a]; B=named[b]; npairs+=1
                    if A.startswith(B+'_'): rel['A=B+'+A[len(B)+1:].split('_')[0]]+=1
                    elif A.rsplit('_',1)[0]==B.rsplit('_',1)[0]: rel['last-token sibling']+=1
                    elif A.split('_')[:3]==B.split('_')[:3]: rel['same 3-prefix']+=1
                    else: rel['other']+=1
                else: part[a][named[b]]+=1
print('named pairs',npairs); print(rel.most_common(25))
print('unnamed ids with co-located named partner',len(part))
out=open(sys.argv[3],'w')
for x,c in part.items(): out.write('#I %x\n'%x+'\n'.join(n for n,_ in c.most_common(20))+'\n')
