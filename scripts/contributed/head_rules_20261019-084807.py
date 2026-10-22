# Head-rewrite analogies over known BO4 model names: when heads A and B share >= SUP distinct tails (A_t and B_t both known,
# t >= 2 tokens), every other known A_t' gets tried as B_t'. Found by gmid's c_t7_for_t8_* family (c_t8_X -> c_t7_for_t8_X,
# 112 names in one rule). Tails shared by more than MAXH heads (e.g. "_01") are skipped as uninformative.
# usage: py contrib/bo4_models/head_rules.py PKL [sup=3] [maxh=40] [findings=1] > cands.txt     (stats on stderr)
import pickle,sys,glob,collections,itertools
d=pickle.load(open(sys.argv[1],"rb")); A=dict(a.split("=",1) for a in sys.argv[2:] if "=" in a)
SUP=int(A.get("sup",3)); MAXH=int(A.get("maxh",40))
names={n.split("/")[-1] for n in d["named"]["xmodel"].values()}
if A.get("findings","1")=="1":
    for f in glob.glob("findings/blkops04/*/xmodel.txt"):
        for l in open(f): names.add(l.strip().split(",")[-1].split("/")[-1])
byt=collections.defaultdict(set); byh=collections.defaultdict(set)
for n in names:
    t=n.split("_")
    for j in range(1,len(t)-1):
        h="_".join(t[:j]); tl="_".join(t[j:]); byt[tl].add(h); byh[h].add(tl)
sup=collections.Counter()
for tl,hs in byt.items():
    if len(hs)<2 or len(hs)>MAXH or tl.count("_")<1: continue
    for a,b in itertools.permutations(sorted(hs),2): sup[(a,b)]+=1
rules=[(a,b) for (a,b),c in sup.items() if c>=SUP]
out=set()
for a,b in rules:
    for tl in byh[a]:
        c=b+"_"+tl
        if c not in names: out.add(c)
print("names",len(names),"rules",len(rules),"cands",len(out),file=sys.stderr)
sys.stdout.write("".join(x+"\n" for x in out))
