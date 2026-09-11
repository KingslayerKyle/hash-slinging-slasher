import json, os, sys, itertools, string, collections
from load_ids import fnv1a63, load_ids
BD = "C:/tmp/bo4src/bundles"
pools = load_ids("C:/tmp/hash-slinging-slasher/snapshots/blkops04.ids"); p171 = pools[171]
vocab = {l.strip() for l in open("csv_vocab.txt", encoding="utf-8") if l.strip() and "_" not in l}
eng = {l.strip() for l in open("english_words.txt", encoding="utf-8") if 2 <= len(l.strip()) <= 14}
words = vocab | eng
known_toks = [l.strip() for l in open("C:/tmp/hash-slinging-slasher/contrib/bo4_wz_speakers.txt", encoding="utf-8") if l.strip()]
probe = ["boost_win", "boost_loss", "character_select", "exert_pain", "exert_death", "menu_select"]
al = string.ascii_lowercase + string.digits

def segs(key, maxp=6, cap=3000):
    out = []
    def rec(i, parts):
        if len(out) >= cap: return
        if i == len(key):
            out.append("_".join(parts)); return
        if len(parts) >= maxp: return
        for j in range(i + 1, len(key) + 1):
            w = key[i:j]
            if w in words or (w.isdigit()) or (len(parts) >= 1 and j - i <= 2 and w.isalnum() and w.isdigit()):
                rec(j, parts + [w])
    rec(0, [])
    return out

results = {}; unresolved_tok = []
for d in sorted(x for x in os.listdir(BD) if os.path.isdir(f"{BD}/{x}")):
    for fn in sorted(os.listdir(f"{BD}/{d}")):
        try: J = json.load(open(f"{BD}/{d}/{fn}", encoding="utf-8"))
        except Exception: continue
        hs = {k: int(v[6:], 16) for k, v in J.items() if isinstance(v, str) and v.startswith("#hash_")}
        hset = set(hs.values())
        tok = None
        for t in known_toks:
            if any(fnv1a63(f"vox_{t}_{p}") in hset for p in probe): tok = t; break
        if tok is None:
            for L in (2, 3, 4):
                for tt in itertools.product(al, repeat=L):
                    t = "".join(tt)
                    if any(fnv1a63(f"vox_{t}_{p}") in hset for p in probe[:3]): tok = t; break
                if tok: break
        if tok is None:
            unresolved_tok.append((d, fn, len(hs))); continue
        got = 0; names = {}
        for k, h in hs.items():
            if k.startswith("hash_"): continue
            for s in segs(k):
                a = f"vox_{tok}_{s}"
                if fnv1a63(a) == h: names[k] = a; got += 1; break
        results[(d, fn)] = (tok, len(hs), got, names)
        print(f"{d}/{fn}: tok={tok} keys={len(hs)} cracked={got}", flush=True)
print("unresolved token:", unresolved_tok)
allnames = {a for _, (t, n, g, nm) in results.items() for a in nm.values()}
new171 = [a for a in allnames if fnv1a63(a) in p171]
open("bundle_aliases.txt", "w", encoding="utf-8").write("\n".join(sorted(allnames)) + "\n")
json.dump({f"{d}/{fn}": {"tok": t, "names": nm} for (d, fn), (t, n, g, nm) in results.items()}, open("bundle_cracked.json", "w"), indent=1)
print("aliases cracked:", len(allnames), "| in pocket 171:", len(new171))
