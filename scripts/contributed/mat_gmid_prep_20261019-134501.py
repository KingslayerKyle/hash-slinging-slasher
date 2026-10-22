# gmid blocks for the still-hashed MATERIALS of the exported BO4 models: block id = the material id, P = the using model's
# family heads (from a fam_blocks file) as material names (mc/mtl_<head>, mc/<head>, t->p swapped back to t8_), V = that
# model's family vocab, plus OUT.ends = 1-5 token suffixes of known material names (most common first).
# Run:  GE=OUT.ends [SYM=1] gmid OUT tokens.txt
# usage: py contrib/bo4_models/mat_gmid_prep.py PKL FAM_BLOCKS OUT
import sys,json,re,pickle,collections
d=pickle.load(open(sys.argv[1],"rb")); M=(1<<63)-1; nm=d["named"]["material"]; PCAP=2000
blocks={}; cur=None
for l in open(sys.argv[2]):
    if l.startswith("#I "): cur=l[3:].strip(); blocks[cur]={}
    elif l[:2] in ("#P","#V"): blocks[cur][l[:2]]=l[3:].split()
u=json.load(open("state/bo4exp/unnamed_models.json"))
T=collections.Counter()
for n in nm.values():
    t=n.split("/")[-1].split("_")
    for j in range(1,min(5,len(t)-2)+1): T["_"+"_".join(t[len(t)-j:])]+=1
open(sys.argv[3]+".ends","w").write("\n".join(["-"]+[x for x,c in T.most_common() if len(x)<=61])+"\n")
mats=collections.defaultdict(lambda:[collections.Counter(),[]])
for k,v in u.items():
    if k not in blocks: continue
    for m in v:
        r=re.fullmatch(r"material_([0-9a-f]+)",m)
        if not r: continue
        x=int(r.group(1),16)&M
        if x in nm: continue
        mats[x][0].update(blocks[k].get("#P",[]))   # counted: heads shared by more of the material's users come first
        mats[x][1]+= [w for w in blocks[k].get("#V",[]) if w not in mats[x][1]]
o=open(sys.argv[3],"w"); n=0
for x,(P,V) in mats.items():
    PP=set()
    for p,_ in P.most_common(PCAP):
        PP.add("mc/mtl_"+p); PP.add("mc/"+p)
        if re.match(r"p[78]_",p): PP.add("mc/t"+p[1:])
    o.write("#I %x\n#P %s\n#V %s\n"%(x," ".join(sorted(PP))," ".join(V[:300]))); n+=1
print("material blocks",n)
