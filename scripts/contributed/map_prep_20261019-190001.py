# Lists for state/hwt from the user's per-map BO4 model lists (F:\Claude Code\bo4_maplists\<map>.log, sorted by id,
# one sorted run per zone file):  head [_w1[_w2]] _tail  over the unnamed ids of the given maps only.
# map-specific = in at most MAXMAPS of all lists (drops the common zones every map loads).
# head = every >=2-token prefix of a map-specific known name; words = map tokens (count >= wmin) + pairs of the top
# PAIRS map tokens; tails = every 1-5 token suffix of map names + the top GT global model tails.
# --validate holds out a random 20% of the maps' named map-specific models (ids = theirs, lists rebuilt without them).
# hold=FILE (idhex per line) holds out exactly those ids instead; gw=FILE adds global single words.
# usage: py contrib/bo4_models/map_prep.py PKL OUTDIR map1[,map2..] [--validate] [maxmaps=2] [wmin=1] [pairs=1000]
#        [gt=20000] [hmin=1]
import pickle,sys,os,glob,collections,random
d=pickle.load(open(sys.argv[1],"rb")); named=d["named"]["xmodel"]; M=(1<<63)-1; O=sys.argv[2]; os.makedirs(O,exist_ok=True)
MAPS=sys.argv[3].split(","); A=dict(a.split("=",1) for a in sys.argv[4:] if "=" in a); VAL="--validate" in sys.argv
MAXM=int(A.get("maxmaps",2)); WMIN=int(A.get("wmin",1)); PAIRS=int(A.get("pairs",1000)); GT=int(A.get("gt",20000)); HMIN=int(A.get("hmin",1))
LD=r"F:\Claude Code\bo4_maplists"
def h(s):
    x=0xCBF29CE484222325
    for c in s.encode(): x=((x^c)*0x100000001B3)&0xFFFFFFFFFFFFFFFF
    return x&M
inmaps=collections.Counter(); mine=set()
for f in glob.glob(LD+r"\*.log"):
    m=os.path.basename(f)[:-4]; s=set()
    for l in open(f):
        n=l.strip().split(",",1)[1].lower()
        s.add(int(n[6:],16)&M if n.startswith("model_") else h(n))
    inmaps.update(s)
    if m in MAPS: mine|=s
spec={x for x in mine if inmaps[x]<=MAXM}
unn=d["pools"]["xmodel"]-set(named)
mapnamed=sorted(x for x in spec if x in named)
held=set()
if "hold" in A:
    held={int(l.split()[0],16)&M for l in open(A["hold"]) if l.strip()}; ids=sorted(held); VAL=True
elif VAL:
    random.seed(1); held=set(random.sample(mapnamed,len(mapnamed)//5)); ids=sorted(held)
else: ids=sorted(spec&unn)
mn=[named[x].split("/")[-1] for x in mapnamed if x not in held]
H=collections.Counter(); T=collections.Counter(); W=collections.Counter()
for n in mn:
    t=n.split("_")
    for j in range(2,len(t)): H["_".join(t[:j])]+=1
    for j in range(1,min(5,len(t)-2)+1): T["_".join(t[len(t)-j:])]+=1
    W.update(t[1:])
G=collections.Counter()
for x,n in named.items():
    if x in held: continue
    t=n.split("/")[-1].split("_")
    for j in range(1,min(5,len(t)-2)+1): G["_".join(t[len(t)-j:])]+=1
heads=[x for x,c in H.most_common() if c>=HMIN]
tails=[x for x,_ in T.most_common()]; ts=set(tails)
tails+=[x for x,_ in G.most_common(GT) if x not in ts]
top=[w for w,_ in W.most_common(PAIRS)]
words=[w for w,c in W.most_common() if c>=WMIN]
words+=[a+"_"+b for a in top for b in top]
if "gw" in A:
    ws=set(words); words+=[w for w in (l.strip() for l in open(A["gw"])) if w and w not in ws]
for nm,L in (("ids",["%x"%x for x in ids]),("heads",heads),("words",words),("tails",tails)):
    open(os.path.join(O,nm+".txt"),"w").write("\n".join(L)+"\n")
if VAL: open(os.path.join(O,"truth.txt"),"w").write("\n".join("%x\t%s"%(x,named[x]) for x in ids)+"\n")
fw=len(heads)*(1+len(words)); tb=len(ids)*len(tails)
print("maps",MAPS,"map-specific",len(spec),"named",len(mapnamed),"ids",len(ids),"heads",len(heads),"words",len(words),
      "tails",len(tails),"forward %.2e table %.2e exp chance %.3f"%(fw,tb,fw*tb*2/2**63))
