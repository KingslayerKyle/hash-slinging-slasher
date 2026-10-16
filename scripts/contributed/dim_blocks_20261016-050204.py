# Blocks for state/dimpm: per exported BO4 model,
#   prefixes = >=2-token cuts of its own material/image/bone cores (t->p swap) and >=3-token cuts of named
#              export models that share a named material with it,
#   vocab    = own tokens + numbers + top global model tokens,
#   sizes    = the model's bounding box in inches (the cast is in cm) snapped to sizes known model names use,
#              as A, xA, AxB, A_B, AxBxC (measured: 266 of ~370 size tokens sit within 15% of an extent),
#   endings  = every run that follows a size token in a known name, plus the model's own tokens.
# Also writes OUT.mids: every run found between a >=2-token head and a size token in known names.
# usage: py contrib/bo4_models/dim_blocks.py PKL OUT [--validate] [gtop=1500]
#   --validate: targets = named export models with a number token; their names are removed from every list.
import json,re,collections,pickle,sys,itertools
sys.path.insert(0,"contrib/bo4_models"); from bonecore import bone_cores
d=pickle.load(open(sys.argv[1],"rb")); named=d["named"]["xmodel"]; M=(1<<63)-1
VAL="--validate" in sys.argv
ECUT=([a[5:] for a in sys.argv if a.startswith("ecut=")] or ["1"])[0]
GTOP=int(([a[5:] for a in sys.argv if a.startswith("gtop=")] or ["1500"])[0])
un=json.load(open("state/bo4exp/unnamed_models.json")); tr=json.load(open("state/bo4exp/train.json"))
B=json.load(open("state/bo4exp/bones.json")); bb=json.load(open("state/bo4exp/bbox.json"))
def h(s):
    x=0xCBF29CE484222325
    for c in s.encode(): x=((x^c)*0x100000001B3)&0xFFFFFFFFFFFFFFFF
    return x&M
mats={}
for n,v in tr: mats["%x"%h(n)]=v
mats.update(un)
DIM=re.compile(r"x?\d+(x\d+)*$")
def has_size(t): return bool(DIM.fullmatch(t)) and any(int(v)>=8 for v in re.findall(r"\d+",t))
if VAL:
    items=[("%x"%h(n),n) for n,v in tr]+[("%x"%x,named[x]) for x in (int(k,16) for k in un) if x in named]
    items=[(k,n) for k,n in items if k in bb and re.search(r"_x?\d+(x\d+)*(_|$)",n.split("/")[-1])]
else:
    items=[(k,None) for k in un if int(k,16) not in named and k in bb]
held={int(k,16) for k,n in items} if VAL else set()
names=[n for x,n in named.items() if x not in held]
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
nice=collections.Counter(); tails=collections.Counter(); MIDS=collections.Counter()
for n in names:
    t=n.split("/")[-1].split("_")
    for i,x in enumerate(t):
        if i>=2 and has_size(x):
            for v in re.findall(r"\d+",x):
                if int(v)>=8 and not v.startswith("0"): nice[int(v)]+=1
            tails["_".join(t[i+1:])]+=1
            for j in range(2,i): MIDS["_".join(t[j:i])]+=1
NICE=sorted(x for x,c in nice.items() if c>=2)
E=["-"]+["_"+t for t,c in tails.most_common() if t and c>=int(ECUT)]
GT=[t for t,_ in collections.Counter(t for n in names for t in n.split("/")[-1].split("_")).most_common(GTOP)]
NUM=["%02d"%i for i in range(0,13)]+[str(i) for i in range(1,6)]+list("abcd")
COMMON={x for x,c in nice.items() if c>=20}
def snaps(e,k=2):
    s=sorted((abs(e-x)/x,x) for x in NICE if abs(e-x)<=max(1.5,0.15*x))
    s=[x for _,x in s[:k]]+[x for _,x in s if x in COMMON and x not in s[:k] and k>1]
    if e>=8 and int(round(e)) not in s: s.append(int(round(e)))
    return s
def dims(v):
    ext=[(v[3]-v[0])/2.54,(v[4]-v[1])/2.54,(v[5]-v[2])/2.54]
    S=[snaps(e) for e in ext]; D=set()
    for i in range(3):
        for a in S[i]: D.add(str(a)); D.add("x%d"%a)
    for i,j in itertools.permutations(range(3),2):
        for a in S[i]:
            for b in S[j]: D.add("%dx%d"%(a,b)); D.add("%d_%d"%(a,b))
    S1=[snaps(e,1) for e in ext]
    for i,j,k in itertools.permutations(range(3),3):
        for a in S1[i]:
            for b in S1[j]:
                for c in S1[k]: D.add("%dx%dx%d"%(a,b,c))
    return D
inv=collections.defaultdict(set)
for k,v in mats.items():
    x=int(k,16)
    if x in named and x not in held:
        for m in v:
            if not m.startswith("material_") and m!="global_invisible": inv[m].add(named[x])
def nb_names(k):
    c=collections.Counter(n for m in mats.get(k,{}) for n in inv.get(m,()))
    return [n for n,_ in c.most_common(30)]
open(sys.argv[2]+".mids","w").write("\n".join(m for m,c in MIDS.most_common() if len(m)<=60)+"\n")
out=open(sys.argv[2],"w"); nb=0; tot=0
for k,n in items:
    C=cores(mats.get(k,{})); bs=B.get(k,[]); BC=sorted(bone_cores(bs)) if len(bs)<=12 else []
    P=set(); own=collections.Counter()
    for c in list(C)+BC:
        t=[x for x in c.split("_") if x]; own.update(t)
        for j in range(2,len(t)+1): P.add("_".join(t[:j]))
    for nn in nb_names(k):
        t=nn.split("/")[-1].split("_")
        for j in range(3,len(t)): P.add("_".join(t[:j]))
    if not P: continue
    D=dims(bb[k])
    if not D: continue
    V=[t for t,_ in own.most_common()]; s=set(V)
    V+=[t for t in NUM if t not in s]; s|=set(NUM); V+=[t for t in GT if t not in s]
    EE=E+["_"+t for t,_ in own.most_common(20)]
    out.write("#I %s\n#P %s\n#V %s\n#D %s\n#E %s\n"%(k," ".join(sorted(P))," ".join(V)," ".join(sorted(D))," ".join(dict.fromkeys(EE))))
    nb+=1; tot+=len(P)*len(D)
out.close()
if VAL: open(sys.argv[2]+".truth","w").write("\n".join(n for k,n in items)+"\n")
print("blocks",nb,"avg P*D",tot//max(nb,1),"ends",len(E),"nice",len(NICE),"mids",len(MIDS))
