# hwt lists for any BO4 pool (material, image, xanim, xmodel): head [_word] _tail against that pool's unnamed ids.
# head = every >=2-token prefix of a known name of the pool (directory kept, e.g. mc/mtl_p8_zm), word = BO4 tokens seen
# >= 2 times (+ bi=N known 2-token runs of the pool), tail = 1-5 token suffixes of the pool's known names (>= tmin).
# Global form: expected chance hits = cands x ids / 2^63 (printed) -- keep it under ~1 and read the new names.
# usage: py contrib/bo4_models/hwt_pool_prep.py PKL POOL OUTDIR [bi=0] [tmin=1] [hmin=1]
import re,collections,pickle,sys,os
d=pickle.load(open(sys.argv[1],"rb")); POOL=sys.argv[2]; O=sys.argv[3]
A=dict(a.split("=",1) for a in sys.argv[4:] if "=" in a); BI=int(A.get("bi",0)); TMIN=int(A.get("tmin",1)); HMIN=int(A.get("hmin",1))
named=d["named"][POOL]; ids=sorted(d["pools"][POOL]-set(named))
H=collections.Counter(); T=collections.Counter(); bc=collections.Counter()
for n in named.values():
    dd,_,b=n.rpartition("/"); dd=dd+"/" if dd else ""; t=b.split("_")
    for j in range(2,len(t)): H[dd+"_".join(t[:j])]+=1
    for j in range(1,min(5,len(t)-2)+1): T["_".join(t[len(t)-j:])]+=1
    for i in range(2,len(t)-1): bc[t[i]+"_"+t[i+1]]+=1
tc=collections.Counter()
for ns in d["allnames"].values():
    for nn in ns: tc.update(t for t in re.split(r"[_/]",nn.lower()) if t)
words={t for t,c in tc.items() if c>=2 and len(t)<=24}
if BI: words|={b for b,c in bc.items() if c>=BI and len(b)<=32}
heads=sorted(x for x,c in H.items() if c>=HMIN and len(x)<=90); tails=sorted(x for x,c in T.items() if c>=TMIN and len(x)<=60)
os.makedirs(O,exist_ok=True)
for f,L in (("ids",["%x"%x for x in ids]),("heads",heads),("words",sorted(words)),("tails",tails)): open(O+"/%s.txt"%f,"w").write("\n".join(L)+"\n")
c=len(heads)*(len(words)+1)*len(tails)
print(POOL,"ids",len(ids),"heads",len(heads),"words",len(words),"tails",len(tails),"cands %.2e"%c,"exp chance %.2f"%(c*len(ids)/2**63))
