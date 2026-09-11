import os, re, collections, sys
from load_ids import fnv1a63, load_ids
pools = load_ids("C:/tmp/hash-slinging-slasher/snapshots/blkops04.ids")
names = {}
for l in open("C:/tmp/hash-slinging-slasher/snapshots/blkops04.pools.txt", encoding="utf-8", errors="replace"):
    p = l.split()
    if len(p) >= 3 and p[0].isdigit(): names[int(p[0])] = p[1]
idx = {}
for pk, ids in pools.items():
    for x in ids: idx[x] = pk
B = chr(92)
pat = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./\:-]{3,120}")
seen = set(); hits = collections.defaultdict(dict); nfiles = 0
for root, _, fns in os.walk("C:/tmp/bo4_w28447/source"):
    for fn in fns:
        p = os.path.join(root, fn)
        try: t = open(p, encoding="utf-8", errors="replace").read()
        except Exception: continue
        nfiles += 1
        for m in pat.finditer(t):
            s = m.group(0).strip("#\"'.:-")
            if s in seen or len(s) < 4: continue
            seen.add(s)
            for cand in {s, s.lower(), s.replace("/", B), s.lower().replace("/", B)}:
                h = fnv1a63(cand)
                pk = idx.get(h)
                if pk is not None: hits[names.get(pk, pk)][h] = cand
        if nfiles % 2000 == 0: print("files", nfiles, "strings", len(seen), {k: len(v) for k, v in hits.items()}, flush=True)
print("DONE files", nfiles, "distinct strings", len(seen))
for k, v in sorted(hits.items(), key=lambda kv: -len(kv[1])): print(k, len(v))
import json
json.dump({k: {f"{h:016x}": n for h, n in v.items()} for k, v in hits.items()}, open("w28447_hits.json", "w"))
