# Lists for state/hwt (global meet-in-the-middle over unnamed BO4 model ids):
#   head [_word] _tail
# head = every >=2-token prefix of a known BO4 model name (+ >=2-token cuts of export material/image cores, t->p),
# word = BO4 tokens seen >= WMIN times across all named BO4 assets, tail = every 1-TMAX token suffix of a known
# model name seen >= TMIN times. --validate holds out the named export models (ids = theirs, lists exclude them).
# bi=N adds known 2-token runs as middles.
# usage: py contrib/bo4_models/hwt_prep.py PKL OUTDIR [--validate] [wmin=2] [tmin=1] [tmax=5] [hmin=1]
import json,re,collections,pickle,sys,os
d=pickle.load(open(sys.argv[1],"rb")); named=d["named"]["xmodel"]; M=(1<<63)-1; O=sys.argv[2]
A=dict(a.split("=",1) for a in sys.argv[3:] if "=" in a); VAL="--validate" in sys.argv
WMIN=int(A.get("wmin",2)); TMIN=int(A.get("tmin",1)); TMAX=int(A.get("tmax",5)); HMIN=int(A.get("hmin",1))
un=json.load(open("state/bo4exp/unnamed_models.json")); tr=json.load(open("state/bo4exp/train.json"))
def h(s):
    x=0xCBF29CE484222325
    for c in s.encode(): x=((x^c)*0x100000001B3)&0xFFFFFFFFFFFFFFFF
    return x&M
held=set()
if VAL:
    held={h(n) for n,v in tr}|{int(k,16) for k in un if int(k,16) in named}
    ids=sorted(held)
else:
    ids=sorted(d["pools"]["xmodel"]-set(named))
names=[n for x,n in named.items() if x not in held]
H=collections.Counter(); T=collections.Counter()
for n in names:
    t=n.split("/")[-1].split("_")
    for j in range(2,len(t)): H["_".join(t[:j])]+=1
    for j in range(1,min(TMAX,len(t)-2)+1): T["_".join(t[len(t)-j:])]+=1
heads={x for x,c in H.items() if c>=HMIN}
mats=dict(un) if not VAL else dict([(n,v) for n,v in tr]+[(k,v) for k,v in un.items() if int(k,16) in named])
for k,v in mats.items():
    for mat,imgs in v.items():
        cs=[] if mat.startswith("material_") else [re.sub(r"^(mtl_|mc/|ml/)","",mat)]
        cs+=[re.sub(r"_[a-z]{1,3}$","",re.sub(r"^mtl_","",re.sub(r"^i_","",i))) for i in imgs if not i.startswith(("$","ximage_","image_"))]
        for c in cs:
            c=c.split("/")[-1]; m=re.match(r"t([78])_(.*)",c)
            for cc in [c]+(["p%s_%s"%m.groups()] if m else []):
                t=cc.split("_")
                for j in range(2,len(t)+1): heads.add("_".join(t[:j]))
tc=collections.Counter()
for kk,ns in d["allnames"].items():
    for nn in ns:
        nn=nn.lower().replace("\\","/")
        if VAL and h(nn) in held: continue
        tc.update(t for t in re.split(r"[_/]",nn) if t)
words=set(t for t,c in tc.items() if c>=WMIN and len(t)<=24)
BI=int(A.get("bi",0))   # bi=N: also every 2-token run inside known model names (not first two tokens) seen >= N times
if BI:
    bc=collections.Counter()
    for n in names:
        t=n.split("/")[-1].split("_")
        for i in range(2,len(t)-1): bc[t[i]+"_"+t[i+1]]+=1
    words|={b for b,c in bc.items() if c>=BI and len(b)<=32}
TRI=int(A.get("tri",0))   # tri=N: 3-token inner runs seen >= N times
if TRI:
    bc=collections.Counter()
    for n in names:
        t=n.split("/")[-1].split("_")
        for i in range(2,len(t)-2): bc["_".join(t[i:i+3])]+=1
    words|={b for b,c in bc.items() if c>=TRI and len(b)<=40}
if int(A.get("mh",0)):   # mh=1: heads also from named BO4 material/image names that look like model names
    for kk in ("material","image"):
        for nn in d["named"][kk].values():
            c=re.sub(r"^(i_mtl_|mtl_|i_)","",nn.split("/")[-1]); c=re.sub(r"_[a-z]{1,3}$","",c) if kk=="image" else c
            if re.match(r"(p[678]_|veh_t8_|c_t8_|wpn_t8_|attach_t8_|fxanim_)",c):
                t=c.split("_")
                for j in range(2,len(t)+1): heads.add("_".join(t[:j]))
words=sorted(words)
tails=sorted(x for x,c in T.items() if c>=TMIN and len(x)<=60)
heads=sorted(x for x in heads if len(x)<=90)
heads=[x for x in heads if not VAL or h(x) not in held]
os.makedirs(O,exist_ok=True)
open(O+"/ids.txt","w").write("\n".join("%x"%x for x in ids)+"\n")
open(O+"/heads.txt","w").write("\n".join(heads)+"\n")
open(O+"/words.txt","w").write("\n".join(words)+"\n")
open(O+"/tails.txt","w").write("\n".join(tails)+"\n")
if VAL: open(O+"/truth.txt","w").write("\n".join(named[x] for x in ids)+"\n")
c=len(heads)*(len(words)+1)*len(tails)
print("ids",len(ids),"heads",len(heads),"words",len(words),"tails",len(tails),"cands %.2e"%c,"exp chance %.2f"%(c*len(ids)/2**63))
