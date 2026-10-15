# Per-model blocks for pm: prefixes = >=2-token cuts of the model's own material/image cores (t->p swap),
# vocab = the model's own core tokens first, then numbers, then the top global model tokens.
# usage: py blocks.py OUT [--validate] [gtop=300]
import json,re,collections,pickle,sys,glob
S=r"C:/Users/helto/AppData/Local/Temp/claude/F--Claude-Code/467e9ad6-6b43-48e4-beb8-3300a86f3f1d/scratchpad"
d=pickle.load(open(S+"/bo4.pkl","rb")); M=(1<<63)-1
def h(s):
    x=0xCBF29CE484222325
    for c in s.encode(): x=((x^c)*0x100000001B3)&0xFFFFFFFFFFFFFFFF
    return x&M
VAL="--validate" in sys.argv
GTOP=int(([a[5:] for a in sys.argv if a.startswith("gtop=")] or ["300"])[0])
ids=d["pools"]["xmodel"]; known=set(d["named"]["xmodel"].values())
for f in glob.glob("state/famedit/found*.txt")+glob.glob("state/pm/found*.txt"):
    for l in open(f,encoding="utf-8"):
        n=l.strip()
        if n: known.add(n)
tr=json.load(open("state/bo4exp/train.json")); un=json.load(open("state/bo4exp/unnamed_models.json"))
sys.path.insert(0,"state/famedit")
def cores(v):
    out=set()
    for mat,imgs in v.items():
        if not mat.startswith("material_"): out.add(re.sub(r"^(mtl_|mc/|ml/)","",mat))
        for i in imgs:
            if i.startswith("$") or i.startswith("ximage_") or i.startswith("image_"): continue
            c=re.sub(r"^i_","",i); c=re.sub(r"^mtl_","",c); c=re.sub(r"_[a-z]{1,3}$","",c); out.add(c)
    res=set()
    for c in out:
        c=c.split("/")[-1]; res.add(c)
        m=re.match(r"t([78])_(.*)",c)
        if m: res.add("p%s_%s"%m.groups())
    return res
if VAL:
    trn=set(n for n,v in tr); known-=trn; items=[(h(n),v) for n,v in tr]; tids=set(h(n) for n in trn)
else:
    kh=set(h(n) for n in known); items=[(int(k,16),v) for k,v in un.items() if int(k,16) not in kh]; tids=ids-kh
GT=[t for t,_ in collections.Counter(t for n in known for t in n.split("/")[-1].split("_")).most_common(GTOP)]
NUM=["%02d"%i for i in range(0,13)]+[str(i) for i in range(1,6)]+list("abc")
out=open(sys.argv[1],"w")
for x,v in items:
    C=cores(v)
    if not C: continue
    P=set(); own=collections.Counter()
    for c in C:
        t=c.split("_"); own.update(t)
        for k in range(2,len(t)+1): P.add("_".join(t[:k]))
    V=[t for t,_ in own.most_common()]; s=set(V)
    V+=[t for t in NUM if t not in s]; s|=set(NUM)
    V+=[t for t in GT if t not in s]
    out.write("#P "+" ".join(sorted(P))+"\n#V "+" ".join(V)+"\n")
out.close()
open(sys.argv[1]+".ids","w").write("\n".join("%x"%i for i in tids)+"\n")
print("models",len(items),"targets",len(tids))
