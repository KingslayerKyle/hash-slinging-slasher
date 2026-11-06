# Markov-walk middles (state/markov, markov.cs): from every known >=2-token model head, step only along ATTESTED bigrams
# (word pairs seen in known names; successors capped at the top N per word), depth 1..D, tail peeled from every unnamed id
# (top NE known 1-3 token suffixes + none). Hits must also have an attested last junction (checked in the tool).
# usage: py markov_prep.py PKL OUT.txt [N=40] [D=4] [NE=1500] [pool=xmodel] [hold=0 (fraction of named held out: validation)]
#        env FREE=k on the tool: one step anywhere may use the top-k middle words instead of an attested successor
#        prints the walk size per depth so D/N can be chosen before running
import pickle,sys,collections,random
A=dict(a.split("=") for a in sys.argv[3:]); N=int(A.get("N",40)); D=int(A.get("D",4)); NE=int(A.get("NE",1500))
POOL=A.get("pool","xmodel"); HOLD=float(A.get("hold",0)); random.seed(1)
d=pickle.load(open(sys.argv[1],"rb")); named=sorted(set(d["named"][POOL].values())); M=(1<<63)-1
OFF=d["offs"][POOL][0] if "offs" in d and POOL in d["offs"] else 0xCBF29CE484222325
def h(s):
    x=OFF
    for c in s.encode(): x=((x^c)*0x100000001B3)&0xFFFFFFFFFFFFFFFF
    return x&M
ids=sorted(d["pools"][POOL]-set(d["named"][POOL]))
if "holdf" in A:  # validation on a given hard set: those names leave every statistic and become the searched ids
    hold=set(l.strip() for l in open(A["holdf"]) if l.strip()); named=[n for n in named if n not in hold]; ids=sorted(h(n) for n in hold)
if HOLD:
    random.shuffle(named); k=int(len(named)*HOLD); hold=named[:k]; named=named[k:]; ids=sorted(h(n) for n in hold)
    open(sys.argv[2]+".held","w").write("\n".join(hold)+"\n")
big=collections.Counter(); heads=set(); tails=collections.Counter()
for n in named:
    t=n.split("_")
    big.update(zip(t,t[1:]))
    for i in range(2,len(t)): heads.add("_".join(t[:i]))
    for i in range(1,min(4,len(t))): tails["_".join(t[-i:])]+=1
succ=collections.defaultdict(list)
for (a,b),c in big.most_common():
    if len(succ[a])<N: succ[a].append(b)
E=[e for e,_ in tails.most_common(NE)]
# walk size per depth: paths(t,d) = sum over successors
p={t:1 for t in succ}; tot=[]
for dd in range(1,D+1):
    q={t:sum(p.get(w,1) for w in succ[t]) for t in succ}
    tot.append(sum(q.get(x.rsplit("_",1)[1],0) for x in heads)); p=q
print("ids",len(ids),"heads",len(heads),"words with succ",len(succ),"walk per depth","  ".join("%.2e"%x for x in tot),
      "total %.2e chance(before last-junction check) %.2f"%(sum(tot),sum(tot)*2*len(ids)*(len(E)+1)/2**64))
o=open(sys.argv[2],"w")
o.write("#OFF %x\n#I\n"%OFF+"".join("%x\n"%i for i in ids)+"#H\n"+"".join(x+"\n" for x in sorted(heads))+"#E\n-\n"+"".join(e+"\n" for e in E)
        +"#S\n"+"".join(a+" "+" ".join(v)+"\n" for a,v in succ.items())+"#BIG\n"+"".join("%s %s\n"%k for k,_ in big.most_common())+"#D %d\n"%D
        +"#FW "+" ".join(w for w,_ in collections.Counter(x for n in named for x in n.split("_")[1:] if x).most_common(5000))+"\n")
