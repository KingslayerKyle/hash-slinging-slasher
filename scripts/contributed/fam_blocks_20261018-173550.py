# Blocks for state/dimpm (bin4): per exported BO4 model, checked only against its own id,
#   H [_w1 [_w2]] _tail
# families F = 3- and 4-token prefixes of its own material/image/bone cores (t->p) and of the named models that share
#   a named material with it (top NB);
# H  = every known model-name prefix (>= 3 tokens) inside those families, most common first, capped HCAP;
# V  = own core tokens + the tokens that follow F inside known names of those families, most common first, capped VCAP;
# tail = global: every 1-5 token suffix of a known model name (OUT.ends, run dimpm with GE=OUT.ends; "#E @G").
# usage: py contrib/bo4_models/fam_blocks.py PKL OUT [--validate] [hcap=2000] [vcap=300] [nb=30] [tmin=1]
import json,re,collections,pickle,sys
sys.path.insert(0,"contrib/bo4_models"); from bonecore import bone_cores
d=pickle.load(open(sys.argv[1],"rb")); named=d["named"]["xmodel"]; M=(1<<63)-1
A=dict(a.split("=",1) for a in sys.argv[3:] if "=" in a); VAL="--validate" in sys.argv
HCAP=int(A.get("hcap",2000)); VCAP=int(A.get("vcap",300)); NB=int(A.get("nb",30)); TMIN=int(A.get("tmin",1))
un=json.load(open("state/bo4exp/unnamed_models.json")); tr=json.load(open("state/bo4exp/train.json"))
B=json.load(open("state/bo4exp/bones.json"))
def h(s):
    x=0xCBF29CE484222325
    for c in s.encode(): x=((x^c)*0x100000001B3)&0xFFFFFFFFFFFFFFFF
    return x&M
mats={}
for n,v in tr: mats["%x"%h(n)]=v
mats.update(un)
if VAL: items=list(dict([("%x"%h(n),n) for n,v in tr]+[(k,named[int(k,16)]) for k in un if int(k,16) in named]).items())
else: items=[(k,None) for k in un if int(k,16) not in named]
held={int(k,16) for k,n in items} if VAL else set()
names=[n.split("/")[-1] for x,n in named.items() if x not in held]
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
HC=collections.defaultdict(collections.Counter); VC=collections.defaultdict(collections.Counter); T=collections.Counter()
for n in names:
    t=n.split("_")
    for j in range(1,min(5,len(t)-2)+1): T["_"+"_".join(t[len(t)-j:])]+=1
    for k in (3,4):
        if len(t)<=k: continue
        F="_".join(t[:k])
        for j in range(3,len(t)): HC[F]["_".join(t[:j])]+=1
        VC[F].update(t[k:])
tails=[x for x,c in T.most_common() if c>=TMIN and len(x)<=61]
open(sys.argv[2]+".ends","w").write("\n".join(["-"]+tails)+"\n")
inv=collections.defaultdict(set)
for k,v in mats.items():
    x=int(k,16)
    if x in named and x not in held:
        for m in v:
            if not m.startswith("material_") and m!="global_invisible": inv[m].add(named[x].split("/")[-1])
out=open(sys.argv[2],"w"); nb=0; tp=0; tv=0
for k,n in items:
    v=mats.get(k,{}); bs=B.get(k,[])
    src=list(cores(v))+(sorted(bone_cores(bs)) if len(bs)<=12 else [])
    own=collections.Counter(); P=set()
    for c in src:
        t=[x for x in c.split("_") if x]; own.update(t)
        for j in range(2,len(t)+1): P.add("_".join(t[:j]))
    c=collections.Counter(nn for m in v for nn in inv.get(m,()))
    src+= [nn for nn,_ in c.most_common(NB)]
    fams=set()
    for s in src:
        t=s.split("_")
        for kk in (3,4):
            if len(t)>kk: fams.add("_".join(t[:kk]))
    hc=collections.Counter(); vc=collections.Counter()
    for F in fams:
        if F in HC: hc.update(HC[F]); vc.update(VC[F])
    P|={x for x,_ in hc.most_common(HCAP)}
    if not P: continue
    V=[t for t,_ in own.most_common()]; s=set(V)
    V+=[t for t,_ in vc.most_common(VCAP) if t not in s]
    out.write("#I %s\n#P %s\n#V %s\n#D -\n#E @G\n"%(k," ".join(sorted(P))," ".join(V)))
    nb+=1; tp+=len(P); tv+=len(V)
out.close()
if VAL: open(sys.argv[2]+".truth","w").write("\n".join(n for k,n in items)+"\n")
print("blocks",nb,"avg P",tp//max(nb,1),"avg V",tv//max(nb,1),"tails",len(tails))
