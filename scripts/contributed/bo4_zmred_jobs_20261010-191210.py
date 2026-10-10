"""jobs.txt for pair.c: per remaining model, its CLIP neighbours' names as skeletons, its described words."""
import json, os, re, sys
import numpy as np
from nltk.corpus import wordnet as wn
D = r'C:\tmp\bo4\glossary'
sys.argv = ['x']
exec(open(os.path.join(D, 'merge_wni.py')).read().split('# pool of every BO4 id')[0])
idx = load(os.path.join(PI, 'fnv1a_xmodels.wni'))
by60 = {k & 0x0FFFFFFFFFFFFFFF: v for k, v in idx.items()}

names = open(os.path.join(D, 'out', 'clip_names.txt')).read().split()
emb = np.load(os.path.join(D, 'out', 'clip.npy')).astype(np.float32)
emb /= np.linalg.norm(emb, axis=1, keepdims=True)
real = []
for n in names:
    if n.startswith('xmodel_') and all(c in '0123456789abcdef' for c in n[7:]):
        real.append(by60.get(int(n[7:], 16)))
    else:
        real.append(n)
named = np.array([r is not None for r in real])
vlm = json.load(open(os.path.join(D, 'vlm.json')))
remaining = open(os.path.join(D, 'remaining_models.txt')).read().split()
K = int(os.environ.get('K', 20))


def words_of(v):
    ws = set()
    for x in [v.get('object', '')] + list(v.get('nouns', [])):
        x = re.sub(r'[^a-z ]', '', str(x).lower()).strip()
        if not x:
            continue
        toks = x.split()
        ws.update(toks)
        if len(toks) > 1:
            ws.add('_'.join(toks)); ws.add(''.join(toks))
        for s in wn.synsets(x.replace(' ', '_'), 'n')[:2]:
            for l in s.lemma_names()[:4]:
                ws.add(l.lower())
            for hy in s.hypernyms()[:1]:
                ws.add(hy.lemma_names()[0].lower())
    for w in list(ws):
        if w.endswith('s') and len(w) > 4:
            ws.add(w[:-1])
        else:
            ws.add(w + 's')
    return sorted(w for w in ws if re.fullmatch(r'[a-z0-9_]{2,24}', w))


with open(os.path.join(D, 'jobs.txt'), 'w') as f:
    nw = 0
    for m in remaining:
        if m not in vlm or 'error' in vlm[m] or m not in names:
            continue
        i = names.index(m)
        sim = emb @ emb[i]
        sim[~named] = -9
        sk = set()
        for j in np.argsort(-sim)[:K]:
            r = real[j].lower()
            sk.add(r)
            t = r.split('_')
            for c in (3, 4, 5):
                if len(t) > c:
                    sk.add('_'.join(t[:c]))
        sk.add('p8_zm_red')
        ws = words_of(vlm[m]) + ['01', '02', '03', 'a', 'b', 'sm', 'lg', 'med', 'dmg', 'full', 'base', 'top']
        nw += len(ws)
        f.write('J %s\n' % m)
        f.writelines('S %s\n' % s for s in sorted(sk))
        f.writelines('W %s\n' % w for w in ws)
print('jobs written; mean words', nw // max(1, len(remaining)))
