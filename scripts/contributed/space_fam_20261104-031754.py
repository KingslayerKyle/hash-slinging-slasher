# dimpm blocks from map PLACEMENTS: per placed model id (own id only), heads = known prefixes (>=3 tokens) of the 3/4-token
# families of its K nearest named neighbours, V = neighbour tokens + family vocabulary, tails global (OUT.ends, GE=).
# input: nbedit-style blocks from space_nb.py ("#I hex" + neighbour names).
# usage: py space_fam.py PKL NBBLOCKS OUT [held=TRUTHFILE] [hcap=2000] [vcap=300]
import sys,collections,pickle
d=pickle.load(open(sys.argv[1],'rb')); named=d['named']['xmodel']
A=dict(a.split('=',1) for a in sys.argv[4:] if '=' in a); HCAP=int(A.get('hcap',2000)); VCAP=int(A.get('vcap',300))
held=set(open(A['held']).read().split()) if 'held' in A else set()
names=[n.split('/')[-1] for n in named.values() if n not in held]
HC=collections.defaultdict(collections.Counter); VC=collections.defaultdict(collections.Counter); T=collections.Counter()
for n in names:
    t=n.split('_')
    for j in range(1,min(5,len(t)-2)+1): T['_'+'_'.join(t[len(t)-j:])]+=1
    for k in (3,4):
        if len(t)<=k: continue
        F='_'.join(t[:k])
        for j in range(3,len(t)): HC[F]['_'.join(t[:j])]+=1
        VC[F].update(t[k:])
tails=[x for x,c in T.most_common() if len(x)<=61]
open(sys.argv[3]+'.ends','w').write('\n'.join(['-']+tails)+'\n')
out=open(sys.argv[3],'w'); nb=0
for b in open(sys.argv[2]).read().split('#I ')[1:]:
    L=[x for x in b.split('\n') if x]; k=L[0].strip(); N=[n for n in L[1:] if n not in held][:40]
    own=collections.Counter(); P=set(); fams=set()
    for s in N:
        t=s.split('_'); own.update(t[2:])
        for kk in (3,4):
            if len(t)>kk: fams.add('_'.join(t[:kk]))
        for j in range(3,len(t)): P.add('_'.join(t[:j]))
    hc=collections.Counter(); vc=collections.Counter()
    for F in fams:
        if F in HC: hc.update(HC[F]); vc.update(VC[F])
    P|={x for x,_ in hc.most_common(HCAP)}
    if not P: continue
    V=[t for t,_ in own.most_common()]; s=set(V); V+=[t for t,_ in vc.most_common(VCAP) if t not in s]
    out.write('#I %s\n#P %s\n#V %s\n#D -\n#E @G\n'%(k,' '.join(sorted(P)),' '.join(V))); nb+=1
print('blocks',nb)
