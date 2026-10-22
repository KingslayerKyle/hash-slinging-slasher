# Blocks for state/dimpm with no size slot: per exported BO4 model, checked only against its own id,
#   P [_mid] E
# (any=1 adds every BO4 token seen twice as a one-word middle; fam=N adds the N most common 2-4 token model family prefixes to every block's P)
# P   = >=2-token cuts of its own material/image/bone cores (t->p swap) + >=3-token cuts of named export
#       models sharing a named material with it,
# mid = OUT.mids (global): every 1-3 token run found inside known model names (>= MINC times) and every
#       2-4 token inner span of the unnamed export cores; plus per block own tokens / top words (V, V x V2),
# E   = the TOPE most common 1-3 token endings of known model names, plus own tokens (and own_01),
#       plus the 1-5 token endings of the named neighbour models.
# usage: py contrib/bo4_models/mid_blocks.py PKL OUT [--validate] [tope=3000] [minc=3] [gtop=400]
import json,re,collections,pickle,sys
sys.path.insert(0,"contrib/bo4_models"); from bonecore import bone_cores
d=pickle.load(open(sys.argv[1],"rb")); named=d["named"]["xmodel"]; M=(1<<63)-1
A=dict(a.split("=",1) for a in sys.argv[3:] if "=" in a)
VAL="--validate" in sys.argv; TOPE=int(A.get("tope",3000)); MINC=int(A.get("minc",3)); GTOP=int(A.get("gtop",400)); FAM=int(A.get("fam",0))
un=json.load(open("state/bo4exp/unnamed_models.json")); tr=json.load(open("state/bo4exp/train.json"))
B=json.load(open("state/bo4exp/bones.json"))
def h(s):
    x=0xCBF29CE484222325
    for c in s.encode(): x=((x^c)*0x100000001B3)&0xFFFFFFFFFFFFFFFF
    return x&M
mats={}
for n,v in tr: mats["%x"%h(n)]=v
mats.update(un)
if VAL:
    items=[("%x"%h(n),n) for n,v in tr]+[("%x"%x,named[x]) for x in (int(k,16) for k in un) if x in named]
else:
    items=[(k,None) for k in un if int(k,16) not in named]
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
ends=collections.Counter(); runs=collections.Counter()
for n in names:
    t=n.split("/")[-1].split("_")
    for k in (1,2,3):
        if len(t)>k+1: ends["_"+"_".join(t[-k:])]+=1
    for i in range(2,len(t)):
        for L in (1,2,3):
            if i+L<len(t): runs["_".join(t[i:i+L])]+=1
E=[e for e,_ in ends.most_common(TOPE)]
mids=set(r for r,c in runs.items() if c>=MINC and len(r)<=40)
spans=set()
for k,n in items:
    for c in cores(mats.get(k,{})):
        t=[x for x in c.split("_") if x]
        for i in range(1,len(t)):
            for L in (2,3,4):
                if i+L<=len(t): spans.add("_".join(t[i:i+L]))
mids|={s for s in spans if len(s)<=48}
if int(A.get("any",0)):   # every token seen >=2 times across all named BO4 assets, as a one-word middle
    tc=collections.Counter()
    for kk,ns in d["allnames"].items():
        for nn in ns:
            nn=nn.lower().replace("\\","/")
            if VAL and h(nn) in held: continue
            tc.update(t for t in re.split(r"[_/]",nn) if t)
    mids|={t for t,c in tc.items() if c>=2 and len(t)<=24}
if A.get("extra"): mids|={l.strip() for l in open(A["extra"]) if l.strip()}   # extra=FILE: more one-token middles
open(sys.argv[2]+".mids","w").write("\n".join(sorted(mids))+"\n")
FAMS=[f for f,_ in collections.Counter("_".join(n.split("/")[-1].split("_")[:k]) for n in names for k in (2,3,4) if len(n.split("/")[-1].split("_"))>k).most_common(FAM)]
GT=[t for t,_ in collections.Counter(t for n in names for t in n.split("/")[-1].split("_")).most_common(GTOP)]
NUM=["%02d"%i for i in range(0,13)]+[str(i) for i in range(1,6)]+list("abcd")
inv=collections.defaultdict(set)
for k,v in mats.items():
    x=int(k,16)
    if x in named and x not in held:
        for m in v:
            if not m.startswith("material_") and m!="global_invisible": inv[m].add(named[x])
def nb_names(k):
    c=collections.Counter(n for m in mats.get(k,{}) for n in inv.get(m,()))
    return [n for n,_ in c.most_common(30)]
out=open(sys.argv[2],"w"); nb=0; tp=0
for k,n in items:
    C=cores(mats.get(k,{})); bs=B.get(k,[]); BC=sorted(bone_cores(bs)) if len(bs)<=12 else []
    P=set(); own=collections.Counter()
    for c in list(C)+BC:
        t=[x for x in c.split("_") if x]; own.update(t)
        for j in range(2,len(t)+1): P.add("_".join(t[:j]))
    NE=set()
    for nn in nb_names(k):
        t=nn.split("/")[-1].split("_")
        for j in range(3,len(t)): P.add("_".join(t[:j]))
        for j in range(max(2,len(t)-5),len(t)): NE.add("_"+"_".join(t[j:]))
    P.update(FAMS)
    if not P: continue
    V=[t for t,_ in own.most_common()]; s=set(V)
    V+=[t for t in NUM if t not in s]; s|=set(NUM); V+=[t for t in GT if t not in s]
    EE=["-"]+E+["_"+t for t,_ in own.most_common(25)]+["_"+t+"_01" for t,_ in own.most_common(25)]+sorted(NE)
    out.write("#I %s\n#P %s\n#V %s\n#D -\n#E %s\n"%(k," ".join(sorted(P))," ".join(V)," ".join(dict.fromkeys(EE))))
    nb+=1; tp+=len(P)
out.close()
if VAL: open(sys.argv[2]+".truth","w").write("\n".join(n for k,n in items)+"\n")
print("blocks",nb,"avg P",tp//max(nb,1),"ends",len(E),"mids",len(mids))
