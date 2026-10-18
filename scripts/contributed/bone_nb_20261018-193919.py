# Blocks for state/nbedit from each exported model's OWN cast bone stems (bonecore.py): the stems, their p7<->p8
# swaps, one-token deletions and +-1..3 number shifts; nbedit then tries one token sub/ins/del against the model's
# own id only. usage: py contrib/bo4_models/bone_nb.py PKL OUT [--validate]
import json,re,pickle,sys
sys.path.insert(0,"contrib/bo4_models"); from bonecore import bone_cores
d=pickle.load(open(sys.argv[1],"rb")); named=d["named"]["xmodel"]; M=(1<<63)-1; VAL="--validate" in sys.argv
un=json.load(open("state/bo4exp/unnamed_models.json")); B=json.load(open("state/bo4exp/bones.json"))
ks=[k for k in B if (int(k,16) in named)==VAL and len(B[k])<=12]
out=open(sys.argv[2],"w"); nb=0; tn=0; truth=[]
for k in ks:
    S=[s for s in bone_cores(B[k]) if s.count("_")>=2]
    if not S: continue
    X=dict.fromkeys(S)
    for s in S:
        m=re.match(r"p([78])_(.*)",s)
        if m: X["p%s_%s"%("7" if m.group(1)=="8" else "8",m.group(2))]=None
    for s in list(X):
        t=s.split("_")
        for i in range(1,len(t)): X["_".join(t[:i]+t[i+1:])]=None
        for i in range(1,len(t)):
            m=re.fullmatch(r"(\d+)([a-z]?)",t[i])
            if m:
                v=int(m.group(1)); w=len(m.group(1))
                for dv in (-3,-2,-1,1,2,3):
                    if v+dv>=0: X["_".join(t[:i]+[str(v+dv).zfill(w)+m.group(2)]+t[i+1:])]=None
    N=[n for n in X if n.count("_")>=1]
    out.write("#I %s\n"%k+"\n".join(N)+"\n"); nb+=1; tn+=len(N)
    if VAL: truth.append(named[int(k,16)])
out.close()
if VAL: open(sys.argv[2]+".truth","w").write("\n".join(truth)+"\n")
print("blocks",nb,"avg nb",tn//max(nb,1))
