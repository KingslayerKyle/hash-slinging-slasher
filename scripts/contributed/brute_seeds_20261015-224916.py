# Seeds for the short-tail brute force (contrib/bo4_models/brute.cs): per-model evidence from a Saluki
# BO4 export. Known names in each unnamed model's family/neighbour groups (whole, minus 1-2 trailing
# tokens), cleaned cast bone cores (whole, minus 1 token), export material-core stems of >=3 tokens.
# Every seed ends in "_"; the tool appends every [a-z0-9_]{1..L} tail.
import json,sys
sys.path.insert(0,"contrib/bo4_models"); from bonecore import bone_cores
groups=sys.argv[1]
S=set()
def add(t,k):
    if k>=2: S.add("_".join(t[:k])+"_")
for l in open(groups,encoding="utf-8"):
    l=l.strip()
    if not l or l.startswith("#V"): continue
    t=l.split("_")
    for k in (len(t),len(t)-1,len(t)-2): add(t,k)
B=json.load(open("state/bo4exp/bones.json"))
for v in B.values():
    if len(v)<=12:
        for b in bone_cores(v):
            t=b.split("_"); add(t,len(t)); add(t,len(t)-1)
for l in open("contrib/bo4_models/exp_stems.txt"):
    t=l.strip().split("_")
    if len(t)>=3: add(t,len(t))
for s in sorted(S): print(s)
