import json, glob, re, collections, os
from load_ids import fnv1a63
B = chr(92)
A = json.load(open("w28447_alias_to_fileid.json"))
known = set(l.rstrip("\n").split(",",1)[1] for l in open("known_bo4_files.txt", encoding="utf-8"))
for fn in glob.glob("C:/tmp/hash-slinging-slasher/findings/blkops04/run_*/sound_asset.txt"):
    for l in open(fn, encoding="utf-8", errors="replace"):
        n = l.strip().split(",",1)[-1]
        if B in n: known.add(n)
X = set()
for n in known:
    p = n.split(B)
    if len(p) >= 5 and p[0] == "en" and p[1] == "vox" and p[2] == "scripted": X.add(p[3]); 
    if len(p) >= 6 and p[0] == "en" and p[1] == "vox" and p[2] == "scripted": X.add(p[4])
banks = [os.path.basename(f).split(".")[0] for f in glob.glob("banks/*.hashes")]
for b in set(banks):
    X.add(b); X.add(re.sub(r"^(mp|zm|wz|cp)_", "", b))
X |= {"exerts","exert","skits","skit","tutor","tutorial","mpl","wz","zmb","cp","common","frontend","ui","core","bik","banter","specialists","chars","characters","announcer","killstreak","killstreaks","scorestreak","scorestreaks","mp","zm","blackout","campaign"}
X = sorted(X)
maps = [("zod","zod"),("red","red"),("tow","tow"),("bod","bod"),("fiv","fiv"),("man","man"),("white","whi"),("orange","oran"),("common","cmn")]
vs = [""] + ["_%d" % i for i in range(10)] + ["_%02d" % i for i in range(40)]
tails = ["sn100.pc.snd","ln100.pc.snd"]
found = {}; groups = collections.defaultdict(list)
for h, a in A.items(): groups[a].append(int(h, 16))
print("aliases:", len(groups), "| X dirs:", len(X), flush=True)
for a, ids in groups.items():
    ids = set(ids); spk = a.split("_")[1] if a.count("_") >= 1 else a
    cands = []
    for x in X:
        for d in (["en","vox","scripted",x,spk], ["en","vox","scripted",x], ["en","vox","scripted",spk,x]):
            cands.append(B.join(d) + B + a)
    m = re.match(r"^vox_plr_(\d+)_(.+)$", a)
    if m:
        for d, tok in maps:
            cands.append(B.join(["en","vox","scripted","zmb",d]) + B + f"vox_{tok}_plr_{m.group(1)}_{m.group(2)}")
            cands.append(B.join(["en","vox","scripted","zmb",d]) + B + a)
    for c in cands:
        for v in vs:
            for t in tails:
                f = c + v + "." + t; hh = fnv1a63(f)
                if hh in ids: found[hh] = f; ids.discard(hh)
        if not ids: break
print("found:", len(found), "of", len(A), flush=True)
open("alias_targeted_found.txt", "w", encoding="utf-8").write("\n".join(sorted(found.values())) + "\n")
left = collections.Counter(re.sub(r"\d+", "N", A[f"{h:016x}"]).rsplit("_", 2)[0] for h in map(lambda s: int(s, 16), A) if int(s := f"{h:016x}", 16) not in found) if False else None
miss = collections.Counter("_".join(re.sub(r"\d+","N",a).split("_")[:3]) for h, a in A.items() if int(h,16) not in found)
print("still missing by shape:", miss.most_common(15))
