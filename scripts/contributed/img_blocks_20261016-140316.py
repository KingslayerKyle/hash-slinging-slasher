# Hashed images (image_<id>) of the BO4 Saluki model export, searched one id at a time.
# Uses state/bo4exp/mat_images.json (export_semantics.py: each material's [slot, image] rows) so every image
# knows its material, its slot (colorMap, normalMap, ...) and its named sibling images.
#   OUT.nb   for state/nbedit: neighbours = named images of the same material (same slot first), then of the
#            other materials of the same models
#   OUT.mid  for state/dimpm (GE=OUT.mid.ends): P = i_ + cuts of the material name (with and without mtl_),
#            of its named sibling image cores and of its models' names; middles = known image inner runs + BO4
#            tokens; endings = the slot's measured suffixes first, then the TOPE commonest image endings.
# usage: py contrib/bo4_models/img_blocks.py PKL OUT [--validate] [tope=50000] [nval=2500]
import json,re,collections,pickle,sys,random
d=pickle.load(open(sys.argv[1],"rb")); M=(1<<63)-1
A=dict(a.split("=",1) for a in sys.argv[3:] if "=" in a); TOPE=int(A.get("tope",50000)); VAL="--validate" in sys.argv
ip=d["pools"]["image"]; inn=d["named"]["image"]; xn=d["named"]["xmodel"]
def h(s):
    x=0xCBF29CE484222325
    for c in s.lower().encode(): x=((x^c)*0x100000001B3)&0xFFFFFFFFFFFFFFFF
    return x&M
MI=json.load(open("state/bo4exp/mat_images.json"))
un=json.load(open("state/bo4exp/unnamed_models.json")); tr=json.load(open("state/bo4exp/train.json"))
H=re.compile(r"x?image_([0-9a-f]{6,16})$")
def iid(i):
    g=H.match(i)
    return (int(g.group(1),16)&M) if g else h(i)
# material -> models (by basename, as the model index labels them)
mm=collections.defaultdict(set)
for n,v in tr:
    for m in v: mm[m].add(h(n))
for k,v in un.items():
    for m in v: mm[m].add(int(k,16))
slot={}; mats=collections.defaultdict(set); name={}
for mat,rows in MI.items():
    for s,i in rows:
        if i.startswith("$"): continue
        x=iid(i); mats[x].add(mat); slot.setdefault(x,collections.Counter())[s]+=1
        if not H.match(i): name[x]=i
        elif x in inn: name[x]=inn[x]
if VAL:
    random.seed(7); items=random.sample(sorted(x for x in name if x in ip),min(int(A.get("nval",2500)),len(name)))
else:
    items=[x for x in mats if x in ip and x not in inn]
held=set(items) if VAL else set()
known={x:n for x,n in name.items() if x not in held}
kn=[n for x,n in inn.items() if x not in held]
# slot -> suffix distribution, measured on known export images
suf=collections.defaultdict(collections.Counter)
for x,n in known.items():
    for s in slot.get(x,()): suf[s]["_"+n.split("_")[-1]]+=1
ends=collections.Counter(); runs=collections.Counter(); tok=collections.Counter()
for n in kn:
    t=n.split("_"); tok.update(t)
    for k in (1,2,3):
        if len(t)>k+1: ends["_"+"_".join(t[-k:])]+=1
    for i in range(2,len(t)):
        for L in (1,2,3):
            if i+L<len(t): runs["_".join(t[i:i+L])]+=1
for ns in d["allnames"].values():
    for s in ns: tok.update(t for t in re.split(r"[_/]",s.lower()) if t)
E=["-"]+[e for e,_ in ends.most_common(TOPE)]
mids=set(r for r,c in runs.items() if c>=2 and len(r)<=40)|set(t for t,c in tok.items() if c>=2 and len(t)<=24)
V=sorted(t for t,c in tok.items() if c>=2 and len(t)<=24)
o=sys.argv[2]
open(o+".vocab","w").write("\n".join(V)+"\n")
open(o+".mid.mids","w").write("\n".join(sorted(mids))+"\n")
open(o+".mid.ends","w").write("\n".join(E)+"\n")
fn=open(o+".nb","w"); fm=open(o+".mid","w"); nb=nm=0
for x in items:
    mys=set(slot.get(x,()))
    same=collections.Counter(); cores=set()
    for mat in mats[x]:
        base=mat.split("/")[-1]; cores.add(base)
        if base.startswith("mtl_"): cores.add(base[4:])
        else: cores.add("mtl_"+base)
        for s,i in MI.get(mat,()):
            y=iid(i)
            if y!=x and y in known: same[known[y]]+=3 if s in mys else 2
        for mx in mm.get(base,()):
            if mx in xn and mx not in held:
                b=xn[mx].split("/")[-1]; cores.add(b)
                g=re.match(r"p([78])_(.*)",b)
                if g: cores.add("t%s_%s"%g.groups())
    N=[n for n,_ in same.most_common(60)]
    if N: fn.write("#I %x\n"%x+"\n".join(N)+"\n"); nb+=1
    for n in N[:20]: cores.add(re.sub(r"^i_","",n))
    P=set(); own=collections.Counter()
    for c in cores:
        t=[y for y in c.split("_") if y]; own.update(t)
        for j in range(2,len(t)+1): P.add("i_"+"_".join(t[:j]))
    if not P: continue
    EE=["@G"]+[e for s in mys for e,_ in suf[s].most_common(8)]+["_"+t for t,_ in own.most_common(25)]
    fm.write("#I %x\n#P %s\n#V %s\n#D -\n#E %s\n"%(x," ".join(sorted(P))," ".join(t for t,_ in own.most_common()) or "01"," ".join(dict.fromkeys(EE)))); nm+=1
fn.close(); fm.close()
if VAL: open(o+".truth","w").write("\n".join(name[x] for x in items)+"\n")
print("targets",len(items),"nb blocks",nb,"mid blocks",nm,"slots",{s:c.most_common(3) for s,c in list(suf.items())[:4]})
