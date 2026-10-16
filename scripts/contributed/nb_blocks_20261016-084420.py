# Blocks for state/nbedit: per exported BO4 model, its named neighbours -- named models that share its named
# materials (most shared first), then known names that begin with one of its own >=3-token core prefixes --
# and a vocabulary of every token seen at least twice across all named BO4 assets (all pools).
# usage: py contrib/bo4_models/nb_blocks.py PKL OUT [--validate] [nb=60] [expand=1]
import json,re,collections,pickle,sys
d=pickle.load(open(sys.argv[1],"rb")); named=d["named"]["xmodel"]; M=(1<<63)-1
A=dict(a.split("=",1) for a in sys.argv[3:] if "=" in a); NB=int(A.get("nb",60)); EXP=int(A.get("expand",0))
VAL="--validate" in sys.argv
un=json.load(open("state/bo4exp/unnamed_models.json")); tr=json.load(open("state/bo4exp/train.json"))
def h(s):
    x=0xCBF29CE484222325
    for c in s.encode(): x=((x^c)*0x100000001B3)&0xFFFFFFFFFFFFFFFF
    return x&M
mats={}
for n,v in tr: mats[h(n)]=v
for k,v in un.items(): mats[int(k,16)]=v
if VAL: items=[x for x in mats if x in named]
else: items=[x for x in mats if x not in named]
def cores(v):
    out=set()
    for mat,imgs in v.items():
        if not mat.startswith("material_"): out.add(re.sub(r"^(mtl_|mc/|ml/)","",mat))
        for i in imgs:
            if i.startswith(("$","ximage_","image_")): continue
            c=re.sub(r"^i_","",i); c=re.sub(r"^mtl_","",c); c=re.sub(r"_[a-z]{1,3}$","",c); out.add(c)
    res=set()
    for c in out:
        c=c.split("/")[-1]; res.add(c)
        m=re.match(r"t([78])_(.*)",c)
        if m: res.add("p%s_%s"%m.groups())
    return res
inv=collections.defaultdict(set)
for x,v in mats.items():
    if x in named:
        for m in v:
            if not m.startswith("material_") and m!="global_invisible": inv[m].add(x)
byp=collections.defaultdict(list)
for x,n in named.items():
    t=n.split("/")[-1].split("_")
    for k in range(3,len(t)): byp["_".join(t[:k])].append(n)
cnt=collections.Counter()
for ns in d["allnames"].values():
    for s in ns: cnt.update(t for t in re.split(r"[_/]",s.lower()) if t)
held=set(items) if VAL else set()
V=sorted(t for t,c in cnt.items() if c>=2 and len(t)<=24)
open(sys.argv[2]+".vocab","w").write("\n".join(V)+"\n")
out=open(sys.argv[2],"w"); nb=0; tn=0
for x in items:
    v=mats[x]
    c=collections.Counter(y for m in v for y in inv.get(m,()) if y!=x)
    N=[named[y] for y,_ in c.most_common(NB)]
    if len(N)<NB:
        seen=set(N)
        for p in sorted(cores(v),key=len,reverse=True):
            t=p.split("_")
            for k in range(len(t),2,-1):
                for n in byp.get("_".join(t[:k]),())[:20]:
                    if n not in seen and h(n)!=x: seen.add(n); N.append(n)
                if len(N)>=NB: break
            if len(N)>=NB: break
    if not N: continue
    N=N[:NB]
    if EXP:   # expand=1: also every one-token deletion and every number shifted by 1-3 (two-edit reach)
        X=dict.fromkeys(N)
        for n in N:
            dd,_,b=n.rpartition("/"); dd=dd+"/" if dd else ""; t=b.split("_")
            for i in range(2,len(t)): X[dd+"_".join(t[:i]+t[i+1:])]=None
            for i in range(2,len(t)):
                m=re.fullmatch(r"(\d+)([a-z]?)",t[i])
                if m:
                    v=int(m.group(1)); w=len(m.group(1))
                    for dv in (-3,-2,-1,1,2,3):
                        if v+dv>=0: X[dd+"_".join(t[:i]+[str(v+dv).zfill(w)+m.group(2)]+t[i+1:])]=None
        N=[n for n in X if h(n)!=x]
    out.write("#I %x\n"%x+"\n".join(N)+"\n"); nb+=1; tn+=len(N)
out.close()
if VAL: open(sys.argv[2]+".truth","w").write("\n".join(named[x] for x in items)+"\n")
print("blocks",nb,"avg nb",tn//max(nb,1),"vocab",len(V))
