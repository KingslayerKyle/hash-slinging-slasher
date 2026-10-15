# BO4 fxanim models: (1) every token prefix of every known fxanim xanim name + model endings,
# (2) writes plan lists: fxanim heads (token prefixes of known fxanim model/xanim names) and
# bone stems (cleaned bone cores of exported models with skeletons, plus their token suffixes).
import json,re,sys,pickle
sys.path.insert(0,"contrib/bo4_models"); from bonecore import bone_cores
d=pickle.load(open(sys.argv[1],"rb"))
anims=[n for n in d["named"]["xanim"].values() if "fxanim" in n]
mods=[n for n in d["named"]["xmodel"].values() if "fxanim" in n]
END=["_mod","_smod","_mdl","","_mod_01","_01_mod","_02_mod","_rig","_rig_mod"]
out=set(); heads=set()
for n in anims+mods:
    t=n.split("_")
    for k in range(2,len(t)+1):
        p="_".join(t[:k]); heads.add(p)
        if n in anims:
            for e in END: out.add(p+e)
open("contrib/bo4_models/fx_heads.txt","w").write("\n".join(sorted(heads))+"\n")
bones=json.load(open("state/bo4exp/bones.json"))
st=set()
for v in bones.values():
    if 1<len(v)<=200:
        for b in bone_cores(v):
            b=re.sub(r"_jnt$","",b); t=b.split("_")
            for k in range(len(t)): st.add("_".join(t[k:]))
open("contrib/bo4_models/fx_bones.txt","w").write("\n".join(sorted(st))+"\n")
for n in sorted(out): print(n)
print(len(heads),len(st),file=sys.stderr)
