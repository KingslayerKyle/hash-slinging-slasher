# Build family groups for famedit from the BO4 Saluki export index.
# usage: py groups.py OUT [--validate]   (validate: drop the exported named models from known, target their ids)
import json,re,collections,pickle,sys,glob
S=r"C:/Users/helto/AppData/Local/Temp/claude/F--Claude-Code/467e9ad6-6b43-48e4-beb8-3300a86f3f1d/scratchpad"
d=pickle.load(open(S+"/bo4.pkl","rb"))
M=(1<<63)-1
def h(s):
    x=0xCBF29CE484222325
    for c in s.encode(): x=((x^c)*0x100000001B3)&0xFFFFFFFFFFFFFFFF
    return x&M
VAL="--validate" in sys.argv
ids=d["pools"]["xmodel"]
known=set(d["named"]["xmodel"].values())
for f in glob.glob("state/famedit/found*.txt")+glob.glob("findings/blkops04/**/xmodel.txt",recursive=True):
    for l in open(f,encoding="utf-8"):
        n=l.strip().split(",")[-1].lower()
        if n and h(n) in ids: known.add(n)
tr=json.load(open("state/bo4exp/train.json"))
un=json.load(open("state/bo4exp/unnamed_models.json"))
if VAL:
    targets=[v for n,v in tr]; trn=set(n for n,v in tr); known-=trn
    tids=set(h(n) for n in trn)
else:
    targets=[v for k,v in un.items() if int(k,16) not in {h(n) for n in []}]
    tids=ids-set(h(n) for n in known)
def cores(v):
    out=set()
    for mat,imgs in v.items():
        if not mat.startswith("material_"): out.add(re.sub(r"^(mtl_|mc/|ml/|mtl_)","",mat))
        for i in imgs:
            if i.startswith("$") or i.startswith("ximage_"): continue
            c=re.sub(r"^i_","",i); c=re.sub(r"^mtl_","",c); c=re.sub(r"_[a-z]{1,3}$","",c); out.add(c)
    res=set()
    for c in out:
        c=c.split("/")[-1]; res.add(c)
        m=re.match(r"t([78])_(.*)",c)
        if m: res.add("p%s_%s"%m.groups())
    return res
fam=collections.defaultdict(set)
for n in known:
    t=n.split("/")[-1].split("_")
    for k in range(2,len(t)): fam["_".join(t[:k])].add(n)
CAP=int(dict(a.split("=") for a in sys.argv if a.startswith("cap=")).get("cap",400)) if any(a.startswith("cap=") for a in sys.argv) else 400
G=collections.defaultdict(set)   # family -> extra vocab from cores
for v in targets:
    C=cores(v); ct=set(t for c in C for t in c.split("_"))
    for c in C:
        t=c.split("_"); ks=[k for k in range(len(t),2,-1) if 0<len(fam.get("_".join(t[:k]),()))<=CAP]
        for k in ks[:2]: G["_".join(t[:k])]|=ct
NUM=["%02d"%i for i in range(0,21)]+[str(i) for i in range(0,11)]+list("abcdef")
out=open(sys.argv[1],"w")
for F,extra in G.items():
    names=sorted(fam[F]); cnt=collections.Counter(t for n in names for t in n.split("_"))
    for t in extra: cnt[t]+=0.5
    V=[t for t,_ in cnt.most_common()]
    V+= [x for x in NUM if x not in cnt]
    out.write("#V "+" ".join(V)+"\n"); out.write("\n".join(names)+"\n")
out.close()
open(sys.argv[1]+".ids","w").write("\n".join("%x"%i for i in tids)+"\n")
print("groups",len(G),"names",sum(len(fam[F]) for F in G),"targets",len(tids))
