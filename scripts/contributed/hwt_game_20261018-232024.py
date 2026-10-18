# One hwt round over every wanted pool of one game: build the name cache (hwt_load.py), then per pool pick the smallest
# suffix threshold tmin whose expected chance hits stay under MAXC, run state/hwt/bin/hwt.exe and collect the names.
# Writes state/hwt/g_<game>_<tag>/<pool>_names.txt and all_names.txt (sound_asset of BO4 apart: confirm with --no-fold).
# usage: py contrib/bo4_models/hwt_game.py <game> <tag> [maxc=0.3] [pools=a,b]
import sys,os,subprocess,pickle
G=sys.argv[1].lower(); TAG=sys.argv[2]; A=dict(a.split("=",1) for a in sys.argv[3:] if "=" in a); MAXC=float(A.get("maxc",0.3))
D="state/hwt/g_%s_%s"%(G,TAG); os.makedirs(D,exist_ok=True); PK=D+"/names.pkl"; HERE="contrib/bo4_models"
subprocess.run(["py",HERE+"/hwt_load.py",G,PK],check=True)
d=pickle.load(open(PK,"rb")); pools=A["pools"].split(",") if "pools" in A else list(d["pools"])
env=dict(os.environ)
for p in pools:
    if p not in d["pools"]: continue
    out=D+"/"+p
    for tmin in (1,2,3,4,6,8,12,16,24,32,48,64,96,128,192,256,384,512):
        r=subprocess.run(["py",HERE+"/hwt_pool_prep.py",PK,p,out,"tmin=%d"%tmin],capture_output=True,text=True,check=True).stdout.strip()
        if float(r.split("exp chance")[1])<=MAXC: break
    print(r,"tmin",tmin,flush=True)
    env["OFF"]="%X"%d["offs"][p][0]
    st=int(r.split("ids ")[1].split()[0])*int(r.split("tails ")[1].split()[0]); NP=str(max(8,-(-st//60000000)))
    with open(out+"_hits.txt","w") as f: subprocess.run([r"state\hwt\bin\hwt.exe",out,NP],stdout=f,stderr=subprocess.DEVNULL,env=env,check=True)
    ns=sorted({l.rstrip("\n").split("\t")[1] for l in open(out+"_hits.txt")})
    open(out+"_names.txt","w").write("".join(n+"\n" for n in ns)); print(p,"names",len(ns),flush=True)
with open(D+"/all_names.txt","w") as f:
    for p in pools:
        if os.path.exists(D+"/%s_names.txt"%p) and not (G=="blkops04" and p=="sound_asset"): f.write(open(D+"/%s_names.txt"%p).read())
