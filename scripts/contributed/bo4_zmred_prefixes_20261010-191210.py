"""Prefix file for gpt_gen.py --prefix-file: "prefix budget" lines.
D&C-GEN-style: every known p8_zm_red_ family (1 and 2 words after the prefix) gets a budget growing with sqrt(size),
with a floor so rare families are covered; hit anchors (names found by us) get a fixed budget on their 2- and 3-word prefixes.
python3 prefixes.py [total] > prefixes.txt"""
import math, sys
from collections import Counter

P = 'p8_zm_red_'
TOTAL = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
names = [l.strip().split(',')[-1] for l in open('/root/gloss/names_train.txt')]
names = [n for n in names if n.startswith(P)]
hits = set()
for f in ('found23.txt', 'loop_found.txt', 'hot_new.txt'):
    try:
        hits |= {l.strip().split(',')[-1] for l in open('/root/gloss/' + f) if l.strip()}
    except FileNotFoundError:
        pass
hits = {h for h in hits if h.startswith(P)}

budget = Counter()
for k, share, floor in ((1, 0.45, 3000), (2, 0.30, 1000)):
    fam = Counter('_'.join(n[len(P):].split('_')[:k]) for n in names if len(n[len(P):].split('_')) > k)
    w = {f: math.sqrt(c) for f, c in fam.items()}
    s = sum(w.values())
    for f, v in w.items():
        budget[P + f + '_'] = max(budget[P + f + '_'], max(floor, int(TOTAL * share * v / s)))
anchor = max(2000, int(TOTAL * 0.25 / max(1, 2 * len(hits))))
for h in hits:
    ws = h[len(P):].split('_')
    for k in (2, 3):
        if len(ws) > k:
            budget[P + '_'.join(ws[:k]) + '_'] += anchor
for p, b in sorted(budget.items(), key=lambda x: -x[1]):
    print(p, b)
print('prefixes', len(budget), 'budget', sum(budget.values()), 'anchors', len(hits), file=sys.stderr)
