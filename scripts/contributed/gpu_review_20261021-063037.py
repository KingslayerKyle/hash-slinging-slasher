# Review GPU global hits: drop ids named since, mark sibling groups (>=2 hit ids sharing all but the last 1-2 tokens),
# score own-export overlap (export_overlap.share). Prints  share  sib  name  ; accept rule used: share>=0.15 or sib, else eyeball.
#   jm = fewest unattested junctions over splits  head(known >=2-token prefix) _a _b _c [_tail(known suffix)]: the 4 joins
#        (head|a, a|b, b|c, c|tail). Measured: real held-out names jm<=2 in 76% (BO4) / 95% (CW); random candidates 1.4-1.8%.
#   Accept: jm<=2 (3-word runs; keeps ~98% of chance hits out) or sib or share>=0.4, else eyeball (0.15 let salads in).
# usage: py gpu_review.py PKL HITS.txt [more hits files]   (pool=xmodel by default; env POOL=material etc.)
import sys, pickle, collections, json, re, random
sys.argv, files = sys.argv[:2], sys.argv[2:]
import os
POOL = os.environ.get("POOL", "xmodel")
d = pickle.load(open(sys.argv[1], "rb")); named = d["named"][POOL]
bg = collections.Counter(); HD = set(); TL = set([""])
for n in named.values():
    t = n.split("_"); bg.update(set(zip(t, t[1:])))
    for i in range(2, len(t)): HD.add("_".join(t[:i]))
    for i in range(1, min(4, len(t))): TL.add("_".join(t[-i:]))
KM = int(os.environ.get("K", "3"))  # middle words of the run that produced the hits
def jm(n):
    t = n.split("_"); best = 9
    for i in range(2, len(t) - KM + 1):
        if "_".join(t[:i]) not in HD or "_".join(t[i + KM:]) not in TL: continue
        j = [(t[i + q - 1], t[i + q]) for q in range(KM + (1 if i + KM < len(t) else 0))]
        best = min(best, sum(bg[p] == 0 for p in j))
    return best
ex = json.load(open("state/bo4exp/unnamed_models.json"))
def toks(s): return set(t for t in re.split(r"[_/\$]", s.lower()) if t)
own = {}
for k, v in ex.items():
    s = set()
    for m, imgs in v.items():
        s |= toks(m)
        for i in imgs: s |= toks(i)
    own[int(k, 16) & ((1 << 63) - 1)] = s
GEN = {"p8", "p7", "t8", "t7", "splm", "clt", "cltp", "c", "attach", "wpn", "veh", "01", "02", "mod"}
def share(n, s):
    t = [x for x in n.split("/")[-1].split("_") if x not in GEN]
    return sum(x in s for x in t) / max(1, len(t)) if s is not None else -1
hits = {}
for f in files:
    for l in open(f):
        if l.strip():
            n, x = l.strip().rsplit(",", 1); x = int(x, 16)
            if x not in named: hits[x] = n
# sib: another hit id whose name has the same token count and differs in at most 2 token positions
# (two independent ids matching parallel names cannot both be chance)
toklists = [n.split("_") for n in hits.values()]
def sibling(n):
    t = n.split("_")
    return any(len(u) == len(t) and u != t and sum(a != b for a, b in zip(t, u)) <= 2 for u in toklists)
for x, n in sorted(hits.items(), key=lambda kv: -share(kv[1], own.get(kv[0]))):
    sib = sibling(n)
    print(f"{jm(n)}\t{share(n, own.get(x)):5.2f}\t{'sib' if sib else '-'}\t{n}\t{x:x}")
