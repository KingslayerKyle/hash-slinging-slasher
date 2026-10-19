# gmid blocks for the still-hashed IMAGES of the exported BO4 models: block id = the image id, P = i_ + every >=2-token prefix
# of the image's material core (when named) and i_ + the using model's family heads (t8_/p8_ both), V = the model's family
# vocab, OUT.ends = 1-5 token suffixes of known image names (most common first, e.g. _c _n _g _o).
# Run:  GE=OUT.ends gmid OUT tokens.txt
# usage: py contrib/bo4_models/img_gmid_prep.py PKL FAM_BLOCKS OUT [pcap=1500]
import sys,json,re,pickle,collections
d=pickle.load(open(sys.argv[1],"rb")); M=(1<<63)-1; ni=d["named"]["image"]
A=dict(a.split("=",1) for a in sys.argv[4:] if "=" in a); PCAP=int(A.get("pcap",1500))
blocks={}; cur=None
for l in open(sys.argv[2]):
    if l.startswith("#I "): cur=l[3:].strip(); blocks[cur]={}
    elif l[:2] in ("#P","#V"): blocks[cur][l[:2]]=l[3:].split()
u=json.load(open("state/bo4exp/unnamed_models.json"))
T=collections.Counter()
for n in ni.values():
    t=n.split("/")[-1].split("_")
    for j in range(1,min(5,len(t)-2)+1): T["_"+"_".join(t[len(t)-j:])]+=1
open(sys.argv[3]+".ends","w").write("\n".join(["-"]+[x for x,c in T.most_common() if len(x)<=61])+"\n")
imgs=collections.defaultdict(lambda:[collections.Counter(),[]])
for k,v in u.items():
    b=blocks.get(k,{})
    for mat,ims in v.items():
        core=None if mat.startswith("material_") else re.sub(r"^(mc/|ml/)?(mtl_)?","",mat)
        for i in ims:
            r=re.fullmatch(r"image_([0-9a-f]+)",i)
            if not r: continue
            x=int(r.group(1),16)&M
            if x in ni: continue
            c=imgs[x][0]
            if core:
                t=core.split("_")
                for j in range(2,len(t)+1): c["_".join(t[:j])]+=1000   # own material core first
            c.update(b.get("#P",[]))
            imgs[x][1]+=[w for w in b.get("#V",[]) if w not in imgs[x][1]]
o=open(sys.argv[3],"w"); n=0
for x,(P,V) in imgs.items():
    PP=set()
    for p,_ in P.most_common(PCAP):
        PP.add("i_"+p)
        if re.match(r"p[78]_",p): PP.add("i_t"+p[1:])
        if re.match(r"t[78]_",p): PP.add("i_p"+p[1:])
    if PP: o.write("#I %x\n#P %s\n#V %s\n"%(x," ".join(sorted(PP))," ".join(V[:300]))); n+=1
print("image blocks",n)
