# Modular kit pieces (p8_kit_*), slot by slot, per exported model, checked only against its own id (state/dimpm):
#   <kit family>_<piece NN> [_<shape/material run>] [_<size>] <tail>
# kit family = p8_kit_<map>_<set>_<NN> read off the model's own kit materials and its named neighbours,
# piece      = the token run up to the first number after a kit family in known kit names (wall_panel_01, door_47),
# middles    = the runs between piece and size/number in known kit names, plus every shape x material-word recombination,
# size       = the model's bounding box (dim_blocks.py rules) or none,
# tail       = what follows in known kit names (_01, _02_grunge, _debris_01 ...).
# usage: py contrib/bo4_models/kit_blocks.py PKL OUT [--validate]
import json,re,collections,pickle,sys,itertools
sys.path.insert(0,"contrib/bo4_models")
d=pickle.load(open(sys.argv[1],"rb")); named=d["named"]["xmodel"]; M=(1<<63)-1
VAL="--validate" in sys.argv
un=json.load(open("state/bo4exp/unnamed_models.json")); tr=json.load(open("state/bo4exp/train.json"))
bb=json.load(open("state/bo4exp/bbox.json"))
def h(s):
    x=0xCBF29CE484222325
    for c in s.encode(): x=((x^c)*0x100000001B3)&0xFFFFFFFFFFFFFFFF
    return x&M
mats={}
for n,v in tr: mats["%x"%h(n)]=v
mats.update(un)
NUMT=re.compile(r"^\d+[a-z]?$")
SIZE=re.compile(r"^(x?\d+(x\d+)*|\d+[hw])$")
def kfam(t):
    # p8_kit_<map>_<set>_<NN> when token 4 is a number, else p8_kit_<a>_<b> (+ number if it follows)
    if len(t)>4 and NUMT.match(t[4]): return 5
    if len(t)>3 and NUMT.match(t[3]): return 4
    return 4 if len(t)>4 else None
def kit_core(s):
    s=s.split("/")[-1]; s=re.sub(r"^(i_)?(mtl_)?","",s); s=re.sub(r"^t8_kit_","p8_kit_",s)
    return s if s.startswith("p8_kit_") else None
allkit=[n for x,n in named.items() if n.split("/")[-1].startswith("p8_kit_")]
def is_kit_model(k):
    for m,imgs in mats.get(k,{}).items():
        if kit_core(m) or any(kit_core(i) for i in imgs): return True
    return False
if VAL:
    items=[(k,named[int(k,16)]) for k in mats if int(k,16) in named and named[int(k,16)].split("/")[-1].startswith("p8_kit_") and k in bb]
else:
    items=[(k,None) for k in un if int(k,16) not in named and k in bb and is_kit_model(k)]
held={int(k,16) for k,n in items} if VAL else set()
kn=[n for n in allkit if h(n) not in held]
pieces=collections.Counter(); middles=collections.Counter(); tails=collections.Counter()
for n in kn:
    t=n.split("/")[-1].split("_"); f=kfam(t)
    if not f: continue
    r=t[f:]; i=next((j for j,x in enumerate(r) if NUMT.match(x)),None)
    if i is None or i>3: continue
    pieces["_".join(r[:i+1])]+=1; r=r[i+1:]
    j=next((j for j,x in enumerate(r) if SIZE.match(x) or NUMT.match(x)),len(r))
    if j: middles["_".join(r[:j])]+=1
    if j<len(r):
        rr=r[j:]
        if SIZE.match(rr[0]) and len(rr)>1 and not NUMT.match(rr[0]) or (len(rr)>1 and SIZE.match(rr[0]) and int(re.findall(r"\d+",rr[0])[0])>=8): rr=rr[1:]
        tails["_"+"_".join(rr)]+=1
