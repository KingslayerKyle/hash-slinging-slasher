# Hashed materials of the BO4 Saluki model export (material_<id>), searched one id at a time.
# Export material names are all `mc/` (11,646 of 11,676 named ones), so every candidate carries mc/.
# Writes two block files for the own-id tools:
#   OUT.nb   for state/nbedit: neighbours = named materials of the same models + named materials sharing an image
#   OUT.mid  for state/dimpm (run with GE=OUT.mid.ends): P = mc/ + cuts of the material's own image cores, of
#            its models' names (p8_->mtl_p8_/t8_) and of its named sibling materials; middles = inner runs of
#            known BO4 material names + every BO4 token; endings = the TOPE commonest 1-3 token material endings.
# usage: py contrib/bo4_models/mat_blocks.py PKL OUT [--validate] [tope=50000] [nval=2500]
import json,re,collections,pickle,sys,random
d=pickle.load(open(sys.argv[1],"rb")); M=(1<<63)-1
A=dict(a.split("=",1) for a in sys.argv[3:] if "=" in a); TOPE=int(A.get("tope",50000)); VAL="--validate" in sys.argv
mp=d["pools"]["material"]; mn=d["named"]["material"]; xn=d["named"]["xmodel"]
def h(s):
    x=0xCBF29CE484222325
    for c in s.lower().encode(): x=((x^c)*0x100000001B3)&0xFFFFFFFFFFFFFFFF
    return x&M
un=json.load(open("state/bo4exp/unnamed_models.json")); tr=json.load(open("state/bo4exp/train.json"))
models={}
for n,v in tr: models[h(n)]=v
for k,v in un.items(): models[int(k,16)]=v
H=re.compile(r"material_([0-9a-f]{6,16})$")
def mid(m):   # material id and full name (if known) for an export material label
    g=H.match(m)
    if g: x=int(g.group(1),16)&M; return x, mn.get(x)
    for dd in ("mc/","splm/","mcs/","wc/"):
        x=h(dd+m)
        if x in mp: return x, dd+m
    return None,None
imgs=collections.defaultdict(set); inmodels=collections.defaultdict(set); name={}
for mx,v in models.items():
    for m,ii in v.items():
        x,n=mid(m)
        if x is None: continue
        imgs[x].update(ii); inmodels[x].add(mx)
        if n: name[x]=n
if VAL:
    random.seed(7); cand=sorted(x for x in name)
    items=random.sample(cand,min(int(A.get("nval",2500)),len(cand)))
else:
    items=[x for x in imgs if x in mp and x not in mn]
held=set(items) if VAL else set()
known={x:n for x,n in name.items() if x not in held}
kn=[n for x,n in mn.items() if x not in held]
# indices
by_img=collections.defaultdict(set)
for x,ii in imgs.items():
    for i in ii:
        if not i.startswith(("$","ximage_","image_")): by_img[i].add(x)
def icore(i):
    c=re.sub(r"^i_","",i); c=re.sub(r"_[a-z]{1,3}$","",c); return c
ends=collections.Counter(); runs=collections.Counter(); tok=collections.Counter()
for n in kn:
    t=n.split("/")[-1].split("_"); tok.update(t)
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
    sib=collections.Counter()
    for mx in inmodels[x]:
        for m in models[mx]:
            y,n=mid(m)
            if y is not None and y!=x and y in known: sib[known[y]]+=2
    for i in imgs[x]:
        for y in by_img.get(i,()):
            if y!=x and y in known: sib[known[y]]+=1
    N=[n for n,_ in sib.most_common(60)]
    if N: fn.write("#I %x\n"%x+"\n".join(N)+"\n"); nb+=1
    cores=set()
    for i in imgs[x]:
        if not i.startswith(("$","ximage_","image_")): cores.add(icore(i))
    for mx in inmodels[x]:
        if mx in xn and mx not in held:
            b=xn[mx].split("/")[-1]; cores.add(b); cores.add("mtl_"+b)
            g=re.match(r"p([78])_(.*)",b)
            if g: cores.add("t%s_%s"%g.groups())
    for n in N[:20]: cores.add(n.split("/")[-1])
    P=set(); own=collections.Counter()
    for c in cores:
        t=[y for y in c.split("_") if y]; own.update(t)
        for j in range(2,len(t)+1): P.add("mc/"+"_".join(t[:j]))
    if not P: continue
    VV=[t for t,_ in own.most_common()]
    EE=["@G"]+["_"+t for t,_ in own.most_common(25)]
    fm.write("#I %x\n#P %s\n#V %s\n#D -\n#E %s\n"%(x," ".join(sorted(P))," ".join(VV) or "01"," ".join(EE))); nm+=1
fn.close(); fm.close()
if VAL: open(o+".truth","w").write("\n".join(name[x] for x in items)+"\n")
print("targets",len(items),"nb blocks",nb,"mid blocks",nm,"vocab",len(V),"mids",len(mids),"ends",len(E))
