# Keep only the hwt hits a stricter run would also produce: some split head [_word] _tail with the tail in the
# tail list of a prep at tmin=STRICT (fewer, commoner suffixes -> fewer chance matches). Writes <pool>_strict.txt.
# usage: py contrib/bo4_models/hwt_strict.py DIR POOL MAXC   (DIR = state/hwt/g_<game>_<tag>, uses names.pkl)
import sys,subprocess,os
D,P,MAXC=sys.argv[1],sys.argv[2],float(sys.argv[3]); out=D+"/"+P+"_strictprep"
for tmin in (1,2,3,4,6,8,12,16,24,32,48,64,96,128,192,256,384,512):
    r=subprocess.run(["py","contrib/bo4_models/hwt_pool_prep.py",D+"/names.pkl",P,out,"tmin=%d"%tmin],capture_output=True,text=True,check=True).stdout
    if float(r.split("exp chance")[1])<=MAXC: break
H=set(l.strip() for l in open(D+"/%s/heads.txt"%P)); W=set(l.strip() for l in open(D+"/%s/words.txt"%P)); T=set(l.strip() for l in open(out+"/tails.txt"))
keep=[]
for n in (l.strip() for l in open(D+"/%s_names.txt"%P)):
    i=max(n.rfind("/"),n.rfind("\\")); dd,t=n[:i+1],n[i+1:].split("_"); ok=False
    for a in range(2,len(t)):
        if dd+"_".join(t[:a]) not in H: continue
        for b in range(a,min(a+3,len(t))):
            if (b==a or "_".join(t[a:b]) in W) and "_".join(t[b:]) in T: ok=True
    if ok: keep.append(n)
open(D+"/%s_strict.txt"%P,"w").write("".join(n+"\n" for n in keep))
print(P,"tmin",tmin,r.split("cands")[1].strip(),"kept",len(keep),"of",sum(1 for _ in open(D+"/%s_names.txt"%P)))