# shape x material-word recombination
matw=collections.Counter(); shapes=collections.Counter()
for m,c in middles.items():
    t=m.split("_")
    if len(t)>=2 and t[-1] in ("wood","metal","concrete","clay","plaster","stone","brick","glass"):
        matw["_".join(t[-2:])]+=c; s="_".join(t[:-2])
        if s: shapes[s]+=c
    else: shapes[m]+=c
mids=set(middles)|{s+"_"+w for s in shapes for w in matw}|set(matw)
open(sys.argv[2]+".mids","w").write("\n".join(sorted(mids))+"\n")
E=["-"]+[t for t,c in tails.most_common(400)]
for i in range(1,7): E.append("_%02d"%i)
E=list(dict.fromkeys(E))
DIM=re.compile(r"x?\d+(x\d+)*$")
nice=collections.Counter()
for n in named.values():
    if h(n) in held: continue
    for x in n.split("/")[-1].split("_")[2:]:
        if DIM.fullmatch(x):
            for v in re.findall(r"\d+",x):
                if int(v)>=8 and not v.startswith("0"): nice[int(v)]+=1
NICE=sorted(x for x,c in nice.items() if c>=2); COMMON={x for x,c in nice.items() if c>=20}
def snaps(e,k=2):
    s=sorted((abs(e-x)/x,x) for x in NICE if abs(e-x)<=max(1.5,0.15*x))
    s=[x for _,x in s[:k]]+[x for _,x in s if x in COMMON and x not in s[:k] and k>1]
    if e>=8 and int(round(e)) not in s: s.append(int(round(e)))
    return s
def dims(v):
    ext=[(v[3]-v[0])/2.54,(v[4]-v[1])/2.54,(v[5]-v[2])/2.54]
    S=[snaps(e) for e in ext]; D=set()
    for i in range(3):
        for a in S[i]: D.add(str(a))
    for i,j in itertools.permutations(range(3),2):
        for a in S[i]:
            for b in S[j]: D.add("%dx%d"%(a,b)); D.add("%d_%d"%(a,b)); D.add("%dh_%dw"%(a,b))
    return D
inv=collections.defaultdict(set)
for k,v in mats.items():
    x=int(k,16)
    if x in named and x not in held:
        for m in v:
            if not m.startswith("material_") and m!="global_invisible": inv[m].add(named[x])
TOPP=[p for p,_ in pieces.most_common(400)]
out=open(sys.argv[2],"w"); nb=0; tp=0
for k,n in items:
    fams=set()
    for m,imgs in mats.get(k,{}).items():
        for c in [m]+list(imgs):
            c=kit_core(c)
            if c:
                t=c.split("_"); f=kfam(t)
                if f: fams.add("_".join(t[:f]))
    for m in mats.get(k,{}):
        for nn in inv.get(m,()):
            t=nn.split("/")[-1].split("_")
            if t[:2]==["p8","kit"]:
                f=kfam(t)
                if f: fams.add("_".join(t[:f]))
    if not fams: continue
    fp=set(TOPP)
    for nn in kn:
        b=nn.split("/")[-1]
        for f in fams:
            if b.startswith(f+"_"):
                t=b.split("_"); fi=len(f.split("_")); r=t[fi:]; i=next((j for j,x in enumerate(r) if NUMT.match(x)),None)
                if i is not None and i<=3:
                    base="_".join(r[:i]); fp.add("_".join(r[:i+1]))
                    for z in range(1,21): fp.add("%s_%02d"%(base,z))
    P=sorted(f+"_"+p for f in fams for p in fp)
    D=sorted(dims(bb[k]))+["-"]
    out.write("#I %s\n#P %s\n#V 01\n#D %s\n#E %s\n"%(k," ".join(P)," ".join(D)," ".join(E)))
    nb+=1; tp+=len(P)
out.close()
if VAL: open(sys.argv[2]+".truth","w").write("\n".join(n for k,n in items)+"\n")
print("kit blocks",nb,"avg P",tp//max(nb,1),"mids",len(mids),"ends",len(E),"pieces",len(pieces))
