"""Guess names for unnamed xanims by editing known names one `_` token at a time (substitute / insert / delete).
usage: python crack.py <names.cdb> <unnamed.json> <out.txt> [vocab size] [base: present|all]
Hash = FNV-1a 64 from 0x47F5817A5EF961BA over the name, 63-bit (MW4 xanims). Every hit is re-hashed in pure Python."""
import collections, json, sys, time
import numpy as np
sys.path.insert(0, r"C:/Users/sosne/AppData/Local/Temp/claude/D--dev-blndr-cod2ue/7118f175-7b8e-49d5-9fda-d76779afb615/scratchpad/hashpkg")
from build_cdb import read, fnv

P = np.uint64(0x100000001B3)
M63 = np.uint64(0x7FFFFFFFFFFFFFFF)
np.seterr(over="ignore")

table = read(sys.argv[1])
unnamed = json.load(open(sys.argv[2]))
targets = np.array(sorted(int(h, 16) for h in unnamed), dtype=np.uint64)
nvocab = int(sys.argv[4]) if len(sys.argv) > 4 else 3000
base_mode = sys.argv[5] if len(sys.argv) > 5 else "present"

cnt = collections.Counter(t for n in table.values() for t in n.split("_") if t)
vocab = [t for t, _ in cnt.most_common(nvocab)]
vocab += [str(i) for i in range(100)] + [f"{i:02d}" for i in range(100)] + [f"v{i}" for i in range(10)]
vocab = sorted(set(vocab))
L = max(len(t) for t in vocab)
V = np.zeros((len(vocab), L), dtype=np.uint64)
lens = np.array([len(t) for t in vocab])
for i, t in enumerate(vocab):
    V[i, :len(t)] = list(t.encode())
active = [lens > c for c in range(L)]


def state(s, h=0x47F5817A5EF961BA):
    for c in s.encode():
        h = ((h ^ c) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h


def vec(prefix, suffix):
    """hashes of prefix + v + suffix for every vocab token v"""
    h = np.full(len(vocab), state(prefix), dtype=np.uint64)
    for c in range(L):
        a = active[c]
        h[a] = (h[a] ^ V[a, c]) * P
    for ch in suffix.encode():
        h = (h ^ np.uint64(ch)) * P
    return h & M63


if base_mode.startswith("@"):                             # @file: one base name per line
    bases = sorted({l.strip() for l in open(base_mode[1:]) if l.strip()})
else:
    present = set(int(h, 16) for h in json.load(open("mumbai_present.json"))) if base_mode == "present" else None
    bases = sorted({n for h, n in table.items() if present is None or h in present})
found = {}
t0 = time.time()
for k, name in enumerate(bases):
    tok = name.split("_")
    for i in range(len(tok) + 1):
        pre = "_".join(tok[:i]) + ("_" if i else "")
        for kind, rest in (("sub", tok[i + 1:]), ("ins", tok[i:])):
            if kind == "sub" and i == len(tok):
                continue
            suf = ("_" + "_".join(rest)) if rest else ""
            h = vec(pre, suf)
            for j in np.nonzero(np.isin(h, targets))[0]:
                cand = pre + vocab[j] + suf
                if fnv(cand) & 0x7FFFFFFFFFFFFFFF == int(h[j]):
                    found[int(h[j])] = cand
        if i < len(tok):                                  # delete token i
            cand = "_".join(tok[:i] + tok[i + 1:])
            hc = fnv(cand) & 0x7FFFFFFFFFFFFFFF
            if cand and np.isin(np.uint64(hc), targets):
                found[hc] = cand
    if k % 2000 == 0:
        print(f"{k}/{len(bases)} bases, {len(found)} found, {time.time() - t0:.0f}s", flush=True)
with open(sys.argv[3], "w") as f:
    for h, n in sorted(found.items(), key=lambda x: x[1]):
        f.write(f"{h:x},{n}\n")
print(f"done: {len(found)} new names of {len(targets)} unnamed, vocab {len(vocab)}, bases {len(bases)}, {time.time() - t0:.0f}s")
